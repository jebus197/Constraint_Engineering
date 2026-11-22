# The first panel round under the autonomy handover, and every seat was wrong about something

22 November 2026, 01:45 GMT

## Summary

A 2-seat free panel reviewed the 6 repairs making up the first batch of work
done under the founder's autonomy handover of 21 November 2026. The round found
1 genuine defect that had survived the author's own falsification, and the
author found 3 errors in the panel's account of it. Both halves are recorded,
because the value of the round lies in the disagreement rather than in a verdict.

The handover's standing instruction is that a panel's proposals are TESTED
before they are adopted. Under the project's own rule that no model vote counts
as evidence, a seat's verdict is a hypothesis and nothing more. Every claim
below was re-run locally before anything was changed.

## What was dispatched

The round is recorded at `bench/logs/batch1_autonomy_2026-11-22`. 2 seats
answered: `cc2`, Claude Opus 4.7 through the command-line interface, in 1026.1
seconds across 63 tool calls; and `fable`, Fable 5.1 by the same route, in
1121.3 seconds across 91 tool calls. Both returned a complete reply.

The brief asked whether each of 6 repairs holds on its own evidence, and whether
any pair needs composing in the founder's sense of that word, which requires a
measurement showing the composed fix dominates either part alone.

## The seats disagreed, and the disagreement was the finding

On 4 of the 6 repairs the seats agreed. On 2 they did not.

| repair | cc2 | fable |
|---|---|---|
| B205(c), the Stop gate's stand-down predicate | FAILS | HOLDS |
| B182, the budget gate's heavy-work detector | FAILS as a closure claim | HOLDS |

Where 2 independent readers of the same artefact return opposite verdicts, at
most 1 can be right and both may be wrong. Each claim was therefore reproduced
rather than adjudicated.

## The defect that was real

Seat cc2 reported that `a_commit_board_is_running` in `scripts/blocker_triage.py`
had lost the fail-safe direction its own docstring promises. That docstring
reads: any failure of the predicate returns the empty string, so a fault costs
the protection and never the triage.

The predicate's exclusions are all questions put to the `ps` command. The
ancestry walk asks for a parent process; the shell discriminator asks for a
command name. Both are documented to fail toward DETECTING a run, which is the
correct direction for `cy_monitor_gate` which also uses them, where the cost of
missing a run is an unobserved 3-hour measurement. It is the wrong direction
here. Where `ps` cannot answer while `pgrep` still can, both exclusions pass
everything through and the predicate returns a process identifier.

This is above threshold because the cost is not confined to the triage. The Stop
gate in `hooks/work_not_narrate.py` stands its entire mechanism down whenever
this predicate is truthy. An over-report therefore switches off the gate that
compels continued work, which is the disabling of a feature that the project's
additive standard forbids.

Producer: `scripts/does_the_board_detector_hold_its_polarity_2026-11-22.py`.

## The 3 errors in the report of it

**The attribution was wrong.** The seat presented the defect as introduced by
the B205(c) repair, calling it a repair that achieved the opposite of its stated
purpose. Running the same experiment against the copy of the function at the
previous commit gives identical results in both arms, so the defect predates
that repair. The ancestry exclusion B205(c) added can only make the predicate
return the empty string more often, never less.

**One of the 2 reported arms does not reproduce.** The seat reported that a
shell was detected as a running board even while `ps` was answering normally.
The command used to plant that shell was a single command, which the shell
replaces itself with rather than waiting on, so what the probe actually
tested was `sleep` and not a shell at all. The same artefact was reproduced here before the
probe was corrected. With a plant that stays a shell, that arm returns the empty
string and the discriminator is sound.

**A factual claim was contradicted by the other seat and settled by counting.**
On whether the project writes `rerun` without a hyphen, cc2 reported 398
occurrences and fable reported 0, concluding the risk was unexercised. Counted
directly across the project's own markdown, Python and text files: 444
unhyphenated against 7,162 hyphenated, an unhyphenated share of 0.058375 with a
Wilson interval of [0.053326, 0.063870] and a Clopper-Pearson interval of
[0.053210, 0.063881] on 2 agreeing routes. cc2 was substantially right that the
form occurs; fable was right that the hyphenated form dominates. Neither had it
whole. The word-boundary behaviour explains the split: a hyphen is a word
boundary, so a pattern matching `run` catches `re-run` and catches nothing
inside `rerun`.

## What the other seat found that the first did not

Seat fable returned 2 findings about the EVIDENCE for the repairs rather than
about the repairs themselves, and both were verified and acted on.

**A figure with no producer.** A comment in `hooks/work_not_narrate.py` declared
that a predicate had been driven over 5 cases and was correct in 5 of 5. No
script reproduced it. The project's rule that a measured figure travels with its
script binds a code comment exactly as it binds a note, and a number existing
only as prose is a claim about evidence rather than evidence. The producer now
exists at `scripts/the_commit_flag_asks_git_2026-11-22.py` and reports 6 of 6,
the 6th case being the seat's own addition, with the never-claim-a-commit
property counted separately from the hit rate.

**A guard that passed or failed by accident of timing.** The parking tests in
`test_blocker_triage_2026-09-10.py` call a function that refuses before any
write while a commit board is running. The product carries an environment seam
built for exactly this situation, and the string naming it appeared 0 times in
the test file. On the day of the round all 5 of those tests failed while a
verification run was genuinely alive, and the code they exercise was healthy
throughout. A red result implicating healthy code is a false record. The seam is
now used, scoped to the parking classes so that the tests of the detector itself
continue to observe the real machine.

## What changed as a result

The polarity is restored by a separate probe asking whether `ps` can answer at
all, which is the cheapest question it can be asked and whose answer is known in
advance, so a failure is about `ps` rather than about any particular process.
Where it cannot answer, the predicate returns the empty string as documented.

The budget gate's vocabulary was widened to admit the bare noun `board`, the
path `bench/tests` without a trailing slash, the noun `guards`, and the
unhyphenated `rerun`. 2 of the phrasings it previously missed are sentences
this project writes at itself: the gate's own refusal message, and section 2 of
the brief dispatched to this very panel. Both are instructions of precisely the
shape the gate exists to refuse, and both passed through it.

Measured in 3 directions before and after, because widening a predicate that
ACCEPTS is a tightening and every instruction newly caught risks a prohibition
newly refused. Instructions that should be refused: 1 of 10 before, 10 of 10
after. Prohibitions that must not be refused: 6 of 6 before and after.
Descriptive prose that must not be refused: 4 of 4 before and after. The
widening is therefore strictly dominant on the named property at no cost to
either safety direction. Producer:
`scripts/the_budget_gates_vocabulary_2026-11-22.py`.

## Composability

No pair of the 6 repairs warrants composing, and for the 1 pair the brief
predicted would tempt a claim the refusal is a measurement rather than a
judgement.

B205(c) and B180 both concern a gate noticing a long-running process, and they
already share 2 pieces of code by duplication. Unifying them is the obvious
composed fix. It cannot work, because the 2 callers require opposite values from
the same helper under the same condition. Measured directly: with `ps` denied,
`cy_monitor_gate`'s process finder still returns the planted identifier, which
is correct for it, while the triage must return the empty string. A single
shared helper cannot satisfy both. The single fix, local to the file whose
polarity is violated, strictly dominates the composed one on the stated
property.

## Status of the repairs

All 6 repairs are BUILT and TESTED. B205, B204, B182 and B180 carry executing
guards; the 2 raised by this round carry new ones at
`test_the_board_detector_fails_toward_writing_2026-11-22.py` and
`test_todays_producers_run_2026-11-22.py`. The board detector guard was proven
able to fail: with the repair reversed it goes red on 2 of its 7 tests, and the
file is restored by the harness that reverses it.

A single pre-existing failure remains in `test_blocker_triage_2026-09-10.py`,
the labelled-set case recorded as the documented single miss in that instrument's
9-of-10 accuracy. It is untouched by this work.

Written under CDSFL note standard v1.9 (1 November 2026).
