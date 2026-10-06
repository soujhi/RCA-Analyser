"""Seeded synthetic incident generator with an answer key. Fictional data only."""
from __future__ import annotations

import numpy as np
import pandas as pd

SCENARIOS = ("A", "B", "C")
START = pd.Timestamp("2026-03-04 22:00")
CADENCE_MIN = 3
_OFFSET = {"A": 0, "B": 1000, "C": 2000}


def _lagged(series: np.ndarray, lag: int, fill: float) -> np.ndarray:
    out = np.full(len(series), fill, dtype=float)
    out[lag:] = series[:-lag] if lag else series
    return out


def generate(scenario: str, seed: int, n_rows: int = 140):
    """Return (DataFrame, answer_key). Scenario A: clear cause. B: confounded. C: cause not in data."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario {scenario!r}")
    rng = np.random.default_rng(seed + _OFFSET[scenario])
    idx = np.arange(n_rows)
    jitter = int(rng.integers(-3, 4))
    ts = START + pd.to_timedelta(idx * CADENCE_MIN, unit="m")

    temp = rng.normal(180.0, 1.2, n_rows)
    speed = rng.normal(42.0, 0.6, n_rows)
    batch = np.full(n_rows, "M-201", dtype=object)
    machine = np.full(n_rows, "OVEN-2", dtype=object)
    event = np.full(n_rows, "", dtype=object)
    note = np.full(n_rows, "", dtype=object)
    downtime = np.zeros(n_rows)

    if scenario == "A":
        t0 = 58 + jitter
        temp += np.clip((idx - t0) * 0.35, 0, 10)
        lam = 0.6 + 0.45 * np.maximum(0, _lagged(temp, 6, 180.0) - 183.0)
        batch[40:] = "M-203"
        loaded = t0 + 36
        batch[loaded:] = "M-204"
        note[t0 + 8] = "oven fan sounds rough"
        note[loaded] = "lot M-204 loaded"
        onset = t0 + 18
        key = {"expected_verdict": "ranked", "expected_top1": "channel:temperature:high",
               "expected_in_top3": ["channel:temperature:high"],
               "decoys": ["batch:M-204", "event:E115"]}
    elif scenario == "B":
        t0 = 60 + jitter
        temp += np.clip((idx - t0) * 1.2, 0, 9)
        lam = 0.6 + 0.5 * np.maximum(0, _lagged(temp, 4, 180.0) - 183.0)
        loaded = t0 + 2
        batch[40:loaded] = "M-203"
        batch[loaded:] = "M-204"
        note[t0 + 6] = "oven fan sounds rough"
        note[loaded] = "lot M-204 loaded"
        onset = t0 + 12
        key = {"expected_verdict": "confounded", "expected_top1": None,
               "expected_in_top3": ["channel:temperature:high", "batch:M-204"], "decoys": []}
    else:
        step = 72 + jitter
        lam = np.where(idx >= step, 3.0, 0.6)
        batch[25:105] = "M-203"
        batch[105:] = "M-204"
        onset = step + 3
        key = {"expected_verdict": "insufficient", "expected_top1": None,
               "expected_in_top3": [], "decoys": ["event:E115"]}

    defects = rng.poisson(lam)
    note[20] = "routine check ok"
    note[min(110 + jitter, n_rows - 1)] = "operator swapped to relief"
    for i in sorted(rng.choice(np.arange(5, 45), size=4, replace=False)):
        event[i] = "E050"
    for i, minutes in ((onset + 12, 18.0), (onset + 26, 41.0)):
        if i < n_rows:
            event[i], machine[i], downtime[i] = "E115", "FEEDER-1", minutes
            note[i] = note[i] or "feeder jammed again"

    df = pd.DataFrame({
        "timestamp": ts, "line": "L3", "machine": machine, "event_code": event,
        "temperature": temp.round(2), "speed": speed.round(2), "defect_count": defects,
        "downtime_minutes": downtime, "batch": batch, "operator_note": note,
    })
    key.update({"scenario": scenario, "seed": seed})
    return df, key
