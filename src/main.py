"""
PO Requisition Agent — Entry Point
Usage: python src/main.py --input data/input/PO_Synthetic_Dataset.xlsx
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import timezone, datetime

from version import AGENT_NAME, AGENT_VERSION
from intake import load_po_file
from validator import validate_pos
from approval_router import route_approvals
from generator import build_po_records
from anomaly_detector import detect_anomalies
from output_writer import write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{AGENT_NAME} v{AGENT_VERSION}")
    parser.add_argument("--input",              required=True, help="Path to input Excel or CSV file")
    parser.add_argument("--manager-threshold",  type=float, default=5000.0,  help="Lower bound for Manager Approval tier")
    parser.add_argument("--vp-threshold",       type=float, default=25000.0, help="Lower bound for VP Approval tier")
    parser.add_argument("--output-dir",         default="data/output",       help="Directory for output files")
    parser.add_argument("--verbose",            action="store_true",         help="Enable DEBUG logging")
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    args = configure_args = parse_args()
    configure_logging(args.verbose)

    log = logging.getLogger(__name__)
    run_ts = datetime.now(timezone.utc)

    log.info(f"=== {AGENT_NAME} v{AGENT_VERSION} — run started at {run_ts.isoformat()} ===")
    log.info(f"Input file       : {args.input}")
    log.info(f"Manager threshold: ${args.manager_threshold:,.2f}")
    log.info(f"VP threshold     : ${args.vp_threshold:,.2f}")

    thresholds = {
        "manager": args.manager_threshold,
        "vp":      args.vp_threshold,
    }

    # Step 1 — Intake
    raw_pos = load_po_file(Path(args.input))
    log.info(f"Loaded {len(raw_pos)} rows from input file.")

    # Step 2 — Validate
    validated = validate_pos(raw_pos)
    error_count = sum(1 for p in validated if p.get("Status") == "Validation Error")
    log.info(f"Validation complete. Errors: {error_count} / {len(validated)}")

    # Step 3 — Approval routing
    routed = route_approvals(validated, thresholds)
    tier_counts = {}
    for p in routed:
        tier = p.get("Approval Tier", "N/A")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    for tier, count in tier_counts.items():
        log.info(f"  Tier '{tier}': {count} POs")

    # Step 4 — Build PO records
    records = build_po_records(routed, run_ts)

    # Step 5 — Anomaly detection
    anomalies = detect_anomalies(records)
    if anomalies:
        log.warning(f"Anomalies detected: {len(anomalies)}")
        for a in anomalies:
            log.warning(f"  ⚠  {a}")

    # Step 6 — Write outputs
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path, log_path = write_outputs(records, anomalies, out_dir, run_ts, thresholds, Path(args.input).name)

    log.info(f"Output Excel : {xlsx_path}")
    log.info(f"Audit log    : {log_path}")
    log.info("=== Run complete ===")


if __name__ == "__main__":
    main()
