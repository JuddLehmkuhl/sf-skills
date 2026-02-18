---
name: sf-diagram
description: >
  Creates Salesforce architecture diagrams using Mermaid with ASCII fallback.
  Use when visualizing OAuth flows, data models (ERDs), integration sequences,
  system landscapes, role hierarchies, or Agentforce agent architectures.
license: MIT
compatibility: "Requires Mermaid-capable renderer for diagram previews"
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "80 points across 5 categories"
---

# sf-diagram: Salesforce Diagram Generation

---

## Diagram Type Decision Framework

```
Is the request about...

Authentication / OAuth?
  --> sequenceDiagram (shows step-by-step token exchange)
  --> Cross-ref: sf-connected-apps for Connected App config

Data model / Object relationships?
  --> flowchart LR (preferred: supports color-coding by object type)
  --> erDiagram (alternative: native cardinality notation)
  --> Cross-ref: sf-metadata for live object/field discovery

API integration / System-to-system calls?
  --> sequenceDiagram (shows request/response timing)
  --> Cross-ref: sf-integration for Named Credentials, External Services

High-level system architecture / Landscape?
  --> flowchart TB (layered architecture with subgraphs)

Agent / AI architecture?
  --> flowchart TB (channels -> agents -> topics -> actions)

Role hierarchy / Org structure?
  --> flowchart TB (top-down hierarchy)

Process / Decision logic?
  --> flowchart TD (decision diamonds, process steps)
  --> Cross-ref: sf-flow for Flow logic documentation
```

### Quick Selection Matrix

| Question to ask | Diagram type | Mermaid keyword |
|-----------------|-------------|-----------------|
| "Who talks to whom, in what order?" | Sequence | `sequenceDiagram` |
| "How are objects related?" | ERD / Data Model | `flowchart LR` or `erDiagram` |
| "What systems are involved?" | System Landscape | `flowchart TB` |
| "How does authentication work?" | OAuth Flow | `sequenceDiagram` |
| "What does the agent architecture look like?" | Agent Architecture | `flowchart TB` |
| "What is the high-level container breakdown?" | C4 Container | `C4Container` |
| "How does a process flow through decisions?" | Flowchart | `flowchart TD` |

---

## Supported Diagram Types

| Type | Mermaid Syntax | Use Case |
|------|---------------|----------|
| OAuth Flows | `sequenceDiagram` | Authorization Code, JWT Bearer, PKCE, Device Flow |
| Data Models | `flowchart LR` | Object relationships with color coding (preferred) |
| Data Models (alt) | `erDiagram` | Crow's foot cardinality for smaller models |
| Integration Sequences | `sequenceDiagram` | API callouts, event-driven flows |
| System Landscapes | `flowchart TB` | High-level architecture, component diagrams |
| C4 Architecture | `C4Context` / `C4Container` | Formal architecture documentation |
| Role Hierarchies | `flowchart TB` | User hierarchies, profile/permission structures |
| Agentforce Flows | `flowchart TB` | Agent -> Topic -> Action flows |

> Full copy-paste examples for each type: [references/diagram-examples.md](references/diagram-examples.md)

---

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Diagram type (use Decision Framework above)
- Specific flow or scope (e.g., "JWT Bearer flow" or "Account-Contact-Opportunity model")
- Output preference (Mermaid only, ASCII only, or Both)

If ERD requested, check for sf-metadata availability. Create TodoWrite tasks for multi-diagram requests.

### Phase 2: Template Selection

| Diagram Type | Template File |
|--------------|---------------|
| Authorization Code Flow | `templates/oauth/authorization-code.md` |
| Authorization Code + PKCE | `templates/oauth/authorization-code-pkce.md` |
| JWT Bearer Flow | `templates/oauth/jwt-bearer.md` |
| Client Credentials Flow | `templates/oauth/client-credentials.md` |
| Device Authorization Flow | `templates/oauth/device-authorization.md` |
| Refresh Token Flow | `templates/oauth/refresh-token.md` |
| Data Model (ERD) | `templates/datamodel/salesforce-erd.md` |
| Integration Sequence | `templates/integration/api-sequence.md` |
| System Landscape | `templates/architecture/system-landscape.md` |
| Role Hierarchy | `templates/role-hierarchy/user-hierarchy.md` |
| Agentforce Flow | `templates/agentforce/agent-flow.md` |

**Template Path Resolution** (try in order):
1. `~/.claude/plugins/marketplaces/sf-skills/sf-diagram/templates/[template]`
2. `[project-root]/sf-diagram/templates/[template]`
3. `~/.claude/plugins/cache/sf-diagram/*/sf-diagram/templates/[template]`

### Phase 3: Data Collection

**OAuth Diagrams**: Use standard actors, CloudSundial-inspired styling (see [references/mermaid-styling.md](references/mermaid-styling.md)), include `autonumber`. Cross-ref: `sf-connected-apps`.

**ERD/Data Model Diagrams**:
1. If org connected, query record counts: `python3 scripts/query-org-metadata.py --objects Account,Contact --target-org myorg`
2. Identify relationships (Lookup vs Master-Detail), object types (Standard, Custom, External)
3. Generate `flowchart LR` with color coding. Cross-ref: `sf-metadata`

**Integration Diagrams**: Identify systems, capture request/response patterns, note async vs sync. Cross-ref: `sf-integration`.

### Phase 4: Diagram Generation

**Mermaid**:
1. Start with an example from [references/diagram-examples.md](references/diagram-examples.md)
2. Apply color scheme from [references/mermaid-styling.md](references/mermaid-styling.md)
3. Add annotations/notes, `autonumber` for sequences
4. For data models: `flowchart LR` with object-type color coding, name + count only

**ASCII fallback**: Box-drawing chars (`+-|`), arrows (`-->`, `<--`), width under 80 chars.

**Validation scoring**:
```
Score: XX/80 Rating
-- Accuracy: XX/20      (Correct actors, flow steps, relationships)
-- Clarity: XX/20       (Easy to read, proper labeling)
-- Completeness: XX/15  (All relevant steps/entities included)
-- Styling: XX/15       (Color scheme, theming, annotations)
-- Best Practices: XX/10 (Proper notation, UML conventions)
```

### Phase 5: Output & Documentation

````markdown
## [Diagram Title]

### Mermaid Diagram
```mermaid
[Generated Mermaid code]
```

### ASCII Fallback
```
[Generated ASCII diagram]
```

### Key Points
- [Important note 1]

### Diagram Score
[Validation results]
````

**Optional preview**: See [references/preview-guide.md](references/preview-guide.md) for localhost live-reload setup.

---

## OAuth Flow Reference

| Flow | When to Use | Key Detail | Template |
|------|------------|------------|----------|
| **Authorization Code** | Web apps with backend server | User grants consent via browser redirect | `oauth/authorization-code.md` |
| **Auth Code + PKCE** | Mobile apps, SPAs, public clients | code_verifier + SHA256 code_challenge | `oauth/authorization-code-pkce.md` |
| **JWT Bearer** | Server-to-server, CI/CD, headless | Sign JWT with X.509 private key | `oauth/jwt-bearer.md` |
| **Client Credentials** | Service accounts, background jobs | No user context, client_id + client_secret | `oauth/client-credentials.md` |
| **Device Authorization** | CLI tools, IoT, Smart TVs | User authorizes on separate device | `oauth/device-authorization.md` |
| **Refresh Token** | Extend existing access sessions | Reuse refresh_token for new access_token | `oauth/refresh-token.md` |

**Quick selection**: User present + web app? --> Auth Code (+ PKCE if public client). No user, server-to-server? --> JWT Bearer or Client Credentials. No browser? --> Device Authorization. Renewing? --> Refresh Token.

Cross-ref: `sf-connected-apps` skill for Connected App configuration, certificate upload, and pre-authorization setup.

---

## Data Model Notation (Summary)

| Arrow | Relationship | Meaning |
|-------|-------------|---------|
| `-->` with `"LK"` | Lookup | Optional parent, no cascade delete |
| `==>` with `"MD"` | Master-Detail | Required parent, cascade delete, roll-ups |
| `-.->` | Convert | Conversion (e.g., Lead) |

**Object colors**: Standard=`#bae6fd` (blue), Custom=`#fed7aa` (orange), External=`#a7f3d0` (green).

> Full notation guide, LDV indicators, OWD display, template catalog, and large-model strategies: [references/data-model-notation.md](references/data-model-notation.md)

---

## Mermaid Syntax (Summary)

Key patterns used across all diagram types:

| Pattern | Syntax | Use |
|---------|--------|-----|
| Auto-number | `autonumber` | Sequence diagrams |
| Sync request | `->>` / `-->>` | Solid/dashed arrows |
| Async fire-forget | `-)` / `--)` | Open arrows |
| Branching | `alt` / `else` / `end` | Error handling paths |
| Parallel | `par` / `and` / `end` | Concurrent calls |
| Grouping | `box rgba(...)` | Participant groups |
| Subgraph | `subgraph name["TITLE"]` | Flowchart groups |
| Node styling | `style A fill:#hex,stroke:#hex,color:#hex` | Individual colors |
| Thick arrow | `==>` | Master-Detail in ERDs |
| Dotted arrow | `-.->` | Conversion/optional |

> Full syntax reference with all node shapes, arrow types, and block constructs: [references/mermaid-syntax.md](references/mermaid-syntax.md)

---

## Styling Quick Reference

Tailwind 200-level pastel fills with dark strokes. Full palette in [references/mermaid-styling.md](references/mermaid-styling.md).

| Component | Fill | Stroke | Usage |
|-----------|------|--------|-------|
| Salesforce Platform | `#bae6fd` | `#0369a1` | CRM clouds, standard objects |
| Connected Apps/OAuth | `#fed7aa` | `#c2410c` | Auth flows, Named Credentials |
| External Systems | `#a7f3d0` | `#047857` | ERP, marketing, data systems |
| Users/Actors | `#ddd6fe` | `#6d28d9` | People, roles |
| Platform Events | `#99f6e4` | `#0f766e` | CDC, streaming, event bus |
| AI/Agentforce | `#fbcfe8` | `#be185d` | Agents, Einstein |
| Automation | `#c7d2fe` | `#4338ca` | Flows, process builders |

Subgraph styling: Tailwind 50-level fills with `stroke-dasharray:5`.

---

## Scoring Thresholds

| Rating | Score | Meaning |
|--------|-------|---------|
| Excellent | 72-80 | Production-ready, comprehensive, well-styled |
| Very Good | 60-71 | Complete with minor improvements possible |
| Good | 48-59 | Functional but could be clearer |
| Needs Work | 35-47 | Missing key elements or unclear |
| Critical Issues | <35 | Inaccurate or incomplete |

---

## Best Practices

**Sequence Diagrams**: Use `autonumber`, `->>` for requests / `-->>` for responses, `activate`/`deactivate` for long processes, `box` for grouping, `Note over` for protocol details, `alt`/`else` for error paths.

**Data Model Diagrams**: Use `flowchart LR`, name + count only (no fields), color by type (Blue=Standard, Orange=Custom, Green=External), `-->` for LK / `==>` for MD, LDV indicator for >2M records, API names not labels, always include legend, limit ~10 objects per diagram.

**Integration Diagrams**: Show error paths with `alt`/`else`, include timeout handling, `-)` for async, distinguish sync/async arrows, show Named Credential token management.

**System Landscape Diagrams**: Nested subgraphs for grouping, top-to-bottom layering (Users -> Platform -> Integration -> External), label connections with protocol, short node labels.

**C4 Diagrams**: Context level for stakeholders, Container level for dev handoff, include technology labels, mark external with `System_Ext`. Note: experimental in Mermaid -- test before committing.

**ASCII Diagrams**: Width <= 80 chars, consistent box sizes, aligned arrows, step numbers for sequences.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Fields in ERD nodes | Unreadable at >6 objects | Name + record count only |
| `erDiagram` for large models | No color coding | Use `flowchart LR` |
| Missing legend | Reader can't decode colors/arrows | Always include legend subgraph |
| >12 objects in one diagram | Unreadable spaghetti | Decompose by domain |
| Hardcoded colors in `%%{init}` | Inconsistent theming | Use individual `style` declarations |
| Missing `autonumber` on sequences | Can't reference steps | Always add `autonumber` |
| No error paths in integrations | Incomplete picture | Add `alt`/`else` blocks |
| Labels in UI names | Breaks with locale changes | Use API names |

---

## Cross-Skill Integration

| Skill | Integration Point | How to Use |
|-------|-------------------|------------|
| `sf-metadata` | ERD auto-discovery | Query live object/field definitions for accurate data model diagrams |
| `sf-connected-apps` | OAuth diagrams | Get Connected App details (consumer key, certificates, pre-auth users) |
| `sf-integration` | Integration sequences | Named Credentials config, External Service specs, Platform Event definitions |
| `sf-ai-agentforce` | Agent architecture | Visualize Agentforce agent -> topic -> action flow |
| `sf-flow` | Process flowcharts | Document Flow decision logic as Mermaid flowcharts |

---

## Reference Files

| File | Content |
|------|---------|
| [references/diagram-examples.md](references/diagram-examples.md) | 6 complete Mermaid examples (OAuth, ERD, Integration, Landscape, C4) |
| [references/mermaid-syntax.md](references/mermaid-syntax.md) | Full syntax for sequenceDiagram, flowchart, erDiagram |
| [references/data-model-notation.md](references/data-model-notation.md) | ERD notation, color coding, LDV/OWD, templates, large-model strategies |
| [references/mermaid-styling.md](references/mermaid-styling.md) | Tailwind color palette, spacing config, node/subgraph styling |
| [references/preview-guide.md](references/preview-guide.md) | Localhost preview server setup and iteration workflow |

---

## Dependencies

**Required**: None (all templates are bundled)
**Optional**: sf-metadata (for ERD auto-discovery from live orgs)

---

## Notes

- **Mermaid Rendering**: Works in GitHub, VS Code, Notion, Confluence, and most modern tools
- **ASCII Purpose**: Terminal compatibility, plain-text documentation
- **Color Accessibility**: Palette designed for color-blind accessibility (icons supplement colors, high-contrast text)
- **C4 Diagrams**: Experimental in Mermaid -- may not render in all viewers
- **erDiagram Limitations**: No individual entity color styling; use `flowchart LR` when color coding is needed

---

## Sources

- [Mermaid Official Documentation](https://mermaid.js.org/intro/syntax-reference.html)
- [Mermaid Sequence Diagram Syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)
- [Mermaid Entity Relationship Diagram Syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
- [Mermaid Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)
- [Mermaid C4 Diagram Syntax (Experimental)](https://mermaid.js.org/syntax/c4.html)
- [Salesforce Data Model Notation](https://developer.salesforce.com/docs/platform/data-models/guide/salesforce-data-model-notation.html)
- [Salesforce Architects -- Diagrams](https://architect.salesforce.com/diagrams/framework/overview)
- [Salesforce Integration Patterns](https://architect.salesforce.com/fundamentals/integration-patterns)
- [C4 Model in Mermaid](https://lukemerrett.com/building-c4-diagrams-in-mermaid/)
- [CloudSundial -- Identity Flow Diagrams](https://cloudsundial.com/diagrams-of-identity-flows-in-context)
- [Tailwind CSS Color Palette](https://tailwindcss.com/docs/colors)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
