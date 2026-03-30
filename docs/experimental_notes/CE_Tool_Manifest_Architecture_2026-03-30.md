# Tool Manifest Architecture for CDSFL Expert Encodings

**Date:** 30 March 2026

---

## The Core Idea

SymPy verification of mathematical claims should be an intrinsic element of the P-pass process, not a separate step. In other domains, other applicable tools should be equally pluggable and user-selectable. When you load a domain-level expert encoding, you should be asked what tools you want to install and use, if not already present. This follows the same paradigm as MCP (Model Context Protocol), where servers declare their capabilities and clients discover and use them.

The encoding becomes a configured verification environment. Load it and you get both the constraint box **and** the tools to verify against it. The P-pass is not just "try to break it with reasoning." It is "try to break it with reasoning AND the appropriate computational tools."

---

## What Exists Now

The interactive smoke test file, `interactive_smoke.py`, has a working `verify_sympy` function. It runs in a subprocess sandbox with a 10-second timeout. It parses SymPy expressions, simplifies them, and classifies results as `VERIFIED_TRUE`, `VERIFIED_FALSE`, or `UNVERIFIABLE`. This function works and has been tested in the tutorial and smoke test pipeline.

`PAPER.md` describes SymPy verification as intrinsic to CDSFL conditions. The registry is supposed to enforce it "by code not by prompt instructions." The mathematical model includes a pluggable domain-specific variable `V_s`.

However:

- SymPy verification is **not** wired into the main benchmark runner, `run_benchmark.py`
- It exists only in `interactive_smoke.py`
- There is no tool declaration mechanism in the encoding files — they are plain text with no metadata about what verification tools they need
- There is no MCP-like tool discovery or installation paradigm

---

## The Three-Layer Encoding Format

Each expert encoding becomes three parts:

1. **The constraints.** HARD and SOFT constraints as they exist now. This is what bounds the model within the problem space.

2. **The tool manifest.** What verification tools this domain needs, separated into required and optional. Each tool entry includes:
   - A name
   - An installation method (pip install, MCP server URL, system package)
   - A verification hook describing how to use it during P-pass

3. **The verification hooks.** Specific mappings from claim types to verification methods. A mathematical claim gets sent to SymPy. A thermodynamic calculation gets numerical verification. A molecular structure claim gets checked via RDKit or equivalent.

---

## Example Tool Manifests

### Mathematics proof task

**Required tools:**
- SymPy — `pip install sympy`. Hook: verify mathematical expression, returns true or false.

**Optional tools:**
- Wolfram Alpha via MCP server. Hook: verify numerical result with specified tolerance.

---

### Chemistry process task

**Required tools:**
- NumPy for numerical calculations. Hook: verify mass balance, energy balance, heat transfer calculations.

**Optional tools:**
- RDKit for molecular property verification.
- Thermodynamic database lookup for enthalpy and heat capacity values.

---

### Turbulence closure task

**Required tools:**
- NumPy and SciPy for numerical PDE solving. Hook: verify realizability conditions on closure tensor.

**Optional tools:**
- OpenFOAM for CFD simulation.
- DNS benchmark datasets for comparison.

---

## How the Runner Uses the Manifest

When the benchmark runner loads an expert encoding, it reads the tool manifest section. For each required tool, it checks availability:

- If a required tool is **missing** — warn the user and offer installation instructions.
- If an optional tool is **missing** — note this and continue without it.

During the P-pass loop, when a model produces output, the runner:

1. Extracts verifiable claims (mathematical expressions, numerical calculations, structural assertions)
2. Routes them to the appropriate verification hook
3. Feeds results back into the P-pass as additional evidence

A claim that SymPy verifies as false is a finding. A claim that SymPy cannot parse is flagged as unverifiable.

This is **graceful degradation**: if the tool is not available, the hook is skipped and flagged, not failed. The P-pass continues with reasoning-only verification for that claim type.

---

## The 60/40 Split

The bench should be 60% known-answer tasks and 40% open problems. With 27 known-answer tasks, this means approximately 18 open-problem tasks for a total of 45.

The 18 open-problem candidates, drawn from the earlier analysis:

**Tier 1 (4 tasks)**
- Turbulence and RANS closure
- Navier-Stokes existence and smoothness
- Catalytic nitrogen fixation
- The Collatz Conjecture

**Tier 2 (6 tasks)**
- The Arrow of Time
- Baryon asymmetry and baryogenesis
- The battery dendrite problem
- Carbon capture thermodynamics
- Protein folding dynamics in vivo
- Morphogenesis and Turing pattern formation

**Tier 2b (4 tasks)**
- The Strong CP problem and axion detection
- Neutrino mass hierarchy
- The Hubble tension
- The black hole information paradox

**Engineering frontier (4 tasks)**
- Commercial nuclear fusion and the Lawson criterion
- Quantum error correction thresholds
- Universal vaccine design via conserved epitopes
- AI interpretability and the black box problem

For open-problem tasks, the measured outputs are:
- **Classification accuracy** — did CDSFL correctly distinguish HARD from SOFT from SPECULATIVE?
- **Gap identification** — did it find what is missing?
- **Contradiction detection** — did multi-architecture review find conflicts between approaches?
- **Decay curve quality** — genuine exploration versus churn?
- **Tool-verification rate** — what fraction of claims survived computational verification?

---

## The Measurement Advantage

The tool-verified P-pass adds a concrete measurement dimension. On every task, you can now measure: what fraction of the model's mathematical or numerical claims were computationally verified as correct?

`PAPER.md` already describes this as the "SymPy verification rate." It is supposed to be a convergence gate:

- A model with a **flat finding curve** and a **low verification rate** is producing churn.
- A model with a **decaying finding curve** and a **high verification rate** is doing genuine falsification work.

This measurement is currently not implemented in the main runner. It exists only in the interactive smoke test. Promoting it to the main benchmark gives every task a computational honesty metric, not just a reasoning quality assessment.

---

## Implementation Path

| Step | Description | Type |
|------|-------------|------|
| 1 | Promote `verify_sympy` from `interactive_smoke.py` to a shared module at `bench/verification/sympy_verify.py` | Code |
| 2 | Define the tool manifest format as a new section in the encoding file format | Code |
| 3 | Build a tool discovery and availability checker — check if each declared tool is importable or reachable, report status, offer installation instructions | Code |
| 4 | Wire verification hooks into the P-pass loop in `run_benchmark.py` | Code |
| 5 | Create the 18 open-problem task JSON definitions with expert encodings including tool manifests | Content |
| 6 | Update the runner for the 45-task bench structure with the 60/40 split | Config |

Steps 1–4 and Step 5 can be done in parallel. Step 6 depends on both.

---

## The MCP Parallel

MCP declares tool capabilities as JSON schemas. Clients discover available tools and call them with structured arguments. The tool manifest in expert encodings follows the same pattern but scoped to domain verification:

- **MCP** says: "here is a server that provides these tools."
- **The encoding** says: "here is a domain that requires these verification capabilities."
- **MCP** handles discovery and invocation.
- **The encoding** handles declaration and hookup.
- **The runner** is the client that mediates between the encoding's tool requirements and the available verification infrastructure.

This is not MCP itself. It is the same design pattern applied to a different problem: domain-specific computational verification within an adversarial falsification loop.

---

## Extrapolation

**What generalises.** The encoding becomes a portable verification laboratory. Load the pharmaceutical crystallisation encoding and you get the thermodynamic constraints AND the tool chain to verify mass balance, heat transfer, and supersaturation profiles. The encoding is self-sufficient — it carries its own verification apparatus. This is what makes it genuinely tradable. A domain expert produces an encoding that includes not just "what I know" but "how I verify." The community that receives it gets both the knowledge and the quality assurance in one artifact.

**Boundary conditions.** The paradigm assumes verification tools exist for the domain. Mathematics has SymPy. Chemistry has RDKit. Engineering has numerical solvers. But some domains — particularly meta-reasoning tasks like self-verifying proofs or CDSFL consistency analysis — have no external verification tool. The verification is purely logical. The paradigm must accommodate "no computational verification available" as a valid state, not a failure.

**Falsifiable questions.**
1. Does tool-verified P-pass produce measurably higher accuracy than reasoning-only P-pass on the same tasks? Directly testable by running with and without verification hooks.
2. Does the tool-manifest paradigm reduce the barrier to creating domain encodings? Testable but [SPECULATIVE] at this stage.
