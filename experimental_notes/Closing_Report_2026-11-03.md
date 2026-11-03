# Closing report, 3 November 2026: the actuator is built, and 12 of 14 of the night's errors were in instruments

3 November 2026, 06:52 GMT

This is the technical companion to the spoken closing report of the same date. It carries the file paths, line numbers and identifiers that the spoken version deliberately omits under Rule 6 of the note standard, and the same claims with the same figures.

## The actuator

`bench/tools/cy_actuator_2026-11-03.py`, 328 lines. Status under Rule 20: **BUILT and TESTED, not ENABLED**. No code path inside the harness invokes it.

It is a thin outer supervisor: it watches a launched run, classifies what happened when the run stopped, records that classification with its evidence to `actuator_decisions.jsonl` beside the run, and under `--act` re-invokes the same launch command with `--resume`. It changes 0 lines of `bench/reference_runner_v3.py`.

Entry B20 stated that releasing its hold would mean building an actuator and nothing else, the detector, the event vocabulary, the pulse file, the role layer, the researcher-facing backend `bench/ux_backend_2026-10-20.py` and the fix comparator `bench/fix_comparator.py` all having been measured as already built by `scripts/has_the_bound_orchestrator_been_built_or_run_2026-11-02.py`.

### Why it is outside the runner

`bench/tools/run_simulated_experiment.py:1066` calls `R.run_experiment(...)` in-process, inside a `try` whose only companion clause is `finally`; there is no `except`. The human-review pause raises `sys.exit(42)`, and `SystemExit` does not inherit from `Exception`, so it is not caught, propagates through `main()`, and becomes the process exit code — while the `finally` still harvests the panel worktree via `bench/panel_sandbox.py`.

The pause was therefore already observable from outside the simulated runner's own process. Anything built inside the runner would have been a second mechanism for a signal that already crosses the boundary, which `simplicity-default` excludes.

An earlier trace reached the opposite conclusion. A search truncated to its first 8 results showed `sys.exit(42)` only in `bench/reference_runner_v3.py.orig`, a stale backup, and not in the live runner — which would have meant the pause was unreachable. Re-running it untruncated found it live at `bench/reference_runner_v3.py:21298` and `:21368`, both behind `if cfg.hil_review` at `:21274`, with the flag wired at `:22494`. The apparent defect was an artefact of the truncation, which is the third occasion this session on which a limited search produced a confident wrong answer.

### The contract, as data

`ASSUMES` holds A1 to A4 and `GUARANTEES` holds G1 to G5, both module-level dictionaries. A2 records that both pause sites sit behind `if cfg.hil_review` and that the field defaults to False at `bench/reference_runner_v3.py:2308`. A3 records that exit code 42 is not a new convention, `bench/launch_exp39.py:86` already reading it as `is_hil_paused()` and propagating it at `:457`.

The declaration has 2 consumers, which is what keeps it from being decorative: `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py::TestTheContractIsReachable::test_every_guarantee_has_a_test` iterates `GUARANTEES` and fails if any guarantee is declared with no test class naming it, and `--contract` prints both dictionaries, costing nothing and dispatching nothing.

### G4 holds by construction

An `ast` pass over `classify` establishes that it compares `exit_code` exactly twice, against `PAUSED` and against 0, and that the final statement of the function is an unconditional `return` of a HOLD decision. Every exit code outside those 2 therefore reaches HOLD by construction.

Executing the classifier against 75 non-permitting exit codes, 0 of which reached RESUME, gives Wilson 95% [0.000000, 0.048724] and Clopper-Pearson 95% [0.000000, 0.047995]. That interval corroborates a structural fact rather than sampling an open space. The 2 routes are independent in the sense the primary/secondary falsifier rule requires: the first executes the function, the second reads its control flow.

### Evidence

- Guard: `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py`, 19 assertions, all passing.
- Mutations: `scripts/the_actuator_contract_mutations_2026-11-03.py`, **7 of 7 red**, Wilson 95% [0.645670, 1.000000], actuator restored byte-for-byte with sha256 compared before the exit code is decided. This is a detection rate across 7 reversions chosen by the author and may not be read as coverage.
- End-to-end against a real subprocess, not only the `_runner` seam: without `--act` it classified a real exit 42 and drove nothing; with `--act` it drove 1 resume, the resumed process completed, and the final decision was DONE.

### The precondition now has a consumer

The watchdog's `events` field, added to `scripts/cy_watchdog_2026-10-02.py` earlier the same night as the one change B20 said the actuator could not be built without, appears in the recorded decisions as `STALLED` on the pause and `CLOSED` on completion. The addition is wired rather than orphaned, which is the condition `additive-standard` imposes.

## 2 falsifications of the author's own work

**In the actuator.** With no `cy_pulse.json` on disk the decision was correct, HOLD, and the recorded reason asserted that the run's process was still alive. That was never measured: `_pid_alive(pid)` returns True when handed `None`, deliberately, so that G2 errs toward holding, and the reason reported that fail-safe as an observation. The known-alive and unknown cases now carry distinct reasons, `pid_known` is carried in the evidence, and mutation M5 guards the separation. A correct decision with a false record still corrupts G1. Recorded as `feedback_a_fail_safe_must_not_be_recorded_as_a_fact_2026-11-03`.

**In the guard.** Mutation M3 removes the resume bound, and first turned the guard red by `pytest` timing out, because without the bound `drive` never terminates. A red that depends on a timeout is the shape that killed `hooks/work_not_narrate.py` in 153 of 360 invocations.

The first repair failed, and that is the more useful half. The 2 tests in `TestG3ItIsBounded` were capped first, on the reasoning that the mutation removes the budget and those tests are named for it; the timeout persisted unchanged. The tests actually looping were in `TestG1EveryActionIsRecorded`, which fed `drive` an unconditional runner under `act=True` and had nothing to do with the budget by name. Capping by name rather than reading which test failed to finish is FOLLOW skipped on the author's own repair. After the correct fix the same mutation reports 4 failed and 15 passed in 0.38 s. Recorded as `feedback_cap_the_test_that_hangs_not_the_one_you_suspect_2026-11-03`.

## A figure quoted to the founder had no producer

`scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py`.

The `sv` commit `40f213d9` carried "10 of the night's errors were in measuring instruments" in its subject line, and an earlier draft of the spoken closing report said 9. Neither had a script behind it. 2 prose figures that disagree is `measured-rate-travels-with-its-script` violated twice.

The produced answer is **12 of 14**, 0.857143, Wilson 95% [0.600586, 0.959906], Clopper-Pearson 95% [0.571871, 0.982205]. The remaining 2 are 1 PROCESS error, where the guards were right and the fault was editing files while a commit's board read them, and 1 SUBJECT error, the actuator's false reason above.

The population is **discovered**, being the `feedback_*` memory files whose filename carries a date in the window 2026-11-02 to 2026-11-03, so a lesson added later joins the denominator. The classification is by reading and is carried per item with each item's own description quoted, because a keyword rule was considered and refused: the same night, classifying the founder's annotations by keyword counted 46 instances of the adverb "simply" as complaints about complexity, and the correction was his.

The script **refuses** to report any count when a lesson in the window has no classification, exiting 1 and naming the unclassified files. That was demonstrated rather than claimed: writing the night's 2 lessons made it decline until each was classified. Its summary line is **derived** from the buckets, after a first version hardcoded "the remaining N is a PROCESS error" while the data held 1 of each — prose failing to track its own figures, inside the script written to catch that.

What it does not establish: it counts errors that were **recorded**. An error nobody wrote down is not in the denominator, so 12 of 14 is a proportion of the night's record and not of the night's mistakes.

## Sequencing: the orchestrator experiment is not next

Read from the register rather than recalled. Ticket `72f1d6095d83` is **OPEN** and ruled 2026-11-01: 1 simulated run under full `cy` on the severity mechanics, explicitly after the severity bounds are set and before the orchestrator work.

Its predecessor's parts exist — `scripts/the_severity_bounds_from_the_archive_2026-11-01.py`, the shadow measure at `bench/reference_runner_v3.py:3890`, and `experimental_notes/data/severity_bounds_prereg_2026-11-02.json` — and the run itself has not been made. Ticket `5ed6f33304fd`, which sets those bounds, is also still OPEN.

So the orchestrator experiment is not the next experiment by the founder's own ruling, whatever the actuator's readiness, and the recommendation to run a regression experiment first should be read against that ruling rather than in place of it.

## Where the next action sits

`scripts/whose_move_is_it_on_each_entry_2026-11-02.py`, which routes an entry by a named artefact rather than by judgement: of 22 live entries, **19 have their next action with the founder**, 0.863636, Wilson 95% [0.666650, 0.952510], Clopper-Pearson [0.650878, 0.970944]; **3 are parked** and nothing more, 0.136364, Wilson [0.047490, 0.333350]; and **0 are the author's with no route**, 0.000000, Wilson [0.000000, 0.148655].

This does not say those 19 need no work. Several have the work already built and tested behind them and wait only on a ruling. It says where the next action sits, which a count of 83 OPEN tickets cannot distinguish.

Written under CDSFL note standard v1.9 (1 November 2026).
