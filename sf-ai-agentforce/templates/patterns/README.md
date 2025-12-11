# Agent Script Patterns

This folder contains reusable patterns for common Agentforce scenarios.

## Pattern Decision Tree

```
What do you need?
│
├─► Guaranteed post-action processing?
│   └─► Use: action-callbacks.agent
│       (run keyword for deterministic callbacks)
│
├─► Setup/cleanup for every reasoning turn?
│   └─► Use: lifecycle-events.agent
│       (before_reasoning / after_reasoning blocks)
│
├─► Navigate to specialist and return with results?
│   └─► Use: bidirectional-routing.agent
│       (store return address, specialist transitions back)
│
└─► None of the above?
    └─► Start with: ../getting-started/hello-world.agent
```

## Patterns Overview

### 1. [action-callbacks.agent](action-callbacks.agent)

**Purpose**: Chain actions with guaranteed execution using `run` keyword.

**Use when**:
- Follow-up actions MUST happen after parent action
- Audit logging required for compliance
- Order matters (send email AFTER order created)

**Key syntax**:
```agentscript
process_order: @actions.create_order
   with customer_id=...
   set @variables.order_id = @outputs.order_id
   run @actions.send_confirmation        # Always runs after create_order
      with order_id=@variables.order_id
   run @actions.log_activity             # Always runs after confirmation
      with event_type="ORDER_CREATED"
```

---

### 2. [lifecycle-events.agent](lifecycle-events.agent)

**Purpose**: Run code before/after every reasoning step automatically.

**Use when**:
- Track conversation metrics (turn count, duration)
- Refresh context before each response
- Log analytics after each turn
- Initialize state on first turn

**Key syntax**:
```agentscript
topic conversation:
   before_reasoning:
      set @variables.turn_count = @variables.turn_count + 1
      run @actions.refresh_context

   reasoning:
      instructions: ->
         | This is turn {!@variables.turn_count}

   after_reasoning:
      run @actions.log_analytics
```

---

### 3. [bidirectional-routing.agent](bidirectional-routing.agent)

**Purpose**: Navigate to specialist topic and return with results.

**Use when**:
- Complex workflows spanning multiple topics
- "Consult an expert" pattern
- Need to bring results back to coordinator
- Want separation of concerns

**Key syntax**:
```agentscript
# In main topic
consult_pricing: @utils.transition to @topic.pricing_specialist

# In specialist topic
before_reasoning:
   set @variables.return_topic = "main_hub"

# ... do specialist work ...

return_with_results: @utils.transition to @topic.main_hub
```

---

## Pattern Combinations

These patterns can be combined:

```
lifecycle-events + action-callbacks
├── before_reasoning: Initialize context
├── reasoning: Process with callbacks
│   └── action with run callbacks
└── after_reasoning: Log results
```

## Validation Scoring Impact

| Pattern | Scoring Boost | Key Requirements |
|---------|--------------|------------------|
| Action Callbacks | +5 pts | No nested run |
| Lifecycle Events | +5 pts | Proper block placement |
| Bidirectional | +5 pts | Return transitions |

## Anti-Patterns to Avoid

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Nested `run` inside `run` | Sequential `run` at same level |
| Lifecycle in wrong order | before_reasoning, reasoning, after_reasoning |
| Forget return transition | Always include return action in specialists |
| Use lifecycle for one-time setup | Use if @variables.turn_count == 1 |
