#!/usr/bin/env python3
"""Filtering B50's stale constant repairs 1 of the 6, not 2, and breaks a 7th.

WHY THIS EXISTS. Entry B50 reports 6 permanently failing assertions in
`bench/tests/test_immune_memory_evaluation.py` and asks him to rule between 3
options. It partitions the 6 as *"2 of them are a stale CONSTANT and are
mechanically fixable"* against *"the other 4 are EMPIRICAL CLAIMS about data the
reset destroyed, and no filter repairs them"*, and names the repair: filtering
`_RECORDING_RUNS` to runs that wrote after the newest reset. All 3 runs in that
constant are pre-reset, so the filter yields the EMPTY list.

THAT PARTITION IS WRONG, AND A COUNT CANNOT SEE IT. Before and after the filter
the totals are IDENTICAL -- 6 failed, 28 passed, both times -- so any instrument
comparing counts reports no change. Comparing the SETS shows a trade:

  REPAIRED : TestWhatTheMemoryHolds::test_disk_memory_reproduces_from_its_recorded_run_reports
  BROKEN   : TestWhatTheMemoryHolds::test_the_evidence_base_is_thin_and_here_is_how_thin
  UNCHANGED: the other 5 of the 6

So 1 of the 6 is mechanically repairable, not 2, and the repair is not free: it
breaks a test that was passing. This is `feedback_pin_a_set_not_a_count` in its
purest form, since the count is the same integer on both sides.

WHY THE BROKEN ONE BREAKS, AND WHY ITS MESSAGE WOULD MISLEAD. It asserts that
some flaw class rests on a single observation. With no pre-reset runs in the
derivable set there is no such class at all, and the assertion then reports
*"the memory has grown past the state this evaluation describes"* -- which is
false in this case, because the memory did not grow; the constant was emptied.
A repair that produces a misleading diagnosis is worse than the failure it
replaces.

HOW IT MEASURES WITHOUT TOUCHING THE TREE. The constant is patched AT RUNTIME by
a pytest plugin written to a temporary directory, never by editing the test file,
so this can run safely while a board is running and cannot leave the repository
modified if it is interrupted.

WHAT THIS DOES NOT DECIDE. His 3 options stand and the ruling is his. This
changes only the price list: option 1's mechanical half repairs 1 assertion and
costs another, and option 2 therefore covers 5 assertions rather than 4.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTFILE = REPO / "bench" / "tests" / "test_immune_memory_evaluation.py"

_PLUGIN = '''
"""Runtime patch: empty `_RECORDING_RUNS` after collection, editing no file."""
import sys


def pytest_collection_finish(session):
    for name, mod in list(sys.modules.items()):
        if name.endswith("test_immune_memory_evaluation") and hasattr(
                mod, "_RECORDING_RUNS"):
            mod._RECORDING_RUNS = []
'''


def _run(extra_args: list[str], pythonpath: str | None = None) -> set[str]:
    """Run the test file and return the set of failing node ids (short form)."""
    env = dict(os.environ)
    if pythonpath:
        env["PYTHONPATH"] = pythonpath + os.pathsep + env.get("PYTHONPATH", "")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTFILE), "--tb=no", "-q",
         *extra_args],
        capture_output=True, text=True, cwd=str(REPO), env=env)
    failing = set()
    for line in r.stdout.split("\n"):
        if line.startswith("FAILED "):
            node = line.split(" ", 1)[1].split(" ")[0]
            failing.add(node.split("::", 1)[1] if "::" in node else node)
    return failing


def measure() -> dict:
    assert TESTFILE.is_file(), f"test file absent: {TESTFILE}"
    before = _run([])
    with tempfile.TemporaryDirectory() as td:
        plug = Path(td) / "_b50_filter_plugin.py"
        plug.write_text(_PLUGIN)
        after = _run(["-p", "_b50_filter_plugin"], pythonpath=td)
    return {"before": sorted(before), "after": sorted(after),
            "repaired": sorted(before - after),
            "broken": sorted(after - before),
            "unchanged": sorted(before & after)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    m = measure()

    if args.json:
        print(json.dumps(m, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"FAILING BEFORE the filter: {len(m['before'])}")
    for n in m["before"]:
        print(f"    {n}")
    print(f"FAILING AFTER  the filter: {len(m['after'])}")
    for n in m["after"]:
        print(f"    {n}")
    print()
    print(f"THE COUNT IS THE SAME INTEGER ON BOTH SIDES: "
          f"{len(m['before'])} -> {len(m['after'])}")
    print("    So a count-based comparison reports NO CHANGE and is wrong.")
    print()
    print(f"REPAIRED by the filter: {len(m['repaired'])}")
    for n in m["repaired"]:
        print(f"    {n}")
    print(f"NEWLY BROKEN by the filter: {len(m['broken'])}")
    for n in m["broken"]:
        print(f"    {n}")
    print(f"UNCHANGED: {len(m['unchanged'])}")
    print()
    print(f"SO B50's PARTITION OF 2 MECHANICAL AND 4 EMPIRICAL IS "
          f"{len(m['repaired'])} AND {len(m['unchanged'])},")
    print(f"    and the mechanical repair costs {len(m['broken'])} "
          f"previously-passing assertion(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
