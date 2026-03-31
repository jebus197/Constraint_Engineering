# Composable Directive Architecture Confer Results

**Date:** 31 March 2026
**Participants:** CC2 (Claude Opus 4.6), CX (Codex GPT-5.4), ChatGPT (GPT-5.4), Gemini 3.1 Pro, DeepSeek Reasoner
**Rounds:** 3 (max rounds reached, 1/5 convergence signal)
**Total output:** ~191,000 characters across 15 dispatches

## Overview

All 5 models under full CDSFL directives reviewed the composable directive architecture proposition. The confer produced structured findings on mathematical modelling, implementation strategy, experimental design, and risk analysis. No model rejected the architecture. All five independently narrowed the claim from "configuration diversity can substitute for model diversity" to "dynamic directive composition is a buildable, testable dispatch architecture that may produce useful cognitive diversity."

## Round 0 Performance

| Model | Characters | Time |
|-------|-----------|------|
| CC2 | 37,313 | 208s |
| CX | 10,212 | 265s (first dispatch under efficiency fixes: reasoning effort medium, MCP servers disabled, ephemeral mode) |
| ChatGPT | 28,183 | 121s |
| Gemini | 8,099 | 47s |
| DeepSeek | 12,074 content + 16,113 reasoning | 163s |

## Round 1 Performance (confer)

| Model | Characters | Time |
|-------|-----------|------|
| CC2 | 11,399 | 73s |
| CX | 7,360 | 101s |
| ChatGPT | 12,561 | 58s |
| Gemini | 7,878 | 43s |
| DeepSeek | 9,163 content + 3,958 reasoning | 98s |

## Round 2 Performance (final confer)

| Model | Characters | Time |
|-------|-----------|------|
| CC2 | 10,056 | 66s |
| CX | 8,225 | 144s |
| ChatGPT | 10,560 | 45s |
| Gemini | 8,391 | 45s |
| DeepSeek | 9,939 content + 12,307 reasoning | 121s |

---

## Section 1: Mathematical Modelling Proposals

### 1.1 Unified Detection Equation Under Composition

All five models independently derived variants of the same extended formula. CC2's final form from Round 2:

```
q_eff(a, k) = p(a,k) · α(L) · κ(D) · d(i,k) · f(a,k) · η(a,k)
```

Where:
- `p(a,k)` — base capability
- `α(L)` — attention yield (composition activation)
- `κ(D)` — coherence penalty
- `d(i,k)` — diversity discount
- `f(a,k)` — delivery feasibility
- `η(a,k)` — decomposition/parsing yield

This extends Section 2 of the Mathematical Appendix directly. Five factors in causal chain: latent capability → composition activation (attention yield) → coherence penalty → diversity discount → delivery feasibility → parsing yield.

### 1.2 Configuration Correlation Coefficient

All five models identified the same core mathematical gap: the existing diversity discount `d_ik` does not distinguish substrate diversity from configuration diversity.

**CC2** proposed source decomposition:
```
d_ik = d_weights · d_config
```
For same-model configurations, `d_weights = 1` (fully correlated on weight axis). Introduced correlation coefficient `ρ ∈ [0, 1]`. Expected values: `ρ_config ∈ [0.7, 0.95]` (high), `ρ_weights ∈ [0.2, 0.6]` (lower).

**CX** proposed overlap decomposition:
```
(1 - o) = (1 - o_weights) · (1 - o_config)
```
For same-weight variants, `o_weights ≈ 1`, so independence comes only from `o_config`.

**ChatGPT** proposed configured agent formalism `a = (m, g)` with dependence discount:
```
η = 1 - λ · ρ̄
```

**Gemini** proposed substrate and configuration distance decomposition using Jaccard similarity of active constraint sets.

**DeepSeek** proposed configuration diversity function using Jaccard distance on findings.

CC2 later challenged its own Pearson correlation and proposed a **log-linear (Ising-type) interaction model** as replacement. DeepSeek proposed miss-correlation coefficient. DeepSeek Round 2 proposed **configuration diversity as subspace projection**, where each configuration projects the model's latent capability vector onto a subspace, and orthogonal configurations can yield negative correlation.

### 1.3 Coherence Penalty

Four of five models independently proposed a multiplicative coherence factor on detection probability that degrades with composition size.

**CC2:** exponential decay beyond a knee point:
```
γ(D) = 1                          if |D| < threshold
γ(D) = exp(-λ(|D| - threshold))   otherwise
```

**CX:** coherence-capacity factor `κ(m, g) ∈ [0, 1]`.

**ChatGPT:** coherence functional `κ` estimated from packet count, conflict graph density, token budget pressure, focus entropy, and empirical instability.

**Gemini:** constraint density `ρ = |constraints| / token_length`, with model-specific threshold. If density exceeds threshold, composer must split dispatch.

The functional form is unresolved but the phenomenon is consensus.

### 1.4 Non-Commutativity and Ordered Composition

CC2, CX, and ChatGPT all identified that merge is commutative for constraint sets but **non-commutative for transforms and context**. Canonical ordering: Universal → Domain (transformed) → Phenotype directives → Situation.

CX formalised this as an ordered operator chain:
```
D_eff = S ∘ T_transform ∘ D ∘ U
```
Monotonicity requirement: the transform preserves HARD constraint ordering.

ChatGPT required associativity of merge representation, acknowledged non-commutativity, and required idempotence for duplicate inclusion.

### 1.5 Phenotype as Transformation Operator

Three models (Gemini, CX, CC2) independently arrived at the same structural insight: the phenotype layer is **not** another additive constraint set. It is a **transformation operator** that modifies how domain and universal packets are rendered.

**Gemini** formalised this as:
```
C_active = P(U ⊕ D) ⊕ S
```
where `P` is a functor.

**CX** formalised it as a monotone transform `T`.

**CC2** proposed the phenotype-as-transformer pattern with rules like max directive length, style, and remove examples.

This fundamentally changes the composition algebra from set union to ordered operator application.

### 1.6 Layer Interaction Terms

**ChatGPT** proposed logistic decomposition with interaction terms, including domain×phenotype, domain×situation, and phenotype×situation interactions.

**DeepSeek** proposed an interaction tensor `I` as a synergy multiplier.

**CX Round 2** proposed an explicit interaction layer:
```
g = U + D + P + I_interaction + S
```

### 1.7 Token Budget and Attention Yield

CC2 Round 1 introduced the **attention yield function**:
```
α(L) = 1                      if L < L₀
α(L) = exp(-β(L - L₀))        otherwise
```

This was the single most-cited new finding across subsequent rounds. Adding more directives is not free. There is an optimal composition size `L*` per model beyond which performance actively degrades.

**Gemini** proposed attention dilution proportional to `1 / log(1 + |constraints|)`.

**ChatGPT** proposed directive-load decay with the same functional structure.

### 1.8 Composition-Dependent Capability Fingerprint

DeepSeek Round 1 proposed that the capability fingerprint must become composition-dependent:
```
φ(m, g) = (D_decay, v̄, A, C, κ)
```
Configuration changes the Duane NHPP discovery rate and the abstraction index.

### 1.9 Minimum Effective Packet Size

DeepSeek Round 2 modelled this as a **sigmoid phase transition**: below a critical token length `L_c`, a packet has near-zero influence.

### 1.10 Composition Benefit Ratio

CC2 proposed a decision framework:
```
B = [ΔCoverage(composed) - ΔCoverage(monolithic)] / [Cost_engineering + Cost_coherence]
```
Architecture justified iff `B > 0`.

---

## Section 2: Implementation Proposals

### 2.1 Dynamic Composer Architecture

All five models converge on a **deterministic, pure-function composer** for v1. Key agreement points:

- **Phase 1:** deterministic lookup (~200–400 lines)
- **Phase 2:** adds optimisation after Experiment 19 data
- **Phase 3:** adds meta-composition only if the registry grows large

**CC2** proposed a `DirectiveComposer` class with a `compose(task, model) → DirectiveSet` method. Pure function, deterministic, fail-loud. Fixed prune order: situation → phenotype → domain → universal (never pruned).

**CX** proposed `compose(task, model, round) → (effective_prompt, manifest_hash)`. Four stages: select packets → apply ordered transforms → validate monotonicity & budget → render provider-specific prompt.

**ChatGPT** proposed typed composition over raw text concatenation, with packet schema in TOML:
```toml
[packet]
hard_constraints = [...]
soft_preferences = [...]
directives = [...]
applies_if = "..."
conflicts_with = [...]
requires = [...]
```

### 2.2 ConfiguredAgent as First-Class Object

ChatGPT proposed a `ConfiguredAgent` dataclass:
- `model_id`
- `composition_id` (hash of ordered packet set + version IDs)
- `packets`
- `effective_directive_text`
- `metadata`

All benchmarking keyed on `(model_id, composition_id)` rather than `model_id` alone.

### 2.3 Composition Provenance

CX and ChatGPT both proposed composition identity:
```
CID = hash(ordered_packet_ids, packet_versions, render_template_version)
```

Every dispatch logs: CID, packet IDs, merge trace, coherence score, rendered prompt checksum, and selection rationale.

### 2.4 Estimated Size

ChatGPT estimated:

| Component | Lines |
|-----------|-------|
| Core selection + merge + render | 200–400 |
| Schema validation + monotonicity & coherence lint | 150–300 |
| Provenance and logging | 100–200 |
| Orchestrator integration | 100–200 |
| **Total (excluding tests)** | **550–1,100** |

---

## Section 3: Experimental Design for Experiment 19

### 3.1 Core Hypothesis

Does N configurations of one model produce finding diversity equivalent to N different models? All models agree this is the key falsifiable prediction.

### 3.2 Design Consensus

All models agree on **blocked factorial design** with randomised assignment. Must control for token length, composition order, manufacturer prompt effect, and exposure topology. Measurement on canonical verified defect events, not raw text. Cost-normalised Pareto evaluation required.

### 3.3 Arm Designs

**CC2** proposed 3 arms:
- **Arm A:** 5 different models, same universal directives
- **Arm B:** 1 model, 5 compositions
- **Arm C:** alternative model, 5 compositions

**CX** proposed 5 arms: monolithic, composed, phenotype ablation, cross-model baseline, manufacturer prompt ablation.

**ChatGPT** proposed 5 arms: monolithic, static layered, dynamic composition, same-model multi-config ensemble, cross-model ensemble. Also proposed a **hypothesis ladder**:
- H1: different-config beats same-config repeats
- H2: multi-config improves coverage at equal cost
- H3: multi-config remains more correlated than cross-model
- H4: dynamic beats static profiles
- H5: modular beats monolithic at equal tokens
- H6: order effects negligible under canonical composition

ChatGPT also proposed **nested ablation**: measure marginal contribution of each layer by comparing Y with universal only → universal + situation → universal + domain + situation → full stack.

### 3.4 Kill Criteria

ChatGPT proposed abandoning or narrowing if:
- Same-model different-config yields little unique-find lift over repeats
- Coherence failures grow faster than coverage gain
- Static profiles perform within 5–10% of dynamic at lower complexity
- Gains disappear after controlling for prompt length and placement

---

## Section 4: Challenges and Risks

### 4.1 Correlated Blind Spots (Critical — all five models)

The strongest consensus finding. Same weights = same training distribution = shared blind spots. Configuration may redistribute attention without extending the capability frontier. CC2 expects `ρ_config ∈ [0.7, 0.95]`. DeepSeek formalised blind spot persistence and proposed a **blind spot injection test**: inject known logical fallacy patterns and check whether any configuration catches them while a different model does.

### 4.2 Coherence Degradation Under Composition (High — four models)

Monotonicity prevents logical contradiction but not cognitive overload. Models can silently drop directives when composed sets exceed effective compliance windows.

### 4.3 Evidence Chain Gap at Step 3 (High — three models)

The existential observation that one CX configuration produced diversity does not support the universal claim that arbitrary compositions manufacture diversity on demand. CX said: *"The weakest step is the jump from 'configuration changes output' to 'configuration can substitute for model diversity.'"*

### 4.4 Non-Separability of Layers (High — two models)

Four layers are not fully separable. Domain knowledge interacts with model phenotype in ways the stack cannot always express. If there are too many interaction terms, the architecture collapses back to ad hoc prompt engineering.

### 4.5 Over-Claim Risk (High — two models)

CX said the evidence supports *"dynamic directive composition is a buildable, testable dispatch architecture that may buy useful cognitive diversity."* It does not yet support *"one model + compositions can stand in for model diversity."*

ChatGPT proposed narrowing *"the configured synthetic domain expert is buildable today"* to *"bounded task-shaped analytical phenotypes are buildable today for bounded review contexts."*

### 4.6 Meta-Composition Infinite Regress (High — DeepSeek)

Automating the composer risks infinite regress and overfitting. Keep composer rule-based and human-curated only. CC2 formalised the meta-composition fixed-point problem: convergence requires the meta-composer to be a contraction mapping.

---

## Section 5: Novel Insights

### 5.1 Organisation Theory Convergence (CC2)

The adversarial brief's critique that composable directives reinvent organisation theory is actually validation. The formalisation adds three things human teams lack: **reproducibility** (explicit, version-controlled), **measurability** (quantitative comparison via the mathematical framework), and **speed** (milliseconds vs. weeks for recomposition).

### 5.2 Composition as Sequential Control Problem (CX Round 2)

Composition chosen on round `r` changes what findings appear, changing what is rational for round `r+1`. The composer should be modelled as a **policy trajectory with switching costs**, not a one-shot selection.

### 5.3 Packet Epistasis (ChatGPT Round 2)

Packet value is not additive. The value of one packet depends on which others are present. Requires interaction terms in the utility model and fractional-factorial experimental design.

### 5.4 Semantic Compilation Gap (CX Round 2)

The registry produces a merged policy object, but prompt composition is still string concatenation. Registry-level monotonicity does not imply dispatch-level monotonicity. Introduced a **compiler-fidelity term** `ψ`.

### 5.5 Exposure Topology and Interference (CX Round 2)

Confer results are not independent because reviewers see each other's findings. Experiment 19 must pre-register and vary the reveal topology (blind, star, ordered chain, full mesh) and estimate topology effects separately.

### 5.6 Falsification Debt (Gemini Round 1)

Dynamically composed constraint graphs are untested at runtime. If the meta-pass checking the composed graph is not run, the output carries **residual falsification debt** that elevates base residual risk.

### 5.7 Constraint Density as Unifier (Gemini Round 2)

Neither token length alone nor constraint count alone captures the degradation. The ratio `ρ = |constraints| / token_length` unifies both CC2's and Gemini's proposals.

---

## Section 6: Unresolved Disagreements

1. **The functional form of coherence penalty.** CC2 uses exponential decay over token length. Gemini uses logarithmic dilution over constraint count. CX uses a branching and load score. ChatGPT uses a multivariate function. Gemini proposed constraint density as the unifier. No convergence. This is an empirical question for Experiment 19.

2. **The composer selection mechanism.** CC2 says constraint satisfaction with deterministic lookup for v1. ChatGPT says utility maximisation. Gemini says contextual multi-armed bandit. CX says sequential control problem. These may be sequential stages of maturity rather than competing approaches.

3. **Recency bias significance.** CC2 raised then retracted. DeepSeek doubled down with a full U-shaped attention model. Unresolved. Requires empirical testing.

4. **Stochastic vs. deterministic coherence checking.** DeepSeek proposed embedding-based cosine similarity. Gemini rejected this as introducing stochastic failure into a deterministic compilation step. Tension remains.

5. **Which correlation model best captures configuration diversity.** CC2 proposed log-linear. DeepSeek Round 1 proposed miss-correlation. DeepSeek Round 2 proposed subspace projection matrices. ChatGPT Round 2 proposed hierarchical dependence. All plausible. None empirically validated.

---

## Section 7: CX Efficiency Fix Results

CX survived all 3 rounds under the new efficiency configuration. Reasoning effort medium instead of extra high. MCP servers disabled. Ephemeral mode enabled.

| Round | Time |
|-------|------|
| 0 | 265s |
| 1 | 101s |
| 2 | 144s |

No crashes, no timeouts. This compares favourably with previous experiments where CX regularly timed out at 600s or crashed entirely.

---

## Section 8: Next Steps

1. Extend Mathematical Appendix with the unified detection equation under composition and the coherence penalty formalism.
2. Build the dynamic composer (Phase 1, deterministic lookup, ~200–400 lines).
3. Design and run Experiment 19 with blocked factorial design testing the configuration diversity hypothesis.
4. Resolve the four unresolved disagreements empirically through the experiment.
5. Update the capability fingerprint to be composition-dependent.
