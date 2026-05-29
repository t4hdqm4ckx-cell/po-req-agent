# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅        |

## Reporting a Vulnerability
If you discover a security vulnerability in this project, please do **not** open a
public GitHub Issue. Instead, contact the repository owner directly via GitHub's
private security advisory feature:

1. Navigate to the **Security** tab of this repository
2. Click **Report a vulnerability**
3. Provide a detailed description, steps to reproduce, and potential impact

You can expect an acknowledgment within **48 hours** and a resolution or mitigation
plan within **14 days**.

## Security Design Principles

### File-Based Isolation
- The Agent reads only from `data/input/` and writes only to `data/output/`
- No network calls are made at any stage of processing
- No external APIs, databases, or cloud services are contacted
- Input files are never modified or deleted

### Input Validation
- All PO records are validated before processing (see `src/validator.py`)
- Required fields are enforced; malformed records are flagged and isolated
- Numeric fields use Python's `Decimal` type to prevent float manipulation
- ID fields (`Vendor ID`, `Cost Center`) are validated against strict regex patterns

### No Credential Handling
- The Agent does not accept, store, or transmit credentials of any kind
- No authentication tokens, API keys, or passwords are used or required
- No `.env` files or secrets management is implemented — none is needed

### Dependency Security
- Dependencies are pinned in `requirements.txt`
- Only four third-party libraries are used: `pandas`, `openpyxl`, `python-dateutil`, `pytest`
- Regularly audit dependencies with:
```bash
  pip audit
```

### Version Control Hygiene
- Real PO data files are excluded from version control via `.gitignore`
- Only synthetic test data (`PO_Synthetic_Dataset.xlsx`) is committed to the repository
- Audit logs and processed output files are gitignored by default

### Principle of Least Privilege
- The Agent requires read access to `data/input/` and write access to `data/output/` only
- No system-level permissions, admin rights, or elevated privileges are required
- Recommended: run the Agent as a non-privileged user in production environments

## Known Limitations
- The Agent does not encrypt output files at rest — apply OS-level encryption if required
- Audit logs contain PO-level detail; restrict access to `data/output/` accordingly
- No role-based access control is implemented — access is managed at the OS/filesystem level

## Secure Usage Checklist
- [ ] Do not commit real PO data to version control
- [ ] Restrict `data/input/` and `data/output/` directory permissions to authorized users only
- [ ] Run `pip audit` after installing or updating dependencies
- [ ] Archive and purge `data/output/` logs per your organization's retention policy
- [ ] Review `CLAUDE.md` before running the Agent to confirm business rules are correct
