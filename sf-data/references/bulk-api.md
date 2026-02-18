# Bulk API 2.0 Details

> Referenced from `SKILL.md` -- Bulk API section

---

## Key Limits

| Limit | Value |
|-------|-------|
| Max records per batch | 10,000 |
| Max payload per batch | 10 MB |
| Batch submissions per 24h | 15,000 (shared Bulk API 1.0 + 2.0) |
| Max records per day (ingest) | 150,000,000 |
| CPU time per batch | 60,000 ms |
| Concurrent ingest jobs | 100 |

## CSV Requirements

```csv
Name,Industry,Type,BillingCity
"Test Account 1","Technology","Prospect","San Francisco"
"Test Account 2","Finance","Customer","New York"
```

- **Encoding**: UTF-8 (no BOM)
- **Line endings**: LF (not CRLF)
- **Header row**: Required, must match API field names exactly
- **Quoting**: Double-quote fields containing commas, newlines, or quotes
- **Null values**: Use `#N/A` to set a field to null

## Sources

- [Bulk API 2.0 Limits and Allocations](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm)
- [Bulk API 2.0 Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm)
