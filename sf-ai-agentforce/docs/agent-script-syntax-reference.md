<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Extracted from SKILL.md to keep the entry point lean and pattern-focused -->
<!-- For patterns and best practices, see SKILL.md and docs/ files -->

# Agent Script Syntax Reference

Comprehensive syntax reference for Agent Script. This document contains the detailed rules,
types, and gotchas for writing valid Agent Script.

> **Entry Point**: Start with [SKILL.md](../SKILL.md) for patterns and workflow.
> This document is the detailed syntax reference.

---

## Table of Contents

1. [Indentation Rules](#indentation-rules)
2. [Comments](#comments)
3. [System Instructions](#system-instructions)
4. [Escalation Description](#escalation-description)
5. [Reserved Words](#reserved-words)
6. [Invalid Keywords](#invalid-keywords)
7. [Action Target Syntax](#action-target-syntax)
8. [Data Type Mappings](#data-type-mappings)
9. [Advanced Action Fields](#advanced-action-fields)
10. [Connection Block](#connection-block)
11. [Resource Access](#resource-access)

---

## Indentation Rules

**Agent Script is whitespace-sensitive (like Python/YAML). Use CONSISTENT indentation throughout.**

| Rule | Details |
|------|---------|
| **Tabs (Recommended)** | Use tabs for easier manual editing and consistent alignment |
| **Spaces** | 2, 3, or 4 spaces also work if used consistently |
| **Mixing** | NEVER mix tabs and spaces (causes parse errors) |
| **Consistency** | All lines at same nesting level must use same indentation |

**RECOMMENDED: Use TAB indentation for all Agent Script files.** Tabs are easier to edit manually and provide consistent visual alignment across editors.

```agentscript
# RECOMMENDED - consistent tabs (best for manual editing)
config:
	agent_name: "My_Agent"
	description: "My agent description"

variables:
	user_name: mutable string
		description: "The user's name"

# ALSO CORRECT - consistent spaces (if you prefer)
config:
   agent_name: "My_Agent"

# WRONG - mixing tabs and spaces
config:
	agent_name: "My_Agent"    # tab
   description: "My agent"    # spaces - PARSE ERROR!
```

**Why Tabs are Recommended:**
- Easier to edit manually in any text editor
- Consistent visual alignment regardless of editor tab width settings
- Single keypress per indentation level
- Clear distinction between indentation levels

---

## Comments

**Single-line comments** use the `#` (pound/hash) symbol:

```agentscript
# This is a top-level comment
system:
   # Comment explaining the instructions
   instructions: "You are a helpful assistant."

config:
   agent_name: "My_Agent"  # Inline comment
   # This describes the agent
   description: "A helpful assistant"

topic help:
   # This topic handles help requests
   label: "Help"
   description: "Provides assistance"
```

**Notes:**
- Everything after `#` on a line is ignored
- Use comments to document complex logic or business rules
- Comments are recommended for clarity but don't affect execution

---

## System Instructions

**System instructions MUST be a single quoted string. The `|` pipe multiline syntax does NOT work in the `system:` block.**

```agentscript
# CORRECT - Single quoted string
system:
   instructions: "You are a helpful assistant. Be professional and friendly. Never share confidential information."
   messages:
      welcome: "Hello!"
      error: "Sorry, an error occurred."

# WRONG - Pipe syntax fails with SyntaxError
system:
   instructions:
      | You are a helpful assistant.
      | Be professional.
```

**Note**: The `|` pipe syntax ONLY works inside `reasoning: instructions: ->` blocks within topics.

---

## Escalation Description

**`@utils.escalate` REQUIRES a `description:` on a separate indented line.**

```agentscript
# CORRECT - description on separate line
actions:
   escalate_to_human: @utils.escalate
      description: "Transfer to human when customer requests or issue cannot be resolved"

# WRONG - inline description fails
actions:
   escalate: @utils.escalate "description here"
```

---

## Reserved Words

**These words CANNOT be used as input/output parameter names OR action names:**

| Reserved Word | Why | Alternative |
|---------------|-----|-------------|
| `description` | Conflicts with `description:` keyword | `case_description`, `item_description` |
| `inputs` | Keyword for action inputs | `input_data`, `request_inputs` |
| `outputs` | Keyword for action outputs | `output_data`, `response_outputs` |
| `target` | Keyword for action target | `destination`, `endpoint` |
| `label` | Keyword for topic label | `display_label`, `title` |
| `source` | Keyword for linked variables | `data_source`, `origin` |
| `escalate` | Reserved for `@utils.escalate` | `go_to_escalate`, `transfer_to_human` |

**Example of Reserved Word Conflict:**
```agentscript
# WRONG - 'description' conflicts with keyword
inputs:
   description: string
      description: "The description field"

# CORRECT - Use alternative name
inputs:
   case_description: string
      description: "The description field"
```

---

## Invalid Keywords

**The following keywords DO NOT EXIST in Agent Script. Using them causes SyntaxError.**

| Invalid Keyword | Error | Why It Happens | Correct Pattern |
|-----------------|-------|----------------|-----------------|
| `internal_actions` | `SyntaxError: Unexpected 'internal_actions'` | Claude may invent this for "local helper functions" | Use `set` statements directly in action blocks |
| `helper_actions` | Not a valid keyword | Same as above | Use `set` statements directly |
| `private_actions` | Not a valid keyword | Same as above | Use `set` statements directly |
| `local_actions` | Not a valid keyword | Same as above | Use `set` statements directly |

**Root Cause**: When needing simple post-action operations (like incrementing a counter), Claude may extrapolate from general programming patterns and invent "local function" syntax that doesn't exist.

**Example: Simple Variable Update After Action**

```agentscript
# WRONG - internal_actions does not exist
internal_actions:
    increment_counter:
        set @variables.count = @variables.count + 1

reasoning:
    actions:
        process: @actions.create_case
            run @actions.increment_counter   # Can't reference internal action

# CORRECT - Use set directly in the action block
reasoning:
    actions:
        create_support_case: @actions.create_case
            with inp_CustomerId=@variables.ContactId
            with inp_Subject=...
            set @variables.case_number = @outputs.out_CaseNumber
            set @variables.cases_created = @variables.cases_created + 1  # Direct set!
```

**For AiAuthoringBundle**: The `run` keyword is NOT supported. Use only `set` statements for post-action variable updates.

**See Also**: `templates/patterns/action-callbacks.agent` for complete patterns.

---

## Action Target Syntax

### Complete Action Type Reference (22 Types)

AgentScript supports 22+ action target types. Use the appropriate protocol prefix:

| Short Name | Long Name (Alias) | Description | Use When |
|------------|-------------------|-------------|----------|
| `flow` | `flow` | Salesforce Flow | **PRIMARY** - Most reliable, recommended for all actions |
| `apex` | `apex` | Apex Class (@InvocableMethod) | Custom server-side logic (use Flow wrapper in AiAuthoringBundle) |
| `prompt` | `generatePromptResponse` | Prompt Template | AI content generation |
| `standardInvocableAction` | `standardInvocableAction` | Built-in Salesforce actions | Standard platform actions (send email, create task) |
| `externalService` | `externalService` | External API via OpenAPI schema | External system calls via External Services |
| `quickAction` | `quickAction` | Object-specific quick actions | Quick actions (log call, create related record) |
| `api` | `api` | REST API calls | Direct Salesforce API calls |
| `apexRest` | `apexRest` | Apex REST endpoints | Custom REST services |
| `serviceCatalog` | `createCatalogItemRequest` | Service Catalog requests | IT service requests, catalog items |
| `integrationProcedureAction` | `executeIntegrationProcedure` | OmniStudio Integration Procedure | OmniStudio/Vlocity integrations |
| `expressionSet` | `runExpressionSet` | Expression Set calculations | Business rule calculations |
| `cdpMlPrediction` | `cdpMlPrediction` | CDP ML predictions | Customer Data Platform ML models |
| `externalConnector` | `externalConnector` | External system connector | Pre-built external connectors |
| `slack` | `slack` | Slack integration | Slack-specific actions |
| `namedQuery` | `namedQuery` | Predefined SOQL queries | Named queries for data retrieval |
| `auraEnabled` | `auraEnabled` | Aura-enabled Apex methods | Lightning component methods |
| `mcpTool` | `mcpTool` | Model Context Protocol tools | MCP tool integrations |
| `retriever` | `retriever` | Knowledge retrieval | Knowledge base searches |

**Target Format**: `<type>://<DeveloperName>` (e.g., `flow://Get_Account_Info`, `standardInvocableAction://sendEmail`)

**0-shot Tip**: If you need a built-in action, check if `standardInvocableAction://` applies before creating a custom Flow.

### Action Targets by Deployment Method

| Target Type | GenAiPlannerBundle | AiAuthoringBundle |
|-------------|-------------------|-------------------|
| `flow://FlowName` | Works | Works (with exact name matching) |
| `apex://ClassName` | Works | Limited (class must exist) |
| `prompt://TemplateName` | Works | Requires asset in org |

### Flow Action Requirements (Both Methods)

**`flow://` actions work in BOTH AiAuthoringBundle and GenAiPlannerBundle**, but require:

1. **EXACT variable name matching** between Agent Script and Flow
2. Flow must be an **Autolaunched Flow** (not Screen Flow)
3. Flow variables must be marked "Available for input" / "Available for output"
4. Flow must be deployed to org **BEFORE** agent publish

**The "Internal Error" occurs when input/output names don't match Flow variables!**

```
ERROR: "property account_id was not found in the available list of
        properties: [inp_AccountId]"

This error appears as generic "Internal Error, try again later" in CLI.
```

### Correct Flow Action Pattern

**Step 1: Create Flow with specific variable names**
```xml
<!-- Get_Account_Info.flow-meta.xml -->
<variables>
    <name>inp_AccountId</name>     <!-- INPUT variable -->
    <dataType>String</dataType>
    <isInput>true</isInput>
    <isOutput>false</isOutput>
</variables>
<variables>
    <name>out_AccountName</name>   <!-- OUTPUT variable -->
    <dataType>String</dataType>
    <isInput>false</isInput>
    <isOutput>true</isOutput>
</variables>
```

**Step 2: Agent Script MUST use EXACT same names**
```agentscript
actions:
   get_account:
      description: "Retrieves account information"
      inputs:
         inp_AccountId: string        # MUST match Flow variable name!
            description: "Salesforce Account ID"
      outputs:
         out_AccountName: string      # MUST match Flow variable name!
            description: "Account name"
      target: "flow://Get_Account_Info"
```

### Common Mistake (Causes "Internal Error")

```agentscript
# WRONG - Names don't match Flow variables
actions:
   get_account:
      inputs:
         account_id: string           # Flow expects "inp_AccountId"!
      outputs:
         account_name: string         # Flow expects "out_AccountName"!
      target: "flow://Get_Account_Info"
```

This will fail with "Internal Error, try again later" because the schema validation fails silently.

### Requirements Summary

| Requirement | Details |
|-------------|---------|
| **Variable Name Matching** | Agent Script input/output names MUST exactly match Flow variable API names |
| **Flow Type** | Must be **Autolaunched Flow** (not Screen Flow) |
| **Flow Variables** | Mark as "Available for input" / "Available for output" |
| **Deploy Order** | Deploy Flow to org BEFORE publishing agent |
| **API Version** | API v65.0+ required for both AiAuthoringBundle and GenAiPlannerBundle |
| **All Inputs Required** | Agent Script must define ALL inputs that Flow expects (missing inputs = Internal Error) |

### Flow Validation Timing (Tested Dec 2025)

**Flow existence is validated at DEPLOYMENT time, NOT during `sf agent validate`!**

| Command | What It Checks | Flow Validation |
|---------|----------------|-----------------|
| `sf agent validate authoring-bundle` | Syntax only | Does NOT check if flows exist |
| `sf project deploy start` | Full deployment | Validates flow existence |

**This means:**
- An agent can **PASS validation** with `sf agent validate authoring-bundle`
- But **FAIL deployment** if the referenced flow doesn't exist in the org

```bash
# Passes - only checks Agent Script syntax
sf agent validate authoring-bundle --api-name My_Agent --target-org MyOrg
# Status: COMPLETED, Errors: 0

# Fails - flow doesn't exist in org
sf project deploy start --source-dir force-app/main/default/aiAuthoringBundles/My_Agent
# Error: "We couldn't find the flow, prompt, or apex class: flow://Missing_Flow"
```

**Best Practice: Always deploy flows BEFORE deploying agents that reference them.**

---

## Data Type Mappings

### Agent Script to Flow Data Types (Tested Dec 2025)

**Confirmed working data types between Agent Script and Flow:**

| Agent Script Type | Flow Data Type | Status | Notes |
|-------------------|----------------|--------|-------|
| `string` | String | Works | Standard text values |
| `number` | Number (scale=0) | Works | Integer values |
| `number` | Number (scale>0) | Works | Decimal values (e.g., 3.14) |
| `boolean` | Boolean | Works | Use `True`/`False` (capitalized) |
| `list[string]` | Text Collection | Works | Collection with `isCollection=true` |
| `string` | Date | Works* | *Use String I/O pattern (see below) |
| `string` | DateTime | Works* | *Use String I/O pattern (see below) |

### Date/DateTime Workaround Pattern

Agent Script does NOT have native `date` or `datetime` types. If you try to connect an Agent Script `string` input to a Flow `Date` or `DateTime` input, it will fail with "Internal Error" because the platform cannot coerce types.

**Solution: Use String I/O pattern**

1. **Flow accepts/returns Strings** (not Date/DateTime)
2. **Flow parses strings internally** using `DATEVALUE()` or `DATETIMEVALUE()`
3. **Flow converts back to string** using `TEXT()` for output

```xml
<!-- Flow with String I/O for Date handling -->
<variables>
    <name>inp_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isInput>true</isInput>
</variables>
<variables>
    <name>out_DateString</name>
    <dataType>String</dataType>       <!-- NOT Date -->
    <isOutput>true</isOutput>
</variables>
<formulas>
    <name>formula_ParseDate</name>
    <dataType>Date</dataType>
    <expression>DATEVALUE({!inp_DateString})</expression>
</formulas>
<formulas>
    <name>formula_DateAsString</name>
    <dataType>String</dataType>
    <expression>TEXT({!formula_ParseDate})</expression>
</formulas>
```

```agentscript
# Agent Script with string type for date
actions:
   process_date:
      inputs:
         inp_DateString: string
            description: "A date value in YYYY-MM-DD format"
      outputs:
         out_DateString: string
            description: "The processed date as string"
      target: "flow://Test_Date_Type_StringIO"
```

### Collection Types (list[string])

`list[string]` maps directly to Flow Text Collection:

```xml
<variables>
    <name>inp_TextList</name>
    <dataType>String</dataType>
    <isCollection>true</isCollection>  <!-- This makes it a list -->
    <isInput>true</isInput>
</variables>
```

```agentscript
actions:
   process_collection:
      inputs:
         inp_TextList: list[string]
            description: "A list of text values"
      target: "flow://Test_Collection_StringIO"
```

### All Inputs Required Rule

If Flow defines 6 input variables but Agent Script only provides 4, publish fails with "Internal Error":

```
FAILS - Missing inputs
   Flow inputs:    inp_String, inp_Number, inp_Boolean, inp_Date
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: "Internal Error, try again later"

WORKS - All inputs provided
   Flow inputs:    inp_String, inp_Number, inp_Boolean
   Agent inputs:   inp_String, inp_Number, inp_Boolean
   Result: Success
```

---

## Advanced Action Fields

### `object` Type with `complex_data_type_name` (Tested Dec 2025)

For fine-grained control over action behavior, use the `object` type with `complex_data_type_name` and advanced field attributes.

> **Note**: The `filter_from_agent` attribute shown below is **GenAiPlannerBundle only**. It causes "Unexpected 'filter_from_agent'" errors in AiAuthoringBundle. Omit this attribute when using `sf agent publish authoring-bundle`.

```agentscript
actions:
   lookup_order:
      description: "Retrieve order details for a given Order Number."
      inputs:
         order_number: object
            description: "The Order Number the user has provided"
            label: "order_number"
            is_required: False
            is_user_input: False
            complex_data_type_name: "lightning__textType"
      outputs:
         order_id: object
            description: "The Record ID of the Order"
            label: "order_id"
            complex_data_type_name: "lightning__textType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
         order_is_current: object
            description: "Whether the order is current"
            label: "order_is_current"
            complex_data_type_name: "lightning__booleanType"
            filter_from_agent: False
            is_used_by_planner: True
            is_displayable: False
      target: "flow://lookup_order"
      label: "Lookup Order"
      require_user_confirmation: False
      include_in_progress_indicator: False
```

### Lightning Data Types (`complex_data_type_name`)

| Type | Description |
|------|-------------|
| `lightning__textType` | Text/String values |
| `lightning__numberType` | Numeric values |
| `lightning__booleanType` | Boolean True/False |
| `lightning__dateTimeStringType` | DateTime as string |

### Input Field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_required` | Boolean | Whether the input must be provided |
| `is_user_input` | Boolean | Whether the LLM should collect from user |
| `label` | String | Display label for the field |
| `complex_data_type_name` | String | Lightning data type mapping |

### Output Field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `filter_from_agent` | Boolean | Hide output from agent reasoning |
| `is_used_by_planner` | Boolean | Whether planner uses this output |
| `is_displayable` | Boolean | Show output to user |
| `complex_data_type_name` | String | Lightning data type mapping |

### Action-Level Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `label` | String | Display name for the action |
| `require_user_confirmation` | Boolean | Ask user before executing |
| `include_in_progress_indicator` | Boolean | Show progress during execution |

### Minimum Required Attributes

Only `description` and `complex_data_type_name` are required. All other attributes are optional:

```agentscript
# Minimal object type - works!
inputs:
   input_text: object
      description: "Text input"
      complex_data_type_name: "lightning__textType"
```

### Mixing Simple and Object Types

You can mix `string`/`number`/`boolean` with `object` types in the same action:

```agentscript
inputs:
   # Simple type (basic syntax)
   simple_text: string
      description: "A simple text input"
   # Object type (advanced syntax)
   advanced_text: object
      description: "An advanced text input"
      label: "Advanced Text"
      is_required: True
      is_user_input: True
      complex_data_type_name: "lightning__textType"
```

---

## Connection Block

For escalation routing to OmniChannel:

```agentscript
connection messaging:
   outbound_route_type: "OmniChannelFlow"    # MUST be this value!
   outbound_route_name: "Support_Queue_Flow" # Must exist in org
   escalation_message: "Transferring you..."  # REQUIRED field
```

---

## Resource Access

| Resource | Syntax |
|----------|--------|
| Variables | `@variables.name` |
| Actions | `@actions.name` |
| Topics | `@topic.name` |
| Outputs | `@outputs.field` |
| Utilities | `@utils.transition to`, `@utils.escalate` |
