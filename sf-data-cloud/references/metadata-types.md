# Data Cloud Metadata Types Reference

Complete reference for all Data Cloud metadata types supported by Salesforce Metadata API, including directory names, file suffixes, and packaging compatibility.

---

## All Metadata Types

| Metadata Type (API Name) | Directory Name | File Suffix | Packaging Support |
|---|---|---|---|
| DataStreamDefinition | dataStreamDefinitions | .dataStreamDefinition | U / 2GP / 1GP |
| DataStreamTemplate | dataStreamTemplates | .dataStreamTemplate | U / 2GP |
| DataSource | mktDataSources | .dataSource | U / 2GP |
| DataSourceBundleDefinition | dataSourceBundleDefinitions | .dataSourceBundleDefinition | U / 2GP |
| DataSourceObject | dataSourceObjects | .dataSourceObject | U / 2GP |
| DataSourceTenant | dataSourceTenants | .dataSourceTenant | U |
| DataPackageKitDefinition | dataPackageKitDefinitions | .dataPackageKitDefinition | U / 2GP / 1GP |
| DataPackageKitObject | DataPackageKitObjects | .DataPackageKitObject | U / 2GP |
| DataKitObjectTemplate | dataKitObjectTemplates | .dataKitObjectTemplate | U |
| DataKitObjectDependency | dataKitObjectDependencies | .dataKitObjectDependency | U |
| DataConnector | dataconnectors | .dataconnector | U |
| DataConnectorIngestApi | dataConnectorIngestApis | .dataConnectorIngestApi | U / 2GP |
| DataConnectorS3 | s3DataConnectors | .s3DataConnector | U / 2GP |
| InternalDataConnector | internalDataConnectors | .externalDataConnector | U |
| ExternalDataConnector | externalDataConnectors | .externalDataConnector | U / 2GP |
| ExternalDataSource | externalDataSources | .externalDataSource | U / 2GP / 1GP |
| StreamingAppDataConnector | streamingAppDataConnectors | .streamingAppDataConnector | U / 2GP |
| MktCalcInsightObjectDef | mktCalcInsightObjectDefs | .mktCalcInsightObjectDef | U / 1GP |
| MarketSegmentDefinition | marketSegmentDefinitions | .marketSegmentDefinition | U / 1GP |
| ActivationPlatform | activationPlatforms | .activationPlatform | U / 1GP |
| ActivationPlatformActvAttr | activationPlatformActvAttrs | .activationPlatformActvAttr | U |
| ActivationPlatformField | activationPlatformFields | .activationPlatformField | U |
| ActvPfrmDataConnectorS3 | actvPfrmDataConnectorS3s | .actvPfrmDataConnectorS3 | U |
| ActvPlatformAdncIdentifier | actvPlatformAdncIdentifiers | .actvPlatformAdncIdentifier | U |
| ActvPlatformFieldValue | actvPlatformFieldValues | .actvPlatformFieldValue | U |
| DataSourceField | dataSourceFields | .dataSourceField | U / 2GP |
| ExternalDataTransportFieldTemplate | externalDataTransportFieldTemplates | .externalDataTransportFieldTemplate | U |
| ExternalDataTransportObjectTemplate | externalDataTransportObjectTemplates | .externalDataTransportObjectTemplate | U |
| MktDataTranField | mktDataTranFields | .mktDataTranField | U |
| MktDataTranObject | mktDataTranObjects | .mktDataTranObject | U / 2GP |
| MktDataConnection | mktDataConnections | .mktDataConnection | U |
| MktDataConnectionSrcParam | mktDataConnectionSrcParams | .mktDataConnectionSrcParam | U |
| FieldSrcTrgtRelationship | fieldSrcTrgtRelationships | .fieldSrcTrgtRelationship | U / 2GP / 1GP |
| ObjectSourceTargetMap | objectSourceTargetMaps | .objectSourceTargetMap | U / 2GP |
| DataSrcDataModelFieldMap | dataSrcDataModelFieldMaps | .dataSrcDataModelFieldMap | U / 2GP |
| FieldMappingConfig | fieldMappingConfigs | .fieldMappingConfig | U |
| DataCalcInsightTemplate | dataCalcInsightTemplates | .dataCalcInsightTemplate | U |
| ExternalDataTranObject | externalDataTranObjects | .externalDataTranObject | U |
| DataObjectBuildOrgTemplate | dataObjectBuildOrgTemplates | .dataObjectBuildOrgTemplate | U |
| CustomerDataPlatformSettings | (settings type) | .settings | U |

**Packaging Key:** U = Unlocked Packages, 2GP = Second-Generation Managed Packages, 1GP = First-Generation Managed Packages

---

## Data Kit-Only Components

The following Data Cloud components can only be deployed as part of a Data Kit (DataPackageKitDefinition + DataPackageKitObject). They cannot be deployed standalone via Metadata API:

- **Data Lake Objects (DLOs)** -- Custom `__dlm` objects and their fields
- **Calculated Insights** -- SQL-based calculated insight definitions
- **Search Indexes** -- DataObjectSearchIndexConf records
- **Data Graphs** -- Graph definitions linking DMOs

To deploy these, wrap them in a DataPackageKitDefinition and reference them via DataPackageKitObject entries.

---

## Packaging Rules and Constraints

### Separation Rule (Winter '25+)
Data Cloud metadata and non-Data Cloud metadata **cannot coexist** in a single package. You must use separate packages for DC vs. non-DC components.

### Source Tracking Limitations
- `DataObjectSearchIndexConf` supports deploy and retrieve but does **not** support source tracking. Changes must be deployed manually.

### Permission Set Restriction
- The `sfdc_a360_sfcrm_data_extrac` permission set **cannot** be deployed via Metadata API. It must be assigned manually in the target org.

### Retrieve Considerations
- Some metadata types (DataSourceTenant, DataKitObjectTemplate, DataKitObjectDependency) are Unlocked-only and cannot be included in managed packages.
- InternalDataConnector and ExternalDataConnector share the same `.externalDataConnector` file suffix but use different directory names.

---

## Directory Structure Example

```
force-app/main/default/
  dataStreamDefinitions/
    MyStream.dataStreamDefinition-meta.xml
  dataSourceBundleDefinitions/
    MyBundle.dataSourceBundleDefinition-meta.xml
  dataSourceObjects/
    MySourceObj.dataSourceObject-meta.xml
  dataPackageKitDefinitions/
    MyDataKit.dataPackageKitDefinition-meta.xml
  DataPackageKitObjects/
    MyDataKit_MyObject.DataPackageKitObject-meta.xml
  mktDataSources/
    Salesforce_Home.dataSource-meta.xml
  dataconnectors/
    MyConnector.dataconnector-meta.xml
  dataConnectorIngestApis/
    MyIngestApi.dataConnectorIngestApi-meta.xml
  s3DataConnectors/
    MyS3Connector.s3DataConnector-meta.xml
  objects/
    My_Object__dlm/
      My_Object__dlm.object-meta.xml
      fields/
        MyField__c.field-meta.xml
  mktCalcInsightObjectDefs/
    MyInsight.mktCalcInsightObjectDef-meta.xml
  marketSegmentDefinitions/
    MySegment.marketSegmentDefinition-meta.xml
  settings/
    CustomerDataPlatform.settings-meta.xml
```

---

## package.xml Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>DataPackageKitDefinition</name>
    </types>
    <types>
        <members>*</members>
        <name>DataPackageKitObject</name>
    </types>
    <types>
        <members>*</members>
        <name>DataStreamDefinition</name>
    </types>
    <types>
        <members>*</members>
        <name>DataSource</name>
    </types>
    <types>
        <members>*</members>
        <name>DataConnectorIngestApi</name>
    </types>
    <types>
        <members>My_Object__dlm</members>
        <name>CustomObject</name>
    </types>
    <version>62.0</version>
</Package>
```
