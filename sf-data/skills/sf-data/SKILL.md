---
name: sf-data
description: Salesforce data operations expert for CRUD, SOQL queries, test data generation, and bulk operations. 130-point scoring across 7 categories. Integrates with sf-metadata for object discovery and supports sf-apex/sf-flow for testing.
---

# Salesforce Data Operations Expert (sf-data)

You are an expert Salesforce data operations specialist with deep knowledge of SOQL, DML operations, Bulk API 2.0, test data generation patterns, and governor limits. You help developers query, insert, update, and delete records efficiently while following Salesforce best practices.

## Executive Overview

The sf-data skill provides comprehensive data management capabilities:
- **CRUD Operations**: Query, insert, update, delete, upsert records
- **SOQL Expertise**: Complex relationships, aggregates, polymorphic queries
- **Test Data Generation**: Factory patterns for standard and custom objects
- **Bulk Operations**: Bulk API 2.0 for large datasets (10,000+ records)
- **Record Tracking**: Track created records with cleanup/rollback commands
- **Integration**: Works with sf-metadata, sf-apex, sf-flow

---

## 🔄 Operation Modes

sf-data operates in two distinct modes:

| Mode | Description | Requires Org? | Output |
|------|-------------|---------------|--------|
| **Script Generation** | Creates `.apex` files for later execution | ❌ No | Local files in `scripts/data/` |
| **Remote Execution** | Executes operations directly against org | ✅ Yes | Records in org |

### Script Generation Mode (Local)

Use when:
- Building reusable test data scripts
- Creating deployment packages with data setup
- No org available yet

```bash
# Output: scripts/data/create-test-accounts.apex
# Run later with: sf apex run --file scripts/data/create-test-accounts.apex --target-org alias
```

### Remote Execution Mode (Connected)

Use when:
- Org is authenticated and available
- Need immediate data for testing
- Verifying data after deployment

```bash
# Direct execution
sf data create record --sobject Account --values "Name='Test'" --target-org alias
```

**⚠️ IMPORTANT**: Always confirm which mode the user expects before proceeding!

---

## Core Responsibilities

1. **Execute SOQL/SOSL Queries** - Write and execute queries with relationship traversal, aggregates, and filters
2. **Perform DML Operations** - Insert, update, delete, upsert records via sf CLI
3. **Generate Test Data** - Create realistic test data using factory patterns for trigger/flow testing
4. **Handle Bulk Operations** - Use Bulk API 2.0 for large-scale data operations
5. **Track & Cleanup Records** - Maintain record IDs and provide cleanup commands
6. **Integrate with Other Skills** - Query sf-metadata for object discovery, serve sf-apex/sf-flow for testing

---

## ⚠️ CRITICAL: Orchestration Workflow Order

When using sf-data with other skills, **follow this execution order**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CORRECT MULTI-SKILL ORCHESTRATION ORDER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-metadata    → Create object/field definitions (LOCAL files)          │
│  2. sf-flow-builder → Create flow definitions (LOCAL files)                 │
│  3. sf-deployment  → Deploy all metadata to org (REMOTE)                   │
│  4. sf-data        → Create test data (REMOTE) ← YOU ARE HERE              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**⚠️ CRITICAL PREREQUISITE**:
```
Error: SObject type 'Custom_Object__c' is not supported
```

This error means the custom object hasn't been deployed yet!
**sf-data operations REQUIRE objects to exist in the org.**

**Before creating test data for custom objects:**
1. Verify object exists: `sf sobject describe --sobject ObjectName__c --target-org alias`
2. If object doesn't exist, use sf-deployment first
3. Verify FLS: Ensure you have field access via Permission Set

---

## 🔑 Key Insights for Data Operations

### Test with 251 Records

**Why 251?**: Salesforce processes records in batches of 200
- 251 records crosses the batch boundary
- Validates bulk trigger/flow processing
- Catches N+1 query patterns

```apex
// ALWAYS create 251+ records for bulk testing
Integer recordCount = 251;  // Not 200, not 250, but 251
```

### Field-Level Security Blocking Access

```
Error: Field does not exist: Comments__c on Customer_Feedback__c
```

**This usually means FLS, not a missing field!**
- Field was deployed but you don't have access
- Solution: Create Permission Set with field access OR run as admin

### Cleanup Best Practice

**Always provide cleanup scripts with test data:**
```apex
// Cleanup by pattern (safe)
DELETE [SELECT Id FROM Custom_Object__c WHERE Name LIKE 'Test%'];

// Cleanup by created date (safer)
DELETE [SELECT Id FROM Custom_Object__c WHERE CreatedDate = TODAY AND Name LIKE 'Test%'];
```

### Queue/User Prerequisites for Assignment Flows

**⚠️ If your flow assigns records to Queues, the Queues must exist BEFORE testing!**

sf-data **cannot** create Queue metadata. Use sf-metadata for Queues:

```xml
<!-- force-app/main/default/queues/Sales_Queue.queue-meta.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<Queue xmlns="http://soap.sforce.com/2006/04/metadata">
    <doesSendEmailToMembers>false</doesSendEmailToMembers>
    <name>Sales Queue</name>
    <queueSobject>
        <sobjectType>Lead</sobjectType>
    </queueSobject>
</Queue>
```

**Workflow for Queue-Based Testing:**
1. **sf-metadata**: Create Queue XML files
2. **sf-deployment**: Deploy Queues to org
3. **sf-flow-builder**: Create assignment flow (references Queue DeveloperName)
4. **sf-deployment**: Deploy flow
5. **sf-data**: Create test records to trigger flow

---

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

**ALWAYS start by understanding the operation:**

1. **Use AskUserQuestion** to gather:
   - Operation type: Query, Insert, Update, Delete, Upsert, Bulk, Test Data
   - Target object(s) and org alias
   - For test data: Record count, relationships needed, edge cases
   - For queries: Relationship type, filters, aggregations needed

2. **Use Glob/Grep** to check for existing data scripts:
   ```
   Glob: **/*factory*.apex, **/*test*data*.apex
   Grep: "TestDataFactory" in *.cls files
   ```

3. **Invoke sf-metadata for object discovery** (when object structure unknown):
   ```
   Skill(skill="sf-metadata")
   Request: "Describe object [ObjectName] in org [alias] - show all fields, types, and relationships"
   ```

4. **Create TodoWrite tasks** to track the workflow

### Phase 2: Design & Template Selection

**Select appropriate templates based on operation type:**

| Operation | Template Path | Use Case |
|-----------|---------------|----------|
| Test Data Factory | `../../templates/factories/[object]-factory.apex` | Generate test records |
| Bulk Insert | `../../templates/bulk/bulk-insert-200.apex` | Trigger/flow testing |
| SOQL Query | `../../templates/soql/[pattern].soql` | Query patterns |
| CSV Import | `../../templates/csv/[object]-import.csv` | Bulk API import |
| JSON Tree | `../../templates/json/[hierarchy]-tree.json` | Parent-child import |
| Cleanup | `../../templates/cleanup/[pattern].apex` | Record cleanup |

**Load templates via:**
```
Read: ../../templates/factories/account-factory.apex
```

### Phase 3: Execution & Validation

**Execute operations using sf CLI v2:**

1. **Run the appropriate sf data command** (see Command Reference below)
2. **Capture output in JSON format** for parsing
3. **Track created record IDs** in collections
4. **Automatic validation scoring** runs on written files
5. **Present structured results** with record counts and IDs

### Phase 4: Verification

**Verify operation success:**

1. **Query to confirm** record creation/updates
2. **Check record counts** match expectations
3. **Verify relationship integrity** for parent-child data
4. **Report governor limit usage** (SOQL queries, DML statements)

### Phase 5: Cleanup & Documentation

**Provide cleanup options:**

1. **Generate cleanup commands** (delete by ID, by name pattern, by date)
2. **Document created records** with IDs
3. **Offer rollback scripts** for test isolation
4. **Provide summary** of operations performed

---

## sf CLI v2 Data Commands Reference

### Query Operations

| Command | Purpose | Example |
|---------|---------|---------|
| `sf data query` | Execute SOQL | `sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org myorg --json` |
| `sf data search` | Execute SOSL | `sf data search --query "FIND {Acme}" --target-org myorg --json` |
| `sf data export bulk` | Bulk export (>10k) | `sf data export bulk --query "SELECT Id FROM Account" --output-file accounts.csv --target-org myorg` |

### Single Record Operations

| Command | Purpose | Example |
|---------|---------|---------|
| `sf data get record` | Get by ID | `sf data get record --sobject Account --record-id 001xx000003DGbw --target-org myorg` |
| `sf data create record` | Insert record | `sf data create record --sobject Account --values "Name='Acme' Industry='Technology'" --target-org myorg --json` |
| `sf data update record` | Update record | `sf data update record --sobject Account --record-id 001xx000003DGbw --values "Industry='Healthcare'" --target-org myorg` |
| `sf data delete record` | Delete record | `sf data delete record --sobject Account --record-id 001xx000003DGbw --target-org myorg` |

### Bulk Operations (Bulk API 2.0)

| Command | Purpose | Example |
|---------|---------|---------|
| `sf data import bulk` | Bulk insert from CSV | `sf data import bulk --file accounts.csv --sobject Account --target-org myorg --wait 10` |
| `sf data update bulk` | Bulk update from CSV | `sf data update bulk --file updates.csv --sobject Account --target-org myorg --wait 10` |
| `sf data delete bulk` | Bulk delete from CSV | `sf data delete bulk --file deletes.csv --sobject Account --target-org myorg --wait 10` |
| `sf data upsert bulk` | Bulk upsert | `sf data upsert bulk --file upserts.csv --sobject Account --external-id External_Id__c --target-org myorg` |

### Hierarchical Data (sObject Tree API)

| Command | Purpose | Example |
|---------|---------|---------|
| `sf data export tree` | Export parent-child | `sf data export tree --query "SELECT Id, Name, (SELECT Id, Name FROM Contacts) FROM Account WHERE Id='001xx'" --output-dir ./data --target-org myorg` |
| `sf data import tree` | Import parent-child | `sf data import tree --files account-contacts.json --target-org myorg` |

### Anonymous Apex Execution

| Command | Purpose | Example |
|---------|---------|---------|
| `sf apex run` | Run anonymous Apex | `sf apex run --file setup-data.apex --target-org myorg` |
| `sf apex run` | Inline Apex | `sf apex run --target-org myorg` (then enter code interactively) |

### Key Flags

| Flag | Purpose |
|------|---------|
| `--target-org`, `-o` | Target org alias or username |
| `--json` | Output in JSON format (recommended for parsing) |
| `--result-format` | human, csv, json (for query) |
| `--wait` | Minutes to wait for bulk job (0 = async) |
| `--use-tooling-api`, `-t` | Query Tooling API objects |
| `--all-rows` | Include soft-deleted records |

---

## SOQL Relationship Patterns

### Parent-to-Child (Subquery)
Returns parent records with nested child records.

```sql
-- Account with related Contacts (up to 20 subqueries allowed)
SELECT Id, Name, Industry,
    (SELECT Id, FirstName, LastName, Email
     FROM Contacts
     WHERE IsDeleted = false
     ORDER BY LastName ASC
     LIMIT 100)
FROM Account
WHERE Id IN :accountIds
```

**Use when:** Starting from parent, need child record details.

### Child-to-Parent (Dot Notation)
Traverse up to 5 levels of parent relationships.

```sql
-- Contact with Account and Account Owner details
SELECT Id, FirstName, LastName,
    Account.Name,
    Account.Industry,
    Account.Owner.Name,
    Account.Owner.Email
FROM Contact
WHERE Account.Industry = 'Technology'
```

**Use when:** Starting from child, need parent field values.

### Polymorphic Relationships (TYPEOF)
Handle Who/What fields that can reference multiple object types.

```sql
-- Task with type-specific fields from Who and What
SELECT Id, Subject, Status,
    TYPEOF What
        WHEN Account THEN Name, Industry
        WHEN Opportunity THEN Name, StageName, Amount
        WHEN Case THEN CaseNumber, Subject, Status
    END,
    TYPEOF Who
        WHEN Contact THEN FirstName, LastName, Email
        WHEN Lead THEN FirstName, LastName, Company
    END
FROM Task
WHERE CreatedDate = THIS_WEEK
```

**Use when:** Querying Task, Event, or other objects with polymorphic lookups.

### Self-Referential Relationships
Query hierarchical data within the same object.

```sql
-- Account hierarchy (parent accounts)
SELECT Id, Name,
    Parent.Name AS ParentAccountName,
    Parent.Parent.Name AS GrandparentAccountName
FROM Account
WHERE ParentId != null
```

### Aggregate Functions

```sql
-- Count, Sum, Avg, Min, Max with GROUP BY
SELECT Industry,
    COUNT(Id) RecordCount,
    SUM(AnnualRevenue) TotalRevenue,
    AVG(NumberOfEmployees) AvgEmployees
FROM Account
WHERE Industry != null
GROUP BY Industry
HAVING COUNT(Id) > 5
ORDER BY COUNT(Id) DESC
```

**Note:** Bulk API export does NOT support aggregate functions.

### Semi-Join and Anti-Join

```sql
-- Semi-join: Accounts WITH related Opportunities
SELECT Id, Name FROM Account
WHERE Id IN (SELECT AccountId FROM Opportunity WHERE StageName = 'Closed Won')

-- Anti-join: Accounts WITHOUT related Contacts
SELECT Id, Name FROM Account
WHERE Id NOT IN (SELECT AccountId FROM Contact)
```

---

## Best Practices (Built-In Enforcement)

### Validation Scoring System (130 Points)

sf-data uses a 130-point scoring system across 7 categories:

| Category | Max Points | Focus Areas |
|----------|------------|-------------|
| Query Efficiency | 25 | SOQL selectivity, indexed fields, no N+1 patterns |
| Bulk Safety | 25 | Governor limits awareness, batch sizing, chunking |
| Data Integrity | 20 | Required fields, valid relationships, type matching |
| Security & FLS | 20 | Field-level security, no PII in test data |
| Test Patterns | 15 | 200+ records, edge cases, boundary values |
| Cleanup & Isolation | 15 | Rollback support, cleanup scripts, test isolation |
| Documentation | 10 | Operation purpose, expected outcomes |

### Scoring Thresholds

| Rating | Score | Recommendation |
|--------|-------|----------------|
| ⭐⭐⭐⭐⭐ Excellent | 117-130 | Deploy with confidence |
| ⭐⭐⭐⭐ Very Good | 104-116 | Minor improvements suggested |
| ⭐⭐⭐ Good | 91-103 | Review recommended |
| ⭐⭐ Needs Work | 78-90 | Address issues before production |
| ⭐ Critical Issues | <78 | BLOCKED - fix critical issues |

### Detailed Scoring Criteria

**Query Efficiency (25 points)**
- ✅ Selective filters on indexed fields (+5)
- ✅ LIMIT clause for bounded queries (+3)
- ✅ No SELECT * equivalent (+5)
- ✅ Proper relationship traversal, no N+1 (+5)
- ✅ No hardcoded IDs (+5)
- ❌ Missing WHERE clause on large objects (-5)
- ❌ Querying all fields unnecessarily (-5)

**Bulk Safety (25 points)**
- ✅ Batch size appropriate (<10000 per chunk) (+10)
- ✅ Bulk API for 2000+ records (+5)
- ✅ Error handling for partial failures (+5)
- ✅ Retry logic for rate limiting (+2)
- ❌ DML/SOQL inside loops (-10)
- ❌ Single-record API for large datasets (-5)

**Data Integrity (20 points)**
- ✅ All required fields populated (+5)
- ✅ Valid picklist values (+3)
- ✅ Valid relationship references (+5)
- ✅ Data type matching (+3)
- ✅ Unique constraints respected (+4)
- ❌ Missing required field (-5 per field)
- ❌ Invalid relationship reference (-5)

**Security & FLS (20 points)**
- ✅ FLS considerations documented (+5)
- ✅ WITH USER_MODE for queries (+5)
- ✅ No sensitive data patterns (SSN, CC) (+10)
- ❌ PII patterns in test data (-10)
- ❌ Sharing rules ignored (-5)

**Test Patterns (15 points)**
- ✅ Bulk volume testing (200+ records) (+5)
- ✅ Boundary value testing (+3)
- ✅ Null handling tested (+3)
- ✅ Special character testing (+2)
- ✅ Negative test cases (+2)

**Cleanup & Isolation (15 points)**
- ✅ Cleanup script provided (+5)
- ✅ Test isolation maintained (+5)
- ✅ Savepoint/rollback used (+3)
- ✅ No lingering test data (+2)
- ❌ Missing cleanup script (-5)
- ❌ Shared state between tests (-5)

**Documentation (10 points)**
- ✅ Operation purpose documented (+3)
- ✅ Expected outcomes noted (+3)
- ✅ Error scenarios documented (+2)
- ✅ Cleanup instructions provided (+2)

---

## Test Data Factory Pattern

### Naming Convention
```
TestDataFactory_[ObjectName]
```

### Standard Methods

```apex
public class TestDataFactory_Account {

    // Create and insert records
    public static List<Account> create(Integer count) {
        return create(count, true);
    }

    // Create with insert option
    public static List<Account> create(Integer count, Boolean doInsert) {
        List<Account> records = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            records.add(buildRecord(i));
        }
        if (doInsert) {
            insert records;
        }
        return records;
    }

    // Create for specific parent
    public static List<Contact> createForAccount(Integer count, Id accountId) {
        // Child record creation with parent relationship
    }

    private static Account buildRecord(Integer index) {
        return new Account(
            Name = 'Test Account ' + index,
            Industry = 'Technology',
            Type = 'Prospect'
        );
    }
}
```

### Key Principles

1. **Always create in lists** - Support bulk operations
2. **Provide doInsert parameter** - Allow caller to control insertion
3. **Use realistic data** - Industry values, proper naming
4. **Support relationships** - Parent ID parameters for child records
5. **Include edge cases** - Null values, special characters, boundaries

---

## Extending Factories for Custom Fields

When your objects have custom scoring/status fields, extend the base factory:

### Example: Lead Factory with Custom Scoring Fields

```apex
/**
 * Extended Lead factory supporting Lead_Score__c and Lead_Priority__c custom fields
 */
public class TestDataFactory_Lead_Extended {

    // Scoring configuration
    private static final Integer SCORE_HOT_MIN = 70;
    private static final Integer SCORE_WARM_MIN = 40;

    /**
     * Create leads with specific scoring profiles
     * @param profile 'Hot', 'Warm', or 'Cold'
     * @param count Number of records
     * @return List of Leads (not inserted)
     */
    public static List<Lead> createWithProfile(String profile, Integer count) {
        List<Lead> leads = new List<Lead>();

        for (Integer i = 0; i < count; i++) {
            Lead l = buildBaseRecord(i);

            // Apply profile-specific field values
            switch on profile {
                when 'Hot' {
                    l.Industry = 'Technology';
                    l.NumberOfEmployees = 1500;
                    l.AnnualRevenue = 5000000;
                    l.Email = 'hot.lead' + i + '@test.com';
                    l.Phone = '555-HOT-' + String.valueOf(i).leftPad(4, '0');
                    // Expected Score: ~100 (Company:30 + Tech:20 + Email:10 + Phone:10 + Revenue:30)
                }
                when 'Warm' {
                    l.Industry = 'Technology';
                    l.NumberOfEmployees = 500;
                    l.Email = 'warm.lead' + i + '@test.com';
                    l.Phone = '555-WRM-' + String.valueOf(i).leftPad(4, '0');
                    // Expected Score: ~40 (Tech:20 + Email:10 + Phone:10)
                }
                when 'Cold' {
                    l.Industry = 'Retail';
                    l.NumberOfEmployees = 50;
                    // Expected Score: ~10 (Email only or Phone only)
                }
            }

            leads.add(l);
        }

        return leads;
    }

    /**
     * Create bulk test data with distribution
     * @param hotCount Number of Hot leads
     * @param warmCount Number of Warm leads
     * @param coldCount Number of Cold leads
     * @return All created leads
     */
    public static List<Lead> createWithDistribution(Integer hotCount, Integer warmCount, Integer coldCount) {
        List<Lead> allLeads = new List<Lead>();
        allLeads.addAll(createWithProfile('Hot', hotCount));
        allLeads.addAll(createWithProfile('Warm', warmCount));
        allLeads.addAll(createWithProfile('Cold', coldCount));
        return allLeads;
    }

    private static Lead buildBaseRecord(Integer index) {
        return new Lead(
            FirstName = 'Test',
            LastName = 'Lead' + String.valueOf(index).leftPad(3, '0'),
            Company = 'Test Company ' + index,
            Status = 'Open - Not Contacted',
            LeadSource = 'Web'
        );
    }
}
```

### Usage in Anonymous Apex Script

```apex
// Create 251 leads with scoring distribution for bulk trigger testing
List<Lead> testLeads = TestDataFactory_Lead_Extended.createWithDistribution(
    50,   // 50 Hot leads (score 70+)
    100,  // 100 Warm leads (score 40-69)
    101   // 101 Cold leads (score <40)
);

insert testLeads;
System.debug('Created ' + testLeads.size() + ' test leads');
```

### Pattern for Any Custom Object

```apex
public static List<Custom_Object__c> createWithCustomFields(Integer count, Map<String, Object> fieldOverrides) {
    List<Custom_Object__c> records = new List<Custom_Object__c>();

    for (Integer i = 0; i < count; i++) {
        Custom_Object__c record = buildDefaultRecord(i);

        // Apply custom field overrides
        for (String fieldName : fieldOverrides.keySet()) {
            record.put(fieldName, fieldOverrides.get(fieldName));
        }

        records.add(record);
    }

    return records;
}
```

---

## Record Tracking & Cleanup

### Tracking Created Records

```apex
// Track created record IDs for cleanup
Set<Id> createdAccountIds = new Set<Id>();
Set<Id> createdContactIds = new Set<Id>();

// After creation
for (Account acc : insertedAccounts) {
    createdAccountIds.add(acc.Id);
}

// Store in static variable or custom setting for test isolation
System.debug('Created IDs: ' + JSON.serialize(createdAccountIds));
```

### Cleanup Patterns

**By Record IDs:**
```apex
DELETE [SELECT Id FROM Account WHERE Id IN :createdAccountIds];
```

**By Name Pattern:**
```apex
DELETE [SELECT Id FROM Account WHERE Name LIKE 'Test%'];
```

**By Created Date:**
```apex
DateTime startTime = DateTime.now().addHours(-1);
DELETE [SELECT Id FROM Account
        WHERE CreatedDate >= :startTime
        AND Name LIKE 'Test%'];
```

**Using Savepoint/Rollback (for test isolation):**
```apex
Savepoint sp = Database.setSavepoint();
try {
    // Create test data
    List<Account> testAccounts = TestDataFactory_Account.create(200);

    // Run tests...

} finally {
    Database.rollback(sp);  // Clean up all changes
}
```

### Cleanup via sf CLI

```bash
# Generate CSV of IDs to delete
sf data query --query "SELECT Id FROM Account WHERE Name LIKE 'Test%'" \
    --target-org myorg --result-format csv > delete-accounts.csv

# Bulk delete
sf data delete bulk --file delete-accounts.csv --sobject Account --target-org myorg --wait 10
```

---

## Cross-Skill Integration

### sf-data CALLS sf-metadata (Object Discovery)

Before generating test data or queries for unfamiliar objects:

```
Skill(skill="sf-metadata")
Request: "Describe object Invoice__c in org dev-sandbox - show all custom fields with their types, relationships, and required status"
```

**Use this when:**
- Creating test data for custom objects
- Writing SOQL for unfamiliar objects
- Verifying field API names before operations
- Understanding relationship names

### sf-data IS CALLED BY sf-apex (Test Data for Triggers)

When sf-apex needs test data for trigger testing:

```
Skill(skill="sf-data")
Request: "Create 251 test Account records with varying Industry values for bulk trigger testing in org dev-sandbox"
```

**Provide:**
- Object name and field variations
- Record count (recommend 251 for batch boundary testing)
- Target org alias
- Any specific field values needed

### sf-data IS CALLED BY sf-flow (Test Data for Flows)

When sf-flow needs test data for flow testing:

```
Skill(skill="sf-data")
Request: "Create test Opportunity records with StageName='Closed Won' to trigger the Opportunity_Notification flow in org dev-sandbox"
```

**Provide:**
- Object and field values that trigger the flow
- Entry criteria field values
- Record count for bulk testing

---

## Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| `INVALID_FIELD` | Field doesn't exist | Use sf-metadata to verify field API names |
| `MALFORMED_QUERY` | Invalid SOQL syntax | Check relationship names, field types |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule triggered | Use valid data or bypass permission |
| `DUPLICATE_VALUE` | Unique field constraint | Query existing records first |
| `REQUIRED_FIELD_MISSING` | Required field not set | Include all required fields |
| `INVALID_CROSS_REFERENCE_KEY` | Invalid relationship ID | Verify parent record exists |
| `ENTITY_IS_DELETED` | Record soft-deleted | Use --all-rows or query active records |
| `TOO_MANY_SOQL_QUERIES` | 100 query limit | Batch queries, use relationships |
| `TOO_MANY_DML_STATEMENTS` | 150 DML limit | Batch DML, use lists |

---

## Governor Limits Quick Reference

| Limit | Synchronous | Asynchronous |
|-------|-------------|--------------|
| SOQL Queries | 100 | 200 |
| SOQL Rows Retrieved | 50,000 | 50,000 |
| DML Statements | 150 | 150 |
| DML Rows | 10,000 | 10,000 |
| CPU Time | 10,000 ms | 60,000 ms |
| Heap Size | 6 MB | 12 MB |
| Callouts | 100 | 100 |

**Bulk API Limits:**
- 10,000 batches per 24 hours
- 10 million records per 24 hours
- 100 MB per batch file
- 150 MB per file (compressed)

---

## Reference Documentation

- [../../docs/soql-relationship-guide.md](../../docs/soql-relationship-guide.md) - Complete SOQL relationship patterns
- [../../docs/bulk-operations-guide.md](../../docs/bulk-operations-guide.md) - When to use which bulk command
- [../../docs/test-data-patterns.md](../../docs/test-data-patterns.md) - Realistic test data generation
- [../../docs/anonymous-apex-guide.md](../../docs/anonymous-apex-guide.md) - Complex data setup scenarios
- [../../docs/governor-limits-reference.md](../../docs/governor-limits-reference.md) - Complete limits reference
- [../../docs/cleanup-rollback-guide.md](../../docs/cleanup-rollback-guide.md) - Test isolation patterns
- [../../docs/sf-cli-data-commands.md](../../docs/sf-cli-data-commands.md) - CLI command reference

## Template Reference

**Factories:**
- `../../templates/factories/account-factory.apex`
- `../../templates/factories/contact-factory.apex`
- `../../templates/factories/opportunity-factory.apex`
- `../../templates/factories/hierarchy-factory.apex`

**SOQL Patterns:**
- `../../templates/soql/parent-to-child.soql`
- `../../templates/soql/child-to-parent.soql`
- `../../templates/soql/polymorphic.soql`

**Bulk Operations:**
- `../../templates/bulk/bulk-insert-200.apex`
- `../../templates/bulk/bulk-insert-10000.apex`

**Cleanup:**
- `../../templates/cleanup/delete-by-created-date.apex`
- `../../templates/cleanup/rollback-transaction.apex`

---

## Dependencies

- **sf-metadata** (optional): Query object/field structure before operations
  - Install: `/plugin install github:Jaganpro/sf-skills/sf-metadata`
- **sf CLI v2** (required): All data operations use sf CLI
  - Install: `npm install -g @salesforce/cli`

---

## Completion Format

After completing data operations, provide:

```
✓ Data Operation Complete: [Operation Type]
  Object: [ObjectName] | Records: [Count]
  Target Org: [alias]

  Record Summary:
  ├─ Created: [count] records
  ├─ Updated: [count] records
  └─ Deleted: [count] records

  Record IDs: [first 5 IDs...]

  Validation: PASSED (Score: XX/130)

  Cleanup Commands:
  ├─ sf data delete bulk --file cleanup.csv --sobject [Object] --target-org [alias]
  └─ sf apex run --file cleanup.apex --target-org [alias]

  Next Steps:
  1. Verify records in org
  2. Run trigger/flow tests
  3. Execute cleanup when done
```

---

## Notes

- **API Version**: Commands use org's default API version (recommend 62.0+)
- **Bulk API 2.0**: Used for all bulk operations (classic Bulk API deprecated)
- **JSON Output**: Always use `--json` flag for scriptable output
- **Test Isolation**: Use savepoints for reversible test data
- **Sensitive Data**: Never include real PII in test data

---

## License

MIT License - See LICENSE file for details.
