# Experiment 13: Session Plan and Progress Report

**Date:** 29 March 2026, 09:35 BST

This session completed the full write-up of Experiment 12, rewrote the README, fixed the shorthand conflict, ran Experiment 13a (confer round on fixes), implemented all approved modifications, and launched Experiment 13b (live orchestration with all fixes active).

---

## 1. Shorthand Fix

The letter `t` was assigned to two different functions: continue and TTS export. This has been resolved. The shorthand `cy` now means continue. The shorthand `t` means TTS export only. Updated in `CLAUDE.md`, `MEMORY.md`, and `ONBOARDING.md`.

---

## 2. Experiment 12 Documentation

Experiment 12 has been fully written up across three documents.

**`EXPERIMENTAL_RESULTS.md`** now contains the complete Experiment 12 entry. This includes the design (20 rounds, 5 models, 3181-line artifact), model performance table, three broken detector analysis (kappa, mu, stop predicate), fingerprint EMA collapse with mathematical explanation, statistical analysis (8 trend tests, only ChatGPT severity significant at p = 0.006), vocabulary novelty trajectory, model attrition timeline, immune response layer, all seven mid-experiment and post-experiment commits, and eight formalised lessons.

**`FOUNDERS_NOTES.md`** now contains two new sections. "The Live Wire" describes the experiment as experienced — watching all three detectors fail in real time, the adaptive response, and the insight that convergence detection is harder than the analytical process it monitors. "The Biodiversity Hypothesis After 809 Findings" reassesses the diversity claim, concluding that diversity value is real but fragile, and that preserving it through an experiment is an engineering problem the dynamic management layer must solve.

---

## 3. README Rewrite

The README has been extended from 216 lines (covering up to 27 March) to approximately 290 lines (covering up to 29 March). New sections cover four cognitive modes and the dynamic management layer, the live orchestration (Experiment 12), and the configured synthetic domain expert thesis. The prose register matches the ChatGPT assessment quality benchmark: measured, substantive, evidence-first. The version line now reads: **CDSFL v1.1, 29 March 2026, 12 experiments, 5 models, approximately 3400 lines of management infrastructure, 177 tests.**

---

## 4. Experiment 13a: Confer Round

CC2 (Opus 4.6) reviewed all 8 post-Experiment 12 fixes under full CDSFL with structured verdicts.

### Results by fix

- **Fix 1 — Vocabulary saturation stop signal.** CC2 verdict: MODIFY (SOFT, confidence 0.82). The proportional growth rate is a monotonically decreasing function of cumulative vocabulary size. This means the signal fires more easily in later rounds by design, which is acceptable for 10–20 round experiments. For longer experiments, an absolute count floor should be considered. Applied: documentation added.

- **Fix 2 — Windowed fingerprint.** CC2 verdict: APPROVE (HARD, confidence 0.90). Edge cases verified. Python slice semantics handle fewer than W entries correctly. Zero finding observations produce neutral D decay. W = 5 is responsive enough while smoothing noise.

- **Fix 3 — Model restart logic.** CC2 verdict: MODIFY (HARD, confidence 0.85). The restart guard used a round-level boolean (`use_decomposition`) that could suppress restarts for models that had never been decomposed, if another model in the same round was already decomposed. Applied: changed to use the per-model `decomposed_models` set.

- **Fix 4 — Adaptive decomposition thresholds.** CC2 verdict: MODIFY (SOFT, confidence 0.78). Thresholds should be derived from `ModelSpec.L` with a safety margin, not hardcoded. Deferred — the current values work for Experiment 13b.

- **Fix 5 — Max rounds scaling.** CC2 verdict: MODIFY (SOFT, confidence 0.80). A 60,000-line artifact would give 300 rounds without a ceiling. Applied: added ceiling of 30 rounds. Documented as budget cap, not convergence criterion.

- **Fix 6 — Fingerprint blending on restart.** CC2 verdict: APPROVE (SOFT, confidence 0.85). The 50/50 blend is a reasonable Bayesian prior. Clearing windowed history is essential and correctly implemented.

- **Fix 7 — Per-model mu computation.** CC2 verdict: APPROVE (HARD, confidence 0.88). Correct structural fix for mu distortion. Max aggregation (continue while any model delivers value) is the right conservative bias. Implemented in `dynamic_management.py` and wired into `DynamicManager.process_round`.

- **Fix 8 — Embedding-based similarity.** CC2 verdict: APPROVE (SOFT, confidence 0.85). Correctly scoped as long-term. Fixes 1, 2, and 7 provide sufficient convergence detection without kappa for current experiments.

**Summary:** 3 modifications applied (Fixes 1, 3, 5). 4 approved as-is (Fixes 2, 6, 7, 8). 1 deferred (Fix 4). No rejections. All fixes coherent with no contradictions between them.

---

## 5. Experiment 13b: Live Orchestration

Launched at 09:34 BST. Running in background. The artifact is now 3772 lines (including all fixes). Max rounds = max(10, min(ceiling(3772 / 200), 30)) = **19**.

### Seven testable predictions

1. Vocabulary saturation fires before round 19.
2. Fingerprints do not collapse after 15 or more rounds.
3. Gemini survives past round 5 (tau raised to 350 seconds).
4. Model restarts extend useful life with genuinely different findings.
5. Kappa moves off zero (improved similarity function).
6. Mu trends downward (per-model computation).
7. Total rounds less than 19 (self-termination).

---

## 6. Commit Chain

| Hash | Description |
|------|-------------|
| `35471eb` | Experiment 12 write-up + README update + shorthand fix |
| `cd023d9` | Experiment 13a confer, apply 3 CC2 modifications |
| `c91d63c` | Implement per-model mu computation (Fix 7) |
| `f5b457e` | Wire per-model mu into `DynamicManager.process_round` |

HEAD is `f5b457e`. 177 tests passing. All pushed to origin.

---

## 7. Remaining Work

- Monitor Experiment 13b to completion and analyse results against the 7 predictions.
- Resolve deferred math model items (A-D1 through A-D5) from the meta-test confer plan.
- Outreach emails to industry specialists.
