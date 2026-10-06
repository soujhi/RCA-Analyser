"""Narrator: Claude writes the words, code supplies every number, the verifier decides what ships."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable

from .contract import Hypothesis
from .verify import verify_narrative

LLM = Callable[[str], str]


@dataclass
class Narration:
    text: str
    source: str          # "claude" or "template"
    verified: bool
    note: str = ""


def facts_for(h: Hypothesis) -> dict:
    return {"title": h.title, "category": h.category, "label": h.label, "score": h.score,
            "subscores": h.subscores, "supporting": h.supporting, "against": h.against,
            "unchecked": h.unchecked}


def template_narration(h: Hypothesis) -> str:
    text = f"{h.title} is a {h.label} candidate (evidence score {h.score:.2f}). "
    text += " ".join(h.supporting[:3])
    if h.against:
        text += " Against it: " + " ".join(h.against[:2])
    text += f" Next check: {h.unchecked[0]}"
    return text.strip()


def build_prompt(facts: dict) -> str:
    return (
        "You brief a production engineer. Write at most three plain sentences about this candidate cause. "
        "Use ONLY the facts below. Do not introduce any number, time or cause that is not in the facts. "
        "Never call anything a confirmed or proven root cause. Mention one thing still to be checked.\n"
        "FACTS:\n" + json.dumps(facts, indent=1)
    )


def narrate(h: Hypothesis, llm: LLM | None = None) -> Narration:
    facts = facts_for(h)
    fallback = template_narration(h)
    if llm is None:
        return Narration(fallback, "template", True, "AI narration is off.")
    try:
        draft = llm(build_prompt(facts)).strip()
    except Exception as exc:  # network, quota, key problems: never block the screen
        return Narration(fallback, "template", True, f"AI unavailable ({type(exc).__name__}).")
    result = verify_narrative(draft, facts)
    if result.ok:
        return Narration(draft, "claude", True)
    bad = result.unmatched_numbers + result.unmatched_times + result.forbidden
    return Narration(fallback, "template", True, "AI text rejected by the number verifier: " + ", ".join(bad))


def make_claude_llm() -> LLM | None:
    """Returns a callable when ANTHROPIC_API_KEY is set, otherwise None (template mode)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    import anthropic

    client = anthropic.Anthropic(api_key=key)
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

    def call(prompt: str) -> str:
        message = client.messages.create(model=model, max_tokens=300,
                                         messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in message.content if getattr(b, "type", "") == "text")

    return call
