"""The Evidence Court: score each factor, list For / Against / Unchecked, decide the verdict."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .contract import CourtResult, EvidenceItem, Hypothesis
from .factors import Factor, jaccard
from .stats import Incident, lagged_spearman

WEIGHTS = {"effect": 0.30, "timing": 0.25, "consistency": 0.20, "specificity": 0.15, "dose": 0.10}
TYPE_WEIGHT = {"channel": 1.0, "batch": 1.0, "machine": 1.0, "event": 1.0, "note": 0.75}
STRONG, MODERATE = 0.70, 0.50
CONFOUND_JACCARD = 0.8
CONFOUND_MINUTES = 15.0
MAX_HYPOTHESES = 3
TEMPORAL_CAP = 0.45   # a factor that starts after the defects began cannot be a cause

UNCHECKED = {
    "channel": ["Check the {t} sensor against a handheld reference reading.",
                "Inspect the equipment behind {t} and its recent maintenance log."],
    "batch": ["Compare the supplier certificate of {t} with earlier lots.",
              "Test retained samples from {t} against the material specification."],
    "machine": ["Inspect {t} and its recent maintenance log."],
    "event": ["Review the alarm history for {t} and what triggered it."],
    "note": ["Ask the author of the note what they saw, and check the related records."],
}
UNCHECKED_PEOPLE = ["Check shift handover and training records for the people involved."]


def label_for(score: float) -> str:
    return "strong" if score >= STRONG else "moderate" if score >= MODERATE else "weak"


def _clip01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def score_factor(df: pd.DataFrame, inc: Incident, f: Factor, cadence_min: float):
    d = df["defect_count"].to_numpy(float)
    m = f.mask
    inside, outside = d[m], d[~m]
    mean_in = float(inside.mean()) if inside.size else 0.0
    mean_out = float(outside.mean()) if outside.size else 0.0
    pooled = float(np.sqrt((inside.var() * inside.size + outside.var() * outside.size) / len(d)))
    cohen = (mean_in - mean_out) / max(pooled, 0.3) if outside.size and inside.size else 0.0
    effect = _clip01(cohen / 1.5)

    lead_min = None
    timing = 0.0
    if f.onset is not None and inc.onset_index is not None:
        lead_min = (inc.onset_index - f.onset) * cadence_min
        timing = 1.0 if lead_min >= 0 else 0.0

    high = inc.high_rows
    overlap = float((m & high).sum())
    consistency = overlap / max(float(high.sum()), 1.0)
    specificity = overlap / max(float(m.sum()), 1.0)

    dose, rho, lag_min = None, None, None
    if f.magnitude is not None:
        rho, lag_rows = lagged_spearman(f.magnitude, d)
        dose, lag_min = _clip01(rho), lag_rows * cadence_min

    sub = {"effect": effect, "timing": timing, "consistency": consistency,
           "specificity": specificity, "dose": dose}
    extras = {"mean_in": mean_in, "mean_out": mean_out, "lead_min": lead_min,
              "rho": rho, "lag_min": lag_min, "rows_active": int(m.sum())}
    return sub, extras


def combine(sub: dict, kind: str) -> float:
    used = {k: v for k, v in sub.items() if v is not None}
    total = sum(WEIGHTS[k] for k in used)
    raw = sum(WEIGHTS[k] * v for k, v in used.items()) / total
    score = raw * TYPE_WEIGHT[kind]
    if sub["timing"] == 0.0:
        score = min(score, TEMPORAL_CAP)
    return round(score, 3)


def statements(sub: dict, ex: dict) -> tuple[list[str], list[str]]:
    """For and Against lines. Every number in them is computed here, nowhere else."""
    pro, con = [], []
    if sub["effect"] >= 0.6:
        pro.append(f"Defects averaged {ex['mean_in']:.1f} per row while this was active, "
                   f"against {ex['mean_out']:.1f} otherwise.")
    elif sub["effect"] <= 0.3:
        con.append(f"Defects were not clearly higher while this was active "
                   f"({ex['mean_in']:.1f} against {ex['mean_out']:.1f} per row).")
    if ex["lead_min"] is not None:
        if sub["timing"] == 1.0 and ex["lead_min"] > 0:
            pro.append(f"It began {ex['lead_min']:.0f} min before defects rose.")
        elif sub["timing"] == 1.0:
            pro.append("It began at the same time defects rose.")
        else:
            con.append(f"It began {abs(ex['lead_min']):.0f} min after defects had already risen.")
    if sub["consistency"] >= 0.7:
        pro.append(f"It was active in {sub['consistency'] * 100:.0f}% of high-defect rows.")
    elif sub["consistency"] <= 0.3:
        con.append(f"It was active in only {sub['consistency'] * 100:.0f}% of high-defect rows.")
    if sub["specificity"] <= 0.4:
        con.append(f"Only {sub['specificity'] * 100:.0f}% of the rows where it was active had high defects.")
    if sub["dose"] is not None:
        if sub["dose"] >= 0.6:
            pro.append(f"Defects rose as it grew (rho {ex['rho']:.2f}, lag {ex['lag_min']:.0f} min).")
        elif sub["dose"] <= 0.2:
            con.append(f"Defects did not follow its size (rho {ex['rho']:.2f}).")
    return pro, con


def unchecked_for(f: Factor) -> list[str]:
    lines = UNCHECKED_PEOPLE if f.kind == "note" and f.category == "people" else UNCHECKED[f.kind]
    return [line.format(t=f.title) for line in lines]


def build_evidence(df, inc, factors, scored, cadence_min) -> tuple[list[EvidenceItem], dict]:
    """Evidence items for the board. Returns (items, factor_id -> list of evidence ids)."""
    items: list[EvidenceItem] = []
    links: dict[str, list[str]] = {}

    def add(category, kind, statement, metrics, rows=()):
        eid = f"EV-{len(items) + 1:03d}"
        items.append(EvidenceItem(eid, category, kind, statement, metrics, tuple(int(r) for r in rows)))
        return eid

    if inc.onset_index is not None:
        hhmm = inc.onset_time.strftime("%H:%M")
        add("overview", "incident",
            f"Defects rose from {inc.baseline_rate:.1f} to {inc.incident_rate:.1f} per row from {hhmm}.",
            {"baseline_rate": inc.baseline_rate, "incident_rate": inc.incident_rate})
    for f in factors:
        sub, ex = scored[f.id]
        rows = np.flatnonzero(f.mask)[:400]
        first = df["timestamp"].iloc[f.onset].strftime("%H:%M") if f.onset is not None else "n/a"
        links[f.id] = []
        if f.kind == "channel":
            text = f"{f.title} stayed outside its normal range for {f.mask.sum() * cadence_min:.0f} min from {first}."
        elif f.kind == "event":
            text = f"{f.title} occurred {int(f.mask.sum())} times, first at {first}."
        elif f.kind == "note":
            text = f"Operator note at {first}: {f.notes[0].split(' ', 1)[1]}"
        else:
            text = (f"{f.title} covered {int(f.mask.sum())} rows from {first}; defects averaged "
                    f"{ex['mean_in']:.1f} per row there against {ex['mean_out']:.1f} elsewhere.")
        links[f.id].append(add(f.category, f.kind if f.kind != "note" else "note_signal", text,
                               {"rows_active": int(f.mask.sum()), **{k: v for k, v in ex.items() if v is not None}}, rows))
        if ex["rho"] is not None and ex["rho"] > 0:
            links[f.id].append(add(f.category, "lag_correlation",
                                   f"Defects follow {f.title.lower()} by about {ex['lag_min']:.0f} min (rho {ex['rho']:.2f}).",
                                   {"rho": ex["rho"], "lag_min": ex["lag_min"]}, rows))
        if f.kind != "note":
            for note in f.notes:
                links[f.id].append(add(f.category, "note_signal", f"Operator note at {note}", {}, rows[:1]))
    return items, links


def run_court(df: pd.DataFrame, inc: Incident, factors: list[Factor], cadence_min: float):
    """Returns (CourtResult, evidence_items)."""
    if inc.onset_index is None:
        return CourtResult("insufficient", "No clear rise in defects was found, so there is nothing to explain.", []), []

    scored = {f.id: score_factor(df, inc, f, cadence_min) for f in factors}
    evidence, links = build_evidence(df, inc, factors, scored, cadence_min)
    ranked = sorted(factors, key=lambda f: combine(scored[f.id][0], f.kind), reverse=True)[:MAX_HYPOTHESES]

    hypotheses = []
    for n, f in enumerate(ranked, start=1):
        sub, ex = scored[f.id]
        pro, con = statements(sub, ex)
        for note in f.notes:
            if f.kind != "note":
                pro.append(f"An operator note mentions the same area: {note}.")
        score = combine(sub, f.kind)
        hypotheses.append(Hypothesis(
            id=f"H{n}", factor_id=f.id, title=f.title, category=f.category, score=score,
            label=label_for(score), subscores={k: (None if v is None else round(v, 3)) for k, v in sub.items()},
            supporting=pro, against=con, unchecked=unchecked_for(f), evidence_ids=links[f.id]))

    by_id = {f.id: f for f in factors}
    top = hypotheses[0]
    if top.score < MODERATE:
        return CourtResult("insufficient",
                           f"No candidate reaches moderate evidence strength. The closest is {top.title}.",
                           hypotheses), evidence

    for i, a in enumerate(hypotheses):
        for b in hypotheses[i + 1:]:
            fa, fb = by_id[a.factor_id], by_id[b.factor_id]
            if "note" in (fa.kind, fb.kind) or min(a.score, b.score) < MODERATE:
                continue
            gap = abs((fa.onset - fb.onset) * cadence_min)
            if jaccard(fa.mask, fb.mask) >= CONFOUND_JACCARD and gap <= CONFOUND_MINUTES:
                a.confounded_with.append(b.id)
                b.confounded_with.append(a.id)
    if top.confounded_with:
        other = next(h for h in hypotheses if h.id == top.confounded_with[0])
        return CourtResult("confounded",
                           f"{top.title} and {other.title} changed within {CONFOUND_MINUTES:.0f} min of each "
                           "other, so this data cannot separate them.", hypotheses), evidence
    return CourtResult("ranked", f"The strongest candidate is {top.title}.", hypotheses), evidence
