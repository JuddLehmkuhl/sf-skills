# Action Plan Template Version Status Lifecycle

Complete guide to template version status transitions, including dead ends and workarounds.

## Status State Machine

```
                    ┌─────────────────────────────────────────────┐
                    │          CREATION METHOD MATTERS             │
                    ├─────────────────────────────────────────────┤
                    │                                             │
                    │  REST API POST ──────────► Draft            │
                    │  Setup UI (manual) ──────► Draft            │
                    │  Metadata API deploy ────► ReadOnly ✗       │
                    │                                             │
                    └─────────────────────────────────────────────┘

    ┌──────────┐    UI: "Publish"    ┌──────────┐    UI: "Deactivate"    ┌──────────┐
    │  Draft   │ ──────────────────► │  Final   │ ─────────────────────► │ Obsolete │
    │          │                     │(Published)│                       │          │
    └──────────┘                     └──────────┘                       └──────────┘
         │                                │                                  │
         │ Can edit items: YES            │ Can edit items: NO               │ Can edit: NO
         │ Can create plans: NO           │ Can create plans: YES            │ Can create plans: NO
         │ Flows can assign: NO           │ Flows can assign: YES            │ Can reactivate: NO
         │                                │                                  │
         └────────────────────────────────┴──────────────────────────────────┘

    ┌──────────┐
    │ ReadOnly │  ← DEAD END (created by Metadata API deploy)
    │          │  Cannot transition to any other status
    └──────────┘  Cannot create plans, cannot publish, cannot edit
                  ONLY option: delete and recreate via REST API
```

## Status Details

### Draft
- **Created by:** REST API POST or Setup UI
- **Can edit items:** Yes — add, modify, delete template items
- **Can create Action Plans:** No
- **Can be assigned by flows:** No
- **Transitions to:** Final (via UI "Publish Template" button)
- **Use case:** Template under development

### Final (Published)
- **Created by:** Publishing a Draft template from Setup UI
- **Can edit items:** No — template is locked
- **Can create Action Plans:** Yes
- **Can be assigned by flows:** Yes (query `WHERE Status = 'Final'`)
- **Transitions to:** Obsolete (via UI "Deactivate Template" button — **PERMANENT**)
- **Use case:** Production template actively in use

### ReadOnly
- **Created by:** Metadata API deployment (`sf project deploy start`)
- **Can edit items:** No
- **Can create Action Plans:** No
- **Can be assigned by flows:** No
- **Transitions to:** **NONE** — this is a dead end
- **Error when trying to change:** *"You can't change the status on read-only templates"*
- **Resolution:** Delete the template and recreate via REST API
- **Use case:** None — this is an unintended state from metadata deployment

### Obsolete
- **Created by:** Deactivating a Final template from Setup UI
- **Can edit items:** No
- **Can create Action Plans:** No
- **Can be assigned by flows:** No
- **Transitions to:** **NONE** — deactivation is permanent
- **Can be deleted:** Only if no active ActionPlan instances reference it
- **Use case:** Deprecated template replaced by a newer version

## Common Scenarios

### Scenario 1: First-time template creation
```
1. POST to REST API → Draft
2. Add items and values via REST API
3. Review in Setup UI
4. Click "Publish Template" → Final
5. Retrieve into source control: sf project retrieve start -m ActionPlanTemplate
```

### Scenario 2: Update an existing Published template
```
1. Cannot edit Final template — must create replacement
2. POST new template via REST API (same Name) → Draft
3. Add updated items and values
4. Publish new template → Final
5. Deactivate old template → Obsolete
6. Delete old template (if no active instances)
7. Retrieve updated templates into source control
```

### Scenario 3: Recover from ReadOnly metadata deploy
```
1. Template deployed via sf project deploy start → ReadOnly (broken)
2. Delete the ReadOnly template: sf data delete record -s ActionPlanTemplate -i <id>
3. Recreate via REST API → Draft
4. Publish from UI → Final
```

### Scenario 4: Template with active instances needs replacement
```
1. Create new template via REST API → Draft
2. Publish → Final
3. Deactivate old template → Obsolete (cannot delete — active instances exist)
4. Old template remains as Obsolete; existing plans still reference it
5. New plans use the new Final template
```

## Flow Integration

Flows that auto-assign templates should query by Name and Status:

```
Get Records: ActionPlanTemplate
  WHERE Name = 'Agency Onboarding - Independent'

Get Records: ActionPlanTemplateVersion
  WHERE ActionPlanTemplateId = {templateId}
  AND Status = 'Final'
```

This pattern works across template replacements because the new template uses the same Name, and only the Final version is selected.
