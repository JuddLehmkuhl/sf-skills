---
name: sf-solution-design
description: >
  Use when designing any Salesforce solution, feature, or customization. Runs an
  8-question checklist against available org capabilities (via PSL discovery) to
  maximize platform leverage before writing custom code. Routes to sf-metadata,
  sf-apex, sf-flow, sf-lwc, sf-ai-agentforce, and sf-deploy once decisions are made.
license: MIT
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "Qualitative — pass/fail on checklist completion"
---

# Solution Design Framework

> **Purpose:** Ensure every Salesforce solution leverages available platform capabilities before building custom solutions.
>
> **When to Use:** Before designing ANY Salesforce solution, feature, or customization. This is Step 0 in the orchestration order.
>
> **Principle:** Configuration first, code second. The ideal Salesforce org is 80% declarative, 20% programmatic.

---

## Guiding Principles

These principles align with the [Salesforce Well-Architected Framework](https://architect.salesforce.com/well-architected/overview) and the [Architect Decision Guides](https://architect.salesforce.com/decision-guides):

1. **Trusted** -- Solutions protect stakeholders through security, compliance, and reliability
2. **Easy** -- Solutions deliver value fast by leveraging out-of-the-box features
3. **Adaptable** -- Solutions evolve with the business without rewrites

### The Configuration-First Mandate

Before writing a single line of Apex or building a custom LWC, ask:

- Can a **standard object** handle this? (Do not create `Application__c` if `Opportunity` fits.)
- Can a **declarative tool** handle this? (Flows, validation rules, formulas, approval processes.)
- Can a **platform feature** handle this? (Einstein, Agentforce, OmniStudio, Data Cloud.)

Only when every declarative and platform option is exhausted should custom code enter the picture.

---

## Overview

This skill provides an intelligent solution design framework that:

1. **Discovers** what features are available in the target org (via PSL analysis)
2. **Evaluates** requirements against an 8-question checklist
3. **Decides** the right tool for each concern (config vs. code, Flow vs. Apex, standard vs. custom)
4. **Routes** to the appropriate skill for implementation

This prevents overbuilding custom solutions when out-of-the-box features already exist.

---

## Cross-Skill Routing Map

This skill is the **entry point** for all Salesforce work. After completing the checklist, route to:

| Decision Outcome | Route To | When |
|---|---|---|
| Need custom objects or fields | `sf-metadata` | Standard objects cannot meet the requirement |
| Need Apex classes or triggers | `sf-apex` | Flow cannot handle the logic (see Decision Matrix below) |
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
1. sf-metadata         --> Create objects/fields (only if needed after checklist)
2. sf-apex             --> Create Apex classes (only if needed after checklist)
3. sf-flow             --> Create Flows that reference Apex/metadata
4. sf-deploy           --> Deploy all metadata to org
5. sf-ai-agentforce    --> Publish agents (requires deployed dependencies)
```

---

## Phase 1: Feature Discovery

Before designing a solution, you must know what is available. Run the discovery process for the target org.

### Option A: Query PSLs Directly (Recommended)

```bash
# Get all Permission Set Licenses in the org
sf data query --query "SELECT Id, MasterLabel, DeveloperName, TotalLicenses, UsedLicenses FROM PermissionSetLicense ORDER BY MasterLabel" --target-org TARGET_ORG --json

# Get PSLs assigned to a specific user
sf data query --query "SELECT PermissionSetLicense.MasterLabel FROM PermissionSetLicenseAssign WHERE AssigneeId = 'USER_ID' ORDER BY PermissionSetLicense.MasterLabel" --target-org TARGET_ORG

# Also check installed packages (may unlock additional features)
sf data query --query "SELECT NamespacePrefix, Name FROM PackageLicense ORDER BY NamespacePrefix" --target-org TARGET_ORG
```

### Option B: Ask User for PSL List

If CLI access is not available, ask the user:

> "To design the best solution, I need to know what features are available in your org. Can you provide:
> 1. A list of Permission Set Licenses from Setup > Company Information > Permission Set Licenses, OR
> 2. Export from this query: `SELECT MasterLabel FROM PermissionSetLicense ORDER BY MasterLabel`
> 3. Which Salesforce cloud(s) are licensed? (Sales Cloud, Service Cloud, FSC, Health Cloud, etc.)"

### Option C: Use Cached Inventory

If an org has a documented feature inventory (like `/docs/AVAILABLE_FEATURES_REFERENCE.md`), reference that document.

### Option D: Infer from Project Structure

If no PSL data is available, examine the project:

```bash
# Check for industry-specific objects
sf data query --query "SELECT QualifiedApiName FROM EntityDefinition WHERE NamespacePrefix IN ('FinServ','HealthCloudGA','Automotive','ConGds') LIMIT 50" --target-org TARGET_ORG

# Check installed packages
sf package installed list --target-org TARGET_ORG
```

---

## Phase 2: PSL-to-Feature Mapping (Condensed Reference)

Use this reference to map discovered PSLs to platform capabilities. Organized by cloud/domain.

> **Tip:** PSL names change across releases. Use pattern matching (`LIKE '%Einstein%'`) rather than exact names.

### Core Platform (All Orgs)

Every Salesforce org includes these capabilities regardless of PSLs:

| Capability | Details |
|---|---|
| Standard Objects | Account, Contact, Lead, Opportunity, Case, Task, Event, Campaign, etc. |
| Record Types & Page Layouts | Multi-process support on any object |
| Validation Rules & Formulas | Declarative data quality enforcement |
| Flows (Record-Triggered, Screen, Autolaunched, Scheduled) | Full automation engine |
| Approval Processes | Multi-step approval routing |
| Reports & Dashboards | Standard analytics |
| Permission Sets & Profiles | Security model |
| Custom Metadata Types | Configuration-as-code |
| Platform Events | Event-driven architecture |
| Change Data Capture | Real-time data change streaming |

### Sales Cloud

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Sales User, Sales Console User | Core sales functionality, console UI |
| Sales Cloud Einstein | AI lead/opportunity scoring, insights |
| Pipeline Inspection | Visual pipeline management with AI |
| Salesforce Forecasting | Revenue forecasting and quotas |
| Sales Engagement | Cadences, sequences, automated outreach |
| Einstein Activity Capture | Auto-log emails and calendar events |
| Sales Action Plans | Templated task sequences |

### Service Cloud

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Service Cloud User | Case management, entitlements, milestones |
| Knowledge | Knowledge base, article management |
| Omni-Channel | Intelligent routing, presence, capacity |
| Field Service | Work orders, service appointments, mobile |
| Einstein for Service | Case classification, reply recommendations |

### Industry Clouds

| Cloud | Key PSL Patterns | Standard Objects / Features |
|---|---|---|
| Financial Services (FSC) | Financial Services Cloud Standard, Digital Lending | InsurancePolicy, Claim, Producer, ARC graphs, Person Accounts, Rollup Summaries, Business Milestones |
| Health Cloud | HealthCloudGA, Care Plans | Patient, CarePlan, CareProgram, ClinicalEncounter, HealthcareProvider |
| Manufacturing Cloud | Manufacturing Cloud | SalesAgreement, AccountForecast, MarketSegment |
| Automotive Cloud | Automotive Cloud | Vehicle, VehicleAsset, TestDrive |
| Consumer Goods | Consumer Goods Cloud | RetailStore, StoreAssortment, Visit |
| Public Sector | Public Sector Solutions | RegulatoryCode, Violation, Inspection |

> **Important:** Question 1 in the checklist below adapts to whichever cloud is licensed. It is NOT FSC-only.

### Einstein AI Features

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Einstein Search, Einstein Search Answers | AI-powered search with natural language |
| Einstein GPT Sales Emails | AI-generated email drafts |
| Einstein Sales Summaries | AI account/opportunity summaries |
| Einstein GPT Service Replies | AI-suggested service responses |
| Einstein Next Best Action | Recommendations engine |
| Einstein Prompt Templates | Reusable AI prompts |
| Unmetered User-Based AI | No per-transaction AI limits |

### Agentforce

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Agentforce (Default) | Core agent platform access |
| Agent Platform Builder | Build custom autonomous agents |
| Agentforce Service Agent Builder | Build service chatbots |
| Agentforce SDR Access/Agent | Automated prospecting agents |
| Agentforce Sales Coach | Real-time sales guidance agents |

> **Note:** PSLs ending in "Agent" require dedicated service accounts. Human users get "Builder" and "Access" PSLs.

### Data Cloud

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Data Cloud | Customer Data Platform, unified profiles |
| Remote Data Cloud | Zero-copy access to external data |
| Data Pipelines Base User | ETL/ELT data ingestion |
| Context Service Runtime | Real-time data for flows/agents |

### OmniStudio

| PSL Pattern | Capabilities Unlocked |
|---|---|
| OmniStudio | FlexCards, OmniScripts, DataRaptors, Integration Procedures |
| Business Rules Engine | No-code decision tables |
| DocGen Designer | Document generation from templates |

### Analytics

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Tableau Next | Tableau dashboards |
| Analytics View Only Embedded App | Embedded analytics in records |
| CRM Analytics | AI-powered analytics |

### Marketing

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Marketing Cloud | Full marketing automation |
| Account Engagement | B2B marketing (Pardot) -- nurture, scoring |

### Documents & Contracts

| PSL Pattern | Capabilities Unlocked |
|---|---|
| Contract Lifecycle Management | End-to-end contract tracking |
| Contracts AI | AI contract analysis |
| DocGen Designer | Template-based document generation |

---

## Phase 3: The 8-Question Solution Design Checklist

**MANDATORY:** Before designing any solution, answer these 8 questions in order. Each question is designed to be cloud-agnostic. Adapt Question 1 based on which cloud(s) are licensed.

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
**Route to:** Einstein Setup in the target org. No skill needed -- this is declarative configuration.

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
**Route to:** OmniStudio Designer in the target org. If custom LWC is still needed alongside, route to `sf-lwc`.

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

After completing the 8-question checklist, use these matrices for the remaining design decisions.

### Decision Matrix: Flow vs. Apex

Use this when the checklist confirms that custom automation is needed.

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

> **Rule of thumb:** Flow handles ~70% of automation. Apex handles the other ~30%, which is often the most business-critical. See the [Architect's Guide to Record-Triggered Automation](https://architect.salesforce.com/decision-guides/trigger-automation) for details.
>
> **Route to:** `sf-flow` for Flow work, `sf-apex` for Apex work. When using Apex triggers, follow the Trigger Actions Framework documented in `salesforce-trigger-framework/SKILL.md`.

### Decision Matrix: Standard Object vs. Custom Object

| Scenario | Use Standard | Use Custom | Rationale |
|---|---|---|---|
| Tracking companies/organizations | Account | -- | Standard object with full platform support |
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

### Decision Matrix: Custom LWC vs. Declarative UI

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

## Phase 5: Solution Patterns

After completing the checklist and decision matrices, use these patterns for common scenarios.

### Account & Relationship Management
```
Hierarchy Visualization  --> ARC relationship graphs (FSC) OR Account Hierarchy (standard)
Individual Tracking      --> Person Accounts
Organization Tracking    --> Business Accounts with Record Types
Relationship Mapping     --> Account-Account Relations OR Contact Roles
Quick Context            --> Einstein Sales Summaries + Record Research
```

### Sales Process
```
Prospecting     --> Sales Engagement cadences OR SDR Agent
Pipeline Mgmt   --> Pipeline Inspection + Forecasting
Activity Logging --> Einstein Activity Capture (automatic)
Deal Progression --> Close Plans + Buying Committee
Follow-ups      --> Meeting Follow-Up Emails (AI-generated)
Coaching        --> Sales Coach agent during calls
```

### Customer Service
```
Support Inquiries --> Service Agent (autonomous)
Response Drafting --> GPT Service Replies
Case Context      --> Work Summaries
Knowledge Lookup  --> Knowledge base + Search Answers
Call Analysis     --> Conversation Insights
Routing           --> Omni-Channel with skill-based routing
```

### Data Integration
```
External System Sync --> Data Cloud pipelines OR Named Credentials + External Services
Real-time Data       --> Context Service in flows OR Platform Events
Record Matching      --> Identity Resolution (Data Cloud) OR Duplicate Rules (standard)
Unified View         --> Customer Data Platform profiles
```
> **Route to:** `sf-integration` for Named Credentials, External Services, REST/SOAP callouts.

### Guided Experiences
```
Multi-step Processes   --> OmniScripts (if available) OR Screen Flows
Dynamic UI Cards       --> FlexCards (if available) OR LWC
Decision Logic         --> Business Rules Engine OR Flow Decision elements
Document Generation    --> DocGen templates OR custom Apex (see sf-apex)
```

### Task & Process Management
```
Templated Task Sequences --> Action Plan Templates (see sf-action-plans)
Required Document Lists  --> Document Checklist Items (see sf-action-plans)
Approval Workflows       --> Approval Processes (standard)
Scheduled Reminders      --> Scheduled Flows (see sf-flow)
```

### Reporting & Analytics
```
Executive Dashboards   --> Tableau
Operational Metrics    --> CRM Analytics
Record-level Insights  --> Embedded Analytics
Standard Reporting     --> Reports & Dashboards (available in ALL orgs)
```

---

## Anti-Patterns: What NOT to Do

Avoiding these common mistakes is as important as following best practices. Each anti-pattern includes the correct approach.

### Anti-Pattern 1: The Golden Hammer

**Symptom:** Using one tool for everything (e.g., building ALL automation in Apex, or ALL UI in custom LWC).

**Why it fails:** Increases maintenance burden, bypasses platform optimizations, and creates unnecessary technical debt.

**Correct approach:** Use the Decision Matrices above. Match the tool to the requirement, not the developer's comfort zone.

### Anti-Pattern 2: Custom Object Sprawl

**Symptom:** Creating custom objects (`Application__c`, `Request__c`, `Interaction__c`) when standard objects (Opportunity, Case, Task) would suffice.

**Why it fails:** Custom objects miss out on standard features (forecasting, entitlements, activity timelines, report types). They require custom security, sharing rules, and UI from scratch.

**Correct approach:** Run the Standard vs. Custom Object decision matrix. If a standard object covers 80%+ of the fields, use it with record types for differentiation.

### Anti-Pattern 3: Ignoring Industry Cloud Data Models

**Symptom:** Building a custom insurance data model when FSC provides InsurancePolicy, Claim, and Producer. Building a custom patient model when Health Cloud provides Patient and CarePlan.

**Why it fails:** Industry cloud objects include pre-built relationships, page layouts, reports, and process automation. Rebuilding these costs months and misses future platform enhancements.

**Correct approach:** Run Phase 1 (Feature Discovery) and Question 1 of the checklist. Always check industry cloud data models before creating custom objects.

### Anti-Pattern 4: Code Where Configuration Suffices

**Symptom:** Writing Apex triggers for field updates that could be Before-Save Flows. Writing Apex for validation that could be Validation Rules. Writing LWC for forms that could be Screen Flows.

**Why it fails:** Code requires test classes (95%+ coverage), deployments, and developer maintenance. Declarative solutions are admin-maintainable and auto-tested by the platform.

**Correct approach:** Use the Flow vs. Apex decision matrix. Only write Apex when declarative tools genuinely cannot handle the requirement.

### Anti-Pattern 5: Gold Plating / Over-Engineering

**Symptom:** Building a generic, framework-level solution for a one-off business requirement. Creating abstract service layers for simple CRUD operations. Adding "future flexibility" that is never used.

**Why it fails:** Premature abstraction adds complexity without value. YAGNI (You Aren't Gonna Need It) applies to Salesforce development too.

**Correct approach:** Build the simplest solution that meets the current requirement. Refactor when (not before) additional complexity is justified by real requirements.

### Anti-Pattern 6: Big Ball of Mud

**Symptom:** No clear separation between triggers, services, selectors, and controllers. God classes with 2000+ lines. Triggers with inline logic instead of framework delegation.

**Why it fails:** Untestable, undeployable, and unmaintainable. Changes in one area break unrelated functionality.

**Correct approach:** Follow the Trigger Actions Framework (`salesforce-trigger-framework/SKILL.md`). Use the layered architecture: `Trigger --> MetadataTriggerHandler --> TA_* --> Services --> DAL`.

### Anti-Pattern 7: Spaghetti Sharing Model

**Symptom:** Dozens of sharing rules, criteria-based sharing, Apex sharing, and manual shares layered on top of each other with no documentation.

**Why it fails:** Nobody can determine why a user does or does not have access to a record. Debugging access issues becomes a multi-day investigation.

**Correct approach:** Design the sharing model upfront. Use the simplest OWD (Organization-Wide Defaults) that meets security requirements. Layer sharing rules sparingly and document each one.

### Anti-Pattern 8: SOQL/DML in Loops

**Symptom:** Querying or updating records inside a `for` loop in Apex. Creating Flow loops that perform Get/Update elements per iteration.

**Why it fails:** Governor limits (100 SOQL queries, 150 DML statements per transaction). Fails silently in small tests but explodes in production with real data volumes.

**Correct approach:** Bulkify all data operations. Collect IDs, query once, process in memory, update once. In Flows, use collection variables. In Apex, use Maps and bulk DML. See `sf-apex/SKILL.md` for patterns.

---

## Usage Examples

### Example 1: "We need to send follow-up emails after meetings"

**Checklist Results:**
- Q2 (Einstein AI): YES -- Meeting Follow-Up Emails PSL available

**Solution:** Configure Einstein Meeting Follow-Up Emails feature. No custom code needed.
**Route to:** Einstein Setup (declarative).

### Example 2: "We need to visualize account ownership hierarchies"

**Checklist Results:**
- Q1 (Standard Features): YES -- ARC (FSC) or Account Hierarchy (standard) available

**Solution:** Configure ARC relationship graph with ownership roles (FSC) or use standard Account Hierarchy. No custom components needed.
**Route to:** `sf-metadata` for relationship configuration.

### Example 3: "We need to automate prospect outreach"

**Checklist Results:**
- Q3 (Agentforce): YES -- SDR Agent PSLs available

**Solution:** Build SDR Agent with custom topics for your industry. No custom Apex/Flows needed.
**Route to:** `sf-ai-agentforce` for agent creation.

### Example 4: "We need to sync data from an external system"

**Checklist Results:**
- Q4 (Data Cloud): Check -- Are Data Cloud PSLs available?
  - If YES: Configure Data Cloud pipeline with identity resolution.
  - If NO: Use Named Credentials + External Services for REST integration.

**Route to:** `sf-integration` for Named Credentials / External Services setup.

### Example 5: "We need a guided onboarding wizard"

**Checklist Results:**
- Q5 (OmniStudio): Check -- Are OmniStudio PSLs available?
  - If YES: Build OmniScript for guided flow with FlexCards for context.
  - If NO: Build Screen Flow with Dynamic Forms. If that is insufficient, build custom LWC.

**Route to:** `sf-flow` for Screen Flows, or `sf-lwc` for custom components.

### Example 6: "We need to track required documents for a loan application"

**Checklist Results:**
- Q1 (Standard Features): YES -- Document Checklist Items + Action Plan Templates available
- Q8 (Documents): YES -- DocGen for template generation if needed

**Solution:** Use Action Plan Templates with Document Checklist Items to track required documents. No custom objects needed.
**Route to:** `sf-action-plans` for template creation.

### Example 7: "We need a nightly batch job to process 2M records"

**Checklist Results:**
- All 8 questions: NO -- This is a bulk data processing requirement

**Decision Matrix (Flow vs. Apex):** Apex -- Batch Apex is required for >10k records with governor limit management.

**Solution:** Build Batch Apex class with proper chunking and error handling.
**Route to:** `sf-apex` for Batch Apex creation, then `sf-testing` for test coverage.

### Example 8: "We need a custom object to track insurance policies"

**Checklist Results:**
- Q1 (Standard Features): Check -- Is FSC licensed?
  - If YES: Use standard InsurancePolicy object. **Do NOT create a custom object.**
  - If NO: Custom object may be needed. Run Standard vs. Custom Object matrix.

**Route to:** `sf-metadata` for either standard object configuration or custom object creation.

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

After discovery, you can generate an org-specific feature reference document:

```markdown
# [Org Name]: Available Features Reference

> **Org:** [Alias]
> **Cloud(s):** [Sales Cloud, Service Cloud, FSC, Health Cloud, etc.]
> **PSLs Assigned:** [Count]
> **Generated:** [Date]

## Available Features
[List features based on discovered PSLs, organized by category]

## Solution Design Checklist (Org-Specific)
[Include the 8 questions with org-specific answers pre-filled]

## Not Available
[List features NOT available based on missing PSLs]

## Recommended Skill Routing
[Based on available features, list which skills are relevant for this org]
```

This becomes a permanent reference for that org's development team.

---

## Sources

- [Salesforce Well-Architected Framework](https://architect.salesforce.com/well-architected/overview) -- Trusted, Easy, Adaptable design principles
- [Architect Decision Guides](https://architect.salesforce.com/decision-guides) -- Official guides for forms, automation, and migration decisions
- [Architect's Guide to Record-Triggered Automation](https://architect.salesforce.com/decision-guides/trigger-automation) -- Flow vs. Apex decision framework
- [Architect's Guide to Building Forms](https://architect.salesforce.com/decision-guides/build-forms) -- Screen Flow vs. LWC vs. OmniScript decisions
- [Salesforce Architecture Basics](https://architect.salesforce.com/fundamentals/architecture-basics) -- Foundation architecture concepts
- [Permission Set Licenses Overview](https://help.salesforce.com/s/articleView?id=platform.users_permissionset_licenses_overview.htm&language=en_US&type=5) -- Official PSL documentation
- [Salesforce Anti-Patterns (Developer Blog)](https://developer.salesforce.com/blogs/engineering/2014/11/salesforce-anti-patterns-a-cautionary-tale) -- Common architecture mistakes
- [Salesforce Anti-Patterns (Salesforce Ben)](https://www.salesforceben.com/a-guide-to-6-salesforce-anti-patterns/) -- Golden Hammer, Big Ball of Mud, Spaghetti Sharing
- [Standard vs. Custom Objects (Salesforce Ben)](https://www.salesforceben.com/understanding-salesforce-standard-objects-vs-custom-objects/) -- When to create custom objects
- [Flow vs. Apex Decision Guide (SFDC Developers)](https://sfdcdevelopers.com/2025/09/17/when-to-use-flow-vs-apex/) -- Detailed comparison with examples
- [Salesforce Flow vs. Apex (Salesforce Ben)](https://www.salesforceben.com/salesforce-flow-builder-vs-apex/) -- Admin vs. developer automation tools
- [Configuration vs. Code (Quality Clouds)](https://qualityclouds.com/salesforce-code-vs-configuration/) -- 80/20 declarative-to-code ratio guidance
- [Salesforce Technical Debt Guide](https://www.default.com/post/salesforce-technical-debt) -- Causes, detection, and remediation
- [Well-Architected Trailhead Module](https://trailhead.salesforce.com/content/learn/modules/salesforce-well-architected) -- Interactive learning for the framework
