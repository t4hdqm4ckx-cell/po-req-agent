"""Unit tests for the anomaly detector module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anomaly_detector import detect_anomalies

BASE_PO = {
    "PO Number":      "PO-001",
    "Vendor Name":    "Acme",
    "Requester Name": "Sarah Chen",
    "Total Amount ($)": "1000.00",
    "Status":         "Approved – Auto",
    "Needed By Date": "2099-12-31",
}


def test_no_anomalies_clean_data():
    records = [{**BASE_PO, "PO Number": f"PO-{i:03d}"} for i in range(5)]
    anomalies = detect_anomalies(records)
    assert anomalies == []


def test_duplicate_po_number():
    records = [BASE_PO, BASE_PO]
    anomalies = detect_anomalies(records)
    assert any("Duplicate" in a for a in anomalies)


def test_high_value_po():
    po = {**BASE_PO, "Total Amount ($)": "150000.00"}
    anomalies = detect_anomalies([po])
    assert any("High-value" in a for a in anomalies)


def test_vendor_concentration():
    # One vendor dominates >20% of spend
    records = [
        {**BASE_PO, "PO Number": "PO-001", "Vendor Name": "BigVendor", "Total Amount ($)": "90000"},
        {**BASE_PO, "PO Number": "PO-002", "Vendor Name": "Other",     "Total Amount ($)": "10000"},
    ]
    anomalies = detect_anomalies(records)
    assert any("concentration" in a.lower() for a in anomalies)


def test_high_volume_requester():
    records = [
        {**BASE_PO, "PO Number": f"PO-{i:03d}", "Requester Name": "Heavy User"}
        for i in range(11)
    ]
    anomalies = detect_anomalies(records)
    assert any("High-volume" in a for a in anomalies)


def test_past_due_needed_by():
    po = {**BASE_PO, "Needed By Date": "2020-01-01"}
    anomalies = detect_anomalies([po])
    assert any("Past-due" in a for a in anomalies)
