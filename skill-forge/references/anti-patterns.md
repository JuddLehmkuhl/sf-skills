# Skill Anti-Patterns

The most common mistakes found in skill libraries. Check every skill against
this list during review.

## 1. Kitchen Sink Skill

**Symptom**: One skill covers 3+ distinct workflows that share no common logic.

**Example**: A single "sf-data" skill that handles SOQL queries, bulk data
loading, test data factories, and data migration — these are four separate concerns.

**Fix**: Split into focused skills. Each skill should answer ONE question:
"What does this skill help me do?" If the answer has "and" in it, consider splitting.

**Test**: Can you describe the skill in one sentence without using "and"?

## 2. README Disguised as Skill

**Symptom**: SKILL.md reads like documentation. Paragraphs explain concepts
instead of giving instructions. Phrases like "Salesforce flows are..." or
"Understanding governor limits is important because..." appear.

**Example**:
```markdown
## About Flows
Flows are a powerful automation tool in Salesforce that allow administrators
to build complex business logic without code. There are several types of flows
including screen flows, record-triggered flows, and scheduled flows...
```

**Fix**: Delete concept explanations. Claude already knows what flows are.
Replace with actionable instructions:
```markdown
## Flow Generation
1. Ask: Screen flow, record-triggered, or scheduled?
2. Select template from Phase 2 table
3. Generate XML at `force-app/main/default/flows/`
```

## 3. Copy-Paste Template Bloat

**Symptom**: SKILL.md contains 100+ lines of XML, JSON, or YAML templates
that should be in `assets/` or `templates/`.

**Test**: Count lines of code blocks in SKILL.md. If they exceed 30% of total
lines, the skill has template bloat.

**Fix**: Move templates to `assets/` or `templates/`. Replace with a 2-3 line
instruction referencing the file path and listing substitution variables.

## 4. Missing Cross-References

**Symptom**: Skill operates in isolation. No mention of upstream or downstream
skills. User must manually figure out the orchestration order.

**Test**: Search SKILL.md for other skill names. If zero hits, cross-refs are missing.

**Fix**: Add a Cross-Skill Integration table (see `references/cross-skill-reference-standard.md`).
At minimum, declare the orchestration position.

## 5. Outdated CLI Commands

**Symptom**: Uses `sfdx` (v1) commands instead of `sf` (v2). Uses deprecated
flags like `--checkonly` instead of `--dry-run`, or `--targetusername` instead
of `--target-org`.

**Common v1 -> v2 Migrations**:

| Deprecated (v1) | Current (v2) |
|-----------------|--------------|
| `sfdx force:source:deploy` | `sf project deploy start` |
| `sfdx force:source:retrieve` | `sf project retrieve start` |
| `sfdx force:apex:test:run` | `sf apex run test` |
| `sfdx force:data:soql:query` | `sf data query` |
| `--targetusername` | `--target-org` / `-o` |
| `--checkonly` | `--dry-run` |
| `--testlevel` | `--test-level` |
| `sfdx force:org:open` | `sf org open` |
| `sfdx force:apex:execute` | `sf apex run` |

**Fix**: Find-and-replace all v1 commands. Verify with `sf --help` for current syntax.

## 6. No Guardrails

**Symptom**: Skill provides the happy path but no warning about what goes wrong.
No gotcha table, no common errors table, no anti-patterns.

**Test**: Search for "Gotcha", "Error", "Warning", "CRITICAL" in SKILL.md.
If none found, guardrails are missing.

**Fix**: Add a Gotchas table (minimum 5 entries) and a Common Errors table
(minimum 3 entries). Source from production incidents, Stack Exchange, and
Salesforce Known Issues.
