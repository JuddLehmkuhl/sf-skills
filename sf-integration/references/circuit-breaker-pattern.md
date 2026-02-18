# Circuit Breaker Pattern

Prevent cascading failures when an external API is down. Uses **Platform Cache** to track failure counts and trip the circuit.

## Circuit Breaker with Platform Cache

```apex
public with sharing class CircuitBreaker {

    // States: CLOSED (normal), OPEN (blocking), HALF_OPEN (testing)
    private static final Integer FAILURE_THRESHOLD = 5;
    private static final Integer OPEN_DURATION_SECONDS = 300; // 5 minutes
    private static final String CACHE_PARTITION = 'local.IntegrationCache';

    /**
     * Check if circuit is open (should block calls)
     */
    public static Boolean isOpen(String serviceName) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(CACHE_PARTITION);
            String state = (String) partition.get(serviceName + '_state');

            if (state == 'OPEN') {
                Long openedAt = (Long) partition.get(serviceName + '_openedAt');
                Long now = Datetime.now().getTime();

                // Check if open duration has elapsed -> move to HALF_OPEN
                if (now - openedAt > OPEN_DURATION_SECONDS * 1000) {
                    partition.put(serviceName + '_state', 'HALF_OPEN');
                    return false; // Allow one test request
                }
                return true; // Still open, block call
            }

            return false; // CLOSED or HALF_OPEN -> allow call
        } catch (Exception e) {
            // If cache unavailable, fail open (allow calls)
            return false;
        }
    }

    /**
     * Record a successful call (reset failure count)
     */
    public static void recordSuccess(String serviceName) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(CACHE_PARTITION);
            partition.put(serviceName + '_failures', 0);
            partition.put(serviceName + '_state', 'CLOSED');
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'Circuit breaker cache error: ' + e.getMessage());
        }
    }

    /**
     * Record a failed call (increment counter, possibly trip breaker)
     */
    public static void recordFailure(String serviceName) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(CACHE_PARTITION);
            Integer failures = (Integer) partition.get(serviceName + '_failures');
            failures = (failures == null) ? 1 : failures + 1;
            partition.put(serviceName + '_failures', failures);

            if (failures >= FAILURE_THRESHOLD) {
                partition.put(serviceName + '_state', 'OPEN');
                partition.put(serviceName + '_openedAt', Datetime.now().getTime());
                System.debug(LoggingLevel.ERROR,
                    'Circuit OPEN for ' + serviceName + ' after ' + failures + ' failures');
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'Circuit breaker cache error: ' + e.getMessage());
        }
    }
}
```

## Using the Circuit Breaker

```apex
public class ResilientCalloutService {

    public static HttpResponse callWithCircuitBreaker(
        String serviceName, HttpRequest request
    ) {
        // Check circuit state
        if (CircuitBreaker.isOpen(serviceName)) {
            throw new CircuitOpenException(
                'Circuit breaker OPEN for ' + serviceName + '. Try again later.');
        }

        try {
            Http http = new Http();
            HttpResponse res = http.send(request);

            if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                CircuitBreaker.recordSuccess(serviceName);
            } else if (res.getStatusCode() >= 500) {
                CircuitBreaker.recordFailure(serviceName);
            }

            return res;
        } catch (CalloutException e) {
            CircuitBreaker.recordFailure(serviceName);
            throw e;
        }
    }

    public class CircuitOpenException extends Exception {}
}
```

**Prerequisites**: Create an Org Cache partition named `IntegrationCache`:
- Setup -> Platform Cache -> New Platform Cache Partition
- Name: `IntegrationCache`, Org cache allocation: 1 MB minimum
