# MATHS REVISION PANEL REVIEW, FULL FINDINGS ACROSS 4 ROUNDS

20 September 2026, 18:21 BST


## What This Review Was


A proposed revision to the project's mathematical model, version 1.1, was produced by an unbounded frontier model asked to improve the existing model. The founder's question was not primarily whether the revision is correct. It was whether the project needs it at all, or whether it is an example of unbounded model churn.

The review ran as 4 rounds of a paid panel. The roster was 7 seats: cc2 and fable on the founder's existing subscription, and cx, cgpt, ge and ds through OpenRouter, with kimi billed to Moonshot credits already bought. The authorised ceiling was 12 pounds. Total spend across all 4 rounds was about 1.49 pounds plus round 4, so cost was never the binding constraint.

Round 4 returned all 7 seats for the first time. Round 3 had lost 2 of them to defects in the project's own dispatch machinery, both since repaired.


## The Verdict, And It Is Unanimous


All 7 seats reached the same verdict: adopt the named corrections. Not adopt the revision as a new model, and not change nothing. Every seat kept the practitioner parameter count at 1. Every seat rejected the revision's multi-state transition apparatus and its decision-value machinery as adding symbols that no live decision reaches.

What changed between rounds 3 and 4 was the ORDER of the adoption list, not its direction.


## The Central Claim Cc1 Put To The Panel Was Wrong, And Is Withdrawn


CC1 reported to the founder, and wrote into the round-4 brief, that 191 fixes had been refused on the strength of a constant nobody measured. That claim is withdrawn in full.

Measured on both refusal paths: all 191 refusals were structural. The proposed fix parsed no usable blocks at all, so it scored 0 and was refused before any constant was consulted. Separately, of 902 scored fixes that did reach the gate, the gate refused 0, with a confidence interval from 0 to 0.4241 percent.

So across the whole archive, the unmeasured constants decided nothing.

Two seats reached this independently before CC1 did. The kimi seat marked the claim partial and gave the exact code reason. The cc2 seat went further and produced the same figure CC1 later produced, 0 of 191, with an interval from 0 to 1.9716 percent.

Worse, the repository already recorded it. A docstring inside the live runner states that the threshold flag reads false 0 times under every method and every corpus tried, and that the gate has never rejected a fix. That statement is pinned by a committed test. CC1 contradicted a test-pinned measurement without consulting it, and then fed the contradiction to 7 paid seats as settled evidence.


## The Item 5 Of 7 Seats Put First Is A Key-Access Hazard


This is the most important single output of the round.

Five seats, cx, cgpt, ge, ds and kimi, all promoted the same item to top priority: wire the existing exam-scoring script to supply the model's parameters, on the grounds that it already computes the recall and false-positive figures the model needs and is currently called by nothing but its own test.

The cc2 seat dissented, and cc2 is right. CC1 verified it directly against the source.

The scoring script takes a path to the answer key and reads it in plaintext. The live runner carries an explicit control stating that no plaintext scoring key may exist while an exam runs, and it refuses to start if that precondition cannot be checked. Wiring the scorer into the live runner as the majority proposes would therefore make the runner read the answer key during a run, which is the exact condition the control exists to forbid.

The cc2 seat names this the failure mode of an earlier experiment, written into the runner instead of into a falsifier. Its alternative design is sound: run the scorer after dispatch, against a vaulted key, and let the result inform the NEXT run's prior rather than the current one.

The panel's majority got this wrong, and the dissenting minority caught it. That is the review process working exactly as intended, and it is a direct argument for keeping panels heterogeneous rather than seeking agreement.


## Panel Independence Was Breached, And The Cause Is The Project'S Own Harness


During round 4, one seat read another seat's answer from the same round.

Measured: the ge seat's recorded tool output contains 4.7945 percent of the cx seat's reply, verbatim, with a confidence interval from 2.8772 to 7.8858 percent. The vector is exact and recorded. The ge seat ran a recursive text search across the bench directory looking for a figure from the brief, and that directory contains the current round's accumulating seat replies.

The timings permit it precisely. The cx seat finished at 117.4 seconds. The ge seat was still working at 279.2 seconds. The dispatcher writes each seat's answer into the live tree as that seat completes, so a later seat searching the tree sweeps its competitors' finished answers into its own context.

The underlying cause is that the 5 paid seats have no sandbox at all. The round's own manifest lists 2 sandbox copies for 7 seats, and both belong to the 2 subscription seats reached through the command line. The paid seats are reached over a network connection and have no working directory to confine, so the containment mechanism that covers the other seats cannot reach them. Their execution tool is confined read-only by the operating system kernel, which was believed sufficient. It is not, because the problem is not what they can WRITE. It is what they can READ.

One clarification, stated because the measurement produced it. An earlier automated reader claimed the overlap was 46 percent. CC1 could not reproduce that figure and reports 4.7945 percent instead, because that is the number with a producing script attached. The finding stands either way; the magnitude is the smaller one.


## A Second, Smaller Correction To Cc1'S Own Instrument


The first version of the contamination detector reported several additional breaches, including one seat reading another that had not yet finished. That is impossible, and it exposed a flaw in the detector rather than in the panel. A single 120-character match between 2 seats answering the same brief is expected coincidence, not contamination. Adding a causality filter, so that a seat can only be accused of reading an answer that existed before it finished, and requiring more than 1 matching window, leaves exactly 1 real breach.


## The Revision'S Own Target Form Is Also Defective


The cc2 seat raised a question the brief did not ask: is the arithmetic the revision proposes to install actually correct?

Its answer is no. It accepts that the existing interpolation is wrong, and accepts CC1's resolution of an earlier apparent contradiction between seats, but argues the revision's replacement is also wrong and names a third form as the correct one.

Independent verification reproduced this 3 ways: symbolic algebra returning a residual of exactly 0 against cc2's stated form, a constraint solver returning unsatisfiable on the negation, and Wolfram Language returning true on a universally quantified statement over the whole parameter box. The Wolfram result is attributed to Wolfram Language and exited cleanly.


## The Correction Is Right And Currently Changes Nothing


A finding CC1 produced while falsifying its own withdrawn claim, and which no seat across 4 rounds had stated.

Every threshold under dispute sits entirely below the observed distribution of fix scores. The lowest score any archived fix received is 0.740000. The live threshold is 0.504931. The alternative threshold proposed by the correction is 0.395043. Of 902 archived scored fixes, 0 fall below either, with a confidence interval from 0 to 0.4241 percent.

So moving the threshold anywhere between those 2 values changes 0 archived decisions. The entire over-refusal debate, which consumed a large part of 3 rounds and produced 3 competing figures of 75.8, 59.66 and 10.4882 percent, is measured over a region of the parameter space that the archive never visits.

The correction remains mathematically right. Its case now rests on being right, not on any harm it has done.


## The Figure That Had No Producer


The round-3 brief presented an over-refusal figure of 75.8 percent as settled, executed evidence. It has no producing script. The seat that supplied it delivered a checking script that runs 23 of 23 checks green and never computes that figure, and in round 4 that seat confirmed it had not re-executed its own number either. Two further seats correctly marked it unverified and accepted it only on the brief's authority.

The brief validator's declared-figure facility, which re-executes any figure a brief quotes, already existed in the repository and would have caught this. It was written after an earlier brief carried a wrong decay figure. It was not used for round 3. It was used for round 4, where all 3 declared figures re-executed and reproduced before a penny was spent.


## Is The Introduction Rate Measurable, And The Median Estimate Is 0.0000


The seats appeared to split and do not actually disagree. The cc2 seat states the resolution cleanly: estimable is not the same as estimated.

The instrument exists and the data is on disk, so the seat arguing it is measurable at the scope where flaws are detectable is right. The estimate that comes out is unusable, so the seats arguing it has no content at the scope the model needs are also right. Beyond the detectable scope it is impossible in principle, because a class of flaw that is never detected never enters any observation channel at all.

The fable seat did what the brief asked and actually ran the fit. The answer is that the introduction rate is not identified on the current archive: the median estimate across 16 usable runs is 0.0000, and 10 of those 16 fall below 0.01. That is a useful answer. It is not a parameter with content.


## Other Findings From The Seat Records


The defective interpolation exists at 6 production sites across 2 runners, not the single site the proposing seat named. Applying its fix as written would desynchronise the runner from its own validator at 55.4460 percent of grid points, which is far outside the validator's tolerance.

Two seats carry provenance defects in their own replies. The ds seat's answer identifies itself as the cgpt seat throughout and refers to ds in the third person, which makes its self-reported round-3 history false for the seat that actually wrote it. The cgpt seat presents an output excerpt that is a splice of 2 separate runs shown as one, above a command that is a comment rather than the code executed.

The cx seat did not finish. It hit the tool-call ceiling and was forced to synthesise early, and its named falsifier for one finding cannot fail.

Of 21 claims put to independent verification by re-execution, 21 reproduced.


## What Remains Open, And It Is Not The Threshold


The question no round has addressed. Of 902 archived scored fixes, 672 score exactly 1.0. A gate cannot discriminate within a distribution piled at its ceiling, whatever value the threshold takes. Whether the scoring mechanism discriminates at all is a better question than where the threshold sits, and unlike the threshold debate it would change something.


## The Containment Question The Founder Has Raised


The founder's position is that no model, under any configuration, should ever be able to reach the real repository, let alone edit it. The measurements above show the current arrangement does not meet that standard for the paid seats, and the reason is structural rather than accidental: the containment mechanism confines by working directory, and a seat reached over a network has no working directory to confine.

The founder also raises a genuine design question that the project does not appear to have settled anywhere. The experimental runners already encode an answer: the first review round is blind, and subsequent rounds are open. The panel review mode has no equivalent stated rule. Whether panel seats SHOULD see each other's answers is therefore an open decision rather than a defect, even though the way they currently see them, by accident of a text search, is plainly a defect.

Written under CDSFL note standard v1.7 (26 August 2026).
