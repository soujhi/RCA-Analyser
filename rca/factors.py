"""Turn the event table into candidate factors. A factor is a yes/no mask over rows."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .stats import baseline_rows, persistent

NOTE_KEYWORDS = {
    "machine": ("fan", "noisy", "vibration", "jam", "bearing", "leak", "belt"),
    "material": ("lot", "material", "supplier", "moisture", "resin"),
    "method": ("changeover", "setup", "recipe", "procedure", "skipped"),
    "measurement": ("sensor", "calibrat", "gauge", "reading", "probe"),
    "people": ("operator", "trainee", "swapped", "relief", "handover"),
    "environment": ("humid", "ambient", "monsoon", "power dip", "dust"),
}
CHANNELS = (("temperature", "Oven temperature"), ("speed", "Line speed"))
MIN_ROWS = 5
MAX_SHARE = 0.95


@dataclass
class Factor:
    id: str
    category: str
    kind: str            # channel | batch | machine | event | note
    title: str
    mask: np.ndarray
    magnitude: np.ndarray | None = None
    notes: list = field(default_factory=list)

    @property
    def onset(self) -> int | None:
        hits = np.flatnonzero(self.mask)
        return int(hits[0]) if hits.size else None


def note_category(text: str) -> str | None:
    lowered = text.lower()
    for category, words in NOTE_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(w), lowered) for w in words):
            return category
    return None


def _usable(mask: np.ndarray) -> bool:
    return MIN_ROWS <= mask.sum() <= MAX_SHARE * len(mask)


def channel_factors(df: pd.DataFrame) -> list[Factor]:
    out = []
    n = len(df)
    for col, title in CHANNELS:
        x = df[col].to_numpy(float)
        base = x[: baseline_rows(n)]
        median = float(np.median(base))
        sigma = max(1.4826 * float(np.median(np.abs(base - median))), 1e-6)
        z = (x - median) / sigma
        for direction, mask, mag in (
            ("high", persistent(z >= 3.0, 3), np.clip(x - median, 0, None)),
            ("low", persistent(z <= -3.0, 3), np.clip(median - x, 0, None)),
        ):
            if mask.sum() >= MIN_ROWS:
                out.append(Factor(f"channel:{col}:{direction}", "machine", "channel",
                                  f"{title} {direction}", mask, mag))
    return out


def group_factors(df: pd.DataFrame) -> list[Factor]:
    out = []
    for col, category, kind in (("batch", "material", "batch"), ("machine", "machine", "machine")):
        for value in sorted(v for v in df[col].unique() if v):
            mask = (df[col] == value).to_numpy()
            if _usable(mask):
                label = f"Batch {value}" if kind == "batch" else f"Machine {value}"
                out.append(Factor(f"{kind}:{value}", category, kind, label, mask))
    for code in sorted(c for c in df["event_code"].unique() if c):
        mask = (df["event_code"] == code).to_numpy()
        if mask.sum() >= 2:
            out.append(Factor(f"event:{code}", "machine", "event", f"Event {code}", mask))
    return out


def note_factors(df: pd.DataFrame) -> list[Factor]:
    out = []
    for i, text in enumerate(df["operator_note"]):
        category = note_category(text) if text else None
        if category:
            mask = np.zeros(len(df), dtype=bool)
            mask[i:] = True
            hhmm = df["timestamp"].iloc[i].strftime("%H:%M")
            factor = Factor(f"note:{category}:{i}", category, "note",
                            f"Operator note ({category}) at {hhmm}", mask,
                            notes=[f"{hhmm} \"{text}\""])
            out.append(factor)
    return out


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    union = (a | b).sum()
    return float((a & b).sum() / union) if union else 0.0


def build_factors(df: pd.DataFrame) -> list[Factor]:
    """Measured factors stay as hypotheses. Notes merge into the closest measured factor
    (same category and mask overlap >= 0.8); leftover notes keep only the earliest note per category."""
    measured = channel_factors(df) + group_factors(df)
    kept: list[Factor] = list(measured)
    seen_categories: set[str] = set()
    for note in note_factors(df):
        best, best_j = None, 0.0
        for f in measured:
            if f.category != note.category:
                continue
            j = jaccard(note.mask, f.mask)
            if j > best_j:
                best, best_j = f, j
        if best is not None and best_j >= 0.8:
            best.notes.extend(note.notes)
        elif note.category not in seen_categories and note.mask.sum() >= MIN_ROWS:
            seen_categories.add(note.category)
            kept.append(note)
    return kept
