# What the 53 ERROR legs actually are

**2026-08-28, 03:58 BST.** Follow-up to the convergence-gate panel, which found that 12 of the 23 `SAME`
verdicts carry an ERRORed leg. Following that into `_direction` showed the damage is wider (40 of 178
leg-bearing directions, 34 of 133 pairs — see `resources/RECOVERY.md`). This note asks the next question:
**what is the ERROR?**

`reverify_falsifier` (`bench/falsifier_verify.py:1064`) documents `ERROR` as covering three different
things at once — a timeout, a harness/launch failure, or a nonzero exit that is not a genuine
demonstration. That conflation is deliberate and it is defensible: the asymmetry exists so that a model
shipping a falsifier with a bad import cannot have its finding silently auto-CONFIRMED. It was put there
after a review on 3 June 2026. **Nothing below argues for removing it.**

## What was measured

25 findings that appear in ERROR-bearing pairs were re-run against the **pristine** tree today, and the
9 that errored were then run again in a subprocess with stderr captured.

| cause | n | what it is |
|---|---|---|
| `MemoryIntegrityError` | 2 | **the target's own guard fired** |
| `FileNotFoundError` | 6 | the falsifier's target file does not exist |
| `RuntimeError: Expected real target document not found` | 1 | same, reported by the harness |

## The two classes are not the same thing, and only one is equipment

**Class 1 — the guard fired (exp45 C0003, C0022).** These falsifiers ask whether `ImmuneMemory` accepts a
negative count. It does not: `_check_count` raises `MemoryIntegrityError`. **That raise IS the answer to
the question the falsifier asked** — the defect is absent. But an uncaught exception is a nonzero exit, so
the verdict recorded is `ERROR` rather than `REFUTED`. The instrument cannot distinguish *"the target's
guard rejected the bad input"* from *"the instrument broke"*, because both arrive as a traceback.

**Class 2 — the target is missing (exp48, 7 of 7).** `FileNotFoundError` on paths under
`~/CDSFL_review_targets/` and inside the repository. This is genuine equipment failure. It is also
low-stakes: **exp48 is the run already excluded for the key-read incident**, so its pairs carry no weight.

## What this does NOT show

The recorded ERROR legs were measured **against a patched tree** — after a candidate fix was applied —
not against the pristine one. This probe used the pristine tree, so it measures an adjacent condition and
not the same one. **16 of the 25 findings probed do not error on the pristine tree at all**, which means
their recorded ERROR arose only under patching, and this note does not establish why. exp44 (15 pairs) and
exp49 (10 pairs) are entirely in that unexplained group.

So the honest scope is: **a distinct non-equipment class exists inside `ERROR` and has been demonstrated
on two findings.** It is not established what fraction of the 53 legs it accounts for, and the largest
groups remain unexplained.

## Not fixed here, and why

Separating "the target's guard fired" from "the instrument broke" changes verdict semantics in the runner's
core, on the same night two of the reporting agent's own empirical claims were refuted by the panel. That
is the wrong moment to edit verdict semantics. It is recorded for a ruling instead.

The shape of a fix, for when it is ruled on: a falsifier's designed demonstration is already required to be
an `AssertionError` or the literal token `FALSIFIED`. An exception raised from **inside the target module**
is evidence the target rejected the input, which is a REFUTED-shaped answer, whereas an exception raised
from the snippet's own frame is instrument failure. The traceback distinguishes them and is already captured.
