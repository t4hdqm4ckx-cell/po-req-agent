"""Anomaly detection module — post-processing scans for unusual patterns."""

import logging
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

log = logging.getLogger(__name__)

HIGH_VALUE_THRESHOLD  = Decimal("100000")
MAX_VENDOR_SPEND_PCT  = Decimal("0.20")
MAX_REQUESTER_POS     = 10


def detect_anomalies(records: list[dict[str, Any]]) -> list[str]:
    """Scan PO records and return a list of anomaly warning strings."""
    anomalies: list[str] = []

    def to_dec(val: Any) -> Decimal:
        try:
            return Decimal(str(val).replace(",", "").replace("$", "").strip())
        except Exception:
            return Decimal("0")

    valid = [r for r in records if r.get("Status") != "Validation Error"]
    total_spend = sum(to_dec(r.get("Total Amount ($)", 0)) for r in valid)

    # 1 — Vendor concentration
    vendor_spend: dict[str, Decimal] = {}
    for r in valid:
        v = str(r.get("Vendor Name", "Unknown"))
        vendor_spend[v] = vendor_spend.get(v, Decimal("0")) + to_dec(r.get("Total Amount ($)", 0))

    if total_spend > 0:
        for vendor, spend in vendor_spend.items():
            pct = spend / total_spend
            if pct > MAX_VENDOR_SPEND_PCT:
                anomalies.append(
                    f"Vendor concentration: '{vendor}' represents {pct:.1%} of total spend "
                    f"(${spend:,.2f} of ${total_spend:,.2f})"
                )

    # 2 — High-volume requesters
    requester_counts = Counter(str(r.get("Requester Name", "")) for r in records)
    for name, count in requester_counts.items():
        if count > MAX_REQUESTER_POS:
            anomalies.append(f"High-volume requester: '{name}' submitted {count} POs")

    # 3 — High-value POs
    for r in valid:
        total = to_dec(r.get("Total Amount ($)", 0))
        if total > HIGH_VALUE_THRESHOLD:
            anomalies.append(
                f"High-value PO: {r.get('PO Number')} = ${total:,.2f} (>{HIGH_VALUE_THRESHOLD:,})"
            )

    # 4 — Past-due needed-by dates
    today = datetime.now(timezone.utc).date()
    for r in valid:
        nb = r.get("Needed By Date")
        if nb:
            try:
                from dateutil import parser as dp
                nb_date = dp.parse(str(nb)).date()
                if nb_date < today:
                    anomalies.append(
                        f"Past-due: PO {r.get('PO Number')} Needed By {nb_date} is in the past"
                    )
            except Exception:
                pass

    # 5 — Duplicate PO numbers
    po_nums = [str(r.get("PO Number", "")) for r in records]
    dupes   = [n for n, c in Counter(po_nums).items() if c > 1 and n]
    for d in dupes:
        anomalies.append(f"Duplicate PO Number detected: '{d}'")

    return anomalies
