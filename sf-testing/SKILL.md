---
name: sf-testing
description: >
  Comprehensive Salesforce testing skill with test execution, code coverage analysis,
  and agentic test-fix loops. Run Apex tests, analyze coverage, generate test patterns,
  and automatically fix failing tests with 120-point scoring.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
  enriched: "2026-02-18"
---

# sf-testing: Salesforce Test Execution & Coverage Analysis

Expert testing engineer specializing in Apex test execution, code coverage analysis, mock frameworks, StubProvider patterns, permission-based testing, and agentic test-fix loops. Execute tests, analyze failures, and automatically fix issues.

## Core Responsibilities

1. **Test Execution**: Run Apex tests via `sf apex run test` with coverage analysis
2. **Coverage Analysis**: Parse coverage reports, identify untested code paths, drive from 75% to 95%+
3. **Failure Analysis**: Parse test failures, identify root causes, suggest fixes
4. **Agentic Test-Fix Loop**: Automatically fix failing tests and re-run until passing
5. **Test Generation**: Create test classes using sf-apex patterns and TestDataFactory templates
6. **Bulk Testing**: Validate with 251+ records for governor limit safety
7. **Trigger Action Testing**: Test TAF actions with `TA_*_Test` naming (see salesforce-trigger-framework)
8. **Permission Testing**: Validate FLS, sharing rules, and profile-based access with `System.runAs()`
9. **Test Suite Management**: Organize tests into `ApexTestSuite` metadata for CI/CD pipelines

## Cross-Skill References

| Skill | Relationship | Key Integration Point |
|-------|-------------|----------------------|
| **salesforce-trigger-framework** | **PRIMARY** - Most tests are for TA_* actions | `TA_<Object>_<Action>_Test` naming convention, bypass testing |
| **sf-apex** | Generate test classes, fix failing code | `Skill(skill="sf-apex", args="Create test class for LeadService")` |
| **sf-data** | Create bulk test data (251+ records) | `Skill(skill="sf-data", args="Create 251 Leads for bulk testing")` |
| **sf-deploy** | Deploy test classes to org | `Skill(skill="sf-deploy", args="Deploy tests to sandbox")` |
| **sf-debug** | Analyze failures with debug logs | `Skill(skill="sf-debug", args="Analyze test failure logs")` |

> **Important**: When testing Trigger Actions Framework components, load `salesforce-trigger-framework/SKILL.md` first. That skill defines the architecture (`Trigger -> MetadataTriggerHandler -> TA_* -> Services -> DAL`) and dictates which layers need testing and how.

---

## Workflow (5-Phase Pattern)

### Phase 1: Test Discovery

Use **AskUserQuestion** to gather:
- Test scope (single class, all tests, specific test suite)
- Target org alias
- Coverage threshold requirement (default: 75%, recommended: 95%)
- Whether to enable agentic fix loop

**Then**:
1. Check existing tests: `Glob: **/*Test*.cls`, `Glob: **/*_Test.cls`
2. Check for Test Data Factories: `Glob: **/*TestDataFactory*.cls`
3. Check for test suites: `Glob: **/*.testSuite-meta.xml`
4. Create TodoWrite tasks

### Phase 2: Test Execution

**Run Single Test Class**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --result-format json --output-dir test-results --target-org [alias]
```

**Run All Tests**:
```bash
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --output-dir test-results --target-org [alias]
```

**Run Specific Methods**:
```bash
sf apex run test --tests MyClassTest.testMethod1 --tests MyClassTest.testMethod2 --code-coverage --result-format json --target-org [alias]
```

**Run Test Suite**:
```bash
sf apex run test --suite-names MySuite --code-coverage --result-format json --target-org [alias]
```

**Run Tests Synchronously (disable parallel)**:
```bash
sf apex run test --class-names MyClassTest --synchronous --code-coverage --result-format json --target-org [alias]
```

### Phase 3: Results Analysis

**Parse test-results JSON**:
```
Read: test-results/test-run-id.json
```

**Coverage Summary Output**:
```
TEST EXECUTION RESULTS
================================================================

Test Run ID: 707xx0000000000
Org: my-sandbox
Duration: 45.2s

SUMMARY
---------------------------------------------------------------
Passed:    42
Failed:    3
Skipped:   0
Coverage: 78.5%

FAILED TESTS
---------------------------------------------------------------
AccountServiceTest.testBulkInsert
   Line 45: System.AssertException: Assertion Failed
   Expected: 200, Actual: 199

LeadScoringTest.testNullHandling
   Line 23: System.NullPointerException: Attempt to de-reference null

OpportunityTriggerTest.testValidation
   Line 67: System.DmlException: FIELD_CUSTOM_VALIDATION_EXCEPTION

COVERAGE BY CLASS
---------------------------------------------------------------
Class                          Lines    Covered  Uncovered  %
AccountService                 150      142      8          94.7%
LeadScoringService            85       68       17         80.0%
OpportunityTrigger            45       28       17         62.2% WARNING
ContactHelper                 30       15       15         50.0% BLOCKED

UNCOVERED LINES (OpportunityTrigger)
---------------------------------------------------------------
Lines 23-28: Exception handling block
Lines 45-52: Bulk processing edge case
Lines 78-82: Null check branch
```

### Phase 4: Agentic Test-Fix Loop

**When tests fail, automatically:**

```
+-------------------------------------------------------------+
|                    AGENTIC TEST-FIX LOOP                     |
+-------------------------------------------------------------+
|                                                              |
|  1. Parse failure message and stack trace                    |
|  2. Identify root cause:                                     |
|     - Assertion failure -> Check expected vs actual           |
|     - NullPointerException -> Add null checks                |
|     - DmlException -> Check validation rules, required fields|
|     - LimitException -> Reduce SOQL/DML in test              |
|  3. Read the failing test class                              |
|  4. Read the class under test                                |
|  5. Generate fix using sf-apex skill                         |
|  6. Re-run the specific failing test                         |
|  7. Repeat until passing (max 3 attempts)                    |
|                                                              |
+-------------------------------------------------------------+
```

**Failure Analysis Decision Tree**:

| Error Type | Root Cause | Auto-Fix Strategy |
|------------|------------|-------------------|
| `System.AssertException` | Wrong expected value or logic bug | Analyze assertion, check if test or code is wrong |
| `System.NullPointerException` | Missing null check or test data | Add null safety or fix test data setup |
| `System.DmlException` | Validation rule, required field, trigger | Check org config, add required fields to test data |
| `System.LimitException` | Governor limit hit | Refactor to use bulkified patterns |
| `System.QueryException` | No rows returned | Add test data or adjust query |
| `System.TypeException` | Type mismatch | Fix type casting or data format |
| `System.MathException` | Division by zero, overflow | Add boundary checks |

**Auto-Fix Command**:
```
Skill(skill="sf-apex", args="Fix failing test [TestClassName].[methodName] - Error: [error message]")
```

### Phase 5: Coverage Improvement

**If coverage < threshold**:

1. **Identify Uncovered Lines**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --detailed-coverage --result-format json --target-org [alias]
```

2. **Generate Tests for Uncovered Code**:
```
Read: force-app/main/default/classes/MyClass.cls (lines 45-52)
```
Then use sf-apex to generate test methods targeting those lines.

3. **Bulk Test Validation**:
```
Skill(skill="sf-data", args="Create 251 [ObjectName] records for bulk testing")
```

4. **Re-run with New Tests**:
```bash
sf apex run test --class-names MyClassTest --code-coverage --result-format json --target-org [alias]
```

---

## Coverage Gap Analysis Workflow (75% to 95%+)

When coverage is below 95%, follow this systematic workflow to close the gap.

### Step 1: Baseline Assessment

```bash
# Get org-wide coverage
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --output-dir test-results --target-org [alias]
```

Parse the results to build a prioritized list:

```
COVERAGE GAP ANALYSIS
================================================================
Target: 95% | Current: 78.5% | Gap: 16.5%

PRIORITY CLASSES (largest uncovered line counts first)
---------------------------------------------------------------
Priority  Class                     Coverage  Uncovered  Impact
1         ContactHelper             50.0%     15 lines   HIGH
2         OpportunityTrigger        62.2%     17 lines   HIGH
3         LeadScoringService        80.0%     17 lines   MEDIUM
4         AccountService            94.7%     8 lines    LOW
```

### Step 2: Categorize Uncovered Code

For each class below target, read the source and categorize uncovered lines:

| Category | Example | Test Strategy |
|----------|---------|---------------|
| **Exception handlers** | `catch (DmlException e)` | Force the exception with bad data |
| **Null/empty guards** | `if (records == null)` | Pass null or empty list |
| **Conditional branches** | `if (Type == 'Enterprise')` | Create data matching each branch |
| **Bulk edge cases** | Loop boundaries, batch splits | Test with 0, 1, 200, 201 records |
| **Permission checks** | `Schema.sObjectType.X.isAccessible()` | Use `System.runAs()` with limited user |
| **Async callbacks** | `@future`, Queueable `execute()` | Call directly in test context |

### Step 3: Write Targeted Tests

For each uncovered category, write a minimal test method. Use the naming convention:
```
test<MethodName>_<Scenario>_<ExpectedResult>
```

Examples:
```apex
@IsTest
static void testProcessAccounts_NullInput_ReturnsEmpty() { ... }

@IsTest
static void testProcessAccounts_EmptyList_ReturnsEmpty() { ... }

@IsTest
static void testCalculateScore_DivisionByZero_HandlesGracefully() { ... }
```

### Step 4: Iterate Until Target

```bash
# Re-run and check coverage incrementally
sf apex run test --class-names MyClassTest --code-coverage --detailed-coverage --result-format json --target-org [alias]
```

Repeat Steps 2-4 until every class is at 95%+.

### Coverage Math Quick Reference

```
Coverage % = (Covered Lines / Total Lines) * 100

To find lines needed to reach target:
  Lines needed = (Target% * Total Lines) - Currently Covered Lines

Example: 150 total lines, 112 covered (74.7%), target 95%
  Lines needed = (0.95 * 150) - 112 = 142.5 - 112 = 31 more lines
```

---

## Testing Trigger Actions Framework (TAF) Components

> **Prerequisite**: Read `salesforce-trigger-framework/SKILL.md` for naming conventions and architecture.

### TAF Test Naming Convention

All Trigger Action test classes follow PS Advisory naming:

| Component | Naming Pattern | Example |
|-----------|---------------|---------|
| Action Class | `TA_<Object>_<Action>` | `TA_Lead_ValidateRequiredFields` |
| Test Class | `TA_<Object>_<Action>_Test` | `TA_Lead_ValidateRequiredFields_Test` |
| Service Test | `<Object>Service_Test` | `LeadService_Test` |
| DAL Test | `DAL_<Object>_Test` | `DAL_Lead_Test` |

### TAF Test Architecture

Test each layer independently:

```
+-----------------------------------+
|  TA_Lead_SetDefaults_Test         |  <-- Tests DML path (insert/update triggers action)
|    insert lead -> verify defaults |
+-----------------------------------+
           |
+-----------------------------------+
|  LeadService_Test                 |  <-- Tests service logic directly
|    LeadService.setDefaults(list)  |
+-----------------------------------+
           |
+-----------------------------------+
|  DAL_Lead_Test                    |  <-- Tests data access
|    DAL_Lead.getByStatus('Open')   |
+-----------------------------------+
```

### Pattern: Testing a Trigger Action via DML

```apex
@IsTest
private class TA_Lead_SetDefaults_Test {

    @TestSetup
    static void makeData() {
        // Use the shared TestDataFactory (see sf-apex/templates/test-data-factory.cls)
        // Do NOT duplicate factory code here
    }

    @IsTest
    static void testBeforeInsert_SetsDefaultLeadSource() {
        // Arrange
        Lead testLead = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Co'
            // LeadSource intentionally omitted to test default
        );

        // Act
        Test.startTest();
        insert testLead;
        Test.stopTest();

        // Assert
        Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :testLead.Id];
        Assert.areEqual('Web', inserted.LeadSource,
            'Default LeadSource should be set to Web by TA_Lead_SetDefaults');
    }

    @IsTest
    static void testBeforeInsert_DoesNotOverrideExistingSource() {
        // Arrange
        Lead testLead = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Co',
            LeadSource = 'Partner Referral'
        );

        // Act
        Test.startTest();
        insert testLead;
        Test.stopTest();

        // Assert
        Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :testLead.Id];
        Assert.areEqual('Partner Referral', inserted.LeadSource,
            'Existing LeadSource should not be overwritten');
    }

    @IsTest
    static void testBeforeInsert_BulkInsert251Records() {
        // Arrange
        List<Lead> leads = new List<Lead>();
        for (Integer i = 0; i < 251; i++) {
            leads.add(new Lead(
                FirstName = 'Test',
                LastName = 'Lead ' + i,
                Company = 'Test Co ' + i
            ));
        }

        // Act
        Test.startTest();
        insert leads;
        Test.stopTest();

        // Assert
        List<Lead> inserted = [SELECT LeadSource FROM Lead WHERE Id IN :leads];
        Assert.areEqual(251, inserted.size(), 'All 251 leads should be inserted');
        for (Lead l : inserted) {
            Assert.areEqual('Web', l.LeadSource,
                'Default LeadSource should be set for all bulk records');
        }
    }
}
```

### Pattern: Testing Trigger Action Bypass

```apex
@IsTest
static void testBypass_ActionDoesNotFire() {
    // Arrange
    TriggerBase.bypass('TA_Lead_SetDefaults');

    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Lead',
        Company = 'Test Co'
    );

    // Act
    Test.startTest();
    insert testLead;
    Test.stopTest();

    // Assert
    Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :testLead.Id];
    Assert.isNull(inserted.LeadSource,
        'LeadSource should remain null when action is bypassed');

    // Cleanup
    TriggerBase.clearBypass('TA_Lead_SetDefaults');
}
```

### Pattern: Testing Service Layer Directly (Unit-Style)

```apex
@IsTest
private class LeadService_Test {

    @IsTest
    static void testSetDefaults_NullLeadSource_SetsDefault() {
        // Arrange - no DML, test service logic directly
        List<Lead> leads = new List<Lead>{
            new Lead(FirstName = 'Test', LastName = 'A', Company = 'Co A'),
            new Lead(FirstName = 'Test', LastName = 'B', Company = 'Co B')
        };

        // Act
        Test.startTest();
        LeadService.setDefaults(leads);
        Test.stopTest();

        // Assert
        for (Lead l : leads) {
            Assert.areEqual('Web', l.LeadSource,
                'Service should set default LeadSource');
        }
    }
}
```

---

## Test Patterns & Templates

### TestDataFactory

> **IMPORTANT**: Do NOT duplicate the TestDataFactory inline. Use the canonical template at:
> `sf-apex/templates/test-data-factory.cls`
>
> That template includes overloaded methods with `doInsert` parameter, User creation
> with profile support, and proper ApexDoc annotations.

**Usage in tests**:
```apex
@TestSetup
static void makeData() {
    List<Account> accounts = TestDataFactory.createAccounts(5);
    // accounts are already inserted by default
    List<Contact> contacts = TestDataFactory.createContacts(3, accounts[0].Id);
}
```

**Creating without insert** (for before-trigger testing):
```apex
// Pass false to skip insert - useful for testing before-insert logic
List<Account> accounts = TestDataFactory.createAccounts(5, false);
```

### Pattern 1: Basic Test Class (Given-When-Then)

```apex
@IsTest
private class AccountServiceTest {

    @TestSetup
    static void setupTestData() {
        List<Account> accounts = TestDataFactory.createAccounts(5);
    }

    @IsTest
    static void testCreateAccount_ValidInput_ReturnsId() {
        // Given
        Account testAccount = new Account(Name = 'Test Account');

        // When
        Test.startTest();
        Id accountId = AccountService.createAccount(testAccount);
        Test.stopTest();

        // Then
        Assert.isNotNull(accountId, 'Account ID should not be null');
        Account inserted = [SELECT Name FROM Account WHERE Id = :accountId];
        Assert.areEqual('Test Account', inserted.Name, 'Account name should match');
    }

    @IsTest
    static void testCreateAccount_NullInput_ThrowsException() {
        // Given
        Account nullAccount = null;

        // When/Then
        try {
            Test.startTest();
            AccountService.createAccount(nullAccount);
            Test.stopTest();
            Assert.fail('Expected IllegalArgumentException was not thrown');
        } catch (IllegalArgumentException e) {
            Assert.isTrue(e.getMessage().contains('cannot be null'),
                'Error message should mention null: ' + e.getMessage());
        }
    }
}
```

### Pattern 2: Bulk Test (251+ Records)

```apex
@IsTest
static void testBulkInsert_251Records_NoGovernorLimits() {
    // Given - 251 records crosses the 200-record batch boundary
    List<Account> accounts = TestDataFactory.createAccounts(251, false);

    // When
    Test.startTest();
    insert accounts;  // Triggers fire in batches of 200, then 51
    Test.stopTest();

    // Then
    Integer count = [SELECT COUNT() FROM Account WHERE Id IN :accounts];
    Assert.areEqual(251, count, 'All 251 accounts should be inserted');

    // Verify no governor limits approached
    Assert.isTrue(Limits.getQueries() < 100,
        'Should not approach SOQL limit: ' + Limits.getQueries());
}
```

### Pattern 3: Mock HTTP Callout Test

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

## StubProvider and Mocking Patterns

### When to Use StubProvider

Use `System.StubProvider` when you need to:
- Test a class in **isolation** without DML (true unit testing)
- Mock a **dependency** that makes callouts, SOQL, or DML
- Create **faster tests** that avoid database operations (up to 35x speedup)
- Test code that depends on another class's **internal state**

### Pattern: StubProvider for Service Dependencies

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

### Using StubProvider in Tests

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

### Pattern: DML Abstraction for Faster Tests

Instead of hitting the database, abstract DML operations behind an interface:

```apex
/**
 * Interface for DML operations. Production uses DatabaseDml;
 * tests can use MockDml to avoid database hits.
 */
public interface IDml {
    List<Database.SaveResult> doInsert(List<SObject> records);
    List<Database.SaveResult> doUpdate(List<SObject> records);
    List<Database.DeleteResult> doDelete(List<SObject> records);
}

/** Production implementation - real DML */
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

/** Test mock - captures DML calls without hitting database */
@IsTest
public class MockDml implements IDml {
    public List<SObject> insertedRecords = new List<SObject>();
    public List<SObject> updatedRecords = new List<SObject>();
    public List<SObject> deletedRecords = new List<SObject>();

    public List<Database.SaveResult> doInsert(List<SObject> records) {
        insertedRecords.addAll(records);
        // Return synthetic success results
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

**Using DML abstraction in tests**:
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

---

## @TestVisible Annotation Patterns

Use `@TestVisible` to expose private members to test classes without changing the public API.

### When to Use @TestVisible

| Use Case | Example | Rationale |
|----------|---------|-----------|
| Private helper methods | `@TestVisible private static Decimal calculateScore(...)` | Test internal logic without making it public |
| Private variables for injection | `@TestVisible private static IDml dmlLayer` | Inject mocks without public setters |
| Private constants for assertions | `@TestVisible private static final String ERROR_MSG` | Assert against the exact message |
| Inner classes | `@TestVisible private class ValidationResult` | Test return types without exposure |

### Pattern: @TestVisible for Dependency Injection

```apex
public class LeadScoringService {

    // Private by default, but test can override for mocking
    @TestVisible
    private static ILeadScorer scorer = new DefaultLeadScorer();

    @TestVisible
    private static IDml dml = new DatabaseDml();

    public static void scoreLeads(List<Lead> leads) {
        for (Lead l : leads) {
            l.Rating = scorer.calculateRating(l);
        }
        dml.doUpdate(leads);
    }
}
```

**Test using @TestVisible injection**:
```apex
@IsTest
private class LeadScoringService_Test {

    private class MockScorer implements ILeadScorer {
        public String calculateRating(Lead l) {
            return 'Hot';
        }
    }

    @IsTest
    static void testScoreLeads_UsesInjectedScorer() {
        // Arrange - inject mock via @TestVisible
        LeadScoringService.scorer = new MockScorer();
        LeadScoringService.dml = new MockDml();

        List<Lead> leads = new List<Lead>{
            new Lead(FirstName = 'Test', LastName = 'Lead', Company = 'Co')
        };

        // Act
        Test.startTest();
        LeadScoringService.scoreLeads(leads);
        Test.stopTest();

        // Assert
        Assert.areEqual('Hot', leads[0].Rating,
            'Rating should be set by mock scorer');
    }
}
```

### Pattern: @TestVisible for Private Method Testing

```apex
public class AccountService {

    // Complex private calculation that needs direct testing
    @TestVisible
    private static Decimal calculateWeightedScore(
        Decimal revenue, Decimal employees, Decimal engagementScore
    ) {
        if (revenue == null || employees == null) {
            return 0;
        }
        return (revenue * 0.5) + (employees * 0.3) + (engagementScore * 0.2);
    }

    public static void updateAccountScores(List<Account> accounts) {
        for (Account a : accounts) {
            a.Score__c = calculateWeightedScore(
                a.AnnualRevenue, a.NumberOfEmployees, a.Engagement_Score__c
            );
        }
    }
}
```

**Direct private method test**:
```apex
@IsTest
static void testCalculateWeightedScore_ValidInputs_ReturnsWeighted() {
    // Directly test private method via @TestVisible
    Decimal result = AccountService.calculateWeightedScore(100000, 50, 80);

    // Expected: (100000 * 0.5) + (50 * 0.3) + (80 * 0.2) = 50015 + 16 = 50031
    Assert.areEqual(50031.0, result, 'Weighted score calculation should be correct');
}

@IsTest
static void testCalculateWeightedScore_NullRevenue_ReturnsZero() {
    Decimal result = AccountService.calculateWeightedScore(null, 50, 80);
    Assert.areEqual(0, result, 'Null revenue should return zero score');
}
```

### Anti-Pattern: Do NOT Overuse @TestVisible

```apex
// BAD - making everything @TestVisible defeats encapsulation
public class BadExample {
    @TestVisible private String name;           // too much exposure
    @TestVisible private Integer count;          // too much exposure
    @TestVisible private void helperOne() {}     // not needed if tested through public API
    @TestVisible private void helperTwo() {}     // not needed if tested through public API
}

// GOOD - only expose what truly cannot be tested through public methods
public class GoodExample {
    private String name;
    private Integer count;

    @TestVisible
    private static IDml dml = new DatabaseDml();  // OK: dependency injection

    public void processRecords(List<Account> accounts) {
        // name and count are tested indirectly through this public method
    }
}
```

---

## System.runAs() Permission Testing Patterns

### When to Use System.runAs()

| Scenario | Why System.runAs() |
|----------|--------------------|
| Testing record sharing rules | Verify users can/cannot see records |
| Testing CRUD/FLS enforcement | Verify `WITH SECURITY_ENFORCED` or `stripInaccessible` |
| Testing profile-based logic | Verify different behavior per profile |
| Resolving MIXED_DML_OPERATION | Separate setup-object DML from non-setup |
| Testing custom permissions | Verify bypass/required permission logic |
| Testing trigger action bypasses | Verify permission-based TAF bypass mechanisms |

### Important Limitation

> **System.runAs() does NOT enforce field-level security or object CRUD permissions in Apex.**
> It only enforces **record-level sharing**. To test FLS/CRUD, your code must explicitly
> use `Schema.sObjectType.X.isAccessible()`, `WITH SECURITY_ENFORCED`, or
> `Security.stripInaccessible()` -- then System.runAs() will control what the schema
> checks return.

### Pattern: Testing Profile-Based Access

```apex
@IsTest
private class AccountService_Security_Test {

    @IsTest
    static void testQueryAccounts_StandardUser_RespectsSharing() {
        // Arrange - create user with Standard User profile
        User stdUser = TestDataFactory.createUser('Standard User');

        Account privateAccount = new Account(Name = 'Private Corp');
        insert privateAccount;

        // Act - query as standard user (sharing enforced)
        List<Account> results;
        System.runAs(stdUser) {
            Test.startTest();
            results = AccountService.getMyAccounts();
            Test.stopTest();
        }

        // Assert - standard user should not see account they don't own
        Assert.areEqual(0, results.size(),
            'Standard user should not see accounts owned by other users');
    }

    @IsTest
    static void testQueryAccounts_AdminUser_SeesAll() {
        // Arrange
        User adminUser = TestDataFactory.createUser('System Administrator');

        Account testAccount = new Account(Name = 'Visible Corp');
        insert testAccount;

        // Act
        List<Account> results;
        System.runAs(adminUser) {
            Test.startTest();
            results = AccountService.getMyAccounts();
            Test.stopTest();
        }

        // Assert - admin sees all
        Assert.isTrue(results.size() > 0,
            'Admin user should see all accounts');
    }
}
```

### Pattern: Testing Custom Permissions (TAF Bypass)

```apex
@IsTest
static void testTriggerBypass_UserWithBypassPermission_SkipsAction() {
    // Arrange - create user and assign bypass permission set
    User bypassUser = TestDataFactory.createUser('Standard User');

    // Assign the permission set that grants the bypass custom permission
    PermissionSet ps = [SELECT Id FROM PermissionSet
        WHERE Name = 'Bypass_Lead_Triggers' LIMIT 1];
    insert new PermissionSetAssignment(
        AssigneeId = bypassUser.Id,
        PermissionSetId = ps.Id
    );

    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Bypass',
        Company = 'Bypass Co'
    );

    // Act - insert as bypass user
    System.runAs(bypassUser) {
        Test.startTest();
        insert testLead;
        Test.stopTest();
    }

    // Assert - trigger action should not have fired
    Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :testLead.Id];
    Assert.isNull(inserted.LeadSource,
        'Trigger action should be bypassed for user with bypass permission');
}
```

### Pattern: Resolving MIXED_DML_OPERATION

```apex
@IsTest
static void testUserCreationWithData() {
    // Setup objects (User, PermissionSetAssignment) must be in separate
    // transaction from non-setup objects (Account, Lead, etc.)

    User testUser;
    System.runAs(new User(Id = UserInfo.getUserId())) {
        // Create user in runAs block to isolate DML
        testUser = TestDataFactory.createUser('Standard User');
    }

    // Now safely perform non-setup DML
    System.runAs(testUser) {
        Account a = new Account(Name = 'Test Account');
        insert a;

        Assert.isNotNull(a.Id, 'Account should be created by test user');
    }
}
```

---

## Test Suite Management (ApexTestSuite)

### What Are Test Suites?

`ApexTestSuite` is a metadata type that groups test classes for targeted execution. Use suites to:
- Run a specific set of tests before deployment
- Organize tests by feature, team, or object
- Speed up CI/CD by running only relevant tests

### Creating a Test Suite (Metadata)

**File path**: `force-app/main/default/testSuites/<SuiteName>.testSuite-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexTestSuite xmlns="http://soap.sforce.com/2006/04/metadata">
    <testClassName>TA_Lead_SetDefaults_Test</testClassName>
    <testClassName>TA_Lead_ValidateRequiredFields_Test</testClassName>
    <testClassName>LeadService_Test</testClassName>
    <testClassName>DAL_Lead_Test</testClassName>
</ApexTestSuite>
```

### Recommended Suite Organization

| Suite Name | Contents | Use Case |
|------------|----------|----------|
| `SmokeTests` | Critical path tests, one per major feature | Pre-deployment sanity check |
| `LeadTests` | All Lead-related TA_*, Service, DAL tests | After Lead changes |
| `OpportunityTests` | All Opportunity-related tests | After Opp changes |
| `IntegrationTests` | Callout mocks, platform event tests | After integration changes |
| `FullRegression` | All test classes | Release validation |

### Running a Suite

```bash
# Run a named test suite
sf apex run test --suite-names LeadTests --code-coverage --result-format json --target-org [alias]

# Run multiple suites
sf apex run test --suite-names LeadTests --suite-names OpportunityTests --code-coverage --result-format json --target-org [alias]
```

### Deploying Test Suites

```bash
# Deploy suite metadata to org
sf project deploy start --source-dir force-app/main/default/testSuites --target-org [alias]
```

### Suite Best Practice: Feature-Aligned Suites for CI/CD

In a CI/CD pipeline, run only the tests that cover changed components:

```bash
# Example: after changing Lead trigger actions, run only Lead suite
sf apex run test --suite-names LeadTests --code-coverage --result-format json --target-org [alias]

# For full deployment validation, run all local tests
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --target-org [alias]
```

---

## Parallel Test Execution Gotchas

### Understanding Parallel Execution

By default, Salesforce runs test classes **in parallel** across multiple threads. This is faster but introduces concurrency issues.

### UNABLE_TO_LOCK_ROW: Root Causes

| Cause | Example | Solution |
|-------|---------|----------|
| **Shared record contention** | Two tests update the same Account | Each test creates its own data |
| **Duplicate unique field values** | Tests insert records with same Email | Use dynamic unique values (e.g., `DateTime.now().getTime()`) |
| **Custom Settings access** | Parallel tests read/write same Custom Setting | Use `@TestSetup` or avoid shared Custom Settings |
| **Standard Price Book** | Multiple tests access `Test.getStandardPricebookId()` | Use `FOR UPDATE` or serialize tests |
| **Trigger on shared metadata** | Triggers updating shared config records | Isolate with `@IsTest(SeeAllData=false)` |

### Preventing Lock Row Errors

**Strategy 1: Create all data in test (no org data dependency)**
```apex
@IsTest(SeeAllData=false)  // This is the default, but be explicit
private class MyTest {
    @TestSetup
    static void makeData() {
        // Every test creates its own isolated data
        TestDataFactory.createAccounts(5);
    }
}
```

**Strategy 2: Use unique values to avoid index collisions**
```apex
public static List<Contact> createContacts(Integer count, Id accountId) {
    String uniqueKey = String.valueOf(Crypto.getRandomLong());
    List<Contact> contacts = new List<Contact>();
    for (Integer i = 0; i < count; i++) {
        contacts.add(new Contact(
            FirstName = 'Test',
            LastName = 'Contact_' + uniqueKey + '_' + i,
            Email = 'test_' + uniqueKey + '_' + i + '@example.com'
        ));
    }
    return contacts;
}
```

**Strategy 3: Run specific test class synchronously (disables parallel)**
```bash
sf apex run test --class-names ProblematicTest --synchronous --code-coverage --result-format json --target-org [alias]
```

**Strategy 4: Mark a test class as safe for parallel execution**
```apex
@IsTest(isParallel=true)
private class FastUnitTest {
    // This test is explicitly safe for parallel execution
    // Use for tests that create all their own data and have no shared state
}
```

**Strategy 5: Disable parallel testing org-wide (last resort)**
```
Setup > Apex Test Execution > Options > Disable Parallel Apex Testing
```

### Lock Row Decision Tree

```
Test fails with UNABLE_TO_LOCK_ROW?
  |
  +-- Does the test use SeeAllData=true?
  |     YES -> Remove SeeAllData, create test data
  |
  +-- Do multiple tests insert records with the same unique field value?
  |     YES -> Add random/unique suffixes to field values
  |
  +-- Does the test access Custom Settings?
  |     YES -> Create test-specific Custom Settings in @TestSetup
  |
  +-- Does the test access Standard Price Book?
  |     YES -> Run synchronously with --synchronous flag
  |
  +-- None of the above?
        -> Run with --synchronous as workaround
        -> File a case if it only happens in parallel
```

---

## Best Practices (120-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Test Coverage** | 25 | 95%+ class coverage; all public methods tested; edge cases covered |
| **Assertion Quality** | 25 | Assert class used; meaningful messages; positive AND negative tests |
| **Bulk Testing** | 20 | Test with 251+ records; verify no SOQL/DML in loops under load |
| **Test Data** | 20 | TestDataFactory used (from sf-apex template); no hardcoded IDs; @TestSetup for efficiency |
| **Isolation** | 15 | SeeAllData=false; no org dependencies; mock external callouts; no UNABLE_TO_LOCK_ROW |
| **Documentation** | 15 | Method names describe scenario; `test<Method>_<Scenario>_<Expected>` convention |

**Scoring Thresholds**:
```
108-120 pts (90%+)  -> Production Ready
 96-107 pts (80-89%) -> Good, minor improvements
 84-95 pts  (70-79%) -> Acceptable, needs work
 72-83 pts  (60-69%) -> Below standard
 <72 pts   (<60%)   -> BLOCKED - Major issues
```

---

## TESTING GUARDRAILS (MANDATORY)

**BEFORE running tests, verify:**

| Check | Command | Why |
|-------|---------|-----|
| Org authenticated | `sf org display --target-org [alias]` | Tests need valid org connection |
| Classes deployed | `sf project deploy report --target-org [alias]` | Cannot test undeployed code |
| Test data exists | Check @TestSetup or TestDataFactory | Tests need data to operate on |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| `@IsTest(SeeAllData=true)` | Tests depend on org data, break in clean orgs | Always `SeeAllData=false` (default) |
| Hardcoded Record IDs | IDs differ between orgs | Query or create in test |
| No assertions | Tests pass without validating anything | Assert every expected outcome |
| Single record tests only | Misses bulk trigger issues | Always test with 200+ records |
| `Test.startTest()` without `Test.stopTest()` | Async code won't execute | Always pair start/stop |
| Duplicate TestDataFactory code | Maintenance burden, divergence risk | Use `sf-apex/templates/test-data-factory.cls` |
| `@TestVisible` on everything | Breaks encapsulation, hides design issues | Only for dependency injection and true private logic |
| Ignoring UNABLE_TO_LOCK_ROW | Flaky CI/CD pipeline | Use unique values and proper data isolation |

---

## CLI Command Reference

### Test Execution Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `sf apex run test` | Run tests | See examples above |
| `sf apex get test` | Get async test status | `sf apex get test --test-run-id 707xx...` |
| `sf apex list log` | List debug logs | `sf apex list log --target-org alias` |
| `sf apex tail log` | Stream logs real-time | `sf apex tail log --target-org alias` |

### Useful Flags

| Flag | Purpose |
|------|---------|
| `--code-coverage` | Include coverage in results |
| `--detailed-coverage` | Line-by-line coverage (slower) |
| `--result-format json` | Machine-parseable output |
| `--output-dir` | Save results to directory |
| `--synchronous` | Wait for completion; disables parallel execution |
| `--test-level RunLocalTests` | All tests except managed packages |
| `--test-level RunAllTestsInOrg` | Every test including packages |
| `--suite-names` | Run a named test suite |

---

## Agentic Test-Fix Loop Implementation

### How It Works

When the agentic loop is enabled, sf-testing will:

1. **Run tests** and capture results
2. **Parse failures** to identify error type and location
3. **Read source files** (test class + class under test)
4. **Analyze root cause** using the decision tree above
5. **Generate fix** by invoking sf-apex skill
6. **Re-run failing test** to verify fix
7. **Iterate** until passing or max attempts (3)

### Example Agentic Flow

```
User: "Run tests for AccountService with auto-fix enabled"

Claude:
1. sf apex run test --class-names AccountServiceTest --code-coverage --result-format json
2. Parse results: 1 failure - testBulkInsert line 45 NullPointerException
3. Read AccountServiceTest.cls (line 45 context)
4. Read AccountService.cls (trace the null reference)
5. Identify: Missing null check in AccountService.processAccounts()
6. Skill(sf-apex): Add null safety to AccountService.processAccounts()
7. Deploy fix
8. Re-run: sf apex run test --tests AccountServiceTest.testBulkInsert
9. Passing! Report success.
```

---

## Common Test Failures & Fixes

| Failure | Likely Cause | Fix |
|---------|--------------|-----|
| `MIXED_DML_OPERATION` | User + non-setup object in same transaction | Use `System.runAs()` to separate transactions |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | Trigger or flow error | Check trigger logic with debug logs |
| `REQUIRED_FIELD_MISSING` | Test data incomplete | Add required fields to TestDataFactory |
| `DUPLICATE_VALUE` | Unique field conflict | Use dynamic values with `Crypto.getRandomLong()` |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule fired | Meet validation criteria in test data |
| `UNABLE_TO_LOCK_ROW` | Record lock conflict in parallel execution | Create isolated data; use unique values; run `--synchronous` |
| `TOO_MANY_SOQL_QUERIES` | SOQL in loops or excessive trigger recursion | Bulkify code; check for recursive triggers |
| `ENTITY_IS_DELETED` | Test references deleted record | Verify record lifecycle in test; check trigger delete logic |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex (for auto-fix and TestDataFactory template), sf-data (for bulk test data), sf-debug (for log analysis), salesforce-trigger-framework (for TAF testing patterns)

Install: `/plugin install github:Jaganpro/sf-skills/sf-testing`

---

## Documentation

| Document | Description |
|----------|-------------|
| [testing-best-practices.md](docs/testing-best-practices.md) | General testing guidelines |
| [cli-commands.md](docs/cli-commands.md) | SF CLI test commands |
| [mocking-patterns.md](docs/mocking-patterns.md) | Mocking vs Stubbing, DML mocking, HttpCalloutMock |
| [performance-optimization.md](docs/performance-optimization.md) | Fast tests, reduce execution time |

## Templates

| Template | Description |
|----------|-------------|
| [basic-test.cls](templates/basic-test.cls) | Standard test class with Given-When-Then |
| [bulk-test.cls](templates/bulk-test.cls) | 251+ record bulk testing |
| [mock-callout-test.cls](templates/mock-callout-test.cls) | HTTP callout mocking |
| [test-data-factory.cls](sf-apex/templates/test-data-factory.cls) | **Canonical** - Reusable test data creation (shared with sf-apex) |
| [dml-mock.cls](templates/dml-mock.cls) | DML abstraction for 35x faster tests |
| [stub-provider-example.cls](templates/stub-provider-example.cls) | StubProvider for dynamic behavior |

---

## Sources

The patterns and guidance in this skill are informed by:

- [Apex Developer Guide: Testing Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_best_practices.htm) - Salesforce official testing documentation
- [Apex Developer Guide: StubProvider Interface](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_interface_System_StubProvider.htm) - Official StubProvider reference
- [Apex Developer Guide: Build a Mocking Framework with the Stub API](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_stub_api.htm) - Official mocking framework guide
- [Apex Developer Guide: Using the runAs Method](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_tools_runas.htm) - Official System.runAs() documentation
- [Apex Developer Guide: TestVisible Annotation](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_annotation_testvisible.htm) - Official @TestVisible reference
- [ApexTestSuite Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_apextestsuite.htm) - Official test suite metadata reference
- [Apex Developer Guide: Code Coverage Best Practices](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_code_coverage_best_pract.htm) - Official coverage guidance
- [Trailhead: Mock and Stub Objects](https://trailhead.salesforce.com/content/learn/modules/unit-testing-on-the-lightning-platform/mock-stub-objects) - Interactive mocking tutorial
- [Trailhead: Permission-Based Tests](https://trailhead.salesforce.com/content/learn/modules/unit-testing-on-the-lightning-platform/permission-based-tests) - Security testing patterns
- [fflib-apex-mocks](https://github.com/apex-enterprise-patterns/fflib-apex-mocks) - Enterprise mocking framework with Stub API support
- [Amoss Framework](https://github.com/bobalicious/amoss) - Apex Mock Objects, Spies and Stubs
- [Gearset: UNABLE_TO_LOCK_ROW Troubleshooting](https://docs.gearset.com/en/articles/9943367-troubleshooting-error-unable_to_lock_row-unable-to-obtain-exclusive-access-to-this-record-in-unit-test-jobs) - Parallel test execution lock diagnostics
- [James Simone: Testing Custom Permissions](https://www.jamessimone.net/blog/joys-of-apex/testing-custom-permissions/) - Advanced permission testing patterns

---

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments of community resources that shaped this skill.

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
