from validation.run_validation import TEST_SEEDS, TUNE_SEEDS, evaluate, to_markdown


def test_tune_and_test_seeds_never_overlap():
    assert not set(TUNE_SEEDS) & set(TEST_SEEDS)


def test_evaluate_reports_every_scenario_and_renders_markdown():
    report = evaluate(range(1, 4))
    assert set(report["scenarios"]) == {"A", "B", "C"}
    assert report["scenarios"]["A"]["n"] == 3
    text = to_markdown(report, range(1, 4))
    assert "| A |" in text and "Failures" in text


def test_scenario_a_and_c_meet_the_minimum_bar_on_held_out_seeds():
    report = evaluate(TEST_SEEDS)["scenarios"]
    assert report["A"]["top1_ok"] / report["A"]["top1_n"] >= 0.9
    assert report["C"]["verdict_ok"] / report["C"]["n"] >= 0.9
