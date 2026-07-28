# Experiment 40 Timing Re-Confer (Neutral Framing) — Outcome

2026-05-16 03:30 BST

## Summary

A five-model compelled-convergence confer (Gemini 3.1 Pro, Codex
GPT-5.5, CC2 Opus 4.7, ChatGPT GPT-5.5, DeepSeek V4 Pro; star
topology; latest CDSFL schema as system prompt) re-decided three
fix-timing questions that a prior confer (2026-05-15) had answered
5/5 under leading questions. The prior round's questions presupposed
deferral; this round removed the bias, presented both competing lines
of reasoning as unlabelled defaults, tagged the working model's own
reasoning for adversarial falsification, and required any "defer" to
carry a specific technical reason plus a named experiment for
canonical-plan marking.

The neutral framing produced genuine divergence where the biased
round had produced false unanimity: Q1 split 3 NOW / 2 DEFER, Q2
split 2 NOW / 3 DEFER, Q3 split 4 DEFER / 1 NOW. No question reached
5/5. The decisions below were resolved on the technically-soundest
argument under P-pass, not by vote count, per the founder's explicit
instruction to extract a sound technical rationale by testing the
working model's logic against the panel.

## Dispatch Record

- Prompt 55,758 chars (system 11,821 + user 43,937). Background:
  full G7 design note, full `merge_arbitration.py`, full fix-tranche
  post-mortem.
- Per-model: codex 50.6 s / chatgpt 60.8 s / cc2 99.8 s / gemini
  127.5 s / deepseek 186.9 s (5,044 content + 22,398 reasoning).
  All five returned cleanly.
- Logs: `bench/logs/confer_exp40_timing_neutral_2026-05-16/`.

## Decisions (binding; recorded in consolidated plan §6c)

### Q1 — G7 enablement: DEFER to Exp 41

Vote 3 NOW (gemini, codex, chatgpt) / 2 DEFER (cc2, deepseek).
Resolved DEFER on the argument that survives falsification: the NOW
camp's safety claim ("G7 degrades gracefully to DEFER on failure")
holds only for *dispatch* failure. The candidate-set construction in
`_try_merge_arbitration` builds the candidate list from live
`registry.entries`, has never executed live (the 18 module tests stub
dispatch with hand-built candidate sets), and a bug there yields a
*wrong* ≥3/5 majority → `registry.resolve(..., "MERGED",
merged_into=WRONG)` → a silent wrong-merge that corrupts the registry
and the convergence signal R17–R21 exists to measure. That is
asymmetric against the bounded, logged, non-corrupting cost of
re-observing known deadlocks, and is the "faked-results" integrity
risk the founder explicitly named. CC2's falsification was decisive:
the Exp-41 staging is a deliberate experimental-design choice, and
the deadlock evidence makes it *more* justified (G7 will fire often
in R17–R21, so a latent integration bug is both more likely to
manifest and harder to diagnose amid live convergence dynamics).
This reverses the working model's pre-confer position (enable now);
the reversal is recorded rather than elided.

*Action at Exp 41:* set `merge_arbitration_enabled=true` in the Exp 41
config; run the §6b G7 close-criterion integration test. G7 stays
config-disabled for Exp 40 R17–R21.

### Q2 — UUID-namespace: DEFER to pre-Exp 41, collision-evidence-gated

Vote 2 NOW / 3 DEFER. The substance was confirmed 5/5: fix 1a
(structural validation) and UUID-namespace fix different bugs at
different layers; the `{f.finding_id: f for f in findings}`
collision-overwrite is a real, separate, still-open silent-data-loss
defect that 1a does not close. The timing split resolved DEFER on the
project's own Popperian discipline: the collision is real in
principle but unobserved in any run; the model-prefix convention
(`CC2_F001` ≠ `Gemini_F001`) makes a true collision require
same-model-same-fid-same-round; UUID-namespace touches every
canonical-ID keying site and would destabilise the 229-test baseline
immediately before a resume, for an unevidenced defect.

*Evidence gate (implemented this session):* an observation-only
finding-ID collision detector
(`bench/dm/_feedback.detect_finding_id_collisions`; module
accumulator `_finding_id_collisions`; cleared at experiment start by
the runner) instruments R17–R21. It records every shared-finding_id
event with a `cross_model` flag, without altering the comprehension
or any dedup/merge behaviour. 10 regression tests including the
observation-only invariant.

*Action at Exp 41 entry:* read the R17–R21 accumulator. Any
`cross_model=True` collision ⇒ implement UUID-namespace before Exp 41
(co-tested with G7). None ⇒ deferral is evidence-justified; detector
remains as a standing tripwire.

### Q3 — In-round reformat re-dispatch: DEFER to Exp 41, evidence-gated

Vote 4 DEFER / 1 NOW. Fix 1e (next-round strengthened reformat,
implemented) preserves correctness — a malformed fix is rejected and
re-requested next round, not silently incorporated. CC2's
falsification of the lone NOW case is decisive: γ-alt triggers on the
decay rate over consecutive zero-novel-CRITICAL rounds, not absolute
finding count; a one-round-delayed finding is still present for the
next round's novelty calculation, so the delay shifts timing and does
not remove findings. Permanent loss is the Q2 collision bug, not the
reformat delay. An in-round re-entrant model call inside the
reconciliation close path is disproportionate ordering/loop risk for
a timing optimisation.

*Action at Exp 41:* implement only if the R17–R21 post-mortem shows a
material residual rate of *non-stale* malformed extract failures
under 1e. Stale findings are out of scope for both mechanisms.

## CC1-Reasoning Falsification Record

The founder required the working model's own reasoning to be
adversarially tested by the panel. Outcome, recorded factually:

- **Q1:** overturned. The working model's pre-confer "registry
  mutation is not novel, enable now" underweighted that the mutation
  *call* is not novel but the *candidate-set construction feeding
  it* is, and is never-live-tested. Position reversed to DEFER.
- **Q2:** substance confirmed 5/5 (1a ≠ UUID; collision-overwrite is
  a real separate open bug). The implicit "implement both now"
  timing was not supported; resolved to evidence-gated deferral plus
  the detector.
- **Q3:** confirmed. The working model's original deferral reasoning
  was technically sound; the neutral panel reached it independently
  (4-1) with CC2 supplying the decisive γ-alt-is-decay-rate argument
  — so it was sound analysis, not framing bias.

## What This Means for R17–R21

R17–R21 restarts on the existing fix tranche (1a–1e, DeepSeek
Phase-1, gamma-input) **plus** the new observation-only collision
detector, with G7 config-disabled. Nothing risky and never-live-tested
mutates state during the headline convergence run. This serves both
stated founder goals: the fix tranche does the convergence work; the
risky merge-mutation code (G7) and the architectural change
(UUID-namespace) land at Exp 41 where failure is cheap and isolated;
and the deferrals are evidence-gated, not blind, so they cannot be
silently forgotten — §6c and the Exp 41 matrix row carry the binding
actions.

## Standing Methodology Change

Fix-timing confers must not present deferral as the baseline. The
adopted question form: "Is the fix technically sound? WHEN — now or
defer? If defer, the specific technical reason (not 'caution') AND
the named experiment, marked in §6c." The 2026-05-15 → 2026-05-16
re-confer is the worked example of why: the biased round was
unanimous defer on all three; the neutral round split every question
and reversed the working model's own G7 position under adversarial
test.

## Cross-references

- `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` §6c
- `experimental_notes/Exp40_Architectural_Confer_Outcome_2026-05-15.md`
  (the biased prior round, retained for the methodology contrast)
- `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`
- Plain-English companion + TTS:
  `Exp40_Timing_Reconfer_Outcome_Plain_English_2026-05-16.md` /
  `~/Desktop/CDSFL_tts/Exp40_Timing_Reconfer_Outcome_2026-05-16.txt`
- Confer logs: `bench/logs/confer_exp40_timing_neutral_2026-05-16/`

Written under CDSFL note standard v1.2 (14 May 2026).
