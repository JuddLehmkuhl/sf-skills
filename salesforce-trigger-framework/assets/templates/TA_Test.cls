/**
 * @description Test class for TA_{{ObjectName}}_{{ActionName}}
 * @author      {{Author}}
 * @date        {{Date}}
 */
@IsTest
private class TA_{{ObjectName}}_{{ActionName}}_Test {
    
    // ═══════════════════════════════════════════════════════════════════════
    // TEST SETUP
    // ═══════════════════════════════════════════════════════════════════════
    
    @TestSetup
    static void makeData() {
        // Create shared test data using TestDataFactory
        // Example:
        // Account acc = TestDataFactory.createAccount();
        // insert acc;
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // POSITIVE TESTS
    // ═══════════════════════════════════════════════════════════════════════
    
    @IsTest
    static void test{{ActionName}}_standardScenario_expectedBehavior() {
        // Arrange
        {{ObjectName}} record = new {{ObjectName}}(
            // Set required fields
        );
        
        // Act
        Test.startTest();
        insert record;
        Test.stopTest();
        
        // Assert
        {{ObjectName}} result = [
            SELECT Id /* add fields to verify */
            FROM {{ObjectName}}
            WHERE Id = :record.Id
        ];
        // System.assertEquals(expected, result.Field__c, 'Assertion message');
    }
    
    @IsTest
    static void test{{ActionName}}_withoutDML_unitTest() {
        // Arrange - Create record without inserting
        {{ObjectName}} record = new {{ObjectName}}(
            // Set required fields
        );
        List<{{ObjectName}}> records = new List<{{ObjectName}}>{ record };
        
        // Act - Call action directly without DML
        TA_{{ObjectName}}_{{ActionName}} action = new TA_{{ObjectName}}_{{ActionName}}();
        action.beforeInsert(records); // Adjust method based on context
        
        // Assert - Verify in-memory changes
        // System.assertEquals(expected, record.Field__c, 'Assertion message');
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // NEGATIVE TESTS
    // ═══════════════════════════════════════════════════════════════════════
    
    @IsTest
    static void test{{ActionName}}_invalidData_throwsError() {
        // Arrange
        {{ObjectName}} record = new {{ObjectName}}(
            // Set invalid data
        );
        
        // Act & Assert
        Test.startTest();
        try {
            insert record;
            System.assert(false, 'Expected DmlException was not thrown');
        } catch (DmlException e) {
            System.assert(e.getMessage().contains('expected error text'),
                'Error message should contain expected text');
        }
        Test.stopTest();
    }
    
    @IsTest
    static void test{{ActionName}}_nullValues_handlesGracefully() {
        // Arrange
        {{ObjectName}} record = new {{ObjectName}}(
            // Set minimal required fields, leave others null
        );
        List<{{ObjectName}}> records = new List<{{ObjectName}}>{ record };
        
        // Act - Should not throw exception
        TA_{{ObjectName}}_{{ActionName}} action = new TA_{{ObjectName}}_{{ActionName}}();
        action.beforeInsert(records); // Adjust method based on context
        
        // Assert - No exception thrown
        System.assert(true, 'Null values should be handled gracefully');
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // BULK TESTS
    // ═══════════════════════════════════════════════════════════════════════
    
    @IsTest
    static void test{{ActionName}}_bulkInsert_handlesGovernorLimits() {
        // Arrange
        List<{{ObjectName}}> records = new List<{{ObjectName}}>();
        for (Integer i = 0; i < 200; i++) {
            records.add(new {{ObjectName}}(
                // Set required fields with unique values using i
            ));
        }
        
        // Act
        Test.startTest();
        insert records;
        Integer queriesUsed = Limits.getQueries();
        Integer dmlUsed = Limits.getDmlStatements();
        Test.stopTest();
        
        // Assert
        System.assertEquals(200, [SELECT COUNT() FROM {{ObjectName}}],
            'All 200 records should be inserted');
        System.assert(queriesUsed < 50,
            'Should use minimal queries. Used: ' + queriesUsed);
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // BYPASS TESTS
    // ═══════════════════════════════════════════════════════════════════════
    
    @IsTest
    static void test{{ActionName}}_whenBypassed_doesNotExecute() {
        // Arrange
        {{ObjectName}} record = new {{ObjectName}}(
            // Set required fields
        );
        
        // Bypass the action
        TriggerBase.bypass('TA_{{ObjectName}}_{{ActionName}}');
        
        Test.startTest();
        try {
            insert record;
        } finally {
            TriggerBase.clearBypass('TA_{{ObjectName}}_{{ActionName}}');
        }
        Test.stopTest();
        
        // Assert - Verify action did NOT run
        {{ObjectName}} result = [
            SELECT Id /* add fields to verify */
            FROM {{ObjectName}}
            WHERE Id = :record.Id
        ];
        // System.assertEquals(null, result.Field__c, 
        //     'Field should be null when action is bypassed');
    }
}
