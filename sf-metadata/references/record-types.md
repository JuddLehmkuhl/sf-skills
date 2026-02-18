# Record Types & Business Processes -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## When to Use Record Types

| Scenario | Use Record Types? | Alternative |
|----------|------------------|-------------|
| Different page layouts per business unit | Yes | Dynamic Forms (field sections) |
| Different picklist values per process | Yes | Dependent picklists (limited) |
| Different sales/support/lead processes | Yes (required) | N/A -- Business Processes need Record Types |
| Controlling field visibility | Maybe | FLS + Permission Sets may suffice |
| Different validation rules per process | Yes (via `RecordType.DeveloperName` in formula) | Custom checkbox field for bypass |
| Different Lightning Record Pages | Optional | App-based or profile-based page assignment |

## Business Process Mapping

| Object | Business Process Type | Controls |
|--------|----------------------|----------|
| Opportunity | Sales Process | `StageName` values |
| Case | Support Process | `Status` values |
| Lead | Lead Process | `Status` values |
| Solution | Solution Process | `Status` values |

**Sales Process Metadata**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<BusinessProcess xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Enterprise_Sales</fullName>
    <description>Sales process for enterprise deals</description>
    <isActive>true</isActive>
    <values>
        <fullName>Prospecting</fullName>
        <default>true</default>
    </values>
    <values>
        <fullName>Discovery</fullName>
        <default>false</default>
    </values>
    <values>
        <fullName>Proposal</fullName>
        <default>false</default>
    </values>
    <values>
        <fullName>Negotiation</fullName>
        <default>false</default>
    </values>
    <values>
        <fullName>Closed Won</fullName>
        <default>false</default>
    </values>
    <values>
        <fullName>Closed Lost</fullName>
        <default>false</default>
    </values>
</BusinessProcess>
```

## Record Type Metadata (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Enterprise</fullName>
    <active>true</active>
    <businessProcess>Enterprise_Sales</businessProcess>
    <compactLayoutAssignment>Enterprise_Compact</compactLayoutAssignment>
    <description>Record type for enterprise-level opportunities</description>
    <label>Enterprise</label>
    <picklistValues>
        <picklist>Industry</picklist>
        <values>
            <fullName>Technology</fullName>
            <default>false</default>
        </values>
        <values>
            <fullName>Finance</fullName>
            <default>false</default>
        </values>
    </picklistValues>
</RecordType>
```

**File path**: `force-app/main/default/objects/Opportunity/recordTypes/Enterprise.recordType-meta.xml`

## Record Type in Apex

```java
// Query Record Type by DeveloperName (recommended)
Id rtId = Schema.SObjectType.Opportunity.getRecordTypeInfosByDeveloperName()
    .get('Enterprise').getRecordTypeId();

// Use in SOQL
List<Opportunity> opps = [
    SELECT Id, Name, StageName
    FROM Opportunity
    WHERE RecordType.DeveloperName = 'Enterprise'
];

// Set Record Type on new record
Opportunity opp = new Opportunity(
    RecordTypeId = rtId,
    Name = 'Big Deal',
    StageName = 'Prospecting',
    CloseDate = Date.today().addDays(90)
);
```

## Record Type in Flow

- Use `$Record.RecordType.DeveloperName` in decision elements
- Use `$Record.RecordTypeId` for direct ID comparison
- When creating records, set `RecordTypeId` using a formula resource or Get Records on RecordType

## Page Layout Assignment per Record Type + Profile

```xml
<!-- In the object-meta.xml or via profileLayoutAssignments -->
<profileLayoutAssignments>
    <layout>Opportunity-Enterprise Layout</layout>
    <profile>Sales User</profile>
    <recordType>Enterprise</recordType>
</profileLayoutAssignments>
```
