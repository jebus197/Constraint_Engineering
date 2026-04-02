# Run 7 Architecture, Model Routing, and Convergence Mechanisms

**Date:** 2026-04-02T11:15+01:00

---

## 1. Extended P-Pass Clarification

The bug fix (Bug 3) was narrow: the **internal remediation** extended P-pass (inside `DetectorHealthMonitor`, deciding whether to apply immune layer fixes) had a dead iteration loop. No state mutated between iterations → same input → same output → early-stop at iteration 2 every time. Default `max_iterations` changed from 3 to 1.

The **CDSFL extended P-pass** (§6 of `cdsfl_core_formal.md`, the protocol models follow for multi-module analysis) is unaffected. Different systems with the same name.

---

## 2. CDSFL Schema — Fully Active

The complete schema is loaded from `bench/directives/universal/cdsfl_core_formal.md` and injected as the system prompt for all 5 models:

| Section | Content |
|---------|---------|
| §1 | Constraint classification (HARD/SOFT) |
| §2 | Constraint precedence |
| §3 | Falsification loop (P-pass) |
| §4 | Proportionality gate |
| §5 | Corroboration model C(n) |
| §6 | Extended P-pass (DAG structure) |
| §7+ | FFF protocol, verification chain |

The models **also review the code that implements this schema**: `dynamic_management.py` is the immune layer governing their dispatch, convergence, failure handling, and remediation. This is the ouroboros.

---

## 3. Model Routing

| Model | Label | API Route | Model ID | Role |
|-------|-------|-----------|----------|------|
| Claude Opus | CC2 | `claude_cli` (Max subscription, $0) | `opus` | Player Manager |
| GPT-5.4 | ChatGPT | `openrouter` | `openai/gpt-5.4` | Participant |
| GPT-5.4 | Codex | `openrouter` (was `codex_exec`) | `openai/gpt-5.4` | Participant |
| Gemini 3.1 Pro | Gemini | `google` (direct) | `gemini-3.1-pro-preview` | Participant |
| DeepSeek Reasoner | DeepSeek | `deepseek` (direct) | `deepseek-reasoner` | Participant |

**OpenRouter:** ChatGPT + Codex (2 models).
**Native APIs:** CC2 (claude_cli), Gemini (google), DeepSeek (deepseek).

Codex switch eliminates the catastrophic `codex exec` decomposed fallback (45-80 min/round → 60-180s expected).

---

## 4. Test Article

`bench/dynamic_management.py` (~6,400 lines):
- Role assignment, load balancing, round progression
- Convergence detection, diminishing returns
- Failure handling, correlated failure model
- Health monitor, remediation chains
- Self-adaptive immune feedback loop

Prompt includes: full source code, mathematical appendix, verification chain, interface summary. Adaptive rounds (R1+) also include all prior findings from all models.

---

## 5. Resolution Setting

**S = 0.5** (electron microscope — default)

| S Value | Analogy | Expected Behaviour |
|---------|---------|-------------------|
| 0.8 | Optical microscope | Fast convergence, only critical bugs |
| **0.5** | **Electron microscope** | **Important bugs count (default)** |
| 0.3 | Scanning tunnelling | Everything including style |
| 0.0 | Unbounded | May never converge |

Findings with `severity < 0.5` are still logged and reported — only excluded from Ω computation. Run 6 data showed genuinely valuable findings clustered in 0.5–0.95 severity.

Config: `DynamicManagementConfig(resolution_threshold=0.5)` — tuneable before launch.

---

## 6. Convergence Mechanisms (Three Independent)

### 6.1 Compound Objective Ω Churn Guard (NEW — Primary)

Per-model. Each round:
1. Filter findings by `severity ≥ S`
2. Compute γ_output on filtered descriptions (Heaps-Duane)
3. Compute A = β_output / β_input (amplification factor)
4. Compute **Ω = A × γ_output**

**Benching:** When Ω < τ (0.10) for 2 consecutive rounds → model benched (excluded from dispatch).
**Termination:** When ALL models benched → run converged.

Models have no convergence awareness. The system measures information-theoretic output and stops dispatching when value is exhausted.

### 6.2 γ-Unified Convergence (Existing)

System-wide Duane γ from per-round finding counts. Stop when γ > 0.5 AND Y(t) not ascending. Did not fire in Run 6 (γ = 0.027 due to ouroboros prompt injection).

### 6.3 DynamicManager Convergence (Existing)

Internal kappa-based convergence from FSM. Inter-model agreement + marginal value threshold.

### Why Ω is Expected to Work

Run 6 problem: γ couldn't see through prompt growth, DM kappa never converged because of elaborate restatements. Ω measures **value per round per model at the resolution you care about**. When Ω → 0 from either direction (vocabulary exhaustion or pure churn), the model is done. The resolution parameter S constrains what "value" means.

---

## 7. Expected Run 7 Trajectory

- **R0–R2:** Genuinely novel findings (Run 6 data: all valuable bugs found in R0–R3)
- **R3–R5:** Models begin exhausting vocabulary at S=0.5. Some bench early (Gemini first, based on Run 6 amplification data)
- **R5–R7:** All models benched → termination
- **Wall clock:** 2–3 hours (was 8+ in Run 6)
- **Same valuable findings** (those came early, before the churn pattern)

---

*Generated by CC (Claude Opus 4.6), 2026-04-02T11:15+01:00*
