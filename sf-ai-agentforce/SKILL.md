---
name: sf-ai-agentforce
description: >
  Creates Agentforce agents using Agent Script syntax with 100-point scoring.
  Use when building AI agents, defining topics and actions, or deploying
  AiAuthoringBundle (v65+) or GenAiPlannerBundle (v65+) metadata.
license: MIT
compatibility: "Requires API v65.0+ (Winter '26) for deployment"
metadata:
  version: "1.0.0"
  author: "Judd Lehmkuhl"
  scoring: "100 points across 6 categories"
---

<!-- TIER: 1 | ENTRY POINT -->
<!-- This is the starting document - read this FIRST -->
<!-- Progressive disclosure: SKILL.md → Quick Refs → Detailed Refs → Specialized Guides -->

# sf-ai-agentforce: Agentforce Agent Creation with Agent Script

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows (directly) or Apex (via Agent Actions)
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment**: Publish agents using `sf agent publish authoring-bundle`

## Document Map (Progressive Disclosure)

**Read documents in tier order based on what you need:**

### Tier 2: Quick References
| Need | Document | Description |
|------|----------|-------------|
| **Full syntax + gotchas** | [agent-script-reference.md](docs/agent-script-reference.md) | Complete Agent Script spec + reserved words |
| **CLI commands** | [cli-guide.md](docs/cli-guide.md) | sf agent commands, preview, publish |
| **Syntax deep dive** | [agent-script-syntax-reference.md](docs/agent-script-syntax-reference.md) | Indentation, types, action targets, data mappings |

### Tier 3: Detailed References
| Need | Document | Description |
|------|----------|-------------|
| **Actions** | [actions-reference.md](docs/actions-reference.md) | Flow, Apex, Prompt actions + connection blocks |
| **Patterns & practices** | [patterns-and-practices.md](docs/patterns-and-practices.md) | Decision tree + best practices |
| **Prompt templates** | [prompt-templates.md](docs/prompt-templates.md) | PromptTemplate metadata integration |

### Tier 3: Battle-Tested Patterns (NEW)
| Need | Document | Description |
|------|----------|-------------|
| **Action invocation** | [action-invocation-patterns.md](docs/action-invocation-patterns.md) | Doomprompting fix, slot-filling, variable capture |
| **Prompt Builder** | [prompt-builder-integration.md](docs/prompt-builder-integration.md) | GenAiPromptTemplate actions, gotchas, merge fields |
| **Flow design** | [agent-flow-design.md](docs/agent-flow-design.md) | Naming, read-only pattern, session variables, ID detection |
| **Deployment lifecycle** | [deployment-lifecycle.md](docs/deployment-lifecycle.md) | Wave rollout, deploy cycle, version management, test suite |

### Examples
| File | Description |
|------|-------------|
| [customer-service-agent.agent](examples/customer-service-agent.agent) | Complete 7-topic agent with session variables and Prompt Builder |
| [agent-get-account-details.flow-meta.xml](examples/agent-get-account-details.flow-meta.xml) | Flow with ID/name detection, formatted output, inp_/out_ convention |

**Quick Links:**
- [Key Insights Table](#-key-insights) - Common errors and fixes
- [Scoring System](#scoring-system-100-points) - 6-category validation
- [Required Files Checklist](#required-files-checklist) - Pre-deployment verification

**Official Reference:**
- [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) - Salesforce's official Agent Script examples

---

## Battle-Tested Patterns

These patterns are validated in production Salesforce orgs and address the most common Agentforce development challenges.

### Action Invocation (Doomprompting Fix)
> **Full guide**: [action-invocation-patterns.md](docs/action-invocation-patterns.md)

**Problem**: Behavioral prompts ("IMMEDIATELY call this action", "MUST invoke") fail because the Atlas planner treats all text as conversation context, not execution directives.

**Solution**: Use `reasoning.actions` with slot-filling syntax:
```agentscript
reasoning:
    actions:
        lookup_account: @actions.get_account_details
            with inp_AccountNameOrId=...
            set @variables.current_account_id = @outputs.out_AccountId
```

The `...` means "LLM extracts this from conversation." The `set` captures output for follow-up actions.

### Prompt Builder Integration
> **Full guide**: [prompt-builder-integration.md](docs/prompt-builder-integration.md)

**When to use**: Generative content (briefings, summaries, analysis). Use Flows for deterministic data retrieval.

**Key syntax**:
```agentscript
actions:
    generate_briefing:
        inputs:
            "Input:Account": object
                complex_data_type_name: "lightning__recordInfoType"
        outputs:
            promptResponse: string
        target: "generatePromptResponse://Template_Name"
```

**Critical**: Input MUST use `object` type with `lightning__recordInfoType`, NOT string.

### Agent Flow Design
> **Full guide**: [agent-flow-design.md](docs/agent-flow-design.md)

**Key conventions**:
| Convention | Pattern | Example |
|------------|---------|---------|
| Flow name | `Agent_Get_<Entity>` | `Agent_Get_Account_Details` |
| Input vars | `inp_<Name>` | `inp_AccountId` |
| Output vars | `out_<Name>` | `out_ContactList` |
| Architecture | Read-only (SOQL only, no DML) | Agent queries, doesn't modify |

**ID vs Name detection**: `LEFT({!inp_AccountNameOrId}, 3) = '001'` routes to ID lookup vs name search.

### Deployment Lifecycle
> **Full guide**: [deployment-lifecycle.md](docs/deployment-lifecycle.md)

**Mandatory cycle**: Deactivate -> Modify -> Deploy -> Validate -> Publish -> Activate

**Wave rollout**: Start with 3-4 flows (Wave 1), test, fix, then add 2-3 topics per wave. Agent routing changes with each new topic -- test incrementally.

**Post-deploy iteration is normal**: Expect 2-3 iterations per wave for hallucination fixes, routing corrections, and reasoning strengthening.

---

## Pattern Templates (December 2025)

Template files for common patterns are in `templates/patterns/`:

| Pattern | Template | Description |
|---------|----------|-------------|
| **Prompt Template Actions** | `patterns/prompt-template-action.agent` | `generatePromptResponse://` target |
| **Multi-Step Workflows** | `patterns/multi-step-workflow.agent` | Boolean flags for progress tracking |
| **Procedural Instructions** | `patterns/procedural-instructions.agent` | `run @actions.x` inside instructions |
| **Topic System Overrides** | `patterns/system-instruction-overrides.agent` | `system:` blocks for persona switching |
| **Input Binding Patterns** | See [patterns-and-practices.md](docs/patterns-and-practices.md) | `...`, `@variables.x`, fixed values |

> **Production patterns**: See [Battle-Tested Patterns](#battle-tested-patterns) for patterns validated in production deployments.

---

## CRITICAL: Two Deployment Methods (Tested Dec 2025)

There are **two deployment methods** with **different capabilities**:

| Aspect | GenAiPlannerBundle | AiAuthoringBundle |
|--------|-------------------|-------------------|
| Deploy Command | `sf project deploy start` | `sf agent publish authoring-bundle` |
| **Visible in Agentforce Studio** | No | Yes |
| Flow Actions (`flow://`) | Supported | Supported (see requirements below) |
| Apex Actions (`apex://`) | Supported | Limited (class must exist) |
| Escalation (`@utils.escalate with reason`) | Supported | NOT Supported (SyntaxError) |
| `run` keyword (action callbacks) | Supported | NOT Supported (SyntaxError) |
| `filter_from_agent` (conditional actions) | Supported | NOT Supported (SyntaxError) |
| Variables without defaults | Supported | Supported |
| Lifecycle blocks (`before/after_reasoning`) | Supported | Supported |
| Topic transitions (`@utils.transition`) | Supported | Supported |
| Basic escalation (`@utils.escalate`) | Supported | Supported |
| API Version | v65.0+ required | v65.0+ required |

**Why the difference?** These methods correspond to two authoring experiences:
- **Script View** (GenAiPlannerBundle): Full Agent Script syntax with utility actions inherent to the script
- **Canvas/Builder View** (AiAuthoringBundle): Low-code visual builder where some utility actions are not yet available

**Recommendation**: Use **AiAuthoringBundle** if you need agents visible in Agentforce Studio. Use **GenAiPlannerBundle** if you need full Agent Script features (`run` keyword, escalate with reason).

---

## CRITICAL: Orchestration Order

**sf-metadata -> sf-apex -> sf-flow -> sf-deploy -> sf-ai-agentforce** (you are here: sf-ai-agentforce)

**Why this order?**
1. **sf-metadata**: Custom objects/fields must exist before Apex or Flows reference them
2. **sf-apex**: InvocableMethod classes must be deployed before Flow wrappers call them
3. **sf-flow**: Flows must be created AND deployed before agents can reference them
4. **sf-deploy**: Deploy all metadata before publishing agent
5. **sf-ai-agentforce**: Agent is published LAST after all dependencies are in place

**MANDATORY Delegation:**
- **Flows**: ALWAYS use `Skill(skill="sf-flow")` - never manually write Flow XML
- **Deployments**: Use `Skill(skill="sf-deploy")` for all deployments
- **Apex**: ALWAYS use `Skill(skill="sf-apex")` for InvocableMethod classes

See `shared/docs/orchestration.md` (project root) for cross-skill orchestration details.

---

## CRITICAL: API Version Requirement

**Agent Script requires API v64+ (Summer '25 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 64, Agent Script features won't be available.

---

## CRITICAL: File Structure

| Method | Path | Files | Deploy Command |
|--------|------|-------|----------------|
| **AiAuthoringBundle** | `aiAuthoringBundles/[Name]/` | `[Name].agent` + `.bundle-meta.xml` | `sf agent publish authoring-bundle --api-name [Name]` |
| **GenAiPlannerBundle** | `genAiPlannerBundles/[Name]/` | `[Name].genAiPlannerBundle` + `agentScript/[Name]_definition.agent` | `sf project deploy start --source-dir [path]` |

**XML templates**: See `templates/` for bundle-meta.xml and genAiPlannerBundle examples.

GenAiPlannerBundle agents do NOT appear in Agentforce Studio UI.

---

## Agent Script Syntax Reference

For detailed syntax rules including indentation, comments, reserved words, action targets, data type mappings, and advanced field attributes, see:

> **[agent-script-syntax-reference.md](docs/agent-script-syntax-reference.md)** -- Complete syntax reference

**Quick reminders:**
- Use TABS for indentation (recommended) -- never mix tabs and spaces
- System instructions: single quoted string only (no pipe `|` syntax)
- Reserved words: `description`, `inputs`, `outputs`, `target`, `label`, `source`, `escalate`
- Flow variable names MUST match Agent Script input/output names exactly
- Use `list[type]` not `list<type>`, `number` not `integer`, `True`/`False` not `true`/`false`

---

### Apex Actions in GenAiPlannerBundle

**`apex://` targets work in GenAiPlannerBundle if the Apex class exists:**

```agentscript
# Works in GenAiPlannerBundle (if class exists in org)
target: "apex://CaseCreationService"
```

**The following do NOT work in either method:**
```agentscript
# DOES NOT WORK - Invalid format
target: "apex://CaseService.createCase"  # No method name allowed
target: "action://Create_Support_Case"   # action:// not supported
```

**RECOMMENDED: Use Flow Wrapper Pattern**

The only reliable way to call Apex from Agent Script is to wrap the Apex in an Autolaunched Flow:

1. **Create Apex class** with `@InvocableMethod` annotation (use sf-apex skill)
2. **Deploy Apex** to org using `sf project deploy start`
3. **Create Autolaunched Flow wrapper** that calls the Apex via Action element:
   ```xml
   <actionCalls>
       <actionName>YourApexClassName</actionName>
       <actionType>apex</actionType>
       <!-- Map input/output variables -->
   </actionCalls>
   ```
4. **Deploy Flow** to org
5. **Reference Flow** in Agent Script:
```agentscript
# CORRECT - Use flow:// target pointing to Flow wrapper
target: "flow://Create_Support_Case"  # Flow that wraps Apex InvocableMethod
```

**Flow Wrapper Example:**

```xml
<!-- Create_Support_Case.flow-meta.xml -->
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <actionCalls>
        <name>Call_Apex_Service</name>
        <actionName>CaseCreationService</actionName>
        <actionType>apex</actionType>
        <inputParameters>
            <name>subject</name>
            <value><elementReference>inp_Subject</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_CaseNumber</assignToReference>
            <name>caseNumber</name>
        </outputParameters>
    </actionCalls>
    <!-- ... variables with isInput=true/isOutput=true ... -->
</Flow>
```

**Alternative: GenAiFunction Metadata (Advanced)**

For advanced users, you can deploy Apex actions via GenAiFunction metadata directly to the org, then associate them with agents through GenAiPlugin (topics). This bypasses Agent Script but requires manual metadata management:

```xml
<!-- GenAiFunction structure -->
<GenAiFunction xmlns="http://soap.sforce.com/2006/04/metadata">
    <invocationTarget>CaseCreationService</invocationTarget>
    <invocationTargetType>apex</invocationTargetType>
    <!-- ... -->
</GenAiFunction>
```

This approach is NOT recommended for Agent Script-based agents.

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- **Agent purpose**: What job should this agent do?
- **Topics needed**: What categories of actions? (e.g., FAQ, Order Management, Support)
- **Actions required**: Flow-based? Apex-based? External API?
- **Variables**: What state needs to be tracked?
- **System persona**: What tone/behavior should the agent have?

**Then**:
1. Check existing agents: `Glob: **/aiAuthoringBundles/**/*.agent`
2. Check for sfdx-project.json to confirm Salesforce project structure
3. Create TodoWrite tasks

### Phase 2: Template Selection / Design

**Select appropriate pattern** based on requirements:

| Pattern | Use When | Template |
|---------|----------|----------|
| Hello World | Learning / Minimal agent | `templates/agents/hello-world.agent` |
| Simple Q&A | Single topic, no actions | `templates/agents/simple-qa.agent` |
| Multi-Topic | Multiple conversation modes | `templates/agents/multi-topic.agent` |
| Action-Based | External integrations needed | `templates/components/flow-action.agent` |
| Error Handling | Critical operations | `templates/components/error-handling.agent` |
| Lifecycle Events | Before/after reasoning logic | `templates/patterns/lifecycle-events.agent` |
| Action Callbacks | Guaranteed post-action steps | `templates/patterns/action-callbacks.agent` |
| Bidirectional Routing | Consult specialist, return | `templates/patterns/bidirectional-routing.agent` |
| **Prompt Template Actions** | AI content generation | `templates/patterns/prompt-template-action.agent` |
| **Multi-Step Workflows** | Complex processes with progress | `templates/patterns/multi-step-workflow.agent` |
| **Procedural Instructions** | Conditional data loading | `templates/patterns/procedural-instructions.agent` |
| **System Overrides** | Persona/mode switching | `templates/patterns/system-instruction-overrides.agent` |

> **Production patterns**: For action invocation, Prompt Builder, flow design, and deployment lifecycle patterns validated in production, see [Battle-Tested Patterns](#battle-tested-patterns).

**Pattern Decision Guide**: See [patterns-and-practices.md](docs/patterns-and-practices.md) for detailed decision tree.

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/templates/[path]`
2. **Project folder**: `[project-root]/sf-ai-agentforce/templates/[path]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/templates/agents/simple-qa.agent`

### Phase 3: Generation / Validation

**Create TWO files** at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml
```

**Required bundle-meta.xml content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

**Required .agent blocks**:
1. `system:` - Instructions and messages (MUST BE FIRST)
2. `config:` - Agent metadata (agent_name, agent_label, description, default_agent_user)
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent topic_selector:` - Entry point topic with label and description
6. `topic [name]:` - Additional topics (each with label and description)

> **Slot-filling and variable capture**: For actions that need deterministic input binding and output capture, use the `with`/`set` pattern from [Battle-Tested Patterns: Action Invocation](#action-invocation-doomprompting-fix). This works in GenAiPlannerBundle (production-validated).

**Validation Report Format** (6-Category Scoring 0-100):
```
Score: 85/100 Very Good
|- Structure & Syntax:     18/20 (90%)
|- Topic Design:           16/20 (80%)
|- Action Integration:     18/20 (90%)
|- Variable Management:    13/15 (87%)
|- Instructions Quality:   12/15 (80%)
|- Security & Guardrails:   8/10 (80%)

Issues:
[Syntax] Line 15: Inconsistent indentation (mixing tabs and spaces)
[Topic] Missing label for topic 'checkout'
All topic references valid
All variable references valid
```

### Phase 4: Deployment

**Step 1: Deploy Dependencies First (if using Flow/Apex actions)**
```bash
# Deploy Flows
sf project deploy start --metadata Flow --test-level NoTestRun --target-org [alias]

# Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --test-level NoTestRun --target-org [alias]
```

**Step 2: VALIDATE AGENT (MANDATORY)**

**CRITICAL: Always validate before deployment to catch syntax errors early!**

```bash
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
```

This validation:
- Checks Agent Script syntax and structure
- Verifies all topic references are valid
- Confirms variable declarations are correct
- Takes ~3 seconds (much faster than failed deployments)

**DO NOT proceed to Step 3 if validation fails!** Fix all errors first.

**Step 3: Deploy Agent Bundle**

**Option A: Deploy via Metadata API (Recommended - More Reliable)**
```bash
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

**Option B: Publish via Agent CLI (Beta - May fail with HTTP 404)**
```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

**CRITICAL: NEW Agents vs UPDATING Existing Agents**

| Operation | Use This Method | Reason |
|-----------|-----------------|--------|
| **Create NEW agent** | `sf agent publish authoring-bundle` | Required to create BotDefinition |
| **Update EXISTING agent** | `sf project deploy start` | More reliable, avoids HTTP 404 |

**HTTP 404 Error is BENIGN for BotDefinition, but BLOCKS UI Visibility**:
- The `sf agent publish authoring-bundle` command may fail with `ERROR_HTTP_404` during "Retrieve Metadata" step
- If "Publish Agent" step completed, the **BotDefinition WAS created** successfully
- However, the **AiAuthoringBundle metadata is NOT deployed** to the org
- This means **agents will be INVISIBLE in Agentforce Studio UI** even though they exist!
- **FIX**: After HTTP 404 error, run `sf project deploy start` to deploy the AiAuthoringBundle metadata:
  ```bash
  sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
  ```
- Verify deployment: `sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]`

**Workflow for NEW Agents** (with HTTP 404 fix):
```bash
# 1. Deploy dependencies first (flows, apex)
sf project deploy start --source-dir force-app/main/default/flows --target-org [alias]
sf project deploy start --source-dir force-app/main/default/classes --target-org [alias]

# 2. Publish agent (may show HTTP 404 but BotDefinition is still created)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# 3. CRITICAL: Deploy AiAuthoringBundle metadata (required for UI visibility!)
# This step is REQUIRED if you got HTTP 404 error above
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]

# 4. Verify agent was created AND metadata deployed
sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName = '[AgentName]'" --target-org [alias]
sf org list metadata --metadata-type AiAuthoringBundle --target-org [alias]

# 5. Activate (required to enable agent)
sf agent activate --api-name [AgentName] --target-org [alias]
```

**Workflow for UPDATING Existing Agents**:
```bash
# Use sf project deploy start (more reliable, no HTTP 404 issues)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
```

The deploy/publish command:
- Creates Bot, BotVersion, and GenAi metadata
- Deploys the AiAuthoringBundle to the org
- Makes agent visible in Agentforce Studio (after activation)

**Step 4: Verify Deployment**
```bash
# Open agent in Agentforce Studio to verify
sf org open agent --api-name [AgentName] --target-org [alias]

# Or query to confirm agent exists
sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName = '[AgentName]'" --target-org [alias]
```

**Step 5: Activate Agent (When Ready for Production)**
```bash
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Phase 5: Verification

```
Agent Complete: [AgentName]
  Type: Agentforce Agent | API: 65.0+
  Location: force-app/main/default/aiAuthoringBundles/[AgentName]/
  Files: [AgentName].agent, [AgentName].bundle-meta.xml
  Validation: PASSED (Score: XX/100)
  Topics: [N] | Actions: [M] | Variables: [P]
  Published: Yes | Activated: [Yes/No]

Next Steps:
  1. Open in Studio: sf org open agent --api-name [AgentName]
  2. Test in Agentforce Testing Center
  3. Activate when ready: sf agent activate
```

---

## Agent Script Syntax Reference (Essentials)

> **Complete Reference**: See [agent-script-reference.md](docs/agent-script-reference.md) for full documentation.

### Block Order (CRITICAL)

Blocks MUST appear in this order:
1. `system:` -> 2. `config:` -> 3. `variables:` -> 4. `language:` -> 5. `start_agent [name]:` -> 6. `topic [name]:`

### Minimal Working Example

```agentscript
system:
	instructions: "You are a helpful assistant. Be professional and friendly."
	messages:
		welcome: "Hello! How can I help you today?"
		error: "I apologize, but I encountered an issue."

config:
	agent_name: "My_Agent"
	default_agent_user: "user@example.com"
	agent_label: "My Agent"
	description: "A helpful assistant agent"

variables:
	EndUserId: linked string
		source: @MessagingSession.MessagingEndUserId
		description: "Messaging End User ID"
	RoutableId: linked string
		source: @MessagingSession.Id
		description: "Messaging Session ID"
	ContactId: linked string
		source: @MessagingEndUser.ContactId
		description: "Contact ID"

language:
	default_locale: "en_US"
	additional_locales: ""
	all_additional_locales: False

start_agent topic_selector:
	label: "Topic Selector"
	description: "Routes users to appropriate topics"

	reasoning:
		instructions: ->
			| Determine what the user needs.
		actions:
			go_help: @utils.transition to @topic.help

topic help:
	label: "Help"
	description: "Provides help to users"

	reasoning:
		instructions: ->
			| Answer the user's question helpfully.
```

### Quick Syntax Reference

| Block | Key Rules |
|-------|-----------|
| **system** | `instructions:` MUST be a single quoted string (NO pipes `\|`) |
| **config** | Use `agent_name` or `developer_name` (both work). `default_agent_user` must be valid org user. |
| **variables** | Use `number` not `integer/long`. Use `timestamp` not `datetime`. Use `list[type]` not `list<type>`. Linked vars don't support lists/objects. |
| **language** | Required block - include even if only `en_US`. |
| **topics** | Each topic MUST have both `label:` and `description:`. |
| **instructions** | Use `instructions: ->` syntax (space before arrow). |

### AiAuthoringBundle Limitations (Tested Dec 2025)

| Feature | Status | Workaround |
|---------|--------|------------|
| `run` keyword | NOT Supported | Define actions in topic, LLM chooses when to call |
| `with`/`set` in `reasoning.actions` | NOT Supported | Define actions in topic `actions:` block only |
| `{!@actions.x}` | NOT Supported | Define actions with descriptions, LLM auto-selects |
| `@utils.setVariables` | NOT Supported | Use `set @variables.x = ...` in instructions |
| `@utils.escalate with reason` | NOT Supported | Use basic `@utils.escalate` with `description:` |
| `integer`, `long` types | NOT Supported | Use `number` type |
| `list<type>` syntax | NOT Supported | Use `list[type]` syntax |
| Nested if statements | NOT Supported | Use flat `and` conditionals |
| `filter_from_agent` | NOT Supported | Use `available when @var == val` syntax |

### CRITICAL: Flow Actions in AiAuthoringBundle (Tested Dec 2025)

**Flow actions (`flow://`) DO work in AiAuthoringBundle**, but require a specific pattern:

```agentscript
# CORRECT PATTERN FOR AiAuthoringBundle
# 1. Define actions in topic blocks (NOT start_agent)
# 2. Use simple action definition (no with/set in reasoning.actions)
# 3. Let the LLM decide when to call the action based on description

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes users to topics"

   # start_agent should ONLY have @utils.transition actions
   reasoning:
      instructions: ->
         | Route the user to the appropriate topic.
      actions:
         go_to_orders: @utils.transition to @topic.order_lookup

topic order_lookup:
   label: "Order Lookup"
   description: "Looks up order information"

   # Define flow actions in the topic's actions: block
   actions:
      get_order:
         description: "Retrieves order details by order number"
         inputs:
            inp_OrderNumber: string
               description: "The order number to look up"
         outputs:
            out_OrderStatus: string
               description: "Status of the order"
            out_OrderTotal: number
               description: "Total amount of the order"
         target: "flow://Get_Order_Details"

   # Simple reasoning - no with/set in reasoning.actions
   reasoning:
      instructions: ->
         | Help the user look up their order.
         | Ask for the order number if not provided.
         | Use the get_order action to retrieve details.
      actions:
         back_to_menu: @utils.transition to @topic.topic_selector
```

**WRONG PATTERN (causes "Internal Error" at publish):**

```agentscript
# DO NOT put flow actions in start_agent
start_agent topic_selector:
   actions:
      my_flow_action:    # WRONG - actions in start_agent fail
         target: "flow://..."

# DO NOT use with/set in reasoning.actions FOR AiAuthoringBundle
# with/set WORKS in GenAiPlannerBundle (production-validated pattern)
reasoning:
   actions:
      lookup: @actions.get_order
         with inp_OrderNumber=...              # AiAuthoringBundle: Internal Error
         set @variables.status = @outputs...   # AiAuthoringBundle: Internal Error
         # GenAiPlannerBundle: works correctly (see action-invocation-patterns.md)
```

**Key Requirements:**
1. **Flow actions in `topic` blocks only** - NOT in `start_agent`
2. **`start_agent` uses only `@utils.transition`** - for routing to topics
3. **No `with`/`set` in `reasoning.actions`** for AiAuthoringBundle - just define actions, LLM auto-calls
4. **Input/output names must match Flow exactly** - Case-sensitive!

### Connection Block (for Escalation)

```agentscript
connection messaging:
   outbound_route_type: "OmniChannelFlow"    # MUST be this value!
   outbound_route_name: "Support_Queue_Flow" # Must exist in org
   escalation_message: "Transferring you..."  # REQUIRED field
```

### Resource Access

| Resource | Syntax |
|----------|--------|
| Variables | `@variables.name` |
| Actions | `@actions.name` |
| Topics | `@topic.name` |
| Outputs | `@outputs.field` |
| Utilities | `@utils.transition to`, `@utils.escalate` |

### Action Invocation (Simplified)

```agentscript
# Define action in topic
actions:
   get_account:
      description: "Gets account info"
      inputs:
         account_id: string
            description: "Account ID"
      outputs:
         account_name: string
            description: "Account name"
      target: "flow://Get_Account_Info"

# Invoke in reasoning (LLM chooses when to call)
reasoning:
   instructions: ->
      | Help user look up accounts.
   actions:
      lookup: @actions.get_account
         with account_id=...    # Slot filling
         set @variables.name = @outputs.account_name
```

---

## Scoring System (100 Points)

### Structure & Syntax (20 points)
- Valid Agent Script syntax (-10 if parsing fails)
- Consistent indentation (no mixing tabs/spaces) (-3 per violation)
- Required blocks present (system, config, start_agent, language) (-5 each missing)
- Uses `agent_name` or `developer_name` (both valid)
- File extension is `.agent` (-5 if wrong)

### Topic Design (20 points)
- All topics have `label:` and `description:` (-3 each missing)
- Logical topic transitions (-3 per orphaned topic)
- Entry point topic exists (start_agent) (-5 if missing)
- Topic names follow snake_case (-2 each violation)

### Action Integration (20 points)
- Valid target format (`flow://` supported, `apex://` NOT supported) (-5 each invalid)
- All inputs have descriptions (-2 each missing)
- All outputs captured appropriately (-2 each unused)
- Action callbacks don't exceed one level (-5 if nested)
- No reserved words used as input/output names (-3 each violation)

### Variable Management (15 points)
- All variables have descriptions (-2 each missing)
- Required linked variables present (EndUserId, RoutableId, ContactId) (-3 each missing)
- Appropriate types used (-2 each mismatch)
- Variable names follow snake_case (-1 each violation)

### Instructions Quality (15 points)
- Uses `instructions: ->` syntax (space before arrow) (-5 if wrong)
- Clear, specific reasoning instructions (-3 if vague)
- Edge cases handled (-3 if missing)
- Template expressions valid (-3 each invalid)

### Security & Guardrails (10 points)
- System-level guardrails present (-5 if missing)
- Sensitive operations have validation (-3 if missing)
- Error messages don't expose internals (-2 each violation)

### Scoring Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Deploy with confidence |
| 80-89 | Very Good | Minor improvements suggested |
| 70-79 | Good | Review before deploy |
| 60-69 | Needs Work | Address issues before deploy |
| <60 | Critical | **Block deployment** |

---

## Cross-Skill Integration

### MANDATORY Delegations

| Requirement | Skill/Agent | Why | Never Do |
|-------------|-------------|-----|----------|
| **Flow Creation** | `Skill(skill="sf-flow")` | 110-point validation, proper XML ordering, prevents errors | Manually write Flow XML |
| **ALL Deployments** | `Skill(skill="sf-deploy")` | Centralized deployment | Direct CLI |

### Flow Integration Workflow

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `Skill(skill="sf-flow")` -> Create Autolaunched Flow | Build Flow with inputs/outputs |
| 2 | `Skill(skill="sf-deploy")` -> Deploy Flow | Validate and deploy Flow |
| 3 | Use `target: "flow://FlowApiName"` in Agent Script | Reference Flow as action |
| 4 | `Skill(skill="sf-deploy")` -> Publish agent | Deploy agent |

### Apex Integration (via Flow Wrapper)

**`apex://` targets DON'T work in Agent Script. Use Flow Wrapper pattern.**

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `Skill(skill="sf-apex")` -> Create `@InvocableMethod` class | Build callable Apex |
| 2 | Deploy Apex via sf-deploy | Get Apex in org |
| 3 | `Skill(skill="sf-flow")` -> Create wrapper Flow calling Apex | Bridge to Agent Script |
| 4 | Deploy Flow + Publish agent via sf-deploy | Complete deployment |
| 5 | Use `target: "flow://WrapperFlowName"` in Agent Script | Reference wrapper Flow |

| Direction | Pattern | Supported |
|-----------|---------|-----------|
| sf-agentforce -> sf-flow | Create Flow-based actions | Full |
| sf-agentforce -> sf-apex | Create Apex via Flow wrapper | Via Flow |
| sf-agentforce -> sf-deploy | Deploy agent metadata | Full |
| sf-agentforce -> sf-metadata | Query object structure | Full |
| sf-agentforce -> sf-integration | External API actions | Via Flow |

---

## Agent Actions (Summary)

> **Complete Reference**: See [actions-reference.md](docs/actions-reference.md) for detailed implementation of all action types.

### Action Target Summary

| Action Type | Target Syntax | Recommended |
|-------------|---------------|-------------|
| **Flow** (native) | `flow://FlowAPIName` | Best choice |
| **Apex** (via Flow) | `flow://ApexWrapperFlow` | Recommended |
| **External API** | `flow://HttpCalloutFlow` | Via sf-integration |
| **Prompt Template** | Deploy via metadata | For LLM tasks |

### Key Requirements for Flow Actions

- Flow must be **Autolaunched Flow** (not Screen Flow)
- Variables marked "Available for input/output"
- Variable names **must match** Agent Script input/output names
- Flow must be deployed **BEFORE** agent publish

### Cross-Skill Integration

| Need | Skill | Example |
|------|-------|---------|
| External API | sf-integration | "Create Named Credential for agent API action" |
| Flow wrapper | sf-flow | "Create HTTP Callout Flow for agent" |
| Apex logic | sf-apex | "Create Apex @InvocableMethod for case creation" |
| Deployment | sf-deploy | `Skill(skill="sf-deploy", args="Deploy to [org]")` |

---

## Common Patterns

### Pattern 1: Simple FAQ Agent
```agentscript
system:
   instructions: "You are a helpful FAQ assistant. Answer questions concisely. Never share confidential information."
   messages:
      welcome: "Hello! I can answer your questions."
      error: "Sorry, I encountered an issue."

config:
   agent_name: "FAQ_Agent"
   default_agent_user: "agent.user@company.com"
   agent_label: "FAQ Agent"
   description: "Answers frequently asked questions"

variables:
   EndUserId: linked string
      source: @MessagingSession.MessagingEndUserId
      description: "Messaging End User ID"
   RoutableId: linked string
      source: @MessagingSession.Id
      description: "Messaging Session ID"
   ContactId: linked string
      source: @MessagingEndUser.ContactId
      description: "Contact ID"

language:
   default_locale: "en_US"
   additional_locales: ""
   all_additional_locales: False

start_agent topic_selector:
   label: "Topic Selector"
   description: "Routes to FAQ handling"

   reasoning:
      instructions: ->
         | Listen to the user's question.
         | Provide a helpful, accurate response.
```

### Pattern 2: Flow Action with Variable Binding
```agentscript
topic account_lookup:
   label: "Account Lookup"
   description: "Looks up account information using Flow"

   actions:
      get_account:
         description: "Retrieves account information by ID"
         inputs:
            inp_AccountId: string
               description: "The Salesforce Account ID"
         outputs:
            out_AccountName: string
               description: "Account name"
            out_Industry: string
               description: "Account industry"
            out_IsFound: boolean
               description: "Whether account was found"
         target: "flow://Get_Account_Info"

   reasoning:
      instructions: ->
         | Ask for the Account ID if not provided.
         | Use the get_account action to look up the account.
         |
         | if @variables.account_found == True:
         |     | Here is the account: {!@variables.account_name}
         | else:
         |     | Account not found. Please check the ID.
      actions:
         lookup: @actions.get_account
            with inp_AccountId=...
            set @variables.account_name = @outputs.out_AccountName
            set @variables.account_found = @outputs.out_IsFound
         back: @utils.transition to @topic.topic_selector
```

### Pattern 3: Conditional Transitions
```agentscript
topic order_processing:
   label: "Order Processing"
   description: "Processes customer orders"

   reasoning:
      instructions: ->
         if @variables.cart_total <= 0:
            | Your cart is empty. Add items before checkout.
         if @variables.cart_total > 10000:
            set @variables.needs_approval = True
            | Large orders require approval.
      actions:
         process: @actions.create_order
            with items=@variables.cart_items
            available when @variables.cart_total > 0
            available when @variables.needs_approval == False
         get_approval: @utils.transition to @topic.approval
            available when @variables.needs_approval == True
```

### Pattern 4: Prompt Builder Action (Generative AI)
```agentscript
topic meeting_prep:
   label: "Meeting Prep"
   description: "Generate AI-powered meeting briefings"

   actions:
      get_account_details:
         description: "Retrieves account details by name or ID"
         inputs:
            inp_AccountNameOrId: string
               description: "Account name or ID"
         outputs:
            out_AccountName: string
            out_AccountId: string
            out_IsFound: boolean
         target: "flow://Agent_Get_Account_Details"

      generate_meeting_prep:
         description: "Generates a meeting prep briefing using AI"
         inputs:
            "Input:Account": object
               complex_data_type_name: "lightning__recordInfoType"
               description: "Account record for the briefing"
         outputs:
            promptResponse: string
               description: "The generated briefing"
         target: "generatePromptResponse://Agent_Meeting_Prep"

   reasoning:
      instructions: ->
         | Generate a meeting prep briefing.
         | First look up the account if needed, then generate the briefing.
      actions:
         lookup: @actions.get_account_details
            with inp_AccountNameOrId=...
            set @variables.current_account_name = @outputs.out_AccountName
            set @variables.current_account_id = @outputs.out_AccountId
         prep: @actions.generate_meeting_prep
            with "Input:Account"=@variables.current_account_id
```

---

## SF CLI Agent Commands Reference

Complete CLI reference for Agentforce agent DevOps. For detailed guides, see:
- [cli-guide.md](docs/cli-guide.md) - Full CLI command reference with preview setup

### Command Quick Reference

| Command | Purpose |
|---------|---------|
| `sf agent validate authoring-bundle` | Validate Agent Script syntax |
| `sf agent publish authoring-bundle` | Publish authoring bundle |
| `sf agent preview` | Preview agent (simulated/live) |
| `sf agent activate` | Activate published agent |
| `sf agent deactivate` | Deactivate agent for changes |
| `sf org open -f <agent-file>` | Open in Agentforce Builder |
| `sf project retrieve start --metadata Agent:Name` | Sync agent from org |
| `sf project deploy start --metadata Agent:Name` | Deploy agent to org |

> Commands are in beta. Use `--help` to verify flags. See [cli-guide.md](docs/cli-guide.md).

### Authoring Commands

```bash
# Validate Agent Script syntax (RECOMMENDED before publish)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, AiAuthoringBundle metadata)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

> **No `--source-dir` or `--async` flags!** Commands auto-find bundles in DX project.

### Preview Commands

```bash
# Preview with agent selection prompt
sf agent preview --target-org [alias]

# Preview specific agent (simulated mode - default)
sf agent preview --api-name [AgentName] --target-org [alias]

# Preview in live mode (requires connected app)
sf agent preview --api-name [AgentName] --use-live-actions --client-app [AppName] --target-org [alias]

# Preview with debug output saved
sf agent preview --api-name [AgentName] --output-dir ./logs --apex-debug --target-org [alias]
```

**Preview Modes:**
| Mode | Flag | Description |
|------|------|-------------|
| Simulated | (default) | LLM simulates action responses - safe for testing |
| Live | `--use-live-actions` | Uses actual Apex/Flows in org - requires connected app |

**See [cli-guide.md](docs/cli-guide.md)** for connected app setup instructions.

### Lifecycle Commands

```bash
# Activate agent (makes available to users)
sf agent activate --api-name [AgentName] --target-org [alias]

# Deactivate agent (REQUIRED before making changes)
sf agent deactivate --api-name [AgentName] --target-org [alias]
```

**Deactivation Required:** You MUST deactivate an agent before modifying topics, actions, or system instructions. After changes, re-publish and re-activate.

### Sync Commands (Agent Pseudo Metadata Type)

The `Agent` pseudo metadata type retrieves/deploys all agent components:

```bash
# Retrieve agent + dependencies from org
sf project retrieve start --metadata Agent:[AgentName] --target-org [alias]

# Deploy agent metadata to org
sf project deploy start --metadata Agent:[AgentName] --target-org [alias]
```

**What Gets Synced:** Bot, BotVersion, GenAiPlannerBundle, GenAiPlugin, GenAiFunction

### Management Commands

```bash
# Open agent in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Update plugin to latest (if commands missing)
sf plugins install @salesforce/plugin-agent@latest
```

### Full Deployment Workflow

```bash
# 1. Deploy Apex classes (if any)
sf project deploy start --metadata ApexClass --target-org [alias]

# 2. Deploy Flows
sf project deploy start --metadata Flow --target-org [alias]

# 3. VALIDATE Agent Script (MANDATORY - DO NOT SKIP!)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
# If validation fails, fix errors before proceeding!

# 4. Deploy/Publish agent (choose one method)
# Option A: Metadata API (more reliable)
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/[AgentName] --target-org [alias]
# Option B: Agent CLI (beta - may fail with HTTP 404)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# 5. Verify deployment
sf org open agent --api-name [AgentName] --target-org [alias]

# 6. Preview (simulated mode)
sf agent preview --api-name [AgentName] --target-org [alias]

# 7. Activate (when ready for production)
sf agent activate --api-name [AgentName] --target-org [alias]

# 8. Preview (live mode - optional, requires connected app)
sf agent preview --api-name [AgentName] --use-live-actions --client-app [App] --target-org [alias]
```

**IMPORTANT**:
- Always run `sf agent validate authoring-bundle` BEFORE deployment to catch errors early (~3 seconds vs minutes for failed deploys)
- If `sf agent publish` fails with HTTP 404, use `sf project deploy start --source-dir` instead - both work for AiAuthoringBundles

---

## Agent Metadata Types Reference

When working with agent metadata directly, these are the component types:

| Metadata Type | Description | Example API Name |
|---------------|-------------|------------------|
| `Bot` | Top-level chatbot definition | `Customer_Support_Agent` |
| `BotVersion` | Version configuration | `Customer_Support_Agent.v1` |
| `GenAiPlannerBundle` | Reasoning engine (LLM config) | `Customer_Support_Agent_Planner` |
| `GenAiPlugin` | Topic definition | `Order_Management_Plugin` |
| `GenAiFunction` | Action definition | `Get_Order_Status_Function` |

### Agent Pseudo Metadata Type

The `Agent` pseudo type is a convenience wrapper that retrieves/deploys all related components:

```bash
# Retrieves: Bot + BotVersion + GenAiPlannerBundle + GenAiPlugin + GenAiFunction
sf project retrieve start --metadata Agent:My_Agent --target-org [alias]
```

### Retrieving Specific Components

```bash
# Retrieve just the bot definition
sf project retrieve start --metadata Bot:[AgentName] --target-org [alias]

# Retrieve just the planner bundle
sf project retrieve start --metadata GenAiPlannerBundle:[BundleName] --target-org [alias]

# Retrieve all plugins (topics)
sf project retrieve start --metadata GenAiPlugin --target-org [alias]

# Retrieve all functions (actions)
sf project retrieve start --metadata GenAiFunction --target-org [alias]
```

### Metadata Relationships

```
Bot (Agent Definition)
|- BotVersion (Version Config)
    |- GenAiPlannerBundle (Reasoning Engine)
        |- GenAiPlugin (Topic 1)
        |   |- GenAiFunction (Action 1)
        |   |- GenAiFunction (Action 2)
        |- GenAiPlugin (Topic 2)
            |- GenAiFunction (Action 3)
```

---

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py <file_path>
```

**Scoring**: 100 points / 6 categories. Minimum 60 (60%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern `*.agent`.

---

## Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| File Extension | `.agentscript` not recognized | Use `.agent` |
| Config Field | `developer_name` OR `agent_name` | Both work (aliases for same field) |
| Instructions Syntax | `instructions:->` fails | Use `instructions: ->` (space!) |
| Topic Fields | Missing `label` fails deploy | Add both `label` and `description` |
| Linked Variables | Missing context variables | Add EndUserId, RoutableId, ContactId |
| Language Block | Missing causes deploy failure | Add `language:` block |
| Bundle XML | Missing causes deploy failure | Create `.bundle-meta.xml` file |
| **Indentation Consistency** | **Mixing tabs/spaces causes parse errors** | **Use TABS consistently (recommended) - easier for manual editing** |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| **Validation Required** | **Skipping validation causes late-stage failures** | **ALWAYS run `sf agent validate authoring-bundle` BEFORE deploy** |
| Deploy Command | `sf agent publish` may fail with HTTP 404 | Use `sf project deploy start --source-dir` as reliable alternative |
| **HTTP 404 UI Visibility** | **HTTP 404 creates Bot but NOT AiAuthoringBundle** | **Run `sf project deploy start` after HTTP 404 to deploy metadata** |
| **System Instructions** | Pipe `\|` syntax fails in system: block | Use single quoted string only |
| **Escalate Description** | Inline description fails | Put `description:` on separate indented line |
| **Agent User** | Invalid user causes "Internal Error" | Use valid org user with proper permissions |
| **Reserved Words** | `description` as input fails | Use alternative names (e.g., `case_description`) |
| **Flow Variable Names** | **Mismatched names cause "Internal Error"** | **Agent Script input/output names MUST match Flow variable API names exactly** |
| **Action Location** | Top-level actions fail | Define actions inside topics |
| **Flow Targets** | `flow://` works in both deployment methods | Ensure Flow deployed before agent publish, names match exactly |
| **AiAuthoringBundle Limitations** | `with`/`set` in `reasoning.actions` NOT supported in AiAuthoringBundle | Use GenAiPlannerBundle for `with`/`set` slot-filling (production-validated). For AiAuthoringBundle: define actions in topic `actions:` block, let LLM auto-call |
| **start_agent Actions** | Flow actions in `start_agent` fail in AiAuthoringBundle | Use `start_agent` only for `@utils.transition`, put flow actions in `topic` blocks |
| **`run` Keyword** | Action chaining syntax | Use `run @actions.x` for callbacks (GenAiPlannerBundle only) |
| **Lifecycle Blocks** | before/after_reasoning available | Use bare `transition to` (not `@utils.transition`) in lifecycle blocks |
| **`@utils.set`/`setVariables`** | "Unknown utils declaration type" error | Use `set` keyword in instructions instead (AiAuthoringBundle) |
| **`escalate` Action Name** | "Unexpected 'escalate'" error | `escalate` is reserved - use `go_to_escalate` or `transfer_to_human` |
| **Connection `outbound_route_type`** | Invalid values cause validation errors | MUST be `"OmniChannelFlow"` - not `queue`/`skill`/`agent` |
| **Connection `escalation_message`** | Missing field causes parse errors | REQUIRED when other connection fields are present |
| **Connection OmniChannelFlow** | HTTP 404 at "Publish Agent" step | Referenced flow must exist in org or BotDefinition NOT created |
| **Nested if statements** | Parse errors ("Missing required element", "Unexpected 'else'") | Use flat conditionals with `and` operators instead |
| **N-ary boolean operations** | Need 3+ conditions | Fully supported: `@variables.a and @variables.b and @variables.c` works |
| **Topic delegation vs transition** | `@utils.transition` = permanent; `@topic.*` = can return | See [agent-script-reference.md](docs/agent-script-reference.md#topic-delegation-vs-transition) |
| **Math operators (`+`, `-`)** | Works in set and conditions | `set @variables.x = @variables.x + 1` is valid |
| **Action attributes** | `require_user_confirmation`, `include_in_progress_indicator`, `label` | Work in AiAuthoringBundle (validated Dec 2025) |

---

## Required Files Checklist

Before deployment, ensure you have:

- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent`
- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml`
- [ ] `sfdx-project.json` in project root
- [ ] Valid `default_agent_user` in config block
- [ ] All linked variables (EndUserId, RoutableId, ContactId)
- [ ] Language block present
- [ ] **Validation passed**: `sf agent validate authoring-bundle --api-name [AgentName]` returns 0 errors
- [ ] All topics have `label:` and `description:`
- [ ] No reserved words used as input/output names
- [ ] Flow/Apex dependencies deployed to org first

---

## LSP Integration (Real-Time Validation)

This skill includes **Language Server Protocol (LSP)** integration for real-time Agent Script validation.

### Prerequisites

1. **VS Code with Agent Script Extension** (Required)
   - Open VS Code -> Extensions (Cmd+Shift+X)
   - Search: "Agent Script" by Salesforce
   - Install the extension

2. **Node.js 18+** (Required)
   - Check: `node --version`
   - Install: `brew install node` (macOS)

### Features

When you edit `.agent` files, the LSP automatically provides:

| Feature | Description |
|---------|-------------|
| Syntax Validation | Real-time error detection |
| Auto-Fix Loop | Claude automatically fixes errors (max 3 attempts) |
| Fast Feedback | ~50ms response time |

### How It Works

```
1. Claude writes/edits .agent file
       |
       v
2. PostToolUse hook triggers
       |
       v
3. LSP validates syntax
       |
       v
4. If errors -> Output to Claude -> Auto-fix
   If valid -> Silent success
```

### Troubleshooting

**"LSP server not found"**
- Install VS Code Agent Script extension
- Verify: `ls ~/.vscode/extensions/salesforce.agent-script-*`

**"Node.js not found"**
- Install Node.js 18+: `brew install node`

**Validation not triggering**
- Ensure hooks are enabled in Claude Code settings
- Check: `ls ~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/hooks/`

---

## Reference & Dependencies

**Docs**: `docs/` folder (in sf-ai-agentforce) - best-practices, agent-script-syntax
- **Path**: `~/.claude/plugins/marketplaces/sf-skills/sf-ai-agentforce/docs/`

**Dependencies**: sf-deploy (optional) for additional deployment options. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 65.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See LICENSE file in sf-ai-agentforce folder.
Copyright (c) 2024-2025 Jag Valaiyapathy
