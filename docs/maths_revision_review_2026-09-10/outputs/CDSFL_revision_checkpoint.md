# CDSFL revision checkpoint — proposal complete

**Updated:** 2026-09-09 23:09:47 UTC (10 September 2026 in London).
**Status:** the authorised mathematical revision proposal is complete. No empirical deployment or upstream implementation is claimed.

## Start here

1. [Revised model specification, version 1.1](./CDSFL_revised_model_specification.md).
2. [Prospective validation plan, version 1.1](./CDSFL_revised_model_validation_plan.md).
3. [Plan and detailed work record](./CDSFL_revision_plan_and_log.md).

## Completed result

The compact core is:

R_next = ((1-s) L R + b (1-R)) / (L R + 1-R).

R is scoped pre-observation failure probability; L is the likelihood ratio of the actual evidence; s is conditional net removal; b is conditional introduction into initially clean targets. The specification includes a likelihood-pair form, complete conditioning and selection requirements, a derivation, and the preserved original coverage/clean-review special cases.

The severe-test addition uses beta=P(pass|flawed) and gamma=P(pass|clean). It derives the posterior bound from independently supported bounds on these quantities. An abstention counterexample defeated the initial binary-only generalisation; the correction is recorded. The core formula did not need changing.

A dependency audit prevents using the desired conclusion to justify its own empirical inputs. Each optional mathematical component has an explicit purpose and an admission criterion.

## Evidence preserved

- Original repository snapshot: jebus197/Constraint_Engineering at 9e3dfe9d68b428acb98e65c0ad3800ec571a4da4.
- [Input manifest](./CDSFL_revision_input_manifest.json): four original documents, preceding review and checks, supplied transcript.
- [Main exact-check report](./CDSFL_revised_model_check_results.json): 5,600 conditional cases; 650 impossible discrete observations; 2,000 branch-policy cases; 125 sequential-repair cases; 125 reductions/expectations; eight incorrect alternatives rejected.
- [Severe-test report](./CDSFL_severe_testing_check_results.json): 450 constructed bound cases and three incorrect alternatives rejected.
- [Final file manifest](./CDSFL_revision_final_manifest.json): hashes for deliverables and supporting work, excluding the manifest itself.
- Separate derivation, adversarial, and validation-design records: work/revision-core/, work/revision-challenge/, work/revision-validation/.
- Earlier version 1.0 documents: work/revision-history/.
- Transcript: work/math-review/Sabine_Maths_and_Circular_Reasoning_transcript.txt.

These are mathematical checks and recorded reviews, not independent empirical samples. A supplemental final validation-document reread failed on a usage limit; that incomplete pass is not counted as supporting evidence.

## What remains for a future authorised phase

- Obtain an external probability/statistics and domain review.
- Select a small independently resolvable STEM task family.
- Run the diagnostic pilot; freeze a calibration/evaluation protocol.
- Compare forecasts and research decisions against simple baselines on new outcomes.
- Implement a versioned migration only when requested; test transfer before broader claims.

The empirical inputs, practical benefit, broad transfer, and application-level originality remain unestablished. Their validation is outside this completed proposal. Do not restart completed derivations merely because the conversation was interrupted.

## Persistent constraints

Preserve human comprehension and the general STEM ambition. Keep truth claims, evidence, target-changing actions, novelty, and resource decisions distinct. No confidence from AI votes; no self-certified calibration or utility. Usage interruptions do not authorise purchases, resets, subscriptions, or scheduled work.

## Subsequent clarification

[Lineage and decay clarification](./CDSFL_lineage_and_decay_clarification.md) explicitly derives the original coverage and risk curves from the revised core and explains the continuing role of Duane discovery-rate models. The core version 1.1 specification was not changed.

## Human explanation clarified

The specification and lineage note now include the founder's phrase “Capable repeated examinations” and explain the conditions for cumulative corroboration. They explicitly state that the mathematical/methodological account can be assessed independently of the CDSFL harness. This is a prose clarification; all equations and computational results are unchanged.
