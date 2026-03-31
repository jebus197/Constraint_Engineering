#!/usr/bin/env python3
"""Gemini Phase 1: Solo mathematical coherence audit of MATHEMATICAL_APPENDIX.md.

Uses decomposed dispatch (staged context loading) to deliver the full model
in chunks, then triggers Gemini's synthesis pass.

Chunks:
  1. §1-5: Base detection/risk framework (~16K chars)
  2. §6: Combined Machine-HIL Detection (G_n) (~9K chars)
  3. §7.1-7.6: Cognitive measurement — discovery through independence (~9K chars)
  4. §7.7-7.11 + §8: Severity, fingerprint, emergence (~15K chars)
  5. Notation summary + attribution (~5K chars)
  6. 12 verified composition extensions (formulas only)
  7. 5 deferred items (A-D1 through A-D5) with fix options
  8. 3 proposed new additions (A-N1 through A-N3)
  Final: Synthesis instruction — full mathematical coherence audit
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from decomposed_dispatch import (
    DecomposedChunk, decomposed_dispatch, save_decomposed_result,
)
from experiment_11_orchestrator import _log

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

BENCH_DIR = Path(__file__).parent
APPENDIX_PATH = BENCH_DIR.parent / "docs" / "MATHEMATICAL_APPENDIX.md"
CDSFL_PATH = BENCH_DIR / "directives" / "universal" / "cdsfl_core_formal.md"
OUTPUT_DIR = BENCH_DIR / "logs" / "gemini_math_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Load sources
# ─────────────────────────────────────────────────────────────────────────────

APPENDIX = APPENDIX_PATH.read_text(encoding="utf-8")
CDSFL = CDSFL_PATH.read_text(encoding="utf-8")
LINES = APPENDIX.split("\n")


def _section(start_line: int, end_line: int) -> str:
    """Extract lines (1-indexed, inclusive)."""
    return "\n".join(LINES[start_line - 1 : end_line])


# ─────────────────────────────────────────────────────────────────────────────
# Chunk definitions
# ─────────────────────────────────────────────────────────────────────────────

CHUNK_1 = _section(1, 280)     # Preamble + §1-5
CHUNK_2 = _section(281, 417)   # §6 G_n
CHUNK_3 = _section(418, 563)   # §7.1-7.6
CHUNK_4 = _section(564, 759)   # §7.7-7.11 + §8
CHUNK_5 = _section(760, 826)   # Notation summary + attribution

# Chunk 6: Verified composition extensions (formulas only, no code)
CHUNK_6_EXTENSIONS = """
=== 12 VERIFIED COMPOSITION EXTENSIONS ===
(All verified via SymPy, March 2026. These extend the existing model for
composable directive architecture. Not yet written into the appendix.)

1. UNIFIED DETECTION EQUATION (all 5 models converged):
   q_eff(a,k) = p(m,k) · α(L(g)) · κ(m,g) · d(a,k) · f_del(a) · η_dec(a)

   Where:
   - p(m,k) = base detection probability (existing)
   - α(L) = attention yield (new — models degrade with long directives)
   - κ(m,g) = coherence penalty (new — conflicting directives degrade quality)
   - d(a,k) = diversity (existing, now decomposed: d = d_weights · d_config)
   - f_del(a) = delivery feasibility (existing)
   - η_dec(a) = decomposition yield (existing)

   REDUCTION: When α=κ=1 and d is not decomposed, reduces to existing
   q_ik = f_del · φ_i · d_ik · p_ik. SymPy verified.

2. ATTENTION YIELD α(L):
   α(L) = 1                         if L ≤ L₀
   α(L) = exp(−β(L − L₀))          if L > L₀

   Where L = total directive length (chars), L₀ = model-specific attention
   threshold, β > 0 = decay rate. Properties: α(L₀)=1, monotonically
   decreasing for L > L₀, bounded in [0,1]. SymPy verified.

   DECOMPOSED DELIVERY EXTENSION (proposed, not yet verified by models):
   If payload of total length L_total is split into n chunks each of length
   Lᵢ < L₀, and the model processes each chunk at α(Lᵢ) ≈ 1, then:
   α_staged ≈ Π α(Lᵢ) ≈ 1  vs  α_monolithic = exp(−β(L_total − L₀)) ≪ 1
   This is a testable prediction about staged vs monolithic delivery.

3. COHERENCE PENALTY — CAPACITY-BASED (CC2/Gemini):
   κ_load(m,g) = exp(−γ · n(g) / C(m))

   Where n(g) = number of directives in composed set g, C(m) = model m's
   directive capacity (estimated from attention threshold). Monotonically
   decreasing in n, increasing in C. SymPy verified.

4. COHERENCE PENALTY — ENTROPY-BASED (DeepSeek):
   κ_focus(m,g) = 1 − H(g) / log|T(g)|

   Where H(g) = −Σ_t p(t)·log(p(t)) is Shannon entropy over topic
   distribution of directives, |T(g)| = number of distinct topics.
   Bounded [0,1]. Equals 1 when all directives are on one topic (maximally
   coherent), 0 when uniformly spread. SymPy verified.

   NOTE: κ_load and κ_focus are complementary, not contradictory. One measures
   capacity load, the other topic focus. They could be combined as:
   κ(m,g) = κ_load(m,g) · κ_focus(m,g)

5. DIVERSITY DECOMPOSITION:
   d(a,k) = d_weights(a,k) · d_config(a,k)

   Separates model diversity (different architectures/training) from
   configuration diversity (same model, different directives). Both factors
   ∈ [0,1]. Preserves all existing F_n properties. SymPy verified.

6. DIVERSITY RATIO:
   δ = J̄_config / J̄_model

   Where J̄ = mean Jaccard distance between finding sets. Bounded [0,1].
   δ = 1 means configuration diversity matches model diversity.
   The composable directive hypothesis predicts δ can be made arbitrarily
   close to 1 for certain task classes. SymPy verified.

7. HIERARCHICAL DEPENDENCE (ChatGPT):
   ρ = ρ_sub + (1 − ρ_sub) · ρ_cfg

   Standard residual correlation. ρ_sub = substrate correlation (same model
   architecture). ρ_cfg = configuration correlation (similar directives).
   If both ∈ [0,1], result ∈ [0,1]. SymPy verified.

8. CORRELATED JOINT MISS PROBABILITY:
   P(∩ miss) = Π(1 − qᵢ) · [1 + ρ · correction_term]

   Standard Pearson ρ model. Stays in [0,1] for ρ ∈ [−1,1]. SymPy verified.

9. ISING LOG-LINEAR MODEL (CC2 alternative, use with caution):
   P(∩ miss) = Π(1 − qᵢ) · exp(Σ ψ_ijk)

   Reduces to independent case when ψ = 0. BUT: can exceed 1 without bounds.
   Required constraint: Σψ ≤ −Σlog(1 − qᵢ). The Pearson model (item 8) is
   safer for current n=5. SymPy verified with noted constraint.

10. CORRELATION-ADJUSTED COVERAGE:
    F_n_adjusted = F_n · η_k

    Where η_k accounts for non-independence. Preserves F_n monotonicity in
    number of agents. SymPy verified.

11. CRITICAL MASS SIGMOID (DeepSeek) + OPTIMAL DIRECTIVE WINDOW:
    φ(L) = 1 / (1 + exp(−k(L − L_c)))

    Below critical length L_c, directives are ineffective (model hasn't
    received enough constraint to change behaviour). Combined with α(L):

    α(L) · φ(L) has a UNIQUE MAXIMUM at some L*.

    This is the optimal directive length. Too short: φ ≈ 0 (directives
    don't activate). Too long: α ≈ 0 (attention degrades). The sweet
    spot exists and is unique. SymPy verified.

12. COMPOSITION MONOTONICITY:
    HARD constraints are preserved through all composition operations.
    The composer enforces this structurally (PolicyViolationError at merge
    time). Lower layers cannot weaken higher-layer HARD constraints.
    This is a structural invariant, not a tunable parameter. SymPy verified.
"""

# Chunk 7: Deferred items
CHUNK_7_DEFERRED = """
=== 5 DEFERRED ITEMS REQUIRING RESOLUTION ===
(From 5-model meta-test Stage 1, March 2026. Each has proposed fix options.)

A-D1: §7.6 Δ CONFOUND
The symmetric difference in the adoption delta Δ masks B's productivity.
If A adopts 3 of B's findings and B adopts 0 of A's, the symmetric Δ
suggests mutual influence when actually it was one-directional.
FIX OPTION A: Asymmetric Δ — report Δ_adopt(A→B) and Δ_adopt(B→A) separately.
FIX OPTION B: Normalise by |A_adopt + A_drop| to make direction explicit.
RESOLVE: Which option is mathematically cleaner? Can they be unified?

A-D2: §7.2/§7.9/§XIII D SYMBOL TRIPLE COLLISION
The symbol D is used for three different quantities:
  - D_decay (§7.9 fingerprint: decay rate)
  - D (§7.2: information density in H(x))
  - D (§XIII white paper: architectural diversity)
FIX: Rename two of three. Candidates: D_decay stays (most established),
ρ_info for information density, δ_arch for architectural diversity.
RESOLVE: Confirm renaming or propose alternative.

A-D3: §7.5 O_A DOMAIN GUARD STEP FUNCTION
The domain guard in O_A uses a step function at |verifiable| ≥ 2.
This creates a discontinuity: going from 1 to 2 verifiable claims
produces a discrete jump in the objectivity metric.
FIX OPTION A: Bayesian smoothing — replace step with sigmoid.
FIX OPTION B: Accept as design choice (the discontinuity is intentional:
below 2 verifiable claims, alignment is genuinely unmeasurable).
RESOLVE: Is the discontinuity mathematically problematic or acceptable?

A-D4: §7.5 MUTUAL SUPPRESSION — F_conv = ∅ MASKING
When F_conv = ∅ (no convergent findings between two models), the mutual
suppression metric is undefined/zero. But F_conv = ∅ with large
|B_A ∪ B_B| (both models produced findings, none overlapped) could indicate
destructive convergence (models actively contradicting each other).
FIX: Flag F_conv = ∅ ∧ |B_A ∪ B_B| > 0 as a pathological case.
Define M_suppress = −1 (sentinel) or a separate diagnostic.
RESOLVE: Formalise the pathological case mathematically.

A-D5: §3 (CORE) DUAL TERMINATION
The current model does not distinguish convergence termination (finding rate
drops below threshold) from budget termination (wall-clock or token limit
reached). These have different implications for the residual risk estimate.
FIX: Formalise budget termination as a distinct state: T_budget vs T_converge.
R_n under T_budget should be marked as a LOWER BOUND (actual risk ≥ R_n)
because the process was interrupted, not exhausted.
RESOLVE: Write the formal definitions.
"""

# Chunk 8: Proposed new additions
CHUNK_8_NEW = """
=== 3 PROPOSED NEW ADDITIONS ===
(From 5-model composable directives confer, March 2026.)

A-N1: ANTI-PARROTING MECHANISM (proposed §7.12)
Detects when a model's findings in later rounds are derivative of other
models' earlier findings rather than independently derived.

novelty_rate(A, r) = |F_A^r ∖ F_prior^r| / |F_A^r|

Where F_A^r = findings from model A in round r, F_prior^r = all findings
from all models in rounds < r. When novelty_rate drops below threshold τ_n,
the model's weight in Y_composite is penalised:

w_parrot(A, r) = max(0, novelty_rate(A, r) − τ_n) / (1 − τ_n)

Applied: Y_composite uses w_parrot(A, r) · w_original(A) as the model weight.

QUESTIONS FOR REVIEW:
- Is the novelty_rate well-defined when F_A^r = ∅?
- Should the threshold τ_n be per-model or global?
- Does this interact with the existing convergence detector?

A-N2: MANAGER SELECTION FUNCTION (already in §7.11, for review)
selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) ≥ 0.5) ∧ (HARD ∨ Sev(f) > τ_soft)

This was added during the 3-model confer. Verify it is consistent with the
severity (§7.7) and multi-verifier (§7.8) definitions. In particular:
- The ≥ 0.5 threshold on S_v is calibrated to L_prior = 0. Is this noted?
- Does the HARD override mean HARD findings bypass verification entirely?

A-N3: CONTRIBUTION DISCOUNT / BENCHING (proposed)
When a model's findings are consistently low-quality (low severity, low
verification rate), its weight in the composite system should decrease:

w_position(A) = v̄(A) · (1 − max(0, Δ_max(A) − τ_Δ)) · ascending_bonus(A)

Where:
- v̄(A) = mean verification score (§7.9 fingerprint)
- Δ_max(A) = maximum adoption delta with any other model
- τ_Δ = adoption delta threshold (above which the model is considered
  derivative rather than independent)
- ascending_bonus(A) = bonus for models showing ascending abstraction
  (H(x) increasing over rounds)

QUESTIONS FOR REVIEW:
- Is v̄ the right anchor for base weight?
- Can Δ_max be gamed by a model that deliberately avoids overlap?
- Should ascending_bonus be additive or multiplicative?
"""

# ─────────────────────────────────────────────────────────────────────────────
# Final synthesis instruction
# ─────────────────────────────────────────────────────────────────────────────

FINAL_INSTRUCTION = """
You are Gemini 3.1 Pro, operating under CDSFL as system prompt. You have
received the COMPLETE mathematical model in 8 chunks:

- Chunks 1-5: The existing MATHEMATICAL_APPENDIX.md (826 lines, ~57K chars)
- Chunk 6: 12 verified composition extensions (SymPy-verified but not yet in appendix)
- Chunk 7: 5 deferred items requiring resolution
- Chunk 8: 3 proposed new additions

YOUR TASK: Full mathematical coherence audit.

You are the mathematical specialist. This is PURE MATHEMATICS — no code, no
architecture, no implementation concerns. Your output must be mathematical
analysis only.

For each of the following tasks, provide your analysis:

TASK 1: SYMBOL TABLE AUDIT
List every symbol used across the entire model (existing + extensions + new).
For each, state: symbol, definition, first occurrence (section), type
(scalar/vector/function/predicate), domain, and whether it collides with
any other symbol. Flag every inconsistency.

TASK 2: DEFERRED ITEM RESOLUTION (A-D1 through A-D5)
For each deferred item, provide:
- Your recommended resolution with full mathematical justification
- The exact text to add/modify in the appendix
- Whether the fix is HARD (must be done for correctness) or SOFT (improvement)

TASK 3: NEW ADDITION ASSESSMENT (A-N1 through A-N3)
For each proposed addition:
- Is it mathematically well-defined? (edge cases, domain, range)
- Does it conflict with any existing formula?
- Is it redundant with anything already in the model?
- Your recommended formulation (modify if needed)

TASK 4: COMPOSITION EXTENSION INTEGRATION
The 12 extensions need to be integrated as new appendix sections (§7.12-7.16
or similar). Propose:
- Section structure and numbering
- Which extensions group naturally
- Cross-references to existing sections
- Any simplifications or unifications that reduce total symbol count

TASK 5: CROSS-SECTION CONSISTENCY
Check the entire model for:
- Formulas that reference symbols defined elsewhere — are all references correct?
- Reduction properties — do all claimed reductions actually hold?
- Domain/range mismatches (e.g., a probability > 1, a log of a negative number)
- Unstated assumptions that should be explicit

TASK 6: DECOMPOSED DELIVERY AS MATHEMATICAL CLAIM
The staged delivery mechanism used to deliver this model to you (the "wait"
pattern) is itself a mathematical claim about attention yield composition:

  α_staged(L_total, n) ≈ Π α(Lᵢ)  where each Lᵢ < L₀

Assess: Is this a valid mathematical model of staged context processing?
What assumptions does it require? Is it falsifiable? Should it be formalised
as part of the attention yield extension (item 2 in the composition extensions)?

OUTPUT FORMAT:
For each task, use this structure:

TASK N:
FINDING: [what you found]
EVIDENCE: [mathematical justification]
PROPOSED_CHANGE: [exact text for appendix, if any]
CONSTRAINT_CLASS: HARD | SOFT
CONFIDENCE: 0.XX

Be thorough. Be precise. Challenge everything. The only way out is mathematics.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_gemini_audit():
    """Run the decomposed Gemini mathematical audit."""

    chunks = [
        DecomposedChunk(CHUNK_1, label="§1-5: Base detection/risk framework"),
        DecomposedChunk(CHUNK_2, label="§6: Combined Machine-HIL Detection (G_n)"),
        DecomposedChunk(CHUNK_3, label="§7.1-7.6: Cognitive measurement (discovery–independence)"),
        DecomposedChunk(CHUNK_4, label="§7.7-7.11+§8: Severity, fingerprint, emergence"),
        DecomposedChunk(CHUNK_5, label="Notation summary + attribution"),
        DecomposedChunk(CHUNK_6_EXTENSIONS, label="12 verified composition extensions"),
        DecomposedChunk(CHUNK_7_DEFERRED, label="5 deferred items (A-D1 through A-D5)"),
        DecomposedChunk(CHUNK_8_NEW, label="3 proposed new additions (A-N1 through A-N3)"),
    ]

    total_chars = sum(c.chars for c in chunks) + len(FINAL_INSTRUCTION)
    _log(f"Gemini Math Audit — {len(chunks)} chunks, ~{total_chars:,} chars total")
    _log(f"CDSFL system prompt: {len(CDSFL):,} chars")
    for i, c in enumerate(chunks):
        _log(f"  Chunk {i+1}: {c.chars:,} chars — {c.label}")
    _log(f"  Final instruction: {len(FINAL_INSTRUCTION):,} chars")
    _log(f"Output: {OUTPUT_DIR}")

    result = decomposed_dispatch(
        api="google",
        model_id="gemini-3.1-pro-preview",
        system_prompt=CDSFL,
        chunks=chunks,
        final_instruction=FINAL_INSTRUCTION,
        max_tokens=65536,
        timeout=600,
    )

    # Save result
    outfile = save_decomposed_result(result, OUTPUT_DIR, "gemini", round_idx=0)
    _log(f"\nGemini audit complete: {result.elapsed_s}s, {len(result.text):,} chars")
    _log(f"Chunks delivered: {result.chunks_delivered}")
    _log(f"Wait responses: {result.wait_responses}")
    _log(f"Result saved: {outfile}")

    return result


if __name__ == "__main__":
    # Load API keys
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

    _log("=== Gemini Phase 1: Mathematical Coherence Audit ===")
    _log(f"Decomposed delivery: 8 chunks + final instruction")
    result = run_gemini_audit()
    _log(f"\n=== AUDIT COMPLETE ===")
    _log(f"Response: {len(result.text):,} chars")
