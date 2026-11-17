#!/usr/bin/env python3
"""Does the B195 watchable-board guard fail when the repair is reverted?

Reverts `scripts/cdsfl_sv.py`'s streaming path 5 distinct ways and requires
`bench/tests/test_the_commit_board_can_be_watched_2026-11-17.py` to go RED each
time.

★ MUTATION 1 IS THE HISTORICAL DEFECT, not an invented one: the streaming path
removed entirely so every caller is buffered again, which is the state the
repair was written against.

★ THE SUBJECT IS RESTORED FROM BYTES CAPTURED BEFORE THE FIRST MUTATION, never
with `git checkout --`, which in this project once ate the file under test, and
the restore is verified by comparing bytes because a restore is a mutation too.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

for _cand in (Path(__file__).resolve().parent, *Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "cdsfl_sv.py"
GUARD = REPO / "bench" / "tests" / "test_the_commit_board_can_be_watched_2026-11-17.py"

MUTATIONS = [
    ("1 THE HISTORICAL DEFECT: no streaming path at all",
     "    if stream:\n        return _git_streamed(*args, root=root, timeout=timeout, check=check)\n",
     ""),
    ("2 the default flipped on, so 23 callers start streaming",
     "    stream: bool = False,\n",
     "    stream: bool = True,\n"),
    ("3 the deadline removed from the read loop, so a hang is for ever",
     "            if _time.monotonic() > deadline:\n"
     "                raise subprocess.TimeoutExpired([\"git\", *args], timeout)\n",
     ""),
    ("4 nothing echoed, so nothing can be watched",
     "            sys.stdout.write(line)\n            sys.stdout.flush()\n",
     ""),
    ("5 the return value dropped, so the 2 arms disagree",
     "    return out.strip()\n",
     "    return \"\"\n"),
]


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main(argv=None) -> int:
    answer_help(__doc__, __file__, argv)
    original = SUBJECT.read_bytes()
    text = original.decode("utf-8")

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation. A harness cannot "
              "tell a mutation from a pre-existing failure.")
        return 2

    red = misses = probes = 0
    try:
        for label, old, new in MUTATIONS:
            if old not in text:
                probes += 1
                print(f"  [PROBE FAILED] {label}: anchor absent. The probe is "
                      f"stale, not the guard.")
                continue
            SUBJECT.write_text(text.replace(old, new, 1), encoding="utf-8")
            if SUBJECT.read_bytes() == original:
                probes += 1
                print(f"  [PROBE FAILED] {label}: the file did not change.")
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS] {label}: the guard stayed GREEN on broken code.")
            else:
                red += 1
                print(f"  [RED]  {label}")
    finally:
        SUBJECT.write_bytes(original)

    if SUBJECT.read_bytes() != original:
        print("  RESTORE FAILED — the subject is not what it was.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print(f"\n  {red} of {len(MUTATIONS)} mutations turned the guard RED; "
          f"{misses} MISS; {probes} probe failure(s)")
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probes == 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
