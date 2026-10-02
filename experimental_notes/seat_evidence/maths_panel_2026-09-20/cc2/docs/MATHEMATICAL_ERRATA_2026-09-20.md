<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'maths_panel_2026-09-20', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 421ff0cda65e2a934a74c2872a5dfbf8dad6767bb6d7b8594809c7b35ca620f6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Mathematical errata, 20 September 2026

Corrections arising from the panel review of the version 1.1 revision proposal
(`docs/maths_revision_review_2026-09-10/`). Each item names the artefact
corrected, the corrected statement, and the runnable falsifier that decides it.
Notation follows `docs/MATHEMATICAL_APPENDIX.md` throughout.

Nothing here is a new parameter. Every correction is to a quantity that already
exists in the appendix or in the panel brief.

---

## E1. The flat-curve residual is nu/(q+nu), not nu/q

**Corrects:** `PANEL_BRIEF_2026-09-20.md` 3.4, which states R* = b/p and
reports 5.71% / 28.57% / 57.14% at p = 0.35.

b/p is the fixed point of the **unconditional** recursion R <- (1-q)R + b, in
which introduction is applied to the whole state. Neither the revision nor the
existing appendix uses that recursion. Both apply introduction to the **clean
fraction**:

- revision, section 4:  R_next = nu + (1-nu)(1-sigma)B
- appendix, line 233:   R_k(i) = R_base*(1-nu) + nu

whose fixed point is

> **R* = nu / (q + nu)**

| nu | brief's nu/q | correct nu/(q+nu) | overstatement |
|---:|---:|---:|---:|
| 0.02 | 5.71% | **5.41%** | 0.30 pp |
| 0.10 | 28.57% | **22.22%** | 6.35 pp |
| 0.20 | 57.14% | **36.36%** | 20.78 pp |

The error is in the **conservative** direction -- the brief overstates residual
risk -- so no stopping decision taken on it was unsafe. The **qualitative** claim
that a flat decay curve is compatible with a large residual **survives**: at
nu = 0.20 the correct residual is still 36.36%.

This is the same quantity the appendix already names in its substrate-ceiling
result (line 248, lim R >= nu_k). E1 makes that bound exact rather than
one-sided: the limit is not merely >= nu, it is nu/(q+nu).

**Falsifier:** `python3 scripts/cc_falsify_section3_2026-09-20.py`
-> `18/18 checks passed`, including
`3.4 REFUTED as stated: the revised model's own fixed point is b/(p+b), NOT b/p`.
Independently confirmed by Wolfram Language (local Wolfram Engine):
`Solve[(1-p) R + b (1-R) == R, R]` -> `{{R -> b/(b + p)}}`.

---

## E2. The degeneracy is a line only at interior targets

**Corrects:** `PANEL_BRIEF_2026-09-20.md` 3.1, "the degeneracy is a line, not a
point."

True, and the (s, b) formula is right, but not uniformly. The admissible set is
the line b(s) = (d - (1-s)z)/(1-z) **intersected with the unit square**. Its
Lebesgue measure in s shrinks to zero as the target d approaches 0 or 1:

| target d at z = 0.25 | measure of admissible s |
|---:|---:|
| 0.5 | 1.000000 |
| 1.0 | **0.000000** (unique point s = 0, b = 1) |
| 0.0 | **0.000000** (unique point s = 1, b = 0) |

The practical reading is the one that matters for falsifiability: the fitting
freedom is **greatest in the middle of the risk range and vanishes at the
extremes**. A model fitted to a mid-range target is the maximally unfalsifiable
case, not a typical one.

**Falsifier:** same script, checks
`3.1 COUNTEREXAMPLE: at d=1 the solution set collapses to a POINT` and the d=0
counterpart (measure 0.00e+00, brute-force grid 0.000050 of 20001 points).

---

## E3. The removal parameter s adds no reachability; the whole degeneracy is b's

**Adds to:** `PANEL_BRIEF_2026-09-20.md` 3.2.

The brief compares the existing collapse form over p (reaching [0, R]) with the
revised action step over (s, b) (reaching [0, 1]) and concludes correctly that
the introduction term carries the degeneracy. The result is stronger than
stated. Let p vary too, and set b = 0:

> sup over s in [0,1], p in [0,1] of (1-s)*R(1-p)/(1-pR) = R, attained at s = 0, p = 0;
> infimum 0.

So the revised model **with b = 0 but s free reaches exactly the existing
model's set [0, R]** -- s is reachability-redundant given the existing model's
own free parameter. Every outcome the revision can reach that the existing model
cannot is reached **by b alone**.

**Consequence for adoption:** if b = nu cannot be estimated, adopting the revised
parameterisation adds no reachable outcome and no content -- only a second name
for a freedom p already had.

**Falsifier:** same script, check `3.2+ s is REACHABILITY-REDUNDANT`.
Wolfram Language independently:
`Maximize[{(1-s)(R(1-p)/(1-p R)), 0<=s<=1 && 0<=p<=1 && 0<R<1}, {s,p}]`
-> maximum `R` at `s -> 0, p -> 0`.

---

## E4. Appendix Phase 2 does conflate observation with repair -- and it errs SAFE

**Concerns:** `docs/MATHEMATICAL_APPENDIX.md` line 226,
R_base = sigma*R_det + (1-sigma)*R_old.

The revision is right that this conflates the two operations. A failed fix does
not un-observe the evidence, yet this form returns the state to the **prior**
R_old with probability (1-sigma). The root cause is a different reading of
sigma: the appendix treats sigma as *how much of the detection benefit is
captured*, so that even a perfect fix (sigma = 1) leaves risk at R_det rather
than at nu.

> appendix at sigma = 1:  R_det(1-nu) + nu
> revision at sigma = 1:  nu

**But the direction of the error is the safe one.** Writing the revision's form
as `correct`:

> existing - correct = (1-nu)*[ sigma*R_det + (1-sigma)*(R_old - R_det) ] >= 0

identically, since R_det <= R_old always. Verified on 8151 grid points with zero
negative cases, and **proved universally** by Wolfram Language:
`Reduce[ForAll[{R,q,sigma,nu}, 0<R<1 && 0<q<1 && 0<=sigma<=1 && 0<=nu<=1, d >= 0]]`
-> `True`.

**Therefore this correction MUST NOT be adopted as a drop-in.** The existing form
systematically **overstates** residual risk -- by up to 0.46 absolute at
sigma = 0.8, nu = 0.1. Replacing it lowers every reported R_k, which makes every
risk-threshold stop **easier** to satisfy. Under the additive standard that is a
removal of a safety margin, and it requires a committed measurement of sigma and
nu showing the replacement dominates -- not a derivation showing it is better
conditioned.

**What IS adoptable now:** the appendix should state, at line 226, that this form
is a conservative approximation and name its bias term. That is additive: it
adds an accuracy statement and removes nothing.

**Falsifier:** `python3 scripts/cc_phase2_conflation_2026-09-20.py`
-> `9/9 passed`, including `Q-B existing >= correct EVERYWHERE (8151 grid points)`
and `Q-B PROOF: existing-correct = (1-nu)[sigma*R_det + (1-sigma)(R_old-R_det)] >= 0`
(residual 0).

---

## E5. Two existing appendix results are confirmed correct and need no revision

Recorded because a review that only reports faults misrepresents the artefact.

- **Break-even re-injection rate** (line 240), nu* = sigma*q*R/(1 - q*R*(1-sigma)),
  is **exactly** what SymPy obtains by solving R_cycle = R_old for nu using the
  appendix's own Phase 2 and Phase 3. It is correctly derived from its own
  premises.
- **Substrate ceiling** (line 248), lim R >= nu_k, holds at every tested
  (R, q, sigma, nu). E1 sharpens it to an equality but does not contradict it.

**Falsifier:** `python3 scripts/cc_phase2_conflation_2026-09-20.py`, checks
`Q-A appendix break-even nu* is CORRECTLY derived from its own phases` and
`Q-A appendix substrate ceiling`.

---

## E6. The introduction parameter is already in the appendix under the name nu

**Concerns:** the claim that the revision *adds* an introduction parameter.

It does not. The appendix's Phase 3 (line 233), R_k(i) = R_base*(1-nu) + nu, is
**algebraically identical** to the revision's action step (1-s)B + b(1-B) at
s = sigma(1-nu), b = nu. The revision's own reference implementation says so:
`sequential_repair_parameters(sigma, nu)` in `CDSFL_revised_core.py` returns
exactly `(sigma(1-nu), nu)`.

The revision's contribution at this point is **the conditioning statement, not
the parameter**: that s is *net* removal and must not be interchanged with raw
efficacy sigma, and that s and b must share the evidence, context and action
they are conditioned on. That is a documentation correction of real value. It is
not new mathematics and it must not be presented as one.

**Falsifier:** same script, checks
`Q-A EXISTING appendix Phase-3 IS the revision's own action step` (SymPy
residual 0) and `Q-A package helper returns s=sig(1-nu), b=nu` (`s=18/25 b=1/10`
exact).

---

## E7. The two-sided gate does not close the nu-hole; it closes it to 1.5%

**Concerns:** `PANEL_BRIEF_2026-09-20.md` 3.5, "the existing two-sided gate
already refuses that case."

The gate's condition (a) counts **novel critical findings**, i.e. *detected*
defects. Residual risk is driven by *undetected* introduced defects. The gate
therefore sees injection only through the same review's sensitivity to the
**injected** class. Measured against the real `_check_gamma_alt_convergence`
with the live `RunnerConfig` (K = 3):

| scenario | gate converges | equilibrium residual nu/(q+nu) |
|---|---:|---:|
| injected class seen at q = 0.35 | 89.84% (Wilson 95% [89.71, 89.97]) | 22.22% |
| injected class seen at q' = 0.05 | **98.50%** (Wilson 95% [98.45, 98.56]) | **66.67%** |

Closed form for the blind spot: (1 - nu*q')^K, giving 98.5075% at nu = 0.10,
q' = 0.05, K = 3 -- inside the Wilson interval. Gate detection power against
injection is **1.49%**.

The brief's 3.5 demonstration used a *deterministic* 2-criticals-per-round
series, which is the easy case. At a realistic stochastic injection rate the
gate's power is low even when the injected class is fully visible, and
negligible when it is not.

**This is not a proposal to change the gate**, which is two-sided by design and
correct at what it measures. It is a statement of its measured power, which
belongs in its docstring so that a reader does not mistake "the gate is
two-sided" for "the gate detects regression."

**Falsifier:** `python3 scripts/cc_gate_low_sensitivity_2026-09-20.py`
-> reproduces all four of the brief's 3.5 control cases against the real
function, then reports the constructed case with a Wilson interval containing
the closed form.

---

## Producers

| File | Decides |
|---|---|
| `scripts/cc_falsify_section3_2026-09-20.py` | E1, E2, E3 (18 checks) |
| `scripts/cc_phase2_conflation_2026-09-20.py` | E4, E5, E6 (9 checks) |
| `scripts/cc_gate_low_sensitivity_2026-09-20.py` | E7 (400 000 simulated rounds, Wilson interval) |

Every symbolic result above was obtained with SymPy and independently confirmed
with Wolfram Language (local Wolfram Engine, via `wolframscript`); every numeric
result was cross-checked with mpmath at 40-50 decimal places. Proportions carry
Wilson intervals from `statsmodels`.

---

## E8. nu is not measurable at the model's scope — but a baselined channel exists and is being discarded

**Answers:** panel brief question 2, the decisive empirical question.

**At the scope the model needs, nu is unidentifiable.** b = P(post flawed | pre
**clean**, action) requires a denominator of clean targets that a repair touched.
This archive never enumerates one, because four independent instruments *refuse
by construction* to admit a clean pre-state:

| instrument | refusal |
|---|---|
| `bench/fix_efficacy.py:175` | non-CONFIRMED baseline -> `INDETERMINATE_NO_BASELINE`, "there is nothing for a fix to cure" |
| `bench/execution_based_matcher.py:137` | `BASELINE_STATE = "pristine"`, both members must CONFIRM |
| `scripts/adjudicate_by_repair.py:46` | a pair is decided only when BOTH falsifiers reproduce CONFIRMED |
| `scripts/discrimination_control_archive.py:38` | if no version reproduces it, the finding is EXCLUDED |

Counted: **246** independently-resolved (pre, post) pairs exist for the
**removal** direction s; **0** for the **introduction** direction b. No field
named `pre_fix_verdict`, `clean_baseline`, `verified_clean`,
`introduction_rate` or `nu_measured` exists anywhere in `bench/`. nu is
currently **assumed, never estimated** — `SHIPPED_NU_B, SHIPPED_NU_F = 0.05,
0.20`, and `model_params` has 0 writers.

**But a narrow, already-running, already-baselined channel does exist.** The e3
and e4 effect gates *do* take a pre-fix baseline and report a delta
(`delta = max(0, total_count - baseline_violations)`). That delta is a genuine
clean-to-flawed transition within the gate's own scope. Measured over the live
archive:

> **e3_ruff introduction events: 20/65 = 30.77%, Wilson 95% [20.89%, 42.80%]**

Implied equilibrium residual at q = 0.35, using E1: **R\* = 46.78%**
(Wilson upper 55.01%). This is a lint-scope number, not an any-flaw-in-class
number, and it must not be quoted as the latter. It is nevertheless the first
executed, non-assumed estimate of an introduction rate in this project.

**And the heaviest gate is one function call away from joining it.**
`e2_regression` carries weight 2.0 — twice e3's — and is the only effect gate
with **no baseline**, although the enclosing scorer already receives a
`baseline` argument. AST-confirmed: `_run_effect_regression(modified_source,
source_path, test_cmd)` is called with `modified` only. Consequently the 70
deduplicated e2 records in `bench/logs/` — of which **44 are RED** — cannot be
decomposed into pre-existing failures and fix-introduced ones. 44/70 is an
unidentified mixture and **must not be reported as nu**.

**Fix, additive, no new parameter and no new flag:**

```python
# bench/reference_runner.py, beside the existing e2 call
e2b_score, e2b_detail = _run_effect_regression(source, source_path, test_cmd)
details["e2_baseline"] = {"score": e2b_score, "detail": e2b_detail}
```

Then, with no new symbol:

> introduction event  <=>  `e2_baseline.score == 1.0` and `e2_regression.score < 1.0`
> nu_hat = (introduction events) / (fixes whose baseline suite was green), Wilson interval.

This satisfies the brief's hard constraint — do not add a parameter without
saying how it would be measured — by measuring a parameter the appendix has
carried since line 215 and never measured. It is wired to an existing caller and
exercised by an existing archive.

**Falsifier:** `python3 scripts/cc_nu_measurability_2026-09-20.py`
-> `ALL CHECKS PASSED`, exit 0. Checks A1-A3 (no clean pre-state admitted),
B1-B3 (e3 baseline present, 20/65 measured), C1-C3 (e2 baseline absent, the gap
is one call).
