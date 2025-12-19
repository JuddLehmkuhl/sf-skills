# Agent Script Templates Catalog

Complete catalog of Agent Script templates organized by difficulty and purpose.

---

## Quick Start Decision Tree

```
What do you need?
│
├─► "Just starting - show me the basics"
│   └─► getting-started/hello-world.agent (BEGINNER)
│
├─► "Complete agent with topics and actions"
│   └─► agent/multi-topic.agent (INTERMEDIATE)
│
├─► "How do I add actions to my agent?"
│   ├─► actions/flow-action.agent (Flow-based)
│   └─► actions/apex-action.agent (Apex-based)
│
├─► "I need a specific pattern"
│   └─► patterns/README.md (see pattern decision tree)
│
├─► "How do I escalate to human agents?"
│   └─► connection/escalation-setup.agent
│
└─► "I need metadata templates"
    ├─► genai-metadata/ (GenAiFunction XML)
    ├─► prompt-templates/ (PromptTemplate XML)
    └─► flows/ (Flow XML)
```

---

## Template Inventory

### Getting Started (BEGINNER)

| Template | Purpose | Prerequisites |
|----------|---------|---------------|
| `getting-started/hello-world.agent` | Minimal working agent | None |

### Core Agent Templates (INTERMEDIATE)

| Template | Purpose | Prerequisites |
|----------|---------|---------------|
| `agent/simple-qa.agent` | Single-topic Q&A agent | hello-world |
| `agent/multi-topic.agent` | Multi-topic with routing | simple-qa |

### Action Templates (INTERMEDIATE)

| Template | Purpose | Prerequisites |
|----------|---------|---------------|
| `actions/flow-action.agent` | Call Flow from agent | multi-topic |
| `actions/apex-action.agent` | Call Apex from agent | flow-action |

### Topic Templates (INTERMEDIATE)

| Template | Purpose | Prerequisites |
|----------|---------|---------------|
| `topics/topic-with-actions.agent` | Topic with action definitions | multi-topic |
| `topics/error-handling.agent` | Input validation pattern | topic-with-actions |

### Connection Templates (INTERMEDIATE)

| Template | Purpose | Prerequisites |
|----------|---------|---------------|
| `connection/escalation-setup.agent` | Human agent handoff | multi-topic |

### Advanced Patterns (ADVANCED)

| Template | Purpose | Prerequisites | Deployment |
|----------|---------|---------------|------------|
| `patterns/lifecycle-events.agent` | before/after reasoning | multi-topic | GenAiPlannerBundle |
| `patterns/action-callbacks.agent` | Deterministic action chains | flow-action | GenAiPlannerBundle |
| `patterns/bidirectional-routing.agent` | Go to topic, return with results | multi-topic | Both |
| `patterns/llm-controlled-actions.agent` | LLM-selected actions | flow-action | Both |
| `patterns/advanced-input-bindings.agent` | Variable/slot filling patterns | flow-action | Both |
| `patterns/prompt-template-action.agent` | generatePromptResponse:// | flow-action | Both |
| `patterns/multi-step-workflow.agent` | Boolean flags for progress | multi-topic | Both |
| `patterns/procedural-instructions.agent` | Conditional data loading | flow-action | GenAiPlannerBundle |
| `patterns/system-instruction-overrides.agent` | Topic-level persona switching | multi-topic | Both |

### Metadata Templates

| Template | Purpose | Used With |
|----------|---------|-----------|
| `bundle-meta.xml` | AiAuthoringBundle metadata | All agents |
| `genai-metadata/genai-function-apex.xml` | Apex → Agent Action | Apex classes |
| `genai-metadata/genai-function-flow.xml` | Flow → Agent Action | Flows |
| `genai-metadata/genai-plugin.xml` | Group actions into plugin | GenAiFunction |
| `prompt-templates/*.xml` | PromptTemplate metadata | generatePromptResponse actions |
| `flows/http-callout-flow.xml` | HTTP callout Flow | External API calls |

---

## Recommended Learning Path

```
BEGINNER
────────
1. getting-started/hello-world.agent
   └─► Learn: Basic structure, config, system block

2. agent/simple-qa.agent
   └─► Learn: Reasoning instructions, topic structure

3. agent/multi-topic.agent
   └─► Learn: Topic transitions, routing

INTERMEDIATE
────────────
4. actions/flow-action.agent
   └─► Learn: Action definitions, Flow integration

5. topics/error-handling.agent
   └─► Learn: Validation, conditional availability

6. connection/escalation-setup.agent
   └─► Learn: Human handoff, Omni-Channel

ADVANCED
────────
7. patterns/lifecycle-events.agent
   └─► Learn: before_reasoning, after_reasoning

8. patterns/action-callbacks.agent
   └─► Learn: run keyword, deterministic chains

9. patterns/system-instruction-overrides.agent
   └─► Learn: Topic-level personas
```

---

## Deployment Notes

| Template Type | AiAuthoringBundle | GenAiPlannerBundle | Notes |
|---------------|-------------------|-------------------|-------|
| Basic agents | ✅ | ✅ | Visible in Agentforce Studio |
| `run` keyword patterns | ❌ | ✅ | NOT visible in Studio |
| Lifecycle with actions | ❌ | ✅ | NOT visible in Studio |
| All others | ✅ | ✅ | Choose based on Studio need |

**Command reference:**
- AiAuthoringBundle: `sf agent publish authoring-bundle --api-name [Name]`
- GenAiPlannerBundle: `sf project deploy start --source-dir [path]`

---

## Related Documentation

- [SKILL.md](../SKILL.md) - Entry point, workflow guide
- [pattern-catalog.md](../docs/pattern-catalog.md) - Pattern decision tree
- [agent-script-syntax.md](../docs/agent-script-syntax.md) - Complete syntax reference
