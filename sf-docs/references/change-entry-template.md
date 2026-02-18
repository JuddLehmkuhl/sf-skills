# Change Entry Template (Release Notes)

## Writing Rules

- One bolded sentence summarizing the change
- 3-5 bullet points of specific changes
- Keep entire entry under 75 words
- Lead with user impact, not technical details
- Follow Salesforce release notes conventions: state what changed, who benefits, and any action required

## Template

```markdown
## [Feature Name]

**[One sentence: What users can now do or what the system now does]**

- [Change 1 - user-facing impact]
- [Change 2 - user-facing impact]
- [Change 3 - user-facing impact]
```

## Example

```markdown
## Automatic Lead Data Completion

**New leads now automatically receive default values for Lead Source and Status, ensuring complete data for routing and reporting.**

- Leads saved without a Lead Source get a default value automatically
- Leads saved without a Status get a default value automatically
- Applies to all new leads created in any way (manual, import, web form)
```

## Changelog File Convention

Change entries are appended to monthly changelog files:

```
docs/changelog/
├── 2024-12.md    # December 2024 changes
├── 2025-01.md    # January 2025 changes
└── 2025-02.md    # February 2025 changes
```

Each monthly file follows this structure:

```markdown
# Release Notes - [Month Year]

## [Date] - [Release Name or Sprint]

### [Feature 1]
**[Summary sentence]**
- [Change]
- [Change]

### [Feature 2]
**[Summary sentence]**
- [Change]
- [Change]

---

## [Earlier Date] - [Release Name or Sprint]

...
```
