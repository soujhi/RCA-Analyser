import json

from rca.data.generator import generate
from validation.ablation import ask_plain_llm, run, score_answer, truth_for


def test_truth_comes_from_the_engine_not_from_the_llm():
    truth = truth_for(generate("A", seed=1)[0])
    assert truth["total_downtime_min"] == 59.0 and truth["verdict"] == "ranked"


def test_score_answer_counts_wrong_numbers_and_overclaimed_certainty():
    truth = truth_for(generate("C", seed=1)[0])
    good = {"onset_time": truth["onset_time"], "total_downtime_min": 59,
            "defects_per_row_after_onset": truth["defects_per_row_after_onset"], "certain": False}
    assert score_answer(good, truth) == {"wrong_numbers": 0, "overclaimed_certainty": False}
    bad = {"onset_time": "09:00", "total_downtime_min": 12, "defects_per_row_after_onset": 9, "certain": True}
    assert score_answer(bad, truth) == {"wrong_numbers": 3, "overclaimed_certainty": True}


def test_run_aggregates_over_scenarios_with_a_fake_llm():
    fake = lambda prompt: json.dumps({"onset_time": "01:00", "total_downtime_min": 59,
                                       "defects_per_row_after_onset": 3, "certain": True})
    totals = run(fake, seeds=range(6, 8))
    assert totals["answers"] == 6 and totals["overclaims"] >= 2


def test_ask_plain_llm_extracts_json_from_chatty_replies():
    df, _ = generate("A", seed=1)
    answer = ask_plain_llm(df, lambda p: 'Sure! {"onset_time": "02:00", "certain": false} Hope that helps.')
    assert answer["onset_time"] == "02:00"
