# Agent Script Pattern Catalog

A decision-focused guide to choosing the right patterns for your Agentforce agent.

---

## Quick Reference: Pattern Selection

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PATTERN DECISION TREE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  What problem are you solving?                                           │
│  │                                                                       │
│  ├─► "I need to run code BEFORE/AFTER every response"                   │
│  │   └─► Lifecycle Events Pattern                                       │
│  │       File: templates/patterns/lifecycle-events.agent                │
│  │                                                                       │
│  ├─► "After action X, Y must ALWAYS happen"                             │
│  │   └─► Action Callbacks Pattern                                       │
│  │       File: templates/patterns/action-callbacks.agent                │
│  │                                                                       │
│  ├─► "Go to specialist topic, then return with results"                 │
│  │   └─► Bidirectional Routing Pattern                                  │
│  │       File: templates/patterns/bidirectional-routing.agent           │
│  │                                                                       │
│  ├─► "Just starting out - what's the minimum?"                          │
│  │   └─► Hello World                                                    │
│  │       File: templates/getting-started/hello-world.agent              │
│  │                                                                       │
│  ├─► "Multiple topics, user chooses where to go"                        │
│  │   └─► Multi-Topic Router                                             │
│  │       File: templates/agent/multi-topic.agent                        │
│  │                                                                       │
│  └─► "Need input validation before actions"                             │
│      └─► Error Handling Pattern                                         │
│          File: templates/topics/error-handling.agent                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pattern Details

### 1. Lifecycle Events

**File**: `templates/patterns/lifecycle-events.agent`

**Purpose**: Execute code automatically before and after every reasoning step.

**Key Syntax**:
```agentscript
topic conversation:
   before_reasoning:
      set @variables.turn_count = @variables.turn_count + 1
      run @actions.refresh_context
         with user_id=@variables.EndUserId
         set @variables.context = @outputs.fresh_context

   reasoning:
      instructions: ->
         | Turn {!@variables.turn_count}: {!@variables.context}

   after_reasoning:
      run @actions.log_analytics
         with turn=@variables.turn_count
```

**When to Use**:
| ✅ Good Use Case | ❌ Not Ideal For |
|------------------|------------------|
| Track conversation metrics | One-time setup (use conditional) |
| Refresh context every turn | Heavy processing (adds latency) |
| Log analytics after each response | Actions that might fail often |
| Initialize on first turn | - |

**Validation Impact**: +5 points for proper lifecycle structure

---

### 2. Action Callbacks

**File**: `templates/patterns/action-callbacks.agent`

**Purpose**: Chain deterministic follow-up actions using the `run` keyword.

**Key Syntax**:
```agentscript
process_order: @actions.create_order
   with customer_id=@variables.customer_id
   set @variables.order_id = @outputs.order_id
   run @actions.send_confirmation
      with order_id=@variables.order_id
   run @actions.log_activity
      with event="ORDER_CREATED"
```

**When to Use**:
| ✅ Good Use Case | ❌ Not Ideal For |
|------------------|------------------|
| Audit logging (must happen) | Optional follow-ups (let LLM decide) |
| Send notification after action | Complex branching logic |
| Chain dependent actions | More than 1 level of nesting |
| Compliance requirements | - |

**Critical Rule**: Only 1 level of `run` nesting allowed!

**Validation Impact**: +5 points for proper callback structure

---

### 3. Bidirectional Routing

**File**: `templates/patterns/bidirectional-routing.agent`

**Purpose**: Navigate to specialist topic, do work, return with results.

**Key Syntax**:
```agentscript
# Main hub stores return address
topic main_hub:
   reasoning:
      actions:
         consult_pricing: @utils.transition to @topic.pricing_specialist

# Specialist records where to return
topic pricing_specialist:
   before_reasoning:
      set @variables.return_topic = "main_hub"

   reasoning:
      actions:
         return_with_results: @utils.transition to @topic.main_hub
```

**When to Use**:
| ✅ Good Use Case | ❌ Not Ideal For |
|------------------|------------------|
| "Consult expert" workflows | Simple linear flows |
| Results need to come back | One-way topic changes |
| Separation of concerns | Single-topic agents |
| Complex multi-step processes | - |

**Validation Impact**: +5 points for proper return transitions

---

### 4. Multi-Topic Router (Hub-and-Spoke)

**File**: `templates/agent/multi-topic.agent`

**Purpose**: Central topic routes to specialized topics based on user intent.

**Key Syntax**:
```agentscript
start_agent topic_selector:
   reasoning:
      instructions: ->
         | Determine what the user needs.
      actions:
         go_orders: @utils.transition to @topic.orders
         go_billing: @utils.transition to @topic.billing
         go_support: @utils.transition to @topic.support
```

**When to Use**:
| ✅ Good Use Case | ❌ Not Ideal For |
|------------------|------------------|
| Multiple distinct use cases | Single-purpose agents |
| Clear routing criteria | Complex interdependencies |
| Modular topic development | Need to share state heavily |

**Validation Impact**: +10 points for complete topic structure

---

### 5. Error Handling

**File**: `templates/topics/error-handling.agent`

**Purpose**: Validate input before processing, handle failures gracefully.

**Key Syntax**:
```agentscript
reasoning:
   instructions: ->
      if @variables.amount is None:
         set @variables.valid = False
         | Please provide an amount.

      if @variables.amount > 10000:
         set @variables.valid = False
         | Amount exceeds maximum allowed.

      if @variables.valid == True:
         | Proceeding with your request.

   actions:
      process: @actions.execute_operation
         available when @variables.valid == True
      retry: @utils.transition to @topic.validation
         available when @variables.operation_failed == True
```

**When to Use**:
| ✅ Good Use Case | ❌ Not Ideal For |
|------------------|------------------|
| Payment processing | Simple queries |
| Data mutations | Read-only operations |
| Compliance workflows | Low-stakes interactions |

**Validation Impact**: +5 points for validation logic

---

## Combining Patterns

Patterns can be combined for complex scenarios:

```
┌─────────────────────────────────────────────────────────────┐
│           LIFECYCLE + CALLBACKS + ROUTING                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  topic order_hub:                                            │
│     before_reasoning:                        ◄── Lifecycle   │
│        set @variables.turn_count = ... + 1                   │
│                                                              │
│     reasoning:                                               │
│        actions:                                              │
│           process: @actions.create                           │
│              run @actions.notify           ◄── Callback      │
│              run @actions.log                                │
│                                                              │
│           consult: @utils.transition       ◄── Routing       │
│              to @topic.specialist                            │
│                                                              │
│     after_reasoning:                         ◄── Lifecycle   │
│        run @actions.update_metrics                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Scoring Summary

| Pattern | Points | Key Requirement |
|---------|--------|-----------------|
| Config block | 10 | All 4 required fields |
| Linked variables | 10 | EndUserId, RoutableId, ContactId |
| Topic structure | 10 | label, description, reasoning |
| Language block | 5 | default_locale present |
| Lifecycle blocks | 5 | Proper before/after structure |
| Action callbacks | 5 | No nested run |
| Bidirectional routing | 5 | Return transitions |
| Error handling | 5 | Validation patterns |
| Template expressions | 5 | {!@variables.x} syntax |

**Total possible**: 60+ points from patterns alone

---

## Related Documentation

- [Agent Script Syntax Reference](agent-script-syntax.md) - Complete syntax guide
- [Testing & Validation Guide](testing-validation-guide.md) - Deployment testing
- [Anti-Patterns](agent-script-syntax.md#anti-patterns) - What to avoid
