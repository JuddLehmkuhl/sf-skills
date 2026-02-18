# Action Plan Object Schema Reference

Complete field reference for Action Plan-related objects.

## Table of Contents

1. [ActionPlanTemplate](#actionplantemplate)
2. [ActionPlanTemplateVersion](#actionplantemplateversion)
3. [ActionPlanTemplateItem](#actionplantemplateitem)
4. [ActionPlanTemplateItemValue](#actionplantemplateitemvalue)
5. [ActionPlan (Instance)](#actionplan-instance)
6. [ActionPlanItem (Instance)](#actionplanitem-instance)
7. [DocumentChecklistItem](#documentchecklistitem)

---

## ActionPlanTemplate

The top-level template definition.

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `Name` | String(255) | Display name |
| `Description` | String(255) | **Max 255 characters** — errors if exceeded |
| `ActionPlanType` | Picklist | `Industries` (DCIs + Tasks) or `Standard` (Tasks only) |
| `TargetEntityType` | Picklist | `Account`, `Lead`, `Opportunity`, `Case`, etc. |
| `IsAdHocItemCreationEnabled` | Boolean | Allow users to add items to generated plans |

**Creation via REST API:**
```json
POST /services/data/v62.0/sobjects/ActionPlanTemplate
{
    "Name": "My Template",
    "ActionPlanType": "Industries",
    "TargetEntityType": "Account",
    "Description": "Short description (max 255 chars)"
}
```

A `ActionPlanTemplateVersion` is auto-created in `Draft` status when the template is created.

---

## ActionPlanTemplateVersion

Controls template status and publishability. One version per template (no multi-version support).

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `ActionPlanTemplateId` | Reference | Parent template |
| `Status` | Picklist | `Draft`, `Final`, `ReadOnly`, `Obsolete` |

**Status Transitions:**
```
Draft → Final (via UI "Publish Template" button only)
Final → Obsolete (via UI "Deactivate Template" button — PERMANENT)
ReadOnly (created by metadata deploy — DEAD END, cannot transition)
```

**Query version status:**
```sql
SELECT Id, Status
FROM ActionPlanTemplateVersion
WHERE ActionPlanTemplateId = '<template_id>'
```

---

## ActionPlanTemplateItem

Individual items within a template (Tasks, DCIs, Events).

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `ActionPlanTemplateVersionId` | Reference | Parent version |
| `Name` | String | Display name for the item |
| `ItemEntityType` | Picklist | `DocumentChecklistItem`, `Task`, `Event`, `RecordAction` |
| `DisplayOrder` | Integer | Controls sequence (1, 2, 3...) |
| `IsRequired` | Boolean | Whether item must be completed |
| `IsActive` | Boolean | Whether item is active |
| `UniqueName` | String | Stable identifier (useful for references) |

**Creation:**
```json
POST /services/data/v62.0/sobjects/ActionPlanTemplateItem
{
    "ActionPlanTemplateVersionId": "<version_id>",
    "Name": "Broker Agreement",
    "DisplayOrder": 1,
    "IsRequired": true,
    "ItemEntityType": "DocumentChecklistItem",
    "UniqueName": "dci_broker_agreement",
    "IsActive": true
}
```

---

## ActionPlanTemplateItemValue

Field values that pre-populate when an item is instantiated.

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `ActionPlanTemplateItemId` | Reference | Parent item |
| `ItemEntityFieldName` | String | **Full qualified**: `Task.Subject`, `DocumentChecklistItem.Name` |
| `ValueLiteral` | String | The value to set on the field |
| `Name` | String | Label for the value |
| `IsActive` | Boolean | |
| `ItemEntityType` | Picklist | **READ-ONLY** — auto-inherited from parent item |

**CRITICAL:** Do NOT include `ItemEntityType` in the creation payload. It auto-populates from the parent `ActionPlanTemplateItem`.

**Common ItemEntityFieldName values:**

For `DocumentChecklistItem`:
| Field Name | Purpose | Example Value |
|------------|---------|---------------|
| `DocumentChecklistItem.Name` | Document name | `"Broker Agreement"` |
| `DocumentChecklistItem.Status` | Initial status | `"New"` |
| `DocumentChecklistItem.Instruction` | Instructions for collecting | `"Collect the signed..."` |

For `Task`:
| Field Name | Purpose | Example Value |
|------------|---------|---------------|
| `Task.Subject` | Task subject line | `"Schedule introduction call"` |
| `Task.Priority` | Priority level | `"High"`, `"Normal"`, `"Low"` |
| `Task.Status` | Initial status | `"Not Started"` |
| `Task.Description` | Detailed description | `"Schedule and conduct..."` |

**Creation:**
```json
POST /services/data/v62.0/sobjects/ActionPlanTemplateItemValue
{
    "ActionPlanTemplateItemId": "<item_id>",
    "ItemEntityFieldName": "Task.Description",
    "ValueLiteral": "Detailed task instructions here",
    "Name": "Description",
    "IsActive": true
}
```

---

## ActionPlan (Instance)

An instantiated action plan on a target record.

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `Name` | String | Plan name |
| `ActionPlanTemplateVersionId` | Reference | Source template version (**must be Final**) |
| `TargetId` | Reference | Target record (Account, Lead, etc.) |
| `StartDate` | Date | **Required** — creation fails without it |
| `ActionPlanState` | Picklist | `Not Started`, `In Progress`, `Completed`, `Canceled` |
| `ActionPlanType` | Picklist | `Industries` or `Standard` |
| `StatusCode` | String | CamelCase version of state |

**GOTCHA:** The API field is `ActionPlanState`, NOT `Status`. The UI displays "Status" but the API name is different.

**Creation:**
```json
POST /services/data/v62.0/sobjects/ActionPlan
{
    "Name": "Onboarding - Acme Insurance",
    "ActionPlanTemplateVersionId": "<version_id_with_Final_status>",
    "TargetId": "<account_id>",
    "StartDate": "2026-02-13",
    "ActionPlanType": "Industries",
    "ActionPlanState": "Not Started"
}
```

Error if version is not Final: *"You can't create an action plan based on an inactive action plan template. Select an action plan template version with a status of Published and try again."*

---

## ActionPlanItem (Instance)

Individual items within an instantiated action plan.

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `ActionPlanId` | Reference | Parent action plan |
| `ItemId` | Reference | **Polymorphic** — DocumentChecklistItem, Task, Event, or RecordAction |
| `ItemState` | Picklist | `Pending`, `InProgress`, `Completed`, `Canceled`, `Deleted`, `Skipped` |
| `DisplayOrder` | Integer | Sequence |
| `IsRequired` | Boolean | |
| `DependencyStatus` | Picklist | `None`, `WaitingOnPrevious`, `Created`, `Error` |
| `ActionPlanTemplateItemId` | Reference | Links back to template definition |

---

## DocumentChecklistItem

Document collection tracking record, auto-created by Industries Action Plans.

| Field | Type | Notes |
|-------|------|-------|
| `Id` | ID | |
| `Name` | String | Document name |
| `Status` | Picklist | `New`, `Pending`, `Accepted`, `Rejected` |
| `ParentRecordId` | Reference | **Links to Account**, NOT ActionPlan |
| `Instruction` | TextArea | Collection instructions |
| `Comments` | TextArea | Notes/issues |
| `IsRequired` | Boolean | |
| `IsAccepted` | Boolean | |
| `IsFrozen` | Boolean | |
| `WhoId` | Reference | Polymorphic: Applicant, Contact, or User |
| `DocumentTypeId` | Reference | Classification lookup |
| `DocumentCategoryId` | Reference | Category lookup |
| `ReceivedDocumentId` | Reference | Links to uploaded ReceivedDocument |
| `ValidatedById` | Reference(User) | Who validated |
| `ValidationDateTime` | DateTime | When validated |

**GOTCHA:** `ParentRecordId` supports 53+ object types including Account, Lead, Opportunity, InsurancePolicy, Claim, etc. It does NOT link via ActionPlanId.

**Query DCIs for an Account:**
```sql
SELECT Id, Name, Status, Instruction, ParentRecordId
FROM DocumentChecklistItem
WHERE ParentRecordId = '<account_id>'
ORDER BY Name
```
