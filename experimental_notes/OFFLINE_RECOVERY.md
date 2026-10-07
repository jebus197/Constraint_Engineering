# Offline recovery: rebuilding context with no network at all

2026-10-07 18:50 BST — standing resource, not dated to one session. Update in place; do not fork a dated copy.

## Why this file exists, and it is not a convenience

OBSERVED 2026-10-07: `scripts/cdsfl_recover.py` — the `rs` restore — **crashes with a traceback when the network is unreachable**, and so do `scripts/cdsfl_sv.py` and `scripts/cdsfl_qc.py`. All 3 call `git_state()` in `scripts/cdsfl_utils.py:59`, which makes an unconditional `git fetch` at line 80.

The distinction that matters is between a fetch that FAILS and a fetch that cannot RUN. `_run_git_rc` returns `(returncode, stdout)`, so a fetch that exits non-zero is already tolerated — `remote_sync` degrades to a sensible string and the script continues. But `subprocess.run(..., timeout=30)` **raises** `subprocess.TimeoutExpired` when the cap expires, and a dead interface raises `OSError`; neither is caught anywhere on the path. Measured by substituting each failure mode into the live function:

| Fetch failure mode | `git_state()` outcome |
|---|---|
| exits non-zero (offline, fast refusal) | SURVIVES — `remote_sync` reads "up to date with origin/sim/shakedown-2026-09-29" |
| `TimeoutExpired` after 30 s (flaky link) | CRASHES |
| `OSError`, network unreachable | CRASHES |

So recovery is least available in exactly the circumstance that makes recovery necessary. The 2026-10-07 full board recorded 25 failures of 10331 decided tests, 0.241990%, Wilson [0.163971%, 0.357000%], and **11 of those 25 were this single cause** — 44.0000%, Wilson [26.6656%, 62.9327%]. The same 10 tests passed in 164.78 s on a later run with the link up, which is what establishes the cause as network-conditional rather than a code regression. The class is **not** recorded in `bench/directives/universal/section_p_shortfalls.json`.

The repair is one point in one function and is PROPOSED, not built: catch the raised forms of a fetch failure and degrade them to the same path the non-zero return code already takes. It is held for a ruling because fixes are suggested to the human in the loop rather than applied.

## The network-free sequence

Every command below was confirmed to make no network call. Run them in order; each line names what it establishes.

1. `date -Iseconds` — the clock. Never type a timestamp; capture it.
2. `git log --oneline -10` — what landed, newest first. Purely local; needs no remote.
3. `git status --porcelain` — whether anything is uncommitted. Purely local.
4. `git branch --show-current` — which branch, which decides whether a commit is legitimate under the simulated-branch ruling.
5. `git show --stat HEAD` — what the newest commit actually touched, as against what its message claims.
6. Read `resources/RECOVERY.md`, newest SESSION STATE block only. The blocks are reverse-chronological and the newest carries the resume pointer.
7. Read `experimental_notes/CDSFL_Agent_Operational_Plan.md` — the operational tracker, which names the exact resume point that the narrative does not.
8. Read the newest `experimental_notes/WORK_IN_FLIGHT_<date>.md` — the per-item work ledger with the founder's verdicts.
9. `python3 -m open_brain.cli session-context --agent cc` — the session summary store. Reads a local database, so it works offline.
10. `python3 scripts/blocker_triage.py` — which open items genuinely block progress. Network-free.

**Do NOT run `rs`, `sv` or `qc` while the link is down.** They will either crash or hang for 30 s per git call before crashing. Once the link is back, run `rs` and capture its exit code.

## What the dated ledgers are for, and what this file is for

`WORK_IN_FLIGHT_<date>.md` is a per-session work ledger: one row per instructed item, carrying the founder's verdict and the closing state. It is correct that these are dated, because they are a record of a particular instruction set and must not be rewritten later.

This file is the opposite: a standing procedure with no date in its name, revised in place whenever the offline-safety of a command changes. If a script on the list above acquires a network call, this file is wrong and must be corrected in the same commit.

## Verification

The offline-safety claim was established by counting network and `git_state` references per script rather than by reading intentions: `cdsfl_recover.py`, `cdsfl_sv.py` and `cdsfl_qc.py` all reference them; `scripts/blocker_triage.py` and `scripts/note_vagueness_lint.py` reference neither. The OpenBrain command-line interface makes 0 network references and reported "Database connection: OK" against a local store.

Written under CDSFL note standard v1.7 (26 August 2026).
