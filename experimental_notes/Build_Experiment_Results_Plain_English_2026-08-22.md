# The build experiment: nine of ten defects fixed by the panel, and five defects found in the instrument that judged them.

22 August 2026, 18:08 to 23:00 BST


## A Correction Added 23 August, And It Changes How The Headline Should Be Read

Nine of ten defects were fixed in the sense that a patch and a test were produced and mechanically validated. None of them are wired. The repository is unchanged.

Measured directly on the branch this morning: the withheld status has zero references in the runner, the corrected copy is still not assigned from any finding's proposed repair, the survived falsification ledger has zero references in the runner, and the dead detection channel is still hardcoded. Every accepted patch is sitting in a log file as a candidate.

So the honest headline is not nine of ten defects fixed. It is nine of ten defects have a validated candidate fix awaiting a decision to merge. That distinction is the whole difference between work done and work landed, and it is exactly the distinction this project keeps discovering it has blurred elsewhere.

A first check of this was made with a crude search that reported three of these as present. It was wrong on two of the three. The precise counts above are what stand.


## What This Was

The first experiment in this project's history designed to fix rather than to find. Six models, CC2 and Fable through the Claude command line tool, and Codex, Gemini, ChatGPT and DeepSeek through their web interfaces, were each given one defect, the file it lives in, and a definition of what done means.

Acceptance was mechanical, and no model and no assistant adjudicated it. A patch was accepted if and only if three things held. The model's new test had to fail at the starting commit. The same test had to pass once its patch was applied. And the full test suite, about 3,600 tests, had to stay green relative to the starting point.

That two sidedness is the answer to the question of how a broken instrument can be used to repair itself. The project's existing gate accepts a test merely for firing, which is one sided, and is why a test consisting of nothing but a print statement is recorded as a confirmation, and why half the archived confirmations cannot be demonstrated. Here, a test that always fails cannot pass the second condition, and a test that always passes cannot pass the first.

The tool loop fired for the first time in this project's history. Four of the six models had never been able to read a file at all. The existing toolkit offered symbolic mathematics, a theorem prover, the test runner and two code checkers, and no way to open the source they were checking.


## The Result

Nine of ten fix tasks were accepted. One was escalated to human review after being rejected at all three rungs of the ladder.

The accepted work: feeding the discrimination control from each finding's own proposed repair, accepted from CC2. Wiring the survived falsification ledger, CC2. Stopping a crashed test from writing a final verdict, Fable. The Bugzilla status vocabulary and machine readable catalogue, CC2. Shelving the load balancer with documentation marking, CC2. A dry run option for the perturbation control, Codex. Moving the memory ledger recount into the save state path, ChatGPT. Citing the frozen severity pre registration from the live queue, CC2. And explaining the 67 unmatchable repairs and 30 errored tests, Codex.

The one that went to human review asks for a change to how discrimination failures reach the escalation ladder, inside a file of 10,510 lines.

One caveat on the count. The dry run task's acceptance came from a manual re evaluation after a harness repair, rather than from the live loop, so the loop only figure is 8 of 9 and the figure including it is 9 of 10. Both are given because the difference is real.

As percentages with proper intervals: 88.9 percent with an exact 95 percent confidence interval from 51.8 to 99.7, or 90.0 percent with an interval from 55.5 to 99.7.


## The Pre Registered Test, Honoured Where It Does Not Flatter The Result

Before the first dispatch, a rule was fixed. An acceptance rate near 100 percent would mean the checks are not binding and the run should be distrusted. A rate near zero would mean the models cannot do the task.

The proposition that the models cannot do the task is decisively rejected, with a probability of about one in ten thousand million million.

The proposition that the checks are not binding is NOT rejected at conventional significance. The probability is 0.087 on one accounting and 0.096 on the other, both above the usual threshold of 0.05.

So the acceptance rate on its own does not rule out a gate that barely tests anything. Ninety percent is high. That has to be said plainly rather than buried, because the entire purpose of fixing the rule in advance is to stop a good looking number being read as more than it is.

What does establish that the checks bite is separate from the rate. First, the gate was commissioned before it was used, with ten tests, and it demonstrably refuses a test asserting merely that true is true, a test that always fails, a patch that matches nothing, a patch with no test, prose with no patch at all, and a patch that passes its own test while breaking something else. Second, eight attempts during the run were genuinely rejected because the model's patch did not make its own test pass, and the human review case was rejected by three independent writers.

The rate is consistent with a working gate. The commissioning tests and the rejections are what demonstrate it.


## The Composition Check, And What It Caught

The gate judges each candidate independently against the same starting point. That is the right unit for judging one model's work and says nothing at all about the set. Assuming that because each part was verified the whole is verified is a composition fallacy, so the set was proved separately.

Six of the eight composed patches apply cleanly together. Two conflict: their search text no longer matches once two earlier patches have landed, because four separate patches touch the same 10,510 line file.

The six that do apply produce all 56 of their tests passing together, and a full suite of 3,668 passing with zero failures the starting point does not already have.

The two conflicting patches are not wrong. They need rebasing onto the combined tree, which is ordinary integration work and not a defect in the models' output. Had the composition step been skipped, this would have surfaced later, on the branch.


## Five Defects In The Instrument That Judged The Models, All Mine

Every one of them rendered a harness failure as a model failure.

First, the third acceptance condition assumed a green test suite instead of measuring it. One test passes in the repository and fails in a fresh checkout of the same commit, because it scans the archive and the archive directory is not tracked. Every task would have been falsely rejected, the run would have reported near zero acceptance, and near zero is this harness's own pre registered signal for the models cannot do the task. The very first model output this harness ever judged was judged wrongly, in the confident direction. Codex's work was valid.

Second, a blanket staging command committed a model's direct writes to the repository. Twice. A model working on the human review task edited the working tree instead of returning a patch, and 157 lines of ungated code went into a commit whose message did not mention it. It happened again while the first instance was being written up. It also poisoned the starting point, so a later rejection was an artefact of that contamination rather than a failure by the model.

The root cause is a hole in an existing ruling. On 29 July this project ruled that file writing tools be removed from panel dispatch, to make the frozen target guarantee true. That ruling was verified as done earlier the same day by checking the granted tool list for the write and edit tools. The list grants a shell, and a shell is a superset of write. The comment beside that list reads no file modification, which is false. The frozen target guarantee has been untrue in every panel dispatch this project has ever run through that route.

The fix already existed and had never once been called. A function to confine panel dispatches to a chosen directory sits in the dispatch layer for exactly this purpose, and its own documentation says that failing open would put the panel back in the repository, which is the exposure it exists to close. Dispatches now run inside a disposable copy. Verified by test: a simulated model write lands in the copy, and does not reach the repository.

Third, the file reading tool prefixed every line with a line number, which made a byte exact search block impossible. Codex stripped the digits and kept the two space separator, so every line it returned carried two extra spaces of indentation. Measured: its block matches the file exactly after removing two leading spaces from every line. Its code was correct. The reader was fixed rather than the matcher, because a fuzzy match would let a patch land somewhere it was never meant to, which is far worse than a rejection.

Fourth, a test that fails to import is labelled as a fix that did not work. Logged during the run and deliberately not paused for, because the second condition rejects it either way and it cannot produce a false acceptance. The defect persists and the model's test does not import are different findings and must not look alike.

Fifth, the results file is overwritten by every resume. Worked around: both the report and the composition check rebuild from the append only run log, which is the reason a run log is append only.

Five of twenty five attempts were decided by one of these defects rather than by the model's work. Any ranking of the models drawn from this run would be an artefact of that, and none is offered.


## The Round Robin Objection, Demonstrated

The founder challenged the use of round robin assignment as belonging to the earliest stage of this project, and asked why it was thought necessary. It was not, and the run produced a concrete demonstration.

One task asks a model to edit a specific document. Round robin handed it to DeepSeek, the one route in the panel with no tool loop, which therefore cannot read the file it is being asked to edit. It guessed at the content and the search block did not match. That is a configuration mismatch, not a model failure.

The project already has a capability aware routing module. It is deliberately independent of any particular runner so a caller can plug into it, it carries an ordering derived from measurements on the seven hardest residual findings from an earlier experiment, and its own documentation states that it exists to replace flat parallel dispatch that had collapsed into identical treatment. A flat ladder was hand rolled instead, which reimplemented an existing mechanism as the very thing that mechanism was written to replace.


## The Inventory Check Is 3 Of 34 Done

Gemini verified three instruments by running them against known good and known bad inputs, and said plainly that it could not reach the other 22 within its tool budget. That honesty is the right behaviour.

The first of the three was reproduced independently and stands: the gamma estimator returns zero for one input and 0.35765 for another, and Gemini reported 0.357, which is a truncation rather than an error. The two inputs give different answers, which is what commissioning requires. The other two take a configuration object and their one line calls could not be replayed exactly, so their values are recorded as unverified rather than accepted on the model's word.

A further defect of mine surfaced here: the report only path bypasses the gate entirely, so this submission was recorded without scrutiny, and the test it carried merely asserts that three keys exist in a dictionary it also added them to. That is precisely the empty test the gate refuses everywhere else.


## The Quarantined Work Could Not Be Fairly Judged, And That Is Also Mine

The two direct writes were quarantined rather than deleted, because the work may well be sound even though the route was wrong, and deleting it would punish a model for a hole I left open. Converted into candidate form and put through the gate, it was rejected because its search text did not match.

That is a verdict on my diff conversion, not on the model. The original applied to the tree as it stood when it was written, and converting it against a different starting point does not match. Its test also fails to import. The underlying work remains unadjudicated.


## What Actually Got Fixed

The most important is the first. The discrimination control has existed inside the runner, with eight distinct outcomes and three self checks, and had never fired once in this project's life, because it waits for a corrected copy of the document that nothing ever supplied. It is now fed from each finding's own proposed repair. The instrument that separates a demonstrated confirmation from an asserted one is, for the first time, connected to something.

The second wires the survived falsification ledger, which records that a claim was tested and stood, closing the gap where a clean control run produces an absence that is indistinguishable from a dispatch failure.

The rest: a crashed test can no longer write a final verdict; the Bugzilla design has its status vocabulary and a machine readable catalogue, having had zero lines of implementation before tonight; the load balancer is shelved and marked; and four smaller items are closed.


## Where This Leaves Things

Nine of ten defects fixed, mechanically verified, none of it resting on my word or anyone's.

Six compose cleanly. Two need rebasing.

Nothing is merged. Accepted patches remain candidates, the fixes go to human review rule stands, and the founder decides what ships.

One task needs a ruling. Three independent writers failed it in the same way, which points at the task rather than the writers: either it is genuinely hard, or my brief for it was under specified.

And the frozen target hole is closed for this harness only. Every other panel dispatch in this project still runs with a shell inside the repository.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
