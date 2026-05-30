---
name: Bug Report
about: Incorrect output, wrong tier routing, missed anomaly, or agent crash
labels: bug
---

## What happened?
<!-- One-sentence summary -->

## Expected behaviour
<!-- What should the agent have done? -->

## Actual behaviour
<!-- What did it do instead? -->

## Input details
- Input file name / row count:
- PO Numbers affected (if applicable):
- Agent version (`src/version.py`):

## Relevant log lines
```
<!-- Paste from agent_log_<timestamp>.txt -->
```

## Reproduction steps
```bash
python src/main.py --input <file> --verbose
```

## Category
- [ ] Validation rule (false positive / false negative)
- [ ] Approval tier routing (wrong tier assigned)
- [ ] Anomaly detection (flag missed or incorrect)
- [ ] Output file (missing sheet, wrong formatting)
- [ ] Agent crash / unhandled exception
- [ ] Other
