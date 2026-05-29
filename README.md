# PO Requisition Agent

An autonomous, file-based Purchase Order processing agent built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Handles the full PO lifecycle: intake → validation → approval routing → PO generation → status tracking.

---

## Features

- **Full end-to-end workflow** — intake raw Excel/CSV, validate, route, generate, output
- **Dollar-threshold approval tiers** — Auto (<$5K), Manager ($5K–$25K), VP (≥$25K)
- **Strict field validation** — required fields, numeric integrity, date logic, ID patterns
- **Anomaly detection** — vendor concentration, duplicate POs, past-due dates, high-value flags
- **Formatted Excel output** — color-coded register, approval queue, error sheet, run summary
- **Full audit log** — timestamped text log with tier distributions and warnings
- **Zero external dependencies** — file-based only, no API calls or network access required

---

## Quickstart

```bash
git clone https://github.com/<your-org>/po-req-agent.git
cd po-req-agent
pip install -r requirements.txt

# Drop your PO file into data/input/, then run:
python src/main.py --input data/input/PO_Synthetic_Dataset.xlsx
```

Output files will appear in `data/output/`.

---

## Approval Tiers

| Total Amount       | Tier             | Auto-Approved |
|--------------------|------------------|---------------|
| < $5,000           | Auto-Approve     | ✅             |
| $5,000 – $24,999   | Manager Approval | ❌             |
| ≥ $25,000          | VP Approval      | ❌             |

Override thresholds at runtime:
```bash
python src/main.py --input data/input/pos.xlsx --manager-threshold 10000 --vp-threshold 50000
```

---

## Input Schema

| Column                  | Type    | Required | Notes                          |
|-------------------------|---------|----------|--------------------------------|
| PO Number               | string  | ✅        |                                |
| Requisition Date        | date    | ✅        | YYYY-MM-DD                     |
| Needed By Date          | date    |          | Must be ≥ Requisition Date     |
| Department              | string  | ✅        |                                |
| Cost Center             | string  | ✅        | Pattern: CC-###                |
| Requester Name          | string  | ✅        |                                |
| Manager                 | string  |          |                                |
| Vendor Name             | string  | ✅        |                                |
| Vendor ID               | string  | ✅        | Pattern: V-####                |
| Payment Terms           | string  |          |                                |
| Category                | string  |          |                                |
| Line Item Description   | string  | ✅        |                                |
| Quantity                | integer | ✅        | Must be ≥ 1                    |
| Unit Price ($)          | float   | ✅        | Must be > 0                    |
| Subtotal ($)            | float   |          |                                |
| Tax Rate (%)            | string  |          | 0%–15%                         |
| Tax Amount ($)          | float   |          |                                |
| Total Amount ($)        | float   | ✅        | Must equal Qty × Unit Price ±$0.02 |
| Notes                   | string  |          |                                |

---

## Output Files

```
data/output/
├── PO_Processed_20250101_120000.xlsx   ← full processed register (4 sheets)
└── agent_log_20250101_120000.txt       ← audit log
```

### Excel sheets
- **PO Register** — all rows, color-coded by status
- **Approval Queue** — pending POs only (for manager/VP action)
- **Validation Errors** — rows that failed validation with error details
- **Run Summary** — aggregate metrics and tier distribution

---

## Project Structure

```
po-req-agent/
├── CLAUDE.md                  ← Claude Code agent instructions
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── main.py                ← CLI entry point
│   ├── intake.py              ← file reading & schema detection
│   ├── validator.py           ← field validation logic
│   ├── approval_router.py     ← tier assignment
│   ├── generator.py           ← PO record construction
│   ├── output_writer.py       ← Excel + log file writing
│   ├── anomaly_detector.py    ← post-processing anomaly scans
│   └── version.py             ← agent version
├── data/
│   ├── input/                 ← drop source files here
│   └── output/                ← agent writes here
├── tests/
│   ├── test_validator.py
│   ├── test_approval_router.py
│   └── test_anomaly_detector.py
└── docs/
    └── WORKFLOW.md
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Built With

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — agentic execution
- `pandas` — data processing
- `openpyxl` — Excel I/O and formatting
- `argparse` — CLI interface

---

## License

MIT
