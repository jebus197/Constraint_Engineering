# CONFOUND — 9 findings whose falsifier never read its target

**Founder ruling, 2026-08-29:** *"Not 'struck from the record' because that is hiding, but recorded in our
experimental notes as a confound, and fixed for future runs."*

This is that record. **Nothing has been deleted, retracted or hidden.** The findings stand in the registry
exactly as they were. What follows is the caveat that must travel with them.

## What was measured

`scripts/target_independence_probe.py` replaces a falsifier's target with an unrelated but syntactically
valid Python file and re-runs it. A falsifier that still reports the defect cannot have been reading the
file it accuses.

Across all 372 archived falsifiers:

| verdict on the real target | verdict on an unrelated file | n | reading |
|---|---|---|---|
| CONFIRMED | ERROR | 346 | coupled — reached for the target and could not use it |
| REFUTED | ERROR | 10 | coupled |
| **CONFIRMED** | **CONFIRMED** | **9** | **target-independent — never touched the file** |
| ERROR | ERROR | 5 | undecidable |
| CONFIRMED | REFUTED | 2 | coupled |

**9 of 372, which is 2.4%.** Not the 93% that the separate figure of 346-of-372-fired-on-every-version
invites. Those two numbers answer different questions and do not conflict.

## The 9

| run | finding | target |
|---|---|---|
| `exp44_evidence_locationkey_live_20` | `C0007` | `bench/evidence.py` |
| `exp44_evidence_locationkey_live_20` | `C0008` | `bench/evidence.py` |
| `exp44_evidence_locationkey_live_20` | `C0022` | `bench/evidence.py` |
| `exp44_evidence_locationkey_live_20` | `C0023` | `bench/evidence.py` |
| `exp44_evidence_locationkey_live_20` | `C0078` | `bench/evidence.py` |
| `exp46_stage6_locationkey_live_2026` | `C0023` | `bench/dm/_shadow_stage6.py` |
| `exp47_divergence_locationkey_live_` | `C0010` | `bench/dm/_divergence.py` |
| `exp47_divergence_locationkey_live_` | `C0058` | `bench/dm/_divergence.py` |
| `exp47_divergence_locationkey_live_` | `C0061` | `bench/dm/_divergence.py` |

## What the confound is, precisely

For these 9, the falsifier verdict of CONFIRMED is **not evidence about the target**. It is evidence that
the falsifier fires unconditionally. The finding itself may still be correct — a model can describe a real
defect and attach a test that does not test it — but **the CONFIRMED status rests on nothing**, and any
downstream count that treats those 9 as verified is inflated by 9.

Three runs are affected: exp44 (5 findings, `bench/evidence.py`), exp46 (1, `bench/dm/_shadow_stage6.py`),
exp47 (3, `bench/dm/_divergence.py`). No run loses its convergence verdict over this — the two-sided gate
reads novelty and severity, not falsifier verdicts — but any claim of the form *"N findings were
independently verified"* on those three runs must say N minus these.

## The caveat that must travel with the number

Coupling here is established **by import**, not by test content. A falsifier that imports its target and
then asserts something unrelated to the accused defect scores identically to a rigorous one. So 348
"coupled" is **not** a clean bill of health — it rules out only the crudest failure. The stronger question,
whether a falsifier tests the defect it actually accuses, is not answered by this measurement and remains
open.

## Fixed for future runs — status

The mechanism that detects this already exists and is **presence-gated**: the discrimination control
(`run_discrimination_control`) runs if and only if a finding carries a corrected copy, which the model has
to supply. No corrected copy, no check, and the gate confirms.

Making it mandatory for critical CONFIRMs is the repair, and it is a **behavioural change to the runner's
verdict path**. It is specified but NOT applied here, for the same reason the merge enable is not: it
changes what a verdict means, the review panel is unavailable tonight (`BLOCKED_Panel_Auth_2026-08-30.md`),
and the founder's own instruction is to take that route when the best fix is not obvious.
