#!/usr/bin/env python3
"""4 reversals against the line-reference guard. Each must turn it red.

A guard that passes is worth nothing until something has been shown to make it
fail, and 2 of this session's own guards passed vacuously until a harness like
this said so. Each reversal below removes 1 load-bearing part of the fix.

IT RESTORES WHAT IT FOUND, from byte copies taken in-process rather than from
git, because the subject may be uncommitted and a checkout would destroy it.

Exit 0 iff every reversal is caught AND both files are restored byte-exactly.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
M = REPO / "scripts" / "task_list_markers.py"
G = REPO / "bench" / "tests" / "test_an_entrys_cited_evidence_must_exist_2026-11-04.py"
TEST = "bench/tests/test_a_line_reference_is_not_a_filename_2026-11-08.py"

MUTATIONS = [
    ("the function stops stripping the reference",
     M, '        target = (root / LINE_REF.sub("", name))',
     "        target = (root / name)"),
    ("the pattern stops matching a RANGE like :10-20",
     M, 'LINE_REF = re.compile(r":\\d+(?:-\\d+)?$")',
     'LINE_REF = re.compile(r":\\d+$")'),
    ("the pattern loses its anchor, so it strips mid-path digits too",
     M, 'LINE_REF = re.compile(r":\\d+(?:-\\d+)?$")',
     'LINE_REF = re.compile(r":\\d+(?:-\\d+)?")'),
    ("the guard goes back to its own copy of the pattern",
     G, "_LINE_REF = _markers.LINE_REF",
     '_LINE_REF = __import__("re").compile(r":\\d+(?:-\\d+)?$")'),
]


def main() -> int:
    # ★ `--help` MUST NOT DO THE WORK. Added 2026-11-08: 8 scripts of this
    # date wrote files while answering `--help`, which
    # `bench/tests/test_help_never_acts_2026-09-11.py` forbids and which
    # `feedback_help_must_never_cost_money` records as 15 of 17 runners
    # billing for a help request. A parser is used rather than
    # `_cli_help.answer_help` because an unrecognised argument then exits 2
    # instead of being ignored, and because it cannot be made unreachable
    # under `python3 -m`, which is how 5 of 9 earlier repairs failed.
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    if not (REPO / TEST).is_file():
        print(f"REFUSED: no guard at {TEST}. A harness with no guard reports "
              f"nothing.")
        return 1
    with tempfile.TemporaryDirectory() as td:
        saved = {}
        for p in (M, G):
            keep = pathlib.Path(td) / (p.name + ".before")
            shutil.copy2(p, keep)
            saved[p] = keep.read_bytes()
            assert len(saved[p]) > 2000, f"{p.name} copy implausibly small"
        print(f"saved {sum(len(v) for v in saved.values())} bytes across "
              f"{len(saved)} file(s)\n")
        rows = []
        try:
            for label, path, old, new in MUTATIONS:
                src = saved[path].decode()
                if src.count(old) != 1:
                    rows.append((label, f"ANCHOR MISS ({src.count(old)})", ""))
                    continue
                path.write_text(src.replace(old, new, 1), encoding="utf-8")
                r = subprocess.run(
                    [sys.executable, "-m", "pytest", TEST, "-q", "-p",
                     "no:randomly"], capture_output=True, text=True,
                    cwd=str(REPO), timeout=600)
                tail = [ln for ln in r.stdout.splitlines()
                        if "passed" in ln or "failed" in ln or "error" in ln]
                rows.append((label, "RED" if r.returncode != 0
                             else "GREEN (VACUOUS)",
                             tail[-1] if tail else ""))
                path.write_bytes(saved[path])
        finally:
            for p, b in saved.items():
                p.write_bytes(b)
                assert p.read_bytes() == b, f"RESTORE FAILED for {p.name}"
            print("restored both files byte-exactly\n")

    for label, verdict, detail in rows:
        print(f"  {verdict:<16} {label}")
        if detail:
            print(f"                   {detail}")
    red = sum(1 for _l, v, _d in rows if v == "RED")
    print(f"\n{red} of {len(MUTATIONS)} reversals caught")
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
