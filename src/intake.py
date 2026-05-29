"""Intake module — reads Excel/CSV input files into a list of PO dicts."""

import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def load_po_file(path: Path) -> list[dict[str, Any]]:
    """Read a PO input file and return rows as a list of dicts.

    Raises SystemExit on unreadable or unsupported files.
    """
    if not path.exists():
        log.error(f"Input file not found: {path}")
        sys.exit(1)

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        log.error(f"Unsupported file type '{ext}'. Supported: {SUPPORTED_EXTENSIONS}")
        sys.exit(1)

    try:
        if ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path, dtype=str)
        else:
            df = pd.read_csv(path, dtype=str)
    except Exception as exc:
        log.error(f"Failed to read input file: {exc}")
        sys.exit(1)

    df.columns = [str(c).strip() for c in df.columns]
    df = df.where(pd.notna(df), other=None)

    log.debug(f"Detected columns: {list(df.columns)}")
    return df.to_dict(orient="records")
