# Governor Limits by Execution Context

> Back to [SKILL.md](../SKILL.md)

## Limits Table

| Limit | Synchronous (Trigger, REST, LWC) | Asynchronous (Future, Queueable) | Batch Apex (per chunk) | Flow |
|-------|----------------------------------|----------------------------------|----------------------|------|
| **SOQL queries issued** | 100 | 200 | 200 | 100 |
| **Records retrieved (all queries)** | 50,000 | 50,000 | 50,000 | 50,000 |
| **SOSL searches** | 20 | 20 | 20 | 20 |
| **Records per SOSL** | 2,000 | 2,000 | 2,000 | 2,000 |
| **Query locator rows** | 10,000,000 | 10,000,000 | 50,000,000 | N/A |
| **CPU time** | 10,000 ms | 60,000 ms | 60,000 ms | N/A (flow limits) |
| **Heap size** | 6 MB | 12 MB | 12 MB | N/A |

## Context-Specific Guidance

- **Triggers** (via `salesforce-trigger-framework`): You share the 100-query / 50,000-row limit with ALL triggers, workflows, process builders, and flows in the same transaction. Keep trigger queries minimal; use a DAL (Data Access Layer) pattern to consolidate.
- **Batch Apex**: Each `execute()` chunk gets its own governor limits. Use `Database.getQueryLocator()` in `start()` to query up to 50 million rows.
- **Flow**: Subject to same per-transaction limits. Record-triggered flows share limits with the trigger transaction. Scheduled flows get their own transaction.
- **LWC / Aura**: Wire adapters and imperative Apex share limits with the Apex transaction they invoke. Use `@AuraEnabled(cacheable=true)` to enable client-side caching.
- **REST API**: Each API call is its own transaction with synchronous limits. Composite API bundles share one transaction.

## Efficient Patterns for Limit Management

```apex
// BAD: SOQL in a loop -- burns 1 query per iteration
for (Contact c : contacts) {
    Account a = [SELECT Name FROM Account WHERE Id = :c.AccountId];
}

// GOOD: Single query + Map lookup -- 1 query total
Set<Id> accountIds = new Set<Id>();
for (Contact c : contacts) {
    accountIds.add(c.AccountId);
}
Map<Id, Account> accountMap = new Map<Id, Account>(
    [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
);
for (Contact c : contacts) {
    Account a = accountMap.get(c.AccountId);
}

// GOOD: SOQL FOR loop -- streams in batches of 200, avoids heap
for (List<Account> batch : [SELECT Id, Name FROM Account WHERE Industry = 'Tech']) {
    // Process 200 records at a time
    // Does NOT count as multiple SOQL queries
}

// GOOD: Use aggregate instead of loading all records
Integer count = [SELECT COUNT() FROM Lead WHERE Status = 'Open'];
// vs loading 50,000 leads just to count them
```
