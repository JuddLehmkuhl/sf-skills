# Dynamic SOQL & Injection Prevention

> Back to [SKILL.md](../SKILL.md)

## When to Use Dynamic SOQL

Use dynamic SOQL when:
- Field names, object names, or WHERE clauses are determined at runtime
- Building search/filter UIs where users select criteria
- Writing generic/reusable utilities (e.g., a selector framework)

## Database.query() -- Simple Dynamic SOQL

```apex
// Basic dynamic query
String objectName = 'Account';
String query = 'SELECT Id, Name FROM ' + objectName + ' LIMIT 100';
List<SObject> results = Database.query(query);

// With access level (Spring '23+, recommended)
List<SObject> results = Database.query(query, AccessLevel.USER_MODE);
```

## Database.queryWithBinds() -- Safe Dynamic SOQL (Preferred)

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

## Database.countQueryWithBinds()

```apex
// Count query with bind variables
String countQuery = 'SELECT COUNT() FROM Account WHERE Industry = :ind';
Map<String, Object> binds = new Map<String, Object>{ 'ind' => 'Technology' };
Integer total = Database.countQueryWithBinds(countQuery, binds, AccessLevel.USER_MODE);
```

## Database.getQueryLocatorWithBinds()

```apex
// For Batch Apex start() method -- supports up to 50 million rows
public Database.QueryLocator start(Database.BatchableContext bc) {
    String query = 'SELECT Id, Name FROM Account WHERE Industry = :ind';
    Map<String, Object> binds = new Map<String, Object>{ 'ind' => 'Technology' };
    return Database.getQueryLocatorWithBinds(query, binds, AccessLevel.USER_MODE);
}
```

## Bind Variable Rules

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
