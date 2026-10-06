## Held-out validation, seeds 1-5

| Scenario | Verdict correct | Top-3 recall | Top-1 correct | Decoy not top-1 | Narration verified |
|---|---|---|---|---|---|
| A | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) |
| B | 100% (5/5) | 100% (10/10) | n/a | n/a | 100% (5/5) |
| C | 100% (5/5) | n/a | n/a | 100% (5/5) | 100% (5/5) |

### Failures (kept on purpose)
- None

## Held-out validation, seeds 6-20

| Scenario | Verdict correct | Top-3 recall | Top-1 correct | Decoy not top-1 | Narration verified |
|---|---|---|---|---|---|
| A | 100% (15/15) | 100% (15/15) | 100% (15/15) | 100% (15/15) | 100% (15/15) |
| B | 93% (14/15) | 100% (30/30) | n/a | n/a | 100% (15/15) |
| C | 100% (15/15) | n/a | n/a | 93% (14/15) | 100% (15/15) |

### Failures (kept on purpose)
- Scenario B seed 9: expected confounded, got ranked, top3 ['batch:M-204', 'channel:temperature:high', 'note:machine:86']
