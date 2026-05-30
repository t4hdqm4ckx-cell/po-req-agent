# PO Requisition Agent — Run Summary
**Date:** 2026-05-29 · **Agent:** v1.0.0 · **Input:** `PO_Synthetic_Dataset.xlsx`

---

## At a Glance

| Metric | Value |
|---|---|
| Total rows processed | 200 |
| Valid POs | 50 (25%) |
| Validation errors | 150 (75%) |
| Total spend (valid POs) | $3,109,301.11 |
| Average PO value | $62,186.02 |
| Run duration | < 1s |

---

## Approval Queue

| Tier | Count | Spend | % of Total Spend |
|---|---|---|---|
| Auto-Approve (< $5K) | 3 | $8,998.92 | 0.3% |
| Manager Review ($5K–$25K) | 14 | $200,509.96 | 6.4% |
| VP Review (≥ $25K) | 33 | $2,899,792.23 | 93.3% |

**Action required:** 47 POs are in a pending state and need human review before processing.

---

## Validation Errors

All 150 errors share the same root cause: `Total Amount ≠ Quantity × Unit Price (±$0.02)`.

This is consistent with a systematic upstream issue — likely **tax amount being folded into `Total Amount ($)` in the source system** without being reflected in the `Tax Amount ($)` column, or a rounding/currency conversion step applied after line-item calculation.

**Recommendation:** Audit the source system's export logic. A one-time fix to the extraction query or export template should resolve the entire 75% failure rate.

---

## Top Spend by Department

| Department | Spend |
|---|---|
| Operations | $1,738,130 |
| Legal | $1,587,140 |
| Human Resources | $1,536,294 |
| Research | $1,428,838 |
| Sales | $1,354,243 |
| Engineering | $1,315,923 |
| IT Infrastructure | $1,253,438 |
| Product | $1,051,856 |
| Marketing | $896,144 |
| Finance | $701,363 |

---

## Top Spend by Category

| Category | Spend |
|---|---|
| IT Hardware | $918,643 |
| Professional Services | $643,892 |
| Marketing | $561,385 |
| Software SaaS | $404,883 |
| Facilities | $274,688 |
| Logistics | $262,247 |
| Office Supplies | $43,563 |

---

## Anomalies Flagged

### 🏢 Vendor Concentration
- **SecureNet Systems** — $626,438 (20.1% of run spend). Exceeds the 20% concentration threshold.  
  → Review vendor diversification strategy for IT Hardware.

### 👤 High-Volume Requesters (> 10 POs)
| Requester | PO Count |
|---|---|
| Monica Shaw | 24 |
| Patricia Dunn | 23 |
| Robert Nash | 23 |
| Carlos Mendes | 22 |
| James Park | 21 |
| Derek Lam | 21 |
| Priya Nair | 20 |
| Tanya Osei | 17 |
| Amanda Reyes | 15 |
| Sarah Chen | 14 |

→ Verify these represent legitimate activity and not duplicate submissions.

### 💰 High-Value POs (> $100K)
10 POs flagged. Largest:

| PO Number | Amount |
|---|---|
| PO-2024-0150 | $190,987.20 |
| PO-2025-0007 | $189,729.45 |
| PO-2024-0136 | $186,325.65 |
| PO-2025-0127 | $184,327.50 |
| PO-2024-0134 | $156,166.54 |

### 📅 Past-Due Needed-By Dates
62 POs have a `Needed By Date` in the past. Oldest: **PO-2025-0183** due 2024-02-11.  
→ Confirm whether these are stale requisitions or retroactive bookings.

---

## Output Files

| File | Description |
|---|---|
| `outputs/PO_Processed_20260529_224746.xlsx` | Full register (4 sheets) |
| `outputs/agent_log_20260529_224746.txt` | Detailed audit log |
| `outputs/dashboard.html` | Interactive HTML dashboard |

---

## Recommended Next Steps

1. **Fix source export** — resolve `Total Amount` mismatch to clear 150 validation errors.
2. **Review approval queue** — 33 VP-level and 14 Manager-level POs awaiting sign-off.
3. **Investigate SecureNet Systems** — vendor concentration above threshold; consider spreading IT Hardware spend.
4. **Triage past-due dates** — 62 POs; determine if stale or retroactive.
5. **High-volume requester audit** — spot-check top submitters for duplicate or split-order activity.
