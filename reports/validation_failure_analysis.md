# Validation Failure Analysis
**Dataset:** `PO_Synthetic_Dataset.xlsx` · **Run:** 2026-05-29 · **Agent:** v1.0.0

---

## Summary

**150 of 200 rows (75%) failed validation** — all due to the same single error type:

> `Total Amount ($X) does not equal Qty × Unit Price ($Y) within ±$0.02`

No other validation rule failures were detected in this dataset.

---

## Root Cause Analysis

### What the rule checks
```
|Total Amount ($) - (Quantity × Unit Price ($))| ≤ $0.02
```

### What we observe
Every failing row shows `Total Amount > Quantity × Unit Price` by a consistent factor. Sampling:

| PO Number | Total Amount | Qty × Unit Price | Δ | Δ % |
|---|---|---|---|---|
| PO-2025-0001 | $64,459.65 | $60,102.24 | +$4,357.41 | +7.25% |
| PO-2024-0002 | $943.26 | $879.50 | +$63.76 | +7.25% |
| PO-2025-0003 | $33,154.50 | $30,486.90 | +$2,667.60 | +8.75% |
| PO-2024-0020 | $216,724.26 | $197,921.70 | +$18,802.56 | +9.50% |
| PO-2025-0055 | $172,621.72 | $157,645.41 | +$14,976.31 | +9.50% |

### Pattern
The delta percentage varies between ~7% and ~10% across rows — consistent with **tax being included in `Total Amount ($)` but not reflected in the `Tax Amount ($)` column**. The `Tax Rate (%)` column in the dataset contains values in this range, confirming the hypothesis.

### Likely cause
The source system (ERP/procurement platform) is exporting `Total Amount` as the **post-tax total** while the agent's validation rule expects it to equal the **pre-tax subtotal** (`Quantity × Unit Price`). The `Tax Amount ($)` column is either blank or not being populated by the export.

---

## Validation Rule Options

Three ways to resolve — the right choice depends on business intent:

### Option A — Update the validation rule *(recommended)*
Change the check to:
```
Total Amount ($) ≈ (Quantity × Unit Price) + Tax Amount ($)
```
This makes the rule tax-aware and matches how the source system exports data.

**Pros:** No upstream changes needed; handles varying tax rates correctly.  
**Cons:** Requires `Tax Amount ($)` to be reliably populated.

### Option B — Fix the source export
Update the ERP export query/template so `Total Amount ($)` equals `Quantity × Unit Price` (pre-tax), and `Tax Amount ($)` carries the tax separately.

**Pros:** Keeps the agent's validation rule simple and unambiguous.  
**Cons:** Requires coordination with the system that generates the input files.

### Option C — Widen the rounding tolerance
Increase `rounding_tolerance` in `config/thresholds.yaml` from `$0.02` to a larger value.

**Pros:** Zero code or upstream changes.  
**Cons:** Masks real data quality issues; not recommended.

---

## Recommendation

**Short term:** Apply Option A in `src/validator.py` to unblock the current dataset.  
**Long term:** Coordinate with the source system owner to implement Option B for cleaner data contracts.

---

## Affected POs (150 rows)

All errors are of type `Total Amount mismatch`. A full list is in `outputs/agent_log_20260529_224746.txt`.

Representative sample by department:

| Department | Error Count |
|---|---|
| Operations | ~23 |
| Legal | ~21 |
| Human Resources | ~20 |
| Research | ~19 |
| Sales | ~18 |
| Engineering | ~17 |
| IT Infrastructure | ~16 |
| Product | ~13 |
| Marketing | ~12 |
| Finance | ~9 |

---

## Next Steps

- [ ] Confirm tax hypothesis with source system owner
- [ ] Implement Option A or B (see above)
- [ ] Re-run agent against corrected dataset
- [ ] Update `schemas/po_input_schema.json` if `Total Amount` semantics change
