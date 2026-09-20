# CDSFL mathematical revision — plan and work record

**Owner:** George Jackson. **Date opened:** 9 September 2026. **Purpose:** develop a reviewable mathematical revision that preserves the ambition of a generally useful, human-comprehensible account of structured scientific enquiry.

**Authorised scope:** suggest and derive fixes and improvements, test them, document their limits, and apply the proposed framework to the review itself. Repository implementation is deferred. No changes to the upstream repository, purchases, subscription changes, or external communications are authorised by this work.

**Continuity:** this file records the plan, actions, evidence, decisions, and unresolved questions. `CDSFL_revision_checkpoint.md` identifies the current stopping point and next actions. Detailed derivations and executable checks are saved as separate deliverables. An interruption does not make an unfinished step complete.

## Acceptance criteria

1. A compact final equation with a plain-language reading and explicit definitions of every quantity.
2. Derivation from a stated observation-and-action model; no substitution of a confidence score for a calibrated probability without disclosure.
3. Preservation of the valid original coverage and clean-review Bayesian equations as identifiable special cases.
4. Correct handling of positive and negative observations, dependence between reviews, failed repairs, new errors, and changed targets.
5. Separate treatment of evidential strength, scientific novelty, expected utility, and resource allocation.
6. Exact worked examples, boundary checks, independently enumerated outcome trees, and deliberately faulty alternatives that the checks reject.
7. Explicit limits on scalar compression, parameter uncertainty, generality, and any claim of novelty.
8. A prospective empirical falsification and calibration plan.
9. A transparent self-audit using the revised concepts, without treating the proposal as evidence for its own assumptions.
10. A semantic dependency audit for conclusions concealed inside premises.
11. A measured severe-testing connection and explicit handling of unresolved outcomes.
12. A stated purpose and admission criterion for every optional mathematical component.

## Work plan

| Phase | Work | Status |
|---|---|---|
| 1 | Preserve the audited source snapshot, prior findings, scope, and user constraints. | Complete: files retained and SHA-256 manifest written. |
| 2 | Derive a minimal observation-plus-action model and compare compact formulations. | Complete: general net-removal/introduction form selected; sequential form derived. |
| 3 | Test special cases, counterexamples, boundaries, correlations, and changes of target. | Complete: exact suite and separate challenge scripts passed. |
| 4 | Specify calibration, decision rules, novelty accounting, and empirical refutation. | Complete: version 1.1 specification and prospective validation plan. |
| 5 | Challenge the proposal independently where resources permit; apply it to its own claims. | Complete: bounded derivation/challenge passes, self-audit, and severe-test correction. Same-model checks are not independent empirical evidence. |
| 6 | Produce the simplified explanation, detailed specification, executable checks, and final checkpoint. | Complete: version 1.1 documents, executable checks, checkpoint, and final provenance manifest. |

## Starting evidence

- Audited repository: `jebus197/Constraint_Engineering` at commit `9e3dfe9d68b428acb98e65c0ad3800ec571a4da4`.
- Local source copies: `work/math-review/PAPER.md`, `MATHEMATICAL_APPENDIX.md`, `README.md`, `EXPERIMENTAL_RESULTS.md`.
- Previous review: [CDSFL_mathematical_review_2026-09-09.md](./CDSFL_mathematical_review_2026-09-09.md).
- Previous exact checks: [CDSFL_math_counterexamples.py](./CDSFL_math_counterexamples.py). These passed during the preceding review and will be used as regression cases for the proposal.
- Central accepted components: conditional detection coverage, the negative-observation Bayesian update, and algebraic properties of the stipulated recurrence where correctly stated.
- Central objections: a negative-observation posterior was interpreted as repair benefit; literature originality was allowed to suppress genuine evidential contribution.

## Action and evidence log

### Before 17:57 UTC — start of revision turn

- Confirmed working directory and inventoried the retained source and review files.
- Retrieved callable GitHub read-tool descriptions. No new repository content or revision was selected; the proposal is based on the audited frozen revision.
- Assigned an independent derivation task named `revised_core`, requesting a compact generative model, exact reductions, and edge cases. It returned a usage-limit error without a completed review. Its work is not counted as supporting evidence.
- User clarified that interruptions may occur and explicitly requested a careful persistent record, a plan, and a self-audit using the revised model. Confirmed the approach is rational with the limitation that self-consistency does not independently validate assumptions.

### 17:57 UTC — continuity setup

- Checked applicable ancestor `AGENTS.md` paths; none were present at the checked paths.
- Checked for a dedicated plan tool; none was available. Adopted this file as the written plan.
- Read the UTC clock: 2026-09-09 17:57:38 UTC.
- Created this plan/log and the checkpoint file before continuing mathematical work.

## Decisions so far

- Preserve the original model's valuable goals and valid identities while deriving corrected state transitions explicitly.
- Keep publication novelty separate from the likelihood of evidence.
- Evaluate both a general two-state action transition and a sequential repair/reinjection special case before choosing the human-facing collapsed form.
- Treat no-progress/usage-limit interruptions as incomplete work, not negative scientific results or approvals.
- Use probability labels only when their event definitions and conditioning are explicit; retain an honest `unestimated` state when calibration is absent.

### Subsequent work — derivation and independent challenge

- Wrote `CDSFL_revision_input_manifest.json` with byte counts and SHA-256 hashes for the four canonical documents and two previous review deliverables.
- Retried `revised_core` after the user's resumed turn. This retry produced an independent derivation of the same Bayes-plus-two-state-transition core. The initial failed attempt still counts as incomplete, not evidence.
- Started `revision_validation` to design prospective calibration/refutation and `revision_challenge` to attack the candidate's assumptions.
- Checked the default Python environment: SymPy was unavailable. Exact arithmetic and independent outcome enumeration will be used without installing packages; mathematical identities will also receive written derivations.
- Searched primary sources on Bayesian reliability, model checking, and probability scoring. Located NIST's Bayesian reliability handbook, Gelman and Shalizi's paper on Bayesian practice/model revision, and primary papers on calibration/proper scoring. These provide context and precedent; they do not validate the proposed CDSFL application.
- Derived the candidate `R_next=[(1-s)L R+b(1-R)]/[L R+1-R]`, with s defined as net removal and b as clean-to-flawed transition probability. Derived the sequential sigma/nu special case separately.
- Independent challenge identified action-selection conditioning: an action chosen using unrecorded private evidence may change the posterior. Added an explicit policy/context requirement and a planned counterexample.
- Wrote draft 0.1 of `CDSFL_revised_model_specification.md`, preserving the likelihood-pair form for zero-probability boundaries and explaining the limits of scalar compression.

## Resolved design questions and remaining empirical questions

- The compact core uses net removal s and clean-to-flawed introduction b. The original sigma/nu vocabulary survives as a clearly specified sequential special case.
- Relevant history, event definitions, provenance, selection, and target versions remain part of the state. The scalar does not replace them.
- Probability forecasts require calibrated, jointly conditioned inputs or explicit uncertainty. Unsupported estimates remain unestimated.
- A staged validation protocol begins with independently resolvable mathematical/numerical tasks and expands only after useful results.
- The requested separate challenge passes completed, including a final severe-testing challenge. One extra validation-document reread failed on a usage limit and adds no evidence.
- Future empirical questions remain: whether the quantities can be identified and calibrated in a useful task family, whether decisions improve at a reasonable cost, whether benefits transfer, and what scholarly contribution is distinct from prior work.

### After derivation — exact checks and adversarial findings

- Wrote the standard-library exact reference calculation, the separately enumerated outcome-tree suite, and a machine-readable report. The final run passed 5,600 conditional cases, rejected 650 impossible observations, checked 2,000 branch policies, 125 sequential-repair trees and 125 reductions/expectations, and rejected eight named incorrect alternatives. Counts concern constructed mathematical cases, not empirical samples.
- Improved the uncertain-parameter counterexample to use interior probabilities: joint averaging yields 0.16 while separately averaging the parameters yields 0.25. Correct conditional marginalisation restores 0.16.
- Read the independent derivation and validation recommendations; ran both separate exact-check scripts successfully. These use related assumptions and overlapping examples, so their agreement is not treated as statistical independence or additional calibration data.
- Accepted challenge findings on hidden action-selection information, insufficient scalar state, dependent parameters, unrestricted post-hoc fitting, and complementary experiments that defeat one-step stopping. These become explicit limits or requirements in the final proposal.
- Clarification of the preceding review: a confirmed flaw followed by an actually executed perfect repair has zero remaining scoped risk. If a further imperfect detector still gates whether repair is attempted, its ex-ante remaining risk is instead 1−q. The prior review's zero-risk boundary assumed the repair actually occurred; the final proposal states this action schedule explicitly. The old recurrence returning one is incorrect under either of those repair policies when q>0.
- Began assembling the final specification and a separate prospective validation plan. No real-world parameter calibration, benchmark reproduction, formal proof-assistant verification, or upstream implementation has occurred.

### 18:12–18:23 UTC — final documents before the next interruption

- Wrote the version 1.0 specification and the user-facing prospective validation plan. One attempted document-write call failed before execution because of quoting in the tool request; the corrected call succeeded. No partial document write resulted from that failed call.
- A final bounded challenge found no new core error, but corrected an imprecise sentence about independence: replacing conditional sensitivities by marginal ones needs justified factorisation; conditional independence is sufficient, not necessary. Added a clarification for transition entries on zero-weight branches and for environmental change during an interval.
- Checked the six original input hashes, current test-script hashes against the recorded results, eleven local document links, and mathematical delimiter balance. Those checks passed.
- A requested final reread of the completed validation document failed on a usage limit. It did not produce a completed review and is not counted as one. The earlier validation-design pass was completed and remains available.
- The user then reported another usage interruption. No claims of continuous work during the intervening period are made.

### 23:00 UTC — resumed after interruption (10 September in London)

- Read the saved checkpoint and the user's supplied Hossenfelder transcript. Preserved an exact local copy and added its hash and original path to the input manifest.
- Used the transcript's warning about assumptions that conceal the desired conclusion as the relevant review criterion. Its assertions about specific current mathematical proofs, models, and companies were not verified or adopted as evidence.
- Re-read the original P-Pass, Invitation to Falsify, and severe-testing/bold-conjecture passages. These explicitly distinguish corroboration from proof, allow replacement of an inferior equation, and reject unsupported formalism. The revision is intended to enforce these existing commitments.
- Added a bounded task to challenge a proposed connection between calibrated miss/false-alarm bounds and residual risk. This directly links the preserved coverage model to severe tests; completion will be recorded only after the result arrives.
- Next: add semantic dependency checks, the severe-testing derivation, a purpose/complexity rule for optional components, and complete the final package.

### 23:00–23:07 UTC — non-circularity and severe testing

- Preserved the version 1.0 specification and validation plan in work/revision-history/ before updating the deliverables to version 1.1, dated 10 September in London.
- Added a semantic dependency audit: a conclusion cannot establish its own premise even when renamed as a regularity, success, or calibration assumption. The update identity does not prove its empirical inputs or practical usefulness.
- Added a component-purpose table. Optional information, decision, multi-state, dependence, and convergence calculations have explicit jobs; they are not mandatory implementation layers.
- The additional challenge identified a non-exhaustive-outcome assumption: with abstention, one minus the false-alarm rate is not the clean-target pass rate. Accepted the counterexample and corrected the general severe-test bound to use directly defined pass probabilities beta and gamma.
- Linked the corrected bound back to original coverage for a completed binary protocol. Recorded limits involving jointly uncertain calibration bounds, selection context, and average versus subtype-uniform detection.
- Wrote and ran 450 exact bound cases and three deliberately misleading alternatives. All mathematical assertions passed. Fixed a result-file newline serialization error and reran this new script; its JSON report now parses and contains the matching source hash.
- The original core arithmetic and its test suite were unchanged; they were not rerun merely to increase the apparent amount of checking.
- Updated the self-audit to include the real abstention counterexample and its correction. No circular numerical confidence score or real-world calibration claim was introduced.

### 2026-09-09 23:09:47 UTC — completion of the proposal

- Completed the version 1.1 specification, empirical validation plan, mathematical dependency audit, severe-testing bound, and component-purpose review.
- Clarified the distinction between zero-probability discrete observations and zero total likelihood in a continuous-density representation. The reference exception wording now accurately describes both. Arithmetic was unchanged; the main suite was rerun after this source change, passed with unchanged counts, and regenerated its source-hashed report.
- The final bounded severe-testing review completed and is preserved in work/revision-challenge/severe_testing_review.md. Its requested correction is implemented.
- This completes the authorised mathematical proposal and documentation. Empirical calibration, external human review, STEM utility comparisons, and repository implementation remain future work; their absence is stated in the deliverables.
- Final packaging verifies the seven input files, both result reports and their source hashes, local document links, and mathematical delimiter balance. The final manifest records deliverable and supporting-file hashes so a later resumption can detect changes.

### 2026-09-09 23:23:15 UTC — lineage and decay clarification

- User asked whether the revision preserves the original model and its decay-curve heritage.
- Re-read the relevant original and revised passages and checked NIST's Duane model description.
- A bounded derivation pass confirmed exact recovery of the original recursion, geometric miss probability, coverage curve, and posterior-odds decay.
- Saved CDSFL_lineage_and_decay_clarification.md, distinguishing exact reductions, changes of reported quantity, retained empirical companion models, and replaced repair/novelty semantics.
- The core version 1.1 specification is unchanged. The clarification does not reproduce the reported Duane fits or certify every curve-based diagnostic.

### 2026-09-09 23:57:29 UTC — repeated examination and standalone contribution

- Accepted the founder's correction adding “repeated” to the human-comprehensible account, and incorporated the complete corrected wording in the specification and lineage note.
- Preserved the prior version 1.1 specification in work/revision-history/ before this explanatory edit. No equation or executable calculation changed.
- A bounded wording review confirmed the statement with explicit conditions: unchanged target, consistently defined failure, and remaining conditional ability to detect errors missed earlier. Returns “can” diminish; decay is not a universal certificate of exhaustion.
- Added an explicit standalone-status explanation. The mathematical/methodological account can be assessed without the CDSFL implementation; its empirical adequacy and distinct scholarly contribution remain open questions.
- Preserved the distinction between a better specified, more defensible research proposal and an empirically established result. Checked the inserted wording and document delimiters; no tests were rerun for this prose edit.
