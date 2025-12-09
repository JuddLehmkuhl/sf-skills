---
name: sf-deploy
description: Comprehensive Salesforce DevOps automation using sf CLI v2. Handles deployments, CI/CD pipelines, scratch orgs, and metadata management with built-in validation and error handling.
---

# sf-deploy: Comprehensive Salesforce DevOps Automation

Expert Salesforce DevOps engineer specializing in deployment automation, CI/CD pipelines, and metadata management using Salesforce CLI (sf v2).

## Core Responsibilities

1. **Deployment Management**: Execute, validate, and monitor deployments (metadata, Apex, LWC)
2. **DevOps Automation**: CI/CD pipelines, automated testing, deployment workflows
3. **Org Management**: Authentication, scratch orgs, environment management
4. **Quality Assurance**: Tests, code coverage, pre-production validation
5. **Troubleshooting**: Debug failures, analyze logs, provide solutions

---

## ⚠️ CRITICAL: Orchestration Workflow Order

When using sf-deployment with other skills, **follow this execution order**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CORRECT MULTI-SKILL ORCHESTRATION ORDER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. sf-metadata    → Create object/field definitions (LOCAL files)          │
│  2. sf-flow-builder → Create flow definitions (LOCAL files)                 │
│  3. sf-deployment  → Deploy all metadata to org (REMOTE) ← YOU ARE HERE    │
│  4. sf-data        → Create test data (REMOTE - objects must exist!)        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**⚠️ DEPLOYMENT ORDER WITHIN sf-deployment:**

```
1. Custom Objects & Fields FIRST
2. Permission Sets (for FLS access)
3. Flows (may reference custom fields)
4. Apex Classes/Triggers
5. Activate Flows (change status to Active)
```

**Why order matters:**
- Flows referencing non-existent fields will fail
- Users can't see fields without Permission Sets
- Triggers may depend on flows being active

---

## 🔑 Key Insights for Deployment

### Always Use --dry-run First

```bash
# CORRECT: Validate before deploying
sf project deploy start --dry-run --source-dir force-app --target-org alias
sf project deploy start --source-dir force-app --target-org alias

# WRONG: Deploying without validation
sf project deploy start --source-dir force-app --target-org alias  # Risky!
```

### Deploy Permission Sets After Objects

**Common Error:**
```
Error: In field: field - no CustomObject named ObjectName__c found
```

**Solution:** Deploy objects first, THEN permission sets referencing them.

### Flow Activation Workflow (CRITICAL)

**Flows deploy as Draft by default for safety. Follow this 4-step activation process:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  FLOW ACTIVATION WORKFLOW                                           │
├─────────────────────────────────────────────────────────────────────┤
│  Step 1: Deploy with <status>Draft</status>                         │
│          sf project deploy start --source-dir flows --target-org X  │
│                                                                      │
│  Step 2: Verify deployment succeeded                                 │
│          sf project deploy report --job-id [id]                      │
│                                                                      │
│  Step 3: Edit XML: Change <status>Draft</status>                    │
│                    to      <status>Active</status>                   │
│                                                                      │
│  Step 4: Redeploy the flow                                          │
│          sf project deploy start --source-dir flows --target-org X  │
└─────────────────────────────────────────────────────────────────────┘
```

**Why two deployments?**
- Draft allows you to verify the flow deployed correctly
- If activation fails (e.g., missing permissions), the flow still exists
- You can test the flow manually before activating
- Production best practice: deploy Draft, test, then activate

**Common Activation Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "Flow is invalid" | Referenced field/object missing | Deploy objects BEFORE flows |
| "Insufficient permissions" | User can't activate | Check "Manage Flow" permission |
| "Version conflict" | Active version exists | Deactivate old version first |

### FLS Warning After Deployment

**⚠️ Deployed fields may be INVISIBLE without FLS!**

After deploying custom objects/fields:
1. Deploy Permission Set granting field access
2. Assign Permission Set to user: `sf org assign permset --name PermSetName --target-org alias`
3. Verify field visibility

---

## CLI Version (CRITICAL)

**This skill uses `sf` CLI (v2.x), NOT legacy `sfdx` (v1.x)**

| Legacy sfdx (v1) | Modern sf (v2) |
|-----------------|----------------|
| `--checkonly` / `--check-only` | `--dry-run` |
| `sfdx force:source:deploy` | `sf project deploy start` |

## Prerequisites

Before deployment, verify:
```bash
sf --version              # Requires v2.x
sf org list               # Check authenticated orgs
test -f sfdx-project.json # Valid SFDX project
```

## Deployment Workflow (5-Phase)

### Phase 1: Pre-Deployment Analysis

**Gather via AskUserQuestion**: Target org, deployment scope, validation requirements, rollback strategy.

**Analyze**:
- Read `sfdx-project.json` for package directories
- Glob for metadata: `**/force-app/**/*.{cls,trigger,xml,js,html,css}`
- Grep for dependencies

**TodoWrite tasks**: Validate auth, Pre-tests, Deploy, Monitor, Post-tests, Verify

### Phase 2: Pre-Deployment Validation

```bash
sf org display --target-org <alias>                    # Check connection
sf apex test run --test-level RunLocalTests --target-org <alias> --wait 10  # Local tests
sf project deploy start --dry-run --test-level RunLocalTests --target-org <alias> --wait 30  # Validate
```

### Phase 3: Deployment Execution

**Commands by scope**:
```bash
# Full metadata
sf project deploy start --target-org <alias> --wait 30

# Specific components
sf project deploy start --source-dir force-app/main/default/classes --target-org <alias>

# Manifest-based
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunLocalTests --wait 30

# Quick deploy (after validation)
sf project deploy quick --job-id <validation-job-id> --target-org <alias>
```

Handle failures: Parse errors, identify failed components, suggest fixes.

### Phase 4: Post-Deployment Verification

```bash
sf project deploy report --job-id <job-id> --target-org <alias>
```

Verify components, run smoke tests, check coverage.

### Phase 5: Documentation

Provide summary with: deployed components, test results, coverage metrics, next steps.

See [examples/deployment-report-template.md](examples/deployment-report-template.md) for output format.

## Deployment Pattern

Standard workflow for all scenarios:

1. **Verify** org auth: `sf org display`
2. **Identify** scope: [full | components | hotfix | scratch]
3. **Validate**: `sf project deploy start --dry-run`
4. **Execute**: `sf project deploy start [options]`
5. **Verify**: `sf project deploy report`

**Variants**:
- **Production**: Full scope + backup + RunAllTests + documentation
- **Hotfix**: Targeted components + RunLocalTests + fast deploy
- **CI/CD**: Scripted + automated gates + notifications
- **Scratch**: `sf project deploy start` (push source)

## CLI Reference

**Deploy**: `sf project deploy start [--dry-run] [--source-dir <path>] [--manifest <xml>] [--test-level <level>]`
**Quick**: `sf project deploy quick --job-id <id>` | **Status**: `sf project deploy report`
**Test**: `sf apex test run --test-level RunLocalTests` | **Coverage**: `sf apex get test --code-coverage`
**Org**: `sf org list` | `sf org display` | `sf org create scratch` | `sf org open`
**Metadata**: `sf project retrieve start` | `sf org list metadata --metadata-type <type>`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| FIELD_CUSTOM_VALIDATION_EXCEPTION | Validation rule blocking | Deactivate rules or use valid test data |
| INVALID_CROSS_REFERENCE_KEY | Missing dependency | Include dependencies in deploy |
| CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY | Trigger/validation error | Review trigger logic, check recursion |
| TEST_FAILURE | Test class failure | Fix test or code under test |
| INSUFFICIENT_ACCESS | Permission issue | Verify user permissions, FLS |

### Flow-Specific Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Element X is duplicated" | Elements not alphabetically ordered | Reorder Flow XML elements |
| "Element bulkSupport invalid" | Deprecated element (API 60.0+) | Remove `<bulkSupport>` |
| "Error parsing file" | Malformed XML | Validate XML syntax |

### Failure Response

1. Parse error output, identify failed components
2. Explain error in plain language
3. Suggest specific fixes with code examples
4. Provide rollback options if needed

## Best Practices

- **Always validate first**: Use `--dry-run` for production
- **Appropriate test levels**: RunLocalTests (deploy), RunAllTests (packages)
- **Code coverage**: >75% for production, >90% recommended
- **Use manifests**: `package.xml` for controlled deployments
- **Version control**: Commit before deploying, tag releases
- **Incremental deploys**: Small, frequent changes over large batches
- **Sandbox first**: Always test before production
- **Backup metadata**: Retrieve before major deployments
- **Quick deploy**: Use for validated changesets

## CI/CD Integration

Standard pipeline workflow:
1. Authenticate (JWT/auth URL)
2. Validate metadata
3. Static analysis (PMD, ESLint)
4. Dry-run deployment
5. Run tests + coverage check
6. Deploy if validation passes
7. Notify

See [examples/deployment-workflows.md](examples/deployment-workflows.md) for scripts.

## Edge Cases

- **Large deployments**: Split into batches (limit: 10,000 files / 39 MB)
- **Test timeout**: Increase wait time or run tests separately
- **Namespace conflicts**: Handle managed package issues
- **API version**: Ensure source/target compatibility

## Cross-Skill Dependency Checklist

**Before deploying, verify these prerequisites from other skills:**

| Dependency | Check Command | Required For |
|------------|---------------|--------------|
| **TAF Package** | `sf package installed list --target-org alias` | TAF trigger pattern (sf-apex) |
| **Custom Objects/Fields** | `sf sobject describe --sobject ObjectName --target-org alias` | Apex/Flow field references |
| **Trigger_Action__mdt** | Check Setup → Custom Metadata Types | TAF trigger execution |
| **Queues** | `sf data query --query "SELECT Id,Name FROM Group WHERE Type='Queue'"` | Flow queue assignments |
| **Permission Sets** | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |

**Common Cross-Skill Issues:**

| Error Message | Missing Dependency | Solution |
|--------------|-------------------|----------|
| `Invalid type: MetadataTriggerHandler` | TAF Package | Install apex-trigger-actions package |
| `Field does not exist: Field__c` | Custom Field or FLS | Deploy field or create Permission Set |
| `No such column 'Field__c'` | Field-Level Security | Assign Permission Set to running user |
| `SObject type 'Object__c' not supported` | Custom Object | Deploy object via sf-metadata first |
| `Queue 'QueueName' not found` | Queue Metadata | Deploy queue via sf-metadata first |

---

## Deployment Script Template

**Reusable bash script for multi-step deployments:**

```bash
#!/bin/bash
#
# Multi-Step Deployment Script
# Generated by sf-deployment skill
#
# Usage: ./scripts/deploy.sh <target-org-alias>

set -e  # Exit on error

TARGET_ORG=${1:-"myorg"}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}/..")" && pwd)"

echo "═══════════════════════════════════════════════════════════════════"
echo "  DEPLOYMENT TO: $TARGET_ORG"
echo "═══════════════════════════════════════════════════════════════════"

# Step 0: Pre-flight checks
echo "📋 Pre-flight checks..."
sf --version || { echo "❌ sf CLI not found"; exit 1; }
sf org display --target-org "$TARGET_ORG" || { echo "❌ Cannot connect to org"; exit 1; }

# Step 1: Deploy Custom Objects/Fields
echo "📦 Step 1: Deploying objects and fields..."
sf project deploy start \
    --source-dir "$PROJECT_DIR/force-app/main/default/objects" \
    --target-org "$TARGET_ORG" \
    --wait 10

# Step 2: Deploy Permission Sets
echo "📦 Step 2: Deploying permission sets..."
sf project deploy start \
    --source-dir "$PROJECT_DIR/force-app/main/default/permissionsets" \
    --target-org "$TARGET_ORG" \
    --wait 10

# Step 3: Deploy Apex (with tests)
echo "📦 Step 3: Deploying Apex..."
sf project deploy start \
    --source-dir "$PROJECT_DIR/force-app/main/default/classes" \
    --source-dir "$PROJECT_DIR/force-app/main/default/triggers" \
    --target-org "$TARGET_ORG" \
    --test-level RunLocalTests \
    --wait 30

# Step 4: Deploy Flows (Draft)
echo "📦 Step 4: Deploying flows..."
sf project deploy start \
    --source-dir "$PROJECT_DIR/force-app/main/default/flows" \
    --target-org "$TARGET_ORG" \
    --wait 10

echo "═══════════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "  1. Assign permission sets: sf org assign permset --name PermSetName --target-org $TARGET_ORG"
echo "  2. Activate flows: Edit XML status to Active, redeploy"
echo "  3. Run test data: sf apex run --file scripts/data/create-test-data.apex --target-org $TARGET_ORG"
```

---

## Generate Package Manifest

**Auto-generate package.xml from source directory:**

```bash
# Generate from source
sf project generate manifest --source-dir force-app --name manifest/package.xml

# Generate for specific metadata types
sf project generate manifest \
    --metadata CustomObject:Account \
    --metadata ApexClass \
    --metadata Flow \
    --name manifest/package.xml

# Deploy using manifest
sf project deploy start --manifest manifest/package.xml --target-org alias
```

**When to use manifest vs source-dir:**

| Scenario | Use | Command |
|----------|-----|---------|
| Deploy everything | `--source-dir` | `sf project deploy start --source-dir force-app` |
| Deploy specific components | `--manifest` | `sf project deploy start --manifest package.xml` |
| CI/CD pipelines | `--manifest` | Controlled, reproducible deployments |
| Development iteration | `--source-dir` | Quick local changes |

---

## Notes

- **CLI**: Uses only `sf` (v2) with modern flag syntax
- **Auth**: Supports OAuth, JWT, Auth URL, web login
- **API**: Uses Metadata API (not Tooling API)
- **Async**: Use `--wait` to monitor; most deploys are async
- **Limits**: Be aware of Salesforce governor limits

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
