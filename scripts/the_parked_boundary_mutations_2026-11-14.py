#!/usr/bin/env python3
"""Does the parked-boundary guard fail when the 2026-11-14 repair is reverted?

6 reversions, each of which must turn
`bench/tests/test_the_parked_boundary_is_honoured_2026-11-14.py` RED.

★ THE FAIL-OPEN MUTATIONS ARE THE POINT. Two of the six invert the direction of
the failure -- a renamed or absent boundary causing headings to be HIDDEN rather
than over-reported. That is the direction this project had to restore once after
a suppression removed live questions from the founder's list, and a guard that
cannot catch it is guarding the wrong half.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED THE FILE, and the subject is
restored from bytes captured before the first one, never with `git checkout --`.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "morning_report_build_2026-10-12.py"
GUARD = REPO / "bench" / "tests" / "test_the_parked_boundary_is_honoured_2026-11-14.py"

MUTATIONS = [
    ("the boundary is ignored entirely",
     "        if _PARKED_SETTLED_BOUNDARY.match(line):\n            break",
     "        if False:\n            break"),
    ("a renamed boundary HIDES instead of failing open",
     "def _parked_headings(text: str) -> list[str]:\n    \"\"\"Every LIVE `## ` heading, stopping at the file's settled boundary.\"\"\"\n    out: list[str] = []",
     "def _parked_headings(text: str) -> list[str]:\n    \"\"\"Every LIVE `## ` heading, stopping at the file's settled boundary.\"\"\"\n    if not any(_PARKED_SETTLED_BOUNDARY.match(l) for l in text.splitlines()):\n        return []\n    out: list[str] = []"),
    ("the boundary pattern becomes case SENSITIVE",
     'r"^#\\s+Settled\\b", re.I)',
     'r"^#\\s+Settled\\b")'),
    ("the boundary pattern matches a level-2 heading too",
     'r"^#\\s+Settled\\b"',
     'r"^#+\\s+Settled\\b"'),
    ("the reader collects deeper headings as well",
     '        if line.startswith("## "):\n            out.append(line[3:].strip())',
     '        if line.lstrip("#").strip() and line.startswith("#") and line.count("#") >= 2:\n            out.append(line.lstrip("# ").strip())'),
    ("the identifier filter is allowed to ADD headings the boundary excluded",
     "    headings = _parked_headings(PARKED.read_text(encoding=\"utf-8\"))",
     "    headings = [l[3:].strip() for l in PARKED.read_text(encoding=\"utf-8\").splitlines() if l.startswith(\"## \")]"),
]


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    original = SUBJECT.read_bytes()
    text = original.decode("utf-8")
    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation.")
        return 2
    red = misses = probe = 0
    try:
        for label, old, new in MUTATIONS:
            if old not in text:
                probe += 1
                print(f"  [PROBE FAILED] {label}: anchor absent, nothing mutated.")
                continue
            SUBJECT.write_text(text.replace(old, new, 1), encoding="utf-8")
            if SUBJECT.read_bytes() == original:
                probe += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged.")
                SUBJECT.write_bytes(original)
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}: the guard stayed GREEN.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)
    ok = SUBJECT.read_bytes() == original
    print(f"\n  subject restored byte-for-byte: {ok}")
    print(f"  {red} of {len(MUTATIONS)} mutations turned the guard RED; "
          f"{misses} MISS; {probe} probe failure(s)")
    if not ok:
        print("  RESTORE FAILED.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe == 0) else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    # The imports are LOCAL to this guard so it needs nothing of the host
    # file: a subject using `from pathlib import Path` binds `Path`, not
    # `pathlib`, and used to be declined for it.
    import pathlib as _hp_pathlib
    import sys as _hp_sys
    _hp_sys.path.insert(
        0, str(_hp_pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
