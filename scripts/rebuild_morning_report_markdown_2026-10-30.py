import pathlib, re
src = pathlib.Path.home()/"Desktop/CDSFL_tts/Morning_Report_2026-10-30.txt"
dst = pathlib.Path("experimental_notes/Morning_Report_2026-10-30.md")
txt = src.read_text()
foot = "Written under CDSFL note standard v1.8.\n"
assert txt.endswith(foot)
body = txt[: -len(foot)]

out = []
for i, L in enumerate(body.split("\n")):
    if L.startswith("SECTION "):
        m = re.match(r"SECTION (\d+)\.\s+(.*)", L)
        out.append("## %s. %s" % (m.group(1), m.group(2).capitalize()))
    elif L.isupper() and len(L) > 25 and not L.startswith(" "):
        out.append("### " + L.capitalize())
    elif i == 0:
        out.append("# " + L.title())
    else:
        out.append(L)

appendix = """
## Technical appendix

The TTS companion names files as nouns with a locator, under Rule 6 of the note
standard, because a path read aloud is noise. This section restores what that
rule removes. It adds nothing to the findings above; every figure in it is the
same figure.

### Producers committed with these figures

| Figure | Producer |
|---|---|
| Layer order decides 0 keys; 0 of 60 pairs collide | `scripts/what_does_layer_order_actually_decide_2026-10-30.py` |
| 4 channels, 2 already ruled, 1 awaiting | `scripts/how_many_channels_actually_await_his_ruling_2026-10-30.py` |
| B50's filter repairs 1 and breaks 1 | `scripts/does_filtering_the_stale_constant_repair_two_2026-10-30.py` |
| The reset re-armed 6 stale pins | `scripts/the_reset_rearmed_six_stale_pins_2026-10-29.py` |
| 2 of 3 ruling-askers already have his ruling | `scripts/which_open_entries_already_have_his_ruling_2026-10-30.py` |
| Options 3 and 1 compose: 7 of 15 prevented | `scripts/do_options_three_and_one_compose_2026-10-29.py` |
| New entries per entry closed, R = 0.7791 | `scripts/task_list_burndown_2026-09-11.py` |
| Which role vocabulary the code speaks, 63 of 67 | `scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py` |
| Questions owed, by direction | `scripts/what_questions_are_owed_2026-10-30.py` |
| Memory index line and character budget | `scripts/the_line_budget_is_the_binding_one_2026-10-29.py` |
| Whether an entry still asks for a ruling | `scripts/does_a_ruled_entry_still_ask_for_a_ruling_2026-10-17.py` |

### Guards

| Guard | Tests | Notes |
|---|---|---|
| `bench/tests/test_what_layer_order_decides_2026-10-30.py` | 12 | 4 of 4 mutations red |
| `bench/tests/test_how_many_channels_await_his_ruling_2026-10-30.py` | 10 | properties, not counts |
| `bench/tests/test_does_filtering_the_stale_constant_repair_two_2026-10-30.py` | 7 | pins sets; proves the runtime patch takes effect |
| `bench/tests/test_the_ledger_budget_is_derived_not_reserved_2026-10-30.py` | 19 | catches the reserve mutation `test_it_lists_commits_not_narrative` passes; z3 maximality |
| `bench/tests/test_the_morning_report_is_generated_2026-10-12.py` | 22 | 15 failed before the archive fix, 22 pass after |
| `bench/tests/test_which_role_vocabulary_2026-10-30.py` | 6 | 2 of 2 mutations red |
| `bench/tests/test_which_open_entries_already_have_his_ruling_2026-10-30.py` | 15 | positive control on 2 known rulings; negative control on 5 of my own quotes |
| `bench/tests/test_the_memory_baseline_skips_an_unclean_save_2026-10-29.py` | 14 | B47's evidence; both save paths, 22 live calls |
| `bench/tests/test_the_claim_channel_enters_r_k_2026-10-29.py` | 16 | C1's evidence; SymPy, z3 and Wolfram on 6 properties |

### Subjects named in sections 8 and 9

- The 4-layer policy merge: `bench/cdsfl_registry/registry.py` —
  `load_effective_policy`, `_deep_merge`, `_check_monotonicity`, and the
  constants `HARD_CONSTRAINTS`, `HARD_THRESHOLDS`, `HARD_STRINGS`
  (17 protected dotpaths).
- The structural role enum: `bench/experiment_11_orchestrator.py:59`,
  `Role = Literal["collator", "player_manager", "participant"]`.
- The claim channel awaiting a ruling: `bench/claim_ledger.py`, class
  `ClaimLedger`, `informative_only = True`.
- The 2 channels already ruled informative-only: `collect_non_cure_ledger`
  (2026-09-30) and the `target_complexity` block in `run_experiment`
  (2026-09-09), both in `bench/reference_runner_v3.py`.
- The default-off facility: `RunnerConfig.sev_f_enabled`, default `False`.
- B50's stale constant: `_RECORDING_RUNS` in
  `bench/tests/test_immune_memory_evaluation.py`.
- The accumulating write path: `ImmuneMemory.load` at
  `bench/reference_runner_v3.py:21620`, `record_experiment` at `:21630`.
- The archived reset:
  `bench/state/immune_memory_archive/immune_memory_20261017T095236Z.why.json`.
- The report generator and its authored half:
  `scripts/morning_report_build_2026-10-12.py`, with
  `experimental_notes/data/morning_report_decisions.json` and its
  `_archived_authored_detail` bucket.
- Absent directories, so neither layer exists: `bench/cdsfl_registry/roles/`
  and `bench/cdsfl_registry/tasks/`.

### Entry and ticket identifiers

- Entries carrying this work: **B21** (role layer), **C1** (claim channel),
  **B50** (immune-memory assertions). All 3 remain OPEN and all 3 now carry the
  correction on their own marker line in
  `experimental_notes/CDSFL_MASTER_TASK_LIST.md`.
- The Stop-gate finding: `pf:c15b3dbe595a`, anchor derived as
  `chat#2026-10-30T02:44:26+00:00#97afe049`.
- **B47 is now DONE**, dated to his ruling of 2026-10-29 rather than to the
  day it was recorded, with
  `bench/tests/test_the_memory_baseline_skips_an_unclean_save_2026-10-29.py`
  as its evidence.
- 6 entries remain OPEN: B21, B22, C1, B41, B50, R1 — of which 1 (B50) is a
  ruling in the sense section 1 meant. C1 awaits a single scalar
  (`CLAIM_CHANNEL_WEIGHT`, currently 0.0), B21 3 panel questions, B22 a panel
  dispatch, B41 a go-ahead, R1 authorisation and money.

### Intervals, with the denominator each belongs to

| Statement | k of n | Wilson 95% | Cross-check |
|---|---|---|---|
| Pairs whose protected keys move under order reversal | 0 of 60 | [0.000000, 0.060172] | one-sided exact 0.048703, scipy and mpmath agree |
| Pairs sharing any leaf key between layers | 0 of 60 | [0.000000, 0.060172] | closed form and statsmodels agree to 1e-12 |
| Channels already ruled informative-only by design | 2 of 4 | [0.150039, 0.849961] | closed form and statsmodels agree |
| Open entries that ask in their own words for a ruling | 4 of 7 | [0.250458, 0.841780] | — |
| Ruling-askers that already carry his ruling | 2 of 3 | [0.207660, 0.938508] | closed form and statsmodels agree |
| Follow-up saves NOT prevented by option 3 | 8 of 15 | [0.301170, 0.751905] | Clopper-Pearson [0.265861, 0.787333] |
| New entries per entry closed (R, subcritical) | — | [0.618100, 0.982100] | exact test against R = 1: p = 1.983431e-02 |

The 1,020 individual pair-by-dotpath comparisons (60 pairs by 17 dotpaths, 0
differing) are stated as a count and deliberately given **no** interval: the 17
dotpaths within 1 pair share a merge mechanism and are not independent
observations. The first draft of this result paired the 60-pair interval with
the 17-dotpath count, and the pre-commit Wilson checker refused the commit,
recomputing [0.0000, 0.1843] for 0 of 17.

B50's before-and-after failure counts are stated as sets rather than as
proportions, because both sides are the same integer (6 of 34) and a proportion
over an unchanged denominator would say nothing about which assertion moved.

### Board reach

The pre-commit board names 73 test files explicitly; 723 exist under
`bench/tests/`, so it does not reach 650 of them. That is deliberate — a full
board is roughly 66 minutes — and
`bench/tests/test_the_morning_report_is_generated_2026-10-12.py` is one of the
650, which is why 15 failing assertions about this document survived 3 commits.

"""
dst.write_text("\n".join(out) + appendix + foot)
print("rebuilt %s (%d lines)" % (dst, len(dst.read_text().splitlines())))

repo_txt = pathlib.Path("experimental_notes/Morning_Report_2026-10-30.txt")
repo_txt.write_text(txt)
print("synced the repo txt mirror (%d lines)" % len(txt.splitlines()))
