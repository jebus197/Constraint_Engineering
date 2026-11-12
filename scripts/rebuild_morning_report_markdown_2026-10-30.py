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

#: GENERALISED 2026-10-31. The script was pinned to a single date, so the next
#: day's companion had to be written by hand -- which is the exact drift this
#: generator exists to prevent. `--date` now selects the report; the default is
#: unchanged, so every existing caller and the guard behave identically.
#:
#: The 2 rendering styles are chosen by the DOCUMENT'S OWN headings, not by its
#: date: a report using "SECTION n." renders as before, and one using "PART n."
#: keeps its heading case and gets its lead sentences emphasised, which is the
#: shape the founder said was easier to read. Keying on the heading rather than
#: on a date is what makes it impossible for this change to alter the 2026-10-30
#: output: that file carries 11 SECTION lines and 0 PART lines.
DEFAULT_DATE = "2026-10-30"
# ★ THE VERSION IS NO LONGER TYPED INTO THE MATCHER, 2026-11-02, and the defect
# was live rather than hypothetical. This read
# `FOOT_PREFIX = "Written under CDSFL note standard v1.8"` and line 206 RAISES
# when no line starts with it. The standard was bumped to v1.9 on 2026-11-01, so
# the current morning report is stamped v1.9 -- VERIFIED by execution: the v1.8
# prefix matches 1 foot line in Morning_Report_2026-11-01.txt and 0 in
# Morning_Report_2026-11-02_GENERATED.txt, meaning this script would have raised
# on today's report while working on yesterday's.
#
# A version typed into a matcher goes stale the next time the standard moves,
# which is the same shape as the stale counts this project keeps finding. The
# prefix now matches ANY declared version, which is strictly MORE permissive --
# every archival stamp from v1.3 onward still matches, so no historical report
# stops being readable.
#
# THE PROJECT'S CANONICAL FOOT-LINE RULE IS NARROWER THAN THIS and is deliberately
# not reimplemented here: `declared_version` in
# bench/tests/test_note_standard_v17_enforced_2026-08-26.py holds the HIGHEST
# version on any foot-line-shaped line and ignores prose mentions. That rule
# exists to decide which RULES a note is held to. This script only needs to LOCATE
# the foot line so it can be preserved, so a prefix match is the simplest
# sufficient predicate and copying the stricter rule here would create a second
# place for it to drift.
FOOT_PREFIX = "Written under CDSFL note standard v"


APPENDIX_2026_10_30 = """
## Technical appendix

Rule 6 keeps paths out of the spoken copy; this restores them, adding no new figures.

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

73 of 727 files are on the gate's list, leaving **654** unreached (0.8996 — a
census, so no interval), per `scripts/precommit_gate_cost_2026-09-10.py`. A full
board is ~99 minutes and cannot gate a commit, which is why 15 failing assertions
in `test_the_morning_report_is_generated_2026-10-12.py` survived 3 commits.

"""


#: Per-date appendices. A date absent here simply gets no appendix, which is
#: correct: an appendix restores paths Rule 6 keeps out of the spoken copy, and
#: a report whose paths are already inline needs none.
APPENDICES = {"2026-10-30": APPENDIX_2026_10_30}


def paths(date: str = DEFAULT_DATE):
    """The 3 files for a given report date: repo text, Desktop text, markdown."""
    stem = f"Morning_Report_{date}"
    return (REPO / "experimental_notes" / f"{stem}.txt",
            pathlib.Path.home() / "Desktop" / "CDSFL_tts" / f"{stem}.txt",
            REPO / "experimental_notes" / f"{stem}.md")


def source(date: str = DEFAULT_DATE) -> pathlib.Path:
    """The versioned copy, falling back to the Desktop one only if absent."""
    repo_txt, desktop_txt, _ = paths(date)
    if repo_txt.is_file():
        return repo_txt
    if desktop_txt.is_file():
        return desktop_txt
    raise FileNotFoundError(
        f"neither {repo_txt} nor {desktop_txt} exists; there is no source to "
        f"rebuild the markdown companion from")


def _emphasise_lead(line: str) -> str:
    """Bold a paragraph's opening sentence, as the PART-style reports do.

    The sentence boundary is a full stop, question mark or colon followed by a
    space and a CAPITAL. Requiring the capital is what stops a decimal being
    read as a boundary: "0.992424" is a full stop followed by a digit, and the
    archive figures in these reports are full of them.
    """
    if not line or line.startswith(("#", "-", "|", " ")):
        return line
    m = re.search(r"^(.{20,400}?[.:?])\s+(?=[A-Z0-9])", line)
    if not m:
        return line
    lead = m.group(1)
    if "**" in lead:
        return line
    return f"**{lead}**" + line[len(lead):]


#: ★ `str.capitalize()` LOWERCASES EVERYTHING AFTER THE FIRST CHARACTER, which
#: destroyed 2 kinds of token in headings it had already shipped. Found
#: 2026-11-12 while rendering that morning's companion.
#:
#: (1) AN ENTRY IDENTIFIER. `B50's price list is wrong` shipped in the
#:     2026-10-30 report as `b50's`. A lowercased identifier is not the
#:     identifier: it cannot be matched against the task list, and this project
#:     requires a code to travel with its subject precisely so a reader can
#:     follow it.
#: (2) THE PRONOUN `I`, in 7 headings across the 2026-10-30, 2026-11-01 and
#:     2026-11-12 reports -- `the part i would want you to read first`.
#:
#: WHY NOT AN ACRONYM ALLOWLIST TOO. The source line is ALL CAPS by the time it
#: reaches here (`L.isupper()` is the gate above), so case carries NO signal and
#: `THE` is indistinguishable from `UX` by shape alone. A list of acronyms would
#: be an addition nothing reaches: measured over every heading in all 3 affected
#: reports, 0 carry an acronym and 2 token shapes carry the damage. So the rule
#: is driven by what the record actually holds -- a token bearing a DIGIT, and
#: the standalone pronoun -- and not by what might one day appear.
_ID_TOKEN = re.compile(r"^([A-Z]+[0-9][A-Za-z0-9]*|[0-9]+[A-Z][A-Za-z0-9]*)(['’][A-Za-z]+)?$")


def _recase(line: str) -> str:
    """`capitalize()`, then put back the tokens it had no right to lower."""
    out = line.capitalize()
    src, got = line.split(" "), out.split(" ")
    if len(src) != len(got):
        return out                      # shapes diverged; change nothing
    for i, s in enumerate(src):
        bare = s.strip(".,;:()[]\"")
        if bare == "I":
            got[i] = s
            continue
        m = _ID_TOKEN.match(bare)
        if m:
            #: Keep the identifier exactly; lower only a trailing possessive,
            #: so `B50'S` becomes `B50's` and not `B50'S`.
            kept = m.group(1) + (m.group(2).lower() if m.group(2) else "")
            got[i] = s.replace(bare, kept, 1)
    #: ★ AND THE 3RD THING `capitalize()` GETS WRONG: it capitalises the FIRST
    #: character of the whole string and nothing else, so every sentence after a
    #: full stop is lowered. `WHY I KEPT STOPPING. MEASURED, AND NOW FIXED`
    #: shipped as `Why I kept stopping. measured, and now fixed`. Only a lower
    #: case letter following a sentence end is raised, so an identifier or a
    #: restored pronoun already in place is never touched twice.
    return re.sub(r"([.!?]\s+)([a-z])",
                  lambda m: m.group(1) + m.group(2).upper(),
                  " ".join(got))


def render(date: str = DEFAULT_DATE) -> str:
    """The markdown companion, as a string. Writes nothing."""
    src = source(date)
    txt = src.read_text()
    # The foot is matched by PREFIX, because the 2 reports word it differently
    # ("... v1.8." against "... v1.8 (17 October 2026)."), and the split is done
    # by INDEX so that everything before it survives byte for byte. Rebuilding
    # the body from stripped lines instead lost the 2 blank lines that separate
    # the prose from the appendix, which showed up immediately as a 7-line diff
    # against the committed 2026-10-30 companion.
    foot_lines = [L for L in txt.split("\n") if L.startswith(FOOT_PREFIX)]
    if not foot_lines:
        raise ValueError(
            f"{src} does not end with the note-standard foot-line, so it is "
            f"either incomplete or not a compliant note")
    foot_line = foot_lines[-1]
    cut = txt.rindex(foot_line)

    foot = txt[cut:]
    body = txt[:cut].split("\n")
    part_style = any(L.startswith("PART ") for L in body)
    out = []
    for i, L in enumerate(body):
        if L.startswith("SECTION "):
            m = re.match(r"SECTION (\d+)\.\s+(.*)", L)
            out.append("## %s. %s" % (m.group(1), _recase(m.group(2))))
        elif L.startswith("PART "):
            # Case is PRESERVED: these headings are deliberately shouted.
            out.append("## " + L)
        elif L.isupper() and len(L) > 25 and not L.startswith(" "):
            out.append("### " + _recase(L))
        elif i == 0:
            out.append("# " + (L if part_style else L.title()))
        else:
            out.append(_emphasise_lead(L) if part_style else L)
    tail = APPENDICES.get(date, "")
    return "\n".join(out) + tail + foot


#: How many diff lines `--check` prints before it stops. A cap is right -- a
#: 2,000-line diff in a terminal is unreadable -- but a cap that does not say
#: what it withheld is a silent falsehood, which is the defect
#: `test_no_script_prints_a_capped_listing_in_silence` caught in this very file
#: on 2026-10-30, the 3rd defect found in it in a day.
_DIFF_LINES_SHOWN = 40


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare only; write nothing and exit 1 on a mismatch")
    ap.add_argument("--date", default=DEFAULT_DATE,
                    help=f"report date to rebuild (default {DEFAULT_DATE})")
    args = ap.parse_args(argv)

    REPO_TXT, DESKTOP_TXT, DST = paths(args.date)
    built = render(args.date)
    if args.check:
        have = DST.read_text() if DST.is_file() else ""
        if have == built:
            print(f"OK - {DST.relative_to(REPO)} matches its source "
                  f"({source(args.date).relative_to(REPO.parent)})")
            return 0
        diff = list(difflib.unified_diff(
            have.split("\n"), built.split("\n"),
            fromfile="committed", tofile="rebuilt", lineterm="", n=1))
        print(f"MISMATCH - {DST.relative_to(REPO)} differs from a rebuild; "
              f"{len(diff)} diff line(s). Fix the GENERATOR, not the markdown: "
              f"a hand edit here is undone by the next rebuild.")
        for line in diff[:_DIFF_LINES_SHOWN]:
            print(f"  {line}")
        if len(diff) > _DIFF_LINES_SHOWN:
            print(f"  ... and {len(diff) - _DIFF_LINES_SHOWN} further diff "
                  f"line(s) not shown")
        return 1

    DST.write_text(built)
    print(f"rebuilt {DST.relative_to(REPO)} "
          f"({len(built.splitlines())} lines) from {source(args.date).name}")
    # keep the 2 spoken copies in agreement, whichever was the source
    txt = source(args.date).read_text()
    for other in (REPO_TXT, DESKTOP_TXT):
        if other.is_file() and other.read_text() != txt:
            other.write_text(txt)
            print(f"synced {other}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
