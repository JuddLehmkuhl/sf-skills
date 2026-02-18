---
name: sf-docs
description: >
  Generates multi-audience documentation from Salesforce code and metadata.
  Creates three outputs: Feature Summary (business-facing, zero jargon),
  Technical Record (developer-facing), and Change Entry (release notes).
  Use this skill after completing significant features, trigger implementations,
  or any changes that require stakeholder communication.
license: MIT
metadata:
  version: "2.1.0"
  author: "Judd Lehmkuhl"
  outputs: "Feature Summary, Technical Record, Change Entry"
---

# sf-docs - Salesforce Documentation Generation

Generates documentation automatically from code, metadata, and context during development.

## Quick Reference

| Item | Details |
|------|---------|
| **Commands** | `/docs`, `/docs summary`, `/docs tech`, `/docs entry` |
| **Outputs** | Feature Summary, Technical Record, Change Entry |
| **Runs after** | `sf-apex`, `sf-flow`, `sf-metadata`, `salesforce-trigger-framework`, `sf-deploy` |
| **Orchestration position** | Step 6 -- documentation pass after implementation and deployment |
| **Input sources** | Apex classes, Flow XML, Custom Metadata, trigger actions, deploy logs |
| **Output locations** | `/docs/features/`, `/docs/technical/`, `/docs/changelog/` |
| **Related skills** | `sf-diagram` (architecture visuals), `sf-testing` (coverage data), `sf-deploy` (deploy manifests) |

---

## Orchestration Position

**sf-docs runs AFTER implementation is complete.**

```
0. sf-solution-design  -> Discover features, answer 8-question checklist
1. sf-metadata         -> Create objects/fields
2. sf-apex             -> Create Apex classes, trigger actions
3. sf-flow             -> Create Flows referencing Apex/metadata
4. sf-deploy           -> Deploy all metadata to org
5. sf-testing          -> Validate tests pass, coverage meets threshold
6. sf-docs             -> YOU ARE HERE: Generate documentation from what was built
```

### When to Invoke sf-docs

| Trigger | Action |
|---------|--------|
| Feature completed and deployed | `/docs` -- generate all three outputs |
| Sprint review approaching | `/docs summary` -- business-facing summary for stakeholders |
| Pull request ready | `/docs tech` -- technical record for reviewers |
| Release cut | `/docs entry` -- change entry for release notes |
| Post-hotfix | `/docs entry` + `/docs tech` -- document the fix and its technical footprint |

### What sf-docs Reads from Other Skills

| Upstream Skill | What sf-docs Reads | Used In |
|----------------|-------------------|---------|
| **sf-apex** | Apex classes, trigger actions, ApexDoc comments, test classes | Technical Record |
| **sf-flow** | Flow XML metadata, flow descriptions, entry conditions | Technical Record, Feature Summary |
| **sf-metadata** | Custom Objects, Custom Fields, Custom Metadata, Permission Sets | Technical Record, Feature Summary |
| **salesforce-trigger-framework** | TA_* classes, Custom Metadata trigger configs, execution order | Technical Record |
| **sf-deploy** | Deploy logs, manifest files, deployment order | Technical Record |
| **sf-testing** | Test results JSON, coverage percentages, test scenarios | Technical Record |
| **sf-diagram** | Mermaid diagrams (ERD, sequence, architecture) | Technical Record |

---

## Decision Framework: Which Output to Generate

```
Is this a user-facing change?
  YES -> Generate Feature Summary
  NO  -> Skip Feature Summary

Does this touch code, metadata, or architecture?
  YES -> Generate Technical Record
  NO  -> Skip Technical Record (config-only changes may not need one)

Is this shipping in a release?
  YES -> Generate Change Entry
  NO  -> Skip Change Entry (internal refactors, tech debt)
```

### Common Scenarios

| Scenario | Feature Summary | Technical Record | Change Entry |
|----------|:-:|:-:|:-:|
| New feature (trigger + flow + metadata) | Yes | Yes | Yes |
| Bug fix affecting users | Yes | Yes | Yes |
| Internal refactor (no user impact) | No | Yes | No |
| New trigger action on existing object | Maybe | Yes | Yes |
| Permission set change | Yes | No | Yes |
| Data migration / data fix | No | Yes | No |
| New integration endpoint | Yes | Yes | Yes |
| Performance optimization | No | Yes | Maybe |

---

## Commands

```
/docs              # Generate all three outputs
/docs summary      # Feature Summary only (business-facing)
/docs tech         # Technical Record only (developer-facing)
/docs entry        # Change Entry only (release notes)
/docs review       # Review existing docs against quality checklist
```

### CLI Integration

```bash
# Create docs directories if they don't exist
mkdir -p docs/features docs/technical docs/changelog

# Stage documentation for commit
git add docs/

# Commit with conventional message
git commit -m "docs: add documentation for [feature-name]"
```

---

## Output 1: Feature Summary (Business-Facing)

> Full template, example, and tech-vs-business comparison: `references/feature-summary-template.md`

### Writing Rules

- Write for someone who has never seen Salesforce Setup
- No code references, API names, or developer jargon
- Active voice, short sentences (under 20 words)
- Lead with what changed for users, not how it was built
- Keep it under one page; use tables for before/after comparisons

### Banned Phrases

| Don't Use | Use Instead |
|-------------|----------------|
| "Implemented" | "Added" or "Now [verb]" |
| "Trigger" / "Apex" / "Flow" | "Automatic process" or "The system" |
| "Custom Metadata" | "Configuration" or "Settings" |
| "Framework" | "Foundation" or omit entirely |
| "Architecture" | Omit - not relevant to business |
| "Metadata-driven" | "Configurable" or "Adjustable without IT" |
| "Deployed" | "Released" or "Now available" |
| "Object" (Salesforce) | Use the business name: "Leads," "Accounts," "Policies" |
| "Record" | Use specific: "lead," "account," "policy" |
| "Field" | Use specific: "Lead Source," "Status" |
| "SOQL" / "Query" | "Lookup" or "Search" |
| "Governor limits" | Omit - internal concern |
| "Bulkified" | Omit - internal concern |
| "Test coverage" | Omit - internal concern |
| "Package" | "Add-on" or omit |
| "API" | Omit unless user-facing |

### Feature Summary Sections

The template uses these sections in order: **What's New** (2-3 sentences), **Why This Matters** (one paragraph), **What Changed** (before/after table), **Who This Affects** (role table), **What Happens Automatically** (bullet list), **What's NOT Included** (limitations).

---

## Output 2: Technical Record (Developer-Facing)

> Full template with all sections and upstream skill cross-referencing guide: `references/technical-record-template.md`

### Writing Rules

- Technical terminology is appropriate
- Include all components, paths, dependencies
- Document architecture decisions and rationale
- Include deployment and rollback procedures
- Assume reader knows Salesforce but not this project

### Technical Record Sections

The template covers: **Summary**, **Components** (created + file paths), **Architecture** (pattern + design decisions), **Behavior** (logic + contexts + edge cases), **Dependencies** (packages + objects + permissions), **Testing** (classes + scenarios), **Deployment** (order + verification + rollback), **Extension** (how to add behavior + configuration), **Limitations**.

---

## Output 3: Change Entry (Release Notes)

> Full template, example, and changelog file conventions: `references/change-entry-template.md`

### Writing Rules

- One bolded sentence summarizing the change
- 3-5 bullet points of specific changes
- Keep entire entry under 75 words
- Lead with user impact, not technical details
- Append to monthly file at `/docs/changelog/[YYYY-MM].md`

---

## Translating Technical to Business Language

> Full translation tables (actions, components, patterns, TAF-specific): `references/technical-to-business-translations.md`

Key principle: replace all Salesforce-specific terms with plain language. Apex/Trigger/Flow become "automatic process." Custom Metadata becomes "configuration." Omit internal concerns (bulkification, test coverage, governor limits).

---

## Inferring Business Impact from Code

> Full code-to-impact mapping and object-to-user tables: `references/business-impact-mappings.md`

Connect what the code does to what users experience. Default field values mean "users don't have to fill in every field manually." Auto-created related records mean "setup steps that were manual now happen automatically."

---

## Quality Checklist

### Feature Summary (Business)

- [ ] Could a non-technical manager understand every sentence?
- [ ] Are there ZERO technical terms (trigger, apex, flow, metadata, object, field)?
- [ ] Does it explain what changed for users, not what developers built?
- [ ] Is "Why This Matters" written in terms of user problems solved?
- [ ] Is "Who This Affects" using job titles, not system roles?
- [ ] Is it under one page?
- [ ] Could someone skim just the headers and tables and understand it?

### Technical Record (Developer)

- [ ] All components listed with correct file paths?
- [ ] Architecture and patterns documented?
- [ ] Dependencies explicit and complete?
- [ ] Deployment order accurate?
- [ ] Rollback procedure would actually work?
- [ ] Extension points documented?
- [ ] Cross-references to upstream skills included?
- [ ] sf-diagram visuals embedded where helpful?

### Change Entry (Release Notes)

- [ ] Under 75 words total?
- [ ] Lead sentence describes user impact (not technical implementation)?
- [ ] Bullet points are user-facing changes?
- [ ] Appended to correct monthly changelog file?

---

## Output Location

| Output | Location |
|--------|----------|
| Feature Summary | `/docs/features/[feature-name].md` |
| Technical Record | `/docs/technical/[feature-name].md` |
| Change Entry | Appended to `/docs/changelog/[YYYY-MM].md` |

---

## Integration with sf-deploy

```bash
# After deployment, generate docs from the deploy manifest
sf project deploy start --source-dir force-app --target-org sandbox \
  --json > deploy-result.json

# Then invoke sf-docs to read the deploy result
/docs tech
```

### Post-Deployment Documentation Workflow

```
1. sf-deploy completes successfully
2. sf-testing confirms all tests pass
3. Run `/docs` to generate all documentation
4. Review generated docs against Quality Checklist
5. Stage and commit: git add docs/ && git commit -m "docs: [feature-name]"
6. Include doc links in PR description or sprint review
```

---

## Integration with sf-diagram

For Technical Records with complex architectures, invoke sf-diagram for visuals:

```
/diagram erd Account Contact Opportunity
/diagram sequence "External System -> Named Credential -> Apex -> Platform Event"
```

Embed the resulting Mermaid code directly in the Technical Record's Architecture section.

---

## Versioning and Document Lifecycle

### When to Update Existing Documentation

| Change Type | Feature Summary | Technical Record | Change Entry |
|-------------|:-:|:-:|:-:|
| Bug fix to documented feature | Update | Update | New entry |
| Enhancement to documented feature | Update | Update | New entry |
| Breaking change | New version | Update + migration notes | New entry |
| Deprecation | Update with sunset date | Update with removal plan | New entry |
| Configuration change only | No change | Update | Optional |

### Document Naming Convention

Use kebab-case for file names. Match names between `features/` and `technical/` directories for easy cross-reference.

```
docs/
├── features/
│   ├── automatic-lead-completion.md
│   └── opportunity-stage-validation.md
├── technical/
│   ├── automatic-lead-completion.md
│   └── opportunity-stage-validation.md
└── changelog/
    ├── 2024-12.md
    └── 2025-01.md
```

---

## Sources

- [Complete Guide to Salesforce Documentation - Salesforce Ben](https://www.salesforceben.com/complete-guide-to-salesforce-documentation/)
- [Functional and Technical Documentation for Salesforce Projects - Salesforce Ben](https://www.salesforceben.com/functional-and-technical-documentation-for-salesforce-projects-whats-the-difference/)
- [Salesforce Best Practices: System Documentation - Cloud Giants](https://www.cloudgiants.com/blog-detailed/salesforce-best-practices-system-documentation)
- [Salesforce DevOps Documentation Best Practices - DevOps Launchpad](https://devopslaunchpad.com/blog/salesforce-devops-documentation-best-practices/)
- [Effective Documentation Strategies for Large Salesforce DevOps Teams - Gearset](https://gearset.com/blog/documentation-for-large-teams/)
- [Salesforce Release Management Best Practices - Minuscule Technologies](https://www.minusculetechnologies.com/blogs/salesforce-release-management-best-practices)
- [Documentation Ideas and Best Practices - Trailhead Community](https://trailhead.salesforce.com/trailblazer-community/feed/0D54S00000BtiCUSAZ)
