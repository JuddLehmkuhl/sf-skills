# Data Cloud XML Metadata Templates

Ready-to-use XML metadata templates for Data Cloud components. Copy and modify these templates when creating Data Cloud metadata for deployment.

---

## DLM Object Definition (__dlm)

Defines a custom Data Model Object (DMO) in Data Cloud.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My_Custom_Object_Home</label>
    <mktDataModelAttributes>
        <creationType>Custom</creationType>
        <dataModelTaxonomy>Salesforce_SFDCReferenceModel_0_93</dataModelTaxonomy>
        <dataSpaceName>default</dataSpaceName>
        <isEnabled>true</isEnabled>
        <isSegmentable>false</isSegmentable>
        <isUsedForMetrics>false</isUsedForMetrics>
        <labelOverride>My Custom Object Home</labelOverride>
        <masterLabel>My Custom Object Home</masterLabel>
        <objectCategory>Salesforce_SFDCReferenceModel_0_93.Related</objectCategory>
    </mktDataModelAttributes>
</CustomObject>
```

### Key Attributes

| Attribute | Description |
|---|---|
| `creationType` | `Custom` for custom DMOs, `System` for standard |
| `dataModelTaxonomy` | Reference model version (e.g., `Salesforce_SFDCReferenceModel_0_93`) |
| `dataSpaceName` | Data space assignment (default: `default`) |
| `isEnabled` | Whether the object is active |
| `isSegmentable` | Whether the object can be used in segment definitions |
| `isUsedForMetrics` | Whether the object is available for calculated insights |
| `objectCategory` | Subject area classification (e.g., `.Related`, `.Individual`, `.Engagement`) |

---

## DLM Field Definitions

### Text Field with Primary Key

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Id__c</fullName>
    <label>Record ID</label>
    <length>60</length>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <labelOverride>Record ID</labelOverride>
        <masterLabel>Record ID</masterLabel>
        <primaryIndexOrder>1</primaryIndexOrder>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <required>false</required>
    <type>Text</type>
</CustomField>
```

The `primaryIndexOrder` attribute designates this field as the primary key. Use `1` for single-field primary keys. For compound keys, use `1`, `2`, etc.

### DateTime Field

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Event_Start__c</fullName>
    <label>Event Start</label>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <required>false</required>
    <type>DateTime</type>
</CustomField>
```

### Number Field

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Amount__c</fullName>
    <label>Amount</label>
    <precision>18</precision>
    <scale>2</scale>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <required>false</required>
    <type>Number</type>
</CustomField>
```

### Boolean Field

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Is_Active__c</fullName>
    <label>Is Active</label>
    <defaultValue>false</defaultValue>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <type>Checkbox</type>
</CustomField>
```

### Foreign Key (Lookup) Field

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Individual_Id__c</fullName>
    <label>Individual ID</label>
    <length>60</length>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <isEventTime>false</isEventTime>
        <referenceFieldName>ssot__Id__c</referenceFieldName>
        <referenceObjectName>ssot__Individual__dlm</referenceObjectName>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <required>false</required>
    <type>Text</type>
</CustomField>
```

The `referenceObjectName` and `referenceFieldName` attributes establish the foreign key relationship to another DMO.

---

## DataStreamDefinition

Defines a data stream that links a connector to a source object and specifies how data flows into Data Cloud.

### CRM Connector Stream (Retrieved from psa-ai-agent org)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataStreamDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <areHeadersIncludedInFile>false</areHeadersIncludedInFile>
    <bulkIngest>false</bulkIngest>
    <creationType>Custom</creationType>
    <dataConnector>SalesforceDotCom_Home</dataConnector>
    <dataConnectorType>SalesforceDotCom</dataConnectorType>
    <dataExtractMethods>FULL_REFRESH</dataExtractMethods>
    <dataPlatformDataSetItemName>SFDC</dataPlatformDataSetItemName>
    <dataSource>Salesforce_Home</dataSource>
    <isLimitedToNewFiles>false</isLimitedToNewFiles>
    <isMissingFileFailure>false</isMissingFileFailure>
    <masterLabel>Account_Home</masterLabel>
    <mktDataLakeObject>Account_Home__dll</mktDataLakeObject>
    <mktDataTranObject>Account_Home</mktDataTranObject>
</DataStreamDefinition>
```

### Ingestion API Stream

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataStreamDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <areHeadersIncludedInFile>false</areHeadersIncludedInFile>
    <bulkIngest>false</bulkIngest>
    <creationType>Custom</creationType>
    <dataConnector>MyIngestConnector</dataConnector>
    <dataConnectorType>IngestApi</dataConnectorType>
    <dataExtractMethods>FULL_REFRESH</dataExtractMethods>
    <dataSource>MyIngestSource</dataSource>
    <isLimitedToNewFiles>false</isLimitedToNewFiles>
    <isMissingFileFailure>false</isMissingFileFailure>
    <masterLabel>Customer_Events</masterLabel>
    <mktDataLakeObject>Customer_Events__dll</mktDataLakeObject>
    <mktDataTranObject>Customer_Events</mktDataTranObject>
</DataStreamDefinition>
```

### S3 Connector Stream

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataStreamDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <areHeadersIncludedInFile>true</areHeadersIncludedInFile>
    <bulkIngest>false</bulkIngest>
    <creationType>Custom</creationType>
    <dataConnector>MyS3Connector</dataConnector>
    <dataConnectorType>AwsS3</dataConnectorType>
    <dataExtractMethods>FULL_REFRESH</dataExtractMethods>
    <dataSource>MyS3Source</dataSource>
    <fileNameWildcard>*.csv</fileNameWildcard>
    <isLimitedToNewFiles>false</isLimitedToNewFiles>
    <isMissingFileFailure>false</isMissingFileFailure>
    <masterLabel>S3_Customer_Data</masterLabel>
    <mktDataLakeObject>S3_Customer_Data__dll</mktDataLakeObject>
    <mktDataTranObject>S3_Customer_Data</mktDataTranObject>
</DataStreamDefinition>
```

### DataStreamDefinition Field Reference

| Field | Type | Description |
|---|---|---|
| `areHeadersIncludedInFile` | boolean | If true, headers are included in the file for single-file streams |
| `bulkIngest` | boolean | If true, files are aggregated before ingestion (wildcard file names) |
| `creationType` | string | `Custom` or `Standard` |
| `dataConnector` | string | Required. Name of the connector this stream uses |
| `dataConnectorType` | enum | Required. Connector type (see enum table below) |
| `dataExtractMethods` | enum | `FULL_REFRESH`, `DATETIME_CDC`, `NUMERIC_CDC`, `BINARY_CDC` |
| `dataExtractField` | string | Transport field name used when extract method is CDC |
| `dataPlatformDataSetItemName` | string | Data Platform Set Item name (e.g., `SFDC` for CRM streams) |
| `dataSource` | string | Required. Reference to the data source |
| `fileNameWildcard` | string | File or wildcard pattern for file-based streams (e.g., `*.csv`) |
| `isLimitedToNewFiles` | boolean | If true, only new files are retrieved |
| `isMissingFileFailure` | boolean | If true, missing files cause failure |
| `masterLabel` | string | Required. UI label for this stream |
| `mktDataLakeObject` | string | Required. Target DLO where data lands (ends with `__dll`) |
| `mktDataTranObject` | string | Transport object name |

### dataConnectorType Enum Values

| Value | Connector |
|---|---|
| `SalesforceDotCom` | Salesforce CRM |
| `IngestApi` | Ingestion API |
| `AwsS3` | Amazon S3 |
| `AzureBlob` | Azure Blob Storage |
| `GoogleCloudStorage` | Google Cloud Storage |
| `Snowflake` | Snowflake |
| `BIG_QUERY` | Google BigQuery |
| `REDSHIFT` | Amazon Redshift |
| `DataCloud` | Data Cloud (cross-org) |
| `SalesforceMarketingCloud` | Marketing Cloud |
| `SalesforceCommerceCloud` | B2C Commerce Cloud |
| `SalesforceInteractionStudio` | Interaction Studio / Personalization |
| `ACCOUNTENGAGEMENT` | Account Engagement (Pardot) |
| `StreamingApp` | Streaming App |
| `ExternalPlatform` | External Platform |
| `CuratedEntity` | Curated Entity (internal) |
| `SFTP` | SFTP |
| `UPLOAD` | File Upload |

---

## Data Connectors

### DataConnectorIngestApi

Defines an Ingestion API connector. Available API version 54.0+. Does NOT support wildcard (`*`) in package.xml.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataConnectorIngestApi xmlns="http://soap.sforce.com/2006/04/metadata">
    <sourceName>MyConnector</sourceName>
    <masterLabel>MyConnector</masterLabel>
</DataConnectorIngestApi>
```

### DataConnectorS3

Defines an Amazon S3 connector. Available API version 50.0+.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataConnectorS3 xmlns="http://soap.sforce.com/2006/04/metadata">
    <fileNameWildcard>*.csv</fileNameWildcard>
    <importFromDirectory>data/customer-events/</importFromDirectory>
    <masterLabel>Customer Events S3</masterLabel>
    <s3BucketName>my-data-cloud-bucket</s3BucketName>
</DataConnectorS3>
```

| Field | Description |
|---|---|
| `fileNameWildcard` | Optional. File pattern (e.g., `*.csv`, `profiles*.csv`) |
| `importFromDirectory` | Required. S3 directory path to import from |
| `masterLabel` | Required. UI label |
| `s3BucketName` | Optional. S3 bucket name |

### DataSource

Defines a data source that groups related data streams.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataSource xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Salesforce_Home</masterLabel>
    <prefix>Sal</prefix>
</DataSource>
```

| Field | Description |
|---|---|
| `masterLabel` | Required. UI label and API name for the data source |
| `prefix` | Required. Short prefix used in naming derived objects |

---

## Data Kit Components

### DataPackageKitDefinition

Defines a Data Kit container for deploying DLOs, calculated insights, and other Data Kit-only components.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataPackageKitDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>DevOps Data Kit for customer data</description>
    <masterLabel>Customer Data Kit</masterLabel>
    <type>DevOps</type>
    <versionNumber>1</versionNumber>
</DataPackageKitDefinition>
```

| Attribute | Description |
|---|---|
| `type` | `DevOps` for deployment kits, `Standard` for bundled data kits |
| `versionNumber` | Increment when updating the kit contents |

### DataPackageKitObject (Referencing a DMO)

Links a DMO to a Data Kit for deployment.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DataPackageKitObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>CustomerDataKit</masterLabel>
    <parentDataPackageKitDefinitionName>CustomerDataKit</parentDataPackageKitDefinitionName>
    <referenceObjectName>My_Object_Home__dlm</referenceObjectName>
    <referenceObjectType>MktDataModelObject</referenceObjectType>
</DataPackageKitObject>
```

### DataPackageKitObject (Referencing a DataSourceBundleDefinition)

Links a data source bundle to a Data Kit.

```xml
<DataPackageKitObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>CustomerDataKit</masterLabel>
    <parentDataPackageKitDefinitionName>CustomerDataKit</parentDataPackageKitDefinitionName>
    <referenceObjectName>MySourceBundle</referenceObjectName>
    <referenceObjectType>DataSourceBundleDefinition</referenceObjectType>
</DataPackageKitObject>
```

### DataPackageKitObject (Referencing a Calculated Insight)

```xml
<DataPackageKitObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>CustomerDataKit</masterLabel>
    <parentDataPackageKitDefinitionName>CustomerDataKit</parentDataPackageKitDefinitionName>
    <referenceObjectName>Email_Engagement_Score</referenceObjectName>
    <referenceObjectType>CalculatedInsight</referenceObjectType>
</DataPackageKitObject>
```

### Reference Object Types

| referenceObjectType | What It References |
|---|---|
| `MktDataModelObject` | Data Model Object (DMO / __dlm) |
| `DataSourceBundleDefinition` | Data source bundle |
| `CalculatedInsight` | Calculated insight definition |
| `SearchIndex` | Data object search index |
| `DataGraph` | Data graph definition |

---

## DataKitObjectTemplate

Template for connector configuration within a Data Kit.

```xml
<DataKitObjectTemplate xmlns="http://soap.sforce.com/2006/04/metadata"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <developerName xsi:nil="true"/>
    <entityPayload>{...JSON with connector config...}</entityPayload>
    <masterLabel>Salesforce Connector Home</masterLabel>
    <parentDataPackageKitDefinitionName xsi:nil="true"/>
    <sourceObject>0hMDa000000GmdXMAS</sourceObject>
    <sourceObjectType>InternalDataConnector</sourceObjectType>
    <templateVersion>1</templateVersion>
</DataKitObjectTemplate>
```

| Attribute | Description |
|---|---|
| `entityPayload` | JSON string containing connector-specific configuration |
| `sourceObject` | Record ID of the source connector |
| `sourceObjectType` | Type of connector (e.g., `InternalDataConnector`, `ExternalDataConnector`) |
| `templateVersion` | Version number for the template |

---

## Ingestion API Schema (OpenAPI YAML)

Schema definition for the Ingestion API connector. This YAML file defines the objects and fields that the connector accepts.

```yaml
openapi: 3.0.0
info:
  title: Customer Events
  version: 1.0.0
components:
  schemas:
    CustomerEvent:
      type: object
      properties:
        eventId:
          type: string
        customerId:
          type: string
        eventType:
          type: string
        eventTime:
          type: string
          format: date-time
        amount:
          type: number
      required:
        - eventId
        - customerId
```

### Schema Rules

- Only top-level properties are supported (no nested objects)
- `required` array defines fields that must be present in every record
- Supported types: `string`, `number`, `integer`, `boolean`
- Supported formats for string: `date-time`, `date`
- The first field listed in `required` is typically used as the primary key

### Multi-Object Schema

```yaml
openapi: 3.0.0
info:
  title: Customer Data
  version: 1.0.0
components:
  schemas:
    Customer:
      type: object
      properties:
        customerId:
          type: string
        firstName:
          type: string
        lastName:
          type: string
        email:
          type: string
        createdDate:
          type: string
          format: date-time
      required:
        - customerId
    CustomerEvent:
      type: object
      properties:
        eventId:
          type: string
        customerId:
          type: string
        eventType:
          type: string
        eventTime:
          type: string
          format: date-time
      required:
        - eventId
        - customerId
```

---

## Calculated Insight SQL Example

Example SQL for a calculated insight that counts email opens per unified individual.

```sql
SELECT
    COUNT(EmailEngagement__dlm.Id__c) AS email_open_count__c,
    UnifiedIndividual__dlm.Id__c AS customer_id__c
FROM EmailEngagement__dlm
JOIN IndividualIdentityLink__dlm
    ON IndividualIdentityLink__dlm.SourceRecordId__c = EmailEngagement__dlm.IndividualId__c
    AND EmailEngagement__dlm.EngagementChannelActionId__c = 'Open'
JOIN UnifiedIndividual__dlm
    ON UnifiedIndividual__dlm.Id__c = IndividualIdentityLink__dlm.UnifiedRecordId__c
GROUP BY customer_id__c
```

### Calculated Insight with Window Function

```sql
SELECT
    ssot__Individual__dlm.ssot__Id__c AS individual_id__c,
    SalesOrder__dlm.OrderTotal__c AS order_total__c,
    ROW_NUMBER() OVER (
        PARTITION BY ssot__Individual__dlm.ssot__Id__c
        ORDER BY SalesOrder__dlm.OrderDate__c DESC
    ) AS order_rank__c
FROM SalesOrder__dlm
JOIN ssot__Individual__dlm
    ON ssot__Individual__dlm.ssot__Id__c = SalesOrder__dlm.IndividualId__c
```

### Streaming Calculated Insight

```sql
SELECT
    WINDOW.START AS window_start__c,
    WINDOW.END AS window_end__c,
    COUNT(*) AS event_count__c,
    customerId AS customer_id__c
FROM CustomerEvent__dlm
GROUP BY
    WINDOW(eventTime, '1 HOUR'),
    customer_id__c
```

---

## File Naming Conventions

| Component | File Name Pattern | Example |
|---|---|---|
| DMO Object | `{ObjectName}__dlm.object-meta.xml` | `Customer_Event__dlm.object-meta.xml` |
| DMO Field | `{FieldName}__c.field-meta.xml` | `Event_Start__c.field-meta.xml` |
| Data Kit Definition | `{KitName}.dataPackageKitDefinition-meta.xml` | `CustomerDataKit.dataPackageKitDefinition-meta.xml` |
| Data Kit Object | `{KitName}_{ObjectRef}.DataPackageKitObject-meta.xml` | `CustomerDataKit_MyObject.DataPackageKitObject-meta.xml` |
| Data Stream | `{StreamName}.dataStreamDefinition-meta.xml` | `CRM_Contacts.dataStreamDefinition-meta.xml` |
| Ingest Connector | `{ConnectorName}.dataConnectorIngestApi-meta.xml` | `CustomerEvents.dataConnectorIngestApi-meta.xml` |
| S3 Connector | `{ConnectorName}.s3DataConnector-meta.xml` | `CustomerData.s3DataConnector-meta.xml` |
| Data Source | `{SourceName}.dataSource-meta.xml` | `Salesforce_Home.dataSource-meta.xml` |
| Calc Insight | `{InsightName}.mktCalcInsightObjectDef-meta.xml` | `EmailScore.mktCalcInsightObjectDef-meta.xml` |
| Segment | `{SegmentName}.marketSegmentDefinition-meta.xml` | `HighValueCustomers.marketSegmentDefinition-meta.xml` |
