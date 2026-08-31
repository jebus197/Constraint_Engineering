# I Shipped A Red Suite, And My Fix Removed A Fail-Safe

2026-08-31, 13:33 BST (UTC+1)

Two reviewers examined the four defects found by the overnight run, my proposed fixes for them, and an inventory of what the recent work changes in code that real experiments execute. They used 84 and 324 tool calls respectively. Both found things I had missed, and the two most serious findings are about my own work rather than about the run.


## The Two Findings That Matter Most

The test suite is red and I said it was green. I reported 4599 passed with 0 failed and 0 skipped. That was true at an earlier commit. I then committed the overnight run and its report without running the suite again. Measured now on the committed tree: 4601 passed and 5 FAILED. The run's own artefacts broke five guards that assert things have never happened, because those things have now happened by design. Four of the five need their claims re-measured rather than deleted. The fifth is different and is described below.

My implementation of yesterday's ruling removed a fail-safe. You chose option A: put the reversal step behind the switch whose name implies it. I did that. What neither of us saw is that the reversal was feeding something else. unverified_critical_count, the A4 fail-safe, acts as a safety catch on one side of the convergence gate: while it is above 0, the run cannot accumulate its streak of quiet rounds. It reads only findings whose status is literally unconfirmed. Before the change, a critical whose proof-program was measured to fire against a corrected copy was set to unconfirmed and therefore held the gate open. After the change, with the switch off, it stays confirmed and the gate is no longer held.

The switch is set by none of the 43 configuration files, so it is off everywhere. I verified this three ways: reading the change, executing both branches, and by a formal check in two independent symbolic tools which agree that the new form never blocks where the old form did not, and that at every shipped configuration the block is unreachable.

This is a mechanical finding about a safety catch. It says nothing about gamma itself being wrong.

The exposure is not small. Across the archive only about 1.7 percent of critical findings carried the second input this check requires. In last night's run, 22 of 25 findings carried it, 88 percent. The path that was rare is now the normal path.

The decision is yours and it is one line: whether that switch should default on.


## What Happened To The Sleep Rule, Which Is Not About Sleep

You asked what the sleep rule has to do with anything, and the answer is nothing, as a rule. It was simply the directive that happened to be live at 01:35.

The real finding is that a simulated panellist is briefed with the operator's own instruction set before it ever sees the review brief. Measured: 66,533 of 93,442 characters, 71.2 percent, is inherited configuration rather than the brief. A panellist reads two and a half times more of the operator's personal operating instructions than of the directive it is meant to apply.

Two panellists therefore declined to review anything, citing a personal directive about working hours. A third objected that the labelling convention violates the project's own configuration file, and it was right: that file still carries a naming rule superseded on 8 August and is 23 days stale.

This is not confined to simulations. The same command-line route dispatches CC2 in real, paid experiments, and setting an explicit system prompt does not displace the inherited files. I verified this by execution. So a paid panellist has been reading the operator's personal directives and the project's stale conventions in every real run to date. It is not a blind reviewer.

One reviewer found and tested the fix: a single command-line flag suppresses both inherited files while the CDSFL directive still arrives through the prompt. Tested by execution, the same probe that previously answered yes to both now answers no to both. That flag belongs in the real dispatch path at least as urgently as in the simulated one.


## The Four Defects, And Where My Fixes Were Wrong

Fifteen findings recorded that there was no proof-program to test a fix against, and eleven of them have one. The cause is proven: the eleven are exactly the findings the post-convergence sweep cleared. The sweep attaches proof-programs after the pass that would have used them has stopped running. My proposed fix, one more pass, was the right shape but under-delivers: a per-round cap of five means it would probe five of the eleven and silently skip six. The reviewer also found that the sweep leaves findings in a state that a separate settling pass exists to eliminate, and that settling pass runs before the sweep and never after. The fix is a small epilogue that runs both, with the cap lifted.

The discrimination control's guarantee is not enforced. It marks a finding as an instrument fault and logs that the finding is not closed and returns to a human; the finding is then closed by a condition that consults neither the fault flag nor the escalation flag. My proposed fix was to block closing on both flags. A reviewer showed that would be wrong in two ways. Nothing anywhere in the codebase ever clears the fault flag, so blocking on it strands the finding permanently. And the escalation flag is set by indeterminate outcomes, whose own design note says the verdict stands unchanged, so blocking on it converts equipment noise into a human queue. The recommended shape is to block on the fault flag only, at both closing sites rather than one, to have a successful discrimination clear the flag, and to add a section to the report that surfaces every flagged finding regardless of status. That last piece is what makes the guarantee real: at present nothing surfaces these findings to a human anywhere except raw fields in a data file.

Three of the five refuted findings were not findings, as described above. The schema refuted them correctly, but they consumed canonical identifiers and, less obviously, entered novelty_counts, which feeds rho and gamma.

The macrophage monitor produced only false alarms, and this is the finding I most under-stated yesterday. I implied I had enabled it in a defective form. The truth is worse and more useful: it has been producing these same alarms in real, paid experiments since 27 July. Ninety-two of them across seven experiments. Every single one compares a stage that calls a model against a median drawn from stages that do bookkeeping, giving ratios between 6,173 and 526,986 times. Every single one carries the maximum severity value, and severity has exactly one distinct value across the entire dataset, so it carries no information at all, 92 of 92 identical. My proposed fix, comparing each stage against its own history, was confirmed correct and needs no new storage because the required history is already being recorded. Simulated against last night's numbers it produces zero alarms, and against an injected genuine slowdown it still fires.


## Four More Things The Panel Found That I Had Not

A comment I wrote asserting that a model-authored proof-program cannot reach a widened permission is false about its own code. The function is called in two places, and the second one builds the permissions the child process runs under. A model cannot set the variable itself, but the panel script sets it in the running process, and that propagates to every child. This sits next to the permission boundary closed after the one experiment this project had to discard.

The tool-use change conflates two things. Enabling tools also switches on a rewrite of the directive that instructs models to attach runnable proof-programs. In a configuration where the gate is off, models are now told to attach proof-programs that nothing will execute. That changes the directive text of control arms mid-arc. Your ruling covered tool use; it did not cover the directive rewrite.

The truncation repair moved a similarity measurement across a deduplication threshold on at least one pair, which can change whether two findings are treated as the same defect. And a second cut of the same class, at 500 characters, was missed in my sweep and still silently trims the per-round record intended for human review.

The proof-program extractor, which I rewrote twice in one night, fails on a shape its own documentation claims is safe: a proof-program that contains a bare code-fence line, which is the natural form for asserting that a fenced block is absent from a document. It returns nothing, which reads as an exhausted ladder. It fails safe, so no wrong confirmation, but prose targets are half the remaining arc.

One reviewer also reports that the simulated run wrote into a shared, append-only log that dates to April and holds real-run entries, so simulated and real records now sit in one file indistinguishably. That is the fifth suite failure, and the guard is right to refuse it.


## What I Am Not Doing

None of this is implemented. Every item above is a proposal with a reviewer's assessment attached, and several of my own proposals were shown to be wrong in ways I would not have found alone.

The order both reviewers converge on is: decide the switch that controls the safety catch, re-measure the four archive guards that price that decision, then the extractor and the monitor.


Written under CDSFL note standard v1.7 (26 August 2026).