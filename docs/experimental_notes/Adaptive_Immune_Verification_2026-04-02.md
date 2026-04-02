# Adaptive Immune Verification: T-Cells for the Collective Immune System

**Date:** 2 April 2026
**Trigger:** Founder observation — verification agents are the T-cells
**Status:** DESIGN — P-passed, falsifiable questions registered

## Core Insight

The current `DetectorHealthMonitor` is innate immunity — single-threaded,
hardcoded pathology checks. The pipeline has no adaptive immunity: no
population of agents that independently verify findings and learn from
exposure.

The 5 generator models are B-cells (produce antibodies/findings). The
missing layer is T-cells (verification agents that check findings against
actual code). The extension is regulatory T-cells (meta-verifiers that
prevent over-rejection).

## Architecture

### Stage 1: Innate Immunity (automated, zero cost, sub-second)
- Similarity dedup via `_finding_similarity()`
- SymPy verification of mathematical claims
- AST structural checking of code claims
- Fast, deterministic, non-specific

### Stage 2: Adaptive Immunity (massively parallel verification agents)
- After dedup: ~30 findings → spawn 30 verification agents in parallel
- Each agent: one finding + file path → reads code, runs SymPy/AST, returns verdict
- Local `claude` CLI agents on Max subscription: zero marginal token cost
- ~10-30s per agent (checking one specific claim, not exploring a codebase)
- Model diversity: mix local CC, cheap OpenRouter models (Qwen3 Coder free,
  DeepSeek-R1-Distill), to prevent correlated blind spots

### Stage 3: Regulatory T-cells (meta-verification, 3-5 agents)
- Review Stage 2 verdicts for correctness
- Prevent autoimmune response (valid findings wrongly rejected)
- Asymmetric threshold: rejection requires stronger evidence than confirmation
- If >95% agreement with Stage 2: accept. Disagreements → next round adjudicates.

### Stage 4: Filtered Context Injection
- Only CONFIRMED findings enter next round's context
- REJECTED findings logged with evidence
- Raw findings preserved in checkpoint for auditability

## Cost Pyramid (inverts at each level)

| Layer | Task | Time per unit | Context needed |
|-------|------|---------------|----------------|
| Generator | Review ~100K source, produce findings | 60-120s | Full codebase |
| Verifier | Check one claim against one file | 10-30s | One finding + one file |
| Meta-verifier | Check one verdict against evidence | 10-20s | One verdict + evidence |

On Max subscription: zero marginal cost for local agents.
Hardware constraint: ~30 concurrent agents on MacBook, hundreds on cloud.

## Nested D-Decay Convergence

The Duane NHPP model applies at every level:
- **Generator D-decay:** finding rate declines as bugs exhausted
- **Verifier D-decay:** FP detection rate declines as obvious FPs caught
- **Meta-verifier D-decay:** verifier-error rate declines as patterns stabilise

Three nested Duane curves converging simultaneously. The methodology
reviews itself at every level.

Residual FP rate after n layers (each catching ~76%):
- 1 layer: 24%
- 2 layers: 5.8%
- 3 layers: 1.4%

## Biological Mapping

| Immune System | CDSFL Architecture |
|---|---|
| Pathogen | Bug in target code |
| B-cell (antibody production) | Generator model (finding production) |
| T-helper cell | PM/orchestrator (dispatches generators) |
| Cytotoxic T-cell | Verification agent (rejects false findings) |
| Regulatory T-cell | Meta-verifier (prevents over-rejection) |
| Memory B-cell | Verification cache (known patterns) |
| Clonal selection | Successful strategies reinforced |
| Thymic selection | High-false-rejection agents demoted |
| Innate immunity | SymPy/AST automated checks |
| Adaptive immunity | Agent-based FFF verification |
| Cytokine signalling | Finding context injection |
| Immune memory | Skip re-checking confirmed patterns |

## Boundary Conditions

1. **Homogeneous population:** shared blind spots → model diversity defence
2. **Autoimmune response:** over-rejection → asymmetric threshold defence
3. **Immune exhaustion:** resource starvation → hardware-aware scaling
4. **Cytokine storm:** cascading verification → hard budget caps

## Falsifiable Questions

1. Does agent diversity (mixed architectures) produce lower residual FP
   rates than homogeneous population?
2. Does the meta-verification layer reduce or increase net error rate?
3. Does three-level D-decay produce faster convergence than single-level?
4. What is the optimal verifier:finding ratio?
5. Does verification caching introduce stale-cache errors over time?

## Implementation Dependency

Requires the PM filter architecture (Stage 1-2 from
`PM_Filter_Architecture_2026-04-02.md`) as foundation. The T-cell
architecture extends it from single-PM to population-based verification.

Build sequence:
1. Wire PM filter (Stages 1-2 from earlier design) — ~200 lines
2. Parallelise verification (one agent per finding) — ~100 lines
3. Add meta-verification layer — ~100 lines
4. Add verification cache — ~150 lines
5. Add hardware-aware agent scaling — ~50 lines

Estimated total: ~600 lines on top of existing infrastructure.
