# Fable seat — full reply, verbatim

Panel round `fingerprint_ladder_review_2026-10-05`. 1108.3s, 74 tool calls, 12,711 chars, ok=True.

Preserved unedited. The founder's standing rule: review output is never summarised in place of the full output.

---

All green. I've reached the diminishing-returns point — further passes produce only sub-threshold observations. Final report.

---

# Verdict — seat Fable, 2026-10-05

Every repository claim below was demonstrated by execution in this turn; outputs quoted are from those runs.

## Part A — the 3 repairs

**A1. The rename (`answer_help` → `_parse_args` in 8 scripts): CORRECT, no guard weakened — but CC1's coverage conclusion is misstated.** Executed, not read: `test_fresh_clone_is_actually_run_2026-09-11.py::TestTheHelperIsNotUsedWhereArgparseAlreadyWorks` and all of `test_help_never_acts_2026-09-11.py` pass (12 passed). However, the sibling guard `test_every_script_that_writes_answers_help` does **not** "still cover these scripts" — it never examines them. Applying its own `WRITES` matcher to all 8: `WRITES=False` for every one, so they are **outside its population by design**, not covered-and-passing. Actual coverage was `test_help_is_answered_2026-09-11.py::TestTheWiringIsReal` — population membership confirmed for all 8 — but that vouches them **structurally** (source mentions `argparse`), and `answers_help` counts an `ArgumentParser` constructed anywhere, including inside a function nothing calls. A defined-but-never-called parser would pass every static guard while `--help` ran the measurement. I executed `--help` on all 8: `rc=0`, `usage:` first line, tree clean. **Delivered:** `bench/tests/test_measurement_scripts_answer_help_2026-10-05.py` — executes `--help` (exit 0 + usage line) and `--no-such-flag` (exit 2) on all 9 scripts (8 + my new one). 18 passed.

**A2. The swallowed exception: repair correct, and the same defect class survives one loop up — now fixed.** The leave-one-out `probe_errors` repair is sound (re-run: `probes that raised: 0`, 175/175 reproduces). But line 240–241 retained `except Exception: continue` around `reg.unverified_critical_count()` at the **run** level: a registry the counter cannot score vanished from the attribution with no trace while staying in `runs_total`, and the script still printed "the attribution is complete, not a lower bound" — a completeness claim computed from `probe_errors` alone. The suite's swallow-guard (`test_no_bare_or_silently_swallowed_exception_handlers`) only flags handlers whose entire body is `pass`, so `continue` escapes it. **Delivered:** fix in `scripts/the_blockers_are_shown_as_settled_2026-10-05.py` — `counter_errors` collected and reported; the completeness line now requires both lists empty. Re-run: 175/175 exact, guard suite passes.

**A3. `co_names`/`co_consts`: genuinely stronger than source text, but still a static reference proxy — one rung down, not a different kind of evidence.** It is immune to comments and commented-out code (a real improvement). Cases, precisely:

- **FALSE PASS (`co_names`):** the name referenced inside `run_experiment` without a reachable call — dead branch (`if False:`), a bare assignment, or a call behind a never-true flag. The compiled code object records the *reference*, not the *execution*.
- **FALSE PASS (`co_consts`):** `run_experiment`'s **docstring is `co_consts[0]`**, and any string literal (a log message) containing `"round_falsifier_reattachments"` satisfies the check after the persist line is deleted. A docstring can satisfy `co_consts` exactly where a comment cannot satisfy source-matching — the same defect class, narrower aperture.
- **FALSE FAIL (both):** a *correct* refactor moving the call or the persist into a helper (module-level or nested — nested code objects have their own `co_names`; the check does not recurse) breaks both tests. That is the "guards break on CORRECT changes" failure the census message warns about, at lower frequency.

I mutation-checked both probes myself: severing the call → `test_the_round_loop_calls_it` FAILED; deleting the persist key → `test_its_record_is_persisted` FAILED; restored, 4 passed. Note: **each mutation failed exactly 1 test, not the "2 tests fail per mutation" stated** — either CC1's mutations were coarser or the claim is overstated; the probes do catch their mutations either way. The call site is real and unconditional (line 16114). Verdict: acceptable conversions, correctly described as proxies; the behavioural form (this file's own `verdict` fixture pattern) remains the stronger standard where feasible.

**The pinned historical set: the right call.** The substring match was unsound in both directions (an id inside a `merged_into` pointer or another finding's description matched spuriously; the claim was always about status membership). Regression detection is **not** lost: the live status→section map is derived each run by calling `build_summary`, and — decisive — the repaired partition is pinned by an executing test, `test_status_partition_covers_everything_2026-08-30.py` (5 passed). The script's live print alone would be insufficient (it always exits 0); the test is what guards the regression.

## Part B — the proposal

**B1. First-pass-only is NOT sufficient, and its stated premise is false.** "A common population by construction" is wrong: each model writes first-pass falsifiers for *its own findings*, and the finding populations differ per model — χ² = 280.0138, p = 2.213e-59 (reproduced) is direct evidence. First-pass-only trades the routing confound for a self-selection confound, and it measures *demonstration of own findings*, not the ladder's construct (*resolution of others' residuals*). **Better mitigation: randomise a small audit fraction of rung assignments** and compute the shadow statistic on randomised attempts only — the only option that measures the ladder's own construct on an assignment independent of the ranking. Covariate modelling (option 3) cannot identify without the overlap randomisation provides.

**B2. The provenance gate is NOT sufficient. Demonstrated, twice.** `falsifier_style` is a source-text regex: `open("/dev/null")` as a decoy → classified `reads`; the word `open(` **in a comment** → classified `reads` (both executed). And the UNSAFE rule aggregated per *model*: 2 detached CONFIRMED + 1 reading REFUTED → `unsafe=False` (executed). A detached falsifier passes the gate by containing the vocabulary of reading. **Delivered:** per-confirmation accounting in `scripts/competence_provenance.py` (Exp 55 still exits 2 with `UNSAFE TO RANK ON`; all 13 pinned tests pass), plus the demonstration script. The regex hole cannot be fixed by text: gating requires **execution-derived provenance** (audit-hook recording of files opened during `reverify_falsifier`, or perturbed-target invariance — a verdict that doesn't change when the target does is detached by measurement). Also: `test_nothing_imports_either_script_into_the_runner` pins this script as RECORD ONLY; promoting it to a gate overturns a pinned design decision and must say so.

**B3. Yes — as a replacement, the continuous rate is the worse instrument.** Exp 42 measured the ladder's actual construct (residual resolution: 0/7 weak, 6/7 rung 1, 7/7 rung 2); a provenance-clean confirm rate measures a related but different one. Under the additive standard, a measurement of the wrong construct cannot displace a committed measurement of the right one. The supported composition: frozen order stays the decider; the shadow rate runs as **CUSUM drift detection**; an alarm triggers **re-running an Exp-42-style fixed-residual probe**; only that reorders. Rate = tripwire, probe = decider — "tools decide" applied to the ranking itself.

**B4. Yes, there is more, and one item I repaired:**
1. **The exercised ladder prefix was uniform even with the mixed bench armed.** `routing_max_rungs=2`; the top rungs are always drawn from {Codex-SIM, CC2-SIM, ChatGPT-SIM}; `DEFAULT_LADDER` mapped all three to `opus` → **0 of 6 source seats got a climb between two different models** (executed). "2 distinct models across the 5 rungs" was true and materially incomplete. **Delivered:** `Codex-SIM → fable` in `sim_dispatch_shim.py` (5 of 6 mixed — the maximum with CC2-SIM pinned to `opus`; derivation in the test docstring), pinned by `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py` with an anti-vacuity probe asserting the old map reads 0/6. All 18 pre-existing ladder tests still pass.
2. **The fingerprint store erases run provenance on every save.** All 11 files in `bench/fingerprints/` — real and `-SIM` alike — carry `experiment=study_run1b_2026-10-03`, one timestamp (executed), because `_save_fingerprints` writes back every loaded profile. The proposal's dimension would be persisted in a store where "which run measured this" is already unanswerable. Also no key contract: routing normalises `-SIM`, fingerprint consumers don't; the proposal must name the lookup key.
3. **`burst_mode="off"`: defensible as the parity default, no longer defensible as the only state.** Burst is fingerprint-driven; with a mixed bench now available, permanently-off burst leaves the burst planner in exactly the never-rehearsed state the routing ladder occupied before 2026-08-30.

All of this is written into the proposal file as an attributed review section.

**Measured facts:** all three reproduce exactly (χ² 280.013760 / 3.008403; p 2.213221e-59 / 0.6987; 0 of 3473, Wilson [0.0000%, 0.1105%]). Wolfram second check (local Wolfram Engine via `wolframscript`, attribution: Wolfram Language): Wilson upper bound 0.11048702870671313% — agrees.

## Disagreement

- **With CC1 on A1:** "the sibling guard still covers these scripts" is the wrong description. It skips them (`WRITES=False`); the rename is safe because the harm class doesn't apply, not because coverage persists. Coverage was structural-only until tonight's executing test.
- **With CC1 on B1:** mitigation 2's "common population by construction" is false, per the project's own χ² measurement. I reject first-pass-only as the recommendation and propose the randomised audit fraction.
- **With the proposal's promotion path (B3):** "shadow ranking does not distort" is the wrong promotion criterion; promotion should go alarm → fixed-residual probe → reorder. I also reject bundling with `immune_memory_enabled` absent a measured advantage of the composed work — shared machinery is a convenience, not a demonstration.
- **With the brief's framing of A3:** "2 tests fail per mutation" did not reproduce; my two mutations each failed exactly 1 test.

## What would refute me

- **A1:** output of `python3 -m pytest bench/tests/test_help_never_acts_2026-09-11.py` showing the 8 scripts in `test_every_script_that_writes_answers_help`'s offender-candidate set (i.e. `WRITES` matching them).
- **A2:** a demonstration that `unverified_critical_count` cannot raise on any archived registry shape — then the run-level handler is dead code and my fix guards nothing (it still costs nothing).
- **A3:** a mutation of `reference_runner_v3.py` that removes the *reachable* call yet keeps both wiring tests green without touching the test file — that would upgrade my "proxy" verdict to "broken proxy".
- **B2:** section 1 of `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py` failing to reproduce (it self-reports staleness via exit 1).
- **B3:** a committed measurement where the provenance-clean rate predicts residual-set resolution better than the Exp-42 probe predicts itself on re-run.
- **B4.1:** `rank_falsifier_writers` yielding a mixed 2-prefix under the old map — re-run section 4 with `Codex-SIM: opus` (the anti-vacuity test does exactly this and asserts 0/6).

## Delivered files

Modified: `scripts/competence_provenance.py`, `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`, `bench/tools/sim_dispatch_shim.py`, `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md` (appended review). New: `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py`, `bench/tests/test_measurement_scripts_answer_help_2026-10-05.py`, `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`. Final guard sweep over the amended tree: 50 passed (help guards, swallow guard, source-text census, help-is-answered), plus 18 + 4 + 18 + 36 + 13 on the targeted files.

**Termination:** stopping here under the diminishing-returns criterion. The last pass (status-partition pinning check) produced confirmation, not a new finding; remaining observations (e.g. `n_attrib = [0]` as a 1-element list, the producer's "any of them in executable code: True" line) are below threshold. One caveat on my own evidence: this sandbox had no `.git`, so git-population guards ran against a scratch index I built from the working tree — in the real checkout the populations are the committed set, which CC1 should confirm includes tonight's files.