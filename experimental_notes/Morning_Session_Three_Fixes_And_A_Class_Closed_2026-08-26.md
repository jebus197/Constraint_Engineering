# Three agreed fixes, and the defect class underneath them

2026-08-26, 11:52 BST (UTC+1)

## Summary

Three items were agreed as unblocked work; all three are done. Following the third uncovered a fourth defect that **closes the class the second was only an instance of**. Two issues raised from a screenshot were also examined: one was real and had two layers, the other was transient but surfaced a 16-day deadline.

Full suite: **4138 passed, 1 failed, 34 skipped, 221.88 s**. The lone failure is the operational tracker's Desktop mirror, which this process cannot overwrite. Commits `ebc8f4a`, `9a2f626`, `3c1689b`, `6cbb0ea`.

## 1 — `stop_reason`: the cause was guarded by a flag that only meant "converged"

**[MEASURED]** Across all 31 archived `completion_signal.json` files, **20 carry `status: INCOMPLETE` with an empty `reason`**. In **7** the sibling `*_report.json` names the cause:

| exp | report says |
|---|---|
| 35 | `EXTENSION_STALLED` |
| 36 | `STATE_CONVERGED at round 45` |
| 37 | `STATE_CONVERGED at round 15` |
| 40 | `GAMMA_ALT_CONVERGED: gamma=0.305 >= 0.3 at round 7` |
| 40 | `HARDENED_CONVERGED (sparsity fallback)` |
| 55 | `HALTED_IRREDUCIBLE_QUEUE_ALARM` |
| 55 | `HALTED_IRREDUCIBLE_QUEUE_ALARM` |

**Mechanism.** [reference_runner_v2.py:11011](bench/reference_runner_v2.py:11011) and [:11025](bench/reference_runner_v2.py:11025) copy the cause into `brain.state.convergence_reason` **only inside `if converged:`**. [insect_brain.py:1394](bench/insect_brain.py:1394) reads that field. Every non-convergence stop therefore reached the report and never the signal.

**Correction to the record.** Last night's note said both exp55 runs produced "no final report". Wrong on the evidence, right on the conclusion — they produced a report naming the alarm and a signal naming nothing. My probe used the filename `final_report.json`; the real name is `<experiment_name>_report.json`.

**Why a third field.** `signal_complete` derives *status* from the *contents* of `convergence_reason` (`"BUDGET_EXHAUSTED" in ...`). Merging stop reasons in would make status depend on the wording of an unrelated halt. `stop_reason` leaves the status logic untouched **by construction rather than by argument**, and `test_a_stop_reason_containing_BUDGET_EXHAUSTED_still_does_not_flip_status` asserts that with adversarial wording.

12 tests including checkpoint round-trip. Four deliberate breaks (drop the fallback, drop it from the checkpoint, merge into `convergence_reason`, re-guard the runner) fail 4, 1, 1 and 1 tests.

## 2 — A test string in a canonical document, through 3929 tests

`resources/MEMORY_EXCLUSIONS.md:11` read:

```
## Accounting (counted BROKEN-STAMP ;OLD: 2026-08-26 00:53 BST)
```

`BROKEN-STAMP` appears in **no Python source anywhere** — not a fixture, not a constant. Typed by hand while checking that sv refuses to advance a stamp on a failed count, then swept into `8f9fe35`.

**Why it survived.** Three guards watch that file — in `test_documentation_drift_guards_2026-08-25.py`, `test_recovery_memory_doc_repairs.py`, and a bucket-sum assertion. All three check **numbers**. Nothing checked the **date beside them**.

The new guard in `bench/tests/test_ledger_stamp_is_a_real_date_2026-08-26.py` was **written first and failed on the real tree** (2 failed, 13 passed) before anything was repaired — a stronger falsification than a synthetic break. Repaired by sv's own recount, not by hand: stamp `2026-08-26 11:32 BST`, total 119, prose updated in step, buckets 62+15+3+39 = 119.

**sv behaved correctly at 01:28.** The memory directory was denied then; it refused to count, left the figures, and printed *"Counts and the 'counted' date are LEFT AS THEY WERE. This is a failed measurement, not a clean bill of health."* The stale 118 was the honest answer available.

## 3 — The stray file was the symptom; 99 MB was the cost

`tmpjwur6y1n.py` caught mid-run in the repo root, present in one `ls` and gone from the next.

**[MEASURED]**

```
repo-root __pycache__    17,874 entries, 70 MB — EVERY ONE named tmp*
bench/__pycache__           371 of 505 tmp*,  29 MB
```

[`_run_hard_gate_compile`](bench/reference_runner_v2.py:7718) wrote a temp `.py` into `_anchor_dir_for(source_path)` and unlinked it in a `finally` — so the `.py` was transient. `py_compile` **also writes bytecode beside it**, and nothing removed that. Root entries come from bare-filename targets (`Path("x.py").parent == "."` = CWD = repo root during a suite run); `bench/` entries come from **real runs**, whose targets live there.

**Fix.** The gate only asks whether source compiles; the builtin `compile()` answers from a string with **no file I/O**. The anchoring existed so ruff/bandit walk up to the repo config — `py_compile` walks up to nothing. The three ruff/bandit sites still write real files and produce no bytecode. Second half: `_anchor_dir_for` no longer returns `"."` for a path naming no directory; `bench/insect_brain.py → "bench"` is unchanged.

**95 MB reclaimed**; 134 genuine module caches kept. 15 tests, the load-bearing one snapshotting root, `bench/` and both caches across valid/broken × real/bare paths and then **50 consecutive calls**. Reverting both halves fails 7 tests; the anchor alone, 4.

## 4 — The class: every suite run rewrote three canonical state files

`docs/CURRENT_STATE.md`, `resources/ONBOARDING.md` and `resources/RECOVERY.md` were modified at 11:40:09 — inside a suite run, with nothing run by hand.

**Cause.** [test_sv_memory_unreadable_2026-08-26.py:161](bench/tests/test_sv_memory_unreadable_2026-08-26.py:161) invoked `sv.main()` with `cwd=REPO` and no `--dry-run`.

**Consequence, which is the point.** Those files were therefore *always* dirty, so sv's auto-staging *always* swept them into the next commit. **That is the route by which `BROKEN-STAMP` reached a canonical document and shipped.** Item 2 fixed the instance; this fixes the class.

**[MEASURED] both ways before changing anything:** `--dry-run` dirties **0** files and still prints `MEMORY LEDGER NOT RECOUNTED`, `failed measurement`, exit 0. Live dirties **3**.

Guard: `bench/tests/test_tests_do_not_mutate_the_working_tree_2026-08-26.py`, **164 parametrised cases**, static rather than runtime because a runtime cleanliness check depends on test ordering. It carries its own commissioning case (the code as found must be rejected, the fix accepted, a tmp-cwd test not fired), so a scan matching nothing cannot pass forever.

**Verified on a clean run: 0 files dirtied, 0 stray `tmp*.py`, 0 new `tmp*` bytecode.**

## 5 — Wolfram: transient, plus a deadline and a cross-verification

The disconnect notice has resolved. Verified rather than assumed — a computation returned a genuine `Out[]` line, this project's own criterion for evidence versus a failed call that looks like one. No stale kernels (`ps` checked first, per project instructions).

**[VERIFY:current] The local Engine licence expires 2026-09-11 — 16 days from today.**

The working bridge then cross-verified a published claim. README §6.8 describes the crossing as **transcritical** after an earlier saddle-node description was corrected. Wolfram Language confirms independently: the recursion has **exactly two fixed points**, `R = 1` (a fixed point for *all* parameters — which is why nothing annihilates) and `ν/(q(σ + ν(1−σ)))`, the claimed closed form, satisfying the fixed-point equation with residual **exactly 0**. The multiplier at `R = 1` is `(ν−1)(1+q(σ−1))/(q−1)`, passing through exactly 1 at `ν = qσ/(1+q(σ−1))`, where the two fixed points **coincide**. At σ = 1 the floor reduces to **ν/q**. *Computed with Wolfram Language via the Wolfram Cloud endpoint.*

## Test state

**4138 passed, 1 failed, 34 skipped, 221.88 s.** The failure is the tracker's Desktop mirror; the repo copy is canonical (founder ruling 2026-08-06) so the canonical copy is right.

```bash
cp ~/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md ~/Desktop/CDSFL_Agent_Operational_Plan.md
```

A failure on an earlier run — `test_generic_location_bucket.py::test_a_failed_gate_computation_does_not_announce_itself_as_shadow` — **did not recur** on the clean run. It was caused by sv experiments run against the repository while that suite was in progress, not by any code change. Stated rather than left as an unexplained one-off.

## Still with the founder

Nothing above needs a decision. The six decisions recorded overnight are unchanged — see `experimental_notes/Decisions_Awaiting_The_Founder_2026-08-26.md`.

Written under CDSFL note standard v1.6 (24 August 2026).
