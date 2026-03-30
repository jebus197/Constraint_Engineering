# CE (Constraint Engineering) Experimental Plan — Version 2, Redesigned

**Saved:** 2026-03-19 04:18 UTC
**Source:** `bench/EXPERIMENT_PLAN.md` in the Constraint Engineering repo

---

## Objective

Demonstrate whether CE produces real, meaningful improvement in AI reasoning quality, or prove that it does not. CE is a scientific method engine. It provides methodological discipline for problems where the optimal solution must be constructed and tested, not looked up. It is not an intelligence amplifier. It is a testing discipline.

CE was designed to operate at the frontier. The experiment must test there.

---

## The Problem with Version 1

Version 1 used a dumb script running unattended. Three fatal flaws:

1. **Fake diminishing returns.** The script counted severity labels in text output using regex pattern matching, not reasoning. It had no understanding of whether findings were real, novel, or meaningful.
2. **Unsupervised execution.** CC's attention window drops after minutes of inactivity. The script ran for hours with no intelligent oversight. Result: hung processes, wasted money, unreliable termination decisions.
3. **Self-assessment.** CC was testing Anthropic models via the Anthropic API, the same rate limit bucket as its own session. Methodologically wrong and operationally broken.

All three are eliminated in version 2.

---

## Key Design Change: The Confer Stage

Version 2 replaces the dumb adaptive termination with the CE confer stage.

1. Script runs P-passes 1 through 3 for a task. This is mechanical — no decisions.
2. Script pauses and invokes CC CLI with the 3-pass output.
3. CC assesses: are these passes showing genuine diminishing returns?
4. CC posts assessment to the IM service.
5. Script invokes CX CLI: read IM, assess CC's finding, agree or disagree?
6. CX reads IM, posts counter-assessment.
7. Script reads both assessments. If agreement on diminishing returns: move to next task. If disagreement: run pass 4 and re-confer. Maximum 5 passes hard cap regardless.

This means: no unsupervised decisions, genuine intelligence at every termination point, two-model adversarial agreement with different training biases, the experiment uses CE to test CE making it self-demonstrating, and no attention window problem because each invocation is fresh, focused, and on-demand.

The IM service is the confer channel. All confer transcripts are logged alongside results.

---

## Model Configurations (8 Models, 4 Providers)

All models are current-generation frontier as of 2026-03-18.

| Config | Model ID | Provider | Access |
|---|---|---|---|
| gpt-5.4 | gpt-5.4 | openai | API |
| o4-mini | o4-mini | openai-reasoning | API |
| gpt-5.3-codex | default codex model | codex exec | Subscription |
| gemini-3.1-pro | gemini-3.1-pro-preview | gemini | API |
| gemini-3-flash | gemini-3-flash-preview | gemini | API |
| llama-4-scout | meta-llama/llama-4-scout-17b-16e-instruct | groq | API |
| sonnet-4.6 | claude-sonnet-4-6 | anthropic | CX runs |
| sonnet-4-thinking | claude-sonnet-4-6 (extended thinking) | anthropic-thinking | CX runs |

- **CC runs:** gpt-5.4, o4-mini, gpt-5.3-codex, gemini-3.1-pro, gemini-3-flash, llama-4-scout
- **CX runs:** sonnet-4.6, sonnet-4-thinking (avoids CC self-assessment)
- Confer calls using CC CLI and CX CLI are covered by existing subscriptions — zero API cost

---

## Three Conditions

**Condition 1 — Control:** Bare prompt, no system instructions, single pass.

**Condition 2 — CE:** Full directives plus iterative P-passes, up to 5, confer-terminated.

**Condition 3 — Calibration Baseline:** Length-matched generic instructions ("be thorough, check your work"), same number of passes, but without CE's specific methodology. No constraint classification, no hard/soft distinction, no adversarial brief, no structured verification.

The calibration baseline isolates methodology from prompt quality. If CE beats calibration baseline, the structured falsification matters. If it does not, CE is just "think harder" in a fancy wrapper.

---

## CE as One Tool in a Chest

CE makes no claim to be the sole arbiter of truth. It is a composable testing discipline.

- **Use when:** the problem has classifiable constraints, single-pass solutions risk undetected failure modes, and the cost of iteration is justified by the cost of being wrong.
- **Do not use when:** the problem is simple enough that single-pass accuracy is reliable, or when there are no meaningful constraints to classify.

CE's falsification loop can be applied to output from any generation approach (domain-optimised prompts, chain-of-thought, etc.). Combined approaches may outperform either alone.

The calibration baseline tells users when CE earns its keep. A methodology that provides the means to falsify itself is consistent with its Popperian core.

The experiment output should be a **suitability map** showing which task properties predict CE's contribution — not a winner/loser declaration.

CE is authoritative on hard constraints (physics does not negotiate) and advisory on soft constraints (preferences are the user's domain).

---

## P-Pass Schemas

**Schema A — Standard Monolithic (5-pass)**
Pass 1 generates the solution. Passes 2–5 iteratively falsify own output. Each pass builds on the full prior chain. Confer after pass 3 to assess diminishing returns. Applies to all tasks.

**Schema B — Extended/Modular (4+1)**
Passes 1–4 each scoped to one module or subsystem, falsifying its constraints in isolation. Pass 5 is an isolated adversarial pass with fresh context and the canonical adversarial brief. Confer after pass 4 to assess whether pass 5 is needed. Applies to tasks with 3 or more distinct modules, tagged at design time.

**Schema C — Cross-Model Adversarial**
Model A generates in pass 1. Model B falsifies in pass 2. Model A responds in pass 3. CC and CX confer to assess diminishing returns. Model B re-checks if needed in pass 4. Isolated adversarial in pass 5. Model pairs chosen for maximum training-bias diversity. Applies to a representative subset of approximately 10 of 25 tasks.

**Grandslam**
Post-main-run. CC and CX confer via IM on results from all schemas. Full CE confer protocol. Deferred to after main data collection.

---

## Task Design (25 Frontier Tasks)

Already designed in `bench/tasks_frontier/`. Five categories, 5 each.

| Category | Description |
|---|---|
| 1 — Proof | Mathematical proofs that are machine-checkable |
| 2 — Code | Programs that must compile and pass a hidden test suite |
| 3 — Design | Engineering problems with quantifiable constraints |
| 4 — Synthesis | Multi-domain problems subject to physical laws |
| 5 — Reasoning-about-reasoning | Self-referential verification protocols |

All tasks are hard enough that frontier models make real errors (10–50% expected single-pass accuracy), but verifiable enough to score objectively.

---

## Measurement

1. **Verification score:** Does the final output pass verification?
2. **Per-pass delta:** What did each pass find? Confer assessment logged.
3. **Cross-schema comparison:** Schema B vs A, Schema C vs A on shared tasks.
4. **Calibration baseline comparison:** CE vs baseline. This is the critical test.
5. **Suitability map:** Which task properties predict CE's contribution?
6. **Breakout observations:** Novel STEM insights tagged for peer review.

---

## Execution Architecture

The script `bench/run_phase2.py` is the orchestrator. It makes no decisions.

It makes API calls for passes 1, 2, and 3. Then it pauses after pass 3. It invokes CC CLI to assess the 3 passes. It posts the CC assessment to IM. It invokes CX CLI to read IM and agree or disagree. It parses agreement. Agreement means move to next task. Disagreement means run pass 4 and re-confer. Maximum 5 passes hard cap.

Checkpoint after every task for crash-safe resume. Cost ledger with hard cap.

**Monitoring:**
- `tail -f bench/results/phase2/overnight.log` — script progress
- `python3 cw_handoff/im_service.py read` — confer transcripts

---

## Budget

| Item | Cost |
|---|---|
| OpenAI API (GPT-5.4 + o4-mini) | ~$10 |
| Codex Business (gpt-5.3-codex + CX runs + confer) | $0 |
| Google API (Gemini 3.1 Pro + Flash) | ~$7 |
| Groq API (Llama 4 Scout) | ~$0.25 |
| Confer via CC + CX | $0 |
| Buffer (30%) | ~$5 |
| **Total** | **~$22** |

Well within the $100 cap.

---

## Sequencing

1. Clear stale checkpoint and cost ledger
2. Pilot: 3 tasks, 1 model — validate difficulty calibration
3. Review pilot with founder
4. Full run: 6 CC-configs × 25 tasks × 3 conditions, with confer
5. CX runs: 2 Anthropic configs × 25 tasks × 3 conditions
6. Schema C cross-model pairs on 10 tagged tasks
7. Grandslam: CC/CX full confer on all results via IM
8. Phase 2.5: Genesis case study, 5–10 real-world CE catches
9. Phase 3: CX adversarial review of entire experiment
10. Final report

---

## CLI Launch Instructions

**Resume conversation from CLI:**
```
cd /Users/georgejackson/Developer_Projects && claude --resume
```

**Launch the experiment after plan approval:**
```
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering && source .env && python3 bench/run_phase2.py --cost-cap 100
```

**Monitor in a separate terminal:**
```
tail -f bench/results/phase2/overnight.log
```

**Watch IM confer transcripts in another terminal:**
```
watch -n 5 python3 cw_handoff/im_service.py read --recent 5
```

---

## Files

| File | Purpose |
|---|---|
| `bench/run_phase2.py` | Experiment orchestrator, confer-enabled |
| `bench/run_benchmark.py` | Core API harness, all providers, retry, throttle |
| `bench/evaluate.py` | Scoring pipeline |
| `bench/report.py` | Results reporting |
| `bench/tasks_frontier/` | 25 frontier tasks, ft-001 to ft-025 |
| `bench/directives/` | Domain-specific CE directives |
| `bench/results/phase2/` | Output directory with checkpoint and cost ledger |
| `bench/EXPERIMENT_PLAN.md` | Plan file |
| `bench/FINANCIAL_LEDGER.md` | All outlays and subscriptions |

---

## Phase 1 Results (Baseline / Floor Test)

Phase 1 established that CE does not hurt and provides marginal improvement on easy tasks. Ceiling effect confirmed: 90–100% baseline detection, 0–12.5 pp improvement. Necessary but insufficient — floor test only.

| Model | Baseline | With CE | Gain |
|---|---|---|---|
| Sonnet 4 | 95% | 100% | +5 pp |
| Sonnet 4 (thinking) | 97.5% | 100% | +2.5 pp |
| GPT-4o | 90% | 100% | +10 pp |
| o3-mini | 95% | 100% | +5 pp |
| Llama 3.3 70B | 87.5% | 100% | +12.5 pp |
| Gemini Flash | Complete | Scoring pending | — |
| Gemini Pro | Incomplete | 504 errors | — |

Pattern: weaker models benefit more. Reasoning models benefit less. Phase 2 tests whether this pattern holds at the frontier.

---

## Locked Design Decisions (from `EXPERIMENT_DESIGN_DECISIONS.md`)

**Three conditions with defined roles:**

- **Control:** Single pass, no system prompt, no iteration. Purpose: raw unfiltered model output, the baseline. Executed first.
- **CE/Experimental:** Iterative P-passes with CDSFL directives. Purpose: the experimental condition, full CE methodology applied.
- **Calibration Baseline/Placebo:** Iterative P-passes with generic "be careful" directives, same iteration mechanism as CE, including adaptive confer termination. Purpose: isolates directive content as the variable. Controls for prompt quality and iteration count.

The calibration baseline deliberately shares the adaptive confer mechanism with CE. Without shared iteration machinery, any CE vs. calibration comparison would conflate "better directives" with "different iteration count."

**Three comparisons, three questions:**
- Control vs. CE: does the full methodology beat raw output?
- Calibration vs. CE: do the specific directives matter?
- Control vs. Calibration: does structured iteration alone help?

**Not defects — by design:**
- Placebo shares confer mechanism with CE
- Control is single-pass while CE is iterative
- Confer CLI costs are not metered in the CostLedger
- Task randomisation seed is constant, not manifest-derived
- Schema C adversarial pass requires `max_passes ≥ 5`
- Deferred report only shows resolved/deferred for adaptive conditions

**Review history:** rounds 1–8 CC/CX adversarial, rounds 9–13 Gemini, round 14 Gemini Extended P-Pass, round 15 CC Full P-Pass. Total approximately 23 review passes across 3 model architectures.
