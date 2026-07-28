# Experiment 39 — Revised Scope

**Date:** 12 April 2026, 02:26 BST
**Context:** Correction to initial scope refinement. Sub-areas are research questions for the experiment, not build targets.

CDSFL = Constraint-Driven Synthesis and Falsification, the Popperian multi-vendor LLM falsification framework.

---

## Correction

The initial scope refinement (Exp39_Scope_Refinement_2026-04-12.md) treated the proposed additions as implementation tasks. The founder's intent: these are **sub-areas of study** for Exp 39. The models investigate them, produce findings, and converge on each. The 22+ fixes are runner infrastructure; the sub-areas are the research questions.

---

## Convergence Risk

Without domain-specialist cells, models studying domain-specific topics (mathematical model extensions, biological architecture, cross-domain synthesis) produce generic findings that never converge. No verification mechanism → no convergence threshold met → wall-clock cap.

**Solution:** Enable specialist cells for the domains under study. Not loosening constraints — extending the constraint box with domain-appropriate tools.

---

## Specialist Cells for Exp 39

### Load-bearing (enable fully)

| Cell | Domain | Tools | Status |
|------|--------|-------|--------|
| Mathematics | Equation verification, convergence proofs, parameter bounds | SymPy, z3, mpmath | B-Cell has tools; needs TOML routing config |
| CS/Software | Code correctness, architecture verification | AST, pytest, ruff, mypy, bandit | CT + B-Cell operational |
| Statistics | Convergence metrics, hypothesis testing | statsmodels, scipy.stats | B-Cell has tools; needs TOML routing config |

### Secondary (enable, lower priority)

| Cell | Domain | Justification |
|------|--------|---------------|
| Biology | Immune analogy evaluation | Meta but valid; macrophage researches the biology |
| Information Science | Retrieval quality, citation verification | Needed if macrophage active |

### Shadow only (test architecture, no pipeline effect)

| Cell | Domain | Justification |
|------|--------|---------------|
| Physics | Dimensional analysis, units | Not directly relevant to CDSFL methodology study |
| Chemistry | Stoichiometry, thermodynamics | Bench Run 2 territory |
| Structural Engineering | Safety factors, material properties | Bench Run 2 territory |

---

## Macrophage — Auditability Resolved

Initial concern (non-determinism of web search) addressed by existing infrastructure:

1. **Verification chain** — model responses already non-deterministic; same Merkle chain handles web search results
2. **Evidence capture** — findings hashed, chained, sealed, queryable
3. **Shadow first** — logs findings without pipeline effect until proven reliable
4. **Blockchain anchoring** — planned post-BR2, provides permanent verifiability
5. **Queryable database** — full reasoning chain traceable by anyone

Further safeguards beyond shadow mode are engineering choices, not fundamental blockers.

---

## Mathematical Model as Sub-Area

The mathematical model is a research question for Exp 39, not a prerequisite. Models study it, propose extensions, verify with SymPy/z3, challenge each other. Output: **verified proposals** for extending R_k(i) (the iterative residual-risk self-assessment after round i) to account for specialist cells, macrophage, cross-domain synthesis. The founder decides what to adopt.

---

## Phase Structure

| Phase | Topic | Specialist Cells |
|-------|-------|-----------------|
| 0 | Fix verification (22+ fixes) | CS/Software |
| 1 | Expert Encodings S_k integration | CS/Software, Mathematics |
| 2 | Mathematical model extensions | Mathematics, Statistics |
| 3 | Macrophage design study | Biology, Information Science |
| 4 | Cross-domain synthesis | All enabled cells |
| Integration | Synthesise across phases | All |

S_k is the severity/stringency tristate gate. Macrophage runs in shadow/advisory mode across all phases.

---

## Falsifiable Predictions

1. Specialist cells reduce rounds-to-convergence per phase vs generic verification. *(Phase 0 vs later phases.)*
2. Macrophage shadow findings would have changed prior round outcomes if active. *(Replay against registry state.)*
3. Models produce verified (SymPy/z3) mathematical extensions with tool access vs verbal argument without. *(B-Cell logs.)* [SPECULATIVE]
