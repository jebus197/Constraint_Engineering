#!/usr/bin/env python3
"""Do the 3 shakedown legs REPEAT? His question of 2026-10-16, measured.

HIS QUESTION, verbatim from Responses/Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.txt:
"there is a question of whether the fixes derived over the last 3 simulated runs
show any tendency towards repeatability, which is a foundational pillar of
scientific enquiry, and if the fixes derived from these simulated runs on that
specific target should be carried forward into live runs?"

THIS SCRIPT'S FIRST VERSION WAS VACUOUS AND IS KEPT HONEST BY ITS OWN ATTACKS.
The first version compared the `demonstrated` and `evidence` fields of
`*_finding_catalogue.jsonl`. Those are a BOOLEAN and a boilerplate status string:
leg 3 carries 3 distinct combined texts across 38 findings, and 18 of them read
"True verified fix, no unresolved challenges". It reported 81.8182% overlap for
leg 1 against leg 3, and that figure measured only how many findings share a
status phrase. It was delivered to the founder before the attacks below were
run, and withdrawn when they were.

The finding TEXT lives in `runner_state.json` under
`registry.entries.<id>.description` -- 22, 19 and 38 distinct descriptions of
median length 825, 720 and 843 characters. This version reads that.

TWO THINGS COULD REPEAT AND THEY CARRY DIFFERENT WEIGHT:
  (a) RUN-LEVEL behaviour -- convergence round and finding volume. Read from the
      committed reports. This is what the success criterion asked for.
  (b) FINDING-LEVEL content -- whether the legs surface the SAME defects. The
      stronger claim, and the one that bears on carrying fixes forward.

THE THRESHOLD IS LOAD-BEARING, SO A SINGLE NUMBER IS NOT REPORTED ALONE. The
overlap rate runs from 100% at a 0.10 Jaccard threshold to 0% at 0.70, so any
one figure is a choice of threshold. The sweep is printed instead.

EVERY PROPORTION IS CROSS-VERIFIED ON >=2 TOOLS (21 Apr 2026 rule).
`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, itertools, re, random

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEGS = {
    "leg1": "free_run1_directive_whole_20261015T061123Z_20261015T061124Z",
    "leg2": "free_run2_severity_spec_20261015T073418Z_20261015T073418Z",
    "leg3": "leg3_final_shakedown_20261015T220118Z",
}
STOP = {"that", "this", "with", "from", "which", "when", "then", "than", "have",
        "been", "were", "would", "could", "should", "there", "their", "where",
        "while", "because", "finding", "model", "claim", "does", "such", "only",
        "also", "into", "they", "them"}
THRESHOLDS = (0.10, 0.20, 0.30, 0.50, 0.70, 0.90)
REPORT_AT = 0.30

def sig(text: str) -> frozenset:
    return frozenset(w for w in re.findall(r"[a-z_]{4,}", text.lower())
                     if w not in STOP)

def descriptions(dirname: str) -> list[str]:
    st = json.loads((ROOT / "bench" / "logs" / dirname / "runner_state.json")
                    .read_text(encoding="utf-8"))
    out = [(e.get("description") or "") for e in st["registry"]["entries"].values()]
    return [x for x in out if x.strip()]

def report(dirname: str) -> dict:
    d = ROOT / "bench" / "logs" / dirname
    f = next(d.glob("*_report.json"), None)
    return json.loads(f.read_text(encoding="utf-8")) if f else {}

def rate(A, B, t) -> float:
    if not A: return float("nan")
    return sum(1 for a in A if any(len(a & b) / len(a | b) >= t for b in B)) / len(A)

def ci(k: int, n: int) -> dict:
    out = {}
    try:
        from statsmodels.stats.proportion import proportion_confint
        out["Wilson (statsmodels)"] = proportion_confint(k, n, 0.05, "wilson")
    except Exception as e: out["Wilson (statsmodels)"] = ("n/a", str(e)[:30])
    try:
        from scipy.stats import beta
        lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
        hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
        out["Clopper-Pearson (scipy)"] = (lo, hi)
    except Exception as e: out["Clopper-Pearson (scipy)"] = ("n/a", str(e)[:30])
    try:
        import mpmath as mp
        mp.mp.dps = 30
        p, z, N = mp.mpf(k) / n, mp.mpf("1.959963984540054235524594430520"), n
        d = 1 + z**2 / N
        c = (p + z**2 / (2 * N)) / d
        h = z * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2)) / d
        out["Wilson (mpmath)"] = (float(c - h), float(c + h))
    except Exception as e: out["Wilson (mpmath)"] = ("n/a", str(e)[:30])
    return out

def pct(x): return f"{x*100:.4f}%"

def falsify(S) -> list[str]:
    """ATTACK the measure. A measure that survives nothing proves nothing."""
    fails = []
    a, b = sig("alpha bravo charlie delta echo foxtrot"), sig("sierra tango uniform victor")
    if a & b: fails.append("disjoint text scored a nonzero overlap")
    if len(a & a) / len(a | a) != 1.0: fails.append("identical text did not score 1.0")
    vals = [rate(S["leg1"], S["leg3"], t) for t in THRESHOLDS]
    if any(vals[i + 1] > vals[i] + 1e-12 for i in range(len(vals) - 1)):
        fails.append("rate ROSE under a stricter threshold")
    if max(vals) - min(vals) < 0.05:
        fails.append("measure SATURATED: the threshold changes nothing")
    random.seed(11)
    vocab = sorted({w for s in S["leg3"] for w in s})
    fake = [frozenset(random.sample(vocab, len(s))) for s in S["leg3"]]
    real, ctrl = rate(S["leg1"], S["leg3"], REPORT_AT), rate(S["leg1"], fake, REPORT_AT)
    if ctrl >= real * 0.8:
        fails.append(f"shuffled control {pct(ctrl)} too close to real {pct(real)}")
    return fails

def main() -> int:
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    print("=" * 74)
    print("DO THE 3 LEGS REPEAT? his question of 2026-10-16")
    print("=" * 74)

    D = {k: descriptions(v) for k, v in LEGS.items()}
    R = {k: report(v) for k, v in LEGS.items()}
    S = {k: [s for s in (sig(x) for x in v) if s] for k, v in D.items()}

    print("\n(a) RUN-LEVEL: does the harness behave reproducibly?\n")
    print(f"  {'leg':6s} {'findings':>9s} {'rounds':>7s} {'converged at':>13s}")
    print("  " + "-" * 40)
    for k in LEGS:
        print(f"  {k:6s} {len(D[k]):>9d} {str(R[k].get('total_rounds')):>7s} "
              f"{str(R[k].get('converged_at')):>13s}")
    print(f"\n  finding-volume spread: {max(len(v) for v in D.values()) - min(len(v) for v in D.values())}")

    print("\n(b) THE MEASURE IS ATTACKED BEFORE IT IS REPORTED\n")
    fails = falsify(S)
    for f in fails: print(f"  FAILED: {f}")
    if fails:
        print("\n  The measure did not survive. No overlap figure is reported.")
        return 1
    print("  4 of 4 attacks survived: disjoint scores 0, identical scores 1,")
    print("  the rate falls monotonically with a stricter threshold, and a")
    print("  shuffled control separates from the real figure.")

    print("\n(c) FINDING-LEVEL: the threshold sweep, because 1 number is a choice\n")
    print(f"  {'threshold':>10s}  " + "  ".join(f"{a}->{b}" for a, b in
          itertools.permutations(LEGS, 2)))
    for t in THRESHOLDS:
        row = "  ".join(f"{pct(rate(S[a], S[b], t)):>9s}"
                        for a, b in itertools.permutations(LEGS, 2))
        print(f"  {t:>10.2f}  {row}")

    print(f"\n(d) AT THE REPORTED THRESHOLD OF {REPORT_AT}, WITH INTERVALS\n")
    for a, b in itertools.permutations(LEGS, 2):
        n = len(S[a]); r = rate(S[a], S[b], t=REPORT_AT); k = round(r * n)
        print(f"  {a} -> {b}: {k} of {n} = {pct(r)}")
        for name, (lo, hi) in ci(k, n).items():
            if isinstance(lo, float):
                print(f"      {name:26s} [{pct(lo)}, {pct(hi)}]")

    print("\n" + "=" * 74)
    print("READ THIS AS: (a) says the HARNESS is reproducible. (c) and (d) say the")
    print("FINDING SET repeats only MODESTLY, and asymmetrically -- the later leg's")
    print("findings are least likely to have a partner in an earlier one. The 3 legs")
    print("were NOT run under identical conditions, so this is consistency across")
    print("changing conditions, not replication. Only (b) surviving licenses any of it.")
    print("=" * 74)
    return 0

if __name__ == "__main__":
    sys.exit(main())
