# RCA Analyzer: Figma Design Doc

**Purpose:** everything needed to build the product's design in Figma and hand it to the Streamlit build without guessing. Values here match `rca/ui/tokens.py` and `rca/ui/components.py`; if you change one, change both.
**Direction:** Apple-style principles, colourful but disciplined. **Platform:** desktop web first (1440 frame, 1040 content column), shown on a laptop or projector. Mobile and dark mode are P2.
**Companions:** spec (`../superpowers/specs/2026-10-06-rca-analyzer-prd.md`), plan (`../superpowers/plans/2026-10-06-rca-analyzer-implementation.md`).

---

## 1. Design principles (Apple's, applied)

Apple's current guidelines (introduced with Liquid Glass at WWDC25) rest on **Hierarchy, Harmony and Consistency**. They build on the long-stated **Clarity, Deference and Depth**. Both sets shape this product.

| Principle | What it means here | Concrete rule |
|---|---|---|
| Clarity | A tired engineer reads it at 6 AM | Large Title for each screen, one primary action, plain words, body text 17 px |
| Deference | The data is the hero, not the chrome | White cards on a grey grouped background, hairline borders, no shadows, no decorative gradients |
| Depth | Layers show what matters | Only the navigation bar floats as glass above content; everything else sits on one layer |
| Hierarchy | What to look at first | One headline sentence per screen, then numbers, then detail; the verdict banner is the loudest element on Court |
| Harmony | Parts feel like one system | One radius family (10, 16, pill), one 4-point spacing grid, one icon style, concentric corners (inner radius = outer radius minus padding) |
| Consistency | Same thing, same look | A category is always the same colour and label; For is always a green check, Against a red cross, Unchecked a dashed grey question mark |

**Glass is for controls and navigation, not content.** Use the translucent material only on the top navigation bar. Never put it behind data.

## 2. Colourful, with discipline

Colour has exactly three jobs: **identity** (which of six causes), **meaning** (For, Against, Unchecked, verdict state) and **action** (primary blue). It never decorates, and it is never the only cue.

Rules:
1. System colours are for **fills, icons and large shapes**. Coloured *text* uses the darker ink variant (table below), because the system hues fail 4.5:1 on white.
2. Every colour that carries meaning also carries a **label and an icon or glyph**.
3. Category colours identify categories only. Meaning colours (green, red) are never used as category colours.
4. At most **one saturated area per view** competes for attention: the verdict banner on Court, the active step in the navigation elsewhere.
5. Tints (12% of the system colour over white) are backgrounds for chips and banners; text on them uses the ink variant.

## 3. Colour tokens

### 3.1 Neutrals

| Token | Hex | Use | Contrast |
|---|---|---|---|
| bg | `#F2F2F7` | Page background (grouped) | n/a |
| surface | `#FFFFFF` | Cards, tiles | n/a |
| label | `#1C1C1E` | Primary text | 17.0:1 on surface, 15.3:1 on bg |
| label2 | `#636366` | Secondary text | 6.0:1 on surface, 5.4:1 on bg |
| separator | `#D1D1D6` | Hairlines, meter track, chart grid | decorative |
| gray | `#8E8E93` | Gray tint source, neutral icons | fill only |

### 3.2 System colours, ink variants and tints

| Name | System fill | Ink (text) | Tint (12% on white) | Ink on white | Ink on tint | System fill on white |
|---|---|---|---|---|---|---|
| blue | `#007AFF` | `#0040DD` | `#E0EFFF` | 7.6 | 6.5 | 4.0 (fails) |
| green | `#34C759` | `#1E7B34` | `#E7F8EB` | 5.3 | 4.8 | 2.2 (fails) |
| orange | `#FF9500` | `#B25000` | `#FFF2E0` | 5.2 | 4.7 | 2.2 (fails) |
| red | `#FF3B30` | `#D70015` | `#FFE7E6` | 5.4 | 4.6 | 3.6 (fails) |
| indigo | `#5856D6` | `#3634A3` | `#EBEBFA` | 9.7 | 8.2 | 5.7 |
| teal | `#30B0C7` | `#00677C` | `#E6F6F8` | 6.5 | 5.9 | 2.6 (fails) |
| pink | `#FF2D55` | `#C30E40` | `#FFE6EB` | 6.1 | 5.1 | 3.7 (fails) |
| purple | `#AF52DE` | `#8944AB` | `#F5EAFB` | 6.0 | 5.2 | 4.1 (fails) |

Gray tint at 14% over white is `#EFEFF0` (notice banner, "computed" badge background).

**Primary action fill:** `blue_fill` `#0066CC` with white text, 5.6:1. System blue `#007AFF` behind white text is only 4.0:1, so it is **not** used behind small white text. System blue stays for chart-free accents and focus rings.

All ratios above are computed by `tests/test_tokens.py`. The system hexes are Apple's published light-mode system colours as remembered by the author; ink variants were chosen and tested here, and the green ink was darkened after the first value failed the test.

### 3.3 Category identity

| Category | Colour | Label | Final icon (Figma) | Build stand-in (P0 code) |
|---|---|---|---|---|
| Machine | blue | Machine | gear | "M" |
| Material | orange | Material | cube | "Ma" |
| Method | indigo | Method | list with check | "Me" |
| Measurement | teal | Measurement | ruler | "Ms" |
| People | pink | People | person | "P" |
| Environment | purple | Environment | leaf | "E" |

The build ships letter stand-ins first. Draw the final 16 px icons in Figma; swapping them in code is P2. The label is always shown next to the colour.

### 3.4 Meaning colours

| Meaning | Icon | Colour | Where |
|---|---|---|---|
| For | check in circle | green ink | Court, Data screen "all good" |
| Against | cross in circle | red ink | Court |
| Still unchecked | dashed circle with question mark | label2 | Court, Data warnings |
| Verdict Ranked | none, title text | blue tint background, blue ink title | Court banner |
| Verdict Cannot separate | none | orange tint, orange ink title | Court banner |
| Verdict Cannot determine | none | gray tint, label title | Court banner |
| Evidence strength | meter | blue fill on separator track | Hypothesis card (neutral: strong evidence is not "good") |

Orange appears as Material's identity and as the "Cannot separate" banner. The contexts never overlap in one component, and both always carry a text label.

### 3.5 Chart colours

| Series | Colour |
|---|---|
| Oven temperature line | orange `#FF9500`, 2 px |
| Defects bars | pink `#FF2D55` |
| Downtime bars | indigo `#5856D6` |
| Operator note markers | purple `#AF52DE`, diamond, 9 px |
| Incident marker | dotted line, label2 |
| Grid | separator, no vertical grid |

Chart fills are decorative geometry (not text), so system fills are allowed.

## 4. Foundations

### 4.1 Typography

Font stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", Roboto, sans-serif`. In Figma use **SF Pro** if licensed to you, otherwise **Inter**. Tracking +0.01em on Large Title only.

| Style | Size / line height | Weight | Use |
|---|---|---|---|
| Large Title | 34 / 41 | 700 | One per screen |
| Title 1 | 28 / 34 | 700 | Section titles, stat-tile numbers |
| Title 3 | 20 / 25 | 600 | Card titles, subsection titles, verdict title |
| Body | 17 / 24 | 400 | Everything readable (web line height, a little looser than Apple's 22) |
| Subheadline | 15 / 20 | 400 | Secondary text, stepper labels (600) |
| Footnote | 13 / 16 | 600 | Chips and badges |

Projector rule: any text a judge must read is at least 15 px. Footnote size is for labels only.

### 4.2 Spacing and layout

4-point grid: 4, 8, 12, 16, 24, 32, 48. Card padding 16, card gap 12, row gap 8 inside lists, section gap 24. Desktop frame 1440 x 900, content column max 1040 centred, 12 columns, 16 gutters. Top padding 24, bottom padding 96.

### 4.3 Shape, depth and material

| Element | Radius |
|---|---|
| Controls (buttons, inputs) | 10 |
| Cards, tiles, banners | 16 |
| Navigation bar | 20 |
| Chips, badges, step pills | full (999) |

Depth is made with background contrast (white card on grey) and a 1 px separator border. No drop shadows. Navigation bar: white at 72% opacity, background blur 20, saturation 180%, 1 px border `rgba(60,60,67,0.12)`. This is the only translucent surface.

### 4.4 Iconography

16 px, 1.5 px stroke, round caps and joins, inherit colour. Four core icons: check-circle, cross-circle, dashed question-circle, info-circle. Reference SF Symbols: `checkmark.circle`, `xmark.circle`, `questionmark.circle`, `info.circle`. No emoji anywhere.

### 4.5 Motion

200 ms ease-out for hover and appearance. Remove all motion when the user prefers reduced motion. No bouncing, no parallax.

## 5. Components

Each component lists anatomy, variants and the rule that matters. Build all as Figma components with auto layout and variants.

**Navigation bar (glass).** Six step pills "1 Start" to "6 Draft". Variants per pill: current (blue_fill background, white text), done (blue ink text), upcoming (label2 text). Pill padding 8 x 16, Subheadline 600. Sticky at top with 8 px offset. Non-interactive status in the build; if made tappable, raise each pill to 44 px.

**Notice banner.** Gray tint card, info icon (label2) and 15 px text: bold "Hypotheses only." plus the engineering-validation sentence and the synthetic label. On every screen after Start. Never dismissible.

**Buttons.** Height 44 minimum, radius 10, label Body 600. Primary: blue_fill with white text. Secondary: white with separator border and label text. States: default, hover (darken 8%), pressed, disabled (40% opacity), focus (3 px system-blue ring with 2 px offset). One primary per screen.

**Sample card.** Caption (Subheadline, label2) above a full-width secondary button titled "A · Clear cause", "B · Two suspects" or "C · Unclear cause".

**Stat tile.** White card, 16 padding, number in Title 1, caption in Subheadline label2. Four per row.

**Category chip.** Pill, height 24, padding 4 x 12, glyph plus label in Footnote 600, tint background, ink text.

**Evidence row.** "computed" badge (gray tint, label2, Footnote), statement in Body, evidence id in Subheadline label2. The badge tells the reader the number came from code.

**Evidence lane card.** White card: category chip, 12 px gap, evidence rows. **Empty variant** (designed on purpose): one muted line saying nothing was recorded plus what is worth checking, for example "Nothing recorded. Worth checking sensor calibration before trusting any reading."

**Verdict banner.** Full-width card, 16 padding, no border. Title Title 3 in the ink colour, one reason sentence in Body. Variants: Ranked, Cannot separate, Cannot determine.

**Evidence meter.** 8 px track (separator) with blue fill, radius 4, caption "Strong evidence, score 0.95". Accessible name carries the same words.

**Point row.** 16 px icon + Body text, 8 px gap. Kinds: For, Against, Unchecked.

**Hypothesis card.** White card: category chip, Title 3 "H1 · Oven temperature high", meter, one paragraph of wording, a footnote line "Wording: template" or "Wording: claude". Beneath it, two columns For and Against, then "Still unchecked" with a checkbox per item.

**Timeline chart.** Three stacked lanes with small titles (Oven temperature, Defects per reading, Downtime (min)), shared time axis, dotted incident line across lanes, purple diamond markers for operator notes. Height 560 on desktop. No legend: the lane titles label the data.

**Data preview table, text areas, action table, download button.** Use platform defaults, styled with the tokens (surface background, separator borders, 10 radius). The action table columns are text, owner, due, done, hypothesis (read-only).

**Cause-and-effect view (P2).** An expander titled "Cause-and-effect view". Graph left to right: evidence nodes (white, hairline), hypothesis nodes (category tint, category-colour outline), verification nodes (grey, dashed). Edge labels "signal" and "verify".

## 6. Screens

All frames 1440 x 900 at the desktop breakpoint; content column 1040. Order below is the user flow. Build each with the states listed.

### Frame 0: Start
Layout: navigation bar, Large Title "Find out what the data supports.", one muted sentence ("Load a production event file. We show what happened, sort the evidence, and put each possible cause on trial. Nothing is ever called a confirmed root cause."), Title 3 "Try a sample incident", three sample cards in a row, Title 3 "Or upload your own", upload drop area. No notice banner on this frame; the sentence above carries the promise.
States: default; error after a bad upload (red-ink message "Missing required columns: batch. Download the template, or check the column names." under the drop area).

### Frame 1: Data, "Is the data ready?"
Notice banner. Four stat tiles (readings, time span, between readings, things to know), then one Point row per warning, or one For row "All required columns found and no gaps detected.", then the 8-row preview table, then Back and Continue.
States: clean; with warnings ("3 rows are missing temperature.").

### Frame 2: Timeline, "What happened"
Notice banner. Headline in 20 px: the computed sentence "Defects rose from 0.5 to 3.8 per row from 02:03." Four stat tiles (defects in total, downtime, stops, recurring events). The timeline chart. Back and Continue.
States: with incident; **no incident** (headline "No clear rise in defects was found.", chart still shown).

### Frame 3: Evidence, "The evidence, sorted"
Notice banner. Muted line "Six places a cause can hide. Empty lanes are shown on purpose." A 3 x 2 grid of lane cards in this order: Machine, Material, Method, Measurement, People, Environment. Button label "Open the Evidence Court".
States: populated lanes with several empty lanes (design Method, Measurement and Environment empty in sample A).

### Frame 4: Court, "Evidence Court"
Notice banner, verdict banner, a switch "Polish the wording with Claude" (off by default, helper text "Numbers still come from code. Any AI text with an unknown number is rejected."), up to three hypothesis cards, the cause-and-effect expander (P2), Back and "Build the RCA draft".
Design **three variants**:
- **A, Ranked:** blue banner; H1 strong (meter about 95%), H2 and H3 weak with Against lines in red. Show the late-lot hypothesis with "It began 39 min after defects had already risen."
- **B, Cannot separate:** orange banner naming both factors; H1 and H2 both strong, each noting the other.
- **C, Cannot determine:** gray banner; all three cards weak; the sentence "No candidate reaches moderate evidence strength." This is a designed success state, not an error.

### Frame 5: Draft, "RCA draft"
Notice banner, editable problem field, "Five whys" with one text area per link (the last link always reads "Not determinable from this data. Complete the verification actions below."), "Verification actions" table, primary button "Download draft (Markdown)", Back.
States: default; with checked actions (done boxes ticked).

### P2 frames
Mobile 390 for Start and Court (stacked columns, same components). Dark mode for all frames.

## 7. Content and voice

Plain words, short sentences, no jargon, no AI hype. Say what the data supports, never what it proves. Negative results are normal and explained.

| Where | Copy |
|---|---|
| Start title | Find out what the data supports. |
| Sample captions | Line 3, night shift / Two things changed together / Nothing obvious in the data |
| Notice | Hypotheses only. Engineering validation is required before any action. This tool never controls equipment and never declares a confirmed root cause. Synthetic demo data. Fictional equipment and figures. |
| Verdict titles | Ranked / Cannot separate / Cannot determine |
| Court sections | For / Against / Still unchecked |
| Primary actions | Continue / Open the Evidence Court / Build the RCA draft / Download draft (Markdown) |
| Empty lanes | Short note on what is worth checking (see the table in the spec) |

## 8. Accessibility checklist

- Text contrast at least 4.5:1 everywhere (tokens are tested).
- Colour is never the only cue: every chip has a label, every For, Against and Unchecked has a distinct icon.
- Controls at least 44 px tall; visible 3 px focus ring on every interactive element.
- Tab order follows reading order; the meter and navigation have accessible names.
- No text under 13 px; judge-facing text at least 15 px.
- Respect reduced motion.
- Do not rely on hover; every hover detail is also available by default.

## 9. Figma file setup

**Pages:** 00 Cover, 01 Foundations, 02 Components, 03 Screens, 04 Prototype, 05 Handoff.

**Variables** (Figma local variables):
- Collection `Primitives`: every system colour, ink and tint from section 3.
- Collection `Semantic`: `bg`, `surface`, `label/primary`, `label/secondary`, `separator`, `accent/action` (blue_fill), `meaning/for`, `meaning/against`, `meaning/unchecked`, `category/<name>` (fill, ink, tint).
- Collections `Spacing` (4, 8, 12, 16, 24, 32, 48) and `Radius` (10, 16, 20, 999).
- Type styles from section 4.1.

**Starter tokens (paste into Tokens Studio or build as variables):**

```json
{
  "color": {
    "bg": "#F2F2F7", "surface": "#FFFFFF", "label": "#1C1C1E", "label2": "#636366", "separator": "#D1D1D6",
    "blue": {"fill": "#007AFF", "ink": "#0040DD", "action": "#0066CC"},
    "green": {"fill": "#34C759", "ink": "#1E7B34"},
    "orange": {"fill": "#FF9500", "ink": "#B25000"},
    "red": {"fill": "#FF3B30", "ink": "#D70015"},
    "indigo": {"fill": "#5856D6", "ink": "#3634A3"},
    "teal": {"fill": "#30B0C7", "ink": "#00677C"},
    "pink": {"fill": "#FF2D55", "ink": "#C30E40"},
    "purple": {"fill": "#AF52DE", "ink": "#8944AB"},
    "gray": {"fill": "#8E8E93"}
  },
  "tintAlpha": 0.12,
  "spacing": [4, 8, 12, 16, 24, 32, 48],
  "radius": {"control": 10, "card": 16, "nav": 20, "pill": 999}
}
```

**Naming:** `Category/Chip` (property `category`), `Verdict/Banner` (property `verdict`), `Point/Row` (property `kind`), `Card/Hypothesis` (property `strength`), `Lane/Card` (property `state`: filled or empty). Use auto layout everywhere; set padding and gaps from the spacing variables only.

**Prototype:** link buttons between frames with Navigate To, Smart Animate, 200 ms ease-out. Build two flows: sample A (Start to Draft) and sample C (Start to Court showing "Cannot determine").

**Order of work (about 45 minutes):** foundations 10, components 20, screens 15.

## 10. Handoff to the build

| Figma | Build |
|---|---|
| Color variables | `COLORS` in `rca/ui/tokens.py` |
| Tints | `tint(color, 0.12)` |
| Spacing, radius | `SPACING`, `RADIUS` |
| Components | HTML builders in `rca/ui/components.py` (`pill`, `category_chip`, `stepper`, `notice_banner`, `verdict_banner`, `stat_tile`, `meter`, `point`, `evidence_row`) |
| Timeline chart | `timeline_figure` in `rca/ui/charts.py` |
| Graph | `build_dot` in `rca/ui/graph.py` |
| Global look | `css()` in `rca/ui/components.py` and `.streamlit/config.toml` |

**Streamlit limits and decisions:** the build is a Streamlit app, so some details are approximated. The file uploader, data table, text areas, checkboxes and switch use the platform's native widgets, restyled with tokens only where Streamlit allows it. The navigation bar is status only (the Continue and Back buttons move between screens). Glass blur works in modern browsers; the fallback is the 72% white background. Letter glyphs stand in for category icons until the swap. If a design detail cannot be built in time, drop it in this order: category icons, glass blur, graph, mobile layout.

## 11. Design QA checklist

- [ ] Every screen has exactly one primary action.
- [ ] Notice banner on every frame except Start.
- [ ] All six category names, colours and glyphs identical across frames.
- [ ] Verdict banner is the loudest element on Court in all three variants.
- [ ] Empty lane variant exists and reads as intentional.
- [ ] Contrast checked for every text and fill pair (see section 3).
- [ ] Spacing values are all on the 4-point grid.
- [ ] No shadows, no emoji, no gradients, glass only on the navigation bar.
- [ ] Copy matches section 7 exactly.

## 12. Dark mode (P2, derive and test before use)

Do not ship dark mode in the build window. When you get to it: use Apple's dark-mode system colour variants as starting points (they are brighter), rebuild all ink and tint values, and re-run the contrast tests for every pair in section 3 against the dark surfaces. Streamlit's theme base must switch too, or the cards will not match the page. The author has not verified any dark values.

## 13. Sources

- Apple design principles, Hierarchy, Harmony, Consistency, and glass as a controls layer: https://www.createwithswift.com/liquid-glass-redefining-design-through-hierarchy-harmony-and-consistency/ and https://developer.apple.com/wwdc25/videos/
- Clarity, Deference, Depth, 44 pt targets and 4-point spacing as practice: https://www.superdesign.dev/blog/apple-design-system
