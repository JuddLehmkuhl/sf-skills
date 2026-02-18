# Technical Record Template (Developer-Facing)

## Writing Rules

- Technical terminology is appropriate
- Be precise and complete
- Include all components, paths, dependencies
- Document architecture decisions and rationale
- Include deployment and rollback procedures
- Assume reader knows Salesforce but not this project

## Cross-Referencing Upstream Skills

When generating the Technical Record, pull data from upstream skill artifacts:

**From sf-apex / salesforce-trigger-framework:**
- List every Apex class, trigger, and trigger action created
- Include the `TA_*` execution order from Custom Metadata
- Document the architecture pattern: `Trigger -> MetadataTriggerHandler -> TA_* -> Services -> DAL`
- Reference test classes and their coverage percentages

**From sf-flow:**
- List every Flow with its type (Record-Triggered, Screen, Autolaunched, Scheduled)
- Include entry conditions and trigger context (Before Save vs After Save)
- Note any Apex Actions invoked from Flows

**From sf-metadata:**
- List all Custom Objects, Custom Fields, Custom Metadata Types created
- Document field-level security requirements
- Include Permission Set assignments

**From sf-deploy:**
- Include the exact deployment order used
- Document any deployment flags or special considerations
- Provide the rollback procedure

**From sf-diagram (optional):**
- Embed Mermaid diagrams for architecture visualization
- Include ERD diagrams for data model documentation

## Template

```markdown
# Technical Record: [Feature Name]

**Generated:** [Timestamp]
**Commit/Branch:** [If known]
**Upstream skills used:** [sf-apex, sf-flow, sf-metadata, etc.]

---

## Summary

[2-3 sentences: What was built, what pattern was used, what it enables]

---

## Components

### Created

| Component | Type | Purpose |
|-----------|------|---------|
| [Name] | [Apex/Trigger/Flow/Metadata] | [What it does] |

### File Paths

```
force-app/main/default/
├── classes/
│   └── [files]
├── triggers/
│   └── [files]
└── customMetadata/
    └── [files]
```

---

## Architecture

**Pattern:** [Name]

**Flow:**
```
[Diagram or description]
```

**Design Decisions:**
- [Decision]: [Rationale]

---

## Behavior

### What It Does

[Detailed description of logic]

### Contexts/Events

| Context | Behavior |
|---------|----------|
| [Context] | [What happens] |

### Edge Cases

- [Case]: [Handling]

---

## Dependencies

### Packages

| Package | ID/Version | Required For |
|---------|------------|--------------|
| [Name] | [ID] | [Purpose] |

### Objects/Fields

| Object | Fields | Access |
|--------|--------|--------|
| [Object] | [Fields] | [Read/Write] |

### Permissions

| Permission | Reason |
|------------|--------|
| [Permission] | [Why needed] |

---

## Testing

| Test Class | Coverage |
|------------|----------|
| [Class] | [%] |

### Scenarios

| Scenario | Validates |
|----------|-----------|
| [Scenario] | [What it proves] |

---

## Deployment

### Order

1. [Step]
2. [Step]

### Verification

```bash
[commands]
```

### Rollback

1. [Step]
2. [Step]

---

## Extension

### Adding New [Behavior]

1. [Step]
2. [Step]

### Configuration

| Setting | Location | Effect |
|---------|----------|--------|
| [Setting] | [Where] | [What it does] |

---

## Limitations

- [Limitation]
```
