---
name: sf-solution-design
description: >
  Use when designing any Salesforce solution, feature, or customization. Runs an
  8-question checklist against available org capabilities (via PSL discovery) to
  maximize platform leverage before writing custom code. Routes to sf-metadata,
  sf-apex, sf-flow, sf-lwc, sf-ai-agentforce, and sf-deploy once decisions are made.
license: MIT
metadata:
  version: "2.1.0"
  author: "Jag Valaiyapathy"
  scoring: "Qualitative -- pass/fail on checklist completion"
---

# Solution Design Framework

> **When to Use:** Before designing ANY Salesforce solution. This is Step 0 in the orchestration order.
>
> **Principle:** Configuration first, code second. Target 80% declarative, 20% programmatic.

---

## Guiding Principles

Aligned with the [Salesforce Well-Architected Framework](https://architect.salesforce.com/well-architected/overview):

1. **Trusted** -- Protect stakeholders through security, compliance, and reliability
2. **Easy** -- Deliver value fast by leveraging out-of-the-box features
3. **Adaptable** -- Evolve with the business without rewrites

Before writing Apex or building a custom LWC, ask:
- Can a **standard object** handle this? (Do not create `Application__c` if `Opportunity` fits.)
- Can a **declarative tool** handle this? (Flows, validation rules, formulas, approval processes.)
- Can a **platform feature** handle this? (Einstein, Agentforce, OmniStudio, Data Cloud.)

---

## Cross-Skill Routing Map

This skill is the **entry point** for all Salesforce work. After completing the checklist, route to:

| Decision Outcome | Route To | When |
|---|---|---|
| Need custom objects or fields | `sf-metadata` | Standard objects cannot meet the requirement |
| Need Apex classes or triggers | `sf-apex` | Flow cannot handle the logic (see Decision Matrix) |
| Need automation (record/schedule) | `sf-flow` | Declarative automation is sufficient |
| Need custom UI components | `sf-lwc` | Standard page layouts and FlexCards cannot meet UX needs |
| Need autonomous agents | `sf-ai-agentforce` | Agentforce PSLs are available and use case fits |
| Need to deploy metadata | `sf-deploy` | After generating metadata with any skill above |
| Need integration with external systems | `sf-integration` | Named Credentials, External Services, Platform Events |
| Need OAuth / Connected Apps | `sf-connected-apps` | External Client Apps, OAuth flows |
| Need Action Plan templates | `sf-action-plans` | Document Checklist Items, lifecycle management |
| Need architecture diagrams | `sf-diagram` | ERD, OAuth flows, system architecture visualization |
| Need to run / review tests | `sf-testing` | Apex test execution, coverage analysis |
| Need to debug issues | `sf-debug` | Log analysis, governor limits, fix suggestions |
| Need SOQL queries | `sf-soql` | Query generation, optimization, validation |

### Orchestration Order

```
0. sf-solution-design  --> YOU ARE HERE: Discover features, run checklist
1. sf-metadata         --> Create objects/fields (only if needed)
2. sf-apex             --> Create Apex classes (only if needed)
3. sf-flow             --> Create Flows that reference Apex/metadata
4. sf-deploy           --> Deploy all metadata to org
5. sf-ai-agentforce    --> Publish agents (requires deployed dependencies)
```

---

## Phase 1: Feature Discovery

Before designing a solution, discover what is available in the target org.

### Option A: Query PSLs Directly (Recommended)

```bash
# Get all Permission Set Licenses in the org
sf data query --query "SELECT Id, MasterLabel, DeveloperName, TotalLicenses, UsedLicenses FROM PermissionSetLicense ORDER BY MasterLabel" --target-org TARGET_ORG --json

# Get PSLs assigned to a specific user
sf data query --query "SELECT PermissionSetLicense.MasterLabel FROM PermissionSetLicenseAssign WHERE AssigneeId = 'USER_ID' ORDER BY PermissionSetLicense.MasterLabel" --target-org TARGET_ORG

# Check installed packages
sf data query --query "SELECT NamespacePrefix, Name FROM PackageLicense ORDER BY NamespacePrefix" --target-org TARGET_ORG
```

### Option B: Ask User for PSL List

> "To design the best solution, I need to know what features are available in your org. Can you provide:
> 1. A list of Permission Set Licenses from Setup > Company Information > Permission Set Licenses, OR
> 2. Export from: `SELECT MasterLabel FROM PermissionSetLicense ORDER BY MasterLabel`
> 3. Which Salesforce cloud(s) are licensed? (Sales Cloud, Service Cloud, FSC, Health Cloud, etc.)"

### Option C: Use Cached Inventory

If an org has a documented feature inventory (like `/docs/AVAILABLE_FEATURES_REFERENCE.md`), reference that document.

### Option D: Infer from Project Structure

```bash
# Check for industry-specific objects
sf data query --query "SELECT QualifiedApiName FROM EntityDefinition WHERE NamespacePrefix IN ('FinServ','HealthCloudGA','Automotive','ConGds') LIMIT 50" --target-org TARGET_ORG

# Check installed packages
sf package installed list --target-org TARGET_ORG
```

---

## Phase 2: PSL-to-Feature Mapping

Map discovered PSLs to platform capabilities using the full reference.

> **Deep dive:** See `references/psl-feature-mapping.md` for complete PSL-to-capability tables organized by cloud/domain.

---

## Phase 3: The 8-Question Solution Design Checklist

**MANDATORY:** Answer these 8 questions in order before designing any solution. Each is cloud-agnostic; adapt Question 1 to the licensed cloud.

### Question 1: Can standard platform or industry cloud features handle this?

**Adapt to the licensed cloud:**
- **Sales Cloud:** Opportunities, Products, Price Books, Quotes, Forecasting, Territory Management
- **Service Cloud:** Cases, Entitlements, Milestones, Knowledge, Omni-Channel, Field Service
- **FSC:** InsurancePolicy, Claim, Producer, ARC graphs, Person Accounts, Rollup Summaries, Business Milestones
- **Health Cloud:** Patient, CarePlan, CareProgram, Clinical data model
- **Manufacturing Cloud:** SalesAgreement, AccountForecast
- **No Industry Cloud:** Standard objects (Account, Contact, Lead, Opportunity, Case), record types, page layouts, validation rules, formula fields, roll-up summary fields

**Also check cross-cloud standard features:**
- Person Accounts for individuals (available in many clouds)
- Account-Account Relationships for hierarchies
- Action Plans for templated task sequences (see `sf-action-plans`)
- Document Checklist Items for required-document tracking
- Business milestones for key date tracking
- Dynamic Forms and Dynamic Actions for flexible page layouts

**If YES:** Use standard configuration. Do not create custom objects or code.
**Route to:** `sf-metadata` for configuration, `sf-action-plans` for Action Plan Templates.

### Question 2: Can Einstein AI automate or assist?

- Einstein Search for intelligent finding
- GPT Sales Emails for drafting outreach
- Sales/Service Summaries for quick context
- Work Summaries for case/thread context
- Reply Recommendations for common responses
- Next Best Action for guidance
- Prompt Templates for reusable AI interactions
- Einstein Copilot for conversational assistance

**If YES:** Configure Einstein features before building custom automation.
**Route to:** Einstein Setup in the target org (declarative configuration).

### Question 3: Should an Agentforce agent handle this?

- SDR Agent for prospecting and outreach
- Service Agent for customer support
- Sales Coach for real-time guidance
- Record Engagement Agent for follow-ups
- Inbound Lead Generation for qualification
- Custom agents for specialized workflows

**If YES:** Build an agent instead of flows/triggers for autonomous tasks.
**Route to:** `sf-ai-agentforce` for agent creation and publishing.

### Question 4: Does Data Cloud provide the data needed?

- Unified customer profiles across systems
- Identity resolution for matching records
- Data pipelines for ETL/ELT
- Zero-copy access to external data
- Segmentation for targeting
- Context Service for real-time data in automations

**If YES:** Use Data Cloud instead of custom integration code.
**Route to:** `sf-integration` for pipeline configuration if external connections are needed.

### Question 5: Can OmniStudio provide a guided experience?

- FlexCards for dynamic, contextual UI
- OmniScripts for step-by-step guided processes
- DataRaptors for no-code data transformation
- Integration Procedures for multi-step integrations
- Business Rules Engine for decision automation
- DocGen for document generation

**If YES:** Use OmniStudio instead of custom LWC/Apex.
**Route to:** OmniStudio Designer. If custom LWC is still needed alongside, route to `sf-lwc`.

### Question 6: Is there an analytics requirement?

- Tableau for executive dashboards
- CRM Analytics for Salesforce data analysis
- Embedded analytics on record pages
- Standard Reports & Dashboards (available in ALL orgs)

**If YES:** Use analytics tools instead of custom reports/dashboards.
**Route to:** Standard reporting or Tableau/CRMA setup in the target org.

### Question 7: Are marketing automations needed?

- Account Engagement (Pardot) for B2B nurture
- Email marketing and drip campaigns
- Lead scoring and grading
- Marketing Copilot for AI assistance
- Campaign management

**If YES:** Use marketing tools instead of custom email/campaign code.
**Route to:** Marketing Cloud or Account Engagement configuration.

### Question 8: Does this involve documents or contracts?

- Contract Lifecycle Management for agreements
- Contracts AI for analysis and extraction
- DocGen for template-based generation
- Document Checklist Items for required-document tracking (see `sf-action-plans`)
- Clause management for reusable content

**If YES:** Use CLM/DocGen instead of custom document handling.
**Route to:** `sf-action-plans` for Document Checklist Items; CLM setup for contracts.

---

## Phase 4: Decision Matrices

After completing the 8-question checklist, use these matrices for remaining design decisions.

### Flow vs. Apex

| Scenario | Use Flow | Use Apex | Rationale |
|---|---|---|---|
| Simple field updates on same record | YES | -- | Before-save flow, no DML cost |
| Record-triggered updates to related records | YES | -- | After-save flow handles bulkification |
| Screen-based user input collection | YES | -- | Screen flows with Dynamic Forms |
| Complex business logic with branching | YES | -- | Flow supports Decision elements |
| Scheduled batch processing (<10k records) | YES | -- | Scheduled-triggered flow |
| Batch processing (>10k records) | -- | YES | Batch Apex for governor limit management |
| Complex algorithms or math | -- | YES | Apex provides full programming capability |
| Callouts with retry logic or auth | -- | YES | Apex HTTP with custom error handling |
| Post-undelete processing | -- | YES | Flows do not support undelete triggers |
| Multi-object transactions with rollback | -- | YES | Database.setSavepoint() in Apex |
| Platform Event publishing/subscribing | EITHER | EITHER | Both support PE; choose by complexity |
| Invocable action for Flow reuse | -- | YES | Apex @InvocableMethod called from Flow |

> **Rule of thumb:** Flow handles ~70% of automation. Apex handles the other ~30%.
> **Route to:** `sf-flow` for Flow work, `sf-apex` for Apex work. For Apex triggers, follow `salesforce-trigger-framework/SKILL.md`.

### Standard Object vs. Custom Object

| Scenario | Use Standard | Use Custom | Rationale |
|---|---|---|---|
| Tracking companies/organizations | Account | -- | Full platform support |
| Tracking people | Contact / Lead / Person Account | -- | Choose based on lifecycle stage |
| Tracking deals/revenue | Opportunity + Products | -- | Full forecasting/pipeline support |
| Tracking support requests | Case | -- | Entitlements, milestones, Omni-Channel |
| Tracking tasks and activities | Task / Event | -- | Activity timeline, logging, reminders |
| Tracking marketing efforts | Campaign + CampaignMember | -- | ROI, hierarchy, member status |
| Industry-specific entity exists | Industry Object | -- | Check industry cloud data model first |
| Truly unique business entity | -- | Custom Object | No standard object fits the concept |
| Junction object for M:M | -- | Custom Object | Standard junction objects are limited |
| Configuration / settings data | -- | Custom Metadata Type | Deployable, queryable, no SOQL limits |

> **Route to:** `sf-metadata` for both standard object configuration and custom object creation.

### Custom LWC vs. Declarative UI

| Scenario | Use Declarative | Use LWC | Rationale |
|---|---|---|---|
| Record detail page | Dynamic Forms | -- | No code needed for field arrangement |
| Conditional field visibility | Dynamic Forms | -- | Component visibility rules |
| Simple data entry wizard | Screen Flow | -- | Built-in navigation, validation |
| Complex multi-step wizard | OmniScript (if available) | LWC | OmniScript preferred; LWC if no OmniStudio |
| Real-time data visualization | -- | LWC | Charts, graphs, custom rendering |
| Third-party JS library integration | -- | LWC | Only LWC supports external libraries |
| Custom record page layout | App Builder + Flexipages | -- | Drag-and-drop layout design |
| Contextual data cards | FlexCard (if available) | LWC | FlexCard preferred; LWC if no OmniStudio |

> **Route to:** `sf-lwc` for custom Lightning Web Components.

---

## Solution Patterns & Examples

> **Patterns:** See `references/solution-patterns.md` for common scenario mappings (account management, sales, service, data integration, guided experiences, task management, analytics).

> **Worked examples:** See `references/usage-examples.md` for 8 end-to-end examples showing how the checklist drives decisions.

---

## Anti-Patterns

> **Deep dive:** See `references/anti-patterns.md` for 8 anti-patterns with symptoms and correct approaches (Golden Hammer, Custom Object Sprawl, Ignoring Industry Clouds, Code Where Config Suffices, Gold Plating, Big Ball of Mud, Spaghetti Sharing, SOQL/DML in Loops).

---

## Quick Reference Card

```
+---------------------------------------------------------------+
|           SOLUTION DESIGN CHECKLIST                           |
+---------------------------------------------------------------+
| 1. Standard platform / industry features?                     |
|    --> Adapts to licensed cloud (Sales/Service/FSC/Health/etc) |
| 2. Einstein AI?                                               |
|    --> Search, GPT, Summaries, NBA, Prompt Templates          |
| 3. Agentforce agent?                                          |
|    --> SDR, Service, Coach, Custom agents                     |
| 4. Data Cloud?                                                |
|    --> CDP, Pipelines, Identity Resolution                    |
| 5. OmniStudio?                                                |
|    --> FlexCards, OmniScripts, BRE, DocGen                    |
| 6. Analytics?                                                 |
|    --> Tableau, CRMA, Embedded, Standard Reports              |
| 7. Marketing automation?                                      |
|    --> Pardot, Campaigns, Copilot                             |
| 8. Documents / Contracts?                                     |
|    --> CLM, DocGen, Contracts AI, Doc Checklist Items          |
+---------------------------------------------------------------+
| ONLY build custom code if ALL 8 questions = NO                |
| Then use Decision Matrices for Flow vs Apex, Std vs Custom    |
+---------------------------------------------------------------+

ROUTING:
  Config needed    --> sf-metadata
  Apex needed      --> sf-apex (follow salesforce-trigger-framework)
  Flow needed      --> sf-flow
  LWC needed       --> sf-lwc
  Agent needed     --> sf-ai-agentforce
  Integration      --> sf-integration / sf-connected-apps
  Action Plans     --> sf-action-plans
  Deploy           --> sf-deploy
  Test             --> sf-testing
  Debug            --> sf-debug
  Diagrams         --> sf-diagram
  SOQL             --> sf-soql
```

---

## Generating Org-Specific Documentation

> **Template:** See `references/org-documentation-template.md` for the full template to generate org-specific feature reference documents after discovery.

---

## Sources

- [Salesforce Well-Architected Framework](https://architect.salesforce.com/well-architected/overview)
- [Architect Decision Guides](https://architect.salesforce.com/decision-guides)
- [Architect's Guide to Record-Triggered Automation](https://architect.salesforce.com/decision-guides/trigger-automation)
- [Architect's Guide to Building Forms](https://architect.salesforce.com/decision-guides/build-forms)
- [Permission Set Licenses Overview](https://help.salesforce.com/s/articleView?id=platform.users_permissionset_licenses_overview.htm&language=en_US&type=5)
- [Flow vs. Apex Decision Guide (SFDC Developers)](https://sfdcdevelopers.com/2025/09/17/when-to-use-flow-vs-apex/)
- [Configuration vs. Code (Quality Clouds)](https://qualityclouds.com/salesforce-code-vs-configuration/)
