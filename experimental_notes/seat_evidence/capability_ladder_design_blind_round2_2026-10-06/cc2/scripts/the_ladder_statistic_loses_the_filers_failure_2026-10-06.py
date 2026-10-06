# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ff0a0e281840bd259d817642e501d021b0deef16f2c5d7f526516749eb2eb1ad
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The competence statistic the ladder would rank on counts ENTRIES, not ATTEMPTS.

WHAT WAS ALREADY FIXED, AND WHY THAT FIX IS HALF OF ONE.
`scripts/competence_provenance.py:falsifier_author` was repaired on 2026-10-06 so an
entry resolved by the routing ladder is credited to `resolved_by_routing` -- the rung
that WROTE the working falsifier -- rather than to `source_model`, the model that
filed the finding and failed to demonstrate it. That repair is correct and this script
does not dispute it.

THE RESIDUAL DEFECT. `analyse()` iterates ENTRIES and assigns each entry to exactly
ONE model. So when a weak filer's falsifier fails and a strong rung resolves it, the
entry leaves the filer's record ENTIRELY -- the filer loses a numerator it should
never have had AND a denominator it SHOULD keep. A failed falsifier is a failed
ATTEMPT, and the founder's ruling is that the ladder rank on "what a model can be
statistically demonstrated to have done". A model that tried and failed did
something, and the current statistic cannot see it.

The direction is the same one the original defect had: it flatters the models the
ladder is supposed to demote. Pre-fix the filer banked a false success; post-fix the
filer simply does not record the failure. In both cases its rate is computed over a
population that excludes its failures.

WHAT THIS SCRIPT MEASURES, over every archived `runner_state.json` and
`*_report.json` in `bench/logs/`:
  A. entry-level (what `competence_provenance.analyse` computes today), and
  B. attempt-level: every (model, finding) falsification ATTEMPT is one Bernoulli
     trial. A routed entry contributes a FAILURE to its `source_model` and a
     success-or-failure to each rung named in `routing_history`.
Both with Wilson 95% intervals, cross-verified by statsmodels and a closed form.
Then it asks the only question that matters for the founder's ruling: does the
RANK ORDER differ between A and B?

ADMISSIBILITY. This reads only `bench/logs/` run artefacts and `bench/routing.py`.
It opens no scoring key, no answer file and no planted-defect manifest.

Run:  python3 scripts/the_ladder_statistic_loses_the_filers_failure_2026-10-06.py
Exit: 0 if A and B agree on rank order; 1 if the defect changes the ladder.
"""
from __future__ import annotations

import collections
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def wilson(k, n, z=1.959963984540054):
    """Wilson score interval, closed form. Returns (lo, hi, centre)."""
    if n == 0:
        return (0.0, 1.0, float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h), p)


def wilson_statsmodels(k, n):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return float(lo), float(hi)


def _entries(path: pathlib.Path):
    try:
        j = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return {}
    reg = j.get("registry") or j
    ents = reg.get("entries") if isinstance(reg, dict) else None
    return ents if isinstance(ents, dict) else {}


def main():
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        print("\nusage: %s" % sys.argv[0].split("/")[-1])
        return 0

    paths = [pathlib.Path(p) for p in
             sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json")))
             + sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "*_report.json")))]

    # A: entry-level, replicating competence_provenance.analyse's attribution.
    entry_lvl = collections.defaultdict(collections.Counter)
    # B: attempt-level.
    att_lvl = collections.defaultdict(collections.Counter)

    n_entries = 0
    n_routed = 0
    n_routed_differs = 0
    n_history = 0

    for p in paths:
        for e in _entries(p).values():
            if not isinstance(e, dict):
                continue
            n_entries += 1
            src = (e.get("source_model") or "").strip()
            rbr = (e.get("resolved_by_routing") or "").strip()
            confirmed = e.get("falsifier_verdict") == "CONFIRMED"

            # ---- A: one entry, one owner (current behaviour) ----
            owner = rbr or src or "?"
            entry_lvl[owner]["n"] += 1
            if confirmed:
                entry_lvl[owner]["k"] += 1

            # ---- B: one attempt, one trial ----
            if src:
                # The filer attempted a falsifier. It succeeded only if the entry
                # was NOT routed away and the verdict is CONFIRMED.
                att_lvl[src]["n"] += 1
                if confirmed and not rbr:
                    att_lvl[src]["k"] += 1
            if rbr:
                n_routed += 1
                if rbr != src:
                    n_routed_differs += 1
            # Every rung the ladder actually dispatched is an attempt, whether or
            # not it won. routing_history is the only place this is recorded.
            hist = e.get("routing_history")
            seen_rungs = set()
            if isinstance(hist, list):
                for h in hist:
                    if not isinstance(h, dict):
                        continue
                    m = (h.get("model_used") or "").strip()
                    if not m:
                        continue
                    n_history += 1
                    key = (m, h.get("round"))
                    if key in seen_rungs:
                        continue
                    seen_rungs.add(key)
                    att_lvl[m]["n"] += 1
                    if (h.get("verdict") or "").upper() == "CONFIRMED":
                        att_lvl[m]["k"] += 1
            elif rbr:
                # Resolved by a rung with no history recorded (pre-2026-10-03
                # archives): still an attempt that succeeded.
                att_lvl[rbr]["n"] += 1
                att_lvl[rbr]["k"] += 1

    print("=" * 78)
    print("ARCHIVE SCANNED")
    print("=" * 78)
    print("  artefacts read                        : %d" % len(paths))
    print("  registry entries                      : %d" % n_entries)
    print("  entries carrying resolved_by_routing  : %d" % n_routed)
    print("    of those, resolver != source_model  : %d" % n_routed_differs)
    print("  routing_history rung records           : %d" % n_history)

    def table(title, data):
        print()
        print("=" * 78)
        print(title)
        print("=" * 78)
        print("  %-12s %6s %6s %8s  %-22s %s"
              % ("model", "k", "n", "rate", "Wilson 95% (closed form)", "statsmodels AGREE"))
        rows = []
        for m, s in data.items():
            k, n = s["k"], s["n"]
            lo, hi, pt = wilson(k, n)
            if n:
                slo, shi = wilson_statsmodels(k, n)
                agree = abs(slo - lo) < 1e-9 and abs(shi - hi) < 1e-9
            else:
                agree = True
            rows.append((m, k, n, pt, lo, hi, agree))
        rows.sort(key=lambda r: (-(r[3] if r[3] == r[3] else -1), r[0]))
        for m, k, n, pt, lo, hi, agree in rows:
            print("  %-12s %6d %6d %7.2f%%  [%7.4f%%, %7.4f%%]  %s"
                  % (m, k, n, 100 * pt, 100 * lo, 100 * hi, "YES" if agree else "NO"))
        return [r[0] for r in rows], rows

    order_a, rows_a = table("A.  ENTRY-LEVEL  (what competence_provenance.analyse computes)",
                            entry_lvl)
    order_b, rows_b = table("B.  ATTEMPT-LEVEL (every dispatched falsification is one trial)",
                            att_lvl)

    print()
    print("=" * 78)
    print("DOES THE DEFECT MOVE THE LADDER?")
    print("=" * 78)
    common = [m for m in order_a if m in order_b]
    pos_b = {m: i for i, m in enumerate(order_b)}
    seq = [pos_b[m] for m in common]
    inversions = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq))
                     if seq[i] > seq[j])
    print("  entry-level order   : %s" % " > ".join(order_a))
    print("  attempt-level order : %s" % " > ".join(order_b))
    print("  models in both      : %d" % len(common))
    print("  rank inversions between A and B : %d" % inversions)

    # The decisive question for the design: do any two models SEPARATE at 95%?
    print()
    print("  PAIRWISE SEPARATION AT 95% (attempt-level, Wilson non-overlap):")
    sep = 0
    pairs = 0
    rb = {r[0]: r for r in rows_b}
    ms = [m for m in order_b if rb[m][2] >= 1]
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = rb[ms[i]], rb[ms[j]]
            pairs += 1
            if a[4] > b[5] or b[4] > a[5]:
                sep += 1
                print("    SEPARATES: %-12s [%.4f, %.4f]  vs  %-12s [%.4f, %.4f]"
                      % (a[0], a[4], a[5], b[0], b[4], b[5]))
    print("    pairs tested: %d   pairs separating: %d" % (pairs, sep))
    if sep == 0:
        print("    NO PAIR SEPARATES. A point-estimate ranking would be ranking noise.")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    if inversions:
        print("  REFUTED: entry-level and attempt-level accounting disagree on the")
        print("  ladder order. The statistic the founder's ruling would rank on is")
        print("  sensitive to this choice, so the choice must be made explicitly.")
    else:
        print("  The two accountings agree on order in this archive. The defect is")
        print("  real in the denominator but has not yet inverted a rank here.")
    return 1 if inversions else 0


if __name__ == "__main__":
    raise SystemExit(main())
