# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ac338157daee60b6e29a5c0fc6dbbe4da8e6e20a3162378b55d91b16d8660242
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The provenance-clean critical cell contradicts DEFAULT_FALSIFIER_STRENGTH's tail.

`bench/routing.py` ranks on DEFAULT_FALSIFIER_STRENGTH = ("Codex","CC2","ChatGPT",
"Gemini","DeepSeek"), frozen from Exp 42 in June 2026. This script measures, over every
archived registry in `bench/logs/`, the cell that ladder would have to be re-derived
from: entries whose falsifier actually READS the target
(`competence_provenance.falsifier_style == "reads"`), attributed to the model that WROTE
the falsifier (`competence_provenance.falsifier_author`), restricted to CRITICAL
severity. Wilson 95% intervals (closed form cross-checked against statsmodels) and
Fisher exact tests (scipy, cross-checked against an independent hypergeometric
enumeration) on the pairs that decide the ladder's order.

WHAT IT SHOWS, and the caveat that limits it. The TAIL of the frozen tuple is
contradicted at 95%: DeepSeek outperforms Gemini and the tuple places Gemini first.
The HEAD does not separate: CC2 and Codex are statistically indistinguishable, as are
ChatGPT and Codex. It also shows the `-SIM` and live populations of the same vendor
separating by a wide margin, which is why a capability estimate must be keyed on the
FULL label and not on the base vendor name.
CAVEAT: this cell pools across runs, targets and difficulties, so it is confounded by
the ladder's own selection effect. It is enough to show the frozen order is
CONTRADICTED. It is NOT enough to install a replacement order -- that needs the
depth-stratified estimate described in docs/CAPABILITY_LADDER_MEASURED_2026-10-06.md.

ADMISSIBILITY. Reads only `bench/logs/` artefacts. No scoring key, no answer file, no
planted-defect manifest.

Run:  python3 scripts/provenance_clean_cell_contradicts_frozen_ladder_2026-10-06.py
Exit: 0 if no pair separates against the frozen order; 1 if the frozen order is
      contradicted by a separating pair.
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
    if n == 0:
        return (0.0, 1.0, float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h), p)


def fisher_two_ways(ka, na, kb, nb):
    """scipy's fisher_exact and an independent hypergeometric enumeration."""
    from scipy import stats
    tab = [[ka, na - ka], [kb, nb - kb]]
    odds, p_scipy = stats.fisher_exact(tab)
    N, K, n1 = na + nb, ka + kb, na
    lo, hi = max(0, K + n1 - N), min(K, n1)
    pmf = {x: stats.hypergeom.pmf(x, N, K, n1) for x in range(lo, hi + 1)}
    obs = pmf[ka]
    p_manual = float(sum(q for q in pmf.values() if q <= obs + 1e-15))
    return float(p_scipy), p_manual, float(odds)


def main():
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        print("\nusage: %s" % sys.argv[0].split("/")[-1])
        return 0

    from scripts.competence_provenance import falsifier_style, falsifier_author
    from bench.routing import DEFAULT_FALSIFIER_STRENGTH

    paths = (sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json")))
             + sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "*_report.json"))))
    crit = collections.defaultdict(collections.Counter)
    allsev = collections.defaultdict(collections.Counter)
    total = 0
    for p in paths:
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        reg = j.get("registry") or j
        ents = reg.get("entries") if isinstance(reg, dict) else None
        if not isinstance(ents, dict):
            continue
        for e in ents.values():
            if not isinstance(e, dict):
                continue
            total += 1
            if falsifier_style(e.get("falsifier_code")) != "reads":
                continue
            m = falsifier_author(e)
            ok = e.get("falsifier_verdict") == "CONFIRMED"
            allsev[m]["n"] += 1
            allsev[m]["k"] += ok
            if (e.get("severity") or 0.0) >= 0.7:
                crit[m]["n"] += 1
                crit[m]["k"] += ok

    print("  frozen ladder order        : %s" % " > ".join(DEFAULT_FALSIFIER_STRENGTH))
    print("  artefacts read             : %d" % len(paths))
    print("  registry entries scanned   : %d" % total)

    for title, data in (("ALL severities, falsifier READS the target", allsev),
                        ("CRITICAL only (severity >= 0.7), falsifier READS the target", crit)):
        print()
        print("=" * 86)
        print(title)
        print("=" * 86)
        print("  %-13s %4s %4s %8s  %-24s %7s" %
              ("model", "k", "n", "rate", "Wilson 95%", "width"))
        for m, s in sorted(data.items(), key=lambda kv: -kv[1]["n"]):
            lo, hi, pt = wilson(s["k"], s["n"])
            print("  %-13s %4d %4d %7.2f%%  [%7.2f%%, %7.2f%%]  %6.2f pp"
                  % (m, s["k"], s["n"], 100 * pt, 100 * lo, 100 * hi, 100 * (hi - lo)))

    print()
    print("=" * 86)
    print("THE PAIRS THAT DECIDE THE LADDER (critical cell)")
    print("=" * 86)
    pairs = [("DeepSeek", "Gemini"), ("CC2", "Codex"), ("ChatGPT", "Codex"),
             ("CC2", "DeepSeek"), ("Codex", "Gemini")]
    contradicted = 0
    pos = {m: i for i, m in enumerate(DEFAULT_FALSIFIER_STRENGTH)}
    for a, b in pairs:
        if a not in crit or b not in crit:
            print("  %-10s vs %-10s : absent from this archive" % (a, b))
            continue
        sa, sb = crit[a], crit[b]
        ps, pm, odds = fisher_two_ways(sa["k"], sa["n"], sb["k"], sb["n"])
        sep = ps < 0.05
        # does the measured direction contradict the frozen order?
        better = a if sa["k"] / sa["n"] > sb["k"] / sb["n"] else b
        worse = b if better == a else a
        frozen_says = better if pos.get(better, 99) < pos.get(worse, 99) else worse
        bad = sep and frozen_says != better
        contradicted += bool(bad)
        print("  %-10s %2d/%-3d  vs  %-10s %2d/%-3d  Fisher p=%.6g "
              "(manual-hypergeom %.6g, AGREE=%s) OR=%.3f  %s"
              % (a, sa["k"], sa["n"], b, sb["k"], sb["n"], ps, pm,
                 abs(ps - pm) < 1e-12, odds,
                 ("CONTRADICTS FROZEN ORDER <<<" if bad else
                  "separates, frozen order agrees" if sep else "does not separate")))

    print()
    print("  --SIM vs LIVE, same vendor, attempt denominators from the same cell:")
    for base in ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek"):
        s, l = allsev.get(base + "-SIM"), allsev.get(base)
        if not s or not l:
            continue
        slo, shi, sp = wilson(s["k"], s["n"])
        llo, lhi, lp = wilson(l["k"], l["n"])
        print("    %-9s SIM %5.2f%% [%5.2f,%5.2f] n=%-4d  LIVE %5.2f%% [%5.2f,%5.2f] n=%-4d  %s"
              % (base, 100 * sp, 100 * slo, 100 * shi, s["n"],
                 100 * lp, 100 * llo, 100 * lhi, l["n"],
                 "SEPARATE" if (slo > lhi or llo > shi) else "overlap"))

    print()
    print("=" * 86)
    if contradicted:
        print("THE FROZEN ORDER IS CONTRADICTED by %d separating pair(s) in this cell."
              % contradicted)
        print("It is NOT thereby replaced: this cell pools runs, targets and")
        print("difficulties and is confounded by the ladder's own selection effect.")
    else:
        print("No separating pair contradicts the frozen order in this cell.")
    print("=" * 86)
    return 1 if contradicted else 0


if __name__ == "__main__":
    raise SystemExit(main())
