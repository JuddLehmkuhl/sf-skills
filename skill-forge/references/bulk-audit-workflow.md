# Bulk Audit Workflow

How to audit and enrich an entire skill library systematically.

## Phase 1: Discovery

```bash
# Find all skills
Glob: ~/.claude/skills/**/SKILL.md

# Count lines for each
for f in ~/.claude/skills/**/SKILL.md; do echo "$(wc -l < "$f") $f"; done | sort -n
```

## Phase 2: Score All Skills

Create a scoring table:

| Skill | Lines | Structure | Density | Complete | Integration | Total | Priority |
|-------|-------|-----------|---------|----------|-------------|-------|----------|
| skill-forge | 230 | 18 | 15 | 10 | 12 | 55 | HIGH |
| sf-deploy | 460 | 20 | 18 | 16 | 14 | 68 | MEDIUM |
| sf-apex | 1132 | 23 | 22 | 22 | 20 | 87 | LOW |

## Phase 3: Prioritize

Sort by total score ascending. Enrich in this order:
1. Skills scoring < 50 (critical — may produce wrong output)
2. Skills scoring 50-69 (below production threshold)
3. Skills scoring 70-84 (functional but could be better)
4. Skills scoring 85+ (polish only)

## Phase 4: Parallel Enrichment

For large libraries, dispatch enrichment in batches:
- 4-6 skills per batch (each in its own agent with Opus model)
- Each agent follows the Enrichment Workflow (`references/enrichment-workflow.md`)
- Commit after each batch completes
- Run bulk validation between batches

```bash
# Validate entire library after each batch
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/bulk_validate.py --errors-only
```

## Phase 5: Regression Check

After all enrichments, verify:
- No skill dropped below its pre-enrichment score
- All skills pass validation
- Cross-skill references are bidirectional (if A references B, B references A)
- Total library token budget is reasonable (sum all SKILL.md files)
