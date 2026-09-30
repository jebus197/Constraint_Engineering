#!/usr/bin/env python3
"""FALSIFIER: arm 4's 6 UNTOOLABLE verdicts are STALE. The ladder ran and ERRORed.

THE CLAIM UNDER TEST is the one both the founder's question and CC1's reading
presuppose: that `UNTOOLABLE` on arm 4 is a statement about the TARGET -- either
"there was nothing here to compute" (the founder's reading) or "the machinery
gave up while it still held source it had produced" (CC1's reading). Both are
false in the same way. `UNTOOLABLE` on those 6 entries is not a statement about
the target at all. It is a PRE-ROUTING label that the routing ladder's own tool
verdict overwrote in `routing_history` and never wrote back to the entry.

WHAT THIS DEMONSTRATES, in four parts, each against the REAL module:

  A. MECHANISM. `bench.routing.resolve_via_routing` returns
     (verdict="ERROR", falsifier_code=<non-empty>) ONLY when the runner's own
     decider `reverify_fn` was CALLED on that code and returned ERROR. The other
     road to "ERROR" -- a rung that produced no code -- necessarily carries an
     EMPTY `falsifier_code`, because `last_code` is assigned before the emptiness
     check (bench/routing.py:161-166). So the archived signature
     (verdict ERROR, code non-empty) is a RECORD OF AN EXECUTION, not of a
     silence. This matters because `ge` refuted re-execution as a route to the
     answer: the 600-char archive cannot be run. It does not need to be. The
     runner already ran the untruncated body and recorded what it decided.

  B. ARCHIVE. Every entry in the arm 4 report carrying falsifier_verdict
     "UNTOOLABLE" carries routing_history verdict "ERROR" with a non-empty body,
     while its stored `falsifier_code` is empty. The entry's field and the
     ladder's field contradict each other, and the ladder's is the tool verdict.

  C. CONSEQUENCE, and this is what puts the finding above threshold.
     `_rejection_lines` (bench/reference_runner_v3.py:13145) branches on exactly
     this field to build the corrective instruction shipped to every seat in the
     next round's registry digest (rendered at :2749 and :2789). On ERROR it says
     "your test did not run to a verdict ... Re-write it so it runs". On
     UNTOOLABLE it says "nothing runnable was attached". For these 6 the panel is
     told to WRITE a falsifier that was already written and already crashed. The
     stale label does not merely misreport; it ships a wrong instruction.

  D. THE LADDER'S STOP IS CONSTANT-GOVERNED, NOT GAMMA-GOVERNED. `max_rungs`
     defaults to 2 (bench/routing.py:139,183); the runner's only call site passes
     no override; `rungs_available` is `len(models)` = 5. "2/5" is the constant
     against the roster. `_estimate_gamma` returns 0.0 for any run of fewer than
     `min_rounds=3` rounds, and arm 4 ran 1 -- its gamma_history is [0.0]. Gamma
     could not have governed this stop even in principle.

FAILS IFF THE DEFECT IS PRESENT: raises AssertionError / prints FALSIFIED when
the archive's UNTOOLABLE entries are stale relabels of an executed ERROR. Exits
cleanly if the labels agree with the ladder.

Run:  python3 scripts/falsifier_untoolable_is_stale_error_2026-09-22.py


WHAT THIS STILL REPORTS AFTER THE FIX, ADDED 2026-09-22 (CC1), BECAUSE A
FALSIFIER THAT FIRES FOREVER WITH NO EXPLANATION STOPS BEING READ.

Parts A and D test the LIVE module and PASS once `reconcile_routing_verdict` is
wired. Parts B and C read `commissioning_arm4_prose_20260922T053349Z`, which is
an ARCHIVED RUN. Its report is a record of what happened on 2026-09-22, and the
fix cannot reach backwards into it: those 6 entries were mislabelled at the time
and will read UNTOOLABLE for ever. So B and C are expected to keep firing, and
their firing is a statement about that archive, NOT evidence that the defect is
live in the code.

The guard that WOULD go red on a regression is
`bench/tests/test_routing_verdict_reconciliation.py`, which exercises the
reconciler directly. Trust that one for the code; read this one for the history.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

REPORT = (REPO / "bench" / "logs" / "commissioning_arm4_prose_20260922T053349Z"
          / "commissioning_arm4_prose_report.json")

failures: list[str] = []


def main() -> int:
    from bench.routing import resolve_via_routing, route
    from bench.reference_runner_v3 import (
        _rejection_lines, _estimate_gamma, EQUIPMENT_FAILURE_VERDICTS,
    )

    print("=" * 72)
    print("A. MECHANISM - what (ERROR, non-empty code) can and cannot mean")
    print("=" * 72)

    calls: list[str] = []

    def reverify_error(code: str) -> str:
        calls.append(code)
        return "ERROR"

    body = "import bench.routing\nassert False, 'boom'\n"
    r_ran = resolve_via_routing(
        {"id": "X1"}, ["Codex", "CC2"],
        resolve_fn=lambda m, f: body,
        reverify_fn=reverify_error,
        # max_rungs left at its default ON PURPOSE -- part D reads that default.
    )
    print(f"  last rung produced code -> verdict={r_ran.verdict!r} "
          f"code_len={len(r_ran.falsifier_code)} resolved={r_ran.resolved} "
          f"rungs_tried={r_ran.rungs_tried}  reverify_calls={len(calls)}")
    assert r_ran.verdict == "ERROR" and r_ran.falsifier_code, (
        "setup: expected the executed-and-crashed signature")
    assert len(calls) == 2, (
        "setup: reverify must have been CALLED for this signature to arise")

    # The ONLY other road to "ERROR" inside resolve_via_routing: a rung that
    # produced nothing. It cannot wear a non-empty falsifier_code.
    calls.clear()
    r_silent = resolve_via_routing(
        {"id": "X2"}, ["Codex", "CC2"],
        resolve_fn=lambda m, f: "",
        reverify_fn=reverify_error,
    )
    print(f"  last rung produced NOTHING -> verdict={r_silent.verdict!r} "
          f"code_len={len(r_silent.falsifier_code)}  reverify_calls={len(calls)}")
    assert r_silent.verdict == "ERROR" and r_silent.falsifier_code == "" and not calls, (
        "setup: the no-code road to ERROR must carry an empty body")
    print("  => (verdict ERROR) AND (code non-empty) IMPLIES reverify_falsifier")
    print("     EXECUTED the untruncated body and returned ERROR. Derived from")
    print("     the real module, not asserted.")

    print()
    print("=" * 72)
    print("B. ARCHIVE - the entry field contradicts the ladder's tool verdict")
    print("=" * 72)
    if not REPORT.is_file():
        print(f"  no arm 4 report at {REPORT}", file=sys.stderr)
        return 2
    ents = json.loads(REPORT.read_text())["registry"]["entries"]

    stale: list[str] = []
    for cid, e in sorted(ents.items()):
        if (e.get("falsifier_verdict") or "").strip().upper() != "UNTOOLABLE":
            continue
        rh = [s for s in (e.get("routing_history") or []) if isinstance(s, dict)]
        if not rh:
            continue
        last = rh[-1]
        lv = (last.get("verdict") or "").strip().upper()
        code_len = len(last.get("last_falsifier_code") or "")
        stored = len(e.get("falsifier_code") or "")
        print(f"  {cid}: entry says UNTOOLABLE | ladder says {lv:<10} "
              f"ladder_code={code_len:3}ch stored_code={stored}ch "
              f"rungs={last.get('rungs_tried')}/{last.get('rungs_available')}")
        if lv and lv != "UNTOOLABLE" and code_len > 0:
            stale.append(cid)
    if stale:
        failures.append(
            f"{len(stale)} entries labelled UNTOOLABLE whose ladder EXECUTED a "
            f"falsifier and returned a different verdict: {', '.join(stale)}")

    print()
    print("=" * 72)
    print("C. CONSEQUENCE - the wrong instruction ships to the next round")
    print("=" * 72)
    print(f"  _rejection_lines defined at reference_runner_v3.py:"
          f"{inspect.getsourcelines(_rejection_lines)[1]}")
    WRONG = "nothing runnable was attached"
    RIGHT = "did not run to a verdict"
    misinstructed: list[str] = []
    for cid in stale:
        lines = _rejection_lines(ents[cid])
        said_wrong = any(WRONG in ln for ln in lines)
        said_right = any(RIGHT in ln for ln in lines)
        print(f"  {cid}: says-'{WRONG}'={said_wrong}  says-'{RIGHT}'={said_right}")
        if said_wrong and not said_right:
            misinstructed.append(cid)
    if misinstructed:
        failures.append(
            f"{len(misinstructed)} entries are told to ATTACH a falsifier that "
            f"was written and crashed: {', '.join(misinstructed)}")
    print("  (these lines render into the registry digest at :2749 and :2789,")
    print("   i.e. into round K+1's prompt for every seat)")

    print()
    print("=" * 72)
    print("D. THE STOP IS CONSTANT-GOVERNED - gamma is not in this circuit")
    print("=" * 72)
    d_rvr = inspect.signature(resolve_via_routing).parameters["max_rungs"].default
    d_route = inspect.signature(route).parameters["max_rungs"].default
    print(f"  resolve_via_routing max_rungs default = {d_rvr}")
    print(f"  route               max_rungs default = {d_route}")
    assert d_rvr == 2 and d_route == 2

    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    i = src.find("result = route(")
    call = src[i:src.find(")", i) + 1]
    print(f"  runner call site: {' '.join(call.split())}")
    overrides = "max_rungs" in call
    print(f"  call site overrides max_rungs? {overrides}")
    assert not overrides, "call site DOES override; part D's premise is wrong"

    g1 = _estimate_gamma([4])
    print(f"  _estimate_gamma([4]) (arm 4 ran 1 round) = {g1}  "
          f"(min_rounds=3 -> structurally 0.0)")
    assert g1 == 0.0
    print("  => the ladder stopped at 2 of 5 because 2 is a hardcoded default,")
    print("     not because returns were diminishing. Gamma is a ROUND-level")
    print("     novelty-decay measure and touches no part of this ladder.")
    print(f"  (for reference, EQUIPMENT_FAILURE_VERDICTS = "
          f"{sorted(EQUIPMENT_FAILURE_VERDICTS)} - UNTOOLABLE and ERROR are")
    print("   co-members, so this relabel changes the REPORT and the FEEDBACK,")
    print("   not the routing or demotion behaviour.)")

    print()
    print("=" * 72)
    if failures:
        for f in failures:
            print("FALSIFIED: " + f)
        print("=" * 72)
        raise AssertionError(
            "UNTOOLABLE on arm 4 is a stale pre-routing label: the ladder "
            "executed a falsifier and returned ERROR, and that verdict was "
            "never written back to the entry.")
    print("NOT FALSIFIED - entry verdicts agree with their ladder's verdicts.")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole falsifier. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
