# Action Plan Template Assignment via Apex

Programmatic patterns for assigning Action Plan Templates to records. Essential for bulk operations, trigger-based assignment, and complex business logic.

## Basic Apex Assignment

```apex
/**
 * Assigns an Action Plan Template to a target record.
 * Requires the template to be in Final/Published status.
 */
public class ActionPlanService {

    /**
     * Create an Action Plan from a published template.
     * @param templateName  The Name of the ActionPlanTemplate
     * @param targetId      The record to assign the plan to (Account, Lead, etc.)
     * @return ActionPlan   The created ActionPlan record
     */
    public static ActionPlan assignTemplate(String templateName, Id targetId) {
        // Query the published template version
        ActionPlanTemplateVersion version = [
            SELECT Id, ActionPlanTemplateId, ActionPlanTemplate.ActionPlanType
            FROM ActionPlanTemplateVersion
            WHERE ActionPlanTemplate.Name = :templateName
              AND Status = 'Final'
            LIMIT 1
        ];

        // Create the Action Plan instance
        ActionPlan plan = new ActionPlan(
            Name                         = templateName + ' - ' + Date.today().format(),
            ActionPlanTemplateVersionId   = version.Id,
            TargetId                      = targetId,
            StartDate                     = Date.today(),
            ActionPlanType                = version.ActionPlanTemplate.ActionPlanType,
            ActionPlanState               = 'Not Started'
        );

        insert plan;
        return plan;
    }
}
```

## Bulk Apex Assignment (Trigger or Batch)

```apex
/**
 * Bulk-assigns Action Plans to multiple records.
 * Use in triggers, batch Apex, or scheduled jobs.
 * Follows PS Advisory conventions: no SOQL/DML in loops.
 *
 * See also: sf-apex skill for Apex patterns and sf-data skill for SOQL.
 */
public class ActionPlanBulkService {

    public static List<ActionPlan> assignTemplateToRecords(
        String templateName,
        List<Id> targetIds
    ) {
        // Single query for the template version
        ActionPlanTemplateVersion version = [
            SELECT Id, ActionPlanTemplateId, ActionPlanTemplate.ActionPlanType
            FROM ActionPlanTemplateVersion
            WHERE ActionPlanTemplate.Name = :templateName
              AND Status = 'Final'
            LIMIT 1
        ];

        // Build all Action Plans in memory (no DML in loop)
        List<ActionPlan> plans = new List<ActionPlan>();
        for (Id targetId : targetIds) {
            plans.add(new ActionPlan(
                Name                         = templateName + ' - ' + Date.today().format(),
                ActionPlanTemplateVersionId   = version.Id,
                TargetId                      = targetId,
                StartDate                     = Date.today(),
                ActionPlanType                = version.ActionPlanTemplate.ActionPlanType,
                ActionPlanState               = 'Not Started'
            ));
        }

        insert plans;
        return plans;
    }
}
```

## Apex Test Class

```apex
@IsTest
private class ActionPlanServiceTest {

    @TestSetup
    static void setup() {
        // Action Plan Templates cannot be created in test context via DML.
        // Use @TestVisible or mock patterns. In integration tests against
        // a real org, ensure a published template exists.
    }

    @IsTest
    static void testAssignTemplate() {
        // Create test Account
        Account acc = new Account(Name = 'Test Account');
        insert acc;

        // In a real test, you would query an existing published template.
        // Action Plan objects are not DML-creatable in pure unit tests
        // without SeeAllData=true or an existing template in the org.
        //
        // Integration test pattern:
        // ActionPlan result = ActionPlanService.assignTemplate(
        //     'Agency Onboarding - Independent',
        //     acc.Id
        // );
        // System.assertNotEquals(null, result.Id);
        // System.assertEquals('Not Started', result.ActionPlanState);
    }
}
```

**Testing note:** ActionPlanTemplate, ActionPlanTemplateVersion, and related objects are not DML-creatable in Apex test context. Integration tests that use `@IsTest(SeeAllData=true)` or org-specific test utilities are required. See [`sf-testing`](../../sf-testing/SKILL.md) for test patterns.

**See also:** [`sf-apex`](../../sf-apex/SKILL.md) for Apex class conventions, bulkification, and trigger architecture.
