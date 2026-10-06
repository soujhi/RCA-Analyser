# RCA Analyzer: Product Requirements and Design Spec

**Status:** Approved for build (architecture approved in chat). **Date:** 2026-10-06
**Event:** TCS-SASTRA Academy Connect Hackathon, Use Case 11 (Manufacturing, Production RCA Analyzer). Build window 3 to 4 hours, 40 teams.
**Readers:** Antigravity agents (primary), the four team owners, reviewers.
**Companions:** implementation plan (`../plans/2026-10-06-rca-analyzer-implementation.md`), design doc (`../../design/figma-design-doc.md`), agent rules (`../../../AGENTS.md`).

> How to read this: sections 5 to 9 are normative. MUST and MUST NOT are hard rules. Every requirement has an ID (R1 to R6, N1 to N8) that the plan and the tests refer to.

---

## 1. Problem and why it matters

Production teams review alarms, downtime notes, quality observations and shift logs to explain why an output or quality target was missed. The evidence is scattered, and the first plausible cause usually wins, which sends the team in the wrong direction. The use case asks for a guided RCA assistant that analyses a synthetic event pack, finds correlations and recurring signals, and drafts *possible* causes. It provides hypotheses and supporting evidence only. It does not control equipment and does not declare a confirmed root cause.

Evidence that the problem is real (sources in section 15):

- Siemens estimates the world's 500 biggest companies lose almost $1.4 trillion a year to unplanned downtime, about 11% of revenues. In automotive an hour costs about $2.3 million. Arithmetic on that estimate: roughly $2.7 million lost every minute.
- Siemens' 2022 edition found about 20 unplanned downtime incidents per facility per month, so every plant runs many investigations a month.
- Deloitte and The Manufacturing Institute project up to 3.8 million US manufacturing jobs to fill from 2024 to 2033, with about 1.9 million possibly unfilled. Experienced investigators are scarce.
- Practitioner guidance says most factories do RCA on whiteboards and sticky notes, and that the first plausible cause is rarely the root.
- The classic method has documented limits: different people build different 5-Whys chains, it cannot go beyond what the investigator already knows, and it tends to isolate a single cause. Ohno's own famous example (blown fuse, ending at a missing strainer) unpacks to seven whys if counted honestly.
- A 2026 IJACSA paper (Rikkyo University with Toyota) reports that LLM analysis pipelines tend to produce confident, ungrounded mechanisms when the true cause is outside the recorded data, and that forcing them to ground each claim made them retract and abstain. Its evidence is directional, with high per-seed variance, on non-public data. We cite it as support for the problem, not as proof of our solution.

## 2. Users and the story

**Primary user: Meena**, a process engineer at a fictional auto-parts coating plant. It is 6:10 AM. Line 3 made 3,350 of 4,000 units overnight, rejects were 12% against a normal 2%, and the line stopped twice (18 and 41 minutes). At 8:00 the plant head wants to know why. She has a 140-row export and three confident people: production blames the new operator, maintenance says replace the feeder, stores says the material lot passed QC. Nobody has shown evidence.

**Job to be done:** "Show me what the data does and does not support, fast enough to defend it at 8:00."

**What she needs, in order:** what happened, where the evidence sits, which causes survive the evidence against them, what to verify next, and a draft she can edit and hand over.

**Secondary users:** the plant head (reads the export), hackathon judges (need to see novelty and verification in a 6-minute demo).

## 3. Product principles

1. **Evidence before conclusion.** Nothing is called a cause until its case against it is shown.
2. **Numbers come from code.** The LLM writes words, never numbers.
3. **"Cannot tell" is a valid answer.** The system abstains when the data cannot support a cause.
4. **Show the case against.** Every hypothesis lists For, Against and Still unchecked.
5. **Plain language for tired people.** No jargon on screen; every number is clickable back to its rows (P1).

## 4. Scope

**In scope:** CSV import and validation, timeline and indicators, six-category evidence board, up to three ranked hypotheses with evidence, uncertainty and missing checks, editable RCA draft with verification actions and the engineering-validation notice, held-out validation harness, optional cause-and-effect view, optional real-data stability check, optional plain-LLM ablation.

**Out of scope (MUST NOT build):** equipment control or write-back, live MES or SCADA integration, declaring a confirmed root cause, predicting future failures, user accounts, cloud deployment, multi-incident analysis in one file.

## 5. Requirements

### 5.1 Functional (traceable to Use Case 11, section 11.4)

| ID | Priority | Requirement | Use case ref | Plan task |
|---|---|---|---|---|
| R1 | P0 | Import and validate a time-stamped event CSV. Accept messy headers. Report missing values, out-of-order and duplicate timestamps in plain language. Reject files missing required columns with a clear message. | 11.4.1 | T3, T12 |
| R2 | P0 | Show an incident timeline and key indicators: defect rise with onset time, total defects, downtime and stops, recurring event codes, threshold breaches. | 11.4.2 | T4, T12 |
| R3 | P0 | Group evidence under machine, material, method, measurement, people, environment. Show empty lanes with a hint instead of hiding them. | 11.4.3 | T5, T6, T12 |
| R4 | P0 | Produce up to three ranked hypotheses, each with For, Against, Still unchecked, an evidence-strength label and score. Abstain (`insufficient`) or flag `confounded` when the data cannot separate causes. | 11.4.4 | T6, T7, T12 |
| R5 | P0 | Generate an editable RCA draft: a five-whys chain built only from evidence that ends in what is not yet known, plus verification actions with owner and due. Always carry the engineering-validation notice. Export to Markdown. | 11.4.5 | T8, T12 |
| R6 | P2 | Interactive cause-and-effect view connecting evidence, hypotheses and verification actions. | 11.5 | T14 |

### 5.2 Non-functional

| ID | Requirement |
|---|---|
| N1 | Python 3.13, pip virtual environment, runs on a laptop with no network (LLM optional). |
| N2 | Analysis of a 150-row file completes in under 2 seconds on a laptop. |
| N3 | Every number on screen is computed by code. LLM text is shown only after `verify_narrative` passes; otherwise the template text is shown. |
| N4 | The app works fully with the LLM switched off or failing. |
| N5 | Accessibility: text contrast at least 4.5:1 (verified by `tests/test_tokens.py`), colour never the only cue, controls at least 44 px tall, visible keyboard focus, respects reduced motion. |
| N6 | The NOTICE string is visible on every screen after Start and inside every export. All demo data carries the synthetic label. |
| N7 | No secrets in the repository. The API key comes from `ANTHROPIC_API_KEY`; the model name from `ANTHROPIC_MODEL`. |
| N8 | Uploaded data never leaves the machine. Only the verified facts of one hypothesis are sent to the LLM, and only when the user switches it on. |

### 5.3 Global constraints (copied verbatim into the plan)

- Python 3.13 and a pip virtual environment (`python -m venv .venv`).
- Dependencies are limited to streamlit, pandas, numpy, scipy, plotly, anthropic, pytest and pytest-playwright (`requirements.txt`).
- Every number shown to a user is computed by code in `rca/`. No LLM output reaches the screen unless `rca.verify.verify_narrative` passes.
- No text may claim a confirmed or proven root cause. The NOTICE string from `rca/contract.py` appears on every screen after Start and in every export.
- All demo data is synthetic and labelled with SYNTHETIC_LABEL.
- At most 3 hypotheses are shown.
- Tune thresholds on seeds 1 to 5 only. Report seeds 6 to 20. Never edit a threshold after viewing test-seed results.
- UI: no emoji, colour is never the only cue, text contrast at least 4.5:1, controls at least 44 px tall, spacing on a 4 px grid.
- No browser storage APIs. App state lives in `st.session_state`.
- The app must work with the LLM off.

## 6. User journey and screen requirements

Six screens in a fixed order, shown in a glass navigation bar. Full visual specs are in the design doc; this section fixes behaviour and acceptance.

| # | Screen | Purpose | Key content | Acceptance (Given, When, Then) |
|---|---|---|---|---|
| 0 | Start | Get to a result in one tap | Large title, three sample cards (A clear cause, B two suspects, C unclear cause), file upload, synthetic label | Given the app opens, When I tap "A · Clear cause", Then the Data screen shows. Given I upload a CSV missing a column, Then I read "Missing required columns: ..." and stay on Start. |
| 1 | Data | Build trust in the input | Four tiles (readings, time span, cadence, things to know), one line per warning, 8-row preview | Given sample A, Then "All required columns found" shows. Given missing temperatures, Then a plain-language warning shows. |
| 2 | Timeline | Answer "what happened?" in 10 seconds | One-sentence headline from computed numbers, four stat tiles, three-lane chart with incident marker and operator notes | Given sample A, Then the headline starts "Defects rose from" and the chart is visible. |
| 3 | Evidence | Show where the evidence sits | Six lanes, each evidence line badged "computed" with its id, empty lanes with a hint | Given any sample, Then all six category names are visible. |
| 4 | Court | Put causes on trial | Verdict banner, up to three hypothesis cards (meter, wording, For, Against, Still unchecked with checkboxes), optional AI wording toggle, cause-and-effect expander (P2) | Given A, Then verdict "Ranked" and "Oven temperature high" first. Given B, Then "Cannot separate". Given C, Then "Cannot determine". |
| 5 | Draft | Hand over something defensible | Notice, editable problem and five-whys, verification action table (owner, due, done), Markdown download | Given I edit the problem and download, Then the file contains my edit, the notice and the synthetic label. |

**UX rules across screens**

- One primary action per screen (Continue). Back is always available.
- Every empty or negative result is explained, never blank. Verdict banners are written in plain words.
- Ticking "I already checked this" marks the action done in the draft. It does **not** change evidence strength (changing a score from a tick would be unprincipled). A later version could record outcomes.
- Colour identifies categories only together with a label and glyph. For and Against also use distinct icons.
- Motion is limited to 200 ms transitions and is removed for reduced motion.

## 7. Engine specification (normative)

All code is deterministic and has no LLM dependency.

### 7.1 Input contract

CSV columns (headers normalised to lower snake case, so `Defect Count` and ` Event-Code ` are accepted):

`timestamp, line, machine, event_code, temperature, speed, defect_count, downtime_minutes, batch, operator_note`

Ingest MUST: drop rows with unreadable timestamps and report them; sort by time; interpolate missing temperature and speed; treat missing defect and downtime values as 0 and report the count; raise `ValueError("Missing required columns: ...")`; require at least 20 valid rows.

### 7.2 Incident detection

- Baseline = first 30% of rows (at least 10).
- Smooth defects with a centred 6-row mean. Threshold = baseline mean + 3 x max(baseline std, 0.3) / sqrt(6).
- The incident starts at the first row of a run of at least 6 consecutive rows above the threshold. `high_rows` are all rows in such runs. If none, there is no incident and the verdict is `insufficient`.

### 7.3 Candidate factors

A factor is a boolean mask over rows plus a category.

| Kind | Source | Mask | Category |
|---|---|---|---|
| channel | temperature, speed | robust z (median and MAD of baseline) at least 3 (high) or at most -3 (low) for at least 3 consecutive rows; needs at least 5 rows | machine |
| batch | each batch value | rows with that batch; 5 to 95% of rows | material |
| machine | each machine value | same rule | machine |
| event | each event code seen at least twice | rows with that code | machine |
| note | operator note containing a keyword prefix (table below) | from the note row to the end | by keyword |

Keyword prefixes (word-start match, so "slot" does not match "lot"): machine (fan, noisy, vibration, jam, bearing, leak, belt), material (lot, material, supplier, moisture, resin), method (changeover, setup, recipe, procedure, skipped), measurement (sensor, calibrat, gauge, reading, probe), people (operator, trainee, swapped, relief, handover), environment (humid, ambient, monsoon, power dip, dust).

**Note merging:** a note factor merges into a measured factor of the same category when their masks overlap (Jaccard) at least 0.8, becoming corroboration text. Unmerged notes keep only the earliest note per category as a hypothesis.

### 7.4 Scoring

For each factor compute five sub-scores in [0, 1]:

| Sub-score | Definition |
|---|---|
| effect | Cohen's d of defects inside the mask against outside, divided by 1.5, clipped |
| timing | 1 if the factor starts no later than the incident onset, else 0 |
| consistency | share of high-defect rows where the factor is active |
| specificity | share of the factor's active rows that are high-defect rows |
| dose | best lagged Spearman correlation (lag 0 to 10 rows) between factor magnitude and defects; only for channel factors, otherwise omitted and the weights renormalised |

`score = weighted mean x type weight`, weights effect 0.30, timing 0.25, consistency 0.20, specificity 0.15, dose 0.10. Type weight is 0.75 for notes (free text is corroboration, not proof) and 1.0 otherwise. **Temporal gate:** if timing is 0 the score is capped at 0.45, because a cause cannot start after its effect.

Labels: strong at least 0.70, moderate at least 0.50, otherwise weak. Statements are generated only from computed numbers (for example "It began 39 min before defects rose").

### 7.5 Verdict rules

| Verdict | Condition | Meaning on screen |
|---|---|---|
| `insufficient` | no incident, or the top score is below 0.50 | "Cannot determine". Closest candidates are still listed, all weak. |
| `confounded` | the top hypothesis and another non-note hypothesis, both at least 0.50, have mask Jaccard at least 0.8 and onsets within 15 minutes | "Cannot separate". Both are flagged. |
| `ranked` | otherwise | "Ranked". Strongest candidate named, still a hypothesis. |

Return at most 3 hypotheses. Every hypothesis has at least one Unchecked item. Unchecked items come from the factor kind (for example "Check the Oven temperature sensor against a handheld reference reading").

### 7.6 Output contract

`EvidenceItem{id "EV-001", category (or "overview" for the incident headline), kind, statement, metrics, rows}`
`Hypothesis{id "H1", factor_id, title, category, score, label, subscores, supporting[], against[], unchecked[], evidence_ids[], confounded_with[]}`
`CourtResult{verdict, reason, hypotheses[]}`. Full types are in `rca/contract.py`.

### 7.7 Known limitations (state these in the deck)

Correlational by design. Assumes one incident per file and a roughly regular reading cadence. Thresholds and weights are design choices tuned on synthetic data. Note handling is keyword-based. Confounding is checked pairwise. A single causal story is never claimed.

## 8. AI layer

- **Narrator:** `narrate(hypothesis, llm)` builds a prompt containing only that hypothesis's facts (JSON), asks for at most three plain sentences, and forbids new numbers, times or causes and any "confirmed" or "root cause" wording.
- **Verifier:** every number, `HH:MM` time and forbidden phrase in the reply is checked against the facts. Numbers match at their written precision (0.947 may be written 0.95). ID tokens such as `M-204` are ignored. A failing reply is replaced by the template text and the rejected tokens are shown as a note.
- **Fallback:** no key, network error or timeout falls back to the template with a short reason. The screen never blocks on the LLM.
- **Config:** `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` (default `claude-sonnet-5-5`; confirm the model provisioned by the organizers).
- **Limit of the verifier:** it checks numerals, not number words ("three") and not causal claims. Say so in the deck.

## 9. Synthetic data and answer key

140 rows, 3-minute readings starting 2026-03-04 22:00, line L3. Generated by `generate(scenario, seed)` which also returns an answer key. All data is fictional and labelled synthetic.

| Scenario | Planted truth | Decoys | Expected |
|---|---|---|---|
| A, clear cause | Oven temperature drifts up from about row 58; defects follow with a 6-row lag and rise with temperature | Lot M-204 loaded about 36 rows after the drift began (after the defects); feeder jams (event E115) after defects began; harmless recurring event E050; an operator swap near the end | `ranked`, top-1 `channel:temperature:high`, decoys not top-1 |
| B, confounded | Temperature drift and lot M-204 begin within 2 rows of each other | Same feeder events | `confounded`; both `channel:temperature:high` and `batch:M-204` in the top 3 |
| C, cause not in data | Defects step up at about row 72 with no channel, lot or note change | Late lot change, feeder jams after onset | `insufficient` |

Each seed adds a small random jitter to the planted times. 20 seeds per scenario.

## 10. Validation protocol

Four layers, each with a number you can show:

1. **Held-out answer key.** Tune on seeds 1 to 5. Lock thresholds. Report seeds 6 to 20: verdict correct, top-3 recall, top-1 correct, decoy not top-1, narration verified. Keep and show every failure.
2. **Real-data stability (P2).** UCI SECOM has 1,567 production examples with 591 sensor features and a pass/fail label with a timestamp; only 104 are failures. There is no ground truth for causes, so test stability: signals chosen on the first half of the timeline must keep their sign and size in the second half, compared with a chance baseline from shuffled labels. Claim stability only, never causes.
3. **Ablation (P2).** Give a plain LLM the same CSV and ask for onset time, total downtime, defect rate and most likely cause. Count wrong numbers against engine-computed truth and count answers that claim certainty when the engine abstains.
4. **UI acceptance.** AppTest smoke tests (fast, in `pytest`) and Playwright browser tests, one per expected outcome (section 11.4), also used to capture the user-manual screenshots and a backup demo video.

**Honesty rules:** results on data we generated are expected to be good and are not evidence of real-world accuracy. Say that on the slide. Never tune after looking at test seeds.

## 11. Judging criteria map and deliverables

| Criterion | How this project earns it | Evidence to show |
|---|---|---|
| a) Technical implementation | Deterministic engine, scoring, verifier, 64 tests, modular code | Architecture diagram, test run |
| b) Solution innovation | Evidence Court (For, Against, Unchecked), computed strength, temporal gate, number verifier, honest abstention | Scenarios B and C on screen |
| c) Completeness | Every outcome in 11.4 plus bonus 11.5 | Requirement-to-screen slide (section 5.1) |
| d) Accuracy of verification | Held-out report with failures, SECOM stability, ablation | `validation/report.md` |
| e) AI usage in SDLC | AI used for planning, tests, code, review, docs, with a log | Antigravity artifacts, `docs/prompt-log.md` |
| f) Prompts used | Prompt log from minute zero | Appendix of 8 to 10 best prompts and their outputs |
| g) Teamwork | One owner per folder, visible commits | Contribution slide, everyone speaks |
| h) Presentation and demo | The Meena story in six minutes | Script below |
| i) Value-added features | SECOM check, ablation, cause-and-effect view, Playwright acceptance suite and screenshots | Bonus slide labelled "outside the use case" |

**Deliverables:** working prototype, source code, architecture and design diagram (`docs/architecture.md`), sample execution and output (`docs/screenshots/`, a sample RCA draft), presentation and demo, user manual (`docs/user-manual.md`).

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Agents report success without running tests | Human runs `pytest` and quotes counts; rule in `AGENTS.md` |
| Streams collide on files | One owner per folder; merge at checkpoints |
| Correlation engine produces false confidence | Temporal gate, abstention, held-out seeds, SECOM chance baseline |
| LLM unavailable at demo | Template fallback, recorded video, one-tap samples |
| Scope creep | P2 items (R6, SECOM, ablation) start only after P0 and P1 are green |
| Playwright selectors need tuning on first run | Budget 20 minutes; AppTest suite already covers the flow |
| Pre-work rules | Confirm whether planning documents and code prepared before the event are allowed. Write the code at the event. |

## 13. Decisions log

- Streamlit, not React and FastAPI: one language, fastest to a working demo, four parallel owners. The engine is a separate package that could sit behind an API later.
- Light theme only for the build; dark tokens are a design-doc P2.
- Evidence strength is not changed by ticking checkboxes (see section 6).
- System blue is not used behind small white text because it measures 4.0:1; the blue fill token is `#0066CC` (5.6:1).
- Category colour is identity, never meaning. Meaning is carried by labels and icons.
- The bonus cause-and-effect view uses Graphviz DOT through `st.graphviz_chart` so no extra dependency is needed.

## 14. Sources

- Siemens, The True Cost of Downtime 2024
- Senseye and Siemens, True Cost of Downtime 2022
- Deloitte and The Manufacturing Institute, 2024 talent study
- Ohno's five-whys example
- Criticism of 5 Whys
- Practitioner view on RCA tools and whiteboards
- Ochi and Uchiyama, Five Whys as an Epistemic-Honesty Scaffold, IJACSA 17(8), 2026
- CausalPulse, AAAI 2026
- Fraunhofer, RAG with knowledge graphs for manufacturing problem solving, CASE 2025
- UCI SECOM dataset
