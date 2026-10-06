from rca.analysis import analyze
from rca.data.generator import generate
from rca.narrate import facts_for, template_narration
from rca.verify import verify_narrative


def _top():
    return analyze(generate("A", seed=1)[0]).court.hypotheses[0]


def test_template_narration_always_passes_the_verifier():
    h = _top()
    assert verify_narrative(template_narration(h), facts_for(h)).ok


def test_verifier_rejects_an_invented_number_and_an_invented_time():
    facts = facts_for(_top())
    assert verify_narrative("Defects rose 37% after the change.", facts).unmatched_numbers == ["37"]
    assert verify_narrative("It began at 09:15.", facts).unmatched_times == ["09:15"]


def test_verifier_rejects_confirmed_root_cause_language():
    assert verify_narrative("This is the confirmed root cause.", facts_for(_top())).forbidden


def test_verifier_accepts_numbers_rounded_to_the_written_precision():
    h = _top()
    assert verify_narrative(f"Evidence score {h.score:.2f}.", facts_for(h)).ok
