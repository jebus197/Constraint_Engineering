#!/usr/bin/env python3
"""Is any LIVE config still on the old required quiet run? -- entry C12.

HIS RULING, 2026-10-08: *"Verdict. Fix it and check your fix with the free
panel."* He was answering the panel finding that even at full roster there is a
0.1159 chance of 3 consecutive quiet rounds arising without the problem space
being exhausted -- a premature convergence -- and that *"The only levers
identified are a longer required quiet run, or more seats."*

THE FIX WAS APPLIED, AND NOT UNDER THIS ENTRY. `REQUIRED_QUIET_RUN` is 7 and
`RunnerConfig.gamma_alt_consecutive_zero_crit` defaults to it, changed in commit
f50d6ead on 2026-10-17 at 10:26 under entry C13. Entry C12 was written at 02:03
the same morning, 8 hours earlier, and still records the value as 3 -- so the
entry is stale rather than the code unfixed. 7 is exactly the value the committed
measurement recommends on the honest reading: `bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`
reports the premature-window rate falling 0.126374 at K=3 through 0.0784, 0.0458
and 0.0263 to 0.0000 at K=7, with `smallest_k_meeting_the_target_on_the_point_estimate`
of 5 and `smallest_k_whose_upper_confidence_bound_meets_it` of 7, and its own note
that the upper bound is the one to spend a decision on because the denominator
shrinks as the window lengthens.

WHY THIS SCRIPT EXISTS ANYWAY. A default is only load-bearing for a run that does
not override it, and 23 config files still set 3. This separates the ones that are
RECORDS OF COMPLETED EXPERIMENTS -- which must not be rewritten, on his ruling
that he is not suggesting rewriting history -- from any that are FORWARD-LOOKING
and would carry the old rate into a future run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OLD_K = 3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old", type=int, default=OLD_K)
    args = ap.parse_args()

    logs = REPO / "bench" / "logs"
    run_dirs = [d.name for d in logs.iterdir() if d.is_dir()] if logs.is_dir() else []

    by_value: dict[int, list[pathlib.Path]] = {}
    for f in sorted((REPO / "bench").rglob("*configs*/*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:                                          # noqa: BLE001
            continue
        if isinstance(d, dict) and "gamma_alt_consecutive_zero_crit" in d:
            by_value.setdefault(d["gamma_alt_consecutive_zero_crit"], []).append(f)

    print("required quiet run, as SET IN CONFIG FILES")
    for k in sorted(by_value):
        print(f"  K={k}: {len(by_value[k])} config(s)")
    print()

    old = by_value.get(args.old, [])
    # A config inside a panel sandbox harvest is a COPY a seat made, not a live
    # config: the live file of the same name is elsewhere in the tree.
    harvested = [f for f in old if "sandbox_harvest" in str(f)]
    live_old = [f for f in old if "sandbox_harvest" not in str(f)]

    spent, pending = [], []
    for f in live_old:
        m = re.match(r"(\d+)", f.stem)
        n = m.group(1) if m else ""
        hits = [r for r in run_dirs if n and r.startswith(f"exp{n}_")]
        (spent if hits else pending).append((f, hits[:1]))

    print(f"of the {len(old)} config(s) still at K={args.old}:")
    print(f"  {len(harvested)} are COPIES inside a panel sandbox harvest, not live configs")
    print(f"  {len(spent)} are configs of experiments ALREADY RUN -- records, and his "
          f"ruling is that history is not rewritten")
    print(f"  {len(pending)} are LIVE and FORWARD-LOOKING")
    print()
    if pending:
        print(f"★ {len(pending)} LIVE CONFIG(S) WOULD CARRY THE OLD RATE INTO A FUTURE RUN:")
        for f, _ in pending:
            print(f"    {f.relative_to(REPO)}")
        print("  Each would run with a premature-convergence rate of 0.126374 rather")
        print("  than 0.0000, so a clean convergence from one of them would be worth")
        print("  less than a clean convergence from a K=7 config.")
        return 1
    print("NO LIVE FORWARD-LOOKING CONFIG IS STILL ON THE OLD VALUE.")
    print("  Every config at the old value is either a record of a completed")
    print("  experiment or a sandbox copy. The fix is complete in the live tree,")
    print("  and the half of his ruling that remains is the FREE PANEL CHECK of")
    print("  whether 7 is the right lever, or whether more seats is the better one.")
    for f, h in spent[:6]:
        print(f"    record: {f.name:44} produced {h[0] if h else ''}")
    if len(spent) > 6:
        print(f"    ... and {len(spent) - 6} further records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
