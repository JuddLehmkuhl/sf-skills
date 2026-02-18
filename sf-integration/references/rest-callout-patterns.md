# REST Callout Patterns

## Synchronous REST Callout

**Use Case**: Need immediate response, NOT triggered from DML

**Template**: `templates/callouts/rest-sync-callout.cls`

```apex
public with sharing class {{ServiceName}}Callout {

    private static final String NAMED_CREDENTIAL = 'callout:{{NamedCredentialName}}';

    public static HttpResponse makeRequest(String method, String endpoint, String body) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(NAMED_CREDENTIAL + endpoint);
        req.setMethod(method);
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000); // 120 seconds max

        if (String.isNotBlank(body)) {
            req.setBody(body);
        }

        Http http = new Http();
        return http.send(req);
    }

    public static Map<String, Object> get(String endpoint) {
        HttpResponse res = makeRequest('GET', endpoint, null);
        return handleResponse(res);
    }

    public static Map<String, Object> post(String endpoint, Map<String, Object> payload) {
        HttpResponse res = makeRequest('POST', endpoint, JSON.serialize(payload));
        return handleResponse(res);
    }

    private static Map<String, Object> handleResponse(HttpResponse res) {
        Integer statusCode = res.getStatusCode();

        if (statusCode >= 200 && statusCode < 300) {
            return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        } else if (statusCode >= 400 && statusCode < 500) {
            throw new CalloutException('Client Error: ' + statusCode + ' - ' + res.getBody());
        } else if (statusCode >= 500) {
            throw new CalloutException('Server Error: ' + statusCode + ' - ' + res.getBody());
        }

        return null;
    }
}
```

## Asynchronous REST Callout (Queueable)

**Use Case**: Callouts triggered from DML (triggers, Process Builder)

**Template**: `templates/callouts/rest-queueable-callout.cls`

See template file for full implementation. Key points:
- Implements `Queueable, Database.AllowsCallouts`
- Accepts `List<Id>` for record context
- Queries records and makes callouts in `execute()`
- Handles errors with logging

## Retry Handler (Queueable Chain Pattern)

**IMPORTANT**: Apex has no `Thread.sleep()`. Inline retry loops execute immediately with zero delay between attempts. For actual timed backoff, use the Queueable Chain pattern below, which enqueues a new job for each retry attempt. The async queue provides natural delay (typically seconds to minutes depending on load).

**Template**: `templates/callouts/callout-retry-handler.cls`

```apex
/**
 * Queueable-based retry: Each retry is a separate async transaction.
 * The async queue provides natural delay between attempts.
 * For longer delays, chain through Scheduled Apex (see below).
 */
public with sharing class RetryableCalloutJob implements Queueable, Database.AllowsCallouts {

    private final HttpRequest request;
    private final Integer retryCount;
    private final Integer maxRetries;
    private final String callbackRecordId;

    private static final Set<Integer> RETRYABLE_CODES = new Set<Integer>{
        408, 429, 500, 502, 503, 504
    };

    public RetryableCalloutJob(HttpRequest request, String callbackRecordId) {
        this(request, callbackRecordId, 0, 3);
    }

    public RetryableCalloutJob(
        HttpRequest request, String callbackRecordId,
        Integer retryCount, Integer maxRetries
    ) {
        this.request = request;
        this.callbackRecordId = callbackRecordId;
        this.retryCount = retryCount;
        this.maxRetries = maxRetries;
    }

    public void execute(QueueableContext context) {
        try {
            Http http = new Http();
            HttpResponse res = http.send(request);

            if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                handleSuccess(res);
                return;
            }

            if (RETRYABLE_CODES.contains(res.getStatusCode()) && retryCount < maxRetries) {
                enqueueRetry();
                return;
            }

            handleFinalFailure(res.getStatusCode(), res.getBody());

        } catch (CalloutException e) {
            if (retryCount < maxRetries) {
                enqueueRetry();
            } else {
                handleFinalFailure(null, e.getMessage());
            }
        }
    }

    private void enqueueRetry() {
        System.debug(LoggingLevel.WARN,
            'Retrying callout, attempt ' + (retryCount + 1) + ' of ' + maxRetries);

        // Each re-enqueue goes back into the async queue,
        // providing natural delay between attempts
        System.enqueueJob(new RetryableCalloutJob(
            request, callbackRecordId, retryCount + 1, maxRetries
        ));
    }

    private void handleSuccess(HttpResponse res) {
        // Update record with success status
        System.debug(LoggingLevel.INFO, 'Callout succeeded');
    }

    private void handleFinalFailure(Integer statusCode, String message) {
        // Log to Integration_Log__c, send notification, etc.
        System.debug(LoggingLevel.ERROR,
            'Callout failed after ' + retryCount + ' retries: ' + message);
    }
}
```

**For longer delays (e.g., 5+ minutes)**: Use Scheduled Apex to schedule the retry:

```apex
// Schedule a retry in N minutes using System.schedule()
Integer delayMinutes = (Integer) Math.pow(2, retryCount); // 1, 2, 4 min
String cronExp = buildCronForMinutesFromNow(delayMinutes);
System.schedule('Retry-' + callbackRecordId + '-' + retryCount,
    cronExp, new ScheduledRetryJob(request, callbackRecordId, retryCount + 1));
```

## Retry Strategy Comparison

| Strategy | Delay | Use When | Limitation |
|----------|-------|----------|------------|
| **Inline loop** (same transaction) | None (immediate) | Transient blips, fast recovery expected | No actual delay; counts against 100-callout limit |
| **Queueable chain** | Seconds-to-minutes (queue latency) | Most retry scenarios | Queue depth limit (50 chained in dev, varies in prod) |
| **Scheduled Apex** | Configurable (minutes-to-hours) | Rate-limited APIs, long outages | Minimum 1-minute granularity; limited scheduled jobs |
| **Platform Event retry** | Built-in with `EventBus.RetryableException` | Event subscriber triggers only | Max 9 retries; increasing backoff managed by platform |
