# Runtime Limit Instrumentation

> Parent: [SKILL.md](../SKILL.md) -- Runtime Limit Instrumentation section

## Using the Limits Class

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

## Key Limits Class Methods

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

## Reusable Limit Logger Utility

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
