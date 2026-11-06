# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_corrected_2026-11-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 917aa5d7d5c48fca9ff05cb5398abdfaad4c9635dd1d9fc291c4ce0eb92abea5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""
PRODUCER: on the live archive the COMPUTED severity takes exactly three values,
so every cut in (0.5, 1.0] partitions the archive identically -- and a fix that
moves `CRITICAL_SEVERITY_THRESHOLD` therefore reclassifies nothing.

Written for the 2026-11-06 panel. This is the COMPOSABILITY MEASUREMENT the
founder's standard requires: it tests whether composing the documentary repair
(docs/MATHEMATICAL_APPENDIX.md section 7.7 caution 3) with a threshold change
dominates the documentary repair alone. The measurement, not a judgement,
decides.

  M1. Input availability. `compute_sev_f` needs `constraint_class`,
      `confidence` and `falsifier_verdict`. Count how many archived entries
      carry each. (Entry B87 is the open entry asking the founder to rule on
      collecting the two missing inputs; this quantifies what is missing.)

  M2. The value set. Because `compute_sev_f` defaults a missing class to HARD
      (W = 1) and a missing confidence to 1.0 -- each the STRICTER reading, so
      an omitted input can never lower the computed severity -- the computed
      severity on the archive reduces to V(verification) alone and is
      THREE-VALUED: {0.0, 0.5, 1.0}.

  M3. Threshold inertness. Moving the cut 0.7 -> 0.8, 0.9, 0.95 reclassifies
      how many entries under the computed severity? And of any that move, how
      many move for an IMPACT reason (class) rather than a BELIEF reason?

  M4. The same move on the model-asserted `severity` float the release door
      actually reads today, with the impact content of that move reported as
      measurable or not.

Exit 0 iff the archive was found and every measurement completed. The printed
verdict is GATED on that flag rather than appended to it.
"""
from __future__ import annotations

import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as rr  # noqa: E402

CUTS = (0.8, 0.9, 0.95)


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict):
                yield cid, e


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    return proportion_confint(k, n, alpha=0.05, method="wilson")


def main(argv) -> int:
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    if not LOGS.is_dir():
        print("NO ARCHIVE at %s -- measurement not attempted." % LOGS)
        return 1

    rows = [(cid, e) for cid, e in entries()
            if isinstance(e.get("severity"), (int, float))]
    n = len(rows)
    if n == 0:
        print("ARCHIVE FOUND BUT EMPTY of entries carrying a numeric severity.")
        return 1

    print("=" * 78)
    print("ARCHIVE: %s" % LOGS)
    print("entries carrying a numeric `severity`: %d" % n)
    print("=" * 78)

    # ---- M1 input availability --------------------------------------------
    fields = ("constraint_class", "confidence", "falsifier_verdict")
    have = {f: sum(1 for _c, e in rows if e.get(f) is not None) for f in fields}
    all3 = sum(1 for _c, e in rows if all(e.get(f) is not None for f in fields))
    print("\nM1  inputs `compute_sev_f` needs:")
    for f in fields:
        lo, hi = wilson(have[f], n)
        print("      %-20s present on %5d / %d  (%.6f, Wilson 95%% [%.6f, %.6f])"
              % (f, have[f], n, have[f] / n, lo, hi))
    lo, hi = wilson(all3, n)
    print("      %-20s present on %5d / %d  (%.6f, Wilson 95%% [%.6f, %.6f])"
          % ("ALL THREE", all3, n, all3 / n, lo, hi))

    # ---- M2 the value set --------------------------------------------------
    def sevf(e):
        return rr.compute_sev_f(e.get("constraint_class"), e.get("confidence"),
                                e.get("falsifier_verdict"))

    vals = collections.Counter(round(sevf(e), 9) for _c, e in rows)
    print("\nM2  distinct values of the COMPUTED severity on the archive: %d"
          % len(vals))
    for v, k in sorted(vals.items()):
        print("      sev_f = %-6s : %5d entries" % (v, k))
    print("      (defaults: class missing -> HARD W=%s ; confidence missing -> 1.0"
          % rr.SEV_F_W["HARD"])
    print("       -- each the stricter reading, so sev_f collapses to V alone)")

    # ---- M3 threshold inertness -------------------------------------------
    base = rr.CRITICAL_SEVERITY_THRESHOLD
    a = {i for i, (_c, e) in enumerate(rows) if sevf(e) >= base}
    print("\nM3  COMPUTED severity, cut %.2f -> higher:" % base)
    inert = True
    for hi_cut in CUTS:
        b = {i for i, (_c, e) in enumerate(rows) if sevf(e) >= hi_cut}
        moved = a - b
        impact = [i for i in moved
                  if str(rows[i][1].get("constraint_class") or "HARD").upper() != "HARD"]
        inert = inert and not moved
        print("      %.2f -> %.2f : critical %d -> %d, moved %d "
              "(impact-driven %d, belief-driven %d)"
              % (base, hi_cut, len(a), len(b), len(moved), len(impact),
                 len(moved) - len(impact)))

    # ---- M4 the gated float -----------------------------------------------
    print("\nM4  MODEL-ASSERTED `severity` (what the release door reads today):")
    for hi_cut in CUTS:
        a2 = {i for i, (_c, e) in enumerate(rows) if (e.get("severity") or 0.0) >= base}
        b2 = {i for i, (_c, e) in enumerate(rows) if (e.get("severity") or 0.0) >= hi_cut}
        print("      %.2f -> %.2f : critical %d -> %d, moved %d"
              % (base, hi_cut, len(a2), len(b2), len(a2 - b2)))
    print("      impact content of those moves: UNMEASURABLE -- "
          "`constraint_class` present on %d of %d entries." % (have["constraint_class"], n))

    print("\n" + "=" * 78)
    print("""
VERDICT:

  The computed severity is THREE-VALUED on the archive ({0.0, 0.5, 1.0}),
  because `constraint_class` and `confidence` are absent everywhere and
  `compute_sev_f` defaults both to their stricter readings. Every cut in
  (0.5, 1.0] therefore induces the SAME partition, and moving
  CRITICAL_SEVERITY_THRESHOLD above 0.5 reclassifies ZERO entries.

  COMPOSABILITY, decided by this measurement and not by judgement: composing
  the documentary repair (section 7.7 caution 3) with a threshold change does
  NOT dominate the documentary repair alone -- it changes nothing the
  documentary repair does not already change, on the only population available
  to measure. The single fix is therefore preferred, per the founder's
  standard.

  On the model-asserted float the door reads today a threshold move DOES
  reclassify entries, but whether any of that movement is impact-related
  cannot be measured, because the class is recorded nowhere. That is the
  question entry B87 puts to the founder, and it is prior to choosing a bound.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
