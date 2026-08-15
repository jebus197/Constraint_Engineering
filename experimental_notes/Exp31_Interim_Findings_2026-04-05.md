# Experiment 31 — Final Findings

**Date:** 5 April 2026, 07:38 BST
**Status:** BUDGET_EXHAUSTED (15 rounds, 360 findings, final κ 0.619, final γ 0.106)

## Experiment Design

Same 3 test articles as Exp 30, same 5 models (CC2, Codex, Gemini, DeepSeek, ChatGPT), directed relay mode, FFF pattern. Base prompt tells models about 39 applied fixes from Exp 30 and instructs them NOT to rediscover closed bugs.

**Purpose:** Demonstrate genuine epistemic convergence after Exp 30 fixes applied.

## Convergence Trajectory

| Round | Findings | Shadow γ | Time (s) |
|-------|----------|----------|----------|
| 0 (blind) | 32 | 0.000 | 378.5 |
| 1 (adaptive) | 40 | -0.170 | 288.4 |
| 2 | 28 | -0.037 | 456.0 |
| 3 | 22 | 0.035 | 326.8 |
| 4 | 25 | 0.053 | 364.6 |
| 5 | 26 | 0.058 | 501.9 |
| 6 | 25 | 0.063 | 447.3 |
| 7 | 19 | 0.079 | 667.1 |
| 8 | 21 | 0.087 | 375.8 |
| 9 | 15 | 0.102 | 410.9 |
| 10 | 18 | 0.109 | 368.8 |
| 11 | 22 | 0.109 | 406.2 |
| 12 | 17 | 0.115 | 426.2 |
| 13 | 25 | 0.110 | 387.2 |
| 14 | 25 | 0.106 | 470.2 |

**Phase 1 (R0–R6):** γ rising slowly (0.000→0.063), findings plateaued at 25–26/round. Structural churn on ~10 bugs without convergence mechanisms.

**Phase 2 (R7–R14):** Good Enough, merge, and B-Cell UNCERTAIN→HIL instructions injected mid-experiment. Finding counts dropped to 15–22 range (R7–R12), γ accelerated to 0.115. Late rounds (R13–R14) reverted to 25 as models exhausted novel bugs and revisited known issues.

**Terminal state:** κ=0.619 (above typical convergence threshold) but γ=0.106 (below 0.5). The models reached inter-rater agreement but could not close findings between rounds due to the dead bug-closed gate. BUDGET_EXHAUSTED is the correct and honest outcome.

### Comparison with Exp 30

| Metric | Exp 30 | Exp 31 |
|--------|--------|--------|
| γ trajectory | 0.567 → 0.320 (falling) | 0.000 → 0.106 (rising) |
| γ slope | -0.018/round | +0.009/round |
| Total findings | 318 | 360 |
| Terminal κ | — | 0.619 |
| Avg findings/round (late) | 22.5 | 20.8 (R7–R14) |
| Outcome | BUDGET_EXHAUSTED | BUDGET_EXHAUSTED |

Exp 30 was diverging. Exp 31 is converging — but too slowly. The 39 applied fixes reduced re-discovery of closed bugs, and the mid-experiment interventions visibly reduced finding churn. The remaining gap is structural: the bug-closed gate (E31-01) and autoimmune lock (E31-02) must be fixed before genuine convergence is achievable.

## Why Convergence Is Not Expected This Run

1. **Bug-closed gate is dead code.** `copy.deepcopy(triaged)` in the immune pipeline severs references to original Finding objects. Stage 4 sets `verified=True` on deep copies. The originals in `all_findings` never see it. NK cell's bug-closed gate checks `matched_pf.verified` on originals — always False.

2. **Good Enough instruction not in running prompt.** Models are proposing competing fixes for the same bugs instead of agreeing on the first sufficient solution. The instruction was added to the runner after Exp 31 launched.

3. **B-Cell UNCERTAIN findings not escalated.** UNCERTAIN findings churn across rounds without resolution. The Stage 5.5 escalation was added after launch.

4. **Finding merge instruction not in running prompt.** Models file separate finding IDs for the same underlying bug. CC2 spontaneously asked DeepSeek to merge in Round 6 — but this isn't mandatory yet.

## Key Findings from Exp 31 (Interim)

### Critical — Architectural

**E31-01: Deep-copy propagation severs verified/escalated flags (sev 0.95)**
- File: `immune_agents.py`, `run_immune_pipeline()`
- Stage 2 deep-copies triaged for NK thread safety. After NK completes, `triaged = nk_triaged_result` replaces triaged with deep copies. Stage 4 and 5 set `verified`/`escalated` on these copies. The originals in `InsectBrain.persist()` → `all_findings` never see the flags.
- Consequence: (a) checkpoint serialises `verified=False` always; (b) bug-closed gate is dead code; (c) auto-escalation fires on findings that should be closed.
- Models: CC2 (R4), DeepSeek (R5), Codex (R6) — independently confirmed.
- Fix: After immune pipeline returns, propagate verified/escalated flags back to the canonical findings in `all_findings`.

**E31-02: Autoimmune override violates reconciliation lock (sev 0.90)**
- File: `immune_agents.py`, `run_immune_pipeline()`
- Reconciliation gate documents that REJECTED verdicts from both pipelines are "LOCKED — cannot be overridden." But autoimmune recovery does `filtered = [tf.finding for tf in triaged]`, resurrecting everything including locked rejections.
- Models: Codex (R2), CC2 (R4), Gemini (R5) — independently confirmed.
- Fix: Maintain a set of locked finding IDs from reconciliation gate. Exclude them from autoimmune resurrection.

**E31-03: check_convergence() ordering masks genuine convergence (sev 0.85)**
- File: `insect_brain.py`, `check_convergence()`
- Max-rounds hard stop fires BEFORE convergence detector. If genuine convergence occurs on the final round, it's reported as BUDGET_EXHAUSTED.
- Models: Codex (R1), CC2 (R3), Gemini (R3), DeepSeek (R4) — independently confirmed.
- **FIXED** during this session: convergence detector now runs first.

**E31-04: signal_complete() precedence masks FAILED as BUDGET_EXHAUSTED (sev 0.80)**
- File: `insect_brain.py`, `signal_complete()`
- BUDGET_EXHAUSTED evaluated before FAILED. If all models crash, experiment runs empty rounds until max_rounds, then reports budget exhaustion instead of failure.
- Models: Codex (R5), DeepSeek (R6) — independently confirmed.
- **FIXED** during this session: FAILED now takes precedence.

### High — Verification Pipeline

**E31-05: Helper T v2 confidence inflation at reconciliation boundary (sev 0.80)**
- File: `immune_agents.py`, `helper_t_v2_shadow()`
- Stores raw `best_reject` confidence, not the `effective_reject` after asymmetric scaling. Example: effective_reject=0.63 (barely wins) stored as 0.90. Reconciliation gate then picks REJECTED at 0.90 over CONFIRMED at 0.75, even though actual margin was 0.03.
- Models: CC2 (R6).
- Fix: Store `round(effective_reject, 4)` not `round(best_reject, 4)`.

**E31-06: Directed message temporal leak — two rounds instead of one (sev 0.75)**
- File: `insect_brain.py`, `_format_responses_with_directed()` and `relay_directed()`
- `m.round_idx >= current_round - 1` with stale `current_round` includes messages from two rounds. Wastes context budget with stale directed messages.
- Models: Codex (R1), DeepSeek (R5) — independently confirmed.
- Fix: Use `m.round_idx == current_round - 1` (strict equality).

**E31-07: NK v2 anomaly detection neutered vs v1 (sev 0.70)**
- File: `immune_agents.py`, NK v2 vs v1
- NK v2 emits UNCERTAIN/0.4 where v1 emits REJECTED/0.6 for anomalous findings. In Helper T v2, UNCERTAIN contributes zero weight — anomaly gate is effectively disabled for v2 path.
- Models: CC2 (R4), ChatGPT (R2).

**E31-08: escalated field missing from checkpoint serialisation (sev 0.70)**
- File: `insect_brain.py`, `_save_checkpoint()`
- Serialises `verified` but not `escalated`. `load_checkpoint` defaults `escalated` to False. Auto-escalated findings lose status on recovery.
- Models: CC2 (R0).

**E31-09: verification_chain.py load_json() accepts non-dict top-level JSON (sev 0.77)**
- File: `verification_chain.py`, `load_json()`
- No `isinstance(data, dict)` guard. A JSON array or scalar passes `json.load()` then crashes on `data.get()`.
- Models: Codex (R0).

**E31-10: CT v2 search-manifest accepts fabricated grep targets (sev 0.72)**
- File: `immune_agents.py`, `_verify_search_manifest()`
- Grep verification is syntactic only. Fabricated grep against nonexistent targets still counts as verified, inflating confidence.
- Models: Codex (R0).

**E31-11: check_convergence() ignores self.state.failed (sev 0.80)**
- File: `insect_brain.py`, `check_convergence()`
- If all models fail, orchestrator spins empty rounds until max_rounds. Then convergence_reason is overwritten with BUDGET_EXHAUSTED, masking the crash.
- Models: Codex (R5), DeepSeek (R6).
- **FIXED** during this session: fail-fast check added at top of check_convergence().

**E31-12: Skin barrier basename resolution ordering (sev 0.70)**
- File: `immune_agents.py`, `skin_barrier_check()`
- Basename match fires before partial path match. Citation `src/test.py` incorrectly resolves to `lib/test.py` via basename match when only bare filenames should use basename fallback.
- Models: Gemini (R0).

**[Correction 2026-08-12.]** `src/test.py` and `lib/test.py` in the line above are
**illustrative example paths, not repository files** — the minimal pair that
demonstrates the ordering defect in `skin_barrier_check()`. Neither has ever
existed here: `git log --all --name-only --format="" | grep -E '^(src|lib)/'`
returns nothing, and this repository has no top-level `src/` or `lib/` directory at
any commit. They are recorded here so that an automated reference check reads them
as the worked example they are rather than as two dead pointers.

### Medium — Persistence

**E31-13: Immune pipeline mutations not persisted (sev 0.75)**
- File: `insect_brain.py`
- `persist()` called BEFORE `run_immune_pipeline()`. Round JSON and checkpoint only store unverified, unescalated findings. Immune verification work from current round lost on crash.
- Models: Gemini (R0), CC2 (R1).

**E31-14: Truncation marker attributed to model (sev 0.50)**
- File: `insect_brain.py`, relay functions
- `[TRUNCATED at 10000 chars]` appears inside model's attributed section. Receiving model may generate meta-findings about truncation.
- Models: DeepSeek (R7).

### Late-Round Findings (R8–R14)

**E31-15: AST constant extraction skips negative literals (sev 0.82)**
- File: `immune_agents.py`, `_extract_constants_from_ast()`
- Python parses `THRESHOLD = -0.5` as `ast.UnaryOp(ast.USub, ast.Constant(0.5))`. The strict `isinstance(node.value, ast.Constant)` check skips all negative numbers. B-Cell v2 cannot ground Z3 claims against negative-valued constants.
- Models: DeepSeek (R9, OPEN), Gemini (R14, claimed and fixed).

**E31-16: Skin barrier lacks path containment (sev 0.85)**
- File: `immune_agents.py`, `skin_barrier_check()`
- Unlike `_verify_ct_claim()` which has path traversal protection (C5-01), skin barrier opens any path validated by `os.path.isfile()`. A finding citing `/etc/passwd:1` would confirm its existence, creating a file-existence oracle for the LLM ecosystem.
- Models: Gemini (R14).

**E31-17: Search manifest dict-to-string parsing (sev 0.77)**
- File: `immune_agents.py`, `_verify_search_manifest()`
- When `args` is a dict (e.g. `{"path": "main.py"}`), validation casts to string `"{'path': 'main.py'}"`. For Read, `os.path.isfile()` correctly fails the stringified dict. For Grep, `re.compile()` accepts it as valid regex. Read attempts systematically rejected, Grep attempts systematically accepted — skews `test_severity` scoring.
- Models: Gemini (R14).

**E31-18: Verification chain epoch schema not validated at load (sev 0.85)**
- File: `verification_chain.py`, `load_json()`
- Records are type-checked (must be dicts) but epochs array accepts any JSON type. `verify_chain()` later calls `epoch.get()` on non-dict epochs, raising `AttributeError` not caught by the `except (KeyError, TypeError, ValueError)` block. Crashes verification instead of returning invalid status.
- Models: Gemini (R14).

## Fixes Applied During This Session

| Fix | File | Description |
|-----|------|-------------|
| check_convergence() ordering | insect_brain.py | Convergence detector runs before budget hard-stop |
| signal_complete() precedence | insect_brain.py | FAILED before BUDGET_EXHAUSTED |
| check_convergence() fail-fast | insect_brain.py | self.state.failed check at top |
| B-Cell UNCERTAIN → HIL escalation | immune_agents.py | Stage 5.5 added |
| Good Enough instruction | run_exp30/31.py | AGREE/CHALLENGE/EXTEND, no aesthetic alternatives |
| Finding merge instruction | run_exp30/31.py | Mandatory dedup before filing |
| Merkle sealing | run_exp31.py | Experiment logs sealed into verification chain |

## Fixes Queued for Post-Experiment

| Finding | File | Priority |
|---------|------|----------|
| E31-01: Deep-copy propagation | immune_agents.py | CRITICAL |
| E31-02: Autoimmune lock enforcement | immune_agents.py | HIGH |
| E31-05: Confidence inflation | immune_agents.py | HIGH |
| E31-06: Directed message leak | insect_brain.py | HIGH |
| E31-07: NK v2 anomaly neutered | immune_agents.py | MEDIUM |
| E31-08: escalated serialisation | insect_brain.py | MEDIUM |
| E31-13: Persist before immune pipeline | insect_brain.py | MEDIUM |
| E31-15: AST negative literal extraction | immune_agents.py | MEDIUM |
| E31-16: Skin barrier path containment | immune_agents.py | HIGH |
| E31-17: Search manifest dict parsing | immune_agents.py | MEDIUM |
| E31-18: Epoch schema validation | verification_chain.py | MEDIUM |

## Next Experiment Plan

- Same 5 models, directed relay, FFF pattern
- **Four** test articles: add `endocrine.py` alongside the existing three
- All queued fixes applied
- Good Enough + merge instructions active from Round 0
- B-Cell UNCERTAIN → HIL escalation active
- Bug-closed gate functional (deep-copy fix)
- Prediction: genuine convergence within 15-round budget
