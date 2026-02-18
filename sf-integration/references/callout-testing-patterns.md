# Callout Testing Patterns

## HttpCalloutMock (Custom Mock)

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

## MultiEndpoint HttpCalloutMock

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

## StaticResourceCalloutMock

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

## MultiStaticResourceCalloutMock

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

## WebServiceMock (SOAP Testing)

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

## Testing Queueable Callouts

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
