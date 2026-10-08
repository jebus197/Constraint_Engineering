# Closing report and outstanding rulings — 2026-10-03 19:15 BST

Technical companion to `~/Desktop/CDSFL_tts/Closing_Rulings_2026-10-03.txt`. That file is the plain-English version for a non-coding reader; this one carries the paths, line numbers and producing scripts a reproducing engineer needs. Three decisions are open; everything else below is either implemented and tested, or recorded with its evidence.

---

## Ruling 1 — the severity gate in the A4 counter

**Status: [NEEDS A FOUNDER RULING]. No code changed.**

`severity` decides in **22 distinct functions across 33 live sites**, including `_settled_novelty_series` and `_corroborated_novelty_series`, which produce `gamma_critical` — the load-bearing convergence measure. It is formal in `docs/MATHEMATICAL_APPENDIX.md` as `s_k` (§4), `Sev(f)` (§7.7), `S_v(f)` (§7.8) and `η_veto` (§7.13), and it weights `L_n`.

The severity test was removed from `unverified_critical_count` (`bench/reference_runner_v3.py:2767`) in commit `6c10fe4`, **2026-09-06 16:21:48**. `experimental_notes/DECISIONS_AWAITING_YOU_2026-09-06.md` item 23 records, at **22:15 the same day**: *"ANSWERED 2026-09-06 22:15 AND THE RECOMMENDATION WAS REJECTED. He rejected both removal and the rubric swap and ordered worked proofs instead."* The commit message quotes the founder approving it; `git grep` finds that quote in only 6 tracked files — the code comment itself and 5 panel `seat_proposals.diff` files, earliest 2026-09-11, i.e. after the commit. Decision-ledger item 2, which governs, is still OPEN. No commit since has revisited the removal.

The measurement behind the removal is sound and was not made for convenience: AUC 0.464 against 0.5 for chance in the deciding band, per-assignment sigma 0.1419 (bootstrap CI [0.1241, 0.1575], 273 duplicate pairs) against a band 0.09 wide, 82 of 273 identical defects on opposite sides of 0.7 (30.04%), and the change was measured to block **more** in 36.8% of 87 archived reports and **fewer in 0 of 87**, Wilson [0.0%, 4.2%].

**The founder's own answer is the best available repair and is already built and wired.** `bench/dm/_rk_proof.py` + `_validate_rk_computation` recompute `R_k` from stated parameters; `severity_is_proven` already gates `:7509` and `:8424`. Measured on real corroboration blocks from study_run1b: **99 of 109 prove, 90.83%, Wilson [83.93%, 94.94%]**, 0 SKIP.

**The decision:** does the severity test return to the A4 counter, gated on `severity_is_proven` rather than the raw float, or does the current state stand? Caution: the removal was measured to make convergence *harder*, so restoring it moves convergence in the *easier* direction, and should be paired with the same 87-report replay run in reverse before it is trusted.

---

## Ruling 2 — which convergence-blocker repair

**Status: [NEEDS A FOUNDER RULING]. Recommendation: adopt neither yet.**

Blockers on the final post-sweep registry: **C0066** (severity 0.45) and **C0073** (0.50). Both UNCONFIRMED, `verdicts == []`, no `routing_history`, no `falsifier_code`, and both carrying `computed_evidence` with `kinds=['reasoned_withdrawal']`. `hil_has_computed_evidence` has **1 occurrence repository-wide, a WRITE at `:14231`, and 0 reads**.

Panel round 1, free seats (`cc2`, `fable`), 0 paid, records at `bench/logs/panel_blocker_round1_2026-10-03/`:

| | cc2 | fable |
|---|---|---|
| position | **B**, `composes: false` | **BOTH**, `composes: true` |
| repair site | the counter — `_handed_to_human(e)` predicate + 5th door + `handed_to_human_ids()` | the valve — `_update_finding_statuses` pre-pass 1, severity-free for UNCONFIRMED, `has_reviews` counts `computed_evidence` |
| A4 before → after | 2 → 0, gate False → True at round 8 | 2 → 1 at round 13, → 0 at round 15 |
| mutation check | 12 of 14 fail reverted, 85.7143%, Wilson [60.0586%, 95.9906%] | 4 of 9 fail reverted; 60 + 92 neighbour tests pass |

**Both independently measured that Position A alone is a no-op** — cc2 to round 100, fable to round 40 across 4 variants; A4 never moves, because `has_reviews` is False for both. cc2: *"an addition nothing reaches."*

**The fact that decides it, found after both seats reported.** `reasoned_withdrawal` is written at exactly **1** site — `:7514`, inside `_post_convergence_sweep()`, attributed by AST. The evidence both repairs read does not exist until after `converged` is assigned. **Neither repair changes a live run.** Record the withdrawal inside the round loop first; then cc2's counter-door is the simpler of the two and mirrors the existing `_integrity_violation_excluded` / `integrity_refused_criticals` pattern.

---

## Ruling 3 — round 2 scope

**Status: [NEEDS A FOUNDER RULING].** Proposed: (1) in-round withdrawal recording, which ruling 2 depends on; (2) persisting `gamma_critical_history` into the registry; (3) the parser class.

The narrow brief worked: 1224 words, both seats done in 903s and 935s. The omnibus attempt (2762 words, 9 faults) hit the 1800s cap with 0 files written — brief *size* was not the cause (briefs of 7482, 9009 and 17901 words all returned 4 seat files); the volume of requested *work* was.

**The parser hypothesis to test.** Two regimes coexist. Sentinel-delimited — `<<<CDSFL_ORIGINAL>>>`, `<<<CDSFL_CORRECTED>>>`, `<<<CDSFL_END>>>`, nonce-protected `<<<CDSFL_TARGET_BEGIN {nonce}>>>` — unambiguous by construction and emitted reliably: **45 of 48 responses, 93.75%, Wilson [83.1646%, 97.8517%]**, 330 markers. And bare regex over prose for every finding field. **Every parser fault in the record belongs to the second regime.** Extending the envelope to the finding fields, with regex retained as fallback, would close the class.

---

## Implemented and tested this session

**Identity pairing for worked proofs.** `_extract_corroboration_sections_with_ids` + identity-first pairing in `validate_round_rk`; the original extractor untouched for its 9 callers and the frozen v1 runner. The original manufactures **226 phantom sections on top of 109 real ones — 67.46%** of what it reports — by matching the bare word inside `corroboration_fit` and prose. Identity reach **104 of 109 = 95.41%, Wilson [89.7088%, 98.025%]**; safety invariant (never reports more sections than the original) holds **48 of 48**. Tests: `bench/tests/test_rk_proof_pairing_by_identity_2026-10-03.py`, 8 tests with a mutation check. Regression: 4333 passed, 1 skipped, 0 attributable failures. Producer: `scripts/rk_pairing_reach_2026-10-03.py`.

**The memory index now trims itself.** `archive_stale_memory_entries` in `scripts/cdsfl_sv.py`, wired into `_preflight_completeness` **before** the audit so a save is never refused for a condition the mechanism can clear. Window 30 days, chosen by measurement (14d/21d both free 4367 chars but would archive the live 2026-09-06 material; 30d frees 3234). Ages **only** `Project State`; standing `Feedback` entries and any entry with no recoverable date never move. Live run: chars **23,227 → 20,049** (headroom 523 → 3701), lines **185 → 168** (headroom 5 → 22), 0 broken pointers, nothing deleted, backup at `MEMORY.backup-20261003T191533.md`. Tests: `bench/tests/test_memory_index_ages_out_mechanically_2026-10-03.py`, 16 tests.

**No trimmer had ever existed.** `MEMORY_ARCHIVE`: **0 commits in the whole history**. Across 39 commits touching `cdsfl_sv.py`, 0 contain `index.write_text`, `_trim_memory`, `_compact_memory`, `_prune_memory` or `_archive_memory`. The trims were manual — `d522e66` 2026-07-03 (26.3K→17.6K) and `ddd6e4c` 2026-08-06 under ruling 7 (24,268→21,456). The founder's judgement that the sv repairs did harm is **not** supported for this file, but the pattern he named is recorded in my own commit message, `f269453` 2026-09-20: *"sv measured, printed, and exited 0 anyway. 7 of its last 13 repairs are that one shape."*

**Onboarding route.** Installer at the top of `resources/ONBOARDING.md` (named 0 times in 2944 lines before); setup row in `START_HERE.md` (0 of 124 lines mentioned it); the drifted 18-of-28 package list removed from `docs/REPRODUCING.md` rather than corrected. Guard: `bench/tests/test_onboarding_route_is_live_2026-10-03.py`, 9 tests, reads the installer's tables by execution, mutation-checked (3 of 9 fail when the route is removed).

**Two instrument defects.** `scripts/help_is_answered_2026-09-11.py` imported `_cli_help` inside a function on the assumption that `scripts/` is `sys.path[0]` — true when run, false when the test imports it, so the coverage check died before asserting. Fixed; it then caught `exhausted_marking_age_lock_2026-10-03.py` running its whole measurement on `--help`, now wired to `answer_help`. 27 tests pass. Four other new scripts were caught by `test_operational_scripts.py` for not rejecting unknown flags loudly; fixed, 8 cases pass.

---

## Corrections — claims withdrawn when execution contradicted them

1. **`gamma_critical` was 0.732, not 0.4274.** `scripts/gate_replay_on_registry_2026-10-03.py` did `d.get("gamma_critical_history") or d.get("gamma_history")` and printed the all-severity curve under the critical label. Caught by the fable seat. The substitution is now printed in unmissable terms.
2. **The deciding series is absent from the registry.** **76 of 81 archived registries lack `gamma_critical_history`** = 93.8272%, Wilson [86.3508%, 97.3347%]; recoverable from a log in only **2 of 76** = 2.6316%, Wilson [0.7247%, 9.0966%]. So **74 runs hold the gate's deciding input in no durable place at all.** Falsified against an alternative-key hypothesis: `gamma_critical_history` is the only gamma key mentioning "crit", and the 3 richer keys occur in the same 5 files. Producer: `scripts/gate_input_is_not_persisted_2026-10-03.py`.
3. **The `escalated` Fisher result (17/72, p = 1.688264e-02) was an artefact** of conditioning on a post-treatment flag — `escalated` is reset to False at `:6944` and `:6956`. Pooled truth: 24 of 24 routed went through the escalated loop, Wilson [86.2024%, 100.0%].
4. **"Sealed three ways" was wrong.** A fourth door with no severity condition exists at `:3943-3953` and fired in this run — `console.log:948`, `REOPEN C0042`, on an entry at severity 0.6 with the same shape.
5. **"52% proven" is withdrawn** — computed from the corrupted reader. True coverage on real sections is 90.83%.
6. **"107 of 150 blocked by the severity clause alone" does not reproduce** — fable gets 57 of 175 alone, 52 needing both, noting 57 + 52 = 109 ≈ 107 and suggesting the original conflated a failing conjunct with a sole cause.
7. **My brief's central framing was incomplete.** Non-convergence was overdetermined: A4 *and* a streak tail of [1, 0, 0] against 3 required. Both seats said so unprompted.

---

## Standing item, not a ruling

**48.28 GiB in 189 panel sandboxes**, of which **27 hold 48.17 GiB** and 158 are under 10 MiB. Nothing deleted and nothing will be. Founder ruling 2026-10-03: this waits until all work is verified, and he will be pointed at them and inspect manually. The useful contribution then is a read-only audit of which sandboxes hold files with no tracked counterpart, because 41 of 220 seat-written scripts have previously been found to exist nowhere else (18.6364%, Wilson [14.0451%, 24.3041%]). Recorded as `feedback_never_delete_bulk_resources_2026-10-03`.

Panel round 1's own seat evidence is preserved at `experimental_notes/seat_evidence/panel_blocker_round1_2026-10-03/` (2 cc2 files, 3 fable files), both sandboxes kept and listed in `sandbox_manifest.json`, and all 116 panel rounds are mirrored.

---

Written under CDSFL note standard v1.7 (26 August 2026).
