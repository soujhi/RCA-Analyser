"""Design tokens. Mirrors docs/design/figma-design-doc.md section 4. Change both together."""
from __future__ import annotations

# Apple-style system colours (light). `*_ink` is the darker variant for TEXT on white or on a tint.
# `blue_fill` is the background for white text (system blue gives only 4.0:1, below WCAG AA).
COLORS = {
    "bg": "#F2F2F7", "surface": "#FFFFFF", "label": "#1C1C1E", "label2": "#636366",
    "separator": "#D1D1D6",
    "blue": "#007AFF", "green": "#34C759", "orange": "#FF9500", "red": "#FF3B30",
    "indigo": "#5856D6", "teal": "#30B0C7", "pink": "#FF2D55", "purple": "#AF52DE", "gray": "#8E8E93",
    "blue_fill": "#0066CC", "blue_ink": "#0040DD", "green_ink": "#1E7B34", "orange_ink": "#B25000", "red_ink": "#D70015",
    "indigo_ink": "#3634A3", "teal_ink": "#00677C", "pink_ink": "#C30E40", "purple_ink": "#8944AB",
}
TINT_ALPHA = 0.12

# name -> (label, colour key, glyph). Colour is identity only; the label and glyph always travel with it.
CATEGORY = {
    "machine": ("Machine", "blue", "M"),
    "material": ("Material", "orange", "Ma"),
    "method": ("Method", "indigo", "Me"),
    "measurement": ("Measurement", "teal", "Ms"),
    "people": ("People", "pink", "P"),
    "environment": ("Environment", "purple", "E"),
}
SPACING = (4, 8, 12, 16, 24, 32, 48)      # 4-point grid
RADIUS = {"control": 10, "card": 16, "pill": 999}
FONT_STACK = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", Roboto, sans-serif'


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def tint(color_hex: str, alpha: float = TINT_ALPHA, over: str = "#FFFFFF") -> str:
    fg, bg = hex_to_rgb(color_hex), hex_to_rgb(over)
    mixed = [round(alpha * f + (1 - alpha) * b) for f, b in zip(fg, bg)]
    return "#{:02X}{:02X}{:02X}".format(*mixed)


def _luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg_hex: str, bg_hex: str) -> float:
    """WCAG contrast ratio."""
    l1, l2 = _luminance(hex_to_rgb(fg_hex)), _luminance(hex_to_rgb(bg_hex))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)
