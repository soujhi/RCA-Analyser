"""Load an event CSV, normalise it, and produce a plain-language health report."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from .contract import NUMERIC_COLUMNS, REQUIRED_COLUMNS

TEXT_COLUMNS = ("line", "machine", "event_code", "batch", "operator_note")


def _norm(header: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(header).strip().lower()).strip("_")


@dataclass
class HealthReport:
    n_rows: int
    start: str
    end: str
    cadence_minutes: float
    missing_by_column: dict
    out_of_order: int
    duplicate_timestamps: int
    bad_timestamps: int
    warnings: list = field(default_factory=list)


def load_events(source) -> tuple[pd.DataFrame, HealthReport]:
    """Accepts a path, file-like object or DataFrame. Raises ValueError on fatal problems."""
    df = source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)
    df.columns = [_norm(c) for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    df = df[list(REQUIRED_COLUMNS)].copy()

    ts = pd.to_datetime(df["timestamp"], errors="coerce")
    bad = int(ts.isna().sum())
    df["timestamp"] = ts
    df = df.dropna(subset=["timestamp"])
    out_of_order = int((df["timestamp"].diff().dt.total_seconds() < 0).sum())
    df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    duplicates = int(df["timestamp"].duplicated().sum())
    if len(df) < 20:
        raise ValueError("Need at least 20 rows with a valid timestamp.")

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    missing_by_column = {c: int(df[c].isna().sum()) for c in NUMERIC_COLUMNS}
    for col in TEXT_COLUMNS:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df[["temperature", "speed"]] = df[["temperature", "speed"]].interpolate(limit_direction="both")
    df[["defect_count", "downtime_minutes"]] = df[["defect_count", "downtime_minutes"]].fillna(0)

    cadence = float(df["timestamp"].diff().dt.total_seconds().median() / 60.0)
    warnings: list[str] = []
    for col, count in missing_by_column.items():
        if count:
            warnings.append(f"{count} rows are missing {col.replace('_', ' ')}.")
    if out_of_order:
        warnings.append(f"{out_of_order} rows were out of time order and have been sorted.")
    if duplicates:
        warnings.append(f"{duplicates} rows share a timestamp with another row.")
    if bad:
        warnings.append(f"{bad} rows had an unreadable timestamp and were dropped.")

    report = HealthReport(
        n_rows=len(df), start=str(df["timestamp"].iloc[0]), end=str(df["timestamp"].iloc[-1]),
        cadence_minutes=round(cadence, 1), missing_by_column=missing_by_column,
        out_of_order=out_of_order, duplicate_timestamps=duplicates, bad_timestamps=bad,
        warnings=warnings,
    )
    return df, report
