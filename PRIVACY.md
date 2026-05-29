# Privacy Policy

## Overview
The PO Requisition Agent ("Agent") is a file-based autonomous tool designed to process
purchase order requests locally. This document outlines how data is handled during
Agent operation.

## Data Handled
The Agent processes the following data types:
- **Purchase Order records** — vendor names, amounts, department/cost center codes
- **Personnel data** — requester names, manager names
- **Financial data** — unit prices, totals, tax rates, payment terms

## Data Storage
- All input files are read from `data/input/` and are **never modified or deleted**
- All output files are written exclusively to `data/output/`
- No data is transmitted externally — the Agent operates **100% locally, file-based only**
- No database, cloud service, or external API receives any processed data

## Data Retention
- Output files persist in `data/output/` until manually deleted
- The Agent does not implement any automatic retention or purge policy
- Audit logs in `data/output/` contain row-level processing records and should be
  managed in accordance with your organization's data retention policy

## Sensitive Data
The Agent may process data that is considered sensitive under applicable regulations
(GDPR, CCPA, SOX, etc.), including:
- Employee names and organizational structure
- Vendor financial relationships and spend data
- Internal cost center and budget information

**Recommended controls:**
- Restrict access to `data/input/` and `data/output/` to authorized personnel only
- Do not commit real PO data to version control (see `.gitignore`)
- Rotate or archive audit logs per your internal compliance schedule

## No External Transmission
This Agent makes **no network calls**. No data leaves the local machine during
any stage of processing: intake, validation, approval routing, generation, or output.

## Synthetic Data
The file `data/input/PO_Synthetic_Dataset.xlsx` included in this repository contains
**fully synthetic data** generated for testing purposes only. It contains no real
vendor names, employee records, or financial information.

## Contact
For questions regarding data handling in this project, contact the repository owner
via GitHub Issues.
