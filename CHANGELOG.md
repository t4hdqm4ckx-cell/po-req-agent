# Changelog

All notable changes to the PO Requisition Agent will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-05-29

### Added
- Full end-to-end PO processing pipeline (intake → validation → approval routing →
  generation → anomaly detection → output)
- `src/main.py` — CLI entry point with `argparse` (`--input`, `--verbose`,
  `--manager-threshold`, `--vp-threshold`, `--output-dir`)
- `src/intake.py` — Excel/CSV file reader with schema detection
- `src/validator.py` — 9-rule field validation engine using Python `Decimal` arithmetic
- `src/approval_router.py` — Dollar-threshold tier assignment (Auto / Manager / VP)
- `src/generator.py` — PO record enrichment with agent metadata
- `src/anomaly_detector.py` — 5 post-processing anomaly scans
- `src/output_writer.py` — 4-sheet color-coded Excel output + plain-text audit log
- `src/config.py` — Central configuration with environment variable overrides
- `src/version.py` — Agent version string
- `tests/test_validator.py` — 10 unit tests for validation logic
- `tests/test_approval_router.py` — 6 unit tests for approval routing
- `tests/test_anomaly_detector.py` — 6 unit tests for anomaly detection
- `data/input/PO_Synthetic_Dataset.xlsx` — 200-row synthetic PO dataset (3 sheets)
- `CLAUDE.md` — Claude Code agent instructions
- `README.md` — Project overview, quickstart, input schema, and CLI reference
- `PRIVACY.md` — Data handling and privacy policy
- `SECURITY.md` — Security policy, design principles, and secure usage checklist
- `CHANGELOG.md` — This file
- `outputs/` — Directory for agent-generated output files
- `.gitignore` — Excludes real PO data, output files, and Python artifacts

### Approval Tiers (default thresholds)
| Tier             | Range              |
|------------------|--------------------|
| Auto-Approve     | < $5,000           |
| Manager Approval | $5,000 – $24,999   |
| VP Approval      | ≥ $25,000          |

### Anomaly Detection Rules
- Vendor concentration > 20% of total spend
- Single requester submitting > 10 POs
- Any PO total exceeding $100,000
- Needed By Date in the past
- Duplicate PO numbers

---

## [Unreleased]

### Planned
- Email notification support (SMTP) for pending approval queue
- Slack webhook integration for approval alerts
- Multi-line item support per PO (one-to-many line items)
- Budget availability check against cost center limits
- Web UI dashboard for approval queue management
- Docker container packaging
- GitHub Actions CI/CD pipeline with automated test runs

---

[1.0.0]: https://github.com/t4hdqm4ckx-cell/po-req-agent/releases/tag/v1.0.0
[Unreleased]: https://github.com/t4hdqm4ckx-cell/po-req-agent/compare/v1.0.0...HEAD
