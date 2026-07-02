# CDSFL Full State Assessment — Plain English

2026-07-02 23:35 BST

A complete picture of where the project stands, written after a roughly three-week pause (11 June to 2 July 2026) and a full recovery of the working record. It is written for a reader with no prior session context.

## What the project is

CDSFL is a method, and a working system, for making AI-assisted technical work trustworthy. Its intellectual root is Karl Popper's principle that knowledge advances by attempts to disprove claims, not by accumulating agreement. The system puts five different AI models, from four different companies, to work reviewing a piece of real software, under one governing rule: **tools decide, not votes.** When a model claims it has found a serious defect, that claim must arrive with a runnable test that demonstrates the defect against the real code. An independent referee program re-runs that test, and the test's outcome, not the model's confidence or the panel's opinion, settles the matter. Whatever the tools genuinely cannot decide goes to a human referee, and the system is engineered to keep that human queue as small and as legitimate as possible.

Underneath sits a simple, powerful piece of mathematics: diminishing returns. As a review proceeds, genuinely new serious findings become rarer, following a decay curve. The slope of that curve, called gamma, measures how depleted the space of findings has become. Gamma is the foundation of the whole model, and by standing directive it is an active, central measure of convergence, never a decorative statistic.

## The central result: honest convergence, proven twice

The project's core claim is that such a panel, properly instrumented, will converge honestly: it will find the real defects, verify them mechanically, and then recognise when it is finished. That claim is now demonstrated on two separate experiments. In May, the panel converged cleanly on the project's own mathematics module at round six. In June, it converged on the directive composer, a substantially larger module, again at round six, and with zero findings left needing human adjudication.

The road there is as important as the destination, because every obstacle turned out to be mechanical plumbing, never the mathematics. Four faults were found and fixed in sequence. First, models were producing findings without runnable tests, which was repaired route by route until all five models produced testable claims. Second, broken tests that exited quietly were wrongly counted as disproving real defects, so the rules were changed so that only a positive demonstration can resolve a serious finding. Third, when a weaker model could not manage to demonstrate its own finding, the finding used to dead-end; now it climbs a ladder to progressively stronger models before any human is asked. Fourth, and decisively, the bookkeeping that decides whether a finding is new was keyed to labels the models invented, so the same defect rediscovered under a fresh label kept counting as new and the system could never see that it was finished. The fix keys novelty to the actual location in the code that a finding points at. With that in place, convergence appeared exactly where the mathematics predicted it.

The founder maintained throughout that the mathematical model was sound and every failure would prove mechanical. That position was vindicated at every single step.

## How the finishing line is now judged

A run is declared finished only when two readings of the same diminishing-returns curve agree. The first is gamma itself: the decay curve of serious findings must have genuinely flattened. The second is a strict count: three consecutive review rounds must produce no new serious finding. Neither alone suffices; both must hold. This two-sided design was settled by founder ruling on 10 June and verified against both successful runs: on each, the gamma reading comfortably cleared its threshold, and the two conditions agreed, with the strict count being the later, binding one. Safety guards surround the gate: an unverified serious finding blocks completion outright, and a suspiciously large pile of unresolved escalations sets off an alarm rather than being waved through.

One clerical confusion is worth recording plainly: an older note gave the May run's gamma as 0.240, which appeared to sit below the threshold. That number was the decay reading over all findings of every severity, which is not what the gate reads. The gate reads the serious-findings curve, and on that curve the May run scores a perfect 1.0. The distinction is now documented everywhere it matters.

## What is genuinely live, and what only appears to be

An honest inventory distinguishes three tiers. Genuinely live and driving decisions: the runnable-test gate, the stronger-model ladder, the location-keyed two-sided finishing gate, the feedback and divergence instructions to models, and the specialist verification cells for mathematics, statistics, biology, information science and software. Built and fully tested but deliberately inert: a severity-calibration mechanism that can lower the rating of a proven-real but practically-dormant defect so it stops blocking completion, which waits only on a small companion piece that tags such findings. Running but decorative: an anomaly-monitoring cell and a literature-research cell whose outputs are logged but reach no live decision, and a novelty calibrator whose estimates never enter the live equation. Written but never executed: a work-allocation component, kept deliberately for the future large-scale phase, and an older convergence detector that was tested against the new one and lost, decisively.

## The experiment programme

The validation campaign walks through the system's own components one at a time. Experiment 40, on the feedback module, taught most of the hard lessons without converging under the early rules. Experiment 41, on the mathematics module, converged. Experiment 42, on the composer, converged with zero human escalations, the landmark. Experiment 43 is next and is the pivotal generalisation test: the same instrument pointed at a different module, the anomaly-monitoring cell, to establish whether the convergence machinery is general or was somehow particular to one target. Its configuration is written, checked end to end, and ready to launch. Beyond it lie a composition test, further component targets, four purpose-written science modules in biology, physics, chemistry and engineering, and a final integration experiment. The eventual 27-problem frontier science benchmark remains deliberately gated behind all of this.

## What blocks the next step

Three things, all small and explicit. First, three API keys for the external model routes are missing from the project's credential file; the June runs used keys typed into a live terminal session, which vanished with it. Restoring them takes minutes and unlocks both the next experiment and the full five-model review panel. Second, the AI vendor's pricing changed during the pause: the premium model tier moves to metered billing on 7 July, and programmatic usage now has its own meter, so run costs deserve a glance before long runs, though the project's design deliberately does not depend on any premium driver model. Third, four decisions rest with the founder: whether to give the anomaly monitor a real voice or retire it, whether to confirm keeping the dormant work-allocator for the future, whether to authorise the careful consolidation of duplicated convergence code, and whether to approve a component rename.

## The immediate path

Keys into the credential file, then launch Experiment 43 under live monitoring. Fold the findings of Experiment 42 back into the system, checking each for staleness. Build the remaining small pieces, each accepted only when an integration test proves its output changes a real decision. And put the instruction-pruning question to the full model panel: measurement during the June work established that each model receives about fifty thousand characters of standing instructions, of which nearly forty-four thousand bypass the trimming machinery entirely, and a careful reduction plan exists awaiting the panel's critique.

## Bottom line

The project set out to show that a panel of rival AI models, disciplined by falsification and governed by tools rather than votes, can review real software and honestly know when it is done. That is now demonstrated twice over, with the finishing line judged by a two-sided reading of the diminishing-returns curve that sits at the heart of the project's mathematics. The instrument is built, tested, and waiting; the next experiment is fully prepared; and the gate between here and it is three API keys.

Written under CDSFL note standard v1.2 (14 May 2026).
