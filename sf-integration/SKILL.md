---
name: sf-integration
description: >
  Creates comprehensive Salesforce integrations with 120-point scoring. Use when
  setting up Named Credentials, External Services, REST/SOAP callouts, Platform
  Events, Change Data Capture, or connecting Salesforce to external systems.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
  updated: "2026-02-18"
---

# sf-integration: Salesforce Integration Patterns

## Key Insights

| Insight | Details | Action |
|---------|---------|--------|
| **Named Credential Architecture** | Legacy (pre-API 61) vs External Credentials (API 61+) | Check org API version first |
| **Callouts in Triggers** | Synchronous callouts NOT allowed in triggers | Always use async (Queueable, @future) |
| **Governor Limits** | 100 callouts per transaction, 120s timeout max | Batch callouts, use async patterns |
| **External Services** | Auto-generates Apex from OpenAPI specs | Requires Named Credential for auth |
| **No Thread.sleep()** | Apex has no sleep/wait primitive | Use Queueable chains or Scheduled Apex for retry delays |
| **Concurrent Limits** | Long-running callouts consume concurrent request slots | Keep timeouts short, use async when possible |

---

## Named Credential Architecture (API 61+)

| Feature | Legacy Named Credential | External Credential (API 61+) |
|---------|------------------------|------------------------------|
| **API Version** | Pre-API 61 | API 61+ (Winter '24+) |
| **Principal Concept** | Single principal per credential | Named Principal + Per-User Principal |
| **OAuth Support** | Basic OAuth 2.0 | Full OAuth 2.0 + PKCE, JWT |
| **Permissions** | Profile-based | Permission Set + Named Principal |
| **Private Connect** | Not supported | Supports Private Connect |
| **Recommendation** | Legacy orgs only | **Use for all new development** |

### Decision Matrix

```
Use LEGACY Named Credential if:
  - Org API version < 61
  - Migrating existing integrations (maintain compatibility)
  - Simple API key / Basic Auth (quick setup)

Use EXTERNAL Credential (API 61+) if:
  - New development (recommended)
  - OAuth 2.0 with PKCE required
  - Per-user authentication needed
  - Fine-grained permission control required
  - JWT Bearer flow for server-to-server
  - Private Connect (private routing) needed
```

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Gather via `AskUserQuestion`:

1. **Integration Type**: Outbound REST, Outbound SOAP, Inbound REST, Event-driven (PE/CDC)
2. **Authentication**: OAuth 2.0 (Client Creds / JWT / Auth Code), Certificate (mTLS), API Key / Basic Auth
3. **External System**: Base URL, API version, rate limits, required headers, response sizes
4. **Sync vs Async**: Real-time -> Sync | Fire-and-forget -> Async | From DML -> MUST be async | Long-running -> Continuation

### Phase 2: Template Selection

| Integration Need | Template |
|-----------------|----------|
| OAuth 2.0 Client Credentials | `templates/named-credentials/oauth-client-credentials.namedCredential-meta.xml` |
| OAuth 2.0 JWT Bearer | `templates/named-credentials/oauth-jwt-bearer.namedCredential-meta.xml` |
| Certificate Auth | `templates/named-credentials/certificate-auth.namedCredential-meta.xml` |
| API Key / Basic Auth | `templates/named-credentials/custom-auth.namedCredential-meta.xml` |
| External Credential (OAuth) | `templates/external-credentials/oauth-external-credential.externalCredential-meta.xml` |
| External Service (OpenAPI) | `templates/external-services/openapi-registration.externalServiceRegistration-meta.xml` |
| REST Callout (Sync) | `templates/callouts/rest-sync-callout.cls` |
| REST Callout (Async) | `templates/callouts/rest-queueable-callout.cls` |
| Retry Handler | `templates/callouts/callout-retry-handler.cls` |
| SOAP Callout | `templates/soap/soap-callout-service.cls` |
| Platform Event | `templates/platform-events/platform-event-definition.object-meta.xml` |
| Event Publisher | `templates/platform-events/event-publisher.cls` |
| Event Subscriber | `templates/platform-events/event-subscriber-trigger.trigger` |
| CDC Subscriber | `templates/cdc/cdc-subscriber-trigger.trigger` |
| CDC Handler | `templates/cdc/cdc-handler.cls` |

### Phase 3: Generation & Validation

**File Locations**:
```
force-app/main/default/
├── namedCredentials/       {{CredentialName}}.namedCredential-meta.xml
├── externalCredentials/    {{CredentialName}}.externalCredential-meta.xml
├── externalServiceRegistrations/  {{ServiceName}}.externalServiceRegistration-meta.xml
├── classes/                {{ServiceName}}Callout.cls + Mock.cls
├── objects/                {{EventName}}__e/
└── triggers/               {{EventName}}Subscriber.trigger
```

Validate using scoring system (see `references/scoring-system.md`).

### Phase 4: Deployment

**Deployment Order** (CRITICAL):
```
1. Named Credentials / External Credentials FIRST
2. External Service Registrations (depends on Named Credentials)
3. Apex classes (callout services, handlers, mocks)
4. Platform Events / CDC configuration
5. Triggers (depends on events being deployed)
```

### Phase 5: Testing & Verification

1. Test Named Credential in Setup -> Named Credentials -> Test Connection
2. Test External Service by invoking generated Apex methods
3. Test Callout using Anonymous Apex or test class with HttpCalloutMock
4. Test Events by publishing and verifying subscriber execution
5. Run test classes to validate all mocks pass

---

## Named Credentials

| Auth Type | Use Case | Key Config |
|-----------|----------|------------|
| **OAuth 2.0 Client Credentials** | Server-to-server, no user context | scope, tokenEndpoint |
| **OAuth 2.0 JWT Bearer** | CI/CD, backend services | Certificate + Connected App |
| **Certificate (Mutual TLS)** | High-security integrations | Client cert required |
| **Custom (API Key/Basic)** | Simple APIs | username/password |

**NEVER hardcode credentials** -- always use Named Credentials.

---

## Deep-Dive References

> Full implementations, code examples, and detailed patterns are in `references/`.

**External Credentials & Services** -- `references/external-credentials-and-services.md`
External Credential XML, Permission Set config, External Service Registration, auto-generated Apex usage.

**REST Callout Patterns** -- `references/rest-callout-patterns.md`
Sync callout class, async Queueable callout, retry handler (Queueable chain), retry strategy comparison table.

**SOAP Callout Patterns** -- `references/soap-callout-patterns.md`
WSDL2Apex process, SOAP service wrapper class with Named Credential endpoint.

**Platform Events & CDC** -- `references/platform-events-and-cdc.md`
Event definition XML, publisher patterns, subscriber trigger with checkpoint, RetryableException, CDC subscriber trigger with change type routing, CDC handler patterns.

**Callout Testing Patterns** -- `references/callout-testing-patterns.md`
HttpCalloutMock, MultiEndpoint mock, StaticResourceCalloutMock, MultiStaticResourceCalloutMock, WebServiceMock (SOAP), Queueable callout testing.

**Circuit Breaker Pattern** -- `references/circuit-breaker-pattern.md`
Platform Cache-based circuit breaker (CLOSED/OPEN/HALF_OPEN states), ResilientCalloutService wrapper, cache partition setup.

**Governor Limits & Rate Limiting** -- `references/governor-limits-and-rate-limiting.md`
Callout limits by execution context, concurrent long-running apex limit, rate limiting best practices, 429 handling.

**Mutual TLS (mTLS)** -- `references/mtls-authentication.md`
Certificate setup, Named Credential with `protocol=Ssl`, inbound mTLS, verification checklist.

**Scoring System (120 Points)** -- `references/scoring-system.md`
6-category breakdown (Security 30, Error Handling 25, Bulkification 20, Architecture 20, Best Practices 15, Testing 10), thresholds, output format.

---

## Retry Strategy Quick Reference

| Strategy | Delay | Use When | Limitation |
|----------|-------|----------|------------|
| **Inline loop** | None (immediate) | Transient blips | No delay; counts against 100-callout limit |
| **Queueable chain** | Seconds-to-minutes | Most retry scenarios | Queue depth limit |
| **Scheduled Apex** | Minutes-to-hours | Rate-limited APIs, long outages | 1-min minimum granularity |
| **Platform Event retry** | Built-in backoff | Event subscriber triggers only | Max 9 retries |

---

## Anti-Patterns

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Hardcoded credentials | Security vulnerability | Use Named Credentials |
| Sync callout in trigger | `CalloutException: Uncommitted work pending` | Use Queueable with `Database.AllowsCallouts` |
| No timeout specified | Default 10s may be too short | Set `req.setTimeout(120000)` |
| `Thread.sleep()` for retry | Does not exist in Apex | Use Queueable chain or Scheduled Apex |
| Retry loop in same transaction | Zero delay, wastes callout limit | Use Queueable chain |
| No retry logic | Transient failures cause data loss | Implement retry via Queueable chain |
| Ignoring status codes | Silent failures | Check `statusCode`, handle 4xx/5xx |
| 100+ callouts per transaction | Governor limit exceeded | Batch callouts, use async |
| No logging | Cannot debug production issues | Log all callout requests/responses |
| Exposing API errors to users | Security risk, poor UX | Catch and wrap in user-friendly messages |
| No circuit breaker | Cascading failures | Use Platform Cache circuit breaker |
| Ignoring 429 responses | API bans, rate limit escalation | Check Retry-After header, backoff |
| Callouts in PE triggers | Consumes async limits | Delegate to Queueable from trigger |

---

## Cross-Skill Integration

| To Skill | When to Use |
|----------|-------------|
| sf-connected-apps | OAuth Connected App for Named Credential |
| sf-apex | Custom callout service beyond templates |
| sf-metadata | Query existing Named Credentials |
| sf-deploy | Deploy to org |
| sf-ai-agentforce | Agent action using External Service |
| sf-flow | HTTP Callout Flow for agent |
| sf-testing | Run test classes, coverage analysis |

**Agentforce flow**: `sf-integration` -> Named Credential + External Service -> `sf-flow` -> HTTP Callout wrapper -> `sf-ai-agentforce` -> Agent with `flow://` target -> `sf-deploy`

---

## CLI Quick Reference

```bash
# Named Credentials
sf org list metadata --metadata-type NamedCredential --target-org {{alias}}
sf project deploy start --metadata NamedCredential:{{Name}} --target-org {{alias}}
sf project retrieve start --metadata NamedCredential:{{Name}} --target-org {{alias}}

# External Credentials & Services
sf org list metadata --metadata-type ExternalCredential --target-org {{alias}}
sf project deploy start --metadata ExternalCredential:{{Name}} --target-org {{alias}}
sf org list metadata --metadata-type ExternalServiceRegistration --target-org {{alias}}
sf project deploy start --metadata ExternalServiceRegistration:{{Name}} --target-org {{alias}}

# Platform Events
sf project deploy start --metadata CustomObject:{{EventName}}__e --target-org {{alias}}

# Batch deploy all integration components
sf project deploy start \
  --source-dir force-app/main/default/namedCredentials,force-app/main/default/externalCredentials,force-app/main/default/externalServiceRegistrations,force-app/main/default/classes \
  --target-org {{alias}}

# Dry-run validation
sf project deploy start --source-dir force-app/main/default/namedCredentials \
  --target-org {{alias}} --dry-run
```

---

## Notes & Dependencies

- **API Version**: 62.0+ (Winter '25) recommended for External Credentials
- **Required Permissions**: API Enabled, External Services access
- **Platform Cache**: Required for Circuit Breaker pattern (1 MB Org cache minimum)
- **Scoring Mode**: Strict (block deployment if score < 54)

---

## Sources

- [Named Credentials and External Credentials](https://help.salesforce.com/s/articleView?id=sf.nc_named_creds_and_ext_creds.htm&language=en_US&type=5)
- [Testing Apex Callouts using HttpCalloutMock](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_restful_http_testing_httpcalloutmock.htm)
- [Testing HTTP Callouts Using Static Resources](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_restful_http_testing_static.htm)
- [Platform Events Best Practices](https://trailhead.salesforce.com/content/learn/modules/platform-events-debugging/apply-best-practices-writing-platform-triggers)
- [CDC Design Considerations](https://developer.salesforce.com/blogs/2022/10/design-considerations-for-change-data-capture-and-platform-events)
- [Callout Limits and Limitations](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_callouts_timeouts.htm)
- [Execution Governors and Limits](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [Mutual TLS for Salesforce](https://help.salesforce.com/s/articleView?id=000383575&language=en_US&type=1)
- [Platform Cache Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_platform_cache_best_practices.htm)

---

## License

MIT License - See LICENSE file for details.
