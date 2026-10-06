import numpy as np

from rca.data.generator import generate
from rca.factors import build_factors, group_factors, jaccard, note_category


def test_note_category_uses_word_prefixes_not_substrings():
    assert note_category("oven fan sounds rough") == "machine"
    assert note_category("lot M-204 loaded") == "material"
    assert note_category("operator swapped to relief") == "people"
    assert note_category("sensor needs calibration") == "measurement"
    assert note_category("all quiet, slot 4 free") is None


def test_jaccard_is_one_for_identical_masks_and_zero_for_disjoint_ones():
    a = np.array([1, 1, 0, 0], dtype=bool)
    assert jaccard(a, a) == 1.0
    assert jaccard(a, ~a) == 0.0


def test_group_factors_skip_the_dominant_machine_and_keep_the_feeder_event():
    df, _ = generate("A", seed=1)
    ids = [f.id for f in group_factors(df)]
    assert "machine:OVEN-2" not in ids and "event:E115" in ids and "batch:M-204" in ids


def test_matching_note_merges_into_the_measured_factor_and_unrelated_note_stays():
    df, _ = generate("A", seed=1)
    factors = {f.id: f for f in build_factors(df)}
    assert any("oven fan" in n for n in factors["channel:temperature:high"].notes)
    leftovers = [f for f in factors.values() if f.kind == "note"]
    assert all("oven fan" not in " ".join(f.notes) for f in leftovers)
    assert any(f.category == "people" for f in leftovers)
