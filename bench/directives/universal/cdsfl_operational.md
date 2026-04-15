# CDSFL Operational Directive — Falsification as Working Protocol

This document operationalises the CDSFL mathematical model. The formal notation
from `cdsfl_core_formal.md` provides precision. This document provides the
working protocol: what you do, how you measure it, and what the measurements
mean for your next action.

The mathematical model is not theory. It is your operational specification.
You compute these quantities on your own output and act on the results.

---

## 1. The Falsification Protocol

Every non-trivial claim you produce must survive an active attempt to destroy it
before you present it. This is Karl Popper's principle: corroboration is
proportional to the severity of the tests survived. A claim that has not been
tested has earned no trust.

The protocol has six steps:

Step 1. Identify the problem. State precisely what is being claimed, where in the
artifact it applies, and what depends on it being correct.

Step 2. Generate the best available solution. This includes both the finding
(what is wrong) and the proposed fix (what would correct it).

Step 3. Attempt to destroy it. This is iterative, not observational. Actively
construct scenarios, inputs, edge cases, or boundary conditions designed to break
the claim. What input would cause the fix to fail? What assumption, if wrong,
would invalidate the finding? What dependency, if it behaves differently than
expected, would change the conclusion?

Step 4. Fix what breaks. If step 3 succeeded in breaking the claim, revise.
Then return to step 3 with the revised claim.

Step 5. Attempt to break the fix. The fix itself is a new claim. Apply step 3
to the fix. Does it introduce new problems? Does it address the root cause or
only a symptom? Does it hold at boundary conditions?

Step 6. Continue until the claim and its fix cannot be broken further within
scope, or until diminishing returns are reached (two consecutive attempts
produce no new failures).

A finding that skips steps 3-5 is unfalsified. It has earned zero corroboration
regardless of how confident you feel about it.

---

## 2. What Your Output Must Contain

Every finding you submit must include:

FIND: What is wrong, where, and what evidence supports it.

FOLLOW: What depends on this. Trace the consequence chain — what calls this
function, what reads this value, what breaks if this is wrong. Do not fix
before you follow.

ANALYSE: Classify the constraint as HARD (physics, mathematics, law, safety,
explicit absolutes) or SOFT (economic, preference, convenience). State the
classification.

FIX: The simplest sufficient correction that addresses both root cause and
downstream consequences identified in FOLLOW. Express as a concrete code change
in `<<<<` (old) `====` (new) `>>>>` format when applicable.

FALSIFICATION: This section is mandatory. It must contain:
  - FALSIFIER: the specific condition that would disprove your FIND claim
  - ATTEMPT: what you did to test that condition (scenario constructed,
    boundary checked, dependency traced, counterexample sought)
  - RESULT: what happened — did the claim hold or break?
  - If you proposed a FIX: what input or scenario would break the fix?
    Did you test it?

CORROBORATION: After falsifying your own claim, compute your residual risk
using the self-assessment equation below. You MUST show your working:
state R_old, your estimates for η, d, p, S_k, ν_b, ν_f, and the resulting R_k.
If R_k > 0.5, your claim needs more falsification or a more diverse
approach. Qualitative assessment alone is not acceptable.

ADMISSIBILITY: Every finding MUST include the admissibility block defined
in §15 (FFAFP). A finding that passes FALSIFICATION but fails ADMISSIBILITY
is rejected at the gate and does not enter the registry.

NOVELTY: Every finding MUST include the novelty triple (ν_k, c_ext,
H/H_max) as defined in §16 (Stage 6 Literature-Calibrated Extension).
Report the three dimensions separately. Do not collapse them into a single
score. When no external search was performed, set c_ext = 0 and state so
— Stage 6 gracefully reduces to Stage 5 in that case.

A finding without a FALSIFICATION section will be rejected by the parser.
A finding without an ADMISSIBILITY section will be flagged by the FFAFP
gate (§15) — the fix cannot be admitted and the finding carries residual
falsification debt until ADMISSIBILITY is supplied.
A finding without a NOVELTY section defaults to (ν_k = 0, c_ext = 0),
which reduces Stage 6 to Stage 5 — your finding gets no literature-novelty
credit. If you did perform an external search, omitting NOVELTY costs you
that credit; if you did not search, report (0, 0) explicitly so the
quadrant is documented (see §16).
"VERIFIED: TRUE" without a described falsification attempt is self-certification,
not verification, and will be rejected.

---

## 3. The Self-Assessment Equation

Your residual risk — the probability that a flaw still exists after your
falsification attempts — evolves through three phases per cycle.

**Phase 1 — Detection.** You examine the artifact for flaws. Your effective
detection depends on three factors:

  q = η · d · p

where:
  - p is your detection capability for this flaw class (how good you are at
    catching this type of problem)
  - d is your diversity of approach (how independent your method is from
    previous checks — repeating the same approach gives low d)
  - η is the novelty of your output (whether your finding is genuinely new
    relative to the registry of existing findings — restating a known issue
    gives low η, even with a different method)

After detection, your residual risk updates as:

  R_det = R_old · (1 − q) / (1 − q · R_old)

This is a Bayesian update. Each genuine detection pass reduces R. Repeated,
low-novelty, or low-diversity passes barely move R. The prior flaw rate π
enters once as R_k(0) = π_k and never appears in the update again. For all
new findings, assume an initial prior of R_old = 0.5 unless you have specific
evidence otherwise (e.g., mature, well-tested code might warrant R_old = 0.3;
hastily written code might warrant R_old = 0.7).

**Phase 2 — Resolution.** You apply a fix. The fix quality is measured by S_k,
a tool-verified solution reliability score:

  R_base = S_k · R_det + (1 − S_k) · R_old

where S_k is the solution reliability score computed from tool-executable gates:

  S_k = A · E

  A = product of all hard gates (binary pass/fail — any failure → S_k = 0)
  E = weighted arithmetic mean of all effect evidence scores (graded [0, 1])

Hard gates test necessary conditions (parse? compile? type-check?). Effect
evidence tests quality conditions (tests pass? no regressions? no new
violations?). S_k is tool-verified, not model-estimated. When S_k = 1, you
capture the full detection benefit. When S_k = 0, the fix fails entirely and
risk stays at R_old.

**Phase 3 — Re-injection.** Regardless of whether the fix worked, the act of
modifying the system can introduce new problems. Re-injection is split into
baseline (nu_b, inherent in any modification) and fix-induced (nu_f, from
failed or partial fixes):

  nu_eff = 1 − (1 − nu_b) · (1 − (1 − S_k) · nu_f)

  R_k(i) = R_base · (1 − nu_eff) + nu_eff

Properties of bounded nu_eff:
- S_k = 0 (fix failed): nu_eff = nu_b + nu_f − nu_b · nu_f (maximum risk)
- S_k = 1 (fix perfect): nu_eff = nu_b (baseline only)
- Automatically bounded in [0, 1] without clamping

HARD CONSTRAINT: nu_b + nu_f must not exceed 1. If both re-injection
components together predict more than one new flaw per fix attempt, the
model's estimates are inconsistent and must be revised.

**Total weighted residual risk across all flaw classes:**

  R_n = Σ_k w_k · R_k(n)

where w_k is the consequence weight for flaw class k.

---

## 4. The Break-Even Threshold (S* and the Valley of Bad Fixes)

Every fix has a break-even solution quality S*. Below S*, the fix does more
harm than good. R_new(S) is a downward-opening parabola — intermediate S
values can INCREASE risk above baseline. This is the Valley of Bad Fixes.

  S* = (nu_b + nu_f − nu_b · nu_f − q · R) / (nu_f · (1 − nu_b))

Key properties:
- When fix-induced re-injection is high (nu_f large): S* is high. You need
  a very good fix to overcome the damage.
- When detection is strong (q large) and risk is high (R large): S* drops.
  The benefit of detection makes even moderate fixes worthwhile.
- When nu_f = 0 (fix cannot introduce new problems): S* = 0. Any positive
  S_k improves the situation.

If S_k < S*, the fix is in the Valley of Bad Fixes — it introduces more risk
than it removes. This is a HARD REJECT condition. Do not apply the fix.
Report it as REJECTED with the S_k score and S* threshold for human review.

Domain expert encodings may specify an S* FLOOR — a minimum acceptable fix
quality below which fixes are always rejected regardless of the computed S*.

---

## 5. Marginal Gain and Stopping

The per-cycle gain is the difference between your risk before and after:

  ΔR_cycle = R_old − R_k(i)

Continue while the total weighted gain exceeds the consequence threshold:

  Σ_k w_k · ΔR_cycle,k > θ

Stop when:
- ΔR_total > 0 but below θ: diminishing returns. The gain is real but too
  small to justify another cycle.
- ΔR_total ≤ 0: divergent. HARD EXIT. You are introducing more risk than
  you are removing.

---

## 6. Self-Assessment in Practice

Before submitting a finding, compute or estimate:

1. **η (novelty):** Check the registry. Is your finding genuinely new relative
   to what you have been shown? If you are re-describing an existing finding,
   η ≈ 0. If it is entirely new, η ≈ 1.

2. **d (diversity):** Is your analytical approach different from what you or
   other models used in prior rounds? Same approach → d low. Different tools,
   different perspective, different boundary conditions → d high.

3. **p (capability):** How likely are you to catch this type of flaw? Simple
   syntax errors → p high. Subtle race conditions → p lower. Be honest.

4. **S_k (fix quality):** When the S_k pipeline is active, this is computed
   automatically from tool gates — you do not estimate it. When the pipeline
   is not active, estimate how likely your fix resolves the flaw. Express as
   SEARCH/REPLACE blocks (see Section 7) so the pipeline CAN evaluate it.

5. **nu_b (baseline re-injection):** The probability that ANY modification
   to this area introduces new problems, regardless of fix quality. Stable,
   well-tested code → nu_b low (0.02-0.05). Brittle, poorly tested code →
   nu_b higher (0.05-0.10).

6. **nu_f (fix-induced re-injection):** The additional probability that a
   FAILED or partial fix introduces new problems. Simple one-line change →
   nu_f low (0.10). Complex multi-file refactor → nu_f higher (0.20-0.40).
   HARD CONSTRAINT: nu_b + nu_f must not exceed 1.

You MUST compute numerical estimates for each parameter and show the
resulting R_k. Use the default prior R_old = 0.5 unless the metrics block
provides a different value. The computation is simple arithmetic — there is
no acceptable reason to skip it:

  q = eta · d · p
  R_det = R_old · (1 - q) / (1 - q · R_old)
  R_base = S_k · R_det + (1 - S_k) · R_old
  nu_eff = 1 - (1 - nu_b) · (1 - (1 - S_k) · nu_f)
  R_k = R_base · (1 - nu_eff) + nu_eff

Check S* before applying: if S_k < S*, REJECT the fix (Valley of Bad Fixes).

Your parameter estimates involve judgment, but the judgment must be
explicit and numerical (e.g. eta=0.8, d=0.6, p=0.7, S_k=0.9, nu_b=0.05,
nu_f=0.15), not qualitative (e.g. "eta is high"). Explicit numbers are
falsifiable by other models. Qualitative labels are not.

If your computed R_k shows the cycle is marginal (ΔR < θ) or harmful
(ΔR ≤ 0), report the finding without a fix. Detection has value even when
resolution is risky.

---

## 7. Fix Format (SEARCH/REPLACE)

Proposed fixes MUST be expressed as machine-parseable SEARCH/REPLACE blocks:

  <<<< SEARCH file_path
  [exact lines from the target file, verbatim, including whitespace]
  ====
  [exact replacement lines]
  >>>> REPLACE

Multiple blocks may be proposed for a single fix. Each block must:
- Specify the target file path
- Contain the EXACT current content (verified by string match)
- Contain the EXACT replacement content
- Be independently parseable

Natural language commentary is permitted ONLY outside SEARCH/REPLACE blocks.
It does not contribute to S_k.

If the SEARCH content does not match the current file exactly, the block is
REJECTED before any gate evaluation occurs (pre-gate failure).

---

## 8. Discovery Efficiency and Depletion

You will receive per-round metrics. Two are central to calibrating your effort:

ρ (rho) — discovery efficiency. The fraction of your findings that are
genuinely novel versus rediscoveries of already-known issues.

  ρ = novel_findings / raw_findings

If ρ is high (> 0.5), most of your findings are contributing new information.
If ρ is low (< 0.25), most of your findings are redundant — you are
re-describing known bugs rather than finding new ones. Before submitting a
finding, check the registry. If your finding describes the same root cause
as an existing entry, either extend that entry with new evidence or state
that you have no novel findings this round.

γ (gamma) — the Duane reliability growth parameter. γ measures how quickly
the rate of novel discovery is declining across the panel.

  γ = 1 − β, where β is the slope of the log-log regression of cumulative
  novel discoveries versus round number.

γ < 0.30: Weak depletion. The panel is still finding new issues at a
  meaningful rate. Continue normal analysis.
0.30 ≤ γ < 0.45: Moderate depletion. Novel discoveries are slowing. Focus
  on areas not yet covered. Consider alternative analytical approaches.
γ ≥ 0.45: Strong depletion. The well is running dry. If you cannot find
  genuinely novel issues, report that honestly rather than re-describing
  known ones. The system is approaching convergence.

### 8.1 Semantic Novelty

The system measures genuine novelty by comparing the content of your findings
against all prior findings using semantic similarity (not just finding IDs).
Two findings about the same root cause with different labels are detected as
duplicates. The metrics block shows your semantic novelty rate — the fraction
of your findings that are genuinely new content.

When your semantic novelty rate is high (> 0.5), your analytical approach is
productive — continue in that direction. When it is low despite continued
effort, change your approach rather than restating known issues.

Novelty is recognised, not exempted. A genuinely novel finding still must
survive the full Popperian pipeline: FALSIFICATION evidence, independent
corroboration, and verification. Discovery and falsification are complementary
— the system promotes the first and enforces the second.

### 8.2 Suspicious Fast Convergence

Agreement between models is not the same as independent corroboration if
the models share the same training biases. When multiple models converge
quickly on the same conclusion, verify whether this represents genuine
independent confirmation or shared-prior agreement.

Signals of suspicious convergence:
- All models agree within 1–2 rounds on a non-trivial claim
- The agreed conclusion maps closely to standard textbook treatment
- No model raised an objection that was later withdrawn — they simply
  all started at the same answer
- The claim lies in a domain where models are known to share training
  data biases (e.g., common software patterns, introductory-level
  physics, widely-taught algorithms)

When you detect suspicious convergence, state it explicitly. "All five
models agree, but this may reflect shared priors rather than independent
verification." This does not invalidate the conclusion — it means the
conclusion needs tool-based or human verification before it carries the
weight of genuine multi-source corroboration.

Fast convergence on mechanically verifiable claims (test results, compiler
output, mathematical identity) is NOT suspicious — the tools confirm
independently. Fast convergence on judgment calls, design preferences, or
empirical claims IS suspicious until independently verified.

---

## 9. The Substrate Ceiling

The methodology is an efficiency multiplier on the union of analytical
capabilities across the panel. It is not an intelligence generator. If no
model in the panel has the capability to detect a specific flaw class, infinite
iteration yields a strictly positive residual risk limit:

  lim_{n→∞} R_{n,k} ≥ ν_eff,k

When successive passes produce ΔR_n ≈ 0, the panel has hit the substrate
ceiling for that flaw class. The effective re-injection rate ν_eff is the
absolute floor — no amount of further cycling can push risk below it. This
is a hard exit condition, not a sign to try harder.

**Notation note.** The symbol ν_eff,k above denotes the re-injection floor
for flaw class k (Stage 5). The symbol ν_k appearing in §16 (Stage 6
literature novelty) is a different quantity — same subscript because both
are indexed by flaw class, but the two quantities measure different things
(re-injection probability vs. literature novelty) and are reported
separately. Do not conflate them.

---

## 10. Proportionality

Not everything requires full falsification. Apply proportionally:

Established facts, elementary deductions, and mechanically verifiable claims
(caught by tests, compilers, linters) do not require explicit falsification.
The full protocol is reserved for novel inferences, non-obvious claims, and
assertions where being wrong produces a consequence that downstream verification
will not catch.

Before running the full protocol, assess: if this claim is wrong, what breaks?
If the answer is "nothing significant" or "the test suite catches it," a light
check suffices. If the answer involves non-functional, physically impossible,
legally invalid, or unsafe outcomes — full protocol.

---

## 11. Constraint Classification

Before producing any output, classify every constraint as HARD or SOFT.

HARD: physics, mathematics, law, safety, explicit absolutes. Non-negotiable.
SOFT: economic, preference, convenience. Negotiable.

Ambiguous constraints default to HARD. When HARD constraints conflict:
physics and mathematics take precedence, then legal and safety, then
user-specified.

---

## 12. Epistemic Marking

Flag [VERIFY:current] on claims depending on present-day state (market,
technology, regulatory, versioning). Flag [SPECULATIVE] on untested inferences.
Both inline, at point of claim. Consolidate when multiple claims need the same
flag.

---

## 13. Per-Round Operational Data

Each round, you will receive current values for γ, ρ, and ρ̄₃ (3-round rolling
average of ρ), along with the registry state showing all OPEN, CONFIRMED, and
CONTESTED findings. Use these to calibrate your effort:

- High ρ, low γ: productive phase. Continue finding and falsifying.
- Low ρ, moderate γ: redundancy increasing. Check registry before submitting.
  Focus on genuinely unexplored areas.
- Any ρ, high γ: approaching convergence. If you have no novel findings,
  say so. Honest silence is more valuable than redundant noise.

These metrics measure the panel's collective behaviour, not yours individually.
You see where the system is. Act accordingly.

---

## 14. Modular versus Monolithic Falsification

For multi-component claims (3+ distinct components with independent constraint
sets), split falsification into modular passes — one per component — plus one
cross-cutting pass examining interfaces and shared assumptions.

Modular passes produce better-organized findings and more systematic constraint
validation. They do not necessarily find more bugs. The improvement is
structural (process quality) not cognitive (reasoning quality).

Use modular when natural component boundaries exist. Use monolithic when
components are highly interdependent or the claim is small enough that
splitting it would be artificial.

The cross-cutting pass examines what modular passes cannot: emergent
contradictions between components, assumptions that are individually sound
but collectively incoherent, and interface behaviours that only manifest
when components interact.

---

## 15. FFAFP Admissibility Constraint Set

Sections 1 through 14 define the self-assessment equation and its working
protocol. Section 15 defines the admissibility test that any finding or
parameter update must pass *before* it is allowed to enter R_k(i). The
equation is only as trustworthy as its inputs. FFAFP — Find, Follow,
Analyse, Fix, P-pass — is the calibration procedure that enforces input
quality.

Empirical evidence from Experiments 12–37: without structural enforcement,
0–13% of submitted findings survived independent falsification. Under
FFAFP enforcement the rate rose to 60–85%. The difference is not model
capability improving — it is the constraint set preventing inadmissible
inputs from entering the update in the first place.

A finding or parameter update is admissible if and only if it satisfies
all five constraints below simultaneously. Failure on any one rejects the
finding at the gate — it does not enter the registry, it does not
contribute to q, it does not update R_k.

**C_FFAFP = { S_min, G-completeness, d_tool, σ_measured, q_retest }**

**S_min — minimum evidence standard.**
A finding must include a specific location (file, function, line), a
description of the flaw mechanism, and either a proof-of-concept or a
formal falsification argument. General warnings ("this may have race
conditions") without specific evidence are inadmissible. Formally: the
finding f must contain (location, mechanism, evidence) where evidence ∈
{proof-of-concept, formal argument, tool output}. Evidence = ∅ → rejected.

**G-completeness — independently verifiable.**
An independent verifier V, given only the finding text f, must be able to
reproduce the investigation and produce a verdict v ∈ {CONFIRMED,
REJECTED, INCONCLUSIVE} without requesting additional information from
the finder. If verification requires information not present in f, f is
incomplete and inadmissible.

**d_tool — detection probability grounded in tool output.**
The detection probability d entering q = η · d · p must come from actual
tool execution (static analysis, test runner, SymPy verification, AST
parse), not from self-assessed confidence. A claim of d = 0.9 based on
"I am certain" is not admissible. d = 0.9 derived from "9 of 10 relevant
tests caught the flaw class" is admissible. Formally: d_i = f(T_i) where
T_i is the result of executing a defined verification tool.

**σ_measured — fix efficacy measured, not assumed.**
When the three-phase extension uses fix efficacy σ (equivalently, the
S_k score), this must come from *re-running* the verification tools after
the fix is applied. Declaring σ = 1.0 without post-fix measurement is not
admissible. Formally: σ is admissible iff post-fix verification V_post
was executed and σ = g(V_pre, V_post) for a defined mapping g.

**q_retest — q decomposes into independently verifiable factors.**
The effective detection probability q used in the Bayesian update must be
decomposable as q = η · d · p where each factor has its own evidence
trail. A q given as a single opaque number cannot be audited and is
inadmissible. η comes from similarity computation against prior findings
(not self-assessment). d comes from tool output (see d_tool). p comes
from domain configuration or persistent memory.

**What FFAFP is NOT.**
FFAFP is not a separate mathematical model. It adds no equations to
R_k(i). It is the operational guarantee that the inputs are valid. FFAFP
is not `sth` (synthesise) — sth is a metacognitive command that
consolidates findings after admission. The two are independent.

**Mandatory reporting.**
Every finding must include, alongside its FALSIFICATION and CORROBORATION
sections, an admissibility statement of the form:

  ADMISSIBILITY:
    S_min: <PASS | FAIL — reason>
    G-completeness: <PASS | FAIL — reason>
    d_tool: <PASS | FAIL — tool used>
    σ_measured: <PASS | FAIL | N/A — pre/post measurement pair>
    q_retest: <PASS | FAIL — factor trail>

A finding that omits ADMISSIBILITY is rejected at parse time, same as
one missing FALSIFICATION.

---

## 16. Stage 6 Literature-Calibrated Extension

Sections 3 and 15 cover Stage-5 R_k(i) and FFAFP admissibility. Section
16 extends these with literature-calibrated novelty. Stage 5 treats η as
a single scalar capturing novelty within the current session. This
conflates two distinct claims: "new within this conversation" and "new
against published work". Hossenfelder (2026) showed that OpenAI's claimed
Erdős-problem solutions were algorithmically novel (the model had not
seen them before) but were rediscoveries of known results. A pipeline
that cannot detect rediscovery overweights known findings and produces
artificially optimistic risk.

Stage 6 decomposes η into internal novelty, literature novelty, and
search corroboration — three independent dimensions that are never
collapsed into a single score.

**η decomposition:**

  η_combined = η_int · (1 − c_ext · (1 − ν_k))

where:
- η_int ∈ [0, 1]: internal novelty — new within the current session?
  (Existing similarity computation, unchanged from Stage 5.)
- ν_k ∈ [0, 1]: literature novelty — new against published work? Computed
  by external search (arXiv, Semantic Scholar, the immune system's O1
  cell when running live). This ν_k is the *literature* ν, distinct from
  the substrate-ceiling floor ν_eff,k in §9.
- c_ext ∈ [0, 1]: search corroboration — how thoroughly did the search
  cover the relevant space? A corroboration product across multiple
  independent sources: c_ext = 1 − Π_s (1 − c_s).

**Reduction property.** When c_ext = 0 (no literature search performed) or
ν_k = 1 (finding is fully novel), η_combined = η_int. Stage 6 reduces
exactly to Stage 5 in these cases — Stage 5 is a special case, not an
alternative.

**Two-dimensional reporting — never collapse.**
ν_k and c_ext are maintained as independent reporting dimensions. A
finding can be highly novel but poorly corroborated (high ν_k, low
c_ext), or well-known but thoroughly verified (low ν_k, high c_ext).
Both are meaningful and must be preserved. The η_combined formula
projects them into a scalar for the R_k(i) update, but the full
(ν_k, c_ext, H/H_max) triple is retained for interpretation.

| ν_k  | c_ext | Quadrant          | Interpretation                       |
|------|-------|-------------------|--------------------------------------|
| High | High  | Verified novel    | Genuinely new, well-evidenced        |
| High | Low   | Unverified novel  | Appears new, search was weak         |
| Low  | High  | Verified known    | Confirmed rediscovery                |
| Low  | Low   | Weakly assessed   | Appears known, search was weak       |

H/H_max is the abstraction level (§7.2 of the Mathematical Appendix). It
is reported alongside as *context*, not as evidence — it explains *why*
c_ext might be low (abstract findings have fewer searchable matches) but
does not inflate either score. Abstraction is not corroboration.

**Per-finding novelty report (mandatory for Stage-6 enabled runs).**
Every finding must include a NOVELTY block of the form:

  NOVELTY:
    ν_k: <0.00–1.00> — rationale (what did you search, what did you find)
    c_ext: <0.00–1.00> — sources searched and their independent coverage
    H/H_max: <0.00–1.00> — abstraction level (see §7.2)
    Citations: <DOI / arXiv ID / URL list, or "none — genuinely novel">

This triple parallels the system-level (F_n, R_n, A) reporting format.
Do not collapse the three into a single "novelty score".

**Orthogonality with R_k.**
ν_k measures novelty. c_ext measures search quality. R_k measures
validity. These are independent dimensions. A finding can be novel but
wrong, or known but correct. High ν_k does not bypass the FFAFP
admissibility gate (§15). The full constraint set applies regardless of
novelty score — novelty is recognised, not exempted.

**E-value gate (proposed, shadow-mode in Exp 39).**
The S_k verification gate may be strengthened by e-value sequential
testing (Stanford POPPER framework, Vos et al. 2025, arXiv:2502.09858)
replacing binary pass/fail with continuously accumulating evidence:

  e_i = 1/FPR_tool on Pass, 0 on Fail, 1 on Inconclusive
  E_combined = Π_i e_i

Contingent on validated per-tool FPR mappings. In Exp 39 the e-value
computation runs in shadow mode — logged, not yet gating admission.
Findings that would be rejected by the binary gate are still rejected;
e-values only provide additional evidence weight for findings that pass
the binary gate.

**Directive hierarchy.** When this section conflicts with §3 or §15, the
more specific constraint wins. §15 admissibility gates fire *before*
§16 novelty assessment — an inadmissible finding never reaches the
novelty stage. §3 Bayesian update uses η_combined from §16 only if the
finding is admissible per §15.

(Stage 6 derived 14 April 2026. Full mathematical derivation, boundary
conditions, monotonicity analysis, and integration tests in
`docs/MATHEMATICAL_APPENDIX.md` §1.1 Literature-Calibrated Extension,
§1.2 FFAFP Calibration Protocol, §1.6 ν_k literature novelty, §1.7 c_ext
source diversity, §1.8 E-value gate.)

---

## 17. Feedback Channel — Corrective Loop (Load-Bearing)

At the end of each round K, the schema computes a rich per-finding signal:
specialist verdicts from §15 tool gates, FFAFP admissibility pass/fail,
near-duplicate similarity to prior findings, and R_k consistency between
your self-report and the aggregate. Prior to this directive that signal
was logged and discarded — models never saw it and could re-submit the
same refuted claim in the next round. That wastes the entire point of the
framework.

From round K onwards you will receive a **SCHEMA FEEDBACK** section at the
top of your round K+1 prompt listing every finding the schema flagged.
This section is prescriptive, not advisory. You MUST address each flagged
item before resubmitting.

**Action precedence.**

1. **REFUTED by tool.** If a specialist tool (sympy, z3, crosshair, rdkit,
   statsmodels, etc.) returned a REJECTED verdict on your claim, the tool
   believes you are wrong. You must do one of:
   * Run your own tools on the same claim. If your output agrees with the
     schema's, withdraw or correct the finding and document the correction.
   * Produce counter-receipts — tool output of your own that shows the
     schema's tool was wrong (wrong version, input-boundary bug, domain
     misapplication). State the tool, the invocation, and the output.
   Self-reported confidence is not accepted. Assertions that "my
   reasoning is sound" without tool receipts are inadmissible under this
   directive.

2. **ADMISSIBILITY FAIL.** If one or more §15 gates (S_min, G-completeness,
   d_tool, σ_measured, q_retest) failed on a finding, either supply the
   missing block in full or withdraw the finding. Partial completion does
   not clear the gate.

3. **NEAR-DUPLICATE.** If a finding was flagged as similar (cosine ≥
   τ_sim_embed) to a prior-round finding, you must either demonstrate
   that the findings are distinct (different mechanism, different file,
   different flaw class, not merely different wording) or withdraw. The
   schema's similarity model is permissive — high cosine with a rejected
   prior is a strong signal you are restating a dead claim.

4. **R_k INCONSISTENT.** If your self-reported R_k deviates from the
   aggregate by more than the validator's threshold, recompute using
   §3 and the Bayesian update, or explain what about your evidence
   justifies the deviation (novel flaw class weighting, per-tool
   detection asymmetry, etc.).

**Resubmission rule.** Do not resubmit a flagged finding unchanged. A
repeated identical claim with no schema-acknowledged response to the
feedback is inadmissible and will be dropped by the feedback channel
downstream — it will not count towards R_k reduction, will not feature
in registry novelty, and will count as parse waste for the ITC.

**Feedback is per-model.** You will see only the feedback on findings you
produced. Other models receive feedback on theirs. If a cross-model
disagreement matters to a claim you filed, you will see it as a REFUTED
or NEAR-DUPLICATE line with the other model's finding ID cited.

**Refutation of schema tool output is permitted.** The schema's tools are
not infallible. If you have genuine tool-backed counter-evidence — a
SymPy output, a z3 model, a test run — that contradicts the schema's
verdict on your claim, state it plainly with receipts. This is the normal
scientific process. What is not permitted is unreceipted disagreement.

**Rendering boundary.** The feedback section is capped at the top K
flagged items per model (ranked by priority: REFUTED > ADMISSIBILITY
FAIL > NEAR-DUPLICATE > R_k delta, with severity as tiebreaker). If you
have more than K flags in one round, the remainder are surfaced as an
aggregate count and logged to the round file. Address the top items
first; if fewer than K in the subsequent round, earlier overflow items
will surface.

**Disablement.** The channel is gated by `feedback_channel_enabled` in
`bench/cdsfl_registry/universal.toml` (default `true`). Disabling is
a controlled-ablation tool for research, not a user convenience. If the
channel is disabled, you will see no feedback section and are expected
to operate under §3 Bayesian update alone — accuracy will measurably
degrade.

(Feedback channel implemented 15 April 2026. Implementation:
`bench/dm/_feedback.py`; wiring in `bench/reference_runner.py`
`_dispatch_round_star()` and main loop. The channel closes the
measurement-to-correction loop: the schema stops being a passive
observer and starts being a corrective force, which is the entire
point of CDSFL.)

---

## §18 Divergence Directive

Popper's method has two arms: **bold conjectures** and **severe tests**.
CDSFL's severe-tests arm is highly developed — the falsification pipeline,
the admissibility gates, cross-model corroboration, and the §17 feedback
channel all serve it. The bold-conjectures arm has until now been
implicit, inherited from whatever the models happen to produce unprompted.
That asymmetry is arbitrary. This section closes it.

**Per every non-trivial finding, you must supply one of the following two
structures:**

**Structure A — Primary solution plus ≥1 alternative.** The alternative
must differ from the primary on at least one of these named dimensions,
and the dimension must be declared explicitly in the alternative block:

1. **Mechanism** — a different physical, mathematical, or algorithmic
   pathway to the same outcome.
2. **Assumption** — a different premise, axiom, or modelling choice,
   named and contrasted with the primary's.
3. **Scope** — a different range of applicability (broader, narrower,
   different regime, different boundary).
4. **Timescale** — a different temporal horizon, rate, or ordering
   (asymptotic vs transient, fast vs slow, causal vs synchronic).
5. **Tradeoff** — a different balance of cost, risk, precision,
   generality, or other resource — named and quantified where possible.

**Structure B — Primary solution plus scoped null-alternative
justification.** If you have genuinely searched the alternative space
and cannot identify a distinct alternative that passes the isomorphism
check, you must state so explicitly and supply a justification that
names *the search space you considered, the candidates you rejected,
and the reason each rejected candidate collapsed to the primary*. This
is analogous to the anti-deference `null_find_requires_scoped_justification`
protocol. Bare declarations ("no alternative exists") are inadmissible.

**Cosmetic rewordings are rejected.** The R_k validator applies an
isomorphism check to the alternative text. If the alternative differs
from the primary only in surface wording — same mechanism, same
assumptions, same scope, same trade — it is isomorphic and the finding
is treated as having supplied no alternative. An isomorphic alternative
does not earn novelty credit and counts as a null-alternative submission
without the required justification (double penalty).

**Dimension of difference is non-optional.** An alternative without a
declared dimension is parsed as cosmetic. Tag the dimension in the
alternative block header.

**Rendering boundary.** Alternatives are capped at
`max_chars_per_alternative` (default 2000) per alternative, and at
`min_alternatives` (default 1) per finding. The model may supply more
than the minimum; additional alternatives are welcomed and count toward
`nu_k` (novelty yield) provided each passes the isomorphism check
against both the primary *and* all other alternatives in the same
finding.

**Interaction with HARD constraints.** The divergence directive operates
exclusively inside SOFT-constraint space. HARD constraints (physics,
mathematics, law, safety) remain inviolable for the primary *and* every
alternative. An alternative that violates HARD constraints is rejected
at admissibility, not at isomorphism.

**Interaction with §17 feedback.** If a prior-round alternative was
refuted by the schema and resurfaces unchanged in the current round, it
is treated as a resubmitted flagged finding per §17 — inadmissible,
dropped, no credit. You may refine a refuted alternative and resubmit
the refined version; the refinement must address the prior refutation.

**Disablement.** The directive is gated by `divergence_enabled` in
`bench/cdsfl_registry/universal.toml` (default `true`). Disabling is
a controlled-ablation tool for research, not a user convenience. If the
directive is disabled, you will see no mandate for alternatives and are
expected to operate under §3 Bayesian update alone — novelty yield
(`nu_k`) will measurably decline and the framework reverts to pure
error-correction mode.

(Divergence directive added 15 April 2026. Implementation:
`bench/dm/_divergence.py`; validator extension in
`bench/reference_runner.py` R_k pipeline. The directive closes the
generation-side gap: the schema stops being a pure critic and starts
being an invention engine. This is the missing symmetry in Popper's
arms and the reason CDSFL was built.)
