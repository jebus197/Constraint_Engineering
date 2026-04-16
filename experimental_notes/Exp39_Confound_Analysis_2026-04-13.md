# Experiment 39-0 — Confound Analysis and Lessons-Forward Audit

**Date:** 13 April 2026  
**Method:** 4-agent forensic investigation (prompt tracing ×2, raw output comparison, context budget analysis) + manual code tracing + lessons-forward audit  
**Verdict:** Exp 39-0 R_k(i) (the iterative residual-risk self-assessment after round i) adoption data is **CONFOUNDED** — not valid for measuring metacognitive capability

---

## 1. Confound Declaration

Experiment 39-0 is confounded by three independent factors that invalidate R_k adoption as a measure of model metacognitive capability:

| # | Confound | Severity | Evidence |
|---|----------|----------|----------|
| C1 | User prompt missing CORROBORATION/FALSIFICATION/ANALYSE | **Critical** | Exp 37 had 10 fields incl. mandatory R_k; reference_runner had 7 — no R_k mandate |
| C2 | Total payload 4.6× system decomposition threshold | **Critical** | 369K chars (ref_runner 163K + runner_core 38K + immune_agents 167K) vs 80K threshold |
| C3 | Monolithic dispatch to 3/5 models despite payload > threshold | **High** | CC2 (Claude Opus 4.6 CLI instance), ChatGPT, and Gemini received 369K monolithically; only Codex and DeepSeek decomposed |

**What is salvageable:** The 78 findings about reference_runner.py bugs, S_k (severity/stringency tristate gate) pipeline verdicts, convergence dynamics, γ history, per-model finding counts. These are unaffected by the R_k confound.

**What is NOT salvageable:** R_k adoption rates. The oscillation measures prompt construction quality and context budget management, not model metacognitive capability.

---

## 2. Lessons-Forward Audit

### Pattern: Lesson Attrition Across Experiment Transitions

Bespoke experiment scripts (`run_exp37_evidence.py`) encode hard-won lessons as code. When replaced by generic infrastructure (`reference_runner.py`), lessons that live only in prompt construction details are silently dropped.

### 11 Documented Lessons Lost

| # | Lesson | Source | Status in reference_runner |
|---|--------|--------|---------------------------|
| 1 | CORROBORATION + FALSIFICATION + ANALYSE in user prompt | Exp 37 lines 2858-2867 | **Fixed this session** |
| 2 | Operational directive loading | Exp 37 lines 185-194 | **Fixed pre-launch** (d54a8e6) |
| 3 | Per-round metrics injection (γ, ρ, ρ̄₃) | Exp 37 lines 2310-2372 | **Fixed pre-launch** (d54a8e6) |
| 4 | Semantic novelty feedback (3 graduated signals) | Exp 37 lines 2354-2371 | **Still missing** |
| 5 | Domain-specific focus areas | Exp 37 lines 2836-2848 | Missing by design |
| 6 | Prior fix summary context | Exp 37 `_build_prior_fix_summary()` | **Still missing** |
| 7 | Consolidation phase (final 3 rounds) | Exp 36 Ground Truth, HIGH priority | **Not implemented** |
| 8 | Per-model ρ tracking with targeted ITC | Exp 36 Ground Truth, HIGH priority | **Not implemented** |
| 9 | Context windowing for long runs | Exp 36 Ground Truth, HIGH priority | **Not implemented** |
| 10 | S_k format pre-check with reformat request | Exp 38 findings | **Not implemented** |
| 11 | Parser fixes P2/P3 (CC2 leak, Gemini verdict) | Exp 38 findings | **Not implemented** |

### Transition Scorecard

| Transition | Lessons Documented | Carried Forward | Lost |
|---|---|---|---|
| Exp 36 → Exp 37 | 13 design improvements | 3 partial | 10 |
| Exp 37 → Exp 38/39 | R_k mechanism, prompt schema, op directive | 0 (at time of Exp 38) | All 6 prompt/context items |
| Exp 38 → Exp 39 | 6 runner bugs, 6 parser fixes, 4 design findings | Bug fixes only | Parser P2/P3, S_k format check |

---

## 3. Fingerprint Gap

### Schema vs Reality

The fingerprint files (`bench/fingerprints/*.json`) contain schema fields for:
- `measured_attention_span` — **null**
- `compression_threshold` — **null**
- `quality_at_capacity` — **null**
- `decomposition_recommended` — **null**
- `attention_ratio` — **null**
- `D_decay` — **null** (used by `burst_planner.py` condition 2, never fires)

### What They Actually Contain

Only the `observed` block with operational counts:
- `max_successful_context_chars`: CC2 (Claude Opus 4.6 CLI instance) = 15.7K, ChatGPT = 27.6K, Codex = 47.4K, DeepSeek = 54.8K, Gemini = 14.0K
- `max_successful_prompt_chars`: 465K (all models)
- `total_findings`, `rounds_participated`, `avg_findings_per_round`

### The Data Exists — The Pipeline Doesn't

The ITC system tracks `parse_yield` per model per round. `decay_analysis.py` fits Duane curves. `burst_planner.py` has the `D_decay` trigger. The infrastructure for fingerprint-driven decomposition was built but never wired:
- Extract per-model `parse_yield_history` from `itc_model_state` in checkpoint
- Pair with `prompt_chars_history` from fingerprints
- Fit inflection point → `measured_attention_span`
- Parse_yield at `max_successful_prompt_chars` → `quality_at_capacity`
- Divergence between raw markers and parse_yield → `compression_threshold`

---

## 4. Test Article Design Error

### 10/14 Sub-Experiments Target the Same 163K File

| Config | Test Article | Chars |
|--------|-------------|-------|
| 39-0 through 39-F, 39-I through 39-M | reference_runner.py | 163,548 |
| 39-G | immune_agents.py | 166,857 |
| 39-H | evidence.py | **23,221** |

Only 39-H uses an appropriately-sized article. The domain decomposition happened — the test article decomposition did not.

### 39-0 Payload Breakdown

| Component | Chars |
|-----------|-------|
| reference_runner.py (test article) | 163,548 |
| immune_agents.py (context) | 166,857 |
| runner_core.py (context) | 38,278 |
| **Total** | **368,683** |

System thresholds: `LENGTH_THRESHOLD = 80,000` (input_complexity.py), `SUBAREA_ESCALATION_CHARS = 80,000` (reference_runner.py). Payload = 4.6× threshold.

### Gate Test Could Have Used evidence.py

The gate purpose was verifying 22+ Exp 38 fixes and Gemini dispatch parity. This requires exercising dispatch, parser, immune layer, and convergence — not a 369K payload. `evidence.py` at 23K exercises all the same code paths.

---

## 5. Manufacturer Claims vs Measured Reality

| Model | Advertised Context | Payload Sent | Output Quality |
|-------|-------------------|-------------|----------------|
| Gemini 3.1 Pro | 1M tokens (~4M chars) | 369K chars | It compressed to 3.6K JSON verdicts (R1) |
| ChatGPT 5.4 | 128K tokens (~512K chars) | 369K chars | 0 chars (R1), recovered in R2 |
| CC2 (Claude Opus 4.6 CLI instance) | 200K tokens (~800K chars) | 369K chars | Split format, R_k fragmented |
| DeepSeek Reasoner | 128K tokens (~512K chars) | Decomposed | 0 chars per chunk (reasoning budget) |
| Codex 5.4 | 200K tokens (~800K chars) | Decomposed | Functional, prompt injection artefact R3 |

**Conclusion:** Output quality degrades well before advertised context limits. This is the most replicated finding in the project (78 rounds, 5 models, 4 experiments). Experiments must be designed around **measured** attention capacity, not marketed capacity.

---

## 6. Priority Remediation

### Immediate (done)
- [x] User prompt fix: ANALYSE, FALSIFICATION, CORROBORATION added to `_build_prompt()`
- [ ] Mark Exp 39-0 as confounded in ONBOARDING.md, RECOVERY.md, experiment report

### Short-term
- [ ] Wire fingerprint attention metrics (extract parse_yield decay curves from checkpoints)
- [ ] Make `pre_decompose_models` dynamic: payload > `LENGTH_THRESHOLD` → decompose all models
- [ ] Semantic novelty feedback (lesson #4)
- [ ] Prior fix summary context (lesson #6)

### Medium-term
- [ ] Consolidation phase (lesson #7)
- [ ] Per-model ρ tracking (lesson #8)
- [ ] Context windowing (lesson #9)
- [ ] S_k format pre-check (lesson #10)
- [ ] Parser P2/P3 fixes (lesson #11)

### Structural
- [ ] Prompt schema as first-class tested artefact (not a string literal in a 3,700-line file)
- [ ] Redesign Exp 39 sub-experiment test articles — decompose by article size, not just domain
- [ ] Lessons-forward checklist: before each experiment, verify all prior lessons are present in the runner
