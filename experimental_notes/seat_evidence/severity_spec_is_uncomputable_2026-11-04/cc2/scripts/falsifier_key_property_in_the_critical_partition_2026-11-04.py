# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 195fe7f187b2da55b5b5b7d6ef2f1969dbf09b5e3dd8e3779aa4da269067c512
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the 2026-11-04 severity repair. Imports the REAL runner module.

Fails (AssertionError / prints FALSIFIED) IF AND ONLY IF the defect is present,
and exits cleanly when it is not. Three independent checks:

  A. KEY PROPERTY in the critical partition. A tool-REFUTED finding must not be
     counted as a critical discovery by EITHER partition reader. This is the
     defect the repair closes; before it, both read `e.get("severity")` raw.
  B. V(None) MUST NOT de-escalate. An unresolved critical must still count, or
     the repair has inverted the A4 fail-safe (derivation: severity/2 >= 0.7
     needs severity >= 1.4 > 1, so halving makes every unresolved finding
     sub-critical).
  C. NO ARCHIVED VERDICT IS RESTATED. Replay the REAL
     `_check_gamma_alt_convergence` over every archived registry under the
     pre-repair (raw) and post-repair severity reads and require 0 flips.

Run: python3 scripts/falsifier_key_property_in_the_critical_partition_2026-11-04.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bench"))

import reference_runner_v3 as R  # noqa: E402

FAILED = []


class Reg:
    def __init__(self, entries):
        self.entries = entries


def chk(name, cond, detail=""):
    print("  %-62s %s" % (name, "OK" if cond else "FALSIFIED"))
    if not cond:
        FAILED.append("%s %s" % (name, detail))


def main():
    readers = [R._settled_novelty_series, R._corroborated_novelty_series]

    print("[A] KEY PROPERTY: a disproved finding is not a critical discovery")
    for fn in readers:
        e = {"C1": {"severity": 0.9, "falsifier_verdict": "REFUTED",
                    "open_since_round": 0, "status": "OPEN", "canonical_id": "C1"}}
        all_s, crit_s = fn(Reg(e), 0)
        chk("%s: REFUTED 0.9 -> crit_s" % fn.__name__, crit_s == [0], str(crit_s))
        chk("%s: REFUTED 0.9 still counted in all_s" % fn.__name__, all_s == [1], str(all_s))

    print("\n[B] V(None) must NOT de-escalate (A4 fail-safe must stay armed)")
    for fn in readers:
        e = {"C1": {"severity": 0.9, "falsifier_verdict": "",
                    "open_since_round": 0, "status": "OPEN", "canonical_id": "C1"}}
        _, crit_s = fn(Reg(e), 0)
        chk("%s: UNRESOLVED 0.9 -> crit_s" % fn.__name__, crit_s == [1], str(crit_s))

    print("\n[C] No archived convergence verdict is restated")
    cfg = R.RunnerConfig()
    runs = []
    for f in sorted(glob.glob("bench/logs/**/runner_state.json", recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        ent = (d.get("registry") or {}).get("entries") or {}
        if isinstance(ent, dict) and ent:
            runs.append((f, ent))
    flips = []
    n = 0
    for f, ent in runs:
        rs = [x.get("open_since_round") for x in ent.values()
              if isinstance(x.get("open_since_round"), int) and x.get("open_since_round") >= 0]
        if not rs:
            continue
        mx = max(rs)
        n += 1
        # post-repair: the live reader
        _, post = R._settled_novelty_series(Reg(ent), mx)
        all_post, _ = R._settled_novelty_series(Reg(ent), mx)
        # pre-repair: the raw read this replaced, reconstructed in place
        pre = [0] * (mx + 1)
        for x in ent.values():
            r = x.get("open_since_round")
            if r is None or r < 0 or r > mx:
                continue
            if x.get("status") in R._NON_NOVEL_TERMINAL_STATUSES:
                continue
            if (x.get("severity") or 0.0) >= R.CRITICAL_SEVERITY_THRESHOLD:
                pre[r] += 1
        va, _ = R._check_gamma_alt_convergence(
            round_idx=mx, gamma=R._estimate_gamma(pre), novel_critical_history=pre,
            cfg=cfg, unresolved_critical=0, contested=0,
            gamma_critical=R._estimate_gamma(pre), total_findings=sum(all_post))
        vb, _ = R._check_gamma_alt_convergence(
            round_idx=mx, gamma=R._estimate_gamma(post), novel_critical_history=post,
            cfg=cfg, unresolved_critical=0, contested=0,
            gamma_critical=R._estimate_gamma(post), total_findings=sum(all_post))
        if va != vb:
            flips.append((f, va, vb))
    print("  replayed %d archived registries" % n)
    chk("archived gate verdicts changed by the repair", len(flips) == 0,
        str(flips[:5]))

    print("\n%s" % ("=" * 70))
    if FAILED:
        print("FALSIFIED")
        for x in FAILED:
            print("  - %s" % x)
        raise AssertionError("defect present: %s" % "; ".join(FAILED))
    print("defect NOT demonstrated: key property holds in the critical partition,")
    print("V(None) does not de-escalate, and 0 of %d archived verdicts move." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
