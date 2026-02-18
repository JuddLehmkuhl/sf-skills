# Token Efficiency Guidelines

Token efficiency is the most common systemic issue across skill libraries.
Every token in SKILL.md competes with conversation context. Apply these rules
to keep skills lean without sacrificing value.

## What Goes Where

| Content Type | Location | Rule of Thumb |
|-------------|----------|---------------|
| Core workflow steps | SKILL.md body | Always inline; this is why the skill exists |
| Gotcha tables (< 20 rows) | SKILL.md body | High value, low token cost; keep inline |
| Gotcha tables (20+ rows) | references/ | Split by category, link from SKILL.md |
| CLI quick reference | SKILL.md body | Keep inline; 10-20 commands maximum |
| Code templates (> 30 lines) | assets/ or templates/ | Reference by path; never inline XML/JSON templates |
| Completion summary templates | references/ | Always in references/; boilerplate wastes SKILL.md tokens |
| API field reference tables | references/ | Too large for SKILL.md; load on demand |
| Decision trees (> 10 branches) | references/ | Inline a summary, link to full version |
| Example interactions | references/ | 1-2 inline examples OK; 3+ goes to references/ |
| XML metadata templates | assets/ or templates/ | Never inline; always file paths |

## Token Budget Guidelines

| Skill Component | Target Budget |
|----------------|---------------|
| Frontmatter (name + description) | 50-100 tokens |
| SKILL.md body | 1,500-3,000 tokens (300-500 lines) |
| Individual reference file | 500-2,000 tokens each |
| Total skill context load | < 5,000 tokens when fully loaded |

## Anti-Pattern: Inline Templates

```markdown
<!-- BAD: 40-line XML template inline in SKILL.md -->
## Field Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>MyField__c</fullName>
    ... (35 more lines)
</CustomField>
```

<!-- GOOD: Reference to template file -->
## Field Template
Use `assets/templates/custom-field.xml` as the base template.
Substitute `{{FIELD_NAME}}`, `{{FIELD_TYPE}}`, and `{{FIELD_LENGTH}}`.
```

Three lines of instruction replace 40 lines of XML. The XML lives in `assets/`
where it can be read on demand without consuming SKILL.md context.
