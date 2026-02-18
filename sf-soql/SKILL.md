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

# sf-soql: SOQL/SOSL Query Expert

> **Prerequisite**: Before writing queries, confirm the schema with `sf-metadata`. Run `sf sobject describe --sobject ObjectName` to verify field API names and relationship names.

## Workflow (4-Phase Pattern)

### Phase 1: Schema Discovery & Requirements

Before writing any query:

1. **Confirm the schema** -- use `sf-metadata` to verify object/field API names
2. **Gather requirements**:
   - What data is needed (objects, fields)
   - Filter criteria (WHERE conditions)
   - Sort requirements (ORDER BY)
   - Record limit requirements
   - Use case context (trigger, batch, flow, LWC, REST API)
   - Security context (user mode vs system mode)

### Phase 2: Query Generation

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

**Scoring**: 90-100 = production-optimized | 80-89 = good, minor tweaks | 70-79 = functional, perf concerns | <70 = refactor needed

---

## Relationship Queries

Child-to-parent uses dot notation (`Contact.Account.Name`), parent-to-child uses subqueries (`SELECT (SELECT Id FROM Contacts) FROM Account`). Custom relationships use `__r` suffix.
> **Deep dive**: [references/relationship-queries.md](references/relationship-queries.md)

## Aggregate Queries

COUNT, SUM, AVG, MIN, MAX with GROUP BY, GROUP BY ROLLUP, GROUP BY CUBE, and HAVING clause.
> **Deep dive**: [references/aggregate-queries.md](references/aggregate-queries.md)

---

## Query Optimization

> **Deep dive**: [references/query-optimization.md](references/query-optimization.md) -- index strategy, selectivity thresholds, optimization patterns, query plan analysis

**Auto-indexed fields**: `Id`, `Name`, `OwnerId`, `CreatedDate`, `LastModifiedDate`, `SystemModstamp`, `RecordTypeId`, External IDs, Master-Detail, Lookups.

**Quick selectivity rules**: <10% of first 1M rows, <5% beyond 1M, result set under 333K records. OR requires all branches selective; AND needs at least one.

**Query plan**: Use REST API `?explain=<SOQL>` or Developer Console Query Plan tool. Target `relativeCost < 1.0` and `leadingOperationType = 'Index'`.

---

## Governor Limits

> **Deep dive**: [references/governor-limits.md](references/governor-limits.md) -- full limits table, context guidance, efficient Apex patterns

| Limit | Sync | Async | Batch |
|-------|------|-------|-------|
| SOQL queries | 100 | 200 | 200 |
| Records retrieved | 50,000 | 50,000 | 50,000 |
| SOSL searches | 20 | 20 | 20 |
| CPU time | 10s | 60s | 60s |

**Key rule**: Never put SOQL in a loop. Collect IDs, query once, use a Map.

---

## Dynamic SOQL

> **Deep dive**: [references/dynamic-soql.md](references/dynamic-soql.md) -- all Database.query variants, bind variable rules, injection prevention

**Preferred**: `Database.queryWithBinds(query, binds, AccessLevel.USER_MODE)` -- prevents injection by design (Spring '23+).

**Injection prevention priority**: (1) Static SOQL with `:bindVar` > (2) `queryWithBinds()` > (3) `String.escapeSingleQuotes()` > (4) Allowlist validation for dynamic identifiers.

---

## Security Patterns

> **Deep dive**: [references/security-patterns.md](references/security-patterns.md) -- WITH SECURITY_ENFORCED, AccessLevel, stripInaccessible

| Context | Recommended Pattern |
|---------|-------------------|
| LWC wire adapters | `AccessLevel.USER_MODE` |
| Trigger / service layer | `AccessLevel.USER_MODE` or `stripInaccessible` |
| Batch / scheduled | `AccessLevel.SYSTEM_MODE` (with explicit checks) |
| Integration / API | `stripInaccessible` |
| Admin utilities | `AccessLevel.SYSTEM_MODE` |

---

## SOSL vs SOQL Decision

| Criterion | SOQL | SOSL |
|-----------|------|------|
| Known object | Yes, one at a time | Across ALL objects |
| Search type | Exact match | Full-text search |
| Wildcards | LIKE only, leading kills index | Efficient by design |
| Use case | Structured queries, DML prep | Search bars, fuzzy match |
| Max results | 50,000 rows | 2,000 per object |
| Governor limit | 100/200 queries | 20 searches |

**Rule of thumb**: User types into a search box = SOSL. Known object + filter fields = SOQL.

> **Deep dive**: [references/sosl-patterns.md](references/sosl-patterns.md) -- SOSL syntax, Apex examples, dynamic SOSL, governor limits

---

## Advanced SOQL

TYPEOF (polymorphic relationships), semi-joins/anti-joins, FOR UPDATE, FORMAT(), convertCurrency(), FIELDS(STANDARD/ALL/CUSTOM), date functions, OFFSET pagination.
> **Deep dive**: [references/advanced-soql.md](references/advanced-soql.md)

---

## Selector Pattern (DAL)

Consolidate all SOQL for an object into a Selector class (`AccountSelector.selectById()`, `selectWithContactsById()`, `selectDynamic()`). Used with `salesforce-trigger-framework` DAL architecture.
> **Deep dive**: [references/selector-pattern.md](references/selector-pattern.md)

---

## CLI Commands Reference

```bash
# Standard query
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org

# JSON output (for scripting)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --json

# CSV output (for export)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --result-format csv

# Human-readable table
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org --result-format human

# Bulk API 2.0 (large datasets, async)
sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --bulk

# Resume bulk query
sf data query resume --target-org my-org --bulk-query-id <JOB_ID>

# Query from .soql file
sf data query --file queries/active-accounts.soql --target-org my-org
```

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
| `SELECT *` (or too many fields) | Wastes heap; FLS issues | Select only needed fields |
| Missing WHERE clause | Returns all records, hits 50K limit | Always filter |
| Leading wildcard `LIKE '%term'` | Cannot use index, full scan | Use SOSL or trailing wildcard |
| Negative filter `!= 'Value'` | Not selective, full scan | Use IN with positive values |
| Dynamic SOQL with string concat | SOQL injection vulnerability | Use `Database.queryWithBinds()` |
| COUNT() on large tables without filter | Hits 50K limit | Add selective WHERE clause |
| FOR UPDATE in batch | Locks records across long execution | Avoid or use narrow scope |
| Hard-coded IDs in SOQL | Breaks across environments | Use Custom Metadata or Custom Labels |
| Querying in constructor | Runs before context is ready (LWC) | Use init methods or wire |

---

## Cross-Skill Integration

| Skill | Integration Point |
|-------|-------------------|
| `sf-metadata` | Schema discovery before writing queries |
| `sf-apex` | Embed queries in Apex service/selector classes |
| `sf-data` | Execute queries and data operations against org |
| `sf-debug` | Analyze slow queries in debug logs, run Code Analyzer |
| `sf-lwc` | Generate wire adapters with SOQL-backed Apex |
| `sf-flow` | Verify flow SOQL usage stays within limits |
| `salesforce-trigger-framework` | DAL/Selector pattern for trigger queries |
| `sf-testing` | Verify SOQL in test context (isolated data) |

---

## Dependencies

**Required**: Target org with `sf` CLI v2 authenticated (`sf org login`)

**Recommended Skills**: `sf-metadata`, `sf-apex`, `sf-debug`, `salesforce-trigger-framework`, `sf-testing`

---

## Sources

- [SOQL and SOSL Reference (Spring '26)](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm)
- [Apex Developer Guide: Dynamic SOQL](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_dynamic_soql.htm)
- [Execution Governors and Limits](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [REST API: Query Performance Feedback](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query_explain.htm)
- [Secure Coding: SQL Injection Prevention](https://developer.salesforce.com/docs/atlas.en-us.secure_coding_guide.meta/secure_coding_guide/secure_coding_sql_injection.htm)
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

## References (Progressive Disclosure)

| Reference | Content |
|-----------|---------|
| [relationship-queries.md](references/relationship-queries.md) | Child-to-parent, parent-to-child, common names |
| [aggregate-queries.md](references/aggregate-queries.md) | COUNT, SUM, GROUP BY, ROLLUP, CUBE, HAVING |
| [query-optimization.md](references/query-optimization.md) | Index strategy, selectivity, query plan analysis |
| [governor-limits.md](references/governor-limits.md) | Limits table, context guidance, efficient patterns |
| [dynamic-soql.md](references/dynamic-soql.md) | Dynamic SOQL, bind variables, injection prevention |
| [security-patterns.md](references/security-patterns.md) | FLS enforcement, access levels, stripInaccessible |
| [sosl-patterns.md](references/sosl-patterns.md) | SOSL syntax, Apex examples, dynamic SOSL |
| [advanced-soql.md](references/advanced-soql.md) | TYPEOF, semi-joins, FOR UPDATE, FIELDS(), OFFSET |
| [selector-pattern.md](references/selector-pattern.md) | DAL/Selector class architecture |

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy / PS Advisory
