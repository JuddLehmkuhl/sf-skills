---
name: skill-forge
description: >
  Create, validate, package, and manage Claude Code skills. Use when users want
  to create a new skill, update an existing skill, validate skill structure,
  bulk-validate all installed skills, or package a skill for distribution. Also
  use for Salesforce-specific skill patterns (orchestration chains, 5-phase
  workflows, template directories, gotcha tables). Combines Anthropic's official
  skill-creator design philosophy with production tooling.
license: MIT
metadata:
  version: "1.0.0"
  author: "Judd Lehmkuhl"
  enriched: "2026-02-18"
---

# Skill Forge

Create well-designed, production-ready Claude Code skills. This skill encodes
Anthropic's official design principles (progressive disclosure, context economy)
with battle-tested tooling for validation and packaging, plus domain-specific
patterns for Salesforce skill development.

## Core Principles

### Context Economy

The context window is shared. Skills compete for space with conversation history,
other skills, and user requests. **Default assumption: Claude is already smart.**
Only add context Claude doesn't already have. Challenge every paragraph: "Does
this justify its token cost?"

Prefer concise examples over verbose explanations.

### Progressive Disclosure (3 Levels)

1. **Metadata** (~100 words) — `name` + `description` in frontmatter. Always in context.
2. **SKILL.md body** (<500 lines) — Loaded when skill triggers. Core workflows only.
3. **Bundled resources** (unlimited) — `references/`, `scripts/`, `assets/`. Loaded on demand.

Keep SKILL.md lean. Move detailed references, schemas, and examples into
`references/` files. Reference them from SKILL.md with clear "when to read" guidance.

### Degrees of Freedom

Match specificity to fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent
- **Medium freedom** (pseudocode/scripts with params): Preferred pattern exists, some variation OK
- **Low freedom** (exact scripts, few params): Fragile operations, consistency critical

---

## Skill Anatomy

```
skill-name/
├── SKILL.md              # Required — frontmatter + instructions
├── scripts/              # Optional — executable automation (Python/Bash)
├── references/           # Optional — docs loaded into context on demand
└── assets/               # Optional — templates, images, fonts (NOT loaded into context)
```

### SKILL.md Frontmatter (Required)

Only `name` and `description` are required. These are the ONLY fields Claude
reads to determine when to trigger the skill.

```yaml
---
name: my-skill-name
description: >
  What the skill does AND when to use it. Be specific about triggers.
  Example: "Use when creating PDF forms, extracting text from PDFs,
  or merging multiple PDF files."
---
```

**Optional fields:** `license`, `metadata`, `compatibility`

**Do NOT add** `version`, `allowed-tools`, `tags`, `author`, `examples`,
`keywords`, `dependencies`, `test_config` to frontmatter — these are not read
by Claude and waste tokens.

### SKILL.md Body

Choose a structure pattern:

| Pattern | Best For | Example |
|---------|----------|---------|
| **Workflow** | Sequential processes | Phase 1 -> Phase 2 -> Phase 3 |
| **Task-based** | Tool collections | "Merge PDFs" / "Split PDFs" / "Extract Text" |
| **Reference** | Standards, specs | "Colors" / "Typography" / "Voice" |
| **Capabilities** | Integrated systems | "### 1. Feature" / "### 2. Feature" |

Mix patterns as needed. Most skills combine workflow + task-based.

### Resources

**`scripts/`** — Deterministic code that gets rewritten repeatedly. Token-efficient
because scripts can execute without loading into context. Test scripts before shipping.

**`references/`** — Documentation Claude reads on demand. Keep individual files
focused. For files >100 lines, add a table of contents at top. Link from SKILL.md
with clear trigger: "See `references/api.md` when working with API endpoints."

**`assets/`** — Files used in output (templates, images, boilerplate). Never loaded
into context. Copied or modified by Claude during execution.

### What NOT to Include

- README.md, CHANGELOG.md, INSTALLATION_GUIDE.md
- User-facing documentation about the skill itself
- Setup/testing procedures for the skill

---

## Workflow: Creating a Skill

### Step 1: Understand with Examples

Before building, gather concrete usage examples:
- "What would a user say that triggers this skill?"
- "Can you give 2-3 example interactions?"
- "What resources (scripts, references, templates) would help?"

### Step 2: Plan Resources

For each example, identify:
- Code that gets rewritten -> `scripts/`
- Documentation Claude needs -> `references/`
- Files used in output -> `assets/`

### Step 3: Initialize

```bash
python3 scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates a scaffold with SKILL.md template and example resource directories.

### Step 4: Implement

1. Start with `scripts/` and `references/` — these are the reusable value
2. Write SKILL.md body — workflows, examples, gotcha tables
3. Delete unused example files and empty directories
4. Keep SKILL.md under 500 lines — split to references if approaching limit

### Step 5: Validate

```bash
python3 scripts/validate_skill.py <path/to/skill-directory>
```

### Step 6: Package

```bash
python3 scripts/package_skill.py <path/to/skill-directory> [output-dir]
```

Creates a `.skill` file (zip format) for distribution.

### Step 7: Bulk Validate (all installed skills)

```bash
python3 scripts/bulk_validate.py [--errors-only] [--format json]
```

Discovers and validates all skills in `~/.claude/skills/` and `./.claude/skills/`.

---

## Quality Scoring Framework

Every skill can be measured against four dimensions. Use this framework when
creating, reviewing, or deciding whether to enrich a skill.

### Scoring Dimensions

| Dimension | Points | What It Measures |
|-----------|--------|------------------|
| Structure | 0-25 | Frontmatter quality, SKILL.md organization, resource usage |
| Content Density | 0-25 | Token-to-value ratio, actionability, no filler |
| Completeness | 0-25 | All necessary sections for the skill type |
| Integration | 0-25 | Cross-skill references, orchestration, deployment path |
| **Total** | **0-100** | **Minimum 70 for production use** |

### Structure Score Rubric (0-25)

| Score | Criteria |
|-------|----------|
| 0-5 | Missing frontmatter or broken YAML; no section headings |
| 6-10 | Frontmatter present but description vague; flat structure, no sections |
| 11-15 | Valid frontmatter with specific triggers; headings present but inconsistent |
| 16-20 | Well-organized sections; resources directory exists; templates separated |
| 21-25 | Progressive disclosure fully applied; scripts/, references/, assets/ used correctly; SKILL.md under 500 lines with heavy content in references |

### Content Density Score Rubric (0-25)

| Score | Criteria |
|-------|----------|
| 0-5 | Mostly conceptual explanation; reads like a README; no actionable instructions |
| 6-10 | Some actionable content but padded with "why" explanations Claude does not need |
| 11-15 | Actionable instructions dominate; occasional filler paragraphs remain |
| 16-20 | Every section provides instructions, tables, or commands; examples are concise |
| 21-25 | Zero filler; every line is either a command, a table row, or a decision point; completion summaries and boilerplate moved to references/ |

### Completeness Score Rubric (0-25)

| Score | Criteria |
|-------|----------|
| 0-5 | Covers only one use case; missing critical sections |
| 6-10 | Covers primary workflow but no error handling or edge cases |
| 11-15 | Primary workflow + some gotchas; missing CLI commands or anti-patterns |
| 16-20 | Full workflow + gotcha table + CLI reference + common errors |
| 21-25 | All sections present including anti-patterns, correct-vs-wrong examples, decision trees, and verification steps |

### Integration Score Rubric (0-25)

| Score | Criteria |
|-------|----------|
| 0-5 | No mention of other skills; operates in isolation |
| 6-10 | Mentions related skills in prose but no structured references |
| 11-15 | Cross-skill table present; orchestration order declared |
| 16-20 | Inbound/outbound skill references; Skill() invocation syntax used; deployment path clear |
| 21-25 | Full integration map with direction, relationship type, and key integration points; works seamlessly in orchestration chains |

### Scoring for Salesforce Skills

Salesforce skills have additional completeness requirements beyond generic skills:

| Required Section | Points Deducted If Missing |
|------------------|---------------------------|
| Orchestration Order | -5 |
| Gotcha Table (5+ entries) | -5 |
| Cross-Skill Integration Table | -3 |
| CLI Quick Reference | -3 |
| Common Errors Table | -3 |
| FLS Warning (if field/object skill) | -3 |
| Anti-Patterns Section | -2 |
| Correct vs Wrong Examples | -1 |

---

## Skill Improvement Decision Framework

### When to Enrich

Trigger an enrichment pass when any of these conditions are true:

| Condition | Action |
|-----------|--------|
| Quality score < 70/100 | Full enrichment pass |
| Cross-skill references missing | Add integration table and orchestration order |
| Gotcha table absent or < 3 entries | Research production failures and add entries |
| CLI commands use `sfdx` (v1) syntax | Update all commands to `sf` (v2) |
| SKILL.md > 500 lines | Split to references/; reduce inline content |
| No anti-pattern section | Add top 5 anti-patterns for the domain |
| Completion summary inline in SKILL.md | Move to references/completion-summary.md |

### Decision Tree: Enrich vs Rewrite vs Split

```
Is the skill fundamentally about one topic?
├── YES: Is >50% of existing content usable?
│   ├── YES → ENRICH (add missing sections, preserve existing)
│   └── NO → REWRITE (start from scratch, import any good tables)
└── NO: Does it cover 2+ distinct domains?
    └── YES → SPLIT into separate skills, then enrich each
```

**Enrich**: Add new sections to existing SKILL.md. Never remove working content.
Typical enrichment adds 200-400 lines to a 200-line skill.

**Rewrite**: When the skill structure is wrong (e.g., README format instead of
skill format), start over. Copy any gotcha tables or CLI references from the
original — those represent production lessons.

**Split**: When a skill tries to cover too much (e.g., "sf-data" covering SOQL,
DML, data loading, and test factories). Extract each concern into its own skill
with proper cross-references.

---

## Token Efficiency Guidelines

See `references/token-efficiency.md` for the full what-goes-where table, token budgets, and the inline template anti-pattern.

**Key rule**: SKILL.md body should be 1,500-3,000 tokens (300-500 lines). Move templates, large tables, and completion summaries to `references/` or `assets/`.

---

## Skill Anti-Patterns

See `references/anti-patterns.md` for detailed examples and fixes.

**Quick checklist** — flag a skill if any of these are true:

| # | Anti-Pattern | Test |
|---|-------------|------|
| 1 | Kitchen Sink | Covers 3+ unrelated workflows |
| 2 | README Disguised as Skill | Paragraphs explain concepts instead of giving instructions |
| 3 | Template Bloat | Code blocks exceed 30% of SKILL.md lines |
| 4 | Missing Cross-References | Zero mentions of other skill names |
| 5 | Outdated CLI | Uses `sfdx` (v1) instead of `sf` (v2) |
| 6 | No Guardrails | No gotcha table, no common errors, no anti-patterns |

---

## Enrichment Workflow

See `references/enrichment-workflow.md` for the full 7-step process (read, score, identify gaps, research, write, validate, re-score).

**Summary**: Score the skill -> fix the lowest dimension -> validate -> confirm score improved by 15+ points.

---

## Bulk Audit Workflow

See `references/bulk-audit-workflow.md` for the 5-phase library audit process (discover, score, prioritize, parallel enrich, regression check).

**Summary**: Score all skills -> sort ascending -> enrich in batches of 4-6 -> validate between batches.

---

## Cross-Skill Reference Standard

See `references/cross-skill-reference-standard.md` for the full standard (table format, direction values, relationship types, invocation syntax, bidirectional verification).

**Key rule**: Every skill interacting with other skills needs a Cross-Skill Integration table with Direction (UPSTREAM/DOWNSTREAM/LATERAL) and Relationship (PRIMARY/SECONDARY).

---

## Salesforce Skill Patterns

See `references/salesforce-skill-patterns.md` for complete patterns including orchestration chains, 5-phase workflow, gotcha tables, CLI references, template directories, FLS warnings, and correct-vs-wrong examples.

**Required sections for every SF skill**: Orchestration Order, Gotcha Table (5+), Cross-Skill Integration, CLI Quick Reference, Common Errors.

---

## Gotcha Tables: Design Pattern

Gotcha tables are the highest-value section of any Salesforce skill:

```markdown
| Gotcha | Details |
|--------|---------|
| Short label | Concise explanation with the fix inline |
```

Rules: labels under 5 words, include fix inline, order by frequency.

---

## Skill Forge Gotchas

| Gotcha | Details |
|--------|---------|
| Frontmatter YAML parse failure | Ensure `---` delimiters are on their own lines with no leading spaces; use `>` for multi-line description |
| validate_skill.py path must be directory | Pass the skill directory path, not the SKILL.md file path |
| Description too generic | "Use for Salesforce stuff" will never trigger. Be specific: "Use when creating custom fields, objects, or permission sets" |
| Resources not loading | Reference files must be explicitly read by Claude via `Read` tool. Just existing in references/ does not auto-load them |
| Skill > 500 lines | Split to references/ immediately. SKILL.md beyond 500 lines hurts context economy for all other skills |
| init_skill.py creates example files | Delete the example placeholder files after scaffolding. They waste tokens if left in place |
| Package excludes hidden files | `.skill` packaging ignores dotfiles. Do not put critical content in hidden files |

---

## Common Errors

| Error | Fix |
|-------|-----|
| `YAML parse error in frontmatter` | Check for tabs (use spaces only), unescaped colons in description, or missing closing `---` |
| `Missing required field: name` | Add `name:` as first field in frontmatter |
| `Missing required field: description` | Add `description:` field. Use `>` for multi-line |
| `SKILL.md not found` | Ensure file is named exactly `SKILL.md` (case-sensitive) |
| `Empty references directory` | Either add reference files or delete the empty directory |
| `Script not executable` | Run `chmod +x scripts/*.py` on script files |
| `Bulk validate finds no skills` | Check that skills are in `~/.claude/skills/` or `./.claude/skills/` (the two default search paths) |

---

## CLI Quick Reference

```bash
# Validate a single skill
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/validate_skill.py /path/to/skill-dir

# Validate all installed skills
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/bulk_validate.py

# Validate all, show only errors
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/bulk_validate.py --errors-only

# Initialize a new skill scaffold
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/init_skill.py my-skill --path ./output

# Package for distribution
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/package_skill.py /path/to/skill-dir ./dist
```

---

## Cross-Skill Integration

| Skill | Direction | Relationship | Key Integration Point |
|-------|-----------|-------------|----------------------|
| All sf-* skills | DOWNSTREAM | PRIMARY | skill-forge defines structure and quality standards that all skills must follow |
| sf-deploy | LATERAL | SECONDARY | Validates skill output artifacts before deployment |
| sf-testing | LATERAL | SECONDARY | Test patterns apply to skill validation scripts |
| skill-builder | UPSTREAM | SECONDARY | Legacy skill creation wizard; skill-forge supersedes it |

---

## Reference Files

- `references/workflows.md` — Sequential and conditional workflow patterns
- `references/output-patterns.md` — Template and example patterns for consistent output
- `references/salesforce-skill-patterns.md` — Complete SF skill design guide with examples
- `references/token-efficiency.md` — What-goes-where table, token budgets, inline template anti-pattern
- `references/anti-patterns.md` — 6 common skill anti-patterns with symptoms, tests, and fixes
- `references/enrichment-workflow.md` — 7-step process for improving an existing skill
- `references/bulk-audit-workflow.md` — 5-phase library audit process
- `references/cross-skill-reference-standard.md` — Direction values, relationship types, invocation syntax, bidirectional verification
