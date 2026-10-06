"""Plain-LLM versus engine on the same event table. Needs ANTHROPIC_API_KEY (or any callable llm).
Run: python -m validation.ablation"""
from __future__ import annotations

import json
import re

import pandas as pd

from rca.analysis import analyze
from rca.data.generator import generate
from rca.narrate import LLM, make_claude_llm

QUESTION = (
    "Below is a CSV of production events from one line. Answer ONLY with JSON using exactly these keys: "
    '{"onset_time": "HH:MM when defects started to rise", "total_downtime_min": number, '
    '"defects_per_row_after_onset": number, "most_likely_cause": "one short phrase", "certain": true or false}\n'
)


def ask_plain_llm(df: pd.DataFrame, llm: LLM) -> dict:
    reply = llm(QUESTION + df.to_csv(index=False))
    match = re.search(r"\{.*\}", reply, re.S)
    return json.loads(match.group(0)) if match else {}


def truth_for(df: pd.DataFrame) -> dict:
    a = analyze(df)
    return {"onset_time": a.incident.onset_time.strftime("%H:%M") if a.incident.onset_time is not None else None,
            "total_downtime_min": a.indicators["total_downtime_min"],
            "defects_per_row_after_onset": round(a.incident.incident_rate, 1),
            "verdict": a.court.verdict}


def score_answer(answer: dict, truth: dict, tolerance_min: int = 15) -> dict:
    """Counts how many of the LLM's numbers are wrong, and whether it claimed certainty without evidence."""
    def minutes(hhmm):
        h, m = (int(x) for x in str(hhmm).split(":")[:2])
        return h * 60 + m

    wrong = 0
    try:
        gap = abs(minutes(answer["onset_time"]) - minutes(truth["onset_time"]))
        wrong += int(min(gap, 1440 - gap) > tolerance_min)
    except (KeyError, ValueError, TypeError):
        wrong += 1
    wrong += int(abs(float(answer.get("total_downtime_min", -1)) - truth["total_downtime_min"]) > 0.5)
    wrong += int(abs(float(answer.get("defects_per_row_after_onset", -1)) - truth["defects_per_row_after_onset"]) > 0.3)
    overclaim = bool(answer.get("certain")) and truth["verdict"] != "ranked"
    return {"wrong_numbers": wrong, "overclaimed_certainty": overclaim}


def run(llm: LLM | None = None, seeds=range(6, 11)) -> dict:
    llm = llm or make_claude_llm()
    if llm is None:
        raise RuntimeError("Set ANTHROPIC_API_KEY or pass an llm callable.")
    totals = {"wrong_numbers": 0, "overclaims": 0, "answers": 0}
    for scenario in "ABC":
        for seed in seeds:
            df, _ = generate(scenario, seed)
            result = score_answer(ask_plain_llm(df, llm), truth_for(df))
            totals["wrong_numbers"] += result["wrong_numbers"]
            totals["overclaims"] += int(result["overclaimed_certainty"])
            totals["answers"] += 1
    return totals


if __name__ == "__main__":
    print(run())
