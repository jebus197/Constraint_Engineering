# Morning Report. The Repair Machinery Was There All Along, And Using It Found Something Big.

2026-08-30, 00:50 BST (UTC+1)

You were right that we already had the repair machinery. You were right about rho. You were right about my briefs. And following your machinery question all the way down found a defect that had been quietly corrupting model fixes and then blaming the models for the result.

One thing needs you before anything else can continue, and it is small: the command line tool is logged out. More on that at the end.


## First, The One That Blocks Things

Both panel reviewers failed within ten seconds tonight. The visible error mentions an untrusted workspace, which is a red herring. The real line underneath is that the login session has expired and could not be refreshed. I checked it directly and the tool reports itself as not logged in.

That blocks every panel dispatch, including the brief I wrote tonight carrying your two questions: whether canaries can be re-pointed at churn rather than silence, and whether the repair I built is the right one. That brief is written and ready and takes one command to send once you are logged back in.

I cannot log in. It needs your credentials and that is not something I will ever do.

One correction I want to make plainly, because I nearly reported a security problem that does not exist. When I first read the log I saw a line saying the working directory was the real repository rather than a sandbox, and I thought the isolation had failed and the reviewers had been let loose in the live tree. It had not. That line is the cleanup step running afterwards, and both reviewers did run inside their sandboxes. I checked before saying anything, and I am telling you about the false alarm because a scare that turns out to be nothing deserves the same clarity as a real one.


## Rho Is Now A Contributor, Not A Veto

Your ruling, and you were right about the inversion. If a measure exists to detect that no new discoveries are being made, and a flattened decay curve says the same thing, then the two together are evidence the space is exhausted. Blocking on it made the churn measure fight the outcome it certifies: the closer a run got to genuine convergence, the closer it got to being refused for churning.

Two places were doing the blocking. One added it to a list of failures. The other was worse: it was an early exit that fired before the two sided gate was even consulted, so a run could satisfy both halves of the gate and still be turned away for exactly the quiescence the gate exists to certify.

Both removed. Nothing is hidden by this. The churn measure is still computed, still recorded, and now appears on every verdict either way, so you can always see it.

You asked whether I tested the fix properly, so here is exactly what I did.

I proved three things formally. First, the new rule can never converge without both halves of the gate. Second, nothing that converged before stops converging, so nothing is lost. Third, and this is the useful one, exactly one situation changes: gate satisfied and churning at the same time. That is precisely the case your ruling was about and nothing else moves. The blast radius is one state.

Then I checked it against the real archive rather than trusting the proof. Of 21 runs carrying a churn series, exactly one was ever affected, and it is the run the reviewer found on Thursday.

Two existing tests asserted the old rule and failed. I did not delete them. I inverted them, so the change of rule is visible where the old rule was written down, and I added the guard that replaces the veto: a run still producing critical findings must not converge, whatever the churn measure says.


## Your Machinery Question, Answered Properly, And I Was Wrong Twice On The Way

You asked why the existing machinery is not being used to detect a bad fix and send it back to the model.

My first answer was that the feedback machinery exists but is not connected. That was wrong, and I withdrew it within the hour. The feedback channel is built, switched on by default, and already tells a model in plain words that its test did not run to a verdict and to rewrite it so it runs. Your own "check your work" line, already in the code and already live.

My second answer was that a fix is never applied and re-tested during a run. Also wrong. There is machinery that takes a proposed fix, applies it to a disposable copy, and verifies it, in flight, today.

I want to be honest about how I got that wrong, because it is the same error you have caught before. I read one file, found a switch set to off, and concluded an absence. I never opened the file next door. Worse, the evidence was already in my hands: one of the reviewers had said it plainly two days ago, in a document I had read and filed myself.

The real gap is narrower and more interesting. What runs today asks whether a fix broke anything. It runs the linters and the project's own test command against the copy. It never asks the one question that matters: does this fix actually cure the specific defect this finding claims?

That is the condition that leaves findings undecided, and it was invisible.


## And The Safe Way To Test A Fix Already Existed Too

Here is where your instinct was most right.

The obvious way to answer that question fails, and I measured why. You cannot just put the patched file somewhere else and run the test, because most tests reach their target by loading it as a module by name, not by opening a path. I counted: 57 of 70 in one run. They would all load the original, see no change, and report every fix as useless. Confidently and wrongly.

And the offline tool that does this properly cannot be used during a run, because it edits the real document under review and puts it back afterwards. The runner checks that document for tampering every round and would object every single time, and a crash in the middle would leave the article damaged.

So I went looking for how the project already solves this, and it does. There is a mechanism built in August for a different purpose that creates a complete disposable mirror of the repository, identical except for one file, so that module loading resolves into the mirror and the real tree is never touched. It even carries a probe that checks whether the mirror was actually load bearing for that particular test, and refuses to give an answer when it was not, rather than giving a confident wrong one.

It was built for one job and never reused. That is the whole answer to your question.


## What It Found

I built the check on that mechanism and ran it across every archived finding that has both a fix and a test: 313 of them.

246 gave a clear answer. 120 fixes cure the defect their own test demonstrates. 126 do not. Slightly more than half fail.

Before you take that number to mean half our fixes are bad, please read this next part, because I do not think it means that.

The check measures whether a pair is consistent: the fix, and the finding's own test. When the test still fires afterwards, either the fix is incomplete or the test does not test what the finding claims. This cannot tell those apart. Given that nine tests in this same archive were separately measured never to read their target at all, a real share of these is the test being wrong rather than the fix. And none of these fixes was ever applied or reviewed. They are proposals from finished runs, and a proposal that turns out not to work is a normal research result, not a scandal.

I also tried to break my own finding before reporting it. The obvious way it could be an artefact is if the fixes were not really being applied. They were: not one of the 246 changed zero lines, none was a wholesale file replacement, and the failing fixes change a median of five real lines. They genuinely apply and genuinely fail to silence their own tests.

Why had nobody measured this? Because the only tool that asks this question only ever looks at findings that have a near duplicate, since its real job is deciding whether two findings are the same. Across the archive, 382 findings carry both a fix and a test, and only 85 have ever been in scope for anything. The other 297, which is 78 percent, had never been checked by any instrument at all.


## The Defect Underneath, Which Is The One That Worries Me

Twelve of the unexplained cases turned out not to be model failures at all.

When a model proposes a fix it marks the passage to find and the text to put in its place. The code that performs that substitution was searching for the old text anywhere in the file, including in the middle of a line. So when a model's marked passage had lost its leading spaces, the search matched partway into an indented line, the replacement was inserted there, and the original line survived alongside it. The result was a file with a duplicated line that will not even parse.

Twelve archived fixes were mangled this way. And then the mangled result was judged, and recorded, as though it were what the model had proposed.

It is fixed. A patch that leaves the file unable to parse is now refused rather than returned, and the twelve silent corruptions became twelve honest "this fix did not apply". The guard stands aside when the original was never Python, because we have prose targets too.

I tried a stricter rule first, anchoring every match to the start of a line. I measured it and threw it away: it refused 210 of the 313, because models routinely strip indentation and most of those matches are harmless. The rule I kept is the simplest one that separates the two cases.

The headline figures did not move, which is the reassuring part. Half the fixes failing was never resting on the corrupted twelve.


## The Other Things You Ruled On

Merge. You said wire it and prefer the second reviewer's answer, and that answer was that the receiving end is finished but the tool that supplies the evidence needs rebuilding, because it edits the live document. That obstacle is now gone: the same overlay makes it safe to run during a run. I validated it against the existing offline tool on every cleanly decided pair it can reach, and they agree ten times out of ten. What I have not done is switch merging on. The merged state is permanent, with no way back, so a wrong merge deletes findings for good. Turning it on should be your call with your eyes open, not mine at one in the morning. It is one line when you want it.

The nine tests that never read their target are recorded as a confound in the notes, not struck, exactly as you asked. Nothing was deleted. The caveat now travels with them.

Uncommissioned machinery. You asked what is left. The honest answer is better than it was: 30 of 34 components are now genuinely commissioned, up from 27, because three had been repaired on Thursday and I had left their flag showing failure, so the instrument that measures instruments was under reporting its own repairs. I re-measured all three rather than assuming. Of the four remaining, one is shelved by your own ruling, one you have said you want removed, one is an offline script, and only one genuinely matters: the falsifier gate.

Experiment 52 roles. You said I was conflating a panel review with being a panel member, and that finding has never been my role. You were right, and the record settles it in a single query: I am the source of zero of 1,154 archived findings. I disqualified myself from a job I have never held. The objection is withdrawn and the specification that carried it has been corrected rather than left standing.

The six places I made you guess. All answered plainly in a note called Six Things I Made You Guess At, including what a severity cutoff actually is, what the frozen scope document would be for, and the sentence about containment that I now agree was unreadable.

Your briefing criticism. You said I ask the panel to find problems and never to propose fixes. I checked all three briefs before accepting it: zero of three asked for a repair. You were exactly right. The new brief asks for the fix and for the reviewer's confidence in it.


## What Remains For You

Log the tool back in. One command, and it unblocks the panel.

The key files are still in plain text and still need your passphrase.

The push, which you ruled goes last. It is 116 commits spanning a week, not one night, so it deserves you awake.

And two decisions when you are ready: whether to switch merging on, and whether the fix check should feed the model facing channel automatically or stay a measurement.


Written under CDSFL note standard v1.7 (26 August 2026).