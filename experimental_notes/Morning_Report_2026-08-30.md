# Morning Report. The Repair Machinery Was There All Along, And Using It Found Something Big.

2026-08-30, 00:50 BST (UTC+1)

You were right that we already had the repair machinery. You were right about rho. You were right about my briefs. And following your machinery question all the way down found a defect that had been quietly corrupting model fixes and then blaming the models for the result.

## The Login, Which You Already Fixed

Both reviewers failed within ten seconds early on. The visible error mentioned an untrusted workspace, which was a red herring; the real line underneath was that the login session had expired. You logged back in at one minute past one, I detected it, and the panel was re-dispatched forty seconds later carrying your two questions: whether canaries can be re-pointed at churn rather than silence, and whether the repair I built is the right one.

## And Now The Part I Got Wrong, Which Is The One You Should Read Twice

Earlier tonight I saw a line in the failure log saying the working directory was the real repository rather than a sandbox. I suspected the isolation had failed and the reviewers had been let loose in the live tree. I checked, concluded it was just the cleanup step running afterwards, and told you it was a false alarm.

It was not a false alarm. It was real, and I reported it to you as nothing. Twice.

The second reviewer opened its review by checking that claim instead of believing it, and found itself in the actual repository, on the main branch, with shell access. It built its own sandbox and confirmed the tracked files were untouched before and after, so nothing was damaged. But it should never have been there.

Here is what happens. The two reviewers run at the same time, and the setting that says which directory they work in was one shared value rather than one each. Each reviewer sets it to its own sandbox and clears it when finished. So when the first reviewer finished at half past one, it cleared the setting for the second, which was still running. Ten minutes later that second reviewer hit its time limit and retried, and the retry ran with no sandbox at all.

The reason I cleared it wrongly is worth more than the fault. I checked that the sandboxes had been created. They had. I never asked whether that setting survived one reviewer finishing while the other was still going. I checked one thing and concluded about all of them, which is the exact failure this project keeps naming and which I have now done three times in one night in three different places.

It is fixed. Each reviewer now owns its own value, so one finishing cannot unsandbox another. Reverting the fix makes the new test fail, so the test is real rather than hopeful.


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

246 gave a clear answer. 120 fixes cure the defect their own test demonstrates. 126 do not. About half fail, and I have to be careful with that word, because when I finally ran the statistics this morning the honest range is 45 to 57 percent. That range includes exactly half, so "more than half", which is what I wrote to you last night, is not something the data supports. "About half" is.

Before you take that number to mean half our fixes are bad, please read this next part, because I do not think it means that.

The check measures whether a pair is consistent: the fix, and the finding's own test. When the test still fires afterwards, either the fix is incomplete or the test does not test what the finding claims. This cannot tell those apart. A real share of these is likely to be the test being wrong rather than the fix. And none of these fixes was ever applied or reviewed. They are proposals from finished runs, and a proposal that turns out not to work is a normal research result, not a scandal.

I also tried to break my own finding before reporting it. The obvious way it could be an artefact is if the fixes were not really being applied. They were: not one of the 246 changed zero lines, none was a wholesale file replacement, and the failing fixes change a median of five real lines. They genuinely apply and genuinely fail to silence their own tests.

Why had nobody measured this? Because the only tool that asks this question only ever looks at findings that have a near duplicate, since its real job is deciding whether two findings are the same. Across the archive, 382 findings carry both a fix and a test, and only 85 have ever been in scope for anything. The other 297, which is 78 percent, had never been checked by any instrument at all.


## The Defect Underneath, Which Is The One That Worries Me

Twelve of the unexplained cases turned out not to be model failures at all.

When a model proposes a fix it marks the passage to find and the text to put in its place. The code that performs that substitution was searching for the old text anywhere in the file, including in the middle of a line. So when a model's marked passage had lost its leading spaces, the search matched partway into an indented line, the replacement was inserted there, and the original line survived alongside it. The result was a file with a duplicated line that will not even parse.

Twelve archived fixes were mangled this way. And then the mangled result was judged, and recorded, as though it were what the model had proposed.

It is fixed. A patch that leaves the file unable to parse is now refused rather than returned, and the twelve silent corruptions became twelve honest "this fix did not apply". The guard stands aside when the original was never Python, because we have prose targets too.

I tried a stricter rule first, anchoring every match to the start of a line. I measured it and threw it away: it refused 210 of the 313, because models routinely strip indentation and most of those matches are harmless. The rule I kept is the simplest one that separates the two cases.

The headline figures did not move, which is the reassuring part. Half the fixes failing was never resting on the corrupted twelve.


## A Correction To A Number I Gave You Earlier Tonight

I reported that nine tests in the archive never read their target at all. That figure is an overcount and I am withdrawing it. The number I can defend is four.

I found this by running a second, independent instrument over the same question and getting a disagreement on one finding. Rather than pick a side I chased it, and the first instrument turned out to have a false alarm mode.

Here is what happens. Several tests begin by checking they are looking at the right file before they test anything, using an assertion. When I replaced the file with an unrelated one to see whether the test noticed, that opening check fired, exactly as it should. But the falsifier gate treats any assertion failure as a demonstration that the defect is present. So a test saying "I cannot examine this file" was recorded as "the defect is confirmed".

Then I corrected my correction, because the first one was also wrong.

I had reduced nine to four by reading the four uncertain tests and sorting them by their shape. That was reasoning, not measurement, and it was wrong in the cautious direction. So I ran them instead. All four produce their real demonstration, printing the finding's own message, against a file that shares nothing with their target. They genuinely never look.

The measured figure is eight of 372, which is 2.2 percent. One of the original nine, and only one, was my false alarm. The confound stands for the other eight and I have named them in the notes.

The sequence is worth your attention more than the number: nine asserted from a single instrument without cross-checking, four inferred from reading source code, eight measured by running it. Only the third was evidence. Both of the first two were me substituting reasoning for the tool output, once in each direction.

What sits underneath is worth more than the correction from 9 to 4, and it is the same component I flagged as the one genuinely uncommissioned piece that matters. A test whose setup fails is recorded as confirming the defect. That is not a fault in any one test. It is the falsifier gate itself, which cannot tell a setup check from a real demonstration because both arrive the same way. That goes to the panel.


## Re-Judging The 133 Pairs, Now That Both Defects Are Repaired

Both of tonight's defects contaminated the original judgement of those pairs: the fall through that let a crashed test produce a verdict, and the applier that corrupted patches. So I re-ran the whole set through the safe overlay version.

Of the 133 pairs, 90 could be re-checked and 43 could not. Of the 23 that were originally judged the same defect, 2 survive, 3 fail, and 18 could not be re-checked at all.

I want to be careful with that. The 43 are not refuted. They are unchecked, and reporting them as refuted would be exactly the confident direction error I keep having to correct.

The three failures are the applier repair working, and they close a chain I would want you to see. All three involve one finding whose proposed fix, run through the old applier, produces a file that does not even parse. So: the applier splices badly, the patch corrupts the file, the corrupted file is judged, the tests fall silent on wreckage, a false "same defect" verdict is recorded, and that verdict is exactly the evidence the merge step requires. Merged is permanent. Two of the original 23 rested on a corrupted patch.

Had merging been switched on before tonight, that is the route by which it would have destroyed findings. Which is why I am glad it was not, and why I have still not switched it on.


## Why 43 Could Not Be Checked, And What It Would Take

Those 43 are experiments 48 and 49, and their review documents are simply not on the disk any more. They were deliberately moved out of the repository on the eighteenth of August, in the commit that closed the answer key exposure. Its own message says why: reviewing models carry shell access, and a key sitting next to the document with a guessable name made every planted claim findable with a single directory listing, at perfect precision, defeating three rounds of hardening.

They are recoverable. I confirmed the documents exist in that commit by listing filenames only, reading no content. And I re-confirmed something you should know is still true: that commit, and the one beside it, are reachable from the experimental branch and from nowhere else. That branch still must not be deleted before the encrypted bundle is verified.

I have not extracted them, deliberately. They are seeded exam documents, and materialising them re-creates the exposure that commit closed. Your own rule allows an unencrypted study copy once an experiment has run, and both have run, so it is permissible. But it sits on the security boundary, and that is a decision for you awake rather than me at one in the morning. If you rule yes it needs no change to the repository at all: extract to a scratch directory and point the checker at that.


## The Other Things You Ruled On

Merge. You said wire it and prefer the second reviewer's answer, and that answer was that the receiving end is finished but the tool that supplies the evidence needs rebuilding, because it edits the live document. That obstacle is now gone: the same overlay makes it safe to run during a run. I validated it against the existing offline tool on every cleanly decided pair it can reach, and they agree ten times out of ten. What I have not done is switch merging on. The merged state is permanent, with no way back, so a wrong merge deletes findings for good. Turning it on should be your call with your eyes open, not mine at one in the morning. It is one line when you want it.

The nine tests that never read their target are recorded as a confound in the notes, not struck, exactly as you asked. Nothing was deleted. The caveat now travels with them.

Uncommissioned machinery. You asked what is left. The honest answer is better than it was: 30 of 34 components are now genuinely commissioned, up from 27, because three had been repaired on Thursday and I had left their flag showing failure, so the instrument that measures instruments was under reporting its own repairs. I re-measured all three rather than assuming. Of the four remaining, one is shelved by your own ruling, one you have said you want removed, one is an offline script, and only one genuinely matters: the falsifier gate.

Experiment 52 roles. You said I was conflating a panel review with being a panel member, and that finding has never been my role. You were right, and the record settles it in a single query: I am the source of zero of 1,154 archived findings. I disqualified myself from a job I have never held. The objection is withdrawn and the specification that carried it has been corrected rather than left standing.

The six places I made you guess. All answered plainly in a note called Six Things I Made You Guess At, including what a severity cutoff actually is, what the frozen scope document would be for, and the sentence about containment that I now agree was unreadable.

Your briefing criticism. You said I ask the panel to find problems and never to propose fixes. I checked all three briefs before accepting it: zero of three asked for a repair. You were exactly right. The new brief asks for the fix and for the reviewer's confidence in it.


## The Panel Reported, And It Found The Most Important Thing Of The Night

Both came back. Fable after 29 minutes, the second after 63, having hit its time limit once and retried.

On the canaries you were right and so was the design. Fable's judgement is that your correction invalidates what the module said it was for, not what it actually measures. Detection capacity is exactly what separates a panel that has genuinely run out of things to find from one that has stopped reading, because both look identical to the gate. It rewrote the module's stated purpose, added a contributory layer that reports three states rather than a yes or no, and built it so that it structurally cannot block anything, with a test asserting that no result it produces carries a field a gate could act on.

It also caught a hard constraint I had missed entirely and that you would have caught: a canary must never be planted in the live document or mid run, because that changes what the other measures are measuring and destroys comparability between rounds. It has to be a separate one off probe, run when the gate first says converged, against a copy with no history.

Its recommendation is keep, not retire, with a named condition for retiring it later: run one probe in Bench Run 2 and measure whether it actually separates the two states. If it does not, retire it then, with data, rather than now without.

Then it attacked my repair proposal and landed three hits, one of which is the most important finding of the night.

The first two I had already found myself during the evening, which is reassuring rather than otherwise: the offline tool I cited as precedent does not use a safe copy, it edits the live document, and a plain copy elsewhere is invisible to most tests because they load their target as a module.

The third is new and it matters a great deal.

Since the 23rd of August there has been a step that builds the control's "corrected" version of the document from the finding's own proposed fix. It is allowed to skip an ownership check, and the code says why, in these words: a finding's own proposed fix corrects this claim by construction.

Tonight I measured that assumption. It is false about half the time. 126 of 246.

So when the fix is the broken half, the control looks at a document that was never actually corrected, sees the test still firing, and concludes the test is defective. It then stamps the test as non discriminating, marks it a mechanical fault, escalates it to you, and un-confirms a finding that was demonstrated. Three false statements about a working instrument attached to a real defect. And the un-confirm is not behind the safety switch you might expect; that switch guards a different place.

The comment above that code names this exact harm, minting a false fault against a sound instrument, and then rules it out using the premise that measurement refutes.

Now the part that matters for how alarmed to be, which I checked myself and the reviewer did not report. It has never happened. Across every archived run, that stamp appears zero times. The step was wired on the 23rd of August and the only runs since are two that halted at round zero. So no past result is contaminated and nothing needs re-scoring.

But Bench Run 2 is its first real exposure, and at a measured one in two rate for the triggering condition it would not be a rare event. This misattribution is what I would want settled before that run starts.

Fable built a repair for it in its sandbox, which is thrown away by design, so the code did not survive but the design did and I have written it down. I have not applied it. It supersedes an assumption from August, it changes what a verdict means, and the reviewer itself lists three things it says need your ruling, including that the remaining ambiguity now fails in the opposite direction. That is a decision, not a repair.

On the smaller question of tests that break in the final round, it measured the actual population rather than arguing: zero to two on every healthy run, and the large counts are all from an old parsing era or from a defect already fixed. Its recommendation is not to build anything, and to switch on the existing routing mechanism instead if a real run ever shows more. I think that is right and it is the kind of scope discipline I have not always shown.


## The Second Reviewer Found Three More, And Disagreed With The First

It opened by checking the brief's first sentence rather than believing it, which is how the sandbox failure above came to light.

Then it found that our disposable review copies were carrying the repository's history into themselves. Every such copy differs from the real file by exactly the change being tested, so with the history reachable, a single command inside that copy returns the original file and another returns exactly what was changed. That is the planted material recoverable perfectly, with no key needed, and it is precisely the leak the canary module refuses to seed a tracked document in order to prevent. It arrived by a route that guard could not see.

I verified it, and it is worse for me than for the project: the fix checker I built earlier tonight runs every single probe through those copies. The instrument I built to measure fixes was handing out the answer key alongside the question. Fixed and tested.

It had a second effect that decides the canary question. The canary module refuses to plant anything in a tracked document, and it checks that by looking for the marker that identifies one. The copy carried that marker, so the module was refusing the one place where planting could ever have been legitimate. So the design the first reviewer proposed was, until tonight, mechanically impossible to run.

Its third finding I have written up for you rather than acted on. When our machinery runs from a disposable copy it wrongly rejects seventeen honest tests as security violations, because it works out where the repository is from its own location. The reviewer's fix widens the list of places a model written test is allowed to read, and that list is the guard we closed after the one experiment we had to throw away, when a model opened the scoring key. It attacked its own widening from three directions and all three still refuse, but it says plainly it did not try them all. Widening that guard at half past two on three probes, with nobody else having seen the change, is not mine to do. There is a more conservative alternative in the note that widens nothing.

And the two reviewers disagree about the canaries, which is the most useful page of the night.

The first says the distinction is real and the instrument measures the right thing. The second proved, rather than argued, that the module has no way of knowing when anything happened: the words for our other measures appear zero times in it, nothing carries a round number, and it built two artificial panels, one genuinely exhausted and one purely recycling, and got byte identical output from both. I reproduced that myself and it is exactly right.

My own reading is that they are answering different questions and both answers stand. The second is right that the module as written cannot tell the two apart. The first is right about the principle. What closes the gap is the first reviewer's own protocol, which neither of them connects because they wrote independently: the sense of time comes from when the probe is run, not from the module. One separate probe at the moment the gate first says converged needs no round number, because there is only one round. So the second reviewer's demonstration is not an argument for scrapping it. It is an argument that the module must never be handed a whole run's findings, which is exactly what the first reviewer's protocol forbids.

Neither can answer the question that actually decides it: does a recycling panel really miss a freshly planted defect? That is one experiment in Bench Run 2.


## You Asked Whether I Have Been Using Your Command Set. I Measured It. You Are Right.

You said you had seen little evidence of it despite calling these commands frequently, and that if true it is a bigger issue than any individual error. Rather than agree or defend, I counted, using the session record on disk.

You issued 118 of these commands across the session. Analyse 49 times, discuss 48, and the ones that matter most here: five calls for the full falsification cycle, and five for the mathematical and scientific tools.

Last night I made 226 tool calls. Three of them touched a mathematical or statistical tool. That is 1.3 percent. All three were the same tool, on the same single proof, inside one 40 minute block at the very start of the night. For everything after that, the fix checker, the half of all fixes figure, the applier defect, the re-judging of the pairs, the counting of tests that never read their target, I used none at all.

So the answer to your question is yes, you are right, and here is the proof that it cost something concrete.

This morning I ran one statistical check on the headline figure I gave you last night. 126 fixes out of 246 do not cure the defect their own test demonstrates. I reported that to you as slightly more than half. The honest range, once computed, is 45 to 57 percent. That range includes exactly half. So "more than half" is not something the data supports. "About half" is. One command, that I should have run last night and did not, falsified my own headline this morning.

I want to be precise about the diagnosis though, because I think you are right in substance and slightly off in mechanism, and the difference matters for fixing it.

Most of last night's errors were not failures to use mathematical tools specifically. They were failures at the same step one level up: the part of the cycle where you gather evidence with whatever tool fits before concluding anything. I said the repair machinery was not connected after reading one file and never opening the one beside it. I cleared the sandbox alarm after checking the copies were created and never checking whether the setting survived one reviewer finishing. I corrected nine to four by reading four tests and sorting them by their shape, when running them gives eight.

Every one of those was recoverable by running something rather than reasoning about it. The mathematical tools are one instrument for that. Searching properly is another. Actually executing the code is a third. The common root is a single sentence, and it is already written in your own directives: the tool output is the evidence, and reasoning selects and interprets it but never substitutes for it.

I have written that up as a standing correction in my own memory, with the measured figures in it, so it is not a promise but a record.


## What Remains For You

First, the five items you asked me to close this morning are done. The three vagueness findings in notes I had linted the spoken version of but never the written one. The memory index, which had nothing in it since the 26th, so four sessions including last night were missing from the file that rebuilds context. The onboarding document, which still claimed all four stopping components were commissioned when one of them had been measured otherwise two days earlier. The audit tool I built to catch exactly that class, which missed this instance because it held three hand written claims and no general rule, and now reads the instrument record itself. And the fix checker, which was built, tested, used by two scripts, and called by nothing that runs. It is wired now, capped at five checks a round, structurally unable to block anything, and with a test that fails if either gate function so much as mentions it.

The key files are still in plain text and still need your passphrase.

The push, which you ruled goes last. It is now over 140 commits spanning a week, not one night, so it deserves you awake.

Five decisions, in the order I would take them.

First and most urgent, the misattribution described above, because Bench Run 2 is when it stops being theoretical. The design for the repair is written down and waiting.

Second, whether to switch merging on. I would not yet. Of the 23 pairs originally judged the same defect, only 5 could be re-checked with the repairs in place: 2 survive and 3 fail. Merged is permanent.

Third, whether to recover the two missing exam documents from the branch, so the 43 unchecked pairs stop being unknown. That sits on the answer key boundary, which is why it is yours.

Fourth, whether to widen the read allowlist so our machinery stops rejecting honest tests when it runs from a disposable copy, or take the conservative route in the note instead. That guard is the one closed after the excluded experiment, which is why it is yours.

Fifth, whether the fix check should feed the model facing channel automatically or stay a measurement.

Nothing is on fire, the suite is green, and everything is committed.


Written under CDSFL note standard v1.7 (26 August 2026).