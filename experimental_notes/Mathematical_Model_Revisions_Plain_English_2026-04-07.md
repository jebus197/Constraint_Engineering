# Mathematical Model Revisions in Plain English

**Date:** 7 April 2026
**Context:** Plain English explanation of the five structural gaps identified in `MATHEMATICAL_APPENDIX.md` against Exp 29–36 experimental evidence. Technical detail in `Exp36_Mathematical_Model_Audit_2026-04-07.md`.

---

## What This Is About

The mathematical appendix (1081 lines) was declared internally coherent on 31 March after an 8-round audit (6 models, 39 SymPy checks, all passing). The algebra is sound. The reductions are correct. The problem is not that the maths is wrong. The problem is that the maths models individual components, while Experiments 29–36 revealed system-level behaviours that emerge from component interactions. The appendix has no metrics for those emergent behaviours.

Five structural gaps were identified. They are not independent. They form one coupled failure cascade.

---

## The Five Gaps

### Gap 1: γ Classifies Wrong at the System Level

**What γ is.** The convergence parameter from the Duane reliability growth model. It measures how quickly the rate of discovering novel findings is decelerating. γ > 0 = convergence (error space exhausting). γ ≈ 0 = churn (constant rate, no depletion). γ < 0 = divergence (accelerating discovery).

**What went wrong.** In Exp 36, γ = 0.411 — firmly positive, classified as "convergence." But the system was churning at a 17:1 dedup ratio. 153 canonical findings collapsed into ~9 actual bugs.

**Why.** γ is computed from cumulative novel findings only. It correctly measures that the novel discovery rate is decelerating. But it cannot see how much raw output was produced to generate those novel findings. A round with 33 raw and 5 novel looks the same to γ as a round with 5 raw and 5 novel. The first is churning. The second is efficient. γ cannot tell them apart.

**Analogy:** Measuring a factory's productivity by counting only the good products leaving the loading dock. Output is declining, so you conclude the factory is winding down. But you never checked the reject pile. The factory is producing just as much as ever — most of it defective.

### Gap 2: ρ Is Not Formalised

**What ρ is.** Discovery efficiency: novel/raw. Of everything the models produced this round, what fraction was genuinely new?

**Why we need it.** We invented ρ during Exp 36 because the existing framework had no way to express the raw-to-novel pipeline. The appendix treats the gap between raw output and canonical findings as a parsing problem (φ_fmt — format yield). φ_fmt captures "can we read this at all?" ρ captures "is this telling us anything new?" A perfectly parseable finding that redescribes a known bug has high φ_fmt and low ρ. The appendix has the first. It needs both.

**Analogy:** φ_fmt is checking whether a letter is written in a language you can read. ρ is checking whether it contains any news you haven't already heard.

### Gap 3: The ITC Feedback Loop Is Not Modelled

**What the appendix models.** A parameter ν representing re-injection — when you fix a bug, you sometimes introduce a new one. ν captures the rate at which fixes create new defects.

**What actually happens.** The ITC does something structurally different. When it detects degradation, it restarts the model with fresh context. The fresh model rediscovers bugs the system already knows about. This is not new defects from fixes — it's old defects from context resets. It's stochastic (DeepSeek churns gradually at 55.6% of extension output; Gemini spikes episodically), and context-dependent (restart_fresh temporarily clears context but the accumulated registry re-inflates it immediately).

**Why this matters.** The appendix's ν is a constant. The ITC-driven re-injection varies per model per round. The appendix's ν represents new defects. The ITC produces rediscoveries. The appendix's ν comes from fixes. The ITC comes from context resets. Modelling one as the other is a category error.

**Analogy:** ν is measuring how many new problems a mechanic creates while fixing your car. The ITC feedback loop is taking your car to a different mechanic who has never seen it before and getting a fresh diagnosis that re-identifies the same faults the first mechanic already found. Both put problems back on your repair list, but the mechanisms are completely different.

### Gap 4: Delivery and Format Quality Degrade With Context Size

**What the appendix says.** f_del (delivery feasibility — does the model produce output?) and φ_fmt (format yield — is it parseable?) are per-model constants. DeepSeek: f_del ≈ 0.8 at 32K tokens.

**What actually happens.** Context grew from 95% of the 200K budget (R3) to 406% (R22, 811K characters). As context inflates, delivery and format quality degrade. Models produce more malformed output, fail to follow structured format, sometimes fail to produce output at all. This is not a constant — it's a function of context size.

**Why this matters.** The degradation triggers the ITC (Gap 3). The ITC restarts models. Fresh models rediscover known bugs. The registry grows. Context grows further. Gap 4 feeds Gap 3 in a self-reinforcing cycle.

The appendix correctly models that different models have different f_del and φ_fmt values. It does not model that these values change over time as context grows. The diversity means they degrade at different *rates*, which compounds the problem, but the fundamental issue is that the parameters move at all.

**Analogy:** Rating each runner in a relay by their personal best time and treating it as fixed. But the race is run carrying a backpack that gets heavier every lap. By lap twenty, personal bests are meaningless. You need time as a function of backpack weight, not as a constant.

### Gap 5: Runner Convergence Gate ≠ Appendix Termination Criteria

**What the appendix specifies.** §7.4 — stop when V̂_remaining (estimated remaining value) drops below a threshold AND the system is not in ascending abstraction (findings getting deeper even as they get rarer).

**What the runners implement.** A 5-condition conjunction: round ≥ 12, open_crit_high == 0, recent_novel ≤ 2, contested == 0, gamma_passed. State-based, no value estimation.

**Why this matters.** The deep analysis showed 3 of the runner's 5 conditions are non-contributing after R6. open_crit_high was permanently zero. gamma_passed permanently true. Stall detector terminate tier never fired. The gate was effectively a 2-condition test (contested + novel) for the last 17 rounds. We can't tell whether the appendix's value-based criterion would have done better because V̂ and H̄ have never been implemented.

**Analogy:** The appendix describes a thermometer that measures the temperature of the remaining soup and stops cooking when it's done. The runner built a timer that checks elapsed time, whether the stove is on, and whether anyone has complained. Three of those five checks are always true after the first few minutes, so the timer is really just checking complaints and elapsed time. It has no idea whether the soup is actually done.

---

## How the Five Gaps Connect

These are not five independent problems. They form one coupled system.

**Gap 4 starts the chain.** Context grows as rounds accumulate. Models receive increasingly bloated prompts. Their delivery and format quality degrade.

**Gap 3 amplifies.** The ITC detects the degradation and restarts models with fresh context. Fresh models rediscover known bugs, inflating the registry. The inflated registry makes context grow further.

**Gap 1 hides the problem.** γ, which only sees novel findings, reports convergence. It cannot see that raw output is stable while novelty collapses. The system looks healthy by the only metric the appendix provides.

**Gap 2 means nobody has a metric to see the churn.** ρ (novel/raw) would reveal the divergence immediately. But ρ does not exist in the formal framework.

**Gap 5 means the system cannot terminate.** The convergence gate is state-based and 3 of its 5 conditions are permanently satisfied. The two remaining conditions (contested + novel) are kept alive by the feedback loop. The appendix's value-based criterion might have terminated earlier and correctly, but it was never implemented.

**The result** is what Exp 36 demonstrated: 23 rounds, 224 minutes, 452 raw findings, 153 canonical entries, ~9 actual bugs. A 17:1 dedup ratio. The mathematical model could not see the problem because each component metric was measuring its own piece correctly. The failure is in the interactions between components, and the appendix does not model interactions.
