#!/usr/bin/env python3
"""The note linter's finding count depends on the FILE'S PATH, not only its text.

WHY THIS IS MEASURED RATHER THAN RECALLED. On 2026-11-01 the same bytes of
`resources/RECOVERY.md` were linted twice during an `sv` and returned 688
findings at one scratchpad filename and 460 at another. A lint count was then
briefly compared against a count taken at a different path, which is the
like-for-like error already recorded on 2026-10-15 -- but the 2026-10-15 lesson
says the DIRECTORY matters. If the FILENAME matters too, every before/after
comparison that renames the file is invalid, including the obvious
`git show HEAD:f > /tmp/f_head.md` idiom.

WHAT THIS SCRIPT DOES. It takes one real document, copies its EXACT BYTES to
several paths that differ only in name or directory, lints each, and reports the
counts. Identical bytes must give an identical count or the instrument is
path-sensitive. No claim is made about WHY; the measurement is the point.

THE CORRECT COMPARISON IDIOM, if path-sensitivity is confirmed: copy BOTH
versions to the SAME path in turn and lint that one path twice.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINT = REPO / "scripts" / "note_vagueness_lint.py"

#: Names chosen to vary ONE thing at a time: the stem, the suffix-ish decoration,
#: and the directory depth. All receive byte-identical content.
VARIANTS = [
    "cmp.md",
    "RECOVERY.md",
    "RECOVERY_head.md",
    "recovery.md",
    "note.md",
    "sub/RECOVERY.md",
]


def count_for(path: Path) -> int | None:
    r = subprocess.run([sys.executable, str(LINT), str(path)],
                       capture_output=True, text=True, cwd=str(REPO))
    for line in reversed(r.stdout.splitlines()):
        line = line.strip()
        if "finding" in line and line[:1].isdigit():
            return int(line.split()[0])
    return None


def measure(source: Path) -> dict:
    raw = source.read_bytes()
    out: dict[str, int | None] = {}
    with tempfile.TemporaryDirectory() as td:
        for name in VARIANTS:
            p = Path(td) / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
            out[name] = count_for(p)
    in_place = count_for(source)
    return {"source": str(source.relative_to(REPO)),
            "bytes": len(raw),
            "at_its_real_path": in_place,
            "at_variant_paths": out}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default="resources/RECOVERY.md")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    src = REPO / args.source
    if not src.exists():
        print(f"no such source: {args.source}")
        return 2
    res = measure(src)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"SOURCE: {res['source']}  ({res['bytes']:,} bytes, byte-identical copies)")
    print(f"  linted at its own real path : {res['at_its_real_path']}")
    print("  linted at variant paths:")
    vals = res["at_variant_paths"]
    for name, n in vals.items():
        print(f"      {name:<24} {n}")
    distinct = sorted({v for v in vals.values() if v is not None})
    allvals = sorted({v for v in list(vals.values()) + [res["at_its_real_path"]]
                      if v is not None})
    print()
    print(f"DISTINCT COUNTS across variant paths : {len(distinct)}  {distinct}")
    print(f"DISTINCT COUNTS including real path  : {len(allvals)}  {allvals}")
    print()
    if len(allvals) > 1:
        print("PATH-SENSITIVE: CONFIRMED. Identical bytes give different counts.")
        print("  => A before/after lint comparison is VALID ONLY at ONE fixed path.")
        print("     Copy each version to the SAME path in turn and lint that path.")
        print("     `git show HEAD:f > /tmp/f_head.md` and comparing to f is INVALID.")
    else:
        print("PATH-SENSITIVE: NOT REPRODUCED on these variants.")
        print("  => The 688-vs-460 observation is then NOT explained by the path,")
        print("     and the cause must be found before any lesson is drawn from it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
