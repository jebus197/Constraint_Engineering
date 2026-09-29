# The Adaptive Distributed-Compute Spec: Sound Foundation, Two Superseded Quantities

**2026-09-29, 13:45 BST.** Audience: a reproducing engineer. Plain-English companion at `~/Desktop/CDSFL_tts/Adaptive_Distributed_Compute_Assessment_2026-09-29.txt`. Producer for every figure below: `scripts/adaptive_spec_estimator_audit_2026-09-29.py`, held by `bench/tests/test_adaptive_spec_estimator_audit_2026-09-29.py` (12 tests).

**Artefact reviewed:** `Responses/Codex, ChatGPT & Grok resources/adaptive_distributed_compute_design_spec.md`, 624 lines, dated **2026-09-14**. It proposes an allocation and topology layer above the canonical model — a scheduler that ranks candidate dispatches by predicted reduction in residual risk per unit of constrained resource.

---

## 1. It is not running on disproven maths. It is running on maths its own author later superseded.

The appendix line **"ΔR_k IS THE WRONG QUANTITY FOR THIS DECISION"** was added on **2026-09-21** in commit `e61a83c`, whose title is *"Astra landed 3 correct hits"* — **7 days after the spec was written, by the same reviewer**. The spec has never been re-run against the correction it helped produce.

**The foundation is intact.** Since 2026-09-14, **0** commits have touched the `1−qR` form, `S_k = A·E`, or `D(n)`, and `b509a44` records *"3 corrections landed, 0 equations changed."*

**Its claims about this repository are all accurate**, checked individually: `bench/dm/_load_balancer.py` exists and is shelved with its own `test_load_balancer_shelved.py`; the Ising/Boltzmann ψ branch sits at `docs/MATHEMATICAL_APPENDIX.md:23` with exactly the reduction property the spec describes; `PM`/`COL`/`PAR` are in `bench/dm/_failure_handler.py`. Its own arithmetic is exact — `1−(1−0.45)(1−0.35) = 0.6425` and a marginal of `0.1925`, both confirmed symbolically — and `D_u(n)` is submodular as §6.6 asserts (SymPy: the marginal difference factors to `p₁p₂(1−p₀) ≥ 0`).

---

## 2. Defect 1 — the scheduling estimator is the conditional quantity

| | form |
|---|---|
| Spec §6.1 | `g = R − R_next`, `R_next = [σ·R_det + (1−σ)·R](1−ν) + ν` |
| Appendix, 2026-09-21 | `E[improvement] = R·q·σ·(1−ν) − ν·(1−R)` |

They differ by `R²qσ(1−ν)(1−q)/(1−qR)`, and the spec's value is **always the smaller**: Wolfram `Resolve[ForAll[{R,q,σ,ν}, dom], gSpec ≤ gExp]` → **True**, SymPy agreeing. *Computed with Wolfram Language.* At `R = 0.99` it reports **0.0028** where the correct value is **0.2663** — a factor of 95.

Because the gap is R-dependent it does **not** cancel in a ranking, and a scheduler ranks units against one another. `score = ĝ/(c + λ_t t + λ_h h)` therefore systematically under-scores the highest-risk work. This is the appendix's own premature-stop band wearing a scheduler's clothes.

---

## 3. Defect 2 — the state update is not the live runner's

The spec uses a single scalar ν. `bench/reference_runner_v3.py:compute_rk` composes **two**:

> `nu_eff = 1 − (1−nu_b)·(1−(1−sk)·nu_f)`

so re-injection depends on fix efficacy. Wolfram `Reduce[domain && liveNext == specNext, σ]` → **False** (never equal for σ<1) and `Resolve[ForAll[...], specNext ≤ liveNext]` → **True**: the spec **understates residual risk**, optimistic exactly when repair is imperfect. *Computed with Wolfram Language.* Verified against the shipped function itself at three parameter points to 1e-12.

---

## 4. A correction to this assessment's own first figure

The ranking-inversion rate was first reported as a single number, **7.9630%**, measured under **uniform** sampling of `(R, q, σ, ν)`. That is a property of an arbitrary prior, not of this project's runs. Re-measured across 6 priors, 60,000 unit pairs each:

| prior | rate | Wilson 95% |
|---|---:|---|
| uniform (first reported) | 7.9567% | [7.7428%, 8.1759%] |
| **high-risk regime R>0.8** | **14.9433%** | [14.6603%, 15.2308%] |
| low-risk regime R<0.4 | 1.7033% | [1.6028%, 1.8100%] |
| near-perfect repair σ>0.9 | 11.9017% | [11.6450%, 12.1632%] |
| no re-injection ν=0 | 16.4533% | [16.1588%, 16.7521%] |
| runner default nu_b=0.05 | 10.4900% | [10.2473%, 10.7377%] |

Intervals computed twice, statsmodels against a direct Wilson closed form, agreeing to better than 1e-12; z3 returns `sat` on the inversion constraint independently.

**The range is 1.70% to 16.45%, and the headline was the uniform row.** In the high-risk regime — where a scheduler's decisions matter most — the rate is roughly **double** the headline. So the defect is *worse where it counts* while the headline figure is an artefact of its prior. **UNMEASURED, and unmeasurable from the current archive.** How often the spec's estimator would misorder *real* scheduling decisions cannot be computed here at all: it would need the observed joint distribution of `(R, q, σ, ν)` across live runs, and no archived run reports those 4 together. This is recorded as a named gap rather than filled with a figure from an assumed prior.

---

## 5. Disposition

**Viable, and unusually well-disciplined.** Shadow-first operation, explicit promotion gates, pre-registered disconfirmation rules, and §12 rule 1 states that if a strong single agent matches the panel the *panel claim should be narrowed*. It is built to be able to refute its own premise.

**It proposes the right instrument for the diversity question rather than answering it.** The most distinct models in any archived run of ours is **6**; the spec proposes a staged curve at 1, 2, 4, 8, 16, 32 with duplicate-seat and same-vendor-varied-tool controls — the control set that separates "diversity" from "more attempts", which this project has never been able to separate.

**Runway placement.** Its own Phase A says finish Exp 56 first and do not substitute this in, which matches our position.
- **Phase B** (WorkUnit / InterfaceContract / EvidencePacket schemas) costs nothing and needs no dispatch — placeable immediately after the simulated shakedown.
- **Phase D** (matched-budget topology experiment) is the paid arm and belongs after BR2, against a founder-set budget: 6 conditions × 6 scale points × ≥3 seeds is a large number of paid dispatches.

**Two things that must not be conflated:** a *paid panel review of the spec document* (hours, modest) and *Phase D* (tests whether adaptive allocation works). Only the second bears on whether distributed compute pays.

**Next step, founder-approved 2026-09-29:** a **free** panel review (`cc2`, `fable`; `FREE_SEATS` — no authorisation needed) run **blind on the unfixed spec**, under neutral framing per `feedback_framing_confound`, with precedent at `scripts/panel_blind_cc_2026-09-20.py`. Concurrence is explicitly *not* the goal — under `feedback_no_model_voting` agreement confirms nothing that SymPy, z3 and Wolfram have not already settled. The panel is pointed at what this assessment bounded out (the cost/latency model, WorkGraph compiler feasibility, §9.3 sample-size adequacy, whether the §9.4 gates are checkable) and at §4's prior-dependence. Running it *before* the fix is deliberate: whether independent tool-enabled seats find the conditional-ΔR error on their own is itself evidence about the method's sensitivity, and fixing first would destroy that signal.

**Known risks:** both free seats died on OAuth expiry earlier on 2026-09-29; the panel parser drops ~10.3% of real replies (measured 2026-09-01), so an absent finding is not reliably a finding not made.

**Bounded:** this assessment did not examine the cost/latency model, whether the WorkGraph compiler is buildable, or §9.3 sample-size adequacy.
