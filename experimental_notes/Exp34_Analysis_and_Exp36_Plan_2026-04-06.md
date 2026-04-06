# Experiment 34 Analysis and Experiment 36 Integration Plan

**Date:** 6 April 2026, 04:45 BST
**Analysed by:** Claude Opus 4.6 (CC)
**Source:** `bench/logs/exp34_endocrine_20260405T225218Z/`

---

## Summary

| Metric | Value |
|--------|-------|
| Total raw findings | 390 |
| Canonical registry entries | 81 |
| Garbage/parser artifacts | 6 |
| Refuted | 4 |
| Duplicate groups consolidated | 12 (covering ~30 entries) |
| Contested (design debate) | 5 |
| **Verified unique findings** | **33** |
| Fix evaluation results | 0/280 SAFE, 279 UNEVALUABLE |
| Substantive convergence round | R11 |
| Gate closest to passing | R14 (open_ch=1, contested=2) |
| Gate at termination (R23) | open_ch=8, contested=7 |
| γ peak / final | 0.758 (R16) / 0.713 (R23) |

---

## Verified Unique Findings (De-duplicated)

### Tier 1 — Critical (must fix before Exp 36)

| # | Group | Key Finding | Sev | Description | Fix |
|---|-------|-------------|-----|-------------|-----|
| 1 | A+I | C0026/C0046 | 1.0 | Sandbox environment asymmetry: pre-fix tools run on real project, post-fix on bare `/tmp`. Different import resolution, config, package structure. | Run both baselines in identical sandboxes; preserve package structure; copy config files. |
| 2 | B | C0027 | 1.0 | Test command paths don't exist in sandbox. Tests always fail for infrastructure reasons. | Copy test directories into sandbox, or skip test execution (static analysis only). |
| 3 | D | C0038 | 0.9 | Tool timeout returns empty diagnostics + `available=True`. Fail-open. | Check `stderr in ("NOT_FOUND", "TIMEOUT")` in each runner. |
| 4 | E | C0008 | 0.9 | `_count_tool_issues` swallows all exceptions as 0. Tool failure = zero issues. | Re-raise `ToolNotFoundError`; sentinel for other failures. |
| 5 | F | C0032 | 0.88 | `evaluate_fix` omits mypy (scan_health runs it). Type coverage gap. | Add `run_mypy` to both baseline and post-fix. |
| 6 | — | C0077 | 0.9 | `EndocrineLayer.run()` has no top-level exception handling. Any step raises = round fails. | Wrap each step in try/except; return partial results. |

### Tier 2 — High (improves reliability)

| # | Finding | Sev | Description | Fix |
|---|---------|-----|-------------|-----|
| 7 | C0013 | 0.85 | Whole-file replacement accepts any 6+ line compilable text. | Require `def`/`class`/`import` at top level. |
| 8 | C0042 | 0.83 | `context_budget: int` annotation lies; body coerces dict/str/float. | Accept `Union` or validate caller-side. |
| 9 | C0058 | 0.85 | `read_text` catches `OSError` but `UnicodeDecodeError` ∈ `ValueError`. | Catch `(OSError, UnicodeDecodeError)`. |
| 10 | C0059 | 0.7 | `compile()` catches `SyntaxError` but null bytes raise `ValueError`. | Catch `(SyntaxError, ValueError)`. |
| 11 | C0010 | 0.79 | Upper median for even-length lists. SymPy verified. | Use `statistics.median`. |
| 12 | C0028 | 0.8 | Response size anomaly emits wrong `signal_type="context_growth"`. | Change to `"response_size_anomaly"`. |
| 13 | C0053 | 0.9 | `_find_target_file` falls back to `source_paths[0]` on no match. | Return `None`; caller returns UNEVALUABLE. |
| 14 | C0062 | 0.7 | `evaluate_fix` has try/finally, no except. Exceptions propagate. | Add except → UNEVALUABLE. |
| 15 | C0011 | 0.77 | Docstring/code strategy numbering mismatch. No diff rejection. | Update docstring; add diff rejection. |
| 16 | C0024 | 0.8 | Strategy 3 multi-line replacement corrupts line indices. | Reverse-order processing. |

### Tier 3 — Medium (PoC-acceptable)

| # | Finding | Sev | Description |
|---|---------|-----|-------------|
| 17 | C0041 | 0.83 | `cumulative_context_chars` sums all models; `context_budget` is per-model. |
| 18 | C0045 | 0.6 | `_categorise_ruff` blanket F→DEAD_CODE (F821 is not dead code). |
| 19 | C0019 | 0.65 | Novelty plateau `n <= 1` threshold (design choice). |
| 20 | C0036 | 0.7 | `commonpath` ValueError on mixed paths. |
| 21 | C0037 | 0.5 | Filename regex excludes hyphens. |
| 22 | C0056 | 0.5 | Strategy 1 `re.DOTALL` allows cross-newline matching. |
| 23 | C0060 | 0.8 | Strategy 3 greedy regex. |
| 24 | C0067 | 0.7 | Double fix evaluation (endocrine + immune Stage 4). |
| 25 | C0018 | 0.5 | Strategy 1 replaces first occurrence only. |
| 26 | C0020 | 0.55 | `_scan_history` grows unbounded. |
| 27 | C0025 | 0.4 | Non-existent source_paths not filtered. |
| 28 | C0034 | 0.79 | Parse failure returns [] but tool marked available. |
| 29 | C0057 | 0.5 | `_find_target_file` uses `os.sep` (cross-platform). |
| 30 | C0072 | 0.74 | No diff/patch format support. |
| 31 | C0079 | 0.5 | `test_cmd` not validated as list. |
| 32 | C0065 | 0.7 | Missing `__init__.py` in sandbox. |
| 33 | — | — | Ruff: `typing.Any` imported but unused (line 41). |

---

## Refuted Findings

| Finding | Claim | Reality |
|---------|-------|---------|
| C0012 | `_count_tool_issues` passes string to tool runners expecting list | Line 599: `tool_runner([file_path])` — already wrapped in list |
| C0014 | `_compute_fix_verdict` allows cross-tool masking | Lines 774-777: each tool checked independently before total |
| C0043 | `tmpdir` used before assignment | Line 677: `tmpdir = None`; line 707: `if tmpdir:` |
| C0080 | NEUTRAL when `total_net < 0` and `tests_passed is None` | Line 781: `total_net < 0` returns SAFE before tests_passed check |

---

## Duplicate Groups

| Group | Core Issue | Findings | Best |
|-------|-----------|----------|------|
| A | Sandbox baseline asymmetry | C0001, C0006, C0015, C0016, C0026, C0044, C0078 | C0026 |
| B | Test cmd path failure | C0002, C0027, C0047 | C0027 |
| C | Upper median | C0004, C0010 | C0010 |
| D | Timeout masked as available | C0005, C0029, C0038, C0049 | C0038 |
| E | Exception swallowing → 0 | C0008, C0061, C0064, C0071 | C0008 |
| F | Missing mypy in eval | C0007, C0032, C0048 | C0032 |
| G | context_budget type lies | C0009, C0017, C0042 | C0042 |
| H | Whole-file replace permissive | C0013, C0033, C0054 | C0013 |
| I | Sandbox strips package dir | C0031, C0046, C0050 | C0046 |
| K | Wrong signal_type | C0028, C0040, C0069 | C0028 |
| L | Strategy 3 index corruption | C0024, C0052 | C0024 |

---

## Deep Run Analysis

### Per-Model Performance

| Model | Raw | Novel | Confirmed | Novelty Rate | Dup Rate | Code Patches |
|-------|-----|-------|-----------|--------------|----------|-------------|
| DeepSeek | 40 | 23 | 13 | 57.5% | 42.5% | 74% |
| CC2 | 60 | 17 | 13 | 28.3% | 71.7% | 0% |
| ChatGPT | 144 | 15 | 15 | 10.4% | 89.6% | 60% |
| Codex | 109 | 14 | 8 | 12.8% | 87.2% | 57% |
| Gemini | 37 | 12 | 9 | 32.4% | 67.6% | 83% |

**Key:** DeepSeek highest novelty rate. ChatGPT best confirmer (100% confirmation).
Gemini only effective challenger (48 challenges vs 0 from CC2/ChatGPT).
CC2 zero code patches — all prose-only fix descriptions.

### Convergence Timeline

- **R0-R5:** Discovery burst (29→21 findings/round, 46 canonical by R5)
- **R6-R10:** Deceleration (γ rising 0.698→0.742, novelty dropping)
- **R11:** Substantive convergence (open_ch=1, contested=0, zero novel ×2)
- **R12-R14:** Near-gate (γ peak 0.758, gate closest at R14)
- **R15-R19:** Post-convergence inflation (unmerged dupes accumulate)
- **R20-R24:** Extension divergence (open_ch 7→12, contested 3→7)

### Extension Mechanism Failure

R21-R24 produced 43 raw findings but only 4 novel (all UNCONFIRMED).
The extension was triggered by unresolved open/contested counts that
*cannot* be resolved by more rounds — they require instrumentation fixes.
**Recommendation:** Extension must produce measurable reduction in blocking
conditions or terminate early.

### Instrumentation Failures

1. **Verdict regex:** CC2 bold-formatted verdicts invisible. ~40% of CC2
   participation lost. Fixed in Exp 35 runner.
2. **CONTESTED resolution:** C0023 challenged 7 times, C0039 challenged 12
   times. Neither resolved. No status path exists.
3. **Fix evaluation:** 279/280 UNEVALUABLE. Sandbox broken. Root cause of
   convergence gate failure.

---

## Exp 36 Integration Plan

### Step 1: Fix endocrine.py (Tier 1 critical fixes)

Apply the 6 critical fixes in order. After each: run 688 tests, pyright, ruff.

### Step 2: Fix runner instrumentation

Already in Exp 35 runner:
- Verdict regex for CC2 bold formatting
- ITC adaptive recovery
- Persistent fingerprints
- Dual topology (relay/star)

Add to Exp 35 runner before Exp 36:
- CONTESTED→REFUTED auto-resolution (3+ challenges, 0 defences in last 3 rounds)
- Extension gate: must reduce open_ch or contested, or terminate
- Per-model context tracking
- Declining-gamma alert (3+ consecutive drops)

### Step 3: CX + Gemini review (full CDSFL)

Submit fixed endocrine + fixed runner for review.

### Step 4: Run Exp 36

Target: evidence layer (`bench/evidence.py`).
Topology: relay (default) with star available via `--topology star`.
Prediction: convergence detection at R12-R15 with working instrumentation.
