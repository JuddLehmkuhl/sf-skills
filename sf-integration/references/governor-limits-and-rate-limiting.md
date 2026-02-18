# Governor Limits & Rate Limiting

## Callout Limits by Execution Context

| Context | Max Callouts | Max Timeout (each) | Max Concurrent Long-Running | Notes |
|---------|-------------|--------------------|-----------------------------|-------|
| **Synchronous Apex** | 100 | 120s | 10 per org | Blocks user thread |
| **@future** | 100 | 120s | 50 per org (shared) | Fire-and-forget |
| **Queueable** | 100 | 120s | 50 per org (shared) | Chainable, stateful |
| **Batch Apex** | 100 per `execute()` | 120s | 50 per org (shared) | Each batch invocation is separate transaction |
| **Scheduled Apex** | 100 | 120s | 50 per org (shared) | Runs as scheduled user |
| **Platform Event Trigger** | 100 | 120s | N/A | Avoid callouts; use Queueable |
| **Flow (HTTP Callout)** | 100 per transaction | 120s | N/A | Counts against same transaction limits |

## Concurrent Long-Running Apex Limit

The **Concurrent Long-Running Apex Limit** is the most common cause of integration failures at scale:

- Default: 10 concurrent requests holding connections > 5 seconds
- When exceeded: `System.LimitException: Apex concurrent request limit exceeded`
- Applies to synchronous callouts that take more than 5 seconds

**Mitigation strategies**:
1. **Reduce timeout**: Set `req.setTimeout()` to the minimum acceptable value (not always 120s)
2. **Go async**: Move callouts to Queueable/Future to use the async limit (50 vs 10)
3. **Batch and consolidate**: Combine multiple API calls into single bulk requests
4. **Circuit breaker**: Stop calling failing endpoints immediately (see [circuit-breaker-pattern.md](circuit-breaker-pattern.md))

## Rate Limiting Best Practices

```
External API rate limits        Salesforce governor limits
        |                              |
1. Know your API's rate limits (requests/min, /hour, /day)
2. Track usage via Custom Metadata or Platform Cache
3. Throttle with Queueable chains (natural pacing)
4. Handle 429 responses: check Retry-After header
5. Use Batch Apex for bulk operations (scope parameter)
6. Monitor with Integration_Log__c custom object
```

**Handling 429 (Too Many Requests)**:
```apex
if (res.getStatusCode() == 429) {
    String retryAfter = res.getHeader('Retry-After');
    Integer waitSeconds = String.isNotBlank(retryAfter)
        ? Integer.valueOf(retryAfter) : 60;

    // Schedule retry after the specified wait period
    // Use Queueable chain or Scheduled Apex
    System.debug(LoggingLevel.WARN,
        'Rate limited. Retry after ' + waitSeconds + ' seconds');
}
```
