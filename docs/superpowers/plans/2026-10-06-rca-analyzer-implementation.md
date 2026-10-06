# RCA Analyzer Implementation Plan

**Goal:** Build a Streamlit app that reads a production event CSV, shows what happened, sorts the evidence into six categories, and puts up to three possible causes on trial (For, Against, Still unchecked), ending in an editable RCA draft.

**Architecture:** A deterministic Python engine (`rca/`) computes every number: incident detection, candidate factors, scoring with a temporal gate, and verdicts (`ranked`, `confounded`, `insufficient`). An optional Claude narrator writes plain wording, and a number verifier rejects any text containing a number the engine did not compute. A six-screen Streamlit UI follows Apple-style design tokens. A separate validation layer holds a seeded generator with an answer key, a held-out harness, and browser tests.

**Tech Stack:** Python 3.13+, streamlit, pandas, numpy, scipy, plotly, anthropic, pytest, pytest-playwright.

**Spec:** `docs/superpowers/specs/2026-10-06-rca-analyzer-prd.md`

## Global Constraints

- Python 3.13+ and a pip virtual environment (`python -m venv .venv`).
- Dependencies are limited to streamlit, pandas, numpy, scipy, plotly, anthropic, pytest and pytest-playwright (`requirements.txt`).
- Every number shown to a user is computed by code in `rca/`. No LLM output reaches the screen unless `rca.verify.verify_narrative` passes.
- No text may claim a confirmed or proven root cause. The NOTICE string from `rca/contract.py` appears on every screen after Start and in every export.
- All demo data is synthetic and labelled with SYNTHETIC_LABEL.
- At most 3 hypotheses are shown.
- Tune thresholds on seeds 1 to 5 only. Report seeds 6 to 20. Never edit a threshold after viewing test-seed results.
- UI: no emoji, colour is never the only cue, text contrast at least 4.5:1, controls at least 44 px tall, spacing on a 4 px grid.
- No browser storage APIs. App state lives in `st.session_state`.
- The app must work with the LLM off.
