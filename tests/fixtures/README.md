# Test Fixtures

Small XLSX files used by the test suite. **Never edit manually** — regenerate with `tests/generate_fixtures.py`.

| File | Rows | Purpose |
|---|---|---|
| `fixture_clean.xlsx` | 5 | All valid — one row per approval tier, including boundary values ($4,999.99 and $25,000.00) |
| `fixture_errors.xlsx` | 6 | Each row triggers a different validation error: missing field, total mismatch, bad Vendor ID, bad Cost Center, tax rate > 15%, Needed By Date before Requisition Date |
| `fixture_edge_cases.xlsx` | 4 | Boundary conditions: minimum PO value ($0.01), rounding within ±$0.02 (pass), rounding just outside (fail), max tax rate exactly 15% |

## Regenerating

```bash
python3 tests/generate_fixtures.py
```
