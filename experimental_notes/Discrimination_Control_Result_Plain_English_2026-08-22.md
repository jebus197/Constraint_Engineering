# The discrimination control has been run, both routes. Half the archive's confirmations are demonstrated. Half are not.

22 August 2026, 02:10 to 03:05 BST


## What Was Asked, And The Rule That Was Fixed Before Any Number Existed

Yesterday's control asked the easy half of the question: change something in the target that the finding does not accuse, and does the test stay put? None of 360 moved.

This is the hard half, and four of the five panel models named it as the single next step. Repair the accused defect, and the test must fall silent. A test that keeps firing after the very defect it accuses has been repaired was never testing that defect.

Before the measurement was taken, a decision rule was written down and taken from CC2, so that it could not be chosen afterwards to suit the answer. If 95 percent or more fall silent, the modern era is sound without reservation. If 10 percent or more keep firing, the record moves materially toward the position that its confirmations cannot be trusted.

That rule is honoured below rather than renegotiated.


## How It Was Done

372 confirmed tests were examined, drawn from experiments 42 through 47, which are the code targets. Experiments 48 and 49 were excluded because their target documents have been deleted from the machine and their tests can never be re-executed.

Every single execution took place inside a throwaway copy of the repository built from symbolic links, using the runner's own machinery. The real repository was never written to at any point. An earlier tool in this project did adjudication by writing to the real file and restoring it afterwards. This deliberately does not.

Four preconditions had to pass before anything was scored.

First, a tripwire. The target was replaced by a file that raises an error the moment anything imports it. A test that still returns a normal verdict against that was never reading the target at all. 8 were excluded on this.

Second, a baseline. The test must actually fire against some real stored version of the file it accuses, found by searching the whole version history across every branch. Without that, falling silent later would mean nothing, because a test that never fires falls silent on everything. 4 were excluded.

Third, determinism. Two runs on identical bytes must give the same answer.

Fourth, the whole repair must apply, not part of it. This was cross checked two separate ways, and 262 of the 263 scored repairs consist of exactly one change block on both counts.


## Route A. Repair The Accused Defect

132 tests fell silent when their own accused defect was repaired.

131 kept firing.

67 could not be scored because the repair's search text matches no stored version of the file.

30 produced an error, 8 never read the target, and 4 had no baseline.

Of the 263 findings that could be scored, 132 fell silent. That is 50.2 percent.

Against the rule fixed in advance, this fails, and it fails on the unfavourable side. The threshold was 95 percent. The result is 50.2 percent, and just under half kept firing.


## Route B, And Why Its Headline Number Should Not Be Quoted

The second route asked whether a test ever responds to the file it accuses, across every stored version of that file. 346 of 360 fire on every single version.

On its face that looks devastating. It is not, and the reason is an internal check built into the analysis. 126 findings fell silent on their own repair under route A while still firing on every stored version under route B. The explanation is simple: this runner suggests repairs to a human being and does not commit them, so most of the accused defects were never actually repaired in the version history. A correct test is right to keep firing on a file whose defect was never fixed.

Route B is therefore largely uninformative here. Route A carries the weight.


## The Objection That Had To Be Answered Before The Result Could Mean Anything

Still firing after the repair conflates two entirely different things. Either the test does not discriminate, or the proposed repair did not work. These are model written repairs which in most cases were never applied or reviewed by anyone. A perfect test facing a bad repair is right to keep firing.

So each of the 130 still firing tests was re-run against up to 8 other findings' repairs to the same file. Those are known to be substantive changes, because each of them was observed to silence some other test.

2 of the 130, which is 1.5 percent, fell silent on some other substantive change. For those, the test is demonstrably sensitive to change and its own repair is what failed.

128, which is 98.5 percent, never fell silent on anything.

So the bad repair explanation accounts for 1.5 percent, not 50 percent.

There is a genuine counter objection here and it should be stated rather than buried. Firing on somebody else's repair is exactly what a correct test should do. Fixing defect Y ought not to silence a test for defect X. So the 98.5 percent figure is not by itself proof of anything being broken. The evidence against those 131 is that they fire on their own repair. What the cross probe adds is narrower but still worth having: for 128 of them, no condition tested anywhere, not their own repair, not eight substantive edits, not an unrelated function rename, not any stored version of the file, has ever been observed to change their answer.


## The Mirror Control. Are The Ones That Passed Actually Any Good?

A test that falls silent on any change at all is not discriminating, it is merely fragile, and its pass would be hollow. So the same probe was run on the 132 that passed.

92, which is 69.7 percent, are specific: silent on their own repair, still firing on all eight of the others.

40, which is 30.3 percent, also fell silent on somebody else's repair.

But that 30.3 percent is mostly not fragility either. Of those 40, 35 were silenced by only one or two of the eight donors. That is the signature of duplicate findings sharing a common root cause, and it is precisely the criterion this project's own repair based adjudicator uses to decide that two findings are the same defect. Exactly one test was silenced by all eight of eight, which is genuine fragility. Four sit somewhere in between.

So the fragile population is between 1 and 5 out of 132, not 40. The half that passes, passes cleanly.


## The Result, Without Softening

Of 263 archived confirmations that could be tested, 132, or 50.2 percent, are backed by a test demonstrated to fire on the accused defect and fall silent on its repair, and almost all of those are specific to their own claim. The other 131 keep firing after the very defect they accuse has been repaired, and 128 of those have never once been observed to fall silent under any condition tested.

By the rule fixed before the measurement, this moves the modern era materially toward the unfavourable position. Half the archive's confirmations are demonstrated. Half are not, and are now known not to be.


## What This Does Not Show, And The Distinction Is The Entire Point

It does not show that the design is unsound, or that the engine cannot work. Three reasons, and each is a measurement rather than a consolation.

First, 50 percent is not zero percent. 132 tests do exactly what the design specifies. They fire on the defect, they fall silent on its repair, and they keep firing through eight other substantive edits to the same file. A design that did not work would return something close to zero, not a clean split down the middle. What a working instrument applied to a mixed population looks like is precisely a split.

Second, the failure has been located and it sits in the gate, not in the concept. CC2 demonstrated earlier tonight that a test consisting of nothing but a print statement containing the word FALSIFIED is recorded as a confirmation. The gate has never required a test to demonstrate that its answer depends on the target at all. Nothing about the underlying idea, that a runner independently re-executing a test is a better arbiter than models agreeing with each other, fails here. One missing check does.

Third, and this matters most: the measurement is itself the repair. The script that produced these numbers is the filter. Run it inside the loop, and the 131 never reach the confirmed state in the first place. The machinery to do that already exists inside the runner, with eight distinct outcomes and three self checks, and has simply never been given a corrected copy to work with. Applied backwards over the archive, it re-grades the record rather than discarding it.


## What Follows

First, feed the control that already exists in the runner. It only runs when a corrected copy of the document is supplied, and no panel has ever been asked for one. A finding's own proposed repair is already produced, so the corrected copy is one step away. Until that lands, no future run can tell a demonstration from an assertion either.

Second, re-grade the archive. Stamp each of the 263 scored findings with its discrimination outcome. 132 become demonstrated confirmations. 131 become asserted ones. This is the typed provenance work Codex argued for, and the data for it now exists.

Third, look into the 67 that could not be scored because the repair matched no stored version, and the 30 that errored. A quarter of the population could not be tested at all, and that is a finding in its own right.

Fourth, do not start a live experiment until the in loop control is working. Adding runs to an instrument that cannot tell a demonstration from an assertion multiplies exactly the problem measured here.

Every figure above is offline and cost nothing. The scripts are named discrimination control archive and discrimination cross probe, in the scripts folder, and the full technical note is in the experimental notes folder dated 22 August 2026.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
