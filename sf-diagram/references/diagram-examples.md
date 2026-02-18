# Mermaid Diagram Examples for Salesforce

Complete, copy-paste-ready examples for the most common Salesforce diagram types.

---

## Example 1: JWT Bearer OAuth Flow (sequenceDiagram)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorBkg': '#ddd6fe',
  'actorTextColor': '#1f2937',
  'actorBorder': '#6d28d9',
  'signalColor': '#334155',
  'signalTextColor': '#1f2937',
  'noteBkgColor': '#f8fafc',
  'noteTextColor': '#1f2937',
  'noteBorderColor': '#334155'
}}}%%
sequenceDiagram
    autonumber

    box rgba(221,214,254,0.3) SERVER ENVIRONMENT
        participant S as Server (CI/CD)
        participant K as Key Store
    end

    box rgba(167,243,208,0.3) SALESFORCE
        participant SF as Salesforce Auth Server
    end

    Note over S,SF: JWT Bearer Flow (RFC 7523)

    S->>K: Retrieve private key
    K-->>S: Return private key

    S->>S: Create JWT (iss, sub, aud, exp)
    S->>S: Sign JWT with RS256

    S->>+SF: POST /services/oauth2/token
    Note over S,SF: grant_type=jwt-bearer<br/>assertion=SIGNED_JWT

    SF->>SF: Verify signature via X.509 cert
    SF->>SF: Validate claims + user pre-auth

    SF-->>-S: Access Token (no refresh token)

    S->>SF: API call with Bearer token
    SF-->>S: API response
```

**Key syntax points**:
- `autonumber` adds step numbers automatically
- `->>` for synchronous request, `-->>` for response
- `+` / `-` after arrow for activate/deactivate shorthand
- `box rgba(...)` groups related participants
- `Note over X,Y:` for protocol details spanning participants

---

## Example 2: Salesforce Data Model ERD (flowchart LR -- preferred format)

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 60, "rankSpacing": 50}} }%%
flowchart LR
    subgraph legend["LEGEND"]
        direction LR
        L_STD["Standard"]
        L_CUST["Custom"]
        L_EXT["External"]
        L_LK["--- LK (Lookup)"]
        L_MD["=== MD (Master-Detail)"]

        style L_STD fill:#bae6fd,stroke:#0369a1,color:#1f2937
        style L_CUST fill:#fed7aa,stroke:#c2410c,color:#1f2937
        style L_EXT fill:#a7f3d0,stroke:#047857,color:#1f2937
        style L_LK fill:#f8fafc,stroke:#334155,color:#1f2937
        style L_MD fill:#f8fafc,stroke:#334155,color:#1f2937
    end

    subgraph std["STANDARD OBJECTS"]
        Account["Account<br/>(317K) | OWD:Private"]
        Contact["Contact<br/>(512K) | OWD:Parent"]
        Opportunity["Opportunity<br/>(89K) | OWD:Private"]
        Case["Case<br/>(45K) | OWD:Private"]
    end

    subgraph cust["CUSTOM OBJECTS"]
        Invoice["Invoice__c<br/>(12K)"]
        InvLine["Invoice_Line__c"]
    end

    %% Relationships
    Account -->|"LK"| Contact
    Account -->|"LK"| Opportunity
    Account -->|"LK"| Case
    Account ==>|"MD"| Invoice
    Invoice ==>|"MD"| InvLine
    Contact -->|"LK"| Case

    %% Standard - Sky Blue
    style Account fill:#bae6fd,stroke:#0369a1,color:#1f2937
    style Contact fill:#bae6fd,stroke:#0369a1,color:#1f2937
    style Opportunity fill:#bae6fd,stroke:#0369a1,color:#1f2937
    style Case fill:#bae6fd,stroke:#0369a1,color:#1f2937

    %% Custom - Orange
    style Invoice fill:#fed7aa,stroke:#c2410c,color:#1f2937
    style InvLine fill:#fed7aa,stroke:#c2410c,color:#1f2937

    %% Subgraph styling
    style legend fill:#f8fafc,stroke:#334155,stroke-dasharray:5
    style std fill:#f0f9ff,stroke:#0369a1,stroke-dasharray:5
    style cust fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
```

**Key design decisions for ERDs**:
- Use `flowchart LR` (not `erDiagram`) so you can color-code nodes by object type
- `-->` for Lookup, `==>` for Master-Detail
- Show object name + record count only (no fields) to keep it clean
- Group by object type in subgraphs
- Always include a legend

---

## Example 3: Salesforce Data Model (erDiagram -- native cardinality)

Use this format when you need crow's-foot cardinality notation or when the audience prefers traditional ER diagrams.

```mermaid
erDiagram
    Account ||--o{ Contact : "has many"
    Account ||--o{ Opportunity : "has many"
    Account ||--o{ Case : "has many"
    Account ||--|{ Invoice__c : "owns (MD)"
    Invoice__c ||--|{ Invoice_Line__c : "owns (MD)"
    Contact ||--o{ Case : "reports"
    Opportunity ||--o{ OpportunityLineItem : "contains"
    Product2 ||--o{ OpportunityLineItem : "referenced by"

    Account {
        Id Id PK
        Text Name
        Lookup ParentId FK "Self-referential"
    }
    Contact {
        Id Id PK
        Lookup AccountId FK
        Text FirstName
        Text LastName
        Email Email
    }
    Opportunity {
        Id Id PK
        Lookup AccountId FK
        Currency Amount
        Picklist StageName
        Date CloseDate
    }
    Invoice__c {
        Id Id PK
        MasterDetail Account__c FK
        Currency Total_Amount__c
        Date Invoice_Date__c
    }
```

**Cardinality symbols** (crow's foot notation):
- `||` = exactly one
- `|o` = zero or one
- `o{` = zero or many
- `|{` = one or many

**When to use `erDiagram` vs `flowchart LR`**:

| Consideration | `flowchart LR` | `erDiagram` |
|---------------|----------------|-------------|
| Color-coding by object type | Yes (via `style`) | No |
| Cardinality notation | Manual labels | Native crow's foot |
| Relationship distinction (LK/MD) | Arrow weight (`-->` vs `==>`) | Label text only |
| Field-level detail | Not practical | Built-in attribute blocks |
| Best for | Executive presentations, large models | Technical data modeling, small models |

---

## Example 4: Integration Sequence (sequenceDiagram with error handling)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorBkg': '#ddd6fe',
  'actorTextColor': '#1f2937',
  'actorBorder': '#6d28d9',
  'signalColor': '#334155',
  'signalTextColor': '#1f2937',
  'noteBkgColor': '#f8fafc',
  'noteTextColor': '#1f2937',
  'noteBorderColor': '#334155'
}}}%%
sequenceDiagram
    autonumber

    box rgba(167,243,208,0.3) SALESFORCE
        participant T as Trigger/Flow
        participant Q as Queueable
        participant NC as Named Credential
    end

    box rgba(254,215,170,0.3) EXTERNAL
        participant API as External API
    end

    T->>Q: Enqueue async job
    activate Q

    Q->>NC: Get auth headers
    NC-->>Q: Authorization: Bearer ...

    Q->>+API: POST /api/v1/accounts

    alt Success (2xx)
        API-->>-Q: 200 OK
        Q->>Q: Update SF records (Synced)
    else Client Error (4xx)
        API-->>Q: 400 Bad Request
        Q->>Q: Create Integration_Log__c
    else Server Error (5xx)
        API-->>Q: 503 Unavailable
        Q->>Q: Retry with backoff
    end

    deactivate Q
```

**Key syntax points**:
- `alt` / `else` / `end` for branching paths
- `activate` / `deactivate` or `+` / `-` suffixes show processing duration
- `-)` for async fire-and-forget messages (e.g., `SF-)Bus: Publish Event`)
- `loop` for retry patterns: `loop Retry up to 3 times`
- `par` / `and` for parallel execution
- `critical` / `option` for critical regions
- `break` for early termination

---

## Example 5: System Landscape (flowchart TB with subgraphs)

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
flowchart TB
    subgraph users["USERS"]
        direction LR
        U1["Sales Reps"]
        U2["Managers"]
        U3["Partners"]
    end

    subgraph salesforce["SALESFORCE PLATFORM"]
        direction TB
        subgraph core["CORE CRM"]
            SF1["Sales Cloud"]
            SF2["Service Cloud"]
        end
        subgraph auto["AUTOMATION"]
            FL["Flows"]
            AP["Apex Services"]
            PE["Platform Events"]
        end
    end

    subgraph integration["INTEGRATION LAYER"]
        MW["MuleSoft Anypoint"]
        GW["API Gateway"]
    end

    subgraph external["EXTERNAL SYSTEMS"]
        SAP["SAP S/4HANA"]
        DW["Snowflake"]
    end

    U1 --> SF1
    U2 --> SF1
    U2 --> SF2
    U3 --> SF2

    SF1 <--> FL
    SF2 <--> FL
    FL <--> AP
    AP <--> PE

    PE --> MW
    AP <--> GW
    MW <--> GW

    GW <-->|"REST/SOAP"| SAP
    MW -->|"ETL"| DW

    %% Users - violet
    style U1 fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
    style U2 fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
    style U3 fill:#ddd6fe,stroke:#6d28d9,color:#1f2937

    %% Salesforce - cyan
    style SF1 fill:#a5f3fc,stroke:#0e7490,color:#1f2937
    style SF2 fill:#a5f3fc,stroke:#0e7490,color:#1f2937

    %% Automation - indigo/violet/teal
    style FL fill:#c7d2fe,stroke:#4338ca,color:#1f2937
    style AP fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
    style PE fill:#99f6e4,stroke:#0f766e,color:#1f2937

    %% Integration - orange
    style MW fill:#fed7aa,stroke:#c2410c,color:#1f2937
    style GW fill:#fed7aa,stroke:#c2410c,color:#1f2937

    %% External - green/amber
    style SAP fill:#a7f3d0,stroke:#047857,color:#1f2937
    style DW fill:#fde68a,stroke:#b45309,color:#1f2937

    %% Subgraphs - 50-level dashed
    style users fill:#f5f3ff,stroke:#6d28d9,stroke-dasharray:5
    style salesforce fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
    style core fill:#ecfeff,stroke:#0e7490,stroke-dasharray:5
    style auto fill:#eef2ff,stroke:#4338ca,stroke-dasharray:5
    style integration fill:#fff7ed,stroke:#c2410c,stroke-dasharray:5
    style external fill:#ecfdf5,stroke:#047857,stroke-dasharray:5
```

---

## Example 6: C4 Context Diagram (experimental Mermaid feature)

C4 support in Mermaid is experimental and may not render in all viewers.

```mermaid
C4Context
    title System Context - Salesforce CRM Platform

    Person(salesRep, "Sales Representative", "Manages leads, opportunities, and accounts")
    Person(serviceAgent, "Service Agent", "Handles customer cases and inquiries")
    Person(partner, "Channel Partner", "Accesses portal for deal registration")

    Enterprise_Boundary(sf, "Salesforce Platform") {
        System(crm, "CRM System", "Sales Cloud + Service Cloud")
        System(agentforce, "Agentforce", "AI-powered customer service agents")
    }

    System_Ext(erp, "SAP S/4HANA", "Enterprise resource planning")
    System_Ext(mktg, "Marketing Cloud", "Email campaigns, journeys")
    System_Ext(dw, "Snowflake", "Data warehouse and analytics")

    Rel(salesRep, crm, "Manages pipeline", "Lightning UI")
    Rel(serviceAgent, crm, "Resolves cases", "Lightning / Agentforce")
    Rel(serviceAgent, agentforce, "AI-assisted", "Chat")
    Rel(partner, crm, "Deal registration", "Experience Cloud")

    Rel(crm, erp, "Syncs orders and invoices", "MuleSoft / REST")
    Rel(crm, mktg, "Sends campaign data", "Marketing Cloud Connect")
    Rel(crm, dw, "Exports analytics data", "ETL / Batch")
```

**C4 Syntax Reference**:

| Function | Purpose | Example |
|----------|---------|---------|
| `Person(id, name, desc)` | Human user | `Person(user, "Sales Rep", "...")` |
| `System(id, name, desc)` | Internal system | `System(crm, "CRM", "...")` |
| `System_Ext(id, name, desc)` | External system | `System_Ext(erp, "SAP", "...")` |
| `Container(id, name, tech, desc)` | Software container | `Container(api, "REST API", "Apex", "...")` |
| `ContainerDb(id, name, tech, desc)` | Database container | `ContainerDb(db, "Database", "PostgreSQL", "...")` |
| `Enterprise_Boundary(id, name)` | Org boundary | `Enterprise_Boundary(sf, "Salesforce")` |
| `Rel(from, to, label, tech)` | Relationship | `Rel(crm, erp, "syncs", "REST")` |

**C4 Diagram Levels**:

| Level | Mermaid Keyword | Scope | Audience |
|-------|----------------|-------|----------|
| Context | `C4Context` | Systems + people + external | Executives, stakeholders |
| Container | `C4Container` | Apps, databases, APIs within a system | Architects, tech leads |
| Component | `C4Component` | Classes, modules within a container | Developers |
| Dynamic | `C4Dynamic` | Runtime interaction flows | Architects, developers |
