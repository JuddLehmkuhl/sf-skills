# Usage Examples

Worked examples showing how the 8-question checklist drives solution design decisions.

## Example 1: "We need to send follow-up emails after meetings"

**Checklist Results:**
- Q2 (Einstein AI): YES -- Meeting Follow-Up Emails PSL available

**Solution:** Configure Einstein Meeting Follow-Up Emails feature. No custom code needed.
**Route to:** Einstein Setup (declarative).

## Example 2: "We need to visualize account ownership hierarchies"

**Checklist Results:**
- Q1 (Standard Features): YES -- ARC (FSC) or Account Hierarchy (standard) available

**Solution:** Configure ARC relationship graph with ownership roles (FSC) or use standard Account Hierarchy. No custom components needed.
**Route to:** `sf-metadata` for relationship configuration.

## Example 3: "We need to automate prospect outreach"

**Checklist Results:**
- Q3 (Agentforce): YES -- SDR Agent PSLs available

**Solution:** Build SDR Agent with custom topics for your industry. No custom Apex/Flows needed.
**Route to:** `sf-ai-agentforce` for agent creation.

## Example 4: "We need to sync data from an external system"

**Checklist Results:**
- Q4 (Data Cloud): Check -- Are Data Cloud PSLs available?
  - If YES: Configure Data Cloud pipeline with identity resolution.
  - If NO: Use Named Credentials + External Services for REST integration.

**Route to:** `sf-integration` for Named Credentials / External Services setup.

## Example 5: "We need a guided onboarding wizard"

**Checklist Results:**
- Q5 (OmniStudio): Check -- Are OmniStudio PSLs available?
  - If YES: Build OmniScript for guided flow with FlexCards for context.
  - If NO: Build Screen Flow with Dynamic Forms. If that is insufficient, build custom LWC.

**Route to:** `sf-flow` for Screen Flows, or `sf-lwc` for custom components.

## Example 6: "We need to track required documents for a loan application"

**Checklist Results:**
- Q1 (Standard Features): YES -- Document Checklist Items + Action Plan Templates available
- Q8 (Documents): YES -- DocGen for template generation if needed

**Solution:** Use Action Plan Templates with Document Checklist Items to track required documents. No custom objects needed.
**Route to:** `sf-action-plans` for template creation.

## Example 7: "We need a nightly batch job to process 2M records"

**Checklist Results:**
- All 8 questions: NO -- This is a bulk data processing requirement

**Decision Matrix (Flow vs. Apex):** Apex -- Batch Apex is required for >10k records with governor limit management.

**Solution:** Build Batch Apex class with proper chunking and error handling.
**Route to:** `sf-apex` for Batch Apex creation, then `sf-testing` for test coverage.

## Example 8: "We need a custom object to track insurance policies"

**Checklist Results:**
- Q1 (Standard Features): Check -- Is FSC licensed?
  - If YES: Use standard InsurancePolicy object. **Do NOT create a custom object.**
  - If NO: Custom object may be needed. Run Standard vs. Custom Object matrix.

**Route to:** `sf-metadata` for either standard object configuration or custom object creation.
