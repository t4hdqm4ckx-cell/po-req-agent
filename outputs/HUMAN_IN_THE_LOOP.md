# Human-in-the-Loop (HITL) Guidelines

## Overview
The PO Requisition Agent is designed to automate routine purchase order processing,
but certain conditions require human judgment before proceeding. This document defines
exactly when a human must be involved, what action is required, and who is responsible.

---

## Approval Routing — Required Human Review

### Manager Approval Required
**Trigger:** Any PO where `Total Amount ($)` is between **$5,000 and $24,999.99**
**Status set by agent:** `Pending – Manager Review`
**Human action required:**
- Review PO details in the `Approval Queue` sheet of the output Excel file
- Verify vendor, cost center, and business justification
- Approve or reject and update `Status` field manually
- Return updated file to `data/input/` for reprocessing if needed

**Responsible party:** Department Manager (listed in `Manager` column of the PO record)

---

### VP Approval Required
**Trigger:** Any PO where `Total Amount ($)` is **≥ $25,000**
**Status set by agent:** `Pending – VP Review`
**Human action required:**
- Review PO in the `Approval Queue` sheet
- Confirm strategic alignment, budget availability, and vendor selection rationale
- Obtain sign-off before issuing PO to vendor
- Document approval decision in the `Notes` field

**Responsible party:** VP or above (as designated by department hierarchy)

---

## Validation Failures — Required Human Correction

**Trigger:** Any row where `Status = "Validation Error"`
**Output location:** `Validation Errors` sheet in the processed Excel file
**Human action required:**
- Review the `Validation Notes` column for specific error details
- Correct the source data in the input file
- Re-run the agent after corrections are made

**Common validation errors requiring human correction:**
| Error | Human Action |
|-------|-------------|
| Missing required field | Locate and supply the missing value |
| Total Amount mismatch | Verify Qty × Unit Price and correct the total |
| Invalid Vendor ID format | Confirm vendor ID against the Vendor Reference sheet |
| Invalid Cost Center format | Confirm cost center with Finance or Accounting |
| Needed By Date in the past | Update date or escalate urgency to requester |
| Tax rate out of range | Confirm applicable tax rate with Finance |

---

## Anomaly Flags — Required Human Investigation

The agent flags anomalies in the audit log but does **not** block processing.
A human must review all anomalies before output files are acted upon.

| Anomaly | Trigger | Human Action Required |
|---------|---------|----------------------|
| Vendor concentration | Single vendor > 20% of total spend | Review for vendor dependency risk; confirm intentional |
| High-volume requester | Single requester > 10 POs in dataset | Verify legitimacy; check for duplicate submissions |
| High-value PO | Any single PO > $100,000 | Escalate to VP; confirm 3-quote procurement policy was followed |
| Past-due Needed By Date | `Needed By Date` is before today | Contact requester to update date or confirm urgency |
| Duplicate PO Number | Same PO Number appears more than once | Identify and remove duplicate; investigate root cause |

---

## File Size Safety Check

**Trigger:** Input file contains **more than 10,000 rows**
**Agent behavior:** Halts immediately and writes error to audit log
**Human action required:**
- Confirm the file is correct and not a system error
- Split into batches of ≤ 10,000 rows and reprocess
- Or explicitly override the limit (requires code change in `src/config.py`)

---

## When the Agent May NOT Proceed Autonomously

The agent must pause and wait for human confirmation in the following scenarios:

1. **Any VP-tier PO** — no PO ≥ $25,000 should be sent to a vendor without human sign-off
2. **Sole-source vendor situations** — flagged via `Notes` field containing "sole-source"
3. **Any PO flagged as a duplicate** — do not reissue until the duplicate is resolved
4. **Any validation error** — do not route or generate until source data is corrected
5. **Anomaly batch** — if more than 3 anomalies are detected in a single run, pause
   and surface the full anomaly list to a Finance manager before distributing output

---

## HITL Escalation Path
---

## Audit Trail Responsibility

All human approval decisions should be documented in the `Notes` field of the
relevant PO record before the file is reprocessed or archived. The agent audit log
(`agent_log_<timestamp>.txt`) serves as the system of record for all automated
decisions. Human overrides are the responsibility of the approving party.

