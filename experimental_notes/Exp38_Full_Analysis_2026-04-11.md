# Experiment 38 Full Analysis

**Date:** 11 April 2026
**Experiment:** Ouroboros — system self-review of `bench/reference_runner.py`
**Duration:** 8 hours 12 minutes, 24 rounds, wall clock cap termination
**Panel:** 5 models (ChatGPT, CC2, Codex, Gemini, DeepSeek), star topology
**Terminal state:** 545 raw findings, 169 canonical, gamma 0.510, never converged

---

## What the Experiment Was

Experiment 38 was the system reviewing itself. Five frontier models examined the reference runner, the central orchestration code for the entire CDSFL bench. The runner contains the convergence logic, the finding lifecycle, the ITC adaptive recovery, the burst mode decomposition, the S_k verification pipeline, and the convergence gate. It is the single largest and most complex file in the repository.

The experiment ran for 8 hours and 12 minutes across 24 rounds before the wall clock cap terminated it. It never converged. 545 raw findings were produced, of which 169 survived deduplication as canonical entries. The gamma parameter reached 0.510 at termination, meaning the discovery rate had fallen to roughly half its initial value. All five models remained active throughout. None were removed.

## The Three Layers of Findings

This experiment produced findings at three distinct layers. The first layer is what the models found. The second is what the experiment's own behaviour revealed about the system. The third is what we found by monitoring the experiment from outside.

---

## Layer 1: What the Models Found

Six real bugs in the runner, independently corroborated by multiple models.

### Bug 1: `_compute_rho()` early return on zero raw findings (severity 0.95)

When a round produces no raw findings, the function aborts instead of computing the rolling average. This means the rolling average freezes rather than declining, which distorts churn detection. Found by Gemini and DeepSeek from round 7 onward.

### Bug 2: `contested_count()` wrong unresolved-challenge filter (severity 0.93)

It checks whether status is not equal to MERGED, but that misses all other terminal statuses like CLOSED, REFUTED, DUPLICATE, and UNCONFIRMED. Findings in those states are incorrectly counted as contested, inflating the contested count and blocking convergence. Reported by three independent models from round 3.

### Bug 3: `open_crit_high_count()` missing REOPENED status (severity 0.93)

When a finding is reopened after being unconfirmed, `build_summary` treats it as active, but the gate function does not count it. Reopened critical or high severity findings are displayed as active in the summary but silently excluded from the hard gate count. Three models.

### Bug 4: `_compute_rho()` off-by-one error (severity 0.91)

Finding indices are zero-based but round numbers are one-based, creating a systematic mismatch in the novelty rate calculation. The most widely reported bug, found by all five models independently from round 1.

### Bug 5: `RunnerConfig.__post_init__` silent override (severity 0.90)

The config validation code sets `rho_earliest_round` to a computed value, discarding whatever the user specified. Confirmed by z3 formal verification in round 22, where the B-Cell produced a grounded proof linking `earliest_stop_round` and `rho_earliest_round`.

### Bug 6: `contested_count()` hardcoded grace period (severity 0.85)

The `contested_grace_rounds` parameter exists in the configuration but the implementation uses a literal value instead. Two models, from round 5.

### Compound effects

All six bugs are consistent with the observed experiment behaviour. The contested_count bugs inflate the contested population. The rho bugs distort the novelty signal. Both feed into the convergence gate, which is why the gate kept failing on multiple conditions simultaneously.

Beyond these six, the models also produced numerous findings about code style, documentation gaps, and architectural suggestions. The immune pipeline filtered these appropriately. Zero S_k rejections were issued across all 24 rounds. The dominant S_k outcome was ESCALATE due to missing SEARCH/REPLACE blocks, which is a parser issue rather than a finding quality issue.

---

## Layer 2: What the Experiment Revealed About Itself

### Phase 0 convergence override bug (root cause of non-convergence)

Burst mode was active with six phases plus integration, giving a theoretical 56-round budget with 8 rounds per phase. Each phase is supposed to get tighter convergence criteria, with `earliest_stop_round` set to the phase's round offset plus 3, and `consecutive_rounds_required` set to 2. But these overrides are only applied when the runner transitions between phases. Phase 0 never transitions because the runner checks for convergence before checking for phase transition, and Phase 0 runs with the base config `earliest_stop_round` of 12, not 3. Phase 0 consumed the entire experiment. Phases 1 through 5 were never reached.

### Gamma dynamics

Gamma rose from zero to 0.377 in the first 6 rounds, crossed 0.45 at round 8, and then climbed at roughly 0.004 per round for the remaining 16 rounds, reaching 0.510 at termination. The flattening of the gamma curve above 0.45 is characteristic of topic depletion. If the Phase 0 override had been in place, convergence would have been attempted from round 3, and the experiment would have moved to Phase 1 long before gamma reached 0.45.

### Sawtooth novelty

From round 7 onward, novelty alternated between burst rounds and zero rounds in a remarkably stable pattern. Burst rounds produced 9, 17, 12, 7, 8, 5, 4, 7, and 6 novel findings. Zero rounds produced exactly 0. This sawtooth is caused by the runner's multi-topic scope. Models cycle through topic areas within the runner code. When a model hits a topic it has not yet catalogued, it produces a burst. On the next round, the same model revisits already-catalogued topics and produces nothing new.

From round 16, the strict alternation broke down. Rounds 16 and 17 were consecutive bursts. Round 19 produced a spike of 7 novel findings from only 12 raw, a 58% conversion rate and the highest since round 2. This suggests the models found a genuinely new topic vein late in the experiment. The final round, R23, produced 6 novel findings at gamma 0.51, demonstrating that novelty is still extractable even at strong depletion.

### Contested deadlock

Contested findings were a persistent convergence blocker throughout the experiment, ranging from 4 to 12 in any given round and never reaching zero. The convergence gate requires contested equals zero. Twelve specific findings were permanently stuck in MERGE DEFERRED status because models disagreed about which other findings they should merge with. No mechanism exists to break this deadlock. Round 21 was the closest the experiment came to convergence, and the only remaining gate blocker was contested equals 9. Everything else — gamma, rho, open critical high — had passed.

### Churn detection without action

The system accurately detects churn, flagging it when `rho_avg` falls below 0.25, which happened in 14 of 24 rounds. But detection feeds only into the gate as a binary blocker. There is no adaptive response. In burst mode, sustained churn is the signal that the current phase is exhausted and should transition. Without the Phase 0 override fix, this signal is detected and then ignored.

---

## Layer 3: What We Found by Monitoring

### D1: Churn detection without adaptive response

Three candidate fixes. First, in burst mode, use churn duration as a phase transition trigger. Second, feed churn into stall convergence as an additional signal. Third, when gamma exceeds 0.45 and churn persists for N rounds, relax specific gate conditions under the jointly confirmed depletion.

### D2: Contested timeout and HIL escalation

If a finding stays contested for more than 2 rounds, it should escalate to HIL with all challenge evidence and be removed from the contested count. This converts a hard deadlock into a soft boundary that drains over time. In Exp 38, this would have started clearing contested findings from R14 onward.

### D3: z3 grounding works for config-space claims

The z3 B-Cell confirmed a real bug in R22 by grounding the relationship between `earliest_stop_round` and `rho_earliest_round`. This proves formal verification can work on the runner's configuration logic, even when it struggles with most code-level claims. Config-space constraints are expressible in SMT-LIB, while arbitrary code behaviour often is not.

### D4: MERGE deadlock accumulation

Twelve findings sat in MERGE DEFERRED for the entire second half of the experiment. The current merge system requires unanimous agreement on which target to merge into. With five models each proposing different targets, unanimity never arrives. Needs either a quorum-based merge heuristic or HIL arbitration.

### D5: Gemini output format degradation

From round 22, Gemini produced findings the parser could not structure. It also consistently produced V-prefix confirmation findings with no target file, making 6 of 7 findings per round UNEVALUABLE. Gemini's output quality degrades with accumulated context length.

### D6: DeepSeek chunk delivery failures

From round 18 onward, DeepSeek consistently failed to receive chunk 1 of the decomposed dispatch. The runner retried with chunk 2 and DeepSeek still produced output, but the pattern indicates an API-level reliability issue. Both DeepSeek and Codex exceeded their coherence budgets.

### Parser and pipeline issues (P1-P6)

- **P1:** Approximately 75% of all canonical findings lacked SEARCH/REPLACE blocks, making them unevaluable by S_k. This is the dominant pipeline bottleneck.
- **P2:** CC2 produced malformed finding IDs when description text leaked into the parser.
- **P3:** Gemini mixed verdict declarations with finding declarations, creating phantom findings.
- **P4:** 22 fix verifications failed because the target file path was missing.
- **P5:** The log message for MATHEMATICAL guard retention is misleading.
- **P6:** DeepSeek's finding ID counter drifted to F100 after several rounds.

### Regex classifier mismatch

The regex classifier used to categorise findings before routing them through the immune pipeline agrees with the LLM classifier only 15% of the time for code findings. The regex categorises virtually everything as mathematical because the runner code contains comparison operators and numeric expressions. The LLM correctly identifies these as code-behavioural. This misrouting does not break the pipeline because the downstream verification tools are domain-agnostic, but it means the classification data in the finding records is unreliable.

---

## Model Performance

All five models remained active for 24 rounds. None were removed.

**HIL flags (59 total):** CC2 21 (CAPABILITY_MISMATCH), ChatGPT 13 (DEGRADATION), Codex 13 (DEGRADATION), DeepSeek 7 (DEGRADATION), Gemini 5.

**Raw finding counts:** Gemini 181, ChatGPT 133, Codex 102, DeepSeek 99, CC2 30.

Gemini produced the most raw findings but had the worst pipeline outcomes, with most findings failing fix verification due to the missing target file parser bug. CC2 produced the fewest raw findings but had the highest quality-per-finding, with several z3-confirmed results and the only consistently formatted SEARCH/REPLACE blocks. ChatGPT and Codex (both GPT-5.4) produced the most findings with valid fix blocks, accounting for most of the ADMISSIBLE verdicts.

---

## What This Means for Experiment 39

Nine fixes, ordered by impact:

1. **Phase 0 convergence override** — apply `phase_convergence_overrides(0)` at burst initialisation, not only at transitions. Without this, the experiment cannot reach Phases 1-5 regardless of anything else.
2. **Six corroborated runner bugs** — contested_count (x2), _compute_rho (x2), open_crit_high_count (x1), RunnerConfig.__post_init__ (x1). These directly affect gate accuracy.
3. **D2: Contested timeout and HIL escalation** — timeout contested findings after 2 rounds, escalate to HIL. The single biggest architectural addition.
4. **D1: Churn feedback** — make churn actionable. In burst mode, enable phase transitions when churn signals topic exhaustion.
5. **SEARCH/REPLACE parser strengthening** — dispatch prompt template and pre-check for missing blocks.
6. **Confirmation-finding parser fix** — distinguish V-prefix verdicts from new findings, require target file field.
7. **MERGE deadlock arbitration** — quorum-based merge or HIL arbitration for findings with 2+ competing merge targets.
8. **Regex classifier replacement** — replace with lightweight heuristic or make LLM classifier primary.
9. **Uninstall deprecated google-generativeai package.**

With all nine fixes applied, Phase 0 should converge within 3-5 rounds. Phases 1-5 should each get their own convergence window. Contested findings should drain via escalation rather than accumulating indefinitely. The S_k pipeline should evaluate a much larger fraction of findings. And the gamma curve should show distinct per-phase depletion rather than one long asymptotic climb.

---

## Broader Implications

The Ouroboros experiment was CDSFL examining its own implementation under its own methodology. The fact that it found real bugs is both validating and humbling. The methodology works — five models, structured falsification, immune pipeline filtering, S_k verification, and convergence gating together produced genuine, corroborated, actionable findings. But the implementation of that methodology had significant bugs that the methodology itself exposed.

The question is whether the system can close the loop — can it fix what it found and then verify the fixes by running again? That is Experiment 39's purpose. If it succeeds, we will have demonstrated a complete improvement cycle: find bugs, fix bugs, verify fixes, all under the same structured protocol.

The sawtooth novelty pattern and gamma dynamics also have implications for the mathematical model. The R_k self-assessment equation predicts diminishing returns per round, and gamma confirms this quantitatively. But the sawtooth pattern suggests the decay is not smooth — it proceeds in topic-correlated bursts. Per-element convergence is not just an optimisation but a correctness requirement. Without it, the system wastes rounds cycling through already-exhausted topics while other topics remain unexplored.

Phase B schema design, which proposes per-element convergence with each subsystem converging independently via finding taxonomy, is directly motivated by this observation. Experiment 38 provided the empirical evidence that this design is necessary.
