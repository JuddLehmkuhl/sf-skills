---
name: sf-data-cloud
description: >
  Use when working with Salesforce Data Cloud (Data 360) -- building DMO/DLO objects,
  deploying data streams, creating calculated insights, configuring identity resolution,
  managing segments, deploying via Data Kits, querying with ANSI SQL, or using the
  Ingestion API. Covers metadata deployment, Apex integration, and the full
  DSO-to-DLO-to-DMO-to-Unified Profile pipeline.
license: MIT
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
---

# sf-data-cloud: Salesforce Data Cloud (Data 360) Development

## Overview

Data Cloud (rebranded Data 360, October 2025) unifies customer data from any source into a single profile. It ingests raw data through connectors, stages it as Data Source Objects (DSOs), materializes it into Data Lake Objects (DLOs), maps it to canonical Data Model Objects (DMOs), resolves identities, computes calculated insights, segments audiences, and activates them to downstream systems.

Core pipeline:

```
External Sources --> Data Streams --> DSO (staging, raw)
    --> DLO (materialized, Parquet/Iceberg on S3)
    --> DMO (canonical virtual view)
    --> Identity Resolution --> Unified Profile
    --> Calculated Insights / Segments --> Activations
```

---

## Architecture Quick Reference

```
+------------------+     +------------------+     +------------------+
| DSO              |     | DLO              |     | DMO              |
| (Data Source Obj) | --> | (Data Lake Obj)  | --> | (Data Model Obj) |
| Raw ingested data|     | Materialized     |     | Canonical schema |
| Staging layer    |     | Parquet on S3    |     | Virtual view     |
| Auto-created     |     | Schema-typed     |     | __dlm suffix     |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
                                              +---------------------+
                                              | Identity Resolution |
                                              | Match + Reconcile   |
                                              +---------------------+
                                                          |
                                                          v
                                              +---------------------+
                                              | Unified Profile     |
                                              +---------------------+
                                                     /         \
                                                    v           v
                                      +----------------+  +---------------+
                                      | Calc Insights  |  | Segments      |
                                      | SQL aggregation|  | Filter criteria|
                                      +----------------+  +---------------+
                                                     \         /
                                                      v       v
                                              +---------------------+
                                              | Activations         |
                                              | MC, Google, S3, etc |
                                              +---------------------+
```

---

## Orchestration Order

```
1. Data Kit (DevOps)    --> Create in sandbox UI first
2. Connectors           --> Authorize connector (UI-only, then retrieve metadata)
3. Data Streams         --> Configure streams linking connectors to source objects
4. DLO Objects          --> Materialized schema-typed objects (auto-created by streams)
5. DMO Objects          --> Canonical model + field mappings
6. Identity Resolution  --> Match + reconciliation rules
7. Calculated Insights  --> SQL aggregations on DMOs
8. Segments             --> Filter criteria for activation
9. Activations          --> Push to Marketing Cloud, Google Ads, S3, etc.
```

Deploy order matters. DMOs depend on DLOs. Identity Resolution depends on DMOs. Calculated Insights and Segments depend on resolved profiles.

---

## UI-Only vs. Deployable Components

Understanding what requires the UI and what can be fully automated via metadata is critical.

| Component | Create via Metadata? | Deploy Between Orgs? | Notes |
|---|---|---|---|
| **Data Kit** | No | Yes (after UI creation) | Must create DevOps Data Kit in UI first, then retrieve/deploy |
| **Connector (CRM)** | No | Yes (deploys INACTIVE) | Auth requires UI; re-authorize after deploy |
| **Connector (Ingestion API)** | Yes | Yes | `DataConnectorIngestApi` XML is simple; no auth needed |
| **Connector (S3)** | Partial | Yes (deploys INACTIVE) | `DataConnectorS3` XML deploys config; credentials require UI |
| **Data Source** | Yes | Yes | `DataSource` XML is simple (label + prefix) |
| **Data Stream** | Yes | Yes | `DataStreamDefinition` XML; references a connector that must exist |
| **DMO (__dlm objects)** | Yes | Yes | Full metadata control via `CustomObject` + `mktDataModelAttributes` |
| **DLO** | No (auto-created) | Yes (via Data Kit) | Auto-created by data streams; deployable within Data Kit |
| **Identity Resolution** | No | Yes (via Data Kit) | Rules created in UI; retrievable and deployable |
| **Calculated Insights** | Yes | Yes (via Data Kit) | SQL-defined; must be wrapped in Data Kit for deploy |
| **Segments** | Partial | Yes | `MarketSegmentDefinition` XML; complex segments easier via UI |
| **Activations** | No | Yes | `ActivationPlatform` metadata; initial setup requires UI |

### Practical Workflow

**First org (manual setup):**
1. Create Data Kit, connectors, and authorize in UI
2. Configure data streams and field mappings
3. Retrieve all metadata via `sf project retrieve start`

**Subsequent orgs (automated deploy):**
1. Create DevOps Data Kit in target org (UI, one-time)
2. Deploy retrieved metadata via `sf project deploy start`
3. Re-authorize connectors in target org (UI)
4. Redeploy Data Kit after re-authorization

---

## Data Kit Deployment Workflow (Critical)

Data Kits are the **only supported deployment mechanism** for Data Cloud metadata between orgs.

### Step-by-Step

1. **Create DevOps Data Kit** in source org: Setup > Data Cloud Setup > Data Kits > New DevOps Data Kit
2. **Download manifest** (package.xml) from the Data Kit
3. **Retrieve metadata** from source org:
   ```bash
   sf project retrieve start --manifest manifest/package.xml --target-org source-org
   ```
4. **CRITICAL: Delete key qualifier files** before deploying (causes DUPLICATE_VALUE errors):
   ```bash
   # Remove key qualifier metadata that conflicts on deploy
   find force-app -name "*KeyQualifier*" -type f -delete
   ```
5. **Create DevOps Data Kit** in target org (must exist before deploying)
6. **Deploy to target org**:
   ```bash
   sf project deploy start --manifest manifest/package.xml --target-org target-org
   ```
7. **Re-authorize connectors** in target org (connectors deploy as INACTIVE)
8. **Redeploy Data Kit** after connector re-authorization

### Data Kit package.xml Example

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
        <name>CustomObject</name>
    </types>
    <version>62.0</version>
</Package>
```

---

## DLM Object Metadata Format

Data Cloud objects use standard CustomObject/CustomField XML with special `mktDataModelAttributes` and `mktDataModelFieldAttributes` blocks. Objects end with `__dlm` suffix; fields use standard `__c` suffix.

### Object XML (`My_Object__dlm.object-meta.xml`)

```xml
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My_Custom_Object_Home</label>
    <mktDataModelAttributes>
        <creationType>Custom</creationType>
        <dataModelTaxonomy>Salesforce_SFDCReferenceModel_0_93</dataModelTaxonomy>
        <dataSpaceName>default</dataSpaceName>
        <isEnabled>true</isEnabled>
        <isSegmentable>false</isSegmentable>
        <isUsedForMetrics>false</isUsedForMetrics>
        <objectCategory>Salesforce_SFDCReferenceModel_0_93.Related</objectCategory>
    </mktDataModelAttributes>
</CustomObject>
```

### Field XML (`fields/MyField__c.field-meta.xml`)

```xml
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Id__c</fullName>
    <label>Record ID</label>
    <length>60</length>
    <mktDataModelFieldAttributes>
        <definitionCreationType>Custom</definitionCreationType>
        <isDynamicLookup>false</isDynamicLookup>
        <primaryIndexOrder>1</primaryIndexOrder>
        <usageTag>None</usageTag>
    </mktDataModelFieldAttributes>
    <required>false</required>
    <type>Text</type>
</CustomField>
```

### Key mktDataModelAttributes Fields

| Attribute | Values | Purpose |
|-----------|--------|---------|
| `creationType` | Custom, Standard | Whether object was created by user or system |
| `dataModelTaxonomy` | Salesforce_SFDCReferenceModel_0_93 | Reference data model version |
| `dataSpaceName` | default, custom name | Target data space |
| `isSegmentable` | true/false | Whether object can be used in segmentation |
| `isUsedForMetrics` | true/false | Whether object is used in calculated insights |
| `objectCategory` | *.Related, *.Profile, *.Other | Category within taxonomy |

### Key mktDataModelFieldAttributes Fields

| Attribute | Values | Purpose |
|-----------|--------|---------|
| `definitionCreationType` | Custom, Standard | Field origin |
| `isDynamicLookup` | true/false | Dynamic relationship lookup |
| `primaryIndexOrder` | 1, 2, ... (integer) | Primary key ordering |
| `usageTag` | None, Key, Partition | Field usage designation |

See `references/xml-templates.md` for complete templates of all metadata types.

---

## Query APIs

| Method | Endpoint / Class | Language | Use Case |
|--------|-----------------|----------|----------|
| Data Cloud SQL | `/api/v2/query` or `/ssot/query-sql` | ANSI SQL | Primary query method for external callers |
| SOQL on DMOs | Standard SOQL endpoints | SOQL | Apex queries on `__dlm` objects (Spring '25+, API v250) |
| ConnectApi.CdpQuery | `ConnectApi.CdpQuery.queryAnsiSqlV2()` | ANSI SQL | Apex server-side queries |
| Data Cloud SQL in Flow | Data Cloud SOQL Lookup | SOQL | Flow-based queries on DMOs |

### SQL vs SOQL Key Differences

| Feature | Data Cloud SQL (ANSI) | SOQL on DMOs |
|---------|----------------------|--------------|
| JOINs | Yes (INNER, LEFT, RIGHT, FULL) | No |
| NULL handling | `IS NOT DISTINCT FROM` | `= null` |
| Aggregation | GROUP BY, HAVING, window functions | GROUP BY, HAVING |
| Subqueries | Yes | Limited |
| Available in Apex | Via ConnectApi | Direct query (Spring '25+) |

See `references/apis.md` for full query examples and endpoint details.

---

## Ingestion API

### Streaming Ingestion

```
POST /api/v1/ingest/sources/{connectorName}/{objectName}
Content-Type: application/json

{"data": [{"field1": "value1", "field2": "value2"}]}
```

| Constraint | Limit |
|-----------|-------|
| Payload size | 200 KB max per request |
| Request rate | 250 requests/second |
| Schema format | OpenAPI 3.0 YAML |

### Bulk Ingestion

```
1. POST /api/v1/ingest/jobs     --> Create job (returns jobId)
2. PUT  /api/v1/ingest/jobs/{jobId}/batches --> Upload CSV data
3. PATCH /api/v1/ingest/jobs/{jobId}        --> Close job (state: UploadComplete)
4. GET  /api/v1/ingest/jobs/{jobId}         --> Check status
```

See `references/apis.md` for full Ingestion API details, schema examples, and authentication.

---

## Apex Integration

### ConnectApi.CdpQuery (ANSI SQL from Apex)

```apex
ConnectApi.CdpQueryInput input = new ConnectApi.CdpQueryInput();
input.sql = 'SELECT FirstName__c, LastName__c FROM Individual_Home__dlm LIMIT 10';
ConnectApi.CdpQueryOutput output = ConnectApi.CdpQuery.queryAnsiSqlV2(input);
// output.data contains List<Map<String, Object>>
```

### SOQL on DMOs (Spring '25+, API v250)

```apex
List<Individual_Home__dlm> individuals = [
    SELECT FirstName__c, LastName__c
    FROM Individual_Home__dlm
    WHERE LastName__c = 'Smith'
    LIMIT 100
];
```

### Test Mocking with SoqlStubProvider

```apex
@IsTest
private class MyDmoQueryTest {
    @IsTest
    static void testDmoQuery() {
        SoqlStubProvider stub = new SoqlStubProvider();
        // Configure stub with test data
        Test.startTest();
        // Execute code under test
        Test.stopTest();
        // Assert results
    }
}
```

See `references/apis.md` for complete Apex patterns, error handling, and test examples.

---

## Directory Structure

```
force-app/main/default/
├── mktDataSources/                # Data source definitions (label + prefix)
├── dataconnectors/                # Generic connector configs
├── dataConnectorIngestApis/       # Ingestion API connector configs
├── s3DataConnectors/              # S3 connector configs
├── dataStreamDefinitions/         # Data stream configs (link connector to source)
├── dataSourceBundleDefinitions/   # Data source bundle configs
├── dataSourceObjects/             # Data source object mappings
├── dataPackageKitDefinitions/     # Data Kit definitions
├── DataPackageKitObjects/         # Data Kit object mappings
├── objects/
│   └── My_Object__dlm/           # DLM object directory
│       ├── My_Object__dlm.object-meta.xml
│       └── fields/
│           └── MyField__c.field-meta.xml
├── mktCalcInsightObjectDefs/      # Calculated Insight definitions
├── marketSegmentDefinitions/      # Segment definitions
├── activationPlatforms/           # Activation target configs
├── fieldSrcTrgtRelationships/     # Field source-target mappings
└── objectSourceTargetMaps/        # Object source-target mappings
```

---

## Gotcha Table

| # | Gotcha | Details |
|---|--------|---------|
| 1 | Data Kit required | Most DC components cannot deploy standalone -- must be in a DevOps Data Kit |
| 2 | Delete key qualifier files | Before deploying, delete all key qualifier files or deployment fails with DUPLICATE_VALUE |
| 3 | No mixed packages (Winter '25+) | DC metadata and non-DC metadata cannot coexist in a single package |
| 4 | FieldSrcTrgtRelationship errors | Common deployment error -- delete problematic XML files or retrieve specific relationships |
| 5 | SQL not SOQL | Data Cloud Query API uses ANSI SQL, not SOQL. Use `IS NOT DISTINCT FROM` for NULL-safe joins |
| 6 | DLM object naming | Objects end with `__dlm` suffix. Fields use standard `__c` suffix |
| 7 | Data Spaces must match | Target org must have data spaces with identical prefix names to source org |
| 8 | Connector re-authorization | After deploying, connectors must be re-authorized in target org |
| 9 | No `sf data cloud` CLI | No dedicated CLI namespace -- all via `sf project deploy/retrieve` with package.xml |
| 10 | 200KB streaming limit | Streaming Ingestion API payloads max 200KB per request |
| 11 | DLO field types immutable | Once a DLO is created, you cannot change field data types |
| 12 | CRM Permission Set manual | `sfdc_a360_sfcrm_data_extrac` permission set cannot be deployed via Metadata API |
| 13 | Identity Resolution order | Must deploy DMOs and field mappings before identity resolution rulesets |
| 14 | Calculated Insight SQL validation | SQL in calculated insights is validated at deploy time -- invalid SQL blocks deployment |
| 15 | Data streams require connectors | DataStreamDefinition references a `dataConnector` that must already exist in the target org |
| 16 | DataConnectorIngestApi no wildcard | `DataConnectorIngestApi` does NOT support `*` wildcard in package.xml -- must list by name |
| 17 | DLO suffix is `__dll` not `__dlm` | DLO (Data Lake Object) suffix is `__dll`; DMO (Data Model Object) suffix is `__dlm` |

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `DUPLICATE_VALUE` on deploy | Key qualifier files conflict | Delete key qualifier files before deploying |
| `FIELD_TYPE_MISMATCH` DLO to DMO | Incompatible field type mapping | Only Number-to-Text mapping allowed. Other mismatches require recreating the DLO |
| `INVALID_CROSS_REFERENCE_KEY` | Missing referenced object | FieldSrcTrgtRelationship references a missing object. Delete the problematic files |
| Connector `INACTIVE` after deploy | Connectors lose auth on deploy | Re-authorize connector in target org, then redeploy Data Kit |
| `Data Kit not found` | Target org missing Data Kit | Create DevOps Data Kit in target org first via Setup > Data Cloud Setup > Data Kits |
| `Data space not found` | Mismatched data space names | Create matching data space in target org or update metadata to use `default` |
| `Cannot modify field type` | DLO field type change attempt | Drop and recreate the DLO with correct field types |
| `SQL syntax error` in Calculated Insight | Invalid ANSI SQL | Validate SQL in Data Cloud SQL editor before deploying as metadata |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Deploying DC metadata in same package as Apex/LWC | Mixed package restriction (Winter '25+) | Separate into two packages -- one for DC, one for platform |
| Skipping Data Kit and deploying individual types | Individual deploy is unsupported for most DC types | Always use Data Kit workflow |
| Using SOQL syntax in Query API | Query API expects ANSI SQL, not SOQL | Use ANSI SQL with JOINs, `IS NOT DISTINCT FROM`, etc. |
| Not filtering early in SQL | DC can hold billions of rows; full scans timeout | Add WHERE clauses and LIMIT early in queries |
| Hardcoding data space names | Data spaces must match between orgs | Use variables or configuration; document required data spaces |
| Modifying DLO field types after creation | Field types are immutable on DLOs | Plan field types upfront; recreate DLO if types must change |
| Deploying without connector re-auth step | Connectors go INACTIVE silently | Include re-auth as an explicit deployment step |

---

## Cross-Skill Integration

| Skill | Direction | Relationship | Key Integration Point |
|-------|-----------|-------------|----------------------|
| sf-metadata | UPSTREAM | PRIMARY | Creates custom objects/fields that DC ingests via CRM connector |
| sf-deploy | DOWNSTREAM | PRIMARY | Deploys Data Kit package.xml to target orgs |
| sf-apex | LATERAL | SECONDARY | `ConnectApi.CdpQuery` for Apex-based DC queries |
| sf-integration | LATERAL | SECONDARY | Named Credentials for cross-org DC API calls |
| sf-connected-apps | UPSTREAM | SECONDARY | OAuth Connected Apps with `cdp_query`, `cdp_ingest`, `cdp_segment` scopes |
| sf-testing | DOWNSTREAM | SECONDARY | `SoqlStubProvider` for DMO test mocking in Apex tests |
| sf-diagram | LATERAL | SECONDARY | Mermaid diagrams for DC pipeline architecture |
| sf-soql | LATERAL | SECONDARY | SOQL on `__dlm` objects (Spring '25+) |

---

## CLI Quick Reference

```bash
# Create SFDX project for Data Cloud
sf project generate --name my-dc-project

# Retrieve DC metadata from Data Kit manifest
sf project retrieve start --manifest manifest/package.xml --target-org source-org

# Deploy DC metadata
sf project deploy start --manifest manifest/package.xml --target-org target-org

# Validate deployment (dry run)
sf project deploy start --dry-run --manifest manifest/package.xml --target-org target-org

# List org connections
sf org list

# Open org to Data Cloud Setup
sf org open --target-org my-org --path lightning/setup/CdpSetup/home

# Open org to Data Cloud home
sf org open --target-org my-org --path lightning/o/SSOT_Home/home

# Generate manifest from source directory
sf project generate manifest --source-dir force-app --name manifest/package.xml
```

---

## Reference Files

Detailed content lives in reference files to keep this skill concise:

| File | Contents |
|------|----------|
| `references/metadata-types.md` | Complete metadata type table with directories, suffixes, and packaging support |
| `references/data-pipeline.md` | Deep dive on DSO, DLO, DMO, connectors, identity resolution, segments, activations |
| `references/apis.md` | Ingestion API (streaming + bulk), Query APIs, Apex ConnectApi, OAuth scopes |
| `references/xml-templates.md` | Real XML metadata templates for all key component types |

---

## Notes

- **CLI**: Uses `sf` CLI v2 -- no dedicated `sf data cloud` namespace exists
- **API Version**: 62.0+ recommended; SOQL on DMOs requires API v250 (Spring '25)
- **Packages**: DC metadata and platform metadata must be in separate packages (Winter '25+)
- **Data Kits**: Required for all cross-org DC metadata deployment
- **Connectors**: Always re-authorize after deploying to a new org
