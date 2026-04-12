# Experiment 39 — Scope Refinement Analysis

**Date:** 12 April 2026, 01:30 BST
**Context:** Founder-proposed additions to Exp 39 scope, assessed for feasibility

---

## Proposed Additions (6)

### 1. Expert Encodings Integration

**Status:** Schema complete (10 sections, S_k framework, tristate). Python encoding at CROSS-VERIFIED. Not wired into runner.

**Integration path:** Immune pipeline B-Cell + CT infrastructure → S_k gate evaluator → registry feedback. Estimated 150-200 lines.

**Verdict:** ✅ Fits in Exp 39 as a dedicated phase.

### 2. Single System + Distributed Compute

**Status:** Single-model spec exists (516 lines, .gitignored, DRAFT). Distributed protocol documented.

**Assessment:** Architectural changes requiring dispatch, convergence, and mathematical model rework. Months of work.

**Verdict:** ❌ Does not fit. Separate workstream post-Bench Run 2.

### 3. Research Cell — The Macrophage

**Naming:** Macrophage (active hunter, processor, presenter). In ouroboros mode: Microglia (brain-resident immune cells).

**Architecture:** Pluggable via TOML config + CellVerdict interface. Stage 2 parallel execution. No refactoring needed.

**HARD constraint:** Non-determinism. Web search results vary by day. Requires caching/snapshotting for reproducibility.

**Verdict:** ⚠️ Feasible as shadow-mode prototype. Full activation in Exp 40 after measuring contribution.

### 4. Composable Domain Cell Types

**Status:** Architecture already supports this. Specialist B-Cell subtypes designed (Software, Maths, Physics, Chemistry, Biology). TOML registration. Cross-synthesis via Helper T-Cell voting.

**Granularity:** One cell per discipline initially. Split when empirical data justifies it.

**Verdict:** ✅ No new code needed. Specialist cells are a separate build-out when domain encodings exist.

### 5. Mathematical Model Extension

**Current model:** R_k(i) = R_k(i-1) · (1 - q_ik) / (1 - q_ik · R_k(i-1)), q = η·d·p

**Extension path:** Add λ_ext parameter modifying p_ik when external research available.

**Principle:** Build → Run → Measure → THEN fit. Extending before data is speculation.

**Verdict:** ❌ Must follow data. Exp 39 generates data; subsequent experiment fits parameters.

### 6. Finding Extraction / HIL Phase Gate

**Status:** Registry tracks everything. Report generator creates summaries. Gap: human review pause between burst mode phases.

**Integration:** `build_findings_summary()` at phase transitions already produces summaries. Add HIL approval gate. ~30-50 lines.

**Verdict:** ✅ Fits in Exp 39.

---

## Exp 39 Scope Summary

| Component | Status | Effort | In Scope? |
|-----------|--------|--------|-----------|
| 22+ fix verification | Built | Done | ✅ Core |
| Expert Encodings S_k | Designed | 150-200 LOC | ✅ Phase |
| HIL phase gate | Trivial | 30-50 LOC | ✅ Addition |
| Gemini → OpenRouter | Config | ~10 LOC | ✅ Switch |
| Macrophage prototype | Novel | 200-300 LOC | ⚠️ Shadow only |
| Single/distributed | Draft | Months | ❌ Later |
| Math model extension | Analytical | After data | ❌ Later |
| Domain cell build-out | Designed | After encodings | ❌ Later |

---

## Gemini OpenRouter Switch

- **Model ID:** `google/gemini-3.1-pro-preview`
- **Pricing:** Identical ($2.00/M in, $12.00/M out)
- **Reasoning:** `extra_body.reasoning.effort: "high"` → Google thinkingLevel high
- **Change:** ~10 lines in `experiment_11_orchestrator.py` ModelConfig
- **Requirement:** Empirical quality comparison before bench commitment

---

## Extrapolation

### What generalises
- Macrophage concept: dedicated information-gathering agent distinct from reasoning agents, with retrieved information going through falsification chain
- Composable cell types: domain config → selective activation → weighted voting → cross-synthesis

### Boundary conditions
- Macrophage fails when external sources are unreliable/adversarial — needs citation verification quality gate
- Domain cell separation fails at discipline boundaries (e.g., thermodynamics at chemistry-physics interface)

### New falsifiable questions
1. Does macrophage measurably improve η (finding detection rate)? *Testable in one experiment.*
2. Does specialist cell diversity improve γ (convergence speed) beyond model diversity? *Testable by comparison.*
3. Minimum domain cells for cross-synthesis emergence? *Testable by panel variation.* [SPECULATIVE]

---

## Sources

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Google Research: Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)
- [BioContextAI: Community-based biomedical context for agentic systems](https://www.biorxiv.org/content/10.1101/2025.07.21.665729v1.full)
- [ScienceDirect: Artificial Immune Systems overview](https://www.sciencedirect.com/topics/immunology-and-microbiology/artificial-immune-system)
- [AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/html/2601.01743v1)
