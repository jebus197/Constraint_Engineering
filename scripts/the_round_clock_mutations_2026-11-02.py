#!/usr/bin/env python3
"""Reverse each property of the per-round wall clock and confirm its guard goes RED.

The 1 that matters most is the ORDERING: the first draft stamped the time after
`json.dumps` had read the list, so every checkpoint would have persisted one
round short. A guard that cannot catch that is not worth having.
"""
from __future__ import annotations
import pathlib, subprocess, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
MOD = REPO / "bench" / "reference_runner_v3.py"
TEST = (REPO / "bench" / "tests" /
        "test_a_round_carries_its_own_time_2026-11-02.py")

MUTATIONS = [
    ("nothing appends, so the series stays empty",
     '''        if len(round_wall_clock) <= round_idx:
            round_wall_clock.append(
                datetime.now(timezone.utc).isoformat(timespec="seconds"))''',
     '''        if False:
            round_wall_clock.append(
                datetime.now(timezone.utc).isoformat(timespec="seconds"))'''),
    ("the series is never persisted, so it dies with the process",
     '''            "round_wall_clock": round_wall_clock,\n''', ''),
    ("the series is not restored on resume, so a restart loses its clock",
     '''            round_wall_clock = ckpt_data.get("round_wall_clock", [])\n''', ''),
    ("the stamp loses its explicit UTC offset",
     '''datetime.now(timezone.utc).isoformat(timespec="seconds")''',
     '''datetime.now().isoformat(timespec="seconds")'''),
    ("the series is cleared on a churn reset, destroying the alignment",
     '''                    gate_history.clear()''',
     '''                    gate_history.clear()
                    round_wall_clock.clear()'''),
    ("a sibling series is dropped, so the addition is no longer additive",
     '''            "open_ch_history": open_ch_history,\n''', ''),
]


def run_suite() -> bool:
    p = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                        "--no-header", "-x"], capture_output=True, text=True,
                       timeout=300, cwd=str(REPO))
    return p.returncode == 0


def main() -> int:
    answer_help(__doc__, __file__)
    original = MOD.read_text()
    print("=" * 78)
    print("PER-ROUND WALL CLOCK MUTATION TEST")
    print("=" * 78)
    if not run_suite():
        print("  THE SUITE IS ALREADY RED. Nothing can be concluded. Stopping.")
        return 2
    print("  baseline: GREEN\n")
    red = applied = 0
    try:
        for label, old, new in MUTATIONS:
            if original.count(old) < 1:
                print(f"  [SKIP  ] {label}")
                print(f"           anchor absent -- NOT APPLIED, nothing tested")
                continue
            applied += 1
            MOD.write_text(original.replace(old, new, 1))
            if run_suite():
                print(f"  [GREEN ] {label}\n           *** NOT GUARDED. ***")
            else:
                red += 1
                print(f"  [RED   ] {label}")
            MOD.write_text(original)
    finally:
        MOD.write_text(original)
    print(f"\n  {red} of {applied} applied mutation(s) turned the suite RED")
    ok = MOD.read_text() == original
    print(f"  runner restored to its original text: {ok}")
    return 0 if (red == applied and applied and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
