# PO Requisition Agent — Workflow Documentation

## Overview

The PO Requisition Agent processes purchase order requests through a six-step pipeline,
from raw file intake to formatted Excel output and a full audit log.

```
data/input/
    └── PO_file.xlsx
           │
           ▼
    ┌─────────────┐
    │  1. Intake  │  Read Excel/CSV → list of raw PO dicts
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │  2. Validation  │  Required fields, numeric checks, date logic, ID patterns
    └──────┬──────────┘
           │
    ┌──────▼──────────────┐
    │  3. Approval Routing │  Assign tier based on Total Amount ($)
    └──────┬───────────────┘
           │
    ┌──────▼──────────────┐
    │  4. PO Generation   │  Enrich with metadata (timestamp, agent version)
    └──────┬───────────────┘
           │
    ┌──────▼──────────────────┐
    │  5. Anomaly Detection   │  Vendor concentration, duplicates, past-due, etc.
    └──────┬───────────────────┘
           │
    ┌──────▼────────────────────────────────────┐
    │  6. Output                                │
    │     PO_Processed_YYYYMMDD_HHMMSS.xlsx     │
    │     agent_log_YYYYMMDD_HHMMSS.txt         │
    └───────────────────────────────────────────┘
           │
    data/output/
```

---

## Step 1 — Intake

**Module:** `src/intake.py`

Reads `.xlsx`, `.xls`, or `.csv` files using `pandas`. All columns are read as
strings to prevent silent type coercion. Column names are stripped of whitespace.
Missing values are normalized to `None`.

**Failure mode:** If the file is missing or unreadable, the agent logs the error
and exits with code 1.

---

## Step 2 — Validation

**Module:** `src/validator.py`

All rows are validated independently. Errors are accumulated (not short-circuited).
A row with any error receives `Status = "Validation Error"` and a pipe-separated
`Validation Notes` string listing every failure.

### Validation Rules

| Check | Rule |
|-------|------|
| Required fields | All 11 required fields must be non-null |
| Quantity | Positive integer ≥ 1 |
| Unit Price | Float > 0 |
| Total Amount | Must equal Qty × Unit Price ±$0.02 |
| Requisition Date | Must be a parseable date |
| Needed By Date | If present, must be ≥ Requisition Date |
| Tax Rate | If present, must be 0%–15% |
| Vendor ID | Must match `V-\d{4}` |
| Cost Center | Must match `CC-\d{3}` |

---

## Step 3 — Approval Routing

**Module:** `src/approval_router.py`

Applies dollar-threshold tiers to all validated rows. Validation errors skip routing.

| Tier | Default Range | Status Assigned |
|------|---------------|-----------------|
| Auto-Approve | < $5,000 | `Approved – Auto` |
| Manager Approval | $5,000 – $24,999.99 | `Pending – Manager Review` |
| VP Approval | ≥ $25,000 | `Pending – VP Review` |

Thresholds are configurable via CLI flags `--manager-threshold` and `--vp-threshold`.

---

## Step 4 — PO Generation

**Module:** `src/generator.py`

Enriches each record with:
- `Processed Timestamp` — ISO 8601 UTC timestamp of the agent run
- `Agent Version` — from `src/version.py`

---

## Step 5 — Anomaly Detection

**Module:** `src/anomaly_detector.py`

Post-processing scans on the full record set:

| Anomaly | Trigger |
|---------|---------|
| Vendor concentration | Single vendor > 20% of total spend |
| High-volume requester | Single requester submits > 10 POs |
| High-value PO | Any PO total > $100,000 |
| Past-due needed-by | `Needed By Date` is before today |
| Duplicate PO numbers | Same `PO Number` appears more than once |

Anomalies are reported in the audit log but do **not** block processing.

---

## Step 6 — Output

**Module:** `src/output_writer.py`

### Excel File (`PO_Processed_<ts>.xlsx`)

| Sheet | Contents |
|-------|----------|
| PO Register | All rows, color-coded by Status |
| Approval Queue | Rows with Status containing "Pending" |
| Validation Errors | Rows with Status = "Validation Error" |
| Run Summary | Aggregate counts, spend totals, tier breakdown |

### Color Coding

| Status | Color |
|--------|-------|
| Approved – Auto | Green |
| Pending – Manager Review | Yellow |
| Pending – VP Review | Orange |
| Validation Error | Red (white text) |
| Closed / Received | Gray |

### Audit Log (`agent_log_<ts>.txt`)

Plain-text file containing:
- Run timestamp, input filename, row counts
- Approval tier distribution
- Per-row validation error details
- All anomaly warnings

---

## CLI Reference

```bash
python src/main.py \
  --input data/input/PO_Synthetic_Dataset.xlsx \
  --manager-threshold 5000 \
  --vp-threshold 25000 \
  --output-dir data/output \
  --verbose
```

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | required | Path to input file |
| `--manager-threshold` | 5000 | Lower bound for Manager Approval tier |
| `--vp-threshold` | 25000 | Lower bound for VP Approval tier |
| `--output-dir` | `data/output` | Output directory |
| `--verbose` | off | Enable DEBUG logging |
