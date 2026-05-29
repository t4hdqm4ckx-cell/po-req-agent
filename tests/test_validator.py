"""Unit tests for the validator module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validator import validate_pos, _validate_record


VALID_PO = {
    "PO Number":             "PO-2025-0001",
    "Requisition Date":      "2025-01-15",
    "Needed By Date":        "2025-02-01",
    "Department":            "Finance",
    "Cost Center":           "CC-100",
    "Requester Name":        "Sarah Chen",
    "Vendor Name":           "Acme Office Supplies",
    "Vendor ID":             "V-1001",
    "Line Item Description": "Copy Paper (Case)",
    "Quantity":              "10",
    "Unit Price ($)":        "50.00",
    "Total Amount ($)":      "500.00",
    "Tax Rate (%)":          "7.25%",
    "Tax Amount ($)":        "36.25",
}


def test_valid_po_passes():
    errors = _validate_record(VALID_PO)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_missing_required_field():
    po = {**VALID_PO}
    del po["Vendor ID"]
    errors = _validate_record(po)
    assert any("Vendor ID" in e for e in errors)


def test_invalid_quantity_zero():
    po = {**VALID_PO, "Quantity": "0"}
    errors = _validate_record(po)
    assert any("Quantity" in e for e in errors)


def test_total_mismatch():
    po = {**VALID_PO, "Total Amount ($)": "999.00"}
    errors = _validate_record(po)
    assert any("Total Amount" in e for e in errors)


def test_invalid_vendor_id_pattern():
    po = {**VALID_PO, "Vendor ID": "VENDOR-1"}
    errors = _validate_record(po)
    assert any("Vendor ID" in e for e in errors)


def test_invalid_cost_center_pattern():
    po = {**VALID_PO, "Cost Center": "DEPT-100"}
    errors = _validate_record(po)
    assert any("Cost Center" in e for e in errors)


def test_needed_before_requisition():
    po = {**VALID_PO, "Needed By Date": "2024-01-01"}
    errors = _validate_record(po)
    assert any("Needed By" in e for e in errors)


def test_tax_rate_too_high():
    po = {**VALID_PO, "Tax Rate (%)": "20%"}
    errors = _validate_record(po)
    assert any("Tax Rate" in e for e in errors)


def test_validate_pos_sets_status():
    results = validate_pos([VALID_PO])
    assert results[0]["Status"] == "Pending"


def test_validate_pos_error_status():
    bad_po = {**VALID_PO, "Quantity": "0"}
    results = validate_pos([bad_po])
    assert results[0]["Status"] == "Validation Error"
    assert results[0]["Validation Notes"] != ""
