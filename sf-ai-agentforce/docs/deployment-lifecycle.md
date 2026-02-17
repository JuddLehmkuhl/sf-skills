<!-- TIER: 3 | DETAILED REFERENCE -->
<!-- Read after: SKILL.md, cli-guide.md, patterns-and-practices.md -->
<!-- Contains: Full deployment lifecycle for Agentforce agents, from rollout through iterative refinement -->

# Deployment Lifecycle: From First Deploy to Production Stability

This document covers the full lifecycle of deploying Agentforce agents -- from the initial rollout strategy through iterative refinement, version management, and production verification. The patterns here are derived from production experience and reflect the reality that agent development is inherently iterative.

---

## 1. Wave-Based Rollout Strategy

Do not ship the entire agent at once. Deploy in waves, starting small and expanding.

### Wave 1: Core Agent + Primary Flows

Ship the minimum viable agent: the core agent definition with 3-4 primary flows that cover the most critical functionality (e.g., account lookup, basic data retrieval, one key workflow).

The goal of Wave 1 is to get the agent working end-to-end before adding complexity:

- Deploy the agent with 1-2 topics maximum
- Include only the actions that those topics need
- Verify the agent can route to the correct topic, invoke actions, and return real data
- Fix hallucination, routing, and action invocation issues at this stage (they are easier to debug with fewer topics)

**Ship it, test it, fix it.** Do not add more topics until Wave 1 is stable.

### Wave 2+: Additional Topics and Flows

Each subsequent wave follows the same cycle:

- Add 2-3 topics per wave
- Deploy, validate, publish (see Section 2)
- Test the **entire agent** after each wave -- not just the new topics

This last point is critical. When you add topics to an agent, you are not just adding functionality. You are changing how the agent reasons about **all** queries, including ones that worked perfectly before.

### Why Waves Work

Agent reasoning changes with each new topic added. A 3-topic agent behaves differently than a 7-topic agent because the Atlas planner considers **all** topics when deciding how to route a query. Adding a "Meeting Prep" topic can break routing for "Account Lookup" if the topic descriptions overlap or are ambiguous.

Testing incrementally catches routing regressions early, when they are cheap to fix. If you deploy 8 topics at once and routing breaks, you have no idea which topic caused the regression. If you deploy 2 topics at a time, the culprit is obvious.

**Budget 2-3 iterations per wave.** This is normal, not a sign of failure (see Section 3).

---

## 2. The Deployment Cycle

Every change to an Agentforce agent follows this mandatory sequence:

```
Deactivate --> Modify --> Deploy --> Validate --> Publish --> Activate
    ^                                                          |
    +----------------------- Next change ---------------------+
```

### Step-by-Step

```bash
# 1. Deactivate the agent (MANDATORY before publish)
sf agent deactivate --api-name MyAgent --target-org myOrg

# 2. Modify: Make changes to .agent file, flows, prompts, etc.
#    (This is your local development step -- edit files in force-app/)

# 3. Deploy metadata to the org
sf project deploy start --source-dir force-app --target-org myOrg

# 4. Validate the authoring bundle (catches syntax errors before publish)
sf agent validate authoring-bundle --api-name MyAgent --target-org myOrg

# 5. Publish the authoring bundle (creates a new version)
sf agent publish authoring-bundle --api-name MyAgent --target-org myOrg

# 6. Activate the agent
sf agent activate --api-name MyAgent --target-org myOrg
```

### Key Rules

- **You CANNOT publish while the agent is active.** Deactivation is mandatory. If you skip it, `sf agent publish` will fail.
- **Always validate before publishing.** The validate step catches Agent Script syntax errors, missing action references, and malformed configurations that would otherwise produce cryptic publish failures.
- **Each publish creates a new version.** Version numbers increment automatically (v1, v2, v3...). There is no way to overwrite a previous version. See Section 4.
- **Deploy before publish.** If you changed flows, Apex classes, or prompt templates, those must be deployed to the org before the agent can reference them. The publish step resolves references against what exists in the org, not what exists locally.

### Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Publishing while agent is active | Publish command fails | Deactivate first |
| Skipping deploy before publish | "Action not found" errors | Deploy flows/classes first |
| Skipping validate | Cryptic publish failure | Run validate, fix reported errors |
| Forgetting to activate after publish | Agent unresponsive in UI | Run activate command |

---

## 3. Post-Deploy Iteration (Expected, Not Failure)

After the first deployment of any wave, expect these issues. They are **normal** and do not indicate a broken design. Budget 2-3 iterations per wave to resolve them.

### Hallucination

**Symptom:** Agent fabricates Account IDs, contact names, or data instead of calling actions to retrieve real data.

**Fix:** Add explicit instructions to the agent or topic description:

```
NEVER fabricate data. You MUST call the action first to retrieve real information.
If an action returns no results, say so honestly. Do not invent data to fill the gap.
```

While behavioral prompting has limits (see [action-invocation-patterns.md](action-invocation-patterns.md)), anti-hallucination instructions are one area where explicit directives do help because they constrain output generation rather than trying to force action invocation.

### Unnecessary Clarifying Questions

**Symptom:** Agent asks "Which account would you like to look up?" when the user already said "Tell me about Acme Corp."

**Fix:** This is a structural problem, not a prompting problem. Use `reasoning.actions` with slot-filling instead of behavioral prompts. When an action defines its inputs with proper slot-filling configuration, the Atlas planner extracts the account name directly from the user's message and passes it to the action without asking.

See [action-invocation-patterns.md](action-invocation-patterns.md) for the full slot-filling pattern.

### Wrong Topic Routing

**Symptom:** Agent routes "What's the onboarding status for Acme Corp?" to the general account lookup topic instead of the onboarding topic.

**Fix:** Strengthen topic descriptions to reduce ambiguity. Add routing hints to `topic_selector` instructions that clarify which queries belong to which topic. Make topic scopes non-overlapping -- if two topics could both handle a query, the planner will guess.

### Missing Context on Follow-Ups

**Symptom:** User asks about Acme Corp, gets the answer, then asks "Who are the contacts?" and the agent asks "Which account?" again.

**Fix:** Implement session variables to persist context across turns:

```agentscript
reasoning:
  actions:
    get_account_details:
      outputs:
        - set @variables.current_account_id = @outputs.out_AccountId
        - set @variables.current_account_name = @outputs.out_AccountName

    get_contacts:
      inputs:
        - in_AccountId: @variables.current_account_id
```

Session variables let follow-up actions reference data from previous turns without re-asking the user.

### The Iteration Mindset

Expect this cycle for every wave:

1. Deploy and test
2. Discover 2-4 issues from the list above
3. Fix issues, redeploy (full cycle from Section 2)
4. Retest -- confirm fixes, check for regressions
5. Repeat until stable (usually 2-3 iterations)

This is a **normal** part of agent development. The Atlas planner is a reasoning engine, not a rule executor. Its behavior emerges from the combination of all topics, actions, and instructions. Small changes can have non-obvious effects, and the only way to find them is to test.

---

## 4. Version Management

### How Versions Work

Each `sf agent publish authoring-bundle` creates a new `genAiPlannerBundle` version. Versions accumulate in the org:

```
force-app/main/default/aiAuthoringBundles/MyAgent/
  MyAgent.agent
  MyAgent.bundle-meta.xml
  genAiPlannerBundles/
    v1.genAiPlannerBundle
    v2.genAiPlannerBundle
    v3.genAiPlannerBundle
    ...
    v14.genAiPlannerBundle    # Production agents can reach v14+ easily
```

### Key Facts

- **Versions only increment.** There is no way to overwrite or delete a version through the CLI.
- **The `.bundle-meta.xml` file references the active version.** When you retrieve from the org, this file tells you which version is currently published.
- **Old versions are safe to leave.** They do not consume meaningful storage or cause runtime issues. Only clean them up if they cause source control confusion.
- **Source control sync:** Run `sf project retrieve start` to pull the latest version from the org. This is the authoritative way to sync your local files with what is actually published.

### Version Tracking in Practice

After several iterations, your version history tells a story:

| Version | Change | Notes |
|---------|--------|-------|
| v1 | Initial deploy | Wave 1: account lookup only |
| v2 | Fix hallucination | Added anti-fabrication instructions |
| v3 | Add contacts topic | Wave 1 complete |
| v4 | Fix routing regression | Contacts topic was stealing account queries |
| v5 | Wave 2: onboarding topic | Added onboarding status actions |
| v6 | Fix session variables | Follow-up queries now retain account context |

This progression is typical. Do not be alarmed by high version numbers.

---

## 5. Pre-Deploy Checklist

Run through this checklist before deploying **any** agent change. Skipping items leads to deploy failures or runtime bugs that are harder to diagnose after the fact.

### Metadata and Configuration

- [ ] `sfdx-project.json` has `"sourceApiVersion": "65.0"` or higher
- [ ] `.bundle-meta.xml` file exists alongside `.agent` file in `aiAuthoringBundles/`
- [ ] All referenced Apex classes compile without errors

### Flows

- [ ] All flows deployed to org and **Active**
  ```bash
  sf data query -q "SELECT Label, ActiveVersionId FROM FlowDefinitionView WHERE Label LIKE 'Agent_%'" --target-org myOrg
  ```
- [ ] All flow input variables marked `isInput: true`
- [ ] All flow output variables marked `isOutput: true`
- [ ] Flow API names match exactly what the `.agent` file references

### Prompt Templates (if using Prompt Builder actions)

- [ ] Prompt templates deployed to org
- [ ] Template API names match action references in `.agent` file

### Agent Validation

- [ ] Agent validates successfully:
  ```bash
  sf agent validate authoring-bundle --api-name MyAgent --target-org myOrg
  ```

### Permissions

- [ ] Permission sets assigned to users who will interact with the agent
- [ ] Agent user has access to all objects and fields referenced by flows and actions

### After Deploy

- [ ] Agent published and activated (Section 2 cycle complete)
- [ ] Run at least T1-T3 from the verification test suite (Section 6)

---

## 6. Production Verification Test Suite Template

Use this template for manual testing after each deployment. Copy it, fill in specifics for your agent, and run through every test case. Mark each as Pass or Fail.

Each test case targets a specific behavior: action invocation, session persistence, topic routing, edge cases, and guardrails.

```markdown
## Test Suite: [Agent Name] v[N]
Date: YYYY-MM-DD
Org: [Production/Sandbox]
Tester: [Name]

### T1: Primary Topic -- Direct Query
Input: "Tell me about [specific account name]"
Expected: Agent calls get_account_details, returns real data, captures session variable
Pass criteria: Data matches Salesforce record. No fabrication.
Result: [ Pass / Fail ]
Notes:

### T2: Follow-Up Using Session Variable
Input: "Who are the contacts?"
Expected: Agent uses captured account_id from T1, calls get_contacts
Pass criteria: Returns contacts for the correct account without re-asking which account
Result: [ Pass / Fail ]
Notes:

### T3: Secondary Topic -- Onboarding Status
Input: "What's the onboarding status for [account]?"
Expected: Agent looks up account, then calls onboarding action
Pass criteria: Returns action plan progress with item counts
Result: [ Pass / Fail ]
Notes:

### T4: Generative Action (Prompt Builder)
Input: "Prep me for a meeting with [account]"
Expected: Agent looks up account, calls meeting prep template
Pass criteria: Returns AI-generated briefing (not just raw data)
Result: [ Pass / Fail ]
Notes:

### T5: Cross-Topic Navigation
Input: Start with account lookup, then ask about onboarding
Expected: Agent switches topics, retains session variables
Pass criteria: Second query uses same account_id without re-asking
Result: [ Pass / Fail ]
Notes:

### T6: Out-of-Scope Query
Input: "What's the weather like today?"
Expected: Agent politely redirects to available capabilities
Pass criteria: No hallucination, suggests what it CAN help with
Result: [ Pass / Fail ]
Notes:

### T7: Ambiguous Query
Input: "Help me with my accounts"
Expected: Agent asks for clarification (which account? what kind of help?)
Pass criteria: Asks a specific question, does not guess
Result: [ Pass / Fail ]
Notes:

### T8: Empty Results
Input: "Tell me about [nonexistent account name]"
Expected: Agent calls action, gets empty result, reports honestly
Pass criteria: Says "not found" or similar. Does NOT fabricate data.
Result: [ Pass / Fail ]
Notes:

### T9: Multi-Turn Conversation
Input: 3+ messages in sequence about the same account
Expected: Session variables persist throughout
Pass criteria: Never re-asks for account name/ID after initial lookup
Result: [ Pass / Fail ]
Notes:

### T10: Edge Case -- ID Input
Input: "Look up 001ABC123DEF456" (or valid Account ID)
Expected: Agent detects ID format, uses ID-based lookup
Pass criteria: Returns account data for that specific ID
Result: [ Pass / Fail ]
Notes:

---

## Summary
Total: __ / 10 passed
Blocking issues:
Follow-up items:
```

### How to Use This Template

- **Wave 1:** Run T1, T2, T6, T7, T8 (core functionality + guardrails)
- **Wave 2+:** Run the full suite after each wave deployment
- **Hotfixes:** Run T1-T2 plus any test case related to the fix
- **Keep results.** Version the test results alongside your agent source. They become invaluable when debugging regressions in later waves.

---

## Related Documents

- [cli-guide.md](cli-guide.md) -- Complete CLI command reference
- [action-invocation-patterns.md](action-invocation-patterns.md) -- Fixing the doomprompting anti-pattern
- [patterns-and-practices.md](patterns-and-practices.md) -- Agent Script best practices
- [agent-flow-design.md](agent-flow-design.md) -- Flow design patterns for Agentforce
