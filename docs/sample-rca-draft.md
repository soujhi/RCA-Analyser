# RCA draft

> Hypotheses only. Engineering validation is required before any action. This tool never controls equipment and never declares a confirmed root cause.
> Synthetic demo data. Fictional equipment and figures.

**Verdict:** ranked

**Problem:** Defects rose from 0.5 to 3.8 per row from 02:03.

## Five whys
1. **Why did output miss its quality target?** Defects rose from 0.5 to 3.8 per row from 02:03. (EV-001)
2. **Why did it happen?** The strongest candidate is Oven temperature high. (EV-002)
3. **What supports that?** Defects averaged 3.3 per row while this was active, against 0.6 otherwise. (EV-002, EV-003, EV-004)
4. **What supports that?** It began 39 min before defects rose. (EV-002, EV-003, EV-004)
5. **Why did that happen?** Not determinable from this data. Complete the verification actions below.

## Verification actions
- [ ] Check the Oven temperature high sensor against a handheld reference reading. Owner: unassigned. Due: unset.
- [ ] Inspect the equipment behind Oven temperature high and its recent maintenance log. Owner: unassigned. Due: unset.
- [ ] Compare the supplier certificate of Batch M-204 with earlier lots. Owner: unassigned. Due: unset.
- [ ] Test retained samples from Batch M-204 against the material specification. Owner: unassigned. Due: unset.
