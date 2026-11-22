# The board refused the first autonomous batch, and all 15 faults were the session's own


22 November 2026, 04:10 GMT

> The plain-English companion to `The_Board_Refused_And_Every_Fault_Was_Mine_2026-11-22.md`, written for a reader outside the project. Its spoken twin is the matching `.txt`, re-rendered rather than copied.

## Summary

The first commit board run under the founder's autonomy handover refused. 15 tests failed against 5,374 passed and 18 skipped, taking 2,712 seconds, which is 45 minutes and 12 seconds. Not one of those failures was inherited from the repository's existing state. All 15 were introduced by the session itself, during the very batch of work the board was judging. A second refusal followed in under 2 minutes, this time on the note-lint ratchet, which is the per-file check that refuses a commit adding new note-standard findings. The instrument built to predict that second refusal then turned out to be wrong in both directions at once.

The claim recorded here is narrow and uncomfortable. On this batch, the subject of the work was sound and the instruments built around it were not. That is consistent with a figure this project has already produced for a different night, where 16 of 18 errors sat in the instruments rather than in the subject, a proportion of 0.888889 with a 95 per cent Wilson interval running from 0.672002 to 0.968980. It is consistent with that figure. It is not independent evidence for it.

## The 15 failures, grouped by cause

Individual fixes do not generalise. Causes do, and the 15 failures reduce to 6 causes.

1. 4 came from closing task entries without re-deriving what depends on them. The script that closes an entry owns 3 surfaces and updates all 3 correctly. It touches none of the 5 further documents derived from those surfaces: the generated decisions file, its spoken twin, the founder's Desktop copy, the 2 decision surfaces that an agreement checker compares against each other, and the memory exclusions ledger. The generated documents carried a modification time of 1 minute past 1 in the morning, against a record written at 52 minutes past 1.

2. 3 came from scripts written that same night with no handling for a help request. This matters more than it sounds. The guard executes any script whose behaviour it cannot establish by reading its structure. So asking one of those scripts, a mutation harness, for its help text would have run the entire harness and edited the working tree as a side effect.

3. 1 came from summarising a panel round instead of preserving it. The founder's standing instruction is that external review output is presented in full, and never summarised in place of the full output. A full record now exists, built from the seats' own replies, with the summary sitting beside it rather than instead of it.

4. 1 came from a memory file written at 19 minutes past 2 leaving a ledger derived at 56 minutes past 1 stale by exactly 1 entry.

5. 1 came from a substring standing in for a function call. A guard written that same night searched for a bare filename, and matched the gate's own list of files 250 lines before the invocation it was actually looking for. The project's record already names this exact failure.

6. 3 came from a guard whose premise test and whose assertions range over different populations. The premise was tested across task list entries, where 8 qualify. The assertions ran across decision rows, where 0 qualify. The 2 sets are disjoint, so the premise passed cleanly while 3 assertions downstream of it failed.

## The repair of that last group was caught incomplete by its own harness

Making 3 live assertions conditional on their premise left the test suite green while 2 properties went entirely unguarded. At 0 flags, neither property can fail, whatever the renderer does. The mutation harness for that guard reported 5 of 8 mutations red, and named both survivors. 2 constructed cases were then added which plant the state needed to force a flag at any live count. The harness now reports 8 of 8 red.

The rule that follows is worth stating plainly. After weakening any assertion, re-run the mutation harness, not the suite. A suite answers the question of whether the code passes. A harness answers the different question of whether the suite would notice if the code stopped working. Only the second question finds a guard that has quietly stopped guarding.

## An anti-vacuity floor breaks when the work progresses

3 instances appeared in a single night, each a floor of the same shape. A test asserts that some live population is large enough for the assertion below it to be meaningful. All 3 floors failed. In all 3, the property being guarded still held, and only the floor failed, because closing entries reduces the very population a floor counts.

Lowering the number buys 1 night and erodes the protection at every close after that. The correct repair is to pin the predicate under test with constructed cases, assert the property without any floor, and skip with a stated reason when the live population really is too small to be informative.

## The instrument built to predict the refusal was wrong in both directions

The note-lint ratchet pre-flight script exists so that the question of whether the note-lint ratchet will refuse a commit costs seconds rather than a 45-minute board. Measured on 22 November 2026, it disagreed with the gate it predicts on 4 separate axes at once.

It selected files ending in markdown or plain text, where the gate takes markdown only. It selected from any directory, where the gate takes the experimental notes directory and excludes archived seat evidence. It read the full working status, which includes untracked and unstaged work, where the gate reads only what has been staged. And it read the working tree, where the gate reads the staging area.

Both error directions were live at the moment of measurement. In one direction it refused on the recovery document going from 81 findings to 83, a file the gate never lints at all. The commit hook's own comment names that hazard in as many words: a guard that fires on the ordinary case teaches people to reach for the override by reflex. In the other direction it passed 2 files the gate would have refused. A new note read 0 findings in the working tree while its staged copy held 3, because a fix had been made and never staged. A brief file printed 33 findings beside a clean exit, because a brand new file was reported and never refused, while the gate holds a new note to a baseline of 0.

The repair is additive. The wide scan is the only thing watching spoken companion files and the resources directory, so it is kept and demoted to advisory. The exit code is now set by the gate's own population alone. A disagreement between the staged copy and the working tree is reported by name for every staged file, with the remedy printed in the same line. That last check earned its place immediately. The recovery document repair described above had never been staged, and would have been lost from the commit entirely.

1 defect was introduced by the repair itself, and is worth recording because it fails closed and so looks like a catastrophe rather than a typo. The revision prefix that reads the staging area is the empty string, because the command takes a path after a colon. Passing a colon builds a doubled colon, every read fails, and a reader that fails closed then reports every staged note as unreadable.

## 2 instruments were rebuilt by hand that already existed

This is the night's broader pattern, and it cost more than any individual defect. The pre-flight tool already existed, and the guard sitting beside it already pinned the path-sensitivity subtlety that was then rediscovered from first principles. A hand-written sweep was built instead, twice, and the first version was wrong on suffix, on directory, on staging, and on working tree against staging area. It also reported a count of 2026 for 2 files, which is a year lifted out of a filename by a pattern that took the first number it found on the matching line.

The cost was not the wrong numbers, which were caught within minutes. The cost is that running the real tool at the outset would have surfaced its 4 genuine defects an hour earlier.

A second, smaller instance of the same pattern. A Python file was verified with the standard library's parser, which returned without error, and the very next run of that file failed with a syntax error. The parser accepts constructs that the symbol table later rejects. The compile function is the check that answers the question. The parse function is not.

## Status of each item

Every repair named here is committed to the working tree and tested by an executing guard. None is merely proposed. The pre-flight repair carries a new guard of 9 tests, which construct a repository holding every case on which the 2 selectors could possibly disagree, and compare the tool's population against the gate's own patterns, lifted from the commit hook at test time so that a stale copy cannot pass unnoticed.

Written under CDSFL note standard v1.9 (1 November 2026).
