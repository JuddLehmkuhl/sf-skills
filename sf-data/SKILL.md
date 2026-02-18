---
name: sf-data
description: >
  Salesforce data operations expert. Use when writing SOQL queries, creating
  test data, performing bulk data operations, importing/exporting data via
  sf CLI, or generating test data factories.
metadata:
  version: "2.1.0"
  author: "Judd Lehmkuhl"
  enriched_by: "Claude Opus 4.6"
  last_updated: "2026-02-18"
---

# Salesforce Data Operations (sf-data)

## Capabilities

- **CRUD**: Query, insert, update, delete, upsert records via sf CLI
- **SOQL**: Relationships, aggregates, polymorphic queries
- **Test Data**: Factory patterns with RecordType support, field overrides, bulk distribution
- **Bulk Operations**: Bulk API 2.0 for large datasets (2,000+ records)
- **Data Tree**: Parent-child relational data movement between orgs
- **Data Masking**: Anonymization for sandbox refreshes

**Cross-references**: `sf-soql` (query optimization), `sf-apex` (Apex classes), `sf-testing` (test execution), `sf-metadata` (object discovery), `sf-deploy` (deployment)

---

## Operation Modes

| Mode | Org Required? | Output | Use When |
|------|---------------|--------|----------|
| **Script Generation** | No | Local `.apex` files | Reusable scripts, no org yet |
| **Remote Execution** | Yes | Records in org | Immediate testing, verification |

Always confirm which mode the user expects before proceeding.

---

## CRITICAL: Orchestration Order

**sf-metadata -> sf-flow -> sf-deploy -> sf-data** (you are here)

sf-data REQUIRES objects to exist in org. Error `SObject type 'X' not supported` = deploy metadata first.

---

## Anti-Patterns Summary

> Full code examples: `references/anti-patterns.md`

| # | Anti-Pattern | Fix |
|---|-------------|-----|
| 1 | SOQL/DML inside loops | Bulkify: collect into maps/lists, single DML outside loop |
| 2 | Hardcoded Record IDs | `Schema.SObjectType.X.getRecordTypeInfosByDeveloperName()` |
| 3 | Hardcoded Profile/Role names | Use Permission Sets or constants |
| 4 | Real PII in test data | Synthetic: `@example.com`, `Test_` prefix |
| 5 | `seeAllData=true` | Create all test data in the test method |
| 6 | Missing required fields | Include all required fields in factory |
| 7 | Single-record tests only | Test with 251+ records (crosses batch boundary) |
| 8 | `FIELDS(ALL)` in production | Select only needed fields |
| 9 | Unscoped DELETE | Always add WHERE clause with Name/Date filter |
| 10 | Ignoring `Database.SaveResult` | Check `isSuccess()` for partial failures |
| 11 | Mixing data creation with assertions | Use factory pattern + focused assertions |
| 12 | Wrong CSV encoding | UTF-8 + LF line endings |

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

## Data Tree Import/Export

> Full examples and plan file structure: `references/data-tree-import-export.md`

Use `sf data export tree` / `sf data import tree` for parent-child relational data between orgs.

| Constraint | Limit |
|------------|-------|
| Max records per export query | 2,000 |
| Max records per import file | 200 |
| API used | Composite sObject Tree |
| Relationship depth | Parent + 1 child level |

Split large exports into multiple files referenced in the plan.

---

## Bulk API Decision Framework

| Record Count | Recommended Approach | Command |
|-------------|---------------------|---------|
| 1 | Single record API | `sf data create record` |
| 2-200 | sObject Tree (preserves relationships) | `sf data import tree` |
| 200-2,000 | Tree with split files OR Bulk API | `sf data import tree` / `sf data import bulk` |
| 2,000-10,000 | Bulk API 2.0 | `sf data import bulk` |
| 10,000-150M | Bulk API 2.0 (batched automatically) | `sf data import bulk` |
| 150M+ | Contact Salesforce / Data Loader | External tooling |

> Bulk API 2.0 limits and CSV format requirements: `references/bulk-api.md`

**Summary limits**: 10K records/batch, 10 MB/batch, 15K batches/24h, 150M records/day

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

> Full implementation and extended examples: `references/test-data-factory.md`

### Naming Convention
```
TestDataFactory_[ObjectName]
```

### API Surface (per factory class)

| Method | Signature | Purpose |
|--------|-----------|---------|
| `create` | `(Integer count)` | Default records, auto-insert |
| `create` | `(Integer count, Boolean doInsert)` | Control insertion |
| `create` | `(Integer count, String rtDevName, Boolean doInsert)` | With RecordType |
| `createWithOverrides` | `(Integer count, Map<String,Object> overrides)` | Field overrides |
| `createContactsForAccount` | `(Integer count, Id accountId)` | Child records |
| `getRecordTypeId` | `(String developerName)` | Cached RT lookup |

### Key Principles

1. Always create in lists (bulk support)
2. Provide `doInsert` parameter (caller controls DML)
3. Synthetic data only (`@example.com`, `Test_` prefix)
4. Cache RecordType lookups (query once)
5. Annotate with `@isTest` (excluded from org code size limit)

---

## Data Masking & Anonymization

> Full masking strategy, tools, and Apex script: `references/data-masking.md`

For sandbox refreshes: use Salesforce Data Mask (managed package) or post-refresh Apex scripts. Mask Names, Email, Phone, SSN, Financial, Address, and Free-text fields. Never skip masking, even on dev sandboxes.

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

## Validation Scoring (130 Points)

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
| `INVALID_FIELD` | Field doesn't exist or FLS | Verify field API names via `sf-metadata`; check Permission Sets |
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

---

## Completion Format

```
Data Operation Complete: [Operation Type]
  Object: [ObjectName] | Records: [Count] | Org: [alias]
  Created: [n] | Updated: [n] | Deleted: [n]
  Validation: [PASSED/FAILED] (Score: XX/130)
  Cleanup: sf data delete bulk --file cleanup.csv --sobject [Object] --target-org [alias]
```

---

## Notes

- **API Version**: Recommend 62.0+
- **Bulk API 2.0**: Used for all bulk operations (classic Bulk API deprecated)
- **JSON Output**: Always use `--json` flag for scriptable output
- **Test Isolation**: Use savepoints for reversible test data
- **Sensitive Data**: Never include real PII in test data
- **Tree Import Limit**: 200 records per file; split larger datasets
- **sf CLI v2 required**: `npm install -g @salesforce/cli`

---

## Sources

- [Salesforce CLI Data Commands Reference](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_data_commands_unified.htm)
- [sObject Tree API](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_setup/sfdx_dev_data_tree.htm)
- [Bulk API 2.0 Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm)
- [Governor Limits Quick Reference](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_apexgov.htm)
- [Apex Testing Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_best_practices.htm)
- [Salesforce Data Mask Overview](https://help.salesforce.com/s/articleView?id=platform.data_mask_overview.htm&language=en_US&type=5)
