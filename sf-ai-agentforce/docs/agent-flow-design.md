# Agent Flow Design Patterns

Comprehensive guide for designing Salesforce Flows that serve as actions for Agentforce agents. These patterns are derived from a production deployment with 10 agent flows and cover naming conventions, architectural decisions, common workarounds, and pre-publish validation.

---

## Table of Contents

1. [Naming Conventions](#1-naming-conventions)
2. [Read-Only Pattern](#2-read-only-pattern)
3. [Formatted Text Output](#3-formatted-text-output)
4. [Session Variables for Context](#4-session-variables-for-context)
5. [ID vs Name Detection](#5-id-vs-name-detection)
6. [Date Filtering](#6-date-filtering)
7. [RecordTypeId Workaround](#7-recordtypeid-workaround)
8. [Loop Counter Pattern](#8-loop-counter-pattern)
9. [Action Reuse Across Topics](#9-action-reuse-across-topics)
10. [Pre-Publish Checklist](#10-pre-publish-checklist)

---

## 1. Naming Conventions

Consistent naming makes flows discoverable in Setup, keeps Agent Script action definitions readable, and avoids confusion when the same flow is reused across multiple topics.

### Flow Names

Use the pattern `Agent_<Verb>_<Noun>` or `Agent_Get_<EntityOrAction>`:

| Flow API Name | Purpose |
|---|---|
| `Agent_Get_Account_Details` | Retrieve account record with multiple output fields |
| `Agent_Get_Account_Contacts` | List contacts associated with an account |
| `Agent_Get_Account_Activity` | Recent tasks and events for an account |
| `Agent_Get_Onboarding_Status` | Progress counters for onboarding checklist |
| `Agent_Get_Document_Checklist` | List document checklist items and their statuses |
| `Agent_Get_Relationship_Map` | Parent/subsidiary account relationships |
| `Agent_Get_Contact_Roles` | Contact roles with gap analysis |
| `Agent_Get_Stale_Accounts` | Accounts with no recent activity (date filter + owner filter) |
| `Agent_Get_Alliance_Network` | Relationship traversal across partner accounts |
| `Agent_Get_Portfolio_Summary` | Aggregated metrics across an owner's accounts |

### Input Variables

Prefix all input variables with `inp_`:

| Variable Name | Data Type | Description |
|---|---|---|
| `inp_AccountId` | String | Salesforce 18-character Account ID |
| `inp_AccountNameOrId` | String | Accepts either account name or ID (see [Section 5](#5-id-vs-name-detection)) |
| `inp_OwnerId` | String | User ID of the account owner |
| `inp_ContactId` | String | Salesforce Contact ID |
| `inp_RecordTypeName` | String | DeveloperName of the desired RecordType |

### Output Variables

Prefix all output variables with `out_`:

| Variable Name | Data Type | Description |
|---|---|---|
| `out_Summary` | String | Formatted text the agent displays directly |
| `out_ContactList` | String | Formatted multi-line list of contacts |
| `out_IsFound` | Boolean | Whether the primary record was found |
| `out_AccountId` | String | Resolved Account ID (for session variable capture) |
| `out_AccountName` | String | Resolved Account Name |
| `out_ItemsCompleted` | Number | Count of completed items |
| `out_ItemsTotal` | Number | Total count of items |

### Why This Convention Matters

- **Discoverability**: All agent flows sort together in Setup when prefixed with `Agent_`.
- **Clarity**: `inp_` and `out_` make it immediately clear which variables are inputs vs outputs when reading Flow XML or Agent Script action definitions.
- **Matching**: Agent Script input/output names **must exactly match** Flow variable API names. A consistent prefix eliminates guesswork.

---

## 2. Read-Only Pattern

Agent flows query data. They do **not** create, update, or delete records.

### Architectural Principle

All record operations use `recordLookups` (Get Records elements). Agent flows never contain `recordCreates`, `recordUpdates`, or `recordDeletes` elements. This is a deliberate design choice:

- **Risk Minimization**: An agent operating on natural language input should not perform destructive operations. Misinterpreted instructions could modify or delete the wrong records.
- **Auditability**: Read-only flows produce no side effects, making them safe to call repeatedly during agent reasoning without concern for duplicate DML.
- **User Control**: When the agent determines that a user wants to take action (create a case, update a field, reassign an owner), it should guide them to the appropriate screen in Salesforce or escalate to a human rather than performing the operation autonomously.

### What This Looks Like in Flow XML

```xml
<!-- CORRECT: Read-only agent flow uses only recordLookups -->
<recordLookups>
    <name>Get_Account</name>
    <object>Account</object>
    <filters>
        <field>Id</field>
        <operator>EqualTo</operator>
        <value><elementReference>inp_AccountId</elementReference></value>
    </filters>
    <getFirstRecordOnly>true</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>

<!-- NEVER in an agent flow -->
<!-- <recordCreates>...</recordCreates>   -->
<!-- <recordUpdates>...</recordUpdates>   -->
<!-- <recordDeletes>...</recordDeletes>   -->
```

### When Write Operations Are Needed

If a business requirement demands that the agent perform a write operation (e.g., logging a task, creating a case), isolate it in a **separate** flow with its own topic and action definition. This separation ensures:

1. The write flow can have `require_user_confirmation: True` in Agent Script
2. The agent explicitly asks the user to confirm before executing
3. Read flows remain safe to call without confirmation prompts

---

## 3. Formatted Text Output

Agent flows return **formatted text strings**, not raw record data. The agent displays the output directly to the user, so the flow is responsible for assembling a human-readable response.

### Pattern Overview

1. Query records with a `recordLookups` element
2. Loop through results
3. Build formatted text using a `textTemplates` element inside the loop
4. Concatenate each row onto an output variable using an `assignments` element
5. Return a single `out_Summary` or `out_ContactList` string

### Example: Contact List Formatting

```xml
<!-- Text template for each contact row -->
<textTemplates>
    <name>ContactRow</name>
    <isViewedAsPlainText>true</isViewedAsPlainText>
    <text>{!Loop_Contact.Name} -- {!Loop_Contact.Title} -- {!Loop_Contact.Email} -- {!Loop_Contact.Phone}</text>
</textTemplates>

<!-- Loop through contacts -->
<loops>
    <name>Loop_Contacts</name>
    <collectionReference>Get_Contacts</collectionReference>
    <iterationOrder>Asc</iterationOrder>
    <nextValueConnector>
        <targetReference>Assign_Contact_Row</targetReference>
    </nextValueConnector>
    <noMoreValuesConnector>
        <targetReference>Set_Output</targetReference>
    </noMoreValuesConnector>
</loops>

<!-- Concatenate each row -->
<assignments>
    <name>Assign_Contact_Row</name>
    <assignmentItems>
        <assignToReference>out_ContactList</assignToReference>
        <operator>Add</operator>
        <value><elementReference>ContactRow</elementReference></value>
    </assignmentItems>
    <assignmentItems>
        <assignToReference>out_ContactList</assignToReference>
        <operator>Add</operator>
        <value><stringValue>
</stringValue></value>
    </assignmentItems>
    <connector>
        <targetReference>Loop_Contacts</targetReference>
    </connector>
</assignments>
```

### Output Example

When the agent displays the result, the user sees:

```
Jane Smith -- VP of Operations -- jane.smith@acme.com -- (555) 123-4567
Bob Johnson -- CFO -- bob.johnson@acme.com -- (555) 234-5678
Alice Williams -- Director of IT -- alice.w@acme.com -- (555) 345-6789
```

### Why Formatted Text Instead of Raw Records

- **Agent Display**: The agent presents text to users in a chat interface. Raw SObject data would require the agent's LLM to format it, adding latency and inconsistency.
- **Consistency**: The flow controls the exact format, ensuring every response looks the same regardless of how the LLM interprets the data.
- **Token Efficiency**: A pre-formatted string is smaller than a serialized SObject with dozens of null fields, reducing token consumption in the agent's context window.

---

## 4. Session Variables for Context

Agentforce agents support **session variables** that persist across multiple turns of conversation. The first action in a conversation captures identifying information (like account name and ID), and all subsequent actions bind to those variables automatically.

### Variable Lifecycle

```
Turn 1: User says "Tell me about Acme Corp"
  |
  v
Agent calls Agent_Get_Account_Details
  with inp_AccountNameOrId = "Acme Corp"
  |
  v
Flow returns out_AccountId = "001XX0000012345" and out_AccountName = "Acme Corp"
  |
  v
Agent captures session variables:
  set @variables.current_account_id = @outputs.out_AccountId
  set @variables.current_account_name = @outputs.out_AccountName
  |
  v
Turn 2: User says "Who are the contacts?"
  |
  v
Agent calls Agent_Get_Account_Contacts
  with inp_AccountId = @variables.current_account_id    <-- No need to re-ask!
  |
  v
Turn 3: User says "What's the onboarding status?"
  |
  v
Agent calls Agent_Get_Onboarding_Status
  with inp_AccountId = @variables.current_account_id    <-- Still bound!
```

### Agent Script Variable Declaration

```agentscript
variables:
    current_account_id: mutable string
        description: "The Salesforce Account ID for the current conversation context"
    current_account_name: mutable string
        description: "The account name for the current conversation context"
```

### Agent Script Action with Variable Capture

```agentscript
topic account_intel:
    label: "Account Intelligence"
    description: "Provides account details, contacts, activity, and portfolio data"

    actions:
        get_account_details:
            description: "Look up an account by name or ID and return key details"
            inputs:
                inp_AccountNameOrId: string
                    description: "The account name or Salesforce Account ID"
            outputs:
                out_AccountId: string
                    description: "The resolved Salesforce Account ID"
                out_AccountName: string
                    description: "The resolved account name"
                out_Summary: string
                    description: "Formatted account details"
            target: "flow://Agent_Get_Account_Details"

    reasoning:
        instructions: ->
            | When the user asks about an account:
            | 1. Use get_account_details to look up the account
            | 2. Capture the account ID for follow-up questions
            |
            | After calling get_account_details:
            |    set @variables.current_account_id = @outputs.out_AccountId
            |    set @variables.current_account_name = @outputs.out_AccountName
```

### Design Considerations

- **First Action Resolves Identity**: The first flow in a conversation should accept flexible input (name or ID) and return both the resolved ID and name.
- **Subsequent Actions Use ID Only**: Follow-up flows accept `inp_AccountId` (not name) since the ID is already captured.
- **Multi-Turn Without Repetition**: Users should never have to repeat which account they are asking about. The session variable eliminates this friction.

---

## 5. ID vs Name Detection

When a flow accepts either a Salesforce record name or an 18-character ID, use a formula variable to detect which was provided and route to the appropriate lookup.

### Formula: Detect ID by Key Prefix

```xml
<formulas>
    <name>formula_IsId</name>
    <dataType>Boolean</dataType>
    <expression>LEFT({!inp_AccountNameOrId}, 3) = '001'</expression>
</formulas>
```

The `001` prefix is the standard Salesforce key prefix for Account records. If the first three characters match, the input is an Account ID. Otherwise, treat it as a name search.

### Decision Element

```xml
<decisions>
    <name>Check_Input_Type</name>
    <defaultConnector>
        <targetReference>Get_Account_By_Name</targetReference>
    </defaultConnector>
    <defaultConnectorLabel>Name Search</defaultConnectorLabel>
    <rules>
        <name>Is_Account_Id</name>
        <conditionLogic>and</conditionLogic>
        <conditions>
            <leftValueReference>formula_IsId</leftValueReference>
            <operator>EqualTo</operator>
            <rightValue><booleanValue>true</booleanValue></rightValue>
        </conditions>
        <connector>
            <targetReference>Get_Account_By_Id</targetReference>
        </connector>
        <label>Is Account ID</label>
    </rules>
</decisions>
```

### Two Lookup Paths

**Path A: ID-based lookup (exact match)**

```xml
<recordLookups>
    <name>Get_Account_By_Id</name>
    <object>Account</object>
    <filters>
        <field>Id</field>
        <operator>EqualTo</operator>
        <value><elementReference>inp_AccountNameOrId</elementReference></value>
    </filters>
    <getFirstRecordOnly>true</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

**Path B: Name-based lookup (CONTAINS search)**

```xml
<recordLookups>
    <name>Get_Account_By_Name</name>
    <object>Account</object>
    <filters>
        <field>Name</field>
        <operator>Contains</operator>
        <value><elementReference>inp_AccountNameOrId</elementReference></value>
    </filters>
    <getFirstRecordOnly>true</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

### Common Key Prefixes

| Object | Key Prefix | Example |
|---|---|---|
| Account | `001` | `001XX0000012345AAA` |
| Contact | `003` | `003XX0000067890BBB` |
| Opportunity | `006` | `006XX0000034567CCC` |
| Case | `500` | `500XX0000045678DDD` |
| Lead | `00Q` | `00QXX0000056789EEE` |
| User | `005` | `005XX0000023456FFF` |

If the flow supports multiple object types, extend the formula:

```xml
<formulas>
    <name>formula_IsId</name>
    <dataType>Boolean</dataType>
    <expression>OR(
        LEFT({!inp_AccountNameOrId}, 3) = '001',
        LEN({!inp_AccountNameOrId}) = 18
    )</expression>
</formulas>
```

---

## 6. Date Filtering

Many agent flows need to retrieve recent activity: tasks logged in the last 30 days, events in the next 7 days, accounts not touched in 90 days. Use formula variables to compute date boundaries.

### Formula: Rolling Date Window

```xml
<formulas>
    <name>formula_ThirtyDaysAgo</name>
    <dataType>Date</dataType>
    <expression>{!$Flow.CurrentDate} - 30</expression>
</formulas>
```

### Using the Date Filter in a Record Lookup

```xml
<recordLookups>
    <name>Get_Recent_Tasks</name>
    <object>Task</object>
    <filters>
        <field>WhatId</field>
        <operator>EqualTo</operator>
        <value><elementReference>inp_AccountId</elementReference></value>
    </filters>
    <filters>
        <field>CreatedDate</field>
        <operator>GreaterThanOrEqualTo</operator>
        <value><elementReference>formula_ThirtyDaysAgo</elementReference></value>
    </filters>
    <sortField>CreatedDate</sortField>
    <sortOrder>Desc</sortOrder>
    <getFirstRecordOnly>false</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

### Common Date Formulas

| Formula Name | Expression | Use Case |
|---|---|---|
| `formula_ThirtyDaysAgo` | `{!$Flow.CurrentDate} - 30` | Recent activity lookups |
| `formula_SevenDaysAgo` | `{!$Flow.CurrentDate} - 7` | Last-week activity |
| `formula_NinetyDaysAgo` | `{!$Flow.CurrentDate} - 90` | Stale account detection |
| `formula_SevenDaysFromNow` | `{!$Flow.CurrentDate} + 7` | Upcoming events/deadlines |
| `formula_StartOfQuarter` | See note below | Quarterly reporting |

**Note on Quarter Calculations**: Flow formulas do not have a native "start of quarter" function. Compute it with:
```
DATE(YEAR({!$Flow.CurrentDate}),
     (CEILING(MONTH({!$Flow.CurrentDate}) / 3) - 1) * 3 + 1,
     1)
```

### Stale Account Pattern

The `Agent_Get_Stale_Accounts` flow combines date filtering with an owner filter to find accounts that need attention:

```xml
<!-- Formula: 90 days ago -->
<formulas>
    <name>formula_NinetyDaysAgo</name>
    <dataType>Date</dataType>
    <expression>{!$Flow.CurrentDate} - 90</expression>
</formulas>

<!-- Get accounts where LastActivityDate is before 90 days ago -->
<recordLookups>
    <name>Get_Stale_Accounts</name>
    <object>Account</object>
    <filters>
        <field>OwnerId</field>
        <operator>EqualTo</operator>
        <value><elementReference>inp_OwnerId</elementReference></value>
    </filters>
    <filters>
        <field>LastActivityDate</field>
        <operator>LessThan</operator>
        <value><elementReference>formula_NinetyDaysAgo</elementReference></value>
    </filters>
    <getFirstRecordOnly>false</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

---

## 7. RecordTypeId Workaround

**CRITICAL GOTCHA**: Flow record lookup filters do **NOT** support cross-object references like `RecordType.DeveloperName`. Attempting to filter on a related object field in a `recordLookups` element causes an `UNKNOWN_EXCEPTION` at runtime.

### What Fails

```xml
<!-- DO NOT DO THIS -- causes UNKNOWN_EXCEPTION at runtime -->
<recordLookups>
    <name>Get_Accounts_By_Type</name>
    <object>Account</object>
    <filters>
        <field>RecordType.DeveloperName</field>
        <operator>EqualTo</operator>
        <value>
            <stringValue>Customer_Standard</stringValue>
        </value>
    </filters>
</recordLookups>
```

This compiles and deploys without error but **fails silently at runtime** with a generic `UNKNOWN_EXCEPTION`, making it extremely difficult to debug.

### Workaround: Use the RecordTypeId Directly

```xml
<!-- CORRECT: Use the actual RecordTypeId -->
<recordLookups>
    <name>Get_Accounts_By_Type</name>
    <object>Account</object>
    <filters>
        <field>RecordTypeId</field>
        <operator>EqualTo</operator>
        <value>
            <stringValue>012000000000000AAA</stringValue>
        </value>
    </filters>
    <getFirstRecordOnly>false</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

### Important Caveats

1. **Org-Specific**: RecordTypeId values differ between sandboxes and production. The ID `012000000000000AAA` above is a placeholder -- you must query the actual ID for each environment.

2. **Query the ID**: Use this SOQL to find the correct RecordTypeId:
   ```sql
   SELECT Id, DeveloperName, Name
   FROM RecordType
   WHERE SObjectType = 'Account'
     AND DeveloperName = 'Customer_Standard'
   ```

3. **Environment Management**: Consider these strategies for managing org-specific IDs:
   - **Custom Metadata Type**: Store RecordTypeId values in a Custom Metadata record, query it in the flow, and use the variable in the filter. This is the most portable approach.
   - **Custom Label**: Store the ID in a Custom Label and reference `{!$Label.AccountRecordTypeId}` in the flow.
   - **Hardcode with Comments**: If the org topology is simple (one sandbox, one production), hardcode the ID with an XML comment documenting which RecordType it represents.

### Alternative: Query RecordType First

Instead of hardcoding, add a preliminary `recordLookups` to fetch the RecordTypeId dynamically:

```xml
<!-- Step 1: Look up the RecordType by DeveloperName -->
<recordLookups>
    <name>Get_RecordType</name>
    <object>RecordType</object>
    <filters>
        <field>SObjectType</field>
        <operator>EqualTo</operator>
        <value><stringValue>Account</stringValue></value>
    </filters>
    <filters>
        <field>DeveloperName</field>
        <operator>EqualTo</operator>
        <value><stringValue>Customer_Standard</stringValue></value>
    </filters>
    <getFirstRecordOnly>true</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>

<!-- Step 2: Use the resolved ID in the actual lookup -->
<recordLookups>
    <name>Get_Accounts_By_Type</name>
    <object>Account</object>
    <filters>
        <field>RecordTypeId</field>
        <operator>EqualTo</operator>
        <value><elementReference>Get_RecordType.Id</elementReference></value>
    </filters>
    <getFirstRecordOnly>false</getFirstRecordOnly>
    <storeOutputAutomatically>true</storeOutputAutomatically>
</recordLookups>
```

This adds one extra SOQL query but eliminates hardcoded IDs entirely.

---

## 8. Loop Counter Pattern

Flow `recordLookups` elements do not support `GROUP BY` or aggregate functions like `COUNT()`. When you need to count records or compute status breakdowns, use Assignment elements inside a Loop to manually tally results.

### Pattern: Counting Completed vs Total Items

**Variables (initialize before the loop):**

```xml
<variables>
    <name>var_CompletedCount</name>
    <dataType>Number</dataType>
    <isCollection>false</isCollection>
    <isInput>false</isInput>
    <isOutput>false</isOutput>
    <scale>0</scale>
    <value><numberValue>0</numberValue></value>
</variables>
<variables>
    <name>var_TotalCount</name>
    <dataType>Number</dataType>
    <isCollection>false</isCollection>
    <isInput>false</isInput>
    <isOutput>false</isOutput>
    <scale>0</scale>
    <value><numberValue>0</numberValue></value>
</variables>
```

**Loop with conditional increment:**

```xml
<loops>
    <name>Loop_Checklist_Items</name>
    <collectionReference>Get_Checklist_Items</collectionReference>
    <iterationOrder>Asc</iterationOrder>
    <nextValueConnector>
        <targetReference>Increment_Total</targetReference>
    </nextValueConnector>
    <noMoreValuesConnector>
        <targetReference>Set_Outputs</targetReference>
    </noMoreValuesConnector>
</loops>

<!-- Always increment total -->
<assignments>
    <name>Increment_Total</name>
    <assignmentItems>
        <assignToReference>var_TotalCount</assignToReference>
        <operator>Add</operator>
        <value><numberValue>1</numberValue></value>
    </assignmentItems>
    <connector>
        <targetReference>Check_If_Completed</targetReference>
    </connector>
</assignments>

<!-- Decision: is this item completed? -->
<decisions>
    <name>Check_If_Completed</name>
    <defaultConnector>
        <targetReference>Loop_Checklist_Items</targetReference>
    </defaultConnector>
    <defaultConnectorLabel>Not Completed</defaultConnectorLabel>
    <rules>
        <name>Is_Completed</name>
        <conditionLogic>and</conditionLogic>
        <conditions>
            <leftValueReference>Loop_Checklist_Items.Status</leftValueReference>
            <operator>EqualTo</operator>
            <rightValue><stringValue>Completed</stringValue></rightValue>
        </conditions>
        <connector>
            <targetReference>Increment_Completed</targetReference>
        </connector>
        <label>Completed</label>
    </rules>
</decisions>

<!-- Increment completed count -->
<assignments>
    <name>Increment_Completed</name>
    <assignmentItems>
        <assignToReference>var_CompletedCount</assignToReference>
        <operator>Add</operator>
        <value><numberValue>1</numberValue></value>
    </assignmentItems>
    <connector>
        <targetReference>Loop_Checklist_Items</targetReference>
    </connector>
</assignments>
```

**Set output variables after the loop:**

```xml
<assignments>
    <name>Set_Outputs</name>
    <assignmentItems>
        <assignToReference>out_ItemsCompleted</assignToReference>
        <operator>Assign</operator>
        <value><elementReference>var_CompletedCount</elementReference></value>
    </assignmentItems>
    <assignmentItems>
        <assignToReference>out_ItemsTotal</assignToReference>
        <operator>Assign</operator>
        <value><elementReference>var_TotalCount</elementReference></value>
    </assignmentItems>
</assignments>
```

### Combining Counters with Formatted Text

The onboarding status flow combines this counting pattern with the formatted text output pattern from [Section 3](#3-formatted-text-output). After the loop completes, it builds a summary like:

```
Onboarding Progress: 7 of 10 items completed (70%)

Pending Items:
- Upload W-9 form -- Due: 2026-02-28
- Complete compliance training -- Due: 2026-03-15
- Sign service agreement -- Due: 2026-03-01
```

Use a formula to compute the percentage:

```xml
<formulas>
    <name>formula_PercentComplete</name>
    <dataType>Number</dataType>
    <expression>IF({!var_TotalCount} > 0,
        ROUND(({!var_CompletedCount} / {!var_TotalCount}) * 100, 0),
        0)</expression>
    <scale>0</scale>
</formulas>
```

---

## 9. Action Reuse Across Topics

A single flow can be declared as an action in **multiple topics**. This is common when a foundational lookup (like resolving an account by name or ID) is needed as a prerequisite in several different conversation contexts.

### Example: Agent_Get_Account_Details Across 4 Topics

The account details flow is the most reused action. It resolves an account name or ID and returns key details. It appears identically in:

| Topic | Why It Needs Account Lookup |
|---|---|
| `account_intel` | Primary lookup -- the user is asking about an account directly |
| `onboarding_status` | Must resolve the account before querying onboarding checklist items |
| `meeting_prep` | Must resolve the account before generating a meeting briefing |
| `relationship_advisor` | Must resolve the account before analyzing relationship data |

### Action Definition (Identical in Each Topic)

The action definition is **copy-pasted verbatim** into each topic. There is no inheritance or reference mechanism in Agent Script -- each topic declares its own actions independently.

```agentscript
# This exact block appears in EACH of the 4 topics above
actions:
    get_account_details:
        description: "Look up an account by name or Salesforce ID. Returns account details including name, status, tier, owner, and key metrics."
        inputs:
            inp_AccountNameOrId: string
                description: "The account name or 18-character Salesforce Account ID"
        outputs:
            out_AccountId: string
                description: "The resolved Salesforce Account ID"
            out_AccountName: string
                description: "The resolved account name"
            out_Summary: string
                description: "Formatted account details summary"
            out_IsFound: boolean
                description: "Whether the account was found"
        target: "flow://Agent_Get_Account_Details"
```

### Design Considerations

- **Copy, Do Not Abstract**: Agent Script does not support shared action definitions or imports. Accept the duplication. Keeping each topic self-contained makes it easier to add or remove topics without side effects.
- **Session Variable Capture**: Each topic should capture `@variables.current_account_id` after calling the action. This ensures that no matter which topic the user enters through, the account context is set for follow-up questions.
- **Description Consistency**: Use the same `description` text in every topic. The LLM uses this description to decide when to call the action; inconsistent descriptions across topics could cause unpredictable behavior.

---

## 10. Pre-Publish Checklist

Before publishing the agent with `sf agent publish authoring-bundle`, verify every flow against this checklist.

### Flow Configuration

- [ ] **Process Type**: `AutoLaunchedFlow` (not Screen Flow, not Record-Triggered Flow)
  ```xml
  <processType>AutoLaunchedFlow</processType>
  ```
- [ ] **Status**: Active (flows may deploy as Draft or Inactive -- check in Setup > Flows)
  ```xml
  <status>Active</status>
  ```
- [ ] **API Version**: 65.0 or higher
  ```xml
  <apiVersion>65.0</apiVersion>
  ```

### Variable Configuration

- [ ] All **input variables** are marked `isInput: true`
  ```xml
  <variables>
      <name>inp_AccountId</name>
      <dataType>String</dataType>
      <isInput>true</isInput>
      <isOutput>false</isOutput>
  </variables>
  ```
- [ ] All **output variables** are marked `isOutput: true`
  ```xml
  <variables>
      <name>out_Summary</name>
      <dataType>String</dataType>
      <isInput>false</isInput>
      <isOutput>true</isOutput>
  </variables>
  ```
- [ ] Variable names match Agent Script action definitions **exactly** (case-sensitive)

### Deployment Order

- [ ] All flows are **deployed to the org** before running `sf agent publish authoring-bundle`
  ```bash
  # Deploy flows first
  sf project deploy start --source-dir force-app/main/default/flows --target-org [alias]

  # Then publish agent
  sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]
  ```
- [ ] Any RecordTypeId values have been updated for the target environment (see [Section 7](#7-recordtypeid-workaround))
- [ ] Any Custom Metadata or Custom Labels referenced by flows exist in the target org

### Agent Script Validation

- [ ] Agent Script `sf agent validate authoring-bundle` passes with 0 errors
- [ ] All `target: "flow://FlowApiName"` references match deployed flow API names
- [ ] All `inputs:` and `outputs:` names match the corresponding flow variable names exactly
- [ ] No reserved words (`description`, `inputs`, `outputs`, `target`, `label`, `source`) used as parameter names

### Quick Validation Command Sequence

```bash
# 1. Deploy all flows
sf project deploy start --source-dir force-app/main/default/flows --target-org [alias]

# 2. Validate agent syntax
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# 3. Publish agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# 4. Verify agent is visible in Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# 5. Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Common Publish Failures

| Error | Cause | Fix |
|---|---|---|
| `We couldn't find the flow` | Flow not deployed or API name mismatch | Deploy flow first; verify API name matches `target:` |
| `Internal Error, try again later` | Input/output name mismatch between Agent Script and Flow | Verify all variable names match exactly (case-sensitive) |
| `UNKNOWN_EXCEPTION` | Cross-object filter in recordLookups (e.g., RecordType.DeveloperName) | Use RecordTypeId directly (see [Section 7](#7-recordtypeid-workaround)) |
| `HTTP 404` during publish | Known CLI issue | Run `sf project deploy start --source-dir` after publish to deploy metadata |
| Flow shows as "Inactive" | Flow deployed but not activated | Activate the flow in Setup > Flows or set `<status>Active</status>` in XML |
