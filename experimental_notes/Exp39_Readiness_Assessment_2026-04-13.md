# Exp 39 Readiness Assessment

**Date:** 13 April 2026, 01:15 BST  
**Branch:** `exp39-experimental` | **Commit:** `f57d6ce`  
**Tests:** 793 total, 77 immune agent tests passing  
**Models consulted:** Gemini 3.1 Pro (confer), Codex 5.3 (dispatched, pending)

---

## Summary

**39-0 can run now.** None of the 10 items on the agreed execution order are truly blocking for the infrastructure gate test. The execution order was designed for the full Exp 39 series (0–M), not as prerequisites for the gate test specifically. Two low-effort improvements are recommended before launch.

---

## Fixes Applied This Session

### Fix 1: `origin_type="model"` on All Finding Sites

**File:** `bench/runner_core.py` — 5 instantiation sites  
**Sites:** JSON array parser (L417), JSON object parser (L496), pipe-delimited (L549), marker (L710), fallback (L734)

Every model-generated finding now carries explicit `origin_type="model"`, distinguishing it from future Ouroboros-origin findings.

### Fix 2: Provenance Fields in FindingRegistry

**File:** `bench/reference_runner.py` — `FindingRegistry.register()` (L307–312)  
**Fields added:** `origin_type`, `source_ref`, `retrieval_query`, `retrieved_at`, `source_hash`, `source_diversity`

Registry entries now capture the full provenance packet from the Finding schema.

### Fix 3: Missing Files Committed

**File:** `bench/macrophage_cell.py` (546 LOC) — missed from prior `sv` commit  
**Also:** 4 confer scripts, confer logs, experimental notes, O1 query extraction fix

---

## Blocking Analysis: Execution Order vs 39-0

| # | Item | Blocking 39-0? | Reasoning |
|---|------|:-:|---|
| 1 | IFalsificationGate protocol | **No** | Current gate works; redesign is for domain-agnosticism |
| 2 | Churn detection (C6) | **No** | 39-0 has hard caps (8 rounds, 1h); basic ρ sufficient |
| 3 | Missing domain TOMLs | **No** | 39-0 config doesn't reference domain TOMLs |
| 4 | B-Cell dispatch | **No** | 39-0 uses generic dispatch |
| 5 | Severity fusion | **No** | Existing NK severity works |
| 6 | Sycophancy detection | **No** | Agreed to shadow alongside, not before |
| 7 | O1 calibration | **No** | Shadow mode with defaults |
| 8 | Run 39-0 | *Goal* | — |
| 9 | MC command sync | **No** | Documentation |
| 10 | Phase 9 | **No** | Explicitly deferred |

---

## Gemini 3.1 Pro Confer (8,245 chars)

Gemini recommended 5 sequential steps before 39-0: (1) state persistence, (2) HIL visibility, (3) gate interface, (4) convergence math, (5) domain routing.

### FFF Falsification of Gemini's Claims

| Gemini Claim | Verdict | Evidence |
|---|---|---|
| IFalsificationGate + Severity Fusion blocking | **Partially refuted** | Current gate works. Exp 38 ran 24 rounds successfully. |
| C6 prevents infinite loops | **Refuted** | `max_rounds: 8` + `wall_clock_cap_s: 3600` prevent loops. |
| cs_software.toml + B-Cell dispatch blocking | **Partially refuted** | 39-0 config doesn't reference domain TOMLs. |
| ImmuneResponse checkpointing mandatory | **Valid for later, not 39-0** | 8-round test, ~1h. Exp 38 completed 24 rounds without it. |
| Round report counts-only limits HIL | **Correct** | HIL should see finding details, not just numbers. |

---

## Parsing & HIL Readability

### System Parsability: ✓ Sound

- Pipeline operates on `Finding` objects throughout
- All 6 core cells consume/produce structured data
- Shadow cells produce `MacrophageSummary` and `OuroborosShadowLog` (both have `.to_dict()`)
- JSON serialisation via `json.dumps(round_data, default=str)` — works
- `origin_type` now set on all findings (Fix 1)
- Registry captures full provenance (Fix 2)

### HIL Readability: 3 Issues Identified

1. **Round report is counts-only** — reviewer sees "14 findings from Gemini" but not what they say. Most important gap.
2. **ImmuneResponse is transient** — immune reasoning trace not persisted for post-hoc review.
3. **Shadow cell data is summary-level** — counts and flags, not detailed observation text.

All reduce HIL visibility but don't prevent pipeline function.

---

## Preflight Results

| Model | Status | Latency |
|---|---|---|
| CC2 (Claude Opus 4.6) | OK | 5.1s |
| Codex (GPT-5.4) | OK | 2.4s |
| ChatGPT (GPT-5.4) | OK | 1.8s |
| Gemini (3.1 Pro) | OK | 6.6s |
| DeepSeek (Reasoner) | OK | 19.2s |

Launcher dry-run confirms 39-0 has no dependencies.

---

## Minimum Viable Path to 39-0

### Recommended (low-effort, high-value)

1. **Enhance round report detail** — add finding descriptions + provenance to round JSON (~30–50 LOC in `reference_runner.py`)
2. **Create minimal `cs_software.toml`** — domain awareness for software analysis (~30–50 lines TOML)

### After these: Run 39-0

```bash
python3 bench/launch_exp39.py --only 39-0
```

### For 39-A Onwards (implement between 39-0 and 39-A)

- ImmuneResponse checkpointing
- Churn detection (C6)
- Severity fusion (§7.7)
- IFalsificationGate protocol
- cs_software.toml (full, not minimal)

---

## Codex Response

Dispatched but had not returned at time of assessment. Will be reviewed on arrival.
