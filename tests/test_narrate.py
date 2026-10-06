from rca.analysis import analyze
from rca.data.generator import generate
from rca.narrate import narrate


def _top():
    return analyze(generate("A", seed=1)[0]).court.hypotheses[0]


def test_narrate_without_an_llm_uses_the_template():
    result = narrate(_top(), None)
    assert result.source == "template" and result.verified


def test_narrate_uses_ai_text_only_when_verified():
    h = _top()
    good = narrate(h, lambda prompt: f"{h.title} looks plausible. Check: {h.unchecked[0]}")
    assert good.source == "claude" and good.verified
    bad = narrate(h, lambda prompt: "Defects jumped 37% because of this.")
    assert bad.source == "template" and "37" in bad.note


def test_narrate_survives_a_broken_ai_call():
    def boom(prompt):
        raise TimeoutError("offline")
    result = narrate(_top(), boom)
    assert result.source == "template" and "TimeoutError" in result.note
