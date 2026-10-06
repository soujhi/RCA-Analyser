import pandas as pd
import pytest

from rca.contract import REQUIRED_COLUMNS
from rca.data.generator import generate


def test_generator_is_deterministic_and_has_required_columns():
    a, key_a = generate("A", seed=1)
    b, _ = generate("A", seed=1)
    pd.testing.assert_frame_equal(a, b)
    assert list(a.columns) == list(REQUIRED_COLUMNS)
    assert 100 <= len(a) <= 150
    assert key_a["expected_verdict"] == "ranked"


def test_generator_scenarios_differ_and_keys_are_set():
    assert generate("B", 1)[1]["expected_verdict"] == "confounded"
    assert generate("C", 1)[1]["expected_verdict"] == "insufficient"
    with pytest.raises(ValueError):
        generate("Z", 1)
