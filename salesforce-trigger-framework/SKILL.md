---
name: salesforce-trigger-framework
description: "Salesforce Apex Trigger Actions Framework implementation for PS Advisory projects. Use this skill when: (1) Creating new Apex triggers, (2) Adding trigger logic to existing objects, (3) Implementing bypass mechanisms, (4) Setting up trigger framework in a new org, (5) Creating trigger handler/action classes, (6) Coordinating Apex triggers with Flow automations, (7) Any task involving Salesforce trigger patterns or trigger frameworks. This skill enforces PS Advisory conventions including naming standards (TA_*, *Trigger), layered architecture (Trigger -> Action -> Service -> DAL), Custom Metadata configuration, and comprehensive test coverage requirements."
license: MIT
metadata:
  version: "2.1"
  author: "PS Advisory"
  framework_author: "Mitch Spano"
  enriched_date: "2026-02-18"
  framework_repo: "https://github.com/mitchspano/trigger-actions-framework"
---

# Salesforce Trigger Actions Framework

**Architecture**: `Trigger -> MetadataTriggerHandler -> Trigger Actions (TA_*) -> Services -> DAL`

## When to Use This Skill

- Creating triggers on any Salesforce object
- Adding business logic that should fire on record DML
- Setting up a new org's trigger architecture
- Coordinating Apex and Flow automations
- Implementing bypass mechanisms for data loads

## Cross-Skill References

| Skill | When to Load Together |
|-------|----------------------|
| `sf-apex` | Always -- every TA_* class follows sf-apex coding standards |
| `sf-testing` | When writing or running tests for trigger actions |
| `sf-flow` | When orchestrating Flows alongside Apex in trigger context |
| `sf-deploy` | When deploying trigger framework components to an org |
| `sf-metadata` | When creating or modifying framework metadata records |
| `sf-debug` | When troubleshooting trigger actions not firing or firing incorrectly |
| `sf-data` | When building test data for 200+ record bulk trigger tests |
| `sf-soql` | When building or optimizing DAL query methods |

**Loading order**: `salesforce-trigger-framework` -> `sf-apex` -> `sf-testing` -> `sf-deploy` -> `sf-debug`

## Framework Installation

```bash
# Option 1: Unlocked package
sf package install --package 04t8b000001Hep2AAC --target-org <alias> --wait 10

# Option 2: Source deployment
git clone https://github.com/mitchspano/trigger-actions-framework.git
cd trigger-actions-framework
sf project deploy start --source-dir trigger-actions-framework --target-org <alias>
```

Verify these exist in org: `TriggerBase`, `MetadataTriggerHandler`, `TriggerActionFlow`, `sObject_Trigger_Setting__mdt`, `Trigger_Action__mdt`.

## PS Advisory Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Trigger | `<ObjectName>Trigger` | `LeadTrigger` |
| Trigger Action | `TA_<ObjectName>_<ActionDescription>` | `TA_Lead_ValidateRequiredFields` |
| Test Class | `TA_<ObjectName>_<ActionDescription>_Test` | `TA_Lead_ValidateRequiredFields_Test` |
| Service Class | `<ObjectName>Service` | `LeadService` |
| DAL Class | `DAL_<ObjectName>` | `DAL_Lead` |

- **Execution order spacing**: increments of 10 (10, 20, 30...)
- **Test coverage**: 95%+ on all trigger actions and services

## Workflow: Adding Trigger Logic to an Object

### Step 1: Check if Trigger Exists

```bash
grep -r "trigger.*on <ObjectName>" force-app/main/default/triggers/
```

If trigger exists, skip to Step 3.

### Step 2: Create the Trigger

**File**: `force-app/main/default/triggers/<ObjectName>Trigger.trigger`

```apex
trigger <ObjectName>Trigger on <ObjectName> (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete
) {
    new MetadataTriggerHandler().run();
}
```

**Meta file**: `force-app/main/default/triggers/<ObjectName>Trigger.trigger-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexTrigger xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <status>Active</status>
</ApexTrigger>
```

### Step 3: Create sObject Trigger Setting (if new object)

**File**: `force-app/main/default/customMetadata/sObject_Trigger_Setting.<ObjectName>.md-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label><ObjectName></label>
    <protected>false</protected>
    <values>
        <field>Object_API_Name__c</field>
        <value xsi:type="xsd:string"><ObjectAPIName__c or ObjectName></value>
    </values>
    <values>
        <field>Bypass_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
</CustomMetadata>
```

### Step 4: Create the Trigger Action Class

**File**: `force-app/main/default/classes/TA_<ObjectName>_<ActionDescription>.cls`

```apex
public with sharing class TA_<ObjectName>_<ActionDescription> implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<<ObjectName>> newList) {
        <ObjectName>Service.methodName(newList);
    }
}
```

**Available interfaces**: `TriggerAction.BeforeInsert`, `.AfterInsert`, `.BeforeUpdate`, `.AfterUpdate`, `.BeforeDelete`, `.AfterDelete`, `.AfterUndelete`.

For full patterns per context, see [trigger-action-patterns.md](references/trigger-action-patterns.md).

### Step 5: Create the Trigger Action Metadata Record

**File**: `force-app/main/default/customMetadata/Trigger_Action.<ObjectName>_<Context>_<Order>_<ActionName>.md-meta.xml`

**IMPORTANT**: Use context-specific fields (`Before_Insert__c`, `After_Update__c`, etc.) -- NOT a generic `sObject__c` lookup.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label><ObjectName> <Context> <Order> <ActionDescription></label>
    <protected>false</protected>
    <values>
        <field>Apex_Class_Name__c</field>
        <value xsi:type="xsd:string">TA_<ObjectName>_<ActionDescription></value>
    </values>
    <values>
        <field>Order__c</field>
        <value xsi:type="xsd:double"><Order></value>
    </values>
    <values>
        <field><Context>__c</field>
        <value xsi:type="xsd:string"><ObjectName></value>
    </values>
    <values>
        <field>Description__c</field>
        <value xsi:type="xsd:string">Description of what this action does</value>
    </values>
    <values>
        <field>Allow_Flow_Recursion__c</field>
        <value xsi:type="xsd:boolean">false</value>
    </values>
</CustomMetadata>
```

**Context field values**: `Before_Insert`, `After_Insert`, `Before_Update`, `After_Update`, `Before_Delete`, `After_Delete`, `After_Undelete`.

### Step 6: Create the Test Class

**File**: `force-app/main/default/classes/TA_<ObjectName>_<ActionDescription>_Test.cls`

```apex
@IsTest
private class TA_<ObjectName>_<ActionDescription>_Test {
    @TestSetup
    static void makeData() {
        // Create test data
    }

    @IsTest
    static void testBeforeInsert_positiveCase() {
        // Arrange, Act (insert records), Assert
    }

    @IsTest
    static void testBeforeInsert_negativeCase() {
        // Test edge cases and error conditions
    }
}
```

For comprehensive testing strategies, see [testing-patterns.md](references/testing-patterns.md).

### Step 7: Verify the Implementation

```bash
sf project deploy start --source-dir force-app --target-org <alias>
sf apex run test --class-names TA_<ObjectName>_<ActionDescription>_Test --target-org <alias> --result-format human
```

## Bypass Mechanisms

```apex
// Action-level bypass
TriggerBase.bypass('TA_Lead_ValidateRequiredFields');
insert leads;
TriggerBase.clearBypass('TA_Lead_ValidateRequiredFields');

// Object-level bypass
MetadataTriggerHandler.bypass('Lead');
insert leads;
MetadataTriggerHandler.clearBypass('Lead');
```

For permission-based bypass, flow bypass, and comprehensive patterns, see [bypass-strategies.md](references/bypass-strategies.md).

## Layered Architecture: Action -> Service -> DAL

| Layer | Responsibility | Queries/DML? | Reusable? |
|-------|---------------|:---:|:---:|
| Trigger Action (TA_*) | Filter records, delegate to service | No | No |
| Service | Business logic, orchestrate DAL calls | Via DAL | Yes |
| DAL | All SOQL queries and DML operations | Yes | Yes |

For full service and DAL class examples, see [service-dal-patterns.md](references/service-dal-patterns.md).

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|-----------------|
| SOQL inside a loop | Hits 100 query limit at scale | Collect criteria, query once outside loop |
| DML in before context | Record Ids are null in before insert; wrong place for child DML | Use after context for related record DML |
| Business logic in TA_* class | Not reusable from Batch/LWC/API | Delegate to Service class |
| Single record method signatures | Fails bulkification | Always accept `List<SObject>` or `Set<Id>` |
| Not clearing bypass | Subsequent DML in same transaction skips triggers silently | Always use `try/finally` with `clearBypass()` |
| Same `Order__c` on two actions | Non-deterministic execution order | Use unique values with spacing of 10 |
| Modifying `newList` records in after context | `Trigger.new` is read-only in after context | Use before context for field changes; DML separately in after |
| Callouts in trigger context | Not allowed synchronously | Enqueue Queueable or publish Platform Event |
| Static variables assumed to reset between batches | They persist across 200-record chunks in one DML | Clear static collections if needed between batches |
| Using `sObject__c` field in Trigger_Action__mdt | Wrong field -- framework uses context-specific lookups | Use `Before_Insert__c`, `After_Update__c`, etc. |

## Before vs After Context Decision

| Need | Context |
|------|---------|
| Set/compute field values on triggering record | Before Insert / Before Update |
| Validate and block save with `addError()` | Before Insert / Before Update / Before Delete |
| Create/update related records (need Id) | After Insert / After Update |
| Publish platform events | After Insert / After Update |
| Audit deletion | After Delete |
| Restore related data | After Undelete |

For recursion control, DmlFinalizer, dynamic entry criteria, Queueable/Platform Event/Batch patterns, see [advanced-patterns.md](references/advanced-patterns.md).

## Trigger Context Variable Availability

| Variable | BI | AI | BU | AU | BD | AD | AUnd |
|----------|:--:|:--:|:--:|:--:|:--:|:--:|:----:|
| `newList` | Y | Y | Y | Y | -- | -- | Y |
| `newMap` | -- | Y | Y | Y | -- | -- | Y |
| `oldList` | -- | -- | Y | Y | Y | Y | -- |
| `oldMap` | -- | -- | Y | Y | Y | Y | -- |
| Record Ids | -- | Y | Y | Y | Y | Y | Y |
| Can modify directly | Y | -- | Y | -- | -- | -- | -- |
| `addError()` | Y | Y | Y | Y | Y | Y | Y |

## Salesforce Order of Execution (where triggers fit)

```
1. System validation rules
2. Before-save record-triggered flows
3. Apex BEFORE triggers          <-- your Before actions
4. Custom validation rules
5. Duplicate rules
6. Record saved (not committed)
7. Apex AFTER triggers           <-- your After actions
8. Assignment/auto-response rules
9. Workflow rules
10. After-save record-triggered flows
11. Roll-up summaries, cross-object workflow (can re-trigger)
12. DML committed
```

## Gotchas

| Gotcha | Mitigation |
|--------|------------|
| Validation rules fire AFTER before triggers | Before-trigger field changes are visible to validation rules |
| Before-save flows run BEFORE Apex triggers | Account for Flow modifications in action logic |
| Mixed DML in tests (User + SObject) | Use `System.runAs()` or separate `@future` method |
| `Trigger.newMap` null in before insert | Records have no Id yet -- do not build Map from Ids |
| `addError` in after context rolls back entire batch | Prefer validation in before context |
| Static variables persist across 200-record chunks | Clear collections between batches if needed |
| `Order__c` ties are non-deterministic | Always use unique Order values |
| Custom Metadata deploys are all-or-nothing | Validate all records locally before deploying |
| Flow recursion limit is 3 (not 16 like Apex) | Set `Allow_Flow_Recursion__c = false` |

## Common Deployment Errors

| Error | Fix |
|-------|-----|
| `Invalid type: MetadataTriggerHandler` | Install framework: `sf package install --package 04t8b000001Hep2AAC --target-org <alias> --wait 10` |
| `Duplicate developer name` on Custom Metadata | Ensure unique DeveloperName per record |
| `Required field missing: Object_API_Name__c` | Add `Object_API_Name__c` to sObject_Trigger_Setting record |
| `Entity is not org-accessible` | Deploy CMT types before CMT records |
| Test: `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Use `TriggerBase.bypass()` in test setup or satisfy validation rules |
| Test: `List has no rows for assignment` | Include Custom Metadata records in deployment package |
| `Apex CPU time limit exceeded` | Profile actions, move heavy logic to async |

**Deployment order**: Framework classes -> CMT types -> Triggers -> Action classes -> Service/DAL classes -> Test classes -> CMT records.

## Metadata Fields Reference

**sObject_Trigger_Setting__mdt**: `Object_API_Name__c`, `Bypass_Execution__c` (checkbox), `Bypass_Permission__c`, `Required_Permission__c`.

**Trigger_Action__mdt**: `Apex_Class_Name__c`, `Order__c`, `Before_Insert__c`/`After_Insert__c`/etc. (context lookup), `Description__c`, `Flow_Name__c`, `Entry_Criteria__c` (formula), `Allow_Flow_Recursion__c`, `Bypass_Execution__c` (checkbox), `Bypass_Permission__c`, `Required_Permission__c`.

## Troubleshooting: Action Not Firing

1. **Wrong context field** -- Must use `Before_Insert__c`, not `sObject__c`
2. **Missing sObject_Trigger_Setting__mdt** -- `Object_API_Name__c` must match exactly (case-sensitive, include `__c` for custom objects)
3. **Trigger not calling MetadataTriggerHandler** -- Verify `new MetadataTriggerHandler().run();`
4. **Bypass checkbox checked** -- Check `Bypass_Execution__c` on both setting and action records

```bash
# Debug: check sObject setting
sf data query --query "SELECT DeveloperName, Object_API_Name__c, Bypass_Execution__c FROM sObject_Trigger_Setting__mdt WHERE Object_API_Name__c = '<ObjectName>'" --target-org <alias>

# Debug: check trigger action config
sf data query --query "SELECT Label, Apex_Class_Name__c, Before_Insert__c, After_Insert__c, Before_Update__c, After_Update__c, Bypass_Execution__c FROM Trigger_Action__mdt WHERE Apex_Class_Name__c LIKE '%<ObjectName>%'" --target-org <alias>
```

## File Checklist for New Trigger Logic

- [ ] `triggers/<ObjectName>Trigger.trigger` (if new object)
- [ ] `triggers/<ObjectName>Trigger.trigger-meta.xml` (if new object)
- [ ] `customMetadata/sObject_Trigger_Setting.<ObjectName>.md-meta.xml` (if new object)
- [ ] `classes/TA_<ObjectName>_<ActionDescription>.cls`
- [ ] `classes/TA_<ObjectName>_<ActionDescription>.cls-meta.xml`
- [ ] `customMetadata/Trigger_Action.<UniqueLabel>.md-meta.xml`
- [ ] `classes/TA_<ObjectName>_<ActionDescription>_Test.cls`
- [ ] `classes/TA_<ObjectName>_<ActionDescription>_Test.cls-meta.xml`
- [ ] Service class if new business logic domain
- [ ] DAL class if new data access patterns

## Flow Integration

Register Flows as trigger actions using `TriggerActionFlow` as the Apex class and `Flow_Name__c` for the Flow API name. Flows share execution order with Apex actions via `Order__c`.

For Flow variable requirements, before-context rules, and complete examples, see [flow-integration.md](references/flow-integration.md).

## Migration from Legacy Frameworks

For step-by-step migration from Kevin O'Hara, fflib, SBLI, or no-framework triggers, see [migration-guide.md](references/migration-guide.md).

## References

| File | Contents |
|------|----------|
| [trigger-action-patterns.md](references/trigger-action-patterns.md) | All interface patterns with context-specific examples and anti-patterns |
| [testing-patterns.md](references/testing-patterns.md) | Testing strategies, bypass testing, bulk testing, mocking, TestDataFactory |
| [bypass-strategies.md](references/bypass-strategies.md) | Permission-based, code-level, object-level, and Flow bypass patterns |
| [migration-guide.md](references/migration-guide.md) | Migrating from O'Hara, fflib, SBLI, or no-framework triggers |
| [flow-integration.md](references/flow-integration.md) | Flow variable requirements, registration, ordering, and limitations |
| [service-dal-patterns.md](references/service-dal-patterns.md) | Service class structure, DAL patterns, selectors, mocking, lazy loading |
| [advanced-patterns.md](references/advanced-patterns.md) | Recursion control, DmlFinalizer, entry criteria, Queueable/Platform Event/Batch patterns |

## Dependencies

- Salesforce CLI (`sf`)
- Trigger Actions Framework package (04t8b000001Hep2AAC) or source deployment
- API Version 55.0 or higher recommended
