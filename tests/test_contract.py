from rca.contract import CATEGORIES, NOTICE, REQUIRED_COLUMNS, CourtResult, EvidenceItem, Hypothesis


def test_constants_match_the_use_case():
    assert CATEGORIES == ("machine", "material", "method", "measurement", "people", "environment")
    assert REQUIRED_COLUMNS[0] == "timestamp" and len(REQUIRED_COLUMNS) == 10
    assert "never declares a confirmed root cause" in NOTICE


def test_dataclasses_serialise_to_plain_dicts():
    h = Hypothesis("H1", "f", "t", "machine", 0.9, "strong", {"effect": 1.0}, ["a"], [], ["b"], ["EV-001"])
    result = CourtResult("ranked", "why", [h]).to_dict()
    assert result["hypotheses"][0]["id"] == "H1" and result["verdict"] == "ranked"
    assert EvidenceItem("EV-001", "machine", "channel", "s").to_dict()["rows"] == ()
