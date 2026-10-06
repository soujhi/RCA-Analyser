"""Small HTML builders. Every string from data is escaped here, nowhere else."""
from __future__ import annotations

from html import escape

from ..contract import NOTICE, SYNTHETIC_LABEL
from .tokens import CATEGORY, COLORS, FONT_STACK, RADIUS, tint

STEPS = ("Start", "Data", "Timeline", "Evidence", "Court", "Draft")

ICONS = {  # simple 16px glyphs, drawn inline so they inherit colour
    "check": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4.8 8.2l2 2 4.4-4.6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "cross": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 5.5l5 5M10.5 5.5l-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
    "question": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2.5 2"/><path d="M6.2 6.3a1.9 1.9 0 113 1.5c-.7.5-1.2.8-1.2 1.6M8 11.4v.1" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
    "info": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 7.2v4M8 4.8v.1" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
}


def css() -> str:
    c = COLORS
    return f"""
<style>
:root {{
  --bg: #f5f5f7;
  --surface: #ffffff;
  --label: #1c1c1e;
  --label-2: #636366;
  --separator: #d1d1d6;
  --blue: #007aff;
  --blue-ink: #0040dd;
  --blue-action: #0066cc;
  --blue-tint: #e0efff;
  --green-ink: #1e7b34;
  --green-tint: #e7f8eb;
  --orange: #ff9500;
  --orange-ink: #b25000;
  --orange-tint: #fff2e0;
  --red-ink: #d70015;
  --red-tint: #ffe7e6;
  --indigo: #5856d6;
  --indigo-ink: #3634a3;
  --indigo-tint: #ebebfa;
  --teal-ink: #00677c;
  --teal-tint: #e6f6f8;
  --pink-ink: #c30e40;
  --pink-tint: #ffe6eb;
  --purple-ink: #8944ab;
  --purple-tint: #f5eafb;
  --radius-control: 10px;
  --radius-card: 16px;
  --radius-nav: 20px;
}}

/* Streamlit Header, Footer & Global App Styling */
header[data-testid="stHeader"] {{ display: none !important; }}
footer {{ display: none !important; }}
html, body, .stApp {{ background: var(--bg) !important; font-family: {FONT_STACK}; color: var(--label); }}
.block-container {{ max-width: 1040px !important; padding-top: 10px !important; padding-bottom: 96px !important; }}

/* Navigation Header */
.rca-nav {{ position: sticky; top: 10px; z-index: 50; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 9px 16px; margin-bottom: 28px;
  border-radius: 16px; background: rgba(250, 250, 252, 0.85); backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%); border: 1px solid rgba(60, 60, 67, 0.12); overflow-x: auto; }}
.rca-nav .brand {{ display: flex; align-items: center; gap: 9px; font-size: 15px; font-weight: 650; white-space: nowrap; color: var(--label); }}
.rca-nav .brand-mark {{ width: 32px; height: 32px; border-radius: 9px; display: grid; place-items: center; color: var(--blue-action); background: var(--blue-tint); }}
.rca-nav .steps {{ display: flex; gap: 4px; align-items: center; }}
.rca-step {{ padding: 8px 12px; border-radius: 9px; font-size: 14px; font-weight: 550; color: var(--label-2); white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; }}
.rca-step.on {{ background: var(--blue-tint); color: var(--blue-ink); font-weight: 700; }}
.rca-step.done {{ color: var(--blue-ink); }}

/* Typography & Headings */
h1 {{ font-size: 36px !important; line-height: 1.15 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: var(--label) !important; margin-bottom: 12px !important; }}
h2 {{ font-size: 20px !important; line-height: 1.25 !important; font-weight: 650 !important; color: var(--label) !important; margin-bottom: 0 !important; }}
h3 {{ font-size: 20px !important; line-height: 1.25 !important; font-weight: 650 !important; color: var(--label) !important; margin-bottom: 0 !important; }}
p, li, label {{ font-size: 16px; line-height: 1.48; color: var(--label); }}
.eyebrow, .section-kicker {{ display: block; margin-bottom: 8px; color: var(--label-2); font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}

/* Hero & Section Layout */
.hero {{ max-width: 760px; padding: 12px 0 28px; }}
.hero h1 {{ font-size: clamp(38px, 4.8vw, 54px) !important; line-height: 1.06 !important; letter-spacing: -0.03em !important; margin-bottom: 16px !important; }}
.hero p {{ color: var(--label-2); font-size: 18px; line-height: 1.5; margin-bottom: 0; }}
.section-heading {{ display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; gap: 24px; }}
.section-heading p {{ margin: 0; color: var(--label-2); font-size: 15px; }}

/* Screen Header */
.screen-header {{ max-width: 790px; margin-bottom: 24px; }}
.screen-header h1 {{ font-size: 38px !important; margin-bottom: 8px !important; letter-spacing: -0.02em !important; }}
.screen-header p {{ margin: 0; color: var(--label-2); font-size: 16px; }}

/* Cards & Containers */
.rca-card {{ background: var(--surface); border-radius: var(--radius-card); padding: 20px; margin-bottom: 16px;
  border: 1px solid rgba(60, 60, 67, 0.16); box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
.rca-tile {{ background: var(--surface); border-radius: var(--radius-card); padding: 18px; border: 1px solid rgba(60, 60, 67, 0.16); min-height: 104px; display: flex; flex-direction: column; justify-content: space-between; }}
.rca-tile b {{ display: block; font-size: 28px; line-height: 34px; font-weight: 700; letter-spacing: -0.02em; color: var(--label); }}
.rca-muted {{ color: var(--label-2); font-size: 15px; line-height: 20px; }}
.rca-row {{ display: flex; gap: 10px; align-items: flex-start; margin: 6px 0; }}

/* Category Chips matching Figma Design */
.category-chip {{ display: inline-flex; align-items: center; gap: 7px; width: max-content; height: 26px; padding: 3px 8px 3px 4px; border-radius: 8px; font-size: 13px; font-weight: 650; }}
.category-chip b {{ width: 20px; height: 20px; display: grid; place-items: center; border-radius: 50%; color: white; font-size: 10px; font-weight: 700; }}
.category-chip.machine {{ color: var(--blue-ink); background: var(--blue-tint); }} .category-chip.machine b {{ background: var(--blue); }}
.category-chip.material {{ color: var(--orange-ink); background: var(--orange-tint); }} .category-chip.material b {{ background: var(--orange); }}
.category-chip.method {{ color: var(--indigo-ink); background: var(--indigo-tint); }} .category-chip.method b {{ background: var(--indigo); }}
.category-chip.measurement {{ color: var(--teal-ink); background: var(--teal-tint); }} .category-chip.measurement b {{ background: #30b0c7; }}
.category-chip.people {{ color: var(--pink-ink); background: var(--pink-tint); }} .category-chip.people b {{ background: #ff2d55; }}
.category-chip.environment {{ color: var(--purple-ink); background: var(--purple-tint); }} .category-chip.environment b {{ background: #af52de; }}

/* Verdict Box */
.verdict-box {{ display: flex; gap: 18px; align-items: flex-start; padding: 22px 24px; border-radius: var(--radius-card); border: 1px solid transparent; margin-bottom: 20px; }}
.verdict-mark {{ width: 48px; height: 48px; border-radius: 14px; display: grid; place-items: center; color: #FFFFFF; font-weight: 700; font-size: 22px; flex: 0 0 auto; }}

/* Callouts & Notices */
.finding-callout {{ padding: 18px 20px; border-radius: var(--radius-card); background: var(--blue-tint); display: flex; gap: 14px; align-items: center; color: var(--blue-ink); margin-bottom: 20px; }}
.finding-icon {{ width: 36px; height: 36px; border-radius: 50%; background: var(--blue-action); color: white; display: grid; place-items: center; flex: 0 0 auto; font-size: 18px; font-weight: 700; }}

/* Streamlit Controls Overrides */
.stButton > button {{
  min-height: 44px !important; padding: 9px 17px !important; border-radius: var(--radius-control) !important;
  border: 1px solid rgba(60, 60, 67, 0.2) !important; background: var(--surface) !important;
  color: var(--label) !important; font-weight: 600 !important; font-size: 15px !important;
  box-shadow: none !important; transition: filter 200ms ease, background 200ms ease !important;
}}
.stButton > button:hover {{ background: #f9f9fb !important; border-color: rgba(60, 60, 67, 0.3) !important; filter: brightness(0.96); }}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {{
  background: var(--blue-action) !important; color: #ffffff !important; border-color: var(--blue-action) !important;
}}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {{
  filter: brightness(0.92) !important;
}}
.stTextArea textarea, .stTextInput input, .stSelectbox select {{ border-radius: var(--radius-control) !important; border: 1px solid var(--separator) !important; }}
.stFileUploader {{ border: 1px dashed #a8a8ae; border-radius: 12px; padding: 16px; background: #fafafa; }}
.stFileUploader:hover {{ border-color: var(--blue); background: var(--blue-tint); }}

@media (prefers-reduced-motion: no-preference) {{ .rca-card, .rca-tile {{ transition: transform .2s ease, box-shadow .2s ease; }} }}
</style>"""


def pill(text: str, color: str, glyph: str = "") -> str:
    base = COLORS[color]
    ink = COLORS.get(f"{color}_ink", COLORS["label"])
    g = f"<span aria-hidden='true'>{escape(glyph)}</span>" if glyph else ""
    return f"<span class='rca-pill' style='background:{tint(base)};color:{ink}'>{g}{escape(text)}</span>"


def category_chip(category: str) -> str:
    label, color, glyph = CATEGORY[category]
    return f"<span class='category-chip {category}'><b>{glyph}</b>{escape(label)}</span>"


def stepper(current: int) -> str:
    items = []
    for i, name in enumerate(STEPS):
        cls = "on" if i == current else "done" if i < current else ""
        num = "✓" if i < current else str(i + 1)
        label = f"{num} {name}"
        items.append(f"<span class='rca-step {cls}'>{escape(label)}</span>")
    brand = (
        f"<div class='brand'><span class='brand-mark'>"
        f"<svg width='19' height='19' viewBox='0 0 20 20' fill='none'>"
        f"<path d='M4.5 5.5h11M4.5 10h7M4.5 14.5h9' stroke='currentColor' stroke-width='1.7' stroke-linecap='round'/>"
        f"<circle cx='15.5' cy='10' r='1.5' fill='currentColor'/></svg></span>"
        f"<span>RCA Analyzer</span></div>"
    )
    return (
        f"<div class='rca-nav' role='navigation' aria-label='Progress'>"
        f"{brand}<div class='steps'>{''.join(items)}</div></div>"
    )


def notice_banner() -> str:
    return (
        f"<div class='rca-card' style='display:flex;gap:12px;align-items:center;background:{tint(COLORS['gray'], .14)};border-color:rgba(60,60,67,0.12)'>"
        f"<span style='color:{COLORS['label2']}'>{ICONS['info']}</span>"
        f"<div class='rca-muted'><b>Hypotheses only.</b> {escape(NOTICE.split('. ', 1)[1])} {escape(SYNTHETIC_LABEL)}</div></div>"
    )


def verdict_banner(verdict: str, reason: str) -> str:
    color, title, bg_mark = {
        "ranked": ("blue", "Ranked", COLORS["blue_fill"]),
        "confounded": ("orange", "Cannot separate", COLORS["orange_ink"]),
        "insufficient": ("gray", "Cannot determine", COLORS["label2"]),
    }[verdict]
    ink = COLORS.get(f"{color}_ink", COLORS["label"])
    icon_glyph = "✓" if verdict == "ranked" else "!" if verdict == "confounded" else "?"
    return (
        f"<div class='verdict-box' style='background:{tint(COLORS[color])};border-color:transparent'>"
        f"<div class='verdict-mark' style='background:{bg_mark}'>{icon_glyph}</div>"
        f"<div><div style='color:{ink};font-weight:700;font-size:24px;line-height:1.2'>{escape(title)}</div>"
        f"<div style='font-size:17px;color:{COLORS['label']};margin-top:4px'>{escape(reason)}</div></div></div>"
    )


def stat_tile(value: str, label: str) -> str:
    return f"<div class='rca-tile'><b>{escape(value)}</b><span class='rca-muted'>{escape(label)}</span></div>"


def meter(score: float, label: str) -> str:
    pct = int(round(min(max(score, 0), 1) * 100))
    return (
        f"<div role='img' aria-label='Evidence strength {escape(label)}, score {score:.2f}'>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'><span class='rca-muted'>Evidence strength</span><strong style='font-size:14px'>{pct}%</strong></div>"
        f"<div style='height:8px;border-radius:4px;background:{COLORS['separator']}'>"
        f"<div style='height:8px;border-radius:4px;width:{pct}%;background:{COLORS['blue_fill']}'></div></div>"
        f"<div class='rca-muted' style='margin-top:4px;font-size:13px'>{escape(label.capitalize())} evidence (score {score:.2f})</div></div>"
    )


def point(kind: str, text: str) -> str:
    icon, color = {"for": ("check", "green_ink"), "against": ("cross", "red_ink"),
                   "unchecked": ("question", "label2")}[kind]
    tone = COLORS[color]
    return f"<div class='rca-row'><span style='color:{tone};flex:none;margin-top:2px'>{ICONS[icon]}</span><span>{escape(text)}</span></div>"


def evidence_row(item_id: str, text: str) -> str:
    return (
        f"<div class='rca-row' style='justify-content:space-between;align-items:flex-start;padding:8px 0;border-bottom:1px solid #EDEDF0'>"
        f"<div><span class='rca-pill' style='background:{tint(COLORS['gray'])};color:{COLORS['label2']};margin-right:8px'>computed</span>"
        f"<span>{escape(text)}</span></div>"
        f"<span class='rca-muted' style='font-size:13px;flex:none'>{escape(item_id)}</span></div>"
    )
