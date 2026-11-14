# Full Suite Triage — 2026-11-14

2026-11-14, 13:37 GMT

## Summary

`python3 -m pytest bench/tests/ -q --netguard-strict` ran against commit `6304f771` for **11,825.11 s = 3:17:05** and reported **32 failed, 17,760 passed, 40 skipped, 1 error**, pytest exit code 1. Recorded in `resources/suite_record.json` via `python3 scripts/suite_record.py record --log <file>`, **without `--clean`**: 3 files were modified at launch — `bench/tickets/sv_completions.jsonl`, which `sv` dirties after every commit, plus `resources/RECOVERY.md` and `experimental_notes/CDSFL_Agent_Operational_Plan.md`, updated after the commit landed. Waiting for a pristine tree would mean never running it.

The previous full measurement was **29 failed** at `846c4ffe` on 2026-11-13.

## The partition, by node id and not by count

| | |
|---|---|
| carried over (same node id in both) | **23** |
| stopped failing | **7** |
| started failing | **10** |

Arithmetic closes both ways: 23 + 10 = 33 rows today, 23 + 7 = 30 rows in the baseline. (33 and 30 rather than 32 and 29 because pytest reports the `ERROR` row outside the failure count.) Producer: `scripts/the_suite_triage_2026-11-14.py`.

**29 → 32 is not 3 new failures.** A net movement of 3 conceals 17 individual changes, and the 2 directions have entirely different causes.

## Board visibility

`hooks/pre-commit` names **308** distinct test files. Only **2 of the 10** new failures sat in one of them.

- 2 of 10 = **0.200000**
- Wilson 95% **[0.056682, 0.509838]** (statsmodels; hand-rolled mpmath agrees to 6.939e-18)
- Clopper-Pearson 95% **[0.025211, 0.556095]** (beta quantile; exact binomial tails by bisection agree to 6.939e-18)

Invisible to the board: `test_note_standard_v17_enforced_2026-08-26.py` (×2), `test_operational_scripts.py`, `test_task_list_burndown_2026-09-11.py`, `test_tests_do_not_mutate_the_working_tree_2026-08-26.py`, `test_the_chat_half_raises_only_real_markers_2026-10-28.py`, `test_the_morning_report_is_generated_2026-10-12.py`, `test_the_spec_is_not_work_2026-10-15.py`.

This is not an argument for enlarging the board unexamined: each added file costs time on every commit, and a board already averages about 29 min (`scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py` — re-run it, the ledger is unversioned).

## B198 — the guard against tests mutating the working tree accused a file that invokes `sv` nowhere

`bench/tests/test_tests_do_not_mutate_the_working_tree_2026-08-26.py::test_no_test_runs_sv_against_the_real_repo_without_dry_run` failed on `bench/tests/test_the_co_author_trailer_is_not_doubled_2026-11-14.py`, written the previous night for B193 (the doubled co-author trailer).

Established by `ast`, not by reading: the accused file holds exactly **1** subprocess call —

```
subprocess.run(["git", "log", "-1", "--format=%B", "4a802768"], cwd=REPO, ...)
```

— which is read-only, and its 4 mentions of `cdsfl_sv.py` are line 4 (prose), line 39 (`import cdsfl_sv as sv`), line 157 (`read_text()` feeding `ast.parse`) and line 180 (an assertion message).

**The old predicate**, 3 regexes ANDed over the whole file:

```python
SV_MAIN  = re.compile(r"sv\.main\(\)|cdsfl_sv\.py['\"]")
DRY      = re.compile(r"--dry-run")
REAL_CWD = re.compile(r"cwd\s*=\s*(REPO|REPO_ROOT|str\(REPO\)|str\(REPO_ROOT\))\b")
```

`SV_MAIN` matched the `read_text()` at line 157; `REAL_CWD` matched the `git log` at line 132. **The printed remedy — pass `--dry-run` — would have put a meaningless flag string into a file with no invocation to pass it to.**

**The first replacement was wrong in the other direction.** It treated an in-process `sv.main()` as writing relative to the process cwd and flagged all 3 such call sites: `test_cdsfl_sv_memory_ledger.py:97`, `test_cdsfl_sv_repairs.py:433`, `test_sv_rulings.py:944`. `sv` writes under `repo_root()`, and all 3 `monkeypatch.setattr(sv, "repo_root", lambda: tmp_path)`. Reading those 3 call sites was all that stood between 1 false accusation and 4.

**The repair** splits the predicate in 2 — `sv_invocation_call_sites()` finds every call that runs `sv`; `sv_offender_call_sites()` filters to those reaching the real repository without `--dry-run`, deciding `cwd` and the flag from the call and its enclosing function. An in-process call is safe when its enclosing function redirects `repo_root` or chdirs. The commissioning test now **calls the live predicate** instead of holding its own copy of the retired conjunction.

Measured over 937 test files: old **1** flagged (false), new **0**, Wilson [0.000000, 0.004083], Clopper-Pearson [0.000000, 0.003929]. 7 of 7 commissioning cases correct. Producer: `scripts/the_sv_mutation_guard_accused_a_clean_file_2026-11-14.py`, executed by `test_the_producer_for_this_repair_actually_runs`.

## B199 — a typo ran a 52.86 s measurement and reported success

| script | before | after |
|---|---|---|
| `scripts/the_exempt_span_mutations_2026-11-14.py` | 52.86 s, mutated a production file 5×, exit 0 | exit 2, <1 s |
| `scripts/the_draft_block_mutations_2026-11-14.py` | ran, exit 0 | exit 2, <1 s |
| `scripts/does_the_parked_composition_beat_either_half_2026-11-14.py` | ran, exit 0, no usage line | usage line, exit 0; exit 2 on anything else |
| `scripts/the_cut_is_a_domain_property_not_a_constant_2026-11-11.py` | ran, exit 0 | exit 2, <1 s |

The first is the serious one: `test_an_unknown_flag_is_rejected_loudly[the_exempt_span_mutations_2026-11-14.py]` drove it with `--this-flag-does-not-exist`, and it mutated `scripts/morning_report_build_2026-10-12.py` five times and restored it — so a parametrised guard case was itself writing to a production file on every full-suite run.

All 4 are wired to `scripts/_cli_help.py:answer_help` as the first statement of `main`. `python3 scripts/measurement_scripts_only_2026-09-11.py --run` now reports **0 of 393**.

**My own fault, 3 times in an hour:** the preamble was pasted from a file doing `import pathlib` into 3 doing `from pathlib import Path`, producing `NameError: name 'pathlib' is not defined` in all 3. The 4th application detects the target's import style with an `ast` walk. A copied preamble carries its source file's assumptions.

## B200 — three instruments measured a proxy

1. **A word count for a heading count** — `test_it_carries_every_decision_with_its_options` asserted `head.count("The options.") >= head.count("DECISION ")` and reported `assert 18 >= 19`. All 18 blocks carried their options; the 19th `DECISION ` was inside B175's authored prose (*THIS DECISION IS THE THIRD PART AND IT IS YOURS*). Converted to a per-block check splitting on `^DECISION \d+\.`, matching its markdown sibling's design since 2026-10-16. Anti-regression case drives synthetic text, not the live report.
2. **An mtime for a content change** — `test_it_is_not_older_than_the_record_it_reports` named `experimental_notes/data/morning_report_decisions.json` at 11:55:24 as the moment the record moved. `git status --porcelain` reports that path clean; the real content change was the commit at 08:20:15. The verdict was right and the reason false. Replaced with `_content_changed_at()`: dirty → mtime, clean+tracked → `git log -1 --format=%ct -- <path>`, untracked or no git → mtime. 3 commissioning cases drive a real throwaway repository.
3. **A non-greedy pattern for a node id** — `ROW = re.compile(r"^(FAILED|ERROR)\s+(\S+?)...")` could not span `test_the_labelled_set[I23: exhausted_round_threshold defaults to 8 while max_rounds is 8-True]`, failed the line entirely, and dropped it from **both** logs: the partition first read 22 carried over where the truth is 23. `parse_or_refuse()` now counts verdict lines as a second form and **raises `SystemExit` rather than reporting the smaller number**.

## B197 — left red deliberately

`bench/tests/test_task_list_burndown_2026-09-11.py::TestTheListTerminates::test_the_process_is_subcritical`:

```
R = 1.033088, 95% interval [0.874617, 1.220273], 281 added against 272 closed, 406 snapshots
```

His 2026-11-08 ruling (*"I accept your recommendation."*) accepted an **interval** crossing 1. The guard was re-scoped on 2026-11-11 to the **point estimate** precisely so it would fire only on something not yet ruled. Snapshots: `846c4ff` 322/274 on 2026-11-13, `6304f77` 340/275 on 2026-11-14 — 18 added, 1 closed in 2 days.

**Recommendation:** rule again that the ratio stands and re-scope to the interval's **lower** bound crossing 1 — `additive-standard`, since the measurement, the report and the ability to fire are all retained. Retiring the assertion is a removal and would need a committed measurement showing a replacement dominates on a named property; none exists. The threshold must not be moved to make this green.

Tickets: `qs:633854939cf3` (branching point estimate), `pf:d59f2cf9c563` (sv mutation guard's false accusation), `pf:24e3397dde0e` (scripts treating a typo as a request to run), `pf:e98c65b9902f` (instruments measuring a proxy). All 4 entries reach 7 of 7 surfaces per `scripts/raise_an_entry_2026-11-02.py`.

Written under CDSFL note standard v1.9 (1 November 2026).
