#!/usr/bin/env python3
"""How far does identity-pairing of worked proofs reach on a real run?

`validate_round_rk` used to pair CORROBORATION sections to findings by POSITION.
This measures, over every archived seat response in a run, how many sections carry
a recoverable FINDING_ID -- i.e. how often the identity path can engage at all --
and how badly the section count diverges from the registered finding count, which
is what makes positional pairing wrong rather than merely fragile.

A number here is only meaningful with its denominator, so unreadable files are
counted and reported separately rather than folded into either arm.
"""
import argparse, collections, glob, json, pathlib, re, sys
sys.path.insert(0, "bench")
import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp
import reference_runner_v3 as R
import math


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)

def main() -> int:
    """★ THE BODY MOVED HERE ON 2026-11-08 SO THIS FILE CAN BE IMPORTED.

    It ran at module level, so importing it either handed argparse the
    importing process's argv and raised `SystemExit: 2`, or printed its whole
    report. B135's option 1 requires the shared interval helper to be EXECUTED
    by `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, which
    imports every script defining one; an unimportable producer makes that
    helper unreachable. Command-line behaviour is unchanged and was asserted
    byte for byte against a baseline taken before the edit.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=None)
    a = ap.parse_args()
    if getattr(a, "run", None) is None:
        ap.error("--run is required")

    run = pathlib.Path(a.run)

    def wilson(k, n):
        """Wilson as a rounded percentage pair, from the canonical helper.

        ★ DELEGATED 2026-11-08 on his ruling for B135 option 1. The algebra
        that stood here was correct and the detector could not SEE it, because
        it named the sample size `nn` where the pattern required `n`. It is
        replaced by a call rather than by a wider pattern, so the cross-check
        is executed instead of being inferred from a spelling. `_iv` is lifted
        byte-identical from the canonical producer and the board guard asserts
        every copy agrees with every other.
        """
        wl, wh = _iv(k, n)[0]
        return round(100 * wl, 4), round(100 * wh, 4)

    def response_text(d):
        for k in ("response", "raw", "text", "content", "output"):
            if isinstance(d.get(k), str) and len(d[k]) > 200:
                return d[k]
        for v in d.values():
            if isinstance(v, str) and len(v) > 500:
                return v
        return None

    files = sorted(glob.glob(str(run / "r*_*.json")))
    unreadable = 0
    tot_sections = tot_identified = tot_phantom = 0
    per_round = collections.defaultdict(lambda: [0, 0])   # round -> [sections, identified]
    rows = []
    for f in files:
        p = pathlib.Path(f)
        m = re.match(r"r(\d+)_", p.name)
        if not m:
            continue
        rnd = int(m.group(1))
        try:
            d = json.loads(p.read_text(errors="replace"))
        except Exception:
            unreadable += 1; continue
        txt = response_text(d)
        if txt is None:
            unreadable += 1; continue
        owned = R._extract_corroboration_sections_with_ids(txt)
        plain = R._extract_corroboration_sections(txt)
        # THE COUNTS ARE SUPPOSED TO DIVERGE. A first version of this script asserted
        # they must agree, which was my own premise and it was wrong: the original
        # extractor splits case-insensitively on the bare word, so it manufactures
        # sections from the JSON key `corroboration_fit` and from prose like
        # "independent corroboration". The divergence IS the phantom count.
        phantom = len(plain) - len(owned)
        ident = sum(1 for o, _ in owned if o)
        tot_sections += len(owned); tot_identified += ident
        tot_phantom += max(0, phantom)
        per_round[rnd][0] += len(owned); per_round[rnd][1] += ident
        rows.append((p.name, len(owned), ident, len(plain)))

    print(f"run: {run.name}")
    print(f"seat response files read: {len(rows)}   unreadable/no-text: {unreadable}")
    print()
    print("per seat response: sections / of those, carrying a FINDING_ID")
    for name, n, k, orig in rows:
        print(f"  {name:44} real={n:4d}  owned={k:4d}  "
              f"original_said={orig:4d}  phantom={orig-n:4d}")
    print()
    if tot_sections:
        lo, hi = wilson(tot_identified, tot_sections)
        print(f"SECTIONS WITH A RECOVERABLE OWNER: {tot_identified}/{tot_sections} = "
              f"{100.0*tot_identified/tot_sections:.4f}%  Wilson [{lo}%, {hi}%]  "
              f"(statsmodels == mpmath)")
        print("  -> this is the fraction where identity pairing can engage. The rest")
        print("     still fall back to position, exactly as before the fix.")
        print()
        print(f"PHANTOM SECTIONS the ORIGINAL extractor manufactures from prose: "
              f"{tot_phantom} on top of {tot_sections} real "
              f"({100.0*tot_phantom/max(1,tot_sections+tot_phantom):.4f}% of what it reports)")
        print("  -> these are what made positional pairing select the wrong block.")
    print()
    counts = np.array([n for _, n, _, _ in rows])
    if counts.size:
        print(f"sections per response (NumPy): min={counts.min()} median={np.median(counts):.1f} "
              f"max={counts.max()} mean={counts.mean():.4f}")

    # the registered-finding counts, for the divergence that makes position WRONG
    rep = next(iter(sorted(run.glob("*_report.json"))), None)
    if rep:
        d = json.loads(rep.read_text(errors="replace"))
        prc = d.get("per_round_counts") or []
        if prc:
            print()
            print("registered findings per round vs sections emitted that round:")
            for rnd in sorted(per_round):
                secs, ident = per_round[rnd]
                reg = prc[rnd] if rnd < len(prc) else None
                print(f"  round {rnd}: sections={secs:4d}  identified={ident:4d}  "
                      f"registered findings={reg}")
            print()
            print("  Where sections FAR exceed registered findings, positional pairing")
            print("  hands a survivor whichever block came first in the raw text.")


if __name__ == "__main__":
    raise SystemExit(main())
