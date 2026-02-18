---
name: skill-forge
description: >
  Create, validate, package, and manage Claude Code skills. Use when users want
  to create a new skill, update an existing skill, validate skill structure,
  bulk-validate all installed skills, or package a skill for distribution. Also
  use for Salesforce-specific skill patterns (orchestration chains, 5-phase
  workflows, template directories, gotcha tables). Combines Anthropic's official
  skill-creator design philosophy with production tooling.
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
| **Workflow** | Sequential processes | Phase 1 → Phase 2 → Phase 3 |
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
- Code that gets rewritten → `scripts/`
- Documentation Claude needs → `references/`
- Files used in output → `assets/`

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

## Salesforce Skill Patterns

When building skills for Salesforce development, apply these proven patterns.
See `references/salesforce-skill-patterns.md` for complete documentation.

### Orchestration Chain

Every SF skill must declare where it sits in the dependency pipeline:

```markdown
## CRITICAL: Orchestration Order
**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-flow)
```

### 5-Phase Workflow

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Requirements | `AskUserQuestion` to gather inputs; `Glob` existing files |
| 2 | Design | Template selection table mapping type → file |
| 3 | Generation | Create artifacts in `force-app/`; validate |
| 4 | Deployment | `--dry-run` first, then deploy; invoke `sf-deploy` |
| 5 | Verification | Completion summary; CLI verification commands |

### Required Sections for SF Skills

- **Orchestration Order** — where this skill fits
- **Key Insights / Gotchas Table** — `| Gotcha | Details |` format
- **Cross-Skill Integration Table** — who calls this skill, who it calls
- **CLI Quick Reference** — `sf` v2 commands in fenced bash blocks
- **Common Errors Table** — `| Error | Fix |` pairs
- **FLS Warning** (if creating fields/objects) — "Fields invisible without Permission Set"
- **templates/ directory** (if generating metadata XML)

---

## Gotcha Tables: Design Pattern

Gotcha tables are the highest-value section of any Salesforce skill. They encode
production lessons that prevent repeated failures:

```markdown
## Gotchas

| Gotcha | Details |
|--------|---------|
| Short label | Concise explanation with the fix inline |
| Another gotcha | What goes wrong and exactly how to fix it |
```

Rules:
- Keep labels under 5 words
- Include the fix IN the details column, not separately
- Order by frequency (most common first)
- Add new gotchas as they're discovered in production

---

## Reference Files

- `references/workflows.md` — Sequential and conditional workflow patterns
- `references/output-patterns.md` — Template and example patterns for consistent output
- `references/salesforce-skill-patterns.md` — Complete SF skill design guide with examples
