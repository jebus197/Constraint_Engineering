#!/usr/bin/env python3
"""How many findings block release while the routing ladder would refuse to serve them?

HIS LIST, 2026-10-16, item 3 of the 7 smaller defects: *"A counter whose release
condition disagrees with it about severity."* His ruling: *"Fix it all."*

THE DISAGREEMENT. `FindingRegistry.unverified_critical_count` blocks release on
an UNCONFIRMED entry at ANY severity, because his ruling of 2026-09-06 removed
the raw severity gate -- *"a model-assigned number deciding convergence is a
vote wearing a number's clothes"*. `_apply_routing`, which obtains the falsifier
that would resolve such an entry, admits a sub-critical one only when it carries
a routable instrument fault with an unspent attempt, or when no instrument has
ever touched it. An entry that falls between the two blocks release forever and
can never be worked.

`execute-do-not-grep`: the admission question is answered by CALLING
`reference_runner_v3._routing_would_admit`, the single predicate both the router
and the registry reader use, against each archived entry. Nothing here asserts
on source text, and nothing dispatches to a model.

WHAT THE REPAIR DOES AND DOES NOT DO. It REPORTS. Releasing these entries would
loosen the A4 gate on a model-assigned severity float, which the founder has
rejected 4 times and struck permanently on 2026-10-16. Widening routing costs a
paid dispatch per entry per round and changes paid-run behaviour, so that is his
decision. His ruling of 2026-10-12 is that a finding no instrument has read must
be *"fed back into the mechanics of the harness for resolution"* -- so a run
that CANNOT feed one back must say so rather than burn silently to the round cap.

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/a_blocker_the_ladder_will_not_serve_2026-10-16.py
    python3 scripts/a_blocker_the_ladder_will_not_serve_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def _runner():
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as R  # noqa: PLC0415
    return R


def _counter_blocks(e: dict) -> bool:
    """The counter's own pre-severity releases, mirrored for classification."""
    if e.get("status") != "UNCONFIRMED":
        return False
    if e.get("irreducible_escalation") and not e.get("integrity_unobserved"):
        return False
    if e.get("exhausted"):
        return False
    return True


def measure() -> dict:
    """Count by CALLING the live counter, never by reimplementing its conditions.

    THE DEFECT THIS REPLACES, and it is the one `execute-do-not-grep` exists for.
    A first version carried `_counter_blocks`, a local copy of the counter's skip
    conditions with THREE checks: a status other than UNCONFIRMED, an irreducible
    escalation, and the `exhausted` marking. The live
    `FindingRegistry.unverified_critical_count` has FIVE, the 2 missing ones being
    an excluded integrity violation and a sub-critical severity that is PROVEN. So
    the copy over-counted, and 3 different denominators for one quantity reached
    the founder's desk: 212 from this producer, 197 from a correction of
    2026-10-16, and 174 from calling the counter across the archive on 2026-10-17.
    He asked, reasonably, whether the figure was real at all.

    A producer that reimplements the predicate it reports on measures the copy.
    This one now instantiates a registry per archived run and calls the runner's
    own `unverified_critical_count()` and `blockers_routing_cannot_serve()`, which
    are the methods the live gate uses.
    """
    R = _runner()
    total = blocked = unservable = 0
    per_run: dict[str, dict] = {}
    why = collections.Counter()
    unreadable = 0
    # TOP-LEVEL RUN STATES ONLY. `rglob` found 74 files where there are 61 runs:
    # 10 sit inside `sandbox_harvest/`, which are archived copies of what a SEAT
    # saw, and 3 at other nesting. Counting them inflates every figure, and it is
    # half of why 3 different denominators -- 212, 197 and 174 -- reached the
    # founder for one quantity. A run state is `bench/logs/<run>/runner_state.json`
    # and nothing deeper.
    for path in sorted(LOGS.rglob("runner_state.json")):
        if len(path.relative_to(LOGS).parts) != 2:
            continue
        try:
            ents = (json.loads(path.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            unreadable += 1
            continue
        if not ents:
            continue
        run = path.relative_to(LOGS).parts[0]
        reg = R.FindingRegistry()
        reg.entries = ents
        try:
            n_blocked = reg.unverified_critical_count()
            unservable_ids = reg.blockers_routing_cannot_serve()
        except Exception:                               # noqa: BLE001
            unreadable += 1
            continue
        total += len(ents)
        blocked += n_blocked
        unservable += len(unservable_ids)
        per_run[run] = {"blocked": n_blocked, "unservable": len(unservable_ids)}
        # Name the reason, so the fix can be aimed rather than guessed at. The
        # reasons are read off the entries the LIVE reader named, not off a
        # locally re-derived set.
        for eid in unservable_ids:
            e = ents.get(eid) or {}
            ns = R._routing_ladder_never_served(e)
            if e.get("error_routed"):
                why["the one-attempt guard is already spent"] += 1
            elif not e.get("escalated") and not ns:
                why["not escalated and already served"] += 1
            elif (e.get("severity") or 0.0) < R.CRITICAL_SEVERITY_THRESHOLD:
                why["sub-critical, served, no routable instrument fault"] += 1
            else:
                why["other"] += 1
    return {
        "entries": total, "blocked": blocked, "unservable": unservable,
        "reasons": dict(why), "unreadable_states": unreadable,
        "runs_affected": sorted(k for k, v in per_run.items() if v["unservable"]),
        "per_run": per_run,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    m = measure()
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
        return 0

    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta

    print("BLOCKERS THE ROUTING LADDER WOULD REFUSE TO SERVE")
    print(f"  archived entries scanned ............. {m['entries']}")
    print(f"  counted as blockers .................. {m['blocked']}")
    print(f"  of those, routing would REFUSE ....... {m['unservable']}")
    n, k = m["blocked"], m["unservable"]
    if n:
        lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
        lo_e, hi_e = proportion_confint(k, n, alpha=0.05, method="beta")
        lo_s = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
        hi_s = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
        assert abs(lo_e - lo_s) < 1e-9 and abs(hi_e - hi_s) < 1e-9
        print(f"  {100*k/n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%]  "
              f"Clopper-Pearson [{100*lo_e:.4f}%, {100*hi_e:.4f}%]")
    print(f"  runs affected ........................ {len(m['runs_affected'])}")
    print()
    print("  WHY EACH ONE IS REFUSED:")
    for r, c in sorted(m["reasons"].items(), key=lambda kv: -kv[1]):
        print(f"       {c:>5}  {r}")
    print()
    print("  THE WORST-AFFECTED RUNS:")
    rows = sorted(m["per_run"].items(), key=lambda kv: -kv[1]["unservable"])
    for run, v in rows[:8]:
        if not v["unservable"]:
            continue
        print(f"       {v['unservable']:>4} of {v['blocked']:>4}  {run}")
    print()
    if k:
        print("  VERDICT: the disagreement is live. These findings block release")
        print("  and cannot be worked. The runner now REPORTS them beside the A4")
        print("  line, as 'A4 LIMBO', so a run says so instead of burning to the")
        print("  round cap. Whether to widen routing or leave them for the human")
        print("  is his decision, because widening costs a paid dispatch per")
        print("  entry per round and narrowing the counter is the severity gate")
        print("  he has struck permanently.")
        return 0
    print("  VERDICT: no archived blocker is unservable. If the router was")
    print("  widened or the counter narrowed, that is a behaviour change needing")
    print("  his ruling -- re-derive before citing this as clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
