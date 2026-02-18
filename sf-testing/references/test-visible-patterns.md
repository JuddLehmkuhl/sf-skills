# @TestVisible Annotation Patterns

> Referenced from: `sf-testing/SKILL.md`

---

## When to Use @TestVisible

| Use Case | Example | Rationale |
|----------|---------|-----------|
| Private helper methods | `@TestVisible private static Decimal calculateScore(...)` | Test internal logic without making it public |
| Private variables for injection | `@TestVisible private static IDml dmlLayer` | Inject mocks without public setters |
| Private constants for assertions | `@TestVisible private static final String ERROR_MSG` | Assert against the exact message |
| Inner classes | `@TestVisible private class ValidationResult` | Test return types without exposure |

---

## Pattern: Dependency Injection via @TestVisible

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

---

## Pattern: Private Method Testing

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
    Decimal result = AccountService.calculateWeightedScore(100000, 50, 80);
    Assert.areEqual(50031.0, result, 'Weighted score calculation should be correct');
}

@IsTest
static void testCalculateWeightedScore_NullRevenue_ReturnsZero() {
    Decimal result = AccountService.calculateWeightedScore(null, 50, 80);
    Assert.areEqual(0, result, 'Null revenue should return zero score');
}
```

---

## Anti-Pattern: Overusing @TestVisible

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
