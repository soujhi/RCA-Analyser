"""Held-out validation. Tune on TUNE_SEEDS only; report TEST_SEEDS. Run: python -m validation.run_validation"""
from __future__ import annotations

import json
from pathlib import Path

from rca.analysis import analyze
from rca.data.generator import SCENARIOS, generate
from rca.narrate import facts_for, template_narration
from rca.verify import verify_narrative

TUNE_SEEDS = range(1, 6)
TEST_SEEDS = range(6, 21)
OUT = Path(__file__).parent


def evaluate(seeds) -> dict:
    results: dict = {}
    failures: list = []
    for scenario in SCENARIOS:
        counts = dict(n=0, verdict_ok=0, recall_hits=0, recall_total=0, top1_ok=0, top1_n=0,
                      decoy_ok=0, decoy_n=0, narration_ok=0, narration_n=0)
        for seed in seeds:
            df, key = generate(scenario, seed)
            court = analyze(df).court
            top3 = [h.factor_id for h in court.hypotheses]
            counts["n"] += 1
            if court.verdict == key["expected_verdict"]:
                counts["verdict_ok"] += 1
            else:
                failures.append({"scenario": scenario, "seed": seed, "expected": key["expected_verdict"],
                                 "got": court.verdict, "top3": top3})
            counts["recall_total"] += len(key["expected_in_top3"])
            counts["recall_hits"] += sum(1 for f in key["expected_in_top3"] if f in top3)
            if key["expected_top1"]:
                counts["top1_n"] += 1
                counts["top1_ok"] += int(bool(top3) and top3[0] == key["expected_top1"])
            if key["decoys"]:
                counts["decoy_n"] += 1
                counts["decoy_ok"] += int(not top3 or top3[0] not in key["decoys"])
            if court.hypotheses:
                h = court.hypotheses[0]
                counts["narration_n"] += 1
                counts["narration_ok"] += int(verify_narrative(template_narration(h), facts_for(h)).ok)
        results[scenario] = counts
    return {"scenarios": results, "failures": failures}


def _rate(num: int, den: int) -> str:
    return "n/a" if den == 0 else f"{num / den:.0%} ({num}/{den})"


def to_markdown(report: dict, seeds) -> str:
    seeds = list(seeds)
    lines = [f"## Held-out validation, seeds {seeds[0]}-{seeds[-1]}", "",
             "| Scenario | Verdict correct | Top-3 recall | Top-1 correct | Decoy not top-1 | Narration verified |",
             "|---|---|---|---|---|---|"]
    for name, c in report["scenarios"].items():
        lines.append(f"| {name} | {_rate(c['verdict_ok'], c['n'])} | {_rate(c['recall_hits'], c['recall_total'])} | "
                     f"{_rate(c['top1_ok'], c['top1_n'])} | {_rate(c['decoy_ok'], c['decoy_n'])} | "
                     f"{_rate(c['narration_ok'], c['narration_n'])} |")
    lines += ["", "### Failures (kept on purpose)"]
    lines += [f"- Scenario {f['scenario']} seed {f['seed']}: expected {f['expected']}, got {f['got']}, top3 {f['top3']}"
              for f in report["failures"]] or ["- None"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    tune, test = evaluate(TUNE_SEEDS), evaluate(TEST_SEEDS)
    text = to_markdown(tune, TUNE_SEEDS) + "\n" + to_markdown(test, TEST_SEEDS)
    (OUT / "report.md").write_text(text)
    (OUT / "results.json").write_text(json.dumps({"tune": tune, "test": test}, indent=2))
    print(text)
