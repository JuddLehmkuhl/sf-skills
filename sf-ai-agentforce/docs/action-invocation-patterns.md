<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md, patterns-and-practices.md -->
<!-- Contains: How to make Agentforce agents reliably invoke actions -->

# Action Invocation Patterns: Fixing the Doomprompting Anti-Pattern

This document addresses the most common failure mode in Agentforce agent development: actions that the agent refuses to call, ignores, or delays behind unnecessary clarifying questions. The root cause is almost always **doomprompting** -- the mistaken belief that stronger behavioral language in prompts will force the Atlas reasoning engine to invoke actions.

---

## 1. The Problem: Doomprompting

**Doomprompting** is Salesforce's name for the anti-pattern of adding increasingly forceful behavioral instructions to agent prompts in an attempt to control action invocation. It manifests as:

- Adding "MUST", "ALWAYS", "IMMEDIATELY" to topic descriptions
- Writing imperative commands in action descriptions ("ALWAYS call this action...")
- Stacking redundant directives across `description`, `reasoning.instructions`, and action `description` fields

**Why it fails:** The Agentforce Atlas planner does not treat text instructions as execution directives. It treats them as **conversation context** -- background information that informs its reasoning but does not compel specific behavior. The planner is an LLM-based reasoning engine, not a rule executor. When it encounters "MUST IMMEDIATELY call get_account_details," it interprets this the same way it interprets "Please look up the account" -- as contextual guidance it may or may not follow.

**The paradox:** Adding stronger language actually makes the problem worse. The more emphatic and repetitive the instructions become, the more noise they add to the planner's context window, making it harder for the planner to identify what action to take and when. Salesforce engineers have observed that agents with cleaner, less verbose prompts outperform agents with aggressive behavioral directives.

---

## 2. Broken Pattern (Before)

The following example shows the triple-layer behavioral prompting approach that **does not work reliably**. This pattern was observed in production Agentforce agents that failed to invoke actions despite extensive prompt engineering.

```agentscript
# BROKEN PATTERN - DO NOT USE
# Triple-layer behavioral prompting (doomprompting)

topic account_lookup:
    label: "Account Lookup"
    description: "IMMEDIATELY look up customer account details when ANY account name is mentioned. MUST call get_account_details without asking clarifying questions."

    actions:
        get_account_details:
            description: "ALWAYS call this action when the user mentions any account name. Do NOT ask for confirmation. MUST be invoked IMMEDIATELY."
            inputs:
                inp_AccountNameOrId: string
                    description: "The account name or Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_AccountId: string
                    description: "The Salesforce Account ID"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Agent_Get_Account_Details"

    reasoning:
        instructions: ->
            | When the user mentions ANY account name, you MUST IMMEDIATELY call get_account_details.
            | Do NOT ask clarifying questions. Do NOT wait for confirmation.
            | ALWAYS invoke the action first, THEN present the results.
            | If the user says "Tell me about Acme Corp", call get_account_details with "Acme Corp" RIGHT AWAY.
            | NEVER respond without first calling get_account_details.
```

**What happens at runtime:** Despite three layers of emphatic instructions (topic description, action description, and reasoning instructions), the Atlas planner may still:

1. Ask "Which account did you mean?" instead of calling the action
2. Respond with "I can help you look up account information. What is the account name?" even though the user already provided it
3. Skip the action entirely and fabricate a response based on its training data
4. Invoke the action intermittently -- working sometimes but not others

The behavioral text is processed as context, not as execution logic. The planner has no mechanism to interpret "MUST" or "IMMEDIATELY" as binding constraints.

---

## 3. Working Pattern (After)

The pattern that reliably triggers action invocation uses **`reasoning.actions` blocks with slot-filling syntax**. Instead of telling the planner what to do in natural language, you declare the data flow using `with` (input binding) and `set` (output capture) statements.

> **Deployment method:** This pattern uses `with`/`set` in `reasoning.actions`, which is a **GenAiPlannerBundle** feature. See [Section 6](#6-llm-driven-vs-deterministic) for AiAuthoringBundle guidance.

```agentscript
# WORKING PATTERN - Use this
# Declarative slot-filling with reasoning.actions

topic account_lookup:
    label: "Account Lookup"
    description: "Look up customer account details, contacts, and recent activity by name"

    actions:
        get_account_details:
            description: "Retrieves account details by name or ID. Accepts partial names."
            inputs:
                inp_AccountNameOrId: string
                    description: "The account name or Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The resolved account name"
                out_AccountId: string
                    description: "The Salesforce Account ID"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Agent_Get_Account_Details"

        get_account_contacts:
            description: "Retrieves contacts for an account"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID"
            outputs:
                out_ContactList: string
                    description: "Formatted list of contacts"
            target: "flow://Agent_Get_Account_Contacts"

        get_recent_activity:
            description: "Retrieves recent activity for an account"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID"
            outputs:
                out_ActivityList: string
                    description: "Formatted list of recent activities"
            target: "flow://Agent_Get_Recent_Activity"

    reasoning:
        instructions: ->
            | Present account data to the user. Never fabricate data.
            | If a lookup returns no results, let the user know.

        actions:
            lookup_account: @actions.get_account_details
                with inp_AccountNameOrId=...
                set @variables.current_account_name = @outputs.out_AccountName
                set @variables.current_account_id = @outputs.out_AccountId

            lookup_contacts: @actions.get_account_contacts
                with inp_AccountId=@variables.current_account_id

            lookup_activity: @actions.get_recent_activity
                with inp_AccountId=@variables.current_account_id
```

**Why this works:** The `reasoning.actions` block with `with`/`set` syntax is **declarative**. It defines a data contract rather than issuing behavioral commands:

- **`with inp_AccountNameOrId=...`** -- The `...` (ellipsis) is slot-filling syntax. It tells the Atlas planner: "Extract the value for this parameter from the conversation context." The planner understands slot-filling as a structured extraction task, which it performs reliably.
- **`set @variables.current_account_id = @outputs.out_AccountId`** -- This captures the action output into a session variable, making it available for subsequent actions.
- **`with inp_AccountId=@variables.current_account_id`** -- This binds a subsequent action's input to a previously captured value, enabling action chaining without repeating lookups.

The planner treats `reasoning.actions` as a structured action catalog with defined input/output contracts. When a user mentions an account name, the planner matches the intent to `lookup_account`, extracts the account name to fill the `...` slot, and invokes the action. No behavioral prompting required.

---

## 4. Syntax Reference Table

| Syntax | Purpose | Example |
|--------|---------|---------|
| `with param=...` | LLM slot-filling from conversation context | `with inp_AccountNameOrId=...` |
| `with param=@variables.x` | Bind to a previously captured session variable | `with inp_AccountId=@variables.current_account_id` |
| `with param="literal"` | Pass a fixed string value | `with inp_Status="Active"` |
| `set @variables.x = @outputs.y` | Capture action output into a session variable | `set @variables.current_account_id = @outputs.out_AccountId` |

**Key rules:**

- The `...` (ellipsis) means "the LLM fills this from conversation context." It is not a placeholder for you to replace -- it is literal syntax.
- `@variables.x` references must point to variables declared in the agent's `variables:` block.
- `@outputs.y` references must match the output parameter names declared in the action's `outputs:` block.
- Multiple `with` and `set` statements can appear on consecutive lines within the same action block.

---

## 5. Variable Capture and Reuse

The core pattern for multi-turn conversations is: **first action captures entity context, subsequent actions bind to the captured ID.**

### Multi-Turn Conversation Flow

```
User: "Tell me about Acme Corp"
  --> lookup_account fires
  --> with inp_AccountNameOrId=... extracts "Acme Corp" from context
  --> set @variables.current_account_name = "Acme Corp"
  --> set @variables.current_account_id = "001xx000003DGbY"

User: "Who are the contacts?"
  --> lookup_contacts fires
  --> with inp_AccountId=@variables.current_account_id uses "001xx000003DGbY"
  --> No need to re-ask which account

User: "Any recent activity?"
  --> lookup_activity fires
  --> with inp_AccountId=@variables.current_account_id uses same "001xx000003DGbY"
  --> Still no re-ask -- session variable persists
```

### Declaring Session Variables

Variables used for cross-action state must be declared in the agent's `variables:` block:

```agentscript
variables:
    # Linked variables (standard -- always include these)
    EndUserId: linked string
        source: @MessagingSession.MessagingEndUserId
        description: "Messaging End User ID"
    RoutableId: linked string
        source: @MessagingSession.Id
        description: "Messaging Session ID"
    ContactId: linked string
        source: @MessagingEndUser.ContactId
        description: "Contact ID"

    # Mutable session variables (for action output capture)
    current_account_name: mutable string
        description: "The name of the account currently being discussed. Set by the account lookup action and used to maintain conversational context across turns."
        visibility: "Internal"
    current_account_id: mutable string
        description: "The Salesforce Account ID of the account currently being discussed. Used to chain subsequent actions (contacts, activity, cases) without re-querying."
        visibility: "Internal"
```

**Variable design guidelines:**

| Guideline | Reason |
|-----------|--------|
| Use `mutable string` for IDs and names | IDs and names change as the user switches context |
| Set `visibility: "Internal"` | Prevents the variable value from being displayed to the user in chat |
| Write descriptive `description` fields | The planner uses descriptions to understand when and how to populate variables |
| Name with `current_` prefix for entity context | Makes it clear the variable tracks the active entity in conversation |

### Cross-Topic Variable Sharing

Session variables are scoped to the entire agent, not individual topics. This means a variable set in one topic is available in all other topics:

```agentscript
topic account_lookup:
    reasoning:
        actions:
            lookup_account: @actions.get_account_details
                with inp_AccountNameOrId=...
                set @variables.current_account_id = @outputs.out_AccountId

topic case_management:
    reasoning:
        actions:
            create_case: @actions.create_support_case
                # Uses variable set by account_lookup topic
                with inp_AccountId=@variables.current_account_id
                with inp_Subject=...
```

---

## 6. LLM-Driven vs Deterministic

Agent Script supports two invocation models. Choose based on whether the agent or the script should decide when to call an action.

### LLM-Driven Invocation (reasoning.actions)

Use `reasoning.actions` when the **planner should decide** which action to call based on user intent. This is the standard pattern for GenAiPlannerBundle agents.

```agentscript
reasoning:
    actions:
        lookup_account: @actions.get_account_details
            with inp_AccountNameOrId=...
            set @variables.current_account_id = @outputs.out_AccountId
```

**When to use:**
- The agent should decide which action to call based on what the user says
- Parameters need to be extracted from natural language conversation
- Multiple actions are available and the planner selects the right one
- The action should only fire when the user's intent matches

### Deterministic Invocation (run keyword)

Use `run @actions.x` inside `instructions:` when an action should **always execute** regardless of context. This is available in **GenAiPlannerBundle only**.

```agentscript
reasoning:
    instructions: ->
        | Welcome the user and load their profile.
        run @actions.load_user_profile
            with inp_UserId=@variables.ContactId
            set @variables.user_name = @outputs.out_UserName
        | Hello {!@variables.user_name}, how can I help?
```

**When to use:**
- An action should always fire when a topic is entered (e.g., loading user context)
- There is no decision-making needed -- the action is always required
- The action is part of a fixed sequence, not a response to user intent

### AiAuthoringBundle Guidance

AiAuthoringBundle does **not** support `with`/`set` in `reasoning.actions` or the `run` keyword. For AiAuthoringBundle agents:

1. **Define actions in the topic's `actions:` block** with clear, descriptive `description` fields
2. **Write clear `reasoning.instructions`** that describe when to use each action
3. **Let the LLM auto-select** actions based on descriptions -- no slot-filling syntax

```agentscript
# AiAuthoringBundle pattern -- no with/set, no run
topic account_lookup:
    label: "Account Lookup"
    description: "Look up customer account details by name"

    actions:
        get_account_details:
            description: "Retrieves account details by name or ID. Accepts partial names."
            inputs:
                inp_AccountNameOrId: string
                    description: "The account name or Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The resolved account name"
                out_AccountId: string
                    description: "The Salesforce Account ID"
            target: "flow://Agent_Get_Account_Details"

    reasoning:
        instructions: ->
            | When the user mentions an account, use the get_account_details action.
            | Present the results clearly. Never fabricate data.
```

In AiAuthoringBundle, the planner relies on action descriptions to decide when to invoke. Write descriptions that clearly state what the action does and what input it expects. Avoid behavioral directives -- describe the action's purpose, not commands for the planner.

---

## 7. Production-Validated

This pattern has been validated in a production Salesforce org with the following characteristics:

| Metric | Value |
|--------|-------|
| Topics | 7 |
| Flow actions | 10 |
| Session variables | 8 (with cross-topic chaining) |
| Deployment method | GenAiPlannerBundle |
| Action invocation reliability | Consistent -- no doomprompting required |

The agent reliably invokes actions based on user intent, chains outputs across topics using session variables, and maintains conversational context across multi-turn interactions. The key insight is that moving from behavioral text instructions to declarative `reasoning.actions` with slot-filling syntax eliminated all action invocation failures.

### Before vs After Summary

| Aspect | Doomprompting (Before) | Slot-Filling (After) |
|--------|----------------------|---------------------|
| Action invocation | Intermittent, unreliable | Consistent, reliable |
| Prompt verbosity | High (repeated directives) | Low (clean descriptions) |
| Parameter extraction | LLM guesses from context | LLM fills structured slots |
| Output capture | Manual, error-prone | Declarative `set` statements |
| Multi-turn context | Frequently lost | Persisted in session variables |
| Maintenance burden | High (constant prompt tuning) | Low (change actions, not prompts) |

---

## Related Documentation

- [SKILL.md](../SKILL.md) -- Complete Agent Script reference and deployment guide
- [agent-script-reference.md](agent-script-reference.md) -- Full syntax specification
- [patterns-and-practices.md](patterns-and-practices.md) -- Pattern decision tree and best practices
- [actions-reference.md](actions-reference.md) -- All action types and connection blocks
