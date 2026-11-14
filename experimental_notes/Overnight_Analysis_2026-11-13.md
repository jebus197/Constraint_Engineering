# Overnight Analysis — 13 November 2026

Written 2026-11-13 05:56 GMT. Markdown companion to `Overnight_Analysis_2026-11-13.txt` in the founder's spoken-output folder.

**This is a RE-RENDER, not a conversion.** The spoken copy carries no markdown, no backticks and no file paths, because those are read aloud as noise. This copy restores the identifiers a reader needs in order to check any claim, and the substance of the 2 is the same. The pairing is required by `tts-output-protocol`; this twin was missing until 2026-11-14 and entry B192, the spoken files with no markdown twin, records the gap.

## Summary

A clean full test-suite run was started at 04:10:53 to establish how much of the project's guard set still passes, because the last such measurement was 5 days and more than 65 commits old. While that run occupied the machine, the session carried out read-only analysis on the open work items, because any edit to the repository would have invalidated the measurement in progress. That analysis advanced 9 of the 29 open items, found 1 previously unknown defect in work completed earlier the same night, and produced 11 prepared repairs whose text was verified against the files they would change.

**The most important single result is that the run in progress cannot discharge the item it was started for.** That item requires a clean repository, and the repository held 36 modified files at the time. The run still has value, because it reports which tests the night's changes broke, but a second run is needed after the work is committed. That sequencing error cost roughly 2 hours of the founder's machine and is recorded as the session's own.

## A defect found in the night's own work

The harness chooses which command-line client serves a model dispatch. Earlier work added a report describing that choice, including whether a newer client is installed. Driving that report twice on the same machine produced opposite verdicts, depending only on whether the selected client's version had been read.

Without reading the version, the report stated that the selected client was the newest the machine offers. With the version read, it stated correctly that the selected client was at version `2.1.220` while `2.1.317` was installed — **a gap of 97 patch releases**. The cause is that the list of newer candidates is built only when a selected version exists, so an unread version produces an empty list, and the report had only 2 branches — a gap, or newest. **An absence of data was rendering as a positive verdict.**

The decision the report describes is correct and unchanged: the client found on the shell's executable search path is still preferred, because which client serves a dispatch decides which model answers. Only the sentence printed about that decision was false.

The repair adds a 3rd state rather than altering either of the existing 2. The report now exposes whether a comparison was possible at all, and the description gains a branch saying that it cannot tell and naming the option that would find out. The repair was proven on a copy before being prepared, **passing 12 checks of 12**, including that an older report structure without the new field still renders rather than failing.

### Why no test caught it

The test suite runs under a network guard that refuses attempts to start subprocesses. Every test must therefore ask the resolver not to read the version — which is exactly the path that produced the false statement. The guard for this area did contain a consistency check, and **that check re-implemented the producer's own condition**, so when the version was unknown both sides of the comparison were 0 and the assertion passed while testing nothing.

A new guard case was written and proven to fail on 3 incomplete versions of the repair and to pass only on the complete one. With the field added but the description untouched it fails on the message assertion rather than on the missing field, which confirms that the message check carries its own weight.

## The suite changes the repository it measures

2 separate tests were observed modifying the repository during the measurement.

The 1st runs a figure-producing script as a subprocess in order to read its printed output, and that script writes a data file as an unconditional side effect. The file changed twice, 31 minutes into the run. The content was correct, because 4 counts legitimately rose when new guards were added, but the location was not.

The 2nd runs the project's real commit hook with its working directory set to the real repository. That hook stages a file into the version-control index, and **the index was rewritten at 04:44:12 with a change nothing had chosen**. The same hook also runs the gate's board of guard files as a nested test run, which took **1032 seconds against its own allowance of 900** and stalled the outer measurement for all of it.

A guard exists against tests modifying the working tree, and it names the staged file among those it protects. **It was blind for 2 independent reasons, either sufficient on its own.** It returned early unless the offending text mentioned 1 particular script, so a modification through the hook was never examined; and it recognised the repository root by a list of 4 variable spellings, while the offending file uses a 5th.

The repair identifies a repository-root variable by what it is assigned from rather than by its name, and widens the set of recognised modifiers. It was falsified on 4 states, including all 3 of the guard's own commissioning examples, and **flags exactly 1 file across all 916 test files** — the file already confirmed from the live process listing. A guard that accused correct code would be the worse error, and this project has had 4 such guards break on correct changes in a single day.

## A 17-minute saving that is also a trade

The test running the real commit hook asserts that the hook exits successfully. That requires the entire hook to pass, including the guard board. The hook's mirror-refreshing stage sits 368 lines before that board, and the mirror ordering is the only thing the test claims to examine.

Asserting the effect of that early stage instead would let the test run in a throwaway repository, would stop the index being modified, and would remove about 17 minutes from every full suite run. **The honest cost is that it checks less.** It stops incidentally proving that the whole hook passes, and that incidental coverage is real, standing at 1 assertion over the hook's whole exit path — which is also precisely what costs the 17 minutes. The end-to-end behaviour is already covered by 2 other tests. Because this changes what a test asserts, it is recorded as a decision for the founder rather than as a repair to apply.

## Mechanisms that are tested and reach nothing

The project's `additive-standard` requires that a new entry point be wired to a caller and executed by a test. 3 mechanisms were confirmed, by reading the modules rather than by any automated search, to have the test and no caller.

- A ticket-kind reader: 18 test references, 0 production callers. Its revert is deliberate and documented.
- A consequence-scale resolver: 15 test references, 0 production callers. Its only other mention sits inside explanatory prose.
- A conversational repair turn: 4 test references, all assertions in its own guard, and 0 production callers.

2 of the 3 come from work completed on 2026-11-12.

**An automated search for this class was attempted and its figure is withdrawn.** 3 successive predicates each had a demonstrable blind spot, and the project's own rule is that a surface defeating 3 predicates is the point to stop rather than write a 4th. What would answer the question is instrumenting imports at run time and recording which functions are entered, which measures reachability by EXECUTION — the 1 route none of the 3 predicates took.

## What the instruction files now say wrongly

**Every one of 11 figures describing what a commit costs reproduces differently today than when it was written.** The mean rose from 1485.03 seconds to 1612.619048 seconds. 2 separate faults are involved and they are not the same.

The 1st is drift and is nobody's error: the source ledger is not under version control and roughly doubled in the 3 days after the figures were recorded.

The 2nd **was wrong when written**. The text describes the exclusion rule as 13 refusals under 300 seconds, while the producing script has excluded runs under 120 seconds as indeterminate since a commit dated 4 days before the text.

The direction of the correction supports the founder's existing ruling rather than undermining it: an avoidable commit costs about 126 seconds MORE than the instruction files claim.

## What a human decision is still needed for

Of 29 open items, a partition verified to cover all of them exactly reports that **7 need a ruling never given, 4 need only a yes-or-no permission, 4 carry a ruling whose remaining question cannot be decided from the text, and 14 can be moved without the founder.** The figure the harness prints each turn — 11 awaiting him — is the first 2 of those groups combined, and 4 of the 11 are blocked on the question of which predicate should replace the one producing that figure.

## The session's own error count: 7 of 7 caught by execution

7 measurement faults were made and corrected during the night.

1. A population census counted its own producing script and 359 archived files from past panel rounds.
2. A detector's total agreed with the authoritative count at 11 while measuring a different set.
3. Index backup files contaminated a count of unreferenced memories, inflating it from 0 to 18.
4. A comparison column was labelled as a loss when it counted a corrected span.
5. A fingerprint check compared a 64-character digest against a 16-character digest, and reported 8 files changed when all 8 were identical.
6. A default argument bound at definition time caused a survey to run against the wrong tree and return nothing.
7. An empty population was printed as 0 of 0 rather than refused.

**Every one was caught by checking a sample or re-reading the output. None was caught by reasoning about the code.** In 6 of the 7 the subject under test was sound and only the measurement of it was wrong. **That split — 7 of 7 caught by execution and 0 by inspection — is the clearest result of the night**, and it argues for executing instruments against known cases rather than inspecting them.

## What happens next

When the run completes, a prepared triage will classify its failures against a named baseline of 4 known failures from 2026-11-07 and against a map of which tests reach the night's changed files. **That triage deliberately refuses to decide whether a failure is pre-existing**, because judging that by name alone was an error already made once during this session, and re-measuring by content gave the opposite answer.

The 11 prepared repairs will then be applied, validated by re-parsing and re-importing every file they touch, committed as 1 batch rather than 1 commit per repair, and followed by a clean-repository run that can finally be recorded.

---

Written under CDSFL note standard v1.9 (1 November 2026).
