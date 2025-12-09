---
name: sf-ai-agentforce
description: Creates Agentforce agents using Agent Script syntax. Generates complete agents with topics, actions, and variables. 100-point scoring across 6 categories. API v64+ required.
---

# sf-ai-agentforce: Agentforce Agent Creation with Agent Script

Expert Agentforce developer specializing in Agent Script syntax, topic design, and action integration. Generate production-ready agents that leverage LLM reasoning with deterministic business logic.

## Core Responsibilities

1. **Agent Creation**: Generate complete Agentforce agents using Agent Script
2. **Topic Management**: Create and configure agent topics with proper transitions
3. **Action Integration**: Connect actions to Flows, Apex, or external services
4. **Validation & Scoring**: Score agents against best practices (0-100 points)
5. **Deployment**: Publish agents using `sf agent publish authoring-bundle`

## ⚠️ CRITICAL: API Version Requirement

**Agent Script requires API v64+ (Summer '25 or later)**

Before creating agents, verify:
```bash
sf org display --target-org [alias] --json | jq '.result.apiVersion'
```

If API version < 64, Agent Script features won't be available.

---

## ⚠️ CRITICAL: File Extension

**Agent Script files use `.agent` extension (NOT `.agentscript`)**

Files must be placed at:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent
```

Each bundle also requires a metadata XML file:
```
force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml
```

---

## ⚠️ CRITICAL: Indentation Rules

**Agent Script uses 4-SPACE indentation (NOT tabs, NOT 3 spaces)**

```agentscript
# ✅ CORRECT - 4 spaces
config:
    developer_name: "My_Agent"
    description: "My agent description"

# ❌ WRONG - 3 spaces (common mistake!)
config:
   developer_name: "My_Agent"
```

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
| Simple Q&A | Single topic, no actions | `templates/agent/simple-qa.agent` |
| Multi-Topic | Multiple conversation modes | `templates/agent/multi-topic.agent` |
| Action-Based | External integrations needed | `templates/actions/flow-action.agent` |
| Error Handling | Critical operations | `templates/topics/error-handling.agent` |

Load via: `Read: ../../templates/[path]` (relative to SKILL.md location)

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
2. `config:` - Agent metadata (developer_name, agent_label, description, default_agent_user)
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent topic_selector:` - Entry point topic with label and description
6. `topic [name]:` - Additional topics (each with label and description)

**Validation Report Format** (6-Category Scoring 0-100):
```
Score: 85/100 ⭐⭐⭐⭐ Very Good
├─ Structure & Syntax:     18/20 (90%)
├─ Topic Design:           16/20 (80%)
├─ Action Integration:     18/20 (90%)
├─ Variable Management:    13/15 (87%)
├─ Instructions Quality:   12/15 (80%)
└─ Security & Guardrails:   8/10 (80%)

Issues:
⚠️ [Syntax] Line 15: Use 4-space indentation, found 3 spaces
⚠️ [Topic] Missing label for topic 'checkout'
✓ All topic references valid
✓ All variable references valid
```

### Phase 4: Deployment

**Step 1: Validate (Optional but Recommended)**
```bash
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]
```

**Step 2: Publish Agent**
```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

This command:
- Validates the Agent Script syntax
- Creates Bot, BotVersion, and GenAi metadata
- Retrieves generated metadata back to project
- Deploys the AiAuthoringBundle to the org

**Step 3: Open in Agentforce Studio (Optional)**
```bash
sf org open agent --api-name [AgentName] --target-org [alias]
```

**Step 4: Activate Agent (Optional)**
```bash
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Phase 5: Verification

```
✓ Agent Complete: [AgentName]
  Type: Agentforce Agent | API: 64.0+
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

## Agent Script Syntax Reference

### Complete Working Example

```agentscript
system:
    instructions: "You are a helpful assistant for Acme Corporation. Be professional and friendly. Never share confidential information."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "I apologize, but I encountered an issue. Please try again."

config:
    developer_name: "My_Agent"
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
    user_query: mutable string
        description: "The user's current question"

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
            | Route to the appropriate topic.
        actions:
            go_to_help: @utils.transition to @topic.help
            go_to_farewell: @utils.transition to @topic.farewell

topic help:
    label: "Help"
    description: "Provides help to users"

    reasoning:
        instructions: ->
            | Answer the user's question helpfully.
            | If you cannot help, offer alternatives.
        actions:
            back_to_selector: @utils.transition to @topic.topic_selector

topic farewell:
    label: "Farewell"
    description: "Ends the conversation gracefully"

    reasoning:
        instructions: ->
            | Thank the user for reaching out.
            | Wish them a great day.
```

### Block Order (CRITICAL)

The blocks MUST appear in this order:
1. `system:` (instructions and messages)
2. `config:` (developer_name, default_agent_user, agent_label, description)
3. `variables:` (linked variables first, then mutable variables)
4. `language:` (locale settings)
5. `start_agent [name]:` (entry point topic)
6. `topic [name]:` (additional topics)

### Config Block

```agentscript
config:
    developer_name: "Agent_API_Name"
    default_agent_user: "user@org.salesforce.com"
    agent_label: "Human Readable Name"
    description: "What this agent does"
```

| Field | Required | Description |
|-------|----------|-------------|
| `developer_name` | Yes | API name (PascalCase with underscores) |
| `default_agent_user` | Yes | Username for agent execution context |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

**IMPORTANT**: Use `developer_name`, NOT `agent_name`!

### System Block

```agentscript
system:
    instructions: "Global instructions for the agent. Be helpful and professional."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "I'm sorry, something went wrong. Please try again."
```

**Note**: System instructions can be a single string (for short instructions) or use `|` multiline format.

### Variables Block

**Linked Variables** (connect to Salesforce data):
```agentscript
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
```

**Mutable Variables** (agent state):
```agentscript
variables:
    user_name: mutable string
        description: "User's name"
    order_count: mutable number
        description: "Number of items in cart"
    is_verified: mutable boolean
        description: "Whether identity is verified"
```

### Language Block

```agentscript
language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False
```

### Topic Blocks

**Entry point topic** (required):
```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes users to appropriate topics"

    reasoning:
        instructions: ->
            | Determine what the user needs.
            | Route to the appropriate topic.
        actions:
            go_to_orders: @utils.transition to @topic.orders
            go_to_support: @utils.transition to @topic.support
```

**Additional topics**:
```agentscript
topic orders:
    label: "Order Management"
    description: "Handles order inquiries and processing"

    reasoning:
        instructions: ->
            | Help the user with their order.
            | Provide status updates and assistance.
        actions:
            back_to_menu: @utils.transition to @topic.topic_selector
```

**IMPORTANT**: Each topic MUST have both `label:` and `description:`!

### Resource Access (@ prefix)

| Resource | Syntax | Example |
|----------|--------|---------|
| Variables | `@variables.name` | `@variables.user_name` |
| Actions | `@actions.name` | `@actions.get_weather` |
| Topics | `@topic.name` | `@topic.checkout` |
| Outputs | `@outputs.field` | `@outputs.temperature` |
| Utilities | `@utils.transition` | `@utils.transition to @topic.X` |
| Utilities | `@utils.escalate` | `@utils.escalate` |

### Instructions Syntax

**CRITICAL**: Use `instructions: ->` (space before arrow), NOT `instructions:->`

**Procedural mode** (with logic):
```agentscript
reasoning:
    instructions: ->
        | Determine user intent.
        | Provide helpful response.
        | If unclear, ask clarifying questions.
```

**Multiline instructions** (prompt-only):
```agentscript
system:
    instructions:
        | You are a helpful assistant.
        | Be professional and courteous.
        | Never share confidential information.
```

### Action Definitions

```agentscript
# Flow-based action
get_account:
    description: "Retrieves account information"
    inputs:
        account_id: string
            description: "Salesforce Account ID"
    outputs:
        account_name: string
            description: "Account name"
        industry: string
            description: "Account industry"
    target: "flow://Get_Account_Info"

# Apex-based action
create_case:
    description: "Creates a support case"
    inputs:
        subject: string
            description: "Case subject"
        description: string
            description: "Case description"
    outputs:
        case_id: string
            description: "Created case ID"
    target: "apex://CaseService.createCase"
```

### Action Invocation

```agentscript
reasoning:
    actions:
        # LLM fills inputs (...)
        lookup: @actions.get_account
            with account_id=...
            set @variables.account_name = @outputs.account_name

        # Fixed value
        default_lookup: @actions.get_account
            with account_id="001XX000003NGFQ"

        # Variable binding
        bound_lookup: @actions.get_account
            with account_id=@variables.current_account_id
```

### Action Callbacks (Chaining)

```agentscript
process_order: @actions.create_order
    with items=...
    set @variables.order_id = @outputs.order_id
    run @actions.send_confirmation
        with order_id=@variables.order_id
    run @actions.update_inventory
        with order_id=@variables.order_id
```

**Note**: Only one level of nesting - cannot nest `run` inside `run`.

### Topic Transitions

```agentscript
# Simple transition
go_checkout: @utils.transition to @topic.checkout

# Conditional transition
go_checkout: @utils.transition to @topic.checkout
    available when @variables.cart_has_items == True
```

### Escalation to Human

```agentscript
topic escalation:
    label: "Escalation"
    description: "Handles requests to transfer to a live human agent"

    reasoning:
        instructions: ->
            | If a user explicitly asks to transfer, escalate.
            | Acknowledge and apologize for any inconvenience.
        actions:
            escalate_to_human: @utils.escalate
                description: "Escalate to a human agent"
```

### Conditional Logic

```agentscript
instructions: ->
    if @variables.amount > 10000:
        set @variables.needs_approval = True
        | This amount requires manager approval.
    else:
        set @variables.needs_approval = False
        | Processing your request.

    if @variables.user_name is None:
        | I don't have your name yet. What should I call you?
```

### Operators

| Type | Operators |
|------|-----------|
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Math | `+`, `-` |
| Null check | `is None`, `is not None` |

### Template Expressions

Use `{!...}` for variable interpolation in instructions:

```agentscript
instructions: ->
    | Hello {!@variables.user_name}!
    | Your account balance is {!@variables.balance}.
```

---

## Scoring System (100 Points)

### Structure & Syntax (20 points)
- Valid Agent Script syntax (-10 if parsing fails)
- Correct 4-space indentation (-3 per violation)
- Required blocks present (system, config, start_agent, language) (-5 each missing)
- Uses `developer_name` not `agent_name` (-5 if wrong)
- File extension is `.agent` (-5 if wrong)

### Topic Design (20 points)
- All topics have `label:` and `description:` (-3 each missing)
- Logical topic transitions (-3 per orphaned topic)
- Entry point topic exists (start_agent) (-5 if missing)
- Topic names follow snake_case (-2 each violation)

### Action Integration (20 points)
- Valid target format (flow:// or apex://) (-5 each invalid)
- All inputs have descriptions (-2 each missing)
- All outputs captured appropriately (-2 each unused)
- Action callbacks don't exceed one level (-5 if nested)

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
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Deploy with confidence |
| 80-89 | ⭐⭐⭐⭐ Very Good | Minor improvements suggested |
| 70-79 | ⭐⭐⭐ Good | Review before deploy |
| 60-69 | ⭐⭐ Needs Work | Address issues before deploy |
| <60 | ⭐ Critical | **Block deployment** |

---

## Cross-Skill Integration

See [../../shared/docs/cross-skill-integration.md](../../shared/docs/cross-skill-integration.md)

| Direction | Pattern |
|-----------|---------|
| sf-agentforce → sf-apex | Create custom Apex actions for agent |
| sf-agentforce → sf-flow | Create Flow-based actions for agent |
| sf-agentforce → sf-deploy | Deploy agent metadata |
| sf-agentforce → sf-metadata | Query object structure for data actions |

**Example**: Creating an agent with a custom Apex action:
```
Skill(skill="sf-apex")
Request: "Create an Apex class CaseService with method createCase that accepts subject and description, returns case ID"

Skill(skill="sf-agentforce")
Request: "Create an agent that uses apex://CaseService.createCase to handle support requests"
```

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
    developer_name: "FAQ_Agent"
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

### Pattern 2: Multi-Topic Router
```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes users to appropriate topics"

    reasoning:
        instructions: ->
            | Determine what the user needs help with.
            | Route to the appropriate topic.
        actions:
            orders: @utils.transition to @topic.order_management
            support: @utils.transition to @topic.support
            billing: @utils.transition to @topic.billing

topic order_management:
    label: "Order Management"
    description: "Helps with orders"

    reasoning:
        instructions: ->
            | Help with order-related questions.
        actions:
            back: @utils.transition to @topic.topic_selector
```

### Pattern 3: Action with Validation
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
```

---

## Anti-Patterns

| Anti-Pattern | Issue | Fix |
|--------------|-------|-----|
| Tab indentation | Syntax error | Use 4 spaces |
| `@variable.name` | Wrong syntax | Use `@variables.name` (plural) |
| `agent_name:` in config | Wrong field | Use `developer_name:` |
| `instructions:->` | Missing space | Use `instructions: ->` |
| Missing `label:` | Deployment fails | Add label to all topics |
| Missing linked variables | Missing context | Add EndUserId, RoutableId, ContactId |
| `.agentscript` extension | Wrong format | Use `.agent` extension |
| Nested `run` | Not supported | Flatten to sequential `run` |
| Missing bundle-meta.xml | Deployment fails | Create XML alongside .agent |
| No language block | Deployment fails | Add language block |

---

## CLI Commands Reference

```bash
# Validate agent script (optional but recommended)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent to org (creates Bot, BotVersion, GenAi metadata)
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# Open agent in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]

# Preview agent (requires connected app setup)
sf agent preview --api-name [AgentName] --target-org [alias] --client-app [app]

# Update plugin to latest (if commands missing)
sf plugins install @salesforce/plugin-agent@latest
```

**IMPORTANT**: Do NOT use `sf project deploy start` for Agent Script files. The standard Metadata API doesn't support direct `.agent` file deployment. Use `sf agent publish authoring-bundle` instead.

---

## Validation

**Manual validation** (if hooks don't fire):
```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py <file_path>
```

**Scoring**: 100 points / 6 categories. Minimum 60 (60%) for deployment.

**Hooks not firing?** Check: `CLAUDE_PLUGIN_ROOT` set, hooks.json valid, Python 3 in PATH, file matches pattern `*.agent`.

---

## 🔑 Key Insights

| Insight | Issue | Fix |
|---------|-------|-----|
| File Extension | `.agentscript` not recognized | Use `.agent` |
| Config Field | `agent_name` causes deploy failure | Use `developer_name` |
| Instructions Syntax | `instructions:->` fails | Use `instructions: ->` (space!) |
| Topic Fields | Missing `label` fails deploy | Add both `label` and `description` |
| Linked Variables | Missing context variables | Add EndUserId, RoutableId, ContactId |
| Language Block | Missing causes deploy failure | Add `language:` block |
| Bundle XML | Missing causes deploy failure | Create `.bundle-meta.xml` file |
| 4-Space Indentation | 3 spaces causes parse errors | Always use 4 spaces |
| `@variables` is plural | `@variable.x` fails | Use `@variables.x` |
| Boolean capitalization | `true/false` invalid | Use `True/False` |
| Deploy Command | `sf project deploy` fails | Use `sf agent publish authoring-bundle` |

---

## Required Files Checklist

Before deployment, ensure you have:

- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].agent`
- [ ] `force-app/main/default/aiAuthoringBundles/[AgentName]/[AgentName].bundle-meta.xml`
- [ ] `sfdx-project.json` in project root
- [ ] Valid `default_agent_user` in config block
- [ ] All linked variables (EndUserId, RoutableId, ContactId)
- [ ] Language block present
- [ ] All topics have `label:` and `description:`

---

## Reference & Dependencies

**Docs**: `../../docs/` - best-practices, agent-script-syntax

**Dependencies**: sf-deploy (optional) for additional deployment options. Install: `/plugin install github:Jaganpro/sf-skills/sf-deploy`

**Notes**: API 64.0+ required | Agent Script is GA (2025) | Block if score < 60

---

## License

MIT License. See [LICENSE](../../LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
