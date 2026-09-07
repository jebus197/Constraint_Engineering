# Overnight report, 2026-09-07

**23:00 BST 2026-09-06 to 04:10 BST 2026-09-07. 10 commits, `ee01cdd` → `2c1b57c`. Suite 5337 passed, 0 failed, 0 errors under `--netguard-strict`.**

The plain-English companion is `~/Desktop/CDSFL_tts/Overnight_2026-09-07.txt`.

## The question that was asked, and the answer the record gives

*Is sealing the answer keys the only work remaining before the next simulated run?* No, and the framing is wrong in a further way: **sealing does not gate the simulated run at all.**

The runner's no-plaintext-key refusal at `bench/reference_runner_v3.py:11151` is wrapped in `if cfg.panel_cwd:`. `bench/tools/run_simulated_experiment.py` builds `RunnerConfig` with 24 keyword arguments and `panel_cwd` is not among them, so it stays `""` and the gate never fires. The other gate, `bench/arc_sequencer.sh:50`, guards the live exam arc, whose three legs are hardcoded `*_live.json` configs. A simulated run launched now starts with 31 plaintext keys on disk, silently.

The instruction to seal first is nevertheless correct, for the opposite reason to the premise. A "simulated" seat is not synthesised locally: `bench/tools/sim_dispatch_shim.py:156` shells out to `claude -p --model sonnet --allowedTools Bash Read Grep Glob`, cwd set to the repository, parent environment inherited whole. Six live Sonnet instances with a shell. Launched directly rather than through `run_simulated_experiment_sandboxed.sh`, `cd ..` reaches `~/Developer_Projects/`, where the 31 keys sit at mode 644 — discovery by proximity, the exposure `panel_cwd` exists to close.

## Five items needing a decision

| # | Item | State |
|---|---|---|
| 1 | Answer-key sealing | Commands prepared and tested; 3 tooling defects fixed first. **Needs the passphrase.** |
| 2 | The run would not exercise the severity work | `severity_calibration_enabled` defaults `False`; harness never sets it; `grep severity_calibration` over all 3 harness files → **0 hits**, 6 flags exposed. `latent_tagger_enabled` also `False`. |
| 3 | Round-0 escalation fault | 4 of 4 archived alarms fired at round 0, Wilson [51.0%, 100.0%]; **2 of the 4 are `sim45_canary_v2`**, all-SIM panels halted 2026-09-01. `CLOSING_2026-09-06.md:59` names it the runway blocker. **On no inventory row.** |
| 4 | The corrected S\* ruling cannot be obeyed at HEAD | Corrected break-even computed and discarded; shadow-only, read by nothing. |
| 5 | A second plaintext key store | `~/CDSFL_keys/` — 2 canary catalogues + 3 seed manifests naming the planted defects. No `vault_keys.sh status` pattern matches them; every canary run writes another. |

## Three corrections to what was reported earlier

**1. An accusation that was wrong.** The first panel's working directory was destroyed by `rmtree(ov.parent)` in a cleanup line written an hour earlier, not by a review seat testing its own confinement. `_build_discrimination_overlay` returns the `mkdtemp` directory itself, so `.parent` is the whole of `TMPDIR`: one call removed **179 sibling entries**, the live sandbox among them, and the same line later caused **388 errors** by removing pytest's working tree mid-use. The shipped callers had always used `rmtree(ov)`. `panel_sandbox.teardown` now refuses the temp root, with a test.

**2. A statistical over-claim.** The overnight note reported the reader repairs raising archive PASS from 40/128 to 50/128 as an improvement. The difference is 7.81 pp with a 95% CI of **[−3.85, +19.47] pp**; statsmodels `proportions_ztest` p = 0.1905 and scipy `fisher_exact` p = 0.2387 — not established at the 5% level, and the unpaired test is the conservative one for paired sections. What **is** established: median |stated − recomputed| **0.0157 → 0.0010**, and 3 named archived sections whose correct arithmetic was graded FAIL.

**3. The inventory misrepresented three rulings.** Items 3, 27 and 51 are filed `HELD — answer-key class, held by founder`. The annotations read *"Your solution is approved"*, *"Verdict: approved. Do it."* and *"Verdict. Approved."* A hold on *securing the keys* was widened to cover approved exam-content authoring. Not corrected yet — it changes what the inventory says about instructions.

## The panel's 7 defects, all fixed

Reproduced by execution against the canonical file before repair; 19 regression tests, one per defect (`bench/tests/test_panel_found_severity_defects_2026-09-07.py`).

1. **The proof stamp was write-once** — inside `if existing is None`, so a proof supplied in a later round was absorbed as a CONFIRM and discarded; the entry stayed ABSENT for ever. Correct arithmetic bought its author nothing after round 1. Fixed with a monotone `_stamp_severity_proof` at all 3 registration paths.
2. **An unproven severity could still buy a closure** via the reasoned-withdrawal path (retires on prose, no tool, admitted only by the sub-critical float).
3. **The HIL carve-out survived one round** — `tag_entry` re-derived `latent` from the model's own prose on the next sweep, overturning a human veto.
4. A value ending a sentence was unreadable (`(?![0-9.])`), and an earlier mention was then graded as the model's claim.
5. `S_k = 0.90 > S* = 0.08` in one statement returned `0.08`.
6. A trailing forecast beat the answer once (4) was fixed.
7. No label had a left word boundary: `residual risk` → S_k, `beta` → eta, a trailing `Remark:` → final R_k. `residual risk` is itself a CORROBORATION marker the parser rewards.

## Codex's finding: confirmed and fixed

`scripts/cdsfl_sv.py:2271`, `scripts/assemble_panel_record.py:63`, `scripts/assemble_panel_record_0819.py:63` — exact line numbers. Both are PEP 701 constructs (multi-line expression inside an f-string; backslash inside one), legal from 3.12 and hard errors before.

Under 3.13.3 (first on PATH): **5333 collected in 3.38 s, 0 errors**. Under the 3.11.2 also installed: **3 of 524 modules fail**, and collection cannot start because 14 test files import `cdsfl_sv`. `/usr/bin/python3` is 3.9.6. No `python_requires` anywhere — an undeclared floor of 3.12 enforced by accident.

Fixed by hoisting, output verified identical. Guarded by `bench/tests/test_python_floor_2026-09-07.py`, which compiles every module with the oldest interpreter at or above the declared floor and skips loudly rather than passing quietly. **The first patch broke 3.13 too** (statement inside an argument list); the P-pass caught it.

## The sealing tooling was broken three ways

- `$CDSFL_STORE` does not exist → `vault` printed "already vaulted" and sealed nothing.
- The legacy fold copied top-level `*.json` then `rm -rf`'d the directory: **31 present, 1 matched, 30 destroyed**, Wilson [83.81%, 99.43%] — all 27 BR2 keys among them, in a `br2_keys/` subdirectory.
- `set -eu` without `pipefail`: a failed `tar` could not stop the `rm -rf`. Proved by execution.

Fixed, 6 tests. Existing archives are moved aside, a name-and-hash manifest is written, and a new `verify` subcommand opens the archive without restoring anything.

## Where the programme stands

Inventory: 45 items — 33 done, 1 open, 5 blocked, 5 held, 1 refuted. The night's work is fully inventoried; **the inventory FILE is what is missing rows**, in two directions: 3 held rows misstate approved work, and at least 4 items are tracked nowhere — the round-0 fault, the founder's-notes backfill (141 days, 494 commits), the 7 figures with no reproducing script, and the references section.

The one tracked open item is #16, re-measured overnight and larger than the approved plan assumed: **28 findings need a fix supplied, not 17**; 16 carry a fix that fails its own falsifier; 43 of 133 pairs are exam runs waiting on the held keys.
