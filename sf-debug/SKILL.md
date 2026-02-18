---
name: sf-debug
description: >
  Salesforce debugging and troubleshooting skill with log analysis, governor limit
  detection, query plan analysis, Event Monitoring, and agentic fix suggestions. Parse
  debug logs, identify performance bottlenecks, analyze stack traces, diagnose production
  issues, and automatically suggest fixes.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  enriched_by: "Claude Code"
  scoring: "100 points across 5 categories"
---

# sf-debug: Salesforce Debug Log Analysis & Troubleshooting

Expert debugging engineer specializing in Apex debug log analysis, governor limit detection, performance optimization, query plan analysis, Event Monitoring for production, and root cause analysis. Parse logs, identify issues, and automatically suggest fixes.

## Core Responsibilities

1. **Log Analysis**: Parse and analyze Apex debug logs for issues
2. **Governor Limit Detection**: Identify SOQL, DML, CPU, and heap limit concerns
3. **Performance Analysis**: Find slow queries, expensive operations, and bottlenecks
4. **Stack Trace Interpretation**: Parse exceptions and identify root causes
5. **Agentic Fix Suggestions**: Automatically suggest code fixes based on issues found
6. **Query Plan Analysis**: Analyze SOQL query performance via REST API explain endpoint
7. **Event Monitoring**: Use EventLogFile for production debugging where debug logs are impractical
8. **Runtime Limit Instrumentation**: Guide use of the `Limits` class for in-code diagnostics

## Debugging Tool Decision Framework

Before diving in, pick the right tool for the situation:

| Scenario | Primary Tool | Why |
|----------|-------------|-----|
| Sandbox exception or error | Debug Logs (sf apex tail log) | Full transaction visibility, real-time streaming |
| Sandbox performance tuning | Debug Logs + Query Plan (REST API explain) | See execution plan and log timing together |
| Production one-off error | Debug Logs (Trace Flag on user, 1-2 hr window) | Targeted capture, minimal overhead |
| Production pattern analysis | Event Monitoring (EventLogFile) | No performance overhead, covers all users |
| Intermittent production issue | Event Monitoring + Real-Time Events | Continuous capture without Trace Flags |
| Query selectivity investigation | REST API explain endpoint | Shows index usage, relative cost without executing |
| Governor limit trending | Limits class instrumentation + Custom Object logging | Runtime data across transactions |
| Post-deployment validation | sf-testing + Debug Logs | Run tests and capture logs simultaneously |
| Async job failures | Transaction Finalizers + Debug Logs | Capture failure context from Queueable jobs |

> **Cross-reference**: For SOQL query optimization after identifying slow queries, use the **sf-soql** skill. For generating optimized queries, fixing selectivity issues, or rewriting SOQL, hand off to sf-soql.

---

## Workflow (5-Phase Pattern)

### Phase 1: Log Collection

Use **AskUserQuestion** to gather:
- Debug context (deployment failure, test failure, runtime error, performance issue)
- Target org alias
- User/Transaction ID if known
- Time range of issue
- Environment (sandbox vs. production -- determines tooling approach)

**Then**:
1. List available logs: `sf apex list log --target-org [alias]`
2. Fetch specific log or tail real-time
3. Create TodoWrite tasks

### Phase 2: Log Retrieval

**List Recent Logs**:
```bash
sf apex list log --target-org [alias] --json
```

**Get Specific Log**:
```bash
sf apex get log --log-id 07Lxx0000000000 --target-org [alias]
```

**Tail Logs Real-Time**:
```bash
sf apex tail log --target-org [alias] --color
```

**Set Debug Level**:
```bash
sf apex log tail --debug-level FINE --target-org [alias]
```

**Delete Old Logs** (free up storage):
```bash
sf apex log delete --target-org [alias]
```

### Phase 3: Log Analysis

Parse the debug log and analyze across these dimensions:

1. **Execution Overview** -- Transaction type (trigger, flow, REST, batch), total execution time, entry point identification
2. **Governor Limit Analysis** -- SOQL Queries (X/100), DML Statements (X/150), DML Rows (X/10,000), CPU Time (X ms / 10,000 ms), Heap Size (X bytes / 6,000,000), Callouts (X/100)
3. **Performance Hotspots** -- Slowest SOQL queries (execution time), non-selective queries (full table scan), expensive operations (loops, iterations), external callout timing
4. **Exceptions and Errors** -- Exception type, stack trace, line number, root cause identification
5. **Recommendations** -- Immediate fixes, optimization suggestions, architecture improvements

### Phase 4: Issue Identification & Fix Suggestions

**Governor Limit Analysis Decision Tree**:

| Issue | Detection Pattern | Fix Strategy |
|-------|-------------------|--------------|
| SOQL in Loop | `SOQL_EXECUTE_BEGIN` inside `METHOD_ENTRY` repeated | Query before loop, use Map for lookups |
| DML in Loop | `DML_BEGIN` inside `METHOD_ENTRY` repeated | Collect in List, single DML after loop |
| Non-Selective Query | REST API explain shows `TableScan` | Add indexed filter or LIMIT; see **sf-soql** |
| CPU Limit | `CPU_TIME` approaching 10000 | Optimize algorithms, use async |
| Heap Limit | `HEAP_ALLOCATE` approaching 6 MB | Reduce collection sizes, use SOQL FOR loops |
| Callout Limit | `CALLOUT_EXTERNAL_ENTRY` count > 90 | Batch callouts, use Queueable |
| Row Limit | `DML_ROWS` approaching 10000 | Batch processing, Database.Stateful |
| Query Rows | `SOQL_ROWS` approaching 50000 | Add WHERE filters, use Batch Apex |

**Auto-Fix Command**:
```
Skill(skill="sf-apex", args="Fix [issue type] in [ClassName] at line [lineNumber]")
```

### Phase 5: Fix Implementation

1. **Generate fix** using sf-apex skill
2. **Deploy fix** using sf-deploy skill
3. **Verify fix** by re-running and checking logs
4. **Report results**

---

## Debug Log Reference

### Log Line Format

```
XX.X (XXXXX)|TIMESTAMP|EVENT_TYPE|[PARAMS]|DETAILS
```

### Key Event Types

| Event | Meaning | Important For |
|-------|---------|---------------|
| `EXECUTION_STARTED` | Transaction begins | Context identification |
| `CODE_UNIT_STARTED` | Method/trigger entry | Call stack tracing |
| `SOQL_EXECUTE_BEGIN` | Query starts | Query analysis |
| `SOQL_EXECUTE_END` | Query ends (includes row count) | Query timing, row count |
| `DML_BEGIN` | DML starts | DML analysis |
| `DML_END` | DML ends | DML timing |
| `EXCEPTION_THROWN` | Exception occurs | Error detection |
| `FATAL_ERROR` | Transaction fails | Critical issues |
| `LIMIT_USAGE` | Limit snapshot | Governor limits |
| `LIMIT_USAGE_FOR_NS` | Per-namespace limits | Managed package isolation |
| `HEAP_ALLOCATE` | Heap allocation | Memory issues |
| `CPU_TIME` | CPU time used | Performance |
| `CALLOUT_EXTERNAL_ENTRY` | Callout starts | External calls |
| `CALLOUT_EXTERNAL_EXIT` | Callout ends | Callout timing |
| `FLOW_START_INTERVIEWS_BEGIN` | Flow execution starts | Flow debugging |
| `FLOW_START_INTERVIEWS_END` | Flow execution ends | Flow timing |
| `VALIDATION_RULE` | Validation rule evaluated | Rule debugging |
| `VALIDATION_FORMULA` | Validation formula result | Formula issues |
| `WF_RULE_EVAL_BEGIN` | Workflow rule evaluation | Workflow debugging |

### Log Categories

Each category controls a different aspect of what gets logged:

| Category | What It Captures |
|----------|-----------------|
| `Apex_code` | Apex execution: method entry/exit, variable assignments, System.debug |
| `Apex_profiling` | Cumulative profiling: SOQL/DML counts, method timing, limit usage |
| `Callout` | HTTP callouts, SOAP calls, external service requests/responses |
| `Database` | DML operations, SOQL queries, query plans, row counts |
| `System` | System methods, namespace loading, Limits class calls |
| `Validation` | Validation rules, formula evaluation, field-level results |
| `Visualforce` | VF page rendering, view state, controller actions |
| `Wave` | Analytics queries, dataset operations |
| `Workflow` | Workflow rules, Process Builder, Flow interviews, field updates |
| `NBA` | Next Best Action strategy execution |

### Log Levels

| Level | Shows | When to Use |
|-------|-------|-------------|
| NONE | Nothing | Disable a category entirely |
| ERROR | Errors only | Production (minimal overhead) |
| WARN | Warnings and errors | Production (low overhead) |
| INFO | General info (default) | General monitoring |
| DEBUG | Detailed debug info | Active debugging |
| FINE | Very detailed | Deep investigation |
| FINER | Method entry/exit | Call stack analysis |
| FINEST | Everything | Last resort (generates huge logs) |

**Recommended Debug Level Presets**:

| Preset | Apex_code | Apex_profiling | Database | System | Use Case |
|--------|-----------|----------------|----------|--------|----------|
| Minimal | ERROR | NONE | ERROR | NONE | Production trace, size-constrained |
| Standard | DEBUG | INFO | INFO | WARN | General sandbox debugging |
| Deep Apex | FINEST | FINE | INFO | DEBUG | Apex logic investigation |
| Query Focus | DEBUG | FINE | FINEST | NONE | SOQL performance analysis |
| Full | FINEST | FINEST | FINEST | FINEST | Last resort (log will be huge/truncated) |

---

## Debug Log Limits and Gotchas

Understanding debug log limits prevents silent data loss and storage issues.

### Hard Limits

| Limit | Value | What Happens When Exceeded |
|-------|-------|---------------------------|
| **Max log size** | 20 MB per log | Log is **truncated** -- end of log is cut off silently |
| **Max logs per user** | 250 logs retained | Oldest logs auto-deleted when new ones arrive |
| **Org-wide log storage** | 1,000 MB (5,000 MB with add-on) | All Trace Flags auto-disabled |
| **Log generation rate** | 1,000 MB in 15 minutes | All Trace Flags auto-disabled org-wide |
| **Trace Flag duration** | Max 24 hours | Must be renewed; defaults to shorter windows |
| **Max active Trace Flags** | 20 per org | Cannot add more until existing ones expire or are deleted |

### Common Gotchas

1. **Truncated logs**: When a log hits 20 MB, the end is silently cut. The `LIMIT_USAGE` section at the bottom (the most useful part) is lost. **Mitigation**: Lower log levels; use targeted categories instead of FINEST on everything.

2. **Log does not capture the issue**: High log levels add overhead that can change timing behavior, masking or altering race conditions. **Mitigation**: Use Event Monitoring for production timing-sensitive issues.

3. **Trace Flag expired**: Trace Flags set in Setup default to 30 minutes in some UIs. The user reports "logs stopped appearing." **Mitigation**: Set explicit ExpirationDate when creating via Tooling API; maximum 24 hours.

4. **Multiple Trace Flags conflict**: If a user-level and class-level Trace Flag overlap, the **highest** level wins per category. This can produce unexpectedly large logs. **Mitigation**: Use only one Trace Flag at a time per entity.

5. **Automated process user**: Flows and Process Builder run as the Automated Process user. You must set a Trace Flag on that user specifically. **Mitigation**: `sf data query --query "SELECT Id, Name FROM User WHERE Name = 'Automated Process'" --target-org [alias]`

6. **Log storage fills up silently**: Once org-wide storage exceeds 1,000 MB, ALL Trace Flags are disabled, including other developers'. **Mitigation**: Schedule regular cleanup: `sf apex log delete --target-org [alias]`

### Trace Flag Management via Tooling API

```bash
# Create a Trace Flag for a specific user (24-hour window)
sf data create record \
  --sobject TraceFlag \
  --values "TracedEntityId='005xx000000000AAA' LogType='USER_DEBUG' DebugLevelId='7dlxx000000000AAA' StartDate='2026-01-15T00:00:00.000Z' ExpirationDate='2026-01-16T00:00:00.000Z'" \
  --target-org my-sandbox \
  --use-tooling-api

# List existing Trace Flags
sf data query \
  --query "SELECT Id, TracedEntityId, LogType, StartDate, ExpirationDate FROM TraceFlag" \
  --target-org my-sandbox \
  --use-tooling-api

# Delete a Trace Flag
sf data delete record \
  --sobject TraceFlag \
  --record-id 7tfxx000000000AAA \
  --target-org my-sandbox \
  --use-tooling-api
```

---

## Query Plan Analysis

### The Correct Approach: REST API Explain Endpoint

> **IMPORTANT**: There is no `--plan` flag on `sf data query`. The query plan feature uses the REST API `explain` parameter.

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

The explain endpoint returns a `plans` array. Each plan object contains:

| Field | Description |
|-------|-------------|
| `cardinality` | Estimated number of rows the query will return |
| `fields` | Fields used by the query filter |
| `leadingOperationType` | How the optimizer accesses data: `Index`, `TableScan`, `Other` |
| `relativeCost` | Cost relative to other plans (lower is better); > 1.0 suggests a table scan |
| `sobjectCardinality` | Total number of records in the object |
| `sobjectType` | Object being queried |
| `notes` | Array of optimizer notes (e.g., "Not considering filter for optimization...") |

### Interpreting Query Plans

| leadingOperationType | relativeCost | Verdict |
|---------------------|--------------|---------|
| `Index` | < 1.0 | Selective -- query is optimized |
| `Index` | > 1.0 | Index exists but not selective enough |
| `TableScan` | any | Full table scan -- needs optimization |
| `Other` | any | Special handling (sharing, polymorphic) |

**Selectivity Rule of Thumb**:
- Standard index: selective if matching rows < 30% of total records AND < 1,000,000 rows
- Custom index: selective if matching rows < 10% of total AND < 333,333 rows
- For objects with < 100,000 records, table scans may still perform acceptably

> **Cross-reference**: Hand off to **sf-soql** skill for rewriting non-selective queries, adding composite filters, or restructuring SOQL for better index utilization.

### Developer Console Query Plan Tool

The Developer Console also provides a built-in Query Plan tool:
1. Open Developer Console
2. Enable: **Help > Preferences > Enable Query Plan** (checkbox)
3. Open Query Editor tab
4. Enter SOQL query and click **Query Plan** button
5. Review the plan output (same fields as REST API explain)

---

## Event Monitoring (Production Debugging)

When debug logs are impractical -- high-traffic production orgs, intermittent issues, security audits, or timing-sensitive bugs -- Event Monitoring provides a non-intrusive alternative.

### What is Event Monitoring?

Event Monitoring captures operational events across your entire org via the **EventLogFile** object. Unlike debug logs:
- No performance overhead on end users
- Captures events for ALL users (not just traced users)
- Retains data for 30 days (or 1 day in Developer Edition)
- No 20 MB truncation limit per event

### Availability

| Edition | Access | Retention |
|---------|--------|-----------|
| Developer Edition | All log types (free) | 1 day |
| Enterprise / Unlimited | Requires Event Monitoring add-on license | 30 days |
| Shield Platform Encryption | Included with Shield | 30 days |

### Key Event Types for Debugging

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

### Querying EventLogFile

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

### Downloading and Analyzing Event Log Files

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

### Real-Time Event Monitoring

For Shield-licensed orgs, Real-Time Events provide streaming event data:

| Real-Time Event | Use Case |
|-----------------|----------|
| `ApiAnomalyEvent` | Detect unusual API access patterns |
| `CredentialStuffingEvent` | Login attack detection |
| `ReportAnomalyEvent` | Unusual report access |
| `SessionHijackingEvent` | Session security |
| `ApexUnexpectedExceptionEvent` | Real-time Apex error alerts |

These are accessed via CometD streaming or Pub/Sub API, not EventLogFile SOQL.

---

## Runtime Limit Instrumentation

### Using the Limits Class

Add instrumentation to Apex code to track governor limit consumption at runtime:

```apex
// Inline debugging: print limit usage at key checkpoints
System.debug(LoggingLevel.WARN, '=== LIMIT CHECK: After Account query ===');
System.debug(LoggingLevel.WARN, 'SOQL Queries: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
System.debug(LoggingLevel.WARN, 'DML Statements: ' + Limits.getDmlStatements() + '/' + Limits.getLimitDmlStatements());
System.debug(LoggingLevel.WARN, 'DML Rows: ' + Limits.getDmlRows() + '/' + Limits.getLimitDmlRows());
System.debug(LoggingLevel.WARN, 'CPU Time: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime() + ' ms');
System.debug(LoggingLevel.WARN, 'Heap Size: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize() + ' bytes');
System.debug(LoggingLevel.WARN, 'Callouts: ' + Limits.getCallouts() + '/' + Limits.getLimitCallouts());
System.debug(LoggingLevel.WARN, 'Query Rows: ' + Limits.getQueryRows() + '/' + Limits.getLimitQueryRows());
```

### Key Limits Class Methods

| Method Pair | What It Tracks | Sync Limit | Async Limit |
|-------------|---------------|------------|-------------|
| `getQueries()` / `getLimitQueries()` | SOQL queries issued | 100 | 200 |
| `getDmlStatements()` / `getLimitDmlStatements()` | DML statements | 150 | 150 |
| `getDmlRows()` / `getLimitDmlRows()` | DML rows processed | 10,000 | 10,000 |
| `getCpuTime()` / `getLimitCpuTime()` | CPU time (ms) | 10,000 | 60,000 |
| `getHeapSize()` / `getLimitHeapSize()` | Heap allocation (bytes) | 6,000,000 | 12,000,000 |
| `getCallouts()` / `getLimitCallouts()` | HTTP/Web service callouts | 100 | 100 |
| `getQueryRows()` / `getLimitQueryRows()` | Total query rows | 50,000 | 50,000 |
| `getFutureCalls()` / `getLimitFutureCalls()` | @future invocations | 50 | 0 (N/A) |
| `getQueueableJobs()` / `getLimitQueueableJobs()` | Queueable jobs enqueued | 50 | 50 |
| `getPublishImmediateDML()` / `getLimitPublishImmediateDML()` | Platform Event publishes | 150 | 150 |

### Reusable Limit Logger Utility

```apex
public class LimitLogger {
    private static final Decimal WARNING_THRESHOLD = 0.80;
    private static final Decimal CRITICAL_THRESHOLD = 0.95;

    public static void checkpoint(String label) {
        List<String> warnings = new List<String>();
        checkLimit(warnings, 'SOQL', Limits.getQueries(), Limits.getLimitQueries());
        checkLimit(warnings, 'DML Stmts', Limits.getDmlStatements(), Limits.getLimitDmlStatements());
        checkLimit(warnings, 'DML Rows', Limits.getDmlRows(), Limits.getLimitDmlRows());
        checkLimit(warnings, 'CPU (ms)', Limits.getCpuTime(), Limits.getLimitCpuTime());
        checkLimit(warnings, 'Heap (bytes)', Limits.getHeapSize(), Limits.getLimitHeapSize());
        checkLimit(warnings, 'Callouts', Limits.getCallouts(), Limits.getLimitCallouts());
        checkLimit(warnings, 'Query Rows', Limits.getQueryRows(), Limits.getLimitQueryRows());

        if (!warnings.isEmpty()) {
            System.debug(LoggingLevel.WARN, '=== LIMIT WARNING [' + label + '] ===');
            for (String w : warnings) {
                System.debug(LoggingLevel.WARN, w);
            }
        }
    }

    private static void checkLimit(List<String> warnings, String name, Integer used, Integer total) {
        if (total == 0) return;
        Decimal pct = (Decimal) used / total;
        if (pct >= CRITICAL_THRESHOLD) {
            warnings.add('CRITICAL ' + name + ': ' + used + '/' + total + ' (' + (pct * 100).setScale(1) + '%)');
        } else if (pct >= WARNING_THRESHOLD) {
            warnings.add('WARNING  ' + name + ': ' + used + '/' + total + ' (' + (pct * 100).setScale(1) + '%)');
        }
    }
}
```

Usage in code:
```apex
LimitLogger.checkpoint('After Account query');
// ... more logic ...
LimitLogger.checkpoint('After Contact DML');
```

---

## Transaction Finalizers (Async Job Debugging)

Transaction Finalizers attach to Queueable jobs and execute regardless of success or failure, making them valuable for debugging async processing.

### Pattern: Capture Queueable Failure Context

```apex
public class MyQueueable implements Queueable {
    public void execute(QueueableContext ctx) {
        // Attach finalizer before any work
        System.attachFinalizer(new MyFinalizer());

        // ... business logic that might fail ...
    }
}

public class MyFinalizer implements Finalizer {
    public void execute(FinalizerContext ctx) {
        String jobId = ctx.getAsyncApexJobId();
        ParentJobResult result = ctx.getResult();

        if (result == ParentJobResult.UNHANDLED_EXCEPTION) {
            String errorMessage = ctx.getException().getMessage();
            System.debug(LoggingLevel.ERROR,
                'Queueable FAILED [' + jobId + ']: ' + errorMessage);

            // Log to custom object for production visibility
            insert new Async_Job_Log__c(
                Job_Id__c = jobId,
                Status__c = 'Failed',
                Error_Message__c = errorMessage.left(32000),
                Timestamp__c = Datetime.now()
            );

            // Optionally re-enqueue (max 5 consecutive retries)
            // System.enqueueJob(new MyQueueable());
        }
    }
}
```

### Finalizer Limits

- A failed Queueable can be re-enqueued up to **5 consecutive times** by its finalizer
- The retry counter resets when a Queueable completes successfully
- Finalizers run in their own execution context (separate governor limits)
- You can enqueue one async job (Queueable, Future, or Batch) from a finalizer

---

## Common Issues & Solutions

### 1. SOQL Query in Loop

**Detection**:
```
|SOQL_EXECUTE_BEGIN|[line 45]
|SOQL_EXECUTE_END|[1 row]
... (repeats 50+ times)
```

**Analysis Output**:
```
CRITICAL: SOQL Query in Loop Detected
   Location: AccountService.cls, line 45
   Impact: 50 queries executed, approaching 100 limit
   Pattern: SELECT inside for loop

RECOMMENDED FIX:
   Move query BEFORE loop, use Map for lookups:

   // Before (problematic)
   for (Account acc : accounts) {
       Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id LIMIT 1];
   }

   // After (bulkified)
   Map<Id, Contact> contactsByAccount = new Map<Id, Contact>();
   for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
       contactsByAccount.put(c.AccountId, c);
   }
   for (Account acc : accounts) {
       Contact c = contactsByAccount.get(acc.Id);
   }
```

### 2. Non-Selective Query

**Detection**:
```
|SOQL_EXECUTE_BEGIN|[line 23]|SELECT Id FROM Lead WHERE Status = 'Open'
|SOQL_EXECUTE_END|[250000 rows queried]
```

**Analysis Output**:
```
WARNING: Non-Selective Query Detected
   Location: LeadService.cls, line 23
   Rows Scanned: 250,000
   Filter Field: Status (not indexed)

RECOMMENDED FIX:
   Option 1: Add indexed field to WHERE clause
   Option 2: Create custom index on Status field (file a Salesforce Support case)
   Option 3: Add LIMIT clause if not all records needed

   // Before
   List<Lead> leads = [SELECT Id FROM Lead WHERE Status = 'Open'];

   // After (with additional selective filter)
   List<Lead> leads = [SELECT Id FROM Lead
                       WHERE Status = 'Open'
                       AND CreatedDate = LAST_N_DAYS:30
                       LIMIT 10000];
```

> **Cross-reference**: Use **sf-soql** skill for deep query optimization, composite index strategies, and SOQL rewriting.

### 3. CPU Time Limit

**Detection**:
```
|LIMIT_USAGE_FOR_NS|CPU_TIME|9500|10000
```

**Analysis Output**:
```
CRITICAL: CPU Time Limit Approaching (95%)
   Used: 9,500 ms
   Limit: 10,000 ms (sync) / 60,000 ms (async)

ANALYSIS:
   Top CPU consumers:
   1. StringUtils.formatAll() - 3,200 ms (line 89)
   2. CalculationService.compute() - 2,800 ms (line 156)
   3. ValidationHelper.validateAll() - 1,500 ms (line 45)

RECOMMENDED FIX:
   1. Move heavy computation to @future or Queueable
   2. Optimize algorithms (O(n^2) -> O(n))
   3. Cache repeated calculations
   4. Use formula fields instead of Apex where possible
   5. Avoid String concatenation in loops (use List<String> + String.join)
```

### 4. Heap Size Limit

**Detection**:
```
|HEAP_ALLOCATE|[5800000]
|LIMIT_USAGE_FOR_NS|HEAP_SIZE|5800000|6000000
```

**Analysis Output**:
```
CRITICAL: Heap Size Limit Approaching (97%)
   Used: 5.8 MB
   Limit: 6 MB (sync) / 12 MB (async)

ANALYSIS:
   Large allocations detected:
   1. Line 34: List<Account> - 2.1 MB (50,000 records)
   2. Line 78: Map<Id, String> - 1.8 MB
   3. Line 112: String concatenation - 1.2 MB

RECOMMENDED FIX:
   1. Use SOQL FOR loops instead of querying all at once
   2. Process in batches of 200 records
   3. Use transient keyword for variables not needed in view state
   4. Clear collections when no longer needed (list.clear())
   5. Select only needed fields (not SELECT *)

   // Before
   List<Account> allAccounts = [SELECT Id, Name FROM Account];

   // After (SOQL FOR loop -- doesn't load all into heap)
   for (Account acc : [SELECT Id, Name FROM Account]) {
       // Process one at a time
   }
```

### 5. Exception Analysis

**Detection**:
```
|EXCEPTION_THROWN|[line 67]|System.NullPointerException: Attempt to de-reference a null object
|FATAL_ERROR|System.NullPointerException: Attempt to de-reference a null object
```

**Analysis Output**:
```
EXCEPTION: System.NullPointerException
   Location: ContactService.cls, line 67
   Message: Attempt to de-reference a null object

STACK TRACE ANALYSIS:
   ContactService.getContactDetails() - line 67
       AccountController.loadData() - line 34
           trigger AccountTrigger - line 5

ROOT CAUSE:
   Variable 'contact' is null when accessing 'contact.Email'
   Likely scenario: Query returned no results

RECOMMENDED FIX:
   // Before
   Contact contact = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contact.Email;  // FAILS if no contact found

   // After (null-safe)
   List<Contact> contacts = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contacts.isEmpty() ? null : contacts[0].Email;

   // Or using safe navigation (API 62.0+)
   Contact contact = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contact?.Email;
```

### 6. Mixed DML Error

**Detection**:
```
|EXCEPTION_THROWN|System.DmlException: MIXED_DML_OPERATION
```

**Analysis Output**:
```
EXCEPTION: System.DmlException - MIXED_DML_OPERATION
   Cannot perform DML on setup and non-setup objects in the same transaction.
   Setup objects: User, PermissionSetAssignment, GroupMember
   Non-setup objects: Account, Contact, Custom__c

RECOMMENDED FIX:
   // Isolate setup DML in a @future method
   @future
   public static void assignPermissionSet(Id userId, Id permSetId) {
       insert new PermissionSetAssignment(
           AssigneeId = userId,
           PermissionSetId = permSetId
       );
   }

   // Or use System.runAs() in tests
   System.runAs(new User(Id = testUser.Id)) {
       // DML on non-setup objects here
   }
```

### 7. Uncommitted Work Pending

**Detection**:
```
|EXCEPTION_THROWN|System.CalloutException: You have uncommitted work pending. Please commit or rollback before calling out.
```

**Analysis Output**:
```
EXCEPTION: System.CalloutException
   DML was performed before an HTTP callout in the same transaction.
   Salesforce requires callouts to happen BEFORE any DML.

RECOMMENDED FIX:
   Option 1: Reorder -- do callouts first, then DML
   Option 2: Move callout to @future(callout=true) method
   Option 3: Use Queueable with AllowsCallouts interface

   public class CalloutQueueable implements Queueable, Database.AllowsCallouts {
       public void execute(QueueableContext ctx) {
           // Callout here, then DML
       }
   }
```

---

## CLI Command Reference

### Log Management

| Command | Purpose |
|---------|---------|
| `sf apex list log` | List available logs (shows log ID, size, user, operation) |
| `sf apex get log` | Download specific log by ID |
| `sf apex tail log` | Stream logs real-time (Ctrl+C to stop) |
| `sf apex log delete` | Delete all logs for the target org |
| `sf apex run --file script.apex` | Execute anonymous Apex (generates debug log) |

### Useful Flags

| Flag | Command | Purpose |
|------|---------|---------|
| `--json` | All commands | Machine-readable output for parsing |
| `--log-id` | `get log` | Specify which log to retrieve |
| `--color` | `tail log` | Colorize log output in terminal |
| `--debug-level` | `tail log` | Set granularity (e.g., FINE, FINEST) |
| `--target-org` | All commands | Specify which org to query |

### Debug Level Control via Tooling API

```bash
# Create a DebugLevel for reuse
sf data create record \
  --sobject DebugLevel \
  --values "DeveloperName='QueryDebug' MasterLabel='Query Debug' ApexCode='DEBUG' ApexProfiling='FINE' Database='FINEST' System='NONE' Validation='NONE' Visualforce='NONE' Workflow='NONE'" \
  --target-org my-sandbox \
  --use-tooling-api
```

---

## Agentic Debug Loop

When enabled, sf-debug will automatically:

1. Fetch debug logs from the failing operation
2. Parse logs and identify all issues
3. Prioritize issues by severity:
   - **Critical**: Limits exceeded, unhandled exceptions, fatal errors
   - **Warning**: Approaching limits (80%+), slow queries (> 500 ms), non-selective queries
   - **Info**: Optimization opportunities, code style, unused queries
4. For each critical issue:
   a. Read the source file at identified line
   b. Generate fix using sf-apex skill
   c. Deploy fix using sf-deploy skill
   d. Re-run operation and check new logs
5. Report final status and remaining warnings

---

## Best Practices (100-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Root Cause** | 25 | Correctly identify the actual cause, not symptoms |
| **Fix Accuracy** | 25 | Suggested fix addresses the root cause |
| **Performance Impact** | 20 | Fix improves performance, doesn't introduce new issues |
| **Completeness** | 15 | All related issues identified, not just the first one |
| **Clarity** | 15 | Explanation is clear and actionable |

**Scoring Thresholds**:

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Excellent | Expert analysis with optimal fix |
| 80-89 | Good | Good analysis, effective fix |
| 70-79 | Acceptable | Acceptable analysis, partial fix |
| 60-69 | Basic | Basic analysis, may miss issues |
| < 60 | Incomplete | Incomplete analysis |

---

## Performance Benchmarks

### Healthy Governor Limits

| Resource | Warning Threshold | Critical Threshold |
|----------|-------------------|-------------------|
| SOQL Queries | 80/100 (80%) | 95/100 (95%) |
| DML Statements | 120/150 (80%) | 145/150 (97%) |
| DML Rows | 8,000/10,000 (80%) | 9,500/10,000 (95%) |
| CPU Time | 8,000/10,000 ms (80%) | 9,500/10,000 ms (95%) |
| Heap Size | 4.8/6 MB (80%) | 5.7/6 MB (95%) |
| Callouts | 80/100 (80%) | 95/100 (95%) |
| Query Rows | 40,000/50,000 (80%) | 47,500/50,000 (95%) |
| Future Calls | 40/50 (80%) | 48/50 (96%) |

### Query Performance

| Category | Acceptable | Needs Optimization |
|----------|------------|-------------------|
| Query Time | < 100 ms | > 500 ms |
| Rows Scanned | < 10,000 | > 100,000 |
| Selectivity | `Index` with relativeCost < 1.0 | `TableScan` at any cost |
| Result Set | < 2,000 rows | > 10,000 rows |

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| **sf-apex** | Generate fixes for identified issues | `Skill(skill="sf-apex", args="Fix NullPointerException in ContactService line 67")` |
| **sf-soql** | Optimize non-selective queries, rewrite SOQL | `Skill(skill="sf-soql", args="Optimize query: SELECT Id FROM Lead WHERE Status = 'Open'")` |
| **sf-testing** | Run tests to reproduce issues | `Skill(skill="sf-testing", args="Run AccountServiceTest to generate debug logs")` |
| **sf-deploy** | Deploy fixes | `Skill(skill="sf-deploy", args="Deploy ContactService.cls to sandbox")` |
| **sf-data** | Create test data for debugging | `Skill(skill="sf-data", args="Create Account with specific conditions")` |
| **sf-flow** | Debug Flow-related issues | `Skill(skill="sf-flow", args="Analyze Flow interview failures in debug log")` |

---

## Documentation

| Document | Description |
|----------|-------------|
| [debug-log-reference.md](docs/debug-log-reference.md) | Complete debug log event reference |
| [cli-commands.md](docs/cli-commands.md) | SF CLI debugging commands |
| [benchmarking-guide.md](docs/benchmarking-guide.md) | Dan Appleman's technique, real-world benchmarks |
| [log-analysis-tools.md](docs/log-analysis-tools.md) | Apex Log Analyzer, manual analysis patterns |

## Templates

| Template | Description |
|----------|-------------|
| [cpu-heap-optimization.cls](templates/cpu-heap-optimization.cls) | CPU and heap optimization patterns |
| [benchmarking-template.cls](templates/benchmarking-template.cls) | Ready-to-run benchmark comparisons |
| [soql-in-loop-fix.cls](templates/soql-in-loop-fix.cls) | SOQL bulkification pattern |
| [dml-in-loop-fix.cls](templates/dml-in-loop-fix.cls) | DML bulkification pattern |
| [null-pointer-fix.cls](templates/null-pointer-fix.cls) | Null-safe patterns |

---

## Sources

- [Debug Log | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_debugging_debug_log.htm)
- [Debug Log Levels | Salesforce Help](https://help.salesforce.com/s/articleView?id=sf.code_setting_debug_log_levels.htm&language=en_US&type=5)
- [Get Feedback on Query Performance | REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query_explain.htm)
- [Developer Console Query Plan Tool FAQ](https://help.salesforce.com/s/articleView?id=000386864&language=en_US&type=1)
- [Execution Governors and Limits | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [Limits Class | Apex Reference Guide](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_methods_system_limits.htm)
- [EventLogFile | Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_eventlogfile.htm)
- [Event Monitoring Overview | Trailhead](https://trailhead.salesforce.com/content/learn/modules/event_monitoring/event_monitoring_intro)
- [Query Event Log Files | Trailhead](https://trailhead.salesforce.com/content/learn/modules/event_monitoring/event_monitoring_query)
- [An Architect's Guide to Event Monitoring](https://www.salesforce.com/blog/architect-guide-event-monitoring/)
- [Transaction Finalizers | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_transaction_finalizers.htm)
- [Best Practices to Resolve Heap Size Error](https://help.salesforce.com/s/articleView?id=000395030&language=en_US&type=1)
- [Apex CPU Time Limit Exceeded | Salesforce Ben](https://www.salesforceben.com/what-is-apex-cpu-time-limit-exceeded-how-do-you-solve-it/)
- [Salesforce Developer Limits Quick Reference (PDF)](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_app_limits_cheatsheet.pdf)
- [Using Event Monitoring | REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/using_resources_event_log_files.htm)
- [Tooling API Reference v66.0](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_tooling.pdf)

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex (for auto-fix), sf-soql (for query optimization), sf-testing (for reproduction), sf-deploy (for deploying fixes)

Install: `/plugin install github:Jaganpro/sf-skills/sf-debug`

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
