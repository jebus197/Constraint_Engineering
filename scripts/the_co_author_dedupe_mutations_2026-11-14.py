#!/usr/bin/env python3
"""Does the co-author dedupe guard actually fail when the repair is reverted?

A guard that passes on broken code guards nothing. This harness reverts the
repair 6 distinct ways and requires `bench/tests/
test_the_co_author_trailer_is_not_doubled_2026-11-14.py` to go RED each time.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED THE FILE. An edit whose pattern no
longer matches leaves the subject intact, the test passes, and the harness would
report that as a MISS -- a false alarm about the guard when the fault is the
probe. This project has already recorded 2 of 5 misses being the probe rather
than the guard, so each mutation asserts the bytes moved before it runs anything.

★ THE SUBJECT IS RESTORED FROM BYTES CAPTURED BEFORE THE FIRST MUTATION, never
with `git checkout --`, which in this project once ate the file under test. The
restore is itself verified by comparing bytes, because a restore is a mutation
too.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "cdsfl_sv.py"
GUARD = REPO / "bench" / "tests" / "test_the_co_author_trailer_is_not_doubled_2026-11-14.py"

#: label -> (what it reverts, old, new). Each must change the file.
MUTATIONS = [
    ("call site appends unconditionally",
     "        full_msg = _append_co_author(message, trailer)",
     '        full_msg = f"{message}\\n\\n{trailer}"'),
    ("dedupe tests the WHOLE message as a substring",
     "    if is_trailer_block and trailer.strip() in lines:",
     "    if trailer.strip() in body:"),
    ("drops the trailer-block requirement",
     "    if is_trailer_block and trailer.strip() in lines:",
     "    if trailer.strip() in para:"),
    ("trailer-line pattern matches any line",
     '_TRAILER_LINE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:\\s")',
     '_TRAILER_LINE = re.compile(r"^.*$")'),
    ("stops stripping trailing whitespace",
     '    body = (message or "").rstrip()',
     '    body = message or ""'),
    ("last paragraph becomes the whole message",
     '    para = body.rsplit("\\n\\n", 1)[-1] if "\\n\\n" in body else body',
     "    para = body"),
]


def _run_guard() -> bool:
    """True when the guard is GREEN."""
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    original = SUBJECT.read_bytes()
    text = original.decode("utf-8")

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation. Fix that first; a "
              "harness cannot tell a mutation from a pre-existing failure.")
        return 2

    red = misses = probe_failures = 0
    try:
        for label, old, new in MUTATIONS:
            if old not in text:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: its anchor is not in the file, so "
                      f"nothing was mutated. The probe is stale, not the guard.")
                continue
            SUBJECT.write_text(text.replace(old, new, 1), encoding="utf-8")
            moved = SUBJECT.read_bytes() != original
            if not moved:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged after the edit.")
                continue
            green = _run_guard()
            if green:
                misses += 1
                print(f"  [MISS]  {label}: the guard stayed GREEN with the repair reverted.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)

    restored_ok = SUBJECT.read_bytes() == original
    print(f"\n  subject restored byte-for-byte: {restored_ok}")
    n = len(MUTATIONS)
    print(f"  {red} of {n} mutations turned the guard RED; "
          f"{misses} MISS; {probe_failures} probe failure(s)")
    if not restored_ok:
        print("  RESTORE FAILED — the subject is not what it was. Fix before committing.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe_failures == 0) else 1


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
