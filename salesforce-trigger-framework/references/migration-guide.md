# Migration Guide: Legacy Frameworks to Trigger Actions Framework

## Table of Contents

1. [Migration Overview](#migration-overview)
2. [From Kevin O'Hara Pattern](#from-kevin-ohara-pattern)
3. [From PS Advisory SBLI Pattern](#from-ps-advisory-sbli-pattern)
4. [From No Framework](#from-no-framework)
5. [Migration Checklist](#migration-checklist)
6. [Parallel Running Strategy](#parallel-running-strategy)

## Migration Overview

### When to Migrate

**Migrate if**:
- Starting a new implementation on an existing org
- Flows and Apex need coordination
- Moving toward unlocked packages
- Need declarative bypass control

**Don't migrate if**:
- Current framework is working well
- No Flow coordination needed
- Migration cost exceeds benefit
- Small org with minimal trigger logic

### Migration Approach

1. **New development**: Use Trigger Actions Framework immediately
2. **Existing triggers**: Migrate object-by-object during natural enhancement cycles
3. **Never**: Big-bang migration of working code

## From Kevin O'Hara Pattern

### Before: Kevin O'Hara Structure

```apex
// Trigger
trigger LeadTrigger on Lead (before insert, after insert, before update, after update) {
    new LeadTriggerHandler().run();
}

// Handler
public class LeadTriggerHandler extends TriggerHandler {
    private List<Lead> newLeads;
    private List<Lead> oldLeads;
    private Map<Id, Lead> newMap;
    private Map<Id, Lead> oldMap;
    
    public LeadTriggerHandler() {
        this.newLeads = (List<Lead>) Trigger.new;
        this.oldLeads = (List<Lead>) Trigger.old;
        this.newMap = (Map<Id, Lead>) Trigger.newMap;
        this.oldMap = (Map<Id, Lead>) Trigger.oldMap;
    }
    
    public override void beforeInsert() {
        setDefaults();
        validateRequiredFields();
        calculateScore();
    }
    
    public override void afterInsert() {
        createDefaultTasks();
        notifyOwner();
    }
    
    private void setDefaults() {
        for (Lead l : newLeads) {
            if (String.isBlank(l.LeadSource)) {
                l.LeadSource = 'Web';
            }
        }
    }
    
    private void validateRequiredFields() {
        for (Lead l : newLeads) {
            if (String.isBlank(l.Company)) {
                l.addError('Company is required');
            }
        }
    }
    
    // ... more methods
}
```

### After: Trigger Actions Framework Structure

```apex
// Trigger - Changed
trigger LeadTrigger on Lead (before insert, after insert, before update, after update) {
    new MetadataTriggerHandler().run();
}

// Separate Action Classes - NEW
public class TA_Lead_SetDefaults implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (String.isBlank(l.LeadSource)) {
                l.LeadSource = 'Web';
            }
        }
    }
}

public class TA_Lead_ValidateRequiredFields implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (String.isBlank(l.Company)) {
                l.addError('Company is required');
            }
        }
    }
}

public class TA_Lead_CalculateScore implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        LeadScoringService.calculateScores(newList);
    }
}

public class TA_Lead_CreateDefaultTasks implements TriggerAction.AfterInsert {
    public void afterInsert(List<Lead> newList) {
        TaskService.createDefaultTasks(newList);
    }
}
```

### Migration Steps

1. **Install Trigger Actions Framework** in the org

2. **Create sObject Trigger Setting** metadata record

3. **Extract each logical unit** from the handler into a separate action class

4. **Create Trigger Action metadata** for each action with proper ordering

5. **Update the trigger** to use `MetadataTriggerHandler`

6. **Delete the old handler class** after verification

7. **Update test classes** to test actions individually

## From PS Advisory SBLI Pattern

### Before: SBLI Structure

```apex
// Trigger
trigger LeadTrigger on Lead (before insert, before update, after insert, after update) {
    new TH_Lead().run();
}

// Handler
public class TH_Lead extends BaseTriggerHandler {
    private List<Lead> newLeadList;
    private List<Lead> oldLeadList;
    
    public TH_Lead() {
        this.newLeadList = (List<Lead>) Trigger.new;
        this.oldLeadList = (List<Lead>) Trigger.old;
    }
    
    protected override void beforeInsert() {
        if (TriggerCheck.canRun('TH_LeadBeforeInsert')) {
            populateDOBAsText(newLeadList);
            processLeadSourceAutomation(newLeadList);
            populateFirstTouchField(newLeadList);
        }
    }
    
    protected override void afterInsert() {
        if (TriggerCheck.canRun('TH_LeadAfterInsert')) {
            LeadService.createFollowUpTasks(newLeadList);
        }
    }
    
    private void populateDOBAsText(List<Lead> leads) {
        // Logic here
    }
}

// TriggerCheck utility
public class TriggerCheck {
    public static Boolean canRun(String name) {
        // Checks User.ByPassTrigger__c field
    }
}
```

### After: Trigger Actions Framework Structure

```apex
// Trigger - Changed
trigger LeadTrigger on Lead (before insert, before update, after insert, after update) {
    new MetadataTriggerHandler().run();
}

// Action Classes - Extract from TH_Lead methods
public class TA_Lead_PopulateDOBAsText implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (l.Date_of_Birth__c != null) {
                l.DOB_Text__c = l.Date_of_Birth__c.format();
            }
        }
    }
}

public class TA_Lead_ProcessLeadSource implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        LeadSourceService.processAutomation(newList);
    }
}

public class TA_Lead_PopulateFirstTouch implements TriggerAction.BeforeInsert {
    public void beforeInsert(List<Lead> newList) {
        for (Lead l : newList) {
            if (l.First_Touch_Date__c == null) {
                l.First_Touch_Date__c = Date.today();
            }
        }
    }
}

public class TA_Lead_CreateFollowUpTasks implements TriggerAction.AfterInsert {
    public void afterInsert(List<Lead> newList) {
        LeadService.createFollowUpTasks(newList);
    }
}
```

### Key Differences

| SBLI Pattern | Trigger Actions Framework |
|--------------|---------------------------|
| `TriggerCheck.canRun()` on User field | Custom Permission on metadata record |
| Methods in single handler class | Separate action classes |
| Order determined by code sequence | Order determined by metadata |
| `BaseTriggerHandler.bypass()` | `TriggerBase.bypass()` |

### Migration Path for TriggerCheck

**Before**: User.ByPassTrigger__c multi-select picklist

**After**: Custom Permissions + Permission Sets

```xml
<!-- Create Custom Permission -->
<CustomPermission>
    <label>Bypass Lead Before Insert</label>
    <n>Bypass_TH_LeadBeforeInsert</n>
</CustomPermission>

<!-- Assign to Permission Set (replaces User field value) -->
<PermissionSet>
    <customPermissions>
        <enabled>true</enabled>
        <n>Bypass_TH_LeadBeforeInsert</n>
    </customPermissions>
</PermissionSet>
```

### Service/DAL Layer Compatibility

**Good news**: Your existing Service and DAL classes don't change!

```apex
// LeadService - NO CHANGES NEEDED
public class LeadService {
    public static void createFollowUpTasks(List<Lead> leads) {
        // Same implementation
    }
}

// DAL_Lead - NO CHANGES NEEDED
public class DAL_Lead {
    public static List<Lead> getLeadsByIds(Set<Id> leadIds) {
        // Same implementation
    }
}
```

The Trigger Actions just call the same services:

```apex
public class TA_Lead_CreateFollowUpTasks implements TriggerAction.AfterInsert {
    public void afterInsert(List<Lead> newList) {
        LeadService.createFollowUpTasks(newList); // Same call
    }
}
```

## From No Framework

If the org has raw trigger logic without any framework:

### Before: Raw Trigger

```apex
trigger LeadTrigger on Lead (before insert, after insert) {
    if (Trigger.isBefore && Trigger.isInsert) {
        for (Lead l : Trigger.new) {
            if (String.isBlank(l.LeadSource)) {
                l.LeadSource = 'Web';
            }
            if (String.isBlank(l.Company)) {
                l.addError('Company is required');
            }
        }
    }
    
    if (Trigger.isAfter && Trigger.isInsert) {
        List<Task> tasks = new List<Task>();
        for (Lead l : Trigger.new) {
            tasks.add(new Task(
                WhoId = l.Id,
                Subject = 'Follow up',
                ActivityDate = Date.today().addDays(3)
            ));
        }
        insert tasks;
    }
}
```

### After: Trigger Actions Framework

1. **Install framework**
2. **Create trigger with MetadataTriggerHandler**
3. **Create sObject setting**
4. **Extract logic into action classes**
5. **Create trigger action metadata records**

## Migration Checklist

### Pre-Migration

- [ ] Install Trigger Actions Framework
- [ ] Document all existing trigger logic per object
- [ ] Identify logical groupings for action classes
- [ ] Plan execution order
- [ ] Create Custom Permissions for bypass needs

### Per-Object Migration

- [ ] Create `sObject_Trigger_Setting__mdt` record
- [ ] Create trigger action classes (TA_*)
- [ ] Create test classes for each action
- [ ] Create `Trigger_Action__mdt` records
- [ ] Update trigger to use `MetadataTriggerHandler`
- [ ] Run all tests
- [ ] Deploy to sandbox and verify
- [ ] Delete old handler class after validation

### Post-Migration

- [ ] Update Permission Sets with new Custom Permissions
- [ ] Remove old bypass mechanism (User field, etc.)
- [ ] Update documentation
- [ ] Train team on new patterns

## Parallel Running Strategy

For high-risk migrations, run both frameworks temporarily:

```apex
trigger LeadTrigger on Lead (before insert, after insert, before update, after update) {
    // Feature flag to control which framework runs
    if (FeatureFlags.useNewTriggerFramework('Lead')) {
        new MetadataTriggerHandler().run();
    } else {
        new TH_Lead().run(); // Old handler
    }
}
```

### Feature Flag Implementation

```apex
public class FeatureFlags {
    
    private static Map<String, Boolean> flagCache;
    
    static {
        flagCache = new Map<String, Boolean>();
        for (Feature_Flag__mdt flag : [
            SELECT Object_Name__c, Use_New_Framework__c 
            FROM Feature_Flag__mdt
        ]) {
            flagCache.put(flag.Object_Name__c, flag.Use_New_Framework__c);
        }
    }
    
    public static Boolean useNewTriggerFramework(String objectName) {
        return flagCache.containsKey(objectName) && flagCache.get(objectName);
    }
}
```

This allows:
- Object-by-object rollout
- Quick rollback if issues arise
- A/B testing of behavior
- Gradual team adoption
