#!/usr/bin/env python3
"""Do any archived door-open entries carry untested instrument-contact fields?

JOINT ROUND J1, 2026-10-12. The producer for two figures cited in
`_routing_ladder_never_served`'s error_routed conjunct and its tests:

  * 68 archived entries carry error_routed=True with NO routing_history —
    the flag (Exp 43, 2026-07-22) predates the history field (2026-09-02).
  * 0 of 681 door-open entries across every archived runner_state.json carry
    error_routed or escalated — Wilson upper bound 0.5609% (statsmodels and
    mpmath agreeing to 1e-9) — i.e. the conjunct guards a state the archive
    does not currently contain; its justification is the LIVE telemetry
    except-path and the pre-2026-09-02 record shape, not a live instance.

Usage: python3 scripts/door_open_archive_carries_no_instrument_contact_2026-10-12.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402

answer_help(__doc__)

from bench.reference_runner_v3 import _routing_ladder_never_served  # noqa: E402


def main() -> int:
    flag_no_history = 0
    door_open = 0
    contact = []
    for p in (glob.glob("bench/logs/*/runner_state.json")
              + glob.glob("bench/logs_quarantine/*/runner_state.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ents = d.get("registry", {}).get("entries", {}) or d.get("entries", {})
        if not isinstance(ents, dict):
            continue
        for cid, e in ents.items():
            if e.get("error_routed") and not e.get("routing_history"):
                flag_no_history += 1
            if _routing_ladder_never_served(e):
                door_open += 1
                if e.get("error_routed") or e.get("escalated"):
                    contact.append((p, cid))
    print(f"error_routed with no routing_history (archive): {flag_no_history}")
    print(f"door-open entries across the archive: {door_open}")
    print(f"door-open AND carrying error_routed/escalated: {len(contact)}")
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(len(contact), max(door_open, 1),
                                    alpha=0.05, method="wilson")
        print(f"proportion {len(contact)}/{door_open}, Wilson "
              f"[{lo:.4%}, {hi:.4%}]")
    except ImportError:
        print("statsmodels unavailable; proportion reported without interval")
    return 0


if __name__ == "__main__":
    sys.exit(main())
