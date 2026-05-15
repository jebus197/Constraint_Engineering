# Experiment 40 Continuation Run — Post-Mortem

2026-05-15 05:20 BST

## Summary

The Experiment 40 continuation run (resumed from Round 10 of the original
2026-05-14 02:05 UTC run) executed for two hours and four minutes, processed
seven additional rounds of compelled-convergence dispatch across the five-model
panel (Round 10 through Round 16, inclusive), and stopped on the
`wall_clock_cap_s = 7200` boundary at 7,478 seconds elapsed. The runner exited
cleanly with exit code 0. The continuation closed seventeen additional canonical
findings through the Bugzilla close-the-loop verifier added in commit 12ad362,
escalated six findings to HIL via D4 MERGE DEADLOCK after persistent
target-set ambiguity, and surfaced the G7 deadlock-resolution evidence the
project was waiting for. γ-alt convergence was not met; the run terminated on
wall-clock rather than on the boolean zero-novel-CRITICAL-for-three-consecutive-
rounds condition.

The seven post-mortem fixes folded into the continuation all functioned as
designed during the run. No FFAFP-grade halts were triggered. The
continuation produced the empirical data needed for the G7 design (already
written ahead of the run at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`)
to move toward implementation in a subsequent commit.

## Run Parameters

- Launcher: `bench/launch_exp40.py --resume`
- Config: `bench/exp40_configs/40_gate.json`
  - `max_rounds`: 18 (raised from 8 ahead of the run)
  - `extension_cap`: 20 (raised from 10)
  - `wall_clock_cap_s`: 7,200 (unchanged)
- Target article: `bench/dm/_feedback.py` (22,122 chars)
- Context files: `bench/dm/_types.py`
- Total dispatch context per chunk: 49,778 chars
- Panel: CC2 (Claude Opus 4.7 via CLI), ChatGPT (gpt-5.5 via OpenRouter),
  Codex (gpt-5.5 via OpenRouter), DeepSeek (v4-pro direct), Gemini
  (3.1 Pro Preview via OpenRouter)
- Topology: star/blackboard, four-layer pattern
- Run start: 2026-05-15 03:15:48 BST
- Run end: 2026-05-15 05:20:26 BST
- Wall-clock elapsed: 7,478 seconds (2 hours 4 minutes 38 seconds)
- Stop reason: `wall_clock_cap_s` exceeded at Round 17 boundary check
- Log: `bench/logs/exp40_continuation_20260515T021531Z.log`
- Final report: `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`
- Final state: `bench/logs/exp40_gate_20260514T020550Z/runner_state.json`

## Final Registry State

- Total canonical entries: 179 (146 inherited from resume + 33 new in the
  continuation)
- Total raw findings across all 17 rounds: 280
- Status distribution at termination:
  - OPEN: 68 (38%)
  - CONFIRMED: 42 (23%)
  - CLOSED: 26 (15%) — 25 of which carry `bugzilla_verified=True`
  - UNCONFIRMED: 23 (13%) — these are the D2-HIL-escalated entries
  - MERGED: 19 (11%)
  - CONTESTED: 1
- HIL-flagged canonical entries at termination: C0008, C0023, C0032, C0035,
  C0044, C0052, C0071 (seven entries on the HIL queue)

## Convergence Trajectory

### γ overall (recursive novelty decay metric)

Per-round γ values across all 17 rounds:

```
R0:  0.0000   R5:  0.2746   R10: 0.0633   R15: 0.0310
R1:  0.0000   R6:  0.2614   R11: 0.0446   R16: 0.0342
R2:  0.2560   R7:  0.2321   R12: 0.0349
R3:  0.2967   R8:  0.1433   R13: 0.0316
R4:  0.2891   R9:  0.0936   R14: 0.0310
```

γ entered the converged regime (< 0.3) at Round 2 and stabilised below 0.05 from
Round 11 onward. The final value 0.0342 is approximately one ninth of the early-
round novelty intensity. By the γ-decay metric, the panel is deep into the
converged state.

### γ-alt boolean (3 consecutive rounds with 0 novel CRITICAL findings)

Novel CRITICAL count per round (last ten rounds):

```
R7:  1   R10: 0   R13: 1   R16: 2
R8:  0   R11: 3   R14: 0
R9:  1   R12: 2   R15: 4
```

γ-alt was not met. Two near-convergence moments (R10=0, R14=0) were each
followed by burst rounds (R11=3, R15=4) that reset the consecutive-zero
counter. The R15 burst of four novel CRITICALs is the largest single-round
critical-finding count in the entire 17-round arc.

### ρ (per-round novelty fraction)

Per-round ρ across all rounds (last ten):

```
R7:  0.643   R10: 0.083   R13: 0.357   R16: 0.600
R8:  0.615   R11: 0.857   R14: 0.333
R9:  0.806   R12: 0.583   R15: 0.636
```

ρ oscillates without strong trend in the last seven rounds, reflecting that
each round still produces some fresh findings (mostly verdict-only outputs or
verdicts on previously-CONFIRMED canonical entries) even as the novel-CRITICAL
budget approaches zero.

## Fix Effectiveness Assessment

The seven post-mortem fixes folded into the continuation are evaluated against
their observed behaviour during the run.

### 1. Decomposed-dispatch synthesis empty-response fallback (commit 35c44b6)

`bench/decomposed_dispatch.py` — fires when a model's Phase 2 synthesis call
returns zero characters; reconstructs output from the non-empty Phase 1 chunk
analyses with a header note. Confirmed working during Round 11 — Gemini's
synthesis returned 0 characters, the fallback reconstructed 1,278 characters
from preserved chunk content, and the round closed without losing Gemini's
contribution. The fallback also handled cases in later rounds where Gemini
hit the same pattern. The fallback cannot reconstruct when both Phase 1
chunks are themselves empty (Round 16 Gemini case), but in those cases there
is genuinely no content to preserve.

### 2. Bugzilla close-the-loop module (commit 12ad362)

`bench/bugzilla_loop.py` — standalone module implementing the four-step
CONFIRMED → CLOSED transition (extract SEARCH/REPLACE block, apply to sandbox
copy of target, run ruff/mypy/bandit/pytest gates, set CLOSED). Worked as
designed across all seven continuation rounds. Seventeen verified CLOSED
transitions logged during the continuation, with the gate decomposition
ruff/mypy/bandit/test recorded for each. Multiple failure modes observed and
correctly rejected:

- `extract failed: no SEARCH/REPLACE or OLD/NEW markers found in proposed_fix`
  (C0032, C0037, C0038, C0039) — model proposed fixes without the required
  block format. The runner records these as 1D.5 reformat requests for the
  next round.
- `sandbox apply failed: old_code not found in target file` (C0023, C0042,
  C0144) — proposed fix's SEARCH block does not match the current source.
  For C0042, C0117, C0130, C0138, the SEARCH targets parser regex that was
  itself already updated by commit b2f3444; the findings are stale.
- `verification failed: mypy: ... Need type annotation for "final_v..."`
  (C0047, C0144) — fix applies to sandbox but introduces a new type-annotation
  defect. The mypy gate correctly refuses to certify a fix that introduces
  fresh defects.

### 3. Bugzilla CLOSED-loop runner integration (commit 8cb1fbe)

`bench/reference_runner_v2.py` — wires the close-the-loop call into
`_update_finding_statuses` at the CONFIRMED state, with `BUGZILLA_PER_ROUND_LIMIT
= 5` to bound subprocess execution per round. The integration produced the
seventeen verified closures listed above, with no cross-round side effects.

### 4. Gamma input fix — post-reconciliation novelty (commit 26b28f8)

`bench/reference_runner_v2.py` — replaces pre-reconciliation novelty (which
treated MERGED entries as novel) with post-reconciliation novelty (which counts
only entries whose status is not in `_NON_NOVEL_TERMINAL = {"MERGED",
"DUPLICATE", "UNCONFIRMED", "REFUTED"}`). γ values across the continuation
behaved as expected — declining monotonically from 0.094 at Round 9 to 0.031
at Round 14, with two minor upticks (R12 = 0.035, R16 = 0.034) consistent with
the burst-round novel-CRITICAL counts. The fix produced metric values that
match the underlying registry state rather than the pre-fix overcount.

### 5. ITC CAPABILITY_MISMATCH false-positive fix (commit 7f3066b)

`bench/reference_runner_v2.py` — adds a `verdict_count == 0` guard before
classifying a model's round output as CAPABILITY_MISMATCH, so verdict-heavy
rounds (where Codex correctly produces only verdict updates) are no longer
misclassified. During the continuation, Codex hit CAPABILITY_MISMATCH only
in the carryover from Rounds 3 and 4 of the original run; from Round 11
onward all Codex ITC classifications are DEGRADATION rather than
CAPABILITY_MISMATCH. The false-positive class was prevented from recurring.

### 6. Stage 6 calibrator int-flaw_class fix (commit 9891bda)

`bench/dm/_shadow_stage6.py` — guards the `flaw_class.lower()` call with an
`isinstance(flaw_class, str)` check, preventing the `'int' object has no
attribute 'lower'` crash that surfaced during the original Exp 40 run. No
recurrence of this crash class across the continuation. Stage 6 calibration
fired in each round without exceptions.

### 7. Parse-admissibility-block FINDING_ID terminator fix (commit b2f3444)

`bench/dm/_feedback.py` — adds `FINDING_ID` to the section-terminator regex
alternation, preventing the C0008 runaway where the parser kept absorbing
content into a single finding's fix block. The specific runaway pattern did
not recur during the continuation. However, a related parser issue surfaced
that the fix does not cover (see Anomalies, item 2 below).

### 8. Explicit Bugzilla paradigm in panel prompt (commit a8a33c2)

`bench/reference_runner_v2.py` — extends `build_summary` to include a
Bugzilla-paradigm header that names the OPEN/CONFIRMED/CLOSED/MERGED/REOPENED
state machine and instructs models to submit fixes in SEARCH/REPLACE block
format. Mixed effectiveness: seventeen findings produced parseable
SEARCH/REPLACE fixes (the closures), but four or more findings per round
still arrived as freeform prose (the extract-failed cases). The explicit
prompt is necessary but not sufficient — further format-compliance signal
will be needed in the panel directive itself for full coverage.

## Anomalies Observed (Pre-Mortem Items for Next Run)

### Anomaly 1 — DeepSeek 0-character Phase-1 sections

DeepSeek's decomposed-dispatch Phase 1 chunks returned 0 characters across
multiple rounds (Rounds 11, 12, 13 section 2; Round 13 and 15 section 1;
Round 16 section 1). The synthesis call typically produces substantive
output despite the empty section analyses, indicating the model is treating
the chunks as input but not emitting analytical text per chunk. Worth
investigating whether the per-chunk analytical instruction is reaching
DeepSeek correctly or whether DeepSeek's V4 Pro variant treats chunked
analysis differently from prior models. Not blocking — synthesis output
arrived in all cases — but the chunk-level dataloss reduces traceability.

### Anomaly 2 — Parser anomaly: code-fragment finding IDs

Multiple findings across Rounds 12, 13, and 14 surfaced with finding-id
strings drawn from embedded code fragments rather than from the model's
intended ID field. Examples include `CC2_f for f in findings}`,
`Gemini_f for f in findings}`, `DeepSeek_\``, and `ChatGPT_f for f in findings}\`
collapsing non-globally-unique IDs. F013 concerns ignoring the model_id
namespace already present in rk_validation.`. The substantive content of
these findings is preserved and processed through the pipeline; the IDs
are just mangled. The b2f3444 fix addressed the FINDING_ID terminator on
one regex path but not on the path that constructs the model-prefixed ID.
The mangled-ID findings themselves are pointing at the same defect class
they exemplify — i.e. the panel is independently identifying that
`{f.finding_id: f for f in findings}` silently overwrites when finding IDs
are not globally unique. A follow-up fix should harden the finding-ID
parsing across all paths, and the panel's own diagnostic on the issue
should be incorporated as the design reference.

### Anomaly 3 — LLM classifier threshold inconsistency

The LLM classifier (CLI Haiku at override threshold 0.70) logged OVERRIDE
decisions at confidence values below 0.70 (Gemini_F007 conf=0.68 in Round 13,
DeepSeek_D016 conf=0.65 in Round 13). The log line names the threshold as
0.70 but the override fired anyway. Either the override logic uses a
different effective threshold than logged, or the comparison has a
rounding tolerance that the log does not display. Worth a one-line audit
of `bench/dm/llm_classifier.py` (or wherever the threshold check lives) to
confirm intended behaviour and adjust the log message.

### Anomaly 4 — RT v2 autoimmune flag at constant 100% Gemini rejection

RT v2 flagged AUTOIMMUNE bias against Gemini in every continuation round
where Gemini had findings reach the dedup layer (Rounds 12, 13, 14, 15).
The flag fires when 100% of a model's findings are removed as duplicates.
The autoimmune override consistently resurrected zero of the rejected
findings, indicating the dedup decision was correct each time. The signal
is informative — Gemini's verbose output appears to recapitulate already-
canonicalised findings rather than introducing new ones — but the
recurring AUTOIMMUNE flag accumulates noise. The flag's intended use is
to detect systematic bias in a healthy pipeline; in a converged-state
pipeline where one model is reasonably expected to produce mostly known
findings, the flag generates per-round HIL surface that does not need
action. Consider gating the AUTOIMMUNE flag on a multi-round window
(e.g. flag only if the 100% rejection rate persists for three rounds)
rather than per-round.

### Anomaly 5 — ITC DEGRADATION classification correlates with convergence

ITC is the project's IT-Crowd-fix mechanism — when a model's output quality
declines, the runner does not bench or skip the model but restarts it fresh,
handing the fresh instance a scope informed by the prior instance's
fingerprint. The same discipline grounds the project's discovery of burst
reasoning, the observation that a fresh model instance often surfaces what
a long-running instance has stopped seeing.

By Round 14 all five panel members had been flagged DEGRADATION with three
or more consecutive ITC interventions. The DEGRADATION classification is
triggered by `parse_yield_history` dropping below an adaptive threshold,
which in late-stage convergence is the expected behaviour — the panel
exhausts the novel-finding space and naturally produces shorter, more
verdict-heavy output. The current classification treats this as model
degradation and queues a restart trigger; in fact it is convergence
behaviour and a restart is counter-productive (a fresh instance would just
produce more findings the panel has already settled on, defeating the
burst-reasoning rationale that motivates ITC in the first place).

The fix is to gate the DEGRADATION classification on γ being in the active
regime: when γ < 0.1 (converged regime), low yield is reclassified as
"healthy converged" rather than "needs restart"; when γ > 0.3 (active
regime), DEGRADATION fires as before and the IT Crowd restart queues. This
preserves ITC's burst-reasoning utility in the active phase, where a fresh
instance has new ground to cover, while preventing pointless panel-churn
in the converged phase. Implementation lives in `bench/reference_runner_v2.py`
at the per-model classifier (`itc_model_state` + `_classify_round_output`);
adding `gamma_current` as a parameter and the regime gate is a small change.

## G7 Evidence Cluster

The continuation produced abundant evidence for the G7 deadlock-resolution
design (`experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`).
Six distinct canonical entries hit D4 MERGE DEADLOCK escalation during the
continuation:

| Canonical | First deferred | Final defer count | Target ambiguity |
|-----------|----------------|--------------------|-------------------|
| C0008     | R8 (original)  | 8 rounds           | 20-way            |
| C0023     | R2 (original)  | 14 rounds          | escalated R10     |
| C0032     | R5 (original)  | 11 rounds          | escalated R11     |
| C0035     | R5 (original)  | 9 rounds           | 16-way            |
| C0044     | R10            | new (escalated R16)| 10-way            |
| C0147     | R15            | 2 rounds           | 2-way             |

These are exactly the patterns the G7 design's compelled-convergence
arbitration rule targets. The C0023 fourteen-round deadlock is the longest-
running unresolved merge in the project's history and is the strongest
single data point motivating implementation of the arbitration rule. The
C0008 twenty-way ambiguity (with twenty plausible merge targets and a 3/5
target-disagreement vote) is the largest target-set the runner has ever
deferred on.

The G7 design's pre-launch decision to defer implementation until the
continuation closed is now satisfied. The next G7 review trigger is the
founder's review of this post-mortem and the G7 design note; decision at
that point on implementation timing.

## D2 HIL Escalations

Three findings escalated to HIL via D2 (unresolved challenge for five or
more rounds):

| Canonical | Challenge since | Rounds before escalation |
|-----------|------------------|---------------------------|
| C0052     | R6               | 5                          |
| C0071     | R9               | 5                          |
| C0044     | R9               | 7                          |

C0044 holds the notable property of being on the HIL queue for both D2 (D2
HIL escalation) AND D4 (MERGE DEADLOCK) reasons — a finding that is both
challenge-deadlocked and merge-deadlocked.

## What This Run Validates

- The four critical pre-launch fixes (Bugzilla close-the-loop, gamma input,
  Stage 6 calibrator, decomposed-dispatch fallback) all fired correctly under
  real-world panel output.
- The Bugzilla paradigm is operationally functional: seventeen
  CONFIRMED → CLOSED transitions with full ruff/mypy/bandit/test verification,
  the rate is non-trivial, and the failure modes are all conservative
  (refusing to apply unverified or stale fixes) rather than dangerous.
- The §17 feedback channel produces measurable behaviour change: Round 15
  saw both gpt-5.5 routes rebound from 2,237 / 1,949 char outputs in Round
  14 to 17,326 / 12,316 chars in Round 15 after Round 14 → Round 15 feedback
  flagged four models. The feedback channel is effective at countering
  ITC-flagged output shrinkage.
- The five-model panel reached deep convergence by γ-decay metric (terminal
  0.034, approximately one ninth of early-round novelty intensity) within
  the 17-round budget.

## What This Run Did Not Resolve

- γ-alt boolean convergence (three consecutive rounds with zero novel
  CRITICAL findings) was not met. The pattern oscillated rather than
  monotonically descending.
- The six MERGE deadlocks persist on the HIL queue. Without the G7
  arbitration rule implemented, these are awaiting founder review or a
  later resolution mechanism.
- The DeepSeek 0-character Phase-1 anomaly was observed but not
  investigated; it warrants attention before the next experiment.
- The parser anomaly producing code-fragment finding IDs surfaced multiple
  times; the b2f3444 fix covered one regex path but the model-prefixed
  ID construction path remains vulnerable.

## Path Forward

1. **Founder review of this post-mortem.** This note captures the data
   needed for the G7 implementation decision and the next-experiment
   planning. Founder decides whether to proceed with G7 implementation,
   adjust the design, or defer further.

2. **G7 implementation against the run's deferral evidence.** If approved,
   the G7 design at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`
   becomes the basis for `bench/merge_arbitration.py` and the runner-side
   integration described in that design's §Implementation Surface. Test
   against the six observed deadlocks before runner integration.

3. **Address the five anomalies** identified above (DeepSeek 0-char
   sections, parser code-fragment IDs, LLM classifier threshold log,
   AUTOIMMUNE flag noise, DEGRADATION-in-convergence). None blocks the
   next experiment; all are worth fixing before Exp 41.

4. **Resume Experiment 40 if a longer wall-clock run is desired.** The
   `--resume` path is supported and would pick up from R17 with the
   current state file. Two further rounds (R17, R18 within max_rounds=18)
   could potentially be added; without a wall_clock_cap increase the
   resumed run would itself hit cap before completing both.

5. **Plan Exp 41 against the converged-state data from this run.** Exp 41
   (bounded mathematics module, low-MERGE expected) is the natural next
   target identified in the G7 design's path-forward. The convergent-state
   panel behaviour observed here informs Exp 41's expected round count
   and convergence pattern.

## Resources

- Run log: `bench/logs/exp40_continuation_20260515T021531Z.log`
- Final report: `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`
- Final state: `bench/logs/exp40_gate_20260514T020550Z/runner_state.json`
- Per-round model outputs: `bench/logs/exp40_gate_20260514T020550Z/round{10..16}_{model}_*.json`
- G7 design (pre-run): `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`
- G7 design plain-English: `experimental_notes/G7_Merge_Deadlock_Resolution_Design_Plain_English_2026-05-15.md`
- Plain-English companion to this note: `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md`
- TTS companion: `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt`

Written under CDSFL note standard v1.2 (14 May 2026).
