## Decisions Awaiting Your Ruling, 2026-09-03 09:22 Bst

> **Retrospective mirror, created 2026-09-05.** This note was written as a spoken-word file only; `tts-output-protocol` requires both forms and the markdown copy was never made. Content is the spoken version's, unaltered apart from headings. Source: `~/Desktop/CDSFL_tts/DECISIONS_AWAITING_YOU_2026-09-03.txt`.


This file replaces twelve separate notes written over the last 48 hours, totalling about eighteen thousand words. Everything already ruled, already done, or now pointless has been removed. What is left is twelve decisions, numbered so you can answer by number alone. Each has one recommendation, not a menu.

Two things at the top, because they change what the older notes say.

Metering is not a decision. You ruled on it on 2 September and the ruling is recorded in the repository: default on, silent in simulated mode, toggle in the interface as the last item after the second bench run. Three of the older notes still list it as needing a ruling. They are stale. It is a build task now, and the machinery exists but is not connected to the main runner.

The temporary working copy is probably moot. Three notes ask you to decide whether to discard it. The folder is no longer present at the path those notes refer to. I have not yet confirmed whether it was deliberately removed or simply cleared, so treat this as one line of housekeeping rather than a decision.

## Section One. New Overnight. Highest Consequence.

DECISION 1. The gate that accepts fixes has never rejected anything.
The threshold that decides whether a proposed fix does more good than harm was derived with one variable frozen at the value one, and that variable is the very thing the gate is testing. At the only operating point the pipeline reaches, the threshold works out to minus one nineteenth, which clamps to zero, so everything passes. The correct threshold is about one half. This has been true since 10 April, so 146 days, across roughly 122 run directories. It was confirmed four independent ways, including by a local Wolfram kernel working in exact fractions. Across twenty three thousand parameter combinations where the gate and the risk model disagree, every disagreement admits a harmful fix and not one rejects a helpful one.
Recommendation. Fix it, but second, not first. See decision 2.

DECISION 2. Four constants that nothing sets.
The risk model reads its parameters from a field that no code anywhere writes to. Every experiment from number 37 to number 49 therefore ran on four literal defaults. The one module built to make the risk vary with the size of a fix has no caller. One reviewer described repairing the threshold while its inputs are constants as polishing the second decimal of a number that has no first one.
Recommendation. Connect that module first, then fix the threshold. This is the ordering both reviewers converged on independently.

DECISION 3. Whether to write the Reduction Criterion into the mathematical appendix.
The idea you and I arrived at, that a simplification is only legitimate when it agrees exactly with the fuller form across a scope declared in advance, or else names and files what it leaves out. Both reviewers judged the reasoning sound. Both said add no machinery.
Recommendation. One definition in the appendix, one sentence in the acceptance policy, nothing else. No score, no weight, no new term in the model.

DECISION 4. A rule about measured numbers.
Three of the eight figures I put to the panel could not be reproduced, because each was a rate stated without the script that produced it. A file already exists in the project written specifically to stop that happening, and I re-created the same fault one day after it was written.
Recommendation. Adopt one sentence as a standing rule. A measured rate must travel with the script that produced it, or it is prose rather than evidence.

DECISION 5. The containment instrument cannot prove it ran.
The check that watches for a reviewing model altering the document under review reports zero observations, with no way to tell never happened from never executed. Three other instruments are in the same state.
Recommendation. Give it an unconditional counter so it can say it ran. Small, and it is a reviewer's own suggestion.

DECISION 6. Whether reviewing models should hold write access at all.
Formally pending since 29 July. Neither reviewer wants it removed, on the grounds that it is what makes them useful reviewers. Both propose measuring instead, and both reached the same discriminator without conferring. The signal is not the boundary crossing but the record left behind. A model exceeding its boundary to help leaves the change visible and says so. The case to worry about leaves the state restored and the record silent, which is what happened on 29 July.
Recommendation. Keep write access, measure disclosure. Decide this before the next simulated run, because it changes what that run records.

## Section Two. Still Open From 1 And 2 September.

DECISION 7. The recording change.
Record the full list of occasions that raised a finding, where an occasion is a particular model with a particular prompt style, seed and round, rather than just the one model that raised it first. That list is the overlap statistic, and without it none of the established methods for estimating what has not yet been found can run. Measured cost across all 29 archived runs is a median of 832 bytes and 0.017 seconds per run, against runs that take about seventy minutes.
Recommendation. Do it. It is recording, not research, and everything else waits on it.

DECISION 8. How to check the duplicate matcher.
The matcher decides whether two findings describe the same defect. It scores about 86 percent, but it scores pairs while its output groups them, and 29.8 percent of the pairs in those groups were never scored at all. The choice is between similarity scoring, which is close to a vote, and running each finding's test against the other's defect, which decides by execution.
Recommendation. Adopt the execution based labelling. It is the only option that does not quietly reintroduce agreement as a truth criterion. Overnight work sharpened this: one reviewer showed that changing the definition of the comparison population swings the headline rate by a factor of three using identical code, so whatever is adopted, the population must be fixed in advance.

DECISION 9. Your experiment. One model alone against one model with agents.
Overnight work strengthened the case and gave it a sharper hypothesis. The defect in decision 1 was found by noticing that two functions with no words in common answer the same question. Ranking every possible pairing by name similarity puts about three quarters of them ahead of the one that mattered, so no mechanical search would have found it. If the load bearing ability is that kind of recognition rather than having several different suppliers, then one model given several differently framed briefs may do as well as a multi vendor panel.
Recommendation. Run it. Two simulated runs, and it now tests something specific.

DECISION 10. The seeded defect catalogue.
Defects are planted deliberately to test whether the panel can detect anything. Both existing catalogues were written by hand. The literature is clear that hand written faults are not a valid substitute for mechanically generated ones, and the first catalogue failed exactly as that predicts: three of its five plants sat directly beneath comments stating the rule they broke.
Recommendation. Replace both with mechanically generated ones. Keep seeding, because it is the only instrument that works when there is a single reviewer.

DECISION 11. The seat contrast.
In April two panel seats were deliberately different and that difference was lost during a reliability fix. The difference turned out to be tool access rather than prompt wording.
Recommendation. Give one seat a shell and restore the contrast. If you prefer not to, the alternative is to state openly in the record that the panel has four genuinely different architectures rather than five.

DECISION 12. Configuration settings that nothing ever sets. Now verified, and corrected twice.
The older notes said nine gates that no configuration enables. Checking that against the real population of forty four configuration files rather than the four I first looked at: the runner reads sixty four settings, and twenty five are never named in any configuration file, which is 39.1 percent with a confidence interval from 28.1 to 51.3 percent.
Never set is not the same as dead. Twenty one of those twenty five carry real numeric defaults, so they are live and simply never varied. I then said four were genuinely unreachable. That was also wrong. Two of the four, human in the loop review and resume, have command line flags, so they are switched on per run rather than per configuration. Human in the loop review is therefore an operating choice made run by run, not a disabled feature, and my suggestion that you ask why it has never been enabled was based on a mistake.
Only two settings have neither a configuration entry nor a command line path: severity calibration, and stall based termination. Those two cannot currently be switched on by any means.
Recommendation. Two small matters, neither urgent. Rule on whether severity calibration and stall based termination should be wired up or deleted. The twenty one never varied numbers are not a separate decision, they are decision 2 appearing in another place and should be handled there.

DECISION 13. Half of a pre-registration from May has never been built. Found only on a second sweep.
This one was missing from the first version of this sheet and was surfaced by re-deriving the list from the notes mechanically rather than from memory, which is why it is worth having done.
A document frozen on 18 May, before the runs it governs, requires every run to report two things. First, the count of findings where the numeric severity score and the five clause consequence rubric disagree. Second, how sensitive the run's verdict is to that disagreement. The second was built on 2 September and is now emitted per run. The first has never been built, and the runner says so in its own comments: it needs a per finding rubric classifier and is not wired.
Why it matters rather than being paperwork. The audit run on 2 September found that in the disputed band the number and the rubric agree on only 141 of 259 judgeable findings, 54.4 percent, with a confidence interval from 48.4 to 60.4 percent. That is not reader disagreement: two independent blind readers agreed with each other on 92.5 percent of shared items, with a kappa of 0.837, while each agreed with the number only about half the time. The pre-registration says that where the two disagree on a finding that could move the verdict, the rubric governs and the adjudication is logged with its reasoning. That remedy does not exist in the code. So on the findings where the gate is actually decided, the run is currently governed by the number, and a document frozen in May says it should be governed by the rubric.
The honest complication. The pre-registration itself says a machine cannot adjudicate those five clauses, and that a model or the human in the loop must do it. So building this is not a small mechanical task, it is a decision about who adjudicates.
Recommendation. Rule on the principle first, not the implementation. Either the rubric governs, in which case this needs a per finding classifier plus an adjudication log and belongs on the runway ahead of the second bench run, or the pre-registration is formally amended to say the number governs and the reason is recorded. What should not continue is the present state, where a frozen document says one thing and the code does another and nothing reports the gap.

## Recommended Order If You Agree With All Of It

Decision 2 then 1, because the threshold repair is meaningless while its inputs are constants. Then 7, the recording change, because the measurement work waits on it. Then 6, because it changes what the next simulated run records. Then 8 and 10 together, since both concern how detection is measured. Then 9, your experiment. Decisions 3, 4 and 5 are small and can land at any point.

One thing I will not do without you regardless of the answers above. The convergence gate decides when a run has finished. Any change to it, even one that only observes, goes to you and the panel first.

