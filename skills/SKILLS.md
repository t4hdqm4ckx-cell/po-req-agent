# Cowork Skills Reference
> Run any skill by typing `/skill-name` in a new Claude session.  
> Skills are autonomous multi-step workflows — they use your connected tools and real data.

---

## Finance

| Skill | Command | What it does |
|---|---|---|
| BvA Variance Analysis | `/bva-variance-analysis` | Full Budget vs. Actuals workflow — upload a BvA Excel file and get variance highlights, commentary, an exec summary Word doc, and a variance slide deck |
| Variance Analysis | `/finance:variance-analysis` | Drill into variances across periods or cost centres |
| Financial Statements | `/finance:financial-statements` | Generate P&L, balance sheet, or cash flow statements |
| Reconciliation | `/finance:reconciliation` | Reconcile accounts and flag discrepancies |
| Journal Entry | `/finance:journal-entry` | Prep and format journal entries |
| Journal Entry Prep | `/finance:journal-entry-prep` | Draft journal entries from source documents |
| Close Management | `/finance:close-management` | Month-end / quarter-end close checklist and tracking |
| Audit Support | `/finance:audit-support` | Pull together audit evidence packages |
| SOX Testing | `/finance:sox-testing` | SOX control testing documentation and walkthroughs |

---

## Data & SQL

| Skill | Command | What it does |
|---|---|---|
| SQL Queries | `/data:sql-queries` | Write and run SQL against connected databases (BigQuery, Postgres, etc.) |
| Build Dashboard | `/data:build-dashboard` | Generate an interactive dashboard from any dataset |
| Analyze Data | `/data:analyze` | Exploratory analysis on a dataset you drop in |
| Statistical Analysis | `/data:statistical-analysis` | Descriptive stats, trends, and correlations |
| Data Visualization | `/data:create-viz` | Build charts and visualisations |
| Explore Data | `/data:explore-data` | Profile a dataset — shape, nulls, distributions |
| Write Query | `/data:write-query` | Translate a business question into SQL |
| Validate Data | `/data:validate-data` | Check a dataset for integrity issues |

---

## Documents & Reports

| Skill | Command | What it does |
|---|---|---|
| Excel / XLSX | `/xlsx` | Create, edit, or analyse Excel files |
| PowerPoint / PPTX | `/pptx` | Build or update PowerPoint slide decks |
| Word / DOCX | `/docx` | Create formatted Word documents |
| PDF | `/pdf` | Read, fill, merge, split, or sign PDF files |

---

## Productivity

| Skill | Command | What it does |
|---|---|---|
| Task Management | `/productivity:task-management` | Organise, prioritise, and track tasks |
| Memory Management | `/productivity:memory-management` | Update and consolidate your memory files |

---

## Tips

- **Drop a file** into the chat before running a skill — most finance and data skills will auto-detect it and start the workflow.
- **Chain skills** — run `/data:sql-queries` to pull data, then `/data:create-viz` to chart it, then `/pptx` to drop it into a deck.
- **BvA fast path** — paste your BvA Excel file and type `/bva-variance-analysis`; the skill handles the rest end-to-end.
- **PO Reqs** — this repo's agent (`python src/main.py --input <file>`) is itself a skill-like workflow; outputs land in `outputs/` and `data/output/`.

---

*Last updated: 2026-05-29 · [github.com/t4hdqm4ckx-cell/po-req-agent](https://github.com/t4hdqm4ckx-cell/po-req-agent)*
