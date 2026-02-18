# Enrichment Workflow

Step-by-step process for improving an existing skill. Follow these steps in
order. Do NOT skip the scoring step.

## Step 1: Read Current State

```
Read: <path>/SKILL.md
Read: <path>/references/*  (if they exist)
Glob: <path>/**/*          (full inventory)
```

Understand what exists before changing anything.

## Step 2: Score Against Quality Framework

Rate each dimension (Structure, Content Density, Completeness, Integration)
using the rubrics in SKILL.md. Record the score:

```
Structure:       __/25
Content Density: __/25
Completeness:    __/25
Integration:     __/25
TOTAL:           __/100
```

Identify the lowest-scoring dimension. That is the priority for enrichment.

## Step 3: Identify Gaps

Check for these specific gaps:

| Gap | How to Check |
|-----|-------------|
| Cross-skill references | Search for other skill names in SKILL.md |
| Gotcha table | Search for "Gotcha" heading |
| Anti-pattern section | Search for "Anti-Pattern" or "Do NOT" |
| CLI commands | Search for `sf ` commands; verify v2 syntax |
| Common errors table | Search for "Error" table |
| Orchestration order | Search for "Orchestration" heading |
| Token efficiency | Count lines of inline code blocks |
| Completion summary location | If inline in SKILL.md, flag for move to references/ |

## Step 4: Research

For Salesforce skills, gather current information:

- **Salesforce release notes**: Check latest API version limits and changes
- **Known Issues**: Search Salesforce Known Issues site for the domain
- **Stack Exchange**: Search for common failures in the skill's domain
- **sf CLI help**: Run `sf <command> --help` to verify flag names

For non-SF skills, verify any external tool versions and API changes.

## Step 5: Write Enriched Content

Rules for enrichment writing:

1. **PRESERVE all existing content** — never delete working sections
2. **ADD new sections** after existing content in logical order
3. **INSERT cross-references** into existing sections where relevant
4. **UPDATE CLI commands** if outdated (this is the one exception to "preserve")
5. **MOVE bloated sections** to references/ if they exceed token guidelines

## Step 6: Validate

```bash
python3 ~/.claude/skills/sf-skills/skill-forge/scripts/validate_skill.py <path/to/skill>
```

Fix any validation errors before considering enrichment complete.

## Step 7: Verify Line Count and Re-Score

After enrichment:
- Count lines: target depends on skill complexity (300-500 for focused skills)
- Re-score against the quality framework
- Verify score improved by at least 15 points
- Confirm no dimension dropped below its pre-enrichment score
