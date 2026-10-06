"""Cause-and-effect view: evidence -> hypothesis -> verification action, as Graphviz DOT."""
from __future__ import annotations

from ..analysis import Analysis
from .tokens import CATEGORY, COLORS, tint

MAX_LABEL = 56


def _q(text: str) -> str:
    """Quote a string for DOT."""
    return '"' + str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def _short(text: str) -> str:
    return text if len(text) <= MAX_LABEL else text[: MAX_LABEL - 1] + "…"


def build_dot(analysis: Analysis) -> str:
    evidence = {e.id: e for e in analysis.evidence}
    lines = ["digraph G {",
             'rankdir=LR; bgcolor="transparent"; nodesep=0.25; ranksep=0.7;',
             'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, penwidth=0.8];',
             'edge [fontname="Helvetica", fontsize=10, color="#8E8E93"];']
    for h in analysis.court.hypotheses:
        color = COLORS[CATEGORY[h.category][1]]
        lines.append(f'{_q(h.id)} [label={_q(h.id + ": " + h.title)}, fillcolor={_q(tint(color, 0.22))}, color={_q(color)}];')
        for eid in h.evidence_ids:
            item = evidence.get(eid)
            if item is None:
                continue
            lines.append(f'{_q(eid)} [label={_q(_short(item.statement))}, fillcolor="#FFFFFF", color="#D1D1D6"];')
            lines.append(f'{_q(eid)} -> {_q(h.id)} [label="signal"];')
        for i, action in enumerate(h.unchecked):
            node = f"{h.id}_check{i}"
            lines.append(f'{_q(node)} [label={_q(_short(action))}, fillcolor="#F2F2F7", color="#8E8E93", style="rounded,filled,dashed"];')
            lines.append(f'{_q(h.id)} -> {_q(node)} [label="verify", style=dashed];')
    lines.append("}")
    return "\n".join(lines)
