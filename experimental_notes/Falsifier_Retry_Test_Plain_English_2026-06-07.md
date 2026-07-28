# The Falsifier Retry Test, and the Confirm-vs-Refute Asymmetry (Plain English)

**2026-06-07 10:29 BST**

## What was tested

Experiment 42 ended without converging: 15 critical findings couldn't be tool-confirmed, and the safety rule that blocks convergence while any unverified critical remains held it open. The proposed fix: when a model's falsifier (its little test) fails, feed the failure back to that model and ask it to fix it — like reprompting any model that gave a malformed answer. This run tested that directly on the 15 stuck findings, then checked whether the results were *correct*, not just present.

## The retry works

Two changes: a harness fix so the test sandbox imports the target by either path style (removing the relative-path failures that broke when a test ran from a throwaway directory), and the retry itself (feed the error back to the source model, once; the runner independently re-runs the fix and decides — the model is never told what verdict to produce).

**Of 15, ten resolved.** Four fixed for free by the harness change; six by a single retry. With the 3-attempt cap, more of the remaining five would resolve. So the core claim holds: on a coding task, a model that wrote a broken test will usually fix it once it sees the real error. Genuine incapability is rare.

## The asymmetry — the real finding

Resolving isn't the same as resolving *correctly*. Each of the ten resolutions was audited against the real code, the auditor writing and running its own corrected test where a verdict looked suspect. **Eight of ten were correct — and the two errors were entirely one-sided.**

- **Every confirmation (7/7) was correct** — real defect, demonstrated for the right reason.
- **Refutations were the weak point: only 1 of 3 was genuine.** The other two *masked real bugs*: one test compared a value the function quietly modifies in place (so the comparison was always equal and the test passed without testing anything); the other built an inert stand-in that never exercised the real limits where the bug lives.

The cause is clean. A **confirmation** requires the test to *actively demonstrate* the defect (raise an error / print a token) — hard to fake. A **refutation** is just a *clean exit* — and a broken test that does nothing in particular also exits cleanly. So a confirmation is trustworthy by construction; a refutation is only as trustworthy as the test's setup. That's a property of what running a test can tell you, not a flaw in the runner.

## The convergence question, answered honestly

The hope was that clearing the 15 residuals would let Experiment 42 converge. The evidence says that's plausible: the panel was already running out of new findings (15 new in round 1 → 1 by the last), and the dominant thing holding convergence open was the queue of unverified criticals. Clear that queue with genuine verdicts and the run can settle, probably with a few extra rounds.

**But the caveat is sharp.** The runner clears the queue *honestly* — it re-runs each fix and decides for itself, so the convergence flag wouldn't be faked. The danger is subtler: two of the resolved findings are false refutations of real bugs. A naive retry would let Experiment 42 declare success while silently carrying two genuine defects labelled non-defects. **That isn't a rigged flag — it's a correct flag on wrong data, which is worse for looking clean.** So: yes, resolving the residuals can take Experiment 42 over the line, and the mechanism is genuine — but a naive version would cross it while hiding two real bugs.

## The fix that follows

The asymmetry is also the cure, and it's cheap. **Trust confirmations as they are** (7/7 reliable). **Accept a refutation only if the test actually set up and exercised the claimed condition**, rather than exiting cleanly for an unrelated reason — both false refutations here would fail that check. In practice: when a finding is refuted but was independently judged likely real, re-ask the model to prove its test triggers the claimed condition, or escalate to a human. This is *not* model voting — it's a structural check on one identified weakness.

## Where this leaves it

The retry is validated and worth building in, with the 3-attempt cap and the human queue as the final escape; the harness change is a free win. The one addition the evidence demands is **refutation scrutiny**, so resolving the residuals yields *correct* verdicts, not merely tidy ones. With that, a re-run of Experiment 42 would be the definitive, honest convergence test. Without it, convergence would be reachable but dishonest — the one outcome ruled out from the start.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Technical: `Falsifier_Retry_Test_2026-06-07.md`. TTS: `~/Desktop/CDSFL_tts/Falsifier_Retry_Test_and_Confirm_Refute_Asymmetry_2026-06-07.txt`.*
