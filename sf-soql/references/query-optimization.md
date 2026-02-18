# Query Optimization Deep Dive

> Back to [SKILL.md](../SKILL.md)

## Index Strategy

**Auto-Indexed Fields** (always selective when filtered):
- `Id`, `Name`, `OwnerId`, `CreatedDate`, `LastModifiedDate`, `SystemModstamp`
- `RecordTypeId`, External ID fields, Master-Detail fields
- Lookup fields (selective when unique or low-cardinality)

**Object-Specific Indexed Fields**:
| Object | Indexed Fields |
|--------|---------------|
| Account | AccountNumber, Site |
| Contact | Email |
| Lead | Email, Name |
| Case | CaseNumber |
| Task / Event | ActivityDate |

## Selectivity Thresholds

```
A filter is selective when it returns:
  - Less than 10% of records (first 1M records in the object)
  - Less than 5% of records (beyond 1M records)
  - AND the result set is under 333,333 records

Two-column index selectivity:
  - Less than 5% of records (first 1M)
  - Less than 2.5% of records (beyond 1M)

When OR is used, ALL branches must be selective individually.
When AND is used, at least one branch must be selective.
```

## Optimization Patterns

```sql
-- BAD: Non-selective, full table scan
SELECT Id FROM Lead WHERE Status = 'Open'

-- GOOD: Selective index + narrowing filter + limit
SELECT Id FROM Lead
WHERE Status = 'Open' AND CreatedDate = LAST_N_DAYS:30
LIMIT 10000

-- BAD: Leading wildcard prevents index usage
SELECT Id FROM Account WHERE Name LIKE '%corp'

-- GOOD: Trailing wildcard can use index
SELECT Id FROM Account WHERE Name LIKE 'Acme%'

-- BAD: Negative operators are never selective
SELECT Id FROM Account WHERE Industry != 'Other'

-- GOOD: Reframe as positive filter
SELECT Id FROM Account WHERE Industry IN ('Technology', 'Finance', 'Healthcare')

-- BAD: Formula fields are not indexed
SELECT Id FROM Account WHERE Revenue_Tier__c = 'Enterprise'

-- GOOD: Filter on the underlying indexed field
SELECT Id FROM Account WHERE AnnualRevenue > 10000000
```

## Query Plan Analysis

> **IMPORTANT**: The `sf data query --plan` flag does NOT exist in sf CLI v2. Query plans must be retrieved via the REST API `explain` parameter or the Developer Console Query Plan tool.

**Method 1: REST API explain parameter**

```bash
# Get query plan via REST API (does NOT execute the query)
# URL format: /services/data/vXX.0/query/?explain=<SOQL>
curl "https://MyDomainName.my.salesforce.com/services/data/v62.0/query/?explain=SELECT+Id+FROM+Account+WHERE+Name='Test'" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Method 2: Developer Console**

1. Open Developer Console (Setup gear icon > Developer Console)
2. Open Query Editor tab (bottom pane)
3. Check the "Use Tooling API" checkbox
4. Enter your SOQL query
5. Click "Query Plan" button
6. Review the plan output

**Method 3: Anonymous Apex with Tooling API callout**

```apex
// Query the explain plan via HttpRequest to Tooling API
String soql = 'SELECT Id FROM Account WHERE Name = \'Test\'';
String endpoint = URL.getOrgDomainUrl().toExternalForm()
    + '/services/data/v62.0/query/?explain='
    + EncodingUtil.urlEncode(soql, 'UTF-8');

HttpRequest req = new HttpRequest();
req.setEndpoint(endpoint);
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());

HttpResponse res = new Http().send(req);
System.debug(res.getBody());
```

**Plan Output Fields**:

| Field | Meaning | Good Value |
|-------|---------|------------|
| `cardinality` | Estimated rows returned | Lower is better |
| `fields` | Index fields considered | Non-empty = index available |
| `leadingOperationType` | How scan starts | `Index` (good) vs `TableScan` (bad) |
| `relativeCost` | Optimizer cost estimate | < 1.0 preferred |
| `sobjectCardinality` | Total records in object | Context for selectivity |
| `sobjectType` | Object being queried | Confirms target |

**Decision matrix**:
```
relativeCost < 1.0 AND leadingOperationType = 'Index'   --> Query is optimized
relativeCost > 1.0 AND leadingOperationType = 'Index'   --> Index exists but filter not selective enough
leadingOperationType = 'TableScan'                       --> No usable index, add selective filter
```
