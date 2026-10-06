import io

import pytest

from rca.data.generator import generate
from rca.ingest import load_events


def test_load_events_accepts_messy_headers_and_reports_missing_values():
    df, _ = generate("A", seed=2)
    df = df.rename(columns={"defect_count": "Defect Count", "event_code": " Event-Code "})
    df.loc[3, "temperature"] = None
    clean, report = load_events(io.StringIO(df.to_csv(index=False)))
    assert "defect_count" in clean.columns and "event_code" in clean.columns
    assert report.missing_by_column["temperature"] == 1
    assert any("temperature" in w for w in report.warnings)
    assert clean["temperature"].isna().sum() == 0


def test_load_events_rejects_missing_columns():
    df, _ = generate("A", seed=2)
    with pytest.raises(ValueError, match="Missing required columns: batch"):
        load_events(df.drop(columns=["batch"]))
