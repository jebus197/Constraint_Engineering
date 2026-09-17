#!/usr/bin/env python3
"""Did CC1 take its own position, and synthesise the range across the seats?

THE CLAUSE, and until now nothing measured it. The `pr` protocol says the panel
runs *"WITHOUT compelled convergence so each model returns an independent verdict
and its strongest falsification and disagreement is preserved as information
rather than smoothed to consensus; CC1 actively participates with its own
position and synthesizes the range"*. Every other clause of P5 has an instrument.
This half had none: no test and no script asked whether CC1 stated a position of
its own, or whether the places the seats DISAGREED survived into the record.

FOUNDER, 2026-09-17: *"If this is a missing test/instrument, then build it and
implement it, and add it to the program of study for the next simulated run."*

WHAT IT MEASURES, from a round's own record and nothing else:

  1. **The range**, derived rather than asserted. Each seat's per-entry verdicts
     are parsed out of that seat's own reply, and the RANGE is the set of entries
     where 2 seats gave different verdicts. Nothing here is a model's opinion of
     a model: it is a set difference over tokens the seats wrote themselves.
  2. **CC1's own position**, as a section the record labels as such.
  3. **Whether the range reached it**: every disagreed entry named in that
     section, with a verdict of CC1's own beside it.

WHAT IT DOES NOT DO. It does not judge whether CC1's position is CORRECT -- that
would be a model scoring a model, which this project forbids (`no model voting`).
It reports coverage of a set that was computed from the seats' own words, and an
entry CC1 did not reach is named rather than counted as passing.

A round where the seats happened to agree everywhere has an EMPTY range, and the
script says so: 0 of 0 is reported as VACUOUS, never as satisfied. That
distinction is the whole reason the count is printed beside the verdict.

Read-only. `--json PATH` writes the measurement; nothing else writes anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: An entry identifier as the task list writes them: A23, V8, R5a, 10.2, 4.3.
ID = re.compile(r"\b([A-Z]{1,2}\d{1,3}[a-z]?|\d{1,2}\.\d{1,2})\b")
#: The verdict tokens the briefs ask seats to use.
VERDICT = re.compile(r"\b(HOLDS|FAILS|PARTIAL|UNCHECKED|UNVERIFIED|WITHDRAWN)\b")
#: `- **entry**: A23`, cc2's block shape, where the verdict is on a later line.
ENTRY_DECL = re.compile(r"\*\*entry\*\*:\s*`?([A-Z]{1,2}\d{1,3}[a-z]?|\d{1,2}\.\d{1,2})", re.I)
SEAT_HEADING = re.compile(r"^##\s+Seat:\s*(\S+)", re.M)
#: The section that carries CC1's own position. Named 3 ways so a record written
#: before this script existed is not failed for a wording choice.
CC1_HEADING = re.compile(r"^#{1,3}\s+.*\bCC1\b.*\b(position|synthesis|synthesise|synthesize)\b",
                         re.M | re.I)


def seat_sections(text: str) -> dict:
    """{seat name: that seat's own reply}, split on the record's seat headings."""
    marks = list(SEAT_HEADING.finditer(text))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out[m.group(1).strip("`* ")] = text[m.start():end]
    return out


def verdicts(section: str) -> dict:
    """{entry id: verdict}, read from 1 seat's own words.

    2 shapes, because the seats write 2: a single line carrying the entry and its
    verdict together (`**A24** -- ... **HOLDS.**`), and a block that declares the
    entry first and gives the verdict a few lines later.
    """
    found, current = {}, None
    for line in section.splitlines():
        decl = ENTRY_DECL.search(line)
        if decl:
            current = decl.group(1).upper()
            continue
        ids = {i.upper() for i in ID.findall(line)}
        verds = VERDICT.findall(line)
        if not verds:
            continue
        if len(ids) == 1:
            found.setdefault(next(iter(ids)), verds[0])
        elif not ids and current:
            found.setdefault(current, verds[0])
            current = None
    return found


def the_range(per_seat: dict) -> dict:
    """The entries the seats did NOT agree on: {id: {seat: verdict}}."""
    everywhere = {}
    for seat, table in per_seat.items():
        for ident, v in table.items():
            everywhere.setdefault(ident, {})[seat] = v
    return {i: s for i, s in everywhere.items()
            if len(s) > 1 and len({v for v in s.values()}) > 1}


def cc1_section(text: str) -> str | None:
    m = CC1_HEADING.search(text)
    if not m:
        return None
    nxt = re.compile(r"^#{1,3}\s+", re.M).search(text, m.end())
    return text[m.start():nxt.start() if nxt else len(text)]


def measure(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    per_seat = {s: verdicts(sec) for s, sec in seat_sections(text).items()}
    rng = the_range(per_seat)
    section = cc1_section(text)
    covered, missing = {}, []
    for ident, seats in sorted(rng.items()):
        if section is None:
            missing.append(ident)
            continue
        named = re.search(rf"\b{re.escape(ident)}\b", section)
        own = bool(named and VERDICT.search(section))
        if named and own:
            covered[ident] = {"seats": seats}
        else:
            missing.append(ident)
    if section is None:
        verdict = "NO_CC1_POSITION"
    elif not rng:
        verdict = "VACUOUS"          # the seats agreed everywhere: nothing to synthesise
    elif missing:
        verdict = "RANGE_NOT_COVERED"
    else:
        verdict = "SATISFIED"
    return {
        "record": str(path),
        "seats": {s: len(t) for s, t in per_seat.items()},
        "entries_with_a_verdict_from_more_than_1_seat":
            len([i for i, s in _everywhere(per_seat).items() if len(s) > 1]),
        "range": {i: s for i, s in sorted(rng.items())},
        "cc1_position_section": bool(section),
        "range_covered": sorted(covered),
        "range_missing": sorted(missing),
        "verdict": verdict,
    }


def _everywhere(per_seat: dict) -> dict:
    out = {}
    for seat, table in per_seat.items():
        for ident, v in table.items():
            out.setdefault(ident, {})[seat] = v
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("record", nargs="?", type=pathlib.Path,
                    help="a panel round's FULL_RECORD markdown file")
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args(argv)

    if a.record is None:
        records = sorted((REPO / "experimental_notes").glob("Panel_Round*_FULL_RECORD_*.md"))
        if not records:
            print("no panel round record found; nothing to measure")
            return 2
        a.record = records[-1]
    if not a.record.is_file():
        print(f"no such record: {a.record}")
        return 2

    out = measure(a.record)
    print(json.dumps(out, indent=2))
    if out["verdict"] == "NO_CC1_POSITION":
        print("\nThe record carries no section stating CC1's own position, so the P5 clause "
              "'CC1 actively participates with its own position and synthesizes the range' "
              "is NOT met by this round.")
    elif out["verdict"] == "RANGE_NOT_COVERED":
        print(f"\nThe seats disagreed on {len(out['range'])} entry/entries and CC1's section "
              f"does not reach {', '.join(out['range_missing'])}.")
    elif out["verdict"] == "VACUOUS":
        print("\nThe seats gave no conflicting verdict, so there is no range to synthesise. "
              "This is reported as VACUOUS rather than as a pass.")
    else:
        print(f"\nSatisfied: {len(out['range_covered'])} disagreed entry/entries, all named "
              f"in CC1's own position.")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0 if out["verdict"] == "SATISFIED" else 3


if __name__ == "__main__":
    sys.exit(main())
