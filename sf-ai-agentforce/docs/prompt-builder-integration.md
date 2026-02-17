<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md, prompt-templates.md -->
<!-- Contains: Prompt Builder (GenAiPromptTemplate) integration with Agentforce agents -->

# Prompt Builder Integration: GenAiPromptTemplate + Agentforce

This document covers how to integrate Prompt Builder templates (`GenAiPromptTemplate`) with Agentforce agents to produce generative AI outputs such as meeting briefings, summaries, analysis, and recommendations.

> **Prerequisite**: Read [prompt-templates.md](prompt-templates.md) first for PromptTemplate metadata fundamentals.
> This document focuses on the **integration patterns** between Prompt Builder and Agentforce -- specifically the `generatePromptResponse://` action target syntax and the `GenAiPromptTemplate` metadata type.

---

## 1. When to Use What -- Decision Tree

Not every agent action needs generative AI. Use the right tool for the job:

```
User request arrives
        |
        v
Is the output deterministic, structured data?
(e.g., "Get me the account details", "Show my open cases")
        |
    YES |                   NO
        v                    |
   Use a Flow               v
   (SOQL query,     Does it require AI-generated
    formatted        narrative or synthesis?
    text output)     (e.g., "Write a briefing", "Summarize activity")
                         |
                     YES |              NO (neither)
                         v               |
                 Is raw data needed       v
                 as input to the      Re-evaluate the
                 AI generation?       requirement
                         |
                     YES |              NO
                         v               v
                  Hybrid Pattern:    Prompt Template
                  Flow gathers       alone (template
                  data, Prompt       has all context
                  Template           via merge fields)
                  generates
                  narrative
```

### Concrete Examples

| Pattern | User Request | Implementation |
|---------|-------------|----------------|
| **Flow** | "Get me the account details for Acme Corp" | Flow runs SOQL, returns structured fields (Name, Industry, Revenue) |
| **Prompt Template** | "Write me a meeting briefing for Acme Corp" | Prompt Template pulls record fields via merge syntax, LLM generates narrative |
| **Hybrid (Flow + Prompt)** | "Summarize this account's recent activity and suggest talking points" | Flow gathers Account fields + related Tasks/Opportunities; Prompt Template synthesizes into narrative briefing |

### Why This Matters

Prompt Builder calls consume Einstein AI credits. Using a Flow for deterministic data retrieval is free and faster. Reserve Prompt Builder for tasks that genuinely require generative AI -- summaries, analysis, recommendations, narrative content.

---

## 2. GenAiPromptTemplate Metadata Deployment

`GenAiPromptTemplate` is the metadata type for Prompt Builder templates. You can create and deploy these via XML metadata files for version control and repeatable deployment.

### File Location

```
force-app/main/default/genAiPromptTemplates/
    TemplateName.promptTemplate-meta.xml
```

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <activeVersionNumber>1</activeVersionNumber>
    <description>Generates a meeting prep briefing for an account</description>
    <masterLabel>Agent Meeting Prep</masterLabel>
    <templateVersions>
        <content>You are a professional account manager assistant.

Generate a comprehensive meeting preparation briefing for the following account.

Account Name: {!$Input:Account.Name}
Industry: {!$Input:Account.Industry}
Annual Revenue: {!$Input:Account.AnnualRevenue}
Billing City: {!$Input:Account.BillingCity}
Account Owner: {!$Input:Account.Owner.Name}

Recent Contacts:
{!$RelatedList:Account.Contacts.Records}

Recent Activities:
{!$RelatedList:Account.Tasks.Records}

Open Opportunities:
{!$RelatedList:Account.Opportunities.Records}

Generate a briefing that includes:
1. Account overview (1-2 sentences)
2. Key contacts and their roles
3. Recent activity summary
4. Open opportunity status
5. Suggested talking points for the meeting
6. Potential risks or concerns

Keep the briefing under 500 words. Use a professional tone.</content>
        <inputDefinitions>
            <description>Salesforce Account record</description>
            <masterLabel>Account</masterLabel>
            <name>Input:Account</name>
            <valueFormatType>RECORD</valueFormatType>
            <valueType>SOBJECT://Account</valueType>
        </inputDefinitions>
        <versionNumber>1</versionNumber>
    </templateVersions>
</GenAiPromptTemplate>
```

### Key Elements

| Element | Description |
|---------|-------------|
| `<activeVersionNumber>` | Which version is currently active (integer) |
| `<description>` | Human-readable description of the template |
| `<masterLabel>` | Display name shown in Prompt Builder UI |
| `<templateVersions>` | Contains one or more versioned templates |
| `<content>` | The actual prompt text with merge field references |
| `<inputDefinitions>` | Declares each input variable the template expects |
| `<valueFormatType>` | How the input is formatted (`RECORD`, `TEXT`, etc.) |
| `<valueType>` | The data type (`SOBJECT://Account`, `STRING`, etc.) |
| `<versionNumber>` | Version number within `templateVersions` |

### Deploy

```bash
sf project deploy start --source-dir force-app/main/default/genAiPromptTemplates
```

---

## 3. Action Syntax for Prompt Templates

This is the most critical section. When connecting a Prompt Builder template to an Agentforce agent, you must use exact syntax in the `.agent` file.

### Complete Action Declaration

```agentscript
generate_meeting_prep:
    description: "Generates a comprehensive meeting prep briefing for an account using AI."
    inputs:
        "Input:Account": object
            complex_data_type_name: "lightning__recordInfoType"
            description: "Salesforce Account record for the account to prepare the briefing for"
    outputs:
        promptResponse: string
            description: "The meeting prep briefing"
    target: "generatePromptResponse://Agent_Meeting_Prep"
```

### Syntax Rules

| Rule | Details |
|------|---------|
| **Target format** | `generatePromptResponse://TemplateName` -- the template API name must match exactly |
| **Input type** | MUST be `object` with `complex_data_type_name: "lightning__recordInfoType"` -- NOT `string` |
| **Input naming** | `"Input:fieldName"` format -- quoted because of the colon character |
| **Output field** | Always `promptResponse: string` -- this is the standard output name for prompt responses |
| **Template name** | The name after `generatePromptResponse://` must match the `masterLabel` or API name of the `GenAiPromptTemplate` in the org |

### Why `object` Type, Not `string`

The Prompt Builder expects a **record reference** -- the actual Account record with all its fields and relationships. If you declare the input as `string`, the agent passes a text value (like an Account ID string). Prompt Builder cannot resolve merge fields like `{!$Input:Account.Name}` from a plain text string. It needs the full record context.

```agentscript
# WRONG -- string type passes text, not a record reference
inputs:
    "Input:Account": string
        description: "Account ID"

# CORRECT -- object type with recordInfoType passes a record reference
inputs:
    "Input:Account": object
        complex_data_type_name: "lightning__recordInfoType"
        description: "Salesforce Account record"
```

---

## 4. Critical Gotchas

These are hard-won lessons from production implementations.

### Gotcha 1: `is_used_by_planner` and `is_displayable` Attributes

The `GenAiPromptTemplate` metadata supports `is_used_by_planner` and `is_displayable` attributes. However, **including them in the prompt template XML causes `SyntaxError` during `sf agent publish authoring-bundle`**.

The `AiAuthoringBundle` validator cannot parse these attributes on GenAiPromptTemplate metadata.

**Solution**: EXCLUDE `is_used_by_planner` and `is_displayable` from your prompt template metadata files entirely. They are only valid on Agent Script action output declarations, not on the template XML itself.

```xml
<!-- WRONG -- these attributes cause SyntaxError at publish time -->
<GenAiPromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <is_used_by_planner>true</is_used_by_planner>
    <is_displayable>true</is_displayable>
    ...
</GenAiPromptTemplate>

<!-- CORRECT -- omit these attributes from template XML -->
<GenAiPromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <activeVersionNumber>1</activeVersionNumber>
    <description>...</description>
    ...
</GenAiPromptTemplate>
```

### Gotcha 2: Prompt Builder UI May Not Work

The Prompt Builder UI at `/lightning/setup/EinsteinPromptStudio/home` may show "Page not found" in some orgs. Even when accessible, the UI can be unreliable for complex templates.

**Recommended path**: Create templates via metadata XML and deploy with `sf project deploy start`. This approach is:
- More reliable than the UI
- Version-controllable in Git
- Repeatable across environments
- Not dependent on UI availability

```bash
# Deploy via metadata (recommended)
sf project deploy start --source-dir force-app/main/default/genAiPromptTemplates

# Verify deployment
sf org list metadata --metadata-type GenAiPromptTemplate --target-org [alias]
```

### Gotcha 3: Input Type Must Be `object`, Not `string`

This is worth repeating because it is the single most common failure when integrating Prompt Builder with Agentforce.

If you declare the input as `string` in the Agent Script action:
- The agent passes a text value (e.g., `"001ABC123DEF"`)
- Prompt Builder receives a string, not a record
- Merge fields like `{!$Input:Account.Name}` cannot resolve
- The prompt generates garbage or errors

If you declare the input as `object` with `complex_data_type_name: "lightning__recordInfoType"`:
- The agent passes a record reference
- Prompt Builder resolves all merge fields correctly
- Related lists and relationship traversals work

### Gotcha 4: Deployment Order

The `GenAiPromptTemplate` must exist in the target org BEFORE you publish or deploy the agent that references it. If the template is missing, you get:

```
Error: We couldn't find the flow, prompt, or apex class: generatePromptResponse://Agent_Meeting_Prep
```

**Deploy order**:
1. Deploy `GenAiPromptTemplate` metadata
2. Deploy any supporting Flows
3. Publish/deploy the Agent

---

## 5. Merge Field Syntax

Inside the prompt template `<content>`, use merge field syntax to reference record data dynamically.

### Record Fields

Direct field references from the input record:

```
{!$Input:Account.Name}
{!$Input:Account.Industry}
{!$Input:Account.AnnualRevenue}
{!$Input:Account.BillingCity}
{!$Input:Account.BillingState}
```

### Relationship Traversal

Access fields on related records via lookup/master-detail relationships:

```
{!$Input:Account.Owner.Name}
{!$Input:Account.Owner.Email}
{!$Input:Account.Parent.Name}
```

### Related Lists

Pull in collections of child records:

```
{!$RelatedList:Account.Contacts.Records}
{!$RelatedList:Account.Tasks.Records}
{!$RelatedList:Account.Opportunities.Records}
{!$RelatedList:Account.Cases.Records}
```

### System Values

Reference system-level context:

```
{!$Flow.CurrentDate}
```

### Merge Field Mapping

The merge fields in the template content map to the `inputDefinitions` in the XML:

```
Template content field          inputDefinitions name
------------------------------  ---------------------
{!$Input:Account.Name}     -->  Input:Account  (the Account record)
{!$Input:Account.Industry} -->  Input:Account  (same record, different field)
```

A single `inputDefinitions` entry for `Input:Account` enables access to ALL fields and relationships on that Account record.

---

## 6. Complete Working Example -- Meeting Prep Action

This example shows the full integration pattern: GenAiPromptTemplate metadata, Agent Script action declaration, and topic reasoning that ties them together.

### Step 1: GenAiPromptTemplate Metadata

**File**: `force-app/main/default/genAiPromptTemplates/Agent_Meeting_Prep.promptTemplate-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPromptTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <activeVersionNumber>1</activeVersionNumber>
    <description>Generates a comprehensive meeting prep briefing for an account, including key contacts, recent activity, and suggested talking points.</description>
    <masterLabel>Agent Meeting Prep</masterLabel>
    <templateVersions>
        <content>You are a professional account manager assistant preparing a meeting briefing.

Generate a comprehensive meeting preparation briefing for the following account.

ACCOUNT INFORMATION
Account Name: {!$Input:Account.Name}
Industry: {!$Input:Account.Industry}
Annual Revenue: {!$Input:Account.AnnualRevenue}
Billing Location: {!$Input:Account.BillingCity}, {!$Input:Account.BillingState}
Account Owner: {!$Input:Account.Owner.Name}
Website: {!$Input:Account.Website}

KEY CONTACTS
{!$RelatedList:Account.Contacts.Records}

RECENT ACTIVITIES (Last 90 Days)
{!$RelatedList:Account.Tasks.Records}

OPEN OPPORTUNITIES
{!$RelatedList:Account.Opportunities.Records}

RECENT CASES
{!$RelatedList:Account.Cases.Records}

Generate a briefing with these sections:
1. ACCOUNT OVERVIEW - 2-3 sentence summary of the account
2. KEY CONTACTS - Who to expect in the meeting and their roles
3. RELATIONSHIP HEALTH - Summary of recent interactions and engagement level
4. ACTIVE DEALS - Status of open opportunities and pipeline
5. OPEN ISSUES - Any unresolved cases or concerns
6. TALKING POINTS - 3-5 recommended topics for the meeting
7. RISKS AND WATCH ITEMS - Anything to be cautious about

Keep the briefing under 500 words. Use a professional, concise tone. Format with clear section headers.</content>
        <inputDefinitions>
            <description>The Salesforce Account record to generate the briefing for</description>
            <masterLabel>Account</masterLabel>
            <name>Input:Account</name>
            <valueFormatType>RECORD</valueFormatType>
            <valueType>SOBJECT://Account</valueType>
        </inputDefinitions>
        <versionNumber>1</versionNumber>
    </templateVersions>
</GenAiPromptTemplate>
```

### Step 2: Agent Script Action Declaration

Define the prompt template action in the agent's topic:

```agentscript
topic meeting_prep:
    label: "Meeting Prep"
    description: "Generates meeting preparation briefings for customer accounts"

    actions:
        get_account_details:
            description: "Retrieves account information by name or ID"
            inputs:
                inp_AccountNameOrId: string
                    description: "The account name or Salesforce Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_AccountId: string
                    description: "The Salesforce Account ID"
            target: "flow://Agent_Get_Account_Details"

        generate_meeting_prep:
            description: "Generates a comprehensive meeting prep briefing for an account using AI."
            inputs:
                "Input:Account": object
                    complex_data_type_name: "lightning__recordInfoType"
                    description: "Salesforce Account record for the account to prepare the briefing for"
            outputs:
                promptResponse: string
                    description: "The meeting prep briefing"
            target: "generatePromptResponse://Agent_Meeting_Prep"

    reasoning:
        instructions: ->
            | Generate a meeting prep briefing for the user.
            | If the user mentions an account name and current_account_id is not set,
            | first look up the account using get_account_details.
            | After getting the Account ID, call generate_meeting_prep to produce the briefing.
            | Present the full briefing to the user.
        actions:
            lookup_account: @actions.get_account_details
                with inp_AccountNameOrId=...
                set @variables.current_account_name = @outputs.out_AccountName
                set @variables.current_account_id = @outputs.out_AccountId

            prep_briefing: @actions.generate_meeting_prep
                with "Input:Account"=@variables.current_account_id
```

### Step 3: Topic Reasoning Flow

The reasoning follows this sequence:

```
1. User: "Prep me for my meeting with Acme Corp"
        |
        v
2. Agent determines current_account_id is not set
        |
        v
3. Agent calls get_account_details (Flow action)
   with inp_AccountNameOrId = "Acme Corp"
        |
        v
4. Flow returns Account ID + Name
   Agent sets @variables.current_account_id
        |
        v
5. Agent calls generate_meeting_prep (Prompt Template action)
   with "Input:Account" = @variables.current_account_id
        |
        v
6. Prompt Builder resolves all merge fields from the Account record,
   generates the narrative briefing via LLM
        |
        v
7. Agent presents the briefing to the user
```

### Step 4: Deploy

```bash
# 1. Deploy the prompt template first
sf project deploy start --source-dir force-app/main/default/genAiPromptTemplates --target-org [alias]

# 2. Deploy the Flow (if not already deployed)
sf project deploy start --source-dir force-app/main/default/flows --target-org [alias]

# 3. Validate the agent
sf agent validate authoring-bundle --api-name My_Agent --target-org [alias]

# 4. Publish the agent
sf agent publish authoring-bundle --api-name My_Agent --target-org [alias]
```

---

## 7. Hybrid Pattern: Flow + Prompt Template

For use cases where you need both deterministic data retrieval AND generative AI synthesis, use the hybrid pattern.

### When to Use

- "Summarize this account's recent activity and suggest talking points"
- "Analyze our pipeline and recommend focus areas"
- "Review this customer's case history and identify trends"

### Architecture

```
User Request
    |
    v
Agent Topic
    |
    ├── Action 1: Flow (data retrieval)
    |   - Runs SOQL queries
    |   - Gathers structured data
    |   - Returns fields to agent variables
    |
    └── Action 2: Prompt Template (AI synthesis)
        - Receives record reference
        - Resolves merge fields (including related lists)
        - LLM generates narrative from data
        - Returns promptResponse
```

### Example: Account Activity Summary

```agentscript
topic activity_summary:
    label: "Activity Summary"
    description: "Summarizes account activity and suggests next steps"

    actions:
        get_account:
            description: "Retrieves account details by name"
            inputs:
                inp_AccountName: string
                    description: "Account name to look up"
            outputs:
                out_AccountId: string
                    description: "The Account record ID"
                out_AccountName: string
                    description: "The account name"
            target: "flow://Agent_Get_Account_Details"

        summarize_activity:
            description: "Uses AI to summarize recent account activity and generate recommendations"
            inputs:
                "Input:Account": object
                    complex_data_type_name: "lightning__recordInfoType"
                    description: "Account record to summarize"
            outputs:
                promptResponse: string
                    description: "AI-generated activity summary with recommendations"
            target: "generatePromptResponse://Account_Activity_Summary"

    reasoning:
        instructions: ->
            | Help the user understand recent activity on an account.
            | First look up the account, then generate an AI-powered summary.
            | The summary includes recent tasks, opportunities, cases, and
            | AI-generated recommendations for next steps.
        actions:
            find_account: @actions.get_account
                with inp_AccountName=...
                set @variables.current_account_id = @outputs.out_AccountId

            generate_summary: @actions.summarize_activity
                with "Input:Account"=@variables.current_account_id
```

In this pattern, the Flow handles the deterministic lookup (finding the Account by name, getting the ID), while the Prompt Template handles the generative synthesis (summarizing activity, suggesting next steps).

---

## Related Documentation

- [prompt-templates.md](prompt-templates.md) -- PromptTemplate metadata fundamentals and variable types
- [actions-reference.md](actions-reference.md) -- Complete action type reference
- [action-invocation-patterns.md](action-invocation-patterns.md) -- Fixing doomprompting and action invocation reliability
- [patterns-and-practices.md](patterns-and-practices.md) -- Decision tree and best practices
