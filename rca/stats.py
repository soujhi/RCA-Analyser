"""Pure numeric helpers. No LLM, no I/O. Everything the UI shows as a number starts here."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

WINDOW = 6          # rows in the centred defect-rate window
BASELINE_SHARE = 0.3


def baseline_rows(n: int) -> int:
    return max(10, int(n * BASELINE_SHARE))


def persistent(mask: np.ndarray, min_len: int) -> np.ndarray:
    """Keep only runs of True that last at least min_len rows."""
    out = np.zeros(len(mask), dtype=bool)
    i = 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j < len(mask) and mask[j]:
                j += 1
            if j - i >= min_len:
                out[i:j] = True
            i = j
        else:
            i += 1
    return out


@dataclass
class Incident:
    onset_index: int | None
    onset_time: pd.Timestamp | None
    baseline_rate: float
    incident_rate: float
    high_rows: np.ndarray


def find_incident(df: pd.DataFrame) -> Incident:
    """The incident starts where the defect rate stays above baseline + 3 standard errors."""
    d = df["defect_count"].to_numpy(float)
    n = len(d)
    base = d[: baseline_rows(n)]
    mean0 = float(base.mean())
    sd0 = max(float(base.std()), 0.3)
    smooth = pd.Series(d).rolling(WINDOW, center=True, min_periods=WINDOW // 2).mean().to_numpy()
    above = persistent(smooth >= mean0 + 3 * sd0 / np.sqrt(WINDOW), WINDOW)
    if not above.any():
        return Incident(None, None, mean0, mean0, np.zeros(n, dtype=bool))
    onset = int(np.flatnonzero(above)[0])
    return Incident(onset, df["timestamp"].iloc[onset], mean0, float(d[onset:].mean()), above)


def indicators(df: pd.DataFrame) -> dict:
    """Headline numbers for the timeline screen."""
    events = df.loc[df["event_code"] != "", "event_code"].value_counts()
    stops = df.loc[df["downtime_minutes"] > 0]
    return {
        "rows": int(len(df)),
        "total_defects": int(df["defect_count"].sum()),
        "total_downtime_min": float(df["downtime_minutes"].sum()),
        "stops": int(len(stops)),
        "stop_minutes": [float(m) for m in stops["downtime_minutes"]],
        "top_events": {str(k): int(v) for k, v in events.head(3).items()},
    }


def lagged_spearman(magnitude: np.ndarray, defects: np.ndarray, max_lag: int = 10):
    """Best Spearman correlation of magnitude(t - lag) with defects(t). Returns (rho, lag_rows)."""
    best_rho, best_lag = 0.0, 0
    for lag in range(max_lag + 1):
        x = magnitude[: len(magnitude) - lag] if lag else magnitude
        y = defects[lag:]
        if np.std(x) == 0 or np.std(y) == 0:
            continue
        rho = float(pd.Series(x).corr(pd.Series(y), method="spearman"))
        if np.isfinite(rho) and rho > best_rho:
            best_rho, best_lag = rho, lag
    return best_rho, best_lag
