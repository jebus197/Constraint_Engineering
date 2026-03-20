CE (Constraint Engineering) Experimental Plan v2 — Redesigned
=============================================================

Owner: George Jackson (The Founder)
Date: 2026-03-18
Status: Redesigned. Previous dumb-script approach abandoned.
Supersedes: v1 (2026-03-17)

Terminology: CE = Constraint Engineering = CDSFL. "CE" preferred throughout.


OBJECTIVE
---------

Demonstrate whether CE produces real, meaningful improvement in AI reasoning
quality — or prove that it does not. CE is a scientific method engine: it
provides methodological discipline for problems where the optimal solution
must be constructed and tested, not looked up. It is not an intelligence
amplifier; it is a testing discipline.

CE was designed to operate at the frontier. The experiment must test there.


THE PROBLEM WITH v1
-------------------

v1 used a dumb script running unattended. Three fatal flaws:

  1. FAKE DIMINISHING RETURNS: The script counted severity labels in text
     output — regex pattern matching, not reasoning. It had no understanding
     of whether findings were real, novel, or meaningful.

  2. UNSUPERVISED EXECUTION: CC's attention window drops after minutes of
     inactivity. The script ran for hours with no intelligent oversight.
     Result: hung processes, wasted money, unreliable termination decisions.

  3. SELF-ASSESSMENT: CC was testing Anthropic models via Anthropic API —
     the same rate limit bucket as its own session. Methodologically wrong
     and operationally broken.

All three are eliminated in v2.


KEY DESIGN CHANGE: THE CONFER STAGE
------------------------------------

v2 replaces the dumb adaptive termination with the CE confer stage:

  1. Script runs P-passes 1-3 for a task (mechanical — no decisions)
  2. Script PAUSES and invokes CC CLI with the 3-pass output
  3. CC assesses: "Are these passes showing genuine diminishing returns?"
  4. CC posts assessment to IM service
  5. Script invokes CX CLI: "Read IM. Assess CC's finding. Agree or disagree?"
  6. CX reads IM, posts counter-assessment
  7. Script reads both assessments:
     - AGREEMENT (diminishing returns) → move to next task
     - DISAGREEMENT → run pass 4, re-confer
     - Max 5 passes hard cap regardless

This means:
  - No unsupervised decisions
  - Genuine intelligence at every termination point
  - Two-model adversarial agreement (different training biases)
  - The experiment USES CE to test CE — self-demonstrating methodology
  - No attention window problem — each invocation is fresh, focused, on-demand

The IM service (Project_Genesis/cw_handoff/im_service.py) is the confer
channel. All confer transcripts are logged alongside results.


MODEL CONFIGURATIONS (8 models, 4 providers)
---------------------------------------------

All models current-generation frontier (as of 2026-03-18).

  Config            Model ID                                    Provider         Access
  ------            --------                                    --------         ------
  gpt-5.4           gpt-5.4                                     openai           API
  o4-mini           o4-mini                                     openai-reasoning API
  gpt-5.3-codex     (default codex model)                       codex exec       subscription
  gemini-3.1-pro    gemini-3.1-pro-preview                      gemini           API
  gemini-3-flash    gemini-3-flash-preview                      gemini           API
  llama-4-scout     meta-llama/llama-4-scout-17b-16e-instruct   groq             API
  sonnet-4.6        claude-sonnet-4-6                            anthropic        CX runs
  sonnet-4-thinking claude-sonnet-4-6 (extended thinking)        anthropic        CX runs

Access methods:
  - "API" = direct API call from script (costs per-call)
  - "subscription" = codex exec --model X (covered by Codex Business)
  - "CX runs" = CX handles via Codex Business (not CC's API key)

CC runs: gpt-5.4, o4-mini, gpt-5.3-codex, gemini-3.1-pro, gemini-3-flash, llama-4-scout
CX runs: sonnet-4.6, sonnet-4-thinking (avoids CC self-assessment)

Confer calls (CC CLI + CX CLI): covered by existing subscriptions, zero API cost.


THREE CONDITIONS
----------------

  1. CONTROL: bare prompt, no system instructions, single pass
  2. CE: full directives + iterative P-passes (up to 5, confer-terminated)
  3. CALIBRATION BASELINE: length-matched generic instructions ("be thorough,
     check your work"), same number of passes, but WITHOUT CE's specific
     methodology (no constraint classification, no HARD/SOFT, no adversarial
     brief, no structured verification)

The calibration baseline isolates METHODOLOGY from PROMPT QUALITY.
If CE beats calibration baseline, the structured falsification matters.
If it doesn't, CE is just "think harder" in a fancy wrapper.


CE AS ONE TOOL IN A CHEST
--------------------------

CE makes no claim to be the sole arbiter of truth. It is a composable
testing discipline:

  - Use when: the problem has classifiable constraints, single-pass solutions
    risk undetected failure modes, and the cost of iteration is justified by
    the cost of being wrong.
  - Don't use when: the problem is simple enough that single-pass accuracy is
    reliable, or when there are no meaningful constraints to classify.
  - Combine: CE's falsification loop can be applied to output from any
    generation approach (domain-optimised prompts, chain-of-thought, etc.).
    Combined approaches may outperform either alone.

The calibration baseline tells users when CE earns its keep. A methodology
that provides the means to falsify itself is consistent with its Popperian
core.

The experiment output should be a SUITABILITY MAP — which task properties
predict CE's contribution — not a winner/loser declaration.

CE is authoritative on HARD constraints (physics doesn't negotiate) and
advisory on SOFT constraints (preferences are the user's domain).


P-PASS SCHEMAS
--------------

  Schema A — Standard Monolithic (5-pass):
    Pass 1: Generate solution
    Passes 2-5: Iteratively falsify own output. Each pass builds on full
    prior chain. Confer after pass 3 to assess diminishing returns.
    Applies to: ALL tasks.

  Schema B — Extended/Modular (4+1):
    Passes 1-4: Each scoped to one module/subsystem, falsifying its
    constraints in isolation.
    Pass 5: Isolated adversarial — fresh context, canonical adversarial brief.
    Confer after pass 4 to assess whether pass 5 is needed.
    Applies to: tasks with 3+ distinct modules (tagged at design time).

  Schema C — Cross-Model Adversarial:
    Model A generates (pass 1) → Model B falsifies (pass 2) →
    Model A responds (pass 3) → Confer: CC+CX assess diminishing returns →
    Model B re-checks if needed (pass 4) → isolated adversarial (pass 5).
    Model pairs chosen for maximum training-bias diversity.
    Applies to: representative subset (~10 of 25 tasks).

  Grandslam — Post-main-run. CC and CX confer via IM on results from all
    schemas. Full CE confer protocol. Deferred to after main data collection.


TASK DESIGN (25 frontier tasks)
-------------------------------

Already designed in bench/tasks_frontier/. Five categories, 5 each:

  1. PROOF: Mathematical proofs (machine-checkable)
  2. CODE: Programs that must compile + pass hidden test suite
  3. DESIGN: Engineering problems with quantifiable constraints
  4. SYNTHESIS: Multi-domain problems subject to physical laws
  5. REASONING-ABOUT-REASONING: Self-referential verification protocols

All tasks are HARD ENOUGH that frontier models make real errors (10-50%
expected single-pass accuracy), but VERIFIABLE enough to score objectively.


MEASUREMENT
-----------

  1. VERIFICATION SCORE: Does the final output pass verification?
  2. PER-PASS DELTA: What did each pass find? Confer assessment logged.
  3. CROSS-SCHEMA COMPARISON: Schema B vs A, Schema C vs A on shared tasks.
  4. CALIBRATION BASELINE COMPARISON: CE vs baseline — the critical test.
  5. SUITABILITY MAP: Which task properties predict CE's contribution?
  6. BREAKOUT OBSERVATIONS: Novel STEM insights tagged for peer review.


EXECUTION ARCHITECTURE
----------------------

  Script: bench/run_phase2.py (orchestrator — no decisions)
    |
    +-- API call (model under test) for passes 1, 2, 3
    |
    +-- PAUSE after pass 3
    |   +-- Invoke: claude -p "Assess these 3 passes..." > /tmp/cc_assess.txt
    |   +-- Post CC assessment to IM
    |   +-- Invoke: codex exec "Read IM. Agree or disagree?" -o /tmp/cx_assess.txt
    |   +-- Parse agreement
    |   +-- Agreement → next task. Disagreement → pass 4, re-confer.
    |
    +-- Max 5 passes hard cap
    |
    +-- Checkpoint after every task (crash-safe resume)
    +-- Cost ledger with hard cap

  Monitoring:
    tail -f bench/results/phase2/overnight.log     (script progress)
    python3 cw_handoff/im_service.py read           (confer transcripts)


BUDGET
------

  Provider          Est. cost    Access
  --------          ---------    ------
  OpenAI API        ~$10         GPT-5.4 + o4-mini
  Codex Business    $0           gpt-5.3-codex + CX Anthropic runs + confer
  Google API        ~$7          Gemini 3.1 Pro + Flash
  Groq API          ~$0.25       Llama 4 Scout
  Confer (CC+CX)    $0           CLI subscriptions
  Buffer (30%)      ~$5          Retries/failures
  ---               ---
  TOTAL             ~$22         Well within $100 cap


SEQUENCING
----------

  1. Clear stale checkpoint and cost ledger
  2. Pilot: 3 tasks, 1 model (validate difficulty calibration)
  3. Review pilot with founder
  4. Full run: 6 CC-configs x 25 tasks x 3 conditions (with confer)
  5. CX runs: 2 Anthropic configs x 25 tasks x 3 conditions
  6. Schema C cross-model pairs on 10 tagged tasks
  7. Grandslam: CC/CX full confer on all results via IM
  8. Phase 2.5: Genesis case study (5-10 real-world CE catches)
  9. Phase 3: CX adversarial review of entire experiment
  10. Final report


CLI LAUNCH INSTRUCTIONS
-----------------------

To resume this conversation from CLI:
  cd /Users/georgejackson/Developer_Projects
  claude --resume

To launch the experiment (after plan approval):
  cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
  source .env
  python3 bench/run_phase2.py --cost-cap 100

To monitor (in a separate terminal):
  tail -f /Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/results/phase2/overnight.log

To watch IM confer transcripts (in another terminal):
  watch -n 5 'python3 /Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/im_service.py read --recent 5'


FILES
-----

  bench/run_phase2.py          — experiment orchestrator (confer-enabled)
  bench/run_benchmark.py       — core API harness (all providers, retry, throttle)
  bench/evaluate.py            — scoring pipeline
  bench/report.py              — results reporting
  bench/tasks_frontier/        — 25 frontier tasks (ft-001 to ft-025)
  bench/directives/            — domain-specific CE directives
  bench/results/phase2/        — output, checkpoint, cost ledger
  bench/EXPERIMENT_PLAN.md     — THIS FILE
  bench/FINANCIAL_LEDGER.md    — all outlays and subscription tracking


PHASE 1 RESULTS (Baseline / Floor Test)
----------------------------------------

Phase 1 established that CE does not HURT and provides marginal improvement
on easy tasks. Ceiling effect confirmed: 90-100% baseline detection, 0-12.5pp
improvement. Necessary but insufficient — floor test only.

  Config              Control → CE    Delta
  ------              ----------      -----
  Sonnet 4            95% → 100%      +5pp
  Sonnet 4 thinking   97.5% → 100%   +2.5pp
  GPT-4o              90% → 100%     +10pp
  o3-mini             95% → 100%     +5pp
  Llama 3.3 70B       87.5% → 100%  +12.5pp
  Gemini Flash        (Phase 1 complete, scoring pending)
  Gemini Pro          (Phase 1 incomplete — 504 errors)

Pattern: weaker models benefit more. Reasoning models benefit less.
Phase 2 tests whether this pattern holds at the frontier.

Note: Gemini Pro Phase 1 was initially reported as "incomplete — 504 errors"
but the raw data (20/20 tasks, both conditions) was recovered and scored on
2026-03-20. Both Gemini models hit 100% baseline detection (ceiling effect).


PHASE 1 COMPLETE RESULTS TABLE
-------------------------------

  Config              Model ID                     Control   CE       Delta   FP(C→CE)
  ------              --------                     -------   --       -----   --------
  Sonnet 4            claude-sonnet-4-20250514     95.0%     100.0%   +5.0pp  45→321
  Sonnet 4 thinking   claude-sonnet-4-20250514     97.5%     100.0%   +2.5pp  33→234
  GPT-4o              gpt-4o                       90.0%     100.0%  +10.0pp   6→95
  o3-mini             o3-mini                      95.0%     100.0%   +5.0pp  15→193
  Llama 3.3 70B       llama-3.3-70b-versatile      87.5%     100.0%  +12.5pp  10→165
  Gemini Flash        gemini-2.5-flash            100.0%     100.0%   +0.0pp  63→552
  Gemini Pro          gemini-2.5-pro              100.0%     100.0%   +0.0pp  95→437

Notes:
  - All models achieve 100% detection under CE (ceiling effect — tasks too easy)
  - False positive counts increase under CE due to multi-pass iteration
  - Gemini models already at 100% baseline — no room for improvement
  - Phase 1 confirms CE does not HURT; Phase 2 tests whether it HELPS at frontier


ROUND-ROBIN DISTRIBUTED COMPUTE TEST
-------------------------------------

Sequenced AFTER the Phase 2 main run (steps 1-6 above). This is the full
distributed compute test against the benchmark — not a convergence check.

PURPOSE:
  Validate the biodiversity hypothesis at scale on the frontier task set.
  The three-architecture review (March 2026) found that heterogeneous
  architectures discover different defects — 16 novel issues from Gemini
  that 8 rounds of CC/CX missed. The round-robin tests whether this
  generalises from code review to the full 25-task frontier set across
  all five categories (proof, code, design, synthesis, self-referential).

PROTOCOL:
  Three architectures rotate as generator → falsifier → arbiter:

  Round 1: CC generates (Schema A, passes 1-3) → Gemini falsifies → CX arbitrates
  Round 2: Gemini generates → CX falsifies → CC arbitrates
  Round 3: CX generates → CC falsifies → Gemini arbitrates

  Each round:
    1. Generator produces solution under full CE directives
    2. Falsifier receives solution + adversarial brief (fresh context, no
       access to generator's intermediate passes)
    3. Falsifier runs independent P-passes against the solution
    4. Arbiter receives both outputs, assesses convergence via confer protocol
    5. If arbiter finds novel issues neither caught → additional pass
    6. Confer-mediated termination (same protocol as Phase 2 main run)

  Stopping condition:
    All three architectures agree (via confer) that diminishing returns
    have been reached on a given task. Irreconcilable disagreements are
    deferred for human review with full reasoning logged.

TASK SET:
  Same 25 frontier tasks as Phase 2. Results directly comparable.
  Schema C cross-model results (step 6) provide the two-model baseline;
  the round-robin extends to three-model full rotation.

MODELS:
  CC:     Claude Opus 4.6 (via Claude Code CLI)
  CX:     Codex 5.3 (via Codex exec)
  Gemini: Gemini 3.1 Pro (via API, google-genai SDK)

  Constraint: sequential execution (M1 Mac, 8GB). No parallel API calls.
  Each round completes fully before the next begins.

MEASUREMENT:
  1. Per-round detection: what did each architecture find that others missed?
  2. Convergence curves: per-task, per-category, per-architecture
  3. Novel-issue rate: does the Nth architecture still find issues after N-1?
  4. Category correlation: does biodiversity matter more for some task types?
  5. Diminishing returns profile: where do complementary blind spots exhaust?
  6. Cost efficiency: marginal cost per novel finding by round

DATA RECORDING:
  All results stored in bench/results/round_robin/:
    - rr_round{N}_{task_id}_{role}.json — per-task, per-role output
    - rr_confer_{task_id}.json — confer transcripts (all three assessments)
    - rr_convergence.csv — per-task convergence metrics
    - rr_summary.json — aggregate results across all rounds
  IM service logs all confer exchanges (queryable via im_service.py).

BUDGET:
  Gemini API: within existing £10 cap (est. ~£3-5 for 25 tasks × 3 rounds)
  CC/CX: CLI subscriptions, zero API cost
  Total additional: ~$5-10 beyond Phase 2 main run

SEQUENCING (within overall plan):
  This is step 6.5 — after Schema C cross-model pairs (step 6), before
  the Grandslam confer (step 7). The Grandslam then covers ALL results:
  Phase 2 main run + Schema C + round-robin.

  Updated sequence:
    1-5. (unchanged)
    6.   Schema C cross-model pairs on 10 tagged tasks
    6.5  Round-robin distributed compute test (25 tasks × 3 rounds)
    7.   Grandslam: CC/CX/Gemini full confer on ALL results via IM
    8-10. (unchanged)
