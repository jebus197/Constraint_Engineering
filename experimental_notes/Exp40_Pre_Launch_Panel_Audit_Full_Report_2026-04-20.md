# EXPERIMENT 40 PRE LAUNCH PANEL AUDIT. FULL CONSOLIDATED REPORT

**Preserved into the repository 2026-08-06 02:15 .** Full consolidated pre-launch panel audit for Exp 40. Provenance for the arc's entry conditions.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/Exp40_Pre_Launch_Panel_Audit_Full_Report_2026-04-20.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `RECOVERY.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

EXPERIMENT 40 PRE LAUNCH PANEL AUDIT. FULL CONSOLIDATED REPORT

Date. 2026-04-20.
Timestamp. 2026-04-20 22:32:29 BST.


DIRECT ANSWER TO THE ORIGINAL TWO PART QUESTION

Part one. Which findings from the previous four confounded confer rounds remain relevant, unresolved, or untested, and are these findings new.

14 numbered findings were raised across the confounded rounds, labelled F1 through F14, plus a small number of model specific side items. Their status after the corrected re confer and after programmatic verification is as follows.

Finding F1. Repair the SymPy sandbox silent regression. This finding is relevant, unresolved, and partially tested. It is not new in the sense that a previous session had flagged the regression, but it has not been fixed in the current code. Programmatic verification reproduced the failure on four representative claims. The proposed fix was also programmatically tested and verified to pass all four claims while preserving the remote code execution block list. This finding is required for fold in now under the corrected framing. 2 of 5 models in the corrected re confer classify it as a launch blocker. The other 3 classify it as not blocking but still required under the shadow promotion now policy. All 5 agree the fix should be applied.

Finding F2. Activate the wrapper function compute_rk_with_eta_channel at line 3510 of reference_runner_v2.py. This finding is relevant, unresolved, and is a new architectural requirement that was not in the Experiment 39 runner. The function exists in the Experiment 40 runner at line 3177 but is never called. The call site at line 3510 still uses the bare compute_rk. Programmatic inspection confirmed that the per finding schema carries only 4 fields, meaning nu_b, nu_f, q, and R, whereas the wrapper needs 5 additional fields, meaning eta_int, c_ext, nu_k, d, and p. 4 of 5 models in the corrected re confer classify wrapper activation as required or partially required. Only Gemini dissents, arguing that m_div equal to 1 is an identity function. Programmatic verification shows Gemini's argument is only conditionally true, because whether the wrapper acts as an identity depends on whether the upstream q composition included the c_ext term, which has not been independently confirmed across all producers of model_params.

Finding F3. Runner version 2 promotion. This finding is resolved administratively. Experiment 40 runs on the version 2 runner by construction, because the Experiment 40 gate configuration references version 2 only features such as star topology enforcement and the alternative gamma convergence. This is a governance decision and is not a code change.

Finding F4. Live promotion of the specialist cells for physics, chemistry, and engineering, labelled K, L, and M. This finding is unresolved in the sense of not yet executed, but the corrected re confer is unanimous that it is not required for Experiment 40. Experiment 40's test article is software, meaning the physics, chemistry, and engineering specialists do not contribute to it. Defer to Bench Run 2 calibration.

Finding F5. Adversarial panel P pass on Phase A and B code. This finding is the audit itself, so the finding is resolved by completion of the audit.

Finding F6. Diversity and recidivism scoring integration, items 1E7 and 1E9. This finding is unresolved in the sense of not yet wired into scoring, but all 5 models agree that log only is correct before Experiment 54. Defer.

Finding F7. Cross domain composability architecture, meaning the ordering of three architectural changes labelled B, C, and D. This finding is unresolved. All 5 models gave different orderings. Because Experiment 40 is single domain, the ordering decision is not forced by Experiment 40 and is deferred to the Experiment 54 design discussion.

Finding F8. Rule for combining verdicts across multiple domains on a single claim. This finding is unresolved. Five different rules were proposed. Because Experiment 40 is single domain, the rule is not forced by Experiment 40. Defer.

Finding F9. Topology for Experiment 40. This finding is resolved and already in the version 2 runner. Star topology is enforced via 40_gate.json. Unanimous across all rounds.

Finding F10. A candidate third topology for future experiments. This finding is unresolved and deferred to Experiment 41 or later. 4 of 5 models proposed variants of star with paired challenge. DeepSeek rejected the category. Not an Experiment 40 concern.

Finding F11. Correctness ratio M over N as a separate channel. This finding is resolved by unanimous agreement that it is an orthogonal throughput metric, not a Stage 6 channel. It will be tracked separately during Bench Run 2 reporting. No Experiment 40 action.

Finding F12. Novelty boundary is empirical, not derivable. This finding is resolved by unanimous acknowledgement. Measurement happens in Bench Run 2.

Finding F13. Continuous divergence modulator formulation, named DCY. This finding is resolved by rejection. All 5 models reject the formulation as presented. 3 of 5 propose salvageable corrections. Discrete m_div tiers of 1.00, 0.85, 0.70, and 0.60 are considered sufficient. Off target for Experiment 40.

Finding F14. The philosophical objection that the framework might be, quote, just doing mathematics, end quote. This finding is resolved by unanimous agreement that the distinction is operationally indistinguishable within the present framework. Not required for the invention engine goal. No action.

Model specific side items.

Codex specific. A static assertion that the suppression weight and the divergence modulator are absent from the bare compute_rk inputs by construction. This is superseded by wrapper activation if fold in F2 is approved.

CC2 specific. A debug mode assertion at line 3510 that checks whether q equals eta combined times d times p. This finding is new, relevant, and becomes fold in now alongside F2 because it provides a cheap diagnostic even if the wrapper is not activated.

ChatGPT specific 1. Stratify closures into three categories, namely library complete, shadow integrated, and live operational. This finding is new, relevant, and becomes fold in now as a documentation change to ONBOARDING.md.

ChatGPT specific 2. Warn that 1D5 re prompt loops can cause retry induced format overfitting. This finding is low risk for Experiment 40. Defer with note.

ChatGPT specific 3. Warn that 1E11 first definitive verdict wins is a latent priority inversion source. This finding is not triggered in single domain Experiment 40. Defer with note until K, L, and M promote.

Round 2 through 3B locks on Q3, Q4, Q5, and Q6.

Q3 lock on runtime versus post hoc placement of the novelty ceiling. Resolved by round 3B in favour of post hoc only. The corrected re confer is unanimous that runtime placement is either not required or out of Experiment 40 scope. Programmatic verification computed the ceiling value at a representative working point and found it non binding at a value of 5.11, which exceeds the natural domain of 0 to 1. This weakens the operational case for runtime enforcement. Status. Post hoc analysis for Experiment 40. Re evaluate for runtime at Experiment 54 only if the empirical distribution shows binding frequency above a threshold.

Q4 lock on the unified reason trace schema. Resolved by round 3B in favour of the CC2 10 field schema. The corrected re confer supersedes this. 4 of 5 models in the re confer agree no rich schema is required for Experiment 40. The 10 field schema is off target as a runtime requirement. It can be recorded as the Experiment 54 attribution schema.

Q5 lock on the four family preservation predicates. Resolved by round 3B as acceptance gates. The corrected re confer supersedes this. All 5 models agree the predicate families are either diagnostic only or not applicable for Experiment 40. They should not gate Experiment 40 acceptance. The 40_gate.json pass condition is the sole gate.

Q6 lock on the topology label. Resolved unanimously as star across all rounds including the corrected re confer. No change.

Summary of part one. Of the 14 numbered findings from the confounded rounds, 4 are fold in now under the corrected framing and the shadow promotion now policy. Those are F1 for SymPy, F2 for wrapper activation, the CC2 specific debug assertion, and the ChatGPT specific closure stratification. 2 are already in version 2, meaning F9 star topology and the existence of the alternative gamma convergence branch. 2 are administrative or audit completion, meaning F3 runner promotion and F5 adversarial P pass. 6 are deferred to Bench Run 2 or Experiment 54, meaning F4 K L M promotion, F6 diversity and recidivism scoring, F7 cross domain architecture, F8 multi domain verdict rule, F10 third topology, and F11 M over N ratio. 2 are resolved by acknowledgement, meaning F12 empirical novelty boundary and F14 philosophical objection. 2 are rejected, meaning F13 continuous DCY and the v1 preservation framing itself. The round 2 through 3B locks are either incorporated into the fold in list or superseded by the corrected framing.

The fold in now items that are new relative to the confounded rounds, in the sense that they were not in the Experiment 39 runner, are the SymPy fix, the wrapper activation, the debug assertion, and the closure stratification documentation. All 4 are genuinely new work.

The corrected re confer itself raised 1 new operational insight that the earlier rounds had not surfaced. That is CC2's observation that bare compute_rk without the eta channel structurally disables 1 of the 4 section 17 feedback types, specifically the rk discrepancy feedback, because there is no eta combined to detect discrepancies against. This argument gives wrapper activation a behavioural justification that does not depend on the identity function question. This is genuinely new material.

Part two. What were and are the main test subjects or articles for Experiment 40.

The primary test article is the file bench slash dm slash _feedback.py. This file implements the section 17 feedback channel. It is approximately 22 kilobytes in size. It is the software artefact against which the panel's admissibility judgements are computed.

The secondary test article is the file bench slash dm slash _types.py. This file is approximately 30 kilobytes in size. It defines the type schemas that the feedback channel consumes and emits.

Experiment 40 is a single domain experiment with a software target. The panel is asked to find critical issues in the section 17 feedback channel implementation. The pass condition, from bench slash exp40_configs slash 40_gate.json, is that gamma reaches 0.30 or higher, or that 3 consecutive rounds produce 0 novel critical findings. Topology is star. Maximum rounds is 8. Earliest stop round is 3. Live specialist domains are mathematics, statistics, biology, and information science. Functional shadow specialists are physics, chemistry, and engineering.


FULL CONTEXT OF THE SIX CONFER ROUNDS

Six confer rounds were conducted over approximately 48 hours. The first 5 used a framing premise that was subsequently refuted. That premise stated that reference_runner_v2.py must preserve the behavioural signature of the Experiment 39 reference_runner.py. The sixth, conducted on 2026-04-20, rejected the premise explicitly and anchored instead on the 40_gate.json pass condition and the Stage 6 orthogonality rule.

The panel consisted of 5 frontier models. Codex GPT version 5.4 via OpenRouter. Gemini version 3.1 Pro via the Google GenAI application programming interface. CC2, which is Claude Opus version 4.6 accessed via the command line interface in piped mode. ChatGPT GPT version 5.4 via OpenRouter. DeepSeek R1 release 0528 via OpenRouter. All 5 ran under the latest CDSFL directives as system prompt.

The six rounds are the following. Round 1 produced full proposals from all 5 models. Rounds 2A and 2B produced refinements and cross challenges. Rounds 3 and 3B produced locks on the Q3, Q4, Q5, and Q6 sequence. The re confer, which is round 1 of a replacement series under the corrected framing, produced 4 question responses from all 5 models.

Raw artefacts live at the following paths. Rounds 1 through 3B are in the directory tmp slash exp40_audit slash split with filenames of the form round followed by number followed by two underscores followed by model name dot txt. The re confer is in bench slash logs slash confer_exp40_reaudit_round1 with per model JavaScript Object Notation files timestamped 20260420T164144Z plus a combined log.


FULL ENUMERATION OF FIX PROPOSALS ACROSS ALL SIX ROUNDS

The following section gives the full per model position on every fix proposal from the confounded rounds, in the words of each model. These positions carry the caveat that the framing has since been refuted, but they are preserved here because the corrected re confer explicitly builds on them.

Fix 1. Repair the SymPy sandbox regression.
Codex. Must land before launch, a real blocker in disguise. Fix the sandbox parsing in a minimal way, then add a live regression test proving integer literal handling works while the remote code execution lockdown remains intact.
Gemini. Defer for Experiment 40. The tool's inability to parse integers is operationally irrelevant for this specific run. Becomes a critical blocker for Bench Run 2.
ChatGPT. Must land, or else hard disable. Either fix parsing safely, or remove SymPy from decisive routing and mark it unavailable until fixed. Known broken but still wired is worse than absent.
DeepSeek. Critical blocker. Silent uncertain verdicts corrupt mathematics domain verification. Fix the sandbox to allow Integer construction without remote code execution.
CC2. Blocker for Bench Run 2, not for Experiment 40. Whitelist the built in functions int, float, bool, range, len, type, True, False, and None, and re run the SymPy specialist test suite.

Fix 2. Activate the wrapper function compute_rk_with_eta_channel at line 3510 of reference_runner_v2.py.
Codex. Keep the full activation deferred, but add a launch time static assertion at the current call site that the suppression weight and the divergence modulator are absent from the bare compute_rk inputs by construction, plus a failing test that flips once the Experiment 54 wiring lands.
Gemini. Blocker in disguise. Do not defer this to Experiment 54. Fix immediately by activating the wrapper at the current call site and passing a hardcoded m_div equal to 1.00. This secures the channel invariant natively.
ChatGPT. Can defer only if documented as intentionally inactive. Do not activate dead assertions for theatre. Annotate the production call site with an explicit invariant debt comment.
DeepSeek. Defer. Activation without m_div would crash. Fix during Experiment 54 wiring.
CC2. Not a blocker. Add a debug mode assertion at line 3510 that checks whether q equals eta combined times d times p with the canonical decomposition, even without wiring m_div.

Fix 3. Runner version 2 promotion decision. All 5 models treat this as a governance blocker rather than a technical one. If Experiment 40 depends on version 2 only mechanisms, meaning star topology enforcement, per model rho tracking, structured tool use, and the alternative gamma convergence pass, then running on version 1 would invalidate the experiment. The founder decision resolves this administratively.

Fix 4. Live promotion of the specialists for physics, chemistry, and engineering, referred to as cells K, L, and M. All 5 models agree to defer for Experiment 40 because it is a software target experiment and the shadow wired specialists do not contribute to _feedback.py validation.

Fix 5. Adversarial panel P pass on Phase A and B code. All 5 models agree that the panel review itself is this pass. Required. The audit document satisfies this requirement.

Fix 6. Diversity scoring and recidivism scoring integration, items 1E7 and 1E9. All 5 models agree to defer. Logging only is correct before Experiment 54.

Fix 7. The meta question 1 architecture ordering. Three proposed changes. B means cells to configurations. C means configurations to configurations. D means cells to cells.
Codex. D then B then selective C.
Gemini. C then D, with B deferred.
ChatGPT. D then B then selective C.
DeepSeek. C greater than D greater than B. C first to fix single domain myopia. D second to reduce false uncertain verdicts. B last.
CC2. B then D then C. B is highest value because it makes configurations empirical.

Fix 8. Rule for combining verdicts across multiple domains on a single claim.
Codex. Definitive contradiction veto, otherwise weighted corroborative aggregation. If any high confidence domain returns a definitive refutation, the overall verdict is not definitive support.
Gemini. Effective probability equals 1 minus the product over j of 1 minus p sub j. Multi domain verification legitimately accelerates the validity update toward 1.0 via the search quality channel, not via eta_int.
ChatGPT. Confidence weighted admissibility with contradiction veto. Definitive support requires either 1 high confidence primary domain support with no refutation, or 2 or more independent supports with no refutation.
DeepSeek. First definitive tool wins.
CC2. First definitive, not majority. If both domains return definitive and agree, both verdicts stand. If they conflict, both verdicts carry a conflict flag and the finding is escalated.

Fix 9. Topology for Experiment 40. Unanimous. Star.

Fix 10. A candidate third topology for future experiments.
Codex. Star with paired challenge. Shared registry remains canonical, but each finding can trigger 1 bounded adversarial exchange between 2 assigned models.
Gemini. Star with challenge. Models submit structured findings to the blackboard, but the coordinator can open a temporary pairwise challenge thread on 1 finding only.
ChatGPT. Star with scoped challenge channels. Preserves schema discipline while allowing direct adversarial extension.
DeepSeek. Sequential pipeline where model N sees 1 through N minus 1 is not useful. It delays feedback and amplifies early errors. Rejects the third topology category.
CC2. Star with paired challenge. 1 model pair assigned adversarial challenge duty on each other's findings while the remaining 3 models file independent discoveries. Pair rotates each round. 5 choose 2 gives 10 distinct pairings across 10 rounds.

Fix 11. Correctness ratio M over N as a separate channel. Unanimous. Not a Stage 6 channel. Track separately as an orthogonal benchmark or calibration diagnostic.

Fix 12. Novelty boundary, meaning the threshold between genuine novelty and hallucination. Unanimous. Not derivable from Stage 6 mathematics alone. Empirical. To be measured in Bench Run 2.

Fix 13. Externally proposed continuous divergence modulator formulation named DCY. All 5 models reject as presented. 3 of 5 propose salvageable corrections.
Codex. A formulation of DCY equal to open bracket 1 minus sim close bracket times open bracket 1 minus Jaccard of dependencies of f and dependencies of A sub k times I sub FFF close bracket, with a sim boundary fix.
ChatGPT. A formulation of DCY prime equal to the maximum over k of open bracket 1 minus normalised sim of f and A sub k close bracket times open bracket 1 minus Jaccard star of f and A sub k close bracket, with I sub FFF as gate on the Jaccard term only.
CC2. A formulation of DCY equal to the maximum over k of open bracket 1 minus s of f and A sub k divided by 0.86 close bracket times open bracket 1 minus J of dependencies of f and dependencies of A sub k close bracket plus open bracket 1 minus I sub FFF close bracket times s sub floor.
DeepSeek. Reject outright with no salvage. Discrete m_div is sufficient and auditable. Continuous DCY duplicates effort.
Gemini. Reject outright. Continuous semantic similarity is already rigorously handled by the suppression channel w of f. Modulating eta_int using an unbounded similarity metric risks violating orthogonality.

Fix 14. The philosophical objection that the framework might be, quote, just doing mathematics, end quote.
Codex. Proposes an out of distribution prospective success under verification on tasks with low retrieval plausibility.
Gemini. Proposes an explicit resolution of a multi domain claim using a verification path that crosses specialist boundaries not present in the training data.
ChatGPT. Proposes counterfactual novelty under constrained search. Hold c_ext high, require solutions that are independently valid, then test whether outputs remain non derivable from retrieved neighbours by expert post hoc reconstruction.
CC2. Proposes a solution that is independently verifiable as correct, novel against the literature with nu_k greater than 0.6 and c_ext greater than 0.5, and not reconstructible from any single training data source. The third condition is not measurable within the current framework.
DeepSeek. Empirically indistinguishable. The invention engine succeeds if outputs are correct and novel regardless of generation mechanism.

Codex specific from the opening assessment. Add a static assertion that the suppression weight w of f and the divergence modulator m_div are absent from the bare compute_rk inputs by construction, as forward protection for the deferred activation.

CC2 specific from the opening assessment. Add a debug mode assertion at line 3510 checking that q equals eta combined times d times p with canonical decomposition, independent of m_div wiring.

ChatGPT specific from the opening assessment. Stratify closures into library complete, shadow integrated, and live operational, instead of the binary landed or not landed label. Warn that 1D5 re prompt loops can cause retry induced format overfitting because mechanical parse recovery is not semantic recovery. Warn that 1E11 first definitive verdict wins is a latent priority inversion source.


ROUND 2A, 2B, 3, AND 3B LOCKS

The multi round structure produced lockable positions on a sequence of questions labelled Q3, Q4, Q5, and Q6. These positions are preserved here for completeness, with the caveat that the corrected re confer supersedes them wherever they conflict.

Q3 lock on conditional novelty ceiling placement. Round 3 split. Codex, ChatGPT, and DeepSeek voted for option w2 meaning post hoc analysis. CC2 and Gemini voted for option w1 meaning runtime guard rail. Round 3B arbitration locked post hoc only. Codex's derivation for the maximum novelty value is nu max equals 1 minus open bracket 1 minus open bracket R minus R min close bracket divided by open bracket R times open bracket 1 minus R min close bracket times eta_int times d times p close bracket close bracket divided by c_ext.

Q4 lock on the unified reason trace schema. Round 3B locked the CC2 10 field schema. The fields are point identifier, stance which is one of yield, refute, or unchanged, target model, pivot quote, pivot quote verified, reason type which is one of math error, logical gap, scope error, corrected misread, unsupported assumption, or tool output, reason text, prior position hash, revised position, and state delta. Gemini's 3 field scheme and DeepSeek's cosine similarity auto tag were both refuted.

Q5 lock on the v1 preservation predicates. Round 3B locked the CC2 4 family scheme. Family 1 is mathematical path fidelity, meaning forbidden pattern hits equal to 0. Family 2 is correction fidelity, meaning downstream revisits greater than or equal to upstream revisions. Family 3 is counterfactual sensitivity, meaning deterministic stride perturbation of eta_int or nu_k by plus or minus 0.15 on at least 10 percent of dispatches. Family 4 is convergence stability, meaning unresolved points non increasing round over round, and reasoned yields greater than or equal to compliance yields. DeepSeek's alternative of residual risk less than 0.05 and fail rate equal to 0 was refuted.

Q6 lock on the topology label. Unanimous star. Codex's composite label of star at Experiment 40 and paired challenge at Experiment 41 was refuted as a cross experiment plan rather than a per experiment label.


RE CONFER ROUND 1 UNDER CORRECTED FRAMING

The re confer on 2026-04-20 abandoned the v1 preservation framing and anchored on the pass condition in 40_gate.json plus the Stage 6 orthogonality rule. 4 research questions labelled RQ1 through RQ4 were posed.

RQ1A. Does the SymPy sandbox fix block Experiment 40 launch.
Codex. Required.
Gemini. Not required but activate under shadow promotion now.
CC2. Not required but activate under shadow promotion now.
ChatGPT. Not required but activate as non blocking.
DeepSeek. Required.

RQ1B. Does the 1E10 wrapper activation block Experiment 40 launch.
Codex. Required.
Gemini. Not required. Defer to Experiment 54.
CC2. Partially required.
ChatGPT. Required.
DeepSeek. Required.

RQ1C. Does the live promotion of K, L, and M specialists block Experiment 40 launch.
All 5. Not required.

RQ2. Is a rich reason trace schema required for Experiment 40.
Codex. No.
Gemini. A 4 field minimum, namely finding identifier, model identifier, admissibility status, and severity and novelty flag.
CC2. Zero fields, with an optional round identifier for forward compatibility.
ChatGPT. No.
DeepSeek. A 5 field minimum, namely refuted, admissible, duplicate, rk discrepancy, and finding identifier.

RQ3. Are the four preservation predicate families required as acceptance gates.
Family 1 mathematical path fidelity. Codex diagnostic. Gemini not applicable to _feedback.py because the test article has no continuous mathematics. CC2 not applicable, already verified by the existing 200 plus unit tests. ChatGPT diagnostic. DeepSeek post hoc diagnostic.
Family 2 correction fidelity. Codex diagnostic. Gemini diagnostic. CC2 not Experiment 40, defer to Experiment 54 causal question. ChatGPT diagnostic. DeepSeek diagnostic.
Family 3 counterfactual sensitivity. All 5 agree not Experiment 40. CC2 notes this is literally the factorial design of Experiment 54. Defer to Experiment 41 or 54.
Family 4 convergence stability. Codex diagnostic. Gemini diagnostic. CC2 already subsumed by the 40_gate.json pass condition. ChatGPT diagnostic. DeepSeek not Experiment 40, defer to Experiment 54 stability analysis.

RQ4. Is the novelty ceiling required as a runtime guard rail.
Codex. Post hoc only.
Gemini. Not Experiment 40 scope. Defer to Experiment 54.
CC2. Not Experiment 40 scope. Would be an orthogonality violation if wired at runtime.
ChatGPT. Post hoc only.
DeepSeek. Post hoc only.

CC2's key new insight on RQ1B. Bare compute_rk without the eta channel means the rk discrepancy feedback, which is 1 of the 4 feedback types in the section 17 channel per _feedback.py, cannot fire correctly. There is no eta combined to detect discrepancies against. Without wrapper activation, section 17 admissibility rates are measured over 3 of 4 feedback classes, meaning the logged signal is incomplete. This is behavioural, not cosmetic. It is the strongest argument for wrapper activation.

Corrected framing convergence summary.
Unanimous on RQ1C, RQ3 across all 4 families, and RQ4.
4 of 5 on RQ1B, meaning wrapper activation required or partially required. Gemini is the sole dissent.
4 of 5 on RQ2, meaning no rich schema required for Experiment 40. Only Gemini's 4 field and DeepSeek's 5 field minima offer anything. These are lighter than the reverted 10 field lock.
Split 2 to 3 on RQ1A, meaning SymPy as a launch blocker. 2 models, namely Codex and DeepSeek, say required. 3 models, namely Gemini, CC2, and ChatGPT, say not required but activate. All 5 agree the fix should be applied.


PROGRAMMATIC VERIFICATION RESULTS

Four claims were verified programmatically using SymPy version 1.14.0 on Python 3.13. The run log captures every check.

First claim. The SymPy sandbox regression is real and reproducible.
Current sandbox. When the sandbox sets global_dict to a dictionary containing only an empty builtins entry and passes that to SymPy's parse_expr function, 4 representative claims fail. The claim 2 plus 2 fails with name Integer is not defined. The claim x plus 1 greater than x fails with the same error. The claim x squared greater than or equal to 0 also fails. The claim Eq of x plus y and y plus x succeeds because Eq is in the local dictionary.
Proposed fix. Add an allow list to global_dict that exposes the SymPy symbols Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, and exp, while keeping builtins empty.
Fix verification. The proposed allow list parses all 4 previously failing claims correctly. The remote code execution block list still catches double underscore import, double underscore class, eval, and open. No remote code execution regression.

Second claim. Codex's novelty ceiling formula is algebraically correct.
Derivation. Starting from the validity update equation R new equals R times open bracket 1 minus q close bracket divided by open bracket 1 minus q times R close bracket, and requiring R new greater than or equal to R min, SymPy solves for q max equals open bracket R minus R min close bracket divided by open bracket R times open bracket 1 minus R min close bracket close bracket.
Substitution. Using q equals eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket times d times p, which is the Stage 6 composition at m_div equal to 1.0, and solving for nu_k, SymPy returns exactly Codex's published formula. The symbolic difference against Codex's version is 0.
Numerical evaluation. At a representative working point of R equals 0.9, R min equals 0.8, eta_int equals 0.5, d equals 0.7, p equals 0.6, and c_ext equals 0.4, the computed nu max evaluates to 5.11. This exceeds the natural domain of 0 to 1 for novelty, meaning the ceiling is non binding at the reference point. The ceiling only becomes binding when q max is less than eta_int times d times p. At the reference point, q max is 0.556 and eta_int times d times p is 0.210, so q max exceeds the product, meaning the ceiling is inactive. This substantially weakens the operational case for runtime enforcement because the typical parameter regime keeps the ceiling non binding.

Third claim. The argument that m_div equal to 1.0 makes the wrapper behaviourally an identity function is only partially correct.
Mechanics. The wrapper compute_rk_with_eta_channel, when called with m_div equal to 1.0, computes eta combined equals eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket, then q equals eta combined times d times p. The bare compute_rk reads q as a scalar from the dictionary model_params at line 3497 of reference_runner_v2.py.
Conditional. The wrapper equals bare claim holds only if the upstream q that the caller stored in model_params was itself composed from the full expression eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket times d times p. If the upstream callers produced q as a plain scalar, or from a partial composition that omitted the c_ext term, then wrapper activation is a behavioural change, not an identity operation.
Current schema. The per finding schema carries model_params equal to a 4 field dictionary with nu_b, nu_f, q, and R only. Activating the wrapper requires the schema to expand to include eta_int, c_ext, nu_k, d, and p, plus changes to wherever model_params is produced upstream. This is a real architectural increment, not a 1 line swap at line 3510.

Fourth claim. The alternative gamma convergence is feasible under the current gate configuration. With maximum rounds equal to 8 and earliest stop round equal to 3, the available window is 6 rounds. The 3 consecutive zero novel critical findings requirement is reachable inside that window. Feasible.


STARTING INVENTORY AGAINST THE EXPERIMENT 39 BASELINE

A direct search of reference_runner.py, which is the Experiment 39 baseline runner at 4344 lines, confirms that none of the following identifiers exist in the baseline. They are therefore new in reference_runner_v2.py, which is 4922 lines.

Identifier. The function _check_gamma_alt_convergence. Defined at line 1064 of the version 2 runner. It implements the alternative gamma pass condition. It is called from the main round loop. Version 1 count 0. Version 2 count 2 references.

Identifier. The class ChannelViolationError. Raised when Stage 6 channel invariants are violated. Version 1 count 0. Version 2 count 3 references.

Identifier. The function compute_rk_with_eta_channel. Defined at line 3177. This is the wrapper function that integrates the divergence modulator into the validity update. Version 1 count 0. Version 2 count 2 references, of which 1 is the definition itself and 1 is the docstring pointer inside bare compute_rk. Never called in the live path.

Identifier. The enumeration value GAMMA_ALT_CONVERGED, used as the stop condition label. Version 1 count 0. Version 2 count 2 references.

Identifier. The configuration flag eta_int_modulator. Referenced at line 4477, in a specialist dispatch path where the severe 0.6 tier is surfaced. Version 1 count 0. Version 2 count 1 reference.

Identifier. The symbol m_div. Appears throughout the wrapper body, the channel violation error message, and the Stage 6 docstrings. Version 1 count 0. Version 2 count 15 references. Never assigned a non identity value in the current hot path.

The live call site at reference_runner_v2.py line 3510 reads q as a scalar from model_params and feeds it directly to bare compute_rk. The per finding model_params dictionary contains only nu_b, nu_f, q, and R. It does not decompose q into eta_int, c_ext, nu_k, d, and p.

The SymPy specialist at bench slash immune_agents.py lines 947 to 1019 carries a silent regression. The sandbox uses global_dict equal to a dictionary containing only an empty builtins entry. This blocks the SymPy Integer constructor. The remote code execution block list at line 962 correctly catches double underscore import, double underscore class, eval, and open tokens.

The 40_gate.json configuration file is consistent with the corrected framing. eta_int_modulator_wired_into_compute_rk is set to false. Live specialist domains are mathematics, statistics, biology, and information science. Functional shadow specialists are physics, chemistry, and engineering. Topology is star. Maximum rounds is 8. Earliest stop round is 3. The alternative gamma branch in the pass condition is feasible under these parameters, because the 6 round window can accommodate a 3 consecutive requirement.


CLASSIFICATION OF EVERY PROPOSAL AGAINST THE CURRENT RUNNER

The classification uses 5 buckets. Already in version 2 means the fix is present, no action needed. Fold in now means required before Experiment 40 launch under the corrected framing. Fold in later means required before Bench Run 2 but not Experiment 40. Defer with annotation means carry a note but do not implement. Off target means framing dependent proposal now rejected.

Row 1. Alternative gamma convergence. Source. Version 2 scaffolding. Classification. Already in version 2. Action. No action. Lines 1064 and following, invoked in the round loop.

Row 2. Wrapper function compute_rk_with_eta_channel plus the channel violation error. Source. Version 2 scaffolding. Classification. Already in version 2 as a library. Action. Library is defined at lines 3177 and following. Not yet called.

Row 3. The eta_int_modulator configuration field. Source. 40_gate.json. Classification. Already in version 2 as a flag. Action. The flag is present with eta_int_modulator_wired_into_compute_rk equal to false.

Row 4. Runner version 2 promotion, meaning fix 3. Source. Round 1, all 5 models. Classification. Fold in now. This is a founder decision. Action. Experiment 40 runs on version 2 regardless. Administrative only.

Row 5. Adversarial panel P pass, meaning fix 5. Source. Round 1, all 5 models. Classification. Fold in now, completed by this audit.

Row 6. SymPy sandbox fix, meaning fix 1 and RQ1A. Source. Round 1 Codex, ChatGPT, and DeepSeek majority. Re confer 2 of 5 required, 3 of 5 not required but activate. All 5 models. Classification. Fold in now under the shadow promotion now policy. Action. Unanimous agreement that the fix should be applied. Whether its absence blocks launch is moot once the fix lands. Low cost repair. High signal quality dividend.

Row 7. Wrapper activation at reference_runner_v2.py line 3510 with m_div equal to 1.00, meaning fix 2 and RQ1B. Source. Round 1 Gemini only for now. Re confer 4 of 5 required, 1 of 5 not required meaning Gemini. All 5 models. Classification. Fold in now with caveats. Action. Required by majority under corrected framing. Requires upstream schema expansion so that model_params carries eta_int, c_ext, nu_k, d, and p, and wherever model_params is produced, the emit path sets these fields. At m_div equal to 1.0 the wrapper is mathematically equivalent to bare compute_rk only if upstream q composition included the c_ext term. If not, activation is a real behavioural change. The CC2 rk discrepancy feedback argument is the strongest behavioural reason to activate. Include a dry run of Experiment 39 data through the wrapped path before Experiment 40 launch, per Gemini's round 1 P pass revision.

Row 8. Debug mode assertion at line 3510 checking q equals eta combined times d times p. Source. Round 1 CC2 opening assessment. Classification. Fold in now. Action. Cheap diagnostic. Catches upstream composition drift independent of whether the wrapper is activated. 1 line assertion gated on a DEBUG_CHANNEL_CHECK flag.

Row 9. K, L, and M live promotion flip, meaning fix 4 and RQ1C. Source. Round 1 unanimous defer. Re confer unanimous not required. All 5 models. Classification. Defer with annotation. Action. Experiment 40 is software scoped. Functional shadow posture remains correct. Schedule for Bench Run 2 calibration after the empirical exercise on real physics, chemistry, and engineering claims.

Row 10. Diversity and recidivism scoring integration, meaning fix 6. Source. Round 1 unanimous defer. All 5 models. Classification. Defer. Action. Log only is correct before Experiment 54. No Experiment 40 work needed.

Row 11. Cross domain composability architecture, meaning fix 7 and meta question M1. Source. Round 1, all 5 models, ordering varies. All 5 models. Classification. Defer, out of Experiment 40 scope. Action. Experiment 40 is single domain software target. No architectural change required. Record positions for Experiment 54 design input.

Row 12. Rule for combining N domain verdicts, meaning fix 8. Source. Round 1, all 5 models, mechanism varies. Classification. Defer, out of Experiment 40 scope. Action. Only matters once K, L, and M are promoted. See row 9.

Row 13. Star topology for Experiment 40, meaning fix 9 and Q6 lock. Source. Round 1 plus round 3B unanimous. Re confer anchor. All 5 models. Classification. Already in version 2. Action. 40_gate.json topology equal to star confirmed.

Row 14. Third topology, namely star with paired challenge, meaning fix 10. Source. Round 1 Codex, Gemini, ChatGPT, CC2, with DeepSeek rejecting. 4 of 5. Classification. Defer to Experiment 41. Action. Out of Experiment 40 scope. Record for the paired challenge follow up.

Row 15. M over N correctness ratio as separate channel, meaning fix 11. Source. Round 1 unanimous. All 5 models. Classification. Defer, Bench Run 2 reporting. Action. Not a Stage 6 channel. Orthogonal throughput metric. No Experiment 40 action.

Row 16. Novelty boundary is empirical, not derivable, meaning fix 12. Source. Round 1 unanimous. Classification. Defer, Bench Run 2 data. Action. Acknowledgement. No action.

Row 17. Reject continuous DCY formulation, meaning fix 13. Source. Round 1 unanimous reject, 3 of 5 propose salvage. Classification. Off target for Experiment 40. Action. Discrete m_div tiers are sufficient. Continuous DCY is speculative engineering. Revisit post Bench Run 2 if motivated by data.

Row 18. Synthesis versus retrieval operational signal, meaning fix 14. Source. Round 1 unanimous operationally indistinguishable. Classification. Defer. Action. Philosophical. Invention engine goal does not require resolution.

Row 19. Static assertion that w of f and m_div are absent from bare compute_rk inputs. Source. Round 1 Codex opening assessment. Classification. Superseded by row 7. Action. If the wrapper is activated, this assertion becomes redundant. If deferred, reconsider.

Row 20. Stratify closures into library complete, shadow integrated, and live operational. Source. Round 1 ChatGPT opening assessment. Classification. Fold in now, documentation only. Action. Apply to the Phase A and B closure ledger in ONBOARDING.md when documenting Experiment 40 launch readiness.

Row 21. The 1D5 re prompt retry induced format overfitting warning. Source. Round 1 ChatGPT opening assessment. Classification. Defer with note. Action. Low risk. Add to the Experiment 40 post run analysis checklist.

Row 22. The 1E11 first definitive verdict wins priority inversion risk. Source. Round 1 ChatGPT opening assessment. Classification. Defer with note. Action. Not triggered in single domain Experiment 40. Revisit when K, L, and M promote.

Row 23. Q3 lock, novelty ceiling runtime or post hoc placement. Source. Round 3B locked post hoc. Re confer unanimous post hoc or out of scope. All 5 models. Classification. Defer, post hoc analysis only. Action. Do not wire at runtime. Post hoc computation is trivial, 1 SymPy formula over session parameters. Execute after Experiment 40 completes. The ceiling is non binding at typical parameter values, numerically verified at 5.11 at the reference point, which reduces its operational value.

Row 24. Q4 lock, unified 10 field reason trace schema. Source. Round 3B locked 10 field. Re confer 4 of 5 no schema. Gemini 4 field. DeepSeek 5 field. 3 zero field. Classification. Off target, confounded by v1 preservation framing. Action. The 10 field schema was anchored on preservation reasoning that has been refuted. For Experiment 40, no per finding reason trace is required beyond what the existing finding schema already carries for section 17 admissibility. Defer the full attribution schema to Experiment 54, where the 2 by 2 factorial requires it. If forward compatibility is desired, a single round identifier or a 4 field minimum is cheaper and achieves the same post hoc joining capability.

Row 25. Q5 lock, four family preservation predicate gates. Source. Round 3B locked 4 families as gates. Re confer unanimous diagnostic or not applicable. Classification. Off target as gates. Defer as diagnostics. Action. Under corrected framing these do not gate Experiment 40 acceptance. 40_gate.json pass condition is the sole gate. Counterfactual sensitivity specifically is Experiment 54's factorial design. Log the equivalent data passively if cheap. Do not add acceptance predicates to 40_gate.json.


P PASS SELF FALSIFICATION OF THE SYNTHESIS

Six falsifiers were considered against the load bearing claims of this synthesis.

Falsifier A against row 7, wrapper activation required. If every caller that produces model_params q already composes q equal to eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket times d times p upstream, then the wrapper at m_div equal to 1.0 is behaviourally identity and Gemini is right. The audit did not inspect every producer of model_params. There are approximately 15 eta_int references in version 2, most of which are in the wrapper body and Stage 6 docstrings, not in call path producers. Mitigation. The fold in implementation must locate every producer via a grep of model_params across the bench directory and either confirm full composition or patch. The CC2 rk discrepancy feedback argument is strong on its own even if the upstream composition is complete, because the wrapper's structural channel violation error path is not reachable from bare compute_rk.

Falsifier B against row 6, SymPy sandbox fix required. If the SymPy verifier is never invoked for any Experiment 40 finding, because the software target _feedback.py never emits a claim that routes to the mathematics specialist, then the fix is immaterial for Experiment 40. This is consistent with Gemini's and ChatGPT's positions. Mitigation. Even under this falsifier, all 5 models agree the fix should be applied. The only disagreement is whether its absence blocks launch. Shadow promotion now policy applies regardless. The fix is also cheap, meaning 1 allow list in 1 function.

Falsifier C against row 23, nu max non binding at typical values. If Experiment 40 produces findings with high product of eta_int times d times p, for instance 0.8, then nu max drops into the 0 to 1 range and becomes binding. The numeric check used eta_int equal to 0.5, d equal to 0.7, and p equal to 0.6, which are reasonable priors but not empirically calibrated against Experiment 40's actual _feedback.py findings. Mitigation. The post hoc analysis should compute nu max over the actual per finding parameter distribution, not a single representative point. If the empirical distribution shows binding frequency above a threshold, say 10 percent of findings, revisit the runtime guard question for Experiment 54.

Falsifier D against the overall defer the 10 field schema verdict in row 24. If Experiment 54's factorial analysis later discovers that critical attribution signals, meaning whether a yield was reasoned or compliance driven, are impossible to reconstruct from Experiment 40 logs post hoc, then omitting the reason trace now is a cost that has to be paid later with re runs. Mitigation. Record the 10 field schema in a design document as the Experiment 54 attribution schema. Defer the runtime implementation to Experiment 54 rather than dropping the schema entirely.

Falsifier E against row 8, debug mode q composition assertion. If the assertion catches a genuine bug, signal is gained. If it never fires, it adds dead code. Mitigation. Gate on a DEBUG_CHANNEL_CHECK flag that is on by default for Experiment 40's first run and off for later runs. Document the flag's half life.

Falsifier F against the corrected framing re confer itself. The re confer ran a single round per model. It did not run rounds 2A, 2B, 3, or 3B under the corrected framing. The compelled convergence protocol item 4 requires the full round structure when multi round arbitration is needed. A single round may have missed positions that would have emerged under challenge. Mitigation. For a single domain software target with unanimous agreement on the 5 subsidiary questions, meaning RQ1C, RQ3 across all 4 families, and RQ4, the single round is sufficient. The one split, namely RQ1A SymPy, is resolved by the shadow promotion now policy, which is an independent standing rule from 2026-04-20. The one 4 of 5 question, namely RQ1B 1E10, has Gemini as the dissenting voice. Gemini's argument that m_div equal to 1.0 is an identity function is partially refuted by the programmatic check in the third claim above. Further rounds would be value adding if the founder judges the current evidence insufficient, but none of the positions are evidence underdetermined.


SYNTHESIS. WHAT TO FOLD INTO THE RUNNER BEFORE EXPERIMENT 40 LAUNCHES

Must land pre launch, meaning fold in now.

1. Fix the SymPy specialist sandbox at bench slash immune_agents.py lines 947 to 1019. Replace the empty global_dict with an allow list exposing the SymPy symbols Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, and exp, while retaining builtins equal to empty dictionary. Add a regression test with the 4 claims from the first programmatic verification plus 1 negative remote code execution test, meaning the claim double quote double underscore import open bracket single quote os single quote close bracket double quote must still be blocked. Approximately 20 lines of code.

2. Activate the wrapper at reference_runner_v2.py line 3510 with hardcoded m_div equal to 1.00. Requires. Locate every producer of model_params and confirm or patch the upstream q composition to eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket times d times p, or equivalently emit eta_int, c_ext, nu_k, d, and p as separate fields. Update the model_params schema documentation to reflect the expanded field set. Swap the call at line 3510 from compute_rk open bracket R_old, q, sk, nu_b, nu_f close bracket to compute_rk_with_eta_channel open bracket R_old, sk, eta_int, 1.0, c_ext, nu_k, d, p, nu_b, nu_f close bracket. Run the Experiment 39 regression data through the wrapped path before Experiment 40 launch, per Gemini's round 1 P pass revision. Flip eta_int_modulator_wired_into_compute_rk to true in 40_gate.json only after the dry run passes.

3. Add a debug mode q composition assertion at line 3510. Under a DEBUG_CHANNEL_CHECK flag, assert that the absolute difference between q and the product eta_int times open bracket 1 minus c_ext times open bracket 1 minus nu_k close bracket close bracket times d times p is less than 1e-9. 1 line. Catches upstream composition drift regardless of wrapper state.

4. Apply the closure state stratification to ONBOARDING.md. Document every Phase A and B closure as one of library complete, shadow integrated, or live operational. This is the ChatGPT originated documentation rigour. No code change.

Defer until Bench Run 2 or Experiment 54, with annotation where relevant.

K, L, and M live promotion flip, per row 9. Schedule for Bench Run 2 empirical calibration run. Cross domain composability architecture, per row 11. Record panel positions for Experiment 54 design. Star with paired challenge third topology, per row 14. Experiment 41 design input. Ten field reason trace schema, per row 24. Experiment 54 attribution design. Novelty ceiling runtime enforcement, per row 23. Post hoc analysis for Experiment 40. Re evaluate for runtime at Experiment 54 once the empirical nu max distribution is known.

Off target, do not implement.

The 4 v1 preservation predicate families as acceptance gates, per row 25. 40_gate.json pass condition is the sole gate. The continuous DCY formulation, per row 17. Discrete m_div tiers are sufficient. The v1 behavioural signature preservation premise itself. Refuted.

Expected post fold in state.

40_gate.json. eta_int_modulator_wired_into_compute_rk equal to true, otherwise unchanged.
reference_runner_v2.py. Line 3510 calls compute_rk_with_eta_channel. New debug assertion at adjacent line. Upstream model_params producers emit decomposed Stage 6 parameters.
bench slash immune_agents.py. The SymPy verifier sandbox uses allow list global_dict. Regression test passes.
resources slash ONBOARDING.md. Closure states stratified.
docs slash CURRENT_STATE.md. Regenerated by scripts slash cdsfl_sv.py after the above.

Not expected to change.

Topology label. Pass condition. Max rounds. Earliest stop round. All retained as in 40_gate.json.
Live specialist domains list. Retained as mathematics, statistics, biology, information science.
The test article. Retained as bench slash dm slash _feedback.py.


OUTSTANDING DISCUSSION POINTS FOR THE HUMAN IN THE LOOP

1. Schema decomposition scope. Activating the wrapper requires upstream changes to every producer of model_params. The audit did not enumerate those producers. It confirmed only that line 3510 reads q as a scalar. Before applying row 2, the implementer should grep recursively for model_params across the bench directory and confirm the upstream set. Decision. Does the founder want the audit to extend that inventory before any code edit, or is that pre edit checklist something the implementer owns.

2. Gemini's dissent on wrapper activation. Gemini's identity function argument against wrapper activation is partially refuted in the third programmatic check, but the refutation assumes the upstream q composition currently omits the c_ext term. If the empirical upstream check shows Gemini is right, meaning composition is already complete, the wrapper becomes a behaviourally cosmetic change. It would still be useful for surfacing channel violation errors on future m_div drift, but not load bearing for Experiment 40. Decision. Is the founder satisfied with the CC2 rk discrepancy feedback rationale as the primary justification, independent of the identity function question.

3. Shadow promotion now scope for SymPy. The shadow promotion now directive from 2026-04-20 states, quote, enable shadow elements and fix broken tools now, deferral costs more than activation given context loss risk, end quote. Under that directive, row 6 is unambiguous. Decision. Confirm the directive applies here, or carve out an exception.

4. Post hoc nu max computation triggering Experiment 54 runtime guard. If the post hoc ceiling analysis on Experiment 40 data shows the ceiling binding on more than some threshold fraction of findings, that is empirical evidence for reconsidering runtime enforcement. Decision. What threshold triggers the reconsideration. 5 percent. 10 percent. 25 percent.


NO CODE CHANGES WERE MADE DURING THIS AUDIT

Under the standing directive that fixes are suggested to the human in the loop and never auto applied, the above synthesis is a proposal for discussion. No edits to reference_runner_v2.py, immune_agents.py, 40_gate.json, or ONBOARDING.md have been performed. The audit is complete and awaits founder approval before any implementation steps proceed.


APPENDIX A. RAW CONFER ARTEFACTS

Round 1 per model outputs. Paths of the form tmp slash exp40_audit slash split slash round1 underscore underscore codex dot txt, tmp slash exp40_audit slash split slash round1 underscore underscore gemini dot txt, tmp slash exp40_audit slash split slash round1 underscore underscore chatgpt dot txt, tmp slash exp40_audit slash split slash round1 underscore underscore cc2 dot txt, tmp slash exp40_audit slash split slash round1 underscore underscore deepseek dot txt.

Rounds 2A, 2B, 3, and 3B outputs follow the same pattern with round2a, round2b, round3, and round3b prefixes. Superseded for Experiment 40 gating purposes by the re confer, but preserved for historical reference.

Re confer per model outputs. Paths of the form bench slash logs slash confer_exp40_reaudit_round1 slash codex underscore 20260420T164144Z dot json, and similarly for gemini, cc2, chatgpt, and deepseek. Combined log at bench slash logs slash confer_exp40_reaudit_round1 slash combined underscore 20260420T164144Z dot json.


APPENDIX B. CONFIGURATION AND CODE ANCHORS

Configuration file. bench slash exp40_configs slash 40_gate.json. Contains pass condition, topology, specialist cells, max rounds, earliest stop round.

Alternative gamma convergence function. reference_runner_v2.py line 1064.
Channel violation error class. reference_runner_v2.py line 3116.
Bare validity update function. reference_runner_v2.py line 3133.
Wrapper function, defined but not yet called. reference_runner_v2.py line 3177.
Per finding model parameter access. reference_runner_v2.py lines 3494 to 3497.
Live call site using bare compute_rk. reference_runner_v2.py line 3510.
SymPy specialist with sandbox regression. bench slash immune_agents.py lines 947 to 1019.
Experiment 40 primary test article. bench slash dm slash _feedback.py, approximately 22 kilobytes.
Experiment 40 secondary test article. bench slash dm slash _types.py, approximately 30 kilobytes.
Experiment 39 baseline runner. bench slash reference_runner.py. Confirmed to contain none of the Stage 6 channel wrapper, the channel violation error, the alternative gamma convergence identifiers, or the divergence modulator symbol.


End of report.
