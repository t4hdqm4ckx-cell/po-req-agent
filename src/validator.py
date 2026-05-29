"""Validator module — field-level validation for PO records."""
from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from dateutil import parser as dateparser

log = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "PO Number", "Requisition Date", "Department", "Cost Center",
    "Requester Name", "Vendor Name", "Vendor ID",
    "Line Item Description", "Quantity", "Unit Price ($)", "Total Amount ($)",
]

VENDOR_ID_RE     = re.compile(r"^V-\d{4}$")
COST_CENTER_RE   = re.compile(r"^CC-\d{3}$")
ROUNDING_TOL     = Decimal("0.02")
MAX_TAX_RATE     = Decimal("0.15")


def _to_decimal(value: Any) -> Decimal | None:
    """Safely convert a value to Decimal; returns None on failure."""
    if value is None:
        return None
    try:
        cleaned = str(value).replace(",", "").replace("$", "").strip()
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_date(value: Any):
    """Parse a date string; returns None on failure."""
    if value is None:
        return None
    try:
        return dateparser.parse(str(value))
    except Exception:
        return None


def validate_pos(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate all PO records. Adds 'Status' and 'Validation Notes' keys."""
    validated = []
    for rec in records:
        errors = _validate_record(rec)
        po = dict(rec)
        if errors:
            po["Status"]           = "Validation Error"
            po["Validation Notes"] = " | ".join(errors)
            log.debug(f"PO {po.get('PO Number', '?')} validation errors: {errors}")
        else:
            po["Status"]           = "Pending"
            po["Validation Notes"] = ""
        validated.append(po)
    return validated


def _validate_record(rec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return errors  # Stop early — downstream checks need values present

    # Quantity
    qty = _to_decimal(rec.get("Quantity"))
    if qty is None or qty < 1 or qty != qty.to_integral_value():
        errors.append("Quantity must be a positive integer ≥ 1")

    # Unit price
    unit_price = _to_decimal(rec.get("Unit Price ($)"))
    if unit_price is None or unit_price <= 0:
        errors.append("Unit Price ($) must be > 0")

    # Total amount integrity check
    total = _to_decimal(rec.get("Total Amount ($)"))
    if total is None or total <= 0:
        errors.append("Total Amount ($) must be > 0")
    elif qty and unit_price:
        expected = qty * unit_price
        if abs(total - expected) > ROUNDING_TOL:
            errors.append(
                f"Total Amount (${total}) does not equal Qty × Unit Price "
                f"(${expected:.2f}) within ±$0.02"
            )

    # Dates
    req_date    = _parse_date(rec.get("Requisition Date"))
    needed_date = _parse_date(rec.get("Needed By Date"))
    if req_date is None:
        errors.append("Requisition Date is not a valid date")
    if needed_date is not None and req_date is not None and needed_date < req_date:
        errors.append("Needed By Date must be ≥ Requisition Date")

    # Tax rate
    tax_raw = rec.get("Tax Rate (%)")
    if tax_raw:
        try:
            rate = Decimal(str(tax_raw).replace("%", "").strip()) / 100
            if rate < 0 or rate > MAX_TAX_RATE:
                errors.append(f"Tax Rate ({tax_raw}) must be between 0% and 15%")
        except InvalidOperation:
            errors.append(f"Tax Rate ({tax_raw}) is not a valid number")

    # ID patterns
    vendor_id = str(rec.get("Vendor ID", "")).strip()
    if not VENDOR_ID_RE.match(vendor_id):
        errors.append(f"Vendor ID '{vendor_id}' must match pattern V-####")

    cost_center = str(rec.get("Cost Center", "")).strip()
    if not COST_CENTER_RE.match(cost_center):
        errors.append(f"Cost Center '{cost_center}' must match pattern CC-###")

    return errors
