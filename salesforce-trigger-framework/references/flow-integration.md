# Flow Integration Reference

## Table of Contents

1. [Overview](#overview)
2. [Creating Trigger Action Flows](#creating-trigger-action-flows)
3. [Flow Variable Requirements](#flow-variable-requirements)
4. [Registering Flows in Metadata](#registering-flows-in-metadata)
5. [Ordering Apex and Flow](#ordering-apex-and-flow)
6. [Before Context Flows](#before-context-flows)
7. [Bypassing Flows](#bypassing-flows)
8. [Limitations](#limitations)
9. [Best Practices](#best-practices)

## Overview

The Trigger Actions Framework allows Flows to be orchestrated alongside Apex trigger actions. This enables:

- **Unified execution order**: Sequence Flows between Apex actions
- **Single configuration view**: All automations visible in Custom Metadata
- **Consistent bypass mechanisms**: Same bypass patterns for Apex and Flow
- **Admin empowerment**: Admins can build Flows that integrate with developer Apex

## Creating Trigger Action Flows

### Step 1: Create an Auto-Launched Flow

1. Go to **Setup > Flows > New Flow**
2. Select **Autolaunched Flow (No Trigger)**
3. **Do NOT select Record-Triggered Flow** - the framework handles triggering

### Step 2: Add Required Variables

The framework passes record collections to your Flow via specific variable names.

## Flow Variable Requirements

### For All Contexts

| Variable Name | Type | Available For | Direction |
|---------------|------|---------------|-----------|
| `newList` | Record Collection | Insert, Update, Undelete | Input |
| `oldList` | Record Collection | Update, Delete | Input |

### For Before Contexts Only

| Variable Name | Type | Available For | Direction |
|---------------|------|---------------|-----------|
| `newListAfterFlow` | Record Collection | Before Insert, Before Update | Output |

### Variable Configuration

**newList Variable**:
- **Data Type**: Record
- **Object**: The sObject type (e.g., Lead)
- **Allow Multiple Values**: ✓ (Collection)
- **Available for Input**: ✓
- **Available for Output**: ✗

**oldList Variable**:
- **Data Type**: Record
- **Object**: The sObject type
- **Allow Multiple Values**: ✓ (Collection)
- **Available for Input**: ✓
- **Available for Output**: ✗

**newListAfterFlow Variable** (Before contexts only):
- **Data Type**: Record
- **Object**: The sObject type
- **Allow Multiple Values**: ✓ (Collection)
- **Available for Input**: ✗
- **Available for Output**: ✓

## Registering Flows in Metadata

### Trigger Action Metadata for Flow

**File**: `force-app/main/default/customMetadata/Trigger_Action.Lead_Before_Insert_25_EnrichFromExternal.md-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>Lead Before_Insert 25 EnrichFromExternal</label>
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

**Key fields**:
- `Apex_Class_Name__c`: Always `TriggerActionFlow` for Flows
- `Flow_Name__c`: The API name of your Flow
- `Allow_Flow_Recursion__c`: Set to `true` only if Flow needs to run recursively

## Ordering Apex and Flow

### Example: Mixed Apex and Flow Execution

| Order | Type | Action | Description |
|-------|------|--------|-------------|
| 10 | Apex | TA_Lead_ValidateRequiredFields | Validate data first |
| 20 | Apex | TA_Lead_SetDefaults | Set default values |
| 25 | **Flow** | Lead_Enrich_From_External | Admin-built enrichment |
| 30 | Apex | TA_Lead_CalculateScore | Score after enrichment |
| 40 | **Flow** | Lead_Assign_To_Queue | Admin-built assignment |
| 50 | Apex | TA_Lead_NotifyOwner | Notify after assignment |

### Metadata Records

```
Trigger_Action.Lead_Before_Insert_10_ValidateRequired.md-meta.xml  (Apex)
Trigger_Action.Lead_Before_Insert_20_SetDefaults.md-meta.xml       (Apex)
Trigger_Action.Lead_Before_Insert_25_EnrichExternal.md-meta.xml    (Flow)
Trigger_Action.Lead_Before_Insert_30_CalculateScore.md-meta.xml    (Apex)
Trigger_Action.Lead_Before_Insert_40_AssignQueue.md-meta.xml       (Flow)
Trigger_Action.Lead_After_Insert_50_NotifyOwner.md-meta.xml        (Apex)
```

## Before Context Flows

### Modifying Records in Before Context

In before-context Flows, use `newListAfterFlow` to return modified records:

**Flow Structure**:
1. Loop through `newList`
2. Modify records using Assignment elements
3. Add modified records to `newListAfterFlow`

**Example Flow Logic**:
```
Loop: For each record in {!newList}
  └── Decision: Is Company blank?
        ├── Yes: Assignment: Set Company = "Unknown"
        └── No: (skip)
  └── Assignment: Add record to {!newListAfterFlow}
```

### Important: Before Context Rules

1. **No DML in Flow**: The framework handles the actual DML
2. **Return ALL records**: Even unmodified records must be in `newListAfterFlow`
3. **Field changes stick**: Changes made to records in before context are saved

## Bypassing Flows

### Code-Level Bypass

```apex
// Bypass a specific flow
TriggerActionFlow.bypass('Lead_Enrich_From_External');

insert leads;

TriggerActionFlow.clearBypass('Lead_Enrich_From_External');
```

### Bypass All Flows

```apex
// Bypass all flows (Apex actions still run)
TriggerActionFlow.bypassAll();

try {
    insert leads;
} finally {
    TriggerActionFlow.clearAllBypasses();
}
```

### Permission-Based Bypass

Add `Bypass_Permission__c` to the Flow's trigger action metadata:

```xml
<values>
    <field>Bypass_Permission__c</field>
    <value xsi:type="xsd:string">Bypass_Lead_EnrichmentFlow</value>
</values>
```

## Limitations

### Recursion Depth

**Critical**: Flows invoked via Trigger Actions have a maximum recursion depth of **3**, not 16 like Apex triggers.

```apex
// This can cause issues with Flow trigger actions
// If Flow A updates a record that triggers Flow B which updates again...
// You'll hit the recursion limit faster than with pure Apex
```

**Mitigation**: Set `Allow_Flow_Recursion__c` to `false` unless absolutely necessary.

### No Direct Trigger Context Access

Flows cannot access:
- `Trigger.isExecuting`
- `Trigger.operationType`
- `Trigger.size`

The framework passes `newList` and `oldList` instead.

### Governor Limits

Flows share governor limits with the transaction. Heavy Flows can exhaust limits before Apex runs.

### Error Handling

Flow errors surface as `Flow.FaultException`. Catch these in Apex if needed:

```apex
try {
    insert leads;
} catch (Flow.FaultException e) {
    // Handle Flow-specific errors
    System.debug('Flow error: ' + e.getMessage());
}
```

## Best Practices

### 1. Use Flows for Admin-Configurable Logic

**Good Flow Use Cases**:
- Field mappings that change frequently
- Assignment rules admins need to modify
- Notification logic with dynamic templates
- Simple field updates based on criteria

**Keep in Apex**:
- Complex validation logic
- Heavy computation
- External callouts
- Anything requiring transaction control

### 2. Document Flow Dependencies

Create a README or Wiki documenting which Flows exist and their purpose:

```markdown
## Lead Trigger Action Flows

| Flow API Name | Context | Order | Purpose | Owner |
|---------------|---------|-------|---------|-------|
| Lead_Enrich_From_External | Before Insert | 25 | Enriches lead data from external source | Admin Team |
| Lead_Assign_To_Queue | Before Insert | 40 | Routes leads to appropriate queue | Sales Ops |
| Lead_Send_Welcome_Email | After Insert | 60 | Sends welcome email series | Marketing |
```

### 3. Test Flows via Apex Tests

```apex
@IsTest
private class LeadTriggerFlows_Test {
    
    @IsTest
    static void testEnrichmentFlow_setsExpectedFields() {
        // Arrange
        Lead l = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company'
        );
        
        // Act - Flow runs as part of trigger
        Test.startTest();
        insert l;
        Test.stopTest();
        
        // Assert - Verify Flow made expected changes
        Lead inserted = [SELECT Id, Enrichment_Status__c FROM Lead WHERE Id = :l.Id];
        System.assertEquals('Complete', inserted.Enrichment_Status__c, 
            'Enrichment Flow should set status');
    }
    
    @IsTest
    static void testEnrichmentFlow_whenBypassed_doesNotRun() {
        // Arrange
        Lead l = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company'
        );
        
        // Bypass the Flow
        TriggerActionFlow.bypass('Lead_Enrich_From_External');
        
        // Act
        Test.startTest();
        insert l;
        Test.stopTest();
        
        // Assert
        Lead inserted = [SELECT Id, Enrichment_Status__c FROM Lead WHERE Id = :l.Id];
        System.assertEquals(null, inserted.Enrichment_Status__c, 
            'Bypassed Flow should not set status');
        
        // Cleanup
        TriggerActionFlow.clearBypass('Lead_Enrich_From_External');
    }
}
```

### 4. Use Subflows for Reusability

If multiple trigger action Flows share logic, extract to a Subflow:

```
Lead_Before_Insert_Enrichment (Trigger Action Flow)
  └── Calls: Common_Lead_Enrichment_Subflow

Lead_Before_Update_Enrichment (Trigger Action Flow)
  └── Calls: Common_Lead_Enrichment_Subflow
```

### 5. Monitor Flow Performance

Use Flow debug logs and the Trigger Actions Framework's built-in logging to identify slow Flows:

```apex
// Enable debug logging for troubleshooting
System.debug('Before Flow execution: ' + Limits.getQueries() + ' queries used');
// Flow runs here
System.debug('After Flow execution: ' + Limits.getQueries() + ' queries used');
```

### 6. Version Control Flow Metadata

Always include Flow metadata in version control:

```
force-app/main/default/flows/
├── Lead_Enrich_From_External.flow-meta.xml
├── Lead_Assign_To_Queue.flow-meta.xml
└── Lead_Send_Welcome_Email.flow-meta.xml
```

### 7. Naming Convention for Trigger Action Flows

Use consistent naming that indicates the Flow is a trigger action:

```
<ObjectName>_<Context>_<ActionDescription>

Examples:
- Lead_BeforeInsert_EnrichData
- Lead_AfterInsert_SendWelcome
- Opportunity_BeforeUpdate_ValidateStage
- Account_AfterUpdate_SyncToExternal
```

## Example: Complete Flow Integration

### Scenario

Lead enrichment Flow that:
1. Checks if Company exists in external system
2. Sets Industry based on external data
3. Marks record as enriched

### Flow Design

**Name**: `Lead_BeforeInsert_EnrichData`

**Variables**:
- `newList` (Input, Record Collection - Lead)
- `newListAfterFlow` (Output, Record Collection - Lead)
- `currentLead` (Record - Lead, for loop)

**Flow Structure**:
```
Start
  │
  ▼
Loop (newList → currentLead)
  │
  ├── Decision: Is Company not blank?
  │     │
  │     ├── Yes ──► Action: Call External_Enrichment_Subflow
  │     │              │
  │     │              ▼
  │     │           Assignment: Set currentLead.Industry
  │     │           Assignment: Set currentLead.Enriched__c = true
  │     │
  │     └── No ───► Assignment: Set currentLead.Enriched__c = false
  │
  ▼
Assignment: Add currentLead to newListAfterFlow
  │
  ▼
End Loop
  │
  ▼
End
```

### Metadata Registration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>Lead Before_Insert 25 EnrichData</label>
    <protected>false</protected>
    <values>
        <field>Apex_Class_Name__c</field>
        <value xsi:type="xsd:string">TriggerActionFlow</value>
    </values>
    <values>
        <field>Flow_Name__c</field>
        <value xsi:type="xsd:string">Lead_BeforeInsert_EnrichData</value>
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
        <value xsi:type="xsd:string">Bypass_Lead_Enrichment</value>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
</CustomMetadata>
```

### Full Execution Order

| Order | Type | Name | What It Does |
|-------|------|------|--------------|
| 10 | Apex | TA_Lead_ValidateRequiredFields | Validates Company, Email |
| 20 | Apex | TA_Lead_SetDefaults | Sets LeadSource, Status defaults |
| **25** | **Flow** | **Lead_BeforeInsert_EnrichData** | **Enriches from external system** |
| 30 | Apex | TA_Lead_CalculateScore | Calculates lead score |
| 40 | Apex | TA_Lead_AssignOwner | Assigns to appropriate rep |
