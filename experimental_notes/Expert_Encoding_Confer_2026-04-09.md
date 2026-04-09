# Expert Encoding Confer Synthesis — 9 April 2026

Two confers dispatched to **Codex GPT-5.4** and **Gemini 3.1 Pro** under full CDSFL 4-layer schema.

## Confer 1: Expert Encoding S_k Gates

### Mandatory Template Fixes (converged, both models)

| Finding | Codex Proposal | Gemini Proposal | Assessment |
|---------|---------------|-----------------|------------|
| **E aggregation broken** — any $e_i=0$ collapses E to zero | Renormalise weighted geometric mean over applicable gates only | Weighted arithmetic mean | Design choice; geometric mean tighter, arithmetic more forgiving |
| **Baseline semantics missing** — delta-from-baseline never defined | First-class template section with explicit definitions per domain | Acknowledged but no schema | Codex's approach more complete |
| **Applicability/skip rules missing** — undefined behaviour for non-applicable gates | Renormalise weights, remove skipped gates from denominator | Default $E=1.0$ when no graded tools apply | Codex cleaner for cross-domain comparability |

### Architectural Findings

- **Tristate** (Codex): ADMISSIBLE / REJECTED / ESCALATE. Distinguishes "demonstrated bad" from "incomplete information." Significant — currently conflated.
- **Epistemological boundary** (Gemini): $S_k$ evaluates tool outcomes, not ground truth. High $S_k$ = absence of known failure modes, not absence of all failure modes.
- **Environment state corruption** (Gemini): If gate $g_1$ modifies filesystem, $g_2$ evaluates corrupted state. Template ignores this.
- **Tool determinism over-specified** (Codex): SAT solvers, FE solvers are "reproducible," not "deterministic." Template would exclude legitimate tools.
- **Timeout handling** (Gemini): Long-running tools killed at timeout register as $A=0$. Need per-domain $t_{\max}$ with timeout → UNVERIFIED, not hard fail.

### Python Reference Fixes

| Gate | Issue | Proposed Fix |
|------|-------|-------------|
| g2 (import) | Too brittle — side-effectful imports, missing env vars | Replace with `py_compile` (Codex) |
| g3 (mypy) | Vetoes untyped codebases universally | Make conditional on existing type baseline (Codex) |
| e5 (SymPy/z3) | Non-executable without LLM intervention | Conditional + weight renormalise (Codex) or replace with `crosshair` (Gemini) |

### Domain-Specific Encodings

| Domain | Gemini (minimal) | Codex (deep) |
|--------|-----------------|--------------|
| **Mathematics** | 2 hard (Lean 4 syntax + type check), 1 graded | 4 hard + 5 graded (step validity, final equivalence, boundary cases, units, corroboration) |
| **Chemistry** | 2 hard (SMILES + balance), 2 graded | 4 hard + 6 graded (mass balance, thermal safety, materials, robustness, regulatory) |
| **Physics/Structural** | 2 hard (Pint dimensional + OpenSeesPy), 2 graded | 4 hard + 5 graded (error resolution, margin, cross-check, sensitivity, traceability) |
| **Hardware** | 2 hard (KiCad ERC + netlist), 1 graded | 4 hard + 6 graded (target resolution, simulation, ERC, margin, firmware, RF match) |

Pattern: Gemini defines the floor, Codex defines the ceiling. **Composable, not competing.**

### Cross-Domain Gaps (S_k fundamentally insufficient)

Converged: **biomedical/clinical** and **legal/regulatory** require HIL. S_k can provide partial evidence but cannot substitute for domain expert judgment in safety-critical or legally binding contexts.

---

## Confer 2: Encoding Enrichment

### Core Diagnosis (converged)

The 27 directives are **compliance skeletons**. Missing categories:

| Category | Description | Tool-Verifiable? |
|----------|-------------|-----------------|
| Failure mode priors | The 80/20 of what actually breaks | Partially (known failure patterns → targeted tests) |
| Diagnostic heuristics | "If X and Y together, suspect Z" | No — requires LLM interpretation |
| Tool-chain realism | Where simulation lies | Yes (validation against known benchmarks) |
| Regime boundaries | Where textbook equations stop working | Partially (boundary detection via sensitivity analysis) |
| Standard gotchas | Known loopholes and misapplications | No — requires domain knowledge |
| Disagreement maps (Codex) | Where experts genuinely differ | No — requires HIL |
| Evidence quality grading (Codex) | Code requirement vs vendor lore vs anecdote | No — requires provenance tracking |
| Escalation triggers (Codex) | Signals to stop and consult senior colleague | Partially (threshold-based) |

### Synthetic Expertise Quality

**Strong coverage:** software (all), mathematics, electronics/RF first principles, analytical chemistry

**Weak/patchy:** injection moulding production, process chemistry scale-up, maritime logistics, clinical trial regulation, CNC production, temporary works

**Key failure modes:**
1. Textbook-over-practice bias (both)
2. Seductive ideality — idealised solutions that don't work in practice (Gemini)
3. Standard blending — mixing US/EU codes into invalid hybrids (Gemini)
4. Plausible synthesis hallucination — true fragments combined into false claim (Codex)
5. False quantification — precise numbers where evidence is weak (Codex)
6. **Suspicious fast convergence** — shared textbook priors masquerading as corroboration (Codex)

### Verification Status for Bench Run 2

| Domain | Minimum Status | Rationale |
|--------|---------------|-----------|
| Software (all) | CROSS-VERIFIED | Strong model coverage, tool-verifiable |
| Mathematics | CROSS-VERIFIED | Strong coverage, SymPy/z3 verifiable |
| Analytical chemistry | CROSS-VERIFIED | Strong coverage, tool-verifiable |
| Hardware (electronics) | CROSS-VERIFIED (Codex) / VALIDATED (Gemini) | Divergence on safety implications |
| Process chemistry | **VALIDATED (HIL required)** | Scale-up heuristics patchy, safety-critical |
| Structural engineering | **VALIDATED (HIL required)** | Failure modes kill people |
| Biomedical | **VALIDATED (HIL required)** | Regulatory + safety-critical |
| Industrial (CNC, welding, injection) | **VALIDATED (HIL required)** | Production heuristics weak |
| Logistics | CROSS-VERIFIED | Lower consequence of error |

### Enrichment Process Design (converged)

Both reject collaborative co-drafting. Both recommend **isolated adversarial review**:

1. **Independent generation** — each model drafts rich encoding in isolation
2. **Independent adversarial review** — different models attack each draft
3. **Synthesis** — merge surviving content
4. **Isolated red-team pass** — fresh context, adversarial brief
5. **HIL review** — where required by domain status

Core principle: **error independence must be preserved** as long as possible.

### Priority Ordering

| Priority | Gemini (pipeline-first) | Codex (risk-first) |
|----------|------------------------|-------------------|
| 1 | software_python_sk | structural_temporary |
| 2 | mathematics_general | chemistry_process |
| 3 | cross_software_hardware | biomedical_clinical |
| 4-9 | Then high-consequence domains | Then pipeline domains |

For BR2: **Gemini's ordering is more pragmatic** — pipeline must work before enriched encodings can demonstrate value.

---

## Source Files

- Expert encodings Codex: `bench/logs/confer_expert_encodings/expert_encodings_cx_20260409T211501Z.txt` (37,449 chars)
- Expert encodings Gemini: `bench/logs/confer_expert_encodings/expert_encodings_gemini_20260409T211501Z.txt` (12,105 chars)
- Enrichment Codex: `bench/logs/confer_encoding_enrichment/encoding_enrichment_cx_20260409T211902Z.txt` (45,790 chars)
- Enrichment Gemini: `bench/logs/confer_encoding_enrichment/encoding_enrichment_gemini_20260409T211902Z.txt` (11,044 chars)
- Template: `bench/directives/universal/expert_encoding_template.md`
- Python reference: `bench/directives/software/software_python_sk.txt`
- Confer scripts: `bench/confer_expert_encodings.py`, `bench/confer_encoding_enrichment.py`
