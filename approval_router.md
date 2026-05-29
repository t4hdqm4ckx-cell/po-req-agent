# Approval Router — PO Requisition Agent

## Overview
The Approval Router is the core business logic module responsible for assigning
every validated PO record to the correct approval tier based on its total dollar
amount. It is the enforcement layer for the organization's procurement authorization
policy.

**Module:** `src/approval_router.py`
**Invoked by:** `src/main.py` (Step 3 of the pipeline)
**Input:** List of validated PO dicts (from `src/validator.py`)
**Output:** Same list with `Approval Tier`, `Approval Reason`, and `Status` fields populated

---

## Approval Tier Logic

The router applies a single rule: **Total Amount ($) determines the tier.**

| Tier | Default Range | Status Assigned | Auto-Processed |
|------|--------------|-----------------|----------------|
| Auto-Approve | < $5,000.00 | `Approved – Auto` | ✅ Yes |
| Manager Approval | $5,000.00 – $24,999.99 | `Pending – Manager Review` | ❌ No |
| VP Approval | ≥ $25,000.00 | `Pending – VP Review` | ❌ No |

Thresholds are defined in `src/config.py` and can be overridden at runtime via:
- Environment variables: `PO_MANAGER_THRESHOLD`, `PO_VP_THRESHOLD`
- CLI flags: `--manager-threshold`, `--vp-threshold`

---

## Fields Set by the Router

For every PO that passes validation, the router populates three fields:

### `Approval Tier`
The name of the tier assigned to the PO.

| Value | Meaning |
|-------|---------|
| `Auto-Approve` | Below manager threshold; no human review required |
| `Manager Approval` | Between manager and VP threshold; requires manager sign-off |
| `VP Approval` | At or above VP threshold; requires VP sign-off |
| `N/A` | Row had a validation error; routing was skipped |

---

### `Approval Reason`
A human-readable string explaining why the tier was assigned.

| Tier | Example Reason |
|------|---------------|
| Auto-Approve | `<$5,000.00 Threshold` |
| Manager Approval | `$5,000.00–$24,999.99 Threshold` |
| VP Approval | `≥$25,000.00 Threshold` |
| N/A | `Validation failed` |

---

### `Status`
The processing status written to the PO record after routing.

| Status | Description |
|--------|-------------|
| `Approved – Auto` | PO is approved; no further action required |
| `Pending – Manager Review` | PO is queued for manager approval |
| `Pending – VP Review` | PO is queued for VP approval |
| `Validation Error` | Set by validator; router does not override this status |

---

## Routing Flowchart

```
Incoming validated PO record
        │
        ▼
Status == "Validation Error"?
        │
       YES ──────────────────────────────────────────────────────────►
        │                                                    Approval Tier = "N/A"
        NO                                                   Approval Reason = "Validation failed"
        │                                                    Status unchanged → exit
        ▼
Parse Total Amount ($) as Decimal
        │
        ▼
Total < MANAGER_THRESHOLD ($5,000)?
        │
       YES ──────────────────────────────────────────────────────────►
        │                                                    Tier   = "Auto-Approve"
        NO                                                   Reason = "<$5,000.00 Threshold"
        │                                                    Status = "Approved – Auto"
        ▼
Total < VP_THRESHOLD ($25,000)?
        │
       YES ──────────────────────────────────────────────────────────►
        │                                                    Tier   = "Manager Approval"
        NO                                                   Reason = "$5,000.00–$24,999.99 Threshold"
        │                                                    Status = "Pending – Manager Review"
        ▼
Total ≥ VP_THRESHOLD ($25,000)
        │
        ▼
Tier   = "VP Approval"
Reason = "≥$25,000.00 Threshold"
Status = "Pending – VP Review"
```

---

## Threshold Configuration

### Default Values (`src/config.py`)
```python
MANAGER_THRESHOLD = Decimal("5000.00")
VP_THRESHOLD      = Decimal("25000.00")
```

### Override via Environment Variables
```bash
export PO_MANAGER_THRESHOLD=10000
export PO_VP_THRESHOLD=50000
python src/main.py --input data/input/pos.xlsx
```

### Override via CLI Flags
```bash
python src/main.py \
  --input data/input/pos.xlsx \
  --manager-threshold 10000 \
  --vp-threshold 50000
```

### Configuration Validation Rules
- `MANAGER_THRESHOLD` must be > 0
- `VP_THRESHOLD` must be > `MANAGER_THRESHOLD`
- If either rule is violated, the agent halts with a CRITICAL error before processing begins

---

## Boundary Behavior

The router uses strict less-than comparisons. Boundary values route as follows:

| Total Amount | Tier Assigned |
|-------------|--------------|
| $4,999.99 | Auto-Approve |
| $5,000.00 | Manager Approval |
| $24,999.99 | Manager Approval |
| $25,000.00 | VP Approval |
| $25,000.01 | VP Approval |

---

## Validation Error Passthrough

The router never modifies rows that have `Status = "Validation Error"`.
These rows are assigned:
- `Approval Tier` = `N/A`
- `Approval Reason` = `Validation failed`
- `Status` = unchanged (`Validation Error`)

This ensures validation errors are cleanly isolated from the approval workflow
and never appear in the `Approval Queue` output sheet.

---

## Output Sheets Driven by This Module

| Sheet | Contents | Populated By Router? |
|-------|----------|---------------------|
| PO Register | All rows including tier and status | ✅ Yes |
| Approval Queue | Rows where Status contains "Pending" | ✅ Yes (indirectly) |
| Validation Errors | Rows where Status = "Validation Error" | ❌ No (set by validator) |
| Run Summary | Tier counts and spend totals | ✅ Yes (indirectly) |

---

## Run Summary Metrics Driven by This Module

The `Run Summary` sheet aggregates the following from router output:

| Metric | Description |
|--------|-------------|
| Auto-Approved POs | Count of rows with Tier = `Auto-Approve` |
| Manager Approval POs | Count of rows with Tier = `Manager Approval` |
| VP Approval POs | Count of rows with Tier = `VP Approval` |
| Auto-Approve Spend ($) | Sum of Total Amount for Auto-Approve tier |
| Manager Approval Spend ($) | Sum of Total Amount for Manager Approval tier |
| VP Approval Spend ($) | Sum of Total Amount for VP Approval tier |

---

## Audit Considerations

When auditing approval routing, verify:

1. Every PO with `Total Amount ($)` < $5,000 has `Approval Tier = Auto-Approve`
2. Every PO with `Total Amount ($)` between $5,000–$24,999.99 has `Approval Tier = Manager Approval`
3. Every PO with `Total Amount ($)` ≥ $25,000 has `Approval Tier = VP Approval`
4. No validation error row was routed to an approval tier
5. Thresholds in `src/config.py` match the policy thresholds at time of run
6. No threshold was modified between run start and audit date
   (`git log --follow src/config.py`)

For full audit procedures see `AUDIT.md`.

---

## Related Files

| File | Relationship |
|------|-------------|
| `src/config.py` | Source of threshold values used by the router |
| `src/validator.py` | Runs before the router; sets `Validation Error` status |
| `src/output_writer.py` | Reads router output to build Approval Queue sheet |
| `AUDIT.md` | Audit procedures for verifying router decisions |
| `HUMAN_IN_THE_LOOP.md` | Defines human actions required for Pending statuses |
| `ERROR_HANDLING.md` | Documents configuration errors that block routing |
