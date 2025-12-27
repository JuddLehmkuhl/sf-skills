# Testing Patterns for Trigger Actions

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Class Structure](#test-class-structure)
3. [Testing Without DML](#testing-without-dml)
4. [Testing with DML](#testing-with-dml)
5. [Bypass Testing](#bypass-testing)
6. [Negative Testing](#negative-testing)
7. [Bulk Testing](#bulk-testing)
8. [Service Layer Testing](#service-layer-testing)
9. [Test Data Factory Pattern](#test-data-factory-pattern)
10. [Coverage Requirements](#coverage-requirements)

## Testing Philosophy

### PS Advisory Testing Standards

- **95%+ code coverage** minimum (not 75%)
- **Every trigger action** has a dedicated test class
- **Positive and negative** test cases required
- **Bulk testing** with 200+ records for governor limit validation
- **Bypass mechanisms** must be tested

### Test Class Naming

```
Trigger Action: TA_Lead_ValidateRequiredFields
Test Class:     TA_Lead_ValidateRequiredFields_Test
```

## Test Class Structure

### Standard Template

```apex
@IsTest
private class TA_<ObjectName>_<Action>_Test {
    
    // ═══════════════════════════════════════════════════════════════
    // TEST SETUP
    // ═══════════════════════════════════════════════════════════════
    
    @TestSetup
    static void makeData() {
        // Create shared test data
        // Use TestDataFactory for complex objects
    }
    
    // ═══════════════════════════════════════════════════════════════
    // POSITIVE TESTS
    // ═══════════════════════════════════════════════════════════════
    
    @IsTest
    static void testAction_standardScenario_expectedBehavior() {
        // Arrange
        
        // Act
        Test.startTest();
        // DML or direct method call
        Test.stopTest();
        
        // Assert
    }
    
    // ═══════════════════════════════════════════════════════════════
    // NEGATIVE TESTS
    // ═══════════════════════════════════════════════════════════════
    
    @IsTest
    static void testAction_invalidData_throwsError() {
        // Test validation errors, edge cases
    }
    
    // ═══════════════════════════════════════════════════════════════
    // BULK TESTS
    // ═══════════════════════════════════════════════════════════════
    
    @IsTest
    static void testAction_bulkInsert_handlesGovernorLimits() {
        // Test with 200+ records
    }
    
    // ═══════════════════════════════════════════════════════════════
    // BYPASS TESTS
    // ═══════════════════════════════════════════════════════════════
    
    @IsTest
    static void testAction_whenBypassed_doesNotExecute() {
        // Test bypass mechanisms
    }
}
```

## Testing Without DML

The Trigger Actions Framework supports testing action logic **without performing DML**. This is faster and allows isolated unit testing.

### Pattern: Direct Method Invocation

```apex
@IsTest
private class TA_Lead_SetDefaults_Test {
    
    @IsTest
    static void testBeforeInsert_blankLeadSource_setsDefault() {
        // Arrange
        Lead testLead = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company'
            // LeadSource intentionally blank
        );
        List<Lead> newList = new List<Lead>{ testLead };
        
        // Act - Direct method call, NO DML
        TA_Lead_SetDefaults action = new TA_Lead_SetDefaults();
        action.beforeInsert(newList);
        
        // Assert
        System.assertEquals('Web', testLead.LeadSource, 'Default LeadSource should be set');
    }
    
    @IsTest
    static void testBeforeInsert_existingLeadSource_preservesValue() {
        // Arrange
        Lead testLead = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company',
            LeadSource = 'Referral'
        );
        List<Lead> newList = new List<Lead>{ testLead };
        
        // Act
        TA_Lead_SetDefaults action = new TA_Lead_SetDefaults();
        action.beforeInsert(newList);
        
        // Assert
        System.assertEquals('Referral', testLead.LeadSource, 'Existing LeadSource should be preserved');
    }
}
```

### Benefits of No-DML Testing

- **Faster execution**: No database operations
- **Isolated testing**: Tests only the action logic
- **No side effects**: Other triggers/flows don't fire
- **Easier debugging**: Failures are localized

## Testing with DML

For integration testing and verifying the full trigger chain:

```apex
@IsTest
private class TA_Lead_SetDefaults_Test {
    
    @IsTest
    static void testIntegration_insertLead_triggersAction() {
        // Arrange
        Lead testLead = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company'
        );
        
        // Act
        Test.startTest();
        insert testLead;
        Test.stopTest();
        
        // Assert - Query to get actual values
        Lead insertedLead = [SELECT Id, LeadSource FROM Lead WHERE Id = :testLead.Id];
        System.assertEquals('Web', insertedLead.LeadSource, 'Trigger should set default LeadSource');
    }
}
```

## Bypass Testing

### Testing Code-Level Bypass

```apex
@IsTest
static void testAction_whenBypassed_doesNotExecute() {
    // Arrange
    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Lead',
        Company = 'Test Company'
    );
    
    // Bypass the specific action
    TriggerBase.bypass('TA_Lead_SetDefaults');
    
    // Act
    Test.startTest();
    insert testLead;
    Test.stopTest();
    
    // Assert
    Lead insertedLead = [SELECT Id, LeadSource FROM Lead WHERE Id = :testLead.Id];
    System.assertEquals(null, insertedLead.LeadSource, 'Bypassed action should not set defaults');
    
    // Cleanup
    TriggerBase.clearBypass('TA_Lead_SetDefaults');
}
```

### Testing Object-Level Bypass

```apex
@IsTest
static void testAction_whenObjectBypassed_noActionsExecute() {
    // Arrange
    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Lead',
        Company = 'Test Company'
    );
    
    // Bypass entire object
    MetadataTriggerHandler.bypass('Lead');
    
    // Act
    Test.startTest();
    insert testLead;
    Test.stopTest();
    
    // Assert - No trigger actions ran
    Lead insertedLead = [SELECT Id, LeadSource, Lead_Score__c FROM Lead WHERE Id = :testLead.Id];
    System.assertEquals(null, insertedLead.LeadSource, 'No defaults set when bypassed');
    System.assertEquals(null, insertedLead.Lead_Score__c, 'No scoring when bypassed');
    
    // Cleanup
    MetadataTriggerHandler.clearBypass('Lead');
}
```

## Negative Testing

### Testing Validation Errors

```apex
@IsTest
static void testValidation_missingRequiredField_throwsError() {
    // Arrange
    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Lead'
        // Company intentionally missing
    );
    
    // Act & Assert
    Test.startTest();
    try {
        insert testLead;
        System.assert(false, 'Expected DmlException was not thrown');
    } catch (DmlException e) {
        System.assert(e.getMessage().contains('Company is required'),
            'Error message should indicate missing Company');
    }
    Test.stopTest();
}
```

### Testing Edge Cases

```apex
@IsTest
static void testAction_nullValues_handlesGracefully() {
    // Arrange
    Lead testLead = new Lead(
        FirstName = null,
        LastName = 'Lead',
        Company = 'Test Company'
    );
    List<Lead> newList = new List<Lead>{ testLead };
    
    // Act - Should not throw exception
    TA_Lead_ComputeFullName action = new TA_Lead_ComputeFullName();
    action.beforeInsert(newList);
    
    // Assert
    System.assertEquals('Lead', testLead.Full_Name__c, 'Should handle null FirstName');
}

@IsTest
static void testAction_emptyList_handlesGracefully() {
    // Arrange
    List<Lead> emptyList = new List<Lead>();
    
    // Act - Should not throw exception
    TA_Lead_SetDefaults action = new TA_Lead_SetDefaults();
    action.beforeInsert(emptyList);
    
    // Assert - No exception thrown
    System.assert(true, 'Empty list should be handled gracefully');
}
```

## Bulk Testing

### Testing Governor Limits

```apex
@IsTest
static void testAction_200Records_respectsGovernorLimits() {
    // Arrange
    List<Lead> leads = new List<Lead>();
    for (Integer i = 0; i < 200; i++) {
        leads.add(new Lead(
            FirstName = 'Test' + i,
            LastName = 'Lead' + i,
            Company = 'Company' + i
        ));
    }
    
    // Act
    Test.startTest();
    insert leads;
    Integer queriesUsed = Limits.getQueries();
    Integer dmlUsed = Limits.getDmlStatements();
    Test.stopTest();
    
    // Assert - Verify bulk processing
    System.assertEquals(200, [SELECT COUNT() FROM Lead], 'All records should be inserted');
    System.assert(queriesUsed < 50, 'Should use minimal queries: ' + queriesUsed);
    System.assert(dmlUsed < 10, 'Should use minimal DML statements: ' + dmlUsed);
}
```

### Testing Batch Size Boundaries

```apex
@IsTest
static void testAction_multipleBatches_handlesCorrectly() {
    // Arrange - More than one batch (200 per batch)
    List<Lead> leads = new List<Lead>();
    for (Integer i = 0; i < 450; i++) {
        leads.add(new Lead(
            FirstName = 'Test' + i,
            LastName = 'Lead' + i,
            Company = 'Company' + i
        ));
    }
    
    // Act
    Test.startTest();
    insert leads;
    Test.stopTest();
    
    // Assert
    List<Lead> insertedLeads = [SELECT Id, LeadSource FROM Lead];
    System.assertEquals(450, insertedLeads.size(), 'All records should be inserted');
    
    for (Lead l : insertedLeads) {
        System.assertEquals('Web', l.LeadSource, 'All records should have default LeadSource');
    }
}
```

## Service Layer Testing

### Testing Services Independently

```apex
@IsTest
private class LeadScoringService_Test {
    
    @IsTest
    static void testCalculateScore_highValueLead_returnsHighScore() {
        // Arrange - No DML needed
        Lead testLead = new Lead(
            Industry = 'Technology',
            AnnualRevenue = 10000000,
            NumberOfEmployees = 500
        );
        
        // Act
        Decimal score = LeadScoringService.calculateScore(testLead);
        
        // Assert
        System.assert(score >= 80, 'High value lead should score 80+');
    }
    
    @IsTest
    static void testCalculateScore_lowValueLead_returnsLowScore() {
        // Arrange
        Lead testLead = new Lead(
            Industry = 'Other',
            AnnualRevenue = 10000,
            NumberOfEmployees = 5
        );
        
        // Act
        Decimal score = LeadScoringService.calculateScore(testLead);
        
        // Assert
        System.assert(score <= 30, 'Low value lead should score 30 or less');
    }
}
```

## Test Data Factory Pattern

### TestDataFactory Class

```apex
@IsTest
public class TestDataFactory {
    
    // ═══════════════════════════════════════════════════════════════
    // LEAD
    // ═══════════════════════════════════════════════════════════════
    
    public static Lead createLead() {
        return createLead(new Map<String, Object>());
    }
    
    public static Lead createLead(Map<String, Object> fieldOverrides) {
        Lead l = new Lead(
            FirstName = 'Test',
            LastName = 'Lead',
            Company = 'Test Company',
            Email = 'test@example.com',
            Status = 'New'
        );
        
        for (String field : fieldOverrides.keySet()) {
            l.put(field, fieldOverrides.get(field));
        }
        
        return l;
    }
    
    public static List<Lead> createLeads(Integer count) {
        return createLeads(count, new Map<String, Object>());
    }
    
    public static List<Lead> createLeads(Integer count, Map<String, Object> fieldOverrides) {
        List<Lead> leads = new List<Lead>();
        for (Integer i = 0; i < count; i++) {
            Map<String, Object> overrides = fieldOverrides.clone();
            overrides.put('LastName', 'Lead' + i);
            overrides.put('Company', 'Company' + i);
            leads.add(createLead(overrides));
        }
        return leads;
    }
    
    // ═══════════════════════════════════════════════════════════════
    // ACCOUNT
    // ═══════════════════════════════════════════════════════════════
    
    public static Account createAccount() {
        return createAccount(new Map<String, Object>());
    }
    
    public static Account createAccount(Map<String, Object> fieldOverrides) {
        Account a = new Account(
            Name = 'Test Account',
            Type = 'Customer',
            Industry = 'Technology'
        );
        
        for (String field : fieldOverrides.keySet()) {
            a.put(field, fieldOverrides.get(field));
        }
        
        return a;
    }
    
    // ═══════════════════════════════════════════════════════════════
    // OPPORTUNITY
    // ═══════════════════════════════════════════════════════════════
    
    public static Opportunity createOpportunity(Id accountId) {
        return createOpportunity(accountId, new Map<String, Object>());
    }
    
    public static Opportunity createOpportunity(Id accountId, Map<String, Object> fieldOverrides) {
        Opportunity o = new Opportunity(
            Name = 'Test Opportunity',
            AccountId = accountId,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 10000
        );
        
        for (String field : fieldOverrides.keySet()) {
            o.put(field, fieldOverrides.get(field));
        }
        
        return o;
    }
}
```

### Using TestDataFactory

```apex
@IsTest
private class TA_Opportunity_ValidateAmount_Test {
    
    @TestSetup
    static void makeData() {
        Account acc = TestDataFactory.createAccount();
        insert acc;
    }
    
    @IsTest
    static void testValidation_validAmount_succeeds() {
        // Arrange
        Account acc = [SELECT Id FROM Account LIMIT 1];
        Opportunity opp = TestDataFactory.createOpportunity(acc.Id, new Map<String, Object>{
            'Amount' => 5000
        });
        
        // Act
        Test.startTest();
        insert opp;
        Test.stopTest();
        
        // Assert
        System.assertEquals(1, [SELECT COUNT() FROM Opportunity], 'Opportunity should be inserted');
    }
}
```

## Coverage Requirements

### Minimum Coverage Checklist

For each trigger action, test must cover:

- [ ] **Happy path**: Standard successful execution
- [ ] **Null handling**: Null field values don't cause exceptions
- [ ] **Empty list**: Empty record list is handled gracefully
- [ ] **Bulk insert**: 200+ records process without governor limits
- [ ] **Validation errors**: Expected errors are thrown with correct messages
- [ ] **Bypass**: Action doesn't run when bypassed
- [ ] **Field changes** (update): Only changed records are processed

### Calculating Coverage

```bash
# Run tests with coverage
sf apex run test --class-names TA_Lead_SetDefaults_Test --code-coverage --result-format human --target-org <alias>

# Check overall org coverage
sf apex run test --test-level RunLocalTests --code-coverage --result-format human --target-org <alias>
```

### Coverage Report Interpretation

```
=== Apex Code Coverage
NAME                          COVERED LINES  UNCOVERED LINES  COVERAGE
────────────────────────────  ─────────────  ───────────────  ────────
TA_Lead_SetDefaults           15             0                100%
TA_Lead_ValidateFields        22             2                91%
LeadService                   45             3                93%
DAL_Lead                      12             0                100%
────────────────────────────  ─────────────  ───────────────  ────────
Overall Coverage                                              96%
```

**Target**: Every file ≥ 90%, Overall ≥ 95%
