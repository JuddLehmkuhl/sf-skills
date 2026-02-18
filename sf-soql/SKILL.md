---
name: sf-soql
description: >
  Advanced SOQL/SOSL skill with natural language to query generation, query optimization,
  relationship traversal, aggregate functions, dynamic SOQL with injection prevention,
  SOSL cross-object search, and performance analysis. Build efficient queries that
  respect governor limits and security requirements across all execution contexts.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  enriched_by: "PS Advisory"
  scoring: "100 points across 5 categories"
---

# sf-soql: Salesforce SOQL/SOSL Query Expert

Expert database engineer specializing in Salesforce Object Query Language (SOQL) and Salesforce Object Search Language (SOSL). Generate optimized queries from natural language, analyze query performance, prevent SOQL injection, and ensure best practices for governor limits and security across all execution contexts.

> **Prerequisite**: Before writing queries, you need to know the schema. Use `sf-metadata` to discover available objects, fields, and relationships. Run `sf org describe-metadata` and `sf sobject describe` commands to confirm field API names and relationship names before constructing queries.

## Core Responsibilities

1. **Natural Language to SOQL/SOSL**: Convert plain English requests to optimized queries
2. **Query Optimization**: Analyze and improve query performance using query plans
3. **Relationship Queries**: Build parent-child and child-parent traversals
4. **Aggregate Functions**: COUNT, SUM, AVG, MIN, MAX with GROUP BY
5. **Dynamic SOQL**: Safe construction with bind variables and injection prevention
6. **SOSL Search**: Cross-object text search when SOQL is insufficient
7. **Security Enforcement**: Ensure FLS, sharing rules, and access level compliance
8. **Governor Limit Awareness**: Design queries within limits for every execution context

## Workflow (4-Phase Pattern)

### Phase 1: Schema Discovery & Requirements

Before writing any query:

1. **Confirm the schema** -- use `sf-metadata` to verify object/field API names
2. **Gather requirements** via AskUserQuestion:
   - What data is needed (objects, fields)
   - Filter criteria (WHERE conditions)
   - Sort requirements (ORDER BY)
   - Record limit requirements
   - Use case context (trigger, batch, flow, LWC, REST API)
   - Security context (user mode vs system mode)

### Phase 2: Query Generation

**Natural Language Examples**:

| Request | Generated SOQL |
|---------|----------------|
| "Get all active accounts with their contacts" | `SELECT Id, Name, (SELECT Id, Name FROM Contacts) FROM Account WHERE IsActive__c = true` |
| "Find contacts created this month" | `SELECT Id, Name, Email FROM Contact WHERE CreatedDate = THIS_MONTH` |
| "Count opportunities by stage" | `SELECT StageName, COUNT(Id) FROM Opportunity GROUP BY StageName` |
| "Get accounts with revenue over 1M sorted by name" | `SELECT Id, Name, AnnualRevenue FROM Account WHERE AnnualRevenue > 1000000 ORDER BY Name` |
| "Search for 'Acme' across accounts and contacts" | `FIND {Acme} IN NAME FIELDS RETURNING Account(Id, Name), Contact(Id, Name, Email)` |

### Phase 3: Optimization

**Query Optimization Checklist**:

1. **Selectivity**: Does WHERE clause use indexed fields?
2. **Field Selection**: Only query needed fields (never SELECT *)
3. **Limit**: Is LIMIT appropriate for use case?
4. **Relationship Depth**: Avoid deep traversals (max 5 levels)
5. **Aggregate Queries**: Use for counts/sums instead of loading all records
6. **Query Plan**: Run explain analysis for queries over large datasets
7. **Context Limits**: Verify query count stays within context-specific limits

### Phase 4: Validation & Execution

```bash
# Test query in target org
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org

# JSON output for programmatic consumption
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org --json

# Bulk query for large datasets (uses Bulk API 2.0)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --bulk
```

---

## Best Practices (100-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Selectivity** | 25 | Indexed fields in WHERE, selective filters, query plan cost < 1.0 |
| **Performance** | 25 | Appropriate LIMIT, minimal fields, no unnecessary joins, bulk-safe |
| **Security** | 20 | WITH SECURITY_ENFORCED or USER_MODE, stripInaccessible, injection-safe |
| **Correctness** | 15 | Proper syntax, valid field references, context-appropriate limits |
| **Readability** | 15 | Formatted, meaningful aliases, comments explaining complex logic |

**Scoring Thresholds**:
```
90-100 pts  Production-optimized query
80-89 pts   Good query, minor optimizations possible
70-79 pts   Functional, performance concerns
60-69 pts   Basic query, needs improvement
<60 pts     Problematic query, refactor required
```

---

## Relationship Queries

### Child-to-Parent (Dot Notation)

```sql
-- Access parent fields via lookup/master-detail
SELECT Id, Name, Account.Name, Account.Industry
FROM Contact
WHERE Account.AnnualRevenue > 1000000

-- Up to 5 levels deep
SELECT Id, Contact.Account.Owner.Manager.Name
FROM Case

-- Custom relationship: use __r suffix
SELECT Id, Name, Custom_Lookup__r.Name, Custom_Lookup__r.Custom_Field__c
FROM Another_Object__c
```

### Parent-to-Child (Subquery)

```sql
-- Get parent with related children
SELECT Id, Name,
       (SELECT Id, FirstName, LastName FROM Contacts),
       (SELECT Id, Name, Amount FROM Opportunities WHERE StageName = 'Closed Won')
FROM Account
WHERE Industry = 'Technology'

-- Custom child relationship: use __r suffix (plural)
SELECT Id, Name,
       (SELECT Id, Name FROM Custom_Children__r)
FROM Parent_Object__c
```

### Common Relationship Names

| Parent Object | Child Relationship | Subquery Example |
|---------------|-------------------|------------------|
| Account | Contacts | `(SELECT Id FROM Contacts)` |
| Account | Opportunities | `(SELECT Id FROM Opportunities)` |
| Account | Cases | `(SELECT Id FROM Cases)` |
| Contact | Cases | `(SELECT Id FROM Cases)` |
| Opportunity | OpportunityLineItems | `(SELECT Id FROM OpportunityLineItems)` |
| Opportunity | OpportunityContactRoles | `(SELECT Id FROM OpportunityContactRoles)` |

> **Tip**: Use `sf-metadata` to discover custom relationship names. Run `sf sobject describe --sobject ObjectName` to see both `childRelationships` and `fields[].relationshipName`.

---

## Aggregate Queries

### Basic Aggregates

```sql
-- Count all records (returns Integer)
SELECT COUNT() FROM Account WHERE Industry = 'Technology'

-- Count with alias (returns AggregateResult[])
SELECT COUNT(Id) cnt FROM Account

-- Multiple aggregates in one query
SELECT SUM(Amount) totalRevenue, AVG(Amount) avgDeal,
       MIN(Amount) smallest, MAX(Amount) largest
FROM Opportunity
WHERE StageName = 'Closed Won' AND CloseDate = THIS_YEAR
```

### GROUP BY

```sql
-- Count by field
SELECT Industry, COUNT(Id) cnt
FROM Account
GROUP BY Industry

-- Multiple groupings with date functions
SELECT StageName, CALENDAR_YEAR(CloseDate) yr, COUNT(Id) cnt
FROM Opportunity
GROUP BY StageName, CALENDAR_YEAR(CloseDate)

-- GROUP BY ROLLUP (subtotals)
SELECT LeadSource, Rating, COUNT(Id)
FROM Lead
GROUP BY ROLLUP(LeadSource, Rating)

-- GROUP BY CUBE (all combinations)
SELECT Type, BillingState, COUNT(Id)
FROM Account
GROUP BY CUBE(Type, BillingState)
```

### HAVING Clause

```sql
-- Filter aggregated results
SELECT Industry, COUNT(Id) cnt
FROM Account
GROUP BY Industry
HAVING COUNT(Id) > 10

-- Complex HAVING
SELECT AccountId, SUM(Amount) total
FROM Opportunity
WHERE StageName = 'Closed Won'
GROUP BY AccountId
HAVING SUM(Amount) > 100000
```

---

## Query Optimization

### Index Strategy

**Auto-Indexed Fields** (always selective when filtered):
- `Id`, `Name`, `OwnerId`, `CreatedDate`, `LastModifiedDate`, `SystemModstamp`
- `RecordTypeId`, External ID fields, Master-Detail fields
- Lookup fields (selective when unique or low-cardinality)

**Object-Specific Indexed Fields**:
| Object | Indexed Fields |
|--------|---------------|
| Account | AccountNumber, Site |
| Contact | Email |
| Lead | Email, Name |
| Case | CaseNumber |
| Task / Event | ActivityDate |

### Selectivity Thresholds

```
A filter is selective when it returns:
  - Less than 10% of records (first 1M records in the object)
  - Less than 5% of records (beyond 1M records)
  - AND the result set is under 333,333 records

Two-column index selectivity:
  - Less than 5% of records (first 1M)
  - Less than 2.5% of records (beyond 1M)

When OR is used, ALL branches must be selective individually.
When AND is used, at least one branch must be selective.
```

### Optimization Patterns

```sql
-- BAD: Non-selective, full table scan
SELECT Id FROM Lead WHERE Status = 'Open'

-- GOOD: Selective index + narrowing filter + limit
SELECT Id FROM Lead
WHERE Status = 'Open' AND CreatedDate = LAST_N_DAYS:30
LIMIT 10000

-- BAD: Leading wildcard prevents index usage
SELECT Id FROM Account WHERE Name LIKE '%corp'

-- GOOD: Trailing wildcard can use index
SELECT Id FROM Account WHERE Name LIKE 'Acme%'

-- BAD: Negative operators are never selective
SELECT Id FROM Account WHERE Industry != 'Other'

-- GOOD: Reframe as positive filter
SELECT Id FROM Account WHERE Industry IN ('Technology', 'Finance', 'Healthcare')

-- BAD: Formula fields are not indexed
SELECT Id FROM Account WHERE Revenue_Tier__c = 'Enterprise'

-- GOOD: Filter on the underlying indexed field
SELECT Id FROM Account WHERE AnnualRevenue > 10000000
```

### Query Plan Analysis

> **IMPORTANT**: The `sf data query --plan` flag does NOT exist in sf CLI v2. Query plans must be retrieved via the REST API `explain` parameter or the Developer Console Query Plan tool.

**Method 1: REST API explain parameter**

```bash
# Get query plan via REST API (does NOT execute the query)
# URL format: /services/data/vXX.0/query/?explain=<SOQL>
curl "https://MyDomainName.my.salesforce.com/services/data/v62.0/query/?explain=SELECT+Id+FROM+Account+WHERE+Name='Test'" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Method 2: Developer Console**

1. Open Developer Console (Setup gear icon > Developer Console)
2. Open Query Editor tab (bottom pane)
3. Check the "Use Tooling API" checkbox
4. Enter your SOQL query
5. Click "Query Plan" button
6. Review the plan output

**Method 3: Anonymous Apex with Tooling API callout**

```apex
// Query the explain plan via HttpRequest to Tooling API
String soql = 'SELECT Id FROM Account WHERE Name = \'Test\'';
String endpoint = URL.getOrgDomainUrl().toExternalForm()
    + '/services/data/v62.0/query/?explain='
    + EncodingUtil.urlEncode(soql, 'UTF-8');

HttpRequest req = new HttpRequest();
req.setEndpoint(endpoint);
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());

HttpResponse res = new Http().send(req);
System.debug(res.getBody());
```

**Plan Output Fields**:

| Field | Meaning | Good Value |
|-------|---------|------------|
| `cardinality` | Estimated rows returned | Lower is better |
| `fields` | Index fields considered | Non-empty = index available |
| `leadingOperationType` | How scan starts | `Index` (good) vs `TableScan` (bad) |
| `relativeCost` | Optimizer cost estimate | < 1.0 preferred |
| `sobjectCardinality` | Total records in object | Context for selectivity |
| `sobjectType` | Object being queried | Confirms target |

**Decision matrix**:
```
relativeCost < 1.0 AND leadingOperationType = 'Index'   --> Query is optimized
relativeCost > 1.0 AND leadingOperationType = 'Index'   --> Index exists but filter not selective enough
leadingOperationType = 'TableScan'                       --> No usable index, add selective filter
```

---

## Governor Limits by Execution Context

| Limit | Synchronous (Trigger, REST, LWC) | Asynchronous (Future, Queueable) | Batch Apex (per chunk) | Flow |
|-------|----------------------------------|----------------------------------|----------------------|------|
| **SOQL queries issued** | 100 | 200 | 200 | 100 |
| **Records retrieved (all queries)** | 50,000 | 50,000 | 50,000 | 50,000 |
| **SOSL searches** | 20 | 20 | 20 | 20 |
| **Records per SOSL** | 2,000 | 2,000 | 2,000 | 2,000 |
| **Query locator rows** | 10,000,000 | 10,000,000 | 50,000,000 | N/A |
| **CPU time** | 10,000 ms | 60,000 ms | 60,000 ms | N/A (flow limits) |
| **Heap size** | 6 MB | 12 MB | 12 MB | N/A |

**Context-specific guidance**:

- **Triggers** (via `salesforce-trigger-framework`): You share the 100-query / 50,000-row limit with ALL triggers, workflows, process builders, and flows in the same transaction. Keep trigger queries minimal; use a DAL (Data Access Layer) pattern to consolidate.
- **Batch Apex**: Each `execute()` chunk gets its own governor limits. Use `Database.getQueryLocator()` in `start()` to query up to 50 million rows.
- **Flow**: Subject to same per-transaction limits. Record-triggered flows share limits with the trigger transaction. Scheduled flows get their own transaction.
- **LWC / Aura**: Wire adapters and imperative Apex share limits with the Apex transaction they invoke. Use `@AuraEnabled(cacheable=true)` to enable client-side caching.
- **REST API**: Each API call is its own transaction with synchronous limits. Composite API bundles share one transaction.

### Efficient Patterns for Limit Management

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

---

## Dynamic SOQL

### When to Use Dynamic SOQL

Use dynamic SOQL when:
- Field names, object names, or WHERE clauses are determined at runtime
- Building search/filter UIs where users select criteria
- Writing generic/reusable utilities (e.g., a selector framework)

### Database.query() -- Simple Dynamic SOQL

```apex
// Basic dynamic query
String objectName = 'Account';
String query = 'SELECT Id, Name FROM ' + objectName + ' LIMIT 100';
List<SObject> results = Database.query(query);

// With access level (Spring '23+, recommended)
List<SObject> results = Database.query(query, AccessLevel.USER_MODE);
```

### Database.queryWithBinds() -- Safe Dynamic SOQL (Preferred)

```apex
// PREFERRED: Bind variables resolved from Map, not local scope
// Introduced Spring '23 -- prevents SOQL injection by design
String query = 'SELECT Id, Name FROM Account WHERE Name = :accountName AND Industry = :ind';
Map<String, Object> binds = new Map<String, Object>{
    'accountName' => userInput,    // safely bound, never concatenated
    'ind' => 'Technology'
};
List<Account> results = Database.queryWithBinds(query, binds, AccessLevel.USER_MODE);
```

### Database.countQueryWithBinds()

```apex
// Count query with bind variables
String countQuery = 'SELECT COUNT() FROM Account WHERE Industry = :ind';
Map<String, Object> binds = new Map<String, Object>{ 'ind' => 'Technology' };
Integer total = Database.countQueryWithBinds(countQuery, binds, AccessLevel.USER_MODE);
```

### Database.getQueryLocatorWithBinds()

```apex
// For Batch Apex start() method -- supports up to 50 million rows
public Database.QueryLocator start(Database.BatchableContext bc) {
    String query = 'SELECT Id, Name FROM Account WHERE Industry = :ind';
    Map<String, Object> binds = new Map<String, Object>{ 'ind' => 'Technology' };
    return Database.getQueryLocatorWithBinds(query, binds, AccessLevel.USER_MODE);
}
```

### Bind Variable Rules

```
- Map keys must start with an ASCII letter (a-z, A-Z)
- Keys are case-insensitive (accountName and AccountName are the same key)
- No duplicate keys allowed
- Supported value types: primitives, SObject, List, Set, Map
- Bind variables use : prefix in the query string (e.g., :myVar)
```

---

## SOQL Injection Prevention

### Threat Model

SOQL injection occurs when user-supplied input is concatenated directly into a SOQL query string, allowing attackers to modify query logic.

```apex
// VULNERABLE: Direct string concatenation
String userInput = request.getParameter('name');
String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
// Attacker sends: ' OR Name != '
// Resulting query: SELECT Id FROM Account WHERE Name = '' OR Name != ''
// Returns ALL accounts
```

### Prevention Methods (Ranked by Preference)

**1. Static SOQL with bind variables (best)**

```apex
// Compile-time checked, injection impossible
String searchName = userInput;
List<Account> results = [SELECT Id, Name FROM Account WHERE Name = :searchName];
```

**2. Database.queryWithBinds() for dynamic queries (recommended)**

```apex
// Bind variables resolved from Map -- injection impossible
String query = 'SELECT Id, Name FROM Account WHERE Name = :searchName';
Map<String, Object> binds = new Map<String, Object>{ 'searchName' => userInput };
List<Account> results = Database.queryWithBinds(query, binds, AccessLevel.USER_MODE);
```

**3. String.escapeSingleQuotes() (last resort)**

```apex
// Only use when bind variables are not feasible (e.g., dynamic field names)
String safeName = String.escapeSingleQuotes(userInput);
String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + safeName + '\'';
List<Account> results = Database.query(query);
```

**4. Allowlist validation for dynamic identifiers**

```apex
// When field/object names come from user input
Set<String> allowedFields = new Set<String>{ 'Name', 'Industry', 'Type', 'BillingState' };
String fieldName = userInput;
if (!allowedFields.contains(fieldName)) {
    throw new QueryException('Invalid field: ' + fieldName);
}
String query = 'SELECT Id, ' + fieldName + ' FROM Account';
```

### Security Scanner Compliance

Salesforce Code Analyzer (PMD rules) flags SOQL injection risks. The `sf-debug` skill can run `sf scanner run` to detect vulnerable patterns. Key rules:
- `ApexSOQLInjection` -- detects unescaped user input in SOQL strings
- `ApexCRUDViolation` -- detects missing FLS/CRUD checks

---

## Security Patterns

### WITH SECURITY_ENFORCED

```apex
// Throws System.QueryException if user lacks FLS on any queried field
// Use in Apex where you want fail-fast behavior
List<Account> results = [
    SELECT Id, Name, Phone, AnnualRevenue
    FROM Account
    WITH SECURITY_ENFORCED
];
```

### Access Level in Database Methods (Spring '23+, Preferred)

```apex
// USER_MODE: enforces FLS + CRUD + sharing rules
List<Account> results = Database.query(soql, AccessLevel.USER_MODE);

// SYSTEM_MODE: bypasses all security (use only when justified)
List<Account> results = Database.query(soql, AccessLevel.SYSTEM_MODE);
```

### stripInaccessible (Graceful Degradation)

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

### Decision Matrix: Which Security Pattern to Use

| Context | Recommended Pattern | Reason |
|---------|-------------------|--------|
| LWC wire adapters | `WITH USER_MODE` / `AccessLevel.USER_MODE` | Consistent with Lightning platform security |
| Trigger / service layer | `AccessLevel.USER_MODE` or `stripInaccessible` | Enforce FLS while maintaining DML capability |
| Batch / scheduled | `AccessLevel.SYSTEM_MODE` (with explicit checks) | Often runs as automated user with limited permissions |
| Integration / API | `stripInaccessible` | Graceful handling of varied integration user profiles |
| Admin utilities | `AccessLevel.SYSTEM_MODE` | Administrative context with elevated permissions |

---

## SOSL: Salesforce Object Search Language

### When to Use SOSL vs SOQL

| Criterion | SOQL | SOSL |
|-----------|------|------|
| **Known object** | Yes, query one object at a time | Can search across ALL objects simultaneously |
| **Search type** | Exact match by default | Full-text search with tokenization |
| **Wildcards** | LIKE only, leading wildcard kills index | Efficient text matching by design |
| **Related objects** | Via relationship queries | Via RETURNING on unrelated objects |
| **Use case** | Structured queries, reporting, DML prep | Free-text search bars, global search, fuzzy match |
| **Results per object** | Up to 50,000 rows | Up to 2,000 per object (hard limit) |
| **Governor limit** | 100/200 queries per transaction | 20 searches per transaction |

**Rule of thumb**: If the user types into a search box, use SOSL. If you know the object and filter fields, use SOQL.

### SOSL Syntax

```sql
FIND {searchExpression}
  [IN searchGroup]
  [RETURNING objectType (fieldList [WHERE condition] [ORDER BY field] [LIMIT n])]
  [WITH snippetOptions]
  [LIMIT n]
```

**Search Groups**:
- `ALL FIELDS` -- searches all searchable fields (default)
- `NAME FIELDS` -- searches only Name fields
- `EMAIL FIELDS` -- searches only Email fields
- `PHONE FIELDS` -- searches only Phone fields
- `SIDEBAR FIELDS` -- searches fields displayed in sidebar search

### SOSL in Apex

```apex
// Basic multi-object search
List<List<SObject>> results = [
    FIND 'Acme*' IN NAME FIELDS
    RETURNING Account(Id, Name, Industry),
              Contact(Id, FirstName, LastName, Email),
              Opportunity(Id, Name, Amount)
];

List<Account> accounts = (List<Account>) results[0];
List<Contact> contacts = (List<Contact>) results[1];
List<Opportunity> opps = (List<Opportunity>) results[2];

// With WHERE filtering on returned objects
List<List<SObject>> results = [
    FIND 'cloud' IN ALL FIELDS
    RETURNING
        Account(Id, Name WHERE Industry = 'Technology' ORDER BY Name LIMIT 10),
        Contact(Id, Name, Email WHERE MailingState = 'CA')
    LIMIT 100
];
```

### Dynamic SOSL

```apex
// Dynamic SOSL uses Search.query()
String searchTerm = String.escapeSingleQuotes(userInput);
String soslQuery = 'FIND {' + searchTerm + '} IN ALL FIELDS '
    + 'RETURNING Account(Id, Name), Contact(Id, Name, Email) LIMIT 50';
List<List<SObject>> results = Search.query(soslQuery);
```

### SOSL Governor Limits

```
- Maximum 20 SOSL queries per transaction (sync and async)
- Maximum 2,000 records returned per object in RETURNING clause
- Maximum 200 characters in search term
- Minimum 2 characters in search term (unless using * wildcard)
- Search terms are tokenized; short common words may be ignored
```

---

## Advanced SOQL Features

### Polymorphic Relationships (TYPEOF)

```sql
-- Query polymorphic fields like Task.What or Event.Who
SELECT Id, Subject, What.Name, What.Type
FROM Task
WHERE What.Type IN ('Account', 'Opportunity')

-- TYPEOF for conditional field selection
SELECT Id, Subject,
    TYPEOF What
        WHEN Account THEN Name, Phone, Website
        WHEN Opportunity THEN Name, Amount, StageName
    END
FROM Task
WHERE CreatedDate = THIS_MONTH
```

### Semi-Joins and Anti-Joins

```sql
-- Semi-join: Records WITH related records
SELECT Id, Name FROM Account
WHERE Id IN (SELECT AccountId FROM Contact WHERE Email != null)

-- Anti-join: Records WITHOUT related records
SELECT Id, Name FROM Account
WHERE Id NOT IN (SELECT AccountId FROM Opportunity)

-- Multi-level semi-join
SELECT Id, Name FROM Account
WHERE Id IN (
    SELECT AccountId FROM Contact
    WHERE Id IN (SELECT ContactId FROM CampaignMember WHERE Status = 'Responded')
)
```

### FOR UPDATE (Record Locking)

```apex
// Lock records to prevent concurrent modification
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WHERE Id = :targetId
    FOR UPDATE
];
// Records locked until transaction commits or rolls back
// NOT supported in: subqueries, aggregate queries, SOSL
```

### FORMAT() and convertCurrency()

```sql
-- Format fields for display (respects user locale)
SELECT FORMAT(Amount), FORMAT(CloseDate), FORMAT(CreatedDate)
FROM Opportunity

-- Convert to user's currency (multi-currency orgs)
SELECT Id, Name, convertCurrency(Amount) convertedAmount
FROM Opportunity
WHERE convertCurrency(Amount) > 100000
```

### FIELDS() Functions

```sql
-- STANDARD fields only (safe for production)
SELECT FIELDS(STANDARD) FROM Account LIMIT 200

-- ALL fields (developer/debug use only -- requires LIMIT 200)
SELECT FIELDS(ALL) FROM Account LIMIT 200

-- CUSTOM fields only
SELECT FIELDS(CUSTOM) FROM Account LIMIT 200
```

### Date Functions in GROUP BY

```sql
-- Available date functions
SELECT CALENDAR_YEAR(CloseDate) yr, CALENDAR_MONTH(CloseDate) mo, COUNT(Id)
FROM Opportunity
GROUP BY CALENDAR_YEAR(CloseDate), CALENDAR_MONTH(CloseDate)

-- Other date functions: DAY_IN_MONTH, DAY_IN_WEEK, DAY_IN_YEAR,
-- DAY_ONLY, FISCAL_MONTH, FISCAL_QUARTER, FISCAL_YEAR,
-- HOUR_IN_DAY, WEEK_IN_MONTH, WEEK_IN_YEAR
```

### OFFSET (Pagination)

```sql
-- Skip first 100 results, return next 50
SELECT Id, Name FROM Account
ORDER BY Name
LIMIT 50 OFFSET 100

-- Maximum OFFSET: 2,000 records
-- For deep pagination, use query locators or keyset pagination
```

---

## Selector Pattern (DAL Architecture)

When using the `salesforce-trigger-framework`, consolidate all SOQL for an object into a Selector (Data Access Layer) class:

```apex
/**
 * @description Selector/DAL for Account queries. All Account SOQL
 *              lives here to avoid scattered queries and simplify testing.
 */
public with sharing class AccountSelector {

    // Standard fields queried by default
    private static final List<String> DEFAULT_FIELDS = new List<String>{
        'Id', 'Name', 'Industry', 'AnnualRevenue', 'OwnerId'
    };

    /**
     * @description Query accounts by Id set
     */
    public static List<Account> selectById(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Industry, AnnualRevenue, OwnerId
            FROM Account
            WHERE Id IN :accountIds
            WITH USER_MODE
        ];
    }

    /**
     * @description Query accounts with contacts by Id set
     */
    public static List<Account> selectWithContactsById(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Industry,
                   (SELECT Id, FirstName, LastName, Email FROM Contacts)
            FROM Account
            WHERE Id IN :accountIds
            WITH USER_MODE
        ];
    }

    /**
     * @description Dynamic query with caller-specified fields and filters
     */
    public static List<Account> selectDynamic(
        Set<String> fields,
        String whereClause,
        Map<String, Object> binds,
        Integer recordLimit
    ) {
        String query = 'SELECT ' + String.join(new List<String>(fields), ', ')
            + ' FROM Account';
        if (String.isNotBlank(whereClause)) {
            query += ' WHERE ' + whereClause;
        }
        query += ' LIMIT ' + recordLimit;
        return Database.queryWithBinds(query, binds, AccessLevel.USER_MODE);
    }
}
```

> See `salesforce-trigger-framework/SKILL.md` for the full `Trigger > MetadataTriggerHandler > TA_* > Services > DAL` architecture pattern.

---

## CLI Commands Reference

### Execute Queries

```bash
# Standard query
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org

# JSON output (for scripting/piping)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --json

# CSV output (for spreadsheet export)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --result-format csv

# Human-readable table
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org --result-format human
```

### Bulk Queries

```bash
# Bulk API 2.0 -- for large datasets (async, no 50K row limit per API call)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --bulk

# Resume a bulk query
sf data query resume --target-org my-org --bulk-query-id <JOB_ID>
```

### Query from File

```bash
# Store complex queries in a .soql file and execute
sf data query --file queries/active-accounts.soql --target-org my-org
```

---

## Cross-Skill Integration

| Skill | Integration Point | Example |
|-------|-------------------|---------|
| `sf-metadata` | **Schema discovery** before writing queries | Verify field API names: `sf sobject describe --sobject Account` |
| `sf-apex` | Embed queries in Apex service/selector classes | Build AccountSelector with optimized SOQL |
| `sf-data` | Execute queries and data operations against org | `sf data query` for validation |
| `sf-debug` | Analyze slow queries in debug logs, run Code Analyzer | Check SOQL counts and row limits in logs |
| `sf-lwc` | Generate wire adapters with SOQL-backed Apex | `@wire(getAccounts)` backed by SOQL |
| `sf-flow` | Verify flow SOQL usage stays within limits | Audit Get Records elements for selectivity |
| `salesforce-trigger-framework` | DAL/Selector pattern for trigger queries | `TA_* > Services > AccountSelector` |
| `sf-testing` | Verify SOQL in test context (isolated data) | Test data factory + selector unit tests |

---

## Natural Language to Query Examples

| Request | Generated Query |
|---------|----------------|
| "Get me all accounts" | `SELECT Id, Name FROM Account LIMIT 1000` |
| "Find contacts without email" | `SELECT Id, Name FROM Contact WHERE Email = null` |
| "Accounts created by John Smith" | `SELECT Id, Name FROM Account WHERE CreatedBy.Name = 'John Smith'` |
| "Top 10 opportunities by amount" | `SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 10` |
| "Accounts in California" | `SELECT Id, Name FROM Account WHERE BillingState = 'CA'` |
| "Contacts with @gmail emails" | `SELECT Id, Name, Email FROM Contact WHERE Email LIKE '%@gmail.com'` |
| "Opportunities closing this quarter" | `SELECT Id, Name, CloseDate FROM Opportunity WHERE CloseDate = THIS_QUARTER` |
| "Cases opened in last 7 days" | `SELECT Id, Subject FROM Case WHERE CreatedDate = LAST_N_DAYS:7` |
| "Total revenue by industry" | `SELECT Industry, SUM(AnnualRevenue) rev FROM Account GROUP BY Industry` |
| "Search for 'cloud' across all objects" | `FIND {cloud} IN ALL FIELDS RETURNING Account(Id, Name), Contact(Id, Name), Opportunity(Id, Name)` |
| "Accounts with open opportunities" | `SELECT Id, Name FROM Account WHERE Id IN (SELECT AccountId FROM Opportunity WHERE IsClosed = false)` |
| "Contacts whose account is in Technology" | `SELECT Id, Name, Email FROM Contact WHERE Account.Industry = 'Technology'` |

---

## Anti-Patterns Quick Reference

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| SOQL inside a loop | Burns queries against 100/200 limit | Collect IDs, query once, use Map |
| `SELECT *` (or too many fields) | Wastes heap; can hit field-level security issues | Select only needed fields |
| Missing WHERE clause | Returns all records, hits 50K limit | Always filter |
| Leading wildcard `LIKE '%term'` | Cannot use index, full table scan | Use SOSL or trailing wildcard |
| Negative filter `!= 'Value'` | Not selective, full scan | Use IN with positive values |
| Dynamic SOQL with string concat | SOQL injection vulnerability | Use `Database.queryWithBinds()` |
| COUNT() on large tables without filter | Hits 50K limit | Add selective WHERE clause |
| FOR UPDATE in batch | Locks records across long execution | Avoid or use narrow scope |
| Hard-coded IDs in SOQL | Breaks across environments | Use Custom Metadata or Custom Labels |
| Querying in constructor | Runs before context is ready (LWC) | Use init methods or wire |

---

## Dependencies

**Required**: Target org with `sf` CLI v2 authenticated (`sf org login`)

**Recommended Skills**:
- `sf-metadata` -- Schema discovery (verify object/field names before writing queries)
- `sf-apex` -- Embedding queries in Apex classes
- `sf-debug` -- Query performance analysis via debug logs and Code Analyzer
- `salesforce-trigger-framework` -- DAL/Selector architecture for trigger queries
- `sf-testing` -- Testing queries with isolated test data

---

## Sources

- [Salesforce SOQL and SOSL Reference (Spring '26)](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm)
- [Apex Developer Guide: Dynamic SOQL](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_dynamic_soql.htm)
- [Execution Governors and Limits](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [REST API: Get Feedback on Query Performance](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query_explain.htm)
- [Secure Coding: SQL Injection Prevention](https://developer.salesforce.com/docs/atlas.en-us.secure_coding_guide.meta/secure_coding_guide/secure_coding_sql_injection.htm)
- [Trailhead: Optimize SOSL Queries in Apex](https://trailhead.salesforce.com/content/learn/modules/apex_database/apex_database_sosl)
- [Trailhead: Mitigate SOQL Injection](https://trailhead.salesforce.com/content/learn/modules/secure-serverside-development/mitigate-soql-injection)
- [Salesforce App Limits Cheatsheet (PDF)](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_app_limits_cheatsheet.pdf)
- [Developer Console Query Plan Tool FAQ](https://help.salesforce.com/s/articleView?id=000386864&language=en_US&type=1)
- [Database.queryWithBinds Release Notes](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_bind_var_soql.htm&language=en_US&release=242&type=5)

---

## Documentation

| Document | Description |
|----------|-------------|
| [soql-reference.md](docs/soql-reference.md) | Complete SOQL syntax reference |
| [cli-commands.md](docs/cli-commands.md) | SF CLI query commands |
| [anti-patterns.md](docs/anti-patterns.md) | Common mistakes and how to avoid them |
| [selector-patterns.md](docs/selector-patterns.md) | Query abstraction patterns (vanilla Apex) |

## Templates

| Template | Description |
|----------|-------------|
| [basic-queries.soql](templates/basic-queries.soql) | Basic SOQL syntax examples |
| [aggregate-queries.soql](templates/aggregate-queries.soql) | COUNT, SUM, GROUP BY patterns |
| [relationship-queries.soql](templates/relationship-queries.soql) | Parent-child traversals |
| [optimization-patterns.soql](templates/optimization-patterns.soql) | Selectivity and indexing |
| [selector-class.cls](templates/selector-class.cls) | Selector class template |
| [bulkified-query-pattern.cls](templates/bulkified-query-pattern.cls) | Map-based bulk lookups |

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy / PS Advisory
