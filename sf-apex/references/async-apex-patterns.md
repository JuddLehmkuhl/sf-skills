# Async Apex Patterns - Full Implementations

> Extracted from sf-apex SKILL.md for progressive disclosure.
> Return to [SKILL.md](../SKILL.md) for the decision matrix and workflow.

---

## Batch Apex

```apex
public class AccountCleanupBatch implements
    Database.Batchable<SObject>,
    Database.Stateful,
    Database.AllowsCallouts {

    private Integer totalProcessed = 0;
    private Integer totalErrors = 0;
    private List<String> errorMessages = new List<String>();

    /**
     * @description Defines the scope of records to process.
     *              Use Database.QueryLocator for up to 50M records.
     *              Use Iterable<SObject> for complex filtering (max 50K).
     */
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Name, Industry, AnnualRevenue, LastActivityDate
            FROM Account
            WHERE LastActivityDate < LAST_N_YEARS:2
            WITH USER_MODE
        ]);
    }

    /**
     * @description Processes each batch of records.
     *              Use Database.update with allOrNone=false for partial success.
     */
    public void execute(Database.BatchableContext bc, List<Account> scope) {
        List<Account> toUpdate = new List<Account>();

        for (Account acc : scope) {
            acc.Description = 'Inactive - last activity over 2 years ago';
            acc.Rating = 'Cold';
            toUpdate.add(acc);
        }

        List<Database.SaveResult> results = Database.update(toUpdate, false);

        for (Integer i = 0; i < results.size(); i++) {
            if (results[i].isSuccess()) {
                totalProcessed++;
            } else {
                totalErrors++;
                for (Database.Error err : results[i].getErrors()) {
                    errorMessages.add(
                        'Account ' + toUpdate[i].Id + ': ' + err.getMessage()
                    );
                }
            }
        }
    }

    /**
     * @description Runs after all batches complete. Send summary email,
     *              chain another batch, or log results.
     */
    public void finish(Database.BatchableContext bc) {
        AsyncApexJob job = [
            SELECT Id, Status, NumberOfErrors, JobItemsProcessed, TotalJobItems
            FROM AsyncApexJob
            WHERE Id = :bc.getJobId()
        ];

        Messaging.SingleEmailMessage mail = new Messaging.SingleEmailMessage();
        mail.setToAddresses(new List<String>{ UserInfo.getUserEmail() });
        mail.setSubject('Account Cleanup Batch Complete');
        mail.setPlainTextBody(
            'Status: ' + job.Status +
            '\nProcessed: ' + totalProcessed +
            '\nErrors: ' + totalErrors +
            (errorMessages.isEmpty() ? '' : '\n\nErrors:\n' + String.join(errorMessages, '\n'))
        );
        Messaging.sendEmail(new List<Messaging.SingleEmailMessage>{ mail });
    }
}
```

### Batch Best Practices

- Use `Database.Stateful` only when you need to maintain state (counters, error lists) -- it serializes between batches, adding overhead
- Use `Database.AllowsCallouts` when batches need HTTP callouts (max 100 callouts per `execute`)
- Use `Database.update(records, false)` (allOrNone=false) for partial success handling
- Default scope is 200; reduce for callout-heavy batches (`Database.executeBatch(batch, 50)`)
- The `finish` method is ideal for chaining batches, sending notifications, or logging

### Invoking a Batch

```apex
// Default scope (200)
Database.executeBatch(new AccountCleanupBatch());

// Custom scope (50 records per execute)
Database.executeBatch(new AccountCleanupBatch(), 50);

// From Schedulable
Database.executeBatch(new AccountCleanupBatch(), 200);
```

---

## Queueable Apex with Chaining

```apex
public class LeadEnrichmentQueueable implements Queueable, Database.AllowsCallouts {

    private List<Id> leadIds;
    private Integer retryCount;
    private static final Integer MAX_RETRIES = 3;

    public LeadEnrichmentQueueable(List<Id> leadIds) {
        this(leadIds, 0);
    }

    private LeadEnrichmentQueueable(List<Id> leadIds, Integer retryCount) {
        this.leadIds = leadIds;
        this.retryCount = retryCount;
    }

    public void execute(QueueableContext ctx) {
        // Attach finalizer for error handling / retry
        System.attachFinalizer(new LeadEnrichmentFinalizer(leadIds, retryCount));

        List<Lead> leads = [
            SELECT Id, Name, Company, Email
            FROM Lead
            WHERE Id IN :leadIds
            WITH USER_MODE
        ];

        List<Lead> toUpdate = new List<Lead>();

        for (Lead l : leads) {
            // Simulate enrichment (replace with callout in real implementation)
            l.Description = 'Enriched on ' + Datetime.now().format();
            toUpdate.add(l);
        }

        if (!toUpdate.isEmpty()) {
            update toUpdate;
        }

        // Chain next job if more work remains
        // NOTE: In async context, only 1 child Queueable can be enqueued per execute
        // In synchronous context (triggers, etc.), up to 50 can be enqueued
        List<Id> nextBatch = getNextBatchOfLeadIds();
        if (!nextBatch.isEmpty()) {
            System.enqueueJob(new LeadEnrichmentQueueable(nextBatch));
        }
    }

    private List<Id> getNextBatchOfLeadIds() {
        // Logic to determine remaining work
        return new List<Id>();
    }
}
```

### Queueable Best Practices

- Prefer Queueable over `@future` for complex logic, SObject parameters, or chaining
- Implement `Database.AllowsCallouts` when making HTTP callouts
- In async context, only 1 child Queueable can be enqueued per `execute`; in synchronous context, up to 50
- Use Finalizers for error handling and retry logic (see below)
- Use `Test.startTest()` / `Test.stopTest()` in tests to execute synchronously

---

## Queueable Finalizer (Error Handling & Retry)

```apex
public class LeadEnrichmentFinalizer implements Finalizer {

    private List<Id> leadIds;
    private Integer retryCount;
    private static final Integer MAX_RETRIES = 3;

    public LeadEnrichmentFinalizer(List<Id> leadIds, Integer retryCount) {
        this.leadIds = leadIds;
        this.retryCount = retryCount;
    }

    public void execute(FinalizerContext ctx) {
        String parentJobId = ctx.getAsyncApexJobId();

        if (ctx.getResult() == ParentJobResult.SUCCESS) {
            System.debug(LoggingLevel.INFO,
                'LeadEnrichment job ' + parentJobId + ' succeeded');
        } else {
            // Log the failure
            String errorMsg = ctx.getException() != null
                ? ctx.getException().getMessage()
                : 'Unknown error';

            System.debug(LoggingLevel.ERROR,
                'LeadEnrichment job ' + parentJobId +
                ' failed (attempt ' + (retryCount + 1) + '): ' + errorMsg);

            // Retry if under max attempts
            if (retryCount < MAX_RETRIES) {
                System.enqueueJob(
                    new LeadEnrichmentQueueable(leadIds, retryCount + 1)
                );
            } else {
                // Max retries exhausted - create a case or send alert
                createErrorCase(parentJobId, errorMsg);
            }
        }
    }

    private void createErrorCase(String jobId, String errorMsg) {
        insert new Case(
            Subject = 'Lead Enrichment Failed After ' + MAX_RETRIES + ' Retries',
            Description = 'Job ID: ' + jobId + '\nError: ' + errorMsg,
            Priority = 'High',
            Origin = 'System'
        );
    }
}
```

### Finalizer Rules

- Only ONE Finalizer can be attached per Queueable job
- Finalizer executes regardless of success or failure
- Finalizer runs in its own transaction with fresh governor limits
- Use `ctx.getResult()` to check `ParentJobResult.SUCCESS` or `UNHANDLED_EXCEPTION`
- Can enqueue a new Queueable from within a Finalizer (for retry patterns)

---

## Schedulable Apex

```apex
public with sharing class DailyAccountCleanupScheduler implements Schedulable {

    /**
     * @description Executes the scheduled job. Keep this method lightweight --
     *              delegate heavy work to Batch or Queueable.
     */
    public void execute(SchedulableContext sc) {
        Database.executeBatch(new AccountCleanupBatch(), 200);
    }

    /**
     * @description Convenience method to schedule this job.
     *              Call from Execute Anonymous or a setup script.
     *
     * Usage:
     *   DailyAccountCleanupScheduler.scheduleDaily();
     */
    public static String scheduleDaily() {
        // CRON: At 2:00 AM every day
        String cronExp = '0 0 2 * * ?';
        return System.schedule(
            'Daily Account Cleanup',
            cronExp,
            new DailyAccountCleanupScheduler()
        );
    }

    /**
     * @description Schedule with a custom CRON expression.
     */
    public static String scheduleCustom(String jobName, String cronExpression) {
        return System.schedule(
            jobName,
            cronExpression,
            new DailyAccountCleanupScheduler()
        );
    }
}
```

### Common CRON Expressions

| Schedule | CRON Expression |
|----------|-----------------|
| Every day at 2:00 AM | `0 0 2 * * ?` |
| Every weekday at 6:00 AM | `0 0 6 ? * MON-FRI` |
| First day of month at midnight | `0 0 0 1 * ?` |
| Every hour | `0 0 * * * ?` |
| Every 15 minutes (via 4 jobs) | `0 0 * * * ?`, `0 15 * * * ?`, `0 30 * * * ?`, `0 45 * * * ?` |

### Schedulable Best Practices

- Keep the `execute` method lightweight -- just launch Batch/Queueable
- Maximum of 100 scheduled Apex jobs at a time
- Scheduled jobs do not support callouts directly; use Batch with `Database.AllowsCallouts` or `@future(callout=true)` from within `execute`
- Use `System.schedule()` from Execute Anonymous for ad-hoc scheduling
- Use `System.abortJob(jobId)` to cancel a scheduled job
- Test with `Test.startTest()` / `Test.stopTest()` -- the job runs synchronously in test context

### Testing a Schedulable

```apex
@IsTest
static void testScheduledExecution() {
    Test.startTest();
    String jobId = DailyAccountCleanupScheduler.scheduleDaily();
    Test.stopTest();

    CronTrigger ct = [
        SELECT Id, CronExpression, TimesTriggered, NextFireTime
        FROM CronTrigger
        WHERE Id = :jobId
    ];
    Assert.areEqual('0 0 2 * * ?', ct.CronExpression,
        'CRON expression should match daily 2 AM schedule');
    Assert.areEqual(0, ct.TimesTriggered,
        'Job should not have fired yet');
}
```
