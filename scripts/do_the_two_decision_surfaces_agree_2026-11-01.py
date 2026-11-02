#!/usr/bin/env python3
"""Do the 2 surfaces that tell him what he must decide agree on the SAME SET?

WHY THIS EXISTS. He challenged a decision count on 2026-11-01: *"Before I went
to sleep you said there were 10 decisions awaiting me. Now you say there are
4?"* The count was repaired that morning and the CLASS was not, so it recurred
the same evening in the worse direction: the generated report derived
{B21, B60, B61, B63} while the spoken file he was actually handed carried
{B21, B60, B61, B71}. Each surface was internally consistent, each was missing a
different decision, and no instrument compared them -- the `execute-do-not-grep`
shape, where 2 declarations of 1 fact have no comparator.

MEMBERSHIP IS THE FAULT, NOT THE COUNT. Both surfaces said 4. A count check
would have passed. The sets differed, so 1 real decision reached him and another
did not, which is why this script compares SETS and reports both directions
separately: a derived decision with no spoken heading (he is never asked) and a
spoken heading with no derived decision (he is asked for something the record
does not track).

HOW THE 2 SURFACES ARE JOINED. The spoken file deliberately carries no entry
codes, because a code read aloud is noise and the note standard forbids it. So
each authored decision carries a `spoken_heading` field, and that field is the
join. A decision with no `spoken_heading` is itself a finding: it cannot be
checked, which is the unwired-addition shape `additive-standard` forbids.

TOOLS. z3 decides the bijection rather than a loop asserting it, and SymPy's
FiniteSet equality is the independent second opinion, per the 2-tool rule.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
SPOKEN_GLOB = "Decisions_Awaiting_You_*.txt"
SPOKEN_DIR = REPO / "experimental_notes"
#: `DECISION 7.` or `### DECISION 7.`, then the heading text on the same line.
_HEADING = re.compile(r"^(?:#+\s*)?DECISION\s+(\d{1,2})\.\s*(.+?)\s*$", re.M)


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def derived() -> list[tuple[str, str]]:
    """(ident, spoken_heading) for every decision the generator would print."""
    sys.path.insert(0, str(REPO / "scripts"))
    mrb = _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb_surfaces")
    md = mrb.build(mrb._session_start()) if hasattr(mrb, "build") else None
    if md is None:                      # fall back to the rendered report
        import subprocess
        md = subprocess.run([sys.executable, str(REPO / "scripts"
                                                 / "morning_report_build_2026-10-12.py")],
                            capture_output=True, text=True, check=True).stdout
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    i1 = md.index("## 1. Decisions that need you")
    i2 = md.index("## 2. Work done this session")
    out = []
    for block in md[i1:i2].split("\n### ")[1:]:
        head = block.splitlines()[0]
        m = re.match(r"\d+\.\s+([A-Za-z]\d+|\S+)", head)
        ident = m.group(1) if m else head[:12]
        key = f"task:{ident}"
        spoken = (detail.get(key) or {}).get("spoken_heading")
        out.append((ident, spoken))
    return out


def spoken() -> tuple[pathlib.Path, list[tuple[int, str]]]:
    files = sorted(SPOKEN_DIR.glob(SPOKEN_GLOB))
    if not files:
        return None, []
    newest = files[-1]
    text = newest.read_text(encoding="utf-8")
    return newest, [(int(n), h.upper()) for n, h in _HEADING.findall(text)]


def main() -> int:
    import sympy as sp
    import z3

    d = derived()
    path, s = spoken()
    print("=" * 78)
    print("DO THE 2 DECISION SURFACES AGREE?")
    print("=" * 78)
    print(f"\ngenerated report : {len(d)} decision(s)")
    for ident, head in d:
        print(f"    {ident:6} -> {head or '*** NO spoken_heading, CANNOT BE CHECKED ***'}")
    print(f"\nspoken file      : {path.name if path else 'NONE FOUND'}, {len(s)} decision(s)")
    for n, head in s:
        print(f"    {n:>6} -> {head}")

    no_join = [i for i, h in d if not h]
    dset = {h for _, h in d if h}
    sset = {h for _, h in s}

    # ── z3: a total injective map from derived headings into spoken headings ──
    names = sorted(dset | sset)
    idx = {h: k for k, h in enumerate(names)}
    solver = z3.Solver()
    # one boolean per (derived, spoken) pairing; a derived heading must match
    # exactly 1 spoken heading and vice versa, so an unmatched member on either
    # side makes the system unsatisfiable.
    pair = {(a, b): z3.Bool(f"m_{idx[a]}_{idx[b]}") for a in dset for b in sset}
    # ★ EMPTY-SIDE GUARD, 2026-11-01. `z3.PbEq([], 1)` raises
    # `ValueError: not enough values to unpack` inside z3's own argument
    # handling, so whenever ONE side is empty this comparator CRASHED instead of
    # reporting. It hit the day it was written: every derived item lacked a
    # `spoken_heading`, which this script's own docstring names as a FINDING in
    # its own right, and the finding became a traceback. A comparator that
    # crashes yields NO verdict, which is strictly worse than a wrong one --
    # and it was about to block a commit while appearing to be a z3 bug.
    if not dset or not sset:
        z3_ok = (not dset) and (not sset)
    else:
        for a in dset:
            solver.add(z3.PbEq([(pair[(a, b)], 1) for b in sset], 1))
        for b in sset:
            solver.add(z3.PbEq([(pair[(a, b)], 1) for a in dset], 1))
        for (a, b), v in pair.items():
            if a != b:
                solver.add(z3.Not(v))
        z3_ok = solver.check() == z3.sat

    # ── SymPy: the independent second opinion ──
    # ★ THE HEADINGS GO IN AS INTEGERS, NOT STRINGS. `FiniteSet` sympifies its
    # arguments, so a heading like "PERMISSION TO MODIFY MY OWN STOP HOOK" is
    # parsed as an expression and raises SyntaxError on the second word. The
    # index map above is already a stable string-to-integer bijection, so the
    # set comparison is done on the integers and carries exactly the same
    # information without handing prose to a parser.
    sympy_ok = bool(sp.FiniteSet(*[idx[h] for h in dset])
                    == sp.FiniteSet(*[idx[h] for h in sset]))

    print("\nVERDICT")
    print(f"    z3 bijection exists      : {z3_ok}")
    print(f"    SymPy FiniteSet equality : {sympy_ok}")
    if z3_ok != sympy_ok:
        print("    ★ THE 2 TOOLS DISAGREE, so neither answer may be used.")
        return 4
    missing = sorted(dset - sset)
    extra = sorted(sset - dset)
    for h in missing:
        print(f"    DERIVED BUT NOT SPOKEN: {h}")
        print("      he is never asked this; add it to the spoken file")
    for h in extra:
        print(f"    SPOKEN BUT NOT DERIVED: {h}")
        print("      he is asked for something the record does not track")
    for i in no_join:
        print(f"    NO JOIN FOR {i}: add `spoken_heading` to its authored detail,")
        print("      or this decision can never be checked against the spoken file")
    if z3_ok and not no_join:
        print(f"\n    AGREE on all {len(dset)} decision(s).")
        return 0
    return 3


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
