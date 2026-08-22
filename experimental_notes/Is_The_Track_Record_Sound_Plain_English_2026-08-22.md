# Is the track record sound, or is the work to date unreliable? An audit, and a five model panel.

22 August 2026, 01:20 to 02:00 BST


## The Question, Put Fairly To Both Sides

Over five days an assistant working on CDSFL audited the harness and found a series of defects. Eleven of that assistant's own claims were withdrawn in the same window. The founder asked whether the cumulative record means the work to date is unreliable, and required that if the answer is yes it should be said plainly rather than softened.

Two positions were put to a five model panel with equal weight, and with no step that forces the models to agree with each other.

The first position. The defects are the ordinary residue of a system that was still being built. A component cannot be faulted for running imperfectly before it is finished. On this view, finding defects is evidence the build is progressing.

The second position. The defects are not build residue. Conclusions were drawn from components that were broken at the time, and presented with more confidence than their state justified. On this view some or all of the recorded results should be set aside.

The panel was given the raw measurements and told explicitly that reassurance was worth nothing and that manufacturing a problem to appear rigorous was equally unwelcome.


## First, A Claim Of Mine That Turned Out To Be False

On 21 August, and again on 22 August, the assistant told the founder that the project's founding principle, which is that tools decide and model votes do not, was currently unauditable on its own record. That claim came from a reviewer and was never checked against the archive.

It is false for every experiment from number 42 onward. Checking it took forty minutes and cost nothing. It is true for experiments 34 through 41, for a reason that turns out to be a dated commit rather than a failure.


## What The Archive Says

There are 2,030 recorded findings across 27 archived runs. 1,442 of them sit in a final state: closed, confirmed, merged or refuted.

Of those 1,442, only 454, or 31.5 percent, carry a record of the runner having independently re-executed the model's own test and reported what it found. On the face of it that is alarming.

A correction is owed on those numbers. An earlier version of this analysis, and the brief the panel was given, reported 2,247 findings and 27.5 percent. Those figures counted one archived directory twice, because a folder named for the latest run holds a byte for byte copy of a folder named for its timestamp. CC2 caught it by reproducing the measurement rather than accepting it. The error ran against the project's own interest, which is the right direction for an error to run, but two figures inside one measurement disagreed and that is a defect.

It is also a mixture of two eras, and reporting it as one number is misleading.

Split by era, the picture is almost binary. From experiment 42 onward, covering 11 runs and 532 final verdicts, 85.3 percent carry that tool record. Among findings that were closed, the figure is 97.4 percent. For experiments 34 through 41, covering 16 runs and 910 final verdicts, the figure is zero. Not low. Zero, in every single run.


## Why The Older Era Is Empty

Searching the project's own version history for the first appearance of the field that records a tool verdict gives a single date: 3 June 2026, commit 4fba6cc. The commit message reads, in the project's own words, that runner decided verdicts replace the confirm or challenge vote.

Every run with a zero score predates that commit.

The configuration files were then read directly rather than trusting the code's default value, because reading a default instead of a configuration file produced a wrong claim earlier this week. The switch is absent in all eight configuration files for experiments 40 and 41, and present and switched on in all seventeen configuration files from experiment 42 onward, including four experiments that have not yet been run.

So the boundary between the two eras is the arrival of the mechanism, not a change in how the system behaved. That is precisely the founder's engine analogy, and it is not a rationalisation, because it is a commit hash with a date attached and a switch that is off before it and on after it.


## Does The Recorded Outcome Actually Follow The Tool?

474 modern findings carry a tool verdict. Where the tool said the defect was confirmed, the finding ended up closed or confirmed in 436 of 437 cases, which is 99.8 percent. Where the tool said the defect was refuted, the finding ended up refuted in 12 of 13. Where the tool could not be run at all, the finding was left unconfirmed in all 9 cases.


## The Measurement That Carries The Most Weight

227 modern findings carry both a tool verdict and a set of model votes. In 201 the two agree, which settles nothing either way. In 26 they disagree, and those 26 are the only real test of the founding principle available in the archive.

The tool prevailed in 25 of the 26. The model majority prevailed in none.

An earlier version of this analysis attached a probability to that, first about 3 in 100 million, then about 4 in 10 million after DeepSeek pointed out that the first figure excluded an ambiguous case in a way that flattered the result. Both are now withdrawn, because CC2 made a more serious objection that destroys the statistic outright.

The objection is this. In the runner, the function that re-runs the tool overwrites the status unconditionally whenever the gate is switched on. So with the gate on, the tool prevailing is not a finding, it is a certainty. Testing it against the possibility that votes were deciding tests something the source code already assigns probability zero. The number was arithmetic on a foregone conclusion.

It is worth dwelling on how that happened, because the same fact appears twice in this analysis pulling in opposite directions. The ordering, votes first and tool second, was cited above as the refutation of the panel's strongest objection, and it genuinely is that. It is also the reason the probability is meaningless. The evidence used to defend the measurement is the evidence that guts it, and the assistant reported the first without noticing the second.

What the table still legitimately establishes is narrower and worth having. It is a regression check: the gate was switched on and nothing bypassed it across every modern run. Given that six paths allowing model votes to merge findings away were found in this same codebase three days earlier, a check that the equivalent path is clean is not nothing. It is a bug check, not a significance test.

CC2 then decomposed the 26 disagreements and showed they are not 26 equivalent contests. 18 of them are cases where the tool failed to run and the runner withheld. Those are sound and they support a real claim: model agreement is not sufficient. 6 of them are votes to merge, reopen or extend a finding, which are housekeeping decisions rather than claims about whether a defect is real, and counting those as the models wanting a different truth was the assistant's construction and is not defensible. That leaves 2 cases where a model majority made an actual truth claim against the tool's truth verdict.

So the claim that the tool overrules the panel on questions of truth rests on 2 cases, not 26. The claim that model agreement is not sufficient rests on 18 and holds.

There is still a way of stating the sound part that requires no interpretation at all. Of 16 findings where the model majority voted to confirm the defect and the runner's test either errored or could not be run, the number that ended up confirmed or closed is zero.


## What The Panel Tried To Do To That Measurement, And What Happened

On the housekeeping bucket, Gemini objected that the measurement only shows the tool acting as a brake, blocking a confirmation the models wanted, and never as an advocate, saving a finding the models wanted to discard. It said the brief provided no evidence the latter had ever happened.

That was checkable, so it was checked. There are 7 such cases. In five the model majority voted to merge the finding away, in one to challenge it, in two to reopen it. In all 7 the tool said the defect was confirmed and in all 7 the finding ended up closed. The tool acts in both directions: 19 times as a brake, 7 times as an advocate.

Four of the five panellists objected that the measurement covers only 227 of 566 modern findings and asked what happened to the rest. Also checkable. 247 findings carry a tool verdict and no model votes at all, so they cannot host a contest between the two and are not a withheld sample. That is 43.6 percent of the modern era decided by the tool with no vote in play. 72 carry votes and no tool verdict, and those are a genuine gap the measurement says nothing about.

The sharpest objection came from Codex, ChatGPT and DeepSeek in three different forms, and it amounts to this: if the same piece of code writes both the tool verdict and the final status, then the agreement between them is a mapping rather than a contest, and proves nothing. DeepSeek put it most precisely by pointing out that if the votes were cast after the models had seen the tool output, then the tool prevailing is indistinguishable from the tool merely formalising what the models already thought.

That one is settled by reading the program rather than the data. In the runner, the function that writes a status from the votes is called first. The function that re-runs the tool and overrides that status is called nine lines later. The second function's own documentation states that it is called after the first so that the falsifier verdict wins. The vote-derived status is written and is then overwritten.

The remaining weakness there is real and worth stating plainly. This is provenance at the level of the code path, not at the level of the individual record. It shows the route every finding took. It does not stamp each finding with the specific event that decided it. Closing that gap is what a typed transition log would do.


## The Finding That Outranks Everything Above

CC2 was the only panellist with the ability to run commands, and rather than reasoning about the gate it ran the gate. What it found has been reproduced independently.

A test consisting of nothing but the instruction to fail, with the word FALSIFIED in the message, is recorded as CONFIRMED. A test that simply prints the word FALSIFIED and does nothing else is recorded as CONFIRMED. A test that prints anything else is recorded as REFUTED.

So the gate measures that a test fired. It does not, and by construction cannot, measure that the test fired because of the claim it was written to check. A test that asserts failure unconditionally is recorded in the archive as an independent tool confirmation, indistinguishable from one that genuinely demonstrates a defect.

And not one of the 2,030 archived findings carries a discrimination record. The control that would separate those two cases has never run, once, in the project's life. The switch that would ask a panel for the corrected copy it needs is set to false in the source.

This does not mean the archived confirmations are false. It means nothing in the archive distinguishes a true confirmation from an empty one. That is a different and more serious statement than anything about coverage percentages, and it applies to the modern era as much as to the older one.


## Two Experiments That Must Come Out Of The Headline Figures

Experiments 48 and 49 should be excluded from any headline claim, for three reasons that were each verified rather than argued.

First, the answer key contamination already recorded in the project's own errata: one panel model held the seeded set from the first round, and that retraction stands.

Second, both target documents have been deleted from the machine. 68 tests cannot be re-executed at all, so neither the control described below nor any replay can reach them.

Third, every detached test in the whole archive lives in these two experiments. Counting confirmed tests whose code never opens, imports or reads anything, the count is 9 by one heuristic and 15 by CC2's broader one, and on both counts every single one is in experiment 48 or 49. These are pure model written arithmetic, for instance an assertion that two hand transcribed sums are equal. If the transcription is wrong then the confirmation is empty and nothing in the system can see it. All are recorded as closed.

The 85.3 percent figure currently includes them.


## A Defect Found While Taking These Measurements

24 modern findings have a tool verdict of error or untoolable, meaning the test did not actually run. Four of them nonetheless ended in a final state.

Two of those four carry an independent fix verification, so something else legitimately closed them. The other two do not. In those two, a test that never ran wrote the verdict refuted.

A correction is owed here too. All four were escalated to a human at the moment they were mislabelled, which was verified after CC2 pointed it out. The status is still wrong and the fix is still cheap, but the phrase used in the first draft, that a finding was killed on no evidence, overstates it and is withdrawn.


## A Measurement Attempted Tonight And Withdrawn

An attempt was made to check whether the headline convergence figures survive the repairs. It reported that all eight runs had moved, and it is withdrawn. The two quantities being compared were not the same series. One is built round by round from the settled counts, the other is a parallel shadow measure kept for comparison. Taking the same statistic of each and calling the difference a change is comparing two different things.

That is the thirteenth withdrawal of the week and it happened inside the analysis of withdrawals, under exactly the same shape as the other twelve: a general claim asserted after one comparison, without first checking that the two things compared were the same thing. It is recorded rather than deleted, because the rate of that error is part of what the founder asked about.


## The Verdict

Neither position. All five panellists reached a split independently. None chose the first position outright and none chose the second. Four returned a split by date. CC2, the one that reproduced the measurements with tools rather than accepting them, returned a three way split and argued that the real fault line is the claim being made, not only the date. Its version is the one adopted here, because it survives evidence the other four did not have.

Before 3 June 2026, covering 910 final verdicts, the archive cannot show these were decided by a tool, because the mechanism did not exist. They are not thereby false. They are unaudited with respect to the founding principle, and they must not be cited as demonstrations of it. Codex's phrasing is the one to adopt: unaudited legacy results.

From 3 June 2026 on code targets, covering experiments 42 through 47, the record is substantially able to audit itself. 85.3 percent backed. 97.4 percent of closures backed. Outcome following the tool 99.8 percent of the time. Every archived series reproducing exactly on replay. The gate demonstrably switched on and never bypassed.

These stand as evidence that a test fired against the real artefact, and that the runner rather than the panel read the result. They do not stand as evidence that the test discriminated the claim, because nothing in the archive can distinguish those two cases.

Experiments 48 and 49 are excluded for the three reasons above.

So the thing that has been over claimed in the record is not that defects were found. That is well supported. It is the phrase that the findings are tool decided. That is supported for the test firing and unsupported for the test firing because of the claim, everywhere, including the modern era.

The founder's engine analogy holds, and the measurements locate exactly where it holds and where it stops. It is not a rationalisation, because the boundary is a dated commit and a configuration switch. What it does not license is citing results from before June as evidence that the principle works. They were produced before the part that demonstrates it was built. And what none of it licenses yet, on either side of the boundary, is the claim that the tests are good tests.


## What Is Still Not Known, And It Is The Important Part

Every panellist made the same point in different words. None of the above tests whether the tests themselves are any good.

All of these measurements ask whether the harness obeyed the tool. They are silent on whether the tool was right. DeepSeek put the failure mode most sharply: a test that always fires would produce exactly the pattern observed, and would also pass the control that was run yesterday. Gemini arrived at the same place from the other side: if the tests cannot recognise a repair, then the 85.3 percent is backed by noise.

Yesterday's control closed one half of that. Change something in the target that the finding does not accuse, and none of 360 tests changed its answer. The other half has never been run: repair the accused defect, and the test must fall silent.


## The Next Step

Run that second control on the archive, offline.

Four of the five panellists named it, arriving from four different arguments. Codex alone preferred building the provenance log first, and its reasoning is preserved rather than smoothed away. CC2's argument for the ranking is the sharpest: a log records which mechanism decided a question, so if the mechanism does not discriminate, the log faithfully records a worthless decision. The log is logically second, not first.

It was believed to require a live experiment, because the version built into the runner waits for a corrected copy of the document that no panel has ever been asked to supply. It does not require one. Measured tonight: 437 modern findings have a test that fired, and 367 of those also carry a proposed repair in a machine applyable form.

So the control can be run against those findings with no dispatch and no metered cost. Apply each finding's own repair to a scratch copy of the target, re-run that finding's own test, and require it to fall silent. The machinery to apply such a repair and re-run a test already exists in the project and was measured at 0.287 seconds per pair.

CC2 proposed a second route which is cheaper still and does not assume that a proposed repair is a correct repair. Most of these defects were subsequently fixed in the repository. So re-run each archived test against the commit that fixed the defect it accuses. If it still fires, it was never testing that claim. This uses only the version history and the archive and applies no repairs at all. Both routes should be run, because they fail in different ways, and agreement between them is itself evidence.

A decision rule has been taken from CC2 in advance, so that it cannot be chosen after the answer is known. If 95 percent or more of the tests fall silent on a corrected copy, the modern era moves to the first position without reservation. If 10 percent or more still fire, it moves materially toward the second.

If a substantial fraction of tests still fire after their own accused defect has been repaired, then all the measurements above show only that the harness faithfully obeyed bad instruments, and the modern era moves toward the second position after all. If they fall silent, the modern archive is evidenced from both directions, and what remains is record keeping and the live experiments.

Ranked below that, and not started. First, connect the repair based adjudication to the merge decision. It was verified tonight that no code path in the current runner writes the merged status at all, so any experiment started today would produce zero merges. Second, the typed provenance log, which turns code level provenance into per record provenance. Third, the fix for the two refusals written on a test that never ran. Fourth, resolving the confound in the correction rate. Three panellists proposed measuring corrections against the age of the code being corrected. CC2's version is better and is the one to build: group each correction by the month the claim was first asserted, rather than the month it was withdrawn. A rate measured by withdrawal month rises mechanically whenever anyone audits anything, which makes it a property of the auditing rather than of the work. A rate measured by assertion month asks the question that actually matters, which is how many of the claims made in March turned out to be wrong. Because recent claims have had less time to be caught, it needs to be paired with a survival measure: report each month's cohort at 30, 60 and 90 days, and compare August's 30 day figure against March's 30 day figure, never against March's lifetime figure.

Fifth, make the control script that was run yesterday safe to invoke without side effects. It writes its output file unconditionally, and during tonight's review a model operating under read only instructions ran it with a small limit and overwrote the committed 397 row result with a 12 row one. It disclosed this before anything else in its report and deliberately did not restore the file itself, so that the damage would be seen and the decision left to the founder. The file was restored from version control the same night.

Every figure above is reproducible offline at zero cost. The script is named track record audit, in the scripts folder of the repository, and the full technical note and the complete verbatim panel record are in the experimental notes folder, both dated 22 August 2026.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
