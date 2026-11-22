# The trim could not reach the section that grows

*21 November 2026, 14:35 GMT*

## Summary

3 repairs were built, tested and mutation-checked against the CDSFL save-and-commit path on 21 November 2026, on the founder's instruction, and are committed by the change that carries this note. **The first commit board refused all 3, and section 4 below records why: 10 of its 18 failing guards were broken by this work's own change to the commit hook.** The first is the one that carried a misdiagnosis: the project's memory index had 14 characters of headroom before the save tool would refuse a save, and the founder's position was that the index should trim itself automatically so that it never fills. **His account of the design was correct and the fault was not what the prior report described.** The automatic trim has existed since 3 October 2026 and runs on every save. What no earlier report stated is the part of the index it can reach.

The second repair makes the commit gate's longest phase observable while it runs, without the gate losing the ability to refuse. The third gives the founder's own copy of the decisions file a fact it had never carried: whether the repair each decision asks about has already been built.

## 1. The memory index: the mechanism was automatic and its scope was the defect

The memory index is `MEMORY.md` in the project's persistent-memory folder. The session loader reads at most 25,000 characters of it, and past that limit it silently drops the newest entries, which are the ones a recovering session needs most. The save tool therefore refuses a save at 98 per cent of that limit, which is 24,500 characters.

3 relief mechanisms already ran automatically inside the save tool's pre-flight pass, in this order: ageing entries out into an archive, grouping entries that share a date onto one line, and grouping feedback entries under the bold sub-headings the index already carries. On 21 November 2026 **all 3 freed 0 characters**, each with its own stated reason, while the index stood at 24,486 characters against the 24,500 refusal line.

The reason is scope, measured by `scripts/the_index_can_never_stop_filling_2026-11-21.py`:

| section of the index | characters | share of the index |
|---|---|---|
| Feedback, which holds the standing lessons | 19,850 | 0.810667, Wilson [0.805712, 0.815526] |
| Project State, the only section that ages | 1,566 | 0.063955, Wilson [0.060958, 0.067088] |
| every other section | 3,070 | 0.125378 |

Ageing is confined to Project State by a named constant. The exclusion of the Feedback section is deliberate and well reasoned: a standing lesson does not become false by being old, and an existing guard, `test_standing_feedback_is_NEVER_moved_however_old`, pins that it is never aged out. So the growth sits in the one section no mechanism was permitted to touch.

### Why a larger trim could not have answered the instruction

The instruction was that the index should never become full. That is a claim about every future day, and it was tested as one. With the index growing at a positive rate, the constraint solver z3 was asked whether any one-off relief R satisfies `for all t >= 0, total - R + rate * t <= refuse`. The answer is **UNSAT**: no finite one-off relief satisfies it. SymPy solving the same inequality symbolically agrees and quantifies it — emptying the **entire** index buys **38.38 days** at the measured growth rate of **638.3173 characters a day**, itself derived from 5.6190 new dated memory files a day over the trailing 21 days at 113.5988 characters a pointer.

The same query in capped form is **SAT**, and the time variable drops out of it entirely.

The result was then checked on a third, independent engine as the secondary falsifier, the open-source tools remaining primary. Computed with Wolfram Language: `Resolve[Exists[{R}, ...]]` returns **False** for the one-off relief and **True** for the capped form, matching z3's unsat and sat exactly; the deadline after emptying the whole index comes back as 38.38216656647592 days against SymPy's 38.38216655129353, agreeing to 1.5 parts in 100,000,000; and the symbolic dominance gap reduces to `lo / (2 * rt)`, which is SymPy's result character for character. Values in this paragraph derived with Wolfram Language. The maximum sustainable budget for the Feedback section is 19,864 characters. So the 4th relief had to be a standing ceiling that re-asserts itself on every save, not a bigger trim.

### The eviction order, and why a composed rule was chosen

Under a standing ceiling with unbounded lesson growth, something must leave the loaded window each time something arrives. That loss is arithmetic, not a preference, and it is stated rather than glossed: an evicted pointer stays reachable, because it is written to a companion file that the index links to and that the recovery command reads in full, but it is no longer in the window injected on an ordinary turn.

2 candidate orders were measured against each other on a named property, which is the demonstration the project's composability standard requires before a composed rule may be recommended. The property is the number of days a 3-star lesson stays inside the loaded window.

| eviction rule | days a 3-star lesson stays loaded |
|---|---|
| age alone | 15.31 |
| salience alone | 8.25, after which no evictable mass remains at all |
| salience first, then age within a tier | **19.43** |

The composed rule dominates age alone by a factor of 1.2696 and salience alone by 2.3545. SymPy establishes that the dominance over age alone is unconditional rather than particular to this index: the difference reduces to `low / (2 * rate)`, which is positive whenever any lower-salience mass exists. Salience alone was refuted by its own measurement, because **102 of 172 pointers are already 3-star**, 0.593023 with Wilson [0.518351, 0.663631], so that tier cannot be protected indefinitely by excluding it.

### What was built

`relieve_memory_index_pressure` in the save tool, called from the same pre-flight pass as the 3 earlier reliefs and ordered last, so it only ever moves what the cheaper loss-free mechanisms could not free. It writes to `MEMORY_FEEDBACK_OVERFLOW.md`, deliberately not to the history archive: the archive holds entries that aged out of Project State and are no longer true of today, whereas a standing lesson pushed out of the window is still in force, and the companion file's own heading says so.

Status: **COMMITTED**. Evidence: `bench/tests/test_the_index_can_never_stop_filling_2026-11-21.py`, 30 tests; `scripts/the_index_relief_mutations_2026-11-21.py`, **11 of 11 mutations turning the guard red**.

### Two defects the falsification pass found in its own work

The pointer-conservation check **refused its own first run** and left the index untouched, which is the correct failure mode. Inserting a navigation link to the companion takes the pointer set from 201 to 202, and a set comparison reads an addition as a change. A pointer to a sibling file is navigation and not a lesson, so it is excluded from the set being conserved.

The mutation harness then found a **coverage gap rather than a weak mutation**. Breaking the branch that appends to an existing companion left the whole guard green, because every test began with no companion on disk and so exercised only the first-write branch. In live use the companion exists from the second save onward, so the branch no test reached is the branch that always runs. A test for the append path was added, and the mutation then turned the guard red.

## 2. The commit gate's longest phase can now be watched, and still refuses

The commit board runs 5,233 guard tests from one line of the pre-commit hook, 5,124 of them before the 4 guards written for this work were added to its list, and that line captured the whole output into a shell variable. A command substitution reveals nothing until it completes, so the longest phase of the board produced no observable output at all. The last 3 full boards spent 2555.93, 2524.70 and 2557.57 seconds in it. The founder's standing directive of 18 May 2026 is that a terminal must show the full current tail of any running process, and this line is what made that unsatisfiable. The save tool's side of the same chain had already been repaired on 17 November 2026, so the captured variable was the only remaining link.

**The obvious repair silently disables the gate, and that is the finding worth recording.** Piping the output through `tee` streams it correctly and destroys the verdict, because a POSIX shell reports the exit status of the last element of a pipeline, and `tee` succeeds whatever the test run did. Driven against real subprocesses in a real shell by `scripts/the_board_can_stream_without_losing_its_verdict_2026-11-21.py`, the `tee` form returned 0 on a tree rigged to exit 1 and 0 on another rigged to exit 2 — **0 of 3 exit codes kept**. A red board would have been recorded as passing and the commit would have gone through. The bash-only `PIPESTATUS` array is not a portable escape: it is 0-indexed in bash, spelled differently and 1-indexed in zsh, and the hook runs under `/bin/sh`. This project has already lost an exit code to exactly that difference twice, on 2 October 2026 and again on 21 November 2026.

3 forms were measured on 3 counts — exit-code fidelity, whether output appears before the child exits, and whether the captured text stays byte-identical, which matters because 6 downstream text searches in the hook read that variable. Exactly 1 form satisfied all 3: a log file with a background follower, which keeps the status in `$?` because no pipeline stands between the test run and the shell. It streams output 1.2 seconds before the child exits in the measurement, and on the real board a progress line arrives roughly every 35.75 seconds, inside the founder's 60-second monitoring cadence.

Unbuffered Python is load-bearing in that form. Redirected to a file, Python block-buffers its output in 8 kibibyte chunks, and the quiet progress format emits 1 character per test, so a 5,233-test board would surface its progress about once per 8,000 tests, which is to say never.

Status: **COMMITTED**. Evidence: `bench/tests/test_the_boards_guard_phase_streams_2026-11-21.py`, 15 tests which extract the hook's own shell block and run it against children rigged to pass, to fail, and to fail on standard error alone; `scripts/the_streaming_board_mutations_2026-11-21.py`, **6 of 6 mutations red**, including the `tee` form.

A guard that forbids the rejected form initially **failed against correct code**, because the hook's own explanatory comment names both forbidden spellings in order to explain why they are forbidden, and a whole-file scan read the explanation as the offence. The check now strips comments first. A detector must not be defeated by the documentation of what it detects.

## 3. The founder's copy of the decisions file now carries the entry's own status

The founder's Desktop copy of the decisions file was 8,482 bytes against the repository copy's 95,259 at the same filename, and carried none of the 4 premise reversals a blind free panel had found on 17 November 2026.

**The obvious reading of that is wrong, and acting on it would have reversed one of the founder's own rulings.** The index-only Desktop copy is the 11 November 2026 repair to his 8 November complaint that the full file, at over 22,000 words, is an almost impossible workload, and a guard named for that complaint pins it. Regenerating his copy at full length re-creates precisely what he objected to.

The defect is therefore not length. An index line carried what a decision **asks** and never what the entry's own record **says**, so an entry already built and running read identically to an entry awaiting a fresh ruling. Measured from the master task list's own markers on 21 November 2026: **34 of 49 open entries are built or better**, and **10 of the 21 awaiting the founder** are, which is 0.476190 with Wilson [0.283440, 0.676305]. 3 of the panel's 4 falsified-premise entries are among them. A ruling given without that fact answers a question that no longer exists.

Each index line now carries a short clause, derived rather than written, where the entry's record warrants it: that its premise has already been falsified, or that the work is already built, tested, committed or enabled, and that the decision is therefore to ratify or close rather than to rule. **10 of 21 lines** now carry it. The cost is 576 characters on a 9,061-character file and nothing is cut. The clause is composed once and rendered to both the spoken and the markdown surface, because the 2 are emitted in the same loop and a clause written into one of them only would make the two surfaces promise different things.

Status: **COMMITTED**. Evidence: `bench/tests/test_his_copy_carries_the_entrys_status_2026-11-21.py`; `scripts/the_status_flag_mutations_2026-11-21.py`, whose headline mutation is the length reversion, so the harness fails if a future change undoes the workload ruling.

## 4. The first commit board refused all 3, and 10 of its 18 failures were this work's own

The commit gate ran for 2663.27 seconds and refused. It reported 18 failing guards against 5,131 passing, and the refusal arrived as readable streamed text naming every failure, which is itself the repair in section 2 working: the same refusal on earlier boards reached the log as 33 bytes carrying no reasons.

**10 of the 18 were caused by the change in section 2, and the cause was a tracing failure rather than a defect in the fix.** The board's test phase had been a single shell line, and 5 separate instruments used that exact line as their anchor. The first of the 5 pins the interpreter and its flags, because the 2 searches that extract a failure's name and its assertion text depend on the quiet output format. The second uses the line as a position, to assert that the cheap note lint runs before the expensive board and that the lint block still refuses on exactly 3 conditions. The third lifts the line out of the hook and runs it against a deliberately failing tree, to prove a red board still produces an exit code other than 0. The fourth is a mutation harness that replaces the line with 5 broken forms and requires that third guard to refuse every one of them. 4 of the 5 were identified from the refusal text; the fifth was found only by searching the repository for the literal, which is the sixth recorded instance in this project of checking a count of instruments rather than the set of them.

**The fifth failure was invisible to the board that the guard's own assertion is about.** A guard dated 10 September 2026 pins the same command without its assignment prefix, a string 14 characters shorter, and a second guard's documentation had asserted for 12 days that the 2 pins were the same text. They never were. Because that file is not on the gate's own list of guards, the failure raised an uncaught exception rather than an assertion and the board reported 18 failures instead of 19. Run on its own it gives 1 failure against 31 passes. The gate's list reaches 317 of 946 test files in the repository, so 629 are reached only by a full suite run, which cannot gate a commit.

**The same pass found that the board had run none of this work's own 70 tests.** All 4 guards written for these repairs were absent from the gate's list. A census committed on 13 November 2026 measures exactly this gap against a rule requiring every guard written since 29 October 2026 to be on the list, and it returned 4 of 245 missing, a proportion of 0.016327 with a 95 per cent Wilson interval from 0.006367 to 0.041219 and a Clopper-Pearson interval from 0.004466 to 0.041272, each computed on 2 agreeing routes. All 4 were dated 21 November 2026. The gap had stood at 33 of 220 on 13 November, so it had been closed down to precisely the files this work added. Nothing refuses over that gap, and that is deliberate: the guard on the census checks that the census works and deliberately pins no figure, because closing the gap must turn it green rather than red. The 4 guards are now on the list, their cost measured first at 70 tests in 64.88 seconds, which is 2.44 per cent of a board. Whether the gap may be gated at all is recorded as entry B204, the census of guards missing from the commit gate that nothing enforces, and is the founder's to rule on, because a rule refusing growth would move the decision about how long every future board takes away from whoever writes the guard.

**A figure of this work's own was paired with the wrong measurement, and a repository-wide consistency check caught it.** The save tool's own documentation stated a confidence interval from 0.060936 to 0.067066 beside a count of 1,566 of 24,486 characters. Rather than guess which half was wrong, every nearby count was searched: that interval is the exact Wilson interval for 1,565 of 24,479, so a count taken at one moment had been printed beside an interval computed when the index was 7 characters smaller. Both numbers were real measurements and the pair was not. The corrected interval runs from 0.060958 to 0.067088, computed on 2 routes agreeing to 7 parts in 10 to the 18th. The neighbouring interval in the same sentence was exact throughout, which is the argument for recomputing a pair rather than reading it over.

Status: **COMMITTED**, in the change that carries this note. Evidence: all 19 failures reproduce and then pass, 1,309 tests across the 12 affected files; the re-aimed mutation harness turns the guard that lifts and runs the line red on 5 of 5 broken forms, selected against the 2 tests that run the block rather than read it; and the gate's declared cost was refreshed from 313 to 317 files and 5,124 to 5,233 collected tests, of which 70 are this work's and 39 are drift in other guard files since 17 November 2026.

## Recommendations, against the project's formal standards

**On the memory index — simplest sufficient, and additive in its symmetric form.** The relief reuses the existing backup, archive-append and pointer-conservation conventions rather than inventing parallel ones, and it is wired into the pre-flight pass that already runs the other 3 reliefs, so it is reachable by a caller and executed by a test. The removal half of the additive standard is satisfied by the companion file: nothing is deleted, every pointer still resolves, and the recovery command reads the companion in full.

**On the eviction order — composability, in the demonstrated sense rather than the weak one.** The composed rule is recommended only because it was measured to dominate either part alone on a named property, by factors of 1.2696 and 2.3545, with the dominance over age alone shown to be unconditional. Where a single rule had performed as well, the single rule would have been preferred.

**On the commit gate — simplest sufficient.** 1 shell block changed, no redesign, and the rejected alternative was rejected on a measurement rather than on judgement.

**On the decisions file — additive.** A clause was added where the record warrants one. Nothing was removed, no cap was introduced, and the existing ruling about the file's length is now protected by a mutation that fails if it is reversed.

## What is still owed to the founder

The index's standing ceiling means a lesson leaves the loaded window roughly every 31 days at the current arrival rate. That is arithmetic and not a decision. What **is** a decision, and is not taken here, is whether the arrival rate itself should fall: 5.6190 new memory files a day is high enough that the index is now larger than can be used in a single turn, and a smaller, more selective set of standing lessons may serve better than a complete one. That is a judgement about what the index is for, so it is put to the founder rather than resolved.

Written under CDSFL note standard v1.9 (1 November 2026).
