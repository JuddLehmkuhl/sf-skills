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

# sf-integration: Salesforce Integration Patterns Expert

Expert integration architect specializing in secure callout patterns, event-driven architecture, and external service registration for Salesforce.

## Core Responsibilities

1. **Named Credential Generation**: Create Named Credentials with OAuth 2.0, JWT Bearer, Certificate, or Custom authentication
2. **External Credential Generation**: Create modern External Credentials (API 61+) with Named Principals
3. **External Service Registration**: Generate ExternalServiceRegistration metadata from OpenAPI/Swagger specs
4. **REST Callout Patterns**: Synchronous and asynchronous HTTP callout implementations
5. **SOAP Callout Patterns**: WSDL2Apex guidance and WebServiceCallout patterns
6. **Platform Events**: Event definitions, publishers, and subscriber triggers
7. **Change Data Capture**: CDC enablement and subscriber patterns
8. **Callout Testing**: HttpCalloutMock, StaticResourceCalloutMock, and WebServiceMock patterns
9. **Resilience Patterns**: Circuit breaker, retry with Queueable chains, rate-limit awareness
10. **Validation & Scoring**: Score integrations against 6 categories (0-120 points)

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

## CRITICAL: Named Credential Architecture (API 61+)

### Legacy Named Credentials vs External Credentials

| Feature | Legacy Named Credential | External Credential (API 61+) |
|---------|------------------------|------------------------------|
| **API Version** | Pre-API 61 | API 61+ (Winter '24+) |
| **Principal Concept** | Single principal per credential | Named Principal + Per-User Principal |
| **OAuth Support** | Basic OAuth 2.0 | Full OAuth 2.0 + PKCE, JWT |
| **Permissions** | Profile-based | Permission Set + Named Principal |
| **Private Connect** | Not supported | Supports Private Connect for private routing |
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

Use `AskUserQuestion` to gather:

1. **Integration Type**:
   - Outbound REST (Salesforce -> External API)
   - Outbound SOAP (Salesforce -> External SOAP Service)
   - Inbound REST (External -> Salesforce REST API)
   - Event-driven (Platform Events, CDC)

2. **Authentication Method**:
   - OAuth 2.0 Client Credentials
   - OAuth 2.0 JWT Bearer
   - OAuth 2.0 Authorization Code
   - Certificate-based (Mutual TLS)
   - API Key / Basic Auth

3. **External System Details**:
   - Base endpoint URL
   - API version
   - Rate limits (requests per minute/hour)
   - Required headers
   - Expected response sizes

4. **Sync vs Async Requirements**:
   - Real-time response needed? -> Sync
   - Fire-and-forget? -> Async (@future, Queueable)
   - Triggered from DML? -> MUST be async
   - Long-running request? -> Continuation (for Visualforce/LWC)

### Phase 2: Template Selection

| Integration Need | Template | Location |
|-----------------|----------|----------|
| OAuth 2.0 Client Credentials | `oauth-client-credentials.namedCredential-meta.xml` | `templates/named-credentials/` |
| OAuth 2.0 JWT Bearer | `oauth-jwt-bearer.namedCredential-meta.xml` | `templates/named-credentials/` |
| Certificate Auth | `certificate-auth.namedCredential-meta.xml` | `templates/named-credentials/` |
| API Key / Basic Auth | `custom-auth.namedCredential-meta.xml` | `templates/named-credentials/` |
| External Credential (OAuth) | `oauth-external-credential.externalCredential-meta.xml` | `templates/external-credentials/` |
| External Service (OpenAPI) | `openapi-registration.externalServiceRegistration-meta.xml` | `templates/external-services/` |
| REST Callout (Sync) | `rest-sync-callout.cls` | `templates/callouts/` |
| REST Callout (Async) | `rest-queueable-callout.cls` | `templates/callouts/` |
| Retry Handler | `callout-retry-handler.cls` | `templates/callouts/` |
| SOAP Callout | `soap-callout-service.cls` | `templates/soap/` |
| Platform Event | `platform-event-definition.object-meta.xml` | `templates/platform-events/` |
| Event Publisher | `event-publisher.cls` | `templates/platform-events/` |
| Event Subscriber | `event-subscriber-trigger.trigger` | `templates/platform-events/` |
| CDC Subscriber | `cdc-subscriber-trigger.trigger` | `templates/cdc/` |
| CDC Handler | `cdc-handler.cls` | `templates/cdc/` |

### Phase 3: Generation & Validation

**File Locations**:
```
force-app/main/default/
├── namedCredentials/
│   └── {{CredentialName}}.namedCredential-meta.xml
├── externalCredentials/
│   └── {{CredentialName}}.externalCredential-meta.xml
├── externalServiceRegistrations/
│   └── {{ServiceName}}.externalServiceRegistration-meta.xml
├── classes/
│   ├── {{ServiceName}}Callout.cls
│   ├── {{ServiceName}}Callout.cls-meta.xml
│   ├── {{ServiceName}}CalloutMock.cls          ← test mock
│   ├── {{ServiceName}}CalloutMock.cls-meta.xml
│   └── ...
├── objects/
│   └── {{EventName}}__e/
│       └── {{EventName}}__e.object-meta.xml
└── triggers/
    ├── {{EventName}}Subscriber.trigger
    └── {{EventName}}Subscriber.trigger-meta.xml
```

**Validate using scoring system** (see Scoring System section)

### Phase 4: Deployment

**Deployment Order** (CRITICAL):
```
1. Deploy Named Credentials / External Credentials FIRST
2. Deploy External Service Registrations (depends on Named Credentials)
3. Deploy Apex classes (callout services, handlers, mocks)
4. Deploy Platform Events / CDC configuration
5. Deploy Triggers (depends on events being deployed)
```

**Use sf-deploy skill**:
```
Skill(skill="sf-deploy")
Request: "Deploy Named Credential {{Name}} with dry-run first"
```

### Phase 5: Testing & Verification

1. **Test Named Credential** in Setup -> Named Credentials -> Test Connection
2. **Test External Service** by invoking generated Apex methods
3. **Test Callout** using Anonymous Apex or test class with HttpCalloutMock
4. **Test Events** by publishing and verifying subscriber execution
5. **Run test classes** to validate all mocks pass

---

## Named Credentials

| Auth Type | Use Case | Template | Key Config |
|-----------|----------|----------|------------|
| **OAuth 2.0 Client Credentials** | Server-to-server, no user context | `oauth-client-credentials.namedCredential-meta.xml` | scope, tokenEndpoint |
| **OAuth 2.0 JWT Bearer** | CI/CD, backend services | `oauth-jwt-bearer.namedCredential-meta.xml` | Certificate + Connected App |
| **Certificate (Mutual TLS)** | High-security integrations | `certificate-auth.namedCredential-meta.xml` | Client cert required |
| **Custom (API Key/Basic)** | Simple APIs | `custom-auth.namedCredential-meta.xml` | username/password |

Templates in `templates/named-credentials/`. **NEVER hardcode credentials** - always use Named Credentials.

---

## External Credentials (API 61+)

### OAuth External Credential

**Use Case**: Modern OAuth 2.0 with per-user or named principal authentication

**Template**: `templates/external-credentials/oauth-external-credential.externalCredential-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{CredentialLabel}}</label>
    <authenticationProtocol>Oauth</authenticationProtocol>
    <externalCredentialParameters>
        <parameterName>clientId</parameterName>
        <parameterType>AuthProviderClientId</parameterType>
        <parameterValue>{{ClientId}}</parameterValue>
    </externalCredentialParameters>
    <externalCredentialParameters>
        <parameterName>clientSecret</parameterName>
        <parameterType>AuthProviderClientSecret</parameterType>
        <parameterValue>{{ClientSecret}}</parameterValue>
    </externalCredentialParameters>
    <principals>
        <principalName>{{PrincipalName}}</principalName>
        <principalType>NamedPrincipal</principalType>
        <sequenceNumber>1</sequenceNumber>
    </principals>
</ExternalCredential>
```

**Permission Set Assignment** (required for External Credentials):
```xml
<!-- In permissionset-meta.xml -->
<externalCredentialPrincipalAccesses>
    <enabled>true</enabled>
    <externalCredentialPrincipal>{{CredentialName}} - {{PrincipalName}}</externalCredentialPrincipal>
</externalCredentialPrincipalAccesses>
```

---

## External Services (OpenAPI/Swagger)

### Generating from OpenAPI Spec

**Process**:
1. Obtain OpenAPI 2.0 (Swagger) or 3.0 spec from external API
2. Create Named Credential for authentication
3. Register External Service in Salesforce
4. Salesforce auto-generates Apex classes

**Template**: `templates/external-services/openapi-registration.externalServiceRegistration-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalServiceRegistration xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{ServiceLabel}}</label>
    <namedCredential>{{NamedCredentialName}}</namedCredential>
    <schema>{{OpenAPISchemaContent}}</schema>
    <schemaType>OpenApi3</schemaType>
    <serviceBinding>{{ServiceBindingName}}</serviceBinding>
    <status>Complete</status>
</ExternalServiceRegistration>
```

### Using Auto-Generated Apex

External Services generate Apex classes like:
- `ExternalService.{{ServiceName}}`
- `ExternalService.{{ServiceName}}_{{OperationName}}`

```apex
// Auto-generated class usage
ExternalService.Stripe stripe = new ExternalService.Stripe();
ExternalService.Stripe_createCustomer_Request req =
    new ExternalService.Stripe_createCustomer_Request();
req.email = 'customer@example.com';
ExternalService.Stripe_createCustomer_Response resp = stripe.createCustomer(req);
```

---

## REST Callout Patterns

### Synchronous REST Callout

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

### Asynchronous REST Callout (Queueable)

**Use Case**: Callouts triggered from DML (triggers, Process Builder)

**Template**: `templates/callouts/rest-queueable-callout.cls`

See template file for full implementation. Key points:
- Implements `Queueable, Database.AllowsCallouts`
- Accepts `List<Id>` for record context
- Queries records and makes callouts in `execute()`
- Handles errors with logging

### Retry Handler (Queueable Chain Pattern)

**Use Case**: Handle transient failures with retry delays between attempts

**Template**: `templates/callouts/callout-retry-handler.cls`

**IMPORTANT**: Apex has no `Thread.sleep()`. Inline retry loops execute immediately with zero delay between attempts. For actual timed backoff, use the **Queueable Chain** pattern below, which enqueues a new job for each retry attempt. The async queue provides natural delay (typically seconds to minutes depending on load).

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

### Retry Strategy Comparison

| Strategy | Delay | Use When | Limitation |
|----------|-------|----------|------------|
| **Inline loop** (same transaction) | None (immediate) | Transient blips, fast recovery expected | No actual delay; counts against 100-callout limit |
| **Queueable chain** | Seconds-to-minutes (queue latency) | Most retry scenarios | Queue depth limit (50 chained in dev, varies in prod) |
| **Scheduled Apex** | Configurable (minutes-to-hours) | Rate-limited APIs, long outages | Minimum 1-minute granularity; limited scheduled jobs |
| **Platform Event retry** | Built-in with `EventBus.RetryableException` | Event subscriber triggers only | Max 9 retries; increasing backoff managed by platform |

---

## SOAP Callout Patterns

### WSDL2Apex Process

**Step 1**: Generate Apex from WSDL
1. Setup -> Apex Classes -> Generate from WSDL
2. Upload WSDL file
3. Salesforce generates Apex classes

**Step 2**: Configure Remote Site Setting or Named Credential

**Step 3**: Use generated classes in Apex

**Template**: `templates/soap/soap-callout-service.cls` (full implementation with async Queueable wrapper)

```apex
public with sharing class {{ServiceName}}SoapService {

    public static {{ResponseType}} callService({{RequestType}} request) {
        try {
            {{WsdlGeneratedClass}}.{{PortType}} stub =
                new {{WsdlGeneratedClass}}.{{PortType}}();
            stub.endpoint_x = 'callout:{{NamedCredentialName}}';
            stub.timeout_x = 120000;

            return stub.{{OperationName}}(request);
        } catch (Exception e) {
            throw new CalloutException('SOAP service error: ' + e.getMessage());
        }
    }
}
```

---

## Platform Events

### Platform Event Definition

**Use Case**: Asynchronous, event-driven communication

**Template**: `templates/platform-events/platform-event-definition.object-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <deploymentStatus>Deployed</deploymentStatus>
    <eventType>HighVolume</eventType>
    <label>{{EventLabel}}</label>
    <pluralLabel>{{EventPluralLabel}}</pluralLabel>
    <publishBehavior>PublishAfterCommit</publishBehavior>
    <fields>
        <fullName>{{FieldName}}__c</fullName>
        <label>{{FieldLabel}}</label>
        <type>Text</type>
        <length>255</length>
    </fields>
</CustomObject>
```

**Event Types & Publish Behavior**:

| Property | Options | Guidance |
|----------|---------|----------|
| `eventType` | `StandardVolume`, `HighVolume` | Use `HighVolume` for production integrations (millions/day, 72-hour retention) |
| `publishBehavior` | `PublishAfterCommit`, `PublishImmediately` | Use `PublishAfterCommit` unless you need events even on rollback |

### Event Publisher

**Template**: `templates/platform-events/event-publisher.cls` (full implementation with bulk support, correlation IDs)

Key patterns:
- Always use `EventBus.publish()` (not DML `insert`)
- Check `Database.SaveResult` for each event
- Use correlation IDs for cross-system traceability
- Handle partial failures in bulk publishes

### Event Subscriber Trigger

**Template**: `templates/platform-events/event-subscriber-trigger.trigger`

```apex
trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
    String lastReplayId = '';

    for ({{EventName}}__e event : Trigger.new) {
        lastReplayId = event.ReplayId;

        try {
            {{EventName}}Handler.processEvent(event);
        } catch (Exception e) {
            // Log error but do NOT throw - allow other events to process
            System.debug(LoggingLevel.ERROR,
                'Event processing error: ' + e.getMessage() +
                ' ReplayId: ' + event.ReplayId);
        }
    }

    // Set resume checkpoint (high-volume events)
    EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
}
```

### Platform Event Retry with EventBus.RetryableException

For subscriber triggers, the platform provides built-in retry with backoff:

```apex
trigger OrderEventSubscriber on Order_Event__e (after insert) {
    for (Order_Event__e event : Trigger.new) {
        try {
            OrderEventHandler.process(event);
        } catch (Exception e) {
            // Throw RetryableException to have the platform retry
            // Platform retries up to 9 times with increasing backoff
            throw new EventBus.RetryableException(
                'Transient error, retrying: ' + e.getMessage()
            );
        }
    }
}
```

**RetryableException behavior**: The platform re-fires the trigger with the same batch of events. Maximum 9 retries. The delay increases automatically between retries (managed by the platform, not configurable). After 9 retries, the trigger moves to the error state and stops processing.

**Best Practice**: Combine checkpoint + retry:
```apex
// Set checkpoint for successfully processed events BEFORE throwing retry
EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastGoodReplayId);
throw new EventBus.RetryableException('Retry from checkpoint');
```

---

## Change Data Capture (CDC)

### CDC Enablement

Enable CDC via Setup -> Integrations -> Change Data Capture, or via metadata.

**Channel Format**: `{{ObjectAPIName}}ChangeEvent` (e.g., `AccountChangeEvent`, `Order__ChangeEvent`)

### CDC Subscriber Trigger

**Template**: `templates/cdc/cdc-subscriber-trigger.trigger`

```apex
trigger {{ObjectName}}CDCSubscriber on {{ObjectName}}ChangeEvent (after insert) {

    for ({{ObjectName}}ChangeEvent event : Trigger.new) {
        EventBus.ChangeEventHeader header = event.ChangeEventHeader;
        String changeType = header.getChangeType();
        List<String> changedFields = header.getChangedFields();
        List<String> recordIds = header.getRecordIds();

        switch on changeType {
            when 'CREATE' {
                {{ObjectName}}CDCHandler.handleCreate(event, header);
            }
            when 'UPDATE' {
                {{ObjectName}}CDCHandler.handleUpdate(event, header, changedFields);
            }
            when 'DELETE' {
                {{ObjectName}}CDCHandler.handleDelete(recordIds, header);
            }
            when 'UNDELETE' {
                {{ObjectName}}CDCHandler.handleUndelete(event, header);
            }
            when 'GAP_CREATE', 'GAP_UPDATE', 'GAP_DELETE', 'GAP_UNDELETE' {
                {{ObjectName}}CDCHandler.handleGap(recordIds, changeType);
            }
            when 'GAP_OVERFLOW' {
                {{ObjectName}}CDCHandler.handleOverflow(header.getEntityName());
            }
        }
    }
}
```

### CDC Handler Service

**Template**: `templates/cdc/cdc-handler.cls` (full implementation with field filtering, gap handling, overflow detection)

Key patterns from the template:
- Filter updates to only sync relevant fields (`SYNC_FIELDS` set)
- Handle GAP events by re-querying current record state
- Handle OVERFLOW by triggering full sync batch jobs
- Delegate callouts to Queueable jobs (`ExternalSyncQueueable`)

---

## Callout Testing Patterns

### HttpCalloutMock (Custom Mock)

Use `HttpCalloutMock` when you need full control over response behavior:

```apex
@IsTest
public class {{ServiceName}}CalloutMock implements HttpCalloutMock {

    private Integer statusCode;
    private String responseBody;
    private Map<String, String> responseHeaders;

    public {{ServiceName}}CalloutMock(Integer statusCode, String responseBody) {
        this.statusCode = statusCode;
        this.responseBody = responseBody;
        this.responseHeaders = new Map<String, String>{
            'Content-Type' => 'application/json'
        };
    }

    public HTTPResponse respond(HTTPRequest req) {
        HttpResponse res = new HttpResponse();
        res.setStatusCode(statusCode);
        res.setBody(responseBody);
        for (String header : responseHeaders.keySet()) {
            res.setHeader(header, responseHeaders.get(header));
        }
        return res;
    }
}
```

**Using in tests**:
```apex
@IsTest
static void testGetSuccess() {
    String mockBody = '{"id":"123","name":"Test Account"}';
    Test.setMock(HttpCalloutMock.class,
        new {{ServiceName}}CalloutMock(200, mockBody));

    Test.startTest();
    Map<String, Object> result = {{ServiceName}}Callout.get('/accounts/123');
    Test.stopTest();

    System.assertEquals('123', result.get('id'));
    System.assertEquals('Test Account', result.get('name'));
}

@IsTest
static void testServerError() {
    Test.setMock(HttpCalloutMock.class,
        new {{ServiceName}}CalloutMock(500, '{"error":"Internal Server Error"}'));

    Test.startTest();
    try {
        {{ServiceName}}Callout.get('/accounts/123');
        System.assert(false, 'Expected CalloutException');
    } catch (CalloutException e) {
        System.assert(e.getMessage().contains('Server Error'));
    }
    Test.stopTest();
}
```

### MultiEndpoint HttpCalloutMock

Route different responses based on endpoint:

```apex
@IsTest
public class MultiEndpointCalloutMock implements HttpCalloutMock {

    private Map<String, HttpResponse> responseMap = new Map<String, HttpResponse>();

    public void addResponse(String endpointContains, Integer status, String body) {
        HttpResponse res = new HttpResponse();
        res.setStatusCode(status);
        res.setBody(body);
        res.setHeader('Content-Type', 'application/json');
        responseMap.put(endpointContains, res);
    }

    public HTTPResponse respond(HTTPRequest req) {
        String endpoint = req.getEndpoint();
        for (String key : responseMap.keySet()) {
            if (endpoint.contains(key)) {
                return responseMap.get(key);
            }
        }
        // Default: 404
        HttpResponse res = new HttpResponse();
        res.setStatusCode(404);
        res.setBody('{"error":"No mock configured for: ' + endpoint + '"}');
        return res;
    }
}
```

### StaticResourceCalloutMock

Use when responses are large or complex JSON/XML stored in static resources:

```apex
@IsTest
static void testWithStaticResource() {
    StaticResourceCalloutMock mock = new StaticResourceCalloutMock();
    mock.setStaticResource('MockAccountResponse'); // Static Resource API Name
    mock.setStatusCode(200);
    mock.setHeader('Content-Type', 'application/json');

    Test.setMock(HttpCalloutMock.class, mock);

    Test.startTest();
    Map<String, Object> result = AccountCallout.get('/accounts/123');
    Test.stopTest();

    System.assertNotEquals(null, result);
}
```

### MultiStaticResourceCalloutMock

Different static resources for different endpoints:

```apex
@IsTest
static void testMultipleEndpoints() {
    MultiStaticResourceCalloutMock mock = new MultiStaticResourceCalloutMock();
    mock.setStaticResource('callout:ExternalApi/accounts', 'MockAccountResponse');
    mock.setStaticResource('callout:ExternalApi/orders', 'MockOrderResponse');
    mock.setStatusCode(200);
    mock.setHeader('Content-Type', 'application/json');

    Test.setMock(HttpCalloutMock.class, mock);

    Test.startTest();
    // Both callouts will get their respective static resource responses
    Map<String, Object> account = AccountCallout.get('/accounts/123');
    Map<String, Object> order = OrderCallout.get('/orders/456');
    Test.stopTest();
}
```

### WebServiceMock (SOAP Testing)

```apex
@IsTest
public class {{ServiceName}}WebServiceMock implements WebServiceMock {

    public void doInvoke(
        Object stub, Object request, Map<String, Object> response,
        String endpoint, String soapAction, String requestName,
        String responseNS, String responseName, String responseType
    ) {
        // Create and populate response object
        {{WsdlGeneratedClass}}.{{ResponseType}} mockResponse =
            new {{WsdlGeneratedClass}}.{{ResponseType}}();
        mockResponse.resultField = 'Mock Value';

        response.put('response_x', mockResponse);
    }
}

// Usage in test:
@IsTest
static void testSoapCallout() {
    Test.setMock(WebServiceMock.class, new {{ServiceName}}WebServiceMock());

    Test.startTest();
    {{ResponseType}} result = {{ServiceName}}SoapService.callService(testRequest);
    Test.stopTest();

    System.assertEquals('Mock Value', result.resultField);
}
```

### Testing Queueable Callouts

```apex
@IsTest
static void testQueueableCallout() {
    // Set mock BEFORE enqueuing
    Test.setMock(HttpCalloutMock.class,
        new {{ServiceName}}CalloutMock(200, '{"status":"ok"}'));

    Test.startTest();
    System.enqueueJob(new {{ServiceName}}QueueableCallout(recordIds, 'CREATE'));
    Test.stopTest();

    // Assert side effects (record updates, logs created, etc.)
    List<Integration_Log__c> logs = [
        SELECT Status__c FROM Integration_Log__c
        WHERE Record_Id__c = :recordIds[0]
    ];
    System.assertEquals('Success', logs[0].Status__c);
}
```

---

## Circuit Breaker Pattern

Prevent cascading failures when an external API is down. Uses **Platform Cache** to track failure counts and trip the circuit.

### Circuit Breaker with Platform Cache

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

### Using the Circuit Breaker

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

---

## Governor Limits & Rate Limiting

### Callout Limits by Execution Context

| Context | Max Callouts | Max Timeout (each) | Max Concurrent Long-Running | Notes |
|---------|-------------|--------------------|-----------------------------|-------|
| **Synchronous Apex** | 100 | 120s | 10 per org | Blocks user thread |
| **@future** | 100 | 120s | 50 per org (shared) | Fire-and-forget |
| **Queueable** | 100 | 120s | 50 per org (shared) | Chainable, stateful |
| **Batch Apex** | 100 per `execute()` | 120s | 50 per org (shared) | Each batch invocation is separate transaction |
| **Scheduled Apex** | 100 | 120s | 50 per org (shared) | Runs as scheduled user |
| **Platform Event Trigger** | 100 | 120s | N/A | Avoid callouts; use Queueable |
| **Flow (HTTP Callout)** | 100 per transaction | 120s | N/A | Counts against same transaction limits |

### Concurrent Long-Running Apex Limit

The **Concurrent Long-Running Apex Limit** is the most common cause of integration failures at scale:

- Default: 10 concurrent requests holding connections > 5 seconds
- When exceeded: `System.LimitException: Apex concurrent request limit exceeded`
- Applies to synchronous callouts that take more than 5 seconds

**Mitigation strategies**:
1. **Reduce timeout**: Set `req.setTimeout()` to the minimum acceptable value (not always 120s)
2. **Go async**: Move callouts to Queueable/Future to use the async limit (50 vs 10)
3. **Batch and consolidate**: Combine multiple API calls into single bulk requests
4. **Circuit breaker**: Stop calling failing endpoints immediately (see pattern above)

### Rate Limiting Best Practices

```
External API rate limits        Salesforce governor limits
        ↓                              ↓
┌─────────────────────────────────────────────────────────────┐
│  1. Know your API's rate limits (requests/min, /hour, /day) │
│  2. Track usage via Custom Metadata or Platform Cache       │
│  3. Throttle with Queueable chains (natural pacing)         │
│  4. Handle 429 responses: check Retry-After header          │
│  5. Use Batch Apex for bulk operations (scope parameter)    │
│  6. Monitor with Integration_Log__c custom object           │
└─────────────────────────────────────────────────────────────┘
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

---

## Mutual TLS (mTLS) Authentication

### Overview

Mutual TLS adds client certificate authentication on top of standard TLS. Both the client (Salesforce) and the server verify each other's identity via certificates.

### When to Use mTLS

- High-security integrations (financial, healthcare, government)
- Regulatory compliance requirements (PCI-DSS, HIPAA)
- Zero-trust network architectures
- When the external system requires client certificate authentication

### Setup Steps

**Step 1: Obtain or generate certificates**
- Obtain a client certificate signed by a Certificate Authority (CA) trusted by the external system
- You need: private key + certificate chain in JKS (Java KeyStore) format

**Step 2: Import certificate into Salesforce**
- Setup -> Certificate and Key Management -> Import from Keystore
- Upload the JKS file containing private key and certificate chain
- Note the certificate label for use in Named Credentials

**Step 3: Configure Named Credential with client certificate**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{ServiceName}} mTLS</label>
    <endpoint>https://{{ExternalHost}}/api</endpoint>
    <principalType>NamedUser</principalType>
    <protocol>Ssl</protocol>
    <certificate>{{CertificateLabel}}</certificate>
</NamedCredential>
```

**Step 4: Use in Apex callout**
```apex
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:{{ServiceName}}_mTLS/resource');
req.setMethod('GET');
// The certificate is automatically sent during TLS handshake
// No additional code needed - Named Credential handles it
```

**Step 5 (Inbound mTLS)**: For external systems calling INTO Salesforce:
- Setup -> Certificate and Key Management -> Mutual Authentication Certificates
- Upload the external system's CA certificate
- Create an API-only integration user with "Enforce SSL/TLS Mutual Authentication" permission

### mTLS Checklist

| Step | Action | Verified |
|------|--------|----------|
| 1 | Client certificate obtained from trusted CA | |
| 2 | JKS keystore created with private key + chain | |
| 3 | Certificate imported in Salesforce Certificate Management | |
| 4 | Named Credential configured with `protocol=Ssl` and certificate | |
| 5 | Remote Site Setting or CSP Trusted Site allows endpoint | |
| 6 | Test connection succeeds from Salesforce | |
| 7 | Certificate expiry monitoring configured | |

---

## Scoring System (120 Points)

### Category Breakdown

| Category | Points | Evaluation Criteria |
|----------|--------|---------------------|
| **Security** | 30 | Named Credentials used (no hardcoded secrets), OAuth scopes minimized, certificate auth where applicable, mTLS for high-security |
| **Error Handling** | 25 | Retry logic present, timeout handling (120s max), specific exception types, logging implemented, circuit breaker for critical integrations |
| **Bulkification** | 20 | Batch callouts considered, CDC bulk handling, event batching for Platform Events |
| **Architecture** | 20 | Async patterns for DML-triggered callouts, proper service layer separation, single responsibility |
| **Best Practices** | 15 | Governor limit awareness, proper HTTP methods, idempotency for retries, rate limit handling |
| **Testing** | 10 | HttpCalloutMock implemented, error scenarios covered, 95%+ coverage, WebServiceMock for SOAP |

### Scoring Thresholds

```
Score: XX/120 Rating
  108-120  Excellent:  Production-ready, follows all best practices
   90-107  Very Good:  Minor improvements suggested
   72-89   Good:       Acceptable with noted improvements
   54-71   Needs Work: Address issues before deployment
    <54    Block:      CRITICAL issues, do not deploy
```

### Scoring Output Format

```
INTEGRATION SCORE: XX/120 Rating
================================================

Security           XX/30  ████████░░ XX%
  Named Credentials used: [Y/N]
  No hardcoded secrets: [Y/N]
  OAuth scopes minimal: [Y/N]
  mTLS where required: [Y/N]

Error Handling     XX/25  ████████░░ XX%
  Retry logic: [Y/N]
  Timeout handling: [Y/N]
  Circuit breaker: [Y/N]
  Logging: [Y/N]

Bulkification      XX/20  ████████░░ XX%
  Batch callouts: [Y/N]
  Event batching: [Y/N]

Architecture       XX/20  ████████░░ XX%
  Async patterns: [Y/N]
  Service separation: [Y/N]

Best Practices     XX/15  ████████░░ XX%
  Governor limits: [Y/N]
  Idempotency: [Y/N]
  Rate limiting: [Y/N]

Testing            XX/10  ████████░░ XX%
  HttpCalloutMock: [Y/N]
  Error scenarios: [Y/N]
  95%+ coverage: [Y/N]

================================================
```

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

### Agentforce Integration Flow

`sf-integration` -> Named Credential + External Service -> `sf-flow` -> HTTP Callout wrapper -> `sf-ai-agentforce` -> Agent with `flow://` target -> `sf-deploy` -> Deploy all

---

## CLI Commands Reference

### Named Credentials
```bash
# List Named Credentials
sf org list metadata --metadata-type NamedCredential --target-org {{alias}}

# Deploy Named Credential
sf project deploy start --metadata NamedCredential:{{Name}} --target-org {{alias}}

# Retrieve Named Credential
sf project retrieve start --metadata NamedCredential:{{Name}} --target-org {{alias}}
```

### External Credentials & Services
```bash
# List External Credentials
sf org list metadata --metadata-type ExternalCredential --target-org {{alias}}

# Deploy External Credential
sf project deploy start --metadata ExternalCredential:{{Name}} --target-org {{alias}}

# List External Service Registrations
sf org list metadata --metadata-type ExternalServiceRegistration --target-org {{alias}}

# Deploy External Service
sf project deploy start --metadata ExternalServiceRegistration:{{Name}} --target-org {{alias}}

# Register External Service via REST API
sf api request rest /services/data/v62.0/externalServiceRegistrations \
  --method POST \
  --body '{"label":"{{Label}}","namedCredential":"{{NC}}","schemaUrl":"{{URL}}"}'
```

### Platform Events
```bash
# Deploy Platform Event
sf project deploy start --metadata CustomObject:{{EventName}}__e --target-org {{alias}}
```

### Batch Deployment
```bash
# Deploy all integration components at once
sf project deploy start \
  --source-dir force-app/main/default/namedCredentials,force-app/main/default/externalCredentials,force-app/main/default/externalServiceRegistrations,force-app/main/default/classes \
  --target-org {{alias}}

# Dry-run validation first
sf project deploy start \
  --source-dir force-app/main/default/namedCredentials \
  --target-org {{alias}} \
  --dry-run
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Hardcoded credentials | Security vulnerability, credential rotation nightmare | Use Named Credentials |
| Sync callout in trigger | `CalloutException: Uncommitted work pending` | Use Queueable with `Database.AllowsCallouts` |
| No timeout specified | Default 10s may be too short | Set `req.setTimeout(120000)` (max 120s) |
| `Thread.sleep()` for retry delay | Does not exist in Apex; will not compile | Use Queueable chain or Scheduled Apex |
| Retry loop in same transaction | Zero delay, wastes callout limit (100 max) | Use Queueable chain for actual delay |
| No retry logic | Transient failures cause data loss | Implement retry via Queueable chain |
| Ignoring status codes | Silent failures | Check `statusCode` and handle 4xx/5xx |
| 100+ callouts per transaction | Governor limit exceeded | Batch callouts, use async |
| No logging | Cannot debug production issues | Log all callout requests/responses |
| Exposing API errors to users | Security risk, poor UX | Catch and wrap in user-friendly messages |
| No circuit breaker | Cascading failures, wasted callout limits | Use Platform Cache circuit breaker |
| Ignoring 429 responses | API bans, rate limit escalation | Check Retry-After header, backoff |
| Callouts in Platform Event triggers | Consumes async limits unnecessarily | Delegate to Queueable job from trigger |

---

## Notes & Dependencies

- **API Version**: 62.0+ (Winter '25) recommended for External Credentials
- **Required Permissions**: API Enabled, External Services access
- **Platform Cache**: Required for Circuit Breaker pattern (at least 1 MB Org cache)
- **Optional Skills**: sf-connected-apps (OAuth setup), sf-apex (custom callout code), sf-deploy (deployment), sf-testing (test execution)
- **Scoring Mode**: Strict (block deployment if score < 54)

---

## Sources

- [Salesforce Named Credentials and External Credentials](https://help.salesforce.com/s/articleView?id=sf.nc_named_creds_and_ext_creds.htm&language=en_US&type=5)
- [Testing Apex Callouts using HttpCalloutMock](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_restful_http_testing_httpcalloutmock.htm)
- [Testing HTTP Callouts Using Static Resources](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_restful_http_testing_static.htm)
- [Platform Events Best Practices](https://trailhead.salesforce.com/content/learn/modules/platform-events-debugging/apply-best-practices-writing-platform-triggers)
- [CDC Design Considerations](https://developer.salesforce.com/blogs/2022/10/design-considerations-for-change-data-capture-and-platform-events)
- [Callout Limits and Limitations](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_callouts_timeouts.htm)
- [Execution Governors and Limits](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)
- [Avoiding Concurrent Request Limits via Callout Optimization](https://developer.salesforce.com/blogs/engineering/2015/11/avoiding-the-concurrent-request-limit-via-synchronous-callout-optimization)
- [Mutual TLS for Salesforce](https://help.salesforce.com/s/articleView?id=000383575&language=en_US&type=1)
- [Enhance Integration Security with mTLS](https://developer.salesforce.com/blogs/2025/10/enhance-integration-security-with-mtls-for-salesforce-and-mulesoft)
- [Platform Cache Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_platform_cache_best_practices.htm)
- [Named Credentials Security Best Practices](https://www.valencesecurity.com/resources/blogs/salesforce-best-practices-when-using-named-credentials)

---

## License

MIT License - See LICENSE file for details.
