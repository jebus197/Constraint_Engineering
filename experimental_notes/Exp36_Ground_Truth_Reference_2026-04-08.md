# Experiment 36 — Ground Truth Reference

**Date:** 8 April 2026, 02:42 BST
**Purpose:** Single canonical reference consolidating all findings, observations, fixes, mathematical insights, and forward path from Experiment 36. This document supersedes the seven individual Exp 36 notes as the authoritative source for project planning.

**Source documents consolidated:**
- `Exp36_Results_2026-04-07.md` — raw results and round data
- `Exp36_Session_Findings_2026-04-07.md` — 14 monitoring lessons + founder observations
- `Exp36_Verification_Analysis_2026-04-07.md` — mathematical verification of 7 claims
- `Exp36_Design_Analysis_2026-04-07.md` — CC2v, Bugzilla model, immune, schema analysis
- `Exp36_Burst_Reasoning_Analysis_2026-04-07.md` — R8 burst phenomenon
- `Exp36_Live_Analysis_CDSFL_as_Bench_2026-04-07.md` — meta-analysis
- `Exp36_Mathematical_Model_Audit_2026-04-07.md` — 5 gap audit scope

---

## I. Test Article: evidence.py

### What It Is

`bench/evidence.py` (590 lines) is the **semantic query layer** — Layer 3 in the CDSFL architecture. It sits between the cryptographic VerificationChain (Layer 2, tamper-evident append-only log) and any consumer (UX, CLI, external auditor, model reviewer).

Its purpose: make the chain queryable without exposing cryptographic internals.

### Role in the CDSFL Schema

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| 1 | PolicyEngine | Rules, directive composition, constraint classification |
| 2 | VerificationChain | Append-only hash chain, Merkle epoch sealing, RFC 9162 proofs |
| **3** | **EvidenceStore (evidence.py)** | **Entity-indexed queries, provenance traces, evidence bundles** |
| 4 | UX / Export | Human-readable audit, external verification |

The evidence layer was **never reviewed by models prior to Experiment 36**. This was its first exposure to the model panel.

### Key Components (590 lines)

| Component | Lines | Purpose |
|-----------|-------|---------|
| `EvidenceRecord` | 64-112 | Wraps a chain record with typed access, extracts finding IDs via `\bC\d{4}\b` regex |
| `ProvenanceEvent` | 116-124 | One event in a finding's lifecycle (submitted, confirmed, challenged, etc.) |
| `EvidenceBundle` | 128-158 | Self-contained exportable proof package for external audit |
| `StoreSummary` | 161-170 | Summary statistics for reporting |
| `_EvidenceIndex` | 198-256 | In-memory multi-field index (by experiment, model, round, type, finding_id) |
| `EvidenceStore` | 263-524 | Main semantic query interface — read-only, wraps VerificationChain |

### Central Design Invariant

The evidence layer is **read-only**. It never modifies the chain. It builds an immutable in-memory index on load, queries that index, and delegates proof generation to the VerificationChain. The chain remains the sole source of truth.

### Dependencies

- Imports from `bench.verification_chain` only (VerificationChain, Verifier, rfc9162_merkle_root)
- No dependency on runner, immune pipeline, endocrine, insect brain, or PolicyEngine
- Pure query layer — orthogonal to runner logic

### Design Gaps Identified by Model Panel

1. Finding ID extraction is regex-based (`\bC\d{4}\b`) — should be structured metadata
2. Event classification is heuristic (infers from artifact_type and payload content) — should be stored explicitly
3. No cross-reference to live registry state (EvidenceStore reads chain only)
4. `from_chain_record()` has a dict-only payload guard that skips string payloads containing finding IDs
5. `export_bundle()` missing experiment filter — could leak cross-experiment records
6. Hash-only records cause finding ID extraction to be silently skipped
7. No payload schema validation
8. No cache invalidation or staleness detection
9. Limited queryability (5 indexed fields, no timestamp range or custom metadata queries)
10. Evidence bundles lack signing key metadata or expiry

### Assessment

evidence.py is architecturally clean, well-tested (495-line test file, 11 test classes), and production-ready for its stated purpose. The findings are **architectural enhancements**, not functional bugs. The code works correctly for what it does — the gaps are about what it doesn't do yet.

**This is the first time the evidence layer has been activated in the CDSFL schema.** It should continue to be the test article for a resumed Exp 36 and can serve as the basis for understanding how the evidence/query layer integrates with the rest of the system.

---

## II. Experiment Results

### Summary Statistics

| Metric | Value |
|--------|-------|
| Target | `bench/evidence.py` (590 lines) |
| Topology | Star (5 models, central coordinator) |
| Rounds | 23 (R0-R22: 20 base + 3 extension) |
| Runtime | 224 minutes (~3h 44m) |
| Termination | EXTENSION_STALLED / INCOMPLETE |
| Total raw findings | 452 |
| Registry canonical entries | 153 |
| Overall novelty rate | 33.8% (153/452) |
| Final gamma | 0.411 |
| Dedup ratio | 17:1 (raw to estimated unique bugs) |
| Estimated actual bugs | ~9 |
| CC2v total verdicts | 50 (25 confirmed, 6 rejected, 11 merged, 8 escalated) |
| HIL flags | 51 (ITC intervention warnings) |
| Contested at termination | 2 |

### Per-Model Raw Finding Counts

| Model | Raw | % of Total |
|-------|-----|-----------|
| DeepSeek | 119 | 26.3% |
| ChatGPT | 107 | 23.7% |
| Codex | 92 | 20.4% |
| Gemini | 92 | 20.4% |
| CC2 | 42 | 9.3% |

CC2's low count (9.3%) is explained by its dual role as both discovery model and CC2v verification agent. Agents 1-3 were not implemented — CC2 operated as a general-purpose model rather than specialised agents.

### Gamma Trajectory

| Round | Gamma | Gate | Key Event |
|-------|-------|------|-----------|
| R0-R1 | 0.000 | telemetry | Bootstrap (MIN_ROUNDS_FOR_GAMMA=3) |
| R2 | 0.626 | telemetry | First gamma computation |
| **R4** | **0.675** | telemetry | **Peak gamma** |
| R5-R7 | 0.671-0.643 | telemetry | Post-peak plateau |
| **R8** | **0.594** | telemetry | **Burst reasoning** (21 novel, z=3.63) |
| R9-R14 | 0.556-0.453 | telemetry | Steady decline |
| **R15** | **0.440** | **soft** | Soft gate threshold crossed |
| R16-R19 | 0.431-0.416 | soft | Gradual decline |
| **R20** | **0.414** | **hard** | Hard gate activated |
| R21-R22 | 0.412-0.411 | hard | Static — gamma effectively stalled |

**Two-phase structure confirmed mathematically:** Phase 1 slope = +0.025/round (rising), Phase 2 slope = -0.013/round (declining). R² = 0.985 for early exponential decay of novelty.

### Convergence Gate — 5 Conditions at Termination

| # | Condition | Requirement | Final State | Met? |
|---|-----------|-------------|-------------|------|
| 1 | Earliest round | >= R12 | R22 | YES |
| 2 | Contested | <= 1 | 2 | **NO** |
| 3 | Recent novel | <= 2 per round (2 consecutive) | [6, 2] (R21 spike) | **NO** |
| 4 | Gamma | < 0.35 (hard) | 0.411 | **NO** |
| 5 | Gamma gate passed | gate tier accepted | hard gate passed | YES |

**Convergence was closest at R18:** novel=2, all conditions met except contested=1. One contested finding blocked the entire gate. By R22, the system had moved *away* from convergence (contested rose to 2, R21 had a 6-novel spike from burst reasoning).

**Without contested-to-HIL escalation, convergence was mathematically unreachable.** The contested findings could not be resolved autonomously. No number of additional rounds would have changed this.

### CC2v Verification (Rounds 20-22 Detail)

| Round | Batch | Confirmed | Rejected | Duplicates | Resolution |
|-------|-------|-----------|----------|------------|------------|
| R20 | 3 | 1 | 1 | 1 | 100% |
| R21 | 6 | 3 | 0 | 3 | 100% |
| R22 | 2 | 1 | 1 | 0 | 100% |
| **Total session** | **50** | **25** | **6** | **11** | **100%** |

CC2v also escalated 8 findings to HIL review and merged 11 duplicates across the full experiment. Verification accuracy improved over time — early batches had high rejection (4/6 at activation), late batches favoured confirmation (pattern: cumulative context helps verification but hurts discovery).

### Fix Generation and Application

| Rounds | Fixes Evaluated | UNEVALUABLE | APPLICABLE | APPLIED |
|--------|-----------------|-------------|-----------|---------|
| R18-R22 | 39 | 39 | 0 | 0 |
| **All rounds** | **~150+** | **~150+** | **0** | **0** |

**100% of proposed fixes were marked UNEVALUABLE.** Root cause: models propose fixes in natural language or pseudo-code, not as directly applicable patches. The fix verification agent (Stage 4 of immune pipeline) needs AST-level patch parsing to evaluate them. This is the central bottleneck preventing findings from reaching CLOSED status.

### Immune Pipeline (Last 5 Rounds)

| Round | Input | Survivors | Rejection Rate | Autoimmune |
|-------|-------|-----------|----------------|------------|
| R18 | 9 | 7 | 22.2% | No |
| R19 | 12 | 11 | 8.3% | No |
| R20 | 16 | 10 | 37.5% | No |
| R21 | 21 | 13 | 28.6% | No |
| R22 | 8 | 6 | 25.0% | No |

Autoimmune flag never triggered across 23 rounds. Rejection rates were moderate (8-38%), indicating the pipeline was filtering but not over-filtering.

### Context Degradation

| Metric | Value |
|--------|-------|
| Context at R22 | 811,213 characters |
| Context budget | 200,000 characters |
| Overshoot | **406%** |
| Endocrine signal | `degrade_relay` (suggested, not actioned) |
| DeepSeek response time at R22 | 124.9s (3.2x median) |
| Gemini response time at R22 | 216.1s (5.6x median) |

Context grew monotonically across 23 rounds. By R20+, every model was receiving summary-only relay (budget enforcement worked mechanically, but the summary itself was still too large). Both DeepSeek and Gemini exceeded their timeout thresholds. The endocrine layer correctly suggested `degrade_relay` but the action was either not implemented or ineffective.

### ITC Interventions

During live monitoring, extensive ITC activity was observed:
- All 5 models flagged DEGRADATION after R1 (aggressive early threshold)
- ChatGPT: 11+ consecutive interventions by R14
- Gemini: 9 consecutive interventions
- Codex: 7, DeepSeek: 3+
- 51 total HIL flags generated across the experiment
- ITC never reached a "healthy" state for any model — continuous management throughout

The ITC's DEGRADATION threshold conflates two distinct problems: (a) model quality degradation (should reduce workload) and (b) discovery space depletion (should transition to consolidation). This conflation drives the ITC-convergence feedback loop.

---

## III. Root Cause Analysis — Four Structural Problems

### Problem 1: ITC-Convergence Feedback Loop (CRITICAL)

The ITC and convergence gate are in structural tension:
1. ITC detects degradation → restarts model with fresh context
2. Fresh model produces novel findings (burst reasoning)
3. Novel stays above threshold (<=2) → convergence gate fails
4. ITC keeps cycling → fresh models keep finding → novelty stays up

This is a self-reinforcing loop. The system optimises for discovery when it should transition to consolidation. The only exit was budget exhaustion at R20 (extended to R23).

**Fix required:** Gamma-aware ITC threshold. When gamma indicates depletion (declining for N rounds), ITC should transition from `restart_fresh` to `change_focus` or `consolidate` mode.

### Problem 2: CONFIRMED =/= CLOSED (CRITICAL)

CONFIRMED findings remain in the ACTIVE pool. Models see them in full detail and can still challenge them. Only CLOSED findings are challenge-resistant, and CLOSED requires a programmatically verified fix.

Exp 36 is a code *review*, not a code *remediation*. The runner doesn't extract, apply, or verify fixes. Findings can never reach CLOSED. They get CONFIRMED, stay in the ACTIVE pool, and models keep engaging with them.

**This directly explains:**
- The 17:1 dedup ratio (findings cycle through CONFIRMED but never CLOSE)
- CC2v single-bug-family dominance (export_bundle confirmed 12+ times)
- The ITC-convergence feedback loop (models keep producing output about CONFIRMED findings)

**Fix required:** Fix-application pipeline. Extract proposed fix → sandbox → Stage 4 verification (pyright/ruff/bandit + tests) → CLOSED on success.

### Problem 3: Contested Findings Block Convergence Indefinitely (HIGH)

The convergence gate requires contested <= 1. Contested findings that models cannot resolve autonomously block termination forever. In Exp 36, one finding was contested from approximately R12-R22 — ten rounds without resolution.

**Fix required:** Contested-to-HIL escalation. After N rounds (suggested: 5) of unresolved contested status, escalate to human review and remove from convergence gate calculation.

### Problem 4: Context Inflation (HIGH)

Context grew to 406% of budget by R22. The endocrine layer detected this and suggested `degrade_relay`, but the action wasn't effective. Models received increasingly toxic context (cumulative findings, verdict history, registry state) that degraded their ability to produce novel, well-targeted findings.

**Fix required:** Context windowing. Limit relay to last N rounds of findings, with CLOSED findings appearing only in compact resolved summary. Hard cap on total characters, enforced by the relay mechanism.

---

## IV. Immune Pipeline Status — Corrections

### IMPORTANT CORRECTION

The Design Analysis (7 April) stated that the skin barrier was "currently observation-only" and that v2 components were "running in shadow." **This was incorrect.**

Investigation of the actual code confirms:

| Component | Actual Status in Exp 36 | Previously Stated |
|-----------|------------------------|-------------------|
| DC v2 | **PRIMARY** | Shadow |
| NK v2 | **PRIMARY** (tau_sim=0.50, intra-round dedup) | Shadow |
| Helper T v2 | **PRIMARY** (two-level aggregation) | Parallel |
| Regulatory T v2 | **PRIMARY** (fixed math) | Shadow |
| CT v2 | Parallel with v1 (both contribute verdicts) | Shadow |
| B-Cell v2 | Parallel with v1 (AST-grounded z3) | Shadow |
| Skin Barrier | **ACTIVE filtering** (observation_only=False) | Observation-only |
| LLM Classifier (WP3c) | Shadow only (logs, no verdict modification) | Not active |
| Formalisation Agent (WP3d) | Shadow only (logs, no verdict modification) | Not active |

**The v2 immune pipeline was already running as primary in Exp 36.** DC, NK, Helper T, and Regulatory T v2 were all primary. CT and B-Cell v2 ran in parallel with v1, both contributing verdicts. The skin barrier was actively filtering findings (not observation-only).

The only components still in true shadow mode are the LLM Classifier (WP3c) and the Formalisation Agent (WP3d). Both log comparison data but do not modify verdicts.

### What This Means for Resumption

Activating v2 immune is **not an outstanding task** — it is already done. The question for resumption is whether to:
1. Promote LLM Classifier from shadow to primary (addresses 21-44% regex misclassification)
2. Promote Formalisation Agent from shadow to primary (feeds B-Cell AST context)
3. Both have low risk — they've been running in shadow and logging data

### DC v1 vs LLM Classifier Agreement (Shadow Data)

| Round | Agreement Rate |
|-------|---------------|
| R13 | 41% |
| R14 | 21% |
| R22 | 44% |

The regex classifier systematically over-classifies findings as "mathematical" when they are actually code_behavioral or code_structural. Promoting the LLM classifier would correct this routing error.

---

## V. The 13 Design Improvements — Status

| # | Improvement | Priority | Status | Source |
|---|-------------|----------|--------|--------|
| **1** | **Contested-to-HIL escalation (5-round threshold)** | HIGH | **NOT IMPLEMENTED** | Session |
| **2** | **Discovery efficiency metric (rho = novel/raw)** | HIGH | Tracked, not gated | Session |
| **3** | **Consolidation phase (final 3 rounds: change_focus only)** | HIGH | **NOT IMPLEMENTED** | Session |
| 4 | Decay-rate convergence (rolling 3-round average) | Medium | **NOT IMPLEMENTED** | Session |
| 5 | Meta-cognitive decay feedback (inject rho, gamma from R5+) | Medium | **NOT IMPLEMENTED** | Session |
| 6 | v2 shadow activation (all cells) | HIGH | **ALREADY DONE** (see Section IV) | Session |
| 7 | Classifier/timeout fixes | Medium | Partial (timeout noted) | Session |
| **8** | **Per-model rho tracking with targeted ITC** | HIGH | **NOT IMPLEMENTED** | Deep analysis |
| **9** | **Gamma-aware ITC DEGRADATION threshold** | HIGH | **NOT IMPLEMENTED** | Deep analysis |
| 10 | Dynamic stall detector terminate threshold | Medium | **NOT IMPLEMENTED** | Deep analysis |
| **11** | **Pre-filter findings before CC2v queue** | HIGH | **NOT IMPLEMENTED** | Deep analysis |
| **12** | **Dedup-aware CC2v (check prior confirmations)** | HIGH | **NOT IMPLEMENTED** | Deep analysis |
| **13** | **Context windowing for long runs** | HIGH | **NOT IMPLEMENTED** | Deep analysis |

### Already Implemented (Beyond the 13)

- Finding registry with canonical state and Bugzilla FSM
- CC2v between-round verification (Agent 4, operational since Exp 35)
- Verdict parsing and status FSM (OPEN/CONFIRMED/CONTESTED/CLOSED/MERGED)
- Directed messaging protocol (relay mode with @tags)
- Persistent signed fingerprints (FP dir + Merkle sealing)
- Endocrine pacing signals
- ITC adaptive recovery (6-level escalation)
- Full v2 immune pipeline (primary for DC, NK, Helper T, Reg T)
- Skin barrier active filtering
- Evidence layer (the test article itself)

### Minimum Viable Fixes for Resumption

Three fixes are required to unblock convergence in a resumed Exp 36:

1. **Contested-to-HIL escalation** (#1) — the 2 contested findings would escalate immediately (>10 rounds unresolved)
2. **Gamma-aware ITC threshold** (#9) — stops the ITC-convergence feedback loop
3. **Dedup-aware CC2v** (#12) — stops re-confirming known findings

With these three fixes, estimated 3-5 additional rounds to convergence.

---

## VI. Mathematical Model Gaps

Five structural gaps between `docs/MATHEMATICAL_APPENDIX.md` and experimental reality (scoped 7 April, execution pending):

| # | Gap | Impact |
|---|-----|--------|
| 1 | **Gamma misclassifies system-level churn** — gamma=0.411 says "converging" while system churns 17:1. Gamma only sees novel rate, not raw-to-novel divergence. | Convergence gate makes decisions on incomplete information |
| 2 | **rho (novel/raw) not formalised** — invented during Exp 36 analysis, fills genuine gap, but not in appendix | Cannot be rigorously tested or related to existing framework |
| 3 | **ITC feedback loop not modelled** — restart_fresh re-injection is not error re-injection (nu). Per-model, time-varying, produces rediscoveries not new defects. | Mathematical model predicts different behaviour from what actually happens |
| 4 | **f_del and phi_fmt are constants but degrade with context** — context grew to 406%. Parameters are functions of context size, not fixed. | Model underestimates degradation in long runs |
| 5 | **Runner gate does not equal appendix termination** — V-hat + ascending abstraction (appendix) vs 5-condition state gate (runners). 3/5 runner conditions non-contributing. | Theory and practice are not reconciled |

**Constraint:** No appendix modifications without founder's explicit approval. Findings first, formalisation second.

---

## VII. Findings to Fold into CDSFL Schema

### Already in Schema (Directives/Constraints)

- Anti-deference enforcement (Layer 1, HARD)
- Falsification required (Layer 1, HARD)
- Non-compensatory convergence (Layer 1, HARD)
- Per-domain verification rules (Layer 2)
- JSON schema payload requirements (Layer 1, HARD)
- SymPy auto-verify (Layer 1, HARD)

### Should Be Promoted to Schema

From Exp 36, two findings are clear candidates for schema promotion:

1. **Contested escalation threshold** — should be `convergence.contested_escalation_rounds: 5` in schema. This is a convergence parameter, not an operational detail.
2. **Discovery efficiency metric (rho)** — should be `convergence.churn_threshold` in schema. Without it, the gate cannot distinguish genuine convergence from masked churn.

### Should Remain Runner-Level (Operational Logic)

- ITC strategies (restart_fresh, change_focus, consolidation)
- Gamma-aware ITC threshold
- Context windowing parameters
- CC2v queue pre-filtering
- Dedup-aware CC2v logic
- Fix-application pipeline mechanics
- Per-model rho tracking
- Dynamic stall detector threshold

These are operational parameters that vary per experiment, not protocol-level constraints.

---

## VIII. Forward Path

### Immediate: Resume Exp 36 (Validation Run)

**Purpose:** Test whether the 3 minimum fixes unblock convergence on a known baseline.

**Prerequisites:**
1. Implement contested-to-HIL escalation (5-round threshold)
2. Implement gamma-aware ITC DEGRADATION threshold
3. Implement dedup-aware CC2v (check prior confirmations before re-verifying)

**Execution:**
- Resume from R22 checkpoint (452 raw, 153 canonical, full registry state)
- 2 contested findings escalate to HIL immediately (>10 rounds unresolved) — founder resolves
- ITC stops restart_fresh cycling (gamma indicates depletion)
- Expected 3-5 additional rounds to convergence

**Scientific value:** Controlled comparison — same test article, same data, different design. Isolates the impact of the fixes.

### Next: Reference Runner for Exp 37+

A reference runner should be built as the canonical entry point for future experiments. This runner:
- Incorporates all 13 design improvements (or as many as are implemented)
- Is parameterised (test article, topology, round limits, convergence thresholds)
- Serves as the executable that a future UX layer calls
- Replaces the per-experiment runner scripts (run_exp35, run_exp36, etc.)

This is distinct from the automation scripts (sv, qc, recover, onboard). Those manage project state. The reference runner manages experiment execution.

### Then: Fresh Exp 37

**Purpose:** Full experiment with all improvements on a new test article.

**Likely improvements beyond the 3 minimum:**
- Fix-application pipeline (CONFIRMED + verified fix → CLOSED)
- Context windowing
- Per-model rho tracking with targeted ITC
- Pre-filter before CC2v queue
- LLM classifier promoted from shadow to primary
- Consolidation phase (final 3 rounds)
- Meta-cognitive decay feedback (inject rho, gamma into prompts from R5+)
- CC2 Agents 1-3 (structural, semantic, integration)

**Test article:** To be determined. Candidates include other components that have not been reviewed: `endocrine.py`, `insect_brain.py`, `runner_core.py`, or `immune_agents.py` itself.

---

## IX. Confirmation of Plan

The plan as understood from the previous session is confirmed:

1. **Resume Exp 36 with the 3 minimum fixes** — validate that contested-to-HIL, gamma-aware ITC, and dedup-aware CC2v unblock convergence. Expect 3-5 rounds.
2. **Build a reference runner** — parameterised, incorporating all improvements, serves as the executable entry point for future experiments and eventually the UX layer.
3. **Run a fresh Exp 37** — full experiment with all improvements on a new test article, using the reference runner.

The evidence layer (evidence.py) should continue as the test article for the resumed Exp 36. This is its first activation in the schema, and the model panel has already built substantial context about it. Changing the test article mid-experiment would invalidate the controlled comparison.

---

## X. Cross-References

### Existing Exp 36 Notes (Retained, This Document Supersedes for Planning)

| File | Content | Status |
|------|---------|--------|
| `Exp36_Results_2026-04-07.md` | Raw results, round data | Retained as data source |
| `Exp36_Session_Findings_2026-04-07.md` | 14 monitoring lessons, founder observations | Retained as primary record |
| `Exp36_Verification_Analysis_2026-04-07.md` | Mathematical verification of 7 claims | Retained as verification record |
| `Exp36_Design_Analysis_2026-04-07.md` | CC2v, Bugzilla, immune, schema analysis | Retained, **immune status corrected here** |
| `Exp36_Burst_Reasoning_Analysis_2026-04-07.md` | R8 burst phenomenon | Retained as analysis |
| `Exp36_Live_Analysis_CDSFL_as_Bench_2026-04-07.md` | Meta-analysis | Retained |
| `Exp36_Mathematical_Model_Audit_2026-04-07.md` | 5 gap audit scope | Retained, execution pending |

### Key Correction Log

| What | Was | Is | Evidence |
|------|-----|----|----------|
| Skin barrier | "observation-only" | **Active filtering** (observation_only=False) | Default parameter in run_immune_pipeline() |
| v2 immune | "running in shadow" | **PRIMARY** for DC, NK, Helper T, Reg T | Hardcoded active in pipeline as of Exp 29 |
| evidence.py line count | "~420 lines" | **590 lines** | Direct file read |
| LLM classifier | "not yet active" | **Shadow** (logs only, no verdict modification) | Code confirms shadow execution when CLI available |
| Formalisation agent | "not yet active" | **Shadow** (precondition extraction, no verdict modification) | Code confirms shadow execution in WP3d block |
