# Panel Review of the Stage 1 Audit, and the Cause of the 97% Removal Rate

**18 August 2026, 15:05 BST.** Plain-English companion; mirrors the TTS file of the
same name in `~/Desktop/CDSFL_tts/`. Full verbatim panel record, all five models:
`Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md`.


## SUMMARY


A 5 model review panel was dispatched to audit three days of assistant findings and
to recommend a path to Bench Run 2. All 5 returned. The cost was roughly 1 to 3
pounds for the 4 metered routes; the fifth runs on an existing subscription.

The panel found the cause of the immune pipeline removing 97 percent of everything
handed to it for the past 4 months. It is one line of arithmetic in the similarity
module. The assistant has independently reproduced the measurement.

The panel also refuted 3 separate claims the assistant had made, including one the
assistant had reported as verified earlier the same afternoon. Each refutation is
recorded below with the measurement that settled it.

No archived experiment changes its convergence verdict. No result is invalidated.



## THE HEADLINE. ONE LINE OF ARITHMETIC


The similarity module compares two findings and returns a score. Part of that
calculation converts a cosine, which in general ranges from minus 1 to plus 1, onto
a 0 to 1 scale. It does this by adding 1 and dividing by 2.

That conversion is correct for a quantity that actually uses the range minus 1 to
plus 1. Sentence embeddings of ordinary English do not. Measured on experiment 46's
27 archived findings, which is 351 pairs: the lowest cosine observed is 0.150 and
NOT ONE of the 351 is negative.

So half the output range is dead. Every real score is squeezed into the upper half.
After the class blending step, the lowest possible score any pair can receive is
0.460.

The duplicate threshold is 0.50. It was calibrated for the older word overlap
backend, whose floor genuinely is 0. When the embedding backend was substituted
underneath it on 12 April 2026, the threshold was not recalibrated.

The result: the entire live range of the score sits within 0.04 of the threshold.

Measured flagging rate under the current arithmetic: 97.4 percent of all pairs
declared duplicates. The rate logged by the pipeline itself over 4 months is 97.1
percent. The mechanism is reproduced.

Worse, and this is the part that makes it structural rather than merely badly tuned.
When 2 findings share a flaw class they receive a small bonus. With that bonus the
lowest possible score is 0.541, which is ABOVE the threshold. Measured flagging rate
for class matched pairs: 100.0 percent, all 79 of them.

Any 2 findings that share a flaw class are duplicates by construction, regardless of
what they actually say.

The proposed fix is to clamp the negative half away rather than fold it in. Measured
on the same 351 pairs, flagging falls from 97.4 percent to 15.8 percent for pairs
without a class match, and from 100.0 percent to 40.5 percent with one. This is a
bug fix, not a recalibration: the old conversion was spending half its range on a
region the data never visits.

Status: PROPOSED. Not built, not tested, not committed. It is a one line change and
it can be validated offline against the 85 tool decided labels at no cost.



## WHAT THIS MEANS FOR THE EXISTING EXPERIMENTS


The panellist with repository access put the consequence plainly, and it is the most
important sentence to come out of this review.

Every convergence in experiments 44 through 49 was reached while the duplicate
discriminator was saturated. For 4 months, every model was told at the start of every
round that essentially all of its prior findings were near duplicates, and that it
must either prove them distinct or withdraw them.

The convergence data therefore measures a panel operating under a standing
instruction to stop reporting. The decay curves are real curves, but they are curves
of a suppressed process.

This is not a claim that the mathematical model is wrong. There is no evidence
against it. The claim is narrower and it is about the runs, not the theory: the runs
are contaminated, the contamination has a known start date, and it now has a known
one line cause.

Experiment 50, run after the fix, would be the first uncontaminated measurement of
the thing this project exists to measure.



## WHERE THE PANEL REFUTED THE ASSISTANT


Three refutations, each settled by measurement rather than by argument.

FIRST. The source pack given to the panel mislabelled its 2 most important sections.
A code excerpt captioned as the two sided convergence gate was actually a different
function, and an excerpt captioned as the settled novelty series was also a different
function. The panellist with repository access caught this and added the part the
assistant had missed: the function shown to the panel is switched off in all 6
experiment configurations. It is not running in this arc at all.

The conclusion the panel reached was nonetheless correct, but it was reached from
evidence the assistant had supplied wrongly. What actually carried the verdict was
the empirical reproduction test, which does not depend on the mislabelled excerpts.

SECOND, and this is the serious one. Earlier the same afternoon the assistant
reported that a defect in the convergence gate's counting input was dormant, with
zero measured effect across all 6 archived runs. That was WRONG.

The measurement had called a function from the convergence location module. The
runner calls a differently named function inside the runner itself. Two different
functions with different signatures. Re measured with the runner's own function,
experiments 44 and 47 both carry stale gate inputs, and the assistant's corrected
figures now reproduce the panellist's independent numbers exactly, down to which
individual rounds differ.

The direction matters. The staleness is PERMISSIVE: experiment 44 under counted
critical findings by 2 and experiment 47 by 5. The gate consistently saw fewer
critical findings than the registry actually held, and under counting criticals makes
convergence easier, never harder.

No archived verdict changes. Both gate windows read 3 consecutive zeros whether the
input is stale or settled.

THIRD. The script that assembles the panel record reported 5 of 5 panellists
returning, while one of those 5 files was a failure record from 3 timed out attempts.
It counted whether a file existed, not whether it contained a response. That is the
governing failure mode of this project, which is that every failure renders as a
confident success, reproduced in the instrument built to record the review. Repaired
to count successes.



## THE ONE LINE DEFECT IN THE ASSISTANT'S OWN REPAIR


The repair committed this morning recomputes a counting list called novelty counts
across every round. The panellist with repository access observed that this list is
not the one the live gate reads. The live gate reads a different list called novel
critical history, and that list carries exactly the same defect the repair was
written to fix: only its final position is ever corrected.

So the repair fixed the copy that does not gate convergence and left the copy that
does.

The same panellist found a further hazard. The retroactive loop assumes the list
index equals the round number. There is a phase transition path that clears the list
mid run, after which index 0 is no longer round 0 and the loop writes wrong values
into every position. This is dormant, because the relevant mode is switched off in
every current configuration, but it is a live hazard for any future Bench Run 2
configuration that enables phases.



## WHERE THE PANEL DISAGREED WITH ITSELF


Disagreement was preserved rather than smoothed. Three genuine splits.

On the churn detector, which cannot fire before round 12 while 5 of the 6 recent
experiments never reach round 12. One panellist called this a critical blocker. Two
called it moderate. The panellist with repository access rated it highest of all, on
a ground the others did not raise: the churn signal is a blocking condition inside
the convergence gate, so a detector that cannot fire is a disconnected safety
interlock, and its failure direction is permissive.

On formalising the simplest sufficient fix principle in the mathematical model. One
panellist argued that a core principle left only in the written directives will be
ignored whenever model attention drifts, so it must be formalised. Three argued
against, on the ground that any measure of simplicity available today is gameable by
a model that has been told it is scored on it, and that it would let a run converge
because fixes got shorter rather than because discovery was exhausted.

On whether to build the duplicate counter now. Two said no, the signal is too thin at
13 pointers across 6 experiments. The panellist with repository access said build it
but do not interpret it, on the ground that 13 is not a measurement of corroboration
at all, it is a measurement of the suppression, and the counter is the instrument
needed to read the first fixed run.



## ON THE BUGZILLA RULING


All 5 panellists endorsed preserving the duplicate record, which the system already
does correctly. All 5 independently broke the analogy at the same joint.

In Bugzilla, 2 reports are duplicates if they share a root cause in one codebase,
which is a fact about a shared inspectable substrate. Two findings about a scientific
claim can name the same passage and be different errors in it. The system's own code
documents this limitation directly: location based keying cannot see a second
distinct defect in an already flagged function.

On resolution, the break is sharper. In Bugzilla a bug is resolved when a fix lands
in code the maintainer controls. A scientific claim can be wrong about the world, and
resolved then means one of 2 very different things: the text was repaired, or the
claim was shown false. Bugzilla has no state for the reported behaviour being correct
and the specification being wrong. This system needs one.

On the simplest sufficient fix, the principle is right and the Bugzilla provenance
for it is not. In software it is a maintenance virtue about minimising regression
risk. In science parsimony is a claim about explanations. The two coincide only
sometimes, and a minimal textual patch to a paper can leave the underlying error
untouched.



## WHAT THE PANEL RECOMMENDS


All 5 agree on the ordering. The immune pipeline fix comes first, ahead of the
remaining accounting work. No money is spent on the full experimental arc until one
live shakedown run shows sane throughput.

The zero cost work, in order:
1. Clamp the cosine conversion in the similarity module. One line.
2. Remove the early exit in the duplicate search loop, which currently stops at the
   first match above threshold rather than the best. Invisible at 97 percent
   flagging, visible at 16 percent.
3. Replay the archive under the clamp and score it against the 85 tool decided
   labels. This is the real Stage 1 exit test.
4. Extend the morning's repair to the list the gate actually reads.
5. Rebuild experiment 47's report from its raw round files, which are all present.
6. Lower or make adaptive the round 12 floor on the churn detector.

Then one live validation run before anything else is spent.

One panellist raised a matter not covered by any question. 17 answer key files remain
reachable from a remote branch, including keys for experiments 50, 51 and 52, which
have not been run. It rated this a validity blocker to be cleared BEFORE any live
run, not as housekeeping. That requires a founder decision.



## WHAT REQUIRES A DECISION


1. Whether to delete the remote branch carrying the 17 answer key files. Panel
   endorsed as blocking. The archive is already bundled, encrypted and restore
   tested, so the history is not at risk.
2. Whether the churn detector's round 12 floor is lowered before Bench Run 2, which
   turns on how many rounds Bench Run 2 runs are expected to take. Nobody has stated
   that figure, which is why the panel split on the severity.
3. Whether the duplicate counter is built now as an instrument or deferred.

Everything else on the list is zero cost and is the assistant's to execute.


---

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
