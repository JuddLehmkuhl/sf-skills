# Data Cloud Data Pipeline Architecture

Complete reference for the Data Cloud data pipeline: ingestion, storage layers, identity resolution, calculated insights, segmentation, and activation.

---

## Data Storage Layers

### DSO -- Data Source Objects

Data Source Objects are the initial landing zone for ingested data.

- **Purpose:** Temporary staging area that holds raw ingested data
- **Format:** CSV-like raw format
- **Lifecycle:** Auto-created by data streams when a connector ingests data
- **Queryability:** Not directly queryable by users or SQL
- **Retention:** Data is transient; it flows through to the DLO layer

### DLO -- Data Lake Objects

Data Lake Objects are the persistent, materialized storage layer.

- **Purpose:** Schema-typed, materialized storage of ingested data
- **Storage:** Parquet format on S3 with Apache Iceberg table abstraction
- **Suffix:** `__dll` (Data Lake Layer) in API references
- **Field Types:** Text, Number, Date, DateTime, Boolean
- **Immutable Types:** Once a field is created, its data type CANNOT be changed
- **Type Mismatch Rule:** The only acceptable type mismatch when mapping DLO to DMO is Number to Text. All other type mismatches will fail.
- **Metadata:** DLO definitions are deployed as part of Data Kits (DataPackageKitDefinition)

### DMO -- Data Model Objects

Data Model Objects provide the semantic, queryable layer over DLO data.

- **Purpose:** Virtual (non-materialized) view into DLO data with business meaning
- **Naming Convention:** `{namespace}__{fieldname}__c` for custom fields
- **Suffix:** `__dlm` (Data Lake Model) in API and SOQL/SQL references
- **Primary Key:** Required on every DMO
- **Foreign Keys:** Optional; used to define relationships between DMOs
- **Standard DMOs:** Approximately 200+ standard DMOs organized by subject area

#### Standard DMO Subject Areas

| Subject Area | Example DMOs |
|---|---|
| Individual | Individual, Account, Household |
| Contact Point | ContactPointAddress, ContactPointEmail, ContactPointPhone |
| Financial | FinancialAccount, FinancialTransaction |
| Loyalty | LoyaltyMemberCurrency, LoyaltyMemberTier, LoyaltyProgram |
| Sales | SalesOrder, SalesOrderProduct, Opportunity |
| Engagement | EmailEngagement, WebEngagement, MobileEngagement |
| Consent | ContactPointConsent, DataUsePurpose |
| Service | Case, ServiceAppointment |
| Survey | Survey, SurveyResponse |
| Product | Product, PriceBook |
| Campaign | Campaign, CampaignMember |

---

## Data Streams and Connectors

### Connector Types

| Connector | Source | Notes |
|---|---|---|
| Salesforce CRM | Sales/Service Cloud | Pre-built bundles with automatic DMO mapping |
| Marketing Cloud Email | MC email engagement data | Bundle for email opens, clicks, sends |
| Marketing Cloud Mobile | MC SMS engagement data | Bundle for SMS sends and responses |
| Marketing Cloud Push | MC push notification data | Bundle for push engagement |
| Ingestion API | Any external source | REST API with streaming and bulk modes |
| Amazon S3 | S3 bucket files | Supports CSV and Parquet file formats |
| Google Cloud Storage | GCS buckets | Automated periodic file transfer |
| Azure Storage | Azure blob storage | Cloud storage connector |
| Snowflake | Snowflake tables/views | Zero-copy integration (no data movement) |
| Databricks | Databricks lakehouse | Zero-copy integration (no data movement) |
| Google BigQuery | BigQuery tables | Zero-copy integration (no data movement) |
| Amazon Redshift | Redshift tables | Zero-copy integration (no data movement) |
| B2C Commerce | Commerce Cloud | Automatic activation target creation |

### Data Stream Configuration

- Each data stream links a connector to a specific source object
- Data streams define the refresh schedule (frequency, start time)
- Modes: Full Refresh or Incremental (upsert/delete)
- Metadata type: `DataStreamDefinition`

---

## Identity Resolution

Identity Resolution unifies records from multiple sources into a single unified profile.

### Match Rules

| Match Type | Description | Use Case |
|---|---|---|
| Exact | Byte-for-byte match | IDs, exact email addresses |
| Exact Normalized | Case-insensitive, trimmed whitespace | Email, name matching |
| Fuzzy/Normalized | Approximate matching with tolerance | Name variations, typos |

### Reconciliation Rules

- Define how conflicts are resolved when matched records have differing field values
- Options: Most Recent, Source Priority, Most Frequent
- Applied per-field to control which source wins

### Constraints

- **Maximum 2 rulesets** per data model, per data space, per org
- **Ruleset ID is immutable** once set -- it cannot be changed after creation
- Identity resolution runs as a scheduled process after data ingestion
- Output: UnifiedIndividual__dlm and IndividualIdentityLink__dlm objects

---

## Calculated Insights

Calculated Insights allow you to create derived metrics and aggregations using SQL.

### Creation Methods
- **SQL Builder:** Write ANSI SQL directly
- **Visual Builder:** Point-and-click interface (limited to simpler aggregations)

### Supported SQL Functions

| Category | Functions |
|---|---|
| Aggregate | SUM, COUNT, AVG, MIN, MAX |
| Window | ROW_NUMBER, RANK, DENSE_RANK, NTILE |
| Conditional | CASE ... WHEN ... THEN ... ELSE ... END |
| Join | INNER JOIN, LEFT/RIGHT/FULL OUTER JOIN |
| Streaming | WINDOW() function for streaming aggregations |

### Key Details
- Metadata type: `MktCalcInsightObjectDef`
- Must be included in a Data Kit for deployment
- Can reference any DMO or unified object
- Output is a new queryable object with calculated fields
- Supports scheduled refresh

---

## Segments

Segments define audiences based on filters applied to DMO and calculated insight data.

### Segment Types

| Type | Refresh Speed | Use Case |
|---|---|---|
| Standard | 12-24 hours | Batch campaigns, large audiences |
| Rapid Publish | 1-4 hours | Time-sensitive but not real-time |
| Real-time | On-demand (event-driven) | Triggered experiences, personalization |
| Dynamic (Parameterized) | Varies | Reusable templates with variable inputs |

### Key Details
- Metadata type: `MarketSegmentDefinition`
- Segments can be nested (segment of a segment)
- Segment membership is stored and queryable
- Used as input for Activations and Data Actions

---

## Activations and Data Actions

### Activations (Batch)

Activations push segment data to external platforms on a scheduled basis.

| Activation Target | Description |
|---|---|
| Marketing Cloud | Email, SMS, push campaigns |
| Google Ads | Customer Match audiences |
| Meta (Facebook) | Custom Audiences |
| Amazon S3 | File export to S3 bucket |
| Google Cloud Storage | File export to GCS |
| Azure Storage | File export to Azure |
| Trade Desk | Programmatic advertising |
| Braze | Customer engagement platform |

- Metadata type: `ActivationPlatform`
- Scheduled frequency: hourly, daily, or custom
- Supports field mapping and filtering before export

### Data Actions (Near Real-Time)

Data Actions trigger near real-time responses based on segment membership changes or data events.

| Target | Description |
|---|---|
| Platform Events | Publish Salesforce Platform Events |
| Webhooks | HTTP POST to external endpoints |
| Marketing Cloud | Journey entry or API event |
| Flow | Trigger a Salesforce Flow |

- Latency: Minutes (not seconds)
- Triggered by segment entry/exit or data change events

---

## Data Spaces

Data Spaces provide organizational containers for data segregation within a single Data Cloud org.

### Key Concepts
- Each org starts with a `default` data space
- Data spaces isolate DMOs, segments, calculated insights, and activations
- Identity resolution runs within a data space boundary
- Users are granted access to specific data spaces via permission sets

### Deployment Considerations
- **Prefix names must match** between source and target orgs for deployment to succeed
- Data space assignments are part of DMO metadata (`dataSpaceName` attribute)
- Cross-data-space queries are not supported
