# Feature Summary Template (Business-Facing)

## Writing Rules

**Language:**
- Write for someone who has never seen Salesforce Setup
- No technical terms without plain-English explanation
- No code references, API names, or developer jargon
- No acronyms unless defined AND necessary
- Use "the system" not "Salesforce" where possible

**Tone:**
- Confident and direct
- Focus on what users experience, not how it's built
- Active voice ("The system now does X" not "X has been implemented")
- Short sentences (under 20 words)

**Structure:**
- Lead with what changed for users
- Explain the benefit in human terms
- Keep it under one page
- Use tables for before/after comparisons

## Template

```markdown
# [Feature Name - in business terms]

**Status:** [Ready for Testing / Released]
**Release Date:** [Date]

---

## What's New

[2-3 sentences maximum. What can users do now that they couldn't before? Or: What does the system do now that it didn't before? Write this for someone who will never read past this section.]

---

## Why This Matters

[One paragraph. What problem does this solve? What was frustrating, slow, or error-prone before? What's better now? No technical details.]

---

## What Changed

| Before | After |
|--------|-------|
| [Old user experience] | [New user experience] |
| [Old manual step] | [New automatic behavior] |

---

## Who This Affects

[List roles and what changes for each. Be specific about job functions, not technical roles.]

| Role | What's Different |
|------|------------------|
| [Job title] | [Plain description of change] |

---

## What Happens Automatically

[List automatic behaviors in plain language. "When X happens, the system now Y."]

- When [user action or event], the system now [automatic result]
- When [user action or event], the system now [automatic result]

---

## What's NOT Included

[Set clear expectations. What does this NOT do yet?]

- This does not [limitation in plain terms]
- [Future capability] is planned for a later phase

---

## Questions?

Contact [team/person] for questions about this change.
```

## Example: Trigger Framework (Business Version)

```markdown
# Automatic Lead Data Completion

**Status:** Ready for Testing
**Release Date:** December 2024

---

## What's New

When someone creates a new lead, the system now automatically fills in the Lead Source and Status fields if they're left blank. This ensures every lead has complete information from the moment it's created.

---

## Why This Matters

Previously, leads created without a source or status would cause problems downstream. Assignment rules wouldn't work correctly, reports would show incomplete data, and someone had to manually clean up the gaps. Now the system handles this automatically.

---

## What Changed

| Before | After |
|--------|-------|
| Leads could be saved with blank Lead Source | Lead Source is automatically set if left blank |
| Leads could be saved with blank Status | Status is automatically set if left blank |
| Incomplete leads caused assignment rule failures | All leads have the minimum data needed for routing |

---

## Who This Affects

| Role | What's Different |
|------|------------------|
| Anyone creating leads | You'll notice Lead Source and Status are filled in automatically if you leave them blank |
| Sales managers | Reports will show consistent lead source data |
| Operations | Fewer leads falling through the cracks due to missing data |

---

## What Happens Automatically

- When a lead is created without a Lead Source, the system sets it to the default value
- When a lead is created without a Status, the system sets it to the default value
- This happens instantly when the lead is saved - no delay, no manual step

---

## What's NOT Included

- This does not change leads that already exist in the system
- This does not apply when you edit an existing lead (only new leads)
- Automatic lead assignment (routing to the right person) is planned for a future phase

---

## Questions?

Contact the project team for questions about this change.
```

## Technical vs Business Comparison

| Technical (Bad for Business) | Business-Friendly (Good) |
|------------------------------|--------------------------|
| "Implemented Trigger Actions Framework with metadata-driven dispatch" | "The system now automatically fills in missing lead information" |
| "Custom Metadata configuration enables runtime bypass" | "Settings can be adjusted without waiting for IT" |
| "Bulkified for governor limit compliance" | [Omit - they don't care] |
| "TA_Lead_SetDefaults implements TriggerAction.BeforeInsert" | [Omit - they don't care] |
