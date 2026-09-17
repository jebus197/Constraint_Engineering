# Sidecar correction to BRIEF.md — the brief itself carried a wrong figure

Filed 2026-09-10 04:05 BST. **The brief is NOT edited.** `bench/logs/` is archival: it records what
the panel was actually given, and a brief rewritten after the fact would make the seats' findings
unreadable. Corrections are filed beside it.

## The defect

Section 2 of `BRIEF.md` states: *"The series is `[11, 4, 2, 3, 6, 2, 3, 2, 9]` and `gamma` is 0.451"*.

**gamma is 0.415413.** Measured with `bench.reference_runner_v3._estimate_gamma`, cross-checked
against an independent numpy `polyfit` of the same log-log regression, agreeing to 1e-9.

Both seats found this independently and both raised it as their strongest disagreement with the
brief. fable: *"A panel brief reviewing '9 figures that were wrong' fed its reviewers a 10th unbacked
figure."*

## Why it is not a rounding quibble

`GAMMA_BANDS` at `bench/reference_runner_v3.py:2636` places the boundary at 0.45:

    (0.45, inf, 'Strong depletion — confirms state-based closure')
    (0.30, 0.45, 'Moderate depletion — consistent with PoC convergence')

0.451 falls in the band ABOVE the true value's band. The brief handed the panel a figure that
upgrades the convergence evidence by one band, in a brief whose subject is 9 figures that were wrong,
and asked the seats to judge whether the process producing figures is sound.

## Where it came from — measured, not guessed

fable identified it as the stale 8-pass value and that is nearly right. Measured:

| series | gamma | band |
|---|---|---|
| 8 passes `[11,4,2,3,6,2,3,2]` | **0.453703** | Strong depletion |
| 9 passes `[11,4,2,3,6,2,3,2,9]` | **0.415413** | Moderate depletion |
| 10 passes `[11,4,2,3,6,2,3,2,9,10]` | **0.365597** | Moderate depletion |

So the figure carried forward was the 8-pass value, whose band IS "Strong depletion" — and it was
then garbled from 0.4537 to 0.451 in prose. `grep` for `0.451` across the task list, the series JSON,
the cycle script and every committed note returns nothing outside this log directory. **The artefacts
were clean; only the prose was wrong**, which is `measured-rate-travels-with-its-script` failing at
the one place the rule does not have a mechanical guard: a number typed into a brief.

## What follows

The seats' findings stand unaffected: neither depended on the brief's figure, both re-derived gamma
themselves before using it, and both said so. That is the two-sided value of requiring seats to
execute rather than read — the brief could not propagate its own error into their answers.

Recorded as task V6 in `experimental_notes/CDSFL_MASTER_TASK_LIST.md`.
