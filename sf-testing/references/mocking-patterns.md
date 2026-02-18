# Mocking & Stubbing Patterns

> Referenced from: `sf-testing/SKILL.md` -- Mock HTTP Callouts, StubProvider, DML Abstraction

---

## Mock HTTP Callout Test

```apex
@IsTest
private class ExternalAPIServiceTest {

    private class MockHttpResponse implements HttpCalloutMock {
        private Integer statusCode;
        private String body;

        MockHttpResponse(Integer statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body;
        }

        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(this.statusCode);
            res.setBody(this.body);
            res.setHeader('Content-Type', 'application/json');
            return res;
        }
    }

    @IsTest
    static void testCallAPI_Success200_ReturnsData() {
        // Given
        Test.setMock(HttpCalloutMock.class,
            new MockHttpResponse(200, '{"success": true, "data": {"id": "12345"}}'));

        // When
        Test.startTest();
        String result = ExternalAPIService.callAPI('test-endpoint');
        Test.stopTest();

        // Then
        Assert.isTrue(result.contains('success'), 'Response should indicate success');
    }

    @IsTest
    static void testCallAPI_Error500_ThrowsException() {
        // Given
        Test.setMock(HttpCalloutMock.class,
            new MockHttpResponse(500, '{"error": "Internal Server Error"}'));

        // When/Then
        try {
            Test.startTest();
            ExternalAPIService.callAPI('test-endpoint');
            Test.stopTest();
            Assert.fail('Expected CalloutException for 500 status');
        } catch (ExternalAPIService.ApiException e) {
            Assert.isTrue(e.getMessage().contains('500'),
                'Exception should contain status code');
        }
    }
}
```

---

## StubProvider: UniversalMock

Use `System.StubProvider` when you need to:
- Test a class in **isolation** without DML (true unit testing)
- Mock a **dependency** that makes callouts, SOQL, or DML
- Create **faster tests** that avoid database operations (up to 35x speedup)
- Test code that depends on another class's **internal state**

```apex
/**
 * StubProvider implementation that mocks any class method.
 * Use with Test.createStub() to create mock objects.
 */
@IsTest
public class UniversalMock implements System.StubProvider {

    // Map of methodName -> return value
    private Map<String, Object> returnValues = new Map<String, Object>();
    // Track which methods were called and with what args
    private Map<String, List<List<Object>>> callLog = new Map<String, List<List<Object>>>();

    public UniversalMock withReturnValue(String methodName, Object returnValue) {
        this.returnValues.put(methodName, returnValue);
        return this;
    }

    public Object handleMethodCall(
        Object stubbedObject,
        String stubbedMethodName,
        Type returnType,
        List<Type> listOfParamTypes,
        List<String> listOfParamNames,
        List<Object> listOfArgs
    ) {
        // Log the call
        if (!callLog.containsKey(stubbedMethodName)) {
            callLog.put(stubbedMethodName, new List<List<Object>>());
        }
        callLog.get(stubbedMethodName).add(listOfArgs);

        // Return configured value
        return returnValues.get(stubbedMethodName);
    }

    public Integer getCallCount(String methodName) {
        if (!callLog.containsKey(methodName)) {
            return 0;
        }
        return callLog.get(methodName).size();
    }

    public List<Object> getLastCallArgs(String methodName) {
        if (!callLog.containsKey(methodName) || callLog.get(methodName).isEmpty()) {
            return null;
        }
        List<List<Object>> calls = callLog.get(methodName);
        return calls[calls.size() - 1];
    }
}
```

### Using UniversalMock in Tests

```apex
@IsTest
private class OpportunityService_Test {

    @IsTest
    static void testCalculateDiscount_UsesExternalPricing() {
        // Arrange - create a mock for PricingService
        UniversalMock mock = new UniversalMock()
            .withReturnValue('getDiscount', 0.15);

        PricingService mockPricing = (PricingService) Test.createStub(
            PricingService.class, mock
        );

        // Inject the mock
        OpportunityService service = new OpportunityService();
        service.pricingService = mockPricing;  // requires @TestVisible or setter

        // Act
        Test.startTest();
        Decimal discount = service.calculateDiscount('Enterprise', 100000);
        Test.stopTest();

        // Assert
        Assert.areEqual(0.15, discount, 'Should use pricing service discount');
        Assert.areEqual(1, mock.getCallCount('getDiscount'),
            'PricingService.getDiscount should be called exactly once');
    }
}
```

---

## DML Abstraction for Faster Tests

Abstract DML operations behind an interface. Production uses `DatabaseDml`; tests use `MockDml` to avoid database hits (up to 35x speedup).

### Interface

```apex
public interface IDml {
    List<Database.SaveResult> doInsert(List<SObject> records);
    List<Database.SaveResult> doUpdate(List<SObject> records);
    List<Database.DeleteResult> doDelete(List<SObject> records);
}
```

### Production Implementation

```apex
public class DatabaseDml implements IDml {
    public List<Database.SaveResult> doInsert(List<SObject> records) {
        return Database.insert(records);
    }
    public List<Database.SaveResult> doUpdate(List<SObject> records) {
        return Database.update(records);
    }
    public List<Database.DeleteResult> doDelete(List<SObject> records) {
        return Database.delete(records);
    }
}
```

### Test Mock Implementation

```apex
@IsTest
public class MockDml implements IDml {
    public List<SObject> insertedRecords = new List<SObject>();
    public List<SObject> updatedRecords = new List<SObject>();
    public List<SObject> deletedRecords = new List<SObject>();

    public List<Database.SaveResult> doInsert(List<SObject> records) {
        insertedRecords.addAll(records);
        return new List<Database.SaveResult>();
    }
    public List<Database.SaveResult> doUpdate(List<SObject> records) {
        updatedRecords.addAll(records);
        return new List<Database.SaveResult>();
    }
    public List<Database.DeleteResult> doDelete(List<SObject> records) {
        deletedRecords.addAll(records);
        return new List<Database.DeleteResult>();
    }
}
```

### Usage in Tests

```apex
@IsTest
static void testProcessAccounts_InsertsRelatedContacts() {
    // Arrange
    MockDml mockDml = new MockDml();
    AccountService service = new AccountService(mockDml);  // inject mock

    List<Account> accounts = new List<Account>{
        new Account(Name = 'Acme Corp')
    };

    // Act
    Test.startTest();
    service.processAccounts(accounts);
    Test.stopTest();

    // Assert - verify DML happened without database round-trip
    Assert.areEqual(1, mockDml.insertedRecords.size(),
        'Should have inserted 1 related contact');
    Assert.isInstanceOfType(mockDml.insertedRecords[0], Contact.class,
        'Inserted record should be a Contact');
}
```
