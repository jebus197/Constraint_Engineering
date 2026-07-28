# Exp 42 Falsifier-Mechanism Fix Campaign — Plan of Record

**2026-06-06 00:06 BST.** Branch `exp39-experimental`, baseline HEAD `5ae340b`.

## Objective

Every model produces parsable, runnable, **testable** falsifiers; no model unable to participate; no core objective compromised; no waffle in the operational directive. All work gated or in separate files; **core code path stays byte-identical until each fix is verified**; fixes enabled only on evidence.

## Issues (consolidated from the live run + analysis)

| ID | Issue | Evidence |
|----|-------|----------|
| I1 | Decomposed synthesis prompt forces the OLD prose falsifier format ("FALSIFICATION (FALSIFIER/ATTEMPT/RESULT)") | 4/5 models wrote prose → 0 testable → 14 HIL |
| I2 | ~~CC2 decomposed path drops its findings text~~ **CORRECTED (Phase 0 harness, 6 Jun): NOT text-loss.** CC2 wrote **zero** falsifiers; same root as I1 (prose-format steered 4 models to prose, CC2 to omitting it). Folds into the I1 fix. | runner received CC2's 13,436 chars intact (mchar==rchar); CC2 wrote 0 FALSIFIER labels |
| I3 | 80K hard floor over-conservative — overrides the per-model fingerprint | composer ~113K decomposed for all 5; 4 fingerprints allow ~418K |
| I4 | Fingerprint records max **non-error** prompt, not max **quality** prompt → over-states capability | 465K fingerprint let 369K through, quality crashed → blunt floor bolted on |
| I5 | Control flow is preemptive, not failure-triggered (founder's intent) | `should_decompose_v2` decomposes before the primary is tried |
| I6 | 43,667-char operational directive is ~half justification/narration + §2/prompt duplication | per-turn fixed tax; inflates payload, dilutes attention |

## The metric (encodes "no compromises")

Degradation in **any** dimension, for **any** model, rejects the fix. Computed per model, per arm, from saved round outputs:

- **M1 Format compliance** — % findings that parse (structured fields).
- **M2 Testable-falsifier rate** — % critical findings yielding a runnable falsifier the runner adjudicates (CONFIRMED/REFUTED, not format-HIL). *The project core.*
- **M3 Admissibility rate** — % findings surviving FFAFP (§15 bar: 60–85%).
- **M4 R_k** present and self-consistent.
- **M5 Alternatives** supplied (§18 requirement).
- **M6 Participation** — every model returns usable, non-empty output.

## Reversibility rails (non-negotiable)

1. Every core fix sits behind a config flag; flag OFF ⇒ byte-identical to `5ae340b`.
2. New infrastructure (metric harness, lean directive, test scripts) lives in NEW files — never edits the live path.
3. A fix is enabled in core ONLY after its test confirms it holds the metric.
4. The lean directive is a separate file selected by flag; the 43K original is never deleted.

## Phases

**Phase 0 — Metric harness (new code, no core touch). ✅ DONE 6 Jun.** `bench/eval/falsifier_metric.py`: given saved round outputs, compute M1–M6 per model. **Validated on the 14-HIL run** — baseline: all 5 models produced output, **0 pipeline loss** (`mchar==rchar`; corrected the earlier CC2 "text-loss" misdiagnosis), **M2 testable-falsifier = 0.00 for all 5** (the core failure), M1=1.0 (findings parse), M3/M4=1.0. Per-model falsifier picture: chatgpt/codex/deepseek/gemini = prose FALSIFIER, cc2 = no FALSIFIER. The harness caught a self-bug (read `text` not `response`) on first run — fixed before trusting it. ruff-clean.

**Phase 1 — The two clear bugs (gated, smoke-tested).**
- I1: decomposed synthesis prompt demands a runnable `FALSIFIER:` python block when `enable_tools` (override the prose triad). Gated on `enable_tools`.
- I2: `_decomposed_claude_cli` extracts the final synthesis text instead of returning empty when tools are on.
- Verify each with a focused smoke test scored by the metric harness; flag OFF ⇒ unchanged.

**Phase 2 — Directive ablation (lean directive, separate file).**
- Free static cuts: §2/prompt duplication + pure narration no instruction references → `cdsfl_operational_lean.md`.
- Ablation: full (43K) vs lean, same target, all 5 models, ≥2 runs, temp 0. Metric per model.
- Decision: lean ≈ full ⇒ adopt lean (flag-selected). Degradation ⇒ bisect to the load-bearing chunk, restore, re-test.

**Phase 3 — Both-ways decomposition test (floor/control-flow evidence).**
- With Phase 1 fixes + Phase 2 lean directive: each model at the composer payload, **whole (primary tooled) vs decomposed**. Metric per model per path. Read-only on core.
- Determines which models handle whole (fingerprint predicts the capable ones do) and whether the 80K floor + preemptive flow should change.

**Phase 4 — Apply verified fixes to core (gated, evidence-driven).**
- If capable models handle whole: failure-triggered control flow (gated) — try primary first, decompose on failure/empty; raise or per-model the floor per the evidence.
- Quality-aware fingerprint update (gated) if Phase 3 justifies it.
- All gated default-off; enabled only after the test confirms.

**Phase 5 — Confirmation run.** Re-run Exp 42 with all verified fixes ON. Pass = testable verdicts (CONFIRMED/REFUTED, not 14 HIL), every model participates, metric held vs baseline.

## Execution note (hour discipline)

Offline, no-API work (Phase 0 harness, Phase 1 fix code, Phase 2 static cuts) proceeds now. API-heavy verification + the Phase 2/3/5 live runs are queued for a monitored window (cy) — not fired unmonitored.

---

Written under CDSFL note standard v1.2 (14 May 2026).
