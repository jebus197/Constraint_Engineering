#!/usr/bin/env python3
"""The reversal check B132 owes: 4 mutations, each must turn the guard red.

A guard that passes is worth nothing until something has been shown to make it
fail. The 4 reversals below each remove one load-bearing part of the
postcondition, and the guard must catch every one.

IT RESTORES WHAT IT FOUND, from a byte copy taken here -- never from git. The
postcondition may be uncommitted when this runs, and `git checkout --` would
destroy it. That exact mistake is on this project's record.

Exit 0 iff every mutation is caught AND the original bytes are restored.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
T = REPO / "scripts" / "morning_report_build_2026-10-12.py"
TEST = "bench/tests/test_a_listed_item_carries_its_ticket_id_2026-11-08.py"

MUTATIONS = [
    ("main() stops calling the postcondition",
     "    _no_tid = items_missing_a_ticket_id(items)\n    if _no_tid:",
     "    _no_tid = []\n    if _no_tid:"),
    ("the store key is no longer stripped to its identifier",
     '    return key.split(":", 1)[1] if ":" in key else key',
     "    return key"),
    ("the scope is dropped, so a study defect is demanded an id",
     '_TICKETED_SOURCES = ("task:",)',
     '_TICKETED_SOURCES = ("task:", "defect:")'),
    ("the refusal stops using exit 3",
     'derived items are in that class.)")\n        return 3',
     'derived items are in that class.)")\n        return 0'),
]


def main() -> int:
    if not (REPO / TEST).is_file():
        print(f"REFUSED: no guard at {TEST}. Install it before reversing it; "
              f"a mutation harness with no guard reports nothing.")
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
                rows.append((label, "RED" if r.returncode != 0 else "GREEN (VACUOUS)",
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
    print(f"\n{red} of {len(MUTATIONS)} mutations caught")
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
