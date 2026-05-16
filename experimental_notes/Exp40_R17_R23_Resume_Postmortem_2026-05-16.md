# Experiment 40 R17–R23 Resume — Post-Mortem

2026-05-16 05:46 BST

## Summary

The Exp 40 resume launched after the 2026-05-16 neutral timing
re-confer ran from 03:32:53 to 05:45:27 BST (7,954 s, ~2 h 13 m,
exit code 0, final report written). It executed **seven rounds
(R17–R23)** and stopped cleanly on the round-cap (`loop_cap`)
boundary. γ-alt convergence was not met; final γ = 0.048.

The run's primary purpose — validate the post-continuation fix tranche
under live load with G7 disabled — succeeded: **all five anomaly fixes
plus the new collision detector were confirmed working in production**,
and the collision detector returned the decisive evidence for the
deferred UUID-namespace decision. Two interpretation caveats are
recorded prominently below: a round-count deviation introduced by the
operator's config choice, and a modified-target confound. Neither is a
runner malfunction; both are operator/experimental-design factors that
the convergence numbers must be read against.

## Run Parameters and Outcome

- Resume: `bench/launch_exp40.py --resume` from the R16 checkpoint
  (179 canonical entries restored).
- Config: `max_rounds=22`, `extension_cap=24`, `wall_clock_cap_s=28800`,
  `merge_arbitration_enabled=False` (G7 disabled per §6c).
- Rounds executed: R17, R18, R19, R20, R21, R22, R23 (seven).
- Stop cause: the main loop is `for round_idx in range(17, loop_cap=24)`
  — it exhausts after round_idx=23. The runner's own log line
  "ended without convergence (likely wall-clock)" is its generic
  non-convergence string and is **inaccurate here**: wall-clock cap
  was 28,800 s, only 7,954 s elapsed. The true stop was the round-cap.
- Final registry: 260 canonical entries (up from 179 at R16 — 81 new
  across R17–R23). Status: CONFIRMED 95, OPEN 64, CLOSED 40, MERGED
  32, UNCONFIRMED 29. 370 total raw findings across the full arc.
- γ tail (last 9 rounds): 0.031, 0.034, 0.040, 0.045, 0.049, 0.049,
  0.050, 0.050, 0.048 — rose slightly off the R16 floor then
  plateaued ~0.049, deep in the converged-by-decay regime.
- novel_critical tail: 4, 2, 2, 6, 10, 10, 8, 9, 15 — rising across
  R17–R23 (see Confound 2).

## Fix-Validation Evidence (the run's primary purpose)

Every fix folded in was confirmed operating correctly in production:

- **DeepSeek/Gemini Phase-1 reasoning-content fix** — **16 live
  recoveries** across the run. Each instance ("section N: content
  empty, recovered X chars from reasoning trace") is content the
  pre-fix code would have discarded as 0 chars. Recoveries ranged
  from ~2,000 to ~33,000 chars. The continuation Anomaly 1 (DeepSeek
  zero-char sections) is closed in production.

- **Fix 1b classifier log-honesty** — every OVERRIDE and skip log
  across all seven rounds used the corrected reasons
  ("llm-primary [software]: threshold N/A" for software-domain
  overrides; "llm=uncategorised: no valid reclass target" for the
  conf>threshold UNCATEGORISED skip). The self-contradictory
  "below threshold 0.70 at conf=0.88" class did not recur.

- **Fix 1c Regulatory-T v2 bias windowing** — validated in BOTH
  directions. It suppressed the per-round AUTOIMMUNE noise for
  Gemini at windowing rounds 1/3 and 2/3 (the original-continuation
  bug), then **correctly fired AUTOIMMUNE at exactly 3/3** and tracked
  the genuinely-sustained bias through 4, 5, and 6 consecutive rounds
  (4 total AUTOIMMUNE fires). DeepSeek and Codex streaks reset
  correctly when their per-round 100%-removal lapsed. `RT v1 vs v2
  flag differs (v1=False v2=True)` confirmed v2's windowed logic
  catching sustained patterns v1 misses, while not crying wolf on
  transient ones.

- **Fix 1e strengthened reformat** — `_REFORMAT` findings flowed
  through the pipeline every round, i.e. the strengthened
  next-round STRUCTURE_VIOLATION request was issued for malformed
  fixes and the models responded with reformatted output. The
  deferred in-round-dispatch decision is supported: 1e handled the
  malformed fraction without an in-round loop.

- **Fix 1a parser hardening** — no mangled / code-fragment finding
  IDs were observed across 370 findings. The structural rule held.

- **Collision detector (the §6c Q2 evidence gate)** —
  **ZERO finding-ID collisions recorded across all seven rounds.**
  This is the decisive evidence for the deferred UUID-namespace
  decision: the model-prefix convention held, no cross-model
  collision manifested. **Per §6c, the UUID-namespace deferral is
  now evidence-justified, not blind.** The detector remains in place
  as a standing tripwire for future runs.

- **G7 (config-disabled per §6c)** — the D4 MERGE deadlocks recurred
  exactly as the neutral confer predicted and accepted: C0023 reached
  21 rounds (the longest-running deadlock in project history), with
  C0008, C0035, C0044, C0147, and newly C0003/C0187 escalating. All
  bounded, logged, state-non-corrupting (findings stayed deferred).
  This is precisely the recurring evidence base that justifies
  enabling G7 at Exp 41. 12 BUGZILLA verified CLOSED transitions
  occurred in parallel — the fix-verification loop is healthy.

## Caveat 1 — Round-Count Deviation (operator config error)

The founder requested **R17–R21 (5 rounds)**. The run executed
**R17–R23 (7 rounds)** — two more than requested. Root cause: the
operator set `max_rounds=22, extension_cap=24` intending five rounds,
treating `extension_cap` as inert headroom. It is not inert: the
runner has an active budget-extension mechanism ("BUDGET EXTENDED to
24: open CRIT/HIGH: 8; contested: 2") that raises `effective_max`
toward `extension_cap` whenever open-CRIT/HIGH + contested findings
persist — which they always do here because G7 is disabled and the
deadlocks never drain. The hard ceiling `loop_cap = extension_cap`
then bounded the run at round_idx 23. Net: the run did 7 rounds, not
5; cost ≈ 2 extra rounds (~30 min, bounded API spend). This was
detected during monitoring, investigated before any intervention
(confirmed not a runaway — the `range(17,24)` ceiling held), and the
run was allowed to complete cleanly rather than be destructively
killed. **Corrective (standing):** for a precise N-round resume, set
`extension_cap == max_rounds`. "Headroom" in `extension_cap` is an
active non-convergence runway, not a safety margin. This is recorded
in the consolidated plan §6c methodology note.

## Caveat 2 — Modified-Target Confound (experimental design)

The target file `bench/dm/_feedback.py` was modified this session
(the collision detector was added to it). R17–R23 therefore reviewed
*different source* than R10–R16. The panel legitimately produced more
findings on the changed code — including registering and **validating
the detector itself** (`CONFIRM C0189 — detect_finding_id_collisions
observation-only detector is correctly implemented... no code change
needed`). This is the dominant driver of the rising novel-CRIT trend
(R17→R23: 2→15). **Consequence for interpretation: the rising
novel-CRIT count across R17–R23 is substantially an artefact of the
modified target, not pure convergence behaviour. Any R17–R23 vs
R10–R16 convergence comparison must state this confound.** The deeper
novelty-oscillation that prevents γ-alt is a separate, pre-existing
phenomenon the broader arc (and G7 at Exp 41) addresses; it is not
introduced by this resume.

## Monitoring Record

60-second FFAFP monitoring ran continuously (~135 heartbeats/events).
No FFAFP-grade pause was triggered: every signal was either an
expected §6c-predicted pattern, a confirmed fix working as designed,
or a benign network-bound wait (five proactive liveness checks, all
healthy). The one event that crossed the investigate threshold — the
"round 23 → round 24" line suggesting a possible runaway — was
investigated before any intervention and proven to be R23's closing
feedback-build, not a new round (no `Round 24/` marker ever existed;
the `loop_cap` ceiling held). Investigate-before-act was the correct
discipline and avoided a destructive kill of a healthy run.

## Path Forward

1. Founder review of this post-mortem and the
   `Exp40_Timing_Reconfer_Outcome_2026-05-16` paired note.
2. **Exp 41 entry actions (consolidated plan §6c + Exp 41 matrix
   row), now with R17–R23 evidence:**
   - Enable G7 (`merge_arbitration_enabled=true`) at Exp 41 — the
     deadlock evidence is overwhelming (C0023 at 21 rounds).
   - UUID-namespace: **deferral confirmed evidence-justified** —
     zero collisions in R17–R23. Implement only if a future run's
     detector fires; otherwise it stays deferred with the detector
     as the standing tripwire.
   - In-round reformat dispatch: still deferred; R17–R23 showed 1e
     handling the malformed fraction. Implement at Exp 41 only if
     that run's post-mortem shows material non-stale residue.
3. The round-count corrective (`extension_cap == max_rounds` for
   bounded resumes) is standing.
4. The R17–R23 convergence numbers must always be cited with
   Caveat 2 (modified-target confound) attached.

## Cross-references

- `experimental_notes/Exp40_Timing_Reconfer_Outcome_2026-05-16.md`
- `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` §6c
- `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`
- Run log: `bench/logs/exp40_R17R21_20260516T023253Z.log`
- Final report: `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`
- Plain-English + TTS:
  `Exp40_R17_R23_Resume_Postmortem_Plain_English_2026-05-16.md` /
  `~/Desktop/CDSFL_tts/Exp40_R17_R23_Resume_Postmortem_2026-05-16.txt`

Written under CDSFL note standard v1.2 (14 May 2026).
