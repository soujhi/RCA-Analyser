"""Browser test for the human-in-the-loop sign-off."""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def open_sample(page: Page, url: str, pattern: str) -> None:
    page.goto(url)
    page.get_by_role("button", name=re.compile(pattern)).click()
    expect(page.get_by_role("heading", name="Is the data ready?")).to_be_visible()


def advance(page: Page, label: str, heading: str) -> None:
    if heading == "The evidence, sorted":
        page.locator(".js-plotly-plot").first.wait_for()
        page.wait_for_timeout(500)
    page.get_by_role("button", name=label).click()
    expect(page.get_by_role("heading", name=heading)).to_be_visible()


def test_engineer_signs_off_and_the_export_attributes_the_decision(page: Page, app_url: str):
    open_sample(page, app_url, r"Clear cause")
    for label, heading in (("Continue", "What happened"), ("Continue", "The evidence, sorted"),
                           ("Open the Evidence Court", "Evidence Court"), ("Build the RCA draft", "RCA draft")):
        advance(page, label, heading)
    name = page.get_by_label("Your name")
    name.fill("Meena")
    name.press("Enter")                      # Streamlit commits text inputs on Enter or blur
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Sign off").click()
    expect(page.get_by_text("Signed off by Meena")).to_be_visible()
    with page.expect_download() as info:
        page.get_by_role("button", name="Download draft (Markdown)").click()
    text = open(info.value.path()).read()
    assert "Signed off by Meena" in text and "not a software finding" in text
