# Stage 1 Accounting Repairs, and a Correction to What Was Reported About Them — plain-English companion

**18 August 2026, 12:28 BST.** Mirrors the TTS file of the same name. Technical version with file and line references: `Stage1_Accounting_Repairs_2026-08-18.md`.


## SUMMARY


Two repairs from Stage 1 of the runway are committed and tested, as commit
dcbc91b. The test suite stands at 3573 passed, 14 skipped, 0 failed.

One of the two was described in the commit message and in the session report as
fixing the input to the convergence gate. Measurement carried out afterwards
refutes that description. The gate's input was already correct, and had been all
along. The repair is still a valid repair, but it corrects a different quantity,
so what it means for the project is different from what was reported.

No experiment is invalidated. No convergence verdict changes. The correction is
about what a repair does, not about whether past results hold.



## THE TWO COUNTERS, BECAUSE THE WHOLE CORRECTION TURNS ON TELLING THEM APART


The reference runner keeps two separate records of how many findings each round
contributed. They look alike and they are not the same object.

The first is called novelty counts. It is a plain running list, one number per
round, appended to as the run proceeds. Once a number is written into it, it
stays written unless something explicitly rewrites it.

The second is called the settled novelty series. It is not a stored list at all.
It is a function that rebuilds the whole per round shape from the finding
registry, from scratch, every single time it is called. Because it rebuilds from
the registry, it always sees each finding's current status.

That difference is the entire story below.



## THE DEFECT THAT WAS FOUND, WHICH IS REAL


Novelty counts was corrected in one position only. At the end of each round the
runner overwrote the last entry in the list with a post deduplication count. It
never went back and revised any earlier entry.

The consequence is straightforward. A finding registered in round 3, and later
discovered in round 7 to be a duplicate of something already known, stayed
counted as a genuine new discovery in round 3 permanently. The round it arrived
in kept crediting it long after the project knew it was not new.

Measured on the archive: of 287 entries marked MERGED that carry round data, 236
of them, which is 82 percent, were merged in a later round than the one they
opened in. So the single position correction reached 18 percent of merges and
missed the rest.

The project specification is explicit that the decay curve input must be
post deduplication, and says in terms that using raw findings inflates the series
with rediscoveries and cross model echoes. A series corrected in one position is
post deduplication in one round and pre deduplication in every other. The repair
recomputes the whole series. That is correct and it is committed.



## THE CORRECTION, WHICH CHANGES WHAT THE REPAIR MEANS


The repair was reported as fixing the input to the two sided convergence gate.
It does not, because the gate does not read novelty counts.

The gate function calls the settled novelty series directly and passes its result
to the gamma estimator. It never touches novelty counts at any point. And the
settled novelty series, because it rebuilds from the registry each time, already
excluded every MERGED, DUPLICATE, UNCONFIRMED and REFUTED entry in every round,
not merely in the last one. It has always done this.

The evidence is direct rather than inferred. The runner's own settled novelty
series was run against 11 archived experiment reports and its output fed to the
runner's own gamma estimator. The result reproduces the archived gamma critical
history exactly in 9 of the 11, including experiments 43, 44, 45, 46, 48 and 49.
The 2 that do not match are runs where the round bound passed in differs from the
one the run used, not runs where the accounting differs.

So the gate was already reading a fully post deduplication series. The
specification requirement was already met on the gate path, and had been met
before this week's work started.



## WHAT THE REPAIR ACTUALLY CORRECTS


Novelty counts feeds two consumers, and neither is the gate.

The first is rho, the discovery efficiency measure: novel findings divided by
raw findings, averaged over a rolling window of the last 3 rounds. When earlier
rounds keep crediting findings later found to be duplicates, rho reads higher
than the run deserved.

The second is the endocrine module, which receives the novelty counts list each
round as one of its inputs.

Worked example, experiment 46. The archived rho average at the close of the run
was 0.3009. Recomputed with every round post deduplication, using the same raw
counts the run itself recorded, it is 0.2176. The configured churn threshold is
0.25. The archived figure sits above that threshold and the corrected figure sits
below it.

Measured across the archive, rho moves in 5 of the runs examined and is unchanged
in the rest. Where it moves it falls, which is the expected direction, because
the correction only ever removes findings from a round and never adds any.



## EXPERIMENT 46 DOES NOT NEED THE ATTENTION IT WAS GIVEN


The session report singled out experiment 46 as needing attention. Two reasons
were given. The first was that it converged with gamma critical at 0.3357 against
a threshold of 0.30, a margin of only 0.036. The second was that its gamma moved
from 0.2910 to 0.3756 under the correction.

The first reason is true and stands. The margin is genuinely the narrowest in the
arc.

The second reason is wrong. Experiment 46's gamma critical series is 4, 2, 3, 2,
1, 0 before the correction and 4, 2, 3, 2, 1, 0 after it. Identical, because
every one of those entries was already settled. The number the gate reads does
not move at all. The figures 0.2910 and 0.3756 came from the all findings series,
which the gate does not read and which does not decide convergence.

Across all 8 experiments in the arc, no run changes its convergence verdict under
this repair.



## A NEW FINDING THAT CAME OUT OF THE CHECK


The churn detector has a configured earliest round of 12. It cannot raise a flag
before then, whatever rho does.

Of experiments 44 through 49, only experiment 44 ever reaches round 12. It ran 13
rounds. Experiment 45 ran 4, experiment 46 ran 6, experiment 47 recorded 9,
experiment 48 ran 6 and experiment 49 ran 7.

So for 5 of the 6 experiments in the current arc, the churn detector was
structurally unable to fire regardless of what discovery efficiency did. This is
OBSERVED in the archived reports, not hypothesised. It is not currently on the
runway and it should be, because a detector that cannot fire on the runs actually
being conducted is not providing the cover it appears to provide.



## AN ANOMALY IN EXPERIMENT 47 THAT IS NOT YET EXPLAINED


Experiment 47's report records 9 rounds. Its finding registry carries entries
whose opening round runs as high as 13. The two do not agree.

This matters immediately, because an earlier draft of the rho measurement showed
experiment 47 as the one run where rho rose rather than fell, by 0.2153. That
rise is an artefact of comparing a 9 round window against a 14 round registry. It
is not a measured effect and it is withdrawn.

The mismatch itself is an OBSERVED anomaly in the archive and belongs to the full
replay, which is the next Stage 1 item.



## THE SECOND REPAIR, THE STARVATION FLOOR, STANDS AS REPORTED


The health monitor named regulatory T v2 watches for the immune pipeline removing
too large a share of what it is given. It carried a deliberate carve out: when
every removal was a duplicate, do not raise the alarm.

The reasoning behind that carve out was sound as far as it went. A high duplicate
rate genuinely is a sign of depletion, and depletion is what the project wants to
observe near convergence, not a fault to be flagged.

The carve out had no floor beneath it. When the pipeline rejects absolutely
everything it is handed, that condition also satisfies the carve out, and the
monitor reported health.

OBSERVED, not hypothesised: every modern run records a rejection rate of 1.0 from
round 1 onward. Experiment 47 records it in 8 of 8 rounds. The monitor did not
fire once in any of them.

Status of this repair: BUILT in the immune agents module, TESTED at 8 passing
tests of which 4 were verified to fail against the pre repair code, COMMITTED as
dcbc91b, and ENABLED, because the monitor is not gated behind any configuration
flag and therefore runs in every experiment.

The first version of the floor was written too broadly. It intercepted genuinely
rejected findings as well as the starvation case, and an existing test caught it.
The floor was narrowed to the exact case the carve out had been hiding.



## WHAT REMAINS IN STAGE 1


Item 1.6, MERGED semantics. This is a decision, not a repair, and it is the
founder's.

When the runner marks a finding MERGED it records a pointer from the old
identifier to the canonical one and stops counting the old one. Every round, the
models are told in their prompt that MERGED means the finding was folded into the
canonical entry. Nothing is folded. The severity does not carry across. The tool
verdicts do not carry across. The supporting evidence does not carry across. The
fact that a second model found the same defect independently does not carry
across.

Measured: the alias map is a strict one to one mapping in all 28 registries in the
archive. No canonical entry has ever gained a second alias. If merging were
folding, entries would accumulate aliases. None ever has.

The two options are these. Either make MERGED genuinely fold, so that a duplicate
raises the standing of the entry it duplicates, which is what independent
corroboration ought to mean in a falsification framework. Or leave the mechanism
as it is and stop describing it to the models as folding, since it is a delete
with a pointer.

Item 1.7, the full replay of experiments 44 through 49 through the repaired
accounting. Zero dispatch cost. It now has more to measure than it did this
morning: rho moves and gamma does not, the experiment 47 round mismatch needs
resolving, and the churn detector finding needs adding.



## STATUS


Stage 1 stands at 5 of 7 items complete. Items 1.2, 1.3 and 1.4, covering alias
key normalisation and the merge integrity guards, landed earlier as commit
e1aca4f. Items 1.1 and 1.5 landed as commit dcbc91b. Items 1.6 and 1.7 remain,
and 1.6 is blocked on a founder decision.

Stage 2, which is the behavioural repair to the immune pipeline's duplicate auto
reject, requires one live experiment run and has not started.


---

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
