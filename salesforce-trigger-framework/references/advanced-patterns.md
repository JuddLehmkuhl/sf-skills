# Advanced Trigger Action Patterns

## Table of Contents

1. [Recursion Control](#recursion-control)
2. [Dynamic Entry Criteria](#dynamic-entry-criteria)
3. [DmlFinalizer](#dmlfinalizer)
4. [Before vs After Context Decision Guide](#before-vs-after-context-decision-guide)
5. [Multiple Interfaces on One Class](#multiple-interfaces-on-one-class)
6. [Performance and Governor Limits](#performance-and-governor-limits)
7. [Queueable Chaining from Trigger Actions](#queueable-chaining-from-trigger-actions)
8. [Platform Events for Async Processing](#platform-events-for-async-processing)
9. [Batch Apex Kickoff from Trigger Actions](#batch-apex-kickoff-from-trigger-actions)

## Recursion Control

The framework tracks how many times a record has been seen in update contexts via `TriggerBase.idToNumberOfTimesSeenBeforeUpdate` and `TriggerBase.idToNumberOfTimesSeenAfterUpdate`. Use these maps to prevent infinite loops when your trigger action updates records that re-fire the trigger.

```apex
public with sharing class TA_Account_SyncStatus implements TriggerAction.AfterUpdate {

    private static final Integer MAX_RECURSION = 2;

    public void afterUpdate(List<Account> newList, List<Account> oldList) {
        Map<Id, Account> oldMap = new Map<Id, Account>(oldList);
        List<Account> accountsToProcess = new List<Account>();

        for (Account acc : newList) {
            Account oldAcc = oldMap.get(acc.Id);
            // Only process if field changed AND recursion limit not reached
            if (acc.Status__c != oldAcc.Status__c
                && TriggerBase.idToNumberOfTimesSeenAfterUpdate.get(acc.Id) < MAX_RECURSION) {
                accountsToProcess.add(acc);
            }
        }

        if (!accountsToProcess.isEmpty()) {
            AccountService.syncStatusToChildren(accountsToProcess);
        }
    }
}
```

### Recursion Control Gotchas

| Scenario | Risk | Mitigation |
|----------|------|------------|
| Action A updates record, fires Action B, which updates record again | Infinite loop | Check `idToNumberOfTimesSeenAfterUpdate` count |
| Two objects update each other in after triggers | Cross-object recursion | Use `TriggerBase.bypass()` before the cross-object DML |
| Flow trigger action updates the same record | Flow recursion limit (3 deep) | Set `Allow_Flow_Recursion__c = false` |
| Queueable enqueued from trigger re-processes same records | Separate transaction, triggers fire again | Use a flag field or static variable in the Queueable |

## Dynamic Entry Criteria

The `Entry_Criteria__c` formula field on `Trigger_Action__mdt` allows you to define a formula that determines whether the action should execute. The framework evaluates this formula at runtime and skips the action if the formula returns `false`.

```
Entry_Criteria__c formula examples:

// Only run during business hours
CASE(MOD(NOW() - DATETIMEVALUE('1900-01-07 00:00:00'), 7),
  0, false,   // Sunday
  6, false,   // Saturday
  AND(HOUR(NOW()) >= 8, HOUR(NOW()) <= 17)
)

// Only run in Production (not sandboxes)
$Organization.IsSandbox = false

// Only run when a specific Custom Setting is enabled
$Setup.Trigger_Settings__c.Enable_Lead_Enrichment__c = true
```

## DmlFinalizer

The `TriggerAction.DmlFinalizer` interface allows you to define logic that runs after all DML in the trigger context completes. Useful for cleanup operations, summary calculations, or publishing consolidated platform events.

```apex
public with sharing class TA_Opportunity_PublishSummaryEvent
    implements TriggerAction.AfterInsert, TriggerAction.DmlFinalizer {

    // Collect data during the trigger action
    private static List<Opportunity> processedOpps = new List<Opportunity>();

    public void afterInsert(List<Opportunity> newList) {
        processedOpps.addAll(newList);
    }

    // This runs AFTER all trigger actions and DML complete
    public void execute(FinalizerContext ctx) {
        if (!processedOpps.isEmpty()) {
            List<Opportunity_Batch_Created__e> events = new List<Opportunity_Batch_Created__e>();
            events.add(new Opportunity_Batch_Created__e(
                Record_Count__c = processedOpps.size(),
                Total_Amount__c = sumAmounts(processedOpps)
            ));
            EventBus.publish(events);
            processedOpps.clear();
        }
    }

    private Decimal sumAmounts(List<Opportunity> opps) {
        Decimal total = 0;
        for (Opportunity opp : opps) {
            total += (opp.Amount != null ? opp.Amount : 0);
        }
        return total;
    }
}
```

## Before vs After Context Decision Guide

| Use Case | Context | Why |
|----------|---------|-----|
| Set default field values | Before Insert | No DML needed -- direct field assignment |
| Validate field values | Before Insert / Before Update | Use `addError()` to prevent save |
| Prevent record deletion | Before Delete | Use `addError()` to block delete |
| Compute derived fields | Before Insert / Before Update | Modify fields in-memory before save |
| Create related records | After Insert | Need parent record Id |
| Update related records on change | After Update | Need committed record state |
| Send notifications | After Insert / After Update | Need committed record state |
| Publish platform events | After Insert / After Update | Events need record Ids |
| Audit deletion | After Delete | Records are finalized, capture for audit |
| Restore related data | After Undelete | Records are restored, sync relationships |
| Cascade field values to children | After Update | Need committed state, DML on children |

**Key rule**: If you need the record's Id or need to perform DML on other objects, use an After context. If you need to modify the triggering record's fields without DML, use a Before context.

## Multiple Interfaces on One Class

When the same logic applies to both insert and update, implement multiple interfaces on a single class. Register the class in Custom Metadata once per context.

```apex
public with sharing class TA_Contact_NormalizePhone implements
    TriggerAction.BeforeInsert,
    TriggerAction.BeforeUpdate {

    public void beforeInsert(List<Contact> newList) {
        normalizePhoneNumbers(newList);
    }

    public void beforeUpdate(List<Contact> newList, List<Contact> oldList) {
        Map<Id, Contact> oldMap = new Map<Id, Contact>(oldList);
        List<Contact> contactsWithPhoneChanges = new List<Contact>();

        for (Contact c : newList) {
            Contact old = oldMap.get(c.Id);
            if (c.Phone != old.Phone || c.MobilePhone != old.MobilePhone) {
                contactsWithPhoneChanges.add(c);
            }
        }

        if (!contactsWithPhoneChanges.isEmpty()) {
            normalizePhoneNumbers(contactsWithPhoneChanges);
        }
    }

    private void normalizePhoneNumbers(List<Contact> contacts) {
        for (Contact c : contacts) {
            if (String.isNotBlank(c.Phone)) {
                c.Phone = PhoneUtils.normalize(c.Phone);
            }
            if (String.isNotBlank(c.MobilePhone)) {
                c.MobilePhone = PhoneUtils.normalize(c.MobilePhone);
            }
        }
    }
}
```

**Registration**: Create TWO metadata records -- one for `Before_Insert__c` and one for `Before_Update__c`, both pointing to the same `Apex_Class_Name__c`.

## Performance and Governor Limits

### SOQL/DML Limits Shared Across Actions

All trigger actions within one DML operation share the same governor limits. There is no per-action isolation.

```
insert 200 accounts;
  TA_Account_Validate:     uses  2 SOQL queries,  0 DML
  TA_Account_SetDefaults:  uses  0 SOQL queries,  0 DML
  TA_Account_CreateTeam:   uses  3 SOQL queries,  1 DML
  TA_Account_Notify:       uses  1 SOQL query,    1 DML
  ----------------------------------------------------------
  TOTAL for transaction:         6 SOQL queries,  2 DML
  Limit:                       100 SOQL queries, 150 DML
```

**Planning rule**: For each object, sum the SOQL/DML usage of all actions across all contexts that fire in one transaction. Ensure the total stays well below limits.

### CPU Time Budgeting

Apex trigger transactions have a 10,000ms (10 second) CPU time limit. Budget across actions:

| Action | Estimated CPU | Notes |
|--------|--------------|-------|
| Simple field assignment | < 50ms for 200 records | Loops with no queries |
| Validation with SOQL | 100-500ms | Depends on query complexity |
| Complex computation | 500-2000ms | Scoring algorithms, etc. |
| External callout | Not allowed in triggers | Must use async |

If your trigger actions collectively approach 5000ms CPU time, move heavy logic to async processing.

## Queueable Chaining from Trigger Actions

For operations too expensive for synchronous trigger execution, enqueue a Queueable:

```apex
public with sharing class TA_Account_EnqueueExternalSync implements TriggerAction.AfterUpdate {

    public void afterUpdate(List<Account> newList, List<Account> oldList) {
        Map<Id, Account> oldMap = new Map<Id, Account>(oldList);
        Set<Id> changedAccountIds = new Set<Id>();

        for (Account acc : newList) {
            Account oldAcc = oldMap.get(acc.Id);
            if (acc.Name != oldAcc.Name || acc.BillingCity != oldAcc.BillingCity) {
                changedAccountIds.add(acc.Id);
            }
        }

        if (!changedAccountIds.isEmpty() && !System.isBatch() && !System.isFuture()) {
            System.enqueueJob(new AccountExternalSyncQueueable(changedAccountIds));
        }
    }
}
```

**Gotcha**: You can only enqueue ONE Queueable from a trigger context (the limit is 1 `System.enqueueJob` per synchronous transaction in some contexts). If multiple actions need async work, consolidate into a single Queueable or use Platform Events.

## Platform Events for Async Processing

When multiple async operations are needed from triggers, publish Platform Events and let subscribers handle them:

```apex
public with sharing class TA_Order_PublishForProcessing implements TriggerAction.AfterInsert {

    public void afterInsert(List<Order> newList) {
        List<Order_Processing__e> events = new List<Order_Processing__e>();

        for (Order o : newList) {
            events.add(new Order_Processing__e(
                Order_Id__c = o.Id,
                Processing_Type__c = 'FULFILLMENT'
            ));
        }

        if (!events.isEmpty()) {
            List<Database.SaveResult> results = EventBus.publish(events);
            for (Database.SaveResult sr : results) {
                if (!sr.isSuccess()) {
                    System.debug(LoggingLevel.ERROR,
                        'Failed to publish event: ' + sr.getErrors());
                }
            }
        }
    }
}
```

## Batch Apex Kickoff from Trigger Actions

```apex
public with sharing class TA_ImportBatch_KickoffProcessing implements TriggerAction.AfterInsert {

    public void afterInsert(List<Import_Batch__c> newList) {
        for (Import_Batch__c batch : newList) {
            if (batch.Status__c == 'Ready') {
                // Only one Database.executeBatch per trigger transaction
                Database.executeBatch(new ImportRecordProcessor(batch.Id), 200);
                break; // Can only start one batch from trigger context
            }
        }
    }
}
```

**Limit**: Only ONE `Database.executeBatch()` call is allowed per trigger transaction. If you need to start multiple batches, chain them or use Platform Events.
