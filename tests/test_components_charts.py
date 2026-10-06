from rca.analysis import analyze
from rca.data.generator import generate
from rca.ui import components as ui
from rca.ui.charts import timeline_figure


def test_pill_escapes_html_from_data():
    assert "<script>" not in ui.pill("<script>alert(1)</script>", "blue")


def test_stepper_marks_exactly_one_current_step():
    html = ui.stepper(2)
    assert html.count("rca-step on") == 1 and "3 Timeline" in html


def test_verdict_banner_has_a_title_for_every_verdict():
    assert "Ranked" in ui.verdict_banner("ranked", "why")
    assert "Cannot separate" in ui.verdict_banner("confounded", "why")
    assert "Cannot determine" in ui.verdict_banner("insufficient", "why")


def test_meter_is_readable_by_screen_readers():
    assert "aria-label" in ui.meter(0.82, "strong") and "Strong evidence" in ui.meter(0.82, "strong")


def test_point_kinds_use_different_icons_so_colour_is_never_the_only_cue():
    icons = {ui.point(k, "x") for k in ("for", "against", "unchecked")}
    assert len(icons) == 3


def test_timeline_figure_has_three_lanes_and_an_incident_marker_on_each():
    df, _ = generate("A", seed=1)
    fig = timeline_figure(df, analyze(df))
    assert len(fig.data) >= 4 and len(fig.layout.shapes) == 3
