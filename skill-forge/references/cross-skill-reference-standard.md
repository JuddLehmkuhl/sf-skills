# Cross-Skill Reference Standard

How to write proper cross-skill references so skills integrate cleanly into
orchestration chains.

## Reference Table Format

Every skill that interacts with other skills MUST include this table:

```markdown
## Cross-Skill Integration

| Skill | Direction | Relationship | Key Integration Point |
|-------|-----------|-------------|----------------------|
| sf-metadata | UPSTREAM | PRIMARY | Must create objects/fields before this skill runs |
| sf-deploy | DOWNSTREAM | PRIMARY | Invoke after generation to deploy artifacts |
| sf-testing | DOWNSTREAM | SECONDARY | Optional: run tests after deploy |
| sf-debug | LATERAL | SECONDARY | Use when deployment fails for log analysis |
```

## Direction Values

| Direction | Meaning |
|-----------|---------|
| UPSTREAM | Must run BEFORE this skill |
| DOWNSTREAM | Runs AFTER this skill |
| LATERAL | Can run independently alongside this skill |
| BIDIRECTIONAL | Each skill can invoke the other |

## Relationship Types

| Type | Meaning |
|------|---------|
| PRIMARY | Required dependency; skill cannot function without it |
| SECONDARY | Optional enhancement; skill works without it |

## Invocation Syntax

When referencing how to invoke another skill, use this format:

```markdown
After generating flow XML, invoke `Skill(sf-deploy)` to deploy to the target org.
```

This makes it clear to Claude that another skill should be loaded and triggered,
not just mentioned in passing.

## Bidirectional Verification

Cross-references must be bidirectional. If `sf-flow` lists `sf-metadata` as
UPSTREAM, then `sf-metadata` must list `sf-flow` as DOWNSTREAM. Run this check
during bulk audit:

```
For each skill A with cross-ref to skill B:
  1. Open skill B's SKILL.md
  2. Verify skill A appears in B's cross-skill table
  3. Verify direction is complementary (UPSTREAM <-> DOWNSTREAM)
  4. Flag any one-way references for correction
```
