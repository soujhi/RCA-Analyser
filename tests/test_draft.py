from datetime import datetime

import pytest

from rca.analysis import analyze
from rca.contract import NOTICE
from rca.data.generator import generate
from rca.draft import (ACTION_RESULTS, DECISIONS, apply_results, build_draft, engineer_status,
                       sign_off, to_markdown)


def _draft(scenario="A"):
    analysis = analyze(generate(scenario, seed=1)[0])
    return analysis, build_draft(analysis)


def test_draft_ends_with_unknown_and_carries_the_notice():
    draft = build_draft(analyze(generate("A", seed=1)[0]))
    assert "Not determinable" in draft.chain[-1].answer
    assert draft.actions and draft.notice == NOTICE
    md = to_markdown(draft)
    assert NOTICE in md and "Synthetic demo data" in md and "- [ ]" in md


def test_draft_for_inconclusive_case_does_not_name_a_cause():
    draft = build_draft(analyze(generate("C", seed=1)[0]))
    assert draft.verdict == "insufficient"
    assert not any("strongest candidate" in link.answer for link in draft.chain)


def test_new_actions_start_unchecked_and_unsigned():
    _, draft = _draft()
    assert all(a["result"] == ACTION_RESULTS[0] and a["note"] == "" and not a["done"] for a in draft.actions)
    assert draft.signoff is None and "Not signed off." in to_markdown(draft)


def test_apply_results_derives_done_and_cleans_editor_rows():
    rows = [{"text": "t", "owner": None, "due": float("nan"), "note": None, "hypothesis": "H1",
             "result": "Problem found", "done": False},
            {"text": "u", "owner": "Ravi", "due": "", "note": "", "hypothesis": "H1", "result": "weird", "done": True}]
    out = apply_results(rows)
    assert out[0]["done"] is True and out[0]["owner"] == "" and out[0]["due"] == ""
    assert out[1]["result"] == ACTION_RESULTS[0] and out[1]["done"] is False


def test_engineer_status_reports_counts_and_never_rules_a_cause_out():
    _, draft = _draft()
    first = draft.actions[0]["hypothesis"]
    mine = [a for a in draft.actions if a["hypothesis"] == first]
    assert engineer_status(draft, first) == f"{len(mine)} actions, none checked yet."
    mine[0]["result"] = "Problem found"
    mine[1]["result"] = "Checked, nothing found"
    text = engineer_status(draft, first)
    assert "1 problem reported by the engineer" in text and "1 checked with nothing found" in text
    for word in ("ruled out", "confirmed", "proven", "root cause"):
        assert word not in text.lower()
    assert engineer_status(draft, "H9") == "no verification actions."


def test_sign_off_needs_a_name_and_a_listed_decision_and_records_the_time():
    _, draft = _draft()
    with pytest.raises(ValueError):
        sign_off(draft, "  ", DECISIONS[0])
    with pytest.raises(ValueError):
        sign_off(draft, "Meena", "Looks great")
    sign_off(draft, " Meena ", DECISIONS[1], now=datetime(2026, 10, 7, 6, 30, 5))
    assert draft.signoff == {"name": "Meena", "decision": DECISIONS[1], "time": "2026-10-07T06:30:05"}


def test_markdown_attributes_engineer_input_and_the_signoff_to_the_person():
    analysis, draft = _draft()
    draft.actions[0].update(result="Problem found", note="thermocouple reads 4 C low")
    draft.actions = apply_results(draft.actions)
    sign_off(draft, "Meena", DECISIONS[0], now=datetime(2026, 10, 7, 6, 30, 5))
    md = to_markdown(draft, True, {h.id: h.title for h in analysis.court.hypotheses})
    assert "- [x]" in md and "Result: Problem found." in md and "Note: thermocouple reads 4 C low" in md
    assert "1 problem reported by the engineer" in md
    assert 'Signed off by Meena as "Accepted as working hypothesis" at 2026-10-07T06:30:05.' in md
    assert "not a software finding" in md and NOTICE in md
