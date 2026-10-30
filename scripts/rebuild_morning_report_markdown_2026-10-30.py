#!/usr/bin/env python3
"""Rebuild the morning report's markdown companion from its spoken source.

WHY A GENERATOR EXISTS AT ALL. On 2026-10-30 a note-lint finding in
`experimental_notes/Morning_Report_2026-10-30.md` was fixed BY HAND, and the next
rebuild regenerated the file from this script's own appendix string and the
finding came straight back. Fixing an artefact a producer owns is not a fix, so
the generator was committed rather than left in a scratchpad.

★ 2 DEFECTS IN THAT FIRST COMMITTED VERSION, BOTH FOUND THE SAME NIGHT.

(1) IT HAD NO TEST. `grep -rl` over `bench/tests/` returned 0 files naming it,
    which is the addition-nothing-reaches half of the additive standard -- the
    shape this project has confirmed 11 times -- committed about an hour after a
    memory about producers was extended. A guard now calls `--check`.

(2) ITS SOURCE WAS AN UNVERSIONED DESKTOP FILE, so it could not be reproduced
    from a fresh clone, which is entry A2's whole subject. The source is now the
    REPO copy, with the Desktop copy used only as a fallback and then brought
    back into agreement. Both were byte-identical at 37,058 bytes when this
    changed, so nothing is lost by preferring the versioned one.

`--check` regenerates in memory and compares, writing nothing, so a guard can
assert the committed markdown matches its source without mutating the tree.
"""
from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
REPO_TXT = REPO / "experimental_notes" / "Morning_Report_2026-10-30.txt"
DESKTOP_TXT = (pathlib.Path.home() / "Desktop" / "CDSFL_tts"
               / "Morning_Report_2026-10-30.txt")
DST = REPO / "experimental_notes" / "Morning_Report_2026-10-30.md"
FOOT = "Written under CDSFL note standard v1.8.\n"


APPENDIX = """
## Technical appendix

The spoken companion names files as nouns under Rule 6, because a path read
aloud is noise. This restores exactly that, and adds no new figures.

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
| 5 dead path citations, 3 placeholders, 2 deliberate | `scripts/a_cited_path_must_exist_2026-10-30.py` |
| This markdown companion itself | `scripts/rebuild_morning_report_markdown_2026-10-30.py` (`--check`) |
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
| `bench/tests/test_a_cited_path_must_exist_2026-10-30.py` | 7 | 3 of 3 mutations red; scoped to 1 document by measurement |
| `bench/tests/test_the_markdown_companion_is_generated_2026-10-30.py` | 6 | includes the corruption control |
| `bench/tests/test_which_open_entries_already_have_his_ruling_2026-10-30.py` | 15 | positive control on 2 known rulings; negative control on 5 of my own quotes |
| `bench/tests/test_the_memory_baseline_skips_an_unclean_save_2026-10-29.py` | 14 | B47's evidence; both save paths, 22 live calls |
| `bench/tests/test_the_claim_channel_enters_r_k_2026-10-29.py` | 16 | C1's evidence; SymPy, z3 and Wolfram on 6 properties |

### Subjects named in sections 8 to 11

| Subject | Where |
|---|---|
| 4-layer policy merge, 17 protected dotpaths | `bench/cdsfl_registry/registry.py` — `load_effective_policy`, `_deep_merge`, `_check_monotonicity` |
| The structural role enum | `bench/experiment_11_orchestrator.py:59` |
| The claim channel awaiting a weight | `bench/claim_ledger.py`, `ClaimLedger`, `CLAIM_CHANNEL_WEIGHT = 0.0` |
| Channels already ruled informative-only | `collect_non_cure_ledger` (2026-09-30), `run_experiment`'s `target_complexity` block (2026-09-09) |
| Default-off panel facility | `RunnerConfig.sev_f_enabled`, default `False` |
| B50's stale constant | `_RECORDING_RUNS` in `bench/tests/test_immune_memory_evaluation.py` |
| The accumulating write path | `ImmuneMemory.load` at `:21620`, `record_experiment` at `:21630` |
| The archived reset | `bench/state/immune_memory_archive/immune_memory_20261017T095236Z.why.json` |
| B47's live mechanism | `record_sv_completion`, `unclean_sv_commits`, `_previous_sv_commit(require_clean=True)` |
| Absent, so neither layer exists | `bench/cdsfl_registry/roles/` and `bench/cdsfl_registry/tasks/` |

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

The 1,020 pair-by-dotpath comparisons (60 by 17, 0 differing) get a count and
**no** interval: the 17 dotpaths in 1 pair share a merge mechanism and are not
independent. The first draft paired the 60-pair interval with the 17-dotpath
count, and the pre-commit Wilson checker refused it, recomputing
[0.0000, 0.1843] for 0 of 17. B50's before-and-after counts are given as SETS,
because both sides are the same integer (6 of 34).

### Board reach

The pre-commit board names 73 test files explicitly; 723 exist under
`bench/tests/`, so it does not reach 650 of them. That is deliberate — a full
board is roughly 66 minutes — and
`bench/tests/test_the_morning_report_is_generated_2026-10-12.py` is one of the
650, which is why 15 failing assertions about this document survived 3 commits.

"""


def source() -> pathlib.Path:
    """The versioned copy, falling back to the Desktop one only if absent."""
    if REPO_TXT.is_file():
        return REPO_TXT
    if DESKTOP_TXT.is_file():
        return DESKTOP_TXT
    raise FileNotFoundError(
        f"neither {REPO_TXT} nor {DESKTOP_TXT} exists; there is no source to "
        f"rebuild the markdown companion from")


def render() -> str:
    """The markdown companion, as a string. Writes nothing."""
    src = source()
    txt = src.read_text()
    if not txt.endswith(FOOT):
        raise ValueError(
            f"{src} does not end with the note-standard foot-line, so it is "
            f"either incomplete or not a compliant note")
    body = txt[: -len(FOOT)]
    foot = FOOT
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
    return "\n".join(out) + APPENDIX + foot


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare only; write nothing and exit 1 on a mismatch")
    args = ap.parse_args(argv)

    built = render()
    if args.check:
        have = DST.read_text() if DST.is_file() else ""
        if have == built:
            print(f"OK - {DST.relative_to(REPO)} matches its source "
                  f"({source().relative_to(REPO.parent)})")
            return 0
        diff = list(difflib.unified_diff(
            have.split("\n"), built.split("\n"),
            fromfile="committed", tofile="rebuilt", lineterm="", n=1))
        print(f"MISMATCH - {DST.relative_to(REPO)} differs from a rebuild; "
              f"{len(diff)} diff line(s). Fix the GENERATOR, not the markdown: "
              f"a hand edit here is undone by the next rebuild.")
        for line in diff[:40]:
            print(f"  {line}")
        return 1

    DST.write_text(built)
    print(f"rebuilt {DST.relative_to(REPO)} "
          f"({len(built.splitlines())} lines) from {source().name}")
    # keep the 2 spoken copies in agreement, whichever was the source
    txt = source().read_text()
    for other in (REPO_TXT, DESKTOP_TXT):
        if other.is_file() and other.read_text() != txt:
            other.write_text(txt)
            print(f"synced {other}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
