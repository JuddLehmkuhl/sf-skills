# Global Value Sets & Picklists -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## Global vs Object-Specific Value Sets

| Feature | Global Value Set | Object-Specific Picklist |
|---------|-----------------|-------------------------|
| **Reusable** | Yes -- shared across objects | No -- tied to one field |
| **Centralized management** | Yes -- single source of truth | No -- each field managed separately |
| **Deployable** | Separate metadata type | Part of field metadata |
| **Value set changes** | Propagate to all fields automatically | Must update each field |
| **Use when** | Same values on 2+ objects | Values unique to one object |

## Global Value Set Metadata (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GlobalValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Industry_Segments</fullName>
    <description>Standard industry segments used across objects</description>
    <masterLabel>Industry Segments</masterLabel>
    <sorted>false</sorted>
    <customValue>
        <fullName>Technology</fullName>
        <default>false</default>
        <label>Technology</label>
    </customValue>
    <customValue>
        <fullName>Healthcare</fullName>
        <default>false</default>
        <label>Healthcare</label>
    </customValue>
    <customValue>
        <fullName>Finance</fullName>
        <default>false</default>
        <label>Finance</label>
    </customValue>
</GlobalValueSet>
```

**File path**: `force-app/main/default/globalValueSets/Industry_Segments.globalValueSet-meta.xml`

## Picklist Field Referencing a Global Value Set

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Industry_Segment__c</fullName>
    <label>Industry Segment</label>
    <type>Picklist</type>
    <valueSet>
        <restricted>true</restricted>
        <valueSetName>Industry_Segments</valueSetName>
    </valueSet>
</CustomField>
```

## Restricted vs Unrestricted Picklists

| Type | Behavior | Use When |
|------|----------|----------|
| **Restricted** (`restricted: true`) | API rejects values not in the value set | Data integrity is critical -- most common choice |
| **Unrestricted** (`restricted: false`) | API accepts any value, even if not in the list | Legacy integrations that may send old values |

## Controlling & Dependent Picklists

```xml
<!-- Controlling field: Type__c (standard picklist) -->
<!-- Dependent field: SubType__c -->
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>SubType__c</fullName>
    <label>Sub Type</label>
    <type>Picklist</type>
    <valueSet>
        <controllingField>Type__c</controllingField>
        <restricted>true</restricted>
        <valueSetDefinition>
            <sorted>false</sorted>
            <value>
                <fullName>Sub_A</fullName>
                <default>false</default>
                <label>Sub A</label>
            </value>
            <value>
                <fullName>Sub_B</fullName>
                <default>false</default>
                <label>Sub B</label>
            </value>
        </valueSetDefinition>
        <valueSettings>
            <controllingFieldValue>Type_1</controllingFieldValue>
            <valueName>Sub_A</valueName>
        </valueSettings>
        <valueSettings>
            <controllingFieldValue>Type_2</controllingFieldValue>
            <valueName>Sub_B</valueName>
        </valueSettings>
    </valueSet>
</CustomField>
```

## Picklist Migration Patterns

| Migration | Steps |
|-----------|-------|
| Object picklist -> Global Value Set | 1. Create GVS with same values. 2. Update field to reference GVS. 3. Deploy both. Values and data are preserved |
| Add values to existing picklist | 1. Add `<customValue>` elements. 2. Deploy. Existing data is unaffected |
| Deactivate values | Set `<isActive>false</isActive>` on values. Existing records retain old values but users cannot select them |
| Rename values | Change `<label>` but keep `<fullName>` the same. API name stays consistent, display changes |
