# Query Plan Analysis (Deep Dive)

> Parent: [SKILL.md](../SKILL.md) -- Query Plan Analysis section

## REST API Explain Endpoint

There is no `--plan` flag on `sf data query`. The query plan feature uses the REST API `explain` parameter.

The REST API provides a query explain endpoint that returns the query optimizer's execution plan **without running the query**:

```
GET /services/data/v62.0/query/?explain=SELECT+Id+FROM+Account+WHERE+Name='Acme'
```

### Using sf CLI to Call the Explain Endpoint

```bash
# Use sf api to call the explain endpoint directly
sf org open --target-org my-sandbox --url-only \
  | xargs -I {} curl -H "Authorization: Bearer $(sf org display --target-org my-sandbox --json | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["accessToken"])')" \
  "{}/services/data/v62.0/query/?explain=SELECT+Id+FROM+Account+WHERE+Name='Acme'"
```

**Simpler approach using Anonymous Apex**:
```bash
# Execute via Anonymous Apex to get explain plan output
sf apex run --target-org my-sandbox --file /dev/stdin <<'EOF'
HttpRequest req = new HttpRequest();
req.setEndpoint(URL.getOrgDomainUrl().toExternalForm()
  + '/services/data/v62.0/query/?explain='
  + EncodingUtil.urlEncode('SELECT Id FROM Account WHERE Name = \'Acme\'', 'UTF-8'));
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
HttpResponse res = new Http().send(req);
System.debug(LoggingLevel.ERROR, '*** QUERY PLAN: ' + res.getBody());
EOF
```

### Explain Response Fields

| Field | Description |
|-------|-------------|
| `cardinality` | Estimated number of rows the query will return |
| `fields` | Fields used by the query filter |
| `leadingOperationType` | How the optimizer accesses data: `Index`, `TableScan`, `Other` |
| `relativeCost` | Cost relative to other plans (lower is better); > 1.0 suggests a table scan |
| `sobjectCardinality` | Total number of records in the object |
| `sobjectType` | Object being queried |
| `notes` | Array of optimizer notes (e.g., "Not considering filter for optimization...") |

### Selectivity Rule of Thumb

- Standard index: selective if matching rows < 30% of total records AND < 1,000,000 rows
- Custom index: selective if matching rows < 10% of total AND < 333,333 rows
- For objects with < 100,000 records, table scans may still perform acceptably

> **Cross-reference**: Hand off to **sf-soql** skill for rewriting non-selective queries, adding composite filters, or restructuring SOQL for better index utilization.

### Developer Console Query Plan Tool

1. Open Developer Console
2. Enable: **Help > Preferences > Enable Query Plan** (checkbox)
3. Open Query Editor tab
4. Enter SOQL query and click **Query Plan** button
5. Review the plan output (same fields as REST API explain)
