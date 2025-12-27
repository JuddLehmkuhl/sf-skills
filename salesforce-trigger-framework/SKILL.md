---
name: salesforce-trigger-framework
description: "Salesforce Apex Trigger Actions Framework implementation for PS Advisory projects. Use this skill when: (1) Creating new Apex triggers, (2) Adding trigger logic to existing objects, (3) Implementing bypass mechanisms, (4) Setting up trigger framework in a new org, (5) Creating trigger handler/action classes, (6) Coordinating Apex triggers with Flow automations, (7) Any task involving Salesforce trigger patterns or trigger frameworks. This skill enforces PS Advisory conventions including naming standards (TA_*, *Trigger), layered architecture (Trigger → Action → Service → DAL), Custom Metadata configuration, and comprehensive test coverage requirements."
---

# Salesforce Trigger Actions Framework

## Overview

This skill implements **Mitch Spano's Trigger Actions Framework** with PS Advisory conventions. The framework provides metadata-driven trigger orchestration, enabling declarative control over execution order, bypass mechanisms, and Apex/Flow coordination.

**Architecture**: `Trigger → MetadataTriggerHandler → Trigger Actions (TA_*) → Services → DAL`

## When to Use This Skill

- Creating triggers on any Salesforce object
- Adding business logic that should fire on record DML
- Setting up a new org's trigger architecture
- Coordinating Apex and Flow automations
- Implementing bypass mechanisms for data loads

## Framework Installation

### Step 1: Deploy Framework Core

The framework requires deployment from the official repository. Run:

```bash
# Clone the framework
git clone https://github.com/mitchspano/trigger-actions-framework.git

# Deploy to target org (adjust for your auth method)
cd trigger-actions-framework
sf project deploy start --source-dir trigger-actions-framework --target-org <alias>
```

**Alternative**: Use the unlocked package installation:
```bash
sf package install --package 04t8b000001Hep2AAC --target-org <alias> --wait 10
```

### Step 2: Verify Installation

Confirm these components exist in the org:
- `TriggerBase` (Apex Class)
- `MetadataTriggerHandler` (Apex Class)
- `TriggerActionFlow` (Apex Class)
- `sObject_Trigger_Setting__mdt` (Custom Metadata Type)
- `Trigger_Action__mdt` (Custom Metadata Type)

## PS Advisory Conventions

### Naming Standards

| Component | Convention | Example |
|-----------|------------|---------|
| Trigger | `<ObjectName>Trigger` | `LeadTrigger`, `OpportunityTrigger` |
| Trigger Action | `TA_<ObjectName>_<ActionDescription>` | `TA_Lead_ValidateRequiredFields` |
| Test Class | `TA_<ObjectName>_<ActionDescription>_Test` | `TA_Lead_ValidateRequiredFields_Test` |
| Service Class | `<ObjectName>Service` | `LeadService` |
| DAL Class | `DAL_<ObjectName>` | `DAL_Lead` |

### Execution Order Spacing

Use increments of **10** for order values to allow insertion of new actions:
- 10, 20, 30... (not 1, 2, 3)

### Test Coverage Requirement

Maintain **95%+ code coverage** on all trigger actions and services.

## Workflow: Adding Trigger Logic to an Object

### Step 1: Check if Trigger Exists

```bash
# Search for existing trigger
grep -r "trigger.*on <ObjectName>" force-app/main/default/triggers/
```

**If trigger exists**: Skip to Step 3
**If no trigger**: Continue to Step 2

### Step 2: Create the Trigger

Create a logic-less trigger that delegates to MetadataTriggerHandler.

**Template location**: `assets/templates/ObjectTrigger.trigger`

```apex
trigger <ObjectName>Trigger on <ObjectName> (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete
) {
    new MetadataTriggerHandler().run();
}
```

**File path**: `force-app/main/default/triggers/<ObjectName>Trigger.trigger`

Also create the meta file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexTrigger xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <status>Active</status>
</ApexTrigger>
```

**File path**: `force-app/main/default/triggers/<ObjectName>Trigger.trigger-meta.xml`

### Step 3: Create sObject Trigger Setting (if new object)

Create Custom Metadata record to enable the framework for this object.

**File path**: `force-app/main/default/customMetadata/sObject_Trigger_Setting.<ObjectName>.md-meta.xml`

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

Each discrete piece of business logic gets its own action class.

**Read the full reference**: See [trigger-action-patterns.md](references/trigger-action-patterns.md) for all context interfaces and patterns.

**Basic template**:

```apex
public with sharing class TA_<ObjectName>_<ActionDescription> implements TriggerAction.BeforeInsert {
    
    public void beforeInsert(List<<ObjectName>> newList) {
        // Delegate to service layer
        <ObjectName>Service.methodName(newList);
    }
}
```

**Available interfaces** (implement only what you need):
- `TriggerAction.BeforeInsert`
- `TriggerAction.AfterInsert`
- `TriggerAction.BeforeUpdate`
- `TriggerAction.AfterUpdate`
- `TriggerAction.BeforeDelete`
- `TriggerAction.AfterDelete`
- `TriggerAction.AfterUndelete`

**File path**: `force-app/main/default/classes/TA_<ObjectName>_<ActionDescription>.cls`

### Step 5: Create the Trigger Action Metadata Record

Register the action with the framework.

**File path**: `force-app/main/default/customMetadata/Trigger_Action.<ObjectName>_<Context>_<Order>_<ActionName>.md-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
        <field>Bypass_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>sObject__c</field>
        <value xsi:type="xsd:string">sObject_Trigger_Setting.<ObjectName></value>
    </values>
    <values>
        <field>Flow_Name__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Allow_Flow_Recursion__c</field>
        <value xsi:type="xsd:boolean">false</value>
    </values>
</CustomMetadata>
```

**Context values for label**: `Before_Insert`, `After_Insert`, `Before_Update`, `After_Update`, `Before_Delete`, `After_Delete`, `After_Undelete`

### Step 6: Create the Test Class

Every trigger action requires a corresponding test class.

**Read the full reference**: See [testing-patterns.md](references/testing-patterns.md) for comprehensive testing strategies.

```apex
@IsTest
private class TA_<ObjectName>_<ActionDescription>_Test {
    
    @TestSetup
    static void makeData() {
        // Create test data
    }
    
    @IsTest
    static void testBeforeInsert_positiveCase() {
        // Arrange
        List<<ObjectName>> records = new List<<ObjectName>>();
        // Add test records
        
        // Act
        Test.startTest();
        insert records;
        Test.stopTest();
        
        // Assert
        // Verify expected behavior
    }
    
    @IsTest
    static void testBeforeInsert_negativeCase() {
        // Test edge cases and error conditions
    }
}
```

### Step 7: Verify the Implementation

```bash
# Deploy and run tests
sf project deploy start --source-dir force-app --target-org <alias>
sf apex run test --class-names TA_<ObjectName>_<ActionDescription>_Test --target-org <alias> --result-format human
```

## Workflow: Integrating Flow with Trigger Actions

The framework can orchestrate Flows alongside Apex actions.

### Step 1: Create the Flow

Create an Auto-Launched Flow with these required variables:
- `newList` (Record Collection, Input)
- `oldList` (Record Collection, Input) - for update/delete contexts
- `newListAfterFlow` (Record Collection, Output) - for before contexts only

### Step 2: Register the Flow as a Trigger Action

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>Lead Before_Insert 25 Enrich_From_External</label>
    <protected>false</protected>
    <values>
        <field>Apex_Class_Name__c</field>
        <value xsi:type="xsd:string">TriggerActionFlow</value>
    </values>
    <values>
        <field>Flow_Name__c</field>
        <value xsi:type="xsd:string">Lead_Enrich_From_External</value>
    </values>
    <values>
        <field>Order__c</field>
        <value xsi:type="xsd:double">25</value>
    </values>
    <values>
        <field>sObject__c</field>
        <value xsi:type="xsd:string">sObject_Trigger_Setting.Lead</value>
    </values>
    <values>
        <field>Allow_Flow_Recursion__c</field>
        <value xsi:type="xsd:boolean">false</value>
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

## Bypass Mechanisms

### Permission-Based Bypass

Add a Custom Permission and reference it in the metadata:

```xml
<values>
    <field>Bypass_Permission__c</field>
    <value xsi:type="xsd:string">Bypass_Lead_Triggers</value>
</values>
```

### Code-Level Bypass

```apex
// Bypass a specific action
TriggerBase.bypass('TA_Lead_ValidateRequiredFields');

// Perform DML without that action running
insert leads;

// Clear the bypass
TriggerBase.clearBypass('TA_Lead_ValidateRequiredFields');
```

### Object-Level Bypass

```apex
// Bypass all actions for an object
MetadataTriggerHandler.bypass('Lead');

// Perform DML
insert leads;

// Clear bypass
MetadataTriggerHandler.clearBypass('Lead');
```

## Layered Architecture Integration

### Pattern: Action → Service → DAL

```
┌─────────────────────────────────────────────────────┐
│ TA_Lead_AssignOwner (Trigger Action)                │
│   └── LeadService.assignOwnerByTerritory(newList)  │
│         └── DAL_Lead.getLeadsByTerritory(...)      │
│         └── DAL_User.getActiveUsersByRole(...)     │
└─────────────────────────────────────────────────────┘
```

**Rules**:
1. Trigger Actions call Services, never DAL directly
2. Services contain business logic, call DAL for data access
3. DAL classes contain all SOQL/DML operations
4. Services and DAL are reusable from Batch, Queueable, LWC, etc.

## File Checklist for New Trigger Logic

When adding trigger logic, ensure ALL these files are created:

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

## References

- [trigger-action-patterns.md](references/trigger-action-patterns.md) - All interface patterns with examples
- [testing-patterns.md](references/testing-patterns.md) - Testing strategies and mocking
- [bypass-strategies.md](references/bypass-strategies.md) - Comprehensive bypass documentation
- [migration-guide.md](references/migration-guide.md) - Migrating from legacy frameworks
- [flow-integration.md](references/flow-integration.md) - Detailed Flow coordination patterns

## Quick Reference: Common Patterns

### Before Insert with Validation

```apex
public with sharing class TA_Lead_ValidateRequiredFields implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (String.isBlank(l.Company)) {
                l.addError('Company is required');
            }
        }
    }
}
```

### After Insert with Related Record Creation

```apex
public with sharing class TA_Opportunity_CreateDefaultLineItems implements TriggerAction.AfterInsert {
    public void afterInsert(List<Opportunity> newList) {
        OpportunityService.createDefaultLineItems(newList);
    }
}
```

### Before Update with Field Change Detection

```apex
public with sharing class TA_Case_EscalateOnPriorityChange implements TriggerAction.BeforeUpdate {
    public void beforeUpdate(List<Case> newList, List<Case> oldList) {
        Map<Id, Case> oldMap = new Map<Id, Case>(oldList);
        List<Case> priorityChangedCases = new List<Case>();
        
        for (Case c : newList) {
            Case oldCase = oldMap.get(c.Id);
            if (c.Priority != oldCase.Priority && c.Priority == 'High') {
                priorityChangedCases.add(c);
            }
        }
        
        if (!priorityChangedCases.isEmpty()) {
            CaseService.escalate(priorityChangedCases);
        }
    }
}
```

## Dependencies

- Salesforce CLI (`sf`)
- Trigger Actions Framework package or source
- API Version 55.0 or higher recommended
