"""Shared data contract. Every module imports its types and constants from here."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

CATEGORIES = ("machine", "material", "method", "measurement", "people", "environment")
REQUIRED_COLUMNS = (
    "timestamp", "line", "machine", "event_code", "temperature",
    "speed", "defect_count", "downtime_minutes", "batch", "operator_note",
)
NUMERIC_COLUMNS = ("temperature", "speed", "defect_count", "downtime_minutes")
NOTICE = (
    "Hypotheses only. Engineering validation is required before any action. "
    "This tool never controls equipment and never declares a confirmed root cause."
)
SYNTHETIC_LABEL = "Synthetic demo data. Fictional equipment and figures."
VERDICTS = ("ranked", "confounded", "insufficient")


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    category: str
    kind: str
    statement: str
    metrics: dict = field(default_factory=dict)
    rows: tuple = ()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Hypothesis:
    id: str
    factor_id: str
    title: str
    category: str
    score: float
    label: str
    subscores: dict
    supporting: list
    against: list
    unchecked: list
    evidence_ids: list
    confounded_with: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CourtResult:
    verdict: str
    reason: str
    hypotheses: list

    def to_dict(self) -> dict:
        return {"verdict": self.verdict, "reason": self.reason,
                "hypotheses": [h.to_dict() for h in self.hypotheses]}
