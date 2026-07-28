# Shadow Systems Analysis — Exp 39-0

## Ouroboros Cell (O1) — Per-Round Assessment

**Round 0 (2563 bytes):** Functionally correct. Identified 4 UNCERTAIN findings as research targets (`Gemini_F002`, `Codex_F003`, `Codex_F001`, `ChatGPT_F001`). Issued 3 arXiv queries (respecting the MAX_QUERIES_PER_ROUND=3 cap). All 3 queries fell back to `shadow_mock` status with 0 papers — the `_fetch_metadata` method attempted real arXiv API calls but caught an exception (likely missing `arxiv` package) and gracefully degraded. Generated 2 candidate claims (respecting MAX_CANDIDATE_CLAIMS=2 cap) with correct provenance packets and `falsification_debt: high`. Set `would_have_injected: true`.

**Rounds 1-5 (193-196 bytes each):** All empty — zero anomalies observed, zero queries, zero candidates, `would_have_injected: false`. This is **expected behaviour**, not a bug. Two conditions feed the Ouroboros targets: (1) Macrophage anomalies (none in any round), and (2) UNCERTAIN entries in `immune_response.final_verdicts` (none in R1-R5 — the NK cell resolved everything to DUPLICATE). With no targets, the cell correctly short-circuits. The 13x file size ratio between R0 and R1-R5 is fully explained by populated vs empty data structures.

### Ouroboros Quality Issues

1. **Query quality (medium priority):** `_target_to_query` converts `"uncertain_finding:Gemini_F002"` into `"uncertain finding Gemini_F002"`. The finding ID is an internal identifier, not a searchable concept. Even if arXiv calls succeeded, results would be irrelevant. The method should extract the actual finding description from the round findings or immune response.

2. **Source diversity (low priority):** All 3 queries went to arXiv only. `_build_queries` (line 267 of `ouroboros_cell.py`) always uses `self.allowed_sources[0]`. No round-robin or diversity-aware source selection exists despite the cell being configured with `["arxiv", "semantic_scholar"]`.

### What Is Working in Ouroboros

Shadow mode isolation, hard caps enforced, provenance packet structure complete, API fallback graceful, JSON log format valid.

---

## Macrophage Cell — Per-Round Assessment

**Rounds 0-5 (all 115 bytes, identical):** All six rounds produced zero observations, zero anomalies, `pipeline_modified: false`. The structure is valid but the content is empty.

### Root Cause — The Macrophage Is Effectively Blind

The runner at `reference_runner.py` line 1802-1808 extracts verdicts via:

```python
all_verdicts = []
if hasattr(immune_result, "cell_verdicts"):
    for vid_list in immune_result.cell_verdicts.values():
        all_verdicts.extend(vid_list)
```

The Macrophage's `_patrol_observe` requires `MIN_FINDINGS_FOR_ANALYSIS = 3` verdicts with `.verdict` and `.confidence` attributes. The checkpoint shows extensive cell verdicts (B-cell, NK-cell, cytotoxic T-cell) across all rounds, yet the Macrophage received nothing usable. Either `immune_result.cell_verdicts` does not exist as an attribute (name mismatch), or the extracted objects lack the expected interface. This is the **highest priority fix**.

Additionally, three monitoring capabilities are implemented in `macrophage_cell.py` but **never wired** from the runner:
- `provenance` — Ouroboros source metadata monitoring
- `gate_stats` — PE gate pass/fail statistics
- `ouroboros_metrics` — Ouroboros activity monitoring

These are dead code paths in Exp 39. The Macrophage cannot detect source monoculture, immune deficiency, or Ouroboros pathologies without them.

SELF_CHECK mode (persistent-anomaly detector, method-claim consistency) is also never activated — PATROL mode only.

---

## Combined Assessment

| System | Correct behaviour? | Producing useful output? | Priority fix |
|---|---|---|---|
| Ouroboros | Yes | R0 only (partial) | Query quality |
| Macrophage | Structurally yes | No (blind) | Verdict wiring |

### Fixes Needed (Priority Order)

1. **Macrophage verdict wiring (high).** Verify the attribute name on the immune response object, confirm extracted verdicts have `.verdict` and `.confidence` attributes, add a diagnostic log when the verdict list is empty. File: `bench/reference_runner.py` lines 1801-1813.

2. **Macrophage unwired parameters (medium).** Wire `provenance`, `gate_stats`, and `ouroboros_metrics` to `_shadow_macrophage.observe()`. Implementations exist in `bench/macrophage_cell.py` lines 183-196 but are never called.

3. **Ouroboros query quality (medium).** Extract actual finding descriptions instead of using internal IDs as search terms. File: `bench/ouroboros_cell.py`, `_target_to_query` method and `_select_targets` method.

4. **Ouroboros source rotation (low).** Alternate between allowed sources in `_build_queries`. File: `bench/ouroboros_cell.py` line 267.

### Not Bugs

- Ouroboros R1-R5 empty output (correct, no targets existed)
- The 13x file size ratio (data vs empty arrays)
- Macrophage `pipeline_modified: false` (advisory guarantee holds)

### Key Files

- `bench/ouroboros_cell.py`
- `bench/macrophage_cell.py`
- `bench/reference_runner.py` (lines 1752-1905)
