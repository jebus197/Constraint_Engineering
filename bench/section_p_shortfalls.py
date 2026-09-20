#!/usr/bin/env python3
"""Recorded Section-P shortfalls: rounds that fell short, with the measured cause.

Section P's guards assert that every archived panel reply meets its conditions.
When a round genuinely falls short, there are only 3 honest options:

  1. delete the round from the archive        -- destroys evidence;
  2. drop it from the measured population     -- makes the guard blind;
  3. RECORD it with its cause, and assert that nothing NEW joins the list.

This module is option 3, and it is the convention the guards already used for
`panel_roster_fix_2026-09-09`, which predated the disagreement field. The data
lives at bench/directives/universal/section_p_shortfalls.json so it reads as a
document rather than as test scaffolding.

WHAT THIS IS NOT. It is not a way to green a red suite. Every entry names the
defect that caused the shortfall and the test that now holds the fix, so a
reader can check the claim. A shortfall with no cause, or with a cause that is
an impression rather than a measurement, does not belong here.

The falsifier that stops this becoming a blanket pass lives beside the guards:
an invented round must NOT be excused by this list.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHORTFALLS = REPO / "bench" / "directives" / "universal" / "section_p_shortfalls.json"


def _load() -> list[dict]:
    if not SHORTFALLS.is_file():
        # FAIL CLOSED: a missing file excuses nothing.
        return []
    return json.loads(SHORTFALLS.read_text(encoding="utf-8")).get("shortfalls", [])


def recorded(condition: str) -> set[tuple[str, str]]:
    """The (round, seat) pairs recorded as shortfalls for `condition`."""
    return {(e["round"], e["seat"]) for e in _load()
            if e.get("condition") == condition and e.get("seat")}


def recorded_rounds(condition: str) -> set[str]:
    return {e["round"] for e in _load() if e.get("condition") == condition}


def is_recorded(condition: str, round_name: str, seat: str) -> bool:
    return (round_name, seat) in recorded(condition)


def main(argv: list | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)
    entries = _load()
    print(f"Recorded Section-P shortfalls: {len(entries)}")
    for e in entries:
        state = "fixed" if e.get("fixed") else "OPEN"
        print(f"  {e.get('condition')}  {e.get('round')}/{e.get('seat')}  [{state}]")
        print(f"      {e.get('what')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
