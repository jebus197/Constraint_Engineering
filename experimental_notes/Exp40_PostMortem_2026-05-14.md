# Experiment 40 Post-Mortem — §17 Feedback Channel Live Exercise

2026-05-14 06:29 BST

## Summary

Experiment 40 dispatched against `bench/dm/_feedback.py` (the §17 feedback-channel module) under reference runner v2 with the rotated 5-model panel (Opus 4.7, GPT-5.5 ×2, Gemini 3.1 Pro Preview via OpenRouter, DeepSeek V4 Pro). The experiment ran 10 rounds (rounds 0 through 9), terminated at the extension-cap boundary without declaring convergence, and produced 207 findings reducing to 146 canonical entries (29% duplicate rate). Cumulative wall-clock 7,249 seconds (≈2 hours) across an initial run (rounds 0-2) and a resumed run (rounds 3-9) with the wall-clock cap raised from 3,600s to 7,200s per founder authorisation when convergence appeared close at the Round-2 review checkpoint.

The headline finding is methodological rather than substantive about the target file: **the project's primary convergence metric (gamma) disagrees with the project's reconciliation pipeline about whether the panel has saturated.** Gamma peaked at 0.297 in Round 3, then declined for six consecutive rounds to 0.143 in Round 9, never crossing the 0.30 convergence threshold. Meanwhile, the reconciliation pipeline (via the autoimmune detector) fired on all five panel models in Round 9, flagging 100% of each model's round-9 findings as duplicates of canonical entries already in the registry. The reconciliation behaviour is unambiguous saturation; gamma reports the opposite. The two metrics are computed against different novelty signals — gamma against pre-reconciliation novel count, reconciliation against canonical-entry uniqueness — and the gap explains why this experiment ran to extension-cap exhaustion when it had effectively saturated by Round 6.

## Launch sequence (three latent bugs, three fixes)

The first three launch attempts each surfaced a latent bug in `bench/launch_exp40.py` that pre-launch panel review had not caught because no panel reviewer was directed to execute the launcher end-to-end against the runner's actual entry signature. Each bug landed as a separate small commit:

| Attempt | Time (BST) | Failure | Fix | Commit |
|---|---|---|---|---|
| 1 | 03:00:01 | `TypeError: run_experiment() missing 1 required positional argument: 'cfg'` after Gate C preflight | Launcher called `run_experiment(runner_cfg, exp_cfg_dict)` with two args; runner signature is `run_experiment(exp_config: ExperimentConfig, cdsfl_text: str, cfg: RunnerConfig)`. Fixed: import `load_default_config`, load `cdsfl_text`, call with correct order. | `22adc0b` |
| 2 | 03:00:01 | `IsADirectoryError: [Errno 21] Is a directory: '/Users/georgejackson/Developer_Projects/Constraint_Engineering'` after Gate C preflight | RunnerConfig was missing `test_article`, `context_files`, `domain` mappings from the JSON config. Empty `test_article` resolved to repo root. | `2fdecbd` |
| 3 | 03:02:22 | `RuntimeError: OPENROUTER_API_KEY not set` from `call_openrouter`, cascading to all four post-rotation OpenRouter routes | Launcher never loaded `.env`. The confer scripts all do; the launcher had never been exercised end-to-end without pre-sourced env. | `ae1de45` |

The fourth attempt at 03:05:50 launched cleanly and ran. The cumulative diagnostic cost: ~10 minutes of agent time across three iterations.

**Class summary for the post-mortem record.** Pre-launch panel review (three rounds of compelled convergence, 56 regression tests including 6 around the launcher's Gate C path) correctly identified what to look for in the running runner code, but did not direct any reviewer to exercise the launcher's full call chain against the runner's actual entry path. The class of failure is "untested integration glue", and each instance fired in the setup phase before any panel work was wasted on a half-broken launcher — which is the right place for these bugs to fail.

## Per-round behaviour

The experiment ran in two segments. The initial run (commit `ae1de45` launched at 03:05:50) executed rounds 0-2 before the original 60-minute wall-clock cap fired at 04:25:52. Resumed with `wall_clock_cap_s` raised from 3,600 to 7,200 at 04:27 via `python3 bench/launch_exp40.py --resume`. Resume executed rounds 3-9, terminating at the extension-cap boundary at 06:27:56.

| Round | Type | Findings (raw) | Duration | gamma | novel CRITICAL | Notable signal |
|---|---|---|---|---|---|---|
| 0 | blind | 15 | 510 s | 0.000 | — | Setup baseline |
| 1 | adaptive | 15 | 1,981 s | 0.000 | 7 | DeepSeek 33-min synthesis (1,981s, 21,904 chars) — only model to push wall-clock |
| 2 | adaptive | 16 | 884 s | 0.256 | 5 | First gamma climb |
| 3 | adaptive | 9 | ? | 0.297 | 1 | **Gamma peak**. Gate fail: `open_ch=18`. γ-alt countdown begins. |
| 4 | adaptive | 18 | ? | 0.289 | 1 | Finding count ticks back up; gamma drifts down |
| 5 | adaptive | 9 | ? | 0.284 | 1 | Steady-state |
| 6 | adaptive | 13 | ? | 0.275 | 4 | Autoimmune fires on Gemini (8/8 rejected); §17 feedback flags all 5 models for Round 7; Stage 6 calibrator non-fatal bug |
| 7 | adaptive | 14 | ? | 0.261 | 1 | HIL flag raised on Gemini (5 consecutive ITC interventions, latest TRANSIENT_FAILURE — 0-char synthesis); autoimmune on CC2 (4/4) and DeepSeek (6/6) |
| 8 | adaptive | 26 | ? | 0.232 | **0** | **First zero-novel-CRITICAL round.** Autoimmune fires on CC2/ChatGPT/Gemini/DeepSeek (4 of 5 models, 25 findings 100%-rejected). Massive MERGE DEFERRED on C0020 with 21 target disagreements. |
| 9 | adaptive | 72 | 353 s | 0.143 | 1 | **Total saturation.** Autoimmune fires on ALL 5 models (72 findings rejected). Gamma drops by 0.089 — the largest single-round decline. γ-alt broken by 1 novel CRITICAL. |

**Gamma history (canonical from report.json):** `[0.0, 0.0, 0.256, 0.2967, 0.2891, 0.2838, 0.2746, 0.2614, 0.2321, 0.1433]`.

## HIL flags raised — 12 events across four models

The runner's ITC (Intelligent Task Controller) issued 12 HIL review flags. CC2 was the only panel member NOT flagged.

| Model | Round | Classification | Consecutive ITC interventions |
|---|---|---|---|
| Codex | 3 | CAPABILITY_MISMATCH | 3 |
| Codex | 4 | CAPABILITY_MISMATCH | 4 |
| Gemini | 5 | DEGRADATION | 3 |
| DeepSeek | 6 | DEGRADATION | 3 |
| ChatGPT | 6 | DEGRADATION | 3 |
| Gemini | 6 | DEGRADATION | 4 |
| ChatGPT | 7 | DEGRADATION | 4 |
| Gemini | 7 | TRANSIENT_FAILURE | 5 |
| ChatGPT | 8 | DEGRADATION | 5 |
| DeepSeek | 9 | DEGRADATION | 4 |
| ChatGPT | 9 | DEGRADATION | 6 |
| Gemini | 9 | DEGRADATION | 6 |

Codex's CAPABILITY_MISMATCH flags in rounds 3-4 are distinct from the other models' DEGRADATION pattern and warrant investigation. Gemini's TRANSIENT_FAILURE in Round 7 corresponds to the 0-character synthesis returned that round (its second; the first was Round 3, 0 chars after 353s).

## Convergence behaviour and the gamma-versus-reconciliation gap

The experiment never declared convergence. Two paths could have:

1. **Primary gate.** `gamma >= 0.30 AND open_ch <= 5 AND contested manageable`. Gamma peaked at 0.297, never crossed 0.30. `open_ch` peaked at 18 in Round 3 (vs gate threshold 5), dropped to 14 by Round 5, and was no longer flagged in the failure summary by Round 7 (suggesting it cleared below 5). `contested` ranged from 1 to 5 across rounds.

2. **γ-alt path.** `gamma >= 0.30 OR 3 consecutive rounds with 0 novel CRITICAL`. The novel-CRITICAL sequence across rounds 1-9 was `[7, 5, 1, 1, 1, 4, 1, 0, 1]` — never three consecutive zeros. Round 8 produced the only zero.

Meanwhile, the reconciliation pipeline tells a different story. The autoimmune detector (a per-model 100%-rejection-rate flag) fired progressively:

- Round 6: Gemini only (8/8 = 100% rejected).
- Round 7: CC2 (4/4) and DeepSeek (6/6).
- Round 8: CC2 (3/3), ChatGPT (5/5), Gemini (9/9), DeepSeek (8/8) — 4 of 5 models.
- Round 9: ALL FIVE models (CC2 11/11, ChatGPT 12/12, Codex 5/5, Gemini 10/10, DeepSeek 34/34) — 72 findings rejected.

In each case the autoimmune override reviewed the rejections and **judged them legitimate** (not bias-driven). The reconciliation pipeline correctly identified late-round findings as duplicates of canonical entries already in the registry. By Round 9 the panel had nothing genuinely new to contribute.

**The architectural gap.** Gamma is computed against the runner's pre-reconciliation novelty count. The novelty count rose in Round 9 (the runner extracted 58 raw "novel" findings) even as reconciliation rejected all 72 as duplicates of canonical entries. Gamma fell because the pre-reconciliation novelty rate stayed high; reconciliation said the same findings were saturated. They are measuring different things at different layers of the pipeline.

This is the load-bearing post-mortem finding for the rest of the arc: **gamma should be computed against post-reconciliation novelty, not pre-reconciliation novelty**, otherwise every subsequent experiment will run to extension-cap exhaustion when the panel has effectively saturated.

## G7 (MERGE deadlock) trigger evidence

The §6b trigger specification for G7 said the first appearance of multi-specialist MERGE deadlock was likely at Experiment 49 (cross-domain synthesis), with Experiment 44 retained as an early-observation checkpoint. **Experiment 40 produced abundant G7 evidence** — substantially earlier than expected.

MERGE DEFERRED events observed across rounds (incomplete enumeration from log capture):

- Round 5 post-processing: `C0016` (3/5 disagreement targets), `C0023` (2/5).
- Round 7 post-processing: `C0030`, `C0032`.
- Round 8 post-processing: `C0030` [2/5], `C0032` [3/5], `C0020` with **21 target disagreements**, `C0035` with 9 target disagreements.
- Round 9 post-processing: `C0008` with **17 target disagreements** (the parser-bug canonical entry itself), `C0020` repeated [2/5], `C0032` [4/5], `C0035` [2/5] with 16 disagreements.

Three of these merge conflicts (C0020, C0035, C0032) recurred across multiple rounds, suggesting the runner repeatedly attempts the auto-merge, defers, and re-attempts on the next round. The deferral notation `[N/5]` is unclear without inspecting source — likely "N out of 5 models cast a vote that doesn't match the merge target" or similar.

**Post-mortem implication for G7 arbitration-rule design.** The §6b spec named multi-tool pairings (pytest + AST + inspect + trace-log parsing) and a minimum evidence threshold of "minimum three observed patterns" before designing the arbitration rule. Experiment 40 has produced far more than three patterns. The arbitration-rule design work that §6b deferred until Exp 49 can begin now from Experiment 40's evidence base.

## Reflexive finding: the panel found the runner's own parser bug

Across rounds 5 through 9, multiple models independently produced findings about a defect in the runner's `FINDING_ID` parser regex. Four of the five panel members (CC2, ChatGPT, Codex, DeepSeek) generated findings about it across the experiment. Sample finding-content (with the runner's parser-runaway artifact preserved in the finding_id slot, illustrating the exact bug being reported):

- `ChatGPT_` is not matched by the terminator regex. The supplied artifact still has: ...`
- `Codex_` does not match `^\s*FINDING\s*:` because `_ID` appears before the colon. This confirms the parser can fail to terminate the ADMISSIBILITY block at the next finding boundary.`
- `DeepSeek_` will not terminate the ADMISSIBILITY section, causing the parser to consume subsequent finding text. The fix must add `FINDING_ID` to the alternation.`
- `CC2_in-terminator-regex issue is well-established. The confirmed C0008/C0025 fixes address the broader terminator issue, but `FINDING_ID` specifically should be added.`

The reconciliation pipeline correctly merged all four convergent findings into canonical entry **C0008** (with C0025 as a related entry). The system identified its own infrastructure bug, the panel converged on the root cause and the fix, and reconciliation produced a clean canonical claim — all while the bug was actively manifesting in the parser's handling of these very findings. This is exactly the reflexive behaviour the project's design intends.

**Action item:** apply the fix proposed by the panel. Add `FINDING_ID` to the terminator regex alternation. Verify against the existing test_feedback_channel.py regression coverage; add a regression case if not already present. Re-run a brief targeted dispatch to confirm the parser-runaway pattern no longer appears in finding-id capture.

## Per-model behaviour observations

**CC2 (Claude Opus 4.7 via Max subscription).** Most stable contributor. Zero HIL flags. R_k validation: 1 FAIL per round consistently (one finding per round where CC2's stated R_k disagreed with the recomputed value). Output sizes ranged 6,316-12,113 chars per round — substantive in every round. The reference model for this panel composition.

**Codex (GPT-5.5 via OpenRouter).** Two HIL flags in rounds 3-4 (CAPABILITY_MISMATCH classification). Variable output (2,749-12,182 chars). R_k validation produced one large-delta failure in Round 3 (model=0.446, recomputed=1.000, delta=0.554). Worth investigating the CAPABILITY_MISMATCH cause specifically — the classification suggests the runner detected something distinct from the DEGRADATION pattern the other models hit.

**ChatGPT (GPT-5.5 via OpenRouter).** Four HIL flags rounds 6-9 (DEGRADATION). Output 4,252-15,048 chars. Notably the two `openai/gpt-5.5` slots (Codex and ChatGPT) produced markedly different output sizes despite using the same model identifier — Codex saturated faster.

**Gemini (3.1 Pro Preview via OpenRouter).** Four HIL flags rounds 5-9, including one TRANSIENT_FAILURE (round 7, 0-char synthesis). Round 3 also produced a 0-char synthesis. Total: 2 of 10 rounds (20% rate) returned empty syntheses after running for 313-353 seconds. **R_k template-bias pattern repeated three times** (Rounds 2, 6, 8) — 6-7 findings per round with identical R_k delta of ~0.10 (model=0.236-0.250, recomputed=0.336-0.342). This is the strongest model-quality finding from the experiment.

Worth investigating whether the recent route change (Google direct API → OpenRouter, applied 14 May) is contributing to Gemini's elevated failure rate, or whether this is a consistent Gemini-on-CDSFL pattern unrelated to route.

**DeepSeek (V4 Pro via OpenRouter).** Two HIL flags (rounds 6 and 9). Dramatic variance in synthesis time across rounds: 1,981 s in Round 1, then 568-884s in rounds 2-5, then 352-569s in rounds 6-9. The Round 1 outlier (33 minutes for a 22K-char synthesis) was the single biggest driver of the original wall-clock-cap firing.

## Stage 6 calibrator non-fatal bug

Logged during Round 6 post-processing:

```
WARNING:cdsfl.shadow_cells:Stage 6 calibrator failed (non-fatal): 'int' object has no attribute 'lower'
```

Something is calling `.lower()` on an int. The Stage 6 calibrator is `shadow_integrated` per the F4 lexicon — its failure does not drive verdicts, so the experiment continued unaffected. But this is a real bug to track down. Likely location: `bench/dm/_shadow_stage6.py`. Probably a finding-classification path where a numeric value is being treated as a string. Add to the post-Exp-40 fix queue.

## Test article behaviour: `bench/dm/_feedback.py`

The target article (the §17 feedback-channel module under test) attracted **146 canonical findings** — substantially more than the gate-criterion calibration anticipated. The gate's `max_open_crit_high=5` threshold was derived from Exp 39-0's calibration on `bench/runner_core.py`. Exp 40's target appears to surface a higher density of critical-high findings, either because:

1. The §17 module has more actual issues than the runner_core target did,
2. The panel scrutinises §17 content more closely because the directive itself is novel,
3. The composer's per-model phenotype transforms emphasise different aspects of `_feedback.py` than they did for runner_core,
4. Some combination.

The reconciliation pipeline reduced 207 raw findings to 146 canonical entries (29% duplicate rate). The first three (C0007, C0008, C0013) plus the recurring merge-conflict entries (C0016, C0020, C0030, C0032, C0035) account for a substantial fraction of the duplicate-merge activity. Inspecting the canonical entries themselves (in `bench/logs/exp40_gate_20260514T020550Z/`) is the next analytical step before declaring whether `_feedback.py` requires substantive code changes.

## §17 feedback channel — the experimental variable, observed

Round 6 → Round 7 transition logged: `[feedback] round 6 → round 7: 5 model(s) flagged`. All five panel members received §17 feedback-channel flags for the next round. **The mechanism Experiment 40 was specifically designed to test is active and routing.** Whether the feedback flagging measurably changed panel behaviour in Round 7 relative to a counterfactual is the analytical question for the post-mortem — comparison points are available in the Round-6-vs-Round-7 per-model JSON files under `bench/logs/exp40_gate_20260514T020550Z/`.

## Action items

1. **Fix the gamma metric.** Compute gamma against post-reconciliation novelty, not pre-reconciliation. Without this fix, every subsequent experiment in the arc will run to extension-cap exhaustion when the panel has saturated. Highest-priority post-Exp-40 code change.

2. **Fix the FINDING_ID terminator regex.** Add `FINDING_ID` to the alternation in the parser regex. The panel converged on the fix; apply it. Add regression test if not already present in `bench/tests/test_feedback_channel.py`.

3. **Fix the Stage 6 calibrator `.lower()` on int bug.** Trace through `bench/dm/_shadow_stage6.py`, identify the path where an int is being treated as a string, correct. Add regression test.

4. **Investigate Gemini's intermittent 0-char syntheses.** 20% of Round dispatches returned empty after running for 5+ minutes. Compare against the prior Google-direct API route to determine whether the OpenRouter route change is contributing. If it is, consider routing Gemini back to Google direct for the remainder of the arc.

5. **Investigate Codex's CAPABILITY_MISMATCH HIL flags** in rounds 3-4. Distinct classification from the DEGRADATION pattern on the other models. The runner's ITC has a specific reason to call this CAPABILITY_MISMATCH; understand what it detected.

6. **Begin G7 arbitration-rule design.** Experiment 40 has produced abundant evidence — far more than the "minimum three observed patterns" threshold the §6b spec named. The deferred-to-Exp-49 work can begin now from Exp 40's evidence base.

7. **Calibrate the convergence gate for the arc.** Either lower the gamma threshold from 0.30, or recalibrate `max_open_crit_high` upward from 5, or recompute gamma against post-reconciliation novelty (per action 1). Some combination of these so future experiments can declare convergence cleanly when they actually have.

8. **Consider per-model timeout tuning.** DeepSeek's Round-1 33-minute synthesis was the single biggest driver of the wall-clock-cap firing. A per-model timeout that fails-fast on stragglers and accepts the missing contribution would let rounds proceed at the median model's pace rather than the slowest.

9. **Decide on resume policy for the rest of the arc.** Experiment 40 required a resume + cap extension to produce a full data harvest. Either future experiments adopt a 7,200s default cap, or the gamma fix (action 1) reduces the round count required for natural termination.

## What to read alongside this note

- **Plain-English companion:** `experimental_notes/Exp40_PostMortem_Plain_English_2026-05-14.md`.
- **TTS read-aloud version:** `~/Desktop/CDSFL_tts/Exp40_PostMortem_2026-05-14.txt`.
- **Final report (machine-readable):** `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`.
- **Per-round + per-model raw responses:** `bench/logs/exp40_gate_20260514T020550Z/` — round{N}_{model}_{timestamp}.json.
- **Initial-run launcher log:** `bench/logs/exp40_launch_20260514T020550Z.log`.
- **Resume launcher log:** `bench/logs/exp40_resume_20260514T032658Z.log`.

## Next review trigger

The next decision for the founder is the priority ordering of the nine action items above. Action 1 (gamma fix) and action 2 (parser regex fix) are highest-leverage. Action 4 (Gemini route investigation) and action 5 (Codex CAPABILITY_MISMATCH investigation) determine the panel composition for the rest of the arc. Once those are settled, the autonomous queue advances to Experiment 41 (bounded mathematics module at `bench/dm/_convergence.py`).

Written under CDSFL note standard v1.2 (14 May 2026).
