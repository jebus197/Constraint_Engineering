# Work in progress — 2026-10-04, founder's rulings of 01:27 BST

Running state note, kept per the founder's instruction: *"take a careful note of where
you are at with each step, even if you do somehow manage to eat through my entire Max
Plan subscription allowance."* Updated as each step lands.

## Cost discipline in force from 2026-10-04 01:30
NO workflows, NO panel dispatches, NO full-suite runs. Targeted edits + targeted tests only.
Measured cause of the spike: 2 Workflow dispatches at 1,036,862 and 1,499,422 subagent
tokens (2,536,284 total), 75 Max-plan seat dispatches (2,081,722 response chars), a
711.4k session context re-sent each turn, and one badly-briefed panel that produced
0 chars across 2 seats x 2 attempts x 1800s.

## Rulings received and their state

| # | Ruling | State |
|---|---|---|
| R1 | Severity: test rubric AND worked proofs in the next runs; they may catch different things | OPEN — see Q1 below |
| R1b | Free panel review on making the severity ruler less coarse | NOT DONE — deferred, costs a dispatch |
| R2 | Withdrawal recorded in-round as a METRIC that blocks nothing | **DONE** |
| R2b | Sweep's work adopted inside the harness, not as an afterthought | **DONE** (same edit as R2) |
| R3 | Parser: extend the sentinel envelope to finding fields | QUEUED |
| R4 | Persist the gate's deciding series | DONE 2026-10-03, guarded by test_the_gate_series_is_persisted_2026-10-03.py |
| R5 | Note standard: no vagueness-by-omission; use project terms in BOTH registers | QUEUED |
| R6 | Take a reliable proof-coverage measure in the next run | QUEUED — depends on R2/R3 landing |

## Q1 — the question back to the founder on severity

He asks what the rubric does in this case, and whether the rubric and the worked proofs
catch different things, as the Haiku arm and the syntax arm did. The honest position:
NOT YET MEASURED. The Haiku case showed equal headline accuracy hiding genuine
complementarity (model-only 5, syntax-only 1). The same test has not been run for
rubric vs worked proofs. That test is cheap and does not need a dispatch: both arms
already exist in the archive. Proposed as the first measurement of the next run.

## Steps completed this session (2026-10-04)

(appended as they land)

### Step 1 — R2 and R2b landed, 2026-10-04T01:33:31+01:00

`record_in_round_withdrawals(registry, responses, round_idx)` added to
`bench/reference_runner_v3.py`, called in the round loop immediately before
`validate_round_rk`, with its per-round counts initialised beside
`gamma_critical_history` and persisted into the state payload as `round_withdrawals`.

It parses the same `WITHDRAW Cxxxx: reason` pattern the sweep already used, and records
it through `_record_computed_evidence` with `kind="reasoned_withdrawal"`, stamping
`withdrawal_round`.

**It blocks nothing, which is the ruling, and that is asserted rather than claimed.**
Executed: with C0066 at severity 0.45 and C0050 at 0.90, `unverified_critical_count()`
reads the same before and after; no status moves; `exhausted` is not set; a CLOSED
finding is skipped; an unknown id is counted and skipped; one seat repeating itself is
recorded once. Guard: `bench/tests/test_in_round_withdrawal_is_a_metric_2026-10-04.py`,
16 tests, including a mutation check that prose without the WITHDRAW token records
nothing, and a payload check that the metric is persisted.

Tests run (targeted, no full suite): 20 passed on the 2 new guards; 107 passed across
A4, gamma-alt, severity-proof, static-queue, computed-evidence and the identity-pairing
suites. 0 failures.

**Why this had to land before the next run.** On study_run1b both blocking findings
already carried `reasoned_withdrawal` evidence, written by `_post_convergence_sweep`
after `converged` was assigned. Both panel repairs read that evidence, so neither could
have changed a live run. This makes the evidence exist while the run is still going.
