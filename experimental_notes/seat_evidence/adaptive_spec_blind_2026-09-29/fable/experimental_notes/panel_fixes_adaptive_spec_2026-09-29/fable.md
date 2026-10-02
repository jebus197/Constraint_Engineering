<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'adaptive_spec_blind_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 49b16e7f77f6fd95c75cabfe4d0d61928635bfa63328ad0260b5297304bc2d4e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Panel fixes: adaptive distributed-compute design spec (2026-09-14)

Seat: **fable** · Blind round, 2026-09-29.
Falsifier (executed, exit 0): `scripts/panel_adaptive_spec_falsifiers_2026-09-29.py`.
All identities cross-checked on SymPy and Wolfram Language (local kernel, `{0,0,0}`, exit 0). *Computed with Wolfram Language.*

The specification lives outside the repository; corrected passages are delivered here.

---

## FIX 1 — §6.1: the re-injection phase must be the S_k-coupled bounded form

**Original (§6.1):**

> R_next = [σ̂_muk R_det + (1−σ̂_muk) R_{u,k}(r)] (1−ν̂_muk) + ν̂_muk

**Replacement:**

> R_next = [σ̂_muk R_det + (1−σ̂_muk) R_{u,k}(r)] (1−ν̂_eff) + ν̂_eff
>
> where ν̂_eff = 1 − (1−ν_b)(1 − (1−σ̂_muk) ν_f), with ν_b + ν_f ≤ 1 enforced by
> rescaling, exactly as in `cdsfl_operational.md` §3 and
> `bench/reference_runner_v3.py:compute_rk`. The re-injection estimate is NOT a
> free per-configuration parameter: it is a declared function of the same
> σ̂_muk used in the resolution phase, through the fixed policy constants
> (ν_b, ν_f). A scheduler that calibrates ν̂_muk independently of σ̂_muk is not
> predicting the canonical update. R_det additionally requires the runner's
> guard: when |1 − q̂R| < 1e-12, R_det = R_{u,k}(r).

**Why (measured):** with ν̂ free, the best possible *constant* ν̂ (0.14) mispredicts
`compute_rk` by up to **0.0736** in R_next, and by >0.01 at **522/729 = 71.6%**
(Wilson95 [68.2%, 74.8%], uniform grid — operational (R,q,σ) distribution unknown)
— an error the size of typical per-pass gains, injected into every g_muk. With
ν̂ = ν_eff(σ̂) the two forms agree to 0.0 over the grid (F1a). SymPy:
spec_form − runner_form = (ν̂ − ν_eff)(1 − R_base); Wolfram Language returns 0
for the same difference.

---

## FIX 2 — §6.1 closing paragraph: gate-failed is NEGATIVE credit, not zero

**Original:**

> A candidate that cannot satisfy an applicable verification gate may be
> valuable as discovery, but it receives **zero verified-risk-reduction
> credit** until an admissible verifier supplies evidence.

**Replacement:**

> The S_k = A·E boundary is tri-state and the scheduler must predict all three
> outcomes distinctly, as `apply_sk_to_rk` enforces them:
> 1. **No applicable gate (NO_SCORE):** zero *movement* — R_next = R exactly.
>    "Not scored" and "scored zero" are different statements.
> 2. **Applicable gate, fix fails (S_k = 0):** **negative** credit. The
>    canonical update sets ν_eff to its maximum (ν_b + ν_f − ν_b ν_f = 0.24 at
>    defaults) and residual risk RISES: compute_rk(0.5, 0.5, 0.0) = 0.62, a
>    credit of −0.12. A scheduler crediting zero here under-penalises
>    configurations whose fixes fail gates, and will over-dispatch them.
> 3. **Applicable gate, fix admitted (S_k > 0):** the coupled update of Fix 1.

**Why (measured):** F2 in the falsifier, run against the shipped functions:
gate-failed R 0.5 → 0.6200 (credit −0.1200); NO_SCORE R 0.5 → 0.5000 (credit 0).

---

## FIX 3 — §6.1: the routing estimator must use the pre-branch EXPECTATION, not the gate's conditional blend

The spec (2026-09-14) predates the appendix entries of 2026-09-21 and
2026-09-29 (`git log` on `docs/MATHEMATICAL_APPENDIX.md`: 8a0952a, b509a44…,
ea43d3f), which rule: the three-phase blend is the **gate** quantity, retained
for gate compatibility; a decision taken **before** the branch is known needs
the branch-weighted expectation — now shipped as `compute_rk_expectation`
("the quantity an explorer needs BEFORE a run"), with exact gain
E[improvement] = R·q̂·σ̂·(1−ν̂_eff) − ν̂_eff·(1−R).

A dispatch decision is exactly such a pre-branch decision. Using the blend:

- **understates** the value of passes on high-risk units by up to **70.3×**
  (R = 0.99, q = 0.3: conditional gain 0.004225 vs expectation 0.2970 — F3c,
  appendix figures reproduced against the shipped code);
- inherits the appendix's **premature-stop band** (θ = 0.05 says STOP across
  R ∈ [0.855, 0.9999] at q = 0.3), which bites §7.1 step 9's stopping rule at
  the highest-risk states;
- **mis-ranks candidates**: within a unit the blend ranks by σq/(1−qR)
  (SymPy + Wolfram: gain = σqR(1−R)/(1−qR)), the expectation by σq, so the
  blend overweights high-q̂/low-σ̂ configurations. Executed reversal (F3a,
  shipped functions, R = 0.9): X(q=0.9, σ=0.4) beats Y(q=0.5, σ=0.8) under the
  spec's g (0.1262 > 0.0509) while Y beats X under the expectation
  (0.3195 > 0.2545). Reversal rate under a uniform draw: 619/20000 = **3.09%**
  (Wilson95 [2.86%, 3.34%]); the operational distribution is unknown, and at
  high R (where dispatch matters most) reversals concentrate.

**Replacement for the g_muk definition:**

> g_muk = R_{u,k}(r) − E[R_next] where E[R_next] is computed by
> `compute_rk_expectation(R, q̂, σ̂)` — equivalently
> g_muk = R·q̂·σ̂·(1−ν̂_eff) − ν̂_eff·(1−R). The observed post-dispatch state
> continues to be updated by the canonical gated `compute_rk`; the expectation
> is a routing estimate only and is never written into the claim state,
> matching the runner's REPORTED-NEVER-GATED boundary.

---

## FIX 4 — §6.4: cold start, units, and an unbounded score

Three well-posedness defects, all executed (F4a, F4b):

1. **e_mu = √(log(1+N_u)/(1+n_mu)) is identically 0 when N_u = 0** — every
   configuration gets zero exploration bonus precisely when nothing has ever
   been observed, so the first dispatches in a task family are pure
   exploitation of uncalibrated priors. (UCB-style terms force initial
   exploration; the +1 smoothing and log(1+·) here remove exactly that.)
2. **The score is unbounded as c_mu + λ_t t_mu + λ_h h_mu → 0** (measured 1e8 at
   c = 1e-9): a near-free tool pass dominates every dispatch regardless of g.
3. **Units are incoherent:** the first term is [risk-reduction]/[money] (λ_t,
   λ_h convert time and human burden to money); βe_mu is dimensionless. β must
   therefore carry [risk-reduction/money] units; the spec calls it "an explicit
   policy value" with no units, so two implementations can agree on β = 0.3 and
   disagree by the currency.

**Replacement:**

> score(m,u|A) = (ĝ_mu + β e_mu) / max(c_mu + λ_t t_mu + λ_h h_mu, c_floor)
>
> with: c_floor > 0 a declared policy constant (units: money); β in units of
> predicted risk-reduction, i.e. the bonus is added to the numerator, making
> the whole score [risk-reduction/money]; and e_mu redefined with an optimistic
> cold start, e.g. e_mu = √(log(1+max(N_u,1))/(1+n_mu)) is NOT sufficient
> (still 0 at N_u=0 via log 1=0) — use e_mu = √(log(e+N_u)/(1+n_mu)) so
> e_mu > 0 at N_u = 0, or grant each configuration one forced exploratory
> dispatch per family before scoring applies. λ_t [money/second] and
> λ_h [money/human-minute] must be published with units.

---

## FIX 5 — §9.2/§9.3: state the design's minimum detectable effect

**Original (§9.2):** "At least three independently seeded or held-out runs per
condition are needed before comparing small differences."

**Replacement:**

> Three runs per condition is a floor for *estimating variance*, not for
> comparing conditions. Executed power analysis (statsmodels TTestIndPower):
> at n = 3 per condition, α = 0.05 two-sided, power 0.8, the minimum
> detectable effect is **Cohen's d ≈ 3.07** — and **d ≈ 4.80** after
> Bonferroni correction over the five comparisons against the adaptive arm
> implied by §9.2's six conditions. A 3/3 success proportion carries Wilson95
> [0.439, 1.000]. The staged curve (6 scales × 6 conditions × 3 seeds = 108
> runs) therefore has power only for enormous effects. Pre-register the
> expected effect size and compute n per condition from it; for d = 1.0 at the
> same α/power, n ≈ 17 per condition (n ≈ 23 Bonferroni-corrected). If the
> per-run cost makes that infeasible, say so and report estimation-only
> results with intervals, not comparisons.

---

## FIX 6 — §9.4: make two of the four promotion gates machine-checkable

As written, a program can evaluate Library ("unit, property, and adversarial
tests" — a test suite exit code) and the invariant halves of Shadow and
Controlled live ("no target or budget mutation", "no invariant breach" — §8
invariants are checkable). It cannot evaluate "counterfactual comparison"
(compared how, passed when?), "matched-budget improvement" (which metric, what
threshold, what test?), or "replicated benefit" (how many replications?).

**Replacement (add to §9.4):**

> Each gate names its statistic, threshold, and decision procedure in advance:
> - **Shadow → Controlled live:** on ≥ N pre-registered archived runs, the
>   shadow allocator's recommended dispatch sequence, replayed against
>   recorded outcomes, yields a §9.1 primary-outcome estimate whose
>   pre-registered lower confidence bound is ≥ the legacy policy's observed
>   value at equal recorded cost; zero §8 invariant violations in the log.
> - **Controlled live → Operational:** MarginalVerifiedYield (§9.3) of the
>   adaptive arm exceeds the flat baseline's at matched budget in ≥ 2 of 3
>   independently seeded suite runs, with the difference's pre-registered
>   interval excluding 0, and false-confirmation count not higher.
> The N, interval method, and thresholds are frozen before the first gated
> run. A gate whose criterion cannot be evaluated by a program plus a scoped
> human sign-off is not a gate; it is a mood.

---

## FIX 7 — §4.1: "checked for coverage of HARD constraints" — define the check

The compiler as specified is buildable **as a validator**: acyclicity
(topological sort), unresolved dependencies (closure over ids), interface
ownership (each InterfaceContract references ≥ 2 units and one owner), target
hashing — all mechanical. Two named checks have no defined mechanism:

1. **HARD-constraint coverage** is only decidable as a *syntactic mapping*
   (every h ∈ H appears in ≥ 1 unit's hard_constraints). Whether the unit's
   acceptance method actually *tests* h is semantic and has no oracle in the
   document.
2. **Duplication** cannot use lexical similarity alone (§8, invariant 8), and
   no admissible identity mechanism is specified for proposed units.

**Replacement (amend §4.1 closing paragraph):**

> …the resulting graph must be checked for: syntactic coverage of HARD
> constraints (every h ∈ H is referenced by at least one unit whose
> oracle_options field names a mechanism purporting to test it — the mapping
> is mechanical; whether the mechanism suffices is a Verification-plane
> question and is itself a work unit), duplication under the audited identity
> mechanism of §8 invariant 8 (claim-key equality, not lexical similarity),
> unresolved dependencies, and interface ownership. The compiler proves graph
> well-formedness; it does not prove task coverage. Uncovered-constraint and
> unowned-interface conditions are REFUSE-to-dispatch, not warnings.

---

## Sound, and said so

- **§6.2 D(n):** the transcription matches PAPER.md Part XIII's general
  multi-class form exactly; the worked example is exact (1−0.55·0.65 =
  257/400 = 0.6425; increment 77/400 = 0.1925; F6, Fraction arithmetic). The
  conditional-increment Δ(m|A) definition is the correct generalisation of
  Part XIII's marginal gain.
- **§6.3:** the Ising transcription matches appendix §0.1 term for term, with
  a clean rename (f_a for failure probability) that *avoids* the appendix's
  own overload of q. Declining to fit ψ couplings early is consistent with the
  appendix's finding that the all-ones normalisation constraint is
  insufficient for n ≥ 3.
- **§6.1 q̂ = η̂·d̂·p̂:** matches `compute_rk_with_eta_channel`'s composed
  q = η_combined·d·p, and the ban on a second novelty multiplier matches the
  channel rule (m_div on η_int only).
- **§6.6:** correctly refuses a submodularity guarantee for the full
  objective; correctly claims it for fixed-event coverage.
- **§6.5, §10:** feasibility-refusal and the shelved-load-balancer reading
  match the additive standard; redundancy floor r_u ∈ {1,2,3} is policy, not
  maths, and is stated as such.

