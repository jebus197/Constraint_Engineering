# Half the proposed fixes in the archive do not silence their own test

**2026-08-30.** First run of `scripts/fix_efficacy_sweep.py`, using the overlay probe in
`bench/fix_efficacy.py`. This is the measurement the founder asked for when they asked why the reducible
pile was not clearing.

## The result

**313 findings probed** — every archived finding carrying a falsifier, a proposed fix, and a target that
still exists. **246 produced a verdict.** The other 67 were equipment and are broken out below.

| outcome | n | share of verdicts |
|---|---|---|
| the fix **cures** the defect its own falsifier demonstrates | **120** | 49% |
| the fix **does not cure** it | **126** | **51%** |

By run: exp42 79 of 165, exp43 9 of 33, exp44 11 of 47, exp45 1 of 13, exp46 7 of 14, exp47 19 of 41. The
rate varies from 8% to 50% across runs, so it is not an artefact of one target.

## What this does NOT say — read before quoting the 51%

**It does not say half the fixes are bad.** The probe measures whether a *pair* is consistent: fix, and the
finding's own test. When the test still fires afterwards, **either the fix is incomplete or the test does
not test what the finding claims**. This measurement cannot tell those apart, and the verdict is named for
what was observed rather than for a cause.

Given that **9 falsifiers in this same archive were separately measured never to read their target at all**,
and that the discrimination control found roughly half of 263 falsifiers did not go quiet when their accused
defect was repaired, a substantial share of these 126 is likely to be **the test being wrong, not the fix**.

**And none of these fixes was ever applied or reviewed.** They are model proposals from finished runs. A
proposal that turns out not to work is a normal research output, not a scandal.

## Falsification of the result itself

The obvious artefact would be fixes that fail to apply, or apply trivially, and so leave the defect in place
for a mechanical reason. Checked, and it is not that:

* **0 of 246** patches changed zero lines.
* **0 of 246** were whole-file replacements.
* Ineffective fixes change a **median of 5 lines** (mean 8, range 1–30); effective ones a median of 9 (mean
  13, range 1–68). Both are substantive edits.

So the fixes genuinely apply and genuinely fail to silence their own tests.

## The 67 that produced no verdict

| outcome | n | meaning |
|---|---|---|
| `INDETERMINATE_OTHER` | 29 | the falsifier ERRORed on the patched target — the fix broke the file it was meant to repair, or the test cannot survive the edit |
| `INDETERMINATE_NO_APPLICABLE_FIX` | 22 | the proposed fix did not apply to the target at all |
| `INDETERMINATE_NO_BASELINE` | 10 | the falsifier did not reproduce on the UNMODIFIED target, so there was nothing for a fix to cure |
| `INDETERMINATE_NOT_INTERCEPTED` | 6 | the falsifier reaches its target by no route the overlay controls, so no verdict is available |

The 29 are worth their own look: a fix that makes its own target un-runnable is a distinct and more serious
condition than a fix that merely does not work, and nothing currently reports it.

## Why nothing had measured this before

`scripts/adjudicate_by_repair.py` performs the same counterfactual, but only for findings that appear in a
**similarity pair** — its question is "are these two findings the same defect". Across the archive, 382
findings carry both a falsifier and a fix and only 85 appear in an adjudicated pair. **The other 297, 78%,
had never been checked for fix efficacy by any instrument**, because a finding with a bad fix and no
near-duplicate was never in scope for anything.

Where both instruments looked, they agree.

## Status

Measurement only. No finding's status was changed, no fix was applied, and every reviewed target is
byte-identical — the probe works through the discrimination control's overlay and the sweep was run with
`git status` clean before and after.
