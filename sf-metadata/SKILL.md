---
name: sf-metadata
description: >
  Generates and queries Salesforce metadata with 120-point scoring. Use when
  creating custom objects, fields, profiles, permission sets, validation rules,
  or querying org metadata structures via sf CLI.
license: MIT
metadata:
  version: "1.1.0"
  author: "Judd Lehmkuhl"
  scoring: "120 points across 6 categories"
  enriched: "2026-02-18"
---

# sf-metadata: Salesforce Metadata Generation and Org Querying

## Cross-Skill Integration

| Skill | Relationship | Key Integration Point |
|-------|-------------|----------------------|
| **sf-apex** | Describe objects for coding | `sf sobject describe --sobject Account` to discover fields before writing Apex |
| **sf-flow** | Describe fields for flow building | Provide field API names, record types, and validation rules for flow design |
| **sf-deploy** | Deploy metadata to org | `Skill(skill="sf-deploy", args="Deploy metadata at force-app/main/default/objects")` |
| **sf-data** | Test data after deploy | `Skill(skill="sf-data", args="Create test data for Invoice__c")` -- requires deployed objects |
| **sf-testing** | Test metadata dependencies | Verify Permission Sets, FLS, sharing rules in test context with `System.runAs()` |
| **sf-soql** | Field discovery for queries | Confirm field API names and relationship names before constructing SOQL |
| **sf-lwc** | Wire adapters need field API names | `import FIELD from '@salesforce/schema/Object.Field__c'` requires exact API names |
| **sf-diagram** | ERD generation from metadata | `Skill(skill="sf-diagram", args="Generate ERD for Invoice__c and related objects")` |
| **salesforce-trigger-framework** | Custom Metadata for trigger actions | CMT records (`sObject_Trigger_Setting__mdt`, `Trigger_Action__mdt`) configure TAF |

---

## CRITICAL: Orchestration Order

**sf-metadata -> sf-flow -> sf-deploy -> sf-data** (you are here: sf-metadata)

sf-data requires objects deployed to org. Always deploy BEFORE creating test data.

## CRITICAL: Field-Level Security

**Deployed fields are INVISIBLE until FLS is configured!** Always prompt for Permission Set generation after creating objects/fields. See **Phase 3.5**.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Operation type: **Generate** metadata OR **Query** org metadata
- If generating: metadata type, target object, specific requirements
- If querying: query type, target org alias, object/metadata type

**Then**: Check existing metadata (`Glob: **/*-meta.xml`), confirm sfdx-project.json exists, create TodoWrite tasks.

### Phase 2: Template Selection / Query Execution

#### Template Selection (Generation)

| Metadata Type | Template |
|---------------|----------|
| Custom Object | `templates/objects/custom-object.xml` |
| Text Field | `templates/fields/text-field.xml` |
| Number Field | `templates/fields/number-field.xml` |
| Currency Field | `templates/fields/currency-field.xml` |
| Date Field | `templates/fields/date-field.xml` |
| Checkbox Field | `templates/fields/checkbox-field.xml` |
| Picklist Field | `templates/fields/picklist-field.xml` |
| Multi-Select Picklist | `templates/fields/multi-select-picklist.xml` |
| Lookup Field | `templates/fields/lookup-field.xml` |
| Master-Detail Field | `templates/fields/master-detail-field.xml` |
| Formula Field | `templates/fields/formula-field.xml` |
| Roll-Up Summary | `templates/fields/rollup-summary-field.xml` |
| Email / Phone / URL | `templates/fields/email-field.xml` etc. |
| Text Area (Long) | `templates/fields/textarea-field.xml` |
| Profile | `templates/profiles/profile.xml` |
| Permission Set | `templates/permission-sets/permission-set.xml` |
| Validation Rule | `templates/validation-rules/validation-rule.xml` |
| Record Type | `templates/record-types/record-type.xml` |
| Page Layout | `templates/layouts/page-layout.xml` |

**Template Path Resolution** (try in order):
1. `~/.claude/plugins/marketplaces/sf-skills/sf-metadata/templates/[path]`
2. `[project-root]/sf-metadata/templates/[path]`

#### Query Execution (sf CLI v2)

| Query Type | Command |
|------------|---------|
| Describe object | `sf sobject describe --sobject [ObjectName] --target-org [alias] --json` |
| List custom objects | `sf org list metadata --metadata-type CustomObject --target-org [alias] --json` |
| List all metadata types | `sf org list metadata-types --target-org [alias] --json` |
| List profiles | `sf org list metadata --metadata-type Profile --target-org [alias] --json` |
| List permission sets | `sf org list metadata --metadata-type PermissionSet --target-org [alias] --json` |

### Phase 3: Generation / Validation

**File paths**:
- Objects: `force-app/main/default/objects/[ObjectName__c]/[ObjectName__c].object-meta.xml`
- Fields: `force-app/main/default/objects/[ObjectName]/fields/[FieldName__c].field-meta.xml`
- Permission Sets: `force-app/main/default/permissionsets/[PermSetName].permissionset-meta.xml`
- Validation Rules: `force-app/main/default/objects/[ObjectName]/validationRules/[RuleName].validationRule-meta.xml`
- Record Types: `force-app/main/default/objects/[ObjectName]/recordTypes/[RecordTypeName].recordType-meta.xml`
- Layouts: `force-app/main/default/layouts/[ObjectName]-[LayoutName].layout-meta.xml`

**Standard vs Custom Object Paths**:

| Object Type | Path Example |
|-------------|--------------|
| Standard (Lead) | `objects/Lead/fields/Lead_Score__c.field-meta.xml` |
| Custom | `objects/MyObject__c/fields/MyField__c.field-meta.xml` |

**Validation Report Format** (6-Category Scoring 0-120):
```
Score: 105/120 ---- Very Good
-- Structure & Format:  20/20 (100%)
-- Naming Conventions:  18/20 (90%)
-- Data Integrity:      15/20 (75%)
-- Security & FLS:      20/20 (100%)
-- Documentation:       18/20 (90%)
-- Best Practices:      14/20 (70%)
```

### Phase 3.5: Permission Set Auto-Generation

**After creating Custom Objects or Fields, ALWAYS prompt the user** for Permission Set generation.

**Permission Set field inclusion rules**:

| Field Type | Include? | Notes |
|------------|----------|-------|
| Required fields | NO | Auto-visible, Salesforce rejects in Permission Set |
| Optional fields | YES | `editable: true, readable: true` |
| Formula fields | YES | `editable: false, readable: true` |
| Roll-Up Summary | YES | `editable: false, readable: true` |
| Master-Detail | NO | Controlled by parent object permissions |
| Name field | NO | Always visible |

**Permission Set XML pattern**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Auto-generated: Grants access to [Object] and its fields</description>
    <hasActivationRequired>false</hasActivationRequired>
    <label>[Object] Access</label>
    <objectPermissions>
        <allowCreate>true</allowCreate>
        <allowDelete>true</allowDelete>
        <allowEdit>true</allowEdit>
        <allowRead>true</allowRead>
        <modifyAllRecords>false</modifyAllRecords>
        <object>[ObjectName__c]</object>
        <viewAllRecords>true</viewAllRecords>
    </objectPermissions>
    <!-- Required fields EXCLUDED (auto-visible) -->
    <!-- Formula fields have editable=false -->
    <fieldPermissions>
        <editable>true</editable>
        <field>[ObjectName__c].[FieldName__c]</field>
        <readable>true</readable>
    </fieldPermissions>
</PermissionSet>
```

### Phase 4: Deployment

```
Skill(skill="sf-deploy", args="Deploy metadata at force-app/main/default/objects/[ObjectName] and permission set to [target-org]")
```

Post-deployment: `sf org assign permset --name [ObjectName]_Access --target-org [alias]`

### Phase 5: Verification

```
Metadata Complete: [MetadataName]
  Type: [CustomObject/CustomField/etc.] | API: 62.0
  Location: force-app/main/default/[path]
  Validation: PASSED (Score: XX/120)
Next Steps: Verify in Setup, check FLS, add to Page Layouts
```

---

## Deep-Dive References

Detailed content has been extracted into reference files. Read these when working in a specific area.

| Reference | File | Content |
|-----------|------|---------|
| Custom Metadata Types | [`references/custom-metadata-types.md`](references/custom-metadata-types.md) | CMT decision matrix, XML templates, access patterns, Apex deploy API, managed packages |
| Sharing Model & Security | [`references/sharing-model.md`](references/sharing-model.md) | OWD matrix, sharing rule types/XML, role hierarchy, Apex sharing, Shield encryption |
| Record Types | [`references/record-types.md`](references/record-types.md) | When to use, business process mapping, XML templates, Apex/Flow access patterns |
| Page Layouts | [`references/page-layouts.md`](references/page-layouts.md) | Layout vs Lightning Record Page, compact layouts, Dynamic Forms, Path config |
| Global Value Sets | [`references/global-value-sets.md`](references/global-value-sets.md) | Global vs object-specific, XML templates, dependent picklists, migration patterns |
| Validation Rules (Advanced) | [`references/validation-rules-advanced.md`](references/validation-rules-advanced.md) | ISNEW/ISCHANGED/PRIORVALUE, VLOOKUP, bypass mechanisms, formula limits |
| Metadata API Patterns | [`references/metadata-api-patterns.md`](references/metadata-api-patterns.md) | package.xml, retrieve/deploy patterns, selective retrieval, API limits |

---

## Consolidated Gotchas

| Category | Gotcha | Impact | Fix |
|----------|--------|--------|-----|
| CMT | Cannot DML in Apex | Runtime error on insert/update | Use `Metadata.DeployContainer` for programmatic CRUD |
| CMT | No triggers on `__mdt` objects | Cannot react to CMT changes | Use platform events or scheduled checks |
| CMT | Deploy-only in production | No manual creation in prod | Deploy via change set, package, or Metadata API |
| CMT | SOQL counts against limits | Unexpected governor limit hits | Use `getInstance()` / `getAll()` instead |
| CMT | 10 MB storage limit | Exhausted CMT capacity | Monitor with `SELECT COUNT() FROM EntityDefinition WHERE QualifiedApiName LIKE '%__mdt'` |
| CMT | Test visibility | `getInstance()` returns deployed records in tests | Use `Metadata.DeployCallback` for test isolation |
| Security | `without sharing` is the default | Data leaks in Apex | Always declare `with sharing` or `inherited sharing` |
| Security | Sharing recalculation is async | Stale access after OWD change | Can take hours -- plan accordingly |
| Security | Manual shares deleted on ownership change | Lost access on reassignment | Use Apex Sharing Reasons (survive ownership changes) |
| Security | Guest user sharing is restrictive | No record ownership for guests | Requires explicit sharing rules |
| Security | PSGs do not affect sharing | Confusion about access level | PSGs grant object/field permissions only, not record access |
| Record Types | Record Type ID varies by org | Broken code on deploy | Never hardcode -- use `DeveloperName` lookups |
| Record Types | Master Record Type is hidden | Unexpected RT on records | Every object has one; used when no RT assigned |
| Record Types | RT assignment is per Profile | Users cannot see unassigned RTs | Assign in Profile settings |
| Record Types | Renaming DeveloperName | Breaks references in code/flows | Plan carefully; update all references |
| Page Layouts | Layout assignment matrix | Missing layout for Profile+RT combos | Every Profile + Record Type combination needs assignment |
| Page Layouts | 200 field limit | Deployment error | Max 200 fields per layout |
| Page Layouts | Mobile vs desktop differ | Inconsistent UX | Lightning Record Pages can have separate mobile/desktop layouts |
| Picklists | Multi-select limited to 500 values | Deployment error at limit | Consider Custom Object for large value sets |
| Picklists | Dependent picklist depth = 1 level | No cascading dependencies | Use Flow screen for multi-level cascades |
| Picklists | Formulas use API name not label | ISPICKVAL fails on label match | `ISPICKVAL(Status__c, 'Active')` uses API name |
| Picklists | Record Type filters picklist values | Users see unexpected subset | Each RT can restrict available values |
| Validation | Null handling | ISNULL misses empty strings | Use `ISBLANK()` (handles both null and empty) |
| Validation | Cross-object null | Null pointer in formula | Guard parent references with `ISBLANK()` |
| Validation | Integration bypass | API loads still trigger rules | Provide `$Permission.Bypass_Validation` mechanism |
| Validation | Batch operations | Errors roll back entire chunk | Validation fires per-record even in batch |
| Metadata API | Deploy order matters | Dependency failures | Deploy objects before fields, fields before VRs |
| Metadata API | Partial deploy = full rollback | One failure kills entire deploy | Test with `--dry-run` first |
| Metadata API | Destructive changes are permanent | Deleted metadata cannot be recovered | Use `destructiveChangesPost.xml` carefully |
| Metadata API | Source tracking = 3 days | Missed changes after gap | Re-retrieve if tracking window exceeded |

---

## Field Type Selection Guide

| Type | Salesforce | Notes |
|------|------------|-------|
| Text | Text / Text Area (Long/Rich) | <=255 chars / multi-line / HTML |
| Numbers | Number / Currency | Decimals or money (org currency) |
| Boolean | Checkbox | True/False |
| Choice | Picklist / Multi-Select | Single/multiple predefined options |
| Date | Date / DateTime | With or without time |
| Contact | Email / Phone / URL | Validated formats |
| Relationship | Lookup / Master-Detail | Optional / required parent |
| Calculated | Formula / Roll-Up | Derived from fields / children |

## Relationship Decision Matrix

| Scenario | Use | Reason |
|----------|-----|--------|
| Parent optional | Lookup | Child can exist without parent |
| Parent required | Master-Detail | Cascade delete, roll-up summaries |
| Many-to-Many | Junction Object | Two Master-Detail relationships |
| Self-referential | Hierarchical Lookup | Same object (e.g., Account hierarchy) |
| Cross-object formula | Master-Detail or Formula | Access parent fields |

---

## Metadata Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Profile-based FLS | Use Permission Sets for granular access |
| Hardcoded IDs in formulas | Use Custom Settings or Custom Metadata |
| Validation rule without bypass | Add `$Permission.Bypass_Validation__c` check |
| Too many picklist values (>200) | Consider Custom Object instead |
| Auto-number without prefix | Add meaningful prefix: `INV-{0000}` |
| Roll-up on non-M-D | Use trigger-based calculation or DLRS |
| Field label = API name | Use user-friendly labels |
| No description on custom objects | Always document purpose |

---

## Common Errors

| Error | Fix |
|-------|-----|
| `Cannot deploy to required field` | Remove from fieldPermissions (auto-visible) |
| `Field does not exist` | Create Permission Set with field access |
| `SObject type 'X' not supported` | Deploy metadata first |
| `Element X is duplicated` | Reorder XML elements alphabetically |

---

## Scoring System

**6-Category Scoring (0-120)**:

| Category (20 pts each) | Key Deductions |
|------------------------|----------------|
| **Structure & Format** | -10 invalid XML, -5 missing namespace, -5 outdated API version, -5 wrong file path |
| **Naming Conventions** | -3 missing `__c` suffix, -2 non-PascalCase, -2 abbreviations in labels |
| **Data Integrity** | -5 no defaults on required, -3 wrong precision/scale, -5 invalid formula syntax |
| **Security & FLS** | -5 exposed sensitive field, -10 SSN/CC patterns, -5 wrong sharing model |
| **Documentation** | -5 missing description, -3 no help text, -3 unclear VR error messages |
| **Best Practices** | -3 Profile-first FLS, -5 hardcoded IDs, -3 no page layout for RT |

**Thresholds**: 108+ Excellent | 96-107 Very Good | 84-95 Good | Block: <72

---

## Field Template Tips

**Number fields**: Omit `<defaultValue>` if empty or zero -- Salesforce ignores it. Only include for meaningful defaults.

**Common mistake**: Using `Lead__c` (with suffix) for standard Lead object. Standard objects have no `__c`.

---

## sf CLI Quick Reference

```bash
# Describe object
sf sobject describe --sobject Account --target-org [alias] --json

# List custom objects
sf org list metadata --metadata-type CustomObject --target-org [alias] --json

# List fields on object
sf org list metadata --metadata-type CustomField --folder Account --target-org [alias] --json

# List all metadata types
sf org list metadata-types --target-org [alias] --json

# Retrieve specific metadata
sf project retrieve start --metadata CustomObject:Account --target-org [alias]

# Generate package.xml from source
sf project generate manifest --source-dir force-app --name package.xml

# Generate custom object interactively
sf schema generate sobject --label "My Object"

# Generate custom field interactively
sf schema generate field --label "My Field" --object Account
```

---

## Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| FLS is the Silent Killer | Deployed fields invisible without FLS | Always prompt for Permission Set generation |
| Required Fields != Permission Sets | Salesforce rejects required fields in PS | Filter out required fields from fieldPermissions |
| Orchestration Order | sf-data fails if objects not deployed | sf-metadata -> sf-flow -> sf-deploy -> sf-data |
| Before-Save Efficiency | Before-Save auto-saves, no DML needed | Use Before-Save for same-record updates |
| Test with 251 Records | Batch boundary at 200 records | Always bulk test with 251+ records |

---

## Reference & Dependencies

**Docs**: `docs/` folder -- metadata-types-reference, field-types-guide, fls-best-practices, naming-conventions
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-metadata/docs/`

**Dependencies**: sf-deploy (optional) for deployment.

**Notes**: API 62.0 required | Permission Sets over Profiles | Block if score < 72

## Validation

```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-metadata/hooks/scripts/validate_metadata.py <file_path>
```

Scoring: 120 points / 6 categories. Minimum 84 (70%) for deployment.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
