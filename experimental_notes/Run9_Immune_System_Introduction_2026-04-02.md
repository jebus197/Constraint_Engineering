# An Introduction to the CDSFL Immune System: What Run 9 Enables and Why It Matters

**Date:** 2 April 2026, 23:57 BST
**Audience:** Readers not already deep in the CDSFL project
**Status:** Run 8 (observation baseline) live; Run 9 (load-bearing immune) pending validation

---

## What This Document Covers

CDSFL is a methodology for making AI-assisted technical work more reliable. Multiple AI models examine the same code or technical artefact, produce findings about what might be wrong, and then those findings are verified through structured falsification before being acted on.

**The problem Run 9 solves:** When multiple AI models produce findings across multiple rounds of review, roughly three-quarters of those findings are noise — duplicate observations, false positives, hallucinated bugs, and severity inflation as models restate familiar issues with increasing confidence. Run 7b demonstrated this: **76% of findings were churn**, meaning they added no new information. That churn pollutes the context for subsequent rounds, producing more churn, wasting compute, and making genuine findings harder to find.

**The solution:** A verification pipeline that sits between rounds. Before findings from one round enter the context for the next round, they pass through six specialised verification agents. Each agent checks the findings from a different angle using different tools. Findings that fail verification are filtered out. Findings that pass are promoted into context. The result: models see only verified, high-signal input, producing fewer but better findings.

---

## Why the Biological Immune System

This is not a metaphor. It is a structural analogy with functional consequences.

The human immune system faces the same problem: distinguish genuine threats from harmless material, using multiple independent detection mechanisms, without destroying healthy tissue in the process. 500 million years of evolutionary selection pressure converged on highly specialised cell types, each with a distinct function, working in parallel and communicating through structured signals.

If a single general-purpose cell could do the same job, evolution would have selected for it (simpler, cheaper to maintain). The persistence of specialisation means it genuinely outperforms generalisation when threats are diverse and unpredictable.

Our threats are diverse and unpredictable. A finding might claim a mathematical bound is violated, a function is missing from source, or a statistical test is insignificant. These are fundamentally different claims requiring fundamentally different verification tools.

---

## The Six Cell Types

The pipeline has three stages:

| Stage | Agent | Function | Time | Tools |
|-------|-------|----------|------|-------|
| 1 | **Dendritic Cell** | Classify findings by claim type | ~1s | Regex patterns |
| 2 (parallel) | **Cytotoxic T-Cell** | Code FFF — read source, verify bugs exist | 30–60s | Claude CLI + Bash/Grep/Read |
| 2 (parallel) | **B-Cell** | Math/Logic/Stats verification | 1–10s | SymPy + z3 + statsmodels |
| 2 (parallel) | **NK Cell** | Dedup + known false-positive matching | <1s | Similarity function + FP DB |
| 3a | **Helper T-Cell** | Confidence-weighted verdict synthesis | ~1s | Aggregation logic |
| 3b | **Regulatory T-Cell** | Autoimmune prevention | ~1s | Pipeline health checks |

### Stage 1: Dendritic Cell (Triage)

**Biology:** Dendritic cells bridge innate and adaptive immunity. They sample the environment, capture foreign material, and present it to other immune cells with context for the right response. They classify, not fight.

**CDSFL:** Classifies each finding by claim type — statistical, logical, structural, mathematical, or code-behavioural. The classification determines which verification pathway the finding needs. Uses pure Python pattern matching. Priority order: statistical → logical → structural → mathematical → behavioural (determined empirically — statistical patterns like p-values are the most distinctive).

### Stage 2: Cytotoxic T-Cell (Code Verification)

**Biology:** Killer cells. Identify compromised cells by inspecting surface proteins. Direct contact, direct verification, direct destruction if warranted.

**CDSFL:** Reads actual source files, checks whether claimed bugs exist at cited locations, produces structured evidence. The most expensive agent (Claude CLI with file access, 30–60s per batch).

**Level 3 Structural Enforcement:** The CT agent operates under strict code constraints, not natural language instructions:

1. **Schema-enforced output:** A JSON schema forces the agent to produce structured evidence. Each piece must include: file path, line number, exact code snippet, and observation. These are not optional.

2. **Mechanical verification:** After the agent returns evidence, `_verify_ct_claim()` reads the real file at the real line and checks whether the cited code actually exists:
   - Exact match → confidence 1.0
   - Found within ±2 lines → confidence 0.8
   - 60%+ token overlap → confidence 0.5
   - No match → confidence 0.0 (agent hallucinated)

3. **Verdict from evidence, not opinion:** The agent is an *investigator*, not a *judge*. If evidence says "bug exists" and mechanical check confirms the code is real, verdict = confirmed. The agent cannot override the mechanical verification.

### Stage 2: B-Cell (Adaptive Verification)

**Biology:** The most adaptive cells in the immune system. Undergo somatic hypermutation (rapidly mutating antibody genes to fine-tune response) and class switching (changing antibody type based on infection — IgM first response, IgG refined response).

**CDSFL:** Selects verification tool based on claim type:
- Mathematical claims → **SymPy** (symbolic mathematics)
- Logical invariants → **z3-solver** (satisfiability modulo theories)
- Statistical claims → **statsmodels** (hypothesis testing)

**Class switching:** When SymPy returns UNCERTAIN on a mathematical claim, the B-Cell switches to z3 as fallback. z3 works with satisfiability rather than symbolic simplification, so claims ambiguous under one approach may be decidable under the other. This mirrors the biological mechanism precisely.

### Stage 2: NK Cell (Pattern Memory)

**Biology:** Traditionally innate immunity (act without prior exposure), but recent research shows adaptive-like traits — memory of specific infections, more vigorous response on re-exposure.

**CDSFL:** Three functions:
1. **Deduplication** — compares new findings against all prior findings using a similarity function
2. **Known false-positive matching** — maintains a database from prior runs. Seeded from Run 7b: Codex hallucinated missing `@dataclass` decorators 8 times (7% of output); severity scores inflated above 0.95 after round 5
3. **Anomaly detection** — flags statistical outliers in the finding stream

Memory persists across runs. Patterns from Run 8 → available in Run 9 → available in Bench Run 2.

### Stage 3a: Helper T-Cell (Synthesis)

**Biology:** Conductors of immunity. Detect pathogens, instruct other cells. Do not kill directly — coordinate.

**CDSFL:** Synthesises all verdicts into a single judgment per finding using confidence-weighted voting.

**Asymmetric thresholds:**
- Rejection requires **0.6+** net confidence
- Confirmation requires only **0.4+**

Rationale: false negatives (suppressing a real bug) are worse than false positives (letting a questionable finding through for another round).

### Stage 3b: Regulatory T-Cell (Autoimmune Prevention)

**Biology:** Shut down the immune response once threats are neutralised. Without them → autoimmune disease (immune system destroys the body it protects).

**CDSFL:** Monitors the pipeline itself:
1. Overall rejection rate > 50% → **autoimmune flag**
2. All findings from one model rejected → **systematic bias flag**
3. When flagged: **all findings pass through regardless** — the pipeline cannot destroy its own input

---

## Structural Enforcement Principle

All six agents are constrained by code, not by instructions:

| Agent | Constraint Mechanism |
|-------|---------------------|
| Dendritic Cell | Classification patterns (regex) |
| Cytotoxic T-Cell | JSON schema + mechanical file verification |
| B-Cell | Tool selection by claim type + subprocess execution |
| NK Cell | Similarity function + false-positive database |
| Helper T-Cell | Voting arithmetic + threshold constants |
| Regulatory T-Cell | Rate checks + threshold constants |

No agent operates on trust. Every agent operates on structure.

---

## Run 8 → Run 9 Transition

**Run 8 (current, observation mode):**
- Immune pipeline runs but does not filter — all findings pass through
- CT agent disabled (expensive, not needed for observation)
- Produces dataset: "what would the pipeline have done?"

**Run 9 (pending validation):**
```python
immune_result = run_immune_pipeline(
    findings, prior_findings, source_paths,
    observation_only=False,   # was True in Run 8
    ct_enabled=True,          # was False in Run 8
)
```
- Full six-cell pipeline becomes load-bearing
- Findings failing verification are removed from context

**Validation criterion:** Run 8 pipeline observations must match manual Run 7b analysis (correctly identify the same churn and false positives found by hand).

---

## Expected Impact

- **Churn reduction:** If pipeline identifies even half of the 76% churn from Run 7b, context per round shrinks dramatically
- **Quality improvement:** Models see only verified findings → produce fewer, better responses
- **Faster convergence:** Fewer rounds needed → shorter total run time
- **Overhead:** 35–65 seconds per round (12–31% of Run 7b's 52 minutes)

---

## Scaling and Future

- **Hardware scaling:** Six agents on M1/8GB. Same cell types can be multiplied on larger hardware (biological clonal expansion)
- **Domain scaling:** B-Cell class-switches to domain tools for Bench Run 2 (pint for physics, astropy for astronomy, shapely for geometry, chempy for chemistry, biopython for biology)
- **Learning:** NK Cell memory grows across runs. Patterns expensive to identify early become cheap to detect later. The system's verification capability ratchets forward.

---

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `bench/immune_agents.py` | ~1090 | Full six-cell pipeline with Level 3 enforcement |
| `bench/ct_verdict_schema.json` | 55 | Schema forcing structured CT evidence |
| `bench/verification_utils.py` | — | z3/statsmodels integration + Python 3.13 discovery |
| `bench/run_baseline_confer.py` | — | Immune pipeline wired after quality gate |
| `bench/tests/test_immune_agents.py` | 38 tests | All cell types, pipeline modes, autoimmune override |
