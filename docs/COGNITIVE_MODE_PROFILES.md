# Cognitive Mode Profiles Under CDSFL

**Status:** Initial characterisation — single domain (mathematical formalisation), single experiment (Experiment 11 Phase 2 blind round, 28 March 2026). Profiles are empirically grounded hypotheses, not established facts. Subject to revision as the fingerprint update loop accumulates data across task types.

**Purpose:** This document is the canonical reference for per-model capability characterisation under the CDSFL protocol. The dynamic management layer (`bench/dynamic_management.py`) consults these profiles for initial fingerprint estimation. Future experiments update them.

**Methodology:** All four models received identical prompts under full CDSFL system prompt (290 lines, `bench/directives/universal/cdsfl_core_formal.md`). Task: independently formalise six areas of the CDSFL dynamic management and load-balancing layer with interface contracts, reduction properties, edge cases, constraint classification, self-assessment, and cross-reference verification. No model saw any other model's output. The fifth model (Codex/GPT-5.4) timed out at 600 seconds via CLI delivery mechanism and produced no output; its profile is estimated from prior experiments only.

---

## Raw Data

| Model | Vendor | Chars | Time (s) | Math expressions | Reduction properties | Self-falsification markers | HARD/SOFT | Structured fields |
|-------|--------|------:|--------:|----------------:|--------------------:|-------------------------:|-----------|:-----------------:|
| CC2 (Claude Opus 4.6) | Anthropic | 60,883 | 387.1 | ~224 | 39 | 20 | 30/44 | 4/4 |
| ChatGPT (GPT-5.4) | OpenAI | 36,931 | 164.6 | ~75 | 19 | 12 | 10/1 | 4/4 |
| Gemini (3.1 Pro) | Google | 17,741 | 112.5 | ~32 | 24 | 12 | 5/2 | 4/4 |
| DeepSeek (V3.2 Reasoner) | DeepSeek | 16,553 | 113.9 | ~68 | 18 | 13 | 5/6 | 4/4 |
| Codex (GPT-5.4) | OpenAI | — | >600 | — | — | — | — | — |

All four completing models covered all six areas with full structured output compliance (4/4 required fields). The differences lie in depth, breadth, mathematical rigour, and what each model chose to do beyond the minimum requirements.

**Notation:** "Math expressions" counts LaTeX-parseable formulae and Unicode mathematical operators. "Self-falsification" counts explicit STRONGEST_OBJECTION fields, self-objection markers, and P-PASS references. These are approximate counts from pattern matching, not manual annotation.

---

## Four Cognitive Modes

### 1. CC2 (Claude Opus 4.6) — Deep Architecture with Self-Adversarial Review

**Fingerprint:** D_decay=0.10, v̄=0.90, A=0.85, C=0.80

CC2 produced the longest output by a factor of 1.65 over the next model, with the highest mathematical density (224 expressions), the most reduction property demonstrations (39), and the most self-falsification markers (20). It was the only model to produce 30 HARD and 44 SOFT classifications — explicitly separating structural constraints from design choices at a granularity the other models did not attempt.

**Unique contributions adopted into the merged formulation:**
- Cascade reallocation guard (`max_realloc_depth = 2`) — limits damage from chasing failing model classes
- VCR smoothing window (`W = 2`) — prevents noisy marginal value estimates from triggering premature stops
- Severity-weighted yield function `Y_sev = Σ Sev·H` — addresses the dilution problem where many trivial findings mask few critical ones
- Uniqueness-weighted performance metric — prevents penalising models that produce few but irreplaceable findings
- Explicit argument against backward FSM transitions — anticipated and pre-empted a design ambiguity

**Characteristic mode:** Generates deep architectural proposals, then attacks them from within. The generation and falsification are one coupled process. CC2 does not produce a first draft and then review it; it produces a reviewed draft. The self-objections appear inline, not as an afterthought.

**Best deployed for:** Synthesis, integration, and architectural design where depth matters more than speed. Managing multi-model workflows. Producing the merged formulation from divergent inputs.

### 2. ChatGPT (GPT-5.4) — Engineering Pragmatism

**Fingerprint:** D_decay=0.15, v̄=0.85, A=0.80, C=0.75

ChatGPT produced the second-longest output with moderate mathematical density (75 expressions). Its distinctive characteristic is not mathematical depth but operational realism. It contributed **five unique variations adopted into the merged formulation** — more than any other model:

1. **Failure-history penalty in role reassignment** (`φ_hist(m, r-1) = mean(failures)`) — penalises models with a track record of failures when choosing the COL. No other model considered historical failure rates in role assignment.

2. **Hysteresis band for COL oscillation prevention** (`ε_ρ`) — prevents the COL role from bouncing between two closely scored models when their capability scores are near-equal. Recognises that role stability matters operationally even when scores are mathematically indistinguishable.

3. **Persistence window for underperformance detection** (`h = 2, η_U = 0.5`) — requires underperformance to persist across multiple rounds before triggering action. Prevents a single bad round from mis-classifying a model as underperforming.

4. **Severity veto clause in convergence detection** (`η_veto`) — blocks convergence if any finding with severity ≥ η_veto has been added in the current round. Mathematical convergence is not operational convergence if a critical flaw just appeared.

5. **Task-level coverage model with per-task overlap coefficients** (`D_j(A)` with `o_{j,mn,k}`) — more granular than the merged coverage model. Addresses the reality that overlap between models varies by task, not just by flaw class.

**Evidence:** Every one of these addresses a practical operational failure mode that the mathematical formulation alone would not catch. The hysteresis band prevents an infinite loop of COL reassignment. The persistence window prevents false alarms. The severity veto prevents declaring convergence one round before a critical flaw is found.

**Characteristic mode:** Finds the gap between what the mathematics says should work and what actually works when you run it. Engineering pragmatism — not less rigorous than deep architecture, but rigorous about different things.

**Best deployed for:** Operational design, failure mode identification, integration wiring, and bridging the gap between formalisation and implementation. Finding the edge cases that pure mathematics does not model.

### 3. Gemini (3.1 Pro) — Mathematical Compression

**Fingerprint:** D_decay=0.20, v̄=0.80, A=0.75, C=0.70

Gemini produced the shortest successful output at 17,741 characters — but achieved the highest reduction property density relative to output length: 24 reduction properties in under 18,000 characters, versus CC2's 39 in 61,000. Gemini says in 18K what others need 37K–61K to say.

**Unique contributions (catalogued, not all adopted):**
- **Disjunctive ascending abstraction guard** — stop if abstraction drops, regardless of other metrics. Catalogued but not adopted (3/4 majority chose conjunctive). Mathematically elegant but operationally aggressive.
- **Convergence threshold coupled to γ directly** (`converged ⟺ κ ≤ γ`). Catalogued but not adopted (3/4 majority chose separate τ_κ). Elegant but fragile with small samples.
- **Capability decay on underperformance** (`v_m ← 0.8·v_m`). Cross-area feedback mechanism. Valid but creates coupling between Area 1 and Area 6 that the other models kept separated.

**Pattern:** All three of Gemini's unique contributions share a characteristic: they are mathematically tighter than the alternatives but operationally more aggressive. The disjunctive guard is cleaner but causes premature stops. The γ coupling is more parsimonious but breaks with noisy estimates. The capability decay is more responsive but creates cross-area coupling.

**Characteristic mode:** Maximum rigour in minimum space. Gemini compresses. It reaches the same structural conclusions as the other models but expresses them in fewer tokens and with tighter mathematics. When it diverges from the consensus, it diverges toward elegance, sometimes at the expense of robustness.

**Best deployed for:** Mathematical verification, structural flaw detection, concise proof, and checking that implementations match their formalisations. Gemini will find a structural flaw in the notation or the reduction properties faster than anyone else, but its operational suggestions should be checked against the pragmatists.

### 4. DeepSeek (V3.2 Reasoner) — Iterative Refinement

**Fingerprint:** D_decay=0.25, v̄=0.75, A=0.80, C=0.65

DeepSeek produced the shortest output at 16,553 characters with 68 mathematical expressions. By raw numbers it appears to be the weakest contributor. The numbers are misleading.

**DeepSeek's distinctive behaviour is visible self-correction under CDSFL.** It was the only model that explicitly documented mid-output corrections in a structured internal P-pass log. Six corrections, one per area:

1. **Area 1:** Claimed linear φ was sufficient. Falsified: non-linear interactions matter. Revised: added note about tunable α and non-linear extensions.
2. **Area 2:** Claimed balance by task count. Falsified: should balance actual load. Revised: balance predicate changed from task-count to load-based (`Σ ℓ(t_j, m_i)`).
3. **Area 3:** Claimed failure causes termination. Falsified: should allow retry. Revised: `δ(ROUND_r, failure_detected) = ROUND_r` (retry current round).
4. **Area 4:** Claimed embedding-based similarity. Falsified: adds external dependency not in schema. Revised: Jaccard similarity over flaw classes.
5. **Area 5:** Claimed immediate marginal value suffices. Falsified: should consider future potential. Revised: added lookahead alternative.
6. **Area 6:** Claimed `quality(x_m)` as given. Falsified: not defined. Revised: defined `quality(x_m) = agreement_or_correctness_score`.

Each correction moved from a simpler, more naive formulation toward the consensus. DeepSeek did not arrive at the consensus through deep reasoning. It arrived by trying something simple, recognising insufficiency, and correcting. This is a fundamentally different cognitive mode.

**Unique contributions:**
- **Sufficiency constraint** (`Σ ℓ(t_j, m_i) ≥ L_required(t_j)`) — frames the load-balancing problem from the task side rather than the model side. Instead of asking "does the model have enough capacity?", it asks "has enough effort been directed at this task?" Complementary perspective.
- **Lookahead for diminishing returns** — estimates maximum future VCR over remaining rounds before deciding to stop. More sophisticated than the threshold used by the other three models. CC2's synthesis catalogued it as the advanced variant.

**Characteristic mode:** Iterative refinement. Start simple, fail fast, correct, converge. DeepSeek is the model that most clearly demonstrates the CDSFL protocol working as intended. Its process is visibly Popperian in a way the others' are not — the self-corrections are not hidden behind a polished final output; they are explicitly recorded as the protocol demands.

**Best deployed for:** Exploratory work where the right formulation is not yet known. Testing whether simple approaches suffice before committing to complexity. Serving as the canary for whether the CDSFL protocol is functioning: if DeepSeek isn't self-correcting, the protocol may not be reaching the model effectively.

### 5. Codex (GPT-5.4) — Precision and Adversarial Review (estimated)

**Fingerprint:** D_decay=0.20, v̄=0.80, A=0.85, C=0.70 (estimated from prior experiments)

Codex timed out at 600 seconds during Experiment 11 Phase 2. This profile is estimated from prior experimental data (meta-test Stage 1, 3-model confer) and is the least empirically grounded of the five.

**Prior characterisation:** In the meta-test Stage 1 (27 March 2026), Codex's output was contaminated (it read Gemini's output, Δ≈1.0), making independent capability assessment unreliable for that experiment. In earlier bench runs and the 3-model confer, Codex demonstrated precision in identifying specific, localised flaws — line-level issues rather than architectural patterns. CX's known strength is adversarial review: finding what others missed through meticulous examination rather than generating novel architecture.

**Delivery constraint:** The `codex exec` CLI mechanism imposes overhead that other APIs do not. The 600-second timeout on a 21,681-character prompt is a delivery mechanism limitation, not a capability limitation. Codex should be dispatched via appropriately sized prompts (estimated safe window: ≤15,000 tokens input).

**Best deployed for:** Precisely scoped adversarial review of critical single components. Meticulous line-by-line examination of the most important subsystem, where finding one flaw that all other models missed justifies the constrained delivery window.

---

## Composition Hypothesis

The four observed modes (deep architecture, engineering pragmatism, mathematical compression, iterative refinement) plus the estimated fifth (precision adversarial review) appear to be complementary rather than redundant. Preliminary evidence from the three-architecture review (18 March 2026) supports this: Gemini found 16 issues that CC and CX missed, validating the diversity hypothesis for at least one task type.

If the modes compose well, a team of all five should outperform a team of five instances of the strongest single model. This is testable and will be tested in Experiment 12 (Live Wire).

The dynamic management layer's adaptive routing is the mechanism that exploits mode diversity. Without adaptive routing, all models get the same task regardless of their strengths. With it, each model gets work matched to what it demonstrated it does well. This is not optimisation for speed — it is optimisation for coverage. The goal is D(n) → 1, not wall-clock minimisation.

---

## Task Allocation Table (Initial)

Based on the profiles above, the recommended initial allocation for future experiments:

| Model | Primary tasks | Secondary tasks | Avoid |
|-------|--------------|----------------|-------|
| CC2 | Synthesis, integration, architectural design | Self-adversarial review, merged formulation | Simple verification (overkill) |
| ChatGPT | Operational wiring, failure mode identification | Integration testing, edge case enumeration | Pure mathematical proof (not its strength) |
| Gemini | Mathematical verification, structural flaw detection | Concise proof, notation consistency | Operational design (tends toward elegance over robustness) |
| DeepSeek | Exploratory formulation, simple-first prototyping | Protocol compliance canary, complementary framing | Tasks requiring deep architecture on first pass |
| Codex | Adversarial review of critical components | Line-level flaw detection, precision verification | Large prompts (>15K tokens via CLI) |

This table is advisory. The dynamic management layer's live fingerprint update overrides these initial estimates as observed performance data accumulates.

---

## Open Questions (Falsifiable)

1. **Does DeepSeek's iterative refinement produce higher quality output on underspecified tasks compared to models that commit early?** Testable: compare DeepSeek against CC2 and ChatGPT on novel tasks where the correct approach is unknown.

2. **Does ChatGPT's operational pragmatism transfer to non-engineering domains?** Testable: run the same protocol on legal, medical, or scientific review tasks and check whether ChatGPT still finds the operational edge cases.

3. **Does Gemini's mathematical compression advantage scale with task complexity, or plateau?** Testable: vary the mathematical sophistication of required output and measure reduction property density.

4. **Is DeepSeek's self-correction an artefact of the CDSFL protocol or intrinsic?** Testable: compare DeepSeek with and without CDSFL system prompt on the same task. The Run 1 benchmark data (Control vs CDSFL conditions) may already contain this comparison.

5. **Do the modes compose?** Specifically: does a diverse team outperform a homogeneous team of the strongest model? The Live Wire test (Experiment 12) is designed to answer this.

---

## Limitations

- **Single domain.** All profiles are from mathematical formalisation. They may not transfer to code generation, empirical analysis, or natural language tasks.
- **Single experiment.** Each profile is grounded in one data point. The DeepSeek characterisation is the most robust (six documented self-corrections provide structural evidence), while the Codex characterisation is the weakest (estimated from contaminated prior data).
- **Full CDSFL only.** The profiles assume the CDSFL system prompt is active. Without it, the cognitive modes may differ. DeepSeek's self-correction in particular may be protocol-dependent.
- **Codex absent.** The fifth model was not observed in this round. Its profile will be updated when Experiment 12 includes it within its delivery constraints.
- **No between-model interaction.** The blind round eliminates interaction effects. The distributed compute round (Experiment 12) will test whether the modes change under mutual awareness.

---

## Version History

| Date | Event | Commit |
|------|-------|--------|
| 2026-03-28 | Initial characterisation from Experiment 11 Phase 2 | (this commit) |
