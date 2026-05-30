# Vendor Concentration Watch
*Append a new entry after each agent run. One data point is noise; a trend is a risk.*

---

## Threshold
Flag any vendor whose spend exceeds **20%** of total run spend (`config/thresholds.yaml → anomaly_detection.vendor_concentration_pct`).

---

## Run History

### 2026-05-29 · PO_Synthetic_Dataset.xlsx · Agent v1.0.0

| Vendor | Spend | % of Run Total | Flag |
|---|---|---|---|
| SecureNet Systems | $626,438.32 | 20.1% | ⚠️ Above threshold |
| Pinnacle Consulting | $415,616.09 | 13.4% | ✅ Within threshold |
| PixelCraft Agency | $341,825.74 | 11.0% | ✅ Within threshold |
| FastShip Logistics | $238,683.32 | 7.7% | ✅ Within threshold |
| TechPro Solutions | $228,910.09 | 7.4% | ✅ Within threshold |

**Total run spend:** $3,109,301.11 (valid POs only)

**Action:** SecureNet Systems marginally exceeds the 20% threshold at 20.1%.  
Recommend reviewing IT Hardware sourcing strategy to ensure at least one qualified alternative vendor is engaged.

---

*Future runs will be appended below this line.*
