# The programme of study for the next simulated run

2026-09-17, 00:26 BST, Europe/London.

## Why This Run Is Being Made

The founder's instruction of 2026-09-16, verbatim: "The purpose of the next simulated run is to enact a study of all recent fixes gathered over the last 10-12 days and to see exactly how well, or otherwise they perform." The run is not a fresh experiment. It is a test of the repairs, to see how they behave together rather than one at a time.

## What Was Repaired, And How Much Of It There Is

Between 2026-09-03 and 2026-09-17 the repository took 323 commits. 84 entries on the master task list are marked DONE, and 151 new test files were added, 1 or more per repair. Grouped by the part of the harness they guard: 27 cover the falsifier and admissibility gates, 17 the panel and its brief, 15 the records and the note linter, 11 the harness guards, 6 the runner and its convergence machinery, and 75 sit outside those groups.

Those 151 tests already prove each repair in isolation. What no test can show is whether the repairs interfere with one another in a live run, which is what this study is for.

## What The Run Must Measure

1. Falsifier supply. The 2026-09-08 run halted because 5 of 14 critical findings arrived with no runnable falsifier. The intake parser was widened afterwards. MEASURE: the share of critical findings arriving with a falsifier the runner can execute, against the 9 of 14 that did last time.

2. The exhausted-round valve. It could never open, because its threshold of 8 equalled the round limit of 8. Set to 6 on the founder's ruling of 2026-09-16. MEASURE: how many findings reach the valve, in which round, and whether any arm still ends in budget exhaustion rather than one of its 2 pre-registered outcomes.

3. The drift detector. Wired on 2026-09-16 after having 0 production callers. For each flaw class it compares the share of findings this run confirmed against the share memory predicted, and accumulates the gap. MEASURE: the largest excursion per flaw class against the threshold of 2.0. Replay of 3 archived runs gave 0.5595, so a live figure near or above 2.0 would mean the threshold is wrong, and a figure far below means it is inert.

4. Seat independence. Every panel seat used to share 1 writable sandbox. Each now gets its own. MEASURE: whether any seat's working files are touched by another, and whether the containment alarm fires with an attributable cause.

5. The admissibility gate on prose. A gap remains: the gate classifies a whole target file rather than each finding inside it. NOTE AND CAUTION: all 3 arms target a Python module, so this gap cannot be exercised by this run. It is listed so that a reader does not mistake silence for a passing result.

6. The panel brief format. Every brief must now require the seat to run the harness, name a mathematical instrument, produce a tested fix rather than a finding, and state what would refute it. MEASURE: whether seats comply, and whether their fixes survive their own falsifiers.

7. Record integrity. The note linter, the DONE-evidence guard and the citation repairs all changed. MEASURE: whether any record written during the run fails its own guard.

## The Three Arms

All 3 target the same file, the registry engine, for 8 rounds, with routing, the falsifier gate and the admissibility gate on, and the hardened gate, merge arbitration and immune memory off.

1. Multi-model panel: 5 seats, CC2, Codex, Gemini, DeepSeek and ChatGPT.
2. Single model with agents: 1 seat, CC2.
3. Seat contrast diversity: 2 seats, Codex and ChatGPT.

The contrast between the first 2 is the question the founder has asked repeatedly: whether several distinct architectures beat 1 architecture wearing several labels.

## What Would Falsify The Claim That The Repairs Work

The claim is that the repairs improve the run rather than merely passing their own tests. It is falsified if any of these occurs. Falsifier supply is no better than the 2026-09-08 run. The valve still never opens, or opens so often that findings bypass review. The drift detector fires on every flaw class, which would mean its threshold is miscalibrated rather than informative. A seat's files are touched by another seat. Any arm ends outside its pre-registered outcomes.

## When To Stop

The run stops on its own terms: convergence, the irreducible-queue alarm, or the round limit. The study stops when every measurement above has a value, or a named reason why it could not be taken. A measurement that could not be taken is reported as such and never as a pass.

## What Is Deliberately Not In This Run

The 4 parked defects in how the CDSFL system prompt is assembled, including the one where the full directive of 27,803 characters is always replaced by a rendering of roughly 2,500. The founder ruled on 2026-09-16 that these fold into the refactor for the revised mathematical model, because both change the text sent to models and doing it twice would pay the replay cost twice. They are listed in the programme so the refactor inherits them.

Experiment 53, the zero-plant control, is deferred until after this run by the founder's ruling. The discrimination control block is to be armed and tested in this run.

Written under CDSFL note standard v1.7 (26 August 2026).
