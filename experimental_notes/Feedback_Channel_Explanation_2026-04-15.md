# Feedback Channel — Plain English Explanation

**Date:** 15 April 2026
**Companion to:** `Feedback_Channel_Phase10_2026-04-15.md` (technical summary)
**Audience:** anyone — no CDSFL background required

---

## The problem we solved

The CDSFL framework is designed to make large language models more reliable. It works by asking multiple models to analyse the same problem, then checking their answers against mathematical tools, looking for agreement across models, and flagging claims that do not survive scrutiny.

Every round of this process produces detailed per-finding judgment. The framework knows when a model's claim has been refuted by a mathematical tool. It knows when a finding fails structural quality checks. It knows when a new finding is really just a repeat of an old one in disguise. It knows when the model's self-reported confidence in a finding does not match the evidence.

**All of this information was being written to log files. The models themselves never saw any of it.**

This is the gap we spent today closing.

Why did this matter? Because the same refuted claim could be resubmitted, unchanged, in the next round. A finding that failed every structural quality check could be carried forward indefinitely. A model whose self-reported confidence disagreed with reality by a wide margin could simply persist in claiming certainty. The framework was measuring errors but doing nothing to correct them.

George's own framing, earlier in the day:

> Measurement is nice, it is a nice to have. But the entire point of this project was to make LLMs more reliable, more trustworthy, and more accurate. What is the point in measurement if we do not use it for anything productive, except for knowing when the models got things wrong?

---

## Four design principles

Four ideas shaped how we built the solution.

1. **Imperative, not advisory.** When the framework flags a finding, the model must address it. There is no opt-out based on the model's self-reported confidence. The directive text reads: *agree with the tool output or show it wrong with your own tool output.* Claims of certainty without receipts are not a permitted response.

2. **Live by default, not shadow first.** Some parts of this framework are built in shadow mode first — they observe and log but do not influence behaviour. The feedback channel is different. It is turned on by default in the framework's configuration. A toggle remains for controlled scientific ablation experiments, but the normal operating mode is live.

3. **No changes to the underlying mathematics.** The framework has a recursive equation, R_k(i), that tracks each finding's corroboration score across rounds. We did not touch that equation. We did not add new convergence thresholds. The feedback channel is pure plumbing — routing information that was already being computed into a place where it can affect model behaviour.

4. **Defensive under all conditions.** Feedback assembly must never crash the main experimental loop. Parser failure, missing finding ID, unreadable number, malformed model response — all yield an empty feedback dictionary, quiet debug log, and the round continues. Observability beats brittleness.

---

## What we built

One new Python module: `bench/dm/_feedback.py` — 533 lines, four distinct surfaces.

### 1. `FindingFeedback` dataclass

Captures all four kinds of signal the framework can flag about a single finding:

- finding ID
- which model originated it
- how severe the model said it was
- what verdict the verification pipeline returned (CONFIRMED / REJECTED / UNCERTAIN)
- refutations (tool name, verdict, evidence)
- admissibility failures (gate names)
- near-duplicates (prior ID, similarity score)
- R_k discrepancy (claimed vs aggregate)

### 2. `build_feedback_records()`

Takes the round's findings, the verification pipeline's results, the R_k validation output, the near-duplicate pairs from the NK-Cell, and the per-finding admissibility failure map. Produces a flat list of feedback records — one per flagged finding. Findings with zero flags do not appear. **Silence means clean.**

### 3. `build_feedback_sections()`

Takes the records and renders them into prompt text, one section per model. Only models with at least one flagged finding appear in the output. Caps output at 10 findings per model by default, with an 8,000-character per-model ceiling to prevent prompt bloat. Priority order: refutation > admissibility > near-duplicate > R_k, with severity as tiebreaker.

### 4. `parse_admissibility_block()`

Permissive parser. Accepts σ or `sigma`. Accepts PASS/FAIL in any case. Accepts colons, dashes, or equals signs as separators. Accepts `G-completeness`, `G_completeness`, or `G completeness`. Missing block returns all five gates as failed, signalling the model to supply one.

---

## How it plugs into the main loop

One file changed in the runner — `bench/reference_runner.py` — at three wiring points:

1. **Dispatch gets a feedback parameter.** The main dispatch function (`_dispatch_round_star`) gets an optional `feedback_sections` parameter. If supplied, it is prepended to each model's prompt before the regular instructions.

2. **New helper runs at round end.** `_build_feedback_for_next_round()` runs after the verification pipeline finishes. It assembles feedback records, builds per-model sections, and returns a dict of model_id → feedback_text. Wrapped in defensive error handling — any failure returns an empty dict and the round continues.

3. **Round-carry state variable.** `feedback_sections_for_next_round` carries the dict from round K to the start of round K+1. That is how round 2 ends up with prompt sections reading *"the schema has evaluated your round 1 findings and flagged the following…"*.

---

## The directive

Section 17 was added to `bench/directives/universal/cdsfl_operational.md` — ~90 lines of text that models themselves see.

It opens by framing the gap: *the schema signal was logged and discarded. That wastes the framework.*

It lists the action precedence:

> REFUTED by a tool > ADMISSIBILITY FAIL > NEAR-DUPLICATE > R_k INCONSISTENT

It states the resubmission rule: unchanged flagged findings are inadmissible. Dropped. No R_k reduction credit. No novelty credit. Parser waste.

It explains per-model routing, rendering boundaries (top-K, max-chars), and that disablement is for controlled scientific ablation only — not for convenience.

A table in `cdsfl_core_formal.md` was also expanded: the single "corroboration model" row became three rows, pointing to Stage 1 reference (geometric `C(n)`), Stage 5–6 operational (recursive `R_k(i)`), and the new Stage 6 feedback channel (per-finding records).

---

## Tests

39 new tests across 5 classes in `bench/tests/test_feedback_channel.py`.

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestPriorityAndAction` | 8 | Action paths, priority ordering (including the edge case where 5 failed admissibility gates outscore 1 refutation), severity tiebreak, R_k delta cap |
| `TestBuildFeedbackRecords` | 12 | Empty inputs, refutations producing records, CONFIRMED staying silent, unknown IDs not crashing, duplicates, R_k WARN/FAIL flagged (PASS/SKIP ignored), merge behaviour |
| `TestBuildFeedbackSections` | 8 | Empty records, header formatting, strict per-model routing, top-K with overflow, singular/plural grammar, max-chars enforcement, all signal types, evidence truncation at 400 chars |
| `TestParseAdmissibility` | 10 | Missing blocks, empty strings, all PASS, mixed, case insensitivity, σ/`sigma` variants, G-completeness variants, section terminator, missing-gate fallback, separator variants |
| `TestFullPipeline` | 1 | End-to-end smoke test on a representative multi-model round |

All 39 green on first real run. Full regression: **832/832 pass**.

---

## One defect caught late

The full regression caught one defect that local tests had missed. The framework has a policy engine (`bench/cdsfl_registry/engine.py`) that validates every config file against a schema. When we added the four new `[feedback_channel.*]` parameters to `universal.toml`, the schema registry had not been updated to know about them. The policy engine rejected the new parameters as unknown.

This was actually a good catch — the validator exists specifically to catch this kind of drift. Fix was adding four matching blocks to `bench/cdsfl_registry/schema.toml`, each declaring `type`, `default`, `constraint_class`, `min_layer`, and `description`. `test_policy_engine.py` went from 39/40 → 40/40. Full regression confirmed 832/832.

---

## One defect still outstanding

The save-state script (`scripts/cdsfl_sv.py`) has a quieter defect that surfaced during the commit. It only stages modifications to already-tracked files. New untracked files are silently excluded.

Our `sv` commit message referenced three new files (`_feedback.py`, `test_feedback_channel.py`, `Feedback_Channel_Phase10_2026-04-15.md`) — but none were actually in the commit. Caught after the push; a follow-up commit (`52391aa`) added them. The repository was in an inconsistent state for <1 minute.

A separate side-task is flagged to fix this. Proposed fix: detect untracked files in known project directories and auto-stage, with a validation step that every path named in the commit message appears in the staged diff before `git commit` is invoked. Close the defect class, not just the symptom.

---

## What this changes in practice

**Before.** A model produced a refuted finding in round 1. The framework recomputed R_k. The framework logged the refutation. The model continued, blissfully unaware. The same incorrect claim could appear across multiple rounds with no visible reason why.

**After.** A refuted finding in round 1 produces a round-2 prompt section that reads:

```
=== SCHEMA FEEDBACK ON YOUR ROUND 1 OUTPUT ===

The schema has evaluated your prior-round findings and flagged
the items below. You MUST address each flagged item in this round:

f1 (your severity 0.85, pipeline verdict: REJECTED) — action: RECALCULATE
  REFUTED by:
    sympy: counterexample x=3, claimed identity fails

=== END SCHEMA FEEDBACK ===
```

The model must either agree with the tool (withdraw or correct the finding) or produce counter-receipts showing the schema's tool output was wrong.

**The pathway to being wrong in a distinct new way remains open. The pathway to being wrong in the same old way is closed.**

---

## Summary

| Artefact | Size |
|----------|------|
| `bench/dm/_feedback.py` | 533 lines (new) |
| `cdsfl_operational.md` §17 | ~90 lines (new) |
| `cdsfl_core_formal.md` table | 1 row → 3 rows |
| `reference_runner.py` wiring | ~40 lines across 3 sites |
| `universal.toml` + `schema.toml` | 4 new parameters, registered both places |
| `test_feedback_channel.py` | 39 tests across 5 classes |
| Schema math changes | **zero** |
| Regression impact | **832/832 pass** |

The schema's measurement now reaches the model as imperative corrective feedback. The project's reliability goal is no longer capped by the model's willingness to read its own log files.

---

## References

- `bench/dm/_feedback.py` — core module
- `bench/directives/universal/cdsfl_operational.md` §17 — directive
- `bench/directives/universal/cdsfl_core_formal.md` — classification summary table
- `bench/cdsfl_registry/universal.toml` `[feedback_channel]` — config
- `bench/cdsfl_registry/schema.toml` `[feedback_channel.*]` — parameter registration
- `bench/reference_runner.py` — wiring (lines ~129, ~1575, ~1747, ~3807)
- `bench/tests/test_feedback_channel.py` — 39 tests
- `experimental_notes/Feedback_Channel_Phase10_2026-04-15.md` — technical summary (companion document)
- Commits: `f29d0e9` (sv) + `52391aa` (follow-up artefact commit)
