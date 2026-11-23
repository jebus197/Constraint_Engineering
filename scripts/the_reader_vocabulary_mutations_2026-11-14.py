#!/usr/bin/env python3
"""Does the reader-vocabulary guard fail when the 2026-11-14 repair is reverted?

7 reversions of the repair found while verifying B184, each of which must turn
`bench/tests/test_the_reader_vocabulary_cannot_drift_2026-11-14.py` RED.

★ THE STALE-FALLBACK MUTATION IS THE ONE WORTH HAVING. Reverting `frx` out of
the fallback tuple changes NOTHING observable on a normal run, because the
import succeeds and the literal is never reached. Only the guard's
import-failure path can see it. A harness that did not include this mutation
would leave the project's only check on that literal unverified.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED THE FILE, and the subject is
restored from bytes captured before the first one, never with `git checkout --`.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
GUARD = REPO / "bench" / "tests" / "test_the_reader_vocabulary_cannot_drift_2026-11-14.py"

MUTATIONS = [
    ("R1 narrow the suffix back, losing his first frx",
     r'    r"(?:[\s.!?]*$|\s*[(\[][^\n]*$)", re.I)',
     r'    r"[\s.!?]*$", re.I)'),
    ("R2 revert frx out of the FALLBACK tuple (invisible on a normal run)",
     '_HIS_KINDS = ("fr", "frx", "pf", "qs", "wr", "stm", "disc", "dis", "ds")',
     '_HIS_KINDS = ("fr", "pf", "qs", "wr", "stm", "disc", "dis", "ds")'),
    ("R3 re-spell the alternation in _MARKER_LINE instead of deriving it",
     r'    r"^\s*(" + _KIND_ALT + r")(?:\s*,\s*(?:" + _KIND_ALT + r"))*\s*$", re.I)',
     r'    r"^\s*(frx|fr|pf|qs|wr|stm|disc|dis|ds)(?:\s*,\s*(?:frx|fr|pf|qs|wr|stm|disc|dis|ds))*\s*$", re.I)'),
    # ★ R4 WAS WITHDRAWN AS A FALSE MISS, 2026-11-14, and is recorded rather
    # than deleted. It reverted the alternation to SHORTEST-first, expecting
    # `fr` to shadow `frx`. The guard stayed GREEN and the guard was RIGHT:
    # Python backtracks out of a failed suffix, which B184 had already measured
    # both ways and recorded as REFUTED. Longest-first makes the pattern correct
    # by CONSTRUCTION rather than correct by the engine's behaviour, which is
    # worth doing and is not a defect being fixed -- so there is nothing for a
    # mutation to catch, and reporting a MISS would blame the guard for the
    # absence of a bug. Replaced by a mutation of the thing that IS load-bearing
    # in that line: the derivation itself.
    ("R4 hardcode _KIND_ALT instead of deriving it from the kind set",
     '_KIND_ALT = "|".join(sorted(_HIS_KINDS, key=len, reverse=True))',
     '_KIND_ALT = "disc|stm|dis|fr|pf|qs|wr|ds"'),
    ("R5 drop the leading boundary so a word ENDING in a kind reads as a marker",
     '    r"(?:^|[\\s.,;:!?)\\]\\"\'’”])((?:" + _KIND_ALT + r")(?:\\s*,\\s*(?:" + _KIND_ALT + r"))*)"',
     '    r"((?:" + _KIND_ALT + r")(?:\\s*,\\s*(?:" + _KIND_ALT + r"))*)"'),

    ("R6 widen the suffix to ANY trailing text, admitting mid-sentence markers",
     r'    r"(?:[\s.!?]*$|\s*[(\[][^\n]*$)", re.I)',
     r'    r"(?:[\s.!?]*$|.*$)", re.I)'),
    ("R7 drop a kind from the alternation source",
     '_KIND_ALT = "|".join(sorted(_HIS_KINDS, key=len, reverse=True))',
     '_KIND_ALT = "|".join(sorted([k for k in _HIS_KINDS if k != "stm"], key=len, reverse=True))'),
]


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    original = SUBJECT.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
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
    ok = hashlib.sha256(SUBJECT.read_bytes()).hexdigest() == sha
    print(f"\n  subject restored, SHA-256 identical: {ok}")
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
