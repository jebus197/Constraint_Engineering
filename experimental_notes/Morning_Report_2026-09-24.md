# Morning report — 24 September 2026

24/09/2026, 02:45 BST. Written overnight on a frozen tree. Two free panel rounds, no paid dispatch.

---

## 1. The prose-scoring flag admitted every harmful fix

**Verdict on the design as built: DOES NOT ACHIEVE its objective.** Both free seats agreed, independently.

Producer: [`scripts/a19_flag_admits_harmful_fixes_2026-09-22.py`](scripts/a19_flag_admits_harmful_fixes_2026-09-22.py), driving `_evaluate_sk_for_findings` over the 5 adversarial STEM fixtures the project already keeps.

| flag | harmful fixes | verdict | R_k |
|---|---|---|---|
| off | 5 of 5 | NO_SCORE | holds 0.5000 |
| **on (before)** | **5 of 5** | **ADMISSIBLE** | falls to 0.3667 |
| **on (after)** | **0 of 5 admitted** | 3 REJECTED, 2 NO_SCORE | held |

Harmful sk before the fix: 0.5333, 0.8333, 1.0000, 1.0000, 0.7333 — every one above break-even `S* = √23161/38 − 7/2 ≈ 0.504931`, confirmed on SymPy and Wolfram Language. Property 1 of `bench/tests/test_prose_acceptance_stem.py` ("a harmful fix is never admitted", :317) failed 5 of 5; Property 2 ("an unmeasured fix may not move R_k", :429) failed 10 of 10.

**The suite passed 175 of 175 throughout, because 0 of its tests set the flag.** It executed one configuration of two. It now runs 275 tests with 9 setting the flag.

**Two causes, both real.** `_scoring_prose` ([:11006](bench/reference_runner_v3.py:11006)) is computed from the TARGET, so one fenced listing puts every fix on the scored path — the gate's own comment at :13175 claimed a per-fix decision and was measured false. And the gates were *not* blind: they fired on 3 of 5 harms, and the arithmetic mean dissolved the hard negative. On prose only 2 gates are available, weighted 1 and 2, so `inf E = 1/3` given clean ruff; executed at 1, 2, 5 and 20 new HIGH bandit findings, all scored ≥ 0.3 and all were admitted. **The security gate alone could never reject.**

**Removal recorded with its measurement.** Both seats wrote a branch under the identical guard, so applied together the second was unreachable. Survivor chosen on a named property — *convictions recorded on harmful fixes*: survivor 3 of 5, removed branch 0 of 5. The removed branch's requirement is kept as `_prose_one_sided["computed_sk"]`.

**Known limit, stated.** The extractor sees Python inside a python-tagged fence. Mathematics in prose is invisible — 9 of 12 computable-bearing prose documents blind. The founder's scenario is only partly served, and widening the extractor is separate, unstarted work.

---

## 2. The FFAFP trace detector had been dead for 2 days

Root cause: the 2026-09-20 16:42 edit added a `scans` key to `new_turn()` and 2 direct reads, while the live state held an `open` turn from the previous version. KeyError on the first tree-scan, swallowed by a blanket `except: pass`, and `state["offset"]` froze at **170431649** — the exact value found in the live state file. Its history ends 2026-09-20T15:33:07.152Z.

**Why this is worse than an ordinary bug:** the failure was indistinguishable from health. The same false-negative shape as the 16-of-17 errored tool calls once read as results.

Repaired 3 ways: `migrate_turn()` fills every key of the current schema, read from `new_turn()` rather than typed; the blanket catch counts stalls and retains the cause; after `STALL_LIMIT = 2` consecutive stalls it **re-arms** at the end of the transcript and declares the window forfeit — *"treat this session's clean FFAFP history as ABSENT EVIDENCE, not as evidence of absence."*

**Verified live:** offset moved 170431649 → 197244516 and it immediately reported a missing P-PASS trace on CC1's own previous turn, naming 7 files.

---

## 3. The Stop gate: armed, fired, and wrong on its first bounce

`hooks/ffafp_stop_gate.py` blocks on 2 signals only — ANALYSE missing and P-PASS missing — leaves FOLLOW/FIND ungated, leaves Wolfram on the report side per the 2026-09-17 ruling, is bounded to one refusal per turn by `stop_hook_active`, and fails open.

**Its first real bounce was a false positive.** It accused 6 paths and called 2 "code": `$SP/gate_in.json` (a scratchpad file whose *resolved* path classifies as `transient`) and `.claude/settings.json` (a string inside a heredoc body, never written). Real code changes that turn: **0**. False-'code' rate on that bounce 2 of 6 = 33.3333%, Wilson [9.6771%, 70.0007%].

Cause: `classify_path` is applied to the path as written in the command text, **before shell expansion**, so `$SP/...` matches no transient prefix and falls through to its `.json` suffix. Repaired: an unresolved path returns `other`. Guarded by `bench/tests/test_ffafp_stop_gate_2026-09-24.py`, which was RED on 3 of 3 unresolved paths before the repair and carries 2 counter-tests so the repair cannot over-shoot.

---

## 4. Wolfram is now wired to CC1, not only to the seats

Measured 2026-09-22: seats used Wolfram in 6 of 6 dispatches; CC1 made 1 call in a day, after being challenged. Every mechanism built for the 2026-09-17 ruling reached seats through the dispatcher's SYSTEM prompt; none reached CC1.

Repaired: the detector carries `stem` into its history and emits a second-falsifier line when the whole recent window is Wolfram-free. And `CDSFL_SEAT`, read at [`bench/wolfram_standard.py:420`](bench/wolfram_standard.py:420) and set by nothing, is now set at both launch sites — every gate-log row previously read `unknown`.

---

## 5. Harvest: the instrument reached 1 destination of 3

The 2026-09-17 fix (sandbox → `bench/logs`) is **vindicated**: 20 of 20 pre-fix CLI-seat runs have no archive, 0 of 8 after it, Fisher exact p = 3.217395e-07, Wolfram agreeing to 4.8e-14. What was never built is `bench/logs` → working tree.

The instrument now covers `sandbox_harvest`, `worktree_harvest` and `panel_worktree_harvest` at full depth, content-addressed — path-addressing had reported 5 false losses on correctly relocated files. **15 files promoted, tested, and folded forward**, including 7 nested mathematical falsifiers the old one-level glob could never see. Remaining: 16 of 73 = 21.9178%, Wilson [13.9661%, 32.6773%]; statsmodels, mpmath@50dps and Wolfram agree to 0.00e+00.

---

## 6. Routing

`max_rungs` sat at exactly 2 against a roster of 5 with no config surface and no override at its single call site, so rungs 3+ were unreachable by construction in every archived run. `routing_max_rungs` now exists on `RunnerConfig`, threaded **only when it differs from the default**, so all 23 routing-enabled configs stay byte-identical and 4 test files' narrow `fake_route` stubs keep working.

Dynamic capability routing is **not built and cannot be grounded today**: capability fingerprinting measures context capacity, not falsification competence, and 0 of 10 model pairs separate (all Fisher p ≥ 0.306). The named trigger is recorded beside the field.

---

## 7. The suite, and what CC1 broke

Measured at `b48dcb9` on a frozen tree: **8553 passed, 47 failed**, 1885.45 s, exit 1. Worse than Tuesday's 24. Promoting 15 seat-written files brought their defects with them.

Closed since, each verified by running the guard: **17 operational-script failures** (13 sharing one cause — a module-level help answer reads the *host's* argv, and the probe imports by passing the script's own path; guarding it with `__name__ == "__main__"` fixes all 13 and leaves `--help` working), **8 routing failures** (my unconditional keyword against narrow stubs), **1 secrets test** (a NameError I introduced at a call site I never exercised — the test's complaint was that dispatch was never reached, so nothing was checked), plus the documentation-drift and full-record guards.

Still red and correct to be: the 2 paid-dispatch guards, which only the founder can clear. Pre-existing and unrelated: the latent-control pair (instrument committed 2026-09-01 against an archive ending 2026-08-27) and round 11's brief figure.

---

## Producers

`scripts/a19_flag_admits_harmful_fixes_2026-09-22.py`, `scripts/a19_prose_gates_are_one_sided_2026-09-22.py` (the "3 of 5 harms actively rejected; 0 of 5 correct fixes rejected; every NO_SCORE held R_k" figure in section 1), `scripts/a19_veto_only_prose_sk_2026-09-22.py`, `scripts/ffafp_liveness_check_2026-09-22.py`, `scripts/panel_harvest_loss_2026-09-22.py`, and the 7 recovered derivations under `scripts/cc_free_seat_2026_09_21/`.

Guards: `bench/tests/test_prose_gates_are_one_sided_2026-09-22.py`, `bench/tests/test_ffafp_dead_detector_2026-09-22.py`, `bench/tests/test_ffafp_state_migration_2026-09-22.py`, `bench/tests/test_ffafp_stop_gate_2026-09-24.py`, `bench/tests/test_routing_max_rungs_is_reachable_2026-09-24.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
