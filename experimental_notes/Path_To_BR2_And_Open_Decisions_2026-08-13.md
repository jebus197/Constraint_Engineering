# The path to Bench Run 2, and the decisions still open

2026-08-13. Written under CDSFL note standard version one point four. This is a reply file, so it addresses you directly.

You asked whether the previous file did all of this. It did not. It answered your annotations, gave the build status of each fix, and named the components you asked me to name. It did not set out the open decisions as a list, and it did not sequence the work. This file does both.

Short answer to your other question. Yes, the path is now meaningfully narrower, and there is a specific reason rather than a general feeling. The panel converged list of ten prerequisites, recorded as items A1 through A10 and described in the queue as blocking every remaining run, is now fully closed. All ten are marked done with commit references. That list was the blocker for the whole remainder of the arc, and it is gone.


## What the queue actually says is left

The live queue names five legs in order. Experiment 53, the zero plant control, paused four rounds into a run. Experiment 50, physics, not started. Experiment 51, biology, not started. Experiment 52, the four cell factorial capstone, not started. Then Bench Run 2.

Everything after the control was blocked on two things: the A1 to A10 list, and the control result. The first is closed. So the control is now the single item gating the rest of the arc.

The capstone carries one extra blocker of its own. Its examination article and answer key are recoverable from published version history, and the reseed has not been done.


## Decisions you have already made, so they are not reopened here

You ruled for a clean control, built working directly with the panel to ensure any new target is genuinely and demonstrably clean.

You ruled do it on the structured statement of numbers, which is your own criterion.

You gave a provisional yes to the perturbation instrument, conditional on clarification. The clarification is in the previous file and the worked example is repeated below, so this now needs only a confirmation.

You approved the four repairs on 10 August with the words go, no further comments.


## Decision one. Confirm or withdraw the perturbation instrument

Status: proposed only. No code exists.

Worked example, since you asked what perturbs it means. Claim ZC-17 in the old control document states that the index used by the hash ring stays within the bounds of the list of servers. Suppose a falsifier accuses that claim. The runner copies the document, changes a number inside the accused passage, say 400 becomes 401, and re-runs the same falsifier against the copy. Then it makes a second copy, changes an unrelated sentence in a different section, and re-runs again.

If the verdict flips when the accused passage changes and holds when the unrelated one changes, the falsifier genuinely depends on the passage it accuses. If the verdict does not move when the accused passage changes, the falsifier is not testing that claim at all. If both changes move it, it is testing nothing in particular. If neither moves it and the falsifier keeps failing, the fault is in the equipment rather than the document.

Cost: three extra executions per confirmed finding, on this machine, no model calls, so computer time and no money.

The problem it addresses is observed, not supposed. Finding C0012 in the chemistry experiment fired because it opened the answer key and printed the planted claims, not because the chemistry was wrong. That is in the archive.

Recommendation: build it, and build it before the capstone. The mechanism currently in place for this job is the discrimination control, which cannot work on a document believed to be correct, because it needs a corrected copy and a corrected copy requires already knowing the answer.


## Decision two. The file access check

Status: built and committed, currently recording only, blocking nothing.

You asked whether this guards against something real. Supposed, not observed. No model has been seen opening a file and discarding its contents to satisfy the check. The concern came from a panel model reasoning about what a model might do if its findings started being refused.

Recommendation: leave it recording and do not arm it. Recording costs nothing and it is the only check that can run on every falsifier rather than a fifth of them. Arming it would be a guard against a thing that has not happened, and you are right that this project should not spend its vigilance that way.


## Decision three. What happens to findings reclassified as equipment error

Two illustrative examples, as you asked.

First. A run reaches round eight with three serious findings outstanding. The verdict reader inspects them and finds all three failed in their own setup before ever reading the target, so it reclassifies them as equipment error. Under the current rule they stop counting, the round eight count becomes zero, and if rounds nine and ten are also quiet the run declares itself finished. Three real questions were never answered and the run reports success.

Second. Same run, alternative rule. The three stay in the outstanding count until cleared by a human. The run does not finish at round ten. It either continues or it stops and says three items await a human, which is an honest description of where it is.

Your own suggestion was a third option: treat them as residuals to be cleared in the post run sweep. That is better than either of mine. It keeps the run moving without pretending the items are gone, and the sweep already exists.

Recommendation: your option. Mark them as residuals, clear them in the sweep.


## Decision four. Stage 6, and a numbering fault you spotted while I was writing this

Status of Stage 6: built. Not running. It leaves no shadow record in any run directory, whereas the ouroboros component has left records in ten and the macrophage component in twenty eight.

You said the numbering mismatch was probably never fixed. You were right, and it is worse than not fixed. There is a dated correction notice in the operational tracker from 20 July, written to stop exactly this confusion, and that notice is itself wrong.

Checked against the run directories, which are ground truth because they are what actually executed, the 20 July map fails on six rows. It has experiments 44 and 45 swapped: it says 44 was the statistics memory module and 45 was the evidence module, when the run record shows the reverse. It says experiment 48 was biology and 49 was physics, when the runs were the chemistry examination and the engineering examination. It says 50 is chemistry and 51 is engineering, when both of those have already run and 50 and 51 are the two that have not started. And it does not mention experiment 53, the zero plant control, at all, although a paused run directory for it exists.

The consequence, had this gone unnoticed: an agent following either the plan table or the 20 July map would re-run three completed experiments, and would run an engineering configuration in the slot the control occupies.

The correct sequence, verified against the run record today, is this. Experiment 44 was the evidence module. 45 was the statistics memory module. 46 was Stage 6. 47 was the divergence directive. 48 was the chemistry examination. 49 was the engineering examination. 50 is physics and has not started. 51 is biology and has not started. 52 is the four cell factorial capstone and has not started. 53 is the zero plant control and is paused.

Stage 6 therefore already ran, as experiment 46. Any plan text describing a forthcoming Stage 6 study is stale by that fact.

Status of the fix: built, in the operational tracker, as a dated correction that carries the measured table and names the queue as authoritative. Not yet committed. The Desktop copy of the tracker re-syncs at the next save.

Recommendation on Stage 6 itself: mark it as not implemented rather than as running in shadow. Describing an absent component as shadow is the ambiguity that reads worst to an outside reviewer.


## Decision five. The survived falsification ledger

Status: built on 8 August, connected to nothing. The name is mine rather than an agreed project term.

Recommendation: withdraw the claim that the project holds such a record until you have agreed both what the ledger should do and what it should be called. Two lines of plumbing would connect it, but connecting a thing nobody named is how the vocabulary drifted in the first place.


## Decision six. The two real defects in the old control document

Status: both present in the document as it stands. The rate limiter admits a negative cost. The hash ring routes an exact match to the wrong server.

Since you have ruled for a new clean control, the old document is no longer the control. That leaves a choice about what to do with it.

Recommendation: keep it, repair nothing, and use it as the planted arm. You already have a document with two known, real, independently confirmed defects that a competent panel ought to find. That is exactly the instrument a clean control cannot be. Building a planted target from scratch would be work, and this one has been validated by two separate live runs finding the same defects.


## Decision seven. Reseeding the capstone article

Status: not done. The capstone examination article and its answer key are recoverable from published version history, one of them byte for byte.

You ruled on 10 August to accept the exposure and reseed. That ruling stands and the work has not been done. It gates the capstone and nothing else.

Recommendation: reseed the capstone article only, not all three. Physics and biology recover as earlier drafts rather than exact copies, and the capstone is the one that recovers exactly.


## Decision eight. The targeted shakedown experiment

This is your proposal and I recommend it, with two changes.

Your proposal is to stop treating the load balancer as dead code and instead give it to the panel as an experiment where the task is not only to find faults but to judge whether the component is worth keeping, whether it can be extended, or whether something else should replace it, and then to build it out so a researcher can switch it on.

Why it is worth doing. Every experiment so far has asked the panel to falsify something that exists. This asks it to judge whether something should exist, and then build it. The machinery has never been tested on that question. If it works, that is a new result rather than a repeat, and it exercises every fix made this week on a real task before those fixes touch the capstone.

First change. The external research already answers part of your scaling question and the answer constrains the design. A study titled nine judges, two effective votes found that correlated errors between models mean a panel of nine behaves statistically like a panel of two. Adding more models of similar training does not buy proportionally more coverage. So the useful axis is not more models answering the same question. It is dividing a problem into parts that different models work on separately, which is the distinction you drew yourself. Give the panel that finding in the brief so they start from the constraint rather than rediscovering it.

Second change. Cap the spend explicitly and run it after the control target is built but before the capstone. This is the kind of open ended task that absorbs money quietly.


## The sequence, with what each step depends on

Stage zero. Free, offline, can start immediately. Enable the structured statement of numbers and replay it across the archive to confirm it changes no historical outcome. The structured statement of numbers is built, tested at ninety four passing tests, committed, and not enabled: zero configurations switch it on. The combined identity rule is in the same state. No money, no dispatch.

Stage one. Build the new clean control target with the panel, as you ruled. Generated from a script rather than written and then checked, so that correctness is a property of the generator. Small paid panel task. Keep the old control document as the planted arm alongside it.

Stage two. The shakedown experiment on the load balancer, capped. This exercises every fix from this week on a real task and answers the scaling question.

Stage three. Run experiment 53, the control, on the new clean target.

Stage four. Experiments 50 and 51, physics and biology. Both were blocked on the A1 to A10 list and the control result. The first is closed and the second arrives at stage three.

Stage five. Reseed the capstone article, then run experiment 52, the four cell factorial.

Stage six. Bench Run 2.

The dependency chain is now short and every link is named. The only step that cannot start today is the capstone, and it is waiting on the reseed rather than on any repair.


## Money

The last balance recorded in the recovery document is four hundred and seventy one dollars and nine cents, dated 28 July. That figure is two weeks old and I have not verified it. It is worth checking before stage two, because the shakedown is the one step whose cost is genuinely open ended.

One paid dispatch has been made since, at roughly three pounds.


## What is not narrowed, stated plainly

Three fixes are built, tested and committed but have never run in a live experiment. Until stage zero completes, their behaviour under real conditions is unmeasured, and unmeasured is not the same as working.

The false alarm rate of this system has still never been measured, and it cannot be measured until a genuinely clean target exists. That is stage one and stage three, and it is the honest reason the control matters more than its position in the queue suggests.

Written under CDSFL note standard v1.4 (13 August 2026).
