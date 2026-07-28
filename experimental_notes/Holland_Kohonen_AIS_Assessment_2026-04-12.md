# Holland, Kohonen, and Artificial Immune Systems: Assessment of Relevance to CDSFL

**Date:** 12 April 2026
**Type:** Literature assessment
**Trigger:** Question posed — do these research lineages impact CDSFL, or are they already covered?

CDSFL = Constraint-Driven Synthesis and Falsification, the Popperian multi-vendor LLM falsification framework.

## Overview

Three research lineages evaluated against CDSFL: John Henry Holland's complex adaptive systems and learning classifier systems; Teuvo Kohonen's self-organising maps; and the broader AIS (Artificial Immune Systems) field that connects them.

**Short answer:** CDSFL already embodies most of the relevant principles, in some cases more thoroughly than published AIS systems. Five incremental improvements are worth pursuing. None requires importing a new algorithm wholesale.

---

## 1. Holland: Complex Adaptive Systems

Holland identified seven CAS (Complex Adaptive Systems) fundamentals — four properties (aggregation, nonlinearity, flows, diversity) and three mechanisms (tagging, internal models, building blocks).

**CDSFL embodies 5 of 7:**

| Fundamental | CDSFL Implementation | Status |
|---|---|---|
| Aggregation | Equivalence classes via union-find | Covered |
| Nonlinearity | S_k = A·E multiplicative gate | Covered |
| Flows | Staged finding pipeline, resource balancing | Covered |
| Diversity | 5 heterogeneous LLMs, 6 cell types, never benched | Covered |
| Tagging | flaw_class routing, DefectCategory strings | Covered (static) |
| Internal models | No anticipatory dispatch | **Gap** |
| Building blocks | No recombination of findings | Not applicable |

S_k is the severity/stringency tristate gate.

**Gap: Internal models.** CDSFL does not predict what each model will find next round and steer dispatch accordingly. The DiminishingReturnsDetector tracks per-model novelty rates — the data for prediction exists, but the forward-looking coupling to prompt construction does not.

**Gap: Credit assignment.** No reinforcement loop propagates confirmation/rejection verdicts back into dispatch weighting. CapabilityFingerprint is static, not adaptive.

The Schema Theorem does not apply (no GA, genetic algorithm). Echo provides loose structural analogies at the finding level.

## 2. Holland: Learning Classifier Systems

LCS (Learning Classifier Systems) combines condition-action rules with reinforcement learning and a genetic algorithm for rule discovery. CDSFL's pipeline contains condition-action structures (S_k gate, remediation chains, FSM transition table) but these are static and designer-specified.

The inversely-proportional mutation rate from CLONALG (good strategies fine-tuned, bad strategies radically changed) is a useful heuristic the DetectorHealthMonitor could adopt, though Bayesian optimisation achieves the same result with less conceptual overhead.

## 3. Kohonen: Self-Organising Maps

**SOMs (Self-Organising Maps) are the wrong tool for CDSFL's problem.** At ~169 canonical findings, the map would have ~64 neurons — marginal territory where SOM adds nothing over simpler methods. The PNNL study (2022) that applied SOMs to 137K CVEs used BERT embeddings as input to the SOM, confirming the embedding does the heavy lifting.

**The actionable finding is not about SOMs.** `_finding_similarity()` already flags its own limitation in a docstring: "a middle ground between raw Jaccard (too strict) and embedding-based similarity (too complex for the current infrastructure)." The complexity argument no longer holds — `sentence-transformers` is available, implementation is ~10 lines, inference under 1 second.

**Second finding:** A 2025 paper on multi-agent LLM convergence measured intrinsic dimensionality (TwoNN-Id) of the embedding space and found it decreases sharply as models converge (~7.94 → ~0.64). This semantic convergence signal is independent of lexical kappa metrics and could serve as a complementary fourth kappa metric.

## 4. Artificial Immune Systems

The AIS field connects Holland and Kohonen through computational immune mechanisms. Key researchers: Forrest (negative selection), de Castro (CLONALG, aiNet), Timmis (DCA), Matzinger (danger theory).

**Field status:** Low-activity. ICARIS last ran standalone ~2013. Timmis's 2007 self-criticism ("AIS has reached an impasse") remains substantially unrefuted. **No published work combines AIS with LLM multi-agent systems.**

### What CDSFL already embodies

| AIS Concept | CDSFL Component | Assessment |
|---|---|---|
| Trained innate immunity | DetectorHealthMonitor (adaptive sensitivity, remediation, pathology memory) | More thorough than published AIS |
| Danger signals | Reg-T autoimmune detection (rejection rate > 65% → override) | Computationally substantive |
| Immune memory | NK Cell false-positive database | Partial — within-experiment only |
| Signal integration | S_k = A·E tristate gate | Structurally analogous to DCA (Dendritic Cell Algorithm) |
| Idiotypic suppression | NK Cell deduplication | Hard threshold, not continuous |

### Ranked improvements (value vs. cost)

1. **Persistent immune memory** — Cross-experiment finding database with encounter counts and outcome records. Low cost, direct value. [Priority: HIGH]

2. **Continuous suppression function** — Replace hard tau_sim threshold (adjusted twice already) with idiotypic-inspired proportional suppression: weight = base × ∏(1 - sim_to_each_other). Addresses documented false-duplicate problem. [Priority: HIGH]

3. **Frequency-scaled confidence** — Findings matching patterns seen N times get log(1+N) confidence scaling. Piggybacks on persistent memory. [Priority: MEDIUM]

4. **Inversely-proportional parameter adaptation** — Successful verification strategies fine-tuned, failing strategies get larger perturbations. Partially exists in DetectorHealthMonitor. [Priority: MEDIUM]

5. **Multi-signal triage accumulation** (DCA-inspired) — Value increases if CDSFL moves to streaming processing. Low current value for batch architecture. [Priority: LOW]

### Not recommended

- **Negative selection:** Exponential scaling in natural language, boundary-coverage holes at exactly the boundary that matters (novel valid finding vs. hallucination).
- **Full CLONALG:** Bayesian optimisation is simpler for the same result.
- **Full DCA:** Signal categorisation problem is presupposed, not solved.

## 5. Net Assessment

Holland provides theoretical vocabulary for what CDSFL already does, plus two genuine gaps (anticipatory dispatch, credit assignment). Kohonen is a dead end, but the research trail leads to embedding-based similarity — a real improvement at minimal cost. AIS is the most relevant strand, but CDSFL is already ahead of the published literature in several areas.

The highest-value improvements are incremental extensions of existing infrastructure: persistent memory, continuous suppression, embedding similarity, credit assignment loop. None requires importing a new algorithm wholesale.

**Novel position confirmed:** No published work combines immune-inspired verification pipelines with multi-agent frontier LLM systems under formal convergence measurement. The immune cell naming is metaphorical, but the DetectorHealthMonitor's adaptive self-regulation and the S_k tristate gate are computationally substantive.

[VERIFY:current] Absence of AIS+LLM publications based on searches conducted 12 April 2026.

## Sources

### Holland / CAS / LCS
- Holland, J.H. (1975) *Adaptation in Natural and Artificial Systems*
- Holland, J.H. (1995) *Hidden Order: How Adaptation Builds Complexity*
- Holland, J.H. (2012) *Signals and Boundaries: Building Blocks for Complex Adaptive Systems*
- Wilson, S.W. (1995) "Classifier fitness based on accuracy" — XCS
- Urbanowicz, R.J. & Moore, J.H. (2009) "Learning Classifier Systems: A Complete Introduction"

### Kohonen / SOMs
- Kohonen, T. (1982/2001) *Self-Organizing Maps*
- Survey of SOM advances 2014-2024 (arXiv 2501.08416, January 2025)
- PNNL: "Efficient Clustering of Software Vulnerabilities using SOM" (IEEE HST 2022)
- GPTrace: crash deduplication using LLM embeddings (arXiv 2512.01609, 2025)
- "Emergent Convergence in Multi-Agent LLM Annotation" (arXiv 2512.00047, 2025)
- Comparative analysis of text embedding models for bug report similarity (arXiv 2308.09193, 2023)

### Artificial Immune Systems
- Forrest, S. et al. (1994) "Self-Non-Self Discrimination in a Computer"
- de Castro, L.N. & Von Zuben, F.J. (2000) "Learning and Optimization Using the Clonal Selection Principle"
- Greensmith, J. et al. (2005) "Detecting Danger: The Dendritic Cell Algorithm"
- Matzinger, P. (1994) "Tolerance, Danger, and the Extended Family"
- Timmis, J. (2007) "Artificial Immune Systems: Today and Tomorrow"
- Jerne, N.K. (1974) Idiotypic network theory (Nobel Prize 1984)
- IIM-DCA with self-adaptive thresholds (2022)
- Immune-inspired AI for edge environments (2025)
