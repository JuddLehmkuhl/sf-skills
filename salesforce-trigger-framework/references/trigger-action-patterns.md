# Trigger Action Patterns Reference

## Table of Contents

1. [Interface Overview](#interface-overview)
2. [Before Insert Pattern](#before-insert-pattern)
3. [After Insert Pattern](#after-insert-pattern)
4. [Before Update Pattern](#before-update-pattern)
5. [After Update Pattern](#after-update-pattern)
6. [Before Delete Pattern](#before-delete-pattern)
7. [After Delete Pattern](#after-delete-pattern)
8. [After Undelete Pattern](#after-undelete-pattern)
9. [Multi-Context Actions](#multi-context-actions)
10. [Service Layer Integration](#service-layer-integration)
11. [Common Anti-Patterns](#common-anti-patterns)

## Interface Overview

The framework provides seven interfaces, each corresponding to a trigger context:

```apex
public interface TriggerAction {
    interface BeforeInsert {
        void beforeInsert(List<SObject> newList);
    }
    interface AfterInsert {
        void afterInsert(List<SObject> newList);
    }
    interface BeforeUpdate {
        void beforeUpdate(List<SObject> newList, List<SObject> oldList);
    }
    interface AfterUpdate {
        void afterUpdate(List<SObject> newList, List<SObject> oldList);
    }
    interface BeforeDelete {
        void beforeDelete(List<SObject> oldList);
    }
    interface AfterDelete {
        void afterDelete(List<SObject> oldList);
    }
    interface AfterUndelete {
        void afterUndelete(List<SObject> newList);
    }
}
```

## Before Insert Pattern

Use for: Field defaulting, validation, data enrichment before records are saved.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.BeforeInsert {
    
    public void beforeInsert(List<<ObjectName>> newList) {
        for (<ObjectName> record : newList) {
            // Direct field manipulation - no DML needed
        }
    }
}
```

### Example: Default Field Values

```apex
public with sharing class TA_Lead_SetDefaults implements TriggerAction.BeforeInsert {
    
    private static final String DEFAULT_LEAD_SOURCE = 'Web';
    private static final String DEFAULT_STATUS = 'New';
    
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (String.isBlank(l.LeadSource)) {
                l.LeadSource = DEFAULT_LEAD_SOURCE;
            }
            if (String.isBlank(l.Status)) {
                l.Status = DEFAULT_STATUS;
            }
        }
    }
}
```

### Example: Validation with addError

```apex
public with sharing class TA_Opportunity_ValidateAmount implements TriggerAction.BeforeInsert {
    
    private static final Decimal MINIMUM_AMOUNT = 1000;
    
    public void beforeInsert(List<Opportunity> newList) {
        for (Opportunity opp : newList) {
            if (opp.Amount != null && opp.Amount < MINIMUM_AMOUNT) {
                opp.addError('Opportunity amount must be at least ' + MINIMUM_AMOUNT);
            }
        }
    }
}
```

### Example: Computed Fields

```apex
public with sharing class TA_Contact_ComputeFullName implements TriggerAction.BeforeInsert {
    
    public void beforeInsert(List<Contact> newList) {
        for (Contact c : newList) {
            c.Full_Name__c = buildFullName(c);
        }
    }
    
    private String buildFullName(Contact c) {
        List<String> nameParts = new List<String>();
        if (String.isNotBlank(c.Salutation)) nameParts.add(c.Salutation);
        if (String.isNotBlank(c.FirstName)) nameParts.add(c.FirstName);
        if (String.isNotBlank(c.LastName)) nameParts.add(c.LastName);
        if (String.isNotBlank(c.Suffix)) nameParts.add(c.Suffix);
        return String.join(nameParts, ' ');
    }
}
```

## After Insert Pattern

Use for: Creating related records, callouts, platform events, operations requiring record IDs.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.AfterInsert {
    
    public void afterInsert(List<<ObjectName>> newList) {
        // Records have IDs now
        // Cannot modify trigger records directly - use DML on other objects
    }
}
```

### Example: Create Related Records

```apex
public with sharing class TA_Account_CreateDefaultContact implements TriggerAction.AfterInsert {
    
    public void afterInsert(List<Account> newList) {
        List<Contact> contactsToInsert = new List<Contact>();
        
        for (Account acc : newList) {
            if (acc.Type == 'Customer') {
                contactsToInsert.add(new Contact(
                    AccountId = acc.Id,
                    LastName = 'Primary Contact',
                    Email = acc.Email__c
                ));
            }
        }
        
        if (!contactsToInsert.isEmpty()) {
            insert contactsToInsert;
        }
    }
}
```

### Example: Publish Platform Event

```apex
public with sharing class TA_Order_PublishEvent implements TriggerAction.AfterInsert {
    
    public void afterInsert(List<Order> newList) {
        List<Order_Created__e> events = new List<Order_Created__e>();
        
        for (Order o : newList) {
            events.add(new Order_Created__e(
                Order_Id__c = o.Id,
                Account_Id__c = o.AccountId,
                Total_Amount__c = o.TotalAmount
            ));
        }
        
        if (!events.isEmpty()) {
            EventBus.publish(events);
        }
    }
}
```

## Before Update Pattern

Use for: Validation based on field changes, field updates, preventing changes.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.BeforeUpdate {
    
    public void beforeUpdate(List<<ObjectName>> newList, List<<ObjectName>> oldList) {
        Map<Id, <ObjectName>> oldMap = new Map<Id, <ObjectName>>(oldList);
        
        for (<ObjectName> record : newList) {
            <ObjectName> oldRecord = oldMap.get(record.Id);
            // Compare old vs new values
        }
    }
}
```

### Example: Field Change Detection

```apex
public with sharing class TA_Opportunity_TrackStageChange implements TriggerAction.BeforeUpdate {
    
    public void beforeUpdate(List<Opportunity> newList, List<Opportunity> oldList) {
        Map<Id, Opportunity> oldMap = new Map<Id, Opportunity>(oldList);
        
        for (Opportunity opp : newList) {
            Opportunity oldOpp = oldMap.get(opp.Id);
            
            if (opp.StageName != oldOpp.StageName) {
                opp.Stage_Changed_Date__c = Date.today();
                opp.Previous_Stage__c = oldOpp.StageName;
            }
        }
    }
}
```

### Example: Prevent Field Changes

```apex
public with sharing class TA_Case_PreventClosedEdits implements TriggerAction.BeforeUpdate {
    
    private static final Set<String> CLOSED_STATUSES = new Set<String>{'Closed', 'Resolved'};
    
    public void beforeUpdate(List<Case> newList, List<Case> oldList) {
        Map<Id, Case> oldMap = new Map<Id, Case>(oldList);
        
        for (Case c : newList) {
            Case oldCase = oldMap.get(c.Id);
            
            if (CLOSED_STATUSES.contains(oldCase.Status) && c.Status != oldCase.Status) {
                c.addError('Cannot modify a closed case');
            }
        }
    }
}
```

## After Update Pattern

Use for: Cascading updates to related records, notifications, external system sync.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.AfterUpdate {
    
    public void afterUpdate(List<<ObjectName>> newList, List<<ObjectName>> oldList) {
        Map<Id, <ObjectName>> oldMap = new Map<Id, <ObjectName>>(oldList);
        
        List<<ObjectName>> changedRecords = new List<<ObjectName>>();
        for (<ObjectName> record : newList) {
            <ObjectName> oldRecord = oldMap.get(record.Id);
            if (record.SomeField__c != oldRecord.SomeField__c) {
                changedRecords.add(record);
            }
        }
        
        if (!changedRecords.isEmpty()) {
            // Process only changed records
        }
    }
}
```

### Example: Sync to Related Records

```apex
public with sharing class TA_Account_SyncToContacts implements TriggerAction.AfterUpdate {
    
    public void afterUpdate(List<Account> newList, List<Account> oldList) {
        Map<Id, Account> oldMap = new Map<Id, Account>(oldList);
        Set<Id> accountsWithAddressChange = new Set<Id>();
        
        for (Account acc : newList) {
            Account oldAcc = oldMap.get(acc.Id);
            if (hasAddressChanged(acc, oldAcc)) {
                accountsWithAddressChange.add(acc.Id);
            }
        }
        
        if (!accountsWithAddressChange.isEmpty()) {
            AccountService.syncAddressToContacts(accountsWithAddressChange);
        }
    }
    
    private Boolean hasAddressChanged(Account newAcc, Account oldAcc) {
        return newAcc.BillingStreet != oldAcc.BillingStreet ||
               newAcc.BillingCity != oldAcc.BillingCity ||
               newAcc.BillingState != oldAcc.BillingState ||
               newAcc.BillingPostalCode != oldAcc.BillingPostalCode;
    }
}
```

## Before Delete Pattern

Use for: Validation before deletion, preventing deletion of certain records.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.BeforeDelete {
    
    public void beforeDelete(List<<ObjectName>> oldList) {
        for (<ObjectName> record : oldList) {
            // Validate deletion is allowed
        }
    }
}
```

### Example: Prevent Deletion

```apex
public with sharing class TA_Account_PreventDeleteWithOpps implements TriggerAction.BeforeDelete {
    
    public void beforeDelete(List<Account> oldList) {
        Set<Id> accountIds = new Set<Id>();
        for (Account acc : oldList) {
            accountIds.add(acc.Id);
        }
        
        Map<Id, Account> accountsWithOpps = new Map<Id, Account>([
            SELECT Id, (SELECT Id FROM Opportunities LIMIT 1)
            FROM Account
            WHERE Id IN :accountIds
        ]);
        
        for (Account acc : oldList) {
            Account accWithChildren = accountsWithOpps.get(acc.Id);
            if (accWithChildren != null && !accWithChildren.Opportunities.isEmpty()) {
                acc.addError('Cannot delete account with opportunities');
            }
        }
    }
}
```

## After Delete Pattern

Use for: Cleanup operations, audit logging, notifications about deletions.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.AfterDelete {
    
    public void afterDelete(List<<ObjectName>> oldList) {
        // Records are deleted - perform cleanup
    }
}
```

### Example: Audit Logging

```apex
public with sharing class TA_Contact_AuditDeletion implements TriggerAction.AfterDelete {
    
    public void afterDelete(List<Contact> oldList) {
        List<Audit_Log__c> logs = new List<Audit_Log__c>();
        
        for (Contact c : oldList) {
            logs.add(new Audit_Log__c(
                Action__c = 'DELETE',
                Object_Type__c = 'Contact',
                Record_Id__c = c.Id,
                Record_Name__c = c.FirstName + ' ' + c.LastName,
                Deleted_By__c = UserInfo.getUserId(),
                Deletion_Date__c = DateTime.now()
            ));
        }
        
        if (!logs.isEmpty()) {
            insert logs;
        }
    }
}
```

## After Undelete Pattern

Use for: Restoring related data, notifications, re-syncing external systems.

### Basic Template

```apex
public with sharing class TA_<ObjectName>_<Action> implements TriggerAction.AfterUndelete {
    
    public void afterUndelete(List<<ObjectName>> newList) {
        // Records are restored - handle reactivation
    }
}
```

## Multi-Context Actions

Sometimes the same logic applies to multiple contexts. Implement multiple interfaces:

```apex
public with sharing class TA_Lead_ComputeScore implements 
    TriggerAction.BeforeInsert, 
    TriggerAction.BeforeUpdate {
    
    public void beforeInsert(List<Lead> newList) {
        computeScores(newList, null);
    }
    
    public void beforeUpdate(List<Lead> newList, List<Lead> oldList) {
        computeScores(newList, new Map<Id, Lead>(oldList));
    }
    
    private void computeScores(List<Lead> leads, Map<Id, Lead> oldMap) {
        for (Lead l : leads) {
            // Only recompute if relevant fields changed (or insert)
            if (oldMap == null || shouldRecompute(l, oldMap.get(l.Id))) {
                l.Lead_Score__c = LeadScoringService.calculateScore(l);
            }
        }
    }
    
    private Boolean shouldRecompute(Lead newLead, Lead oldLead) {
        return newLead.Industry != oldLead.Industry ||
               newLead.AnnualRevenue != oldLead.AnnualRevenue ||
               newLead.NumberOfEmployees != oldLead.NumberOfEmployees;
    }
}
```

**Note**: Register this action TWICE in Custom Metadata - once for Before_Insert, once for Before_Update.

## Service Layer Integration

### Pattern: Thin Actions, Fat Services

```apex
// TRIGGER ACTION - Thin, orchestration only
public with sharing class TA_Opportunity_CalculateCommission implements TriggerAction.AfterUpdate {
    
    public void afterUpdate(List<Opportunity> newList, List<Opportunity> oldList) {
        Map<Id, Opportunity> oldMap = new Map<Id, Opportunity>(oldList);
        List<Opportunity> closedWonOpps = new List<Opportunity>();
        
        for (Opportunity opp : newList) {
            Opportunity oldOpp = oldMap.get(opp.Id);
            if (opp.StageName == 'Closed Won' && oldOpp.StageName != 'Closed Won') {
                closedWonOpps.add(opp);
            }
        }
        
        if (!closedWonOpps.isEmpty()) {
            CommissionService.calculateAndCreateCommissions(closedWonOpps);
        }
    }
}

// SERVICE - Fat, all business logic
public with sharing class CommissionService {
    
    public static void calculateAndCreateCommissions(List<Opportunity> opportunities) {
        Map<Id, Decimal> commissionRates = getCommissionRates(opportunities);
        List<Commission__c> commissions = new List<Commission__c>();
        
        for (Opportunity opp : opportunities) {
            Decimal rate = commissionRates.get(opp.OwnerId);
            if (rate != null && opp.Amount != null) {
                commissions.add(new Commission__c(
                    Opportunity__c = opp.Id,
                    Sales_Rep__c = opp.OwnerId,
                    Amount__c = opp.Amount * rate,
                    Commission_Date__c = Date.today()
                ));
            }
        }
        
        if (!commissions.isEmpty()) {
            DAL_Commission.insertCommissions(commissions);
        }
    }
    
    private static Map<Id, Decimal> getCommissionRates(List<Opportunity> opportunities) {
        Set<Id> ownerIds = new Set<Id>();
        for (Opportunity opp : opportunities) {
            ownerIds.add(opp.OwnerId);
        }
        return DAL_User.getCommissionRatesByUserId(ownerIds);
    }
}

// DAL - Data access only
public with sharing class DAL_Commission {
    
    public static void insertCommissions(List<Commission__c> commissions) {
        insert commissions;
    }
}

public with sharing class DAL_User {
    
    public static Map<Id, Decimal> getCommissionRatesByUserId(Set<Id> userIds) {
        Map<Id, Decimal> rates = new Map<Id, Decimal>();
        for (User u : [SELECT Id, Commission_Rate__c FROM User WHERE Id IN :userIds]) {
            rates.put(u.Id, u.Commission_Rate__c);
        }
        return rates;
    }
}
```

## Common Anti-Patterns

### ❌ Anti-Pattern: DML in Before Context

```apex
// BAD - DML in before trigger causes issues
public void beforeInsert(List<Lead> newList) {
    List<Task> tasks = new List<Task>();
    for (Lead l : newList) {
        tasks.add(new Task(WhoId = l.Id)); // l.Id is null!
    }
    insert tasks; // Wrong context for DML
}
```

### ❌ Anti-Pattern: SOQL in Loop

```apex
// BAD - SOQL inside loop
public void beforeInsert(List<Lead> newList) {
    for (Lead l : newList) {
        List<Account> matches = [SELECT Id FROM Account WHERE Name = :l.Company]; // N+1 queries
    }
}
```

### ✅ Correct: Bulkified Query

```apex
// GOOD - Query once, process in loop
public void beforeInsert(List<Lead> newList) {
    Set<String> companyNames = new Set<String>();
    for (Lead l : newList) {
        companyNames.add(l.Company);
    }
    
    Map<String, Account> accountsByName = new Map<String, Account>();
    for (Account a : [SELECT Id, Name FROM Account WHERE Name IN :companyNames]) {
        accountsByName.put(a.Name, a);
    }
    
    for (Lead l : newList) {
        Account matchingAccount = accountsByName.get(l.Company);
        if (matchingAccount != null) {
            l.Matched_Account__c = matchingAccount.Id;
        }
    }
}
```

### ❌ Anti-Pattern: Business Logic in Trigger Action

```apex
// BAD - Too much logic in trigger action
public void afterInsert(List<Opportunity> newList) {
    // 200 lines of commission calculation logic...
}
```

### ✅ Correct: Delegate to Service

```apex
// GOOD - Thin action, delegate to service
public void afterInsert(List<Opportunity> newList) {
    CommissionService.processNewOpportunities(newList);
}
```
