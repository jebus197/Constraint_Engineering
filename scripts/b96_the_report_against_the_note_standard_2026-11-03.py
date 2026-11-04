#!/usr/bin/env python3
"""B96's figures, which had NO producer until this file existed.

THE DEBT THIS PAYS, AND IT IS MINE. B96 was written on 2026-11-03 quoting 15
figures -- the spoken report's finding counts, the share of them sitting in
content the written copy exempts, and 4 interval pairs -- every one of which was
computed in an ad-hoc shell heredoc and never committed. That is a direct breach
of `measured-rate-travels-with-its-script`, in an entry whose own subject is the
project's rules reaching the documents it produces, and written while citing that
same rule against other work.

FOUND BY COMPLETING A VERIFICATION I HAD SAMPLED. Commit 01b6e408 claimed "19 of
24 quoted figures reproduce exactly". That list of 24 was hand-picked by me, and
the entries B91 to B96 quote **64** figures, so the check covered 0.375000 of
them, Wilson 95% [0.266660, 0.497496]. Completing it gives 39 of 64 reproduced,
0.609375, Wilson [0.486919, 0.719444] -- and ALL 15 of the unreproduced ones in
B96 are unreproduced for the same reason: no producer existed.

WHAT IS MEASURED HERE. The 2 rendered copies of the morning report, as the
generator writes them, under the note linter's own `blocking()` predicate -- the
same predicate the note standard's guard uses, so a count printed here is the
count that guard would produce. The markdown copy's verbatim regions are read out
of the file rather than assumed, and a spoken finding is attributed to exempt
content only if its sentence appears inside one of them.

THE FIGURES MOVE WITH THE DOCUMENT AND THAT IS SAID PLAINLY, which is the lesson
from the bare-clock producer earlier the same night: these are counts over a
GENERATED artefact that is rewritten whenever the decision list changes. A later
run reporting different numbers is not a contradiction. Quote the pair WITH the
total, as 2 of 15, or the figure cannot be checked.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MD = REPO / "experimental_notes" / "Morning_Report_2026-11-03_GENERATED.md"
TX = (pathlib.Path.home() / "Desktop" / "CDSFL_tts"
      / "Morning_Report_2026-11-03_GENERATED.txt")
LINT = REPO / "scripts" / "note_vagueness_lint.py"


def _lint():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_nvl_b96", LINT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_nvl_b96"] = mod
    spec.loader.exec_module(mod)
    return mod


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, on 2 INDEPENDENT implementations each.

    PROPAGATED 2026-11-03 from the one producer that already had both routes.
    An audit of this session's producers by STEM-IMPORT COUNT passed this file,
    and the count was a proxy: the project had already measured that `scipy` and
    `statsmodels` resolve to the identical verifier, so 2 library names can buy
    0 cross-checks. The predicate that matters is ROUTES PER QUANTITY -- Wilson
    from statsmodels against Wilson written out, and Clopper-Pearson from
    scipy's beta quantile against mpmath's regularized incomplete beta by
    bisection. 2 libraries computing 2 DIFFERENT intervals is not a cross-check
    of either one.

    The 3rd return value is the LARGER of the 2 disagreements, so a drift in
    either quantity surfaces in the single number the caller already prints.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    # second Wilson, written out, to catch a library disagreement
    import math
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

        def _f(x):
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
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def main() -> int:
    argparse.ArgumentParser(
        description=("Produce B96's figures: the spoken and written morning "
                     "report against the note standard.")).parse_args()
    nvl = _lint()
    print("=" * 78)
    print("B96's FIGURES, WHICH HAD NO PRODUCER UNTIL THIS FILE")
    print("=" * 78)

    missing = [p for p in (MD, TX) if not p.is_file()]
    if missing:
        print(f"\n  the report has not been generated here: {missing}")
        print("  run scripts/morning_report_build_2026-10-12.py --write first.")
        return 1

    print("\n1. VERBATIM REGIONS IN EACH RENDERING, read rather than assumed.")
    md_txt = MD.read_text(errors="replace")
    spans = [m.group(1) for m in re.finditer(
        r"<!-- verbatim-begin:.*?-->(.*?)<!-- verbatim-end -->", md_txt, re.S)]
    exempt = "\n".join(spans)
    tx_txt = TX.read_text(errors="replace")
    print(f"   written copy : {md_txt.count('verbatim-begin')} begin, "
          f"{md_txt.count('verbatim-end')} end, {len(spans)} closed region(s)")
    print(f"   spoken copy  : {tx_txt.count('verbatim-begin')} begin, "
          f"{tx_txt.count('verbatim-end')} end")
    if md_txt.count("verbatim-begin") != md_txt.count("verbatim-end"):
        print("   ★ UNBALANCED in the written copy, which the note standard")
        print("     calls malformed. That was a live defect on 2026-11-03.")

    print("\n2. BLOCKING FINDINGS, under the linter's own predicate.")
    rows = {}
    for p in (MD, TX):
        b = nvl.blocking(p)
        sp = [x for x in b if "SPELLED NUMBER" in x[1]]
        rows[p.name] = (b, sp)
        print(f"   {p.name[:46]:46s} blocking {len(b):3d}, spelled-number {len(sp):3d}")

    print("\n3. HOW MANY SPOKEN FINDINGS THE WRITTEN COPY EXEMPTS.")
    _b, sp = rows[TX.name]
    in_ex = [x for x in sp if x[3].strip()[:46] and x[3].strip()[:46] in exempt]
    k, n = len(in_ex), len(sp)
    print(f"   spoken spelled-number findings      : {n}")
    print(f"   in content the written copy exempts : {k}")
    print(f"   GENUINELY OWED                      : {n - k}")
    if n:
        (wl, wh), (cl, ch), diff = _iv(k, n)
        print(f"     {k} of {n}, {k / n:.6f}")
        print(f"     Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"     Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-impl |diff| {diff:.1e})")
    print("   => the asymmetry explains only this share. The rest are genuine")
    print("      Rule 27 violations in prose the spoken renderer writes itself,")
    print("      which the written renderer never emits.")

    print("\n4. THE FIGURES MOVE WITH THE DOCUMENT, SAID PLAINLY.")
    print(f"   written copy: {len(md_txt.splitlines())} lines against Rule 10's 300")
    print(f"   spoken copy : {len(tx_txt.splitlines())} lines against 400")
    print("   Both are GENERATED and are rewritten whenever the decision list")
    print("   changes, so these counts move together. A later run reporting")
    print("   different numbers is not a contradiction: quote the pair WITH its")
    print("   total, as 2 of 15, or the figure cannot be checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
