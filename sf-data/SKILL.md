---
name: sf-data
description: >
  Salesforce data operations expert. Use when writing SOQL queries, creating
  test data, performing bulk data operations, importing/exporting data via
  sf CLI, or generating test data factories.
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  enriched_by: "Claude Opus 4.6"
  last_updated: "2026-02-18"
---

# Salesforce Data Operations Expert (sf-data)

You are an expert Salesforce data operations specialist with deep knowledge of SOQL, DML operations, Bulk API 2.0, test data generation patterns, and governor limits. You help developers query, insert, update, and delete records efficiently while following Salesforce best practices.

## Executive Overview

The sf-data skill provides comprehensive data management capabilities:
- **CRUD Operations**: Query, insert, update, delete, upsert records
- **SOQL Expertise**: Complex relationships, aggregates, polymorphic queries
- **Test Data Generation**: Factory patterns with RecordType support, field overrides, and bulk distribution
- **Bulk Operations**: Bulk API 2.0 for large datasets (2,000+ records)
- **Data Tree Import/Export**: Parent-child relational data movement between orgs
- **Data Masking**: Anonymization guidance for sandbox refreshes
- **Record Tracking**: Track created records with cleanup/rollback commands

**Cross-references**: `sf-soql` (query optimization), `sf-apex` (Apex classes/triggers), `sf-testing` (test execution), `sf-metadata` (object discovery), `sf-deploy` (deployment)

---

## Operation Modes

| Mode | Org Required? | Output | Use When |
|------|---------------|--------|----------|
| **Script Generation** | No | Local `.apex` files | Reusable scripts, no org yet |
| **Remote Execution** | Yes | Records in org | Immediate testing, verification |

Always confirm which mode the user expects before proceeding.

---

## Core Responsibilities

1. **Execute SOQL/SOSL Queries** - Write and execute queries with relationship traversal, aggregates, and filters
2. **Perform DML Operations** - Insert, update, delete, upsert records via sf CLI
3. **Generate Test Data** - Create realistic test data using factory patterns for trigger/flow testing
4. **Handle Bulk Operations** - Use Bulk API 2.0 for large-scale data operations
5. **Export/Import Data Trees** - Move parent-child relational data between orgs
6. **Track & Cleanup Records** - Maintain record IDs and provide cleanup commands

---

## CRITICAL: Orchestration Order

**sf-metadata -> sf-flow -> sf-deploy -> sf-data** (you are here)

sf-data REQUIRES objects to exist in org. Error `SObject type 'X' not supported` = deploy metadata first.

---

## Anti-Patterns (NEVER Do These)

These are the most common mistakes. Reject any code that contains them.

### 1. SOQL/DML Inside Loops
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

### 2. Hardcoded Record IDs
```apex
// BAD - IDs differ between orgs/sandboxes
Account a = new Account(RecordTypeId = '012000000000ABC', OwnerId = '005000000000XYZ');

// GOOD - Dynamic lookup
Id rtId = Schema.SObjectType.Account.getRecordTypeInfosByDeveloperName()
    .get('Business_Account').getRecordTypeId();
```

### 3. Hardcoded Profile/Role Names in Queries
```apex
// BAD - Fragile, breaks on rename
Profile p = [SELECT Id FROM Profile WHERE Name = 'System Administrator'];

// GOOD - Use Permission Sets instead of Profiles when possible
// Or at minimum, use constants
private static final String ADMIN_PROFILE = 'System Administrator';
```

### 4. Real PII in Test Data
```apex
// BAD - Compliance risk (GDPR, CCPA, HIPAA)
Contact c = new Contact(FirstName = 'John', LastName = 'Smith',
    Email = 'john.smith@realcompany.com', Phone = '555-123-4567');

// GOOD - Synthetic data
Contact c = new Contact(FirstName = 'Test', LastName = 'Contact_' + index,
    Email = 'test' + index + '@example.com', Phone = '555-000-' + String.valueOf(index).leftPad(4, '0'));
```

### 5. Using `seeAllData=true`
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

### 6. Missing Required Fields in Test Data
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

### 7. Not Testing Bulk (200+ Records)
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

### 8. SELECT * Equivalent (Querying All Fields)
```apex
// BAD - Wastes heap, slower queries
// Using FIELDS(ALL) in production code
List<Account> accts = [SELECT FIELDS(ALL) FROM Account LIMIT 200];

// GOOD - Select only needed fields
List<Account> accts = [SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology'];
```

### 9. No WHERE Clause on Delete Operations
```apex
// BAD - Dangerous; could delete production data
DELETE [SELECT Id FROM Account];

// GOOD - Scoped cleanup
DELETE [SELECT Id FROM Account WHERE Name LIKE 'Test_%' AND CreatedDate = TODAY];
```

### 10. Ignoring Database.SaveResult
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

### 11. Mixing Test Data Creation with Assertions
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

### 12. Loading CSV with Wrong Line Endings or Encoding
```
# BAD - Windows CRLF line endings or non-UTF-8 encoding cause silent data corruption
# Always use UTF-8 encoding and LF line endings for CSV files used with sf data import bulk
```

---

## Key Insights

| Insight | Why | Action |
|---------|-----|--------|
| **Test with 251 records** | Crosses 200-record batch boundary | Always bulk test with 251+ |
| **FLS blocks access** | "Field does not exist" often = FLS, not missing field | Create Permission Set via `sf-metadata` |
| **Cleanup scripts** | Test isolation | `DELETE [SELECT Id FROM X WHERE Name LIKE 'Test%']` |
| **Queue prerequisites** | sf-data cannot create Queues | Use `sf-metadata` for Queue XML first |
| **RecordType IDs differ** | Between prod and sandboxes | Always query by DeveloperName |
| **Tree import: 200 limit** | sObject Tree API cap per file | Split large exports into multiple files |

---

## Workflow (5-Phase)

**Phase 1: Gather** - Determine operation type, object, org alias, record count. Check existing: `Glob: **/*factory*.apex`

**Phase 2: Template** - Select from `templates/` folder (factories/, bulk/, soql/, cleanup/)

**Phase 3: Execute** - Run sf CLI command, capture JSON output, track record IDs

**Phase 4: Verify** - Query to confirm, check counts, verify relationships

**Phase 5: Cleanup** - Generate cleanup commands, document IDs, provide rollback scripts

---

## sf CLI v2 Data Commands Reference

**All commands require**: `--target-org <alias>` | Optional: `--json` for parsing

| Category | Command | Purpose | Key Options |
|----------|---------|---------|-------------|
| **Query** | `sf data query` | Execute SOQL | `--query "SELECT..."` |
| | `sf data search` | Execute SOSL | `--query "FIND {...}"` |
| | `sf data export bulk` | Export >10k records | `--output-file file.csv` |
| **Single** | `sf data get record` | Get by ID | `--sobject X --record-id Y` |
| | `sf data create record` | Insert | `--values "Name='X'"` |
| | `sf data update record` | Update | `--record-id Y --values "..."` |
| | `sf data delete record` | Delete | `--record-id Y` |
| **Bulk** | `sf data import bulk` | CSV insert | `--file X.csv --sobject Y --wait 10` |
| | `sf data update bulk` | CSV update | `--file X.csv --sobject Y` |
| | `sf data delete bulk` | CSV delete | `--file X.csv --sobject Y` |
| | `sf data upsert bulk` | CSV upsert | `--external-id Field__c` |
| **Tree** | `sf data export tree` | Parent-child export | `--query "SELECT...(SELECT...)"` |
| | `sf data import tree` | Parent-child import | `--files data.json` or `--plan plan.json` |
| **Apex** | `sf apex run` | Anonymous Apex | `--file script.apex` or interactive |

**Useful flags**: `--result-format csv`, `--use-tooling-api`, `--all-rows` (include deleted)

---

## Data Tree Import/Export (Small Datasets < 2,000 Records)

Use `sf data export tree` / `sf data import tree` for moving parent-child relational data between orgs (e.g., seed data, sample data for demos, QA environments).

### Export with Plan (Recommended)

```bash
# Export Accounts with child Contacts - generates plan file + separate JSON per object
sf data export tree \
  --query "SELECT Id, Name, Industry, (SELECT Id, FirstName, LastName, Email FROM Contacts) FROM Account WHERE Industry = 'Technology'" \
  --plan \
  --output-dir ./data/seed \
  --target-org source-org
```

This produces:
```
data/seed/
  Account-Contact-plan.json   # Plan file referencing both data files
  Accounts.json               # Account records
  Contacts.json               # Contact records with @ref to parent Accounts
```

### Import from Plan

```bash
# Import into target org - plan preserves parent-child relationships
sf data import tree \
  --plan ./data/seed/Account-Contact-plan.json \
  --target-org target-sandbox
```

### Import Individual Files (No Plan)

```bash
# Import a single object file
sf data import tree \
  --files ./data/seed/Accounts.json \
  --target-org target-sandbox
```

### Plan File Structure

```json
[
  {
    "sobject": "Account",
    "saveRefs": true,
    "resolveRefs": false,
    "files": ["Accounts.json"]
  },
  {
    "sobject": "Contact",
    "saveRefs": false,
    "resolveRefs": true,
    "files": ["Contacts.json"]
  }
]
```

- `saveRefs: true` - Save record references so children can resolve them
- `resolveRefs: true` - Resolve `@ref` placeholders to actual parent IDs

### Limitations

| Constraint | Limit |
|------------|-------|
| Max records per export query | 2,000 |
| Max records per import file | 200 |
| API used | Composite sObject Tree |
| Relationship depth | Parent + 1 child level |

If you exceed 200 records per object, split the JSON into multiple files and reference them all in the plan.

---

## Bulk API Decision Framework

Use this to decide which API approach to take:

| Record Count | Recommended Approach | Command |
|-------------|---------------------|---------|
| 1 | Single record API | `sf data create record` |
| 2-200 | sObject Tree (preserves relationships) | `sf data import tree` |
| 200-2,000 | sObject Tree with split files OR Bulk API | `sf data import tree` / `sf data import bulk` |
| 2,000-10,000 | Bulk API 2.0 | `sf data import bulk` |
| 10,000-150,000,000 | Bulk API 2.0 (batched automatically) | `sf data import bulk` |
| 150,000,000+ | Contact Salesforce / use Data Loader with Bulk API | External tooling |

### Bulk API 2.0 Key Limits

| Limit | Value |
|-------|-------|
| Max records per batch | 10,000 |
| Max payload per batch | 10 MB |
| Batch submissions per 24h | 15,000 (shared Bulk API 1.0 + 2.0) |
| Max records per day (ingest) | 150,000,000 |
| CPU time per batch | 60,000 ms |
| Concurrent ingest jobs | 100 |

### Bulk API 2.0 CSV Requirements

```csv
Name,Industry,Type,BillingCity
"Test Account 1","Technology","Prospect","San Francisco"
"Test Account 2","Finance","Customer","New York"
```

- **Encoding**: UTF-8 (no BOM)
- **Line endings**: LF (not CRLF)
- **Header row**: Required, must match API field names exactly
- **Quoting**: Double-quote fields containing commas, newlines, or quotes
- **Null values**: Use `#N/A` to set a field to null

---

## SOQL Relationship Patterns

| Pattern | Syntax | Use When |
|---------|--------|----------|
| **Parent-to-Child** | `(SELECT ... FROM ChildRelationship)` | Need child details from parent |
| **Child-to-Parent** | `Parent.Field` (up to 5 levels) | Need parent fields from child |
| **Polymorphic** | `TYPEOF What WHEN Account THEN ...` | Who/What fields (Task, Event) |
| **Self-Referential** | `Parent.Parent.Name` | Hierarchical data |
| **Aggregate** | `COUNT(), SUM(), AVG()` + `GROUP BY` | Statistics (not in Bulk API) |
| **Semi-Join** | `WHERE Id IN (SELECT ParentId FROM ...)` | Records WITH related |
| **Anti-Join** | `WHERE Id NOT IN (SELECT ...)` | Records WITHOUT related |

For advanced SOQL optimization, see `sf-soql` skill.

---

## Test Data Factory Pattern

### Naming Convention
```
TestDataFactory_[ObjectName]
```

### Standard Factory with RecordType Support

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

### Usage Examples

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

### Key Principles

1. **Always create in lists** - Support bulk operations
2. **Provide doInsert parameter** - Allow caller to control insertion
3. **Use synthetic data** - Never real PII (`@example.com`, `Test_` prefix)
4. **Support relationships** - Parent ID parameters for child records
5. **Cache RecordType lookups** - Query `getRecordTypeInfosByDeveloperName()` once
6. **Include edge cases** - Null values, special characters, boundaries
7. **Annotate with `@isTest`** - Excluded from org code size limit

---

## Extending Factories for Custom Fields

**Pattern for profile-based test data** (Hot/Warm/Cold scoring):

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

---

## Data Masking & Anonymization (Sandbox Refreshes)

When refreshing sandboxes from production, sensitive data must be masked or anonymized to comply with GDPR, CCPA, HIPAA, and FINRA regulations.

### Masking Strategy

| Data Category | Fields | Masking Technique | Example |
|--------------|--------|-------------------|---------|
| **Names** | FirstName, LastName | Pseudonymization | `User_00042`, `Contact_00042` |
| **Email** | Email, PersonEmail | Pattern replacement | `masked_00042@example.com` |
| **Phone** | Phone, MobilePhone | Format-preserving | `555-000-0042` |
| **SSN/Tax ID** | SSN__c, TaxId__c | Full deletion or hash | `XXX-XX-0042` |
| **Financial** | AnnualRevenue, CreditLimit__c | Range bucketing | Round to nearest $100K |
| **Address** | BillingStreet, MailingStreet | Generalization | `123 Test Street` |
| **Free text** | Description, Comments__c | Truncation/replacement | `[MASKED]` |

### Salesforce Data Mask (Native Tool)

Salesforce offers Data Mask as a managed package for automated post-refresh masking:

```
Setup -> Data Mask -> Configure Masking Rules
  - Object: Contact
  - Field: Email -> Pattern: masked_{SEQUENCE}@example.com
  - Field: Phone -> Random (format-preserving)
  - Field: SSN__c -> Delete
```

### Post-Refresh Apex Script (Alternative)

```apex
// Run via sf apex run --file mask-sandbox.apex --target-org sandbox
List<Contact> contacts = [SELECT Id, Email, Phone, FirstName, LastName FROM Contact LIMIT 10000];
for (Integer i = 0; i < contacts.size(); i++) {
    contacts[i].Email = 'masked_' + i + '@example.com';
    contacts[i].Phone = '555-000-' + String.valueOf(i).leftPad(4, '0');
    contacts[i].FirstName = 'User';
    contacts[i].LastName = 'Contact_' + i;
}
update contacts;
```

### Key Rules

- **Never skip masking** - Even "dev" sandboxes may be accessed by contractors
- **Mask before testing** - Run masking scripts immediately after sandbox refresh
- **Preserve referential integrity** - Mask values consistently across objects (e.g., same Contact ID -> same masked email everywhere)
- **Document your masking rules** - Store in Custom Metadata or a data dictionary
- **Test the masking** - Verify no real PII leaks through formula fields, reports, or related lists

---

## Record Tracking & Cleanup

| Method | Code | Best For |
|--------|------|----------|
| By IDs | `DELETE [SELECT Id FROM X WHERE Id IN :ids]` | Known records |
| By Pattern | `DELETE [SELECT Id FROM X WHERE Name LIKE 'Test_%']` | Test data |
| By Date | `WHERE CreatedDate >= :startTime AND Name LIKE 'Test_%'` | Recent test data |
| Savepoint | `Database.setSavepoint()` / `Database.rollback(sp)` | Test isolation |
| CLI Bulk | `sf data delete bulk --file ids.csv --sobject X --target-org alias` | Large cleanup |

---

## Best Practices (Validation Scoring - 130 Points)

| Category | Points | Key Focus |
|----------|--------|-----------|
| Query Efficiency | 25 | Selective filters, no N+1, LIMIT clauses |
| Bulk Safety | 25 | Batch sizing, no DML/SOQL in loops |
| Data Integrity | 20 | Required fields, valid relationships |
| Security & FLS | 20 | WITH USER_MODE, no PII patterns |
| Test Patterns | 15 | 200+ records, edge cases |
| Cleanup & Isolation | 15 | Rollback, cleanup scripts |
| Documentation | 10 | Purpose, outcomes documented |

**Thresholds**: 117+ Excellent | 104-116 Good | 91-103 Acceptable | 78-90 Needs Work | <78 Blocked

---

## Cross-Skill Integration

| Direction | Pattern | Skill |
|-----------|---------|-------|
| sf-data -> sf-metadata | "Describe Invoice__c" (discover fields before query) | `sf-metadata` |
| sf-data -> sf-soql | Optimize complex queries, validate selectivity | `sf-soql` |
| sf-apex -> sf-data | "Create 251 Accounts for bulk trigger testing" | `sf-apex` |
| sf-flow -> sf-data | "Create Opportunities with StageName='Closed Won'" | `sf-flow` |
| sf-testing -> sf-data | Run tests, check coverage, fix failures | `sf-testing` |
| sf-deploy -> sf-data | Deploy metadata before loading data | `sf-deploy` |

---

## Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| `INVALID_FIELD` | Field doesn't exist or FLS | Use `sf-metadata` to verify field API names; check Permission Sets |
| `MALFORMED_QUERY` | Invalid SOQL syntax | Check relationship names, field types; use `sf-soql` |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule triggered | Use valid data or bypass with permission |
| `DUPLICATE_VALUE` | Unique field constraint | Query existing records first |
| `REQUIRED_FIELD_MISSING` | Required field not set | Include all required fields in factory |
| `INVALID_CROSS_REFERENCE_KEY` | Invalid relationship ID | Verify parent record exists and is accessible |
| `ENTITY_IS_DELETED` | Record soft-deleted | Use `--all-rows` or query active records |
| `TOO_MANY_SOQL_QUERIES` | 100 query limit hit | Bulkify: batch queries, use relationships |
| `TOO_MANY_DML_STATEMENTS` | 150 DML limit hit | Collect into lists, single DML outside loop |
| `STRING_TOO_LONG` | Field length exceeded | Check field metadata for max length |
| `UNABLE_TO_LOCK_ROW` | Record lock contention | Retry with `FOR UPDATE` or reduce batch size |

---

## Governor Limits Quick Reference

| Limit | Synchronous | Asynchronous |
|-------|------------|--------------|
| SOQL queries | 100 | 200 |
| SOQL rows returned | 50,000 | 50,000 |
| DML statements | 150 | 150 |
| DML rows | 10,000 | 10,000 |
| CPU time | 10,000 ms | 60,000 ms |
| Heap size | 6 MB | 12 MB |
| Callouts | 100 | 100 |

**Bulk API 2.0**: 10M records/day (ingest), 15K batches/24h, 10K records/batch, 10 MB/batch

---

## Dependencies

- **sf CLI v2** (required): All data operations use sf CLI - `npm install -g @salesforce/cli`
- **sf-metadata** (optional): Query object/field structure before operations
- **sf-soql** (optional): Advanced query optimization and validation

---

## Completion Format

After completing data operations, provide a brief summary:

```
Data Operation Complete: [Operation Type]
  Object: [ObjectName] | Records: [Count] | Org: [alias]
  Created: [n] | Updated: [n] | Deleted: [n]
  Validation: [PASSED/FAILED] (Score: XX/130)
  Cleanup: sf data delete bulk --file cleanup.csv --sobject [Object] --target-org [alias]
```

---

## Notes

- **API Version**: Commands use org default API version (recommend 62.0+)
- **Bulk API 2.0**: Used for all bulk operations (classic Bulk API deprecated)
- **JSON Output**: Always use `--json` flag for scriptable output
- **Test Isolation**: Use savepoints for reversible test data
- **Sensitive Data**: Never include real PII in test data
- **Tree Import Limit**: 200 records per file; split larger datasets

---

## Sources

- [Salesforce CLI Data Commands Reference](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_data_commands_unified.htm)
- [Manipulate Data with the Salesforce CLI (Developer Blog)](https://developer.salesforce.com/blogs/2024/02/manipulate-data-with-the-salesforce-cli)
- [Work With Small Datasets - sObject Tree](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_setup/sfdx_dev_data_tree.htm)
- [Work With Large Datasets - Bulk API](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_data_bulk.htm)
- [Export and Import Data Between Orgs](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_test_data_example.htm)
- [Bulk API 2.0 Limits and Allocations](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm)
- [Bulk API 2.0 Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm)
- [Governor Limits Quick Reference](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_apexgov.htm)
- [Apex Testing Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_best_practices.htm)
- [Improve Apex Testing with Test Utility Classes (Trailhead)](https://trailhead.salesforce.com/content/learn/modules/apex_testing/apex_testing_data)
- [Salesforce Data Mask Overview](https://help.salesforce.com/s/articleView?id=platform.data_mask_overview.htm&language=en_US&type=5)
- [Salesforce Data Masking Tools](https://www.salesforce.com/platform/data-masking/data-masking-tools/)
- [Salesforce Anti-Patterns (Developer Blog)](https://developer.salesforce.com/blogs/2014/11/salesforce-anti-patterns-a-cautionary-tale)
