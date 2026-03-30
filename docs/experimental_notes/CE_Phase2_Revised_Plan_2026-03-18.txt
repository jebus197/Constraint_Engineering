# Constraint Engineering Phase 2 — Revised Plan

**Date:** 18 March 2026

This document describes the revised Phase 2 experimental design for Constraint Engineering (CE, formerly CDSFL). It replaces the earlier dumb-script approach with an intelligent, monitored methodology that uses the CE confer stage at every termination decision point.

---

## What Changed and Why

The original design ran a Python script unattended overnight. The script made autonomous decisions about when to stop iterating (diminishing returns) using a crude severity-label counter. This had three fatal problems.

**First,** the script had no genuine understanding of diminishing returns. It counted the words "trivial", "moderate", and "severe" in model output. That is string matching, not reasoning.

**Second,** CC (Claude Code) could not maintain attention on a background script. After a few minutes of inactivity, CC effectively sleeps. The script ran unsupervised, hung, and burned money.

**Third,** the methodology was not CE. The whole point of CE is structured falsification with intelligent confer stages. A dumb script running unsupervised is the opposite of that.

---

## The Revised Architecture

The script becomes an orchestrator that invokes CC and CX at every decision point. It never makes termination decisions itself.

- **Step 1.** The script sends the task prompt to the model under test (via API or CLI) and collects the response. This is pass 1, the control condition.
- **Step 2.** The script sends the same task with CE directives and collects pass 1 of the CE condition. Then it runs passes 2 and 3 automatically.
- **Step 3.** After pass 3, the script pauses. It writes the accumulated output to a file and invokes CC via the CLI in print mode.

  CC receives: *"Here are 3 passes of CE falsification on this task. Assess whether genuine diminishing returns have been reached. Are the findings in pass 3 substantively novel compared to passes 1 and 2, or are they rehashing the same issues?"*

  CC writes its assessment to the IM service.

- **Step 4.** The script invokes CX via the Codex CLI in exec mode.

  CX receives: *"Read the IM service. CC has assessed whether diminishing returns have been reached on this task. Here is the raw output from all 3 passes. Do you agree or disagree with CC's assessment? Post your counter-assessment to the IM service."*

- **Step 5.** The script reads the IM service for both assessments. If CC and CX agree that diminishing returns have been reached, the script moves to the next task. If they disagree, the script runs pass 4 and re-confers. Maximum 5 passes hard cap.
- **Step 6.** The same process runs for the calibration baseline condition (generic "be-careful" instructions instead of CE directives).
- **Step 7.** The script logs the full confer transcript alongside the results for every task. This is primary data for the study.

---

## Models and Access Methods

**CC runs (non-Anthropic models, via direct API):**
- Gemini 3.1 Pro Preview via Google API
- Gemini 3 Flash Preview via Google API
- Llama 4 Scout via Groq API

**CX runs (via Codex Business subscription, zero incremental cost):**
- gpt-5.3-codex (latest Codex model)
- gpt-5.4 (OpenAI flagship)
- o4-mini (OpenAI reasoning)
- Sonnet 4.6 (Anthropic, via CX subscription)

**Confer calls:**
- CC via `claude` CLI, print mode (included in Max subscription)
- CX via `codex exec` CLI (included in Business subscription)

**Total estimated API cost:** approximately $10 (Gemini plus Groq only). All other model access is through existing subscriptions.

---

## The Confer Stage

This is the CE methodology operating on its own evaluation. Two models with different training biases assess the same output and reach agreement on whether the falsification loop has converged. This is not an add-on. This IS the experiment demonstrating CE in action.

The confer uses the existing IM service from Project Genesis. The IM service is a lightweight JSON rolling buffer that CC, CX, and CW can all read and write. It provides attribution, timestamps, and a permanent record.

```
CC posts via:  python3 cw_handoff/im_service.py post cc "message"
CX posts via:  python3 cw_handoff/im_service.py post cx "message"
Any agent reads via:  python3 cw_handoff/im_service.py read
```

---

## Three Conditions Per Task

- **Condition A — Control:** Raw prompt, no directives. Single pass. Measures what the model produces without any methodology.
- **Condition B — CE:** Full CE directives with iterative falsification. 3–5 passes with intelligent termination via CC + CX confer.
- **Condition C — Calibration Baseline:** Length-matched generic instructions ("take your time, be careful, check your work"). Same iteration structure as Condition B. Isolates whether CE's gains come from the methodology itself or just from having a longer, more encouraging prompt.

---

## Schema C — Cross-Model Adversarial

For the 10 tasks tagged for Schema C, two different models check each other's work. Model A generates, Model B falsifies, Model A responds, Model B re-checks, then an isolated adversarial pass.

**Cross-model pairs (maximise training-bias diversity):**
- Sonnet 4.6 thinking vs gpt-5.4
- gpt-5.4 vs Gemini 3.1 Pro
- Gemini 3.1 Pro vs Sonnet 4.6 thinking

---

## Task Set

25 frontier tasks across 5 categories:

- **Proof** (5 tasks): mathematical proofs requiring novel construction
- **Code** (5 tasks): systems with complex constraint interactions
- **Design** (5 tasks): architectural problems with competing requirements
- **Synthesis** (5 tasks): cross-domain problems requiring integration
- **Reasoning** (5 tasks): multi-step logical chains with verification

All tasks are designed with 10–50% expected single-pass accuracy for frontier models. This avoids the ceiling effect observed in Phase 1 where 90–100% baseline accuracy compressed measurable improvement.

Tasks are stored in `bench/tasks_frontier/` as individual JSON files.

---

## Monitoring

The script logs all output to `bench/results/phase2/overnight.log` in real time. Monitor via:

```bash
tail -f /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/results/phase2/overnight.log
```

The IM service provides a second monitoring channel:

```bash
cd /Users/georgejackson/Developer_Projects/Project_Genesis && python3 cw_handoff/im_service.py read
```

---

## Budget

- **Hard cap:** $100
- **Estimated spend:** approximately $10 in API costs (Gemini plus Groq)
- All OpenAI and Anthropic model access via existing subscriptions
- The cost ledger tracks every API call and aborts safely if the cap is reached

---

## How to Start the Test

```bash
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
source .env
python3 bench/run_phase2.py --cost-cap 100
```

**To resume after any interruption:**

```bash
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
source .env
python3 bench/run_phase2.py --resume --cost-cap 100
```

**To monitor in a second terminal:**

```bash
tail -f /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/results/phase2/overnight.log
```

**To monitor IM confer exchanges in a third terminal:**

```bash
watch -n 10 "cd /Users/georgejackson/Developer_Projects/Project_Genesis && python3 cw_handoff/im_service.py read --recent 5"
```

---

## What Comes After

- **Phase 2.5:** Genesis case study appendix. 5–10 real-world CE catches from the CC + CX adversarial work on Project Genesis.
- **Phase 3:** Grandmaster round. CW orchestrates a full adversarial P-pass ping-pong between CC and CX on the Phase 2 results themselves. This is the final quality gate before the study is written up.

The study output will be a suitability map, not a winner/loser declaration. It will show which task properties predict CE's contribution and when simpler approaches are sufficient. CE makes no claim to be the sole arbiter of truth. It is one tool in a chest of approaches, composable with other methods, and self-aware enough to tell users when it is not helping.
