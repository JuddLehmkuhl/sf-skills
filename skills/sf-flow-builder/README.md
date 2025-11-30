# sf-flow-builder

Creates and validates Salesforce flows using best practices and metadata standards (API 62.0).

## Features

✨ **Comprehensive Flow Creation** (7 Flow Types)
- Screen Flows (user-guided forms and wizards)
- Record-Triggered Flows - After-Save (automation after create/update)
- Record-Triggered Flows - Before-Save (modify records before saving)
- Record-Triggered Flows - Before-Delete (validate or prevent deletion)
- Platform Event-Triggered Flows (real-time event processing)
- Autolaunched Flows (reusable logic for Apex/API)
- Scheduled Flows (time-based batch processing)

🧩 **NEW: Reusable Subflow Library** (5 Pre-Built Components)
- **Sub_LogError** - Structured error logging with observability
- **Sub_SendEmailAlert** - Standard notification patterns
- **Sub_ValidateRecord** - Common validation logic
- **Sub_BulkUpdater** - Bulk update patterns with error handling
- **Sub_QueryWithRetry** - Query with built-in fault handling
- Complete documentation and deployment guides
- See: [Subflow Library](docs/subflow-library.md)

🏗️ **NEW: Orchestration Patterns** (3 Architecture Patterns)
- **Parent-Child** - Multiple independent responsibilities
- **Sequential** - Pipeline processing with data propagation
- **Conditional** - Scenario-based routing to specialized handlers
- Automatic complexity detection and pattern suggestions
- Complete examples with full implementations
- See: [Orchestration Guide](docs/orchestration-guide.md)

🔒 **NEW: Enhanced Validation & Scoring** (6-Category System)
- **110-point comprehensive scoring** across 6 categories:
  - Design & Naming (20 pts) - Conventions and documentation
  - Logic & Structure (20 pts) - Decision complexity and Transform usage
  - Architecture & Orchestration (15 pts) - Modularity and reusability
  - Performance & Bulk Safety (20 pts) - Bulkification and governor limits
  - Error Handling & Observability (20 pts) - Fault paths and logging
  - Security & Governance (15 pts) - Running mode and permissions
- **Bulkification checks** - prevents DML in loops (CRITICAL)
- **Transform element recommendations** - 30-50% performance gains
- **Simulation mode** - tests with 200+ records before deployment
- **Advisory mode** - Non-critical checks provide suggestions without blocking
- API 62.0 (Winter '26) compliance
- See: [Enhanced Validator](validators/enhanced_validator.py)

🔐 **NEW: Security & Governance**
- **Security validation** - System mode detection, sensitive field warnings
- **Governance checklist** - 85-item checklist with 200-point scoring system
- **Architecture review template** - Formal review process for complex flows
- **Profile testing guidance** - Standard User, Custom Profiles, Permission Sets
- Minimum governance score: 140/200 for production deployment
- See: [Governance Checklist](docs/governance-checklist.md)

📚 **NEW: Auto-Documentation Generator**
- **Automated documentation** from flow XML parsing
- Extracts 50+ data points (design, performance, security, dependencies)
- Populates comprehensive template automatically
- Testing status tracking and troubleshooting sections
- See: [Documentation Generator](generators/doc_generator.py)

🚀 **Safe Deployment**
- Two-step deployment (validate → deploy)
- Integration with sf-deployment skill
- Activation control (always prompts before activating)
- Comprehensive error handling

📋 **Testing Guidance**
- Type-specific testing checklists
- Bulk testing recommendations (200+ records)
- Security and profile testing (FLS/CRUD validation)
- Debug log analysis
- Production readiness verification

## Quick Start

### Basic Usage

```
"Create a screen flow to collect customer feedback and save it to a custom object"

"Create a record-triggered flow on Opportunity that updates related contacts when stage changes"

"Create an autolaunched flow that takes an account ID and returns the total opportunity value"
```

### Flow Types

**Screen Flow**
```
User: "Create a screen flow for account creation"

The skill will:
1. Ask for flow details (name, description, target org)
2. Generate interactive screens with form fields
3. Validate the flow structure
4. Deploy with two-step process
5. Provide testing checklist
```

**Record-Triggered Flow**
```
User: "Create a record-triggered flow on Account after save"

The skill will:
1. Ask for trigger object and conditions
2. Generate bulkified flow with <bulkSupport>true</bulkSupport>
3. Validate no DML in loops (CRITICAL check)
4. Add fault paths to DML operations
5. Deploy and provide bulk testing guidance
```

**Autolaunched Flow**
```
User: "Create an autolaunched flow with input/output variables"

The skill will:
1. Design input/output variables
2. Create reusable logic
3. Validate naming conventions
4. Deploy with testing recommendations
```

**Scheduled Flow**
```
User: "Create a scheduled flow to run nightly at 2am"

The skill will:
1. Set up schedule configuration
2. Create bulkified batch processing logic
3. Ensure DML is outside loops (best practice)
4. Deploy and provide monitoring guidance
```

## Validation Features

### Comprehensive Checks

**CRITICAL ERRORS** (Block deployment immediately):
- ❌ DML operations inside loops (causes bulk failures)
- ❌ Broken element references
- ❌ Missing required elements
- ❌ Invalid XML structure

**WARNINGS** (Block in strict mode):
- ⚠️  Missing <bulkSupport>true</bulkSupport> on record-triggered flows
- ⚠️  DML operations without fault paths
- ⚠️  Unused variables
- ⚠️  Loops that should use Transform element
- ⚠️  Naming convention violations

**BEST PRACTICES**:
- ✓ API version 62.0 (latest)
- ✓ Descriptive element names
- ✓ Flow description present
- ✓ Transform used for field mapping

### Enhanced Scoring System (6 Categories)

Flows are scored 0-110 across 6 best practice categories:
- **Design & Naming** (20 pts) - Naming conventions, documentation, element naming
- **Logic & Structure** (20 pts) - Decision complexity, Transform usage, DML in loops check
- **Architecture & Orchestration** (15 pts) - Modularity, subflow usage, reusability
- **Performance & Bulk Safety** (20 pts) - Bulkification, SOQL/DML counts, governor limits
- **Error Handling & Observability** (20 pts) - Fault paths, error logging, monitoring
- **Security & Governance** (15 pts) - Running mode, sensitive fields, API version

**Rating Scale:**
- ⭐⭐⭐⭐⭐ Excellent (95-110 pts / 95%+)
- ⭐⭐⭐⭐ Very Good (85-94 pts / 85-94%)
- ⭐⭐⭐ Good (75-84 pts / 75-84%)
- ⭐⭐ Fair (60-74 pts / 60-74%)
- ⭐ Needs Improvement (<60 pts / <60%)

**Example Report:**
```
═══════════════════════════════════════════════════════════════════
   Flow Validation Report: Account_Update_Flow (API 62.0)
═══════════════════════════════════════════════════════════════════

🎯 Best Practices Score: 92/110 ⭐⭐⭐⭐ Very Good

──────────────────────────────────────────────────────────────────
CATEGORY BREAKDOWN:
──────────────────────────────────────────────────────────────────

✅ 📋 Design & Naming: 18/20 (90%)
   ✓ Naming convention: RTF_Account_UpdateIndustry
   ✓ Description present and clear
   ℹ️  Could improve: Add more detailed description (-2 pts)

✅ 🧩 Logic & Structure: 20/20 (100%)
   ✓ No DML in loops
   ✓ Simple decision structure
   ✓ Transform element used

⚠️  🏗️  Architecture & Orchestration: 12/15 (80%)
   ℹ️  Single monolithic flow - could break into subflows (-3 pts)

✅ ⚡ Performance & Bulk Safety: 20/20 (100%)
   ✓ Bulk-safe design
   ✓ Governor limits: Well within limits

⚠️  🔧 Error Handling & Observability: 15/20 (75%)
   ℹ️  No structured error logging (Sub_LogError not used) (-5 pts)

✅ 🔒 Security & Governance: 15/15 (100%)
   ✓ User mode (respects FLS/CRUD)
   ✓ No sensitive data accessed

═══════════════════════════════════════════════════════════════════
✅ DEPLOYMENT APPROVED (advisory recommendations provided)
═══════════════════════════════════════════════════════════════════

💡 Recommendations for Improvement:
1. [Error Handling] Add Sub_LogError for structured error logging
2. [Architecture] Consider breaking into parent + subflows for complex logic
3. [Documentation] Expand flow description for better documentation
```

## Two-Step Deployment

The skill always uses a safe deployment process:

**Step 1: Validation (Check-Only)**
```
- Deploys with --check-only flag (dry-run)
- Verifies metadata structure
- Checks org-specific compatibility
- No actual deployment yet
```

**Step 2: Actual Deployment**
```
- Only proceeds if validation passes
- Deploys to target org
- Monitors deployment status
- Provides verification steps
```

**Step 3: Activation Prompt**
```
Always asks before activating:
- "Keep as Draft" (recommended for production)
- "Activate Now" (use after thorough testing)
```

## Best Practices Enforced

### Performance
- **Bulkification**: All record-triggered flows must handle collections
- **No DML in Loops**: CRITICAL ERROR if detected
- **Transform Element**: 30-50% faster than loops for field mapping
- **Minimize DML**: Batch operations where possible

### Design
- **Error Handling**: Fault paths on all DML operations
- **Meaningful Names**: Variables (camelCase), Elements (PascalCase_With_Underscores)
- **Descriptions**: Document complex logic
- **Subflows**: Reusable patterns

### Security
- **System vs User Mode**: Understand implications
- **Field-Level Security**: Validate permissions
- **No Hardcoded Data**: Use variables or custom settings

## Requirements

- **Salesforce CLI**: `sf` command installed and configured
- **sf-deployment skill**: Version ≥2.0.0 (for deployment operations)
- **Python 3**: For validation script (optional but recommended)
- **Target Org**: Authenticated org with appropriate permissions

## File Structure

```
~/.claude/skills/sf-flow-builder/
├── skill.md                                      # Main skill definition
├── README.md                                     # This file
├── LICENSE                                       # MIT License
│
├── templates/
│   ├── screen-flow-template.xml                  # Screen flow base
│   ├── record-triggered-after-save.xml           # After-save trigger base
│   ├── record-triggered-before-save.xml          # Before-save trigger base
│   ├── record-triggered-before-delete.xml        # Before-delete trigger base
│   ├── platform-event-flow-template.xml          # Platform event base
│   ├── autolaunched-flow-template.xml            # Autolaunched base
│   ├── scheduled-flow-template.xml               # Scheduled flow base
│   ├── flow-documentation-template.md            # Documentation template
│   ├── architecture-review-template.md           # Review template
│   └── subflows/                                 # Reusable subflow library
│       ├── subflow-error-logger.xml              # Sub_LogError
│       ├── subflow-email-alert.xml               # Sub_SendEmailAlert
│       ├── subflow-record-validator.xml          # Sub_ValidateRecord
│       ├── subflow-bulk-updater.xml              # Sub_BulkUpdater
│       └── subflow-query-with-retry.xml          # Sub_QueryWithRetry
│
├── validators/                                   # Python validation scripts
│   ├── enhanced_validator.py                    # 6-category validator (110 pts)
│   ├── naming_validator.py                      # Naming convention checks (advisory)
│   ├── security_validator.py                    # Security & governance checks
│   ├── flow_simulator.py                        # Bulk simulation (200+ records)
│   └── flow_validator.py                        # Legacy validator (deprecated)
│
├── generators/
│   └── doc_generator.py                         # Auto-documentation generator
│
├── examples/                                    # Complete example implementations
│   ├── screen-flow-example.md                   # Screen flow walkthrough
│   ├── record-trigger-example.md                # Record trigger example
│   ├── autolaunched-example.md                  # Autolaunched example
│   ├── error-logging-example.md                 # Sub_LogError usage
│   ├── orchestration-parent-child.md            # Parent-child pattern
│   ├── orchestration-sequential.md              # Sequential pattern
│   └── orchestration-conditional.md             # Conditional pattern
│
├── docs/                                        # Comprehensive documentation
│   ├── subflow-library.md                       # Subflow library guide (40+ pages)
│   ├── orchestration-guide.md                   # Orchestration patterns guide
│   ├── governance-checklist.md                  # 85-item governance checklist
│   ├── security-best-practices.md               # Security guidance (planned)
│   ├── flow-best-practices.md                   # Salesforce Flow best practices
│   └── troubleshooting.md                       # Common issues and solutions
│
└── tests/                                       # Testing resources (planned)
    └── test_flows/                              # Sample flows for testing
```

## Testing Your Flows

### Screen Flows
- Navigate to Setup → Flows → [FlowName]
- Click "Run" to test UI
- Verify all screens and decision paths
- Test with invalid data for validation

### Record-Triggered Flows
- Create test records that meet trigger criteria
- **CRITICAL**: Test with bulk data (200+ records)
- Check Debug Logs for execution
- Verify no governor limit errors

### Autolaunched Flows
- Create Apex test classes to invoke
- Test with various input parameters
- Verify output variables
- Check error handling

### Scheduled Flows
- Test logic manually before activating schedule
- Monitor first scheduled run
- Verify batch processing with expected volume

## Troubleshooting

### "Validation fails but I can't see the issue"
Run the Python validator directly:
```bash
python3 ~/.claude/skills/sf-flow-builder/validators/flow_validator.py \
  force-app/main/default/flows/YourFlow.flow-meta.xml
```

### "Flow works in sandbox but fails in production"
- Check field-level security differences
- Verify all dependent metadata deployed
- Review validation rules
- Test with production data volume

### "Performance issues with flow"
- Check for DML in loops (validator catches this)
- Use Transform element instead of loops
- Minimize DML operations
- Use Get Records with filters

### "Flow doesn't appear after deployment"
- Check deployment status: `sf project deploy report`
- Verify user permissions
- Refresh metadata in org

## Examples

See the `examples/` directory for detailed walkthroughs:

**Basic Flow Types:**
- `screen-flow-example.md` - Customer feedback form
- `record-trigger-example.md` - Opportunity stage updates
- `autolaunched-example.md` - Account total calculation

**NEW - Orchestration Patterns:**
- `orchestration-parent-child.md` - Account industry change orchestrator
- `orchestration-sequential.md` - Order processing pipeline (5 steps)
- `orchestration-conditional.md` - Case triage router (4 handlers)

**NEW - Reusable Subflows:**
- `error-logging-example.md` - Structured error logging with Sub_LogError

## Resources

- [Salesforce Flow Documentation](https://help.salesforce.com/s/articleView?id=sf.flow.htm)
- [Flow Best Practices](https://help.salesforce.com/s/articleView?id=sf.flow_prep_bestpractices.htm)
- [API 62.0 Release Notes](https://help.salesforce.com/s/articleView?id=release-notes.rn_forcecom_flow.htm)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the SKILL.md for detailed workflow
3. Run the Python validator for detailed diagnostics

## Version

**Current Version**: 1.3.0 (Complete Rewrite - Best Practices Integration)
**API Version**: 62.0 (Winter '26)
**Last Updated**: 2025-11-30

### What's New in 1.3.0 🎉

**Major Enhancements - Industry Best Practices Integration:**

**🧩 Reusable Subflow Library (NEW):**
- ✅ 5 pre-built, production-ready subflow templates
- ✅ Sub_LogError - Structured error logging with observability
- ✅ Sub_SendEmailAlert - Standard notification patterns
- ✅ Sub_ValidateRecord - Common validation logic
- ✅ Sub_BulkUpdater - Bulk update patterns with error handling
- ✅ Sub_QueryWithRetry - Query with built-in fault handling
- ✅ 40+ page documentation guide (docs/subflow-library.md)
- ✅ Complete deployment and usage instructions

**🏗️ Orchestration Patterns (NEW):**
- ✅ 3 architectural patterns with complete implementations
- ✅ Parent-Child pattern - Multiple independent responsibilities
- ✅ Sequential pattern - Pipeline processing with data propagation
- ✅ Conditional pattern - Scenario-based routing to handlers
- ✅ Automatic complexity detection and pattern suggestions
- ✅ Comprehensive orchestration guide (docs/orchestration-guide.md)
- ✅ Real-world examples for each pattern

**🔒 Enhanced Validation System (NEW):**
- ✅ **110-point comprehensive scoring** (upgraded from 100)
- ✅ **6-category validation** (Design, Logic, Architecture, Performance, Errors, Security)
- ✅ enhanced_validator.py - New multi-category validator
- ✅ naming_validator.py - Naming convention checks (advisory)
- ✅ security_validator.py - Security and governance checks
- ✅ Advisory mode - Non-critical checks provide suggestions without blocking
- ✅ Rating system: ⭐⭐⭐⭐⭐ (Excellent) to ⭐ (Needs Improvement)

**🔐 Security & Governance (NEW):**
- ✅ Security validation - System mode detection, sensitive field warnings
- ✅ 85-item governance checklist with 200-point scoring
- ✅ Architecture review template for complex flows
- ✅ Profile testing guidance (Standard User, Custom Profiles, Permission Sets)
- ✅ FLS/CRUD validation testing procedures
- ✅ Minimum governance score: 140/200 for production deployment

**📚 Auto-Documentation (NEW):**
- ✅ doc_generator.py - Automated documentation from flow XML
- ✅ Extracts 50+ data points automatically
- ✅ Comprehensive template with 15+ sections
- ✅ Testing status tracking, troubleshooting, dependencies
- ✅ One-command generation from any flow XML

**🎯 5-Phase Workflow Enhancement:**
- ✅ Phase 1: Subflow library offering + governance assessment
- ✅ Phase 2: Orchestration pattern suggestions for complex flows
- ✅ Phase 3: Enhanced validation with 6-category scoring
- ✅ Phase 4: Auto-documentation generation + governance completion
- ✅ Phase 5: Security/profile testing + auto-generated docs review

### Previous Versions

**1.2.0 - Simulation & Extended Flow Types:**
- Bulk simulation mode (tests with 200+ records)
- Governor limit analysis and warnings
- Resource usage tracking (SOQL, DML, CPU time)
- Platform Event-triggered flows
- Record-Triggered before-save and before-delete flows
- Enhanced template library (7 types total)

**1.1.0 - Initial Release:**
- Basic flow creation (5 types)
- Validation with 100-point scoring
- Two-step deployment
- Integration with sf-deployment skill

## License

This skill is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2024-2025 Jag Valaiyapathy
