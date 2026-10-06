"""Editable RCA draft: a five-whys chain built only from evidence, ending in what is NOT yet known.
Engineer input (results, sign-off) is recorded separately and never changes computed evidence."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .analysis import Analysis
from .contract import NOTICE, SYNTHETIC_LABEL

ACTION_RESULTS = ("Not yet checked", "Problem found", "Checked, nothing found", "Could not check")
DECISIONS = ("Accepted as working hypothesis", "Needs more checks", "Not accepted")


@dataclass
class ChainLink:
    question: str
    answer: str
    evidence_ids: list = field(default_factory=list)


@dataclass
class RcaDraft:
    problem: str
    verdict: str
    chain: list
    actions: list
    notice: str = NOTICE
    signoff: dict | None = None


def build_draft(analysis: Analysis) -> RcaDraft:
    court = analysis.court
    incident_ev = next((e for e in analysis.evidence if e.kind == "incident"), None)
    problem = incident_ev.statement if incident_ev else "No clear rise in defects was found."
    chain = [ChainLink("Why did output miss its quality target?", problem,
                       [incident_ev.id] if incident_ev else [])]
    actions: list[dict] = []
    if court.hypotheses:
        top = court.hypotheses[0]
        if court.verdict == "insufficient":
            chain.append(ChainLink("Why did it happen?", court.reason))
        else:
            chain.append(ChainLink("Why did it happen?", f"The strongest candidate is {top.title}.",
                                   top.evidence_ids[:1]))
            for line in top.supporting[:2]:
                chain.append(ChainLink("What supports that?", line, top.evidence_ids))
            if court.verdict == "confounded":
                chain.append(ChainLink("Can this data separate the candidates?", court.reason))
        for h in court.hypotheses[:2]:
            for line in h.unchecked[:2]:
                actions.append({"text": line, "owner": "", "due": "", "done": False, "hypothesis": h.id,
                                "result": ACTION_RESULTS[0], "note": ""})
    chain.append(ChainLink("Why did that happen?",
                           "Not determinable from this data. Complete the verification actions below."))
    return RcaDraft(problem, court.verdict, chain, actions)


def _clean(value) -> str:
    return "" if value is None or value != value else str(value)       # None and NaN become ""


def apply_results(records: list[dict]) -> list[dict]:
    """Normalise rows coming back from the editor and derive `done` from the engineer's result."""
    out = []
    for r in records:
        row = dict(r)
        for key in ("text", "owner", "due", "note", "hypothesis"):
            row[key] = _clean(row.get(key))
        result = _clean(row.get("result"))
        row["result"] = result if result in ACTION_RESULTS else ACTION_RESULTS[0]
        row["done"] = row["result"] != ACTION_RESULTS[0]
        out.append(row)
    return out


def engineer_status(draft: RcaDraft, hypothesis_id: str) -> str:
    """What the engineer reported for one candidate. Never says a cause is ruled out or confirmed."""
    rows = [a for a in draft.actions if a.get("hypothesis") == hypothesis_id]
    if not rows:
        return "no verification actions."
    count = lambda name: sum(1 for a in rows if a.get("result", ACTION_RESULTS[0]) == name)
    found, clear, cannot, todo = (count(ACTION_RESULTS[i]) for i in (1, 2, 3, 0))
    if found == clear == cannot == 0:
        return f"{len(rows)} actions, none checked yet."
    parts = []
    if found:
        parts.append(f"{found} {'problem' if found == 1 else 'problems'} reported by the engineer")
    if clear:
        parts.append(f"{clear} checked with nothing found")
    if cannot:
        parts.append(f"{cannot} could not be checked")
    if todo:
        parts.append(f"{todo} not yet checked")
    return ", ".join(parts) + "."


def sign_off(draft: RcaDraft, name: str, decision: str, now: datetime | None = None) -> None:
    """Record the engineer's decision. This is the person's decision, not a software finding."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Enter your name to sign off.")
    if decision not in DECISIONS:
        raise ValueError("Choose one of the listed decisions.")
    stamp = (now or datetime.now()).isoformat(timespec="seconds")
    draft.signoff = {"name": name, "decision": decision, "time": stamp}


def to_markdown(draft: RcaDraft, synthetic: bool = True, hypothesis_titles: dict | None = None) -> str:
    lines = ["# RCA draft", "", f"> {draft.notice}"]
    if synthetic:
        lines.append(f"> {SYNTHETIC_LABEL}")
    lines += ["", f"**Verdict:** {draft.verdict}", "", f"**Problem:** {draft.problem}", "", "## Five whys"]
    for i, link in enumerate(draft.chain, start=1):
        refs = f" ({', '.join(link.evidence_ids)})" if link.evidence_ids else ""
        lines.append(f"{i}. **{link.question}** {link.answer}{refs}")
    lines += ["", "## Verification actions"]
    for a in draft.actions:
        done = a.get("done") or a.get("result", ACTION_RESULTS[0]) != ACTION_RESULTS[0]
        note = f" Note: {a['note']}" if a.get("note") else ""
        lines.append(f"- [{'x' if done else ' '}] {a['text']} Owner: {a['owner'] or 'unassigned'}. "
                     f"Due: {a['due'] or 'unset'}. Result: {a.get('result', ACTION_RESULTS[0])}.{note}")
    titles = hypothesis_titles or {}
    ids = sorted({a.get("hypothesis") for a in draft.actions if a.get("hypothesis")})
    lines += ["", "## What the engineer reported"]
    lines += [f"- {i} {titles.get(i, '')}: {engineer_status(draft, i)}".replace("  ", " ") for i in ids] or ["- Nothing recorded."]
    lines += ["", "## Sign-off"]
    if draft.signoff:
        s = draft.signoff
        lines.append(f"Signed off by {s['name']} as \"{s['decision']}\" at {s['time']}. "
                     "This records the engineer's decision, not a software finding.")
    else:
        lines.append("Not signed off.")
    return "\n".join(lines) + "\n"
