import numpy as np

from rca.data.generator import generate
from rca.stats import find_incident, indicators, persistent


def test_persistent_keeps_only_long_runs():
    mask = np.array([1, 1, 0, 1, 1, 1, 0, 1], dtype=bool)
    assert persistent(mask, 3).tolist() == [False, False, False, True, True, True, False, False]


def test_find_incident_detects_onset_after_baseline_in_scenario_a():
    df, _ = generate("A", seed=1)
    inc = find_incident(df)
    assert inc.onset_index is not None and 60 <= inc.onset_index <= 100
    assert inc.incident_rate > 3 * inc.baseline_rate


def test_indicators_report_the_two_planted_stops():
    df, _ = generate("A", seed=1)
    ind = indicators(df)
    assert ind["stops"] == 2 and ind["stop_minutes"] == [18.0, 41.0]
    assert ind["total_downtime_min"] == 59.0
