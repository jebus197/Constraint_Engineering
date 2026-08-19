# Panel Review — Enforcement, Prose Targets, and the Runway to BR2

**19 August 2026, dispatched 09:19 BST.** Five models, no compelled convergence.
Brief: 46,459 characters carrying two primary-source packs (raw code with line
numbers, raw measurement tables) plus a quarantined ledger of CC1's claims.

**This file is the COMPLETE, VERBATIM record.** Every response appears exactly as
returned, unedited and untrimmed. Analysis and synthesis live in the companion
note; nothing here is summarised.

---

## Gemini 3.1 Pro Preview (`ge`) — OpenRouter

- returned: **yes**
- elapsed: 44.6s
- length: 5,411 characters

### Verbatim response

Here are my independent adjudications. I have verified the claims against the provided source pack and applied the "tools decide" standard. 

### Q1. THE ENFORCEMENT GAP
**Diagnosis:** The founder is correct in principle, but CC1’s proposed fix (return-to-source then escalate) is inefficient. 
**Recommendation:** 
*   **For SKIP (37.7% - missing parameters):** Return to the source model once. If it fails again, accept the finding but **ZERO its risk-reduction contribution** ($R_k = R_{old}$). Do not discard the defect entirely just because the model cannot format its math.
*   **For FAIL (35.8% - bad math):** The runner already has the model's stated parameters. The runner should **override the model's $R_k$ with the correct deterministic calculation**, log the correction, and proceed. 
**Attack on CC1:** CC1 treats arithmetic failures and missing data as the same class of error. They are not. Rejecting a valid STEM defect because an LLM is bad at floating-point arithmetic is a failure of harness design.
**Self-Falsification:** Overriding the model's math violates the founder's strict rule that "models must formulate conclusions through the mathematical model." If the model's math is wrong, its underlying reasoning for the fix might be hallucinated, and silently fixing the arithmetic masks this.

### Q2. THE PROSE-TARGET WALL
**Diagnosis:** Defaulting to `NO_SCORE` and penalizing prose targets by +0.12 is a critical failure. The measurement proves counterfactual repair works *better* on markdown (41.9% decision rate) than Python (16.7%).
**Recommendation:** Do not use `NO_SCORE`. Use the counterfactual repair tool's verdict to derive $\sigma$ ($S_k$). If both falsifiers agree the defect is resolved in the counterfactual pass, $\sigma = 1$. If they fail, $\sigma = 0$. The tool decides.
**Self-Falsification:** Counterfactual repair on prose relies on an LLM-as-judge to evaluate the falsifier, unlike a deterministic compiler. Treating an LLM's text evaluation as mathematically equivalent to a passing unit test injects subjective bias into a rigid equation.

### Q3. MEASURING $\nu$ ON PROSE
**Recommendation:** Do **not** measure $\nu$ from prose fix artefacts. Keep it tied to the constants ($\nu_b, \nu_f$). 
**Attack on CC1:** CC1’s position to "measure it, never show it to the generating model" is structurally invalid. The operational directive explicitly commands the model to *"compute your residual risk... state your estimates for... $\nu_b, \nu_f$"*. If you hide $\nu$ from the model, it cannot compute $R_k$, guaranteeing a 100% FAIL/SKIP rate in Phase 3. Furthermore, calibrating "shared interfaces" on 129 markdown fixes is pseudo-science; you will arbitrarily penalize good fixes based on brittle parsing.
**Self-Falsification:** By keeping $\nu$ constant, the system ignores the theoretical model where complex, sprawling fixes carry higher re-injection risk. A one-word typo fix and a complete chapter rewrite will carry the exact same complexity penalty.

### Q4. THE BUGZILLA DEFICIT FOR STEM
**Recommendation:** 
*   **(a) Epistemic state:** Add a single new status: `TARGET_INVALID` (or `SPEC_FLAWED`). This allows the model to correctly identify that its falsifier passed because the ground-truth target is wrong, not the claim.
*   **(b) Keying structure:** Do not build full schema enforcement. Key findings by a tuple of `(location, falsifier_hash)`. If a model finds a second defect in the same paragraph, the falsifier code/logic will be different, generating a different hash. This is practically free to implement.
**Self-Falsification:** Keying by `falsifier_hash` is vulnerable to trivial variations. If a model generates the exact same falsifier logic but changes a variable name or adds a comment, the hash changes, and the system will suffer a duplicate explosion.

### Q5. THE RUNWAY QUESTION
**Is the budget sufficient?** YES.
**Minimum sufficient design:** 
1. Execute Stage 1 (Accounting repairs + Replay). **Cost: $0.**
2. Run **exp50 (physics)** as the single live validation of the Stage 2 behavioural fixes. 
3. If exp50 converges cleanly, proceed to 51, 52, and 54.
**Attack on CC1:** CC1 recommends re-running exp46 because it has a baseline. This is a waste of money. The tracker explicitly states the Stage 2.1 bug caused the pipeline to pass *"0 [findings] from round 1 of every run since April 12"*. The exp46 baseline is fundamentally broken. Comparing a fixed system against a system that auto-rejected 97% of findings proves nothing to a hostile reviewer. Exp50 provides a clean, unsuppressed run from start to finish.
**Self-Falsification:** If exp50 fails to converge, we have burned a pristine, built exam target on a broken harness, and we have no prior baseline on that specific target to debug *why* it failed.

### Q6. LOOSE ENDS
**Blocker identified in the source pack:** 
Tracker Item 1.8 states: *"churn detector cannot fire on most of the arc. `rho_earliest_round=12`; of exp44-49 only exp44 reaches R12"*. 
**Diagnosis:** The runs are converging in 4 to 9 rounds. Your churn detector is configured to ignore everything before round 12. It is effectively dead code. 
**Recommendation:** You cannot proceed to BR2 without calibrating `rho_earliest_round` to the actual observed lifecycle of a run (e.g., Round 3 or 4). If you do not fix this, you have no mathematical proof of stability for your capstone experiments.

---

## ChatGPT GPT-5.5 (`cgpt`) — OpenRouter

- returned: **yes**
- elapsed: 527.3s
- length: 14,178 characters

### Verbatim response

I cannot read `/Users/...` from this API session, so this is an adjudication against the supplied source pack, not an independent filesystem inspection.

## Verdict in one line

Proceed, but only after three mechanical repairs are in place: enforce corroboration working, make prose sigma/nu neutral-or-measured rather than punitive-by-default, and repair duplicate/merge accounting before any paid exp50 run. The remaining runway is sufficient for a publishable BR2 **if** the claims are narrowed and one matched rerun is done; it is not sufficient for a fully calibrated finished platform.

---

# Q1 — Enforcement gap

## Diagnosis

Yes. The founder’s diagnosis is right.

If the operational directive says models **MUST** show residual-risk working, but `_validate_rk_computation` is advisory and “never rejects findings”, then the harness is not enforcing one of its own stated epistemic controls.

The measured failure rate is too large to treat as cosmetic:

- 35.8% wrong arithmetic when enough parameters exist.
- 37.7% uncheckable.
- Only 23.4% clean pass.

That means the runner is currently accepting a large amount of unsupported risk prose.

## Simplest sufficient enforcement

Do **not** hard-reject the scientific finding on first failure.

Reject the **corroboration block**, not necessarily the falsifier.

Recommended policy:

1. **PASS**  
   Accept the model’s stated `R_k`.

2. **WARN**  
   Accept only the runner-recomputed `R_k`, not the model’s stated value. Log discrepancy.

3. **FAIL**  
   Return once to the same model with:
   - its stated parameters,
   - runner recomputation,
   - discrepancy,
   - instruction to repair the arithmetic or restate parameters.

4. **SKIP**  
   Return once asking for the missing required fields.

5. **Second FAIL/SKIP**  
   Mark the finding as:
   - falsifier status: whatever the tool actually decided;
   - corroboration status: **INVALID / UNCORROBORATED**;
   - residual-risk contribution: **zero / no score**.

6. **Escalate** only when the finding is high-severity, tool-confirmed, or needed for a run decision.

This preserves the CDSFL principle: tools decide factual confirmation. A bad `R_k` calculation should not erase a real falsifier, but it also must not contribute to confidence, convergence claims, routing, or publication metrics.

## Why not hard rejection?

Because at the measured rate it would discard roughly three quarters of first-round findings. That would introduce a new selection effect: the system would favour models that format arithmetic correctly over models that found valid defects.

The failure directions differ:

- **FAIL with understated risk** creates false confidence.
- **FAIL with overstated risk** unfairly suppresses a valid finding.
- **SKIP** is worse epistemically because the direction is unknowable.

So the sufficient fix is: **block risk use, not defect evidence**.

---

# Q2 — Prose sigma and nu

## Core problem

The current treatment is wrong for prose targets.

If `apply_sk_to_rk` gives `NO_SCORE` for sigma on prose, then sigma has not been assessed. Penalising that by pushing reinjection risk upward is not measurement. It is an artefact of missing instrumentation.

On prose/markdown targets, absence of AST/compiler/tests must not be treated as evidence of bad repair.

## Recommended fix for sigma

Use counterfactual repair as the primary prose sigma mechanism.

For a proposed prose fix:

1. Apply the fix to a copy of the target.
2. Re-run the original falsifier against:
   - original target;
   - repaired target.
3. Require directional agreement:
   - original fails;
   - repaired version no longer fails;
   - no obvious converse/regression failure is introduced.
4. Assign sigma:
   - `sigma = 1` or high value if counterfactual repair resolves the falsifier;
   - `sigma = 0` if it does not;
   - `NO_SCORE` if the repair cannot be applied or the falsifier cannot be re-run.

For `NO_SCORE`, use **zero movement**, not maximum reinjection penalty.

That means:

- do not reward;
- do not punish;
- mark as unmeasured.

## Does the markdown surprise change the answer?

Yes. It strengthens the case for counterfactual repair.

The measured result that counterfactual repair decides 41.9% of MARKDOWN pairs versus 16.7% of PYTHON pairs directly refutes the project assumption that prose is necessarily less decidable. For prose, counterfactual repair should become the default sigma path, not a fallback.

## Recommended fix for nu

For prose, nu should not be guessed from sigma or constants.

It should be measured from the fix artefact’s blast radius:

- number of changed lines/tokens;
- number of distinct sections touched;
- whether definitions, theorem statements, assumptions, interfaces, notation, or shared terms move;
- whether cross-references are changed;
- whether the fix affects a local sentence or a reusable conceptual object.

If nu cannot be measured, again use neutral `NO_SCORE` / zero movement, not punitive inflation.

---

# Q3 — Should nu be measured from the fix artefact?

Yes, but modestly.

The appendix defines nu as reinjection/complexity risk:

> “Localised one-line changes have low nu. Changes to shared interfaces have higher nu.”

That is artefact-dependent. A formula with only constants and sigma cannot implement that definition.

## Minimum implementation

For each parsed fix, compute a complexity vector.

For code:

- changed lines/tokens;
- hunks;
- files;
- functions/classes touched;
- signature/API/schema changes;
- call-site fanout if cheaply available.

For prose/markdown:

- changed lines/tokens;
- sections touched;
- equations changed;
- assumptions/definitions/theorems touched;
- references/citations changed;
- whether a term used elsewhere is redefined.

Then compute an ordinal complexity score:

```text
c = weighted sum of normalized features
nu = 1 - exp(-lambda * c)
```

Keep the first version simple and monotone.

## Calibration with only 129 parseable archived fixes

Do not pretend this is enough for a precise supervised calibration.

Use the 129 fixes to calibrate scale, not truth.

Recommended calibration:

1. Hand-label or rule-label obvious anchors:
   - local one-line/sentence change;
   - local paragraph/function change;
   - multi-location change;
   - shared-interface / definition / signature change.

2. Set monotone bands, for example:
   - local one-line: very low nu;
   - local block: low;
   - multiple sections/functions: medium;
   - shared interface/definition/signature: high.

3. Fit only the mapping from feature score to those bands.

4. Replay archive with sensitivity bands:
   - conservative nu;
   - nominal nu;
   - aggressive nu.

If conclusions change across reasonable nu mappings, the system is not yet calibrated enough to make strong quantitative claims from `R_k`.

## Failure mode if nu is wrong

- Too low: broad risky repairs look deceptively safe.
- Too high: necessary broad repairs are punished even when they genuinely resolve the flaw.
- Formatting-heavy prose fixes may look complex when semantically trivial.
- Small edits to central definitions may look safe when they are actually high-blast-radius.

## Attack on CC1’s position

CC1 is mostly right that nu belongs in Phase 3 and should be measured from the fix artefact.

But two cautions:

1. **“Never show it to the generating model” is not enough.**  
   Hiding the exact formula avoids gaming, but if models receive no behavioural signal at all, they will not learn to prefer simpler sufficient repairs.

   Better: show the principle, not the scoring formula:
   > “Prefer the smallest repair that resolves the falsifier; broad changes are penalised.”

2. **Phase ordering does not rescue bad measurement.**  
   Putting nu after sigma ensures the equation has the right structure, but if sigma or nu are badly estimated, the numeric output can still be misleading.

---

# Q4 — Minimum Bugzilla/STEM structural change before BR2

## (a) Missing epistemic state

A single new status value is not quite sufficient.

The system needs to separate two axes:

1. **Finding validity**
   - confirmed;
   - rejected;
   - uncertain;
   - duplicate;
   - merged.

2. **Target/specification status**
   - target artefact defect;
   - specification/world-model defect;
   - invalid report;
   - unresolved.

Minimum before BR2:

```text
finding_verdict = CONFIRMED
target_resolution = SPECIFICATION_OR_TARGET_CLAIM_WRONG
```

or equivalent.

The important point is that CDSFL must be able to record:

> The model’s finding was right, and the target claim was wrong.

Without that, STEM evaluation is forced into software-bug semantics and will misclassify successful falsifications.

Deferred:

- discussion-board layer;
- model-generated theories;
- full epistemic workflow;
- rich maintainer-style triage UX.

## (b) Structural keying instead of location-only keying

Do not build full schema enforcement before BR2 unless it is already almost done.

Cheaper sufficient fix:

Add a sidecar structural fingerprint for each finding:

```text
fingerprint = hash(
  normalized claim text,
  defect type,
  accused proposition/equation/function,
  falsifier type,
  failure signature,
  cited location
)
```

Use this for duplicate/merge decisions.

Minimum rule:

- same location alone is not enough to force duplicate;
- duplicate requires same or near-same structural fingerprint, or counterfactual repair equivalence;
- multiple live findings may exist at one function/section/equation if their fingerprints differ.

This gets most of the benefit without a full schema migration.

---

# Q5 — Is the remaining runway sufficient?

## Answer

Yes, but only for a narrowed publication claim.

It is sufficient to validate:

> The repaired CDSFL harness can run prospective STEM falsification experiments with enforced corroboration, repaired duplicate accounting, and prose-compatible repair scoring.

It is **not** sufficient to claim:

> The old exp44-49 convergence curves are clean evidence of the true process.

Those curves came from a suppressed process and should be treated as compromised historical runs.

## Minimum sufficient design

Before any paid live run:

1. Implement enforcement for `R_k` working.
2. Implement prose-safe sigma/nu:
   - counterfactual repair when decidable;
   - neutral `NO_SCORE` otherwise.
3. Fix duplicate auto-reject / feedback rendering.
4. Preserve tool verdicts through synthesis.
5. Fix or explicitly quarantine merge semantics.
6. Replay exp44-49 and show:
   - old accounting reproduction;
   - new accounting deltas;
   - no unexplained replay mismatch.

Then run:

### Live matched rerun

Run **exp46** again.

Reason: same target/config gives the cleanest before/after test, and exp46 had the narrowest convergence margin.

This is the cheapest live causal check against the four-month defect.

### First clean prospective run

Run **exp50** after the behavioural fixes.

Reason: replay cannot validate prompt-visible behavioural changes.

### Continue only if both pass

Then proceed to:

- exp51;
- exp52 four-cell factorial;
- exp54 capstone.

## Is exp46 + exp50 enough?

Enough to decide whether to continue.

Not enough by itself for the full BR2 publication if the paper makes broad domain claims. For publication, exp51/52/54 still matter.

## What would a hostile reviewer demand?

A hostile reviewer would demand at least one of these:

1. Same-target before/after evidence that the behavioural fix changed the process.  
   That is why exp46 rerun matters.

2. Prospective clean runs not contaminated by the duplicate-suppression regime.  
   That is why exp50/51/52/54 matter.

3. Proof that archive replay reproduces old metrics before claiming deltas.  
   If replay cannot reproduce old series, the accounting repair is not validated.

4. Evidence that prose sigma/nu is not just another unvalidated model judgement.  
   That is why counterfactual repair and neutral `NO_SCORE` are needed.

I would not spend the money on a full exp44-49 rerun unless exp46 or replay exposes an unexplained failure.

---

# Q6 — Loose ends that could block progression

## Blocks before exp50

These should be fixed before a paid live run:

1. **Duplicate auto-reject / prompt feedback**
   - If models are still told their findings are near-duplicates, exp50 is not clean.

2. **Tool verdict preservation**
   - If tool-confirmed/rejected findings become final `DUPLICATE`/`UNCERTAIN` through synthesis, the run cannot support the CDSFL claim.

3. **Corroboration enforcement**
   - At least reject/repair invalid `R_k` blocks before they affect metrics.

4. **Prose sigma/nu neutralisation**
   - No prose target should be penalised merely because no AST/compiler/test suite exists.

5. **Replay old accounting exactly before reporting repaired deltas**
   - If old series cannot be reproduced, replay conclusions are not trustworthy.

6. **Exam-target contamination risk**
   - The tracker says answer-key blobs remain reachable from a remote branch. If any live model or tool can access that repository state, this is a blocker. If not, document the isolation.

## Blocks before capstone / BR2

1. **exp54 is not built.**
2. **Merge semantics remain unresolved.**
   - If `MERGED` is described as fold but implemented as delete-with-pointer, publication metrics need either corrected semantics or corrected wording.
3. **Short-run churn detector issue**
   - `rho_earliest_round=12` means most current runs never trigger it. Either adapt it for short runs or do not claim it monitored those runs.
4. **exp47 round-count inconsistency**
   - Not a blocker to exp50, but any retrospective analysis involving exp47 needs quarantine or correction.

---

# Strongest falsification of my answer

My recommendation fails if source inspection shows that `R_k`, sigma, or nu actually **do** gate convergence, routing, or acceptance somewhere outside the cited functions.

If they gate live decisions, then “keep the falsifier but zero/neutralise the corroboration contribution” may be too weak; bad `R_k` would already be behaviourally contaminating the run, and stricter rejection or rerouting would be required before exp50.

---

## Codex GPT-5.5 (`cx`) — OpenRouter

- returned: **yes**
- elapsed: 524.4s
- length: 11,928 characters

### Verbatim response

I cannot inspect `/Users/...` from this API session, so this verdict is against the appended primary extracts. My strongest global caveat: if the live repository contradicts the line references or measurements in the pack, this answer should lose to the source.

## Q1 — Enforcement gap

Yes. The diagnosis is right.

If the directive says models **MUST** show the residual-risk working, and the runner only logs arithmetic failures, then CDSFL is not enforcing one of its own claimed safeguards.

But I would **not** switch on first-round hard rejection of all FAIL/SKIP blocks. At the measured rate, that would discard about three quarters of findings immediately, including likely true tool-confirmed defects.

### Simplest sufficient enforcement

Use a **repair-before-reject** gate:

1. **If parameters are complete but R_k is wrong**  
   The runner recomputes R_k and tells the model:  
   “Your stated R_k does not follow from your own numbers. Correct this block.”

2. **If parameters are missing / SKIP**  
   Return once to source with a strict template requiring:
   `R_old, eta, d, p, S_k/sigma, nu_b, nu_f/nu, R_k`.

3. **One correction attempt only.**

4. **If still FAIL/SKIP after correction**  
   Do not let that finding contribute to residual-risk claims, convergence claims, or published corroboration statistics. Route/escalate if the experiment design allows it.

5. **Do not delete the underlying defect automatically** if the falsifier itself is tool-confirmed. Separate:
   - “defect/falsifier confirmed”
   - from “risk/corroboration block compliant”

This preserves true findings while enforcing the mathematics.

Failure direction matters:

- Wrong R_k **too low** = dangerous overconfidence.
- Wrong R_k **too high** = conservative numerically, but still proves the model is not following the required computation.
- SKIP = uncheckable, so it cannot support a quantitative claim.

So my recommendation: **return once, then quarantine/zero quantitative contribution, then escalate if available.** Not immediate hard rejection.

---

## Q2 — Prose-target wall

The current behaviour is wrong if `sk=0` on prose causes maximum re-injection penalty. “Not assessed” is not evidence of “maximally bad fix.”

### Fix

For prose/markdown targets, obtain `sigma` by **counterfactual repair**, not by AST/compiler/test-suite signals.

Process:

1. Apply the proposed prose repair to a copy of the target.
2. Re-run the original falsifier/check.
3. Where possible, also run the reverse/control check.
4. Score:
   - original defect no longer reproduced and control agrees → high/1 sigma
   - defect still reproduced → sigma 0
   - ambiguous / no executable falsifier → `NO_SCORE`, but with **zero movement**, not penalty movement

The measured surprise matters: markdown counterfactual repair deciding **41.9%** of pairs versus **16.7%** for Python means the project should stop assuming prose is intrinsically less decidable. Prose has no compiler, but the falsifier can still be re-run against an edited claim.

So:

- **NO_SCORE with zero movement is right only when the repair cannot be assessed.**
- It is not right as the default for all prose.
- The better default is: try counterfactual repair first; only then neutral `NO_SCORE`.

For `nu`, prose also has artefacts: changed lines, sections, equations, definitions, cross-references, claim locations. It should not require AST.

---

## Q3 — Should `nu` be measured from the fix artefact?

Yes, but cautiously.

The current code makes `nu` effectively constant. That contradicts the appendix definition, where `nu` is about change complexity: one-line local edits low, shared-interface edits high.

### Minimum calibration with 129 parseable fixes

Do not pretend 129 fixes gives a reliable learned reinjection model. Use a monotone, auditable heuristic.

Extract features such as:

- number of changed lines/tokens
- number of hunks
- number of distinct sections/files/locations touched
- whether equations/definitions/interfaces/signatures move
- whether shared vocabulary, claim schema, or cross-reference structure changes
- whether the repair is local to the accused claim or global to the target

Create a complexity score:

```text
C = weighted sum of normalized features
```

Then map to `nu` by empirical rank/quantile over the 129 fixes:

```text
nu = nu_min + rank_percentile(C) * (nu_max - nu_min)
```

Use conservative bounds, for example:

- tiny local prose/code fix: low `nu`
- multi-location/shared-interface fix: high `nu`
- top decile capped high but not automatically 1.0

The important point is monotonicity, not precision.

### Failure mode

If `nu` is too high, CDSFL will punish broad but necessary repairs and prefer trivial local edits.

If `nu` is too low, models can propose sweeping repairs that erase the immediate defect while injecting uncontrolled changes.

Both are bad. The worse publication risk is claiming calibrated precision when the data only supports a coarse complexity proxy.

### Attack on CC1

CC1 is right that `nu` should be measured from the fix artefact.

But I reject “never show it to the generating model” as too strong.

Do not show exact weights if gaming is a concern, but the model should be told the rule qualitatively:

> local sufficient repairs are preferred; broad/shared-interface repairs carry reinjection cost.

Otherwise the system punishes models for a hidden objective.

Also, saying “Phase 3 comes after resolution, so ordering is enforced by the equation” is only partly true. The equation enforces ordering algebraically, but a badly calibrated `nu` can still dominate outcomes and make the ordering meaningless in practice.

---

## Q4 — Bugzilla deficit for STEM

### (a) Missing epistemic state

A new status value helps, but is not sufficient by itself.

Minimum before BR2:

Add a distinct epistemic outcome such as:

```text
FINDING_CONFIRMED_TARGET_CLAIM_FALSE
```

or

```text
TARGET_SPECIFICATION_DEFECT
```

Meaning:

> the finding correctly refuted a claim in the target; the target/paper/specification, not the finding, is wrong.

But this needs at least three fields:

1. finding validity: confirmed / rejected / uncertain
2. target-claim validity: supported / refuted / uncertain
3. correction state: unresolved / repaired / superseded

Do not overload one Bugzilla-style status field with all three.

### (b) Structure-keyed claims

Do not build full schema enforcement before BR2 unless it is already cheap.

Minimum useful change:

- keep location as a field
- add a structural fingerprint:
  - normalized claim text
  - relation/operator
  - variables/entities
  - units/quantities where present
  - cited equation/table/section if present
- duplicate only if structure fingerprint is sufficiently same, not merely same location
- explicitly allow multiple live defects at the same location

This addresses the documented limitation: location-only keying cannot see a second distinct defect in an already-flagged function/claim.

Defer:

- full ontology
- discussion-board layer
- model-derived theory monitoring
- mature cross-paper claim graph

For BR2, the publishable requirement is narrower: do not collapse distinct STEM claims merely because they live in the same place.

---

## Q5 — Runway

Yes, the remaining budget can be sufficient.

But **CC1’s minimum of only exp46 re-run plus exp50 is not enough for publication standard** unless the published claim is very narrow.

### Minimum sufficient design

I would do:

1. **Offline replay exp44–49**
   - reproduce old archived series exactly under old accounting
   - report deltas under repaired accounting
   - do not use the old convergence curves as clean evidence of behaviour

2. **Implement enforcement before live runs**
   - R_k correction gate
   - prose sigma counterfactual scoring
   - neutral `NO_SCORE`
   - measured artefact-based `nu`
   - duplicate-auto-reject repair
   - tool verdict preservation

3. **One matched live re-run**
   - exp46 is a good choice because it had the narrow convergence margin and only 6 rounds
   - purpose: same-target before/after behavioural check

4. **At least two clean prospective runs**
   - exp50 physics
   - exp51 biology

5. **Run exp52 factorial**
   - this is needed if BR2 claims mechanism/condition effects, not just “the harness ran once”

6. **Build/run exp54 only after the above pass**
   - capstone should integrate validated fixes, not discover basic instrumentation defects

I would not pay for a full exp44–49 live re-run unless replay fails to reproduce the archived series or exp46/exp50 expose a new behavioural instability.

### What a hostile reviewer would demand

A hostile reviewer will not accept exp44–49 as clean convergence evidence because the process was suppressed by the 97% duplicate flagging.

They may demand:

- at least one same-target before/after run
- more than one clean prospective domain
- proof the duplicate repair changed what models saw
- predeclared enforcement rules
- sensitivity analysis for `nu`
- separation of tool-confirmed defects from model arithmetic compliance
- evidence that prose scoring is not just LLM judgement renamed as measurement

The current plan covers this only if it goes beyond exp46+exp50.

So: **runway is sufficient, but not generous. Do not spend it on six historical re-runs. Spend it on replay + one matched re-run + clean prospective runs.**

---

## Q6 — Loose ends that block progression

I see the following blockers before exp50/51/52/54/BR2:

1. **Duplicate auto-reject / feedback repair**
   Because it changes what models see. Must be fixed before any clean live run.

2. **Tool verdict preservation through synthesis**
   If 19 CONFIRMED + 8 REJECTED tool verdicts can become mostly DUPLICATE/UNCERTAIN, the runner is not preserving tool decisions.

3. **R_k enforcement**
   Not necessarily hard rejection, but the correction/quarantine gate must exist before new results are publishable.

4. **Prose `sigma`/`NO_SCORE` behaviour**
   Must not punish unassessed prose repairs as maximum reinjection.

5. **`nu` no longer constant**
   At least a coarse artefact-complexity measure is needed.

6. **MERGED semantics**
   If the system tells models MERGE folds evidence but implementation deletes-with-pointer, either implementation or prompt must change.

7. **Replay exit test**
   If old accounting cannot be reproduced from archive, stop. The replay harness is then untrusted.

8. **exp47 round-length inconsistency**
   Must be resolved before using exp47 in per-round replay comparisons.

9. **Churn detector timing**
   If `rho_earliest_round=12`, most exp44–49 runs could never trigger it. Do not claim churn-monitor validation from those runs.

10. **exp54 not built**
   Not a blocker for exp50, but it is a blocker for the capstone/BR2 arc.

I would not block exp50 on the full structural Bugzilla/STEM schema work. The minimum epistemic status + structural fingerprint can be done before BR2, but the expensive platform layer should be deferred.

---

## Final recommendation

Proceed, but in this order:

1. Fix enforcement, prose scoring, `nu`, duplicate feedback, and tool-verdict preservation.
2. Replay exp44–49.
3. Re-run exp46.
4. Run exp50 and exp51 as clean prospective tests.
5. Run exp52.
6. Build exp54 only after those pass.

Do not do a full exp44–49 live re-run unless replay or exp46 shows the repaired system cannot be trusted.

## Strongest falsification of my answer

My answer fails if source inspection shows any of these are false:

- R_k truly has no role in any claimed guarantee or publication metric.
- The duplicate flag was not actually rendered into prompts.
- Counterfactual repair labels are too contaminated by broad repairs to score prose sigma.
- Archive replay cannot reproduce old series.
- exp50/51/52 are not financially available in practice.

If any of those hold, the minimum design above is too optimistic.

---

## DeepSeek V4 Pro (`ds`) — DeepSeek direct

- returned: **yes**
- elapsed: 306.8s
- length: 6,913 characters
- note: retry; system prompt corrected to state no tool access

### Verbatim response

## Q1 — Enforcement gap

Diagnosis is right: accepting a residual-risk block that does not follow from the model’s own numbers is a mechanical compliance failure. But the unit of rejection should be the **corroboration block, not the finding**.

The finding’s existence is already decided by the runner re-executing the falsifier. R_k is a derived risk estimate. Conflating “bad arithmetic” with “false finding” would discard ~73.5% of findings, most of which may still be valid tool-confirmed detections.

**Simplest sufficient fix:** add a `risk_status` to each corroboration block.

- `PASS` / `WARN`: accept R_k.
- `FAIL`: mark R_k `null`, send **one** targeted correction request back to the source model containing the runner’s recomputed R_k and the specific mismatched terms.
- `SKIP`: request the missing parameters once.
- After one failed correction, leave R_k `null` and propagate “not computed” downstream. Do not zero the finding itself.

Hard rejection fails by creating false negatives. Escalation loses context and costs more. Return-once is the cheapest mechanism that still enforces the working requirement.

Attack on CC1 #1: “highest-value” is only true if R_k actually gates something. The brief also says R_k does not gate convergence. I would need to read every R_k consumer in `reference_runner_v2.py` before ranking this above the Stage 2 behavioural fix.

## Q2 — Prose-target sigma/nu

Current behaviour is wrong: `sk=0` means “fix has zero efficacy”, not “we don’t know”. That pushes risk up by 0.12 per finding on a prose target for a fix nobody assessed.

**Fix:**

1. Make `apply_sk_to_rk` return a tri-state: `SK_KNOWN`, `SK_UNKNOWN`, not a silent zero.
2. On prose, obtain sigma from **counterfactual repair**: apply the fix, re-run the original falsifier and the reverse/guard falsifier, and require both directions to agree. Sigma becomes the share of falsifier-direction tests that pass after repair.
3. Do not let `SK_UNKNOWN` trigger the re-injection penalty. Propagate R_k as “not computable” rather than forcing a penalty.

The measured surprise does change my answer. Markdown falsifiers are executable without a compiler; 41.9% decisiveness versus 16.7% on Python means prose is not the wall for sigma. The wall is the code’s assumption that no AST means no assessment.

## Q3 — Measuring nu from the fix artefact

Yes, measure nu. The current constants discard exactly the distinction the appendix defines: localised one-line changes versus shared-interface changes.

**Calibration with 129 archived fixes:** extract structural features from the fix artefact:

- lines added/deleted
- distinct locations touched
- whether a shared structural interface changes (for prose: headings, links, signatures, shared claims)
- scope of change

If there are archived outcome labels, fit a monotonic model to those outcomes and hold out a validation slice. If there are no outcome labels, **calibrate by percentile rank only**; that gives a complexity index in [0,1], not a true probability. Do not present it as a calibrated re-injection probability.

**Failure mode of getting it wrong:** too-high nu makes simple sufficient fixes look risky; too-low nu hides genuine re-injection risk. If calibrated on the same archive without held-out data, it will overfit and may misrank novel fixes.

**Attack on CC1 #3:** hidden measurement is good for anti-gaming, but hidden nu is not an enforcement mechanism. It is a post-hoc accounting label. “Ordering enforced by the equation” is misleading because the model never sees the equation’s consequence when it chooses the fix. If the goal is behavioural simplicity pressure, the model needs a signal; if the goal is accurate reporting, hidden measured nu is fine.

## Q4 — Epistemic state and structural keying

**(a) Minimum change:** add a terminal status value — e.g. `TARGET_REFUTED` or `SPECIFICATION_WRONG` — meaning: the finding is correct, the target claim is what must change. Add one field pointing to the refuted target claim. A status value is sufficient for BR2 if every report/aggregation branch treats it as a successful detection.

**(b) Minimum structural keying:** do not build full schema enforcement. At claim parse time, compute a normalised claim fingerprint from claim subject/predicate/expected-value structure and use that as the primary identity key. Location becomes secondary. This directly addresses the “second distinct defect in an already-flagged function” problem and is much cheaper than full schema.

Defer: discussion-board layer, full schema constraints, full epistemic workflow.

## Q5 — Runway

**No.** The current plan is not enough for publication standard.

CC1 is partly right that six full re-runs are unnecessary. But `exp46 re-run + exp50` is still a pilot, not a confirmatory package.

**Minimum sufficient design:**

1. Stage 1 replay passes its exit test: reproduce the old accounting exactly, then report a defensible delta.
2. Pre-register primary endpoints and the matched-pair target **before** live runs. Selecting exp46 because it had the narrowest margin is post-hoc; that selection must be frozen now.
3. Run **exp46** as the matched before/after on the same target/config.
4. Run **exp50 and exp51** as two clean cross-domain live runs. One clean run cannot separate the fix effect from domain or seed effect.
5. Defer exp52 factorial and exp54 capstone until those pass.

That is **three live runs**: one matched re-run plus two clean runs. If the budget only permits two, label it a pilot and use BR2 as the confirmatory study. Do not call two runs publication standard.

A hostile reviewer will demand:

- pre-registration of endpoints and run selection
- more than one clean domain
- a genuine before/after control, not only a new target
- seed robustness or repeated runs
- held-out validation of sigma/nu calibration
- proof that unrun experiment answer keys are not reachable

## Q6 — Loose ends

Two blockers from the tracker are not yet fully closed:

1. **Remote branch answer-key exposure.** The tracker says 17 answer-key blobs are reachable from a remote branch, including unrun exp50/51/52. That must be scrubbed or the branch deleted before any live run; otherwise the key-vault claim is false.
2. **exp47 report/registry length mismatch.** Any per-round exp47 replay comparison is invalid until the 9-round report and the registry’s `open_since_round` up to 13 are reconciled or declared invalid.

## Strongest self-falsification

I have not seen the actual consumers of R_k or the archived fix-artefact schema. If R_k feeds a gate not shown here, my Q1 “do not reject the finding” fix may be insufficient. I would need to read `reference_runner_v2.py` around all R_k consumers before finalising Q1. For Q5, my three-run minimum is still underpowered; one repeated run per domain is not robust. I defend it as the minimum publishable package, not a rigorous one.

---

## Claude Opus 4.7 (`cc2`) — Claude CLI, Max subscription

- returned: **yes**
- elapsed: 620.1s
- length: 15,583 characters

### Verbatim response

**Panel verdict — independent. 2026-08-19, HEAD `8d8e729`.**

I re-derived the enforcement numbers from the archive myself before answering. My corpus scoping differs from CC1's (704 corroboration blocks vs its 385, same six runs), and the proportions land in the same place: PASS 24.1%, WARN 3.6%, FAIL 31.7%, SKIP 40.6%. The headline is robust. What it *means* is not, and that is where my verdict departs from CC1's.

---

## Four things I found that are not in the pack

**1. Most of the SKIP tier is the harness failing to read compliant working, not models failing to show it.** Of 286 SKIPs, 220 have an `R_k =` line carrying a readable number that `_RK_RE_TRAILING_FLOAT` (`reference_runner_v2.py:7303`) cannot reach, because it anchors on `$` and the models write markdown. Real examples pulled today:

```
R_k = 0.30 × (1 − 0.90×0.85×0.80) × 0.60 + 0.05 = 0.30 × 0.388 × 0.60 + 0.05 = **0.12**.
Residual risk: `R_k ≈ 0.385`.
```

Bold markers, a backtick, a full stop. That is it. **77% of the "did not show its working" tier showed its working.** Switching on enforcement against this measurement would reject compliant models for using asterisks.

**2. The return-to-source mechanism the founder is asking for already exists, is already wired, and is starved.** `_feedback.py:304-326` builds an `R_k INCONSISTENT` record; `:481-486` renders it into the next round's prompt. It fires — 20 of 170 files in exp44, 2 of 43 in exp45 — against a 31.7% FAIL rate. The reason is `priority_score` (`:155-175`): near-duplicate contributes up to **+2.0**, R_k discrepancy at most **+1.0** and typically ~0.08 (it is `min(1.0, |delta|)`). With `top_k=10` and the similarity function flagging 97% of pairs, every finding carried a near-duplicate flag worth ≥1.4 and the R_k flag was crowded out of every prompt. **The enforcement gap and the dedup defect are the same defect seen twice.**

**3. Two hard bugs in that path, both free to fix.**

- `_feedback.py:483` tells the model `aggregate = 0.26`. The value it prints is the fourth element of `validate_round_rk`'s tuple, which is `recomputed_rk` — the recompute from *the model's own stated parameters*. The prompt calls the model's own arithmetic an "aggregate", i.e. a peer average. `cdsfl_operational.md:746` repeats the same wrong word. A model told "you differ from the aggregate" is entitled to hold its ground; a model told "your own numbers do not close" is not. **The flag has been misnaming its own evidence for the whole arc.**
- `_feedback.py:325` is dedented out of the `for finding in targets:` loop opened at `:322`. When a finding id resolves to more than one target, only the last record ever receives its discrepancy; `rec` leaks from the loop. Latent, silent, one-line fix.

**4. The prose counterfactual result is real and its interpretation in the pack is wrong.** 41.9% vs 16.7% replicates exactly. The per-run breakdown does not survive it:

| run | SAME | DIFFERENT |
|---|---|---|
| exp44 (py) | 5 | 10 |
| exp45–47 (py) | 0 | 0 |
| exp48 (md) | 11 | 0 |
| exp49 (md) | 7 | 0 |

Markdown returns **18 SAME and 0 DIFFERENT**. It does not decide better — it decides in one direction only. That is the signature of a degenerate mode: on prose, "apply the fix" rewrites the passage, both falsifiers stop firing against a passage that no longer exists, and SAME falls out by construction. It is DS's patch-equivalence objection, now with measured support the tracker does not have. Under any prior where the prose duplicate base rate is ≤0.85, 18/18 has p ≤ 0.054 — suggestive, not proof. And the Python "16.7%" is entirely exp44; three of four Python runs decided nothing at all, which is its own unexplained failure and is being averaged into a rate.

---

## Q1 — Diagnosis right, enforcement wrong

**The founder's diagnosis is correct and is more correct than he knows.** It is not that enforcement was designed and left advisory. It was designed, built, wired, mislabelled in the prompt, and then out-competed for prompt space by a broken duplicate detector. That is four mechanical failings on your side, exactly as stated.

**Simplest sufficient enforcement, in order, all free:**

1. Fix the extractor: accept a float anywhere on the R_k line, strip `**`, backticks, trailing punctuation. Recovers ~220 blocks from SKIP.
2. Rename `aggregate` → `recomputed from your stated η, d, p, S_k, ν` in `_feedback.py:483` and `cdsfl_operational.md:746`, and print the recompute *and the four intermediate values* so the model sees where it diverged.
3. Fix the `:325` indentation.
4. Raise R_k discrepancy in `priority_score` from `min(1.0, |Δ|)` to a flat **+2.5 on FAIL** — above near-duplicate, below REFUTED. A FAIL is a self-inconsistency, which is strictly more damning than a similarity score.
5. Re-measure after 1–4 on the archive. **Only then decide about rejection.**

**Do not switch on rejection now.** Not because 73.5% is too painful, but because 73.5% is not the failure rate — it is the failure rate of the instrument plus the models, undifferentiated, and CDSFL's founding principle forbids acting on an unvalidated measurement. Tools decide; this tool has not been shown to work.

On the eventual policy: **return-to-source once, then downweight, never hard-reject.** A hard reject on FAIL fails in the dangerous direction — it discards a true finding whose author fumbled the arithmetic, and residual risk is a self-report about a *claim*, not the claim itself. Escalation up the routing ladder I would not build: it spends money to re-derive a number that gates nothing (see Q3), and the escalation ladder is untested.

One caveat that cuts against my own recommendation 4: the FAIL population I sampled is dominated by models applying a *consistently different* equation — `R_k = R_old·(1−q)·S_k + ν`, with no `/(1−q·R_old)` denominator and S_k as a multiplier rather than a blend. That is not sloppiness, it is a competing formula appearing across models. The directive states the correct four lines plainly at `cdsfl_operational.md:257-262`, so this is a genuine model failure — but a *systematic* one, which means feedback naming the specific divergent term will likely fix it in one round. That is testable on replay before any live spend.

---

## Q2 — sigma and nu on prose: NO_SCORE is right, and the counterfactual route is not the fix

**Keep NO_SCORE with zero movement.** `apply_sk_to_rk`'s docstring at `:7201-7217` is the best-reasoned code in the pack and the distinction it protects — "not scored" ≠ "scored zero" — is correct. Do not weaken it.

**Do not build prose sigma on counterfactual repair.** The 18/0 asymmetry above is a live warning that the method returns SAME by construction on text. The tracker's item 4.1 — a generated control target carrying two known-distinct defects with a plausible common repair — is the test that settles it, costs only scripting, and I would **promote it from PROPOSED to blocking for any prose sigma work**.

**What I would do instead, and it is cheaper:** on prose, sigma has an honest tool-verifiable proxy that is not patch equivalence — *does the falsifier the finding itself supplied still fire after the fix, and does a falsifier written against the fix's own claim fail?* That is the falsifier surviving as an artefact, not the repair surviving as a diff. It uses machinery you already have. But it is unvalidated, so it belongs behind the 4.1 control too.

Until then: NO_SCORE, and say so in the paper. "On prose targets the harness declines to score fix efficacy, and R_k is held" is a publishable, defensible statement. "We scored prose fix efficacy by patch equivalence" is a reviewer's opening.

**One correction to the pack.** The A2 NO_SCORE path landed 2026-08-01 (in `043a0a8`, 15 August). exp44–49 ran 27–29 July. `NO_SCORE` appears **zero times** in every archived log. It has 325 passing unit tests and **has never executed in a live run**. exp50 and exp51 will be the first. That is not a blocker — it is a named risk that belongs in the exp50 pre-flight.

---

## Q3 — Measure nu from the artefact: yes, but CC1 is wrong that it is free

**Measure it.** Lines changed, distinct locations, whether a signature or shared interface moves — these are AST facts, and the appendix's own definition of nu is a complexity measure, so the code using two constants is a straightforward mismatch between spec and implementation. **Do not show it to the generating model:** the moment nu is visible and rewarded, "declare the fix one-line" becomes the winning move. CC1 is right about that, and right that Phase-3 placement enforces the ordering by arithmetic rather than by prompt.

**CC1 is wrong that this is replay-validatable at zero cost.** `check_sk_threshold` (`:7464`) takes `nu_b` and `nu_f` and is called live at `:7609`; below S\*, the fix is set `SK_REJECTED`. A rejected verdict scores **+3.0** in `priority_score` and enters the next round's prompt. So changing nu changes S\* rejections, which changes prompts, which invalidates replay for exactly the reason the runway tracker gives for Stage 2. There were 467 Valley-of-Bad-Fixes log lines across the arc — this path is live, not dormant.

And the second half is worse: on prose, NO_SCORE short-circuits at `:7595`, **before** the S\* check. Measured nu never reaches a prose target at all. So for BR2 and the exam experiments, measured nu is currently inert. Building it and claiming it as a BR2 improvement would be claiming a change that cannot fire on BR2's targets.

**Recommendation:** build the nu measurer, log it in shadow beside the constant, ship neither into R_k before exp50. Calibration on 129 fixes is thin, and the failure mode of getting it wrong is asymmetric and nasty — nu too high pushes R_k up permanently and, on the S\* path, rejects good fixes for being large. Shadow first. That genuinely *is* free.

---

## Q4 — Minimum for BR2

**(a) A new status value is sufficient, and it is a two-line change.** `refinements.py:182-185` already carries a four-value vocabulary. Add `STATUS_TARGET_REFUTED` — the finding is correct and the target is wrong — and make sure it does not fall through to `unconfirmed_novel`. For BR2 you need the *state to exist and be recordable*, not adjudicated automatically. Human-in-the-loop assignment is fine and honest; the publishable claim is "the harness distinguishes a defect in the artefact from a defect in the specification", not "it decides which".

**(b) Cheaper than schema enforcement:** make the location key a **pair** — `(location, mechanism_hash)` — where mechanism_hash is a normalised hash of the FIND clause's mechanism phrase. That is a composite key change, not a schema regime. It closes the exact documented limitation at `:4331` (a second distinct defect in an already-flagged function) at roughly the cost of one function.

**Defer:** everything else. Merge-fold semantics (tracker 1.6), the discussion layer, model-derived theories. None of it is needed for BR2 to be publishable.

---

## Q5 — Is the budget sufficient? **No.** But it is close, and the gap is nameable.

Straight answer, since it was asked straight: **the current plan does not reach publication standard, and the shortfall is one specific thing.**

exp44–49 all converged while the similarity function flagged 97% of pairs. Those curves are curves of a suppressed process. exp50–52 will run un-suppressed. **You will therefore have no run of the fixed harness on a target the broken harness also ran.** Every comparison in the paper becomes across-target as well as across-harness, and a hostile reviewer will say — correctly — that you cannot separate the fix from the target. That is the demand the current plan does not meet, and it is the only one I would call fatal.

**Minimum sufficient design:**

1. Stage 1 replay of all six on repaired accounting. Free. This is the before/after that does not need new spend, and its exit test (reproduce the old series exactly) is the right one.
2. **One matched re-run.** CC1 picks exp46 on narrowest gamma margin. I disagree: pick **exp44**. It is the only run with 13 rounds (so `rho_earliest_round=12` can actually fire — tracker 1.8), the only run where counterfactual repair produced both labels, it carries the most findings, and it is the only Python run where the S\*/nu path has live data. exp46 has 6 rounds and decided 0 of 10 pairs; a re-run of it will not show you much. exp46's narrow margin is an argument for reporting it carefully, not for spending on it.
3. exp50 as the first clean run, with a pre-flight specifically for the never-executed NO_SCORE path.
4. The 4.1 generated control. Scripting cost only.

That is one live re-run more than CC1 proposes and one target different. Everything else in the arc stands.

What a hostile reviewer will still demand and you will not have: an independent ground truth for finding identity. You cannot buy that with the remaining budget. **Narrow the claim instead** — the tracker already has the right wording ("free-text similarity is not a reliable final identity decider on the hard cases") and it should go in the paper in exactly that form.

---

## Q6 — Loose ends not yet named

1. **NO_SCORE has never executed live.** exp50/51 are its first exercise. Pre-flight it.
2. **`priority_score` starvation** is a general defect, not an R_k one. Fix the near-duplicate rate and every other feedback class silently gets louder — including ones nobody has measured under an uncrowded prompt. Expect surprises in exp50 that are not regressions.
3. **exp45, exp46 and exp47 decided zero of 40 counterfactual pairs.** The pack presents the Python rate as 16.7%; it is 30% for exp44 and 0% for the other three. Something is different about those runs and it is unexplained. Free to investigate, and it may be the same defect as (2).
4. **Two ν's coexist.** Models state ν_eff (219 of 223 FAILs state it directly, ignoring the directive's request for ν_b and ν_f), and it is used for nothing but validation; the runner computes its own from constants. Before measuring nu, decide which one is canonical and delete the other, or you will be calibrating against a quantity the system does not use.
5. `bench/logs/immune_pipeline.log` is modified in the working tree and two untracked confer scripts are present. Housekeeping, but commit before exp50 so the run has a clean provenance hash.

---

## Strongest falsification of my own answer

**My central recommendation — fix the extractor and the label, then re-measure before enforcing — assumes the recovered 220 SKIPs will mostly land in PASS. They may land in FAIL.** Every sample I printed shows the divergent formula `R_old·(1−q)·S_k + ν`, and if that pattern holds across the recovered blocks, cleaning the extractor moves the FAIL rate from 31.7% to something near 60% and my "measure before you enforce" advice will have bought a worse number rather than a truer one. I would still take that trade — a true 60% is actionable and a muddled 31.7% is not — but the founder should expect the number to get *worse* before it gets better, and should not read that as a regression.

**And my sharpest finding is the thinnest.** The 18/0 markdown asymmetry rests on 18 observations. At a prose duplicate base rate of 0.9 it has p = 0.15, which is nothing. I have argued from it that prose counterfactual repair is degenerate, and I would be wrong if disputed prose pairs simply are overwhelmingly duplicates. The 4.1 control settles it and costs almost nothing — which is precisely why I am recommending it rather than recommending you act on my inference.

---


*5 of 5 panellists returned a usable response (counted by ok=true AND non-empty text, not by file presence).*

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).