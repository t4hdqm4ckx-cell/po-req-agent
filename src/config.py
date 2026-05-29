"""
PO Requisition Agent — Central Configuration
All tunable parameters live here. Override via environment variables or CLI flags.
"""

import os
from decimal import Decimal

# ── Agent Identity ─────────────────────────────────────────────────────────────
AGENT_NAME    = "PO Requisition Agent"
AGENT_VERSION = "1.0.0"

# ── Approval Tier Thresholds ($) ───────────────────────────────────────────────
# Override with env vars: PO_MANAGER_THRESHOLD, PO_VP_THRESHOLD
MANAGER_THRESHOLD: Decimal = Decimal(os.getenv("PO_MANAGER_THRESHOLD", "5000.00"))
VP_THRESHOLD:      Decimal = Decimal(os.getenv("PO_VP_THRESHOLD",      "25000.00"))

APPROVAL_TIERS = {
    "auto": {
        "label":  "Auto-Approve",
        "status": "Approved – Auto",
        "min":    Decimal("0"),
        "max":    MANAGER_THRESHOLD - Decimal("0.01"),
    },
    "manager": {
        "label":  "Manager Approval",
        "status": "Pending – Manager Review",
        "min":    MANAGER_THRESHOLD,
        "max":    VP_THRESHOLD - Decimal("0.01"),
    },
    "vp": {
        "label":  "VP Approval",
        "status": "Pending – VP Review",
        "min":    VP_THRESHOLD,
        "max":    Decimal("Infinity"),
    },
}

# ── Validation Rules ───────────────────────────────────────────────────────────
REQUIRED_FIELDS = [
    "PO Number",
    "Requisition Date",
    "Department",
    "Cost Center",
    "Requester Name",
    "Vendor Name",
    "Vendor ID",
    "Line Item Description",
    "Quantity",
    "Unit Price ($)",
    "Total Amount ($)",
]

VENDOR_ID_PATTERN    = r"^V-\d{4}$"
COST_CENTER_PATTERN  = r"^CC-\d{3}$"
ROUNDING_TOLERANCE   = Decimal("0.02")
MAX_TAX_RATE         = Decimal("0.15")   # 15%
MIN_QUANTITY         = 1
MAX_FILE_ROWS        = 10_000            # Agent halts above this count

# ── Anomaly Detection Thresholds ───────────────────────────────────────────────
ANOMALY_VENDOR_CONCENTRATION = Decimal("0.20")   # Flag if single vendor > 20% of spend
ANOMALY_REQUESTER_MAX_POS    = 10                # Flag if requester submits > 10 POs
ANOMALY_HIGH_VALUE_PO        = Decimal("100000") # Flag any PO above $100K

# ── File & Directory Paths ─────────────────────────────────────────────────────
INPUT_DIR  = os.getenv("PO_INPUT_DIR",  "data/input")
OUTPUT_DIR = os.getenv("PO_OUTPUT_DIR", "data/output")

SUPPORTED_INPUT_EXTENSIONS = {".xlsx", ".xls", ".csv"}

# ── Output Formatting ──────────────────────────────────────────────────────────
EXCEL_FONT        = "Arial"
EXCEL_HEADER_SIZE = 10
EXCEL_DATA_SIZE   = 9

# Hex color palette (no # prefix for openpyxl)
COLORS = {
    "navy":        "1F3864",
    "white":       "FFFFFF",
    "light_blue":  "DCE6F1",
    "green":       "E2EFDA",
    "yellow":      "FFF2CC",
    "orange":      "FCE4D6",
    "red":         "FF0000",
    "gray":        "F2F2F2",
}

STATUS_COLORS = {
    "Approved – Auto":          COLORS["green"],
    "Pending – Manager Review": COLORS["yellow"],
    "Pending – VP Review":      COLORS["orange"],
    "Validation Error":         COLORS["red"],
    "Closed":                   COLORS["gray"],
    "Received":                 COLORS["green"],
    "Partially Received":       COLORS["yellow"],
}

CURRENCY_COLUMNS = {
    "Unit Price ($)",
    "Subtotal ($)",
    "Tax Amount ($)",
    "Total Amount ($)",
}

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_LEVEL       = os.getenv("PO_LOG_LEVEL", "INFO")   # DEBUG | INFO | WARNING
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOG_FORMAT      = "%(asctime)s  %(levelname)-8s  %(message)s"
