# Getting Started with Agent Script

This folder contains templates for learning Agent Script from scratch.

## Start Here

1. **[hello-world.agent](hello-world.agent)** - The minimal viable agent
   - Shows the absolute minimum structure required
   - Includes comments explaining why each block exists
   - Use as a starting point for any new agent

## What You'll Learn

### Required Blocks (in order)

```
┌─────────────┬──────────────────────────────────────────────────┐
│ Block       │ Purpose                                          │
├─────────────┼──────────────────────────────────────────────────┤
│ system:     │ Agent personality and default messages           │
│ config:     │ Deployment metadata (agent_name, label, etc.)    │
│ variables:  │ Data connections and state storage               │
│ language:   │ Locale configuration                             │
│ start_agent │ Entry point topic (exactly one required)         │
│ topic       │ Additional conversation topics (optional)        │
└─────────────┴──────────────────────────────────────────────────┘
```

### Minimum Requirements

For a deployable agent, you need:

- ✅ **system** block with `instructions` and `messages`
- ✅ **config** block with `agent_name`, `default_agent_user`, `agent_label`, `description`
- ✅ **variables** block with 3 linked variables (EndUserId, RoutableId, ContactId)
- ✅ **language** block with `default_locale`
- ✅ One **start_agent** topic with `label`, `description`, and `reasoning`

### Deployment

```bash
# Validate without deploying
sf agent validate authoring-bundle --api-name Your_Agent_Name --target-org your-org

# Deploy and make visible in Agentforce Studio
sf agent publish authoring-bundle --api-name Your_Agent_Name --target-org your-org
```

## Next Steps

After mastering the basics, explore:

- [patterns/](../patterns/) - Common patterns for actions, lifecycle events, and routing
- [topics/](../topics/) - Partial templates for specialized topics
- [actions/](../actions/) - Flow and Apex action templates
