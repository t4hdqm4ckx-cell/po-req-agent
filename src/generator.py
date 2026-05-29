"""Generator module — enriches PO records with agent metadata."""

from datetime import datetime, timezone
from typing import Any

from version import AGENT_VERSION


def build_po_records(
    records: list[dict[str, Any]],
    run_ts: datetime,
) -> list[dict[str, Any]]:
    """Add agent metadata fields to each record."""
    ts_str = run_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    enriched = []
    for rec in records:
        po = dict(rec)
        po["Processed Timestamp"] = ts_str
        po["Agent Version"]       = AGENT_VERSION
        enriched.append(po)
    return enriched
