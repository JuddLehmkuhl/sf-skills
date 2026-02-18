# Security Patterns

> Back to [SKILL.md](../SKILL.md)

## WITH SECURITY_ENFORCED

```apex
// Throws System.QueryException if user lacks FLS on any queried field
// Use in Apex where you want fail-fast behavior
List<Account> results = [
    SELECT Id, Name, Phone, AnnualRevenue
    FROM Account
    WITH SECURITY_ENFORCED
];
```

## Access Level in Database Methods (Spring '23+, Preferred)

```apex
// USER_MODE: enforces FLS + CRUD + sharing rules
List<Account> results = Database.query(soql, AccessLevel.USER_MODE);

// SYSTEM_MODE: bypasses all security (use only when justified)
List<Account> results = Database.query(soql, AccessLevel.SYSTEM_MODE);
```

## stripInaccessible (Graceful Degradation)

```apex
// Silently removes inaccessible fields instead of throwing
SObjectAccessDecision decision = Security.stripInaccessible(
    AccessType.READABLE,
    [SELECT Id, Name, SecretField__c FROM Account]
);
List<Account> safeAccounts = decision.getRecords();
// SecretField__c silently removed if user lacks FLS
Set<String> removedFields = decision.getRemovedFields().get('Account');
```

## Decision Matrix: Which Security Pattern to Use

| Context | Recommended Pattern | Reason |
|---------|-------------------|--------|
| LWC wire adapters | `WITH USER_MODE` / `AccessLevel.USER_MODE` | Consistent with Lightning platform security |
| Trigger / service layer | `AccessLevel.USER_MODE` or `stripInaccessible` | Enforce FLS while maintaining DML capability |
| Batch / scheduled | `AccessLevel.SYSTEM_MODE` (with explicit checks) | Often runs as automated user with limited permissions |
| Integration / API | `stripInaccessible` | Graceful handling of varied integration user profiles |
| Admin utilities | `AccessLevel.SYSTEM_MODE` | Administrative context with elevated permissions |
