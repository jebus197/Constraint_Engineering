#!/usr/bin/env python3
"""The fourth ladder outcome: a transport-dead serve writes a ruling-shaped record.

THE QUESTION THIS ANSWERS (joint round J1, 2026-10-12). The composition repair in
`_routing_ladder_never_served` distinguishes three serve outcomes by the record's
`resolved` flag and verdict string: SERVED-AND-NO-READING (verdict in
`NO_READING_ROUTING_VERDICTS`, door releases), SERVED-AND-RULED (any other
verdict, door blocks), and RESOLVED (tool verdict clears it). Is there a fourth?

THERE IS, AND IT IS THE OPPOSITE DIRECTION FROM THE ONE ASKED. The brief asked
for a record shape where the verdict is empty but an instrument did read the
finding (door too wide). Measured here, the live defect is the inverse: a
record whose verdict is a RULING STRING written when NO instrument ever read
the finding (door too narrow, permanently).

PART 1 — THE LIVE LADDER NEVER EMITS THE NO-READING SENTINELS. Executed, not
read off the source: every reachable terminal of `bench.routing.route` /
`resolve_via_routing` is enumerated by stubbing `resolve_fn` (raises, returns
empty, returns code) and `reverify_fn` (every verdict the runner's decider can
return, per the return sites of `bench/falsifier_verify.py`). The reachable
set intersected with `NO_READING_ROUTING_VERDICTS` is EMPTY. So the door's
release case is reachable only through an EMPTY routing history (never served)
or a mocked outcome — never from a verdict the live ladder wrote.

PART 2 — THE TRANSPORT-DEAD SERVE, END TO END. When every rung's dispatch
fails (the 402-cascade class), `resolve_via_routing` returns verdict "ERROR"
with `resolved=False` and `rungs_tried` counting rungs NO model answered.
`_apply_routing` appends that record BEFORE the transport-dead guard runs, so
a C0066-shaped entry served once on a dead transport:
  * carries a routing_history record whose verdict, "ERROR", the door treats
    as a ruling — the door CLOSES although nothing ever read the finding;
  * is never served again, because the `_never_served` admission requires an
    EMPTY routing_history, which the failed serve just consumed;
  * and blocks A4 for the life of the run — the exact composed defect the
    2026-10-12 repair was built to remove, one failure class over.
The guard's own comment says a transport-dead round "must not burn the attempt
nor mint a false 'ladder exhausted' record"; for the never-served class it
burns the attempt AND mints the record.

Usage: python3 scripts/transport_dead_serve_blocks_for_ever_2026-10-12.py
Exit 0 always; it prints the measurement. Run on the unfixed tree it prints
BLOCKED FOR EVER; after the repair it prints RELEASED AND RE-SERVED.
"""
import os
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402

answer_help(__doc__)

import bench.reference_runner_v3 as rr  # noqa: E402
import bench.routing as routing  # noqa: E402

EXP = {"models": [{"label": "X-SIM"}, {"label": "Y-SIM"}]}


def part1_reachable_verdicts() -> set:
    """Every verdict `route` can return, by execution over stubbed dependencies."""
    # The verdict strings bench/falsifier_verify.py's reverify path can return,
    # read from its return sites and executed here as stub deciders.
    REVERIFY_VOCAB = ["CONFIRMED", "REFUTED", "ERROR", "UNTOOLABLE",
                      "INTEGRITY_VIOLATION", "NON_DISCRIMINATING"]
    finding = {"id": "F1", "source_model": "X-SIM", "description": "d"}
    reached = set()

    def sim(fn, reverify, rungs=("Y-SIM",), self_rung=None):
        r = routing.resolve_via_routing(finding, list(rungs), fn, reverify,
                                        max_rungs=0, self_rung=self_rung)
        reached.add(r.verdict)

    # A dispatch exception never reaches resolve_via_routing: the runner's
    # resolve_fn closure in _apply_routing catches it and returns "" (verified
    # by execution -- passing a raising stub here propagates, which is the
    # wrapper's job to prevent). So "transport dead" and "model produced
    # nothing" are the SAME shape at this layer: empty code.
    sim(lambda m, f: "", lambda c: "CONFIRMED")             # dead transport / nothing
    for v in REVERIFY_VOCAB:                                # decider rules v
        sim(lambda m, f: "assert False", lambda c, _v=v: _v)
    sim(lambda m, f: "x", lambda c: "CONFIRMED", rungs=())  # empty ladder
    sim(lambda m, f: "x", lambda c: "REFUTED", rungs=(), self_rung="X-SIM")
    # The dedup path, through route() itself.
    dup = routing.route(finding, ["X-SIM", "Y-SIM"],
                        [{"id": "F0", "description": "d"}],
                        lambda m, f: "", lambda c: "ERROR",
                        lambda a, b: 1.0)
    reached.add(dup.verdict)
    return reached


def entry(cid="C9001"):
    return {
        "canonical_id": cid, "status": "UNCONFIRMED", "severity": 0.45,
        "description": "never served", "source_model": "X-SIM",
        "falsifier_code": "", "falsifier_verdict": "", "verdicts": [],
        "escalated": False, "verified": False,
        "open_since_round": 5, "last_status_change_round": 5,
    }


class DeadTransportResult:
    """The exact RoutingResult shape Part 1 measured for an all-rungs-dead serve."""

    def __init__(self):
        self.verdict = "ERROR"      # measured: resolve_fn raising on every rung
        self.resolved = False
        self.falsifier_code = ""
        self.model_used = "Y-SIM"   # resolve_via_routing sets last_model BEFORE dispatch
        self.duplicate_of = None
        self.rungs_tried = 1
        self.ladder_was_empty = False


def part2_end_to_end() -> None:
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = entry()
    repo = str(Path(__file__).resolve().parents[1])
    cfg = rr.RunnerConfig(routing_enabled=True)
    with mock.patch.object(routing, "route", return_value=DeadTransportResult()):
        rr._apply_routing(reg, 7, EXP, cfg=cfg, repo_root=repo)   # the first serve
        n_after_first = len(reg.entries["C9001"].get("routing_history") or [])
        rr._apply_routing(reg, 8, EXP, cfg=cfg, repo_root=repo)   # is it retried?
        n_after_second = len(reg.entries["C9001"].get("routing_history") or [])
    e = reg.entries["C9001"]
    rec = (e.get("routing_history") or [{}])[0]
    a4 = reg.unverified_critical_count(9)
    named = reg.ladder_unserved_findings(9)
    print("PART 2 — a C0066-shaped entry served once on a dead transport:")
    print(f"  routing_history[0].verdict = {rec.get('verdict')!r}, "
          f"resolved = {rec.get('resolved')!r}")
    print(f"  records after round-7 serve: {n_after_first}; "
          f"after round-8 pass: {n_after_second} "
          f"({'RE-SERVED' if n_after_second > n_after_first else 'NEVER RE-SERVED'})")
    print(f"  A4 at round 9 = {a4}; ladder_unserved_findings = {named}")
    if a4 and not named and n_after_second == n_after_first:
        print("  -> BLOCKED FOR EVER: the door reads the dead-transport record "
              "as a ruling, the serve's one admission is consumed, and neither "
              "mechanism can release it. The composed defect is back.")
    else:
        print("  -> RELEASED AND RE-SERVED: the record is reclassified as "
              "no-reading, the door names it, and the ladder may try again.")


def main() -> int:
    reached = part1_reachable_verdicts()
    overlap = reached & rr.NO_READING_ROUTING_VERDICTS
    print("PART 1 — verdicts the live ladder can return, by execution:")
    print(f"  reachable: {sorted(reached)}")
    print(f"  NO_READING_ROUTING_VERDICTS: {sorted(rr.NO_READING_ROUTING_VERDICTS)}")
    print(f"  intersection: {sorted(overlap)} "
          f"({'EMPTY' if not overlap else 'NON-EMPTY'})")
    print()
    part2_end_to_end()
    return 0


if __name__ == "__main__":
    sys.exit(main())
