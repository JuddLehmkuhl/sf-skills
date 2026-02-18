# Service and DAL Layer Patterns

## Table of Contents

1. [Responsibilities: Action vs Service](#responsibilities-action-vs-service)
2. [Service Class Structure](#service-class-structure)
3. [Bulkification in Service Layer](#bulkification-in-service-layer)
4. [Error Handling in Services](#error-handling-in-services)
5. [Transactional Boundaries](#transactional-boundaries)
6. [DAL Class Structure](#dal-class-structure)
7. [Selector Patterns](#selector-patterns)
8. [Mock-Friendly Design for Unit Testing](#mock-friendly-design-for-unit-testing)
9. [Lazy Loading Patterns](#lazy-loading-patterns)

## Responsibilities: Action vs Service

| Responsibility | Trigger Action (TA_*) | Service Class |
|---------------|----------------------|---------------|
| Filter records by criteria | Yes -- determine which records need processing | No |
| Build old map from oldList | Yes -- context-specific plumbing | No |
| Business logic | No -- delegate to service | Yes -- all business rules here |
| Call DAL for queries | No -- never query from action | Yes -- orchestrate DAL calls |
| Call DAL for DML | No -- never DML from action (except addError) | Yes -- orchestrate DML through DAL |
| Reusable from Batch, LWC, API | No -- trigger-specific | Yes -- designed for reuse |

## Service Class Structure

```apex
public with sharing class OpportunityService {

    // ================================================================
    // PUBLIC METHODS - Called from trigger actions, batch, LWC, etc.
    // Always accept List<SObject> or Set<Id>, never single records.
    // ================================================================

    public static void calculateCommissions(List<Opportunity> opportunities) {
        if (opportunities == null || opportunities.isEmpty()) {
            return;
        }

        // Gather data
        Set<Id> ownerIds = extractOwnerIds(opportunities);
        Map<Id, Decimal> ratesByUser = DAL_User.getCommissionRatesByUserId(ownerIds);

        // Process
        List<Commission__c> commissions = buildCommissionRecords(opportunities, ratesByUser);

        // Persist
        if (!commissions.isEmpty()) {
            DAL_Commission.insertCommissions(commissions);
        }
    }

    public static void validateStageTransitions(
        List<Opportunity> newList,
        Map<Id, Opportunity> oldMap
    ) {
        Map<String, Set<String>> allowedTransitions = getStageTransitionRules();

        for (Opportunity opp : newList) {
            Opportunity oldOpp = oldMap.get(opp.Id);
            if (opp.StageName != oldOpp.StageName) {
                Set<String> allowed = allowedTransitions.get(oldOpp.StageName);
                if (allowed == null || !allowed.contains(opp.StageName)) {
                    opp.addError(
                        'Cannot transition from ' + oldOpp.StageName +
                        ' to ' + opp.StageName
                    );
                }
            }
        }
    }

    // ================================================================
    // PRIVATE METHODS - Internal helpers
    // ================================================================

    private static Set<Id> extractOwnerIds(List<Opportunity> opportunities) {
        Set<Id> ownerIds = new Set<Id>();
        for (Opportunity opp : opportunities) {
            ownerIds.add(opp.OwnerId);
        }
        return ownerIds;
    }

    private static List<Commission__c> buildCommissionRecords(
        List<Opportunity> opportunities,
        Map<Id, Decimal> ratesByUser
    ) {
        List<Commission__c> commissions = new List<Commission__c>();
        for (Opportunity opp : opportunities) {
            Decimal rate = ratesByUser.get(opp.OwnerId);
            if (rate != null && opp.Amount != null) {
                commissions.add(new Commission__c(
                    Opportunity__c = opp.Id,
                    Sales_Rep__c = opp.OwnerId,
                    Amount__c = opp.Amount * rate,
                    Commission_Date__c = Date.today()
                ));
            }
        }
        return commissions;
    }

    private static Map<String, Set<String>> getStageTransitionRules() {
        return DAL_StageTransition.getTransitionRules();
    }
}
```

## Bulkification in Service Layer

Service methods must handle collections, never single records. This ensures they work correctly whether called from a trigger (up to 200 records), a batch job (up to 2000), or a screen flow (1 record).

```apex
// WRONG -- single record signature
public static void processOpportunity(Opportunity opp) {
    // Forces callers to loop and call repeatedly
}

// CORRECT -- collection signature
public static void processOpportunities(List<Opportunity> opportunities) {
    // Handles 1 or 10,000 records efficiently
}
```

## Error Handling in Services

| Technique | When to Use | Example |
|-----------|------------|---------|
| `record.addError(msg)` | Validation in before context -- blocks the save for that record | `opp.addError('Amount required');` |
| `record.SomeField__c.addError(msg)` | Field-level error -- shows error next to the field in UI | `opp.Amount.addError('Must be positive');` |
| Throw `CustomException` | Unrecoverable error, should abort entire transaction | `throw new OpportunityService.ServiceException('Config missing');` |
| Collect errors in list | Partial success pattern -- log errors, continue processing | Add to `List<String> errors` and log after loop |

**Rule**: In before-context trigger actions, prefer `addError()` because it prevents the individual record from saving while allowing other records in the batch to succeed. In after-context actions, `addError()` rolls back the entire transaction for that record (including before-context changes).

## Transactional Boundaries

All trigger actions within a single DML operation share one transaction. If any action throws an uncaught exception, the entire transaction rolls back.

```
insert accounts;  // One transaction
  +-- TA_Account_Validate (Before Insert)     -- same transaction
  +-- TA_Account_SetDefaults (Before Insert)  -- same transaction
  +-- TA_Account_CreateContact (After Insert) -- same transaction
  +-- TA_Account_SendNotification (After Insert) -- same transaction
```

If `TA_Account_CreateContact` fails with an uncaught exception, the account insert and any previous action side effects are rolled back. Use `addError()` or try/catch in services to handle errors gracefully.

## DAL Class Structure

DAL classes encapsulate all SOQL queries and DML operations for a single SObject. They are the only classes that should contain SOQL or DML statements.

```apex
public with sharing class DAL_Account {

    // ================================================================
    // SELECTORS (Query Methods)
    // ================================================================

    public static List<Account> getAccountsByIds(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Type, Industry, BillingStreet, BillingCity,
                   BillingState, BillingPostalCode, OwnerId
            FROM Account
            WHERE Id IN :accountIds
        ];
    }

    public static List<Account> getAccountsWithContacts(Set<Id> accountIds) {
        return [
            SELECT Id, Name,
                   (SELECT Id, FirstName, LastName, Email FROM Contacts)
            FROM Account
            WHERE Id IN :accountIds
        ];
    }

    public static Map<String, Account> getAccountsByName(Set<String> names) {
        Map<String, Account> accountsByName = new Map<String, Account>();
        for (Account acc : [
            SELECT Id, Name, Type
            FROM Account
            WHERE Name IN :names
        ]) {
            accountsByName.put(acc.Name, acc);
        }
        return accountsByName;
    }

    // ================================================================
    // DML WRAPPERS
    // ================================================================

    public static List<Database.SaveResult> insertAccounts(List<Account> accounts) {
        return Database.insert(accounts, false); // allOrNone = false for partial success
    }

    public static List<Database.SaveResult> updateAccounts(List<Account> accounts) {
        return Database.update(accounts, false);
    }

    public static void deleteAccounts(List<Account> accounts) {
        delete accounts;
    }
}
```

## Selector Patterns

| Pattern | Naming Convention | Example |
|---------|------------------|---------|
| By Id set | `get<Object>sByIds(Set<Id>)` | `getAccountsByIds(accountIds)` |
| By name | `get<Object>sByName(Set<String>)` | `getAccountsByName(names)` |
| With children | `get<Object>sWith<Child>(Set<Id>)` | `getAccountsWithContacts(ids)` |
| By related Id | `get<Object>sBy<Parent>Id(Set<Id>)` | `getContactsByAccountId(accIds)` |
| Count | `count<Object>sBy<Criteria>(...)` | `countContactsByAccountId(accIds)` |
| Aggregate | `getSum<Field>By<Criteria>(...)` | `getSumAmountByAccountId(accIds)` |

## Mock-Friendly Design for Unit Testing

Design DAL classes to be mockable using virtual methods or interfaces:

```apex
public virtual with sharing class DAL_Account {

    // Virtual methods allow test mocking via StubProvider
    public virtual List<Account> getByIds(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Type, OwnerId
            FROM Account
            WHERE Id IN :accountIds
        ];
    }
}

// In test class, use StubProvider to mock DAL
@IsTest
private class AccountService_Test {

    @IsTest
    static void testServiceWithMockedDAL() {
        // Create mock
        DAL_Account mockDAL = (DAL_Account) Test.createStub(
            DAL_Account.class,
            new DAL_AccountMock()
        );

        // Inject mock
        AccountService.dalAccount = mockDAL;

        // Test service logic without real SOQL
        Test.startTest();
        AccountService.processAccounts(new Set<Id>{ '001000000000001' });
        Test.stopTest();

        // Assert service behavior
    }
}

private class DAL_AccountMock implements System.StubProvider {
    public Object handleMethodCall(
        Object stubbedObject, String stubbedMethodName,
        Type returnType, List<Type> listOfParamTypes,
        List<String> listOfParamNames, List<Object> listOfArgs
    ) {
        if (stubbedMethodName == 'getByIds') {
            return new List<Account>{
                new Account(Name = 'Mock Account', Type = 'Customer')
            };
        }
        return null;
    }
}
```

## Lazy Loading Patterns

For DAL methods called from service classes that may be invoked multiple times in one transaction, use lazy loading to avoid redundant queries:

```apex
public with sharing class DAL_CustomMetadata {

    private static Map<String, Commission_Rate__mdt> rateCache;

    public static Map<String, Commission_Rate__mdt> getCommissionRates() {
        if (rateCache == null) {
            rateCache = new Map<String, Commission_Rate__mdt>();
            for (Commission_Rate__mdt rate : Commission_Rate__mdt.getAll().values()) {
                rateCache.put(rate.Role__c, rate);
            }
        }
        return rateCache;
    }

    // Clear cache in tests
    @TestVisible
    private static void clearCache() {
        rateCache = null;
    }
}
```
