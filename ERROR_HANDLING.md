# Error Handling Guide — PO Requisition Agent

## Overview
This document details every error type the PO Requisition Agent can produce, what
causes each error, how the agent responds, and what corrective action is required.
It is intended for developers, Finance operations staff, and system administrators.

---

## Error Severity Levels

| Level | Description | Agent Behavior |
|-------|-------------|----------------|
| **CRITICAL** | Agent cannot continue; run is halted | Writes error to audit log and exits with code 1 |
| **ERROR** | A specific PO record failed processing | Row flagged as `Validation Error`; run continues |
| **WARNING** | Anomaly or data quality issue detected | Logged in audit log; run continues |
| **INFO** | Normal operational message | Logged to console and audit log |

---

## 1. File-Level Errors (CRITICAL)

These errors halt the agent entirely before any PO is processed.

### 1.1 Input File Not Found
**Trigger:** The file path passed to `--input` does not exist
**Agent behavior:** Logs error and exits with code 1
**Error message:**
```
ERROR  Input file not found: data/input/my_pos.xlsx
```
**Corrective action:**
- Confirm the file path is correct
- Confirm the file exists in `data/input/`
- Re-run with the correct `--input` path

---

### 1.2 Unsupported File Type
**Trigger:** Input file extension is not `.xlsx`, `.xls`, or `.csv`
**Agent behavior:** Logs error and exits with code 1
**Error message:**
```
ERROR  Unsupported file type '.pdf'. Supported: {'.xlsx', '.xls', '.csv'}
```
**Corrective action:**
- Convert the file to `.xlsx` or `.csv` before running the agent
- Do not rename the extension without converting the format

---

### 1.3 File Unreadable or Corrupt
**Trigger:** File exists but cannot be parsed (password-protected, corrupt, wrong format)
**Agent behavior:** Logs error and exits with code 1
**Error message:**
```
ERROR  Failed to read input file: [Errno 13] Permission denied / File is not a zip file
```
**Corrective action:**
- Confirm the file is not password-protected
- Re-export the file from its source system as a fresh `.xlsx` or `.csv`
- Confirm read permissions on the file: `ls -la data/input/`

---

### 1.4 Input File Exceeds Row Limit
**Trigger:** Input file contains more than 10,000 rows (configurable in `src/config.py`)
**Agent behavior:** Logs error and exits with code 1
**Error message:**
```
ERROR  Input file contains 12,450 rows, exceeding MAX_FILE_ROWS limit of 10,000.
       Split into batches and reprocess.
```
**Corrective action:**
- Split the input file into batches of ≤ 10,000 rows
- Process each batch separately
- To override the limit, update `MAX_FILE_ROWS` in `src/config.py` with documented approval

---

### 1.5 Output Directory Not Writable
**Trigger:** Agent cannot write to `data/output/`
**Agent behavior:** Logs error and exits with code 1
**Error message:**
```
ERROR  Cannot write to output directory: data/output/
```
**Corrective action:**
- Check directory permissions: `ls -la data/`
- Grant write access: `chmod 755 data/output/`
- Confirm disk space is available: `df -h`

---

## 2. Row-Level Validation Errors (ERROR)

These errors apply to individual PO rows. The agent flags the row and continues
processing all remaining rows.

All row errors are:
- Written to the `Validation Notes` column in the processed Excel output
- Visible in the `Validation Errors` sheet of the output workbook
- Summarized in the audit log under `--- Validation Errors ---`

### 2.1 Missing Required Field
**Trigger:** Any of the 11 required fields is blank or null
**Status set:** `Validation Error`
**Validation Note example:**
```
Missing required field: 'Vendor ID'
```
**Corrective action:**
- Locate the row in the source input file
- Supply the missing value
- Re-run the agent with the corrected file

---

### 2.2 Invalid Quantity
**Trigger:** `Quantity` is zero, negative, non-numeric, or a decimal
**Validation Note example:**
```
Quantity must be a positive integer ≥ 1
```
**Corrective action:**
- Confirm the quantity with the requester
- Update to a whole number ≥ 1 in the source file

---

### 2.3 Invalid Unit Price
**Trigger:** `Unit Price ($)` is zero, negative, or non-numeric
**Validation Note example:**
```
Unit Price ($) must be > 0
```
**Corrective action:**
- Confirm the unit price with the vendor quote or procurement record
- Update the source file with the correct positive value

---

### 2.4 Total Amount Mismatch
**Trigger:** `Total Amount ($)` does not equal `Quantity × Unit Price ($)` within ±$0.02
**Validation Note example:**
```
Total Amount ($1,250.00) does not equal Qty × Unit Price ($1,200.00) within ±$0.02
```
**Corrective action:**
- Recalculate: `Total = Quantity × Unit Price`
- If tax is included in the total, ensure `Subtotal` and `Tax Amount` fields are
  populated correctly and `Total = Subtotal + Tax Amount`
- Update the source file with the correct total

---

### 2.5 Invalid Date Format
**Trigger:** `Requisition Date` cannot be parsed as a valid date
**Validation Note example:**
```
Requisition Date is not a valid date
```
**Corrective action:**
- Reformat the date as `YYYY-MM-DD` (e.g., `2025-05-29`)
- Confirm the cell is not stored as plain text in Excel (format as Date)

---

### 2.6 Needed By Date Before Requisition Date
**Trigger:** `Needed By Date` is earlier than `Requisition Date`
**Validation Note example:**
```
Needed By Date must be ≥ Requisition Date
```
**Corrective action:**
- Confirm both dates with the requester
- Update to a valid future needed-by date

---

### 2.7 Tax Rate Out of Range
**Trigger:** `Tax Rate (%)` is negative or exceeds 15%
**Validation Note example:**
```
Tax Rate (20.00%) must be between 0% and 15%
```
**Corrective action:**
- Confirm the applicable tax rate with your Finance or Tax team
- Update the source file with the correct rate
- If a rate above 15% is legitimately required, update `MAX_TAX_RATE` in
  `src/config.py` with documented approval

---

### 2.8 Invalid Vendor ID Format
**Trigger:** `Vendor ID` does not match the pattern `V-####` (e.g., `V-1001`)
**Validation Note example:**
```
Vendor ID 'VENDOR-1' must match pattern V-####
```
**Corrective action:**
- Look up the correct Vendor ID in the `Vendor Reference` sheet
- Update the source file with the correctly formatted ID

---

### 2.9 Invalid Cost Center Format
**Trigger:** `Cost Center` does not match the pattern `CC-###` (e.g., `CC-100`)
**Validation Note example:**
```
Cost Center 'DEPT-100' must match pattern CC-###
```
**Corrective action:**
- Confirm the correct cost center code with Finance or Accounting
- Update the source file with the correctly formatted code

---

## 3. Anomaly Warnings (WARNING)

Anomalies do not block processing but must be reviewed before output is acted upon.
All anomalies are written to the audit log under `--- Anomalies ---`.

### 3.1 Vendor Concentration
**Trigger:** A single vendor accounts for > 20% of total PO spend
**Log message:**
```
WARNING  Vendor concentration: 'Acme Office Supplies' represents 34.2% of total spend
         ($51,300.00 of $150,000.00)
```
**Resolution:** Finance Manager must review and confirm concentration is intentional

---

### 3.2 High-Volume Requester
**Trigger:** A single requester name appears on > 10 POs in the dataset
**Log message:**
```
WARNING  High-volume requester: 'Sarah Chen' submitted 14 POs
```
**Resolution:** Verify no duplicate submissions; confirm volume is legitimate

---

### 3.3 High-Value PO
**Trigger:** A single PO total exceeds $100,000
**Log message:**
```
WARNING  High-value PO: PO-2025-0042 = $125,000.00 (>$100,000)
```
**Resolution:** Confirm VP approval and 3-quote procurement policy compliance

---

### 3.4 Past-Due Needed By Date
**Trigger:** `Needed By Date` is before today's date
**Log message:**
```
WARNING  Past-due: PO PO-2025-0018 Needed By 2024-12-01 is in the past
```
**Resolution:** Contact requester to update the date or confirm urgency

---

### 3.5 Duplicate PO Number
**Trigger:** The same `PO Number` appears more than once in the input file
**Log message:**
```
WARNING  Duplicate PO Number detected: 'PO-2025-0007'
```
**Resolution:** Identify which record is the original; remove the duplicate from
the source file; investigate how the duplicate was created

---

## 4. Configuration Errors (CRITICAL)

### 4.1 Invalid Threshold Configuration
**Trigger:** `MANAGER_THRESHOLD` ≥ `VP_THRESHOLD` in `src/config.py`
**Agent behavior:** Logs error and exits with code 1
**Corrective action:**
- Ensure `MANAGER_THRESHOLD` < `VP_THRESHOLD` at all times
- Example valid config: Manager = $5,000 / VP = $25,000

---

### 4.2 Invalid Environment Variable
**Trigger:** `PO_MANAGER_THRESHOLD` or `PO_VP_THRESHOLD` environment variable is set
to a non-numeric value
**Log message:**
```
ERROR  Invalid value for PO_MANAGER_THRESHOLD: 'five-thousand' — must be numeric
```
**Corrective action:**
- Set environment variables as plain numbers: `export PO_MANAGER_THRESHOLD=5000`
- Or remove the environment variable to use the default from `src/config.py`

---

## 5. Reprocessing After Errors

### Standard Reprocessing Workflow
1. Open the `Validation Errors` sheet in `PO_Processed_<timestamp>.xlsx`
2. Review the `Validation Notes` column for each error row
3. Correct the corresponding rows in the original input file
4. Save the corrected file to `data/input/` (use a new filename with a version suffix,
   e.g., `PO_Batch_001_v2.xlsx`)
5. Re-run the agent:
   ```bash
   python src/main.py --input data/input/PO_Batch_001_v2.xlsx
   ```
6. Confirm the `Validation Errors` sheet in the new output is empty

---

## 6. Debugging with Verbose Mode

For detailed step-by-step logging during a run, use the `--verbose` flag:

```bash
python src/main.py --input data/input/PO_Synthetic_Dataset.xlsx --verbose
```

Verbose mode outputs DEBUG-level logs including:
- Per-row validation results
- Approval tier assignment for every PO
- Anomaly detection scan progress
- File read/write confirmation

---

## 7. Error Quick Reference

| Error | Level | Agent Stops? | Fix Location |
|-------|-------|-------------|--------------|
| File not found | CRITICAL | ✅ Yes | CLI `--input` path |
| Unsupported file type | CRITICAL | ✅ Yes | Convert file format |
| File unreadable / corrupt | CRITICAL | ✅ Yes | Re-export source file |
| Exceeds 10,000 row limit | CRITICAL | ✅ Yes | Split input file |
| Output dir not writable | CRITICAL | ✅ Yes | Fix permissions |
| Missing required field | ERROR | ❌ No | Source input file |
| Invalid quantity | ERROR | ❌ No | Source input file |
| Invalid unit price | ERROR | ❌ No | Source input file |
| Total amount mismatch | ERROR | ❌ No | Source input file |
| Invalid date format | ERROR | ❌ No | Source input file |
| Needed By before Req Date | ERROR | ❌ No | Source input file |
| Tax rate out of range | ERROR | ❌ No | Source input file / config.py |
| Invalid Vendor ID format | ERROR | ❌ No | Source input file |
| Invalid Cost Center format | ERROR | ❌ No | Source input file |
| Vendor concentration | WARNING | ❌ No | Finance Manager review |
| High-volume requester | WARNING | ❌ No | Manual investigation |
| High-value PO | WARNING | ❌ No | VP approval required |
| Past-due Needed By Date | WARNING | ❌ No | Update date with requester |
| Duplicate PO Number | WARNING | ❌ No | Remove duplicate from source |
| Invalid threshold config | CRITICAL | ✅ Yes | src/config.py |
| Invalid env variable | CRITICAL | ✅ Yes | Environment / shell config |
