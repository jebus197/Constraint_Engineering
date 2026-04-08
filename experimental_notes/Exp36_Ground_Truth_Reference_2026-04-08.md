# Experiment 36 — Ground Truth Reference

**Date:** 8 April 2026, 02:42 BST (updated 07:00 BST)
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
| **R8** | **0.594** | telemetry | **Burst reasoning** (21 novel, z=5.24 per R1-R7 baseline) |
| R9-R14 | 0.556-0.453 | telemetry | Steady decline |
| **R15** | **0.440** | **soft** | Soft gate threshold crossed |
| R16-R19 | 0.431-0.416 | soft | Gradual decline |
| **R20** | **0.414** | **hard** | Hard gate activated |
| R21-R22 | 0.412-0.411 | hard | Static — gamma effectively stalled |

**Two-phase structure confirmed mathematically:** Phase 1 slope = +0.025/round (rising), Phase 2 slope = -0.013/round (declining). R² = 0.961 for R1-R4 early exponential decay of novelty (computed 8 April audit; prior R² = 0.985 claim could not be reproduced — see `Mathematical_Model_Audit_2026-04-08.md`).

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

## IV. Convergence Was Reached — Instrumentation Failed to Detect It

### The Observation

The discovery space was exhausted by approximately R15. The model panel had found ~9 actual bugs in a 590-line file. From R15-R22, the 17:1 dedup ratio means models were rediscovering the same bugs, reformulating them, and re-submitting. Novel findings were mostly <=2 per round (the R21 spike of 6 was caused by an ITC restart_fresh injecting a fresh model into a depleted space).

The CDSFL methodology worked. The five-model panel found the bugs, the immune pipeline classified them, CC2v verified them. The failure was purely in the measurement layer — the convergence gate's 5 conditions weren't calibrated for what "done" actually looks like.

### The Gamma/Rho Divergence

Two signals diverged and nothing in the instrumentation detected it:

**Gamma (novelty-derived):** Declining steadily. 0.675 at R4 to 0.411 at R22. The decay curve of novel findings was exponential early (R² = 0.961 for R1-R4, computed 8 April audit) then flattened to a low but non-zero residual rate.

**Raw output:** Stable. Not rising, but not declining. Findings per round averaged ~20 with no downward trend. Models kept producing at roughly the same rate throughout.

The gap between these two is the churn. 452 raw findings, 153 novel. 299 findings (66% of all output) were rediscoveries of known bugs in slightly different words. By the late rounds, rho (novel/raw) was running at 8-25%, meaning 75-92% of operational output was waste.

Gamma only sees the novel count. It does not know how much raw output was produced to generate those novel findings. A round with 33 raw and 5 novel looks identical to gamma as a round with 5 raw and 5 novel. The first is churning. The second is efficient. Gamma cannot distinguish them.

### Three Instrumentation Failures

1. **Contested findings not escalated** — two findings the models couldn't resolve autonomously held the gate open. These needed a human, not more rounds.
2. **ITC restart_fresh inflated novelty** — fresh models re-entered a depleted space and produced "novel" reformulations of known bugs. This kept the novel count above the <=2 threshold.
3. **Gamma couldn't see the churn** — gamma=0.411 looks like "moderate depletion" but the raw-to-novel ratio (17:1) shows the system was effectively saturated.

### The Coupled Cascade

The five mathematical model gaps (see Section VII below) form one coupled failure chain:

- **Gap 4 starts the chain.** Context grows. Models degrade.
- **Gap 3 amplifies.** ITC restarts models. Fresh models rediscover known bugs. Registry grows. Context grows further.
- **Gap 1 hides the problem.** Gamma reports convergence. It cannot see the churn.
- **Gap 2 means nobody has a metric to see it.** Rho would reveal the divergence immediately. But rho does not exist in the formal framework.
- **Gap 5 means the system cannot terminate.**

### Resolution

Formalise rho, add it to the convergence gate, and use gamma AND rho jointly for system-level classification. The mathematical model audit (Section VII) validates this computationally. Then formalisation follows. Then code. No appendix changes without founder approval.

---

## V. Immune Pipeline Status — Corrections

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

## VI. The 13 Design Improvements — Status

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

## VII. Mathematical Model Gaps

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

## VIII. Findings to Fold into CDSFL Schema

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

## IX. CC2 Sub-Agent Design — Closed Constraint Space

### Architecture

The CDSFL experiment architecture has two distinct layers:

- **5-model discovery panel** (DeepSeek, ChatGPT, Codex, Gemini, CC2) — the discovery layer. These are models in the panel. They explore the test article freely and produce findings. The cost of that freedom is hallucination, conflation, and churn. The immune pipeline exists to filter the consequences.
- **4 CC2 sub-agents** (Citation Verifier, Fix Extractor, Dedup Assessor, CC2v) — the verification layer. All closed constraint space. All mechanical. All running in parallel. No open-ended exploration. No generative function.

There are no "open-space agents." The previous CC1 instance's error was conflating the sub-agents with a "structural/semantic/integration" discovery specialist design. The discovery is handled by the panel. The sub-agents verify, extract, classify, and deduplicate what the panel produces.

### Design Principle — Closed Constraint Space

Each sub-agent operates in a **closed constraint space**: bounded operational domain, rigid input/output contract, claims mechanically verifiable against the constraint boundaries.

Each agent has:
1. **A single question it answers.** Not "what bugs exist?" but "does this specific finding describe the code at this specific location?"
2. **A rigid output schema.** Structured verdicts with mandatory evidence fields. If the agent can't fill the evidence fields from what it observed, it can't produce the output.
3. **Expert encoding as boundary.** Each agent receives only information relevant to its task — not the full registry, not the full codebase context, not other models' findings. The encoding limits what it can perceive, claim, and hallucinate about.
4. **Mechanical verifiability of outputs.** Every claim is testable against something concrete. "This code exists at line 47" — check the file. "This diff applies cleanly" — apply it.

This prevents **conflation** (the agent cannot see things outside its constraint space) and **hallucination** (the output schema requires mechanically checkable evidence; hallucinations fail validation at the boundary, not downstream).

### The 4 Agents

| Agent | Constraint Question | Output Schema | Capability |
|-------|-------------------|---------------|------------|
| 1 — Citation Verifier | "Does this finding accurately describe the code at the cited location?" | `{verified, cited_code, match_assessment, confidence}` | Haiku-level |
| 2 — Fix Extractor | "Can this natural-language fix be expressed as an applicable code change?" | `{extractable, diff, applies_cleanly, test_result}` | Opus-level (NL→code is hard) |
| 3 — Dedup Assessor | "Does this new finding describe the same bug as an existing one?" | `{duplicate, shared_root_cause, evidence_from_both}` | Haiku-level |
| 4 — CC2v (existing) | "Confirm, reject, duplicate, or escalate?" | Confidence-gated verdict | Opus-level |

All 4 run in **parallel** on each finding. Efficiency is a primary goal — with 4 agents running simultaneously, throughput increases and findings that fail early checks (bad citation, known duplicate) are flagged immediately rather than consuming CC2v slots.

### Implementation Structure

Each agent needs:
- **Directive** — constraint space definition, goes in `bench/directives/`
- **Schema** — output format, goes in agent dispatch code
- **Validator** — Python function checking output against cited evidence; if validation fails, output is discarded (same principle as immune pipeline rejection)

Agent 2 (Fix Extractor) is the highest-leverage addition — it bridges the fix-application gap (100% UNEVALUABLE in Exp 36) and closes the CONFIRMED → CLOSED pathway that drove the 17:1 dedup ratio.

### Relationship to Immune Pipeline

The CC2 sub-agents mirror the immune pipeline's architecture. The skin barrier is a constraint (does this file:line exist?). NK is a constraint (is this semantically distinct?). B-Cell is a constraint (does this mathematical claim hold?). Each immune cell has a narrow expert encoding and a binary output domain. The CC2 sub-agents apply the same pattern to the pre-verification stage.

---

## X. Meta-Cognitive Feedback — Design Decision

### Specification

The mathematical appendix (section 8.1) defines a "Metacognitive Feedback Protocol" with three signals: novelty trajectory, discovery efficiency (rho), and cumulative gamma. A prompt template exists:

> DISCOVERY METRICS: Your panel has discovered [N] new findings in the last 3 rounds (trajectory: [N, N-1, N-2]). Discovery efficiency is [X]% (novel/total this round). Cumulative gamma: [Y]. If your novel contribution is declining, prioritise high-quality verdicts on existing findings over new discoveries.

### Decision

**Meta-cognitive feedback is reserved for Experiment 37.** It will not be introduced in the resumed Exp 36.

Rationale: if introduced simultaneously with the 3 minimum fixes (contested-to-HIL, gamma-aware ITC, dedup-aware CC2v), the effect cannot be isolated. The resumed Exp 36 is a controlled comparison — same test article, same data, different design. Adding meta-cognitive feedback would confound the results.

### Constraints for Exp 37 Implementation

- **Data only, no authority.** The prompt presents metrics. It does not instruct the model to stop, slow down, or declare convergence. The convergence gate retains sole authority.
- **Constrained response space.** The model is told: "Use these metrics to adjust your search strategy. Do not reduce output quality. Do not declare convergence. Focus on OPEN findings you haven't addressed and issue verdicts on existing findings."
- **Gaming risk.** Exp 32 showed models can learn to signal false convergence. Mitigation: the prompt reframes low novelty as a good signal (the space is depleted, time to consolidate), not a failure.

---

## XI. Canonical Execution Plan (revised 8 April 2026, 07:00 BST)

### Completed

| Task | Date | Outcome |
|------|------|---------|
| Mathematical model audit | 8 April 2026, 04:46 BST | 25/25 internal checks pass (SymPy/Wolfram/z3). All 5 gaps confirmed. Report: `Mathematical_Model_Audit_2026-04-08.md` |
| Appendix gap-fill | 8 April 2026, 06:05 BST | 1081→1155 lines. λ_itc, ρ formalisation, f_del(i,t), runner gate reconciliation. Committed: `317b8f1` |
| Disputed numbers corrected | 8 April 2026, 06:05 BST | R²=0.985→0.961 (R1-R4), z=3.63→5.24 (R1-R7 baseline). Qualitative findings unchanged |
| Rho threshold calibrated | 8 April 2026, 06:05 BST | θ_ρ=0.25, 3-round rolling average, from t_earliest. Triggers R16 in Exp 36 (matches ~R15 saturation) |

### Phase A — Exp 36 Resume (validate fixes)

**Goal:** Validate that 5 targeted fixes break the coupled cascade and allow convergence. Resume from R22 checkpoint, expect 3-5 rounds.

| # | Fix | What It Does | Why It's Minimum |
|---|-----|-------------|-----------------|
| A1 | Registry windowing | OPEN/CONTESTED in active view; CLOSED/MERGED compact; REFUTED/DUPLICATE hidden | Breaks churn loop at root — models stop re-engaging with resolved findings |
| A2 | ρ as C6 in convergence gate | θ_ρ=0.25, 3-round rolling, from t_earliest=12 | Detects churn that γ can't see. Formalised in appendix §7.1a |
| A3 | Contested → HIL escalation | 5-round threshold for contested findings | Removes sole convergence blocker at R19 (4/5 conditions met, C2 failed) |
| A4 | Gamma-aware ITC | Check ρ before DEGRADATION dispatch | Prevents blind restarts that feed the burst cycle (R8: F=13.49, p=0.0017) |
| A5 | Dedup-aware CC2v | Check prior confirmations before queueing | Prevents re-verification of already-confirmed findings |
| A6 | Resume Exp 36 | From R22 checkpoint with A1-A5 in place | Controlled comparison: same test article (evidence.py), same data, different design |

**Critical note:** A1 (registry windowing) and A2 (ρ) are essential. Without them, the coupled cascade recurs even with A3-A5 fixed. The audit traced the chain: context grows → ITC bursts → γ hides churn → no ρ to flag it → runner gate can't terminate. A1 breaks the first link, A2 enables detection.

**Semantic layer:** evidence.py (the Exp 36 test article) is already in the runner. The 5 fixes modify the existing runner. No semantic layer "addition" needed — it's the ouroboros cycle: schema fixes feed back into the codebase the schema reviews.

### Phase B — Reference Runner + CC2 Architecture (Exp 37 infrastructure)

| # | Task | Description |
|---|------|-------------|
| B1 | Reference runner | Parameterised entry point (test article, topology, round limits, convergence thresholds). Replaces per-experiment runner scripts. Incorporates all Phase A fixes + 13 design improvements. |
| B2 | CC2 role redesign | CC2 becomes manager/router only — no finding generation. Bounded authority (route, assess, escalate). Does not inject findings, override tool-backed verdicts, or make convergence decisions. |
| B3 | 5 CC2 sub-agents | All closed-constraint-space, mechanical. See Section IX (updated). |
| B4 | Domain-parameterised immune cells | Extend `ClaimType` enum per domain. Add domain-specific verification functions. Domain TOML routing for tool selection. Architecture (6-stage pipeline) invariant; content (stages 1-3) domain-specific. |
| B5 | Meta-cognitive feedback | Exp 37 only. Data-only, constrained response. See Section X. |
| B6 | Ascending abstraction guard | Convergence gate override: if ascending abstraction active (§7.3), gate cannot trigger regardless of other conditions. Appendix §7.4 reconciliation. |
| B7 | Promote LLM classifier + formalisation agent | From shadow to primary. v2 immune already primary for DC, NK, Helper T, Reg T. |

**CC2 Sub-Agent Design (revised — 5 agents, not 4):**

| # | Agent | Constraint Question | Output Schema | Capability |
|---|-------|-------------------|---------------|------------|
| 1 | Citation Verifier | Does finding accurately describe cited code/material? | {verified, cited_material, match_assessment, confidence} | Haiku |
| 2 | Fix Extractor | Can this NL fix become an applicable change? | {extractable, diff_or_correction, applies_cleanly, test_result} | Opus |
| 3 | Dedup Assessor | Does new finding describe same issue as existing one? | {duplicate, shared_root_cause, evidence_from_both} | Haiku |
| 4 | Programmatic Verifier | Can this NL claim be verified by tools (SymPy/AST/z3/SciPy)? | {verifiable, tool_used, result, verdict} | Opus + tools |
| 5 | CC2v | Confirm/reject/duplicate/escalate? (LLM verdict fallback) | {verdict, confidence, evidence_trace} | Opus |

Agent 4 (Programmatic Verifier) bridges the gap between what the immune pipeline's B Cell can mechanically parse and what requires LLM judgment. It decomposes NL claims into programmatic tests. Agent 5 (CC2v) handles genuinely ambiguous cases that Agent 4 cannot verify. CC2 routes findings to the appropriate agent based on finding attributes — the routing can be mechanically defined.

**Domain-Parameterised Immune Cells (B4 detail):**

The immune pipeline's 6-stage architecture is domain-agnostic. What changes per domain is the content of stages 1-3:

| Stage | Cell | Domain-Agnostic | Domain-Specific |
|---|---|---|---|
| 1 | DC | Dispatch mechanism | `ClaimType` enum + classification patterns |
| 2a | CT | LLM dispatch + verdict schema | Prompt template + source material format |
| 2b | B Cell | Tool dispatch + class-switching | Tool selection (SymPy/z3/statsmodels/dimensional) |
| 3 | NK | Similarity matching at τ_sim | Known false-positive patterns |
| 4 | HT | Cross-round dedup | Fully agnostic |
| 5 | RT | Reconciliation gate | Fully agnostic |

Domain examples:
- **Mathematics:** PROOF_STEP → z3, COMPUTATION → SymPy, BOUND → SymPy inequality
- **Physics:** CONSERVATION_LAW → SymPy, DIMENSIONAL → unit analysis, NUMERICAL → SciPy
- **Chemistry:** REACTION_BALANCE → stoichiometric, THERMODYNAMIC → SymPy energy, SAFETY → standards lookup
- **Engineering:** CODE_COMPLIANCE → standards table, LOAD_CALCULATION → numerical, MATERIAL → database cross-reference

Parameterisation via domain TOML files (already exist: `physics.toml`, `chemistry.toml`, `mathematics.toml`).

### Phase C — Bench Run 2 (27 frontier STEM tasks)

| # | Task | Description |
|---|------|-------------|
| C1 | 27 task-specific expert encodings | FT-001 through FT-027. 50-100 lines each. HARD/SOFT constraints, verification procedures, failure modes. Must NOT leak solutions. Plan: `bench/BENCH_EXPANSION_PLAN.md`. Tasks: `bench/tasks_frontier/`. |
| C2 | Finding schema adaptation | Claim + evidence format for non-SE tasks (not just code citations). |
| C3 | Domain verification routing | Extends B4. Three-layer composition: universal → domain → task-specific. |
| C4 | Open-problem scoring metrics | For FT-028+ (18 planned open-problem tasks). |
| C5 | Dry-run all 27 tasks | Verify tool availability, graceful degradation, no answer leakage. |
| C6 | Execute Bench Run 2 | 27 frontier tasks across 8 domains (mathematics, software, cross-domain, chemistry, hardware, structural, industrial, physics). |

**Domain transferability assessment:** The CDSFL schema is not over-optimised for SE. The core architecture (P-Pass, convergence measurement, multi-agent review, γ/ρ tracking, registry lifecycle) is domain-agnostic. What is SE-specific are the immune pipeline's verification procedures (CT code tracing, B Cell AST analysis) and finding schema (code citations). These are parameterised, not hardcoded — domain adaptation is configuration, not rewriting. 29 directive files across 12 domains already exist.

**Convergence prediction:** CDSFL may show cleaner convergence on concrete STEM tasks than on software engineering, because: (a) formal verification tools (SymPy, z3) are more directly applicable, (b) solution spaces are more bounded, (c) ground truth is more mechanically checkable. The 17:1 dedup ratio in Exp 36 reflects SE's unbounded solution space — mathematics and physics tasks with definite answers should produce lower churn.

### Phase D — Documentation and Outreach

| # | Task | Description |
|---|------|-------------|
| D1 | README rewrite | From blog post summary (founder working on blog post). Current README is outdated. |
| D2 | Mathematical Model Companion | Plain English walkthrough of appendix. Uses concrete examples from experiments. |
| D3 | Outreach dissemination | Blog post as main article. Point people to it, not send it directly. |

### Sequencing

A → B → C → D. Phases A and B can partially overlap (reference runner can be built while Exp 36 resume runs). Phase C is blocked on having a working reference runner (B1) and domain-parameterised immune cells (B4). Phase D is blocked on Bench Run 2 results for the strongest claims.

### Exp 37 — Full Experiment (After Reference Runner)

**Purpose:** Full experiment with all Phase B improvements on a new test article.

**Test article:** To be determined. Candidates: `endocrine.py`, `insect_brain.py`, `runner_core.py`, or `immune_agents.py` itself.

**Improvements beyond Phase A fixes:** CC2 sub-agents 1-5 running in parallel, CC2 as manager-only, fix-application pipeline (CONFIRMED → CLOSED), context windowing, per-model ρ tracking, pre-filter before CC2v queue, LLM classifier promoted, consolidation phase, meta-cognitive feedback, ascending abstraction guard, domain-parameterised immune cells.

---

## XII. Cross-References

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
| CC2 sub-agents | "4 agents" | **5 agents** (Programmatic Verifier added) | Design discussion 8 April 2026, P-pass survives |
| CC2 role | "player-manager (finds + verifies)" | **Manager/router only** (no finding generation) | Guardian layer parallel from Genesis, P-pass survives |
| R²=0.985 (early decay) | "CONFIRMED" | **DISPUTED** → R²=0.961 (R1-R4 window) | Mathematical model audit, 8 April 2026 |
| z=3.63 (R8 burst) | "CONFIRMED" | **DISPUTED** → z=5.24 (R1-R7 baseline) | Mathematical model audit, 8 April 2026 |
| Minimum Exp 36 fixes | "3 fixes" | **5 fixes** (registry windowing + ρ as C6 are essential) | Audit coupled cascade analysis |
| Forward path | "6-item task sequence" | **4-phase plan** (A: resume, B: reference runner, C: BR2, D: docs) | Revised 8 April 2026, 07:00 BST |
