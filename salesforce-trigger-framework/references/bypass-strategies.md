# Bypass Strategies Reference

## Table of Contents

1. [Bypass Overview](#bypass-overview)
2. [Permission-Based Bypass](#permission-based-bypass)
3. [Code-Level Bypass](#code-level-bypass)
4. [Object-Level Bypass](#object-level-bypass)
5. [Flow Bypass](#flow-bypass)
6. [Bypass Use Cases](#bypass-use-cases)
7. [Bypass Best Practices](#bypass-best-practices)

## Bypass Overview

The Trigger Actions Framework provides multiple bypass mechanisms at different granularities:

| Bypass Type | Granularity | Configuration | Use Case |
|-------------|-------------|---------------|----------|
| Permission-Based | Per action or object | Custom Metadata + Custom Permission | Permanent role-based bypass |
| Code-Level | Per action | Apex code | Data migration scripts |
| Object-Level | All actions on object | Apex code | Bulk data operations |
| Flow Bypass | Per flow | Apex code | Temporary Flow disable |

## Permission-Based Bypass

### Creating a Custom Permission

**File**: `force-app/main/default/customPermissions/Bypass_Lead_Triggers.customPermission-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomPermission xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Bypass Lead Triggers</label>
    <description>Allows user to bypass all Lead trigger actions</description>
    <isLicensed>false</isLicensed>
</CustomPermission>
```

### Configuring Bypass in Metadata

#### Object-Level Bypass Permission

**File**: `force-app/main/default/customMetadata/sObject_Trigger_Setting.Lead.md-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>Lead</label>
    <protected>false</protected>
    <values>
        <field>Object_API_Name__c</field>
        <value xsi:type="xsd:string">Lead</value>
    </values>
    <values>
        <field>Bypass_Permission__c</field>
        <value xsi:type="xsd:string">Bypass_Lead_Triggers</value>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
</CustomMetadata>
```

#### Action-Level Bypass Permission

**File**: `force-app/main/default/customMetadata/Trigger_Action.Lead_Before_Insert_10_SetDefaults.md-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>Lead Before_Insert 10 SetDefaults</label>
    <protected>false</protected>
    <values>
        <field>Apex_Class_Name__c</field>
        <value xsi:type="xsd:string">TA_Lead_SetDefaults</value>
    </values>
    <values>
        <field>Order__c</field>
        <value xsi:type="xsd:double">10</value>
    </values>
    <values>
        <field>Bypass_Permission__c</field>
        <value xsi:type="xsd:string">Bypass_Lead_SetDefaults</value>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>sObject__c</field>
        <value xsi:type="xsd:string">sObject_Trigger_Setting.Lead</value>
    </values>
    <values>
        <field>Flow_Name__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Allow_Flow_Recursion__c</field>
        <value xsi:type="xsd:boolean">false</value>
    </values>
</CustomMetadata>
```

### Assigning Permission via Permission Set

**File**: `force-app/main/default/permissionsets/Data_Migration_User.permissionset-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Data Migration User</label>
    <description>Allows bypassing triggers during data migration</description>
    <hasActivationRequired>false</hasActivationRequired>
    <license>Salesforce</license>
    <customPermissions>
        <enabled>true</enabled>
        <name>Bypass_Lead_Triggers</name>
    </customPermissions>
    <customPermissions>
        <enabled>true</enabled>
        <name>Bypass_Account_Triggers</name>
    </customPermissions>
</PermissionSet>
```

## Code-Level Bypass

### Bypassing a Specific Action

```apex
// Bypass a single action
TriggerBase.bypass('TA_Lead_SetDefaults');

// Perform operations
insert leads;

// Clear bypass (important!)
TriggerBase.clearBypass('TA_Lead_SetDefaults');
```

### Bypassing Multiple Actions

```apex
// Bypass multiple actions
TriggerBase.bypass('TA_Lead_SetDefaults');
TriggerBase.bypass('TA_Lead_ValidateFields');
TriggerBase.bypass('TA_Lead_AssignOwner');

try {
    // Perform operations
    insert leads;
} finally {
    // Always clear bypasses
    TriggerBase.clearAllBypasses();
}
```

### Checking Bypass Status

```apex
if (TriggerBase.isBypassed('TA_Lead_SetDefaults')) {
    System.debug('TA_Lead_SetDefaults is currently bypassed');
}
```

## Object-Level Bypass

### Bypassing All Actions for an Object

```apex
// Bypass all trigger actions for Lead
MetadataTriggerHandler.bypass('Lead');

// Perform bulk operations - no trigger actions will run
insert leads;
update leads;
delete leads;

// Clear bypass
MetadataTriggerHandler.clearBypass('Lead');
```

### Bypassing Multiple Objects

```apex
// Bypass multiple objects
MetadataTriggerHandler.bypass('Lead');
MetadataTriggerHandler.bypass('Account');
MetadataTriggerHandler.bypass('Contact');

try {
    // Perform cross-object operations
    insert accounts;
    insert contacts;
    insert leads;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

## Flow Bypass

### Bypassing a Specific Flow

```apex
// Bypass a flow registered as a trigger action
TriggerActionFlow.bypass('Lead_Enrich_From_External');

insert leads;

TriggerActionFlow.clearBypass('Lead_Enrich_From_External');
```

### Bypassing All Flows

```apex
// Bypass all flows for a transaction
TriggerActionFlow.bypassAll();

try {
    insert leads;
} finally {
    TriggerActionFlow.clearAllBypasses();
}
```

## Bypass Use Cases

### Data Migration Script

```apex
public class LeadMigrationBatch implements Database.Batchable<SObject> {
    
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator('SELECT Id, ... FROM Legacy_Lead__c');
    }
    
    public void execute(Database.BatchableContext bc, List<Legacy_Lead__c> scope) {
        // Bypass all Lead triggers during migration
        MetadataTriggerHandler.bypass('Lead');
        
        try {
            List<Lead> leadsToInsert = new List<Lead>();
            for (Legacy_Lead__c legacy : scope) {
                leadsToInsert.add(transformToLead(legacy));
            }
            insert leadsToInsert;
        } finally {
            // Always clear in finally block
            MetadataTriggerHandler.clearBypass('Lead');
        }
    }
    
    public void finish(Database.BatchableContext bc) {
        // Migration complete
    }
    
    private Lead transformToLead(Legacy_Lead__c legacy) {
        // Transform logic
    }
}
```

### Integration Handler

```apex
public class ExternalSystemIntegrationHandler {
    
    public static void processInboundLeads(List<Lead> inboundLeads) {
        // Skip validation since data is already validated externally
        TriggerBase.bypass('TA_Lead_ValidateFields');
        
        // Skip auto-assignment since external system assigns
        TriggerBase.bypass('TA_Lead_AssignOwner');
        
        try {
            insert inboundLeads;
        } finally {
            TriggerBase.clearAllBypasses();
        }
    }
}
```

### Test Data Creation

```apex
@IsTest
private class AccountServiceTest {
    
    @TestSetup
    static void makeData() {
        // Bypass triggers when creating test data
        // This speeds up test setup significantly
        MetadataTriggerHandler.bypass('Account');
        MetadataTriggerHandler.bypass('Contact');
        
        try {
            Account acc = new Account(Name = 'Test Account');
            insert acc;
            
            Contact con = new Contact(
                AccountId = acc.Id,
                LastName = 'Test Contact'
            );
            insert con;
        } finally {
            MetadataTriggerHandler.clearAllBypasses();
        }
    }
    
    @IsTest
    static void testSomeMethod() {
        // Actual test - triggers run normally
        Account acc = [SELECT Id FROM Account LIMIT 1];
        acc.Name = 'Updated Name';
        update acc; // Triggers fire here
    }
}
```

### Recursive Prevention in Service Layer

```apex
public class AccountService {
    
    public static void syncToExternalSystem(Set<Id> accountIds) {
        // Prevent infinite loop: update from external sync triggers another sync
        if (TriggerBase.isBypassed('TA_Account_SyncToExternal')) {
            return;
        }
        
        TriggerBase.bypass('TA_Account_SyncToExternal');
        
        try {
            // Perform sync
            List<Account> accounts = DAL_Account.getAccountsById(accountIds);
            ExternalSystemService.sync(accounts);
            
            // Update sync timestamp - won't trigger another sync
            for (Account acc : accounts) {
                acc.Last_Sync_Date__c = DateTime.now();
            }
            update accounts;
        } finally {
            TriggerBase.clearBypass('TA_Account_SyncToExternal');
        }
    }
}
```

## Bypass Best Practices

### 1. Always Clear Bypasses

```apex
// BAD - Bypass never cleared
TriggerBase.bypass('TA_Lead_SetDefaults');
insert leads;
// Other code in same transaction won't have triggers

// GOOD - Use try/finally
TriggerBase.bypass('TA_Lead_SetDefaults');
try {
    insert leads;
} finally {
    TriggerBase.clearBypass('TA_Lead_SetDefaults');
}
```

### 2. Prefer Specific Bypasses Over Object-Level

```apex
// LESS PREFERRED - Bypasses everything
MetadataTriggerHandler.bypass('Lead');

// PREFERRED - Only bypass what you need
TriggerBase.bypass('TA_Lead_SetDefaults');
TriggerBase.bypass('TA_Lead_SendWelcomeEmail');
```

### 3. Document Why Bypass is Needed

```apex
public class DataMigrationService {
    
    /**
     * Bypasses Lead triggers during migration because:
     * 1. Data is already validated by source system
     * 2. Owners are pre-assigned in migration data
     * 3. Welcome emails should not be sent for historical leads
     */
    public static void migrateLegacyLeads(List<Lead> leads) {
        TriggerBase.bypass('TA_Lead_ValidateFields');
        TriggerBase.bypass('TA_Lead_AssignOwner');
        TriggerBase.bypass('TA_Lead_SendWelcomeEmail');
        
        try {
            insert leads;
        } finally {
            TriggerBase.clearAllBypasses();
        }
    }
}
```

### 4. Use Permission-Based for Permanent Bypasses

For users who should **always** bypass certain triggers (like integration users), use Custom Permissions rather than code:

```xml
<!-- Integration User Permission Set -->
<customPermissions>
    <enabled>true</enabled>
    <name>Bypass_Lead_DuplicateCheck</name>
</customPermissions>
```

### 5. Test Both Bypassed and Non-Bypassed Scenarios

```apex
@IsTest
static void testAction_normalExecution_runsAction() {
    Lead l = new Lead(LastName = 'Test', Company = 'Test');
    insert l;
    
    Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :l.Id];
    System.assertEquals('Web', inserted.LeadSource, 'Default should be set');
}

@IsTest
static void testAction_bypassed_skipsAction() {
    TriggerBase.bypass('TA_Lead_SetDefaults');
    
    try {
        Lead l = new Lead(LastName = 'Test', Company = 'Test');
        insert l;
        
        Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :l.Id];
        System.assertEquals(null, inserted.LeadSource, 'Default should NOT be set when bypassed');
    } finally {
        TriggerBase.clearBypass('TA_Lead_SetDefaults');
    }
}
```

### 6. Log Bypass Usage in Production

```apex
public class BypassLogger {
    
    public static void logBypass(String actionName, String reason) {
        if (!Test.isRunningTest()) {
            Bypass_Log__c log = new Bypass_Log__c(
                Action_Name__c = actionName,
                Bypass_Reason__c = reason,
                User__c = UserInfo.getUserId(),
                Timestamp__c = DateTime.now()
            );
            insert log;
        }
    }
}

// Usage
BypassLogger.logBypass('TA_Lead_SetDefaults', 'Data migration batch - ticket #12345');
TriggerBase.bypass('TA_Lead_SetDefaults');
```
