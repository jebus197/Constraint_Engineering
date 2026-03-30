# CE Gemini Review — Round 4

**Date:** 2026-03-18T21:43:00+00:00
**Model:** Gemini (via gemini CLI v0.29.5, gemini-3-pro-preview)
**Input:** Pre-fix `run_benchmark.py` (908 lines) + current `run_phase2.py` (1005 lines)
**Context:** Final pass, asked to assess diminishing returns

Full unfiltered Gemini output below.

---

### 1. Dead Module Linkage (Integration Failure)

`run_phase2.py` is architecturally disconnected from the provided `run_benchmark.py`. It attempts to import seven critical symbols — `estimate_call_cost`, `run_adaptive`, `run_cross_model`, `run_placebo`, `AdaptiveThrottle`, `make_throttle`, and `PLACEBO_DIRECTIVES` — none of which exist in `run_benchmark.py`. This is not merely a missing feature but a complete system failure; the Phase 2 experiment runner will fail with an `ImportError` immediately upon execution.

---

### 2. Recursive Label Truncation (Parser Fragility)

The `_extract_section` regex in `run_benchmark.py` uses a positive lookahead to find the start of the next section to determine where the current one ends.

```python
stop_labels = [re.escape(item) for item in SECTION_LABELS if item != label]
stop_pattern = rf"(?=\n(?:{'|'.join(stop_labels)}):\s*(?:\n|$)|\Z)"
```

If a model generates a `REVISED_ANSWER` that happens to contain one of these labels (e.g., a code comment saying `// This fixes the bug found in INITIAL_ANSWER`), the regex will prematurely truncate the answer at that point. This leads to silent data loss where only the first half of a model's response is recorded and evaluated.

---

### 3. Atomic Loop Escape (Cost Cap Bypass)

The cost cap logic in `run_phase2.py` checks the budget before calling `run_adaptive`. However, `run_adaptive` is an "atomic" operation from the perspective of the main loop, executing up to `max_passes` (default 5). With expensive reasoning models or high-token "thinking" blocks, a single task can consume the entire remaining budget — and potentially hundreds of dollars beyond it — in its internal iterative loop before the ledger is updated and the cap is checked again.

---

### 4. Draft Pollution Fallback in Extended Mode

In `run_benchmark.py`, the `run_extended` function sets the draft for the next pass using:

```python
current_draft = extracted_revision or response
```

If the model fails to include the `REVISED_ANSWER` tag (a common occurrence with lower-tier models or under pressure), the code falls back to using the entire raw response. This includes the model's internal reasoning, the `ISSUES_FOUND` meta-commentary, and conversational filler. When this "polluted" draft is passed to the final "isolated" adversarial pass, the reviewer is no longer blind; they are anchored by the previous model's self-criticism, defeating the core methodological goal of context isolation.

---

## Recommendation

These findings represent a significant risk to the integrity of the benchmark data and the safety of the API spend. Diminishing returns have **not** been reached, as the core execution path for Phase 2 remains fundamentally broken due to the import desynchronization.
