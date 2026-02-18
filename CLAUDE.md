# Salesforce Development Skills

This configuration provides Claude Code with comprehensive Salesforce development expertise.

## Skill Loading

Load skills based on the task at hand. Skills are organized by domain:

### Solution Design (Load First for ANY New Work)
- `sf-solution-design` - **MANDATORY before designing solutions** - Feature discovery, PSL-to-capability mapping, 8-question checklist to leverage platform features before building custom

### Foundation Skills
- `sf-metadata` - Custom objects, fields, permission sets, validation rules
- `sf-data` - SOQL, data operations, test data factories
- `sf-soql` - SOQL query generation, optimization, and validation

### Development Skills
- `sf-apex` - Apex classes, triggers, batch jobs, test classes
- `sf-flow` - Screen flows, record-triggered flows, scheduled flows
- `sf-lwc` - Lightning Web Components with SLDS 2 validation
- `salesforce-trigger-framework` - Mitch Spano's Trigger Actions Framework (PS Advisory conventions)

### Integration Skills
- `sf-connected-apps` - Connected Apps, OAuth configuration, External Client Apps
- `sf-integration` - Named Credentials, External Services, REST/SOAP callouts, Platform Events

### AI & Automation
- `sf-ai-agentforce` - Agentforce agents, Agent Script, Topics, Actions (API v65+)

### Quality & Debugging
- `sf-testing` - Apex test execution, coverage analysis, and test-fix loops
- `sf-debug` - Log analysis, governor limits, and agentic fix suggestions

### DevOps & Documentation
- `sf-deploy` - Deployment automation using sf CLI v2
- `sf-diagram` - Mermaid diagrams for ERD, OAuth flows, architecture
- `sf-docs` - Multi-audience documentation (business summaries, technical records, release notes)

### Utilities
- `skill-builder` - Interactive wizard for creating new Claude Code skills

## Orchestration Order

When creating Salesforce solutions, follow this dependency order:

```
0. sf-solution-design → RUN FIRST: Discover available features, answer 8-question checklist
1. sf-metadata        → Create objects/fields (only if needed after checklist)
2. sf-apex            → Create Apex classes (only if needed after checklist)
3. sf-flow            → Create Flows that reference Apex/metadata
4. sf-deploy          → Deploy all metadata to org
5. sf-ai-agentforce   → Publish agents (requires deployed dependencies)
```

> ⚠️ **Step 0 is mandatory.** Many solutions can be achieved with configuration instead of code. The Solution Design Framework ensures you leverage what's already available.

## PS Advisory Conventions

### Trigger Framework
All triggers must use the Trigger Actions Framework with these conventions:
- Trigger naming: `<ObjectName>Trigger`
- Action naming: `TA_<ObjectName>_<ActionDescription>`
- Test naming: `TA_<ObjectName>_<ActionDescription>_Test`
- Order spacing: increments of 10 (10, 20, 30...)
- Architecture: `Trigger → MetadataTriggerHandler → TA_* → Services → DAL`

See `salesforce-trigger-framework/SKILL.md` for complete documentation.

### Code Standards
- 95%+ test coverage on all Apex
- Bulkification required for all triggers and flows
- No SOQL/DML in loops
- Use Custom Metadata for configuration

## Quick Reference

### Common Commands
```bash
# Deploy to sandbox
sf project deploy start --source-dir force-app --target-org sandbox

# Run tests
sf apex run test --class-names MyTest --target-org sandbox --result-format human

# Validate agent
sf agent validate authoring-bundle --api-name MyAgent

# Publish agent
sf agent publish authoring-bundle --api-name MyAgent
```

### File Locations
```
force-app/main/default/
├── classes/           # Apex classes
├── triggers/          # Apex triggers
├── flows/             # Flow definitions
├── objects/           # Custom objects and fields
├── customMetadata/    # Trigger Action configs
├── permissionsets/    # Permission sets
└── aiAuthoringBundles/ # Agentforce agents
```

## Skill-Specific Instructions

When working on a specific domain, read the relevant SKILL.md file first:

- **Solution Design**: Read `sf-solution-design/SKILL.md` - **START HERE for any new feature/solution**
- **Triggers**: Read `salesforce-trigger-framework/SKILL.md`
- **Agentforce**: Read `sf-ai-agentforce/SKILL.md`
- **Apex**: Read `sf-apex/SKILL.md`
- **Flows**: Read `sf-flow/SKILL.md`
- **LWC**: Read `sf-lwc/SKILL.md`
- **Metadata**: Read `sf-metadata/SKILL.md`
- **SOQL**: Read `sf-soql/SKILL.md`
- **Testing**: Read `sf-testing/SKILL.md`
- **Debugging**: Read `sf-debug/SKILL.md`
- **Deployments**: Read `sf-deploy/SKILL.md`
- **Diagrams**: Read `sf-diagram/SKILL.md`
- **Documentation**: Read `sf-docs/SKILL.md`
- **Integrations**: Read `sf-integration/SKILL.md`
- **Connected Apps**: Read `sf-connected-apps/SKILL.md`
