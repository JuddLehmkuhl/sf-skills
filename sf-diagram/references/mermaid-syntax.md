# Mermaid Syntax Quick Reference

---

## Sequence Diagram Syntax

```
sequenceDiagram
    autonumber                          %% Auto-number all messages
    participant A as Alice              %% Named participant
    actor U as User                     %% Actor (stick figure)

    A->>B: Synchronous request          %% Solid line, filled arrow
    B-->>A: Synchronous response        %% Dashed line, filled arrow
    A-)B: Async (fire-and-forget)       %% Solid line, open arrow
    A--)B: Async response               %% Dashed line, open arrow

    activate B                          %% Start activation bar
    deactivate B                        %% End activation bar
    A->>+B: Request (shorthand activate)
    B-->>-A: Response (shorthand deactivate)

    Note over A,B: Spanning note        %% Note across participants
    Note right of A: Side note          %% Note on one side

    alt Condition A                     %% Alternative paths
        A->>B: Path A
    else Condition B
        A->>B: Path B
    end

    opt Optional Step                   %% Optional block
        A->>B: Maybe this happens
    end

    loop Every 5 minutes                %% Loop block
        A->>B: Poll for status
    end

    par Parallel A                      %% Parallel execution
        A->>B: Call B
    and Parallel B
        A->>C: Call C simultaneously
    end

    critical Establish connection        %% Critical region
        A->>B: Connect
    option Connection timeout
        A->>A: Log failure
    end

    break When quota exceeded            %% Break / early exit
        B-->>A: 429 Rate Limited
    end

    box rgba(221,214,254,0.3) GROUP NAME  %% Visual grouping
        participant X
        participant Y
    end
```

---

## Flowchart Syntax

```
flowchart LR                            %% LR=left-right, TB=top-bottom, TD=top-down
    A["Rectangle label"]                %% Rectangle node
    B(["Stadium shape"])                %% Stadium/pill shape
    C{"Diamond decision"}               %% Decision diamond
    D[("Cylinder database")]            %% Database cylinder
    E(("Circle"))                       %% Circle node
    F[["Subroutine"]]                   %% Subroutine shape

    A --> B                             %% Arrow
    A -->|"label"| B                    %% Labeled arrow
    A ==> B                             %% Thick arrow
    A -.-> B                            %% Dotted arrow
    A <--> B                            %% Bidirectional

    subgraph name["TITLE"]              %% Subgraph grouping
        direction LR                    %% Direction within subgraph
        X --> Y
    end

    style A fill:#bae6fd,stroke:#0369a1,color:#1f2937   %% Node styling
    style name fill:#f0f9ff,stroke:#0369a1,stroke-dasharray:5  %% Subgraph styling
```

---

## erDiagram Syntax

```
erDiagram
    ENTITY_A ||--o{ ENTITY_B : "relationship label"

    ENTITY_A {
        type attribute_name PK "comment"
        type attribute_name FK
        type attribute_name UK "unique"
    }

    %% Cardinality: ||=exactly one, |o=zero/one, o{=zero/many, |{=one/many
    %% Examples:
    PARENT ||--o{ CHILD : "has many (optional)"
    PARENT ||--|{ CHILD : "has many (required)"
    A |o--o| B : "zero-or-one to zero-or-one"
```
