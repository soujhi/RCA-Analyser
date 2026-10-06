from rca.analysis import analyze
from rca.data.generator import generate


def test_scenario_a_ranks_the_temperature_factor_first_and_gates_the_late_lot():
    result = analyze(generate("A", seed=1)[0]).court
    assert result.verdict == "ranked"
    assert result.hypotheses[0].factor_id == "channel:temperature:high"
    lot = next(h for h in result.hypotheses if h.factor_id == "batch:M-204")
    assert lot.label == "weak" and any("after defects had already risen" in s for s in lot.against)


def test_scenario_b_is_confounded_and_names_both_factors():
    result = analyze(generate("B", seed=1)[0]).court
    assert result.verdict == "confounded"
    assert {h.factor_id for h in result.hypotheses[:2]} == {"channel:temperature:high", "batch:M-204"}
    assert result.hypotheses[0].confounded_with


def test_scenario_c_abstains_instead_of_inventing_a_cause():
    result = analyze(generate("C", seed=1)[0]).court
    assert result.verdict == "insufficient"
    assert all(h.label == "weak" for h in result.hypotheses)


def test_every_hypothesis_has_unchecked_items_and_at_most_three_are_returned():
    for scenario in "ABC":
        court = analyze(generate(scenario, seed=2)[0]).court
        assert 1 <= len(court.hypotheses) <= 3
        assert all(h.unchecked for h in court.hypotheses)


def test_evidence_ids_are_unique_and_referenced_ids_exist():
    a = analyze(generate("A", seed=3)[0])
    ids = [e.id for e in a.evidence]
    assert len(ids) == len(set(ids))
    for h in a.court.hypotheses:
        assert set(h.evidence_ids) <= set(ids)
