# Apex Controller Integration for LWC

LWC-facing `@AuraEnabled` contract patterns. For comprehensive Apex patterns (triggers, batch jobs, test classes), see the **sf-apex** skill.

---

## Cacheable Methods (for @wire)

```apex
public with sharing class LwcController {

    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts(String searchTerm) {
        String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
        return [
            SELECT Id, Name, Industry, AnnualRevenue
            FROM Account
            WHERE Name LIKE :searchKey
            WITH SECURITY_ENFORCED
            ORDER BY Name
            LIMIT 50
        ];
    }
}
```

## Non-Cacheable Methods (for DML)

```apex
@AuraEnabled
public static Account createAccount(String accountJson) {
    Account acc = (Account) JSON.deserialize(accountJson, Account.class);

    SObjectAccessDecision decision = Security.stripInaccessible(
        AccessType.CREATABLE,
        new List<Account>{ acc }
    );

    insert decision.getRecords();
    return (Account) decision.getRecords()[0];
}
```

## Error Handling in Apex Controllers

```apex
@AuraEnabled
public static void updateRecords(List<Id> recordIds) {
    try {
        // Business logic
    } catch (DmlException e) {
        throw new AuraHandledException(e.getMessage());
    } catch (Exception e) {
        throw new AuraHandledException(
            'An unexpected error occurred. Please contact your administrator.'
        );
    }
}
```

**Rule**: Always throw `AuraHandledException` -- other exceptions expose stack traces to the client.
