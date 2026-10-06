"""One call that runs the whole engine on a loaded event table."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .contract import CourtResult, EvidenceItem
from .court import run_court
from .factors import build_factors
from .stats import Incident, find_incident, indicators


@dataclass
class Analysis:
    incident: Incident
    indicators: dict
    evidence: list
    court: CourtResult
    cadence_min: float


def analyze(df: pd.DataFrame) -> Analysis:
    cadence = float(df["timestamp"].diff().dt.total_seconds().median() / 60.0)
    incident = find_incident(df)
    court, evidence = run_court(df, incident, build_factors(df), cadence)
    return Analysis(incident, indicators(df), evidence, court, cadence)
