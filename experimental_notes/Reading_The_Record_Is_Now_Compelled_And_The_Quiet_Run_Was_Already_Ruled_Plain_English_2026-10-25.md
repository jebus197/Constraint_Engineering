# Reading the record is now compelled, and the quiet run was already ruled — plain English

**2026-10-25, 01:30 to 01:45 BST. Commit `a026fb7a`, pushed to branch `sim/shakedown-2026-09-29`.**

## The short version

Seven defects raised on the night of 2026-10-24 were fixed and committed. The eighth item, a question about how many quiet rounds an experiment must see before it may declare convergence, needed no work at all: the change the founder was querying had been made on his own ruling of 2026-10-08, and the measurement and the cost were both already recorded. The one thing still outstanding is a decision, not a build.

## A gate that will not let his words go unread

The founder annotated 2 notes on 2026-10-23 and received a reply saying that no decisions were waiting for him. The reply was accurate — the register of his verdicts genuinely held zero — but it was reached by reading an index rather than by opening the files. Eight annotations sat unanswered as a result.

A check that would have caught this already existed. It refuses a commit if any of his annotations lacks a recorded verdict, and it works correctly. The problem was timing: it only runs when something is committed, and a whole day passed with no commit. So the fix was not to invent a new check but to move the existing one to a moment that happens every single turn — the end of a turn.

That is now `hooks/his_responses_freshness_gate.py`. It reads his annotation files using the project's dedicated reader, never using `grep`, which has twice mistaken his files for binary data and skipped them silently. If any annotation of his has no recorded verdict, the turn cannot end. To prove it works, the original incident was replayed: 8 verdict rows were removed from a copy of the record, and the gate named all 8 annotations, quoted his words back, and refused.

Its own first test run found a flaw. A line that formats a file path for display can throw an error when the file sits outside the project folder, and the module's safety net would have turned that error into a silent pass. A gate that fails silently is worse than no gate, so that line is now wrapped so it cannot throw. The gate also refuses at most 3 times per turn and then yields with the problem stated, so it can never trap a session.

## The depth and breadth instruction now exists where he said it should

The founder had asked that most of his subscription allowance go to careful reasoning rather than to spawning parallel helper agents, and he said the instruction belonged in both his global and project configuration files. It was in neither properly: the global file said nothing about it at all, and the project file had a single buried paragraph.

He also corrected the wording. The old version said to spend on reasoning depth and NEVER on breadth, which he judged too absolute, suggesting something closer to a 70:30 or 60:40 balance instead. He asked for both terms to be defined explicitly, and for it to be clear they describe reasoning.

They now are. **Depth** means reasoning effort concentrated in one place on one problem: working out what a change will affect before making it, deriving an answer rather than asserting one, and reading the actual record before making claims about it. **Breadth** means reasoning effort spread across several parallel helpers, each thinking separately and reporting back a summary — and the summary is where detail is lost.

**On the 70:30 ratio, the honest answer is that it cannot be enforced.** Neither the harness nor the hooks label a thought as "depth" or "breadth", so no mechanism can check a 70:30 split at the moment a decision is made. The project has a standing rule against adding things nothing can reach, and 11 confirmed defects in its history were exactly that: additions that did nothing. A 70:30 split written as an enforceable rule would have been the twelfth. So 70:30 is recorded as the direction of travel and is reported, not policed.

**On his other question — whether reasoning depth can be required BEFORE the parallel helpers are used — the answer is yes, and it is now built.** Any brief sent to a helper must state three things: what it is testing, what result would prove it wrong, and why one context cannot answer it. A hook that already ran on every such call now refuses a brief missing any of the three. Plain literal labels are required rather than any judgement about whether a brief "looks considered", because a judgement-based version of this same check was written the previous day and failed in both directions, producing 5 false alarms and then missing the one real case.

His two-sided reasoning — too much depth risks tunnel vision, too much breadth spreads thinking thinly — is recorded with the halves marked unequally, because only one is measured. Of 12 errors on 2026-10-11, 10 were catchable by more careful reasoning before running anything. The tunnel-vision half is marked as his untested hypothesis, with a specific test that could confirm or refute it.

## The rule caught the person arguing for it

Three figures had been quoted to him in support of this directive, and none had a script behind it. Under the project's own standard, a number with no script that produces it is a claim about evidence rather than evidence.

Writing that script changed all three. The real figures are 108 parallel-helper calls over 68 days before the instruction against 8 over 18 days after, so 1.5882 per day falling to 0.4444, with a significance value of 0.0199 by one statistical package and 0.0196 by an independent calculation. The figures quoted had been 1.2750, 0.4286 and 0.003578. The conclusion survives — parallel helper use did fall, and the fall is statistically real — but the numbers were wrong, and the significance value was roughly 5.6 times too small.

The script also records what it cannot measure. Counted as calls, parallel helpers are under half a percent of all activity in both periods. Counted in tokens they cost far more, because each helper spends its own allowance, and that per-call cost cannot be attributed. So no statement like "70% of the allowance went to depth" is defensible, and the script says so.

## Twice in one night the first number computed was the alarming one

A hand-written test brief happened to contain the word "without", which the guard protecting the founder's 8 GB machine treats as a sign that a brief is forbidding something rather than requesting it. That made a brief which did request a test run read as one that forbade it, and it looked like a serious regression. The first rate computed was 25.42%.

Measured properly against the 115 real briefs recoverable from the session history, the true answer is that 14 cases are deliberate prohibitions — which is exactly the documented, correct behaviour — and **zero** are accidental. The guard needed no change; the test brief did. A 25.42% defect rate was within a sentence of being reported for a guard with no defect.

The same thing happened again within the hour. A new rule about where the note-standard line belongs flagged this session's own correctly-written summary, because it looked at the first mention of the standard in a document rather than the last. Reading the last mention instead — which is what the convention actually means — cut the findings from 23 of 582 notes to 15, while still catching all 3 of the files the founder had complained about.

## A red test, and two ways an instrument can lie

One test had been failing because it supplied 3 quiet rounds to a gate that now requires 7. The gate was correct all along; only the test's setup was out of date.

Fixing it properly exposed two subtle traps. First, a default value in a Python class is calculated once when the class is created, so reading the current setting in one place while the gate compares against a frozen copy in another means the two can silently disagree — and they did. Second, a test patch applied to one spelling of a module name never reached a test that imports the same file under a different spelling, because Python treats those as two separate modules. In both cases the check reported success while actually testing nothing. Both are the same failure as 3 guards that went blind to a wrapper earlier in the month.

## His feed-back instruction is now recorded as done

He had asked whether the work of feeding problems back into the project's own machinery could be marked complete. Rather than find a ticket claiming it, a script checks three routes by running them: a problem can become a tracked ticket; a ticket can be put to the model panel; and a resolved problem becomes a test that actually turns red when the code it guards is broken. All three pass. The panel route now shows 60 requests with none going unanswered, improved from 30 of 60 a few days earlier. The ticket is closed with that run attached as its evidence, which is the only way this system permits a closure.

## Why he was confused about the note standard, and it was not his fault

He wrote that he was unaware of a version 1.8 of the note standard and that the last he knew of was 1.7. Version 1.8 does exist and has since 2026-10-17. But the project's own introductory document still said version 1.7, locked in August. His understanding was correct for the document he had been given, and wrong only about the project — which is the document's failing, not his. That pointer has now gone stale twice and says so.

His separate objection, that the note-standard line was printed at the top of a file rather than the bottom, was simply correct. There was no reason for it. Measured first: of 582 notes carrying the line, 559 — just over 96% — put it at the bottom, and 2 of the 9 exceptions are the files he complained about.

## The project's own commit check caught a mistake made during this session

Adding the new requirement that briefs state their reasoning broke two existing tests of the same file. Both are replays of real briefs from 2026-10-17: one that forbids test runs and must be allowed, and one that requests them and must be refused with the right advice. The new check fired first and changed both outcomes.

This was a failure to trace consequences before making a change. The fix was to complete the old briefs rather than weaken the new rule, since forbidding a tool and explaining your reasoning are unrelated concerns and a real brief would do both. A further test now proves the new requirement is what lets those briefs through, so nobody later mistakes this for a test quietly loosened to make a change pass. The scope was measured rather than guessed: 1,436 tests ran and exactly 2 failed. The final commit ran 1,439 green.

## The convergence question: he had already ruled, and he was right to suspect it

He asked why the requirement of 3 consecutive rounds with no new critical findings had become 7, objected that 4 extra rounds amount to a real time and money penalty on every experiment, and wondered whether he had already given a ruling on it.

He had. The change was made on his own ruling of 2026-10-08, after he was shown that the old setting had an 11.59% chance of declaring a false quiet, and he said "Fix it."

The underlying measurement is committed and was read off the project's archive with no model involved. With 3 quiet rounds required, 23 of 182 windows closed prematurely — about 1 run in 8. With 4 required it is 12 of 153, with 5 it is 6 of 131, with 6 it is 3 of 114, and with 7 it is **0 of 99**. Seven is the first setting with no premature closures observed at all and the smallest whose statistical upper bound meets the 5% target; 5 only meets the target on the central estimate, with an upper bound nearly twice as high. Going beyond 7 does not help, because the number of comparable windows shrinks as the requirement lengthens.

**The cost he objects to was already written down, in his interest, in the same place as the measurement.** Runs that would have converged at round 3 or 4 now cannot close before round 7, so a converging run grows by about 4 rounds — roughly an hour more per run, measured against one shakedown leg's 71.5 minutes over 5 rounds, and 4 more rounds of paid dispatch on a real roster.

So the extra rounds are not held in hope that they turn up nothing. The old setting was measured declaring convergence that had not happened in 1 run out of 8. The trade is about an hour per converging run against that risk. Whether that trade is still the one he wants is his decision, and a review brief on exactly this question exists but has never been run.

## What is waiting for him

One discussion, carrying 3 registered questions so that none of them can be lost. **[qs:0dff2c161fdd]** whether the 70:30 balance in reported-but-not-enforced form is what he wants. **[qs:524186098488]** whether his ruling of 2026-10-08 on the quiet rounds stands now that its cost is in front of him again. **[qs:08cf82f5081c]** whether the review brief on that very question, which exists but has never been run, should now be dispatched. The main task list stays paused on his instruction, with 58 workable tickets behind it. Three review briefs remain unrun, including the one on this very question.

Written under CDSFL note standard v1.8.
