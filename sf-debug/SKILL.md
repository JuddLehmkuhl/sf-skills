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

## Debugging Tool Decision Framework

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

> **Cross-reference**: For SOQL query optimization after identifying slow queries, use the **sf-soql** skill.

---

## Workflow (5-Phase Pattern)

### Phase 1: Log Collection

Gather from the user:
- Debug context (deployment failure, test failure, runtime error, performance issue)
- Target org alias
- User/Transaction ID if known
- Time range and environment (sandbox vs. production -- determines tooling approach)

### Phase 2: Log Retrieval

```bash
sf apex list log --target-org [alias] --json        # List recent logs
sf apex get log --log-id 07Lxx0000000000 --target-org [alias]  # Get specific log
sf apex tail log --target-org [alias] --color        # Tail real-time
sf apex log delete --target-org [alias]              # Delete old logs (free storage)
```

### Phase 3: Log Analysis

Parse the debug log across these dimensions:

1. **Execution Overview** -- Transaction type, total execution time, entry point
2. **Governor Limit Analysis** -- SOQL (X/100), DML Stmts (X/150), DML Rows (X/10K), CPU (X/10K ms), Heap (X/6MB), Callouts (X/100)
3. **Performance Hotspots** -- Slowest SOQL queries, non-selective queries, expensive operations, callout timing
4. **Exceptions and Errors** -- Exception type, stack trace, line number, root cause
5. **Recommendations** -- Immediate fixes, optimization suggestions, architecture improvements

### Phase 4: Issue Identification & Fix Suggestions

**Governor Limit Decision Tree**:

| Issue | Detection Pattern | Fix Strategy |
|-------|-------------------|--------------|
| SOQL in Loop | `SOQL_EXECUTE_BEGIN` repeated in `METHOD_ENTRY` | Query before loop, Map for lookups |
| DML in Loop | `DML_BEGIN` repeated in `METHOD_ENTRY` | Collect in List, single DML after loop |
| Non-Selective Query | REST API explain shows `TableScan` | Add indexed filter or LIMIT; see **sf-soql** |
| CPU Limit | `CPU_TIME` approaching 10000 | Optimize algorithms, use async |
| Heap Limit | `HEAP_ALLOCATE` approaching 6 MB | Reduce collection sizes, SOQL FOR loops |
| Callout Limit | `CALLOUT_EXTERNAL_ENTRY` count > 90 | Batch callouts, use Queueable |
| Row Limit | `DML_ROWS` approaching 10000 | Batch processing, Database.Stateful |
| Query Rows | `SOQL_ROWS` approaching 50000 | Add WHERE filters, use Batch Apex |

**Auto-Fix**: `Skill(skill="sf-apex", args="Fix [issue type] in [ClassName] at line [lineNumber]")`

### Phase 5: Fix Implementation

1. Generate fix via sf-apex skill
2. Deploy via sf-deploy skill
3. Verify by re-running and checking logs
4. Report results

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
| `SOQL_EXECUTE_END` | Query ends (includes row count) | Query timing |
| `DML_BEGIN` / `DML_END` | DML operation | DML analysis/timing |
| `EXCEPTION_THROWN` | Exception occurs | Error detection |
| `FATAL_ERROR` | Transaction fails | Critical issues |
| `LIMIT_USAGE` | Limit snapshot | Governor limits |
| `LIMIT_USAGE_FOR_NS` | Per-namespace limits | Managed package isolation |
| `HEAP_ALLOCATE` | Heap allocation | Memory issues |
| `CPU_TIME` | CPU time used | Performance |
| `CALLOUT_EXTERNAL_ENTRY/EXIT` | Callout start/end | External calls/timing |
| `FLOW_START_INTERVIEWS_BEGIN/END` | Flow execution | Flow debugging/timing |
| `VALIDATION_RULE` / `VALIDATION_FORMULA` | Validation evaluated | Rule/formula debugging |

### Log Categories

| Category | What It Captures |
|----------|-----------------|
| `Apex_code` | Apex execution: method entry/exit, variable assignments, System.debug |
| `Apex_profiling` | Cumulative profiling: SOQL/DML counts, method timing, limit usage |
| `Callout` | HTTP callouts, SOAP calls, external service requests/responses |
| `Database` | DML operations, SOQL queries, query plans, row counts |
| `System` | System methods, namespace loading, Limits class calls |
| `Validation` | Validation rules, formula evaluation, field-level results |
| `Visualforce` | VF page rendering, view state, controller actions |
| `Workflow` | Workflow rules, Process Builder, Flow interviews, field updates |

### Log Levels

| Level | When to Use |
|-------|-------------|
| NONE | Disable a category entirely |
| ERROR | Production (minimal overhead) |
| WARN | Production (low overhead) |
| INFO | General monitoring (default) |
| DEBUG | Active debugging |
| FINE | Deep investigation |
| FINER | Call stack analysis |
| FINEST | Last resort (huge logs) |

### Recommended Debug Level Presets

| Preset | Apex_code | Apex_profiling | Database | System | Use Case |
|--------|-----------|----------------|----------|--------|----------|
| Minimal | ERROR | NONE | ERROR | NONE | Production trace, size-constrained |
| Standard | DEBUG | INFO | INFO | WARN | General sandbox debugging |
| Deep Apex | FINEST | FINE | INFO | DEBUG | Apex logic investigation |
| Query Focus | DEBUG | FINE | FINEST | NONE | SOQL performance analysis |
| Full | FINEST | FINEST | FINEST | FINEST | Last resort (log will be huge/truncated) |

---

## Debug Log Limits and Gotchas

### Hard Limits

| Limit | Value | What Happens When Exceeded |
|-------|-------|---------------------------|
| Max log size | 20 MB per log | Log **truncated** -- end cut off silently |
| Max logs per user | 250 retained | Oldest auto-deleted |
| Org-wide log storage | 1,000 MB | All Trace Flags auto-disabled |
| Log generation rate | 1,000 MB in 15 min | All Trace Flags auto-disabled org-wide |
| Trace Flag duration | Max 24 hours | Must be renewed |
| Max active Trace Flags | 20 per org | Cannot add more until existing expire/deleted |

### Common Gotchas

1. **Truncated logs**: 20 MB limit cuts the end silently -- `LIMIT_USAGE` section (most useful part) is lost. Lower log levels; use targeted categories.
2. **Timing changes**: High log levels add overhead that can mask race conditions. Use Event Monitoring for timing-sensitive production issues.
3. **Trace Flag expired**: Defaults to 30 min in some UIs. Set explicit ExpirationDate via Tooling API (max 24 hrs).
4. **Multiple Trace Flags conflict**: Overlapping user-level + class-level flags use highest level per category, producing unexpectedly large logs.
5. **Automated Process user**: Flows/Process Builder run as Automated Process user. Set Trace Flag on that user specifically.
6. **Log storage fills silently**: Exceeding 1,000 MB disables ALL Trace Flags. Schedule cleanup: `sf apex log delete`.

### Trace Flag Management via Tooling API

```bash
# Create Trace Flag (24-hour window)
sf data create record --sobject TraceFlag \
  --values "TracedEntityId='005xx...' LogType='USER_DEBUG' DebugLevelId='7dlxx...' StartDate='2026-01-15T00:00:00.000Z' ExpirationDate='2026-01-16T00:00:00.000Z'" \
  --target-org my-sandbox --use-tooling-api

# List existing Trace Flags
sf data query --query "SELECT Id, TracedEntityId, LogType, StartDate, ExpirationDate FROM TraceFlag" \
  --target-org my-sandbox --use-tooling-api

# Delete a Trace Flag
sf data delete record --sobject TraceFlag --record-id 7tfxx... --target-org my-sandbox --use-tooling-api
```

---

## Query Plan Analysis

**Interpreting query plans** (via REST API explain endpoint or Developer Console):

| leadingOperationType | relativeCost | Verdict |
|---------------------|--------------|---------|
| `Index` | < 1.0 | Selective -- query is optimized |
| `Index` | > 1.0 | Index exists but not selective enough |
| `TableScan` | any | Full table scan -- needs optimization |
| `Other` | any | Special handling (sharing, polymorphic) |

> Full query plan examples, REST API explain endpoint usage, and Developer Console setup: see [references/query-plan-analysis.md](references/query-plan-analysis.md)

---

## Event Monitoring (Production Debugging)

Use Event Monitoring via **EventLogFile** when debug logs are impractical (high-traffic prod, intermittent issues, timing-sensitive bugs). No performance overhead, captures all users, 30-day retention.

Key event types: `ApexExecution`, `ApexUnexpectedException`, `API`, `ApexTrigger`, `FlowExecution`, `BulkApi`.

> Full EventLogFile queries, download patterns, real-time events, and availability matrix: see [references/event-monitoring.md](references/event-monitoring.md)

---

## Runtime Limit Instrumentation

Use the `Limits` class to track governor limit consumption at runtime. Key methods: `getQueries()`, `getDmlStatements()`, `getCpuTime()`, `getHeapSize()`, `getCallouts()`, `getQueryRows()`.

> Full Limits class method table, inline debug snippet, and reusable LimitLogger utility: see [references/runtime-limit-instrumentation.md](references/runtime-limit-instrumentation.md)

---

## Transaction Finalizers (Async Job Debugging)

Attach to Queueable jobs via `System.attachFinalizer()`. Execute regardless of success/failure. Failed Queueable can be re-enqueued up to 5 consecutive times.

> Full pattern with code example and finalizer limits: see [references/transaction-finalizers.md](references/transaction-finalizers.md)

---

## Common Issues & Solutions

| Issue | Detection Pattern | Fix Summary |
|-------|-------------------|-------------|
| SOQL in Loop | `SOQL_EXECUTE_BEGIN` repeating 50+ times | Query before loop, Map for lookups |
| Non-Selective Query | 250K+ rows queried, no indexed filter | Add indexed WHERE filter, LIMIT; use **sf-soql** |
| CPU Time Limit | `CPU_TIME` > 9500/10000 | Move to async, optimize O(n^2), cache calculations |
| Heap Size Limit | `HEAP_ALLOCATE` > 5.8MB/6MB | SOQL FOR loops, batch processing, clear collections |
| NullPointerException | `EXCEPTION_THROWN` on dereferenced null | Null-safe queries (`List.isEmpty()`), safe navigation `?.` |
| Mixed DML | `MIXED_DML_OPERATION` | Isolate setup DML in `@future` or `System.runAs()` in tests |
| Uncommitted Work | Callout after DML in same transaction | Reorder (callouts first), or use Queueable with AllowsCallouts |

> Full detection examples, analysis output, and fix code for all 7 issues: see [references/common-issues-fixes.md](references/common-issues-fixes.md)

---

## CLI Quick Reference

| Command | Purpose |
|---------|---------|
| `sf apex list log` | List available logs |
| `sf apex get log --log-id ID` | Download specific log |
| `sf apex tail log --color` | Stream logs real-time |
| `sf apex log delete` | Delete all logs for org |
| `sf apex run --file script.apex` | Execute anonymous Apex (generates log) |

| Flag | Command | Purpose |
|------|---------|---------|
| `--json` | All | Machine-readable output |
| `--log-id` | `get log` | Specify log to retrieve |
| `--color` | `tail log` | Colorize terminal output |
| `--debug-level` | `tail log` | Set granularity (FINE, FINEST) |
| `--target-org` | All | Specify org |

```bash
# Create a reusable DebugLevel via Tooling API
sf data create record --sobject DebugLevel \
  --values "DeveloperName='QueryDebug' MasterLabel='Query Debug' ApexCode='DEBUG' ApexProfiling='FINE' Database='FINEST' System='NONE' Validation='NONE' Visualforce='NONE' Workflow='NONE'" \
  --target-org my-sandbox --use-tooling-api
```

---

## Agentic Debug Loop

When enabled, sf-debug automatically:

1. Fetch debug logs from the failing operation
2. Parse and identify all issues
3. Prioritize: **Critical** (limits exceeded, fatal errors) > **Warning** (80%+ limits, slow queries) > **Info** (optimization opportunities)
4. For each critical issue: read source -> generate fix (sf-apex) -> deploy (sf-deploy) -> verify logs
5. Report final status and remaining warnings

---

## Performance Benchmarks

### Governor Limit Thresholds

| Resource | Warning (80%) | Critical (95%) |
|----------|--------------|----------------|
| SOQL Queries | 80/100 | 95/100 |
| DML Statements | 120/150 | 145/150 |
| DML Rows | 8,000/10,000 | 9,500/10,000 |
| CPU Time | 8,000/10,000 ms | 9,500/10,000 ms |
| Heap Size | 4.8/6 MB | 5.7/6 MB |
| Callouts | 80/100 | 95/100 |
| Query Rows | 40,000/50,000 | 47,500/50,000 |

### Query Performance

| Category | Acceptable | Needs Optimization |
|----------|------------|-------------------|
| Query Time | < 100 ms | > 500 ms |
| Rows Scanned | < 10,000 | > 100,000 |
| Selectivity | `Index` relativeCost < 1.0 | `TableScan` at any cost |
| Result Set | < 2,000 rows | > 10,000 rows |

---

## Scoring (100 Points)

| Category | Points | Key Rules |
|----------|--------|-----------|
| Root Cause | 25 | Correctly identify actual cause, not symptoms |
| Fix Accuracy | 25 | Fix addresses root cause |
| Performance Impact | 20 | Fix improves performance, no new issues |
| Completeness | 15 | All related issues identified |
| Clarity | 15 | Explanation is clear and actionable |

---

## Cross-Skill Integration

| Skill | When to Use |
|-------|-------------|
| **sf-apex** | Generate fixes for identified issues |
| **sf-soql** | Optimize non-selective queries, rewrite SOQL |
| **sf-testing** | Run tests to reproduce issues |
| **sf-deploy** | Deploy fixes |
| **sf-data** | Create test data for debugging |
| **sf-flow** | Debug Flow-related issues |

---

## Documentation & Templates

| Document | Description |
|----------|-------------|
| [debug-log-reference.md](docs/debug-log-reference.md) | Complete debug log event reference |
| [cli-commands.md](docs/cli-commands.md) | SF CLI debugging commands |
| [benchmarking-guide.md](docs/benchmarking-guide.md) | Dan Appleman's technique, real-world benchmarks |
| [log-analysis-tools.md](docs/log-analysis-tools.md) | Apex Log Analyzer, manual analysis patterns |

| Template | Description |
|----------|-------------|
| [cpu-heap-optimization.cls](templates/cpu-heap-optimization.cls) | CPU and heap optimization patterns |
| [benchmarking-template.cls](templates/benchmarking-template.cls) | Ready-to-run benchmark comparisons |
| [soql-in-loop-fix.cls](templates/soql-in-loop-fix.cls) | SOQL bulkification pattern |
| [dml-in-loop-fix.cls](templates/dml-in-loop-fix.cls) | DML bulkification pattern |
| [null-pointer-fix.cls](templates/null-pointer-fix.cls) | Null-safe patterns |

## Sources

- [Debug Log | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_debugging_debug_log.htm)
- [Debug Log Levels | Salesforce Help](https://help.salesforce.com/s/articleView?id=sf.code_setting_debug_log_levels.htm&language=en_US&type=5)
- [Get Feedback on Query Performance | REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query_explain.htm)
- [Execution Governors and Limits | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [Limits Class | Apex Reference Guide](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_methods_system_limits.htm)
- [EventLogFile | Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_eventlogfile.htm)
- [Transaction Finalizers | Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_transaction_finalizers.htm)
- [Salesforce Developer Limits Quick Reference (PDF)](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_app_limits_cheatsheet.pdf)

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex (auto-fix), sf-soql (query optimization), sf-testing (reproduction), sf-deploy (deploying fixes)

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
