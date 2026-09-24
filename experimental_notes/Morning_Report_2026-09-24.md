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

## 7. The suite, measured twice

| run | commit | passed | failed | seconds | note |
|---|---|---|---|---|---|
| first | `b48dcb9` | 8,553 | **47** | 1885.45 | worse than Tuesday's 24 |
| killed | `f1ec381` | — | — | — | CC1 edited a hook inside the window — 5th invalidation in a day |
| **clean** | `d193539` | **8,606** | **9** | 2292.31 | frozen tree, untouched |

**38 of the 47 closed**, each verified by running the guard rather than reading it. The rise from 24 to 47 was the cost of promoting 15 seat-written files: their defects came with them.

The largest group was 17 operational-script failures, of which **13 shared one cause and it was CC1's**: a help answer placed at module level reads the *host's* argv, and the probe imports each script by passing its own path, so the guard refused that path and the import exited 2. Guarding with `__name__ == "__main__"` fixes all 13 and leaves `--help` working. Four more were real defects in the promoted files — 2 collapsing every non-zero exit code to 1, 1 swallowing an exception into a bare `pass`, 2 printing a list cut to 5 under a heading that reads as complete.

Eight were routing failures, also CC1's: threading `max_rungs` unconditionally broke `fake_route` stubs in 4 files, and those stubs are right to be narrow — they assert on behaviour, and a stub that must grow whenever a signature gains an optional parameter is a test coupled to a signature.

One was a **NameError CC1 introduced in the secrets path**. `seat_environment(seat=model_id)` at the Codex launch site had no `model_id` in scope, because CC1 verified the function in isolation and never exercised the call site. The test that caught it guards that no secret reaches a seat, and its complaint was exact: *"subprocess.run was never reached, so nothing was checked"*. A test that cannot run is not a passing test.

**The 9 remaining:** 3 are the founder's (paid-dispatch guards, correct to be red); 3 pre-existing and unrelated (the latent-control pair, whose instrument was committed 2026-09-01 against an archive ending 2026-08-27, and an earlier round's brief figure); 3 were CC1's, of which 2 are now fixed. The last is item 8 below.

---

## 8. What the self-review found in CC1's own work, before the panel saw it

**The Stop gate's false refusal was repaired twice, and the first repair opened a hole.**

The first fix made `classify_path` return `"other"` for a path carrying an unexpanded shell variable, and the test asserted exactly that — 27 tests green — **while the gate went on refusing**, because its 3 consumers test `!= "transient"` and `"other"` still counted. *A fix verified only at the layer it edited is not verified.*

The second fix gave unresolved paths their own class, excluded by name. That worked, and **it made the gate evadable**:

```
bench/reference_runner_v3.py          -> COUNTS
$REPO/bench/reference_runner_v3.py    -> IGNORED   ← real code, evaded
${HOME}/proj/bench/runner.py          -> IGNORED   ← braced form, evaded
```

2 of 2 evasion forms succeed, Wilson [34.2380%, 100.0000%], mpmath agreeing to 5.55e-17. Introduced at ~02:55 while fixing a false alarm, and it is the worse of the two faults: a false refusal is visible and self-correcting on the next bounce; a silent evasion is neither. It also **inverts this project's own asymmetry** — `detect_target_kind` resolves every ambiguous case to the safer side, and this one was resolved to the unsafe side.

CC1's position, put to the panel to attack rather than confirm: the safe default is that an unresolved path COUNTS, accepting the false alarm, because a missed refusal costs the gate's whole purpose — but that restores the false alarm that gets such gates parked. The properly correct answer is probably neither: the hook sees the whole Bash command text and the variable is *assigned* in that text, so it can be **resolved** rather than guessed at.

**And 2 end-to-end tests CC1 wrote for the gate were vacuous.** Both ran it as a subprocess and asserted its exit code. Probed directly, `fa.scan` left `state["open"]` None and `on_close` empty, so `fa.audit` received **no turn at all** — they passed because nothing was examined. That is the substitution-tautology shape this project has caught 3 times. Deleted, the reason written where they stood, the fixture recorded as OWED.

**Still open, item 8:** 3 scripts act when imported. They write only inside a temporary directory, so nothing in the repository is touched, but the rule is right. CC1 attempted the wrap, broke 2 of 3 on a multi-line construct, restored them, and stopped rather than keep cutting at working files at 03:00. It is now a named task for the review panel.

---

## Producers

`scripts/a19_flag_admits_harmful_fixes_2026-09-22.py`, `scripts/a19_prose_gates_are_one_sided_2026-09-22.py` (the "3 of 5 harms actively rejected; 0 of 5 correct fixes rejected; every NO_SCORE held R_k" figure in section 1), `scripts/a19_veto_only_prose_sk_2026-09-22.py`, `scripts/ffafp_liveness_check_2026-09-22.py`, `scripts/panel_harvest_loss_2026-09-22.py`, and the 7 recovered derivations under `scripts/cc_free_seat_2026_09_21/`.

Guards: `bench/tests/test_prose_gates_are_one_sided_2026-09-22.py`, `bench/tests/test_ffafp_dead_detector_2026-09-22.py`, `bench/tests/test_ffafp_state_migration_2026-09-22.py`, `bench/tests/test_ffafp_stop_gate_2026-09-24.py`, `bench/tests/test_routing_max_rungs_is_reachable_2026-09-24.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
