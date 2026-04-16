# Feedback Channel — Closing the Measurement-to-Correction Loop

**Date:** 15 April 2026 (evening session)
**Branch:** `exp39-experimental`
**Scope:** Phase 10 — new `bench/dm/_feedback.py` module, `cdsfl_operational.md` §17 (the Feedback Channel directive), runner wiring, 39 new tests.

---

## Context

The CDSFL (Constraint-Driven Synthesis and Falsification) schema performs rich per-finding calculation every round:

- **Cytotoxic T cells** run tests against claimed code defects.
- **B cells** run specialist verification (sympy, z3, statsmodels, scipy, pint, crosshair, rdkit, biopython, networkx, and twelve others).
- **NK cells** detect near-duplicates.
- **Helper T cells** aggregate verdicts.
- **Regulatory T cells** flag autoimmune over-rejection.
- An R_k validator recomputes each finding's self-assessed corroboration against the aggregate derivation. R_k(i) is the iterative residual-risk self-assessment after round i.
- The FFAFP (Find, Follow, Analyse, Fix, P-pass) admissibility gate classifies each finding against five structural requirements (S_min, G-completeness, d_tool, σ_measured, q_retest).

All of that machinery produced detailed per-finding judgment, round after round, and wrote it to the logs. **Models never saw any of it.** The same refuted claim could be resubmitted unchanged in the next round; a finding with zero admissibility gates passing could carry forward indefinitely; a finding whose self-reported R_k disagreed by 0.6 with the aggregate would simply persist. The schema knew, the schema logged, the models continued regardless.

This is the gap this session was dedicated to closing.

---

## Design Principles

Four principles shaped the implementation:

1. **Imperative, not advisory.** Flagged findings MUST be addressed. There is no self-reported-confidence escape hatch. Directive wording: *"agree with the tool output or show it wrong with your own tool output."* Claims of certainty without receipts are not a permitted response.

2. **Live-default, not shadow-first.** The founder's framing was unambiguous — measurement for its own sake is wasted. The channel is enabled by default in `universal.toml`. A toggle remains for controlled ablation experiments, but the normal operating mode is live.

3. **No schema math changes.** No new convergence thresholds. No new R_k terms. The feedback channel is pure plumbing, routing data that was already being computed into a place where it can affect model behaviour.

4. **Defensive under all conditions.** Feedback assembly must never crash the main loop. A parse failure, a missing finding_id, an unparseable float, a malformed model response — all yield an empty feedback dict, logged at debug level, with the round continuing as before.

---

## Architecture

### New module: `bench/dm/_feedback.py` (533 lines, four surfaces)

- **`FindingFeedback` dataclass** — captures per-finding schema judgment across all four signal sources.

  ```
  finding_id            : str
  model_origin          : str
  severity_claimed      : float
  final_verdict         : str  (CONFIRMED | REJECTED | UNCERTAIN)
  refutations           : List[(tool, verdict, evidence)]
  admissibility_failures: List[gate_name]
  duplicates            : List[(prior_id, cosine)]
  rk_discrepancy        : Optional[(claimed, aggregate)]
  ```

- **`build_feedback_records()`** — takes round findings, `ImmuneResponse`, R_k validation output, NK-Cell duplicate pairs, and per-finding admissibility failure map. Produces a flat list of `FindingFeedback` records, one per flagged finding. Findings with zero flags do not appear.

- **`build_feedback_sections()`** — renders per-model prompt sections. Returns `Dict[model_id, str]`. Only models with at least one flagged finding appear. Top-K cap defaults to 10 items per model. Max-chars-per-model cap defaults to 8000. Priority: refutation > admissibility > duplicate > R_k, with severity as tiebreak.

- **`parse_admissibility_block()`** — permissive regex parser. Accepts σ or `sigma`. Case-insensitive PASS/FAIL. Colon, dash, or equals separator. `G-completeness`, `G_completeness`, or `G completeness` all accepted. Missing block returns all 5 gates as failed, signalling the model to supply it.

### Integration: `bench/reference_runner.py` (three wiring points)

1. **`_dispatch_round_star`** gets an optional `feedback_sections` parameter. The internal `_make_prompt(mc_label)` closure prepends the per-model feedback section to the base prompt before returning.

2. **New helper `_build_feedback_for_next_round()`** runs at the end of each round, after `immune_result` is available (line ~3808). Extracts duplicate pairs from `TriagedFinding`, parses admissibility per finding, calls `build_feedback_records` + `build_feedback_sections`, returns per-model dict. Wrapped in defensive `try/except` that returns empty dict on any failure.

3. **`feedback_sections_for_next_round`** dict carries output from round K to dispatch of round K+1. Declared before the main loop, populated at end of each round, consumed at start of the next.

### Config knobs

`RunnerConfig` gets three new fields, surfaced in `universal.toml`:

```toml
[feedback_channel]
enabled = true                 # live default
top_k = 10                     # max detailed flags per model per round
max_chars_per_model = 8000     # hard cap on rendered section size
mode = "imperative"            # imperative = MUST address
```

---

## Directive

**`cdsfl_operational.md` §17 (new, ~90 lines).** Opens with the gap framing ("the schema signal was logged and discarded, that wastes the framework"). Lists action precedence: REFUTED > ADMISSIBILITY FAIL > NEAR-DUPLICATE > R_k INCONSISTENT. Resubmission rule: unchanged flagged findings are inadmissible, dropped, no R_k reduction credit, no registry novelty credit. Per-model routing explained. Refutation of a schema tool is permitted **with receipts**. Rendering boundary (top-K). Disablement note — controlled ablation only, not convenience.

**`cdsfl_core_formal.md` classification summary table expanded.** Single "Corroboration model" row → three rows:
- Stage 1 reference: `C(n) = 1 − (1 − p)^n` (geometric)
- Stage 5–6 operational: recursive `R_k(i)` with η·d·p, S_k (the severity/stringency tristate gate), ν_eff, η_combined via ν_k (the literature-novelty score) & c_ext
- Stage 6 (the current mathematical framework) feedback channel: per-finding feedback records

Each row points to the relevant operational section and source file.

---

## Tests — `bench/tests/test_feedback_channel.py` (39 tests, 5 classes)

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestPriorityAndAction` | 8 | Action ordering (4 paths + NONE), priority invariants with edge case (5 admissibility gates > refutation intentionally), severity tiebreak, R_k delta cap at 1.0 |
| `TestBuildFeedbackRecords` | 12 | Empty inputs, refutation produces record, CONFIRMED is silent, unknown finding_id does not crash, admissibility attachment paths, empty list silent, duplicates, R_k WARN/FAIL flagged, None floats, full merge |
| `TestBuildFeedbackSections` | 8 | Empty records, header with round number, strict per-model routing, top-K truncation with overflow notice, singular/plural overflow grammar, max-chars cap enforcement, all signal types rendered, evidence truncation at 400 chars |
| `TestParseAdmissibility` | 10 | Missing block, empty string, all PASS, mixed, case-insensitive, σ/sigma variants, G-completeness variants, section terminator, missing gates count as failed, separator variants |
| `TestFullPipeline` | 1 | End-to-end smoke test on representative multi-model round |

All 39 green. Full regression green (832 total, was 793).

---

## Operational Consequence

With the channel live, a refuted finding in round K produces a round K+1 prompt section reading:

```
=== SCHEMA FEEDBACK ON YOUR ROUND 2 OUTPUT ===

The schema has evaluated your prior-round findings and flagged
the items below. You MUST address each flagged item in this round:
  ...

f1 (your severity 0.85, pipeline verdict: REJECTED) — action: RECALCULATE
  REFUTED by:
    sympy: counterexample x=3, claimed identity fails

=== END SCHEMA FEEDBACK ===
```

The model must either agree with the tool (withdraw or correct the finding) or produce counter-receipts showing the schema's tool output was wrong. Self-reported confidence is not accepted.

Previously the same finding would be computed against R_k, marked as a known flaw, and the model would be free to resubmit it next round unchanged. Now resubmitting it unchanged is explicitly inadmissible under §17. The pathway to being wrong in a distinct new way remains open; the pathway to being wrong in the same old way is closed.

---

## Summary

| Artefact | Size |
|----------|------|
| `bench/dm/_feedback.py` | 533 lines (new) |
| `cdsfl_operational.md` §17 | ~90 lines (new) |
| `cdsfl_core_formal.md` table | 1 row → 3 rows |
| `reference_runner.py` wiring | ~40 lines across 3 sites |
| `universal.toml` config | 1 new section |
| `test_feedback_channel.py` | 39 tests, 5 classes (new) |

Schema math changes: **zero.** Regression impact: **zero.** Model-facing behaviour change: **measurement now feeds correction.**

The project's reliability goal is no longer capped by the model's willingness to read its own log files.

---

## References

- `bench/directives/universal/cdsfl_operational.md` §17
- `bench/directives/universal/cdsfl_core_formal.md` (Classification Summary table)
- `bench/cdsfl_registry/universal.toml` `[feedback_channel]`
- `bench/dm/_feedback.py`
- `bench/reference_runner.py` (lines ~129, ~1575, ~1747, ~3807)
- `bench/tests/test_feedback_channel.py`
