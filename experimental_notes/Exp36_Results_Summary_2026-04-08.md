# Experiment 36 — Results Summary

**Date:** 8 April 2026
**Target:** `bench/evidence.py`
**Panel:** Claude Opus, ChatGPT, Codex, DeepSeek, Gemini (5 models)
**Rounds:** 45 (STATE_CONVERGED)
**γ (Duane):** 0.393 (Moderate depletion)

## What the Experiment Found

217 findings generated across 45 rounds. After deduplication and closure, 12 remained open. All 12 were mechanically cross-checked using AST parsing, regex verification, and source inspection. They describe **3 actual bugs**.

### Bug 1 — Finding-ID Extraction Misses Records

- **Location:** `_extract_finding_ids()`, line 185
- **Description:** Regex `\b[A-Za-z]\d{3,5}\b` only searches `payload` and `metadata` fields. Finding IDs in `artifact_type`, `recorded_by`, or underscore-compound strings (e.g., `C0042_analysis`) are silently missed. `trace_finding()` and `query()` return empty results with no error.
- **Verification:** AST parse confirming only two call sites (lines 111, 113) inside `payload`/`metadata` branches. Regex execution confirming `\b` word boundary fails on underscore-adjacent IDs.
- **Findings:** C0200, C0205, C0210, C0213, C0214, C0216, C0217 (7 findings, same root cause)

### Bug 2 — verify_bundle Doesn't Verify Record Content

- **Location:** `verify_bundle()`, lines 507–541
- **Description:** Checks that `chain_hash` appears in the Merkle tree, but never recomputes the hash from `sealed_body` content. Tampered payloads pass verification if `chain_hash` field is preserved.
- **Verification:** AST parse confirming zero calls to `_compute_entry_hash` or `_compute_chain_hash` inside `verify_bundle()`. Only hash-related operations are `.get("chain_hash")` string comparisons.
- **Findings:** C0211, C0215 (2 findings, same root cause)

### Bug 3 — Timestamp Sort Has No Tiebreaker

- **Location:** `trace_finding()`, line 431; `_utc_now()`, verification_chain.py line 230
- **Description:** Sort key is `e.timestamp_utc` only. `_utc_now()` uses second-level precision (`%Y-%m-%dT%H:%M:%SZ`). Records appended within one second can be misordered. `record_index` exists in `ProvenanceEvent` but is not used as tiebreaker.
- **Verification:** AST parse confirming single-attribute sort key and format string without `%f` microseconds.
- **Findings:** C0087, C0208, C0209 (3 findings, same root cause)

## Redundancy

12 findings for 3 bugs = **4.0× redundancy**. This is itself a finding: the dedup agent (Agent 3) should have caught 9 of these. Routing threshold (Jaccard similarity ≥ 0.65) was too restrictive for semantic duplicates with different surface phrasing.

## What Was Fixed

### In evidence.py: Nothing

None of the 3 discovered bugs were fixed by the experiment.

### In Pipeline Infrastructure: 6 Fixes

| Fix | Component | Issue |
|-----|-----------|-------|
| Model ID | cc2_manager.py:57 | `claude-opus-4` → `claude-opus-4-6` (model ID didn't exist) |
| CC2v parser | cc2_manager.py:599–640 | Markdown stripping + keyword fallback (all findings were escalating) |
| mark_verified | run_exp36_evidence.py | Signature mismatch `(fid, round_idx)` → `(fid)` |
| CT v2 timeout | insect_brain.py | 300s → 600s (was timing out) |
| Empty-choices guards | 5 files, 12 sites | Upstream 500 errors → `CircuitBreakerTripped` instead of crash |
| Registry cleanup | runner_state.json | 48 phantom entries describing already-fixed bugs, closed manually |

These kept the experiment running. They did not fix what the experiment was studying.

## CC2 Agent Pipeline Assessment

| Agent | Invocations | Result | Assessment |
|-------|------------|--------|------------|
| 1 (Citation) | 6 | ALL UNCLEAR (conf=0.30) | **Broken.** Haiku too weak for code reasoning. Zero signal. |
| 2 (Fix) | 2 | 1 EXTRACTED, 1 NOT_EXTRACTABLE | Working, low volume. Only fires when `proposed_fix` exists. |
| 3 (Dedup) | 2 | Both NOVEL | Barely functional. Routing threshold too restrictive. |
| 4 (Programmatic) | 1 | VERIFIED_TRUE (conf=0.95) | Best result, worst coverage. Routing patterns too narrow. |
| 5 (CC2v) | All routed | Real CONFIRM/REJECT/ESCALATE | Working but over-relied-upon. No tools — pure semantic judgment. |

**Structural problem:** Pipeline designed for tool-backed agents (1,3,4) to handle bulk, CC2v (5) as fallback. In practice, CC2v handles almost everything. Tool-backed agents are ornamental.

## Lessons

1. **Tool constraint box is the mechanism.** Every CC2 agent must operate within a defined tool envelope. Tool output is the evidence. LLM reasoning interprets tool output — it never substitutes for it. An agent with no tools is not a verifier.

2. **Fix generation must be a first-class pipeline stage.** The system currently finds bugs and describes them repeatedly but does not generate, test, or verify fixes. The deliverable should be: bug + verified fix + consequence map.

3. **Fixes are suggested, not auto-applied.** CC2 agents verify both bugs and fixes, but the human makes the final decision. The pipeline presents verified, explained, ready-to-apply recommendations.

## Forward Path: Experiment 37

Target: `evidence.py` again, clean run with all fixes pre-applied. Revised CC2 pipeline with tool envelopes on all agents, fix generation as pipeline stage, broader routing for dedup and programmatic verification. Monitoring: per-round checks on all 5 agents, pause-and-FFAF if any agent fails for 2 consecutive rounds.
