# Morning Report. The Panel Refuted Me Twice, And Both Refutations Matter.

2026-08-28, 03:46 BST (UTC+1)

You were right that the earlier report was thin. This one is not. Both panels were dispatched, and the first has already overturned two claims I made to you yesterday.

This is the one to read. There is a second file next to it, Overnight Four Rulings Answered, which holds the long-form answers to the four questions you asked and the exact commands for the key encryption. Everything in it that you need to act on is repeated here, so read this one first and open that one only if you want the working.

One piece of housekeeping: there is a stray 162 byte file in the folder called tilde dollar e underscore Four underscore Older underscore Rulings. It is a lock file Word leaves behind when a document is opened. It is junk and safe to delete, but it is yours rather than mine so I have left it alone.


## Both Panels Dispatched, And They Cost Nothing

I had told you these dispatches cost money. That was wrong in the same way the experiment 52 error was wrong: CC2 and Fable both run on your Max plan through the Claude command line interface. No metered cost. The metered routes are Codex, Gemini, ChatGPT and DeepSeek, which is the five model panel, not this.

Each reviewer runs inside a throwaway git worktree. They can read the repository and run its tests freely, but nothing they write escapes. That guard exists because on the twenty second of August a model edited the working tree during a dispatch and a blanket staging command committed it.

Both briefs and both sets of results are now versioned in the repository rather than living only in the ignored log tree, because the question asked is half the provenance of the answer.


## The First Panel Refuted My Empirics, And The Correction Makes The Finding Worse

I told you the rho churn flag had never fired, and that the closest any run came was experiment 43 at a rolling average of 0.287 against a threshold of 0.25, a margin of 0.037.

That is wrong, and both reviewers caught it independently.

Fable checked every round of every archived report rather than the final three rounds I happened to sample. It found experiment 42, the take up slack run, at round 12 with a rolling average of 0.1921. That is below the threshold at a round where churn is eligible to fire. Under today's code that run trips churn.

So the trapdoor is not something a future run might reach. The archive already contains a run that crosses it.

My 0.287 figure was only correct within the window I looked at, which is precisely the error I have made repeatedly this week: measuring a subset and reporting it as the whole. Experiment 43's true minimum is 0.1587 at round 7. The runner's own shadow floor comment already recorded corrected averages of 0.2176 for experiment 46 and 0.1944 for experiment 48, both under the threshold, and I did not read it.

CC2 reached the same verdict independently: mechanism confirmed, empirical claim refuted. Two reviewers, separately, each running the archive themselves. That is replication rather than agreement, which is the only kind of concurrence this project accepts.

Both also confirmed something I had traced only halfway. The churn flag vetoes both convergence paths, not just the critical quiescence one. I had followed it into a single gate and stopped.


## The Second Refutation: The Merge Evidence Base Is Half What I Said

I told you the merge path could be wired to counterfactual repair because the tool had already produced 23 verdicts of SAME in both directions.

Fable audited those 23 rows rather than taking the summary count, which is what I did. Only 11 are clean. The other 12 carry at least one leg that ERRORed, and an errored leg is an equipment failure, not a verdict. So the evidence base is 11, not 23, and my number was overstated by roughly half.

Its recommendation, which I think is right: before wiring anything, tighten the adjudicator so that SAME requires a genuine refutation on all four legs and any error disqualifies the pair. Otherwise the first thing the merge path would do is delete findings on the strength of equipment failures.

It added a second point I had missed entirely. MERGED is a terminal status with no way back. Both REFUTED and CLOSED can be reopened; MERGED cannot. So a wrong merge is unrecoverable, which raises the bar for the evidence considerably.


## Following The Panel Finding Into The Code Made It Three Times Bigger

Fable reported 12 contaminated rows. I did not take the figure of 12 on trust. I went and looked at the function that produces the verdicts, and the hole is worse than 12.

The line that returns the verdict SAME was the fall through. Anything that was not a positive confirmation landed on it. So a falsifier that crashed did not merely contaminate a verdict, it produced one. The adjudicator read an equipment failure as evidence that two findings are the same defect. The same fall through reaches the verdict DIFFERENT as well, which Fable did not catch.

Measured across both recorded legs of every direction rather than the first leg of every row: 40 of 178 directions rest on legs that cannot carry them, touching 34 of the 133 pairs. Not 12.

That is fixed. A verdict now requires legs that can support it, and anything else is reported as what it is, an inconclusive equipment failure. Removing the guard again fails exactly the five known bad cases and leaves the five known good ones passing, so the test is commissioned rather than hopeful.

This one mattered more than it looks, because of Fable's other point. The merged status is terminal. Had the merge path been wired to the old adjudicator, the first thing it would have done is delete findings permanently on the strength of crashes.


## And Then A Step Further, Which Found Something I Did Not Expect

Having established that errored legs are being counted, the obvious next question is what the errors actually are. I re-ran 25 of the findings involved and captured what came out.

They are two different things, and only one of them is equipment.

Two of them error because the target's own guard fired. The falsifier asks whether the immune memory module will accept a stored tally of minus five. It will not, because a check inside the module raises. That raise is the answer to the question the falsifier asked, and the answer is that the defect is absent. But a raised exception is an unclean exit, so it was scored as an error rather than a refutation. The instrument cannot tell the target's guard rejecting bad input apart from the instrument itself breaking, because both arrive as a traceback.

The other seven are a missing target file, which is genuine equipment failure, and six of those seven are on experiment 48, the run already excluded for the key read, so they carry no weight.

I want to be careful about what this does and does not show, because taking the first example and generalising is exactly the error I keep making. The first case alone would have supported a headline that the errors are refutations in disguise. The other seven refute that. And the recorded errors were measured against a patched file rather than a clean one, so this probe looks at an adjacent condition and not the identical one. Sixteen of the 25 do not error on a clean tree at all, and experiments 44 and 49 are entirely unexplained.

So the honest statement is that a distinct non equipment class exists inside the error bucket and has been demonstrated on two findings. What share of the 53 it accounts for is not established.

I have not fixed it. Separating the target's guard firing from the instrument breaking changes what a verdict means in the core of the runner, and tonight, when two of my own claims have just been refuted, is not the night to edit that. It is written up for your ruling with the shape of a fix attached.


## The Second Panel Is The Bigger One. The Instrument Inventory Was Overstating Itself.

The second dispatch asked both reviewers to test a claim the project has been leaning on: that 32 of the 34 rows in the instrument inventory are commissioned, meaning a test would genuinely fail if that component quietly stopped working.

Both went and tested all 34 by breaking each component and running the test the inventory names. Both refuted it. One scored 23 confirmed, 9 where the named test does not catch the break but some other test does, and 2 where nothing catches it at all. The other found five or six genuinely unprotected and seven where the inventory points at the wrong test file.

I re-ran the important ones myself rather than take either at their word, and the two that matter both reproduced.

The admissibility gate is the one that decides whether a proposed fix is good enough to accept, and it is live in all 19 configurations. Hardwiring it to accept everything leaves 321 tests passing. Nothing anywhere required it to reject anything, so a gate whose entire purpose is refusing harmful fixes could have been accepting all of them silently.

The status machinery is the second. Deleting the part that collects disagreement votes leaves all 156 tests naming it green. A model disagreeing with a confirmed finding would simply vanish, the contested count would under-report, and one of the three convergence conditions would open early on evidence that was never actually uncontested.

Both are now closed with tests that fail when the gate is hardwired open.


## A Test File That Turned Itself Off When Its Component Broke

This is the one I would put in front of you first, and both reviewers found it independently.

One test file decided whether to run by calling the very component it exists to test. The intention was reasonable: skip these tests if some external tools are not installed. But the check it used was to run the fix-quality scorer and see whether it gave a sensible answer.

So when the fix-quality scorer breaks, the check fails, and the tests skip. I reproduced it: the file goes from 45 passing to 33 passing and 12 skipped, and the exit code is zero. It reads as green. Break the scorer, and its tests stop running instead of failing.

That is the same shape as the broken stamp we closed on Tuesday, moved one level up into the test layer. The guard now checks for the tools it claims to check for, and the same break produces 11 real failures.

There is now also a suite-wide rule so this class cannot come back: no skip condition, nor any name it resolves to, may call a function defined in the runner.

Two of the three tests I wrote for all this did not catch their own target when first written, and I only found that because I checked. One of those two was actually my mistake in the other direction: my break was patching a duplicate line in a different function, so the test was being blamed for a bad experiment. Both are correct now and both demonstrably fail against the defect.


## The Inventory Was Overstating How Many Tests Cover Each Row

While in there: the inventory works out how many test files mention each component using a plain text search rather than a whole-word one. So the row for the immune components claimed 40 test files when the true figure is 17, and the health row claimed 17 when it is 2. More than double, on three rows, always in the direction that looks reassuring.

The headline figure is now 27 of 34 rather than 32, and the calibration line moves from five rows measured with two disagreements to all 34 measured with six disagreements in the confident direction.


## The Finding That Worries Me Most, Which Needs Your Ruling

One reviewer went further and re-ran a measurement rather than reading it.

A falsifier is supposed to be a small piece of code that demonstrates a defect. The check that decides whether it succeeded accepts a falsifier that never touches the file it is supposed to be testing. A falsifier consisting of nothing but a print statement is recorded as a confirmation. That was already known and recorded on 22 August. What is new is the scale: of 372 archived falsifiers replayed against every historical version of their target, 346 fired on every single version and were never once quiet. A falsifier that genuinely tests a specific defect should be silent on at least one version. It is possible for a defect to be present throughout, so this is not proof, but 93 percent is not a rate a healthy population produces.

And the control designed to catch exactly this gives a clean bill of health to a falsifier that ignores its target. The reviewer demonstrated it directly. So the reassuring result recorded on 21 August, that none of 360 findings moved under a meaningless perturbation, is exactly the result you would get if a large share of the corpus never reads its target at all. The pass is uninformative rather than reassuring.

I have recorded that reinterpretation in the inventory and not acted on it. It bears on how much of the archived falsifier corpus means anything, which is too big a question to settle unsupervised.

## Canary Seeding Is Built And Tested, And Its Own Panel Is Running

You ruled: build it, test it, and give it its own independent three model panel review in its own context window. That is done, and the panel is running as I write.

The idea, in plain terms. The convergence gate reads only what the reviewers said, so it cannot tell a clean document from a panel that has stopped looking. Both are silence. A canary is a defect of known type and known location, quietly planted in the document under review. If the panel is still working, it finds them. Silence plus killed canaries is positive evidence that the panel really is exhausted. Silence plus missed canaries is a dead panel. That turns convergence from an absence of signal into a demonstration, which is exactly why you called it the right shape.

The technique is mutation testing, from a 1978 paper by DeMillo, Lipton and Sayward, pointed at reviewers rather than at a test suite.

One constraint shaped the whole build. A list of planted defects is an answer key, and this project's standing rule is that keys live outside the repository. So the module refuses, outright, to read a catalogue from any path inside the repository. I then spent time trying to defeat my own guard: a symlink from outside pointing in, a symlinked directory pointing at the repository root, a dot dot traversal back in, and a bare relative filename. All four refused, and all four are now tests.

One of those tests taught me something worth keeping. My first traversal attempt failed with a file not found error, which looks like the guard working. It was not. On this operating system the temporary directory sits under a symlink, so the traversal landed somewhere that does not exist and never reached the guard at all. The test now builds the path from a different place and checks the traversal genuinely reaches the file before expecting a refusal. A guard that is never reached cannot be said to have held.

Then I attacked the measurement, and found a real defect in my own code. The scoring worked out, for each model, what fraction of the planted defects it found, using only the list of what each model caught. So a model that caught nothing simply did not appear in the results. Not zero. Absent. The completely blind reviewer, which is the single thing this instrument exists to find, was the one result that could go missing. That is silent omission in the reassuring direction, inside the module written to catch silent omission in the reassuring direction. Fixed: the list of models actually asked is now required, and an empty list is refused.

I wrote and committed my own position on the build before either reviewer reported, because a position written after reading theirs is a summary wearing a position's clothes.

Two things in that position you should see. First, a gap I deliberately left open: the design refuses a held-out set drawn from a single generator, but two generators where one contributes a single canary is barely better and is currently accepted. Setting a minimum would mean inventing a number, and an invented threshold is the exact problem the project already has with the churn threshold of 0.25, which has no derivation on record. I would rather leave it named than invent one.

Second, the blocking dependency, which is uncomfortable. The intended way to decide whether a finding really killed a canary is the counterfactual method: the finding's falsifier fires on the seeded document and not on the clean one. But that is the very machinery tonight's other panel put a live finding on. Wiring canary scoring to it today would build a new instrument on top of a broken one. So the honest answer to what is missing before this can be connected to the gate is: fix the falsifier check first.

And the strongest case against it, which I put in the brief and answered myself: canary seeding measures the detection of defects we already know how to build, and the panel's value lies in finding defects we do not. Finding every hand-built canary is consistent with total blindness to whatever nobody thought to plant. I do not think that kills the idea, but it does narrow what any score can be claimed to certify, and it should be stated plainly rather than left implicit.

## The Canary Panel Reported, And It Found Nine Things I Had Missed

I had already attacked my own module and thought it solid. Both reviewers ran it rather than reading it, and between them found nine real defects. Three matter a great deal.

The guard was protecting the wrong tree. I wrote it to refuse any catalogue path inside the repository, but the way it worked out where the repository is was to look at where the module file itself sits. Panel reviewers run in throwaway copies of the repository, which is how these very dispatches work. So a copy running in one of those would happily read an answer key sitting in the real tracked repository. That is the same shape as the run we had to exclude, walking in through the front door. It now looks for the marker that identifies any version-controlled directory, so every tree is covered.

The second is subtler and it is where the two reviewers contradicted each other, which turned out to be the most useful thing on the page. One said a path with the wrong capitalisation was correctly refused. The other said it read the answer key. I tested both and they are both right about what they each ran: changing the capitalisation of a folder below the repository is refused, and changing the capitalisation of a folder in the repository's own path reads the key. On this operating system, folder names ignore capitalisation but the comparison in my code did not. Fixed, and both cases are now tests.

The third I had actually written down myself and under-rated. The seeded document is itself an answer key, and a worse one than the catalogue, because anyone with the document's version history can see exactly what was changed. Your own project measured this on the 29th of July and found the planted set recoverable at perfect precision with no key at all. I had recorded that as a caveat in a comment. One reviewer correctly said a caveat is not a guard. The module now refuses outright to seed a document that is under version control.

There was also a provenance error of mine worth telling you about, because it changes the argument rather than just the wording. I wrote that the excluded run happened through a path that looked innocuous. The record says something different: a model wrote a falsifier that opened the scoring key, and its own stated reason was that editing the file would have destroyed a seeded fault the panel was being scored on. In other words, seeding created the motive. That is the only real-world evidence this design has about how often seeding causes harm, and it counts against the design rather than for it. I have corrected it in place, and I would rather you saw the corrected version, because the original made my own module look safer than the evidence supports.

The remaining six were measurement defects: a canary listed in both the practice set and the measured set could let a practice catch count as a real one, an empty generator name counted as a second generator and defeated the diversity guard, planted defects that were never actually planted were still being counted in the denominator and quietly lowering everyone's score, and the blindness check was scanning the whole document rather than the change, so a perfectly innocent target containing the phrase "a seeded random number generator" was rejected outright. That last one would have hit the biology material.

All nine are fixed and the module now carries 42 tests, each one pinned to the attack the reviewer actually ran.


## The Night'S Scariest Number Turned Out To Be Much Smaller Than It Looked

I said earlier that 346 of 372 archived falsifiers fired on every version of their target, and that 93 percent is not a rate a healthy population produces. That is true as far as it goes, but it invites a conclusion it does not support, so I built the measurement that settles it.

The decisive test is blunt. Replace the file a falsifier is supposed to be testing with an unrelated file, and re-run it. If it still reports the defect, it was never reading the file. If it errors or goes quiet, it was.

Across all 372: 9 are provably not reading their target and 348 are. That is 2.4 percent, not 93.

The two numbers do not contradict each other. They answer different questions. Firing on every historical version remains unexplained and still needs looking at. But the crude failure, the falsifier that never touches the file it accuses, affects 9 findings and not most of the corpus. Those 9 sit in 3 runs on 3 files, and I have named them in the record so their evidence can be discounted.

One caveat has to travel with that number, and I have written it where the number prints so it cannot get separated. What the test establishes is that the falsifier reaches for its target, because destroying the target makes it fail. It does not establish that the falsifier tests the defect it actually accuses. A falsifier that loads its target and then checks something unrelated looks identical to a rigorous one. So this rules out the crudest failure and is not a clean bill of health for the other 348.

## Where The Two Reviewers Disagree, Preserved Rather Than Smoothed

On the unreachable guard, Fable says confirmed and treats it as a defect. CC2 says confirmed as control flow but only partial as a defect, because the ordering is deliberate and locked by a test. Both are right about the code; they differ on intent. That difference is information and I have not resolved it by preferring one.

On merge, Fable says wiring. CC2 says wiring at the registry but building at the adjudicator. Also preserved.


## What I Found Before The Panel Reported

The recovery work you asked about is done, and doing it found something.

The claim that blocked it was never a measurement. The replay accounting script printed, as a settled conclusion, that no archived report carries a rho series in any form, that this was measured across every report, and that no amount of replay would make it available. I checked that assertion against the code by parsing the module: the word rho appeared in it five times and every occurrence was inside a print statement. There was no counting code and no reference to any rho key. The word measured was doing work that nothing did. That assertion then propagated into the recovery document and reached you as a decision to make.

So I built the replay. It fails its own exit test on 10 of 18 runs, and by this project's own rule a replay that cannot reproduce the past is measuring itself, so it withholds the result rather than delivering a number. But the failure is itself the finding, and it is specific: replayed rho is exactly novelty over raw, while archived rho is consistently higher. Experiment 42 at round 9 recorded 0.4, which is 2 over 5, while the report records the novelty as 1. At round 11 it recorded 0.875, which is 7 over 8, against a recorded 3.

So the novelty figure in the report is not the numerator that fed rho. They are different quantities, one settled and one not, which is the same all versus settled split that made gamma look wrong on experiment 41c, now appearing in a second measure. Both inputs are now persisted, so the next run makes this replayable instead of arguable.


## A Structural Answer To The Conflation, Which You Asked For Directly

You told me to make deliberate and real efforts to stop these errors recurring, and named the resources that should prevent them.

Three times in 48 hours a canonical document asserted a fact about data, the data said otherwise, and I acted on the document without opening the data. Merge arbitration defaults off, which was true in no configuration. The 133 pairs pending your ruling, which a tool had decided ten days earlier. No report carries a rho series, which 22 of 31 do. Every one reached you as a decision.

The shape is identical each time: a prose claim about data, ageing silently while the data moved.

Documents cannot check themselves, so their claims now have checkers. A new audit script holds a registry of claims whose data source is named, and verifies each against that source. It found a live one on its first run. It is deliberately narrow, because verifying prose in general is not possible, but the standard it implies is the useful part: a claim that cannot be checked does not belong in a canonical document as a fact.

It is commissioned rather than asserted. The load bearing test puts the stale wording back into the real file, confirms the audit fails, restores the file, and then checks the restore was exact. Without a known bad case an audit can pass forever by matching nothing, which is exactly what the vagueness linter did from version 1.5 until someone finally ran it.


## What Remains For You, And It Is Short

Two things need you, and neither can be done without you.

The 31 key files are still sitting in plain text. The three commands are in the other file on your desk and they need a passphrase that should exist only in your head and your password manager.

The push, which you ruled goes last. Everything from the three uploaded documents is now done, so it is ready when you are.

Four things need a decision rather than an action, and none is urgent.

Whether the churn measure should become a contributor rather than a veto. That is your own framing, both reviewers agree with it, and I have not touched it. It changes gating behaviour and the panel spent the night refuting my claims about the surrounding evidence, which is the wrong moment to start editing a gate.

Whether the falsifier check should tell the difference between a target's own guard correctly rejecting bad input and the instrument breaking. Right now both arrive as a crash and both are scored the same way. Changing that changes what a verdict means in the core of the runner.

Whether the nine falsifiers that never read their target should have their findings struck from the record. I have named them but changed nothing.

And whether a missed canary should block convergence. That is a new way for a run to fail, so it is yours.


## What The Night Cost And What It Produced

25 commits. The test suite finished at 4317 passing, 35 skipped and nothing failing, in 4 minutes. It started the window at 4154, so it grew by 163, every one written because something specific was found to be untested rather than to raise a number.

Three panel dispatches, all free. Two on questions you had already approved, one on the canary build because you ruled it should have its own.

The pattern worth taking away, and it held every single time tonight: every figure I reported without going and looking was wrong. The closest approach to the churn threshold, wrong. The merge evidence base, wrong by half, and then wrong again in the other direction when I followed it into the code and found three times the damage. The instrument inventory's 32 of 34, wrong. And the 93 percent that frightened me most, wrong by two orders of magnitude in the reassuring direction once I built the measurement instead of quoting the proxy.

Two of those errors were mine reading a summary. Two were reviewers reading a summary. One was my own module. The failure does not belong to any particular reader.

Sleep well. None of this is on fire.


Written under CDSFL note standard v1.7 (26 August 2026).