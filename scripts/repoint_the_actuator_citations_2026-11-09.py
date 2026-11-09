#!/usr/bin/env python3
"""Re-point the actuator's declared citations after the runner moves.

WHY THIS EXISTS, AND WHY THE CITATIONS ARE NOT MADE SELF-HEALING INSTEAD.
`bench/tools/cy_actuator_2026-11-03.py` pins each contract claim to a FILE AND
LINE plus the substring that line must hold, and
`bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py` fails when a
line no longer holds its substring. That is the pin working: any edit above a
citation moves it, and the failure forces a human to confirm the citation still
names the right site. A citation that silently followed its substring would
follow it to the WRONG site just as willingly, which is the defect recorded as
`a_pin_must_live_outside_what_it_measures`. So the churn is the price of the
guard, not a fault in it.

WHAT IS A FAULT IS DOING THE ARITHMETIC BY HAND. On 2026-11-09 the 6 A2
citations moved +144 and then +15 within a few hours, and `sys.exit(42)` occurs
at BOTH the round and the phase site, so taking the first match for both would
have left one citation pointing at the wrong block WHILE THE GUARD PASSED. This
script resolves that the only way it can be resolved safely: candidates are
searched in table order and each must come AFTER the one before it, so block
order disambiguates identical substrings.

It reports the distinct deltas. ONE distinct delta means a clean block shift and
nothing within the block moved relative to anything else -- the cheap signal
that the move was mechanical. SEVERAL deltas mean the block itself changed
shape, and every citation then needs reading by eye before it is accepted.

    python3 scripts/repoint_the_actuator_citations_2026-11-09.py            # report only
    python3 scripts/repoint_the_actuator_citations_2026-11-09.py --apply    # write
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ACTUATOR = REPO / "bench/tools/cy_actuator_2026-11-03.py"

_ENTRY = re.compile(
    r'"(?P<key>[A-Za-z0-9_.]+)":\s*\(\s*"(?P<path>[^"]+)",\s*(?P<line>\d+),'
    r'\s*\n\s*"(?P<needle>(?:[^"\\]|\\.)*)"\s*\)')


def _plan(src: str):
    """Candidate new line for every citation, in table order.

    The floor is the previous citation's new line, so an identical substring
    occurring at 2 sites resolves by block order rather than by `str.find`.
    """
    plan, floors = [], {}
    for m in _ENTRY.finditer(src):
        path, old = m.group("path"), int(m.group("line"))
        needle = m.group("needle").encode().decode("unicode_escape")
        target = REPO / path
        if not target.exists():
            plan.append((m, old, None, needle, "file is gone"))
            continue
        lines = target.read_text(encoding="utf-8").splitlines()
        floor = floors.get(path, 0)
        cands = [i + 1 for i, l in enumerate(lines)
                 if needle in l and i + 1 > floor]
        if not cands:
            plan.append((m, old, None, needle, "substring not found below the floor"))
            continue
        new = min(cands, key=lambda c: abs(c - old))
        floors[path] = new
        plan.append((m, old, new, needle, ""))
    return plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="write the new line numbers (default: report only)")
    args = ap.parse_args(argv)

    src = ACTUATOR.read_text(encoding="utf-8")
    plan = _plan(src)
    if not plan:
        print("no citations found -- the table's shape has changed")
        return 2

    print(f"{'CITATION':24s} {'OLD':>7s} {'NEW':>7s} {'DELTA':>7s}  SUBSTRING")
    moved, broken = [], []
    for m, old, new, needle, why in plan:
        key = m.group("key")
        if new is None:
            broken.append((key, why))
            print(f"{key:24s} {old:7d} {'--':>7s} {'--':>7s}  {needle[:40]!r}  <- {why}")
            continue
        mark = "" if old == new else "  <- moves"
        print(f"{key:24s} {old:7d} {new:7d} {new-old:+7d}  {needle[:40]!r}{mark}")
        if old != new:
            moved.append((m, old, new))

    deltas = sorted({new - old for _, old, new in moved})
    print()
    if not moved:
        print("every citation still points at its substring; nothing to do")
    else:
        print(f"{len(moved)} citation(s) move; distinct deltas: {deltas}")
        if len(deltas) == 1:
            print("  1 delta -> a clean block shift, nothing moved WITHIN the block")
        else:
            print("  SEVERAL deltas -> the block changed shape. READ EVERY "
                  "CITATION BY EYE before accepting this.")
    if broken:
        print(f"\n{len(broken)} citation(s) CANNOT be re-pointed and need a human:")
        for key, why in broken:
            print(f"  {key}: {why}")

    if args.apply and moved:
        out = src
        for m, old, new in moved:
            out = out.replace(m.group(0),
                              m.group(0).replace(f", {old},", f", {new},", 1), 1)
        compile(out, str(ACTUATOR), "exec")
        ACTUATOR.write_text(out, encoding="utf-8")
        print(f"\nwrote {len(moved)} new line number(s) to {ACTUATOR.relative_to(REPO)}")
    elif moved:
        print("\nreport only; pass --apply to write")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
