#!/usr/bin/env python3
"""Composable Directive Architecture Confer: 5-model CDSFL review.

All 5 models (CC2, CX, ChatGPT, Gemini, DeepSeek) under full CDSFL directives
review the composable directive architecture proposition, evaluate mathematical
modelling approaches, and propose implementation strategy.

Iterates until convergence or diminishing returns (max 3 rounds).
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from experiment_11_orchestrator import (
    call_openrouter, call_gemini, call_deepseek, call_codex, _log,
)

CDSFL_PATH = Path(__file__).parent / "cdsfl_registry" / "universal.toml"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8") if CDSFL_PATH.exists() else ""

CDSFL_FORMAL_PATH = Path(__file__).parent / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_FORMAL = CDSFL_FORMAL_PATH.read_text(encoding="utf-8") if CDSFL_FORMAL_PATH.exists() else ""

OUTPUT_DIR = Path(__file__).parent / "logs" / "composable_directives_confer"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# The confer packet — 6-field standard format
CONFER_PROMPT = """
=== REVIEW TARGET ===
Composable Directive Architecture for CDSFL: design, mathematical modelling,
and implementation strategy. This is a proposed architectural evolution where
CDSFL directives are decomposed into modular, composable packets that combine
dynamically per-dispatch to create task-specific cognitive configurations.

Your task: evaluate the proposition, propose how it should be mathematically
modelled within the existing CDSFL formal framework (MATHEMATICAL_APPENDIX.md),
identify the optimal implementation strategy, and falsify weak claims.

=== PROPOSITION SUMMARY ===

CLAIM: CDSFL directives can be decomposed into modular, composable packets that
combine dynamically per-dispatch to create task-specific cognitive configurations.
This preserves core Popperian constraints while tightening the problem space.
Evidence suggests this produces genuine cognitive diversity more efficiently than
multiple frontier models.

EVIDENCE CHAIN:
1. CX (same weights + different config) ≠ ChatGPT (same weights + bare config) — DEMONSTRATED
2. Therefore configuration drives at least some cognitive diversity — DEMONSTRATED
3. Therefore modular, composable configurations could manufacture diversity — PLAUSIBLE
4. Therefore dynamic per-dispatch composition is the natural architecture — FOLLOWS
5. Therefore the configured synthetic domain expert is buildable today — PIECES EXIST

THE FOUR-LAYER DIRECTIVE STACK:
| Layer | Scope | Changes When | Example | Status |
|---|---|---|---|---|
| Universal | All tasks, all models | Never | falsification_required, anti_deference | EXISTS |
| Domain | Per problem domain | Domain changes | Structural safety, medical protocols | EXISTS (28 files, 10 domains) |
| Phenotype | Per model/class | Capability observed | CX: tighter box; DeepSeek: simpler prompts | PARTIAL |
| Situation | Per dispatch | Every dispatch | Verified facts, code, adversarial brief | EXISTS (confer packet) |

MISSING PIECE: Dynamic composer (~200-400 lines) that assembles all four layers
per-dispatch. Reads task context → selects domain + phenotype packets → assembles
with universal + situation → validates monotonicity → emits per-dispatch directive set.

P-PASS RESULTS (5 passes survived):
- Pass 1: Combinatorial contradiction risk → MANAGEABLE (monotonicity enforcement exists)
- Pass 2: Already partially exists → TRUE but dynamic composition is genuinely new
- Pass 3: Coherence under dynamic assembly → REAL RISK, empirically testable
- Pass 4: Packet analogy → Better as "microservices for cognition"
- Pass 5: Config diversity = independent findings? → KEY FALSIFIABLE PREDICTION, N=1

=== EXISTING MATHEMATICAL FRAMEWORK (for context) ===

The CDSFL mathematical model (MATHEMATICAL_APPENDIX.md) currently covers:
- §1: Residual Risk R_n (Bayesian posterior after n passes)
- §2: Class-Specific Diversity Discount d_ik (pass × flaw class matrix)
- §3: Corroboration and termination
- §4: Severity-weighted coverage
- §5: Multi-agent coverage G_n
- §6: Priority-weighted coverage
- §7: Cognitive Measurement Framework:
  - §7.1: Duane NHPP (discovery rate decay)
  - §7.2: Abstraction Index H(x) (finding depth)
  - §7.3: Total Cognitive Yield Y(t) = N(t) · H̄(t)
  - §7.4: Online Total Value Estimator V̂
  - §7.5: Objective Alignment O_A (sycophancy detection)
  - §7.6: Adoption Delta Δ (independence measurement)
  - §7.7: Per-Finding Severity
  - §7.8: Multi-Verifier Severity (Bayesian evidence fusion)
  - §7.9: Capability Fingerprint (D_decay, v̄, A, C)
  - §7.11: Manager Selection Function
- §8: Emergence, Metacognition, Substrate Agnosticism:
  - §8.1: Metacognitive Feedback Protocol
  - §8.2: Composite System Emergence (Y_composite > max(Y_i) + k·σ̂)
  - §8.3: Second-Order Cognitive System definition
  - §8.4: Substrate Agnosticism
  - §8.5: Falsifiable Claims

KEY FORMULAS FOR REFERENCE:
- Detection: q_ik = f_del(i) · d_ik · p_ik
- Coverage: F_n = Σ_k w_k · [1 − Π_i (1 − q_ik)]
- Cognitive Yield: Y(t) = N(t) · H̄(t)
- Emergence: Y_composite > Y_union + k·σ̂(Y)
- Capability Fingerprint: (D_decay, v̄, A, C)
- Monotonicity: lower layers cannot weaken HARD constraints from higher layers

=== INTERACTION SURFACE ===

The composable directive architecture interacts with the existing framework via:
1. The CDSFL registry (cdsfl_registry/) — already has universal.toml + 28 domain
   files + model-specific Layer 4 files. Monotonicity enforcement exists.
2. The orchestrator (experiment_11_orchestrator.py) — dispatches to 5 models with
   per-model system prompts. Currently selects directives statically at benchmark start.
3. The confer packet format — already demonstrates dynamic situation-layer composition.
4. The phenotype layer — partial (model-specific registry settings exist but not
   wired to dynamic composition).
5. The mathematical model — needs extension to formalise composition effects on
   detection probability, cognitive diversity, and emergence.

=== VERIFIED FACTS ===
1. CX (gpt-5.4 + manufacturer system prompt + CDSFL as user-message) produces
   measurably different findings from ChatGPT (gpt-5.4 + CDSFL as system message).
   Same weights, different analytical phenotype. Demonstrated in Experiment 17.
2. CX found a qualitatively unique issue (dispatch_watchdog key mismatch) that
   no other model found — genuine biodiversity value from configuration alone.
3. The CDSFL registry already enforces monotonicity: lower layers cannot weaken
   HARD constraints. PolicyViolationError fires at merge time.
4. 28 domain-specific directive files exist across 10 domains (structural, hardware,
   chemistry, software, logistics, biomedical, industrial, product-engineering,
   cross-domain, mathematics).
5. The confer packet (6-field: review target, code extracts, interaction surface,
   verified facts, explicit unknowns, adversarial brief) IS a situation-layer
   directive composed dynamically per-dispatch.
6. Three-architecture review demonstrated genuine emergence: composite Y > max
   individual Y. Gemini found 16 issues CC/CX missed.
7. CX efficiency confer R2 (4 models, 2 rounds) identified that CX's overhead
   comes partly from MCP servers, xhigh reasoning effort, and session persistence —
   ALL now fixed via CLI overrides. Cost per dispatch should drop significantly.

=== EXPLICIT UNKNOWNS ===
1. Whether N different directive compositions of one model produce finding diversity
   equivalent to N different models. This is the key falsifiable prediction.
2. Whether composition order matters (is the stack commutative?).
3. Minimum effective composition size — below which directive packets lose effect.
4. Whether composed directives outperform monolithic directives of equal token length.
5. How to formally extend the mathematical model to capture composition effects.
   Specifically: how does d_ik (diversity discount) change when the "diversity" comes
   from configuration rather than different model weights?
6. Whether the dynamic composer can itself be automated (meta-composition).
7. The optimal granularity for directive packets — too coarse = monolithic (no benefit),
   too fine = incoherent (contradiction risk).

=== ADVERSARIAL BRIEF ===
The composable directive architecture claim may be weaker than it appears. Before
validating, test for:
(a) Configuration diversity may produce CORRELATED findings, not independent ones.
    Same model weights = same training distribution = shared blind spots. Config
    changes may only shift the output distribution, not the capability frontier.
(b) The CX evidence (N=1) may be an artifact of the manufacturer system prompt,
    not a generalisable property of configuration. Without the hidden prompt, the
    diversity disappears.
(c) Monotonicity enforcement may be necessary but not sufficient for coherence.
    Non-contradictory != coherent. A directive set can be internally consistent
    but collectively unfocused.
(d) The four-layer stack assumes clean separation of concerns. In practice,
    domain knowledge may interact with model phenotype in ways the stack cannot
    express (e.g., "DeepSeek needs simpler prompts" is phenotype, but "simpler
    structural engineering prompts" is phenotype × domain interaction).
(e) The dynamic composer adds system complexity. Every new abstraction layer is
    a new failure surface. The marginal diversity gain may not justify the
    engineering cost and maintenance burden.
(f) Human teams already do this (compartmentalised thinking, role assignment).
    The composable architecture may be reinventing organisation theory rather
    than discovering something novel. What does formalisation add?
=== END ADVERSARIAL BRIEF ===

YOUR TASK: Produce structured findings. For each finding, state:
- Finding ID (e.g. CDA-001)
- Type: NOVEL (new insight) | VALIDATION (confirms known claim) | CHALLENGE (disputes prior analysis)
- Severity: CRITICAL | HIGH | MEDIUM | LOW
- Description: what the insight, validation, or challenge is
- Mathematical formalisation: how this should be modelled in the existing framework
  (reference specific sections of MATHEMATICAL_APPENDIX.md where relevant)
- Proposed implementation: specific, concrete change or addition
- Falsification: how could this claim fail or this implementation make things worse?

Focus areas (in priority order):
1. Mathematical modelling of composition effects within the existing framework
2. Implementation architecture for the dynamic composer
3. Experimental design for Experiment 19 (testing the composable hypothesis)
4. Integration with existing infrastructure (registry, orchestrator, confer packet)
5. Risk analysis and boundary conditions
"""

MODELS = [
    ("CC2", "anthropic/claude-opus-4-6", "openrouter"),
    ("CX", None, "codex_exec"),
    ("ChatGPT", "openai/gpt-5.4", "openrouter"),
    ("Gemini", "gemini-3.1-pro-preview", "google"),
    ("DeepSeek", "deepseek-reasoner", "deepseek"),
]


def dispatch(label, model_id, api, prompt, round_idx):
    """Dispatch to a model and save results."""
    _log(f"  Dispatching to {label} ({model_id or 'codex exec'}) via {api}...")
    t0 = time.monotonic()
    try:
        if api == "openrouter":
            text = call_openrouter(model_id, CDSFL_FORMAL, prompt, max_tokens=32768, timeout=300)
        elif api == "codex_exec":
            text = call_codex(prompt, CDSFL_FORMAL, timeout=600, max_retries=1)
        elif api == "google":
            text = call_gemini(model_id, CDSFL_FORMAL, prompt, max_tokens=32768, timeout=300)
        elif api == "deepseek":
            text = call_deepseek(model_id, CDSFL_FORMAL, prompt, max_tokens=16384, timeout=900)
        else:
            raise ValueError(f"Unknown API: {api}")
        elapsed = time.monotonic() - t0
        _log(f"  {label}: {len(text)} chars, {elapsed:.1f}s")

        # Save
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        outfile = OUTPUT_DIR / f"round{round_idx}_{label.lower()}_{ts}.json"
        outfile.write_text(json.dumps({
            "model": label,
            "model_id": model_id or "codex-exec/gpt-5.4",
            "api": api,
            "round": round_idx,
            "chars": len(text),
            "elapsed_s": round(elapsed, 1),
            "response": text,
        }, indent=2), encoding="utf-8")
        _log(f"  Saved: {outfile}")
        return text, elapsed
    except Exception as e:
        elapsed = time.monotonic() - t0
        _log(f"  {label}: ERROR — {e} ({elapsed:.1f}s)")
        return f"ERROR: {e}", elapsed


def run_confer(max_rounds=3):
    """Run confer rounds until convergence or max_rounds."""
    all_findings = {}

    for round_idx in range(max_rounds):
        _log(f"\n=== CONFER ROUND {round_idx} ===\n")

        if round_idx == 0:
            prompt = CONFER_PROMPT
        else:
            # Build confer prompt with prior findings
            prior = "\n\n".join(
                f"--- {label} (Round {round_idx - 1}) ---\n{text[:4000]}"
                for label, (text, _) in all_findings.get(round_idx - 1, {}).items()
            )
            prompt = (
                f"=== CONFER ROUND {round_idx} ===\n"
                f"Previous findings from all models:\n\n{prior}\n\n"
                f"Original problem:\n{CONFER_PROMPT}\n\n"
                f"Your task: review all prior findings. Produce ONLY:\n"
                f"1. NOVEL findings not yet raised\n"
                f"2. CHALLENGES to prior findings you believe are wrong\n"
                f"3. VALIDATIONS of prior findings with additional evidence\n"
                f"4. MATHEMATICAL FORMALISATIONS that improve on prior proposals\n"
                f"Do NOT repeat findings already raised unless you have new evidence.\n"
                f"If you believe convergence has been reached, state so explicitly.\n"
            )

        round_results = {}
        for label, model_id, api in MODELS:
            text, elapsed = dispatch(label, model_id, api, prompt, round_idx)
            round_results[label] = (text, elapsed)

        all_findings[round_idx] = round_results

        # Check for convergence signals
        convergence_signals = sum(
            1 for label, (text, _) in round_results.items()
            if any(
                phrase in text.lower()
                for phrase in [
                    "convergence has been reached",
                    "convergence achieved",
                    "i believe convergence",
                    "declare convergence",
                    "sufficient convergence",
                ]
            )
        )
        _log(f"\nRound {round_idx}: {convergence_signals}/5 models signal convergence")

        if round_idx > 0 and convergence_signals >= 2:
            _log(f"Convergence reached at round {round_idx}.")
            break

    _log(f"\nConfer complete. {len(all_findings)} rounds, results in {OUTPUT_DIR}")


if __name__ == "__main__":
    _log("Composable Directive Architecture Confer — 5 models under CDSFL")
    _log(f"Output: {OUTPUT_DIR}")
    run_confer(max_rounds=3)
