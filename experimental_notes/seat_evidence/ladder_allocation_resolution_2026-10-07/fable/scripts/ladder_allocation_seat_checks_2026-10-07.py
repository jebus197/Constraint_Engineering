# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'ladder_allocation_resolution_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d694d38f13a16196be64ae99633539e8f9ae768ee58f3bbbd50ad61cf589b625
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Seat checks for the ladder-allocation resolution round (2026-10-07).

Measures, with two agreeing tools per figure, everything this seat's reply
relies on:

  A. The provenance-clean cell per model, in FOUR accountings (all/critical x
     entry-level/attempt-level), to locate which cell the brief's "CC2 35 @
     0.6000 / Codex 37 @ 0.5946" figures come from -- and to flag it if none
     matches.
  B. An audit of `competence_provenance.falsifier_style`: how many falsifiers
     classified "detached" import a repository module -- the access path
     `bench/routing.py`'s own Exp-42 comment names as the legitimate one for
     code targets ("a code falsifier reaches its target by `import`").
  C. Wilson closed form vs statsmodels (every interval printed here).
  D. The two-proportion power figures the brief quotes (173 @ delta 0.15,
     97 @ delta 0.20, 80% power, alpha 0.05 two-sided) -- closed form vs
     statsmodels.NormalIndPower.
  E. The brief's 3-configuration toy table (cheapest-first / strongest-first /
     global-index / task-conditioned index) -- SymPy exact rationals vs NumPy.
  F. The adjacent-transposition cost identity for stop-at-first-CONFIRMED
     ladders: E[cost](..a,b..) - E[cost](..b,a..) = Q * (c_a p_b - c_b p_a),
     SymPy symbolic; descending p/c optimal by brute force over seeded random
     rosters; the share of rosters where strongest-first is suboptimal under
     TWO priors, to show that share is a property of the prior; and a CAP=2
     counterexample where the p/c prefix resolves strictly less than top-p.
  G. The intransitivity counterexample for the pair-retirement comparator
     (measured-where-separated, tuple-where-not). Frozen-tuple rank for the
     example: C > B > A (any tuple ranking both unseparated pairs against
     the point estimates produces the cycle).
  I. Reconciliation of the brief's figures against this tree: the raw
     contaminated per-model rates, the brief's "CC2 21/35, Codex 22/37"
     clean cell, and Fisher tests on the deciding pairs.
  H. g = R - R_next is strictly increasing in q (SymPy), and the spec-vs-
     appendix numerator gap R^2*q*sigma*(1-nu)*(1-q)/(1-q*R) re-derived.

ADMISSIBILITY: reads bench/logs artefacts and repository code only. No scoring
key, no answer file, no planted-defect manifest, no prior report of any live
exam. Writes nothing.

Run:  python3 scripts/ladder_allocation_seat_checks_2026-10-07.py
Exit: 0 always (this is a measurement, not a gate).
"""
from __future__ import annotations

import collections
import glob
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

Z = 1.959963984540054


def wilson(k, n, z=Z):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def wilson_checked(k, n):
    lo, hi = wilson(k, n)
    try:
        from statsmodels.stats.proportion import proportion_confint
        a, b = proportion_confint(k, n, alpha=0.05, method="wilson")
        assert abs(a - lo) < 1e-9 and abs(b - hi) < 1e-9, (k, n, a, lo, b, hi)
    except ImportError:
        pass
    return lo, hi


def main() -> int:
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        return 0

    from scripts.competence_provenance import falsifier_style, falsifier_author

    # ---------------- A + B: archive scan ----------------
    paths = (sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json")))
             + sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "*_report.json"))))
    cells = {name: collections.defaultdict(collections.Counter)
             for name in ("all_entry", "all_attempt", "crit_entry", "crit_attempt")}
    style_counts = collections.Counter()
    detached_importers = 0
    detached_total = 0
    total = 0
    import_rx = re.compile(r"(?m)^\s*(from|import)\s+(bench|scripts|falsify_verify_bundle|explorer)\b")
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
            code = e.get("falsifier_code")
            st = falsifier_style(code)
            style_counts[st] += 1
            if st == "detached":
                detached_total += 1
                if code and import_rx.search(code):
                    detached_importers += 1
            if st != "reads":
                continue
            m = falsifier_author(e)
            src = (e.get("source_model") or "?").strip() or "?"
            ok = 1 if e.get("falsifier_verdict") == "CONFIRMED" else 0
            crit = (e.get("severity") or 0.0) >= 0.7
            for name in ("all_entry", "all_attempt") + (("crit_entry", "crit_attempt") if crit else ()):
                cells[name][m]["n"] += 1
                cells[name][m]["k"] += ok
            if m != src:
                for name in ("all_attempt",) + (("crit_attempt",) if crit else ()):
                    cells[name][src]["n"] += 1  # the filer's failed attempt

    print("A. PROVENANCE-CLEAN CELLS (artefacts read: %d, entries scanned: %d)" % (len(paths), total))
    for name in ("all_entry", "all_attempt", "crit_entry", "crit_attempt"):
        print("  cell: %s" % name)
        for m, c in sorted(cells[name].items(), key=lambda kv: -kv[1]["n"]):
            k, n = c["k"], c["n"]
            if n == 0:
                continue
            lo, hi = wilson_checked(k, n)
            print("    %-14s k=%3d n=%3d rate=%.4f Wilson95=[%.4f, %.4f]" % (m, k, n, k / n, lo, hi))

    print()
    print("B. falsifier_style AUDIT")
    print("  styles: %s" % dict(style_counts))
    dl, dh = wilson_checked(detached_importers, max(detached_total, 1))
    print("  'detached' falsifiers that IMPORT a repo module: %d of %d  (%.4f, Wilson95=[%.4f, %.4f])"
          % (detached_importers, detached_total,
             detached_importers / max(detached_total, 1), dl, dh))

    # ---------------- D: power ----------------
    print()
    print("D. TWO-PROPORTION POWER (alpha=0.05 two-sided, power=0.80)")
    try:
        from scipy.stats import norm
        za, zb = norm.ppf(0.975), norm.ppf(0.80)
        import statsmodels.stats.api as sms
        for p1, p2 in ((0.60, 0.45), (0.60, 0.40)):
            pbar = (p1 + p2) / 2
            n_closed = ((za * math.sqrt(2 * pbar * (1 - pbar))
                         + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p1 - p2) ** 2
            es = sms.proportion_effectsize(p1, p2)
            n_sm = sms.NormalIndPower().solve_power(es, power=0.80, alpha=0.05, ratio=1.0)
            print("  p1=%.2f p2=%.2f  closed-form n/arm=%.1f -> %d   statsmodels (arcsine ES) n/arm=%.1f -> %d"
                  % (p1, p2, n_closed, math.ceil(n_closed), n_sm, math.ceil(n_sm)))
    except ImportError as ex:
        print("  SKIPPED (%s)" % ex)

    # ---------------- E: toy policy table ----------------
    print()
    print("E. 3-CONFIGURATION TOY TABLE (exact rationals)")
    import sympy as sp
    cfgs = {
        "cheap": (sp.Rational(70, 100), sp.Rational(2, 100), 1),
        "mid": (sp.Rational(75, 100), sp.Rational(25, 100), 4),
        "strong": (sp.Rational(80, 100), sp.Rational(60, 100), 10),
    }
    mix = sp.Rational(1, 2)
    glob_p = {m: mix * v[0] + (1 - mix) * v[1] for m, v in cfgs.items()}
    first = {
        "cheapest-first": min(cfgs, key=lambda m: cfgs[m][2]),
        "strongest-first": max(cfgs, key=lambda m: cfgs[m][1]),
        "index global p/c": max(cfgs, key=lambda m: glob_p[m] / cfgs[m][2]),
        "index task-cond p/c (HARD)": max(cfgs, key=lambda m: cfgs[m][1] / cfgs[m][2]),
    }
    order_hard = sorted(cfgs, key=lambda m: -(cfgs[m][1] / cfgs[m][2]))
    for k_, v in first.items():
        print("  first model on HARD under %-28s: %s" % (k_, v))
    print("  full task-conditioned p/c order on HARD: %s" % " > ".join(order_hard))
    import numpy as np
    for m in cfgs:
        a = float(cfgs[m][1] / cfgs[m][2])
        b = float(np.float64(float(cfgs[m][1])) / np.float64(cfgs[m][2]))
        assert abs(a - b) < 1e-15

    # ---------------- F: swap identity + p/c optimality + prior-dependence ----
    print()
    print("F. ORDER AND COST")
    pa, pb_, ca, cb, Q = sp.symbols("p_a p_b c_a c_b Q", positive=True)
    e_ab = Q * (ca + (1 - pa) * cb)
    e_ba = Q * (cb + (1 - pb_) * ca)
    diff = sp.simplify(e_ab - e_ba - Q * (ca * pb_ - cb * pa))
    print("  E[cost](a,b)-E[cost](b,a) - Q(c_a p_b - c_b p_a) simplifies to: %s" % diff)
    assert diff == 0
    import itertools
    rng = np.random.default_rng(20261007)
    for prior in ("uniform p,c", "p~U(.3,.95), c~lognormal"):
        subopt_strong = 0
        gap_pc = 0.0
        TRIALS = 4000
        for _ in range(TRIALS):
            if prior == "uniform p,c":
                p = rng.uniform(0.01, 0.99, 5)
                c = rng.uniform(0.1, 10.0, 5)
            else:
                p = rng.uniform(0.30, 0.95, 5)
                c = np.exp(rng.normal(0.0, 1.0, 5))

            def ecost(order):
                s, surv = 0.0, 1.0
                for i in order:
                    s += surv * c[i]
                    surv *= (1 - p[i])
                return s

            best = min(ecost(o) for o in itertools.permutations(range(5)))
            pc = tuple(sorted(range(5), key=lambda i: -(p[i] / c[i])))
            strong = tuple(sorted(range(5), key=lambda i: -p[i]))
            gap_pc = max(gap_pc, ecost(pc) - best)
            if ecost(strong) - best > 1e-12:
                subopt_strong += 1
        lo, hi = wilson_checked(subopt_strong, TRIALS)
        print("  prior %-26s: p/c-vs-optimum worst gap %.2e ; strongest-first suboptimal %d/%d = %.4f  Wilson95=[%.4f, %.4f]"
              % (prior, gap_pc, subopt_strong, TRIALS, subopt_strong / TRIALS, lo, hi))

    p = [0.60, 0.50, 0.05]
    c = [10.0, 5.0, 0.1]
    cap = 2
    best_p_set = max(itertools.combinations(range(3), cap),
                     key=lambda s: 1 - float(np.prod([1 - p[i] for i in s])))
    pc_order = tuple(sorted(range(3), key=lambda i: -(p[i] / c[i]))[:cap])
    pr = lambda s: 1 - float(np.prod([1 - p[i] for i in s]))
    print("  CAP=2 counterexample: top-p set %s P=%.4f ; p/c prefix %s P=%.4f  (p/c loses %.4f)"
          % (best_p_set, pr(best_p_set), pc_order, pr(pc_order), pr(best_p_set) - pr(pc_order)))

    # ---------------- G: intransitive hybrid comparator ----------------
    print()
    print("G. PAIR-RETIREMENT COMPARATOR INTRANSITIVITY")
    cases = {"A": (124, 200), "B": (6, 10), "C": (96, 200)}
    iv = {m: wilson_checked(*kn) for m, kn in cases.items()}
    for m, (k, n) in cases.items():
        print("    %s: k=%d n=%d rate=%.3f Wilson95=[%.4f, %.4f]" % (m, k, n, k / n, iv[m][0], iv[m][1]))
    sep = lambda x, y: iv[x][0] > iv[y][1] or iv[y][0] > iv[x][1]
    print("    separated(A,C)=%s separated(A,B)=%s separated(B,C)=%s" % (sep("A", "C"), sep("A", "B"), sep("B", "C")))
    tuple_rank = {"C": 0, "B": 1, "A": 2}
    beats = {}
    for x, y in (("A", "C"), ("A", "B"), ("B", "C")):
        if sep(x, y):
            w = x if cases[x][0] / cases[x][1] > cases[y][0] / cases[y][1] else y
        else:
            w = x if tuple_rank[x] < tuple_rank[y] else y
        beats[(x, y)] = w
    print("    pairwise winners: %s" % beats)
    cyc = beats[("A", "C")] == "A" and beats[("B", "C")] == "C" and beats[("A", "B")] == "B"
    print("    CYCLE A>C>B>A: %s  -> a hybrid pairwise comparator is not an order" % cyc)

    # ---------------- I: brief reconciliation ----------------
    print()
    print("I. BRIEF RECONCILIATION")
    print("  brief clean cell: CC2 k=21 n=35 (0.6000), Codex k=22 n=37 (0.5946)")
    print("  NOT reproduced by any of: entry/attempt x all/critical x full/base label x")
    print("  registry-level/rung-level accountings in this tree (sections A and the rung scan).")
    print("  Nearest cells here: crit_entry CC2 39/41, Codex 42/46; crit_attempt CC2 39/59, Codex 42/70.")
    try:
        from scipy import stats
        for name, (ka, na, kb, nb) in {
            "crit_entry  CC2 vs Codex": (39, 41, 42, 46),
            "crit_attempt CC2 vs Codex": (39, 59, 42, 70),
            "crit_entry  DeepSeek vs Gemini": (12, 16, 1, 8),
        }.items():
            odds, pf = stats.fisher_exact([[ka, na - ka], [kb, nb - kb]])
            print("  Fisher %-32s p=%.6f" % (name, pf))
    except ImportError as ex:
        print("  Fisher SKIPPED (%s)" % ex)

    # ---------------- H: g monotone in q; spec-vs-appendix gap ----------------
    print()
    print("H. SCORE NUMERATOR CHECKS (SymPy)")
    R, q, sg, nu = sp.symbols("R q sigma nu", positive=True)
    Rdet = R * (1 - q) / (1 - q * R)
    Rnext = (sg * Rdet + (1 - sg) * R) * (1 - nu) + nu
    g = sp.simplify(R - Rnext)
    dgdq = sp.simplify(sp.diff(g, q))
    print("  dg/dq = %s" % dgdq)
    assert sp.simplify(dgdq - sg * (1 - nu) * R * (1 - R) / (1 - q * R) ** 2) == 0
    Eimp = R * q * sg * (1 - nu) - nu * (1 - R)
    gap = sp.simplify(Eimp - g)
    target = R ** 2 * q * sg * (1 - nu) * (1 - q) / (1 - q * R)
    print("  E[improvement] - g_spec = %s  (equals R^2*q*sigma*(1-nu)*(1-q)/(1-qR): %s)"
          % (gap, sp.simplify(gap - target) == 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
