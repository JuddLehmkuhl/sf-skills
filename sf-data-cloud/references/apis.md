# Data Cloud API Reference

Complete reference for Data Cloud APIs: authentication, ingestion, query, Apex integration, and Connect REST resources.

---

## Authentication (Two-Step OAuth)

Data Cloud uses a two-step OAuth flow. First obtain a standard Salesforce access token, then exchange it for a Data Cloud token.

### Step 1: Obtain Salesforce Access Token

Use any standard Salesforce OAuth flow (JWT Bearer, Web Server, etc.) to obtain an access token.

Example using JWT Bearer Flow:

```
POST https://login.salesforce.com/services/oauth2/token
grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
assertion={signed_jwt}
```

### Step 2: Exchange for Data Cloud Token

```
POST https://{instance_url}/services/a360/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:salesforce:grant-type:external:cdp
subject_token={salesforce_access_token}
subject_token_type=urn:ietf:params:oauth:token-type:access_token
```

Response:

```json
{
  "access_token": "{data_cloud_token}",
  "instance_url": "https://{tenant_url}",
  "token_type": "Bearer",
  "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
  "expires_in": 7200
}
```

The `instance_url` in the response is the Data Cloud tenant URL used for subsequent API calls.

---

## OAuth Scopes

| Scope | Purpose |
|---|---|
| `cdp_ingest_api` | Ingestion API (streaming and bulk) |
| `cdp_query_api` | Query API (SQL queries against DMOs) |
| `cdp_profile_api` | Profile data access |
| `cdp_calculated_insight_api` | Calculated Insights API |
| `cdp_identityresolution_api` | Identity Resolution API |
| `cdp_segment_api` | Segments API |
| `api` | Standard Salesforce API access |
| `refresh_token` | Obtain a refresh token |
| `offline_access` | Offline access (equivalent to refresh_token) |

---

## Streaming Ingestion API

Send small batches of records in real-time via REST.

### Endpoint

```
POST https://{tenant_url}/api/v1/ingest/sources/{connector_name}/{object_name}
Authorization: Bearer {data_cloud_token}
Content-Type: application/json
```

### Request Body

```json
{
  "data": [
    {
      "eventId": "evt-001",
      "customerId": "cust-123",
      "eventType": "page_view",
      "eventTime": "2026-01-15T10:30:00.000Z"
    },
    {
      "eventId": "evt-002",
      "customerId": "cust-456",
      "eventType": "purchase",
      "eventTime": "2026-01-15T10:31:00.000Z"
    }
  ]
}
```

### Response

- **202 Accepted** -- Data accepted for processing
- Data is processed approximately every 3 minutes

### Limits

| Limit | Value |
|---|---|
| Max payload size | 200 KB |
| Max requests per second | 250 |
| Processing interval | ~3 minutes |

---

## Bulk Ingestion API

Upload large CSV files for batch processing.

### Workflow

**1. Create Job**

```
POST https://{tenant_url}/api/v1/ingest/jobs
Authorization: Bearer {data_cloud_token}
Content-Type: application/json

{
  "object": "CustomerEvent",
  "sourceName": "MyIngestConnector",
  "operation": "upsert"
}
```

**2. Upload CSV Data**

```
PUT https://{tenant_url}/api/v1/ingest/jobs/{job_id}/batches
Authorization: Bearer {data_cloud_token}
Content-Type: text/csv

eventId,customerId,eventType,eventTime,amount
evt-001,cust-123,purchase,2026-01-15T10:30:00.000Z,99.99
evt-002,cust-456,page_view,2026-01-15T10:31:00.000Z,0
```

**3. Close Job**

```
PATCH https://{tenant_url}/api/v1/ingest/jobs/{job_id}
Authorization: Bearer {data_cloud_token}
Content-Type: application/json

{
  "state": "UploadComplete"
}
```

**4. Check Status**

```
GET https://{tenant_url}/api/v1/ingest/jobs/{job_id}
Authorization: Bearer {data_cloud_token}
```

### Operations
- `upsert` -- Insert or update records based on primary key
- `delete` -- Delete records matching primary key

### Limits

| Limit | Value |
|---|---|
| Max CSV file size | 150 MB |
| Max files per job | 100 |
| Max job creation rate | 20 per hour |

---

## Ingestion API Schema Requirements

The Ingestion API connector requires an OpenAPI 3.0 YAML schema to define the object structure.

| Requirement | Detail |
|---|---|
| Spec version | OpenAPI 3.0 |
| Format | YAML |
| Nesting | No nested objects allowed |
| Min objects | At least 1 object per schema |
| Min fields | At least 1 field per object |
| Max fields | 1000 fields per object |
| Object name length | Max 80 characters |

---

## Query APIs

### Comparison

| API | Endpoint | Row Limit | Result Window | Key Features |
|---|---|---|---|---|
| Query Connect (newest) | `POST /services/data/v64.0/ssot/query-sql` | No row limit | 24 hours | Parameterized queries, async results |
| Query V2 (legacy) | `POST /api/v2/query` | Cursor-based pagination | 1 hour | Direct tenant URL |
| Query V2 Connect | `POST /services/data/v61.0/ssot/queryv2` | Cursor-based pagination | 1 hour | Superseded by query-sql |

### Query Connect (Recommended)

**Submit Query:**

```
POST https://{instance_url}/services/data/v64.0/ssot/query-sql
Authorization: Bearer {salesforce_access_token}
Content-Type: application/json

{
  "sql": "SELECT ssot__FirstName__c, ssot__LastName__c FROM ssot__Individual__dlm WHERE ssot__Id__c = :id",
  "parameters": {
    "id": "ind-12345"
  }
}
```

**Check Status:**

```
GET https://{instance_url}/services/data/v64.0/ssot/query-sql/{query_id}
```

**Get Rows:**

```
GET https://{instance_url}/services/data/v64.0/ssot/query-sql/{query_id}/rows
```

**Cancel Query:**

```
DELETE https://{instance_url}/services/data/v64.0/ssot/query-sql/{query_id}
```

### Query V2 (Legacy)

```
POST https://{tenant_url}/api/v2/query
Authorization: Bearer {data_cloud_token}
Content-Type: application/json

{
  "sql": "SELECT ssot__FirstName__c FROM ssot__Individual__dlm LIMIT 100"
}
```

Response includes `nextBatchId` for cursor pagination.

---

## Data Cloud SQL vs. SOQL

Data Cloud uses ANSI SQL, not SOQL. Key differences:

| Feature | Data Cloud SQL | SOQL |
|---|---|---|
| Syntax | ANSI SQL | Salesforce SOQL |
| Object suffix | `__dlm` (e.g., `ssot__Individual__dlm`) | Standard API names |
| JOINs | INNER, LEFT/RIGHT/FULL OUTER | Relationship queries only |
| NULL handling | `IS NOT DISTINCT FROM` supported | `= null` not supported |
| Type casting | `::` and `CAST()` both supported | Not supported |
| Subqueries | Full subquery support | Limited |
| GROUP BY | Full SQL GROUP BY | Supported with aggregate queries |
| HAVING | Supported | Supported |
| UNION | Supported | Not supported |

### Object Naming in SQL

| Object Type | SQL Name Pattern | Example |
|---|---|---|
| Standard DMO | `ssot__ObjectName__dlm` | `ssot__Individual__dlm` |
| Custom DMO | `CustomObjectName__dlm` | `Customer_Event__dlm` |
| Unified Individual | `UnifiedIndividual__dlm` | `UnifiedIndividual__dlm` |
| Identity Link | `IndividualIdentityLink__dlm` | `IndividualIdentityLink__dlm` |
| Calculated Insight | `InsightName__cio` | `Email_Engagement_Score__cio` |

---

## Apex Integration

### Query Data Cloud from Apex (ConnectApi)

```apex
// Build and execute a SQL query
ConnectApi.CdpQueryInput queryInput = new ConnectApi.CdpQueryInput();
queryInput.sql = 'SELECT ssot__FirstName__c, ssot__LastName__c FROM ssot__Individual__dlm LIMIT 10';
ConnectApi.CdpQueryOutputV2 response = ConnectApi.CdpQuery.queryAnsiSqlV2(queryInput);

// Access results
List<Map<String, Object>> rows = response.data;
for (Map<String, Object> row : rows) {
    String firstName = (String) row.get('ssot__FirstName__c');
    String lastName = (String) row.get('ssot__LastName__c');
}

// Pagination -- get next batch
if (response.nextBatchId != null) {
    ConnectApi.CdpQueryOutputV2 nextPage = ConnectApi.CdpQuery.nextBatchAnsiSqlV2(response.nextBatchId);
}
```

### Direct SOQL Access (Spring '25+, API v250)

Starting with Spring '25, you can query Data Cloud DMOs directly via SOQL in Apex:

```apex
// Direct SOQL query against DMO
List<SObject> results = [
    SELECT ssot__FirstName__c, ssot__LastName__c
    FROM ssot__Individual__dlm
    WHERE ssot__Id__c = :someId
];

// Access fields
for (SObject record : results) {
    String firstName = (String) record.get('ssot__FirstName__c');
}
```

### Streaming Ingestion from Apex

```apex
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:DataCloudIngestion/api/v1/ingest/sources/MyConnector/MyObject');
req.setMethod('POST');
req.setHeader('Content-Type', 'application/json');
req.setBody('{"data": [{"eventId": "evt-001", "customerId": "cust-123"}]}');

Http http = new Http();
HttpResponse res = http.send(req);
// Expect 202 Accepted
```

---

## Connect REST API Resources

| Resource | Path | Method | Description |
|---|---|---|---|
| Query SQL | `/services/data/v64.0/ssot/query-sql` | POST | Submit an ANSI SQL query |
| Query Status | `/services/data/v64.0/ssot/query-sql/{id}` | GET | Check query execution status |
| Query Rows | `/services/data/v64.0/ssot/query-sql/{id}/rows` | GET | Retrieve query result rows |
| Cancel Query | `/services/data/v64.0/ssot/query-sql/{id}` | DELETE | Cancel a running query |
| Calculated Insights | `/services/data/v64.0/ssot/calculated-insights` | GET | List calculated insight definitions |
| Calculated Insight Detail | `/services/data/v64.0/ssot/calculated-insights/{name}` | GET | Get specific calculated insight |
| Token Exchange | `/services/a360/token` | POST | Exchange SF token for DC token |
| Data Graphs | `/services/data/v64.0/ssot/data-graphs` | GET | List data graph definitions |
| Segments | `/services/data/v64.0/ssot/segments` | GET | List segment definitions |

---

## Cross-Org Apex Pattern

When querying Data Cloud from a separate Salesforce org (e.g., querying a Data Cloud org from a Service Cloud org):

### Setup Requirements

1. **Connected App** in the Data Cloud org with scopes: `cdp_query_api`, `cdp_profile_api`, `api`, `refresh_token`
2. **Auth Provider** in the source org pointing to the DC org's Connected App
3. **Named Credential** in the source org using the Auth Provider
4. **External Credential** with appropriate principal and permission set mapping

### Apex Callout Pattern

```apex
public class DataCloudService {

    private static final String NAMED_CREDENTIAL = 'callout:DataCloud_Query';

    public static List<Map<String, Object>> queryDataCloud(String sql) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(NAMED_CREDENTIAL + '/services/data/v64.0/ssot/query-sql');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');

        Map<String, Object> body = new Map<String, Object>();
        body.put('sql', sql);
        req.setBody(JSON.serialize(body));

        Http http = new Http();
        HttpResponse res = http.send(req);

        if (res.getStatusCode() == 200) {
            Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
            return (List<Map<String, Object>>) result.get('data');
        }

        throw new CalloutException('Query failed: ' + res.getStatusCode() + ' ' + res.getBody());
    }
}
```

### Key Points
- Uses SQL (not SOQL) for Data Cloud queries
- Named Credential handles token management automatically
- The Data Cloud token exchange happens behind the scenes via the Auth Provider
- Response format matches the ConnectApi.CdpQueryOutputV2 structure
