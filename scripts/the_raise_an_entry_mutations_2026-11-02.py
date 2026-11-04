#!/usr/bin/env python3
"""Break each surface in turn and require the raise-an-entry checker to notice.

A CHECKER I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. This one was written
because 8 of 13 completed commit attempts on 2026-11-02 were refused, 0.615385,
Wilson 95% [0.355229, 0.822903], and 3 of those were an entry whose other
surfaces were not reached. A tool built in response to my own incompleteness is
exactly the tool I should not take on trust.

3 MUTATIONS, EACH ON A DIFFERENT SURFACE, each restored by hash:
  M1  the authored detail for the entry is removed   -> surface 4 must fail
  M2  its `spoken_heading` is removed                -> surface 5 must fail
  M3  the 2 spoken mirrors are made to differ        -> surface 6 must fail
  M4  the canonical asking sentence is removed       -> surface 7 must fail

THE REGISTER IS DELIBERATELY NOT MUTATED. `bench/tickets/tickets.jsonl` is
append-only by design, so a mutation there could not be restored by rewriting a
file, and a harness that cannot restore what it found is the fault recorded on
2026-11-01 when `git checkout --` ate the subject of the work. Surface 3 is
covered by the guard's live assertions instead.
"""
from __future__ import annotations
import argparse

import hashlib
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "raise_an_entry_2026-11-02.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
DESK = (pathlib.Path.home() / "Desktop" / "CDSFL_tts"
        / "Decisions_Awaiting_You_2026-11-02.txt")
ENTRY = "B87"


def _check():
    spec = importlib.util.spec_from_file_location("_rae_m", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_rae_m"] = m
    try:
        spec.loader.exec_module(m)
        return m.check(ENTRY)
    finally:
        sys.modules.pop("_rae_m", None)


def _fails(rows, n: int) -> bool:
    """Did the surface whose name starts with `n.` fail?"""
    for name, ok, _ in rows:
        if name.startswith(f"{n}."):
            return not ok
    return False


def _summary() -> str:
    """The harness's own first docstring line, so `--help` needs no new prose."""
    doc = (__doc__ or "").strip()
    return doc.splitlines()[0] if doc else "mutation harness; writes and restores"


def main() -> int:
    # ★ `--help` MUST NOT MUTATE ANYTHING, 2026-11-03. This harness WRITES: it
    # reverses a property in the tree, runs the suite, then restores. With no
    # parser, `--help` fell straight through to that work, so asking what the
    # script does would have mutated the repository and then put it back -- a
    # write that leaves no diff is still a write, and a concurrent reader would
    # have seen the mutated state. His standing rule is that a `--help` must
    # never cost money; here it could have cost a tree.
    #
    # Measured by `scripts/help_writers_rate_2026-09-17.py`: 5 of 609 scripts
    # wrote and ignored the flag -- 0.8210%, Wilson 95% [0.3512%, 1.9074%],
    # Clopper-Pearson [0.2671%, 1.9055%] -- and all 5 were mutation harnesses
    # written on 2026-11-02, so this is 1 defect made 5 times in 1 day.
    argparse.ArgumentParser(
        description=_summary()).parse_args()
    d0, k0 = DETAIL.read_bytes(), (DESK.read_bytes() if DESK.is_file() else None)
    h0 = hashlib.sha256(d0).hexdigest()
    g0 = hashlib.sha256(k0).hexdigest() if k0 is not None else None
    results: list[tuple[str, bool, str]] = []
    try:
        base = _check()
        bad = [n for n, ok, _ in base if not ok]
        results.append(("the UNMUTATED record reaches every surface",
                        not bad, "all reached" if not bad else f"unreached: {bad}"))

        # M1 -- the authored detail disappears
        d = json.loads(d0.decode())
        d.pop(f"task:{ENTRY}", None)
        DETAIL.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        r = _check()
        results.append(("M1 the authored detail removed -> surface 4 fails",
                        _fails(r, 4), "caught" if _fails(r, 4) else
                        "MISSED: the generator's own check did not refuse"))

        # M2 -- the join field disappears
        d = json.loads(d0.decode())
        d[f"task:{ENTRY}"].pop("spoken_heading", None)
        DETAIL.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        r = _check()
        results.append(("M2 the spoken_heading removed -> surface 5 fails",
                        _fails(r, 5), "caught" if _fails(r, 5) else
                        "MISSED: the surfaces were reported as agreeing"))
        DETAIL.write_bytes(d0)

        # M3 -- the mirrors diverge
        if k0 is not None:
            DESK.write_bytes(k0 + b"\n")
            r = _check()
            results.append(("M3 the spoken mirrors made to differ -> surface 6 fails",
                            _fails(r, 6), "caught" if _fails(r, 6) else
                            "MISSED: a 1-byte divergence went unnoticed"))
        else:
            results.append(("M3 the spoken mirrors made to differ",
                            False, "SKIPPED: no Desktop mirror found"))

        # M4 -- the canonical asking sentence disappears from the ENTRY'S TEXT.
        #
        # WHY THIS MUTATION EXISTS: surface 7 was added only AFTER this tool
        # passed an entry the commit gate then refused twice. Checks 4 and 5
        # read the generator and the spoken file; the 3rd decision instrument
        # reads each entry's OWN TEXT and needs `**NEEDS HIS RULING:**` to see
        # an ask at all. Without this mutation, surface 7 would be an addition
        # no test reaches -- the shape the additive standard names.
        t0 = TASK_LIST.read_bytes()
        th0 = hashlib.sha256(t0).hexdigest()
        try:
            txt = t0.decode()
            if "**NEEDS HIS RULING:**" in txt:
                # EVERY occurrence, not the first. The first may belong to a
                # different entry, and the generator reads authored detail and
                # markers rather than asking sentences, so removing them all
                # changes ONLY the entry-text producer -- which is the surface
                # under test.
                TASK_LIST.write_text(
                    txt.replace("**NEEDS HIS RULING:**", "the question is"),
                    encoding="utf-8")
                r = _check()
                results.append(
                    ("M4 the canonical ask removed -> surface 7 fails",
                     _fails(r, 7),
                     "caught" if _fails(r, 7) else
                     "MISSED: the entry-text producer still read an ask"))
            else:
                results.append(
                    ("M4 the canonical ask removed -> surface 7 fails",
                     False, "SKIPPED: no canonical ask present to remove"))
        finally:
            TASK_LIST.write_bytes(t0)
        th1 = hashlib.sha256(TASK_LIST.read_bytes()).hexdigest()
        results.append(("the task list was restored byte-for-byte",
                        th0 == th1, f"{th0[:12]} -> {th1[:12]}"))
    finally:
        DETAIL.write_bytes(d0)
        if k0 is not None:
            DESK.write_bytes(k0)

    h1 = hashlib.sha256(DETAIL.read_bytes()).hexdigest()
    g1 = hashlib.sha256(DESK.read_bytes()).hexdigest() if DESK.is_file() else None
    print("=" * 74)
    print("DOES THE RAISE-AN-ENTRY CHECKER NOTICE A SURFACE GOING UNREACHED?")
    print("=" * 74)
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    restored = (h1 == h0) and (g1 == g0)
    print()
    print(f"  both files restored byte-for-byte: {restored}")
    print(f"    authored detail {h0[:12]} -> {h1[:12]}")
    print(f"    desktop mirror  {str(g0)[:12]} -> {str(g1)[:12]}")
    n = sum(1 for _, ok, _ in results if ok)
    print(f"  {n} of {len(results)} propert(ies) hold")
    return 0 if n == len(results) and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
