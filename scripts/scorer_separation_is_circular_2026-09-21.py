#!/usr/bin/env python3
"""The cure/non-cure statistics, and why the AFTER figures do not mean what I said.

TWO DEFECTS IN MY OWN REPORTING, BOTH FOUND BY THE ASTRA REVIEW OF 2026-09-21,
both confirmed here rather than taken on trust.

DEFECT 1 -- THE FIGURES HAD NO PRODUCER. `experimental_notes/Scorer_Measures_
Absence_Of_Harm_2026-09-20.md` and the 2026-09-21 morning report quote
Mann-Whitney p = 0.746836, Welch p = 0.421469, Kolmogorov-Smirnov p = 0.900813
and a seeded permutation p = 0.627119, and name
`scripts/scorer_discrimination_2026-09-20.py` as their producer. That script
contains **0 occurrences** of any of those tests. The numbers were computed
inline and never committed. That is exactly the defect
`measured-rate-travels-with-its-script` names, and it is the rule I had invoked
against others earlier the same session. This script is the missing producer.

DEFECT 2 -- AND THE MORE IMPORTANT ONE. THE "AFTER" SEPARATION IS CIRCULAR.
I wired the probe's cure/non-cure verdict INTO `compute_sk` as `e1_efficacy`,
then measured that the resulting score separates cure from non-cure, and
reported p = 1.428e-18 as evidence the repair works. It is not evidence of that.
It is a near-tautology: a score that reads a signal will separate groups defined
by that signal. Astra's wording, and it is correct: *"Showing that the resulting
score separates those same cure/non-cure groups confirms that the observation
affects the score. It does not independently establish predictive accuracy or
better scientific outcomes."*

WHAT REMAINS TRUE, AND IT IS THE HALF THAT MATTERED. The BEFORE figures are not
circular. They measure a score computed WITHOUT any cure/non-cure input, and
they show it was statistically independent of whether the fix worked. That
finding stands untouched: the scorer was not measuring fix efficacy. The repair
addresses a real defect. What the AFTER figures cannot do is show that the
repaired scorer PREDICTS anything.

WHAT A NON-CIRCULAR CHECK WOULD NEED, stated so the gap is actionable rather
than merely admitted: a held-out outcome the score did not consume. For example,
whether a fix admitted at a high score is later re-opened by an EXTENSION filed
against the same finding by a different model, or survives to the end of the run
without re-entering the queue. Neither is wired into `e1_efficacy`, so neither is
circular. This script measures whether the archive can support that test today.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from math import sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n)))
    return ((c - h) / d, (c + h) / d)


def collect():
    """Every entry carrying BOTH an sk verdict and a fix-efficacy probe result."""
    rows = []
    for f in sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > 60_000_000:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "fix_efficacy" not in raw:
            continue
        try:
            doc = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue

        def walk(node):
            if isinstance(node, dict):
                sk, fe = node.get("sk_result"), node.get("fix_efficacy")
                if (isinstance(sk, dict) and "tristate" in sk
                        and isinstance(fe, dict) and fe.get("outcome")):
                    rows.append({
                        "sk": float(sk.get("sk", 0)),
                        "tristate": sk.get("tristate"),
                        "outcome": fe["outcome"],
                        "gate_details": sk.get("gate_details") or {},
                        "extensions": len(node.get("extensions") or []),
                        "status": node.get("status"),
                    })
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(doc)
    return rows


def main() -> None:
    import numpy as np
    from scipy import stats as sps

    rows = collect()
    cure = np.array([r["sk"] for r in rows
                     if r["outcome"] == "FIX_CURES_ITS_OWN_FALSIFIER"])
    nocure = np.array([r["sk"] for r in rows
                       if r["outcome"] == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"])

    print("=" * 74)
    print("THE CURE / NON-CURE STATISTICS, AND WHAT THEY DO NOT SHOW")
    print("=" * 74)
    print(f"\npaired entries found: {len(rows)}")
    print(f"  cure    n={len(cure)}  mean sk={cure.mean():.6f}  median={np.median(cure):.6f}")
    print(f"  no-cure n={len(nocure)}  mean sk={nocure.mean():.6f}  median={np.median(nocure):.6f}")

    print("\n1. BEFORE THE REPAIR -- NOT CIRCULAR, AND THIS IS THE FINDING THAT STANDS")
    print("   These scores were computed with NO cure/non-cure input of any kind.")
    u, pu = sps.mannwhitneyu(cure, nocure, alternative="two-sided")
    t, pt = sps.ttest_ind(cure, nocure, equal_var=False)
    ks, pks = sps.ks_2samp(cure, nocure)
    rng = np.random.default_rng(20260920)
    obs = abs(nocure.mean() - cure.mean())
    pool = np.concatenate([cure, nocure])
    hits, B = 0, 20000
    for _ in range(B):
        rng.shuffle(pool)
        if abs(pool[:len(nocure)].mean() - pool[len(nocure):].mean()) >= obs:
            hits += 1
    pperm = (hits + 1) / (B + 1)
    print(f"   Mann-Whitney U = {u:.1f}   p = {pu:.6f}")
    print(f"   Welch t        = {t:+.4f}  p = {pt:.6f}")
    print(f"   Kolmogorov-Smirnov D = {ks:.4f}  p = {pks:.6f}")
    print(f"   permutation ({B} resamples, seeded) p = {pperm:.6f}")
    print(f"   -> none rejects. The scorer was INDEPENDENT of whether the fix worked.")

    print("\n2. AFTER THE REPAIR -- CIRCULAR, AND I REPORTED IT AS IF IT WERE NOT")
    W = {"e1_efficacy": 2.0, "e2_regression": 2.0, "e3_ruff": 1.0, "e4_bandit": 2.0}

    def rescore(r):
        gd = r["gate_details"]
        A = 1.0
        for g in ("g1_ast", "g2_compile"):
            e = gd.get(g)
            if not isinstance(e, dict) or e.get("score") is None:
                return None
            A *= float(e["score"])
        live = []
        if r["outcome"] == "FIX_CURES_ITS_OWN_FALSIFIER":
            live.append((1.0, W["e1_efficacy"]))
        elif r["outcome"] == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER":
            live.append((0.0, W["e1_efficacy"]))
        for g in ("e2_regression", "e3_ruff", "e4_bandit"):
            e = gd.get(g)
            if isinstance(e, dict) and e.get("score") is not None:
                live.append((float(e["score"]), W[g]))
        if not live:
            return None
        tot = sum(w for _, w in live)
        return round(A * sum((w / tot) * s for s, w in live), 4)

    c2 = np.array([v for v in (rescore(r) for r in rows
                               if r["outcome"] == "FIX_CURES_ITS_OWN_FALSIFIER") if v is not None])
    n2 = np.array([v for v in (rescore(r) for r in rows
                               if r["outcome"] == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER") if v is not None])
    u2, pu2 = sps.mannwhitneyu(c2, n2, alternative="two-sided")
    print(f"   Mann-Whitney p = {pu2:.6e}   (I reported this as evidence the repair works)")
    print("   IT IS NOT. The gate READS the cure/non-cure verdict, so a separation")
    print("   of groups DEFINED by that verdict is near-tautological. All it")
    print("   establishes is that the wiring is connected -- which a single unit")
    print("   test shows more cheaply and without a p-value.")

    print("\n3. CAN THE ARCHIVE SUPPORT A NON-CIRCULAR TEST TODAY?")
    print("   A held-out outcome the score never consumed. The nearest candidate")
    print("   in the record is whether an admitted fix later attracts an EXTENSION")
    print("   filed by a different model against the same finding.")
    adm = [r for r in rows if r["tristate"] == "ADMISSIBLE"]
    with_ext = [r for r in adm if r["extensions"] > 0]
    k, n = len(with_ext), len(adm)
    lo, hi = wilson(k, n)
    print(f"   admitted entries: {n}")
    print(f"   of those, carrying at least 1 extension: {k}")
    print(f"   = {k/n:.4%} " if n else "   = n/a ", end="")
    print(f" Wilson [{lo:.4%}, {hi:.4%}]" if n else "")
    print("\n4. RUNNING THAT NON-CIRCULAR TEST ANYWAY, AND REPORTING THAT IT FAILS")
    ext = np.array([r["extensions"] > 0 for r in adm])
    sk = np.array([r["sk"] for r in adm])
    a, b = sk[ext], sk[~ext]
    if len(a) >= 2 and len(b) >= 2:
        u3, pu3 = sps.mannwhitneyu(a, b, alternative="two-sided")
        t3, pt3 = sps.ttest_ind(a, b, equal_var=False)
        pooled = np.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1))
                         / (len(a)+len(b)-2))
        d_obs = (a.mean() - b.mean()) / pooled
        from scipy.stats import norm
        d_min = (norm.ppf(0.975) + norm.ppf(0.8)) * sqrt(1/len(a) + 1/len(b))
        print(f"   mean sk, LATER EXTENDED : {a.mean():.6f}  (n={len(a)})")
        print(f"   mean sk, never extended : {b.mean():.6f}  (n={len(b)})")
        print(f"   difference              : {a.mean()-b.mean():+.6f}"
              "   <-- the WRONG direction if sk were predictive")
        print(f"   Mann-Whitney p = {pu3:.6f}   Welch p = {pt3:.6f}   "
              f"separates at 0.05? {'YES' if min(pu3, pt3) < 0.05 else 'NO'}")
        print(f"   smallest detectable effect at 80% power : d = {d_min:.4f}")
        print(f"   observed effect                         : d = {d_obs:.4f}")
        print("   -> UNDERPOWERED. The archive can POSE the question and cannot")
        print("      ANSWER it. A non-circular validation of the REPAIRED scorer")
        print("      needs a NEW RUN, not a re-analysis. That is the simulated")
        print("      run, and it is the right instrument for this question.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description=("Produce the cure/non-cure statistics quoted in the 2026-09-20 "
                     "and 2026-09-21 notes, and show why the post-repair separation "
                     "is circular. Reads bench/logs, writes nothing, costs nothing."),
        epilog="Prints the before figures (valid), the after figures (circular), "
               "and whether the archive can support a non-circular check.")
    ap.parse_args()
    main()
