"""One browser test per expected outcome in section 11.4. Run: pytest -m e2e tests/e2e --override-ini addopts="" """
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e
SHOTS = Path("docs/screenshots")


def open_sample(page: Page, url: str, pattern: str) -> None:
    page.goto(url)
    page.get_by_role("button", name=re.compile(pattern)).click()
    page.wait_for_timeout(1000)
    expect(page.get_by_role("heading", name="Is the data ready?")).to_be_visible()


def advance(page: Page, label: str, heading: str) -> None:
    page.get_by_role("button", name=label).click()
    page.wait_for_timeout(1000)
    expect(page.get_by_role("heading", name=heading)).to_be_visible()


def test_outcome_1_import_and_validate(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    expect(page.get_by_text("readings", exact=True)).to_be_visible()


def test_outcome_1_bad_upload_is_explained_in_plain_language(page: Page, app_url: str):
    page.goto(app_url)
    page.set_input_files("input[type=file]", files=[{"name": "bad.csv", "mimeType": "text/csv",
                                                      "buffer": b"timestamp,line\n2026-03-04 22:00,L3\n"}])
    page.wait_for_timeout(1000)
    expect(page.get_by_text("Missing required columns")).to_be_visible()


def test_outcome_2_timeline_and_indicators(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    advance(page, "Continue", "What happened")
    expect(page.get_by_text("Defects rose from")).to_be_visible()
    expect(page.locator(".js-plotly-plot").first).to_be_visible()


def test_outcome_3_evidence_is_grouped_in_six_lanes(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    advance(page, "Continue", "What happened")
    advance(page, "Continue", "The evidence, sorted")
    for name in ("Machine", "Material", "Method", "Measurement", "People", "Environment"):
        expect(page.get_by_text(re.compile(name)).first).to_be_visible()


def test_outcome_4_court_ranks_the_clear_case(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    for label, heading in (("Continue", "What happened"), ("Continue", "The evidence, sorted"),
                           ("Open the Evidence Court", "Evidence Court")):
        advance(page, label, heading)
    expect(page.get_by_text("Ranked", exact=True)).to_be_visible()
    expect(page.get_by_text("Oven temperature high").first).to_be_visible()
    expect(page.get_by_text("Still unchecked").first).to_be_visible()


@pytest.mark.parametrize("pattern,verdict", [(r"Two suspects", "Cannot separate"),
                                           (r"Unclear cause", "Cannot determine")])
def test_outcome_4_court_is_honest_when_data_cannot_decide(page: Page, app_url: str, pattern: str, verdict: str):
    open_sample(page, app_url, pattern)
    for label, heading in (("Continue", "What happened"), ("Continue", "The evidence, sorted"),
                           ("Open the Evidence Court", "Evidence Court")):
        advance(page, label, heading)
    expect(page.get_by_text(verdict, exact=True)).to_be_visible()


def test_outcome_5_draft_keeps_edits_and_the_notice_in_the_export(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    for label, heading in (("Continue", "What happened"), ("Continue", "The evidence, sorted"),
                           ("Open the Evidence Court", "Evidence Court"), ("Build the RCA draft", "RCA draft")):
        advance(page, label, heading)
    problem = page.get_by_label("Problem")
    problem.fill("Night shift defects rose on Line 3 (edited by engineer)")
    problem.press("Control+Enter")          # Streamlit commits text areas on Ctrl+Enter or blur
    page.wait_for_timeout(500)
    with page.expect_download() as info:
        page.get_by_role("button", name="Download draft (Markdown)").click()
    text = Path(info.value.path()).read_text()
    assert "edited by engineer" in text and "Hypotheses only" in text and "Synthetic demo data" in text


def test_notice_is_visible_on_every_screen_after_start(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    for label, heading in (("Continue", "What happened"), ("Continue", "The evidence, sorted"),
                           ("Open the Evidence Court", "Evidence Court"), ("Build the RCA draft", "RCA draft")):
        expect(page.get_by_text("Hypotheses only").first).to_be_visible()
        advance(page, label, heading)


def test_capture_screenshots_for_the_user_manual(page: Page, app_url: str):
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(app_url)
    page.get_by_role("button", name=re.compile(r"Clear cause")).wait_for()
    page.screenshot(path=str(SHOTS / "01-start.png"))
    page.get_by_role("button", name=re.compile(r"Clear cause")).click()
    page.wait_for_timeout(1000)
    steps = (("Is the data ready?", "02-data", "Continue", "What happened"),
             ("What happened", "03-timeline", "Continue", "The evidence, sorted"),
             ("The evidence, sorted", "04-evidence", "Open the Evidence Court", "Evidence Court"),
             ("Evidence Court", "05-court", "Build the RCA draft", "RCA draft"))
    for here, name, button, there in steps:
        expect(page.get_by_role("heading", name=here)).to_be_visible()
        page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)
        advance(page, button, there)
    page.screenshot(path=str(SHOTS / "06-draft.png"), full_page=True)
