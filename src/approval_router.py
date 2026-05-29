"""Approval routing module — assigns tier and status based on dollar thresholds."""

import logging
from decimal import Decimal
from typing import Any

log = logging.getLogger(__name__)


def route_approvals(
    records: list[dict[str, Any]],
    thresholds: dict[str, float],
) -> list[dict[str, Any]]:
    """Assign Approval Tier and Status to each validated PO."""
    manager_min = Decimal(str(thresholds["manager"]))
    vp_min      = Decimal(str(thresholds["vp"]))

    routed = []
    for rec in records:
        po = dict(rec)
        if po.get("Status") == "Validation Error":
            po["Approval Tier"]   = "N/A"
            po["Approval Reason"] = "Validation failed"
            routed.append(po)
            continue

        total_str = str(po.get("Total Amount ($)", "0")).replace(",", "").replace("$", "").strip()
        try:
            total = Decimal(total_str)
        except Exception:
            total = Decimal("0")

        if total < manager_min:
            po["Approval Tier"]   = "Auto-Approve"
            po["Approval Reason"] = f"<${manager_min:,.2f} Threshold"
            po["Status"]          = "Approved – Auto"
        elif total < vp_min:
            po["Approval Tier"]   = "Manager Approval"
            po["Approval Reason"] = f"${manager_min:,.2f}–${vp_min:,.2f} Threshold"
            po["Status"]          = "Pending – Manager Review"
        else:
            po["Approval Tier"]   = "VP Approval"
            po["Approval Reason"] = f"≥${vp_min:,.2f} Threshold"
            po["Status"]          = "Pending – VP Review"

        log.debug(f"PO {po.get('PO Number')} → {po['Approval Tier']} (${total:,.2f})")
        routed.append(po)

    return routed
