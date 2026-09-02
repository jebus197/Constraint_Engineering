# CDSFL consolidated report — overnight 1 September to afternoon 2 September

Prepared 2 September 2026, 16:32 BST.

This gathers roughly 24 hours of work into one place, because there has been a lot of it and it should not be lost. It is written to be read aloud. Where a decision is needed from you, the section says so plainly and gives you enough to rule on without reading code.


## The Short Answer To Your Question

No. Not all the agreed work is complete.

Of 67 tracked items, 36 are closed. That is 53.7 percent, with a confidence interval from 41.9 to 65.1 percent. Twelve are open, 3 need a ruling from you, and 1 is dormant.

More importantly, the loop you set has not reached its own stopping condition. You said to continue until the models and I agree there is a robust solution going into the next round of real experiments. No reviewer has yet said the runner is ready. The scope also grew during the period, because the loop kept finding things, and several of the open items did not exist yesterday.

The test suite is green at 4,854 passing and none failing.


## What Is Solid Now

The simulated experiment converges honestly. The last run reached convergence at round 4 on real evidence rather than on absence, and found all 5 defects that had been deliberately planted in the target. Earlier runs converged only because there was nothing to find, which is a hollow result and which you rightly rejected.

The sandbox is genuinely blind. Twice it was not. The first failure removed the answer files from the working copy but left the whole history readable, so a reviewer could retrieve the reference experiment's answers, including 12 severity scores, with a single command. Every simulated run before that repair was measured through that hole.

A rule that was blocking honest reporting has been withdrawn on your instruction. It had never been ratified. It arrived as 2 models agreeing, the tracker recorded that it still needed a ruling, and 40 minutes later a commit restated it as a standing ruling. You could not remember approving it because you had not.

The audit your own pre-registration demanded in May has finally been run. It compares the numeric severity score against the 5 clause written definition, blind. They agree on 54.4 percent of the hardest cases, with an interval from 48.4 to 60.4. That is barely better than chance. Crucially it is not reader disagreement: 2 independent readers agreed with each other 92.5 percent of the time. So the number and the definition are measuring different things at the boundary where the decision gets made.


## The Single Most Important Finding

For months the project has asked at what point it stops paying to put the same question to another model. That question is largely answered in the existing literature, and the harness is on the wrong side of the one precondition that makes the answer available.

Every method in that family needs 2 numbers: how many findings were seen by exactly one reviewer, and how many by exactly two. The overlap between reviewers is what tells you how much you have not found.

The harness records the first number and destroys the second. Of 2,050 real archived findings, 2,048 are recorded as found by exactly one model and only 2 by more than one. When 2 models find the same defect, the system creates 2 separate unlinked records.

Feeding those figures to the standard estimators gives an estimated completeness of about a quarter of one percent, and 2 estimators from the same family disagree by a factor of 152. That is not a hard estimation problem. It is a signal that the data is outside the range where those methods work. The ecology literature has a name for this exact pathology, which is failing to recognise an individual you have already seen.

Until that is fixed, no number about coverage, saturation, or when to stop is trustworthy.


## A Correction To Something I Told You Earlier Today

I reported that 2 panel seats running the same model weights produced measurably different results under 2 different instruction conditions, and that this justified building diversity from prompts when only one model is available.

The attribution was wrong. The difference was that one seat had a working shell and could run the code, and the other had a plain interface call and had to write its test blind. The runner says so in its own source. One reviewer reached the same objection independently.

The measured difference is real: 25.9 percent of that seat's findings carried a runnable test, against 17.3 percent for the other. But it measures tool access, not prompt wording.

This matters because your distinction, between one model used directly and one model equipped with agents, is exactly the right frame, and the evidence currently supports your framing rather than mine.


## What I Got Wrong, Measured

You asked directly whether I am unreasonably error prone. The honest answer is yes, in one specific repeating way.

Of 54 commits in the period, 13 corrected a previous claim of mine. That is 24.1 percent, interval 14.6 to 36.9. The review panel caught 9 of those 13. The recurring shape is that I verify the easy case and ship it as though it were the whole set. I did that with the duplicate detector, with a timing test, with the simulation filter, and with a coverage calculation, all in one night.

Two things qualify that. The reviewers err too, and one of them refuted the other outright today. And the record overstates my error rate, because until this afternoon I had only ever asked the panel to find faults. Across 7 briefs, permission to call something sound appeared twice, against 25 instructions to find what was wrong. Across 14 replies there were 176 pieces of evidence attached to problems and zero attached to any proposed cure.

That last number is the answer to your joke about having built a problem calculator. It was structural, and it was caused by the question I was asking.

When the brief was rewritten to permit a verdict of sound, to require a measurement that each proposed fix actually works, and to include the project specification, the very next round produced recommendations with evidence attached to the remedy for the first time.


## Decisions That Need You

There are 5. Each one says what it is, why it matters, and what I recommend.

### DECISION 1. THE RECORDING CHANGE. This is the one that unlocks everything else.

What it is. Today, when a finding is recorded, the system notes which single model raised it. The proposal is to record instead the full list of occasions that raised it, where an occasion means a particular model, using a particular prompt style, with a particular random seed, in a particular round.

Why it matters. That list is the overlap statistic. Without it, none of the established methods for estimating what you have not yet found can run at all. With it, they all become available immediately, including a stopping rule that means the same thing whether a researcher has one model or a hundred.

What it costs, measured across all 29 real archived runs. A median of 832 bytes and 0.017 seconds per run. Worst case 4,357 bytes and 0.267 seconds. Around 33 kilobytes across the entire archive. Against a run that takes 69.6 minutes.

There is a second benefit that is easy to miss. Counting seeds and rounds as occasions means a single run produces dozens of occasions rather than 5, which is the only realistic route to having enough overlap data to work with.

My recommendation. Do it. It is recording, not research, and the cost is negligible.

## Decision 2. How To Check The Matcher, And Whether It Smuggles Voting Back In.

What it is. Before any of the above means anything, we need to know how good the system is at recognising that 2 findings describe the same defect. A first version exists and scores about 86 percent precision. But it scores pairs of findings directly, while the output it produces groups them, and 29.8 percent of the pairs in those groups were never actually scored. They are present only because the grouping chains through other pairs. So roughly a third of the output has unmeasured accuracy.

The choice. One reviewer proposed a way of labelling that is consistent with this project's founding principle: take 2 candidate findings, run each one's test against the other's defect, and if both fire they are the same defect, decided by execution rather than by opinion. Cost is 2 sandbox runs per pair and no model calls at all. The alternative, which is what the current 86 percent rests on, uses similarity scoring, which is closer to a vote.

My recommendation. Adopt the execution based labelling. It is the only option here that does not quietly reintroduce agreement as a truth criterion, which is the thing this whole project exists to avoid. Also seed defects deliberately, because a planted defect has a known identity and therefore gives free ground truth with no extra dispatches.

## Decision 3. The Experiment You Proposed.

What it is. Run the harness twice on the same target. Once with a single model used directly, and once with a single model that has agents and tools available. Compare what each finds.

Why it matters. It separates 2 things that are currently tangled: whether the benefit comes from having different models, or from having tools. Today's corrected finding suggests tools matter a great deal, and if that holds, a researcher with only one model can still get most of the benefit by giving that model a shell rather than by buying a second vendor.

My recommendation. Run it. It is the cleanest test of the scaling question and it costs 2 simulated runs.

## Decision 4. The Seeded Defect Catalogue.

What it is. To test whether the panel can detect anything, defects are deliberately planted in the target. I wrote 2 such catalogues by hand.

The problem. The software engineering literature is clear that hand written planted faults are not a valid substitute for real ones, while mechanically generated ones are. And my first catalogue failed in exactly the way that result predicts. Three of its 5 plants sat directly beneath comments stating the rule they broke, so finding them tested comment reading rather than defect detection. The 2 that required real reasoning were both missed by all 6 reviewers, and both had been assigned to the group whose results are not reported, so the headline score looked perfect while 40 percent went unfound.

My recommendation. Replace both catalogues with mechanically generated ones. Keep seeding, because it is the only instrument that can tell you about defects no reviewer can see, and the only one that works when there is just one reviewer.

## Decision 5. Three Smaller Rulings Outstanding.

Spend metering. You have already ruled: default on, silent in simulation, with a user toggle when the interface exists. It now needs building. Nothing meters today on either kind of run.

The temporary working copy. There is uncommitted work sitting in a temporary folder that gets cleared on reboot. I assessed both halves as superseded, and a reviewer's independent check agreed the content is preserved elsewhere. My recommendation is to discard it and remove the folder. It is your call because it is the only copy of that particular arrangement.

The seat contrast. In April, 2 panel seats were deliberately different, and that difference was lost during a reliability fix. Today's correction shows the difference was tool access rather than prompt wording. So the choice is whether to restore it by giving one seat a shell, or to accept that the panel has 4 genuinely different architectures rather than 5 and say so openly in the record.


## What I Propose To Do Next, If You Agree

In order. First, the recording change, because everything else waits on it. Second, the execution based matcher check, so we know what the overlap numbers are worth. Third, the mechanically generated seeded catalogue, which is slow to build and independent of the other two, so it should start in parallel. Fourth, your experiment comparing one model alone against one model with agents.

Only after those does it make sense to build anything that decides how to divide work across whatever resources a researcher has, because until then such a thing would be optimising against a number that does not yet exist.

One thing I will not do without you. The convergence gate is the mechanism that decides when a run has finished. Any change to it, even a change that only observes and does not act, goes to you and to the panel first.
