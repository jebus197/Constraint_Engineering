# Why the existing machinery was not clearing the reducible pile

**Founder question, 2026-08-29:** *"is there genuinely nothing that can be utilised to detect when a fix is
either (genuinely) 'inadmissible', and/or when such a condition is detected, feed it back to the model/s and
require them to use a stronger/better falsifier (or to just 'check your work, it appears to be wrong') and/or
to build a better fix? We should already have much of this machinery. Why isn't it being used in these
specific cases?"*

**Short answer: most of it IS being used. One specific thing is not, and it cannot be, by design — but the
same measurement can be taken a different way that the design permits.**

CC1's framing on the morning of 2026-08-28 — that the machinery exists and is simply "not wired" — is
**withdrawn**. It was wrong, and checking rather than asserting is what showed it.

## What IS wired, enabled, and running

`build_feedback_sections` composes a per-model corrective block and the runner prepends it to that model's
prompt in the **next round** (`reference_runner_v2.py:10302` builds it, `:9973` delivers it). It is ON by
default: `_directive_factor_state(cfg, "feedback")` returns `(True, True)` on a stock `RunnerConfig`.

The corrective lines it already emits, verbatim from the source:

| condition detected | what the model is told |
|---|---|
| falsifier verdict `ERROR` | *"FALSIFIER ERROR: your test did not run to a verdict (broken import, syntax error, truncation, or a setup guard firing). It demonstrated nothing. Re-write it so it runs."* |
| falsifier verdict `UNTOOLABLE` | *"NO FALSIFIER: nothing runnable was attached, so nothing was demonstrated."* |
| `SK_REJECTED` / `SK_NO_SCORE` | *"FIX NOT SCORED…"* — fix-admission undefined or the evidence gates went silent |
| corrected copy refused | *"CORRECTED COPY REFUSED: … Re-send it in the CORRECTED_COPY form"* |

So the founder's *"just 'check your work, it appears to be wrong'"* already exists for broken and missing
falsifiers. It is neither absent nor switched off.

## CORRECTION, 2026-08-30 00:40 — the section below was wrong when first written

**The original text of this section claimed "a fix is never applied and its own falsifier re-run during a
live experiment." That is false and is withdrawn.**

`bench/bugzilla_loop.py::attempt_close` already extracts a proposed fix, applies it to a **sandbox copy**
via `apply_fix_to_sandbox`, runs verification against that copy, and deletes the copy in a `finally`. It is
called from `_update_finding_statuses` at `reference_runner_v2.py:2596` and it **runs in flight today**.

CC1 asserted the absence after reading `reference_runner_v2.py` and finding `apply_fixes_back_enabled=False`,
and never opened `bugzilla_loop.py`. This is the *check the whole set* failure again: a universal claimed
after checking one member.

Worse, the evidence was already in hand. CC2 stated it plainly in the convergence-gate panel of 2026-08-28
— *"That is apply-a-fix-and-re-run, in scope, already running"* — in a document CC1 had read and versioned
two days earlier.

**The gap, stated accurately this time**, is narrower and more specific:

`run_verification` runs **ruff, mypy, bandit and the experiment's generic `test_cmd`** against the sandbox.
It does **not** run *that finding's own falsifier*. So the machinery asks "did this fix break anything, and
do the project's tests still pass" — it never asks **"does this fix actually cure the defect this finding's
own falsifier demonstrates?"**

That is the `FIX_INEFFECTIVE` condition, and it is why 16 of the 48 undecided pairs are invisible to the
live loop.

**The repair is correspondingly smaller than first proposed.** Not a new subsystem: one additional check
inside the existing sandbox verification, running the finding's attached falsifier against the sandbox copy
that `apply_fix_to_sandbox` has already produced. The sandbox, the apply, the cleanup and the call site all
exist.

---

## Original section, retained for the record (its claim is withdrawn above)

**A fix is never applied and its own falsifier re-run during a live experiment.** That is the counterfactual
test, and it is the only way to detect the `FIX_INEFFECTIVE` condition — a fix that does not cure the defect
it claims to cure. **16 of the 48 undecided similarity pairs are exactly this condition**, and the live loop
cannot see it.

The reason is not neglect. It is founder-directed methodology, `bench/launch_exp41.py:6`, dated 2026-05-22:

> STATIC TEST ARTICLE — `apply_fixes_back_enabled=false`. The panel reviews `bench/dm/_convergence.py`
> (frozen) every round; fixes fold post-experiment, not mid-experiment.

`apply_fixes_back_enabled` defaults `False` and is explicitly false in the exp41 and exp42 launchers. If the
target changed between rounds the experiment would stop measuring what it is designed to measure. `exp42`'s
launcher says the same thing in the same words.

`scripts/adjudicate_by_repair.py` exists to do post-hoc precisely what the frozen-target design forbids
in-flight. So the 48 undecided pairs are **the residue at the moment each run stopped**, analysed months
later, not evidence of unused machinery.

## The gap that is real, and closable without unfreezing anything

Detecting `FIX_INEFFECTIVE` does **not** require rewriting the reviewed target. `adjudicate_by_repair`
already proves this: it writes the patched text, runs the falsifier, and restores the original in a
`finally`. The reviewed article is byte-identical afterwards.

So the same measurement can be taken in-flight on a **scratch copy**, leaving the frozen target untouched,
and its result fed into the feedback channel that already exists — one more line beside the four above:

> YOUR FIX DOES NOT CURE YOUR OWN FALSIFIER. Applying it and re-running your test leaves the test still
> demonstrating the defect. Either the fix is incomplete or the test does not test what the finding claims.

That closes the founder's loop for the largest single category of undecided pairs, costs one falsifier
re-run per proposed fix, and does not touch the static-article methodology.

**A second, smaller gap:** the in-round re-ask (`_inround_reask`) fires on **one** condition only — output
that did not parse — and its prompt says *"Do not add new analysis; reformat what you already produced."*
Everything else waits for the next round, so a finding whose falsifier errors in the **final** round never
gets a repair opportunity at all.

## Status

Diagnosis only. Nothing changed by this note. The proposed probe and the final-round gap are going to the
review panel with a request for the **fix**, not merely the finding — a briefing defect the founder
identified on 2026-08-29 and which this session has confirmed applied to all three previous dispatches.
