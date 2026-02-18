# Salesforce Skill Design Patterns

Proven patterns for building Claude Code skills that work with Salesforce orgs.
These patterns emerged from the sf-skills collection (sf-metadata, sf-flow,
sf-deploy, sf-apex, sf-testing) and encode production lessons.

## Table of Contents

1. [Orchestration Chain](#orchestration-chain)
2. [5-Phase Workflow](#5-phase-workflow)
3. [Gotcha Tables](#gotcha-tables)
4. [Cross-Skill Integration](#cross-skill-integration)
5. [CLI Quick Reference](#cli-quick-reference)
6. [Template Directories](#template-directories)
7. [FLS Warning Pattern](#fls-warning-pattern)
8. [Common Errors Table](#common-errors-table)
9. [Post-Deployment Checklist](#post-deployment-checklist)
10. [Correct vs Wrong Pattern](#correct-vs-wrong-pattern)

---

## Orchestration Chain

Every Salesforce skill must declare its position in the metadata dependency
pipeline. This prevents agents from creating flows that reference non-existent
fields, or deploying before objects are ready.

```markdown
## CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-flow)

Objects/fields must exist before flows reference them.
Flows must exist before deployment. Deploy before test data.
```

The chain is a cross-skill contract. Each skill trusts that upstream skills have
completed their work before it begins.

---

## 5-Phase Workflow

All Salesforce skills follow this phase structure:

### Phase 1: Requirements Gathering

Use `AskUserQuestion` to collect inputs. Check existing metadata via `Glob`.

```markdown
### Phase 1: Requirements

1. Operation type: Generate or Query?
2. If generating: metadata type, target object, specific requirements
3. Check existing: `Glob: **/*-meta.xml`
```

### Phase 2: Design / Template Selection

Map user's choice to a specific template file:

```markdown
### Phase 2: Template Selection

| Type | Template |
|------|----------|
| Text Field | `templates/fields/text-field.xml` |
| Picklist | `templates/fields/picklist-field.xml` |
| Lookup | `templates/fields/lookup-field.xml` |
```

### Phase 3: Generation + Validation

Create artifacts in the correct `force-app/` path. Run validation.

```markdown
### Phase 3: Generate

1. Create file at `force-app/main/default/objects/<Object>/fields/<Field>.field-meta.xml`
2. Validate XML structure
3. Score against quality rubric
```

Optional **Phase 3.5**: Auto-generate Permission Set for new fields (sf-metadata pattern).

### Phase 4: Deployment

Always validate before deploying:

```markdown
### Phase 4: Deploy

1. Dry run: `sf project deploy start --dry-run --source-dir force-app -o alias`
2. If clean: `sf project deploy start --source-dir force-app -o alias`
3. Invoke sf-deploy skill for complex deployments
```

### Phase 5: Verification

CLI-based verification + completion summary:

```markdown
### Phase 5: Verify

1. Check deployment: `sf project deploy report --job-id <id>`
2. Verify flows active: query FlowDefinitionView
3. Verify FLS: check permission set assignment
4. Print completion summary
```

---

## Gotcha Tables

The highest-value section of any Salesforce skill. Encode production failures
as a compact lookup table:

```markdown
## Gotchas

| Gotcha | Details |
|--------|---------|
| Fields invisible after deploy | FLS not configured — deploy Permission Set and assign to user |
| Flow deploys as inactive | XML `<status>Active</status>` doesn't guarantee activation — check in Setup |
| Person Account layout prefix | Use `PersonAccount-` not `Account-` for PA page layouts |
```

**Rules:**
- Labels under 5 words
- Include the fix inline (not in a separate column)
- Order by frequency
- Add new gotchas as discovered — this table grows over time

---

## Cross-Skill Integration

Show which skills this skill calls (outbound) and which call it (inbound):

```markdown
## Cross-Skill Integration

| Direction | Skill | When |
|-----------|-------|------|
| Outbound | sf-deploy | After generation, to deploy metadata |
| Outbound | sf-metadata | To discover existing fields before generating flows |
| Inbound | sf-flow | Calls this skill to deploy generated flows |
```

---

## CLI Quick Reference

Present `sf` CLI v2 commands in fenced bash blocks, grouped by operation:

```markdown
## CLI Quick Reference

### Deploy
```bash
# Validate (dry run)
sf project deploy start --dry-run --source-dir force-app -o alias

# Deploy
sf project deploy start --source-dir force-app -o alias

# Check status
sf project deploy report --job-id <id>
```

### Query
```bash
# Check flow activation
sf data query -q "SELECT Label, ActiveVersionId FROM FlowDefinitionView WHERE Label LIKE '%MyFlow%'" -o alias

# Check permission set assignment
sf data query -q "SELECT Id FROM PermissionSetAssignment WHERE PermissionSet.Name = 'MyPermSet'" -o alias
```
```

**Rules:**
- Always use `sf` (v2), never `sfdx` (v1)
- Use `--dry-run` not `--checkonly` (v1 syntax)
- Include inline `#` comments for non-obvious flags

---

## Template Directories

Organize XML templates by metadata type:

```
templates/
├── fields/
│   ├── text-field.xml
│   ├── picklist-field.xml
│   ├── lookup-field.xml
│   └── formula-field.xml
├── objects/
│   └── custom-object.xml
├── flows/
│   ├── record-triggered-before-save.xml
│   └── screen-flow.xml
└── permission-sets/
    └── base-permission-set.xml
```

Each Phase 2 includes a **template selection table** mapping the user's choice
to a specific file. This makes template selection deterministic.

---

## FLS Warning Pattern

Include this warning in any skill that creates fields or objects:

```markdown
## CRITICAL: Field-Level Security

**Deployed fields are INVISIBLE until FLS is configured!**

After creating objects/fields:
1. Deploy Permission Set granting field access
2. Assign Permission Set: `sf org assign permset --name PSName -o alias`
3. Verify field visibility in the UI
```

This is the single most common Salesforce deployment failure.

---

## Common Errors Table

Map error messages to fixes:

```markdown
## Common Errors

| Error | Fix |
|-------|-----|
| `no CustomObject named X found` | Deploy objects before permission sets |
| `Flow is invalid` | Deploy referenced objects/fields first |
| `Insufficient permissions` | Check Manage Flow permission |
| `Version conflict` | Deactivate old flow version first |
```

---

## Post-Deployment Checklist

Include in any skill that involves deployment:

```markdown
## Post-Deployment Checklist

1. **Flows active?** Setup > Flows — may deploy as inactive
2. **Permission sets assigned?** Deploy does NOT auto-assign
3. **Org features enabled?** Path Settings, Account Teams need manual toggle
4. **Browser cache cleared?** Cmd+Shift+R after layout changes
5. **Record-type picklist defaults?** RT defaults override field defaults
```

---

## Correct vs Wrong Pattern

Show the right way alongside the wrong way for critical operations:

```markdown
### Always Validate Before Deploying

```bash
# CORRECT: Validate first
sf project deploy start --dry-run --source-dir force-app -o alias
sf project deploy start --source-dir force-app -o alias

# WRONG: Deploy without validation
sf project deploy start --source-dir force-app -o alias  # Risky!
```
```

This pattern is effective for teaching `--dry-run` first, test data quantities
(251+ records for batch boundary testing), and `sf` vs `sfdx` command syntax.
