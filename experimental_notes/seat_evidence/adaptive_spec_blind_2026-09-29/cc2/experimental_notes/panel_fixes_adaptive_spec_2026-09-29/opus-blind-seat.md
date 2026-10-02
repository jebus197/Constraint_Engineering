<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'adaptive_spec_blind_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b61500d090fbc89b71125cb149149f0b0234e3d7add3801fafa660a5efc9dd20
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Panel fixes — adaptive distributed-compute design spec (2026-09-14)

**Seat:** opus-blind-seat · **Round:** blind · **Date:** 2026-09-29
**Target:** `adaptive_distributed_compute_design_spec.md` (624 lines, outside the repo)
**Producer for every number below:** `scripts/adaptive_spec_falsifiers_2026-09-29.py`
(9 checks, all executed; check 7 is a control that HELD).

**Overall position:** the specification is sound enough for the runway, at Phase B.
Its discipline is real — it refuses to redefine the canonical model, it names its own
disconfirmation rules (§12), and it correctly shelves `_load_balancer.py`. Six defects
bite, and five of them are in §6, the allocation mathematics. Two are load-bearing:
§6.1 predicts the wrong branch quantity for the decision it is making, and §6.5's
objective does the thing §6.7.1 forbids. Neither requires abandoning the design.

---

## FIX 1 — §6.1: `ν̂` is written as a free parameter; the runner derives it from `σ`

**Original (§6.1):**

> \\[
> R_{\mathrm{next}} =
> \left[\hat\sigma_{muk}R_{\mathrm{det}}
> +(1-\hat\sigma_{muk})R_{u,k}(r)\right](1-\hat\nu_{muk})
> +\hat\nu_{muk}
> \\]
>
> […] \(q=d\cdot p\), \(\eta\), \(\sigma\), \(\nu\) | The existing effective detection,
> novelty, fix-efficacy, and re-injection mechanics. The scheduler consumes their
> calibrated estimates; it does not alter their update law.

**Why it is wrong.** `bench/reference_runner_v3.py:compute_rk` does not accept a `ν`.
It accepts `nu_b`, `nu_f` and computes

    nu_eff = 1 - (1 - nu_b) * (1 - (1 - sk) * nu_f)

which is a **function of `sk`** — and `sk` is the same slot as `σ` (the runner's own
comment: *"Phase 2: Resolution (S_k replaces sigma)"*). At the shipped defaults
`nu_b=0.05, nu_f=0.20`, `ν` is the affine decreasing function `0.05 + 0.19(1-σ)`,
sweeping 0.190 across `σ ∈ [0,1]`. A scheduler estimating `σ̂` and `ν̂`
independently predicts states the runner cannot produce, and loses the coupling
that makes a weak fix doubly penalised — so it **over-rewards low-`σ̂` candidates**.

Measured: the best single constant `ν̂` leaves `sup|spec − compute_rk| = 0.051471`
at `R=0.5, q=0.30` (best `ν̂ = 0.1375`).

**Replacement text for §6.1:**

> Given the present canonical claim-state \(R_{u,k}(r)\), the scheduler predicts the
> existing three-phase update. **Re-injection is not a free parameter.** The canonical
> implementation derives it from the fix-efficacy term and the two policy constants
> \(\nu_b\) (baseline) and \(\nu_f\) (failed-fix):
>
> \\[
> \nu_{\text{eff}}(\sigma) = 1-(1-\nu_b)\bigl(1-(1-\sigma)\nu_f\bigr)
> \\]
>
> \\[
> R_{\mathrm{next}} =
> \left[\hat\sigma_{muk}R_{\mathrm{det}}
> +(1-\hat\sigma_{muk})R_{u,k}(r)\right]\bigl(1-\nu_{\text{eff}}(\hat\sigma_{muk})\bigr)
> +\nu_{\text{eff}}(\hat\sigma_{muk})
> \\]
>
> The scheduler estimates \(\hat\sigma\) only; \(\nu_b,\nu_f\) are inherited policy
> constants and are **not** per-configuration estimates. A scheduler that estimates
> \(\hat\nu\) independently of \(\hat\sigma\) is predicting a state the canonical
> runner cannot reach, and systematically over-rewards low-efficacy candidates
> because it drops the penalty coupling. The single source of truth is
> `bench/reference_runner_v3.py:compute_rk`; any transcription must be checked
> against it numerically, not by inspection.

Also amend the notation table row so it reads
`q=d·p, η, σ` … and add a separate row:
`ν_b, ν_f` | Policy constants. The composed `ν_eff` is DERIVED from `σ` and is not
a per-configuration estimate.

---

## FIX 2 — §6.1: the closing S_k claim says "zero credit"; the formula gives NEGATIVE credit

**Original (§6.1, final paragraph):**

> `S_k=A\cdot E` remains a hard qualification boundary. A candidate that cannot satisfy
> an applicable verification gate may be valuable as discovery, but it receives **zero
> verified-risk-reduction credit** until an admissible verifier supplies evidence.

**Why it is wrong — three distinct things are conflated.** Substituting `σ=0` into
§6.1's *own* `R_next` gives `g = R − R_next = ν(R−1)`, which is **strictly negative**
for every `R<1, ν>0`. SymPy returns `nu*(R - 1)`; z3 returns **unsat** on `g ≥ 0`
anywhere in the open unit cube; Wolfram `Reduce` returns **False** on the same
question (*computed with Wolfram Language*). The live function agrees:
`compute_rk(0.5, 0.30, sk=0.0) = 0.620000`, i.e. `g = −0.120000` — a **penalty of
0.12**, not zero.

The runner never emits that penalty, and the reason is instructive: it does not route
a non-admissible outcome through `compute_rk` at all. `apply_sk_to_rk` intercepts,
and both `REJECTED` and `NO_SCORE` return `R_old` unchanged. The docstring states
the principle: *"'Not scored' and 'scored zero' are different statements."*
§6.1 collapses them, and additionally never links `σ̂` to `S_k` — the score in §6.4
consumes a free `σ̂`, so a candidate whose gate product will be 0 can carry `σ̂=0.9`
and win the dispatch. The "hard qualification boundary" has **no formal expression
in the score**.

**Replacement text for §6.1, final paragraph:**

> `S_k = A·E` remains a hard qualification boundary, and it enters the scheduler in
> two distinct places rather than as a sentence.
>
> 1. **`σ̂` is an estimate OF `S_k`, not a separate quantity.** The canonical
>    implementation passes one value into the resolution phase; the scheduler's
>    `σ̂_muk` is its forecast of the `S_k` that the applicable gate will return.
>    A configuration with no admissible verifier has no `σ̂`, not a low one.
> 2. **Three outcomes, three different arithmetics.** The scheduler must carry the
>    canonical tri-state (`ADMISSIBLE` / `REJECTED` / `NO_SCORE`), because they
>    produce different states:
>    - `ADMISSIBLE`: `R_next` per the update above.
>    - `REJECTED` and `NO_SCORE`: **`R_next = R_u,k(r)` exactly, so `g_muk = 0`.**
>      Substituting `σ̂ = 0` into the update law instead gives `g = ν(R−1) < 0` —
>      a *penalty* for a fix that was never assessed. That is not "zero credit"
>      and it accrues risk a prose target can never work off.
>    Conform to `bench/reference_runner_v3.py:apply_sk_to_rk`, which is the single
>    sink where an `S_k` outcome may move `R_k`.
> 3. `x_{mu} = 0` in §6.5 whenever no admissible verifier exists for the unit's
>    failure class **and** the unit's policy forbids unverified discovery credit.
>    The exclusion belongs in the feasibility constraint, where a program can
>    check it, not in prose.

---

## FIX 3 — §6.1/§6.4: `g` is the negative-branch conditional; a dispatch decision is pre-branch

**Original (§6.1):**

> The predicted class-level value of dispatching \(m\) is therefore:
> \\[ g_{muk}=R_{u,k}(r)-R_{\mathrm{next}} \\]

**Why it is wrong.** `R_next` is the blend `A = σ·R_det + (1−σ)·R` carried through
phase 3. `docs/MATHEMATICAL_APPENDIX.md` (§1.1, entry added 2026-09-29) establishes
that `A` is **not** a posterior conditional except at `σ = 1`, and that the quantity
a *pre-branch* decision needs is the branch-weighted expectation
`M = R(1 − qσ)`, implemented as `compute_rk_expectation`. The appendix already says
this for the **stopping** decision — *"ΔR_k is the change conditional on the
non-detection branch, while a decision about whether to run another cycle is a
decision taken before the branch is known"*. **A dispatch decision is the same kind
of decision**, and the appendix does not say so.

`A ≥ M` on the whole domain (z3: `A < M` is **unsat**; Wolfram
`Resolve[ForAll[...], Reals]` → **True**, *computed with Wolfram Language*), with
`A − M = σqR²(1−q)/(1−qR)`. Because that gap depends on `(q, σ)` — which differ per
candidate — the transformation is **not** rank-preserving:

    strictly-ordered candidate pairs : 64979
    ranking inversions               : 1537
    inversion rate                   : 2.3654%   Wilson 95% [2.2513%, 2.4851%]

**Sampling distribution, stated:** uniform on `q, σ ∈ {0.05, 0.10, …, 0.95}` (19×19
= 361 candidates), `R` fixed at 0.5, `ν_b=0.05, ν_f=0.20`, all unordered pairs. This
is **not** the operational distribution, which is unknown. The rate is a property of
this grid as much as of the estimator.

Worked inversion: `m1=(q=0.05, σ=0.10)` vs `m2=(q=0.35, σ=0.05)`. §6.4 dispatches
`m1`; the pre-branch expectation prefers `m2`.

**Replacement text, §6.1, to follow the `g_muk` definition:**

> \\[ g^{A}_{muk}=R_{u,k}(r)-R_{\mathrm{next}} \\]
>
> **This is the negative-branch blend, and it is not the quantity a dispatch decision
> needs.** `R_next` is the state *given the pass reported nothing*. A dispatch is
> chosen **before** the branch is known, so the decision-relevant quantity is the
> branch-weighted expectation, `bench/reference_runner_v3.py:compute_rk_expectation`:
>
> \\[ M_{muk} = R_{u,k}(r)\bigl(1-\hat q_{muk}\hat\sigma_{muk}\bigr)
>   \ \text{carried through phase 3},\qquad
>   g_{muk}=R_{u,k}(r)-M_{muk} \\]
>
> The scheduler **ranks on \(g\), reports both, and gates on neither.** `A ≥ M`
> everywhere, so substituting one for the other is not a scale change: on a uniform
> 19×19 grid of \((q,\sigma)\) at \(R=0.5\), **2.37% of strictly-ordered candidate
> pairs [Wilson 95%: 2.25%, 2.49%] are ranked in the opposite order** by the two
> quantities. The canonical gate continues to consume `A`; the appendix records why
> feeding `M` to a gate calibrated on `A` would loosen every threshold in the project.
> [VERIFY:current — this depends on the appendix revision in force; see FIX 6.]

---

## FIX 4 — §6.5: the LP objective adds gains that do not add, and §6.7.1 forbids it

**Original (§6.5):**

> \\[ \max_x\ \sum_u\sum_m x_{mu}\,\hat g_{mu} \\]
> […] \\[ \sum_m x_{mu}\geq r_u \\]
> where \(r_u\) is a risk-based minimum redundancy requirement, ordinarily 1, 2, or 3

**Why it is wrong.** With `r_u = 2` or `3` the objective sums the gains of two or three
configurations **on the same unit**. But the detection update composes multiplicatively
in the **odds** — SymPy and Wolfram both return `T(T(R,q₁),q₂) − T(R, 1−(1−q₁)(1−q₂))
= 0` exactly — so the true joint gain is the *single-pass* gain at
`q_eff = 1−(1−q₁)(1−q₂)`. §6.7.1 states the prohibition in words
(*"Their predicted gains cannot both be summed as if they covered disjoint defects"*);
§6.5's objective performs it in symbols. §6.6's own submodularity paragraph is about
`D_u(n)`, not about `g`, so it does not cover this.

The bias is **two-signed**, with an exact boundary (Wolfram `Reduce`, re-derived in
SymPy, *computed with Wolfram Language*):

    (g₁+g₂) − g_joint > 0  ⟺  R < R*,   R* = (1 − √(1−q_eff)) / q_eff ∈ [½, 1)

- `R = 1/2` (`= RK0_PI_BASE`, the runner's default prior), `q₁=q₂=1/2`:
  `g₁+g₂ = 1/3`, `g_joint = 3/10` — the objective **overstates by 11.11%**.
- `R = 9/10`, `q₁=q₂=1/2`: `0.163636` vs `0.207692` — it **understates by 21.21%**.
- z3: no point with `R ≤ 1/2` fails to overstate (**unsat**); a point where it
  understates exists (**sat**). Wolfram `Resolve[ForAll[..., gap>0]]` → **False**
  globally, **True** restricted to `0 < R ≤ 1/2`.
- On a uniform grid `R, q₁, q₂ ∈ {0.05,…,0.95}³` (6858 non-degenerate points):
  overstates **71.35%** [Wilson 95%: 70.27%, 72.41%], understates 28.65%.
  *This grid is not the operational distribution.* What is known is that `R` is
  **initialised at exactly 0.5**, on the overstating side of the boundary.
- On the live function with §6.2's own numbers (`R=0.5, q_A=0.45, q_B=0.35, σ=1`,
  shipped `ν`): `g_A+g_B = 0.188661` vs sequential `0.173507` — **+8.73%**.

A two-signed bias is worse than a one-signed one: it cannot be treated as a
conservative bound.

**Replacement text for §6.5 (objective and a new constraint):**

> At one scheduling epoch the transparent baseline maximises the **jointly composed**
> gain per unit, not the sum of per-configuration gains:
>
> \\[ \max_x\ \sum_u \hat g_u\!\left(\{m : x_{mu}=1\}\right),\qquad
>    \hat g_u(A) = R_{u,k}(r) - \Phi\!\left(R_{u,k}(r),\,
>    1-\textstyle\prod_{m\in A}(1-\hat q_{muk})\right) \\]
>
> where \(\Phi\) is the canonical update of §6.1. **Do not write
> \(\sum_u\sum_m x_{mu}\hat g_{mu}\).** The detection update composes
> multiplicatively in the odds, so two passes on one unit are exactly one pass at
> \(q_{\text{eff}}=1-\prod(1-q_m)\), and the additive form is biased with sign
> boundary \(R^{*}=(1-\sqrt{1-q_{\text{eff}}})/q_{\text{eff}}\in[\tfrac12,1)\):
> it **overstates** below \(R^{*}\) (11.11% at \(R=\tfrac12, q_1=q_2=\tfrac12\)) and
> **understates** above it (21.21% at \(R=0.9\)). Because the canonical prior
> \(R_k(0)=0.5\) sits on the overstating side, an additive allocator would
> systematically over-buy redundancy in early rounds and under-buy it on units that
> have accrued risk through re-injection. The composed form is still submodular in
> \(A\) at fixed \(R\), so the greedy rule of §6.6 survives unchanged.
>
> Add: \\[ \text{overlap}(u,u')\neq\emptyset \Rightarrow \text{units }u,u'
> \text{ share a claim key and their gains are composed, not summed} \\]
> making §6.7.1's prohibition a **constraint the solver enforces** rather than a
> paragraph the implementer is asked to remember.

---

## FIX 5 — §6.4: the exploration term is zero when uncertainty is greatest, and the score is unit-dependent

**Original (§6.4):**

> \\[ \operatorname{score}(m,u\mid A)=
> \frac{\hat g_{mu}}{c_{mu}+\lambda_t t_{mu}+\lambda_h h_{mu}} +\beta e_{mu} \\]
> One initial exploration term is:
> \\[ e_{mu}=\sqrt{\frac{\log(1+N_u)}{1+n_{mu}}} \\]
> […] \(\lambda_t\), \(\lambda_h\), and \(\beta\) are explicit policy values.
> They must be fixed before a comparative run.

**Two defects.**

**(a) `N_u = 0` kills the term for every candidate.** `log(1+0) = 0`, so `e_mu ≡ 0`
for all `n_mu ∈ {0,…,49}` — executed and confirmed. On the first unit of a new task
family, a never-tried configuration (`n_mu=0`) scores exactly the same exploration
bonus as a saturated one (`n_mu=49`): zero. Exploration is switched **off precisely
when §6.3 says the intervals are widest and the couplings unfittable**. Standard
UCB either puts a global pull count in the numerator that is ≥1 by construction or
forces one pull per arm before scoring; this form does neither.

**(b) The score is not invariant under a change of cost unit.** Term 1 has units of
risk-per-currency; term 2 is dimensionless times `β`. Rescale currency by `s`
(dollars → cents, `s=100`) and rescale `λ_t, λ_h` to preserve term 1: term 1 shrinks
by `1/s`, term 2 does not. Worked flip — `g_A=0.020, D_A=1.00, n_A=6` vs
`g_B=0.015, D_B=1.00, n_B=0`, `N_u=8`, `β=0.0010`: **dollars picks A** (0.020560 vs
0.016482), **cents picks B** (0.000760 vs 0.001632). The flip band for this pair is
`β ∈ (0.000054, 0.005423)`, a ~100-fold window whose *location* moves with the unit.
Over a stated random box — `g ~ U(0.001,0.05)`, `D ~ U(0.05,5.0)`, `n ~ U{0..19}`,
`N_u ~ U{1..49}`, `β ~ log-uniform(1e-4,1)`, 200 000 draws, seed 20260929 — the
dollars-vs-cents ranking flips in **22.39%** of draws, Wilson 95% [22.21%, 22.57%].
**That box is my prior, not the operational one, which is unknown.** The
qualitative point does not depend on the box: `β` silently carries units, and §6.4
says to fix it before a run without saying in what.

**Replacement text for §6.4:**

> \\[ \operatorname{score}(m,u\mid A)=
> \frac{\hat g_{mu} + \beta\,\hat s_{mu}}{c_{mu}+\lambda_t t_{mu}+\lambda_h h_{mu}} \\]
>
> The exploration bonus is applied to the **numerator**, so the whole score has one
> unit — risk per unit resource — and the ranking is invariant under a change of
> currency unit. Adding \(\beta e_{mu}\) *outside* the ratio is not equivalent:
> rescaling currency by \(s\) shrinks the ratio term by \(1/s\) and leaves the bonus
> untouched, which flips candidate rankings (22.4% of draws on a stated random box;
> worked example at \(\beta=0.001\) where dollars pick A and cents pick B).
>
> \(\hat s_{mu}\) is the **upper end of the uncertainty interval on \(\hat g_{mu}\)**
> minus its point estimate, which §6.1 already requires the estimator to carry, and
> which is in the units of \(g\). Where a count-based surrogate is used instead:
>
> \\[ e_{mu}=\sqrt{\frac{\log\bigl(2+N_u\bigr)}{1+n_{mu}}} \\]
>
> with \(N_u\) the number of completed allocations in the task family. **The `1+N_u`
> form is wrong at \(N_u=0\):** it is identically zero for every \(n_{mu}\), so the
> first unit of a new task family gets no exploration incentive at all and a
> never-tried configuration is indistinguishable from a saturated one. Any
> alternative must satisfy the property test \(e_{mu}(N_u=0, n=0) >
> e_{mu}(N_u=0, n=49)\), which the specified form fails.
>
> \(\lambda_t\) carries units of currency per unit time, \(\lambda_h\) currency per
> unit human-review burden, and \(\beta\) is dimensionless. State the currency,
> time and burden units in the pinned policy version; a policy that fixes the
> numbers without fixing the units has not fixed the policy.

---

## FIX 6 — §9.2/§9.3: the design cannot resolve the difference it is built to test; and §9.4's live gates are not program-evaluable

**Original (§9.2):** *"At least three independently seeded or held-out runs per
condition are needed before comparing small differences."*
**Original (§9.3):** *"Measure a staged curve at 1, 2, 4, 8, 16, and then 32 effective
workers"* … *"\\[ \text{MarginalVerifiedYield}(n) = \frac{V_n-V_{n-1}}{C_n-C_{n-1}} \\]"*
**Original (§9.4):** *"Controlled live | … | Matched-budget improvement and no
invariant breach"* and *"Operational | … | Replicated benefit, auditability, and
defined rollback"*

**Power, measured (statsmodels `TTestIndPower`, two-sample t, α=0.05 two-sided):**

    n/arm   power @ d=0.8   power @ d=1.5   min detectable d @ 80% power
        3          0.1193          0.2932                         3.071
        5          0.2007          0.5494                         2.024
       10          0.3951          0.8870                         1.325
       20          0.6934          0.9961                         0.909

At `n=3` the design resolves only `d > 3.07` — three standard deviations. §9.2 has
six conditions, so 15 pairwise comparisons; with Bonferroni `α=0.05/15` the minimum
detectable effect becomes **`d = 6.40`**. §9.2's own sentence says three runs are
what is needed *"before comparing small differences"*; **three runs cannot compare
small differences at all.** And `MarginalVerifiedYield`'s numerator has
`SE(V_n − V_{n−1}) = √(2/3)·σ = 0.8165σ` at three runs per arm, so even the **sign**
of the marginal gain is undetermined unless the true gain exceeds `1.600σ`.

The design is also ambiguous about its own size: 6 scales × 6 conditions × 3 seeds is
108 runs if "three" is per *cell*; "per condition" reads as 18 runs, leaving `n=1`
per (scale, condition) cell and **no within-cell variance estimate at all**.

**Gate checkability, measured.** Of §9.4's four gates, **2 of 4** admit a program
predicate (Library → test-runner exit status; Shadow → target-hash equality plus a
zero budget-ledger delta). The two that decide whether the layer goes live do not:
"matched-budget improvement" names no statistic, no threshold and no interval;
"replicated benefit" has no `k`; "auditability" has no predicate. Mechanically, the
word "threshold" appears **4 times in 624 lines with 0 numeric values attached** —
every one defers to "the policy threshold", "the documented threshold", or "the
pre-registered threshold". Deferring is legitimate in a design brief; presenting
them in a gate table headed *"Promotion evidence"* is not, because it reads as a
decision procedure that does not exist.

**Replacement text for §9.2 (final paragraph) and §9.4:**

> **§9.2.** Three runs per condition is a smoke test, not a comparison. Measured with
> a two-sample t-test at α=0.05: **n=3 has 12% power against d=0.8 and resolves only
> d > 3.07 at 80% power**; across this table's 15 pairwise comparisons with a
> Bonferroni correction the minimum detectable effect is **d = 6.40**. Three runs is
> therefore the floor for *detecting a gross failure*, and the programme must
> pre-register, per primary comparison: (i) the effect size it intends to detect,
> (ii) the `n` that gives it 80% power at that size, (iii) the multiplicity
> correction, and (iv) the variance estimate the `n` was computed from, with its
> provenance. Where the required `n` is unaffordable, say so and report the
> comparison as **underpowered by construction** rather than as a null result.
> `MarginalVerifiedYield(n)` must be reported with a confidence interval; at three
> runs per arm `SE(V_n − V_{n−1}) = 0.82σ`, so its **sign** is undetermined below a
> true gain of `1.60σ`, and a curve of such point estimates must not be read as a
> trend. State whether three runs is per condition (18 runs) or per (scale,
> condition) cell (108 runs); the former leaves no within-cell variance estimate.
>
> **§9.4.** Each promotion criterion must be a predicate a program can evaluate from
> stored artefacts, with the statistic, threshold and interval named in the pinned
> policy version — not a phrase requiring a judgement this document does not specify.
> As written, 2 of the 4 gates qualify (Library: test-runner exit status; Shadow:
> target-hash equality and zero budget-ledger delta) and the 2 that authorise live
> operation do not. Specifically: **"matched-budget improvement"** must become a named
> statistic, a direction, a threshold, and a pre-registered `n` with its power; and
> **"replicated benefit"** must name `k` independent replications and the agreement
> criterion across them. Until those are written, the correct status of Controlled
> live and Operational is *specified but not gated*, and the table should say so.

---

## Things I checked that turned out SOUND — recorded because a round of only complaints is obliging, not sceptical

1. **§6.2's worked example is exactly right.** `1−(1−0.45)(1−0.35) = 257/400 = 0.6425`
   and the marginal contribution `77/400 = 0.1925`, both exact in SymPy rationals.
   The marginal-gain point it illustrates is the correct one.
2. **§6.2's `Δ_{u,k}(m|A) = P(D ∩ ¬∪D_a)` is the right conditional object**, and
   §6.3's refusal to manufacture a scalar correlation correction is the right call —
   it matches the appendix's own Ising branch and its stated data-hunger.
3. **§6.6 is correctly hedged.** It claims submodularity for `D_u(n)` (true for fixed
   discovery events) and explicitly declines to claim a global optimisation guarantee
   for the full objective. That is the honest version.
4. **§4.1's acyclicity obligation, §4.2's dependency-closure and interface-ownership
   obligations are all decidable** and I implemented each to confirm it — Kahn's
   algorithm separates a DAG from a cycle, dangling dependency refs are set
   membership, interface ownership is an arity check on declared contracts. **3 of the
   compiler's 5 obligations are buildable today.** The other 2 — HARD-constraint
   coverage and duplication — need an oracle the document never supplies ("entail"
   and "decidab" occur 0 times in 624 lines, and §8.8 specifies dedup *negatively*,
   by forbidding lexical similarity and naming no replacement). The compiler is a
   specification for three fifths of itself and a wish for the rest; that is a
   scoping problem, not a fatal one, and Phase B should build the 3 and route the 2
   to an explicit oracle-or-human WorkUnit.
5. **§10's judgement on `bench/dm/_load_balancer.py` is correct** and consistent with
   this project's own additive standard: it is shelved, not live, and the spec
   proposes a replacement with committed invariants rather than a rewrite-by-assertion.
6. **§12's disconfirmation rules are pre-registered and genuinely disconfirming** —
   rule 2 in particular concedes the scheduler in advance if the flat panel is not
   beaten at matched budget. That is the part of this document that most deserves
   to go on the runway.

---

## A dependency risk the spec cannot be blamed for, but the founder must price

The spec is dated **2026-09-14** and declares that it *"CONSUMES the canonical
mathematics without redefining it."* `docs/MATHEMATICAL_APPENDIX.md` has **7 commits
after that date**:

    ea43d3f 2026-09-29 Apply both of Astra's corrections; assess its distributed-compute spec
    d6eeb90 2026-09-29 Retract the invented Wolfram denial rule; explorer A-vs-M; I31 cannot fire
    2b56916 2026-09-21 The panel corrected 2 of my claims and found a gamma demotion in the appendix
    e61a83c 2026-09-21 Astra landed 3 correct hits; 1 of my claims is withdrawn ...
    0a4a491 2026-09-21 Mark the 7.12 confound the founder ruled on, and correct my own first draft
    b509a44 2026-09-21 I attacked the maths model's Phase 2 and lost; 3 corrections landed
    8a0952a 2026-09-18 appendix: the coverage-to-risk inverse at line 169 was the NEGATIVE of the inverse

**Two of those touch the exact quantity §6.1 uses.** `d6eeb90` (A-vs-M) is why FIX 3
exists; `b509a44` established that the `σ=1, ν=0` corner overstates the expected
improvement everywhere else. So FIX 3 is not a drafting error by the spec's author —
**the appendix moved under it, 15 days after it was written, on the one equation it
depends on most.** That is the real structural cost of a layer that consumes a live
model by reference: it inherits the model's revision rate. The mitigation is cheap
and belongs in §6.1: pin the consumed appendix by commit hash and require the
transcription to be executed against `compute_rk` in CI, so the next appendix
revision breaks a test instead of silently invalidating a scheduler.
