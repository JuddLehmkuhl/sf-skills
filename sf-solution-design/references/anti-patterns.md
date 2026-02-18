# Solution Design Anti-Patterns

Avoiding these common mistakes is as important as following best practices. Each anti-pattern includes the correct approach.

## Anti-Pattern 1: The Golden Hammer

**Symptom:** Using one tool for everything (e.g., building ALL automation in Apex, or ALL UI in custom LWC).

**Why it fails:** Increases maintenance burden, bypasses platform optimizations, and creates unnecessary technical debt.

**Correct approach:** Use the Decision Matrices in SKILL.md. Match the tool to the requirement, not the developer's comfort zone.

## Anti-Pattern 2: Custom Object Sprawl

**Symptom:** Creating custom objects (`Application__c`, `Request__c`, `Interaction__c`) when standard objects (Opportunity, Case, Task) would suffice.

**Why it fails:** Custom objects miss out on standard features (forecasting, entitlements, activity timelines, report types). They require custom security, sharing rules, and UI from scratch.

**Correct approach:** Run the Standard vs. Custom Object decision matrix. If a standard object covers 80%+ of the fields, use it with record types for differentiation.

## Anti-Pattern 3: Ignoring Industry Cloud Data Models

**Symptom:** Building a custom insurance data model when FSC provides InsurancePolicy, Claim, and Producer. Building a custom patient model when Health Cloud provides Patient and CarePlan.

**Why it fails:** Industry cloud objects include pre-built relationships, page layouts, reports, and process automation. Rebuilding these costs months and misses future platform enhancements.

**Correct approach:** Run Phase 1 (Feature Discovery) and Question 1 of the checklist. Always check industry cloud data models before creating custom objects.

## Anti-Pattern 4: Code Where Configuration Suffices

**Symptom:** Writing Apex triggers for field updates that could be Before-Save Flows. Writing Apex for validation that could be Validation Rules. Writing LWC for forms that could be Screen Flows.

**Why it fails:** Code requires test classes (95%+ coverage), deployments, and developer maintenance. Declarative solutions are admin-maintainable and auto-tested by the platform.

**Correct approach:** Use the Flow vs. Apex decision matrix. Only write Apex when declarative tools genuinely cannot handle the requirement.

## Anti-Pattern 5: Gold Plating / Over-Engineering

**Symptom:** Building a generic, framework-level solution for a one-off business requirement. Creating abstract service layers for simple CRUD operations. Adding "future flexibility" that is never used.

**Why it fails:** Premature abstraction adds complexity without value. YAGNI (You Aren't Gonna Need It) applies to Salesforce development too.

**Correct approach:** Build the simplest solution that meets the current requirement. Refactor when (not before) additional complexity is justified by real requirements.

## Anti-Pattern 6: Big Ball of Mud

**Symptom:** No clear separation between triggers, services, selectors, and controllers. God classes with 2000+ lines. Triggers with inline logic instead of framework delegation.

**Why it fails:** Untestable, undeployable, and unmaintainable. Changes in one area break unrelated functionality.

**Correct approach:** Follow the Trigger Actions Framework (`salesforce-trigger-framework/SKILL.md`). Use the layered architecture: `Trigger --> MetadataTriggerHandler --> TA_* --> Services --> DAL`.

## Anti-Pattern 7: Spaghetti Sharing Model

**Symptom:** Dozens of sharing rules, criteria-based sharing, Apex sharing, and manual shares layered on top of each other with no documentation.

**Why it fails:** Nobody can determine why a user does or does not have access to a record. Debugging access issues becomes a multi-day investigation.

**Correct approach:** Design the sharing model upfront. Use the simplest OWD (Organization-Wide Defaults) that meets security requirements. Layer sharing rules sparingly and document each one.

## Anti-Pattern 8: SOQL/DML in Loops

**Symptom:** Querying or updating records inside a `for` loop in Apex. Creating Flow loops that perform Get/Update elements per iteration.

**Why it fails:** Governor limits (100 SOQL queries, 150 DML statements per transaction). Fails silently in small tests but explodes in production with real data volumes.

**Correct approach:** Bulkify all data operations. Collect IDs, query once, process in memory, update once. In Flows, use collection variables. In Apex, use Maps and bulk DML. See `sf-apex/SKILL.md` for patterns.
