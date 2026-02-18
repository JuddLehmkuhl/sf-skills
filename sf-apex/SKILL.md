---
name: sf-apex
description: >
  Generates and reviews Salesforce Apex code with 2025-2026 best practices and 150-point
  scoring. Use when writing Apex classes, triggers, test classes, batch jobs, queueable
  chains, schedulable jobs, REST services, or reviewing existing Apex code for
  bulkification, security, and SOLID principles.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "150 points across 8 categories"
---

# sf-apex: Salesforce Apex Code Generation and Review

Expert Apex developer specializing in clean code, SOLID principles, and 2025-2026 best practices. Generate production-ready, secure, performant, and maintainable Apex code.

## Core Responsibilities

1. **Code Generation**: Create Apex classes, triggers (TAF), tests, async jobs, REST services from requirements
2. **Code Review**: Analyze existing Apex for best practices violations with actionable fixes
3. **Validation & Scoring**: Score code against 8 categories (0-150 points)
4. **Deployment Integration**: Validate and deploy via sf-deploy skill

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Class type (Trigger, Service, Selector, Batch, Queueable, Schedulable, Test, Controller, REST Service)
- Primary purpose (one sentence)
- Target object(s)
- Test requirements

**Then**:
1. Check existing code: `Glob: **/*.cls`, `Glob: **/*.trigger`
2. Check for existing Trigger Actions Framework setup: `Glob: **/*TriggerAction*.cls`
3. Create TodoWrite tasks

### Phase 2: Design & Template Selection

**Select template**:
| Class Type | Template |
|------------|----------|
| Trigger | `templates/trigger.trigger` |
| Trigger Action | `templates/trigger-action.cls` |
| Service | `templates/service.cls` |
| Selector | `templates/selector.cls` |
| Batch | `templates/batch.cls` |
| Queueable | `templates/queueable.cls` |
| Test | `templates/test-class.cls` |
| Test Data Factory | `templates/test-data-factory.cls` |
| Standard Class | `templates/apex-class.cls` |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-apex/templates/[template]`
2. **Project folder**: `[project-root]/sf-apex/templates/[template]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-apex/templates/apex-class.cls`

### Phase 3: Code Generation/Review

**For Generation**:
1. Create class file in `force-app/main/default/classes/`
2. Apply naming conventions (see [docs/naming-conventions.md](docs/naming-conventions.md))
3. Include ApexDoc comments
4. Create corresponding test class

**For Review**:
1. Read existing code
2. Run validation against best practices
3. Generate improvement report with specific fixes

**Run Validation**:
```
Score: XX/150 Rating
|- Bulkification: XX/25
|- Security: XX/25
|- Testing: XX/25
|- Architecture: XX/20
|- Clean Code: XX/20
|- Error Handling: XX/15
|- Performance: XX/10
|- Documentation: XX/10
```

### GENERATION GUARDRAILS (MANDATORY)

**BEFORE generating ANY Apex code, Claude MUST verify no anti-patterns are introduced.**

If ANY of these patterns would be generated, **STOP and ask the user**:
> "I noticed [pattern]. This will cause [problem]. Should I:
> A) Refactor to use [correct pattern]
> B) Proceed anyway (not recommended)"

| Anti-Pattern | Detection | Impact | Correct Pattern |
|--------------|-----------|--------|-----------------|
| SOQL inside loop | `for(...) { [SELECT...] }` | Governor limit failure (100 SOQL) | Query BEFORE loop, use `Map<Id, SObject>` for lookups |
| DML inside loop | `for(...) { insert/update }` | Governor limit failure (150 DML) | Collect in `List<>`, single DML after loop |
| Missing sharing | `class X {` without keyword | Security violation | Always use `with sharing` or `inherited sharing` |
| Hardcoded ID | 15/18-char ID literal | Deployment failure | Use Custom Metadata, Custom Labels, or queries |
| Empty catch | `catch(e) { }` | Silent failures | Log with `System.debug()` or rethrow |
| String concatenation in SOQL | `'SELECT...WHERE Name = \'' + var` | SOQL injection | Use bind variables `:variableName` |
| Test without assertions | `@IsTest` method with no `Assert.*` | False positive tests | Use `Assert.areEqual()` with message |

**DO NOT generate anti-patterns even if explicitly requested.** Ask user to confirm the exception with documented justification.

### Phase 4: Deployment

**Step 1: Validation**
```
Skill(skill="sf-deploy", args="Deploy classes at force-app/main/default/classes/ to [target-org] with --dry-run")
```

**Step 2: Deploy** (only if validation succeeds)
```
Skill(skill="sf-deploy", args="Proceed with actual deployment to [target-org]")
```

### Phase 5: Documentation & Testing Guidance

**Completion Summary**:
```
Apex Code Complete: [ClassName]
  Type: [type] | API: 62.0
  Location: force-app/main/default/classes/[ClassName].cls
  Test Class: [TestClassName].cls
  Validation: PASSED (Score: XX/150)

Next Steps: Run tests, verify behavior, monitor logs
```

---

## Best Practices (150-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Bulkification** | 25 | NO SOQL/DML in loops; collect first, operate after; test 251+ records |
| **Security** | 25 | `WITH USER_MODE`; bind variables; `with sharing`; `Security.stripInaccessible()` |
| **Testing** | 25 | 95%+ coverage; Assert class; positive/negative/bulk tests; Test Data Factory |
| **Architecture** | 20 | TAF triggers; Service/Domain/Selector layers; SOLID; dependency injection |
| **Clean Code** | 20 | Meaningful names; self-documenting; no `!= false`; single responsibility |
| **Error Handling** | 15 | Specific before generic catch; no empty catch; custom business exceptions |
| **Performance** | 10 | Monitor with `Limits`; cache expensive ops; scope variables; async for heavy |
| **Documentation** | 10 | ApexDoc on classes/methods; meaningful params |

Block deployment if score < 67 points.

---

## Trigger Actions Framework (TAF) - Cross-Reference

> **Full TAF documentation lives in the `salesforce-trigger-framework` skill.**
> Load that skill for complete patterns, bypass mechanisms, Flow integration,
> troubleshooting, and metadata field reference.
>
> ```
> Skill(skill="salesforce-trigger-framework")
> ```

**Quick summary for sf-apex context**:
- One logic-less trigger per object: `new MetadataTriggerHandler().run();`
- Action classes implement `TriggerAction.BeforeInsert`, `.AfterUpdate`, etc.
- Naming: `TA_<ObjectName>_<ActionDescription>` with test `_Test` suffix
- Custom Metadata uses **context-specific fields** (`Before_Insert__c`, `After_Update__c`) -- NOT generic `Object__c`/`Context__c`
- Order spacing: increments of 10

**If TAF is NOT installed**, use the Standard Trigger Pattern:

```apex
trigger LeadTrigger on Lead (before insert, before update) {
    LeadScoringService scoringService = new LeadScoringService();
    if (Trigger.isBefore) {
        if (Trigger.isInsert) {
            scoringService.calculateScores(Trigger.new);
        } else if (Trigger.isUpdate) {
            scoringService.recalculateIfChanged(Trigger.new, Trigger.oldMap);
        }
    }
}
```

---

## Async Apex Patterns

### Decision Matrix

| Scenario | Use | Governor Limits |
|----------|-----|-----------------|
| Simple callout, fire-and-forget | `@future(callout=true)` | 50 calls/txn, 200 queued |
| Complex logic, needs chaining | `Queueable` | 50 enqueued/txn, 1 chain depth (async) |
| Process millions of records | `Batch Apex` | 50M records, 2K scope default |
| Scheduled/recurring job | `Schedulable` | 100 scheduled jobs |
| Post-queueable cleanup/retry | `Queueable Finalizer` | 1 finalizer per Queueable |

### Batch Apex

Use Batch Apex when processing large data volumes (thousands to millions of records). Each `execute` invocation gets a fresh set of governor limits.

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

**Batch Best Practices**:
- Use `Database.Stateful` only when you need to maintain state (counters, error lists) -- it serializes between batches, adding overhead
- Use `Database.AllowsCallouts` when batches need HTTP callouts (max 100 callouts per `execute`)
- Use `Database.update(records, false)` (allOrNone=false) for partial success handling
- Default scope is 200; reduce for callout-heavy batches (`Database.executeBatch(batch, 50)`)
- The `finish` method is ideal for chaining batches, sending notifications, or logging

**Invoking a Batch**:
```apex
// Default scope (200)
Database.executeBatch(new AccountCleanupBatch());

// Custom scope (50 records per execute)
Database.executeBatch(new AccountCleanupBatch(), 50);

// From Schedulable
Database.executeBatch(new AccountCleanupBatch(), 200);
```

### Queueable Apex with Chaining

Use Queueable for complex async logic that needs state, SObject types as parameters, or job chaining.

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

**Queueable Best Practices**:
- Prefer Queueable over `@future` for complex logic, SObject parameters, or chaining
- Implement `Database.AllowsCallouts` when making HTTP callouts
- In async context, only 1 child Queueable can be enqueued per `execute`; in synchronous context, up to 50
- Use Finalizers for error handling and retry logic (see below)
- Use `Test.startTest()` / `Test.stopTest()` in tests to execute synchronously

### Queueable Finalizer (Error Handling & Retry)

Attach a Finalizer to a Queueable job for post-transaction cleanup, error logging, or automatic retry.

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

**Finalizer Rules**:
- Only ONE Finalizer can be attached per Queueable job
- Finalizer executes regardless of success or failure
- Finalizer runs in its own transaction with fresh governor limits
- Use `ctx.getResult()` to check `ParentJobResult.SUCCESS` or `UNHANDLED_EXCEPTION`
- Can enqueue a new Queueable from within a Finalizer (for retry patterns)

### Schedulable Apex

Use Schedulable for recurring jobs. Schedulable classes typically delegate to Batch or Queueable for the actual work.

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

**Common CRON Expressions**:
| Schedule | CRON Expression |
|----------|-----------------|
| Every day at 2:00 AM | `0 0 2 * * ?` |
| Every weekday at 6:00 AM | `0 0 6 ? * MON-FRI` |
| First day of month at midnight | `0 0 0 1 * ?` |
| Every hour | `0 0 * * * ?` |
| Every 15 minutes (via 4 jobs) | `0 0 * * * ?`, `0 15 * * * ?`, `0 30 * * * ?`, `0 45 * * * ?` |

**Schedulable Best Practices**:
- Keep the `execute` method lightweight -- just launch Batch/Queueable
- Maximum of 100 scheduled Apex jobs at a time
- Scheduled jobs do not support callouts directly; use Batch with `Database.AllowsCallouts` or `@future(callout=true)` from within `execute`
- Use `System.schedule()` from Execute Anonymous for ad-hoc scheduling
- Use `System.abortJob(jobId)` to cancel a scheduled job
- Test with `Test.startTest()` / `Test.stopTest()` -- the job runs synchronously in test context

**Testing a Schedulable**:
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

---

## Custom Exceptions

Define custom exceptions in your service layer for clean error handling and meaningful error messages. Custom exception classes MUST end with `Exception`.

### Exception Hierarchy Pattern

```apex
/**
 * @description Base exception for all application-level errors.
 *              Extend this for domain-specific exceptions.
 */
public class ApplicationException extends Exception {}

/**
 * @description Thrown when a service layer operation fails due to
 *              business rule violations.
 */
public class ServiceException extends ApplicationException {}

/**
 * @description Thrown when required data is not found.
 */
public class DataNotFoundException extends ApplicationException {}

/**
 * @description Thrown when an external integration fails.
 */
public class IntegrationException extends ApplicationException {
    public Integer statusCode { get; private set; }
    public String endpoint { get; private set; }

    public IntegrationException(String message, Integer statusCode, String endpoint) {
        this(message);
        this.statusCode = statusCode;
        this.endpoint = endpoint;
    }
}
```

### Service Layer Usage

```apex
public with sharing class OpportunityService {

    public class OpportunityServiceException extends Exception {}

    public static void closeOpportunities(List<Id> oppIds) {
        if (oppIds == null || oppIds.isEmpty()) {
            throw new OpportunityServiceException(
                'Cannot close opportunities: no IDs provided'
            );
        }

        Savepoint sp = Database.setSavepoint();
        try {
            List<Opportunity> opps = [
                SELECT Id, StageName, IsClosed
                FROM Opportunity
                WHERE Id IN :oppIds
                WITH USER_MODE
            ];

            if (opps.size() != oppIds.size()) {
                throw new DataNotFoundException(
                    'Expected ' + oppIds.size() + ' opportunities but found ' + opps.size()
                );
            }

            for (Opportunity opp : opps) {
                if (opp.IsClosed) {
                    throw new OpportunityServiceException(
                        'Opportunity ' + opp.Id + ' is already closed'
                    );
                }
                opp.StageName = 'Closed Won';
            }

            update opps;
        } catch (OpportunityServiceException e) {
            Database.rollback(sp);
            throw e; // Re-throw business exceptions
        } catch (Exception e) {
            Database.rollback(sp);
            throw new OpportunityServiceException(
                'Failed to close opportunities: ' + e.getMessage(), e
            );
        }
    }
}
```

**Custom Exception Best Practices**:
- Class name MUST end with `Exception` (Apex compiler requirement)
- Use `Savepoint` and `Database.rollback()` in service methods for transactional integrity
- Catch specific exceptions before generic `Exception`
- Re-throw or wrap exceptions -- never swallow them silently
- Include context (record IDs, field values) in exception messages
- Nest exceptions in service classes for locality: `public class MyServiceException extends Exception {}`

---

## Apex REST Services

Expose Apex logic as RESTful endpoints for external integrations.

### REST Service Pattern

```apex
@RestResource(urlMapping='/api/accounts/*')
global with sharing class AccountRestService {

    /**
     * @description Retrieve account by ID.
     *              GET /services/apexrest/api/accounts/{accountId}
     */
    @HttpGet
    global static AccountDTO getAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');

        List<Account> accounts = [
            SELECT Id, Name, Industry, AnnualRevenue, BillingCity, BillingState
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (accounts.isEmpty()) {
            RestContext.response.statusCode = 404;
            return null;
        }

        return new AccountDTO(accounts[0]);
    }

    /**
     * @description Create a new account.
     *              POST /services/apexrest/api/accounts
     *              Body: { "name": "Acme", "industry": "Technology" }
     */
    @HttpPost
    global static AccountDTO createAccount() {
        RestRequest req = RestContext.request;
        Map<String, Object> body = (Map<String, Object>)
            JSON.deserializeUntyped(req.requestBody.toString());

        String name = (String) body.get('name');
        if (String.isBlank(name)) {
            RestContext.response.statusCode = 400;
            throw new RestServiceException('Account name is required');
        }

        Account acc = new Account(
            Name = name,
            Industry = (String) body.get('industry')
        );
        insert acc;

        RestContext.response.statusCode = 201;
        return new AccountDTO(acc);
    }

    /**
     * @description Update an existing account.
     *              PATCH /services/apexrest/api/accounts/{accountId}
     */
    @HttpPatch
    global static AccountDTO updateAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');

        Map<String, Object> body = (Map<String, Object>)
            JSON.deserializeUntyped(req.requestBody.toString());

        Account acc = [
            SELECT Id, Name, Industry
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (body.containsKey('name')) {
            acc.Name = (String) body.get('name');
        }
        if (body.containsKey('industry')) {
            acc.Industry = (String) body.get('industry');
        }

        update acc;
        return new AccountDTO(acc);
    }

    /**
     * @description Delete an account.
     *              DELETE /services/apexrest/api/accounts/{accountId}
     */
    @HttpDelete
    global static void deleteAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');
        delete [SELECT Id FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        RestContext.response.statusCode = 204;
    }

    /**
     * @description DTO to control JSON serialization.
     *              Never return raw SObjects from REST endpoints.
     */
    global class AccountDTO {
        public String id;
        public String name;
        public String industry;
        public Decimal annualRevenue;
        public String billingCity;

        public AccountDTO(Account acc) {
            this.id = acc.Id;
            this.name = acc.Name;
            this.industry = acc.Industry;
            this.annualRevenue = acc.AnnualRevenue;
            this.billingCity = acc.BillingCity;
        }
    }

    public class RestServiceException extends Exception {}
}
```

**Apex REST Best Practices**:
- Use DTOs (wrapper classes) -- never expose raw SObjects to external consumers
- Set `RestContext.response.statusCode` explicitly (201 for create, 204 for delete, 400 for bad request, 404 for not found)
- Use `WITH USER_MODE` for FLS/CRUD enforcement
- Class must be `global` for REST exposure; use `with sharing` for row-level security
- Validate input before DML; return meaningful error responses
- URL mapping supports wildcards: `/api/accounts/*` matches `/api/accounts/001xx000003ABCD`
- Test using `RestContext.request` and `RestContext.response` in test methods

**Testing REST Services**:
```apex
@IsTest
static void testGetAccount() {
    Account testAcc = new Account(Name = 'Test REST Account');
    insert testAcc;

    RestRequest req = new RestRequest();
    req.requestURI = '/services/apexrest/api/accounts/' + testAcc.Id;
    req.httpMethod = 'GET';
    RestContext.request = req;
    RestContext.response = new RestResponse();

    Test.startTest();
    AccountRestService.AccountDTO result = AccountRestService.getAccount();
    Test.stopTest();

    Assert.areEqual(testAcc.Name, result.name,
        'Should return the correct account name');
}
```

---

## Platform Cache

Use Platform Cache to store frequently-accessed data in memory, reducing SOQL queries and improving performance.

### Org Cache Pattern (Shared Across All Users)

```apex
public with sharing class CacheManager {

    private static final String PARTITION_NAME = 'local.AppCache';

    /**
     * @description Retrieve a cached value with automatic cache-miss handling.
     *              Returns null if partition is unavailable.
     */
    public static Object get(String key) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            return partition.get(key);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache miss or unavailable: ' + e.getMessage());
            return null;
        }
    }

    /**
     * @description Store a value in org cache with TTL (seconds).
     */
    public static void put(String key, Object value, Integer ttlSeconds) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            partition.put(key, value, ttlSeconds);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache put failed: ' + e.getMessage());
        }
    }

    /**
     * @description Remove a cached value.
     */
    public static void remove(String key) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            partition.remove(key);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache remove failed: ' + e.getMessage());
        }
    }
}
```

### CacheBuilder Pattern (Recommended)

Use `Cache.CacheBuilder` for automatic cache-miss handling. The framework calls `doLoad` when a key is not in cache.

```apex
public class ActiveUsersCacheBuilder implements Cache.CacheBuilder {

    /**
     * @description Called automatically when the cache key is missing.
     *              Return value is cached with the partition's default TTL.
     */
    public Object doLoad(String key) {
        return [
            SELECT Id, Name, Email, Profile.Name
            FROM User
            WHERE IsActive = true
            WITH USER_MODE
        ];
    }
}
```

**Usage**:
```apex
// First call: executes SOQL, caches result
// Subsequent calls: returns cached data (no SOQL)
List<User> activeUsers = (List<User>) Cache.Org.get(
    ActiveUsersCacheBuilder.class,
    'AllActiveUsers'
);
```

**Platform Cache Best Practices**:
- Always handle `Cache.Org.OrgCacheException` -- cache may be unavailable or partition at capacity
- Use Org Cache for data shared across users; Session Cache for user-specific data
- Cache a few large items rather than many small items to reduce overhead
- Set appropriate TTL; default is 8 hours for Org Cache
- Invalidate cache when underlying data changes (`remove()` or overwrite with `put()`)
- Cache partition must be created in Setup > Platform Cache before use
- Minimum 10 KB cache available; check with `Cache.Org.getCapacity()`
- Do NOT cache sensitive data (PII, credentials) unless encrypted

---

## Code Review Red Flags

| Anti-Pattern | Fix |
|--------------|-----|
| SOQL/DML in loop | Collect in loop, operate after |
| `without sharing` everywhere | Use `with sharing` by default |
| No trigger bypass flag | Add Boolean Custom Setting |
| Multiple triggers on object | Single trigger + TAF |
| SOQL without WHERE/LIMIT | Always filter and limit |
| `System.debug()` everywhere | Control via Custom Metadata |
| `isEmpty()` before DML | Remove - empty list = 0 DMLs |
| Generic Exception only | Catch specific types first |
| Hard-coded Record IDs | Query dynamically |
| No Test Data Factory | Implement Factory pattern |
| Raw SObject in REST response | Use DTO wrapper classes |
| No Savepoint in service methods | Use `Database.setSavepoint()` / `rollback()` |

---

## Modern Apex Features (API 62.0+)

- **Null coalescing**: `value ?? defaultValue`
- **Safe navigation**: `record?.Field__c`
- **User mode**: `WITH USER_MODE` in SOQL
- **Assert class**: `Assert.areEqual()`, `Assert.isTrue()`
- **Queueable Finalizers**: `System.attachFinalizer()` for post-transaction cleanup
- **Transaction Finalizers**: `FinalizerContext.getResult()`, `getException()`

**Breaking Change (API 62.0)**: Cannot modify Set while iterating - throws `System.FinalException`

---

## Flow Integration (@InvocableMethod)

Apex classes can be called from Flow using `@InvocableMethod`. This pattern enables complex business logic, DML, callouts, and integrations from declarative automation.

### Quick Reference

| Annotation | Purpose |
|------------|---------|
| `@InvocableMethod` | Makes method callable from Flow |
| `@InvocableVariable` | Exposes properties in Request/Response wrappers |

### Template

Use `templates/invocable-method.cls` for the complete pattern with Request/Response wrappers.

### Example

```apex
public with sharing class RecordProcessor {

    @InvocableMethod(label='Process Record' category='Custom')
    public static List<Response> execute(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request req : requests) {
            Response res = new Response();
            res.isSuccess = true;
            res.processedId = req.recordId;
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(label='Record ID' required=true)
        public Id recordId;
    }

    public class Response {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Processed ID')
        public Id processedId;
    }
}
```

**See Also**: [docs/flow-integration.md](docs/flow-integration.md) - Complete @InvocableMethod guide

---

## Common Exception Types Reference

When writing test classes, use these specific exception types:

| Exception Type | When to Use | Example |
|----------------|-------------|---------|
| `DmlException` | Insert/update/delete failures | `Assert.isTrue(e.getMessage().contains('FIELD_CUSTOM_VALIDATION'))` |
| `QueryException` | SOQL query failures | Malformed query, no rows for assignment |
| `NullPointerException` | Null reference access | Accessing field on null object |
| `ListException` | List operation failures | Index out of bounds |
| `MathException` | Mathematical errors | Division by zero |
| `TypeException` | Type conversion failures | Invalid type casting |
| `LimitException` | Governor limit exceeded | Too many SOQL queries, DML statements |
| `CalloutException` | HTTP callout failures | Timeout, invalid endpoint |
| `JSONException` | JSON parsing failures | Malformed JSON |
| `InvalidParameterValueException` | Invalid method parameters | Bad input values |

**Test Example:**
```apex
@IsTest
static void testShouldThrowExceptionForMissingRequiredField() {
    try {
        // Code that should throw
        insert new Account(); // Missing Name
        Assert.fail('Expected DmlException was not thrown');
    } catch (DmlException e) {
        Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'),
            'Expected REQUIRED_FIELD_MISSING but got: ' + e.getMessage());
    }
}
```

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-metadata | Discover object/fields before coding | `Skill(skill="sf-metadata")` |
| sf-data | Generate 251+ test records after deploy | `Skill(skill="sf-data")` |
| sf-deploy | Deploy to org - see Phase 4 | `Skill(skill="sf-deploy", args="Deploy to [org]")` |
| sf-flow | Create Flow that calls your Apex | See @InvocableMethod section above |
| sf-lwc | Create LWC that calls your Apex | `@AuraEnabled` controller patterns |
| salesforce-trigger-framework | Full TAF patterns, bypass, Flow integration | `Skill(skill="salesforce-trigger-framework")` |

## Dependencies

**All optional**: sf-deploy, sf-metadata, sf-data, salesforce-trigger-framework. Install: `/plugin install github:Jaganpro/sf-skills/[skill-name]`

---

## Cross-Skill Dependency Checklist

**Before deploying Apex code, verify these prerequisites:**

| Prerequisite | Check Command | Required For |
|--------------|---------------|--------------|
| TAF Package | `sf package installed list --target-org alias` | TAF trigger pattern |
| Custom Fields | `sf sobject describe --sobject Lead --target-org alias` | Field references in code |
| Permission Sets | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |
| Trigger_Action__mdt | Check Setup > Custom Metadata Types | TAF trigger execution |

**Common Deployment Order:**
```
1. sf-metadata: Create custom fields
2. sf-metadata: Create Permission Sets
3. sf-deployment: Deploy fields + Permission Sets
4. sf-apex: Deploy Apex classes/triggers
5. sf-data: Create test data
```

---

## LSP-Based Validation (Auto-Fix Loop)

The sf-apex skill includes Language Server Protocol (LSP) integration for real-time syntax validation. This enables Claude to automatically detect and fix Apex syntax errors during code authoring.

### How It Works

1. **PostToolUse Hook**: After every Write/Edit operation on `.cls` or `.trigger` files, the LSP hook validates syntax
2. **Apex Language Server**: Uses Salesforce's official `apex-jorje-lsp.jar` (from VS Code extension)
3. **Auto-Fix Loop**: If errors are found, Claude receives diagnostics and auto-fixes them (max 3 attempts)
4. **Two-Layer Validation**:
   - **LSP Validation**: Fast syntax checking (~500ms)
   - **150-Point Validation**: Semantic analysis for best practices

### Prerequisites

For LSP validation to work, users must have:

| Requirement | How to Install |
|-------------|----------------|
| **VS Code Salesforce Extension Pack** | VS Code > Extensions > "Salesforce Extension Pack" |
| **Java 11+ (Adoptium recommended)** | https://adoptium.net/temurin/releases/ |

### Validation Flow

```
User writes Apex code -> Write/Edit tool executes
                              |
                    +-------------------------+
                    |   LSP Validation (fast)  |
                    |   Syntax errors only     |
                    +-------------------------+
                              |
                    +-------------------------+
                    |  150-Point Validation    |
                    |  Semantic best practices |
                    +-------------------------+
                              |
                    Claude sees any errors and auto-fixes
```

### Sample LSP Error Output

```
============================================================
APEX LSP VALIDATION RESULTS
   File: force-app/main/default/classes/MyClass.cls
   Attempt: 1/3
============================================================

Found 1 error(s), 0 warning(s)

ISSUES TO FIX:
----------------------------------------
[ERROR] line 4: Missing ';' at 'System.debug' (source: apex)

ACTION REQUIRED:
Please fix the Apex syntax errors above and try again.
(Attempt 1/3)
============================================================
```

### Graceful Degradation

If LSP is unavailable (no VS Code extension or Java), validation silently skips - the skill continues to work with only 150-point semantic validation.

---

## Reference

**Docs**: `docs/` folder (in sf-apex) - best-practices, trigger-actions-framework, security-guide, testing-guide, naming-conventions, solid-principles, design-patterns, code-review-checklist
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-apex/docs/`

---

## Notes

- **API Version**: 62.0 required
- **TAF Optional**: Prefer TAF when package is installed, use standard trigger pattern as fallback
- **Scoring**: Block deployment if score < 67
- **LSP**: Optional but recommended for real-time syntax validation

---

## Sources

- [Future vs Queueable vs Batch vs Schedulable - SFDC Prep](https://sfdcprep.com/salesforce-apex-future-vs-queueable-vs-batch-vs-schedulable/)
- [Simple Guide to Batch Apex - Salesforce Ben](https://www.salesforceben.com/batch-apex/)
- [Master Queueable Apex - Salesforce Ben](https://www.salesforceben.com/master-queueable-apex-when-why-and-how-to-use-it/)
- [Apex Scheduler - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_scheduler.htm)
- [Apex Scheduler Best Practices - Trailhead](https://trailhead.salesforce.com/content/learn/modules/asynchronous_apex/async_apex_scheduled)
- [Batch Apex Syntax & Best Practices - Trailhead](https://trailhead.salesforce.com/content/learn/modules/asynchronous_apex/async_apex_batch)
- [Transaction Finalizers - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_transaction_finalizers.htm)
- [Apex Finalizers Introductory Guide - Salesforce Ben](https://www.salesforceben.com/apex-finalizers-introductory-guide/)
- [Apex REST Methods - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_rest_methods.htm)
- [Apex Integration Services - Trailhead](https://trailhead.salesforce.com/content/learn/modules/apex_integration_services/apex_integration_webservices)
- [Platform Cache Best Practices - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_platform_cache_best_practices.htm)
- [Platform Cache - Trailhead](https://trailhead.salesforce.com/content/learn/modules/platform_cache/platform_cache_use)
- [CacheBuilder Interface - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_platform_cache_builder.htm)
- [Custom Exceptions - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_exception_custom.htm)
- [Service Layer Principles - Trailhead](https://trailhead.salesforce.com/content/learn/modules/apex_patterns_sl/apex_patterns_sl_apply_sl_principles)
- [Top 10 Apex Design Patterns - SFDC Stacks](https://www.sfdcstacks.com/2025/03/blog-post.html)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
