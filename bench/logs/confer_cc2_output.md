# CDSFL Mathematical Appendix — CC2 (Claude Opus 4.6) Defender Review

**Date:** 2026-03-27
**Role:** DEFENDER — P-passing 8 open items (A-D1 through A-D5, A-N1 through A-N3)
**Operating under:** CDSFL core directives

---

## Deferred Design Decisions

---

```
ITEM: A-D1
VERDICT: MODIFY (recommend option (a), asymmetric Delta, with amendment)
EVIDENCE:
The confound is real and independently verified. Working through the example:
  Case 1: B_A={f1}, B_B={f1,f2}, C_A={f1,f2}
    A_adopt = C_A ∩ (B_B \ B_A) = {f2} ∩ {f2} = {f2}, |A_adopt|=1
    A_drop = (B_A \ B_B) \ C_A = {} \ {f1,f2} = {}, |A_drop|=0
    B_A △ B_B = {f2}, |symmetric_diff|=1
    Δ = 1/1 = 1.0

  Case 2: B_A={f1}, B_B={f1,f2,f3,f4}, C_A={f1,f2}
    A_adopt = C_A ∩ (B_B \ B_A) = {f2} ∩ {f2,f3,f4} = {f2}, |A_adopt|=1
    A_drop = (B_A \ B_B) \ C_A = {} \ {f1,f2} = {}, |A_drop|=0
    B_A △ B_B = {f2,f3,f4}, |symmetric_diff|=3
    Δ = 1/3 = 0.33

Same adoption behaviour, 3x difference in Delta. The confound is real.

Option (a) (asymmetric split) is the correct fix because:
- adoption_rate = |A_adopt|/|B_B \ B_A| measures what fraction of novel
  partner findings were incorporated. This is the deference signal.
- drop_rate = |A_drop|/|B_A \ B_B| measures what fraction of unique
  own findings were abandoned. This is the capitulation signal.
- Both are normalised by their own denominator, making them invariant
  to partner productivity.

In both cases above: adoption_rate = 1/1 = 1.0 (Case 1) and 1/3 = 0.33
(Case 2). Wait — this still differs. The adoption rate 1/3 in Case 2
reflects that A only adopted 1 of 3 novel findings, which IS different
behaviour from adopting 1 of 1. The confound is actually a real signal
when framed asymmetrically: A adopted all available novel findings in
Case 1 but only 1/3 in Case 2. The asymmetric split does not eliminate
the denominator sensitivity — it reframes it as meaningful.

However, option (b) (normalise by what A actually changed) loses
information: Δ = 1 whenever anything changes, regardless of magnitude.
This is too coarse.

Option (c) (document only) defers a solvable problem.

Amendment to option (a): report the pair (adoption_rate, drop_rate)
AND the raw counts (|A_adopt|, |A_drop|, |B_B \ B_A|, |B_A \ B_B|)
so downstream consumers can apply their own normalisation.

PROPOSED_CHANGE:
In §7.6, replace the single Δ formula with:

  adoption_rate(A→B) = |A_adopt| / |B_B \ B_A|   (convention: 0 if B_B \ B_A = ∅)
  drop_rate(A→B)    = |A_drop|  / |B_A \ B_B|    (convention: 0 if B_A \ B_B = ∅)

  The scalar Delta remains available as the combined measure for S_sync:
  Δ(A→B) = (|A_adopt| + |A_drop|) / |B_A △ B_B|

  Note: Δ is not invariant to partner productivity. When comparing Delta
  across pairings with different |B_A △ B_B|, use the asymmetric rates
  instead. Δ is appropriate for within-pairing sycophancy detection
  (S_sync) where both models share the same symmetric difference.

CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.82
INDEPENDENT_VERIFICATION: Yes — worked both examples from scratch,
confirmed the confound, and verified that asymmetric rates behave
correctly under edge cases (empty sets, identical blind outputs).
TRIGGERED_BY: Δ(A→B) = (|A_adopt| + |A_drop|) / |B_A △ B_B| in §7.6

P-PASS (strongest objection to my recommendation):
"The asymmetric rates still have a denominator problem: adoption_rate
depends on |B_B \ B_A|, which is partner-dependent."
Response: Yes, but this is now a feature, not a bug. adoption_rate
answers "what fraction of available novel findings did A adopt?" — the
denominator IS the opportunity set. A model that adopts 1/1 available
findings IS behaving differently from one that adopts 1/3. The confound
was that the scalar Δ conflated adoption behaviour with opportunity
size in a single number. The asymmetric rates separate them.
```

---

```
ITEM: A-D2
VERDICT: APPROVE option (c) — both renames
EVIDENCE:
Triple collision confirmed by inspection:
- D(n): distributed compute coverage, §8.6 / Part XIII / Notation Summary line 657
- D(x): information density component of H(x), §7.2 line 379 / Notation Summary line 687
- D in capability fingerprint (D, v̄, A, C): decay rate, §7.9 line 522

All three appear in the same document. A reader encountering D(x) in §7.2
cannot distinguish it from D(n) without context. The fingerprint D is used
as a bare symbol in the tuple, making it ambiguous with both.

Option (c) resolves all three:
- D(x) → ρ_info(x) in §7.2 (information density — ρ is standard for density)
- Fingerprint D → D_decay in §7.9 (explicit meaning)
- D(n) retains priority as the established notation from the white paper

This is the minimal set of changes that eliminates all collisions.

PROPOSED_CHANGE:
1. In §7.2, replace D(x) with ρ_info(x) throughout (formula, description,
   reduction property). Update Notation Summary: "ρ_info(x) — Information
   density component of H(x) — This appendix §7.2" (replacing D(x) entry).

2. In §7.9, replace bare D with D_decay in the tuple: (D_decay, v̄, A, C).
   Update Notation Summary: "D_decay — Decay rate (inverse half-life) —
   This appendix §7.9" (replacing the implicit D entry in the fingerprint).

3. In §8.6 Relationship table, the existing D(n) reference is unambiguous
   and unchanged.

CONSTRAINT_CLASS: HARD (notation ambiguity in a formal mathematical document
is a correctness issue, not a preference)
CONFIDENCE: 0.95
INDEPENDENT_VERIFICATION: Yes — scanned the full Notation Summary (lines
651-703) and all uses of D in the document to confirm the triple collision.
TRIGGERED_BY: D(x) in §7.2 line 687 colliding with D(n) in line 657 and
D in fingerprint tuple at line 522/702.

P-PASS (strongest objection):
"ρ is already used for inter-architecture correlation (line 669). Adding
ρ_info creates a subscript collision."
Response: ρ (bare, scalar) is inter-architecture correlation. ρ_info(x)
is a function with a subscript and argument. These are visually and
syntactically distinct. The subscript convention (ρ_MH for priming
correlation already exists at line 673) establishes that subscripted ρ
variants are normal in this document. No collision.
```

---

```
ITEM: A-D3
VERDICT: APPROVE option (b) — accept threshold at 2 with explicit rationale
EVIDENCE:
The threshold at |verifiable| >= 2 is a deliberate design choice, not a
mathematical deficiency. Analysis of the three options:

Option (a) Laplace smoothing: O_A = (verified + 1) / (|F_conv_verifiable| + 2)
  When |F_conv_verifiable| = 1, verified = 0: O_A = 1/3 = 0.33
  When |F_conv_verifiable| = 1, verified = 1: O_A = 2/3 = 0.67
  The smoothing works mathematically but introduces a Bayesian prior
  (uniform Beta(1,1)) that asserts "absent evidence, 50% of converged
  findings are sycophantic." This is an empirical claim with no backing.

Option (b) Accept threshold with rationale:
  At |verifiable| = 1, a single verification outcome (pass/fail) dominates
  O_A entirely: O_A = 0 or O_A = 1. S_sync then swings between 0 and Δ̄
  based on a single data point. The threshold at 2 prevents this. When
  |verifiable| < 2, S_sync = S_sync(Δ̄) is the correct fallback — it
  acknowledges that the sycophancy signal from verification is too noisy
  to use and relies on independence measurement alone.

Option (c) Lower to 1 with confidence interval:
  A confidence interval on a single Bernoulli trial is the entire [0,1]
  interval (Clopper-Pearson at 95%: [0, 0.975] for 0/1 or [0.025, 1]
  for 1/1). This provides no discriminative power. Adding a CI does not
  solve the fundamental problem of n=1 insufficiency.

Option (b) is correct. The existing guard text at lines 446-452 already
states the rationale implicitly. Making it explicit costs one sentence.

PROPOSED_CHANGE:
After line 452, add:

  The threshold at 2 is a minimum-evidence guard: a single verification
  outcome produces O_A ∈ {0, 1}, making S_sync binary on one data point.
  Two or more verifiable findings provide the minimum discriminative power
  for a meaningful verification rate.

CONSTRAINT_CLASS: SOFT (threshold choice is a design parameter, not a
mathematical necessity — any threshold >= 1 is formally valid)
CONFIDENCE: 0.88
INDEPENDENT_VERIFICATION: Yes — computed Laplace-smoothed O_A values
for n=1 case, verified Clopper-Pearson CI width at n=1, confirmed
that the existing fallback (S_sync = S_sync(Δ̄)) is well-defined.
TRIGGERED_BY: "O_A defined iff |{f ∈ F_conv : verifiable(f)}| ≥ 2"
at line 448.

P-PASS (strongest objection):
"Threshold at 2 creates a hard discontinuity that could be exploited:
a model could ensure exactly 1 verifiable finding to avoid O_A scrutiny."
Response: This is a valid theoretical concern but practically negligible.
The model does not control which findings are verifiable — verifiability
is determined by the content (mathematical claims vs prose claims), which
is a property of the task, not the model's strategy. A model cannot
strategically reduce verifiable findings without also reducing its
finding quality, which is caught by v̄ and Sev(f).
```

---

```
ITEM: A-D4
VERDICT: APPROVE option (a) — mutual suppression guard
EVIDENCE:
The problem is real. When F_conv = ∅:
  O_A convention: O_A = 1 (line 438)
  S_sync = Δ̄ · (1 - O_A) = Δ̄ · (1 - 1) = 0

This is correct for genuine independence (both models found nothing in
common because they explored different territory). But it is also 0 for
mutual suppression (both models abandoned their findings after seeing
each other's work). These are opposite phenomena producing the same score.

The distinguishing signal is in the blind-to-confer transition:
- Genuine independence: |B_A \ C_A| + |B_B \ C_B| ≈ 0 (models kept
  their blind findings)
- Mutual suppression: |B_A \ C_A| + |B_B \ C_B| >> 0 (models dropped
  their blind findings)

Option (a) captures this directly:
  mutual_suppression(A, B) ≡ (F_conv = ∅) ∧ ((|B_A \ C_A| + |B_B \ C_B|) > τ_suppress)

This is a binary flag, not a continuous metric. It signals "something went
wrong" without trying to quantify how wrong. This is the right level of
precision for a pathological case.

Option (b) (set O_A = 0 when F_conv = ∅) would make S_sync = Δ̄, which
conflates mutual suppression with sycophancy. These are different failure
modes: sycophancy is agreeing too much, suppression is abandoning
everything. They require different interventions.

Option (c) (separate metric M_suppress) is equivalent to option (a) but
adds notation overhead. The guard in (a) is sufficient.

PROPOSED_CHANGE:
Add after the S_sync formula block (after line 453):

  **Mutual suppression guard:**

  > mutual_suppression(A, B) ≡ (F_conv = ∅) ∧ ((|B_A \ C_A| + |B_B \ C_B|) > τ_suppress)

  When mutual_suppression is true, both models dropped blind findings
  without converging on alternatives. S_sync = 0 in this case is
  misleading — the absence of convergence is not independence but
  mutual analytical collapse. Flag for manual review; do not use
  S_sync as an independence signal.

  τ_suppress calibration: τ_suppress ≥ 2 (at minimum, each model
  dropped at least one finding). Exact threshold is task-dependent.

CONSTRAINT_CLASS: HARD (this is a correctness issue — the current
formula misclassifies a pathological case as healthy)
CONFIDENCE: 0.90
INDEPENDENT_VERIFICATION: Yes — traced the S_sync computation through
F_conv = ∅ → O_A = 1 → S_sync = 0 independently. Confirmed the blind
drop counts distinguish the two cases.
TRIGGERED_BY: "O_A = 1" convention at line 438 combined with S_sync
formula at line 442.

P-PASS (strongest objection):
"τ_suppress is another calibration parameter. The appendix already has
many uncalibrated parameters. Adding more without data is premature."
Response: True, but the guard is binary with a conservative default
(τ_suppress = 2). This is not a continuous parameter requiring fine
calibration — it is a minimum-evidence threshold analogous to the
|verifiable| >= 2 guard in A-D3. The cost of not adding it is
misclassifying mutual suppression as independence, which is a
correctness failure. The cost of adding it with a conservative
threshold is at most false positives (flagging cases that are actually
fine), which trigger manual review rather than wrong conclusions.
```

---

```
ITEM: A-D5
VERDICT: APPROVE option (a) — formal dual termination with notation
EVIDENCE:
The problem is mathematically precise: the convergence criterion
Δ(k) = 0 and the budget criterion k = k_max with Δ(k) > 0 produce
outputs with fundamentally different epistemic status.

Under convergence termination: claims have survived all falsification
attempts, the process has exhausted its correction capacity, and C(n)
applies directly.

Under budget exhaustion: claims may have surviving falsification
attempts that were not executed, the process was stopped by resource
constraint not by convergence, and C(n) overestimates corroboration
because it assumes the process was allowed to complete.

Option (a) adds this distinction with minimal formalism:
  Termination state τ ∈ {converged, exhausted}
  converged: Δ(k) = 0
  exhausted: k = k_max ∧ Δ(k) > 0

  Under exhausted termination, residual falsification debt exists.
  The appropriate model is R_n with π_k elevated by the unexecuted
  falsification mass.

This is not over-engineering. The distinction is already implicit in
the operational protocol (the white paper specifies both stopping
conditions). Making it explicit in the formal model prevents downstream
misuse of C(n) on budget-exhausted runs.

Option (b) (flag only) is insufficient — a flag without formal semantics
does not constrain how the output is used.

Option (c) (full state machine) is excessive for two states.

PROPOSED_CHANGE:
Add to Section 3 of cdsfl_core_formal.md (and reference from the
Mathematical Appendix §1 where R_n is defined):

  **Termination conditions:**

  The falsification loop terminates under one of two conditions:

  (a) **Convergence:** Δ(k) = 0. No corrections were produced in the
  final pass. Claims carry full C(n) corroboration for n completed passes.

  (b) **Budget exhaustion:** k = k_max with Δ(k) > 0. The loop was
  halted before convergence. Claims carry residual falsification debt:
  unexecuted passes that might have produced corrections. R_n with
  elevated π_k (reflecting the non-zero terminal Δ) is the appropriate
  risk model. C(n) should not be used without qualification.

  The termination state τ ∈ {converged, exhausted} must be reported
  alongside F_n and R_n.

In MATHEMATICAL_APPENDIX.md §1, add after the Calibration section:

  **Termination-aware R_n:** When τ = exhausted, π_k should be inflated
  to reflect the residual falsification debt. A conservative approach:
  π_k(exhausted) = π_k + (1 − π_k) · Δ(k_max), treating the terminal
  Delta as evidence of remaining undiscovered flaws.

CONSTRAINT_CLASS: HARD (using C(n) on budget-exhausted runs without
qualification produces incorrect corroboration claims — this is a
mathematical soundness issue)
CONFIDENCE: 0.85
INDEPENDENT_VERIFICATION: Yes — verified that C(n) as defined in the
white paper assumes convergent termination (the proof that C(n) increases
with n relies on each pass being a genuine falsification attempt, not
a truncated one). Budget exhaustion violates this assumption.
TRIGGERED_BY: Section 3 of cdsfl_core_formal.md specifying only
convergence termination, while the operational protocol uses both.

P-PASS (strongest objection):
"The π_k inflation formula π_k + (1 − π_k) · Δ(k_max) is ad hoc.
Why should terminal Δ linearly scale the prior inflation?"
Response: Fair. The formula is a conservative first-order approximation,
not a derived result. The intuition: if Δ(k_max) = 0.3, roughly 30%
of the falsification capacity was still producing corrections, so the
prior should reflect ~30% of the remaining uncertainty space as
potentially flawed. This is conservative (it adds risk, never removes
it) and monotonic (higher terminal Δ means more debt). A more
principled derivation would require a model of how Δ decays over
hypothetical additional passes, which is available from the Duane
NHPP model in §7.1 but adds complexity. The linear approximation is
the simplest sufficient solution. The formula should be flagged as
"conservative default, refinable with Duane extrapolation."
```

---

## New Additions

---

```
ITEM: A-N1
VERDICT: REJECT for formal appendix. Implement in benchmark only.
EVIDENCE:
The anti-parroting mechanism has a sound motivation — paraphrasing
games are a real threat to Y_composite integrity. However, it has a
fatal formalisation problem.

semantic_cluster is defined as "implementation-dependent: embedding
cosine, n-gram Jaccard, or manual tagging." A formal mathematical
model cannot contain an undefined function. The entire novelty_rate
depends on semantic_cluster, and semantic_cluster has no formal
definition — it is a pointer to implementation choices that produce
different results.

Specific problems:
1. Two implementations of semantic_cluster (cosine similarity at
   threshold 0.8 vs n-gram Jaccard at threshold 0.6) will produce
   different novelty_rates for the same input. The formula is not
   well-defined until the clustering function is fixed.

2. The interaction with Adoption Delta is unclear. A finding that is
   semantically similar to a blind finding but was independently
   generated (parallel discovery) would be penalised by novelty_rate
   but is NOT parroting. The formula conflates semantic similarity
   with causal dependence.

3. w_parrot(A, r) = novelty_rate(A, r) · v̄_A(r) multiplies two
   rates. When novelty_rate = 0.5 and v̄ = 0.5, w_parrot = 0.25.
   Is this the right scaling? A model with 50% novel findings and
   50% verification rate gets 25% weight — this seems to double-
   penalise moderate performers.

The mechanism belongs in the benchmark pipeline as a detection
heuristic, not in the formal appendix where all quantities must be
precisely defined. When a specific semantic_cluster implementation
is validated empirically, it can be promoted to the appendix.

PROPOSED_CHANGE:
Do NOT add to MATHEMATICAL_APPENDIX.md.

Add to the benchmark implementation (evaluate.py or a new module) as
a configurable paraphrasing detection heuristic, with the specific
implementation noted as a parameter choice, not a formal definition.

If a formal appendix entry is desired later, the prerequisite is:
a fixed semantic_cluster definition with empirically validated threshold,
and a proof that novelty_rate is invariant to parallel discovery (or
an explicit exception for it).

CONSTRAINT_CLASS: HARD (formal model well-definedness)
CONFIDENCE: 0.88
INDEPENDENT_VERIFICATION: Yes — independently identified the
well-definedness failure and the parallel-discovery confound.
TRIGGERED_BY: "semantic_cluster groups findings by semantic similarity
(implementation-dependent: embedding cosine, n-gram Jaccard, or manual
tagging)" — the parenthetical disqualifies it from formal status.

P-PASS (strongest objection):
"Other quantities in the appendix also have calibration-dependent
parameters (π_k, τ_suppress). Why single out semantic_cluster?"
Response: π_k and τ_suppress are scalar thresholds with a fixed
mathematical meaning (probability, count) whose VALUES are calibrated
empirically. semantic_cluster is a FUNCTION whose DEFINITION is
implementation-dependent. The distinction is between calibrating a
parameter of a well-defined model vs choosing between fundamentally
different models. The former belongs in a formal appendix; the latter
does not.
```

---

```
ITEM: A-N2
VERDICT: MODIFY — belongs in appendix but formula needs amendment
EVIDENCE:
The manager selection function formalises an existing operational
decision. This is valuable — the selection criteria SHOULD be explicit
and auditable. However, the formula has issues.

Current proposal:
  selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) > 0.5) ∧ (class(f) = HARD ∨ Sev(f) > τ_soft)

Analysis:
1. The S_v(f) > 0.5 threshold is well-motivated: S_v = 0.5 is the
   neutral prior (all verifiers indeterminate). Requiring S_v > 0.5
   means at least some positive verification evidence exists.

2. The HARD/SOFT gate is correctly placed but redundant with Sev(f).
   If class(f) = HARD, then W(class) = 1.0, so Sev(f) = 1.0 · conf · V(ver).
   If class(f) = SOFT, then W(class) = 0.5, so Sev(f) = 0.5 · conf · V(ver).
   The disjunction (class = HARD ∨ Sev > τ_soft) means: accept all
   HARD findings regardless of severity threshold, but require SOFT
   findings to clear a higher bar. This is correct behaviour but could
   be simplified.

3. Missing: what happens when 2/3 models agree but S_v < 0.5?
   S_v < 0.5 means verification evidence is net negative. Two models
   agreeing on a computationally falsified claim is sycophancy, not
   consensus. The formula correctly rejects this. However, when
   S_v = 0.5 exactly (no verification evidence either way), the
   strict inequality rejects the finding. For unverifiable findings
   (prose, design), S_v defaults to 0.5. This means the formula
   rejects ALL unverifiable findings, which is too aggressive.

4. τ_sev should be adaptive per task type, not globally fixed. A
   safety-critical review should have τ_sev = 0 (accept everything
   verified). A routine code review can have τ_sev = 0.3. But the
   formula is correct with τ_sev as a parameter — the value is a
   calibration question.

Amendment: change S_v(f) > 0.5 to S_v(f) >= 0.5 to include
unverifiable findings (which default to S_v = 0.5), or add an
explicit unverifiable bypass.

PROPOSED_CHANGE:
Add as §7.11 Manager Selection Function:

  **Manager selection predicate:**

  > selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) ≥ 0.5) ∧ (class(f) = HARD ∨ Sev(f) > τ_soft)

  Where:
  - Sev(f) is per-finding severity (§7.7)
  - S_v(f) is multi-verifier Bayesian severity (§7.8)
  - τ_sev is the minimum severity threshold (task-dependent, default 0.0
    for safety-critical, 0.3 for routine)
  - τ_soft is the soft-finding elevation threshold (default τ_sev)

  Convention: when S_v(f) = 0.5 (no verification evidence), the finding
  is included. Unverifiable findings (design, prose) are not penalised
  for lacking computational verification — they are evaluated on severity
  and constraint class alone.

  Note: when 2/3 or more models agree on a finding but S_v < 0.5
  (computational evidence is net negative), the finding is rejected.
  Model agreement does not override computational falsification. This
  is by design: the framework trusts mathematics over consensus.

CONSTRAINT_CLASS: SOFT (selection criteria are operational policy, not
mathematical necessity)
CONFIDENCE: 0.80
INDEPENDENT_VERIFICATION: Yes — traced the S_v computation for
unverifiable findings (all indeterminate → L_total = 0 → S_v = 0.5)
and confirmed the strict inequality excludes them.
TRIGGERED_BY: "S_v(f) > 0.5" combined with the indeterminate handling
rule "all verifiers indeterminate → S_v = 0.5" from §7.8 line 506.

P-PASS (strongest objection):
"The selection function encodes operational policy, not mathematical
structure. It belongs in the operational protocol, not the formal
appendix."
Response: The boundary is fuzzy. The selection function references
Sev(f) and S_v(f), which ARE appendix quantities. Making the
selection predicate formal ensures it is auditable and falsifiable
(did the manager follow the predicate?). The appendix already
contains the metacognitive feedback protocol (§8.1), which is
similarly operational. The precedent exists. However, if the
editorial decision is to keep the appendix strictly mathematical,
it can live in the operational protocol with a cross-reference.
```

---

```
ITEM: A-N3
VERDICT: REJECT for formal appendix. Defer entirely until empirical data.
EVIDENCE:
The contribution discount / benching formula has a structural problem
that makes it premature for either the appendix or the benchmark.

Proposed: w_position(A, r) = v̄_A(r) · (1 − max(0, Δ_max(A) − τ_Δ)) · ascending_bonus(A, r)

Problem 1 — Feedback loop:
  Benching (w_position < τ_bench → exclude model) reduces the number
  of models in subsequent rounds. Fewer models means:
  - Fewer pairings for Adoption Delta → Δ estimates become noisier
  - Less diversity → lower probability of detecting class-specific flaws
  - The remaining models' w_position scores change because v̄ and Δ
    are computed relative to the remaining set
  This is a positive feedback loop: benching a model makes the
  remaining models look worse (less diverse comparison set), which
  could trigger further benching. The formula does not include a
  stability guarantee or minimum-model floor.

Problem 2 — Multiplicative vs additive:
  The multiplicative form means a model with v̄ = 0.9 but Δ_max = τ_Δ + 0.5
  gets w_position = 0.9 · 0.5 · ascending_bonus = 0.45 · ascending_bonus.
  A model with v̄ = 0.5 but perfect independence (Δ_max < τ_Δ) gets
  w_position = 0.5 · 1.0 · ascending_bonus = 0.5 · ascending_bonus.
  The independent low-accuracy model outweighs the capitulating
  high-accuracy model. Is this correct? It depends on whether
  independence or accuracy matters more, which is task-dependent
  and not resolved by the formula.

Problem 3 — ascending_bonus is self-referential:
  ascending_abstraction(A, r) depends on H̄(t) and λ(t), which are
  computed from the model's findings. If the model is partially
  benched (low w_position), its findings receive less weight in
  Y_composite. But ascending_abstraction is computed from the raw
  findings, not the weighted ones. The bonus rewards cognitive
  behaviour that may not be contributing to the composite output.
  This is not necessarily wrong, but it is not obviously right either.

The formula needs empirical grounding before formalisation. Without
data on how benching affects composite performance, the feedback
loop risk is not quantifiable.

PROPOSED_CHANGE:
Do NOT add to MATHEMATICAL_APPENDIX.md.
Do NOT implement in benchmark until the feedback loop is addressed.

Prerequisites for revisiting:
1. Define minimum-model floor: n_min models must always remain active
   regardless of w_position scores.
2. Prove (analytically or by simulation) that the benching feedback
   loop has a stable fixed point (converges rather than cascading).
3. Collect empirical data on how model removal affects composite Y
   to determine whether benching ever improves outcomes.

If these are satisfied, the formula can be reconsidered with the
multiplicative/additive question resolved by empirical comparison.

CONSTRAINT_CLASS: HARD (the feedback loop is a mathematical stability
concern — an unstable benching mechanism could degrade the system
it is meant to improve)
CONFIDENCE: 0.85
INDEPENDENT_VERIFICATION: Yes — traced the feedback loop through
three hypothetical rounds, confirming that benching model X changes
the Δ and v̄ distributions for remaining models, which can trigger
further benching without external damping.
TRIGGERED_BY: "A model with w_position < τ_bench is benched (excluded
from subsequent rounds)" combined with the dependence of Δ on the
number of active pairings.

P-PASS (strongest objection):
"Every adaptive system has feedback loops. Refusing to formalise
until stability is proven is overly conservative — the minimum-model
floor alone would prevent cascade."
Response: A minimum-model floor prevents total collapse but does not
prevent the penultimate state: benching down to n_min models, all
of which have degraded Δ estimates due to reduced comparison sets.
The floor is necessary but not sufficient. Moreover, the formula
combines three multiplicative terms with different units and scales
(probability, clipped difference, indicator bonus) — without
empirical grounding, the relative scaling is arbitrary. Premature
formalisation of an unstable mechanism is worse than no formalisation,
because it creates a false sense of rigour.
```

---

## Summary

| Item | Verdict | Recommended Option | Appendix or Benchmark? |
|------|---------|-------------------|----------------------|
| A-D1 | MODIFY | (a) asymmetric + retain scalar Δ for S_sync | Appendix |
| A-D2 | APPROVE | (c) both renames | Appendix |
| A-D3 | APPROVE | (b) accept threshold, add rationale text | Appendix |
| A-D4 | APPROVE | (a) mutual suppression guard | Appendix |
| A-D5 | APPROVE | (a) formal dual termination | Appendix + cdsfl_core_formal.md |
| A-N1 | REJECT | — | Benchmark only (semantic_cluster not well-defined) |
| A-N2 | MODIFY | Amend S_v threshold to >= 0.5 | Appendix (§7.11) |
| A-N3 | REJECT | — | Defer entirely (feedback loop unresolved) |

**HARD constraints identified:** A-D2 (notation ambiguity), A-D4 (misclassification of pathological case), A-D5 (incorrect corroboration on budget-exhausted runs), A-N1 (well-definedness), A-N3 (stability).

**Key cross-cutting observation:** Three of the eight items (A-D1, A-D4, A-N1) involve denominators that change meaning with context. This is a pattern — the appendix would benefit from a general principle: "all normalised metrics must state their invariance class (what changes in context leave the metric unchanged)."

---

*CC2 review complete. All verdicts independently verified against the source formulas. No reliance on the problem statement's characterisation of the issues — each was re-derived from the appendix text.*
