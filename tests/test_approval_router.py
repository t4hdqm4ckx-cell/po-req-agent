"""Unit tests for the approval router module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from approval_router import route_approvals

THRESHOLDS = {"manager": 5000.0, "vp": 25000.0}

BASE = {
    "PO Number": "PO-2025-0001",
    "Status":    "Pending",
    "Total Amount ($)": "0",
}


def make_po(total: str) -> dict:
    return {**BASE, "Total Amount ($)": total}


def test_auto_approve_below_manager():
    result = route_approvals([make_po("4999.99")], THRESHOLDS)
    assert result[0]["Approval Tier"] == "Auto-Approve"
    assert result[0]["Status"]        == "Approved – Auto"


def test_manager_approval_boundary():
    result = route_approvals([make_po("5000.00")], THRESHOLDS)
    assert result[0]["Approval Tier"] == "Manager Approval"
    assert result[0]["Status"]        == "Pending – Manager Review"


def test_vp_approval_boundary():
    result = route_approvals([make_po("25000.00")], THRESHOLDS)
    assert result[0]["Approval Tier"] == "VP Approval"
    assert result[0]["Status"]        == "Pending – VP Review"


def test_high_value_vp():
    result = route_approvals([make_po("150000.00")], THRESHOLDS)
    assert result[0]["Approval Tier"] == "VP Approval"


def test_validation_errors_skip_routing():
    error_po = {**BASE, "Status": "Validation Error", "Total Amount ($)": "50000"}
    result   = route_approvals([error_po], THRESHOLDS)
    assert result[0]["Approval Tier"] == "N/A"


def test_custom_thresholds():
    result = route_approvals([make_po("8000.00")], {"manager": 10000.0, "vp": 50000.0})
    assert result[0]["Approval Tier"] == "Auto-Approve"
