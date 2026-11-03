# The actuator is built: a run that pauses itself can now be driven forward

3 November 2026, 06:40 GMT

## Summary

The actuator, whose absence was the single thing holding entry B20, is built and tested. It is `bench/tools/cy_actuator_2026-11-03.py`, 328 lines, a thin outer supervisor that watches a launched run, classifies what happened when the run stopped, records that classification together with the evidence behind it, and — only when explicitly permitted — re-invokes the same launch command with `--resume`. It changes 0 lines of the reference runner.

Its status under Rule 20 of the note standard is BUILT and TESTED, and explicitly NOT ENABLED: no code path inside the harness invokes it. The end-to-end that would wire it into a real experimental run is the simulated orchestrator experiment, which is paused.

## Why the actuator sits outside the runner rather than inside it

This was traced before anything was written, rather than assumed afterwards.

The simulated runner calls `R.run_experiment(...)` in-process at `bench/tools/run_simulated_experiment.py:1066`. That call sits inside a `try` whose only companion clause is `finally`; there is no `except`. The human-review pause raises `sys.exit(42)`, and `SystemExit` is not a subclass of `Exception`, so it is not caught, propagates out through `main()`, and becomes the process exit code — while the `finally` still harvests the panel worktree first, so nothing a seat wrote is lost.

The pause is therefore already observable from outside the simulated runner's own process, with no change to the reference runner at all. Anything built inside the runner would have been a second mechanism for a signal that already crosses the boundary, which the simplest-sufficient standard excludes.

An earlier, truncated version of this trace reached the opposite conclusion. A search limited to its first 8 results showed the exit code only in a stale backup file, `bench/reference_runner_v3.py.orig`, and not in the live runner, which would have meant the pause was unreachable. Re-running the same search without the truncation showed the live runner carries it at `bench/reference_runner_v3.py:21298` and `:21368`, both behind `if cfg.hil_review` at `:21274`, with the command-line flag wired at `:22494`. The apparent defect was an artefact of the truncation.

## The contract is declared as data, not as prose

The actuator declares 4 assumptions and 5 guarantees as module-level dictionaries, `ASSUMES` and `GUARANTEES`.

The assumptions are: that the run has a log directory; that it was launched with the human-review flag, without which both pause sites are unreachable because the field defaults to False at `bench/reference_runner_v3.py:2308`; that exit code 42 means paused for review, which is not a new convention since `bench/launch_exp39.py:86` already reads it that way; and that the launch command is supplied verbatim, so a resume re-invokes the same command rather than a reconstruction of it.

The guarantees are: no resume without a recorded decision carrying its evidence; never resuming while the run's own process is alive; a bound on the number of resumes; anything unclassifiable holds, with the record naming what was seen; and an append-only decision log.

Declaring this as data rather than in a docstring is what keeps it from being decorative. The declaration has 2 callers. The guard iterates `GUARANTEES` and fails if a guarantee is declared without a test class naming it, so the declaration cannot drift ahead of what is actually held. And `--contract` prints both dictionaries, which costs nothing and dispatches nothing.

## One guarantee holds by construction rather than by sampling

The fourth guarantee — that any unrecognised state holds rather than resuming — was first supported by executing the classifier against 75 exit codes other than 0 and 42, of which 0 reached a resume decision: Wilson 95% interval [0.000000, 0.048724], Clopper-Pearson [0.000000, 0.047995].

That interval is weak, and a second and independent route settles the same claim outright. A syntax-tree pass over the classifier finds it compares the exit code exactly twice, against the pause code and against 0, and that the final statement of the function is an unconditional return of a HOLD decision. Every exit code outside those 2 therefore reaches HOLD by construction. The sweep corroborates a structural fact rather than sampling an open space.

The 2 routes are independent in the sense this project requires: the first executes the classifier and observes its outputs, the second reads its control flow. This is not 2 library names resolving to 1 verifier.

## Evidence

The guard is `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py`, 19 assertions, all passing. Its load-bearing structure is a pair: the first test asserts that a resume does fire on the single state that permits it, and the second asserts that no other state reaches a resume. Either alone is satisfiable by a constant: a classifier hard-wired to hold passes the second, and a classifier hard-wired to resume passes the first. Only the pair establishes that the exit code and the liveness of the run's own process are what decide.

The mutation harness is `scripts/the_actuator_contract_mutations_2026-11-03.py`. It reverts each guarantee in turn and requires the guard to go red: 7 of 7 mutations red, Wilson 95% [0.645670, 1.000000], with the actuator restored byte-for-byte afterwards and its sha256 compared before the exit code is decided. That figure is a detection rate across 7 reversions chosen by the author, and cannot be read as coverage of the space of possible defects.

The actuator was also proven end-to-end against a real subprocess rather than only against the test seam. Without permission to act it classified a real exit code of 42 and drove nothing. With permission it drove 1 resume, the resumed process completed, and the final decision was DONE.

## The precondition built earlier the same night now has a consumer

Entry B20 named 1 change the actuator could not be built without: the monitoring watchdog emitted 10 distinct event kinds to standard output only, so no program could learn which condition had fired. That was built earlier the same night, adding the events to the watchdog's return value and to the pulse file.

The actuator's recorded decisions now carry those event kinds — STALLED on the pause and CLOSED on completion in the end-to-end run. The addition is wired to a consumer rather than left orphaned, which is the condition the additive standard imposes on any new field.

## 2 falsification findings, both against the author's own work

The first was in the actuator. With no pulse file on disk the decision was correct — hold — but the recorded reason asserted that the run's process was still alive. That was never measured: the liveness check returns True when handed no process identifier, deliberately, so that the refusal errs toward holding, and the reason reported that fail-safe as an observed fact. The known-alive and unknown cases now carry separate reasons, and a mutation guards the separation. A correct decision with a false record still corrupts the guarantee that every action is recorded with its evidence.

The second was in the guard rather than the subject. The mutation that removes the resume bound first turned the guard red by causing the test suite to time out, because without a bound the drive loop never terminates. A red signal that depends on a timeout is the shape that killed a sibling stop hook in 153 of 360 invocations: it is slow, it depends on a timeout being configured at all, and it is indistinguishable from an unrelated hang. The fake runner used by the guard now refuses past a hard cap, so a missing bound fails immediately and legibly instead: the same mutation reports 4 failed and 15 passed in 0.38 seconds.

The first attempt at that repair failed, and that is the more useful half of the finding. The 2 tests in the budget class were capped first, on the reasoning that the mutation removes the budget and those tests are named for it. The timeout persisted unchanged. The tests actually looping were in the recording class, which fed the drive loop an unconditional runner and had nothing to do with the budget by name. Capping the tests whose names matched the mutation, rather than reading which test failed to finish, is the trace step skipped on the author's own repair.

## What remains

No code path inside the harness invokes the actuator. It is the outermost layer, so there is no code caller by design, but the run that would exercise it inside a real experiment has not happened.

The founder's own ruled order places a different run ahead of it. Ticket `72f1d6095d83`, still open and ruled 1 November 2026, is 1 simulated run under the full monitoring protocol on the severity mechanics, explicitly after the severity bounds are set and before the orchestrator work. The parts of its predecessor exist: the bounds are derived from the archive by `scripts/the_severity_bounds_from_the_archive_2026-11-01.py`, the shadow measure sits at `bench/reference_runner_v3.py:3890`, and the pre-registration is `experimental_notes/data/severity_bounds_prereg_2026-11-02.json`. The run itself has not been made.

So the orchestrator experiment is not the next experiment, whatever the actuator's readiness.

Written under CDSFL note standard v1.9 (1 November 2026).
