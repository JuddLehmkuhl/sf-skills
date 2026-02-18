# Testing Trigger Actions Framework (TAF) Components

> Referenced from: `sf-testing/SKILL.md`
> Prerequisite: Read `salesforce-trigger-framework/SKILL.md` for naming conventions and architecture.

---

## TAF Test Architecture

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

---

## Pattern: Testing a Trigger Action via DML

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

---

## Pattern: Testing Trigger Action Bypass

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

---

## Pattern: Testing Service Layer Directly (Unit-Style)

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
