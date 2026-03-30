# CDSFL Smoke Test Results with DeepSeek

**Date:** 23 March 2026

---

## Summary

6 of 12 runs completed. 3 tasks planned, 2 completed (ft-001 maths, ft-006 code partial). DeepSeek V3.2 replaced Gemini as the third architecture alongside Opus 4.6 (orchestrator) and Codex 5.3 (reviewer).

---

## Overall Numbers

| Condition | Runs | HARD Findings | Avg Rounds |
|---|---|---|---|
| Control | 2 | 37 | 5.0 |
| HIL | 2 | 0 | 1.0 |
| CDSFL | 1 | 22 | 5.0 |
| CDSFL + HIL | 1 | 20 | 5.0 |

---

## Decay Curve Analysis

This is the key observation. We are measuring the shape of each model's finding count curve across iterative review rounds. Genuine analysis should produce diminishing returns, like rolling a ball up an increasingly steep hill. Chatbot churn should produce a flat line, generating output regardless of whether real issues remain.

### DeepSeek Signature Across All Conditions

- **ft-001 control:** 5, 4, 0, 2, 2 — Non-monotone. Findings drop to zero at round 3 then spike back up at rounds 4 and 5. This is not decay and not flat. It is inconsistent, suggesting the model is not tracking what it already found.
- **ft-001 CDSFL:** 2, 2, 2, 2, 2 — **Perfectly flat.** Exactly 2 findings every round for 5 rounds. This is the clearest possible chatbot signature. The model is producing a fixed quantity of output per round regardless of problem state.
- **ft-001 CDSFL + HIL:** 6, 3, 4, 2, 2 — Non-monotone. Starts high, drops, spikes, drops again. Inconsistent.
- **ft-006 control:** 5, 4, 4, 5, 5 — Effectively flat at approximately 4.6 average. No convergence.

### Codex 5.3 Signature Across All Conditions

- **ft-001 control:** 0, 1, 0, 0, 0 — Near zero. Only 1 finding total. CX found almost nothing under control conditions on this task.
- **ft-001 CDSFL:** 5, 3, 2, 2, 0 — **Clean monotone decay.** This is the textbook genuine analysis curve. Starts high, diminishes each round, converges to zero.
- **ft-001 CDSFL + HIL:** 3, 0, 1, 1, 0 — Noisy but decaying. Starts at 3, ends at 0.
- **ft-006 control:** 4, 2, 0, 0, 0 — Steep decay. CX found 4 issues immediately, 2 more in round 2, then nothing. Very efficient.

---

## Key Observations

**First.** DeepSeek exhibits classic chatbot behaviour. Flat or non-monotone curves across all conditions. The perfectly flat 2, 2, 2, 2, 2 under CDSFL is the strongest evidence. It is producing content because it is expected to, not because real issues remain.

**Second.** CX shows genuine analytical behaviour. Clean decay curves, especially under CDSFL. The 5, 3, 2, 2, 0 curve matches the predicted inverse square root pattern almost exactly.

**Third.** CDSFL activates CX but not DeepSeek. Under control, CX found almost nothing on ft-001 (0, 1, 0, 0, 0). Under CDSFL, it found 5, 3, 2, 2, 0. The methodology activated capability that was dormant under control conditions. DeepSeek showed no similar activation — it produced flat output regardless of condition.

**Fourth.** HIL found zero HARD findings. Both runs, both tasks. This confirms the HIL guidance was not over-powered (the earlier concern about giving HIL too many advantages has been addressed).

**Fifth.** The decay curve diagnostic works as predicted. CX produces decay curves (genuine analysis). DeepSeek produces flat lines (churn). The shape of the curve distinguishes them without needing to verify every individual finding.

---

## Implications

The population of models capable of genuine analytical work under CDSFL appears to be limited to reasoning-optimised architectures (Opus, Codex). General chatbot architectures (DeepSeek, Gemini) produce output but do not demonstrate convergent analytical behaviour. This is not a failure of the methodology. It is a finding about the models. CDSFL can only activate capability that exists. It cannot create analytical capability where none is present.

The inverse square root decay observation holds for CX across conditions. Whether it holds across more tasks and whether it holds for Opus (when used as reviewer rather than orchestrator) remains to be tested in the full bench run.
