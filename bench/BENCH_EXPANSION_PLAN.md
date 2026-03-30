# Bench Expansion Plan: Expert Encodings, Open Problems, and Tool-Verified P-Pass

**Date:** 30 March 2026
**Status:** PLANNED — not yet in progress
**Trigger:** After Experiment 15/16 iteration stabilises and immediate management layer work is complete

---

## 1. Problem Statement

The bench has three gaps that limit the strength of its conclusions:

### 1a. Expert encodings don't match the frontier tasks

The 28 domain-specific directive files are generic industry constraint boxes (creepage distances, CAP theorem, heat transfer formulas). They are organised by broad domain and loaded by alphabetical sort. The mapping to the 27 frontier tasks is systematically wrong:

- Mathematics (7 tasks, all proof-based): directive explicitly disclaims proof-based mathematics
- Software (6 tasks): gets distributed systems directive; 5 of 6 are unrelated to distributed systems
- Chemistry (3 tasks): gets analytical chemistry; none are analytical chemistry
- Hardware (2 tasks): gets embedded systems; neither is embedded
- Physics (1 task): no directive exists at all
- Cross-domain (5 tasks): gets mechanical-electrical interface; 2 are meta-reasoning
- Industrial (1 task): rocket nozzle gets CNC machining directive

**Required:** Task-specific expert encodings — constraint boxes that bound each model to the specific problem space under consideration.

### 1b. All tasks have known solutions

Every frontier task has a known answer. Critics can dismiss improvements as training-data retrieval. The bench cannot demonstrate the "science calculator" thesis without tasks where the answer doesn't exist.

**Required:** Open-problem frontier tasks where the measured output is rigour, classification accuracy, and gap identification — not correctness.

### 1c. SymPy verification is not wired into the main runner

`verify_sympy()` exists in `interactive_smoke.py` and works. The PAPER describes it as intrinsic to CDSFL conditions. But `run_benchmark.py` doesn't use it. Computational verification is not part of the P-pass loop.

**Required:** Tool-verified P-pass with pluggable verification hooks declared by each encoding.

---

## 2. Target Architecture

### 2.1 Encoding format (extended)

Each expert encoding file gains two new sections:

```
TASK: ft-004
DOMAIN: Mathematics — Proof
SCOPE: Continuous nowhere-differentiable functions, Weierstrass construction

[HARD constraints — non-negotiable]
...

[SOFT constraints — negotiable]
...

[Verification procedures]
...

[Tools — required]
sympy: pip install sympy
  hook: verify_expression(claim) → VERIFIED_TRUE | VERIFIED_FALSE | UNVERIFIABLE

[Tools — optional]
wolfram: mcp://wolfram-alpha
  hook: verify_numerical(expression, tolerance) → bool

[Limitations]
...
```

### 2.2 Encoding content principle

Expert encodings contain:
- The known **structure** of the problem space (mathematical framework, physical laws, known theorems)
- **HARD constraints** that any valid solution must satisfy
- **Known failure modes** (where models and humans commonly go wrong)
- **Verification procedures** (how to check whether a proposed solution is complete and correct)
- **Tool declarations** (what computational tools can verify claims in this domain)

Expert encodings do NOT contain:
- The solution itself
- Key proof steps or derivations
- Numerical answers from ground_truth_notes
- Hints that effectively give away the answer

The encoding tells the model HOW to think about the problem and WHERE the guardrails are. It does not tell the model WHAT to think.

### 2.3 Directory structure

```
bench/directives/
  universal/           ← existing (unchanged)
    cdsfl_core.txt
    cdsfl_core_formal.md
  task_specific/       ← NEW: per-task expert encodings
    ft-001.txt         ← Erdos-Szekeres (mathematics/proof)
    ft-002.txt         ← Irrationality of sum of square roots
    ...
    ft-027.txt         ← Riemann Hypothesis
    ft-028.txt         ← Turbulence closure (open problem)
    ...
    ft-045.txt         ← AI interpretability (open problem)
  hardware/            ← existing domain-level (kept as general safety layer)
  software/
  chemistry/
  ...
```

### 2.4 Runner modification

`run_benchmark.py` changes:

1. `load_task_directives(directives_dir, task_id)` — new function, checks `task_specific/{task_id}.txt`
2. `compose_directives()` gains a third layer: universal → domain → task-specific
3. `load_tool_manifest(encoding_text)` — parses [Tools] sections, checks availability
4. `verify_claim(claim, tool, hook)` — routes claims to appropriate verification tool
5. P-pass loop calls `verify_claim()` on extracted mathematical/numerical claims

Estimated code change: ~150-200 lines in `run_benchmark.py`, ~100 lines in new `bench/verification/` module.

### 2.5 Bench composition (60/40 split)

**Known-answer tasks (27 existing):** Unchanged. Provide calibration data.

**Open-problem tasks (18 new):** No known solution. Measured outputs: HARD/SOFT/SPECULATIVE classification accuracy, gap identification, contradiction detection, decay curve quality, tool-verification rate.

**Total: 45 tasks.** 60% known-answer, 40% open-problem.

---

## 3. The 18 Open-Problem Tasks

### Tier 1 — Strongest candidates (4 tasks)

| ID | Title | Domain | Why amenable |
|----|-------|--------|-------------|
| ft-028 | Turbulence and RANS Closure | Physics/Engineering | Richest constraint box. N-S equations defined. DNS data for verification. Realizability conditions. Measurable progress. |
| ft-029 | Navier-Stokes Existence and Smoothness | Mathematics | Clay Millennium. Deep existing structure. Failed Lean proof (2025) as case study. CDSFL can map proof strategy landscape. |
| ft-030 | Catalytic Nitrogen Fixation | Chemistry/Engineering | N≡N bond 945 kJ/mol. Nitrogenase mechanism known. Clear target (ambient T&P). Multi-domain. |
| ft-031 | The Collatz Conjecture | Mathematics | Simple statement, profound resistance. Known approaches with clear failure modes. Computational verifiability. |

### Tier 2 — Strong candidates (6 tasks)

| ID | Title | Domain | Why amenable |
|----|-------|--------|-------------|
| ft-032 | The Arrow of Time | Physics | Well-defined stat-mech. Known circular reasoning in existing derivations. Falsification catches circularity. |
| ft-033 | Baryon Asymmetry | Physics | Sakharov conditions defined. Known candidate mechanisms with constraints. |
| ft-034 | Battery Dendrite Problem | Chemistry/Engineering | Clear electrochemistry. Phase-field models exist. Multi-physics coupling. |
| ft-035 | Carbon Capture Thermodynamics | Engineering | Minimum work of separation is a hard bound. Known sorbent chemistries. Engineering optimisation. |
| ft-036 | Protein Folding In Vivo | Biology/Chemistry | AlphaFold solved static. In-vivo dynamics is open. MD simulation framework. Chaperone interactions. |
| ft-037 | Morphogenesis and Turing Patterns | Biology/Mathematics | Reaction-diffusion equations defined. Parameter search bounded. Computational verifiability. |

### Tier 2b — Physics frontier (4 tasks)

| ID | Title | Domain | Why amenable |
|----|-------|--------|-------------|
| ft-038 | The Strong CP Problem and Axion | Physics | θ parameter. Falsifiable prediction (axion mass). Clear mathematical framework. |
| ft-039 | Neutrino Mass Hierarchy | Physics | Dirac vs Majorana. Neutrinoless double beta decay. Defined experimental signatures. |
| ft-040 | The Hubble Tension | Physics/Cosmology | H₀ discrepancy between CMB and local measurements. Statistical analysis. Multi-dataset. |
| ft-041 | Black Hole Information Paradox | Physics | Unitarity vs GR. Hawking radiation entanglement entropy. Well-defined mathematical conflict. |

### Engineering frontier (4 tasks)

| ID | Title | Domain | Why amenable |
|----|-------|--------|-------------|
| ft-042 | Nuclear Fusion Lawson Criterion | Physics/Engineering | Triple product defined. Known engineering constraints. Measurable progress. |
| ft-043 | Quantum Error Correction Thresholds | Physics/Engineering | Surface codes. Threshold theorem. Defined metrics. |
| ft-044 | Universal Vaccine via Conserved Epitopes | Biology/Chemistry | Conserved viral structures. Antibody cross-reactivity. Defined target. |
| ft-045 | AI Interpretability | Software/Mathematics | Transformer latent space. Formal framework needed. Meta-level (AI studying AI). |

---

## 4. Tool Manifest — Verification Tools by Domain

| Domain | Required tools | Optional tools |
|--------|---------------|----------------|
| Mathematics (proof) | SymPy (symbolic algebra, simplification, equation verification) | Wolfram Alpha (MCP), Lean4 (formal verification) |
| Mathematics (numerical) | NumPy, SciPy | Wolfram Alpha (MCP) |
| Software (code) | Python interpreter (run and test generated code) | pytest, mypy |
| Chemistry | NumPy (stoichiometry, thermodynamics calculations) | RDKit (molecular properties), thermodynamic databases |
| Physics | SymPy (equation verification), NumPy (numerical checks) | Wolfram Alpha (MCP) |
| Engineering | NumPy, SciPy (numerical PDE/ODE) | OpenFOAM (CFD), FEniCS (FEM) |
| Biology | NumPy (population dynamics, kinetics) | BioPython (sequence analysis) |
| Cross-domain / meta | None computational — verification is purely logical | — |

---

## 5. Implementation Steps

### Phase 1: Expert encodings for existing 27 tasks

Write task-specific expert encodings for ft-001 through ft-027. Each encoding:
- Bounds the model to the specific problem space
- Contains HARD/SOFT constraints, known failure modes, verification procedures
- Declares required/optional tools
- Does NOT leak the solution (P-pass each encoding against its task's ground_truth_notes)

**Estimated effort:** 27 files, ~50-100 lines each. Can be parallelised.

### Phase 2: Open-problem task definitions

Write JSON task definitions for ft-028 through ft-045. Each includes:
- `prompt`: the structured problem statement
- `verification_method`: how to assess the analysis (classification accuracy, not correctness)
- `why_frontier_hard`: what makes this genuinely hard
- `expected_single_pass_accuracy`: "N/A — open problem" or estimated analysis quality
- `ground_truth_notes`: what IS known (for classification accuracy measurement)

Write corresponding expert encodings for each.

**Estimated effort:** 18 JSON files + 18 encoding files.

### Phase 3: Runner modifications

1. Promote `verify_sympy()` to `bench/verification/sympy_verify.py`
2. Add `load_task_directives()` to `run_benchmark.py`
3. Extend `compose_directives()` for three-layer composition
4. Add tool manifest parser
5. Wire verification hooks into P-pass loop
6. Update CLI: `--condition` gains `universal+domain+task` option
7. Update evaluation pipeline for open-problem scoring

**Estimated effort:** ~200-300 lines of new code.

### Phase 4: Integration and testing

1. Dry-run all 45 tasks under all conditions
2. Verify tool availability and graceful degradation
3. Verify no answer leakage in expert encodings
4. Update bench unit tests
5. Update documentation (PAPER, README, EXPERIMENTAL_RESULTS)

---

## 6. Open Questions

### 6.1 Encoding granularity

How specific should expert encodings be? A continuum exists:
- Too vague: "Check your arithmetic" (current mathematics_general.txt) — no value
- Right level: "Proof must demonstrate uniform convergence; known failure mode is hand-waving the tail bound" — bounds without solving
- Too specific: "Use x_m = (⌊b^m x⌋ + 1)/b^m and show the head terms cancel" — gives the answer

Where is the line? The P-pass on each encoding should catch answer leakage, but the principle needs to be explicit.

**Proposed rule:** The encoding may state WHAT must be true (constraints) and WHAT goes wrong (failure modes). It may NOT state HOW to achieve it (proof steps, construction methods, specific formulas for the solution).

### 6.2 Open-problem scoring

Known-answer tasks have clear scoring: did the model get it right? Open-problem tasks need a different metric. Proposed:
- **Classification accuracy:** Does HARD/SOFT/SPECULATIVE classification agree with expert consensus?
- **Gap identification:** Did the analysis identify known open sub-problems?
- **Contradiction detection:** Did multi-architecture review find genuine conflicts?
- **Verification rate:** Fraction of claims that survived tool verification
- **Decay curve quality:** Genuine exploration vs churn (vocabulary novelty, cross-round overlap)

Is this sufficient? What does a domain expert need to see to decide if the analysis is "bunk/typical AI generated slop or not"?

### 6.3 Tool availability and fairness

If SymPy verification is intrinsic to the P-pass, models that produce SymPy-parseable output benefit more than those that don't. Is this a confound or a feature? (Arguably a feature — producing machine-verifiable claims is itself a sign of rigour.)

Models accessed via different APIs have different tool-calling capabilities. Claude can use tools natively; GPT via function calling; Gemini via tool declarations; DeepSeek has limited tool support. The tool-verified P-pass may advantage models with better structured output. Does the runner need to normalise for this?

### 6.4 18 open problems — is that too many?

Each open-problem task requires genuine domain expertise to encode. Can the encodings be written to a high enough standard for 18 diverse domains? Or should we start with 4-6 (Tier 1 + 2 strongest Tier 2) and expand after validating the approach?

**Proposed:** Start with Tier 1 (4 tasks: turbulence, Navier-Stokes, nitrogen fixation, Collatz). Validate the encoding format and scoring. Then expand to the full 18.

### 6.5 Existing domain directives — keep or replace?

The generic domain directives (hardware_power.txt, chemistry_process.txt, etc.) still have value as general safety layers. The three-layer composition (universal → domain → task-specific) keeps them. But if task-specific encodings make domain directives redundant, should the domain layer be optional?

**Proposed:** Keep as optional middle layer. The 2×2 factorial design can test whether the domain layer adds value on top of task-specific encodings.

### 6.6 Claim extraction from free-form text

The interactive smoke test works because it has structured steps with explicit `sympy_claims` lists. The main benchmark gets free-form text responses. Extracting verifiable mathematical claims from free-form text is a separate problem. Options:
- Require models to emit claims in a parseable format (schema constraint)
- Use a secondary model pass to extract and formalise claims
- Use regex/heuristic extraction for obvious mathematical expressions

This needs prototyping before committing to an approach.

### 6.7 The recursive question

ft-045 (AI Interpretability) is AI studying AI. ft-025 (CDSFL Consistency) is CDSFL testing itself. Adding these meta-level tasks creates recursion. Is this a feature (the methodology should be able to examine itself) or a confound (self-referential analysis may be systematically biased)?

The PAPER explicitly discusses this (the methodology applied to itself, Experiment 12). The position appears to be: self-reference is a feature, but findings from self-referential tasks must be weighted differently from external-subject tasks.

---

## 7. Dependencies and Sequencing

```
Experiment 15/16 iteration
        │
        ├── stabilises → Immune persistence (JSON, ~150 lines)
        │                        │
        │                        ├── Policy Engine consolidation
        │                        │
        │                        └──── Expert encodings (Phase 1+2)
        │                                    │
        │                                    ├── Runner modifications (Phase 3)
        │                                    │
        │                                    └──── Integration + testing (Phase 4)
        │                                                │
        │                                                └── Bench Run 2
        │
        └── (parallel) Expert encoding content work can begin any time
```

Expert encoding content (Phases 1+2) can be written in parallel with experiment iteration. Runner modifications (Phase 3) depend on the encoding format being finalised. Integration (Phase 4) depends on everything.

---

## 8. Success Criteria

The bench expansion is complete when:

1. All 27 existing tasks have task-specific expert encodings
2. At least 4 open-problem tasks (Tier 1) have JSON definitions and expert encodings
3. The runner loads task-specific encodings and composes three layers
4. SymPy verification is wired into the P-pass loop for mathematics tasks
5. A dry-run of all tasks under all conditions completes without error
6. No expert encoding leaks its task's solution (verified by P-pass)
7. Open-problem scoring metrics are implemented in `evaluate.py`
8. Documentation updated (PAPER, README, EXPERIMENTAL_RESULTS, ONBOARDING, RECOVERY)

Bench Run 2 can proceed once criteria 1-8 are met.

---

*This plan is a living document. It will be updated as experiments inform priorities and as open questions are resolved.*
