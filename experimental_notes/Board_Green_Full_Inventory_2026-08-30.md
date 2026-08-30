# THE BOARD IS GREEN: 4521 PASSED, 0 FAILED, 0 SKIPPED

2026-08-30, 21:38 BST (UTC+1)

A complete inventory of every action agreed on 30 August was rebuilt from the record rather than from memory: 37 items, drawn from 6 self-proposed repairs, 2 reviews by Fable and 2 by CC2. Each was then verified mechanically against the working tree. Nine were still outstanding at the start of this pass. All 37 are now closed, and the test suite reports 4521 passed, 0 failed and 0 skipped, against 4434 passed with 34 skipped and 2 failed at the start of the day.

The reason a fresh inventory was needed is worth stating plainly. CC2's first review ended with a ranked list of 9 actions. Four of them, ranked 4th, 5th, 7th and 8th, were not carried out, and a subsequent summary nonetheless described the work as substantially complete. The inventory below exists because that pattern had repeated.


## The Network Ruling, And The Design Error It Exposed

The instruction was that the internet is always available here, and that testing the literature-retrieval component costs nothing beyond an existing subscription. It only costs money during a real experimental run.

The test suite's network guard had been conflating two entirely different risks under one label: dispatching a paid model, which costs money, and looking up a scientific paper, which does not. Three tests had been switched off by that conflation for 49 days.

The first repair attempted was a list of permitted free hosts. That was the wrong shape, and measuring it showed why: literature retrieval follows a document identifier to whichever publisher happens to host the paper, and the very first run reached www.mdpi.com, which no such list would ever have contained. A permitted-host list therefore passes the test by blocking the exact fetch the test exists to perform. That is precisely how those 3 tests spent 49 days reporting success without ever running.

It was inverted to a list of paid endpoints that stay blocked, with everything else permitted for the duration of a marked test. 8 tests now hold the money guard in place: paid endpoints and their subdomains are refused inside the window, hostnames arriving in byte form are normalised rather than waved through, and the window closes and clears its resolved addresses on every exit path. The three tests now run by default and reach the wire.


## The Proof-Program Transport Is Repaired

This was ranked 4th by CC2 in the first review and was one of the items skipped.

When a model proves a defect exists, it writes a small program and sends it back inside the reply, wrapped in markers meaning "this section is code". The markers are three backticks. The pattern that pulled the program back out allowed the closing marker to appear anywhere at all, including in the middle of a line inside a piece of quoted text. A proof-program that quotes a code listing, which is the only shape available for a claim about a document that prints code, was therefore cut off at its own first inner marker. The fragment still parsed and still contained an assertion, so it passed every check for being runnable and looked exactly like a complete proof.

The repair uses a precedent this codebase already contained for the opposite direction: the closing marker must sit alone on its line. Both affected test fixtures now survive transport byte for byte and reach a confirmed verdict. The 4 tests that had been excused from the ordinary acceptance set are no longer excused, and the test class that documented the defect now asserts the repair instead, so the defect cannot return unnoticed.


## The Discrimination Control Has Been Connected

The control that checks whether a proof-program fires because of the claim, rather than merely firing, has never run once in this project's life. The reason is now established and repaired.

A configuration flag named discrimination_control_ask was written once and read nowhere. This project's own record diagnosed that on 21 August and specified the one-line connection required. It was never applied. The function that composes the instruction to models accepts a parameter asking them to supply a corrected copy alongside their proof-program, and its only caller passed nothing, so the main panel was never asked. Only the routing path and the residual sweep asked.

That is the whole explanation for CC2's measurement: across the real experiment 45 and the simulated run, the number of findings carrying both of the control's two required inputs is 0 of 58, Wilson 95 percent confidence interval [0.0000, 0.0621]. The control was neither idle nor broken. It had never been given anything to work with.

It is now connected using this project's own established pattern for passing configuration into that layer, and enabled for the simulated run. The connection was measured, not assumed: the instruction grows by 858 characters when the ask is switched on.


## The Remaining Seven, All Closed

The target path is now normalised once, at the point of entry, rather than being consumed raw at 8 sites and normalised at 1. An absolute path used to disable the discrimination control silently while every other consumer carried on working.

Routing telemetry is now written into the report. The record of whether a routing attempt actually reached a model existed only inside one function and died there, which is why "0 resolved by strong writer" was indistinguishable from a dead connection for 4 consecutive rounds.

Files that version control is told to ignore now travel into a reviewer's sandbox. This was Fable's own first action item and is the direct successor to an earlier defect where reviewers were handed a tree missing the work under discussion. It is capped at 1 megabyte per file and the count is printed: 5,340 files carried, 40.6 megabytes, 7 skipped for size. An earlier estimate of 622 files and 18.7 megabytes was wrong, because the command used reports directories rather than their contents.

Fable, the sixth panel member, now has both a performance-specification entry and a composer configuration file. It had neither, so it silently ran with default parameters, no context-budget limit, and an entirely empty system briefing. The values are inherited from the closest sibling model and are marked as inherited in both files, because nobody has profiled Fable and a stated default is honest where an invented measurement would not be.

The verification stage now declares its truncation. It cut the target at 80,000 characters without telling the model, so on a large external target it would verify findings against a prefix while reporting a complete verification.

A paid-dispatch tripwire was added to the simulation harness itself. If the substitution layer ever has a hole, the run now refuses at the network layer rather than billing.

Two settings were deliberately diverged from the real experiment 45 so that machinery the real run never reaches is still stress-tested: the verification stage's minimum round, and the post-convergence sweep. Both divergences are stated in the configuration rather than silently inherited.


## One Thing The Reader Should Weigh

Neither review by either model has seen the current state of the code. The first review was handed a tree missing 12 files of uncommitted work, which is a defect since repaired. The second review saw the tree as it stood at that moment, but 9 further repairs have landed since. A third review of the final state has been dispatched, and its verdict is the last outstanding item before a simulated run.


Written under CDSFL note standard v1.7 (26 August 2026).