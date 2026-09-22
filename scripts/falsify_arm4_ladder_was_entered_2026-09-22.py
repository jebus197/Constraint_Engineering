#!/usr/bin/env python3
"""FALSIFIER: two same-day claims about arm 4's deferred criticals, against the archive.

CLAIM A (bench/tests/test_hil_queue_says_which_kind_2026-09-22.py, module
docstring and test 4): "the ladder was never entered" on arm 4's deferred
criticals, and "a deferred item has `rungs_tried == 0` by construction".

CLAIM B (scripts/arm4_untoolable_anatomy_2026-09-22.py, section 2): settling
whether the routing-generated source would have run "would mean EXECUTING the
source, which this archive forbids: it is truncated at 600".

BOTH ARE REFUTED BY THE SAME REGISTRY FIELD. `_apply_routing` appends a
routing_history step AFTER `route()` returns (reference_runner_v3.py:5992)
and sets `routing_deferred` on the equipment-failure branch AFTER that
(:6158) -- so a deferred entry records what the ladder actually did. In the
arm-4 archive every deferred entry carries rungs_tried in {1,2} with
rungs_available=5 and error_routed=True (a model was genuinely reached): the
ladder WAS entered and stopped at the max_rungs=2 constant
(bench/routing.py:139) with 3 rungs untried. And each step carries `verdict`
-- the runner's own re-execution result for the UNTRUNCATED source of the
last rung (ERROR for all 6 UNTOOLABLE entries, INTEGRITY_VIOLATION for
C0008): the archive does not forbid execution, it RECORDS one.

`rungs_tried == 0` deferral exists only on the empty-ladder branch
(reference_runner_v3.py:6039), which arm 4 never took.

Prints FALSIFIED (exit 1) iff the archive contradicts the claims -- i.e. iff
any deferred entry carries rungs_tried > 0 or an executed step verdict.
Exits cleanly only if every deferred entry really shows rungs_tried == 0 and
no executed verdict, which is what the claims assert.

Run:  python3 scripts/falsify_arm4_ladder_was_entered_2026-09-22.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARM4 = (REPO / "bench" / "logs" / "commissioning_arm4_prose_20260922T053349Z"
        / "commissioning_arm4_prose_report.json")


def main() -> int:
    if not ARM4.is_file():
        print(f"archive absent: {ARM4}", file=sys.stderr)
        return 2
    ents = json.loads(ARM4.read_text(encoding="utf-8"))["registry"]["entries"]
    deferred = {c: e for c, e in ents.items() if e.get("routing_deferred")}
    assert deferred, "no deferred entries; this falsifier is aimed at nothing"

    entered, executed = [], []
    for cid, e in sorted(deferred.items()):
        for s in (e.get("routing_history") or []):
            if not isinstance(s, dict):
                continue
            tried = s.get("rungs_tried") or 0
            if tried > 0:
                entered.append((cid, tried, s.get("rungs_available")))
            v = (s.get("verdict") or "").strip()
            if v and v != "UNTOOLABLE" and (s.get("last_falsifier_code") or "").strip():
                executed.append((cid, v))

    print(f"  deferred entries          : {len(deferred)}")
    print(f"  ...with rungs_tried > 0   : {len(entered)}  {entered}")
    print(f"  ...with an EXECUTED step verdict on recorded source: "
          f"{len(executed)}  {executed}")

    if entered or executed:
        print("FALSIFIED:")
        if entered:
            print("  * 'the ladder was never entered / deferred implies "
                  "rungs_tried==0 by construction' is contradicted by "
                  f"{len(entered)} of {len(deferred)} deferred entries.")
        if executed:
            print("  * 'the archive forbids executing the routed source' is "
                  "contradicted: the runner executed the untruncated source at "
                  "run time and recorded the verdict on the routing step.")
        return 1
    print("OK: every deferred entry shows rungs_tried == 0 and no executed "
          "verdict; the claims stand.")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole falsifier. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
