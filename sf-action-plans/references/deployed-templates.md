# Deployed Action Plan Templates — XS Brokers Production

Last verified: 2026-02-13

## Template Summary

| Template | Id | Status | Items | Type |
|----------|----|--------|-------|------|
| Agency Onboarding - Independent | `0PRa5000000LgXJGA0` | Final | 4 DCIs + 6 Tasks | Industries |
| Agency Onboarding - Alliance | `0PRa5000000LgYvGAK` | Final | 4 DCIs + 6 Tasks | Industries |
| Agency Onboarding - Owned Group | `0PRa5000000LgaXGAS` | Final | 2 DCIs + 6 Tasks | Industries |
| 90-Day Growth Plan | `0PRa5000000LfBRGA0` | Final | 17 Tasks | Industries |

### Deactivated (Obsolete)

| Template | Id | Status | Notes |
|----------|----|--------|-------|
| Agency Onboarding - Independent (v1) | `0PRa5000000Lf9pGAC` | Obsolete | Original had 5 DCIs + 7 Tasks. |
| Agency Onboarding - Independent (v2) | `0PRa5000000Lg7VGAS` | Obsolete | Missing Task.ActivityDate — tasks invisible in UI. Replaced by `0PRa5000000LgXJGA0`. |
| Agency Onboarding - Alliance (v2) | `0PRa5000000Lg97GAC` | Obsolete | Missing Task.ActivityDate — tasks invisible in UI. Replaced by `0PRa5000000LgYvGAK`. |
| Agency Onboarding - Owned Group (v2) | `0PRa5000000Lg98GAC` | Obsolete | Missing Task.ActivityDate — tasks invisible in UI. Replaced by `0PRa5000000LgaXGAS`. |

---

## Agency Onboarding - Independent

**Id:** `0PRa5000000LgXJGA0`
**UniqueName:** `Agency_Onboarding_Independent_9e03d513_08b5_11f1_a087_cb5de7a1a997`
**Description:** Independent agency onboarding: 4 documents (Agreement, W-9, E&O, P&C License) + 6 BDM tasks. Auto-assigned via Intake Wizard or safety net flow.
**Target:** Account | **AdHoc Items:** false

### Document Checklist Items

| # | Name | UniqueName | Instruction |
|---|------|------------|-------------|
| 1 | Broker Agreement | `ind_v3_dci_1` | Collect the signed XS Brokers Broker Agreement from the agency. Legal contract covering commission terms, binding authority, trust account obligations, and E&S transaction responsibilities. Both parties must sign before appointment. |
| 2 | W-9 | `ind_v3_dci_2` | Collect IRS Form W-9. Required before commission payments. Must include legal entity name, tax classification, TIN/EIN, authorized signature. Current IRS version, signed within 12 months. |
| 3 | E&O Declaration Page | `ind_v3_dci_3` | Collect E&O insurance declaration page. Must show current policy period, adequate coverage limits, agency named as insured, insurance carrier. Full policy not required — declaration page only. |
| 4 | P&C License | `ind_v3_dci_4` | Collect P&C license for resident state. Must be current (not expired), match agency legal name. NPN should match Salesforce record. Future: NIPR API integration for automated verification. |

### Tasks

| # | Name | UniqueName | Priority | Days | Description |
|---|------|------------|----------|------|-------------|
| 5 | Schedule introduction call | `ind_v3_task_1` | High | 3 | Intro call with agency principal. Cover XS Brokers value prop, product lines, submission process, book of business discussion, onboarding timeline, commission structures. |
| 6 | Capture agency details in Salesforce | `ind_v3_task_2` | High | 3 | Complete Agency Intake Wizard. Capture: legal name, DBA, phone, website, NPN, agency owner, E&S premium written, business mix, E&S wholesalers used, primary contact details. |
| 7 | Send document request to agency | `ind_v3_task_3` | High | 5 | Send formal request for 4 documents (Agreement, W-9, E&O Dec Page, P&C License). Include instructions for each and submission deadline. |
| 8 | Follow up on outstanding documents | `ind_v3_task_4` | Normal | 14 | Check Document Checklist status. Follow up on items still marked 'New'. Escalate to sales leader if unresponsive. Update DCI status as received. |
| 9 | Review submission for completeness | `ind_v3_task_5` | High | 21 | Final review of all documents and Account record before appointment. Verify all fields populated, contacts created, docs signed/current. |
| 10 | Submit for appointment approval | `ind_v3_task_6` | High | 25 | Submit for formal appointment approval. Routes to manager, updates status Prospect→Active, notifies accounting for AIM setup, generates Agency Code. Phase 3 approval process pending. |

---

## Agency Onboarding - Alliance

**Id:** `0PRa5000000LgYvGAK`
**UniqueName:** `Agency_Onboarding_Alliance_c9947b5f_08b5_11f1_a087_897ca19fadd7`
**Description:** Alliance member onboarding: 4 documents (Agreement, W-9, E&O, P&C License) + 6 BDM tasks. Auto-assigned via Intake Wizard or safety net flow.
**Target:** Account | **AdHoc Items:** false

### Document Checklist Items

| # | Name | UniqueName | Instruction |
|---|------|------------|-------------|
| 1 | Broker Agreement | `al_v3_dci_1` | Collect signed XS Brokers Broker Agreement. Alliance-specific terms may differ from Independent. Both parties must sign before appointment. |
| 2 | W-9 | `al_v3_dci_2` | Collect IRS Form W-9. Required before commission payments. Current IRS version, signed within 12 months, with legal entity name, TIN/EIN. |
| 3 | E&O Declaration Page | `al_v3_dci_3` | Collect E&O declaration page. Current policy period, adequate limits, agency named as insured. |
| 4 | P&C License | `al_v3_dci_4` | Collect P&C license for resident state. Must be current, match legal name. NPN should match Salesforce record. |

### Tasks

| # | Name | UniqueName | Priority | Days | Description |
|---|------|------------|----------|------|-------------|
| 5 | Schedule introduction call | `al_v3_task_1` | High | 3 | Intro call covering XS Brokers value prop, product lines, submission process, and Alliance-specific commission/relationship terms. |
| 6 | Capture agency details in Salesforce | `al_v3_task_2` | High | 3 | Complete Agency Intake Wizard. Capture all profile details. Alliance members may have parent group context. |
| 7 | Send document request to agency | `al_v3_task_3` | High | 5 | Formal request for 4 documents with instructions and deadline. |
| 8 | Follow up on outstanding documents | `al_v3_task_4` | Normal | 14 | Check Document Checklist, follow up on outstanding items, escalate if unresponsive. |
| 9 | Review submission for completeness | `al_v3_task_5` | High | 21 | Final review of documents and Account record before appointment submission. |
| 10 | Submit for appointment approval | `al_v3_task_6` | High | 25 | Submit for formal appointment approval. Routes to manager, triggers status update and AIM setup. |

---

## Agency Onboarding - Owned Group

**Id:** `0PRa5000000LgaXGAS`
**UniqueName:** `Agency_Onboarding_Owned_Group_f481b566_08b5_11f1_8e57_1d789675b42b`
**Description:** Owned Group location onboarding: 2 documents (E&O, P&C License) + 6 BDM tasks. Parent handles Agreement and W-9. Auto-assigned via Intake Wizard or safety net flow.
**Target:** Account | **AdHoc Items:** false

### Document Checklist Items

Only 2 DCIs — parent group handles Agreement and W-9.

| # | Name | UniqueName | Instruction |
|---|------|------------|-------------|
| 1 | E&O Declaration Page | `og_v3_dci_1` | Collect E&O declaration page for this location's resident state. May differ from parent group's coverage. |
| 2 | P&C License | `og_v3_dci_2` | Collect P&C license for this location's resident state. Must be current, location-specific if different from parent. |

### Tasks

| # | Name | UniqueName | Priority | Days | Description |
|---|------|------------|----------|------|-------------|
| 3 | Schedule introduction call | `og_v3_task_1` | High | 3 | Intro call with location manager or primary contact. Coordinate with parent group's BDM if different. |
| 4 | Capture agency details in Salesforce | `og_v3_task_2` | High | 3 | Complete Intake Wizard for this location. Capture location-specific details (may differ from parent). |
| 5 | Send document request to agency | `og_v3_task_3` | High | 5 | Request 2 documents (E&O and P&C License). Fewer docs since parent handles Agreement and W-9. |
| 6 | Follow up on outstanding documents | `og_v3_task_4` | Normal | 10 | Check Document Checklist, follow up on outstanding items. |
| 7 | Review submission for completeness | `og_v3_task_5` | High | 14 | Final review. Verify documents current, Account fields populated, location linked to parent group. |
| 8 | Submit for appointment approval | `og_v3_task_6` | High | 18 | Submit location for appointment. Triggers status update, AIM setup for this location. |

---

## 90-Day Growth Plan

**Id:** `0PRa5000000LfBRGA0`
**UniqueName:** `X90_Day_Growth_Plan_d5f5e38a_07e6_11f1_bc93_a7f3a72ab162`
**Description:** 17-task growth plan across 3 phases (Days 1-30, 31-60, 61-90). Manually assigned by BDM after onboarding is complete.
**Target:** Account | **AdHoc Items:** false

This template is assigned AFTER onboarding completion. See the retrieved XML file at:
`force-app/main/default/actionPlanTemplates/X90_Day_Growth_Plan_d5f5e38a_07e6_11f1_bc93_a7f3a72ab162.apt-meta.xml`

---

## Source Control

Retrieved XML files in `force-app/main/default/actionPlanTemplates/`:

```
Agency_Onboarding_Independent_9e03d513_08b5_11f1_a087_cb5de7a1a997.apt-meta.xml
Agency_Onboarding_Alliance_c9947b5f_08b5_11f1_a087_897ca19fadd7.apt-meta.xml
Agency_Onboarding_Owned_Group_f481b566_08b5_11f1_8e57_1d789675b42b.apt-meta.xml
X90_Day_Growth_Plan_d5f5e38a_07e6_11f1_bc93_a7f3a72ab162.apt-meta.xml
```

These files are **reference-only** — deploying them via Metadata API creates ReadOnly templates.
To recreate, use the REST API workflow documented in SKILL.md.
