# Advanced Validation Rule Patterns -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## Core Patterns

| Pattern | Formula | Use |
|---------|---------|-----|
| Conditional Required | `AND(ISPICKVAL(Status,'Closed'), ISBLANK(Close_Date__c))` | Field required when condition met |
| Email Regex | `NOT(REGEX(Email__c, "^[a-zA-Z0-9._-]+@..."))` | Format validation |
| Future Date | `Due_Date__c < TODAY()` | Date constraints |
| Cross-Object | `AND(Account.Type != 'Customer', Amount__c > 100000)` | Related field checks |

## ISNEW() vs ISCHANGED() Patterns

| Function | Behavior | Use Case |
|----------|----------|----------|
| `ISNEW()` | True only on record creation | Validate initial values at creation |
| `ISCHANGED(field)` | True when field value changes (update only) | Prevent changes to locked fields |
| `PRIORVALUE(field)` | Returns the previous value of a field | Compare old vs new values |

**Prevent status regression**:
```
AND(
    NOT(ISNEW()),
    ISCHANGED(Status__c),
    CASE(
        TEXT(PRIORVALUE(Status__c)),
        "Draft", 1,
        "Submitted", 2,
        "Approved", 3,
        "Completed", 4,
        0
    ) > CASE(
        TEXT(Status__c),
        "Draft", 1,
        "Submitted", 2,
        "Approved", 3,
        "Completed", 4,
        0
    )
)
```
Error message: "Status cannot be reverted to a previous stage."

## PRIORVALUE for Update Detection

```
/* Detect when a critical field changes and require a reason */
AND(
    NOT(ISNEW()),
    ISCHANGED(Amount),
    OR(
        PRIORVALUE(Amount) > Amount * 1.5,
        Amount > PRIORVALUE(Amount) * 1.5
    ),
    ISBLANK(Amount_Change_Reason__c)
)
```
Error message: "A change reason is required when amount changes by more than 50%."

## Multi-Field Conditional Validation

```
/* Require multiple fields when opportunity reaches Proposal stage */
AND(
    ISPICKVAL(StageName, 'Proposal'),
    OR(
        ISBLANK(Proposal_Date__c),
        ISBLANK(Proposal_Amount__c),
        ISBLANK(Decision_Maker__c)
    )
)
```
Error message: "Proposal Date, Proposal Amount, and Decision Maker are required at the Proposal stage."

## Cross-Object Validation with VLOOKUP

**Note**: `VLOOKUP` is only available in validation rules, not in formula fields.

```
/* Ensure the assigned user has the required certification */
VLOOKUP(
    $ObjectType.Certification__c.Fields.Is_Active__c,
    $ObjectType.Certification__c.Fields.User__c,
    OwnerId
) = false
```
Error message: "Record owner must have an active certification."

## Bypass Mechanisms

**Using Custom Permission** (recommended):
```
AND(
    NOT($Permission.Bypass_Validation),
    /* actual validation logic here */
    ISBLANK(Required_Field__c)
)
```

**Using Custom Setting (hierarchy)**:
```
AND(
    NOT($Setup.Validation_Bypass__c.Bypass_All__c),
    /* actual validation logic here */
    ISBLANK(Required_Field__c)
)
```

**Using Custom Metadata Type**:
```
AND(
    NOT($CustomMetadata.Validation_Config__mdt.Default.Bypass_Enabled__c),
    /* actual validation logic here */
    ISBLANK(Required_Field__c)
)
```

## Validation Rule Limits

| Limit | Value |
|-------|-------|
| Active validation rules per object | 500 |
| Formula size (compiled) | 5,000 characters |
| Formula size (uncompiled) | 3,900 characters |
| VLOOKUP calls per rule | 1 |
| Cross-object references | 10 levels (spanning relationships) |
| REGEX pattern length | 16,384 characters |
| Evaluation order | Validation rules fire AFTER before-save flows and before-save triggers |
