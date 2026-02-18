# Event Monitoring (Production Debugging)

> Parent: [SKILL.md](../SKILL.md) -- Event Monitoring section

When debug logs are impractical -- high-traffic production orgs, intermittent issues, security audits, or timing-sensitive bugs -- Event Monitoring provides a non-intrusive alternative.

## What is Event Monitoring?

Event Monitoring captures operational events across your entire org via the **EventLogFile** object. Unlike debug logs:
- No performance overhead on end users
- Captures events for ALL users (not just traced users)
- Retains data for 30 days (or 1 day in Developer Edition)
- No 20 MB truncation limit per event

## Availability

| Edition | Access | Retention |
|---------|--------|-----------|
| Developer Edition | All log types (free) | 1 day |
| Enterprise / Unlimited | Requires Event Monitoring add-on license | 30 days |
| Shield Platform Encryption | Included with Shield | 30 days |

## Key Event Types for Debugging

| EventType | What It Captures | Debug Use Case |
|-----------|-----------------|----------------|
| `ApexExecution` | Apex class execution: CPU time, run time, method name | Performance profiling across users |
| `ApexUnexpectedException` | Unhandled Apex exceptions in production | Triage production errors without Trace Flags |
| `API` | REST/SOAP API calls: endpoint, response time, status | Integration debugging |
| `Login` | Login attempts, IP, browser, success/failure | Security investigation |
| `ReportExport` | Report exports: who, what, when | Data access auditing |
| `LightningPageView` | Lightning page loads and performance | UX performance |
| `ApexTrigger` | Trigger execution time and entity | Trigger performance trending |
| `ApexSoap` | SOAP callout details | External service debugging |
| `BulkApi` | Bulk API job details | Data load debugging |
| `FlowExecution` | Flow interview execution | Flow performance analysis |

## Querying EventLogFile

```bash
# List available event types from the last 7 days
sf data query \
  --query "SELECT Id, EventType, LogDate, LogFileLength FROM EventLogFile WHERE LogDate >= LAST_N_DAYS:7 ORDER BY LogDate DESC" \
  --target-org production-org

# Get Apex execution events from last 24 hours
sf data query \
  --query "SELECT Id, EventType, LogDate, LogFileLength FROM EventLogFile WHERE EventType = 'ApexExecution' AND LogDate = TODAY" \
  --target-org production-org

# Get unexpected Apex exceptions (production error triage)
sf data query \
  --query "SELECT Id, EventType, LogDate, LogFileLength FROM EventLogFile WHERE EventType = 'ApexUnexpectedException' AND LogDate >= LAST_N_DAYS:7" \
  --target-org production-org
```

## Downloading and Analyzing Event Log Files

```bash
# Download a specific event log file (returns CSV)
sf data get record \
  --sobject EventLogFile \
  --record-id 0AT... \
  --target-org production-org \
  --json

# Or use curl for the LogFile blob
ACCESS_TOKEN=$(sf org display --target-org production-org --json | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["accessToken"])')
INSTANCE_URL=$(sf org display --target-org production-org --json | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["instanceUrl"])')

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$INSTANCE_URL/services/data/v62.0/sobjects/EventLogFile/0ATxx.../LogFile" \
  -o apex_execution_events.csv
```

## Real-Time Event Monitoring

For Shield-licensed orgs, Real-Time Events provide streaming event data:

| Real-Time Event | Use Case |
|-----------------|----------|
| `ApiAnomalyEvent` | Detect unusual API access patterns |
| `CredentialStuffingEvent` | Login attack detection |
| `ReportAnomalyEvent` | Unusual report access |
| `SessionHijackingEvent` | Session security |
| `ApexUnexpectedExceptionEvent` | Real-time Apex error alerts |

These are accessed via CometD streaming or Pub/Sub API, not EventLogFile SOQL.
