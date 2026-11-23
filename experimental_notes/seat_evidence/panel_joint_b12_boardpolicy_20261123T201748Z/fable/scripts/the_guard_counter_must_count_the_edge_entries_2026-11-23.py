# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_joint_b12_boardpolicy_20261123T201748Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 93b0414060e4d2c20ea5872a43f123b1628b98f5ca6dd41d44aca8cac81eef72
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The board's guard counter must count the assignment's first and last entries.

DESTINATION `scripts/`. Written 2026-11-23, panel round `panel_b12_20261123T170728Z`.

WHY. `board_guard_count` in `why_is_the_board_getting_slower_2026-11-23.py`
counted full-line regex matches over the whole hook. The first entry of the
`GUARDS="..."` assignment carries the `GUARDS="` prefix and the last carries
the closing quote, so the counter missed EXACTLY 2 on every call: the brief
of this round printed 329, the producer printed 330, the hook's own runtime
count recorded 331, and the true entry count at dispatch was 332. Three
circulating values for one quantity, all from counters, none wrong about
CONSTANCY -- but a systematic -2 on a figure the founder reads.

HOW. A synthetic hook text with a KNOWN entry count whose first and last
entries sit against the quotes -- the exact defect shape, supplied as input
data rather than as a retyped copy of the function under test, which the
falsifier-integrity standard forbids. The real `board_guard_count` is
imported from the real producer and must return the known count, on the
synthetic text and (>= smoke level) on the real hook.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

def _repo_root() -> pathlib.Path:
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root")


REPO = _repo_root()

SYNTH = '''# a hook-shaped fixture
GUARDS="bench/tests/test_first_guard_2026-01-01.py
bench/tests/test_middle_guard_2026-01-02.py
bench/tests/test_last_guard_2026-01-03.py"
echo done
'''


def main() -> int:
    spec = importlib.util.spec_from_file_location(
        "slower_producer_under_test",
        REPO / "scripts" / "why_is_the_board_getting_slower_2026-11-23.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["slower_producer_under_test"] = mod
    spec.loader.exec_module(mod)

    got = mod.board_guard_count(SYNTH)
    if got != 3:
        print(f"FALSIFIED: 3 entries in the fixture, counter returned {got} "
              "-- the quote-adjacent first/last entries are being dropped")
        return 1
    real = mod.board_guard_count()
    if real < 300:
        print(f"FALSIFIED: the real hook counted {real}; the extractor broke")
        return 1
    print(f"OK: synthetic 3 of 3 counted; real hook counts {real}.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
