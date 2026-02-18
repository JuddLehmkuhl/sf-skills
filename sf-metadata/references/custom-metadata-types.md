# Custom Metadata Types (CMT) -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## When to Use: Decision Matrix

| Criteria | Custom Metadata Types | Custom Settings (Hierarchy) | Custom Settings (List) | Custom Labels |
|----------|----------------------|----------------------------|----------------------|---------------|
| **Deployable** | Yes (metadata) | No (data) | No (data) | Yes (metadata) |
| **Packageable** | Yes (protected/public) | No | No | Yes |
| **SOQL Queryable** | Yes (`__mdt`) | Yes (`__c`) | Yes (`__c`) | No |
| **Accessible in Formulas** | Yes (`$CustomMetadata`) | Yes (`$Setup`) | No | Yes (`$Label`) |
| **Accessible in Flow** | Yes (Get Records) | Yes (Get Records) | Yes (Get Records) | Yes (formula) |
| **Accessible in Apex** | Yes (`getInstance()`) | Yes (`getInstance()`) | Yes (`getAll()`) | Yes (`System.Label`) |
| **Record limit** | 10 MB total storage | 10 MB (hierarchy) / 10 MB (list) | Same | 5,000 labels |
| **Per-user values** | No | Yes (hierarchy) | No | No (use Translation) |
| **Governor limit free** | Yes (cached, no SOQL) | Yes (cached) | Yes (cached) | Yes |
| **Editable in production** | No (deploy only) | Yes (via Setup) | Yes (via Setup) | No (deploy only) |

**Decision guide**:
- Need per-user/profile configuration? --> **Hierarchy Custom Settings**
- Need admin-editable config in production without deployments? --> **Custom Settings**
- Need deployable, versionable configuration? --> **Custom Metadata Types**
- Need simple translatable text? --> **Custom Labels**
- Need feature flags with deployment control? --> **Custom Metadata Types**
- Need routing rules, mapping tables? --> **Custom Metadata Types**

## CMT File Structure

```
force-app/main/default/
-- customMetadata/
   -- Feature_Flag.Enable_Dark_Mode.md-meta.xml
   -- Feature_Flag.Enable_New_UI.md-meta.xml
-- objects/
   -- Feature_Flag__mdt/
      -- Feature_Flag__mdt.object-meta.xml
      -- fields/
         -- Is_Enabled__c.field-meta.xml
         -- Description__c.field-meta.xml
```

## CMT Object Definition (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Feature flags for controlling application behavior</description>
    <label>Feature Flag</label>
    <pluralLabel>Feature Flags</pluralLabel>
    <visibility>Public</visibility>
</CustomObject>
```

## CMT Field Definition (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Is_Enabled__c</fullName>
    <defaultValue>false</defaultValue>
    <description>Whether this feature flag is active</description>
    <externalId>false</externalId>
    <fieldManageability>DeveloperControlled</fieldManageability>
    <label>Is Enabled</label>
    <type>Checkbox</type>
</CustomField>
```

**Field Manageability Options**:

| Value | Meaning | Use When |
|-------|---------|----------|
| `DeveloperControlled` | Only deployable, not editable in subscriber org | Configuration that should not change post-install |
| `SubscriberControlled` | Editable in subscriber org via Setup | Configuration that admins should be able to change |
| `Locked` | Cannot be changed after packaging | Critical configuration that must not be modified |

## CMT Record Definition (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <label>Enable Dark Mode</label>
    <protected>false</protected>
    <values>
        <field>Is_Enabled__c</field>
        <value xsi:type="xsd:boolean">true</value>
    </values>
    <values>
        <field>Description__c</field>
        <value xsi:type="xsd:string">Controls dark mode across Lightning pages</value>
    </values>
</CustomMetadata>
```

## CMT Access Patterns

**In Apex** (governor-limit free):
```java
// Get a single record by DeveloperName
Feature_Flag__mdt flag = Feature_Flag__mdt.getInstance('Enable_Dark_Mode');
Boolean isEnabled = flag.Is_Enabled__c;

// Get all records
Map<String, Feature_Flag__mdt> allFlags = Feature_Flag__mdt.getAll();

// SOQL query (counts against governor limits -- prefer getInstance/getAll)
List<Feature_Flag__mdt> flags = [
    SELECT DeveloperName, Is_Enabled__c
    FROM Feature_Flag__mdt
    WHERE Is_Enabled__c = true
];
```

**In Flow**:
- Use **Get Records** element on the `Feature_Flag__mdt` object
- Filter by `DeveloperName` for specific records
- No SOQL limit impact (treated as metadata query)

**In Formulas & Validation Rules**:
```
$CustomMetadata.Feature_Flag__mdt.Enable_Dark_Mode.Is_Enabled__c
```

**In Process Builder / Workflow** (legacy):
```
{!$CustomMetadata.Feature_Flag__mdt.Enable_Dark_Mode.Is_Enabled__c}
```

## CMT Common Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Feature Flags** | Toggle features on/off per environment | `Feature_Flag__mdt` with `Is_Enabled__c` checkbox |
| **Mapping Tables** | Map external values to Salesforce values | `Field_Mapping__mdt` with `Source_Field__c`, `Target_Field__c` |
| **Routing Rules** | Route records based on criteria | `Case_Routing__mdt` with `Priority__c`, `Queue_Name__c` |
| **Integration Config** | Store endpoint paths, retry counts | `Integration_Setting__mdt` with `Endpoint__c`, `Retry_Count__c` |
| **Trigger Actions** | Configure TAF trigger actions | `Trigger_Action__mdt` with `Apex_Class_Name__c`, `Order__c` |
| **Approval Thresholds** | Configure approval limits | `Approval_Threshold__mdt` with `Amount__c`, `Approver_Role__c` |

## CMT in Managed Packages

| Visibility | Subscriber Can See? | Subscriber Can Edit? | Use Case |
|-----------|--------------------|--------------------|----------|
| `protected: true` | No | No | Internal package configuration |
| `protected: false` | Yes | Depends on manageability | Customer-facing configuration |

## CMT Deploy via Metadata API (Apex)

```java
// Programmatically create/update CMT records
Metadata.CustomMetadata cmRecord = new Metadata.CustomMetadata();
cmRecord.setFullName('Feature_Flag.Enable_Dark_Mode');
cmRecord.setLabel('Enable Dark Mode');

Metadata.CustomMetadataValue flagValue = new Metadata.CustomMetadataValue();
flagValue.setField('Is_Enabled__c');
flagValue.setValue(true);
cmRecord.addValue(flagValue);

Metadata.DeployContainer container = new Metadata.DeployContainer();
container.addMetadata(cmRecord);

// Deploy asynchronously -- callback receives result
Metadata.Operations.enqueueDeployment(container, new MyDeployCallback());
```
