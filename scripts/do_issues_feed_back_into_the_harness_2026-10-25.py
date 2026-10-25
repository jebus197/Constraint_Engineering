#!/usr/bin/env python3
"""Do issues raised in a note actually re-enter the harness machinery?

HIS INSTRUCTION, recorded in chat: issues of this kind should be fed back into
the full machinery of the harness for resolution rather than handled ad hoc. On
2026-10-25 he asked whether that work can be recorded as completed. This script
answers by EXECUTION rather than by finding a ticket that claims it.

THE 3 PATHS an issue must be able to travel, and what each is checked by:
  1. TRACKED   -- the issue becomes a ticket with a stable id in `bench/ticket_store`.
                  Checked by constructing a ticket and reading its id back.
  2. DISPATCHABLE -- a ticket can be put to the model panel. Checked by confirming
                  the panel-request recorder accepts a ticket id and that a request
                  with no reply is reported as unreached, which is the failure the
                  2026-10-20 measurement found in 30 of 60 requests.
  3. GUARDED   -- a resolved issue becomes an EXECUTING test that goes red on
                  regression. Checked by running the guard and by MUTATING the
                  thing it guards to confirm it actually goes red. A guard that
                  passes both before and after a mutation guards nothing.

PATH 3 IS THE ONE THAT MATTERS and it is why this script exists. On 2026-10-25
`test_pre_verdict_sweep_shadow_2026-10-06.py` was found RED, having gone stale
when `REQUIRED_QUIET_RUN` rose from 3 to 7. A red guard means path 3 was BROKEN:
an issue could become a test that nobody could rely on.

USAGE
    python3 scripts/do_issues_feed_back_into_the_harness_2026-10-25.py
    python3 scripts/do_issues_feed_back_into_the_harness_2026-10-25.py --json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))


def path1_tracked() -> dict:
    """An issue becomes a ticket with a stable, content-derived id."""
    try:
        from ticket_store import TicketStore, tid_of
        a = tid_of("pf", "a worked example of a fed-back issue", "", "")
        b = tid_of("pf", "a worked example of a fed-back issue", "", "")
        c = tid_of("pf", "a DIFFERENT issue", "", "")
        st = TicketStore()
        return {"ok": a == b and a != c,
                "stable_id": a == b, "distinct_ids": a != c,
                "live_tickets": len(st.workable()) + len(st.deferred_tickets()),
                "how": "tid_of called twice on the same text and once on different text"}
    except Exception as e:                                   # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def path2_dispatchable() -> dict:
    """A ticket can be put to the panel, and an unanswered request is reported."""
    s = REPO / "scripts" / "panel_requests_are_tracked_2026-10-20.py"
    if not s.is_file():
        return {"ok": False, "error": f"missing {s.name}"}
    # NO --json ON THIS TRACKER. Its interface is `[--file]` and it prints text.
    # Guessing the flag cost a false FAIL on the first run of this script, which
    # is the same field-and-flag guessing that produced 4 other errors tonight.
    # Read the interface; do not assume it.
    r = subprocess.run([sys.executable, str(s)],
                       capture_output=True, text=True, timeout=600, cwd=REPO)
    if r.returncode != 0:
        return {"ok": False, "error": f"exit {r.returncode}: {r.stderr[-300:]}"}
    total = unreached = None
    for line in r.stdout.splitlines():
        if ":" not in line:
            continue
        label, _, val = line.partition(":")
        val = val.strip()
        if not val.isdigit():
            continue
        if "requesting a panel" in label:
            total = int(val)
        elif "reached by nothing" in label:
            unreached = int(val)
    if total is None or unreached is None:
        return {"ok": False,
                "error": f"could not parse the tracker's output: {r.stdout[:200]!r}"}
    return {"ok": total > 0 and unreached == 0,
            "requests": total, "unreached": unreached,
            "how": "the committed panel-request tracker, run for real, output parsed"}


def path3_guarded() -> dict:
    """A resolved issue is an EXECUTING guard that goes red on regression.

    Mutation-checked: `REQUIRED_QUIET_RUN` is the value whose change broke this
    path once already, so the guard is run, then the value is perturbed in a
    SUBPROCESS, and the guard must go red. Nothing in the repository is edited.
    """
    guard = "bench/tests/test_pre_verdict_sweep_shadow_2026-10-06.py"
    green = subprocess.run([sys.executable, "-m", "pytest", guard, "-q"],
                           capture_output=True, text=True, timeout=900, cwd=REPO)
    # Mutation: force the fixture's derived window to a value the gate rejects.
    # MUTATE WHAT THE GATE READS. Forcing the module constant alone leaves the
    # guard GREEN, because `RunnerConfig.gamma_alt_consecutive_zero_crit` froze
    # its default at class creation. That false negative on 2026-10-25 is what
    # exposed the half-derived fixture; the mutation now reaches the real input
    # by making the gate demand a longer quiet run than the fixture supplies.
    # PATCH THE MODULE THE TEST ACTUALLY IMPORTS. The guard does
    # `import bench.reference_runner_v3 as R`, so patching bare
    # `reference_runner_v3` creates a SECOND module object in sys.modules and the
    # mutation never reaches the test -- which is exactly why this check reported
    # a green guard twice on 2026-10-25. Same failure class as the 3 guards that
    # went blind to a wrapper on 2026-10-11.
    mut = (
        "import sys\n"
        "import bench.reference_runner_v3 as R\n"
        "_orig = R._check_gamma_alt_convergence\n"
        "def _patched(*a, **k):\n"
        "    if len(a) > 3 and hasattr(a[3], 'gamma_alt_consecutive_zero_crit'):\n"
        "        a[3].gamma_alt_consecutive_zero_crit = R.REQUIRED_QUIET_RUN + 5\n"
        "    return _orig(*a, **k)\n"
        "R._check_gamma_alt_convergence = _patched\n"
        "import pytest\n"
        f"sys.exit(pytest.main(['{guard}', '-q', '-x', '-p', 'no:cacheprovider']))\n")
    red = subprocess.run([sys.executable, "-c", mut],
                         capture_output=True, text=True, timeout=900, cwd=REPO)
    return {"ok": green.returncode == 0 and red.returncode != 0,
            "guard_green_as_committed": green.returncode == 0,
            "guard_red_under_mutation": red.returncode != 0,
            "mutation": "the gate made to demand a longer quiet run than the fixture supplies, patched on bench.reference_runner_v3",
            "how": "pytest run for real, then re-run against a mutated constant"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = {"path1_tracked": path1_tracked(),
           "path2_dispatchable": path2_dispatchable(),
           "path3_guarded": path3_guarded()}
    res["paths_verified"] = sum(1 for v in res.values() if isinstance(v, dict) and v.get("ok"))
    res["paths_total"] = 3
    res["complete"] = res["paths_verified"] == 3

    if a.json:
        print(json.dumps(res, indent=2))
        return 0 if res["complete"] else 1

    for k in ("path1_tracked", "path2_dispatchable", "path3_guarded"):
        v = res[k]
        print(f"  {'PASS' if v.get('ok') else 'FAIL'}  {k}")
        for kk, vv in v.items():
            if kk != "ok":
                print(f"          {kk}: {vv}")
    print(f"\n  {res['paths_verified']} of {res['paths_total']} paths verified; "
          f"complete = {res['complete']}")
    return 0 if res["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
