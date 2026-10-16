#!/usr/bin/env python3
"""Do the 3 shakedown legs REPEAT? His question of 2026-10-16, measured.

HIS QUESTION, verbatim from Responses/Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.txt:
"there is a question of whether the fixes derived over the last 3 simulated runs
show any tendency towards repeatability, which is a foundational pillar of
scientific enquiry, and if the fixes derived from these simulated runs on that
specific target should be carried forward into live runs?"

WHAT REPEATABILITY CAN AND CANNOT MEAN HERE. The 3 legs ran the same target with
the same stand-in seats. Two DIFFERENT things could repeat and they carry
different weight:

  (a) RUN-LEVEL behaviour -- convergence round, gamma, finding volume. If these
      agree across legs the HARNESS is behaving reproducibly. This is measurable
      from the committed reports and is what the success criterion asked for.

  (b) FINDING-LEVEL content -- whether the legs surface the SAME defects. This is
      the stronger claim and the one that bears on carrying fixes forward.

This script measures both and reports them separately, because (a) holding while
(b) fails would mean a reproducible harness producing non-reproducible findings,
which is the case that matters for his question.

EVERY PROPORTION IS CROSS-VERIFIED ON >=2 TOOLS (21 Apr 2026 rule).
`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, collections, itertools, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEGS = {
    "leg1 (directive whole)": "free_run1_directive_whole_20261015T061123Z_20261015T061124Z",
    "leg2 (severity deciding)": "free_run2_severity_spec_20261015T073418Z_20261015T073418Z",
    "leg3 (final shakedown)": "leg3_final_shakedown_20261015T220118Z",
}

def load(dirname):
    d = ROOT / "bench" / "logs" / dirname
    cat = next(d.glob("*_finding_catalogue.jsonl"), None)
    rep = next(d.glob("*_report.json"), None)
    findings, report = [], {}
    if cat:
        for line in cat.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try: findings.append(json.loads(line))
                except json.JSONDecodeError: pass
    if rep:
        try: report = json.loads(rep.read_text(encoding="utf-8"))
        except json.JSONDecodeError: pass
    return findings, report

def ci_two_tools(k, n):
    """Wilson and Clopper-Pearson from 2 independent libraries."""
    out = {}
    try:
        from statsmodels.stats.proportion import proportion_confint
        out["wilson_statsmodels"] = proportion_confint(k, n, 0.05, "wilson")
    except Exception as e:
        out["wilson_statsmodels"] = ("unavailable", str(e)[:40])
    try:
        from scipy.stats import beta
        lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
        hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
        out["clopper_scipy"] = (lo, hi)
    except Exception as e:
        out["clopper_scipy"] = ("unavailable", str(e)[:40])
    try:
        import mpmath as mp
        mp.mp.dps = 30
        p = mp.mpf(k) / n
        z = mp.mpf("1.959963984540054235524594430520")
        d = 1 + z**2 / n
        c = (p + z**2 / (2 * n)) / d
        h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
        out["wilson_mpmath"] = (float(c - h), float(c + h))
    except Exception as e:
        out["wilson_mpmath"] = ("unavailable", str(e)[:40])
    return out

def pct(x): return f"{x*100:.4f}%"

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()

    print("=" * 74)
    print("DO THE 3 LEGS REPEAT? his question of 2026-10-16")
    print("=" * 74)

    data = {}
    for label, d in LEGS.items():
        f, r = load(d)
        data[label] = (f, r)
        if not f:
            print(f"  {label}: NO CATALOGUE FOUND at bench/logs/{d}")

    print("\n(a) RUN-LEVEL: does the harness behave reproducibly?\n")
    hdr = f"  {'leg':26s} {'findings':>9s} {'rounds':>7s} {'converged':>10s}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    rounds, counts = [], []
    for label, (f, r) in data.items():
        n = len(f)
        rd = r.get("total_rounds") or r.get("rounds_run")
        cv = r.get("converged_at")
        if rd is None:
            rd = len({x.get("round") for x in f if x.get("round") is not None}) or None
        counts.append(n)
        if cv is not None: rounds.append(cv)
        print(f"  {label:26s} {n:>9d} {str(rd):>7s} {str(cv):>10s}")

    if counts:
        spread = max(counts) - min(counts)
        print(f"\n  finding-volume spread across legs: {spread} "
              f"(min {min(counts)}, max {max(counts)})")

    print("\n(b) FINDING-LEVEL: do the legs surface the SAME defects?\n")
    print("  BOUNDARY STATED FIRST. The catalogue carries no defect-identity field.")
    print("  `mechanism` is a PIPELINE label (e.g. verified_flag), `canonical_id` is")
    print("  per-run, and `severity` is a number. So \"did the same defect recur\"")
    print("  cannot be read directly from the record. What CAN be measured is the")
    print("  overlap of finding TEXT, which is an UPPER BOUND on defect recurrence:")
    print("  shared wording may describe one defect or merely one vocabulary.\n")

    def sig(x):
        t = " ".join(str(x.get(f) or "") for f in ("demonstrated", "evidence"))
        toks = re.findall(r"[a-z_]{4,}", t.lower())
        stop = {"that", "this", "with", "from", "which", "when", "then", "than",
                "have", "been", "were", "would", "could", "should", "there",
                "their", "where", "while", "because", "finding", "model"}
        return frozenset(w for w in toks if w not in stop)

    sigs = {k: [sig(x) for x in v[0]] for k, v in data.items()}
    labels = list(sigs)

    def best_overlap(a, b, thresh=0.30):
        """Count findings in `a` with a >=thresh Jaccard partner in `b`."""
        hits = 0
        for sa in a:
            if not sa: continue
            for sb in b:
                if not sb: continue
                j = len(sa & sb) / len(sa | sb)
                if j >= thresh:
                    hits += 1
                    break
        return hits

    print("  pairwise: findings in A with a >=30% token-overlap partner in B")
    for a, b in itertools.combinations(labels, 2):
        na, nb = len(sigs[a]), len(sigs[b])
        hab = best_overlap(sigs[a], sigs[b])
        print(f"    {a.split()[0]:5s} -> {b.split()[0]:5s}: {hab} of {na} = {pct(hab/na) if na else 'n/a'}")
        for name, (lo, hi) in ci_two_tools(hab, na).items():
            if isinstance(lo, float):
                print(f"       {name:20s} [{pct(lo)}, {pct(hi)}]")
        hba = best_overlap(sigs[b], sigs[a])
        print(f"    {b.split()[0]:5s} -> {a.split()[0]:5s}: {hba} of {nb} = {pct(hba/nb) if nb else 'n/a'}")

    print("\n" + "=" * 74)
    print("READ THIS AS: (a) is the harness reproducible, (b) is the FINDING SET")
    print("reproducible. They are different claims and only (b) licenses carrying")
    print("a fix forward on the grounds that the defect recurs.")
    print("=" * 74)
    return 0

if __name__ == "__main__":
    sys.exit(main())
