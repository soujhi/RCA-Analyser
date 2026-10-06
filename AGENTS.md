# RCA Analyzer: agent rules

A Streamlit app that reads a production event CSV and ranks **hypotheses** for a quality incident, showing evidence For, Against and Unchecked. TCS-SASTRA hackathon, Use Case 11 (Production RCA Analyzer).

- Spec (read first): `docs/superpowers/specs/2026-10-06-rca-analyzer-prd.md`
- Plan (execute task by task): `docs/superpowers/plans/2026-10-06-rca-analyzer-implementation.md`
- Design: `docs/design/figma-design-doc.md`

## Commands

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                                  # unit and AppTest, fast, no browser
python -m streamlit run app.py
python -m validation.run_validation
playwright install chromium
pytest -m e2e tests/e2e --override-ini addopts=""       # browser tests
```

## Layout and owners (one owner per folder, never edit another owner's folder)

| Folder | Owner stream | Holds |
|---|---|---|
| `rca/contract.py`, `rca/data/`, `rca/ingest.py`, `validation/` | Data and validation | Types, generator, loader, metrics |
| `rca/stats.py`, `factors.py`, `court.py`, `analysis.py`, `draft.py` | Engine | All numbers and scoring |
| `rca/verify.py`, `rca/narrate.py`, `docs/` | AI and docs | Narrator, verifier, deliverables |
| `rca/ui/`, `app.py`, `tests/e2e/` | UI | Screens, tokens, browser tests |

## Hard rules

1. Every number a user sees is computed by code in `rca/`. The LLM only writes words.
2. LLM text is shown only if `rca.verify.verify_narrative` passes. The app must work with the LLM off.
3. Never write that anything is a confirmed, proven or definite root cause. Use the NOTICE string from `rca/contract.py` on every screen after Start and in every export.
4. At most 3 hypotheses are shown. When evidence is weak the verdict is `insufficient`, and that is a correct answer.
5. All demo data is synthetic and carries SYNTHETIC_LABEL.
6. Tune thresholds on seeds 1-5 only. Report seeds 6-20. Never change a threshold after looking at seeds 6-20.
7. UI: no emoji, colour is never the only cue, text contrast at least 4.5:1, controls at least 44 px tall, spacing on a 4 px grid. Use tokens from `rca/ui/tokens.py`.
8. Python 3.13 only. Do not add dependencies beyond `requirements.txt` without asking the team.

## Workflow

- Follow the plan: write the test, run it and see it fail, implement, run it and see it pass, commit.
- Never say tests pass without running them in this session and quoting the pass count.
- If a test fails twice, stop and ask. Do not weaken a test to make it pass.
- Commit after every task with the message given in the plan.
- Append every significant prompt to `docs/prompt-log.md`: date, tool, prompt, what came back, what we changed.
