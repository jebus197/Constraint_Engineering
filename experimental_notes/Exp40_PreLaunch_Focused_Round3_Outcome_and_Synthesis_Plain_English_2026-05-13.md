# Pre-Launch Review, Round Three — What the Final Panel Said, and What it Means

2026-05-13 02:06 BST

## What this note is

This is the plain-English companion to the technical record of the third (and final) pre-launch expert-review round for Experiment 40 in the project's current experimental arc. The arc covers fifteen consecutive experiments numbered 40 through 54, plus a follow-on benchmark run. Experiment 40 is the first of these and the gate that opens the rest; it has been ready to dispatch for several weeks but was waiting on expert-panel review of items that had not yet been examined by the full panel.

Three rounds of review have now run: one in April, one earlier in May, and this final one. Together, they have closed every item that needed expert judgement. The note records what happened in this third round, what it changed, and what now stands ready.

## How a review round works, briefly

The project runs reviews against a panel of five large language models from different vendors: Anthropic's Claude, OpenAI's GPT (twice, in two distinct slots), Google's Gemini, and DeepSeek. The panel operates under a rule the founder calls compelled convergence: each model receives the same questions independently, with no cross-talk between them, and is required to give a single definitive answer per question rather than a list of options. The agent then reports what the panel agreed on, and where they disagreed, with reasoning.

The point of compelled convergence is to spare the founder from refereeing technical disagreements between experts where they are not themselves a domain expert. The panel either agrees, or it surfaces the disagreement openly and works toward agreement under further questioning.

## Why a third round was needed

The second round, run earlier in May, returned about 80 percent agreement across its five questions. The remaining 20 percent had genuine disagreement on three specific points. Standing policy says rounds should continue until the panel converges on every point, not just most. The agent had handled the residual disagreement by writing it up for the founder to adjudicate, but that is the menu-for-the-founder failure mode the compelled-convergence policy was designed to prevent. Round Three was the corrective dispatch: same panel, same protocol, three focused questions, force convergence.

## What Round Three resolved

The first question concerned the trigger for two arbitration mechanisms in the project's runner. These two mechanisms handle what happens when expert-specialist subsystems disagree with each other, or when a merge between their outputs deadlocks. The original plan named Experiment 44 as the trigger point — meaning, "wait until that experiment runs, then look at its logs to design the arbitration rules from observed evidence". One of the five models (DeepSeek) had argued in Round Two that this was structurally wrong: Experiment 44 by design involves only one expert specialist plus a couple of support layers, not the multiple specialists that would produce a conflict or deadlock. The first experiment that does produce multi-specialist co-rule is number 49.

In Round Three, the other four models were given DeepSeek's argument directly and asked to either move or defend their prior position. All four moved. The plan now names Experiment 49 as the primary trigger, with Experiment 44 retained as an early-observation checkpoint just in case anything anomalous shows up there. The operational behaviour was already correct because of a migration clause in the prior text; this change just makes the wording match the structural reality.

The second question concerned a labelling problem. The project uses a small vocabulary to describe how mature a software component is: whether the code is just present and tested but not hooked into anything yet ("library-complete"), whether it is hooked into the system but only watches and reports without changing outcomes ("shadow-integrated"), or whether it is fully operational and actually drives decisions ("live-operational"). A specific debug-time safety check sat awkwardly between these three labels. The check is off by default, so "library-complete" seemed wrong because the code is hooked in. But when toggled on by a flag, it can halt a running experiment if it detects a mathematical mismatch, which fits neither "shadow" (which only observes) nor "live" (which drives normal decisions). The first two rounds had divided three-to-two on which existing label to force the check into.

Round Three proposed a fourth label: "tripwire". This is the project's new term for code that sits in the pipeline, is observation-only by default, but becomes assertive when an explicit flag is set. Four of the five models agreed this was a cleaner architectural move than forcing a poor fit into the existing three. The fifth (Claude, in the CC2 slot) held that the existing three labels were sufficient if you squinted. Its position is defensible but did not refute the cleaner solution; the new label was adopted. Future flag-gated safety checks now have a category that fits.

The third question concerned the content of three later experiments in the arc, where the test articles have to be drafted from scratch because no existing module fits the experimental need. The panel was asked whether each of three specific refinements should be applied: should a logic-rule cluster be added to the physics module; should a chemistry tool reference be renamed from a generic Python primitive to the actual configured tool name; and should the engineering module gain an optimisation cluster while dropping an astronomy reference that doesn't belong there?

Two of the three refinements drew 5-of-5 agreement immediately: yes, rename the chemistry tool to its proper name; yes, drop the astronomy reference from the engineering module. The third refinement (logic-rule cluster in physics) and a parallel question (optimisation cluster in engineering) divided four-to-one. Four models had read a partial excerpt of a routing configuration in the project's plan that did not show logic-routing for physics or optimisation-routing for engineering. The fifth (Claude again, this time correct) had read the actual configuration files on disk and reported a different picture: both routings DO exist in the source files.

The agent verified by opening the files directly. The fifth model was right. The four-model majority had trusted a partial summary in the plan instead of reading the source. The plan's summary turned out to be the problem, not the configuration. The corrections were applied: the logic and optimisation clusters were added to the relevant test-article descriptions, and the plan's summary text was corrected to reflect what the configurations actually say.

This last finding is more than a minor edit. It is a working demonstration of the project's core methodology: when a majority of expert reviewers agrees but the majority is anchored to a derivative source, going to the primary source falsifies the majority. The dissenting reviewer's persistence carried the round.

## What the three rounds together have accomplished

Round One (21 April) reviewed the full fifteen-experiment plan from end to end. It surfaced and committed to the early code fixes that are now part of Experiment 40's runtime: a corrected mathematics-sandbox configuration that had been silently rejecting every symbolic-math judgement, an activation of a more general mathematical wrapper running in a parameter regime where it reduces to the simpler form, and a debug-time safety check on the same site. It also confirmed the overall scope of the arc.

The overnight follow-up shift (22 April) closed five practical gaps in the runner code with new tests, specified-but-not-yet-implemented entries for three further gaps that the project deliberately leaves for post-mortem evidence to drive, and added a documentation lexicon for component-maturity labels.

Round Two (10 May) closed items the panel had not yet examined: the fix to the audit-logging code, the design briefs for the four later-arc test articles, the trigger specifications for the three deferred arbitration gaps, and the closure-now disposition of four residual concerns from a founder oversight session in April.

Round Three (this round) cleaned up the three points where Round Two had left disagreement.

The cumulative effect: every item that needed expert review before Experiment 40 launches has now been reviewed and converged. The list of items previously flagged as needing founder adjudication is empty.

## What stands ready now

The branch is the project's current development line. The most recent commit captures the Round Three work and the corrections it generated. The test suite still runs at the same 1,311 collected tests as before. There are no pre-launch blockers. There are no founder-judgement items outstanding from the focused-review work-stream.

What remains before Experiment 40 actually dispatches is operational rather than deliberative: a documentation sweep across the project's accessible top-level documents to make sure they reflect current state (the founder has specifically flagged that the README has been somewhat neglected and is the leading item), and then the experiment itself.

After Experiment 40 returns its result, the rest of the arc — fourteen more experiments — proceeds with lessons folded in between each. Four of the later experiments require a small drafting step ahead of their run because their test articles do not exist yet as code modules and have to be written from the design briefs the panel has now finalised; each draft is roughly half an hour of focused work. The rest dispatch immediately against existing code modules.

The founder has named a seven-day window for completing as much of the arc as possible, oriented toward producing a paper or whitepaper that supports outreach to potential funders and reviewers. The pace required is aggressive but feasible.

## What to read next

The agent operational tracker at `experimental_notes/CDSFL_Agent_Operational_Plan.md` carries the next-step pointer and per-experiment matrix. The consolidated plan at `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` carries the full design briefs and trigger specifications. The technical record of this round, with full per-model responses and convergence detail, is the companion to this note at `experimental_notes/Exp40_PreLaunch_Focused_Round3_Outcome_and_Synthesis_2026-05-13.md`.

Written under CDSFL note standard v1.2 (14 May 2026).
