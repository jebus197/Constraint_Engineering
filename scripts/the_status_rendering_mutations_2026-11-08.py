#!/usr/bin/env python3
"""5 reversals against the status-rendering guard. Each must turn it red.

A guard that passes is worth nothing until something has been shown to make it
fail, and this guard's own first version was written to watch 1 of 2 renderers
while the fix was applied to only that one -- so the half the founder actually
reads stayed wrong and nothing said so. Each reversal below removes 1
load-bearing part.

IT RESTORES WHAT IT FOUND, from a byte copy taken in-process rather than from
git, because the subject may be uncommitted and a checkout would destroy it.
That mistake is on this project's record.

Exit 0 iff every reversal is caught AND the original bytes are restored.
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
T = REPO / "scripts" / "morning_report_build_2026-10-12.py"
TEST = "bench/tests/test_a_study_defects_status_reaches_him_2026-11-08.py"

MUTATIONS = [
    ("the WRITTEN renderer stops reading the status",
     '        _st = str(o.get("status") or "").strip()',
     '        _st = ""'),
    ("the SPOKEN renderer stops reading the status",
     '        _sst = str(o.get("status") or "").strip()',
     '        _sst = ""'),
    ("the extractor pre-cuts the status again, taking the decision back",
     '            "status": str(drec.get("status", "")),',
     '            "status": str(drec.get("status", ""))[:60],'),
    ("the spoken copy uses a different cap, so the 2 disagree again",
     "            _sshown = _sst[:200]",
     "            _sshown = _sst[:150]"),
    ("the spoken status skips the normaliser, so backticks are read aloud",
     '            A("Recorded status: " + _spoken(_sshown)',
     '            A("Recorded status: " + str(_sshown)'),
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
        print(f"REFUSED: no guard at {TEST}. A mutation harness with no guard "
              f"reports nothing.")
        return 1
    with tempfile.TemporaryDirectory() as td:
        keep = pathlib.Path(td) / "before.py"
        shutil.copy2(T, keep)
        original = keep.read_bytes()
        assert len(original) > 20000, "the saved copy is implausibly small; refusing"
        print(f"saved {len(original)} bytes before mutating\n")
        rows = []
        try:
            for label, old, new in MUTATIONS:
                src = original.decode()
                if src.count(old) != 1:
                    rows.append((label, f"ANCHOR MISS ({src.count(old)})", ""))
                    continue
                T.write_text(src.replace(old, new, 1), encoding="utf-8")
                r = subprocess.run(
                    [sys.executable, "-m", "pytest", TEST, "-q", "-p",
                     "no:randomly"], capture_output=True, text=True,
                    cwd=str(REPO), timeout=600)
                tail = [ln for ln in r.stdout.splitlines()
                        if "passed" in ln or "failed" in ln or "error" in ln]
                rows.append((label, "RED" if r.returncode != 0
                             else "GREEN (VACUOUS)",
                             tail[-1] if tail else ""))
        finally:
            T.write_bytes(original)
            assert T.read_bytes() == original, "RESTORE FAILED -- inspect the file"
            print("restored the original bytes exactly\n")

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
