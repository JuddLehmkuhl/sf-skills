# Sharing Model & Security -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## Organization-Wide Defaults (OWD) Matrix

| OWD Setting | Owner Access | Other Users | Use Case |
|------------|-------------|-------------|----------|
| **Private** | Full (CRUD) | No access | Sensitive data: Salary, Medical, Cases |
| **Public Read Only** | Full (CRUD) | Read only | Reference data users need to see but not edit |
| **Public Read/Write** | Full (CRUD) | Read + Edit | Collaborative data: Activities, Notes |
| **Public Read/Write/Transfer** | Full (CRUD) | Read + Edit + Transfer | Cases, Leads that can be reassigned |
| **Controlled by Parent** | Inherited | Inherited from parent | Detail in Master-Detail relationship |
| **Public Full Access** | Full (CRUD) | Full (CRUD) | Campaigns (special) |

**Setting OWD**:
- Setup -> Sharing Settings -> Organization-Wide Defaults
- Changes trigger recalculation (can take hours on large orgs)
- Start restrictive (Private), then open up with sharing rules

## Sharing Rules Types

| Rule Type | Definition | Example |
|-----------|-----------|---------|
| **Owner-Based** | Share records owned by users in Group A with Group B | "Share all Cases owned by US Support team with US Managers" |
| **Criteria-Based** | Share records matching field criteria with a group | "Share all Opportunities where Amount > 1M with VP Sales role" |
| **Guest User** | Share records with unauthenticated site users | "Share published Knowledge Articles with guest users" |
| **Manual Sharing** | One-off sharing by record owner or admin | User clicks "Sharing" button on record |

**Sharing Rule Metadata (XML)**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SharingRules xmlns="http://soap.sforce.com/2006/04/metadata">
    <sharingCriteriaRules>
        <fullName>High_Value_Opportunities</fullName>
        <accessLevel>Read</accessLevel>
        <description>Share high-value opps with executive team</description>
        <label>High Value Opportunities</label>
        <sharedTo>
            <role>VP_Sales</role>
        </sharedTo>
        <criteriaItems>
            <field>Amount</field>
            <operation>greaterOrEqual</operation>
            <value>1000000</value>
        </criteriaItems>
    </sharingCriteriaRules>
</SharingRules>
```

## Role Hierarchy

- Role hierarchy grants **read access** (or read/write, depending on OWD) upward
- Users higher in the hierarchy can see records owned by users below them
- Does NOT grant access downward
- Roles are separate from Profiles -- a user has one Profile and one Role

**Role hierarchy metadata path**: `force-app/main/default/roles/[RoleName].role-meta.xml`

## Apex Sharing (Programmatic)

```java
// Create a sharing record programmatically
Account_Share__Share shareRecord = new Account_Share__Share();
shareRecord.ParentId = recordId;       // Record to share
shareRecord.UserOrGroupId = userId;     // User or Group receiving access
shareRecord.AccessLevel = 'Edit';       // Read or Edit
shareRecord.RowCause = Schema.Account_Share__Share.RowCause.Manual;
insert shareRecord;
```

**Apex sharing rules**:
- Only works when OWD is Private or Public Read Only
- `RowCause` can be `Manual` or a custom Apex Sharing Reason
- Custom Apex Sharing Reasons survive ownership changes (Manual does not)
- Must be explicitly deleted when no longer needed

## Sharing Model in Different Contexts

| Context | Enforced By | Notes |
|---------|------------|-------|
| Standard UI | Automatic | Sharing always enforced |
| Apex (default) | `without sharing` runs as system | Must explicitly use `with sharing` |
| Apex (`with sharing`) | Enforced | Running user's sharing rules applied |
| Apex (`inherited sharing`) | Inherited from caller | Safe default for utility classes |
| Flow | Running user context | Sharing enforced unless "System Context" |
| SOQL (`USER_MODE`) | Enforced | `[SELECT ... FROM Account WITH USER_MODE]` |
| SOQL (`SYSTEM_MODE`) | Not enforced | Default in Apex system context |
| REST API | Running user | Always enforced |
| LWC Wire | Running user | Sharing enforced via wire adapter |

## Shield Platform Encryption Considerations

| Consideration | Details |
|--------------|---------|
| Encrypted fields cannot be filtered | SOQL WHERE clause cannot filter on encrypted fields |
| Encrypted fields cannot be sorted | ORDER BY not supported on encrypted fields |
| Formula fields limitations | Formulas referencing encrypted fields lose encryption |
| Custom indexes not supported | Cannot create custom indexes on encrypted fields |
| Deterministic encryption | Allows filtering on exact match (equality only), not LIKE |
| Metadata impact | Encrypted field metadata includes `<encryptionScheme>` element |
