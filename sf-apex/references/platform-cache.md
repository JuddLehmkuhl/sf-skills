# Platform Cache - Full Patterns

> Extracted from sf-apex SKILL.md for progressive disclosure.
> Return to [SKILL.md](../SKILL.md) for the workflow and scoring.

---

## Org Cache Pattern (Shared Across All Users)

```apex
public with sharing class CacheManager {

    private static final String PARTITION_NAME = 'local.AppCache';

    /**
     * @description Retrieve a cached value with automatic cache-miss handling.
     *              Returns null if partition is unavailable.
     */
    public static Object get(String key) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            return partition.get(key);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache miss or unavailable: ' + e.getMessage());
            return null;
        }
    }

    /**
     * @description Store a value in org cache with TTL (seconds).
     */
    public static void put(String key, Object value, Integer ttlSeconds) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            partition.put(key, value, ttlSeconds);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache put failed: ' + e.getMessage());
        }
    }

    /**
     * @description Remove a cached value.
     */
    public static void remove(String key) {
        try {
            Cache.OrgPartition partition = Cache.Org.getPartition(PARTITION_NAME);
            partition.remove(key);
        } catch (Cache.Org.OrgCacheException e) {
            System.debug(LoggingLevel.WARN, 'Cache remove failed: ' + e.getMessage());
        }
    }
}
```

---

## CacheBuilder Pattern (Recommended)

```apex
public class ActiveUsersCacheBuilder implements Cache.CacheBuilder {

    /**
     * @description Called automatically when the cache key is missing.
     *              Return value is cached with the partition's default TTL.
     */
    public Object doLoad(String key) {
        return [
            SELECT Id, Name, Email, Profile.Name
            FROM User
            WHERE IsActive = true
            WITH USER_MODE
        ];
    }
}
```

**Usage**:
```apex
// First call: executes SOQL, caches result
// Subsequent calls: returns cached data (no SOQL)
List<User> activeUsers = (List<User>) Cache.Org.get(
    ActiveUsersCacheBuilder.class,
    'AllActiveUsers'
);
```

---

## Best Practices

- Always handle `Cache.Org.OrgCacheException` -- cache may be unavailable or partition at capacity
- Use Org Cache for data shared across users; Session Cache for user-specific data
- Cache a few large items rather than many small items to reduce overhead
- Set appropriate TTL; default is 8 hours for Org Cache
- Invalidate cache when underlying data changes (`remove()` or overwrite with `put()`)
- Cache partition must be created in Setup > Platform Cache before use
- Minimum 10 KB cache available; check with `Cache.Org.getCapacity()`
- Do NOT cache sensitive data (PII, credentials) unless encrypted
