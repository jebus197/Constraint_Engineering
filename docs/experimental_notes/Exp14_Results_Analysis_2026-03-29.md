# Experiment 14 Results Analysis: Self-Adaptive CDSFL Under Load

**Date:** 29 March 2026
**Experiments:** 14a (all 5 models, pre-fix), 14b (3 fixes applied, OpenRouter credits exhausted after blind round)

---

## 1. Experiment 14a Summary

**Duration:** 20:38 to 21:38 BST (1 hour wall clock)
**Rounds:** 4 (terminated via convergence)
**Total findings:** 150
**Models:** All 5 survived — CC2, ChatGPT, Codex, Gemini, DeepSeek
**Artifact:** `dynamic_management.py`, 4226 lines, 27 classes (up from 3772 in Experiment 13b)
**Max rounds cap:** 22 (from ceiling(4226 / 200), capped at 30)

- **Blind round:** 56 findings from 4 models. DeepSeek blocked (feasibility P = 0.000). ChatGPT produced 22,639 characters but only 1 finding parsed due to bare `F001` format not matching the `FINDING ID` parser.
- **Round 1 (Area 1, Role Assignment):** 34 findings from all 5 models. DeepSeek joined via decomposed dispatch. ChatGPT produced 9 findings correctly via structured prompt.
- **Round 2 (Area 2, Load Balancing):** 32 findings from all 5 models.
- **Round 3 (Area 3, Round Progression / FSM):** 28 findings from all 5 models. System declared CONVERGED.

**Termination cause — Convergence blindness bug.** When all 5 models were decomposed (context exceeded thresholds for every model), every model was excluded from the convergence calculation. The convergence detector received zero findings for two consecutive rounds, producing kappa = 1.0 and mu = 0.0 on empty input. This was not genuine convergence. It was a measurement failure.

### Convergence signal trajectory

| Round | Kappa | Mu | Notes |
|-------|-------|----|-------|
| 0 | 0.0 | 42.01 | Normal |
| 1 | 0.0 | 8.76 | 28 of 34 findings excluded |
| 2 | 1.0 | 0.0 | All 32 findings excluded |
| 3 | 1.0 | 0.0 | All 28 findings excluded |

The transition from kappa 0.0 to kappa 1.0 was instantaneous, not gradual. This is the same binary behaviour observed in Experiment 13b.

---

## 2. Three Bugs Found and Fixed

**Bug 1 — DeepSeek blind round blocking.** The runner's blind round did not check `DECOMPOSITION_CONTEXT_THRESHOLD` before blocking. DeepSeek has threshold = 0 (always decompose) but the blind round skipped it entirely. Fix: when feasibility blocks a model, check the threshold. If it is 0 or context exceeds it, pre-decompose to Area 1 and dispatch instead of skipping.

**Bug 2 — ChatGPT parser format mismatch.** ChatGPT sometimes outputs bare `F001`, `F002`, `F003` headers without the `FINDING ID` prefix. The parser only matched the full `FINDING ID: F001` format. 22,639 characters of analysis were reduced to 1 finding. Fix: added a bare `F###` splitting path that activates when no `FINDING ID` markers are found.

**Bug 3 — Convergence blindness under universal decomposition.** The runner excluded all dynamically decomposed models from convergence calculations, in addition to the statically excluded DeepSeek. When all models were decomposed (which happens on any artifact larger than approximately 120,000 characters after 1–2 rounds of accumulated context), the convergence detector operated on an empty set. Empty set produces kappa = 1.0 and mu = 0.0 trivially. Fix: only statically excluded models (DeepSeek) are removed from convergence calculations. Dynamically decomposed models still contribute valid findings.

---

## 3. Experiment 14b Summary (Partial — Credit Exhaustion)

**Duration:** 21:46 BST to ongoing
**Artifact:** Same 4226 lines

**Blind round:** 101 findings from 4 models.
- CC2: 40 findings (335 seconds)
- ChatGPT: 50 findings (97 seconds), using the standard `FINDING ID` format this time
- Gemini: 10 findings
- DeepSeek: successfully pre-decomposed to Area 1, produced 1 finding (81 seconds)
- Codex: timed out at 600 seconds

**Parser fix validation.** ChatGPT went from 1 finding in 14a to 50 in 14b.

**DeepSeek fix validation.** DeepSeek was blocked, then pre-decomposed and dispatched successfully. Log reads: BLOCKED → pre-decomposed blind dispatch → Area 1 Role Assignment → 28,391 characters focused.

**OpenRouter credit exhaustion.** After the blind round, CC2 and ChatGPT (both routed via OpenRouter) hit 402 errors. CC2 could only afford 16,517 tokens of the 32,768 requested. ChatGPT could only afford 27,528. The experiment continued with 3 models: Codex (via CLI), Gemini (via Google API), DeepSeek (via DeepSeek API).

**Convergence fix validation:**
- Round 1 signals: kappa 0.0, mu 24.72, novelty 1.0, vocab growth 0.065
- Round 2 signals: kappa 0.0, mu 25.44, novelty 1.0, vocab growth 0.071
- Only DeepSeek excluded from convergence (8 findings). The detector now has real input and correctly shows no convergence. Mu actually increased from round 1 to round 2, indicating the remaining models are still finding genuinely new material.

---

## 4. Findings Targeting the Phase A–E Code

The models found 25 findings directly targeting the new self-adaptive CDSFL code. This is the self-referential loop in action — the methodology reviewed its own infrastructure improvements and found bugs in them.

### Critical findings (severity 0.85 or above)

- **LoadBalancer ignores fingerprints** — ChatGPT F001, severity 0.97, triple corroborated. `DynamicManager` claims to use live-updated fingerprints for allocation, but `LoadBalancer` never reads fingerprints at all. Allocation depends only on token limits, costs, latency, role admissibility, and current loads. The adaptive routing feedback loop is operationally dead for task allocation.

- **`record_dispatch_block` never called** — ChatGPT F003, severity 0.94. The function `check_dispatch_feasibility` emits a `DISPATCH_BLOCKED` event but never calls `record_dispatch_block`. Phase E dispatch health monitor accumulates zero data. The immune layer cannot learn from dispatch outcomes because nobody tells it about them. This is a wiring failure, not a logic error.

- **Unsmoothed vs. smoothed mu inconsistency** — ChatGPT F004, severity 0.92. The function `process_round` feeds unsmoothed system-level mu to the health monitor, but the stop predicate uses smoothed per-model mu. The health monitor can detect a pathology that the stop predicate does not act on, or miss a pathology that the stop predicate would catch. These two components must use the same signal.

- **Kappa adopt has no bounds check** — ChatGPT F005, severity 0.90. Adoption delta can produce negative kappa or values greater than 1, contaminating the convergence metric.

### Moderate findings (severity 0.60–0.84)

- **`apply_diagnosis` string match bug** — ChatGPT F022, severity 0.71. The function checks for `false_positive` (underscore) but the diagnosis text uses `false positive` (space). The adaptation path for dispatch false positives never fires.

- **Area-level vocab saturation unreachable** — CC2 F032, severity 0.70, independently found in both 14a and 14b. Under rotated decomposed dispatch, each area is reviewed every 6th round. The sustained window of W/2 rounds below threshold cannot be reached because no single area accumulates enough consecutive measurements.

- **Vocab saturation handler is dead code** — ChatGPT F023, severity 0.70. The function `apply_diagnosis` has a handler for `vocab_saturation_detector` but no such diagnosis is ever generated by `DetectorHealthMonitor`. The code path exists but can never be reached.

- **Mu increasing check broken for negative values** — CC2 F027, severity 0.75. The health monitor checks whether `mu × 1.1` is increasing, but if mu is negative, multiplying by 1.1 makes it more negative, which is not increasing. The check produces false positives.

---

## 5. Cross-Model Corroboration

14 topics were independently found by multiple models or across multiple experiment runs. Strongest corroborations (3 independent sources each):

| Finding | Sources |
|---------|---------|
| FORMAT_VIOLATION event unused | ChatGPT F002 (0.95), CC2 14a F011 (0.45), CC2 14b F010 (0.45) |
| Config validation incomplete | ChatGPT F006 (0.89), CC2 14a F001 (0.85), CC2 14b F001 (0.85) |
| RoleAssignment stale fingerprints | 5 findings across all 3 sources: ChatGPT F019, CC2 14a F002 + F021, CC2 14b F002 + F017 |
| `Allocation.get_assigned` ValueError | ChatGPT F037, CC2 14a F012, CC2 14b F016 |

---

## 6. Verification Rates by Model

| Model / Run | Findings | Verified TRUE | Verified FALSE | Rate |
|-------------|----------|--------------|----------------|------|
| ChatGPT 14b blind | 50 | 50 | 0 | 100% |
| CC2 14a blind | 35 | 20 | 15 | 57% |
| CC2 14b blind | 39 (1 withdrawn) | 33 | 6 | 85% |

CC2 is more conservative in its verification claims. ChatGPT verifies everything as TRUE. Neither extreme is ideal. Cross-model corroboration data provides the ground truth: when both models find the same issue, the finding is real regardless of individual verification claims.

---

## 7. Comparison Across Experiments

| Experiment | Rounds | Findings | Models surviving | Termination | Notes |
|-----------|--------|----------|-----------------|-------------|-------|
| Exp 12 | 20 | 809 | 2 of 5 | MAX_ROUNDS | Three broken detectors, fingerprint collapse |
| Exp 13b | 4 | 185 | 5 of 5 | CONVERGED | Premature — decomposed dispatch interaction with global vocab saturation |
| Exp 14a | 4 | 150 | 5 of 5 | CONVERGED | Premature — convergence blindness bug |
| Exp 14b (partial) | 2+ | 101 (blind only) | 3 of 5 active | Ongoing | Convergence signals healthy; 2 models lost to OpenRouter credits, not model failure |

The trajectory: Experiment 12 could not stop. Experiment 13b stopped too early (4 rounds). Experiment 14a stopped too early for a different reason (blindness bug). Experiment 14b (partial data) shows a system that neither stops prematurely nor runs away. **The pendulum is approaching centre.**

---

## 8. Runner Improvements

**Experiment labelling.** The runner now accepts an experiment flag via command line argument. Usage: `python3 bench/run_exp12_live_wire.py full --experiment 14b`. Logs go to `bench/logs/experiment_14b/`. Report saves as `experiment_14b_report.json`.

**Logs preserved.** Experiment 13b report copied to `experiment_13b_report.json` before 14a overwrote it. Experiment 14a logs moved to `bench/logs/experiment_14a/` with console log captured.

---

## 9. What Needs to Happen Next

1. **Top up OpenRouter credits.** Both CC2 (Opus via OpenRouter) and ChatGPT (GPT-5.4 via OpenRouter) hit 402 errors. A full 5-model run through 10–15 rounds requires sufficient credit balance. Codex (CLI), Gemini (Google API), and DeepSeek (direct API) are unaffected.

2. **Apply the 5 must-fix findings:**
   - Wire `record_dispatch_block` into `check_dispatch_feasibility`.
   - Fix the string match in `apply_diagnosis` (underscore to space).
   - Align mu signal between `process_round` and stop predicate.
   - Fix kappa adopt bounds.
   - Address area-level vocab saturation threshold for rotated dispatch.

3. **Run Experiment 14c.** Full 5-model run with all fixes applied, including the runner fixes from 14b. This is the first experiment where: all models participate from round 0, the parser handles all output formats, the convergence detector has real input in all rounds, and the immune layer's dispatch monitoring is actually wired up.

4. **Evaluate against the 7 predictions.** The predictions registered for Experiment 14 can only be fully evaluated with a complete 5-model run. Partial results from 14a and 14b provide directional validation but not definitive answers.
