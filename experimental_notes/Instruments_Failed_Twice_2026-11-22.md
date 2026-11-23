# When The Instruments Failed Twice, And A Guard Could Not Judge Its Own Repair

22 November 2026, 20:35 GMT

## Summary

Batch 3 of the autonomy run was placed on the commit gate 3 times. Across that
window 2 measuring instruments written earlier the same day were found to be
wrong, a regression guard committed hours earlier was found unable to judge the
repairs it was written for, and a pre-board predictor was found blind to an
entire class of staged file. None was found by reading code. Each was found by
executing something, or by a second independent route disagreeing with the
first.

The board's own figures: the 1st attempt refused after **2930.35 s = 48 min
50 s** with `1 failed, 5489 passed, 22 skipped, 2 xfailed`. The 2nd refused in
**36 lines**, before the board, on the note-lint ratchet. The 3rd is running.

## 1. The pre-board predictor could not see documents, entry B210

`scripts/which_guards_does_this_commit_risk_2026-11-22.py` derives which guards
a staged diff risks and runs only those, so a refusal is found in minutes
rather than after a full board. Its filter, `behaviour_changing`, read:

```python
p.startswith(("scripts/", "hooks/", "bench/")) and p.endswith(".py")
```

`experimental_notes/RUNWAY_to_BR2_2026-08-18.md` fails both conditions, so no
guard naming a document could ever be selected. The pre-board check passed
**1619 tests, 0 failures**, and the board then refused on
`bench/tests/test_r1_has_a_position_on_the_runway_2026-11-01.py::test_the_citation_prefix_is_byte_stable`,
a guard that sits on the gate's `GUARDS` list and names that document in a
`git show` argument.

This is the 4th named blind spot in that predictor and the first true **by
construction** rather than by a matching accident. The earlier 3 were an
ignored path, a guard whose subject is a set naming no member, and a guard
whose trigger is time.

### The measurement that justified widening it

The exclusion was deliberate. Its docstring said data and notes are named by
about 100 guards each and that admitting them "is the board with extra steps".
That counted the union of all guards naming them, **before this script grew the
DECIDING/ADVISORY split its own header describes**. Measured on the batch-3
diff before anything was changed: 6 non-`.py` staged files are named by **62
guards, of which 34 are on the gate**. The gate intersection is already applied
downstream, so the deciding set rises 34 to 64 and the pre-board cost 348 s to
519 s. Against an expected **1.916667 boards per landed batch** that is 0.24 of
a board to avoid a whole board.

### A discriminator proposed and measured as useless

The narrower idea was to count a document's guards only where the path appears
in a code string rather than a comment or docstring. Checked with an `ast` walk
that strips docstrings: **62 guards either way.** Per file it moves a little,
the task list 40 to 38 and the runway 6 to 5, but the union is identical. It was
dropped rather than built, and is recorded so it is not proposed again.

### The subject defect was also mine, and its remedy was in the file

The failing guard freezes lines 1 to 849 of the runway byte-for-byte, because 5
live line citations point into that region from
`experimental_notes/Research_FULL_RECORD_2026-09-09.md`, a verbatim panel
transcript that may not be edited to follow a shift, while
`bench/tests/test_line_citations_resolve_2026-09-01.py` checks only that a
cited line is in range. A supersession notice was inserted at line 11 and 6
table cells changed at line 313; **both hunks sit inside the frozen prefix**.

Line 932 of that same document records that an earlier session made the
identical mistake: "This block was first written at the head of the file and
`test_the_citation_prefix_is_byte_stable` refused the commit". It states the
convention, append at the foot and never insert above, and notes that STAGE 0C
sits at line 718 for the same reason. The remedy was written in the file being
edited and was not read. Both hunks are now a correction block at the foot and
the prefix is byte-identical.

### What the enlarged check caught immediately

**13 failures and 3 errors in 441.06 s**, all from 1 root cause: entry B210 had
no ticket identifier, so `scripts/morning_report_build_2026-10-12.py` refused
with exit 3, and because every decision-surface checker runs that generator the
failure presented as batch-wide. Raising the ticket through
`scripts/harvest_tickets_2026-10-17.py --sources task_list` and adding authored
detail to `experimental_notes/data/morning_report_decisions.json` took all 7
surfaces to REACHED and returned **102 passed** across the 7 affected files.

An error was made and corrected in that diagnosis: surfaces 4 and 5 were first
called batch-wide and pre-existing, because the reference entry B87 failed them
too. B87 failed through the same shared generator. One cause, not two.

## 2. `test_the_cy_refusal_budget_binds_2026-11-22.py` could not judge its own repair, entry B209

`bench/tests/test_the_cy_refusal_budget_binds_2026-11-22.py` was committed
before its repair, deliberately, and its docstring claimed it asserts the property rather than which key is used, "so whichever of B209's 2 options is taken,
this file judges it".

That is false. A key for the refusal counter must meet 3 conditions:

1. **Stable** across repeated polls of the same activity, or the refusal count cannot climb past 1.
2. **Distinct** enough that a budget exhausted once does not silence the gate
   for ever.
3. **Computable without reading the run**, since unwatched runs are the only
   ones needing protection.

All 5 of the guard's tests assert condition 1. Conditions 2 and 3 are asserted
by nothing. Driving the real hook with `CDSFL_CY_STATE` redirected to a
temporary path, candidate (a), keying on the session identifier alone, produces
**[1, 2, 3, 4, 5]** over its first 5 calls and **[63, 64, 65]** over its last 3
of 65, with `spend`'s only reset path, `if st.get("key") != key`, unable ever
to fire for a constant key. So (a) turns both strict `xfail` cases green, the
markers come off, the file reports a successful repair, and the session is
silenced permanently after the 61st refusal.

### The real structure of the defect

Driving it produced a sharper account than the entry records. **The churn is
simultaneously the defect and the safeguard's only reset mechanism.** Condition
2 holds today, and holds by means of the key changing, which is the behaviour
that breaks condition 1. So a repair must supply a new reset path and not
merely hold the key still. Candidate (a) does 1 of those 2 jobs and destroys
the other. A contiguous-activity epoch, where the count resets to 0 when the live set empties, addresses both by design; it is untested and goes to the panel.

The state is a single slot, `{"key": ..., "n": ...}`, so a per-run budget is
impossible by construction. That independently confirms the budget is
session-level, and that an earlier objection to candidate (a) on per-run
fairness grounds measured the wrong requirement.

### A second consequence, not in the entry

Every refused stop re-injects the same context: 1004 characters of
hard-constraint block, 1365 of roster, about 700 of goal block and 1180 of
refusal message, **4249 characters or about 1062 tokens per refusal**. `MAX_REFUSALS`, declared as 60, is what would cap that cost; with the counter resetting,
the number of refusals is governed by the run's duration instead, so the cost
has no upper bound. Observed across this batch: 7 refusals, counter sequence
**[1, 1, 2, 3, 1, 1, 1]**, peak 3, where a working counter reads 7.

That also corrects a stale figure in the project's own instructions, which pin
the roster injection at about 2809 characters. Executed,
`scripts/task_list_markers.py:open_roster` returns **1365**. The 1-line-per-open-entry rule is confirmed, while the pinned number has moved by a factor
of 0.4859 because the open backlog fell to 24 entries.

## 3. The interval routine failed twice, and cross-routing caught both

Computing a Clopper-Pearson interval by exact binomial tails as a second route
to `proportion_confint(k, n, method="beta")`:

- **Failure 1.** The lower bound solved `cdf(k-1, p) = 0.025` and the upper
  `cdf(k, p) = 0.975`; the correct equations are `1 - alpha/2` and `alpha/2`.
  Correct equations attached to opposite tails returned the mirror image,
  **[0.805880, 0.194120]** against statsmodels' [0.067586, 0.932414]. An
  inverted interval, printed.
- **Failure 2.** With the equations fixed and `assert lo <= hi` added, the
  upper bound returned **1.061982**, which is not a probability. `mp.findroot`
  is unconstrained and converged outside the domain. **The new assertion passed
  while the interval was still invalid.**

The repair is to constrain the solver: bisect on an explicit [0, 1] bracket,
assert a sign change at the ends before solving, and assert
`0 <= lo <= hi <= 1` after. Both routes then agree to **1.388e-17** at 2 of 4
and **1.110e-16** at 44 of 92 and 160 of 266, independently reproducing the
gate's pinned refusal rate [0.372970, 0.584990] and the hash chain's
[0.539926, 0.660794].

Neither failure was visible from inside the instrument that produced it. The
only reason either was examined is that statsmodels disagreed, by 0.74 and then
by 0.13. A single-route verdict would have published an inverted interval.

## 4. A figure the project had never pinned

The pinned cost figures give a board's mean duration, 1876.858696 s or 31.28
min over 92 boards, and the gate's refusal rate, 44 of 92 or 0.478261, Wilson
[0.379121, 0.579143]. Neither is the figure a plan needs. Expected boards to
land 1 batch is **1.916667** by closed form and **1.915960** over 400,000 NumPy
draws, agreeing to 0.000707; propagated from the Wilson bounds that is
[1.610621, 2.376104] boards, or **60.0 min per landed batch, interval
[50.4, 74.3]**.

The stated limit cuts against the model: boards are not independent, since a
refusal is diagnosed and repaired before the next attempt, so the geometric
form overstates the tail. It is a planning multiplier, not a distribution.

## 5. A correction stopped by its own falsifier

A suspicion arose that the turn hook over-reports what the founder personally
owes, since 1 of the 8 entries it names, B94, already carries a ruling dated
2026-11-08. A documentation repair was drafted and a falsifying condition
written down: that the tail's "2 separable things" might name a different pair
from the header's "both halves".

It does. The header's pair is what `v_bar` measures and the 4 sibling runners;
the tail's pair is whether a mean of severity is admissible and 4 formulas
computing 1 name. **B94 is correctly classified, the count of 8 is right, and
the repair would have removed a decision that genuinely awaits an answer.** It
was not applied.

## What is still open

- The free-seat panel round on batches 2 and 3. The brief validates at exit 0
  with all 8 required sections and 8 declared figures re-executed.
- B209's repair, deliberately withheld: it changes when a gate refuses.
- 2 tests for B209's condition 2, drafted and verified to pass today and to go
  red under candidate (a). A test for condition 3 cannot be written until
  `refusal_key()` is extracted from `main()`, which is part of the repair.
- Whether `test_the_citation_prefix_is_byte_stable` should be relaxed to permit in-place
  correction of stale claims. It is stricter than the citations require: they
  need no line shift and unchanged content at cited lines, while the guard
  forbids any byte change in lines 1 to 849. A reader starting at the top still
  meets the stale claim first.

Written under CDSFL note standard v1.9 (1 November 2026).
