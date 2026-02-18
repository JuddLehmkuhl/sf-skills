# Anti-Patterns: Full Code Examples

> Referenced from `SKILL.md` -- Anti-Patterns section

---

## 1. SOQL/DML Inside Loops

```apex
// BAD - Governor limit violation (100 SOQL / 150 DML max per transaction)
for (Account acc : accounts) {
    List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
    update acc;
}

// GOOD - Bulkified
Map<Id, List<Contact>> contactsByAcct = new Map<Id, List<Contact>>();
for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
    if (!contactsByAcct.containsKey(c.AccountId)) {
        contactsByAcct.put(c.AccountId, new List<Contact>());
    }
    contactsByAcct.get(c.AccountId).add(c);
}
update accounts; // Single DML
```

## 2. Hardcoded Record IDs

```apex
// BAD - IDs differ between orgs/sandboxes
Account a = new Account(RecordTypeId = '012000000000ABC', OwnerId = '005000000000XYZ');

// GOOD - Dynamic lookup
Id rtId = Schema.SObjectType.Account.getRecordTypeInfosByDeveloperName()
    .get('Business_Account').getRecordTypeId();
```

## 3. Hardcoded Profile/Role Names in Queries

```apex
// BAD - Fragile, breaks on rename
Profile p = [SELECT Id FROM Profile WHERE Name = 'System Administrator'];

// GOOD - Use Permission Sets instead of Profiles when possible
// Or at minimum, use constants
private static final String ADMIN_PROFILE = 'System Administrator';
```

## 4. Real PII in Test Data

```apex
// BAD - Compliance risk (GDPR, CCPA, HIPAA)
Contact c = new Contact(FirstName = 'John', LastName = 'Smith',
    Email = 'john.smith@realcompany.com', Phone = '555-123-4567');

// GOOD - Synthetic data
Contact c = new Contact(FirstName = 'Test', LastName = 'Contact_' + index,
    Email = 'test' + index + '@example.com', Phone = '555-000-' + String.valueOf(index).leftPad(4, '0'));
```

## 5. Using `seeAllData=true`

```apex
// BAD - Tests depend on org data, fail unpredictably
@isTest(seeAllData=true)
static void testMethod() { ... }

// GOOD - Create all test data in the test
@isTest
static void testMethod() {
    List<Account> accts = TestDataFactory_Account.create(5);
    // ...
}
```

## 6. Missing Required Fields in Test Data

```apex
// BAD - Fails silently or with cryptic errors
Contact c = new Contact(LastName = 'Test');
insert c; // Fails if org requires Email or AccountId

// GOOD - Include all required fields upfront
Contact c = new Contact(
    FirstName = 'Test', LastName = 'Contact_0',
    AccountId = testAccount.Id, Email = 'test0@example.com'
);
```

## 7. Not Testing Bulk (200+ Records)

```apex
// BAD - Only tests single record; hides governor limit issues
@isTest static void testSingle() {
    insert new Account(Name = 'Test');
}

// GOOD - Cross the 200-record batch boundary
@isTest static void testBulk() {
    List<Account> accts = TestDataFactory_Account.create(251);
    // Assertions on all 251 records
}
```

## 8. SELECT * Equivalent (Querying All Fields)

```apex
// BAD - Wastes heap, slower queries
// Using FIELDS(ALL) in production code
List<Account> accts = [SELECT FIELDS(ALL) FROM Account LIMIT 200];

// GOOD - Select only needed fields
List<Account> accts = [SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology'];
```

## 9. No WHERE Clause on Delete Operations

```apex
// BAD - Dangerous; could delete production data
DELETE [SELECT Id FROM Account];

// GOOD - Scoped cleanup
DELETE [SELECT Id FROM Account WHERE Name LIKE 'Test_%' AND CreatedDate = TODAY];
```

## 10. Ignoring Database.SaveResult

```apex
// BAD - Partial failures go undetected
insert records;

// GOOD - Check results when partial success matters
Database.SaveResult[] results = Database.insert(records, false);
for (Database.SaveResult sr : results) {
    if (!sr.isSuccess()) {
        for (Database.Error err : sr.getErrors()) {
            System.debug(LoggingLevel.ERROR, err.getStatusCode() + ': ' + err.getMessage());
        }
    }
}
```

## 11. Mixing Test Data Creation with Assertions

```apex
// BAD - Hard to maintain, not reusable
@isTest static void testTrigger() {
    Account a = new Account(Name='Test', Industry='Tech', Type='Prospect',
        BillingCity='SF', BillingState='CA', Phone='555-0000');
    insert a;
    // 50 more lines of data setup...
    System.assertEquals('Expected', a.Status__c);
}

// GOOD - Factory + focused assertion
@isTest static void testTrigger() {
    List<Account> accts = TestDataFactory_Account.create(1);
    Test.startTest();
    // invoke trigger logic
    Test.stopTest();
    Account result = [SELECT Status__c FROM Account WHERE Id = :accts[0].Id];
    System.assertEquals('Expected', result.Status__c);
}
```

## 12. Loading CSV with Wrong Line Endings or Encoding

```
# BAD - Windows CRLF line endings or non-UTF-8 encoding cause silent data corruption
# Always use UTF-8 encoding and LF line endings for CSV files used with sf data import bulk
```
