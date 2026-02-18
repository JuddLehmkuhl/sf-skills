# Test Data Factory Pattern: Full Implementation

> Referenced from `SKILL.md` -- Test Data Factory Pattern section

---

## Naming Convention

```
TestDataFactory_[ObjectName]
```

## Standard Factory with RecordType Support

```apex
@isTest
public class TestDataFactory_Account {

    // --- RecordType Cache (query once, reuse) ---
    private static Map<String, Id> rtCache = new Map<String, Id>();

    public static Id getRecordTypeId(String developerName) {
        if (!rtCache.containsKey(developerName)) {
            Schema.RecordTypeInfo rti = Schema.SObjectType.Account
                .getRecordTypeInfosByDeveloperName().get(developerName);
            if (rti == null) {
                throw new TestDataFactoryException(
                    'RecordType "' + developerName + '" not found on Account'
                );
            }
            rtCache.put(developerName, rti.getRecordTypeId());
        }
        return rtCache.get(developerName);
    }

    // --- Core Factory Methods ---

    public static List<Account> create(Integer count) {
        return create(count, null, true);
    }

    public static List<Account> create(Integer count, Boolean doInsert) {
        return create(count, null, doInsert);
    }

    public static List<Account> create(Integer count, String recordTypeDeveloperName, Boolean doInsert) {
        List<Account> records = new List<Account>();
        Id rtId = (recordTypeDeveloperName != null)
            ? getRecordTypeId(recordTypeDeveloperName) : null;
        for (Integer i = 0; i < count; i++) {
            Account a = buildRecord(i);
            if (rtId != null) { a.RecordTypeId = rtId; }
            records.add(a);
        }
        if (doInsert) { insert records; }
        return records;
    }

    // --- With Field Overrides ---

    public static List<Account> createWithOverrides(Integer count, Map<String, Object> overrides) {
        return createWithOverrides(count, overrides, true);
    }

    public static List<Account> createWithOverrides(Integer count, Map<String, Object> overrides, Boolean doInsert) {
        List<Account> records = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            Account a = buildRecord(i);
            for (String field : overrides.keySet()) {
                a.put(field, overrides.get(field));
            }
            records.add(a);
        }
        if (doInsert) { insert records; }
        return records;
    }

    // --- Child Record Helper ---

    public static List<Contact> createContactsForAccount(Integer count, Id accountId) {
        return createContactsForAccount(count, accountId, true);
    }

    public static List<Contact> createContactsForAccount(Integer count, Id accountId, Boolean doInsert) {
        List<Contact> contacts = new List<Contact>();
        for (Integer i = 0; i < count; i++) {
            contacts.add(new Contact(
                FirstName = 'Test',
                LastName = 'Contact_' + i,
                AccountId = accountId,
                Email = 'test.contact' + i + '@example.com'
            ));
        }
        if (doInsert) { insert contacts; }
        return contacts;
    }

    private static Account buildRecord(Integer index) {
        return new Account(
            Name = 'Test Account ' + index,
            Industry = 'Technology',
            Type = 'Prospect',
            BillingCity = 'San Francisco',
            BillingState = 'CA'
        );
    }

    public class TestDataFactoryException extends Exception {}
}
```

## Usage Examples

```apex
// Default - 251 records, auto-insert
List<Account> accts = TestDataFactory_Account.create(251);

// With specific RecordType
List<Account> bizAccts = TestDataFactory_Account.create(10, 'Business_Account', true);
List<Account> personAccts = TestDataFactory_Account.create(10, 'Person_Account', true);

// With field overrides (no insert - caller controls DML)
Map<String, Object> overrides = new Map<String, Object>{
    'Industry' => 'Finance',
    'AnnualRevenue' => 5000000
};
List<Account> financeAccts = TestDataFactory_Account.createWithOverrides(50, overrides, false);
insert financeAccts;

// With child contacts
List<Account> accts = TestDataFactory_Account.create(5);
for (Account a : accts) {
    TestDataFactory_Account.createContactsForAccount(3, a.Id);
}
```

## Extending Factories for Custom Fields

Pattern for profile-based test data (Hot/Warm/Cold scoring):

```apex
public class TestDataFactory_Lead_Extended {
    public static List<Lead> createWithProfile(String profile, Integer count) {
        List<Lead> leads = new List<Lead>();
        for (Integer i = 0; i < count; i++) {
            Lead l = new Lead(
                FirstName = 'Test', LastName = 'Lead_' + i,
                Company = 'Test Co ' + i, Status = 'Open'
            );
            switch on profile {
                when 'Hot'  { l.Industry = 'Technology'; l.NumberOfEmployees = 1500; l.Email = 'hot' + i + '@example.com'; }
                when 'Warm' { l.Industry = 'Technology'; l.NumberOfEmployees = 500;  l.Email = 'warm' + i + '@example.com'; }
                when 'Cold' { l.Industry = 'Retail';     l.NumberOfEmployees = 50; }
            }
            leads.add(l);
        }
        return leads;
    }

    // Bulk distribution: crosses 200-record batch boundary
    // createWithDistribution(50, 100, 101) -> 251 leads
    public static List<Lead> createWithDistribution(Integer hot, Integer warm, Integer cold) {
        List<Lead> all = new List<Lead>();
        all.addAll(createWithProfile('Hot', hot));
        all.addAll(createWithProfile('Warm', warm));
        all.addAll(createWithProfile('Cold', cold));
        return all;
    }
}
```

## Key Principles

1. **Always create in lists** - Support bulk operations
2. **Provide doInsert parameter** - Allow caller to control insertion
3. **Use synthetic data** - Never real PII (`@example.com`, `Test_` prefix)
4. **Support relationships** - Parent ID parameters for child records
5. **Cache RecordType lookups** - Query `getRecordTypeInfosByDeveloperName()` once
6. **Include edge cases** - Null values, special characters, boundaries
7. **Annotate with `@isTest`** - Excluded from org code size limit
