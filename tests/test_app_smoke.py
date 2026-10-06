from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _app():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def test_start_screen_renders_three_samples_without_error():
    at = _app()
    assert not at.exception
    labels = [b.label for b in at.button]
    assert {"A · Clear cause", "B · Two suspects", "C · Unclear cause"} <= set(labels)


def _click(at, label):
    next(b for b in at.button if b.label == label).click()
    at.run()
    assert not at.exception


def _to_court(at, sample):
    _click(at, sample)
    for label in ("Continue", "Continue", "Open the Evidence Court"):
        _click(at, label)


def test_full_walkthrough_for_sample_a_reaches_the_draft():
    at = _app()
    _to_court(at, "A · Clear cause")
    assert any("Evidence Court" in t.value for t in at.title)
    assert any("Ranked" in m.value for m in at.markdown)
    _click(at, "Build the RCA draft")
    assert any("RCA draft" in t.value for t in at.title)
    assert any("Hypotheses only" in m.value for m in at.markdown)


def test_sample_c_shows_the_cannot_determine_state():
    at = _app()
    _to_court(at, "C · Unclear cause")
    assert any("Cannot determine" in m.value for m in at.markdown)


def test_signing_off_needs_a_name_then_records_the_engineers_decision():
    at = _app()
    _to_court(at, "A · Clear cause")
    _click(at, "Build the RCA draft")
    at.button(key="signoff_button").click()
    at.run()
    assert any("Enter your name" in e.value for e in at.error)
    at.text_input(key="signoff_name").set_value("Meena")
    at.selectbox(key="signoff_decision").set_value("Needs more checks")
    at.button(key="signoff_button").click()
    at.run()
    assert not at.exception
    signed = " ".join(m.value for m in at.markdown)
    assert "Signed off by Meena as" in signed and "Needs more checks" in signed       # quotes are HTML-escaped
    assert any("not a software finding" in m.value for m in at.markdown)
