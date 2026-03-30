# CE (Constraint Engineering) Experimental Plan — Version 2, Redesigned

**Owner:** George Jackson (The Founder)
**Date:** 18 March 2026
**Status:** Redesigned. Previous dumb-script approach abandoned.
**Supersedes:** Version 1 from 17 March 2026

**Terminology:** CE = Constraint Engineering = CDSFL. CE is preferred throughout.

---

## Objective

Demonstrate whether CE produces real, meaningful improvement in AI reasoning quality, or prove that it does not. CE is a scientific method engine. It provides methodological discipline for problems where the optimal solution must be constructed and tested, not looked up. It is not an intelligence amplifier. It is a testing discipline.

CE was designed to operate at the frontier. The experiment must test there.

---

## The Problem with Version 1

Version 1 used a dumb script running unattended. Three fatal flaws were identified.

1. **Fake diminishing returns.** The script counted severity labels in text output using regex pattern matching, not reasoning. It had no understanding of whether findings were real, novel, or meaningful.

2. **Unsupervised execution.** CC's attention window drops after minutes of inactivity. The script ran for hours with no intelligent oversight. Result: hung processes, wasted money, unreliable termination decisions.

3. **Self-assessment.** CC was testing Anthropic models via the Anthropic API, the same rate limit bucket as its own session. Methodologically wrong and operationally broken.

All three are eliminated in version 2.

---

## Key Design Change: The Confer Stage

Version 2 replaces the dumb adaptive termination with the CE confer stage.

1. The script runs P-passes 1 through 3 for a task. This is mechanical — no decisions are made.
2. The script pauses and invokes CC CLI (Claude Code command line interface) with the 3-pass output.
3. CC assesses whether these passes are showing genuine diminishing returns.
4. CC posts its assessment to the IM (instant messaging) service.
5. The script invokes CX CLI (Codex command line interface) and asks it to read the IM channel, assess CC's finding, and agree or disagree.
6. CX reads IM and posts its counter-assessment.
7. The script reads both assessments. If they agree that diminishing returns have been reached, the script moves to the next task. If they disagree, the script runs pass 4 and re-confers. There is a maximum of 5 passes regardless.

This means no unsupervised decisions. There is genuine intelligence at every termination point. Two models with different training biases must reach adversarial agreement. The experiment uses CE to test CE, making it self-demonstrating. There is no attention window problem because each invocation is fresh, focused, and on-demand.

The IM service, located at `Project_Genesis/cw_handoff/im_service.py`, is the confer channel. All confer transcripts are logged alongside results.

---

## Model Configurations: 8 Models Across 4 Providers

All models are current-generation frontier as of 18 March 2026.

| Config | Model | Provider | Access |
|---|---|---|---|
| gpt-5.4 | gpt-5.4 | OpenAI | API |
| o4-mini | o4-mini | OpenAI (reasoning) | API |
| gpt-5.3-codex | default codex model | codex exec | Subscription |
| gemini-3.1-pro | gemini-3.1-pro-preview | Google | API |
| gemini-3-flash | gemini-3-flash-preview | Google | API |
| llama-4-scout | meta-llama/llama-4-scout-17b-16e-instruct | Groq | API |
| sonnet-4.6 | claude-sonnet-4-6 | Anthropic | CX runs |
| sonnet-4-thinking | claude-sonnet-4-6 with extended thinking | Anthropic (thinking) | CX runs |

- **CC runs:** gpt-5.4, o4-mini, gpt-5.3-codex, gemini-3.1-pro, gemini-3-flash, llama-4-scout
- **CX runs:** sonnet-4.6, sonnet-4-thinking (avoids CC self-assessment)
- **Confer calls** using CC CLI + CX CLI are covered by existing subscriptions at zero API cost

---

## Three Conditions

**Condition 1 — Control:** Bare prompt, no system instructions, single pass.

**Condition 2 — CE:** Full directives plus iterative P-passes, up to 5, terminated by the confer mechanism.

**Condition 3 — Calibration Baseline:** Length-matched generic instructions such as "be thorough, check your work." Same number of passes, but without CE's specific methodology. No constraint classification, no hard vs. soft distinction, no adversarial brief, no structured verification.

The calibration baseline isolates methodology from prompt quality. If CE beats the calibration baseline, the structured falsification matters. If it does not, CE is just "think harder" in a fancy wrapper.

---

## CE as One Tool in a Chest

CE makes no claim to be the sole arbiter of truth. It is a composable testing discipline.

- **Use it when:** the problem has classifiable constraints, single-pass solutions risk undetected failure modes, and the cost of iteration is justified by the cost of being wrong.
- **Do not use it when:** the problem is simple enough that single-pass accuracy is reliable, or when there are no meaningful constraints to classify.

CE's falsification loop can be combined with output from any generation approach, such as domain-optimised prompts or chain-of-thought. Combined approaches may outperform either alone.

The calibration baseline tells users when CE earns its keep. A methodology that provides the means to falsify itself is consistent with its Popperian core.

The experiment output should be a **suitability map**, showing which task properties predict CE's contribution, rather than a winner vs. loser declaration.

CE is authoritative on hard constraints (physics does not negotiate) and advisory on soft constraints (preferences are the user's domain).

---

## P-Pass Schemas

**Schema A — Standard Monolithic (5 passes)**
Pass 1 generates the solution. Passes 2–5 iteratively falsify the model's own output. Each pass builds on the full prior chain. The confer stage runs after pass 3 to assess diminishing returns. Applies to all tasks.

**Schema B — Extended Modular (4+1 passes)**
Passes 1–4 are each scoped to one module or subsystem, falsifying its constraints in isolation. Pass 5 is an isolated adversarial pass with fresh context and the canonical adversarial brief. The confer stage runs after pass 4 to assess whether pass 5 is needed. Applies only to tasks with 3 or more distinct modules, tagged at design time.

**Schema C — Cross-Model Adversarial**
Model A generates in pass 1. Model B falsifies in pass 2. Model A responds in pass 3. The confer stage assesses diminishing returns. Model B re-checks if needed in pass 4. An isolated adversarial pass runs as pass 5. Model pairs are chosen for maximum training-bias diversity. Applies to a representative subset of approximately 10 of 25 tasks.

**Grandslam**
Post-main-run phase. CC and CX confer via IM on results from all schemas using the full CE confer protocol. Deferred to after main data collection.

---

## Task Design: 25 Frontier Tasks

Already designed and stored in `bench/tasks_frontier/`. Five categories, 5 tasks each.

| Category | Description |
|---|---|
| 1 — Proof | Mathematical proofs that can be machine-checked |
| 2 — Code | Programs that must compile and pass a hidden test suite |
| 3 — Design | Engineering problems with quantifiable constraints |
| 4 — Synthesis | Multi-domain problems subject to physical laws |
| 5 — Reasoning-about-reasoning | Self-referential verification protocols |

All tasks are hard enough that frontier models make real errors (10–50% expected single-pass accuracy), but verifiable enough to score objectively.

---

## Measurement

1. **Verification Score:** Does the final output pass verification?
2. **Per-Pass Delta:** What did each pass find? The confer assessment is logged.
3. **Cross-Schema Comparison:** Schema B vs A, and Schema C vs A, on shared tasks.
4. **Calibration Baseline Comparison:** CE vs baseline. This is the critical test.
5. **Suitability Map:** Which task properties predict CE's contribution?
6. **Breakout Observations:** Novel STEM insights tagged for peer review.

---

## Execution Architecture

The script `bench/run_phase2.py` acts as an orchestrator that makes no decisions itself.

It calls the API for the model under test for passes 1, 2, and 3. After pass 3 it pauses. It invokes the Claude CLI to assess the 3 passes. It posts CC's assessment to IM. It invokes `codex exec` to get CX's counter-assessment. It parses whether they agree. If they agree on diminishing returns, it moves to the next task. If they disagree, it runs pass 4 and re-confers. There is a maximum of 5 passes as a hard cap.

The script checkpoints after every task for crash-safe resume. It tracks costs with a hard cap.

**Monitoring:**
- `tail -f bench/results/phase2/overnight.log` — script progress
- `python3 cw_handoff/im_service.py read --recent 5` — confer transcripts (watch mode)

---

## Budget

| Item | Cost |
|---|---|
| OpenAI API (GPT-5.4 + o4-mini) | ~$10 |
| Codex Business (GPT-5.3 + CX runs + confer) | $0 |
| Google API (Gemini 3.1 Pro + Flash) | ~$7 |
| Groq API (Llama 4 Scout) | ~$0.25 |
| Confer via CC + CX CLI | $0 |
| Buffer (30%) | ~$5 |
| **Total** | **~$22** |

Well within the $100 cap.

---

## Sequencing

1. Clear stale checkpoint and cost ledger
2. Pilot: 3 tasks with 1 model to validate difficulty calibration
3. Review pilot with founder
4. Full run: 6 CC-configs × 25 tasks × 3 conditions, with confer
5. CX runs: 2 Anthropic configs × 25 tasks × 3 conditions
6. Schema C cross-model pairs on 10 tagged tasks
7. Grandslam: CC and CX full confer on all results via IM
8. Phase 2.5: Genesis case study with 5–10 real-world CE catches
9. Phase 3: CX adversarial review of entire experiment
10. Final report

---

## CLI Launch Instructions

**Resume conversation from CLI:**
```
cd ~/Developer_Projects && claude --resume
```

**Launch the experiment after plan approval:**
```
cd ~/Developer_Projects/Constraint_Engineering && source .env && python3 bench/run_phase2.py --cost-cap 100
```

**Monitor script progress (separate terminal):**
```
tail -f bench/results/phase2/overnight.log
```

**Watch IM confer transcripts (separate terminal):**
```
watch -n 5 python3 cw_handoff/im_service.py read --recent 5
```

**Resume after any crash:**
```
cd ~/Developer_Projects/Constraint_Engineering && source .env && python3 bench/run_phase2.py --resume --cost-cap 100
```

---

## Files

| File | Purpose |
|---|---|
| `bench/run_phase2.py` | Experiment orchestrator with confer enabled |
| `bench/run_benchmark.py` | Core API harness with all providers, retry logic, and throttling |
| `bench/evaluate.py` | Scoring pipeline |
| `bench/report.py` | Results reporting tool |
| `bench/tasks_frontier/` | 25 frontier tasks (ft-001 through ft-025) |
| `bench/directives/` | Domain-specific CE directives |
| `bench/results/phase2/` | Output, checkpoint, and cost ledger |
| `bench/EXPERIMENT_PLAN.md` | Plan document |
| `bench/FINANCIAL_LEDGER.md` | All outlays and subscriptions |

---

## Phase 1 Results: Baseline and Floor Test

Phase 1 established that CE does not hurt and provides marginal improvement on easy tasks. The ceiling effect was confirmed with 90–100% baseline detection and 0–12.5 percentage point improvement. Necessary but insufficient as a floor test only.

| Model | Baseline | With CE | Gain |
|---|---|---|---|
| Sonnet 4 | 95% | 100% | +5 pp |
| Sonnet 4 (thinking) | 97.5% | 100% | +2.5 pp |
| GPT-4o | 90% | 100% | +10 pp |
| o3-mini | 95% | 100% | +5 pp |
| Llama 3.3 70B | 87.5% | 100% | +12.5 pp |
| Gemini Flash | Phase 1 complete | scoring pending | — |
| Gemini Pro | Did not complete | 504 errors | — |

The pattern shows that weaker models benefit more while reasoning models benefit less. Phase 2 tests whether this pattern holds at the frontier.
