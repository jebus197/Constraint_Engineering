# The board refused the first autonomous batch, and all 15 faults were the session's own

22 November 2026, 04:10 GMT

## Summary

The first commit board run under the founder's autonomy handover refused, with
15 tests failed against 5,374 passed and 18 skipped in 2712.17 seconds, which is
45 minutes and 12 seconds. Not one failure was inherited from the repository's
existing state. All 15 were introduced by the session itself during the batch
the board was judging. A second refusal followed in under 2 minutes on the note
lint ratchet, and the instrument built to predict that refusal turned out to be
wrong in both directions at once.

The claim this note records is narrow and uncomfortable: on this batch, the
subject of the work was sound and the instruments around it were not. That is
consistent with a figure this project has already produced for a different
night, where 16 of 18 errors were in the instruments rather than the subject
(0.888889, Wilson 95 per cent interval [0.672002, 0.968980]), and it is not
independent evidence for it.

## The 15 failures, by cause rather than by symptom

Individual fixes do not generalise. Causes do, and 15 failures reduce to 6.

**4 came from closing entries without re-deriving what depends on them.**
`scripts/close_an_entry_2026-11-02.py` owns 3 surfaces and updates all 3. It
touches none of the 5 artefacts derived from those surfaces: the generated
decisions markdown, its spoken twin, the founder's Desktop copy, the 2 decision
surfaces an agreement checker compares, and the memory exclusions ledger. The
generated documents carried a modification time of 01:01:34 against a record
written at 01:52:06.

**3 came from scripts written the same night with no handling for a help
request.** This matters more than it sounds. The guard executes any script whose
behaviour it cannot establish structurally, so asking
`scripts/the_standing_goal_mutations_2026-11-22.py` for its help text would have
run its entire mutation harness and edited the working tree.

**1 came from summarising a panel round instead of preserving it.** The
founder's standing instruction is that external review output is presented in
full and never summarised in place of the full output. A full record now exists
at 44,567 bytes, built from the seats' own replies, with the summary beside it
rather than instead of it.

**1 came from a memory file written at 02:19 leaving a ledger derived at 01:56
stale by exactly 1 entry.**

**1 came from a substring standing in for a call.** A guard written that same
night used `str.index` on a bare filename, which matched the gate's own file
list 250 lines before the invocation it meant to find. The project's record
already names this exact failure.

**3 came from a guard whose premise test and whose assertions range over
different populations.** The premise was tested over task list entries, where 8
qualify; the assertions ran over decision rows, where 0 do. The 2 sets are
disjoint, so the premise passed while 3 assertions downstream of it failed.

## The repair of that last group was caught incomplete by its own harness

Making 3 live assertions conditional on their premise left the test suite green
while 2 properties went unguarded, because at 0 flags neither can fail whatever
the renderer does. `scripts/the_status_flag_mutations_2026-11-21.py` reported
5 of 8 mutations red and named both survivors. 2 constructed cases were then
added that plant the state needed to force a flag at any live count, and the
harness reports 8 of 8 red.

**The rule that follows: after weakening any assertion, re-run the mutation
harness rather than the suite.** A suite answers whether the code passes. A
harness answers whether the suite would notice if the code stopped. Only the
second question finds a guard that has quietly stopped guarding.

## An anti-vacuity floor breaks when the work progresses

3 instances appeared in a single night, each a floor of the same shape: a test
asserting that some live population is large enough for the assertion below it
to be meaningful, written as `> 0`, `0 < added`, or `len(det) >= 5`. All 3
failed. In all 3 the property being guarded still held, and only the floor
failed, because closing entries reduces the population a floor counts.

Lowering the number buys one night and erodes the protection at every
subsequent close. The correct repair is to pin the predicate under test with
constructed cases, assert the property without a floor, and skip with a stated
reason when the live population is genuinely too small to inform.

## The instrument built to predict the refusal was wrong in both directions

`scripts/note_ratchet_preflight_2026-11-01.py` exists so that the question "will
the note-lint ratchet refuse this commit" — the per-file check that refuses a commit
adding note-standard findings — costs seconds rather than a 45-minute board.
Measured on 22 November 2026, it disagreed with the gate it predicts on 4 axes
at once.

It selected files by suffix `.md` or `.txt` where the gate takes `.md` only. It
selected from any directory where the gate takes `experimental_notes/` and
excludes archived seat evidence. It read `git status`, which includes untracked
and unstaged work, where the gate reads only what is staged. And it read the
working tree where the gate reads the index.

**Both error directions were live at the moment of measurement.** It exited 1 on
`resources/RECOVERY.md` going from 81 findings to 83, a file the gate never
lints. The hook's own comment names that hazard in as many words: a guard that
fires on the ordinary case teaches people to reach for the override by reflex.
In the other direction it exited 0 on 2 files the gate would have refused. A
new note read 0 findings in the working tree while its staged copy held 3,
because a fix had been made and never staged. A brief file printed 33 findings
beside an exit code of 0, because a new file was reported and never refused,
while the gate holds a new note to a baseline of 0.

**The repair is additive.** The wide scan is the only thing watching spoken
companions and the resources directory, so it is kept and demoted to advisory.
The exit code is now set by the gate's own population alone. A disagreement
between the staged copy and the working tree is reported by name for every
staged file, with the remedy in the line. That last check earned its place
immediately: the `resources/RECOVERY.md` repair described above had never been
staged and would have been lost from the commit.

A defect was introduced by the repair itself and is worth recording, because it
fails closed and therefore looks like a catastrophe rather than a typo. The
revision prefix that reads the index is the empty string, since `git show`
takes a path after a colon. Passing a colon builds a doubled colon, every read
fails, and a fail-closed reader then reports every staged note as unreadable.

## Two instruments were rebuilt by hand that already existed

This is the night's broader pattern and it cost more than any individual defect.
The pre-flight tool already existed, and the guard beside it already pinned the
path-sensitivity subtlety that was then rediscovered from first principles. A
hand-written sweep was built instead, twice, and the first version was wrong on
suffix, directory, staging, and on tree against index. It also reported a count
of 2026 for 2 files, which is a year lifted out of a filename by a pattern that
took the first number it found on the matching line.

The cost was not the wrong numbers, which were caught. It is that running the
real tool at the outset would have surfaced its 4 defects an hour earlier.

A second, smaller instance: a Python file was verified with `ast.parse`, which
returned without error, and the next invocation of that file failed with a
syntax error. The parser accepts constructs that the symbol table rejects, so
`compile` is the check that answers the question and `ast.parse` is not.

## Status of each item

Every repair named here is COMMITTED to the working tree and TESTED by an
executing guard. None is merely proposed. The pre-flight repair carries
`bench/tests/test_the_preflight_population_is_the_gates_2026-11-22.py`, 9 tests
that construct a repository holding every case on which the 2 selectors could
disagree and compare the tool's population against the gate's own patterns,
lifted from the hook at test time so a stale copy cannot pass unnoticed.

Written under CDSFL note standard v1.9 (1 November 2026).
