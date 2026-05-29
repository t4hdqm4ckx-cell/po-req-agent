# Audit Guide — PO Requisition Agent

## Overview
This document provides step-by-step instructions for auditing both the PO Requisition
Agent's automated processing logic and the human approval decisions made during the
PO lifecycle. It is intended for internal audit teams, Finance managers, and compliance
officers conducting periodic or ad-hoc reviews.

---

## 1. Audit Objectives

| Objective | Description |
|-----------|-------------|
| Process Integrity | Confirm the agent applied correct validation rules and approval tiers |
| Approval Compliance | Verify all POs above threshold received appropriate human sign-off |
| Data Accuracy | Confirm PO amounts, vendors, and cost centers are accurate and complete |
| Anomaly Resolution | Confirm all flagged anomalies were investigated and resolved |
| Segregation of Duties | Confirm no requester approved their own PO |
| Completeness | Confirm all submitted POs were processed with no silent failures |

---

## 2. Audit Artifacts

Before beginning an audit, collect the following files from `data/output/` and `outputs/`:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Processed Excel file | `data/output/PO_Processed_<timestamp>.xlsx` | Primary record of all PO decisions |
| Audit log | `data/output/agent_log_<timestamp>.txt` | Agent run log with tier distribution and anomalies |
| Input source file | `data/input/PO_Synthetic_Dataset.xlsx` (or actual input) | Original unmodified PO data |
| HUMAN_IN_THE_LOOP.md | `outputs/HUMAN_IN_THE_LOOP.md` | HITL policy reference |
| config.py | `src/config.py` | Agent configuration at time of run |
| version.py | `src/version.py` | Agent version at time of run |

---

## 3. Pre-Audit Checklist

- [ ] Obtain the exact input file used for the run being audited
- [ ] Obtain the corresponding processed Excel output and audit log (matched by timestamp)
- [ ] Confirm agent version in `version.py` matches `Agent Version` field in the Excel output
- [ ] Confirm approval thresholds in `config.py` match those recorded in the Run Summary sheet
- [ ] Confirm no modifications were made to the input file after agent processing
- [ ] Confirm output files have not been manually edited (check file modified timestamps)

---

## 4. Step-by-Step Audit Procedures

### 4.1 Validate Approval Tier Assignment

**Objective:** Confirm every PO was assigned the correct approval tier based on Total Amount.

**Steps:**
1. Open `PO_Processed_<timestamp>.xlsx` → `PO Register` sheet
2. Filter the `Approval Tier` column
3. For each tier, verify the `Total Amount ($)` falls within the correct range:

| Tier | Expected Range |
|------|---------------|
| Auto-Approve | < $5,000 |
| Manager Approval | $5,000 – $24,999.99 |
| VP Approval | ≥ $25,000 |

4. Flag any row where the tier does not match the amount
5. Cross-reference `Approval Reason` column — it should state the threshold applied
6. Document any discrepancies in the audit findings log

**Pass criteria:** 100% of POs assigned to the correct tier with no exceptions

---

### 4.2 Audit Validation Error Handling

**Objective:** Confirm all validation errors were correctly identified and isolated.

**Steps:**
1. Open `PO Register` sheet → filter `Status = "Validation Error"`
2. Cross-reference with `Validation Errors` sheet — row counts must match exactly
3. For each error row, review the `Validation Notes` column:
   - Confirm the stated error is accurate against the source data
   - Confirm no valid PO was incorrectly flagged as an error
4. Verify no validation error rows appear in the `Approval Queue` sheet
5. Confirm error rows were not processed through approval routing
   (`Approval Tier` should be `N/A`)

**Pass criteria:** All validation errors correctly flagged; no error rows routed for approval

---

### 4.3 Audit Human Approval Compliance

**Objective:** Confirm all POs requiring human review received documented approval.

**Steps:**
1. Open `Approval Queue` sheet — this contains all `Pending` status POs
2. For each row, verify:
   - `Manager` field is populated (approver is identified)
   - `Notes` field contains approval documentation or decision rationale
   - `Status` has been updated from `Pending` to a resolved state if reprocessed
3. For VP-tier POs (≥ $25,000):
   - Confirm VP name or approval reference is documented in `Notes`
   - Confirm no VP-tier PO was sent to vendor without resolved status
4. Check for segregation of duties violations:
   - `Requester Name` must not match `Manager` on the same PO
   - Flag any self-approved POs immediately

**Pass criteria:** All pending POs have documented approver; no self-approvals

---

### 4.4 Audit Anomaly Detection and Resolution

**Objective:** Confirm all anomalies were investigated and appropriately resolved.

**Steps:**
1. Open `data/output/agent_log_<timestamp>.txt`
2. Navigate to the `--- Anomalies ---` section
3. For each anomaly listed, verify:

| Anomaly Type | Audit Check |
|-------------|-------------|
| Vendor concentration > 20% | Confirm Finance Manager reviewed and approved concentration |
| High-volume requester > 10 POs | Confirm no duplicate submissions; legitimate volume explained |
| High-value PO > $100,000 | Confirm 3-quote policy was followed; VP approval documented |
| Past-due Needed By Date | Confirm requester updated date or urgency was escalated |
| Duplicate PO Number | Confirm duplicate was identified, removed, and root cause documented |

4. Confirm resolution documentation exists for each anomaly (email, notes, or updated PO record)

**Pass criteria:** All anomalies have documented resolution; no unresolved flags

---

### 4.5 Audit Completeness — Row Count Reconciliation

**Objective:** Confirm no POs were silently dropped or duplicated during processing.

**Steps:**
1. Count total rows in the input source file (excluding header)
2. Count total rows in the `PO Register` sheet of the processed Excel output
3. Counts must match exactly
4. Cross-check with the audit log:
   - `Input Rows (Total)` must equal source file row count
   - `Valid POs` + `Validation Errors` must equal `Input Rows (Total)`
5. Verify `Run Summary` sheet totals are consistent with `PO Register` row counts

**Reconciliation formula:**
**Pass criteria:** Zero unexplained variance between input count and output count

---

### 4.6 Audit Financial Accuracy

**Objective:** Confirm monetary calculations are accurate across all PO records.

**Steps:**
1. For a random sample of ≥ 20 POs from `PO Register`:
   - Verify: `Subtotal ($)` = `Quantity` × `Unit Price ($)`
   - Verify: `Tax Amount ($)` = `Subtotal ($)` × `Tax Rate (%)`
   - Verify: `Total Amount ($)` = `Subtotal ($)` + `Tax Amount ($)`
2. Confirm `Total Spend ($)` in `Run Summary` equals `=SUM` of all `Total Amount ($)` values
3. Spot-check `Average PO Value ($)` in Run Summary against manual calculation
4. Flag any row where amounts do not reconcile within $0.02 rounding tolerance

**Pass criteria:** All sampled rows reconcile within rounding tolerance; summary totals match

---

### 4.7 Audit Agent Configuration Integrity

**Objective:** Confirm the agent was not misconfigured to bypass controls.

**Steps:**
1. Review `src/config.py` at the time of the run:
   - `MANAGER_THRESHOLD` = $5,000.00 (or documented override)
   - `VP_THRESHOLD` = $25,000.00 (or documented override)
   - `MAX_FILE_ROWS` = 10,000
   - `ANOMALY_VENDOR_CONCENTRATION` = 0.20 (20%)
   - `ANOMALY_HIGH_VALUE_PO` = $100,000
2. Confirm no threshold was lowered or disabled without documented approval
3. Verify `AGENT_VERSION` in `src/version.py` matches the version recorded in processed output
4. Confirm `src/config.py` was not modified between run start and audit date
   (check git commit history: `git log --follow src/config.py`)

**Pass criteria:** All thresholds match policy; no unauthorized configuration changes

---

## 5. Audit Findings Log Template

For each finding, document the following:
---

## 6. Audit Frequency Recommendations

| Audit Type | Frequency | Scope |
|------------|-----------|-------|
| Full process audit | Quarterly | All steps in this guide |
| Approval compliance spot-check | Monthly | Sections 4.3 and 4.4 only |
| Configuration integrity check | Every agent update | Section 4.7 only |
| Financial accuracy sample | Monthly | Section 4.6 — 20 PO sample |
| Anomaly resolution review | After every agent run | Section 4.4 |

---

## 7. Escalation Path for Audit Findings
---

## 8. Audit Sign-Off

Upon completion of a full audit cycle, the auditor must document:

| Field | Value |
|-------|-------|
| Audit Period | [Start Date] – [End Date] |
| Agent Version Audited | v1.0.0 |
| Total POs Reviewed | |
| Total Findings | |
| Critical Findings | |
| High Findings | |
| Overall Assessment | Pass / Pass with Findings / Fail |
| Auditor Name | |
| Auditor Signature | |
| Date Completed | |
| Reviewed By | |

