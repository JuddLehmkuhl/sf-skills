# Agent Script Syntax Reference

Complete syntax reference for the Agent Script language used in Agentforce.

**Updated**: December 2025 - Corrected based on actual Salesforce implementation.

---

## File Structure

Agent Script files use the `.agent` extension and contain YAML-like syntax with specific Agent Script keywords.

**Required Files** (per agent):
```
force-app/main/default/aiAuthoringBundles/[AgentName]/
├── [AgentName].agent           # Agent definition
└── [AgentName].bundle-meta.xml # Metadata XML
```

**bundle-meta.xml content**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

### Block Order (CRITICAL)

Blocks MUST appear in this order:
1. `system:` - Instructions and messages
2. `config:` - Agent metadata
3. `variables:` - Linked and mutable variables
4. `language:` - Locale settings
5. `start_agent [name]:` - Entry point topic
6. `topic [name]:` - Additional topics

### Complete Working Example

```agentscript
system:
    instructions: "You are a helpful assistant. Be professional and friendly."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "I apologize, but I encountered an issue."

config:
    developer_name: "My_Agent"
    default_agent_user: "user@org.salesforce.com"
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
        description: "User's current question"

language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False

start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes users to appropriate topics"

    reasoning:
        instructions: ->
            | Determine user intent and route.
        actions:
            go_help: @utils.transition to @topic.help
            go_farewell: @utils.transition to @topic.farewell

topic help:
    label: "Help"
    description: "Provides help to users"

    reasoning:
        instructions: ->
            | Answer the user's question helpfully.

topic farewell:
    label: "Farewell"
    description: "Ends conversation gracefully"

    reasoning:
        instructions: ->
            | Thank the user and say goodbye.
```

---

## Indentation Rules

**CRITICAL**: Agent Script requires **4-space indentation**.

```agentscript
# ✅ CORRECT - 4 spaces per level
config:
    developer_name: "My_Agent"
    description: "Description"

# ❌ WRONG - 3 spaces
config:
   developer_name: "My_Agent"

# ❌ WRONG - tabs
config:
	developer_name: "My_Agent"
```

---

## Blocks

### System Block

Global agent settings and instructions. **Must be first block**.

```agentscript
system:
    instructions: "You are a helpful assistant. Be professional."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "I'm sorry, something went wrong. Please try again."
```

For longer instructions, use multiline format:
```agentscript
system:
    instructions:
        | You are a helpful customer service agent.
        | Be professional and courteous.
        | Never share confidential information.
    messages:
        welcome: "Hello!"
        error: "Sorry, an error occurred."
```

### Config Block

Defines agent metadata. **Required fields**: developer_name, default_agent_user, agent_label, description.

```agentscript
config:
    developer_name: "Customer_Support_Agent"
    default_agent_user: "agent.user@company.salesforce.com"
    agent_label: "Customer Support"
    description: "Helps customers with orders and inquiries"
```

| Field | Required | Description |
|-------|----------|-------------|
| `developer_name` | Yes | API name (PascalCase with underscores) |
| `default_agent_user` | Yes | Username for agent execution context |
| `agent_label` | Yes | Human-readable name |
| `description` | Yes | What the agent does |

**IMPORTANT**: Use `developer_name`, NOT `agent_name`!

### Variables Block

Declares state variables. **Linked variables first, then mutable**.

**Linked Variables** (connect to Salesforce data - REQUIRED):
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
        description: "The customer's name"
    order_count: mutable number
        description: "Number of items in cart"
    is_verified: mutable boolean
        description: "Whether identity is verified"
```

### Language Block

Locale settings. **Required for deployment**.

```agentscript
language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False
```

### Topic Blocks

Define conversation topics. **Each topic requires `label:` and `description:`**.

**Entry point topic** (required):
```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes users to appropriate topics"

    reasoning:
        instructions: ->
            | Determine user intent and route.
        actions:
            go_orders: @utils.transition to @topic.orders
```

**Regular topic**:
```agentscript
topic orders:
    label: "Order Management"
    description: "Handles order inquiries"

    reasoning:
        instructions: ->
            | Help with order questions.
        actions:
            back: @utils.transition to @topic.topic_selector
```

---

## Variable Types

| Type | Description | Default | Example |
|------|-------------|---------|---------|
| `string` | Text values | `""` | `"John Doe"` |
| `number` | Integers or decimals | `0` | `42`, `99.99` |
| `boolean` | True/False | `False` | `True`, `False` |
| `list[type]` | Array of values | `[]` | `list[string]` |
| `object` | Complex object | `{}` | Custom structure |

**Note**: Boolean values must be capitalized: `True`, `False`

---

## Resource References

Use the `@` prefix to reference resources.

| Resource | Syntax | Usage |
|----------|--------|-------|
| Variables | `@variables.name` | Access stored values |
| Actions | `@actions.name` | Invoke defined actions |
| Topics | `@topic.name` | Reference topics |
| Outputs | `@outputs.field` | Action output values |
| Utilities | `@utils.transition` | Built-in utilities |
| Utilities | `@utils.escalate` | Escalate to human |

```agentscript
# Variable reference
if @variables.user_name is None:

# Action reference
invoke: @actions.get_order
    with order_id=@variables.current_order_id

# Topic reference
go: @utils.transition to @topic.checkout

# Output capture
set @variables.status = @outputs.order_status

# Escalation
escalate: @utils.escalate
    description: "Transfer to human agent"
```

---

## Instructions

### Syntax (CRITICAL)

Use `instructions: ->` (with space before arrow), NOT `instructions:->`.

```agentscript
# ✅ CORRECT
reasoning:
    instructions: ->
        | Determine user intent.

# ❌ WRONG - missing space before arrow
reasoning:
    instructions:->
        | Determine user intent.
```

### Prompt Mode (|)

Use `|` for natural language instructions:

```agentscript
instructions: ->
    | This is line one.
    | This is line two.
    | Each line starts with a pipe.
```

### Procedural Mode (->)

Use `->` for logic-based instructions:

```agentscript
instructions: ->
    if @variables.amount > 1000:
        | This is a large order.
    else:
        | Standard order processing.
```

### Template Expressions

Use `{!...}` for variable interpolation:

```agentscript
instructions: ->
    | Hello {!@variables.user_name}!
    | Your order total is ${!@variables.total}.
```

---

## Conditionals

### If/Else

```agentscript
instructions: ->
    if @variables.amount > 1000:
        | Large order - requires approval.
    else:
        | Standard order.

    if @variables.status == "shipped":
        | Your order is on its way!

    if @variables.email is None:
        | Please provide your email address.

    if @variables.verified == True:
        | Identity confirmed.
```

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `==` | Equals | `@variables.status == "active"` |
| `!=` | Not equals | `@variables.count != 0` |
| `>` | Greater than | `@variables.amount > 100` |
| `<` | Less than | `@variables.count < 10` |
| `>=` | Greater or equal | `@variables.age >= 18` |
| `<=` | Less or equal | `@variables.priority <= 5` |

### Null Checks

```agentscript
if @variables.name is None:
    | Name not provided.

if @variables.email is not None:
    | Email is available.
```

---

## Actions

### Defining Actions

```agentscript
topic my_topic:
    label: "My Topic"
    description: "Topic description"

    actions:
        get_order:
            description: "Retrieves order details"
            inputs:
                order_id: string
                    description: "The order ID"
            outputs:
                status: string
                    description: "Order status"
                total: number
                    description: "Order total"
            target: "flow://Get_Order_Details"

    reasoning:
        instructions: ->
            | Help the user with their order.
```

### Target Formats

| Type | Format | Example |
|------|--------|---------|
| Flow | `flow://FlowName` | `flow://Get_Order_Details` |
| Apex | `apex://ClassName.methodName` | `apex://OrderService.getOrder` |

### Invoking Actions

```agentscript
reasoning:
    actions:
        # LLM fills input from conversation
        lookup: @actions.get_order
            with order_id=...

        # Fixed value
        default: @actions.get_order
            with order_id="DEFAULT"

        # Variable binding
        bound: @actions.get_order
            with order_id=@variables.current_order_id

        # Capture outputs
        full: @actions.get_order
            with order_id=...
            set @variables.status = @outputs.status
            set @variables.total = @outputs.total
```

### Action Callbacks (Chaining)

```agentscript
process: @actions.create_order
    with items=...
    set @variables.order_id = @outputs.order_id
    run @actions.send_confirmation
        with order_id=@variables.order_id
    run @actions.update_inventory
        with items=@variables.cart_items
```

**Note**: Only one level of `run` nesting is supported.

### Conditional Availability

```agentscript
checkout: @actions.process_payment
    with amount=@variables.total
    available when @variables.cart_count > 0
    available when @variables.verified == True
```

---

## Topic Transitions

### Basic Transition

```agentscript
reasoning:
    actions:
        go_orders: @utils.transition to @topic.orders
```

### Conditional Transition

```agentscript
go_checkout: @utils.transition to @topic.checkout
    available when @variables.cart_count > 0
```

### Escalation to Human

```agentscript
topic escalation:
    label: "Escalation"
    description: "Transfers to human agent"

    reasoning:
        instructions: ->
            | Transfer the conversation to a human.
        actions:
            escalate: @utils.escalate
                description: "Escalate to a human agent"
```

---

## Deployment

### Publish Command

```bash
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
```

This command:
- Validates Agent Script syntax
- Creates Bot, BotVersion, GenAi metadata
- Deploys the AiAuthoringBundle

**Do NOT use** `sf project deploy start` for Agent Script files.

### Other Commands

```bash
# Validate without publishing
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Open in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

---

## Common Patterns

### Simple Q&A Agent

```agentscript
system:
    instructions: "You are a helpful FAQ assistant. Answer concisely."
    messages:
        welcome: "Hello! How can I help?"
        error: "Sorry, an error occurred."

config:
    developer_name: "FAQ_Agent"
    default_agent_user: "agent@company.com"
    agent_label: "FAQ Assistant"
    description: "Answers frequently asked questions"

variables:
    EndUserId: linked string
        source: @MessagingSession.MessagingEndUserId
        description: "End User ID"
    RoutableId: linked string
        source: @MessagingSession.Id
        description: "Session ID"
    ContactId: linked string
        source: @MessagingEndUser.ContactId
        description: "Contact ID"

language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False

start_agent topic_selector:
    label: "Topic Selector"
    description: "Handles FAQ questions"

    reasoning:
        instructions: ->
            | Answer the user's question.
            | If unsure, offer to connect them with support.
```

### Multi-Topic Router

```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes to specialized topics"

    reasoning:
        instructions: ->
            | Determine what the user needs.
            | Route to the appropriate topic.
        actions:
            orders: @utils.transition to @topic.orders
            billing: @utils.transition to @topic.billing
            support: @utils.transition to @topic.support
```

### Validation Pattern

```agentscript
instructions: ->
    if @variables.email is None:
        set @variables.valid = False
        | Please provide your email address.

    if @variables.amount <= 0:
        set @variables.valid = False
        | Amount must be greater than zero.

    if @variables.valid == True:
        | All validations passed. Proceeding.
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| Parse error | Invalid syntax | Check 4-space indentation |
| Unknown resource | Invalid `@` reference | Use `@variables`, `@actions`, etc. |
| Undefined variable | Variable not declared | Add to `variables:` block |
| Undefined topic | Topic not found | Add topic or fix reference |
| Invalid target | Wrong action target format | Use `flow://` or `apex://` |
| Nested run | `run` inside `run` | Flatten to sequential `run` |
| Missing label | Topic without label | Add `label:` to all topics |
| Wrong config field | Using `agent_name` | Use `developer_name` |
| Missing space | `instructions:->` | Use `instructions: ->` |

---

## Anti-Patterns

| Anti-Pattern | Issue | Fix |
|--------------|-------|-----|
| Tab indentation | Syntax error | Use 4 spaces |
| `@variable.name` | Wrong syntax | Use `@variables.name` (plural) |
| `agent_name:` | Wrong field | Use `developer_name:` |
| `instructions:->` | Missing space | Use `instructions: ->` |
| Missing `label:` | Deploy fails | Add label to all topics |
| `.agentscript` | Wrong extension | Use `.agent` |
| No bundle XML | Deploy fails | Create `.bundle-meta.xml` |
| No language block | Deploy fails | Add `language:` block |
| Missing linked vars | Missing context | Add EndUserId, RoutableId, ContactId |
