"""Number verifier: reject any number or time in a narrative that the engine did not compute."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

ID_TOKEN = re.compile(r"\b[A-Za-z]+-?\d+\b")      # M-204, E115, EV-001, H1
TIME = re.compile(r"\b\d{1,2}:\d{2}\b")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
FORBIDDEN = re.compile(r"\b(confirmed|proven|definitely|root cause is|the root cause)\b", re.I)


@dataclass
class VerifyResult:
    ok: bool
    unmatched_numbers: list = field(default_factory=list)
    unmatched_times: list = field(default_factory=list)
    forbidden: list = field(default_factory=list)


def _walk(value, texts: list, numbers: list) -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        numbers.append(float(value))
    elif isinstance(value, str):
        texts.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            _walk(v, texts, numbers)
    elif isinstance(value, (list, tuple)):
        for v in value:
            _walk(v, texts, numbers)


def allowed_from(facts) -> tuple[list[float], set[str]]:
    texts: list[str] = []
    numbers: list[float] = []
    _walk(facts, texts, numbers)
    times: set[str] = set()
    for t in texts:
        times.update(TIME.findall(t))
        cleaned = TIME.sub(" ", ID_TOKEN.sub(" ", t))
        numbers.extend(float(x) for x in NUMBER.findall(cleaned))
    return numbers, times


def _matches(written: str, allowed: list[float]) -> bool:
    decimals = len(written.split(".")[1]) if "." in written else 0
    value = float(written)
    return any(round(a, decimals) == value for a in allowed)


def verify_narrative(text: str, facts) -> VerifyResult:
    allowed, times = allowed_from(facts)
    bad_times = [t for t in TIME.findall(text) if t not in times]
    cleaned = TIME.sub(" ", ID_TOKEN.sub(" ", text))
    bad_numbers = [n for n in NUMBER.findall(cleaned) if not _matches(n, allowed)]
    forbidden = [m.group(0) for m in FORBIDDEN.finditer(text)]
    return VerifyResult(not (bad_times or bad_numbers or forbidden), bad_numbers, bad_times, forbidden)
