# CDSFL Experimental Results

**Status:** Active — results recorded as experiments complete.

This document is the canonical record of all empirical testing of the CDSFL methodology. Each experiment is recorded with full methodology, raw data references, and findings — including null results and failures. Nothing is omitted.

---

## Prior Experiments (pre-formal recording)

The following experiments were conducted before this results document was established. Summaries are reconstructed from commit history, MEMORY.md, and session records. Raw data for these experiments exists in `bench/results/` but was not formally written up at the time.

### Experiment 0: Four-Condition Self-Test

**Date:** March 2026 (pre-2026-03-18)
**Model:** Claude Code (Opus 4.6)
**Task set:** Seeded-fault benchmark (code review)

Four conditions tested:
1. **Control** — no methodology
2. **CDSFL only** — full framework, no domain expertise
3. **HIL only** — domain expertise, no framework
4. **CDSFL + HIL** — full framework with domain expertise

**Key finding:** All single-invocation conditions capped at approximately the same recall rate regardless of methodology. Iterative multi-pass review with expert direction achieved complete coverage. Implication: there exists a complexity threshold below which methodology formalisation adds no measurable detection value. Iteration, not single-pass structure, is load-bearing.

**Raw data:** `bench/results/` (pre-Phase 2 files)

### Experiment 1: Three-Architecture Adversarial Review

**Date:** 2026-03-18
**Models:** Claude Code (Opus 4.6), Codex (5.3), Gemini
**Scope:** Full codebase + methodology review

CC/CX conducted 8 rounds of adversarial review. Gemini was then applied independently:
- CC/CX found ~24 issues across 8 rounds and converged
- Gemini found 16 novel issues that all 8 CC/CX rounds missed
- Gemini Extended P-Pass (5 modules) found additional issues

**Key finding:** Heterogeneous architectures find defects that homogeneous review misses — validates the biodiversity hypothesis. Convergence curves were different. Failure modes were different. Epistemic diversity is not redundancy; it is additional compute.

**Commits:** `afcc323` (main review), see MEMORY.md for full commit trail
**Raw data:** `~/Desktop/Accessibility/CE_Gemini_EPP_Module{1-5}_2026-03-18.txt`

---

## Formal Experiments

### Experiment 2: Gemini 3.1 Pro Diagnostic Run

**Date:** 2026-03-20
**Model:** gemini-3.1-pro-preview (Google, Paid Tier 1 API)
**Orchestrator/Assessor:** Claude Code (Opus 4.6), acting as Tier 2 domain expert
**Purpose:** Validate infrastructure, establish calling patterns, generate pilot dataset before full 25-task frontier run
**SDK:** google-genai 1.67.0 (migrated from deprecated google-generativeai)

#### Design

Three frontier tasks spanning different domains:
- ft-001: mathematics/proof (Erdős–Szekeres theorem) — expected 40–50% single-pass
- ft-006: software/code (Interval Scheduling with Weighted Dependencies) — expected 20–30% single-pass
- ft-013: cross-domain/design (Solar-Powered Water Purification System) — expected 20–30% single-pass

Three conditions per task:
1. **Control** — raw prompt, no system instruction. 1 run.
2. **Prompt Engineering (PE)** — competent human-level prompting ("think carefully, show reasoning, double-check"). Not CDSFL. Not leading the model. 5 runs per task (to measure variance).
3. **CDSFL** — full framework: HARD/SOFT constraint classification, P-Pass self-falsification, epistemic marking, structured output. 1 run (further passes on assessor judgment).

#### Infrastructure

- All calls made via Google GenAI SDK (`google.genai`), not deprecated `google.generativeai`
- `max_output_tokens`: 16384
- HTTP timeout: 300s (5 min)
- Inter-call spacing: 3s (rate limit buffer)
- No model fallback — Gemini 3.1 Pro or failure recorded
- Error protocol: diagnose, adapt prompt, retry up to 5 cycles, then stop and report

#### Results: ft-001 (Erdős–Szekeres Theorem)

Nine binary scoring criteria derived from ground truth (labelling definition, uniqueness proof, pigeonhole bounds, monotonicity bridge, correct 16-element construction, proofs of no length-5 subsequences, length-4 exhibition, no wrong-length error).

| Condition | Run | Score | Pct | Latency | Response |
|-----------|-----|-------|-----|---------|----------|
| Control | 1 | 8/9 | 89% | 62.4s | 6,342 ch |
| PE | 1 | 9/9 | 100% | 68.8s | 6,135 ch |
| PE | 2 | 7/9 | 78% | 42.9s | 6,015 ch |
| PE | 3 | 8/9 | 89% | 49.5s | 5,850 ch |
| PE | 4 | 6/9 | 67% | 57.9s | 6,142 ch |
| PE | 5 | 8/9 | 89% | 50.5s | 6,066 ch |
| CDSFL (initial) | 1 | 9/9 | 100% | — | — |
| CDSFL (revised) | 1 | 9/9 | 100% | 101.8s | 11,414 ch |

**Condition averages:**

| Condition | Mean | Range | Latency | Size |
|-----------|------|-------|---------|------|
| Control | 89% | 89–89% (n=1) | 62.4s | 6,342 ch |
| PE | 84.4% | 67–100% (n=5) | 53.9s | 6,042 ch |
| CDSFL | 100% | 100–100% (n=1) | 101.8s | 11,414 ch |

**CDSFL self-falsification quality:** Gemini identified 3 genuine tightening points in its own initial answer: (1) implicit pigeonhole in Part 2 proof, (2) verification by enumeration rather than mathematical demonstration, (3) monotonicity/distinctness bridge unstated. All three are legitimate. Revised answer addressed all three.

**PE variance:** 33-percentage-point spread across 5 identical PE runs (67%–100%). "Think carefully" did not consistently improve output and may have introduced instability relative to the unguided control.

**Infrastructure:** Zero INFRA_FAILs across 7 API calls. Gemini 3.1 Pro is stable when called correctly via the new SDK without subprocess contamination.

**Scoring limitations:** Pattern-based automated scoring produced some false negatives (e.g., uniqueness proof present but using variable names the regex missed). Manual review must supplement automated scoring for subsequent tasks.

**Assessor note:** This task is at the easier end of the frontier set (40–50% expected). The Erdős–Szekeres theorem is well-known and likely in training data. Differential effects between conditions are predicted to be larger on harder, less-trained tasks. The PE variance signal is potentially more informative than the mean scores at this difficulty level.

#### Results: ft-006 (Interval Scheduling — software/code)

*Pending — runs in progress as of 2026-03-20T23:20Z*

#### Results: ft-013 (Solar Water Purification — cross-domain/design)

*Pending — runs in progress as of 2026-03-20T23:20Z*

#### Diagnostic Summary

*To be completed when all three tasks are scored.*

---

## Planned Experiments

### Experiment 3: Full Gemini Frontier Run (25 tasks)

**Status:** Planned — pending diagnostic completion
**Model:** gemini-3.1-pro-preview
**Task set:** Full 25-task frontier set
**Conditions:** Control, PE, CDSFL (as per diagnostic design)
**Orchestrator:** CC via CLI
**Budget:** $20 cap (Google API)

### Experiment 4: Three-Way Round-Robin Convergence Test

**Status:** Planned — pending Experiment 3
**Models:** Claude Code (Opus 4.6), Codex (5.3), Gemini 3.1 Pro
**Design:** All three architectures iterate on each other's output under full CDSFL. CC orchestrates. Sequential execution (M1 8GB constraint). Confer/defer protocol shared across all three. `confer` for agreement, `defer` for irreconcilable disagreement → human review.
**Purpose:** Test biodiversity hypothesis systematically. Does heterogeneous multi-architecture adversarial review under CDSFL find more than any single architecture alone? Measure convergence curves per architecture.
**Stopping criterion:** All architectures agree diminishing returns reached, or 5-round cap.

---

*Raw data for all experiments is stored in `bench/results/`. This document is the interpretive record. For the technical methodology, see the [white paper](../PAPER.md). For the experimental design rationale, see the [experiment plan memory file](../../.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_experiment_plan.md).*
