import pytest

from rca.ui.tokens import CATEGORY, COLORS, SPACING, contrast, tint


def test_all_spacing_values_sit_on_the_four_point_grid():
    assert all(s % 4 == 0 for s in SPACING)


def test_body_text_meets_wcag_aa_on_both_backgrounds():
    for bg in (COLORS["surface"], COLORS["bg"]):
        assert contrast(COLORS["label"], bg) >= 7.0
        assert contrast(COLORS["label2"], bg) >= 4.5


@pytest.mark.parametrize("name", ["blue", "green", "orange", "red", "indigo", "teal", "pink", "purple"])
def test_ink_colours_are_readable_on_white_and_on_their_own_tint(name):
    ink = COLORS[f"{name}_ink"]
    assert contrast(ink, COLORS["surface"]) >= 4.5, name
    assert contrast(ink, tint(COLORS[name])) >= 4.5, name


def test_every_category_has_a_label_a_colour_and_a_glyph():
    assert len(CATEGORY) == 6
    for label, colour, glyph in CATEGORY.values():
        assert label and colour in COLORS and glyph


def test_white_text_on_the_blue_fill_meets_wcag_aa():
    assert contrast("#FFFFFF", COLORS["blue_fill"]) >= 4.5
    assert contrast("#FFFFFF", COLORS["blue"]) < 4.5   # why the system blue is not used behind small white text
