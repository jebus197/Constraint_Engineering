# The actuator: measured scope, before any code is written

Derived 2026-11-03 from execution and source, not from the entry's prose.

## What already exists, each verified by running it or reading its own code

| component | state | evidence |
|---|---|---|
| role layer | BUILT | `has_the_bound_orchestrator_been_built_or_run_2026-11-02.py` |
| UX backend | BUILT | `bench/ux_backend_2026-10-20.py`, exposes `TABS`, `seats` |
| fix comparator | BUILT | `bench/fix_comparator.py`, 20636 bytes, exposes `compare` |
| watchdog detection | BUILT | 10 event kinds in `probe()`, AST-measured, lines 445-567 |
| events machine-readable | BUILT 2026-11-03 | this session; 7th return element + pulse key |
| review gate | BUILT | `bench/hil_review_trigger.py`, `assess()`, 2 clauses |
| the PAUSE action | BUILT | runner line 21288: checkpoint, `hil_status`, partial report, **exit 42** |
| the RESUME action | **ABSENT** | nothing drives `--resume --hil-review` |
| alarm -> pause path | **ABSENT** | the gate is consulted only from inside the runner's own loop |

`assess()`'s own docstring: *"Decide whether a human-review stop is warranted. Pauses nothing by itself."*

## The 2 candidate scopes, and why only one is built first

**(a) Inject a watchdog alarm into the review gate as a new clause.** Requires a
runner change: the gate is consulted only from inside the loop, so an external
process cannot supply a clause without a flag the gate reads.

**REFUSED FOR NOW, on B20's own measurement.** Across 8 runs carrying both a
round series and a watchdog log, **5 of 8 diverged** (gamma dipped or the gate
flipped) and **0 of 5 were alarm-silent**, 0.000000 Wilson 95% [0.000000,
0.434482]. So every observed divergence already produced an alarm. A new path
for a gap with 0 observed instances is precisely the addition that nothing
reaches, which `additive-standard`'s symmetric form rejects. And the gate
already reads `gamma_critical` and `gamma_critical_history` every round, with
`_progress_per_round` computing improvement over a window, so the narrow case
B20 describes is partly covered by `STALLED_AND_OUT_OF_ROOM` already.

**(b) Drive the RESUME of a run that paused itself.** Requires NO runner change.
Exit 42 already means "paused for review", the checkpoint is already written,
the partial report is already on disk, and `--resume --hil-review` is already
the documented continuation. **THIS IS THE SIMPLEST SUFFICIENT SCOPE** and it is
what closes the cycle `cy` names: the pause exists, the diagnosis is the
orchestrator's job, and the resume is the step nothing performs.

## The classification table, recorded rather than inferred

Each event's own message states what it means, so the table is read off the
source rather than guessed:

| event | class | why, in the event's own words |
|---|---|---|
| `STALLED` | ALARM | *"SILENCE IS NOT SUCCESS -- pause, diagnose, repair, resume"* |
| `TROUBLE` | ALARM | a matched problem line in output new since the last tick |
| `LOG TRUNCATED` | ALARM | *"doing something unusual and the operator should hear it"* |
| `WATCHDOG` | ALARM | *"cannot read the log; treating as stalled"* -- a watch fault |
| `PROCESS GONE` | BENIGN | *"the run has ended"* -- fires on every normal termination |
| `QUIET BUT WORKING` | BENIGN | explicitly the not-hung case, CPU advanced |
| `PROGRESS` | BENIGN | *"round N landed"* |
| `QUEUE` | BENIGN | at or under its bound, reported so the figure is visible |
| `BACKLOG` | BENIGN | problem lines written BEFORE the watch armed |
| `BACKLOG LINE` | BENIGN | the same, summarised |
| `ARMED` | BENIGN | startup |
| `HEARTBEAT` | BENIGN | *"alive"* |

`STALLED` names the action the actuator performs, which is why the actuator's
behaviour is specified by the watchdog's own alarm text rather than invented.

## What the actuator must NOT do

- **Not `SIGSTOP`.** The runner installs no signal handlers, and the Wolfram
  serial gate holds a machine-wide exclusive file lock, so freezing a runner
  that holds it would block every other caller on the machine.
- **Not apply a fix.** The fix belongs to the model the actuator hands control
  to, inside the sandbox his instruction requires -- and that sandbox is itself
  the gate, which is why the actuator needs no fix authority of its own.
- **Not a second pause path.** The runner's pause records its reasons whether it
  fires or not, by design; a parallel path would be a pause whose reasons live
  somewhere else.

## His constraint on the experiment, which is not the build

His instruction: the orchestrator runs in its own sandbox with an isolated copy
of the repository, which it is not told about. A model that can see the sandbox
can reason about being observed, and the behaviour being measured is how it acts
when it believes its changes are real.

Written under CDSFL note standard v1.9 (1 November 2026).
