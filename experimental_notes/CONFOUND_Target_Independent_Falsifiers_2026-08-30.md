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
then asserts something unrelated to the accused defect is recorded as coupled, exactly as a rigorous one is. So 348
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


---

# CORRECTION, 2026-08-30 01:47 — the figure of 9 is an OVERCOUNT

**The "9 of 372" above is withdrawn as a confirmed count. The defensible floor is 4.**

Found by cross-verifying against a second, independent instrument — the overlay tripwire built the same
night — which disagreed on one finding. Chasing the disagreement instead of preferring a side showed the
substitution probe has a **false-positive mode**.

## The false-positive mode

`reverify_falsifier` records **any** `AssertionError` as CONFIRMED. Several falsifiers open with a
**precondition assertion** — *am I looking at the right module?* — before testing anything:

```python
from bench.dm import _divergence as div
source = inspect.getsource(div)
assert "_ALT_HEADER_RE" in source          # precondition, not the test
```

Replace the target with an unrelated file and **that precondition fires**. The probe sees CONFIRMED and
concludes "it never read the target", when the truth is the opposite: it read the target, found the wrong
one, and said so — and the harness translated *"I cannot examine this"* into *"the defect is present"*.

exp47 C0010 is confirmed as exactly this.

## Revised breakdown of the 9

| | n | findings |
|---|---|---|
| **no `bench` import at all — genuinely detached** | **4** | exp44 C0022, C0023, C0078; exp47 C0061 |
| confirmed probe false positive | 1 | exp47 C0010 |
| imports the target; CONFIRMED-on-unrelated may be a precondition firing | 4 | exp44 C0007, C0008; exp46 C0023; exp47 C0058 |

**So: 4 confirmed, up to 9, and 4 need individual examination.** The confound stands for the 4; for the
other 5 it is unproven either way.

## The finding underneath is worth more than the count

**A falsifier whose setup fails is recorded as demonstrating the defect.** That is not a defect in any
individual falsifier — it is the verdict rule in `reverify_falsifier`, which cannot distinguish a
precondition assertion from the designed demonstration, because both arrive as `AssertionError`.

This is **I14, the falsifier gate** — the single component the instrument inventory still lists as
uncommissioned and that genuinely matters. It already accepts a falsifier that never touches its target;
it also accepts one that could not find its target and said so.

That is the item to put to the panel, and it is worth more than the correction from 9 to 8.


---

# SECOND CORRECTION, same night — the figure is 8. The first correction was ALSO wrong.

**Sequence: 9 asserted → 4 inferred → 8 measured.** The middle step is the one to learn from.

The correction above reduced 9 to a "defensible floor of 4" by **reading the falsifiers statically** and
sorting them by whether they import their target and whether they open with a precondition assertion. That
was inference, not measurement, and it was wrong in the cautious direction.

**Running them settles it.** Each of the four "uncertain" findings was executed against a target replaced
wholesale, with stderr captured:

| finding | what it did against a destroyed target |
|---|---|
| exp44 C0007 | `AssertionError: FALSIFIED: _check_monotonicity accepted bool True for numeric HARD threshold…` |
| exp44 C0008 | `AssertionError: FALSIFIED: load_effective_policy accepted model='../evil_model'…` |
| exp46 C0023 | `AssertionError: _compute_cid collapses distinct directive contents into the same cid…` |
| exp47 C0058 | `AssertionError: F016 present: distinct order-sensitive contrast statements were collapsed…` |

Every one printed **FALSIFIED** and raised with **the finding's own message** — its real demonstration, not
a setup check — against a file sharing nothing with its target. They are genuinely target-independent.

## Final count

| | n |
|---|---|
| **genuinely target-independent** | **8** |
| probe false positive (precondition assertion, exp47 C0010) | 1 |
| **of 372** | **8, or 2.2%**, 95% Wilson CI **[1.1%, 4.2%]** |

The eight: exp44 C0007, C0008, C0022, C0023, C0078; exp46 C0023; exp47 C0058, C0061.

**The confound stands for these 8.** exp47 C0010 is removed from it.

## What the middle step cost, and why it is recorded

Nothing reached the founder wrongly — both corrections were made in the same session, before the morning.
But the pattern is worth naming, because it is the *same* pattern in the opposite direction: **the first
figure was asserted from one instrument without cross-checking; the second was inferred from source text
without running anything.** Only the third was measured.

The founder's standing rule covers both: the tool output is the evidence, and reasoning selects and
interprets it but never substitutes for it. Reading four falsifiers and sorting them by shape is reasoning
substituting for it.
