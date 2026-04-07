# Experiment 36 — Complete Session Findings

**Date:** 7 April 2026, 01:50–05:34 BST (224 min experiment, ~4h total session)
**Session scope:** Launch, live monitoring, and post-run analysis of Exp 36

This document collates ALL findings from the Exp 36 monitoring session — CC monitoring observations, founder observations and questions, joint analysis, and design proposals. It is the authoritative record of what was learned.

## I. Monitoring Observations (CC)

### Lesson 1: Gamma Bootstrap Period
`MIN_ROUNDS_FOR_GAMMA = 3` means γ returns 0.0 unconditionally until 3 rounds complete. This initially looked like a bug (γ=0.000 at R0 and R1) but is by design — the log-log regression needs at least 3 data points. Not a deficiency; just requires understanding.

### Lesson 2: Aggressive Early ITC
All 5 models were flagged DEGRADATION→change_focus after just one adaptive round (R1). This is aggressive but was ultimately productive — it triggered 31 merges in R2, the most significant single-round merge activity in the experiment. The ITC's threshold for "degradation" may be too sensitive for early rounds when models are still building understanding.

### Lesson 3: CC2v Activation and Maturation
CC2v activated at R6 (`VERIFICATION_MIN_ROUND = 6`) and processed 6-finding batches per round. Early batches had high rejection rates (4/6 rejected). By R16, the pattern reversed: 5/6 confirmed. The verification agent's accuracy improved as it accumulated codebase context. This is the opposite of the discovery-model fixation problem: cumulative context *helps* verification but *hurts* discovery.

### Lesson 4: DeepSeek Malformed Finding IDs
DeepSeek occasionally produced finding IDs that collided with the parser's regex patterns, creating malformed entries in the registry. These need post-experiment cleanup. The parser should be hardened against model-generated IDs that contain special characters or overly long strings.

### Lesson 5: ITC Intervention Accumulation
By R14, ChatGPT had 11+ consecutive ITC interventions, Gemini 9, Codex 7, DeepSeek 3+. The ITC never reached a state where models were "healthy" — every model was being continuously managed. This is sustainable for the experiment but indicates the degradation detection threshold is too aggressive for longer runs.

### Lesson 6: Shadow Pipeline Regex Classifier Drift
DC v1 regex classifier agreement with LLM classifier (Haiku): 41% at R13, 21% at R14, 44% at R22. The regex systematically over-classifies as "mathematical" when findings are actually code_behavioral or code_structural. The regex patterns were calibrated for a different finding format or code artifact.

### Lesson 7: B Cell v2 Z3 Counterexample
B Cell v2 shadow produced its first SMT-grounded counterexample at R14, rejecting Codex_F002 with a Z3 SAT counterexample for `round_idx`. This is programmatic falsification of a model claim — the formal verification pipeline working as designed. Still in shadow mode but validates the approach.

### Lesson 8: LLM Classifier Timeouts
Two findings (DeepSeek_F001, Gemini_F001) timed out at the 15-second limit in R13. The Haiku classification step needs a longer timeout for long finding descriptions, particularly when the finding includes proposed fixes with code snippets.

### Lesson 9: Fix Verification Limitations
All model-proposed fixes were evaluated as UNEVALUABLE by the fix verification shadow. The models propose fixes in natural language or pseudo-code, not as directly applicable patches. The fix verification agent needs AST-level patch parsing to be useful.

### Lesson 10: ITC-Convergence Feedback Loop (Critical)
The ITC restart_fresh mechanism and the convergence gate are in structural tension:
- ITC detects degradation → restarts model with fresh context
- Fresh model produces novel findings (burst reasoning)
- Novel stays above ≤2 threshold → convergence gate fails
- ITC keeps cycling → fresh models keep finding → novelty stays up

This is a self-reinforcing loop. The system optimises for discovery when it should be transitioning to consolidation. ChatGPT had 11+ consecutive interventions. The only exit was budget exhaustion at R20 (extended to R23).

### Lesson 11: OPEN Bathtub Curve
OPEN count trajectory: 30→40→17→15→12→14→18→16→34→38→33→36→38→37→42→42→39→36→37→38→44→48→44. This bathtub curve is directly caused by Lesson 10 — burst reasoning injects findings faster than verdicts resolve them in the second half.

### Lesson 12: Stall Detector Firing Without Authority
The stall detector issued advisories from R15 onwards ("Stall advisory: open_ch=0 static 3r, contested=1 static 3r, γ≥0.3"). But the stall detector's advisory tier has no convergence authority — it logs a warning and continues. The terminate tier (γ≥0.45) never fired because γ had dropped below 0.45 by R15. The stall detector correctly identified the system as stuck but couldn't act on it.

### Lesson 13: Near-Convergence at R18
The convergence gate almost fired at R18. Novel=2, γ passed, all conditions met EXCEPT contested=1. One persistent finding blocked the entire gate. The gate correctly identified near-convergence but had no mechanism to escalate the blocker.

### Lesson 14: Extension Unproductive
Budget extended from R20 to R24 due to contested findings. During extension: contested went from 1 to 2, novel rebounded to 6 (R21), γ barely moved (0.414→0.411). The extension burned 3 rounds (~30 min, significant API cost) without resolving any convergence conditions.

## II. Founder Observations

### Observation A: Novelty Decay as Primary Signal
The founder identified that the novelty decay curve, not the raw finding count, is the meaningful convergence signal. Raw output per round stayed stable (8–33 findings) while novel declined from 30 to 1. The ratio between these — discovery efficiency — is the real measure of productive exploration vs. churn.

This reframes how to read gamma. Gamma measures the cumulative novel depletion curve. But it doesn't see the raw-to-novel gap. When γ rises AND raw output stays high, the divergence IS the churn signal.

### Observation B: Gamma's Blind Spot
Gamma tracks cumulative novel findings. It does not know how much raw output was produced to generate those novel findings. A round with 33 raw findings and 5 novel (15% efficiency) looks the same to gamma as a round with 5 raw and 5 novel (100% efficiency). The founder correctly identified this as a gap in the convergence instrumentation.

### Observation C: Contested Should Be HIL, Not Model-Resolved
The founder asked: "Why isn't contested a HIL condition?" This is a direct design improvement. After 20 rounds of model debate, 2 findings remained contested. Models are not the best final arbiter of genuinely ambiguous issues. Routing persistent contested findings to HIL and removing them from the convergence gate would:
- Sharpen the convergence metric (fewer blockers)
- Leverage human judgement for what it's good at (ambiguity resolution)
- Reduce wasted rounds (the R18–R23 extension was entirely caused by contested findings)

### Observation D: Shadow Pipeline Impact
The founder asked what the shadow pipeline would do if active. Assessment: v2 Helper T (flagging ~4 duplicates/round) + B Cell v2 (Z3 formal proofs) + reconciliation locks (5 findings both pipelines agree are false) would reduce canonical count by ~15–20%. This would lower OPEN, accelerate convergence, and provide a cleaner signal. Activating v2 for Exp 37 is indicated.

### Observation E: Decay Curves as Meta-Cognitive Feedback (Novel Design Proposal)
The founder proposed feeding models their own decay data — novelty trajectory, discovery efficiency, gamma — so they can recognise when they're churning and self-modulate toward verdict-issuing rather than discovery.

This is a **neuromodulatory signal** in the "models as neurones" framework. Individual neurons don't decide when the brain is done processing, but they receive modulatory signals (dopamine, serotonin) that adjust firing rates based on network-level state. The decay curve would serve this function: not giving the model convergence authority, but modulating its behaviour toward consolidation when the discovery space is depleted.

**Implementation sketch:** Add to star topology prompt from round 5+:
"DISCOVERY METRICS: Your panel has discovered [N] new findings in the last 3 rounds (trajectory: [N, N-1, N-2]). Discovery efficiency is [X]% (novel/total this round). Cumulative gamma: [Y]. If your novel contribution is declining, prioritise high-quality verdicts on existing findings over new discoveries."

**Risk:** Models might prematurely declare convergence to "please" the prompt (the Exp 32 self-optimisation problem). Mitigation: the prompt provides data, not stopping instructions. The convergence gate retains sole authority.

### Observation F: Information-Theoretic Framing
The founder asked about entropy. The correct framing: the novelty decay curve represents declining **surprisal** (Shannon information). Each round's output carries less new information. When output entropy (variety of text) stays high but informational entropy (novel content) drops, the gap is churn. The models produce diverse text that all says the same thing.

This maps to: high output entropy + low informational entropy = churn signal.

## III. Joint Design Proposals for Exp 37

Based on all findings above, seven concrete design changes are proposed:

### 1. Contested → HIL Escalation (from Founder Observation C)
After 5 rounds of persistent contested status on a finding, escalate to HIL and remove from convergence gate. The gate should not be blocked by findings that require human judgement.

### 2. Discovery Efficiency Metric (from Founder Observations A, B)
Add ρ = novel/raw as a per-round metric. When ρ < 0.15 for 3 consecutive rounds, the system is in churn. Log as telemetry alongside gamma. Consider as a soft convergence signal.

### 3. Consolidation Phase (from CC Lesson 10)
In the final 3 rounds of budget, ITC transitions from restart_fresh to change_focus only. This allows novelty to decay naturally toward the ≤2 threshold instead of being sustained by burst reasoning.

### 4. Decay-Rate Convergence (from Founder Observation A)
Use rolling 3-round average novel decline rate as a softer convergence criterion. A system with novelty declining monotonically at [7, 5, 4, 2, 1] is clearly converging even if one round briefly exceeds the threshold.

### 5. Meta-Cognitive Decay Feedback (from Founder Observation E)
Inject discovery metrics (novelty trajectory, ρ, gamma) into the star topology prompt from R5+. Models see their own decay and can self-modulate toward verdicts. NOT a convergence authority — data only.

### 6. v2 Shadow Activation (from CC Lessons 6, 7 and Founder Observation D)
Activate Helper T v2 and B Cell v2 for Exp 37. Test whether better dedup and formal verification reduce registry inflation and accelerate convergence.

### 7. Classifier and Timeout Fixes (from CC Lessons 6, 8)
Recalibrate DC v1 regex or promote LLM classifier to primary. Increase LLM classifier timeout to 30s.

## IV. Experiment 36 Summary Statistics

| Metric | Value |
|--------|-------|
| Rounds | 23 (20 base + 3 extension) |
| Termination | EXTENSION_STALLED |
| Brain signal | INCOMPLETE |
| Total raw findings | 452 |
| Registry canonical | 153 |
| Overall novelty rate | 33.8% |
| Final γ | 0.411 |
| Runtime | 224 min |
| HIL flags | 51 |
| CC2v verdicts | 50 (25C / 6R / 11M / 8E) |
| CC2v HIL escalations | 9 unique findings |
| Contested at end | 2 |
| Per model | DeepSeek 119, ChatGPT 107, Codex 92, Gemini 92, CC2 42 |

## V. Files Produced

| File | Content |
|------|---------|
| `experimental_notes/Exp36_Results_2026-04-07.md` | Full results with round-by-round data |
| `experimental_notes/Exp36_Session_Findings_2026-04-07.md` | This document |
| `experimental_notes/Exp36_Live_Analysis_CDSFL_as_Bench_2026-04-07.md` | CDSFL-as-bench P-pass analysis |
| `experimental_notes/Exp36_Burst_Reasoning_Analysis_2026-04-07.md` | Burst reasoning P-pass analysis |
| `~/Desktop/CDSFL_tts/Exp36_Results_2026-04-07.txt` | Results TTS |
| `~/Desktop/CDSFL_tts/Exp36_Live_Analysis_CDSFL_as_Bench_2026-04-07.txt` | Bench analysis TTS |
| `~/Desktop/CDSFL_tts/Exp36_Burst_Reasoning_Analysis_2026-04-07.txt` | Burst reasoning TTS |
| `bench/logs/exp36_evidence_20260407T004931Z/exp36_report.json` | Structured report (526KB) |
| `bench/logs/exp36_console.log` | Full console output |
