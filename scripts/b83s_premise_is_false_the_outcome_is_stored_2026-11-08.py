"""B83's premise is FALSE: the discrimination outcome IS stored. MEASURED.

HIS RULING, 2026-11-08: I accept your recommendation. The recommendation was to
write the discrimination control's outcome onto the registry entry at the point
it is computed.

IT WAS ALREADY WRITTEN, AND HAS BEEN SINCE 2026-09-01. `git log -S` puts
``entry["discrimination"] = rec`` in commit ce08914c, dated 2026-09-01 -- 2
months BEFORE the entry claiming nothing wrote it. The entry's own observation
was accurate about the wrong name: it measured a field called
``discrimination_control``, which 0 of 30 entries carry because NOTHING HAS EVER
WRITTEN A FIELD OF THAT NAME. The field that exists is ``discrimination``, and
it carries the full record -- outcome, detail, both shas, both verdicts,
intercepted, deterministic and round.

SO THE DEFECT WAS IN MY INSTRUMENT, NOT IN THE RUNNER. This is the
store-key-is-not-an-identifier failure, where a lookup under a name the store
does not use returns nothing and the miss is then reported as a finding. It has
now happened 3 times in 1 day: twice in this session's own ticket lookups
(``task:B102`` against the stored ``B102``) and once here, where it produced an
entry, a recommendation and a request for his ruling on work that did not need
doing.

WHAT IS NOT CLAIMED. That the control is working well. 22 of 30 entries carry an
outcome and 8 do not, and of the 22 the dominant outcome is
INDETERMINATE_NOT_INTERCEPTED -- which is the substantive question the entry
raised and which this file does NOT answer. The entry's second half stands: 2 of
319 refutations may be low because findings are sound or low because falsifiers
are not discriminating. That question is now ANSWERABLE from the archive,
because the field is there to compute over, which is precisely what the entry
said persistence would buy.

WHAT THIS FILE THEREFORE ESTABLISHES, narrowly: the persistence half of B83 is
already satisfied, so no field needs adding, and the entry's premise is
withdrawn rather than built.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

#: The run the entry itself measured, named so the figure is reproducible.
RUN = REPO / "bench/logs/study_run1b_rerun_20261102T033919Z_20261102T033920Z"

#: The name the entry looked for, and the name the runner actually writes.
CLAIMED_FIELD = "discrimination_control"
ACTUAL_FIELD = "discrimination"


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


def entries(run: pathlib.Path = RUN) -> dict:
    """The run's stored registry entries, by canonical id."""
    state = run / "runner_state.json"
    if not state.is_file():
        return {}
    return json.loads(state.read_text()).get("registry", {}).get("entries", {})


def survey(run: pathlib.Path = RUN):
    """(n, carrying_actual, carrying_claimed, outcome_tally)."""
    ents = entries(run)
    carrying = sum(
        1 for e in ents.values()
        if isinstance(e.get(ACTUAL_FIELD), dict)
        and e[ACTUAL_FIELD].get("outcome"))
    claimed = sum(1 for e in ents.values() if CLAIMED_FIELD in e)
    tally = collections.Counter(
        e[ACTUAL_FIELD]["outcome"] for e in ents.values()
        if isinstance(e.get(ACTUAL_FIELD), dict)
        and e[ACTUAL_FIELD].get("outcome"))
    return len(ents), carrying, claimed, tally


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()

    if not RUN.is_dir():
        print(f"REFUSED: {RUN} is not in this checkout, so the entry's own "
              f"figure cannot be reproduced and nothing is concluded.")
        return 1

    n, carrying, claimed, tally = survey()
    print(f"the run the entry measured: {RUN.name}")
    print(f"  stored registry entries                        : {n}")
    print(f"  carrying a NON-EMPTY `{ACTUAL_FIELD}` outcome   : {carrying}")
    print(f"  carrying any `{CLAIMED_FIELD}` field  : {claimed}")

    if n:
        (wl, wh), (cl, ch), diff = _iv(carrying, n)
        print(f"\n  stored: {carrying} of {n} = {carrying / n:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
        print(f"    the 2 routes of each agree to {diff:.2e}")

    print(f"\n  outcomes actually stored:")
    for k, v in tally.most_common():
        print(f"    {v:3d}  {k}")

    print()
    if claimed == 0 and carrying > 0:
        print(f"  B83's PREMISE IS WITHDRAWN. The entry reported that the "
              f"stored `{CLAIMED_FIELD}` field read empty for all {n} entries, "
              f"and that is true -- because nothing has ever written a field of "
              f"that name. The outcome is stored under `{ACTUAL_FIELD}` on "
              f"{carrying} of {n}, and has been written since 2026-09-01.")
        print(f"  NO FIELD NEEDS ADDING. The persistence half of the "
              f"recommendation he accepted was already satisfied when he ruled.")
    elif carrying == 0:
        print(f"  THE PREMISE STANDS: 0 of {n} entries carry an outcome under "
              f"either name, so the control's output is genuinely not persisted.")
    else:
        print(f"  MIXED: both fields are present, which means 2 writers "
              f"disagree about the name. That is worse than either case and "
              f"needs resolving before anything reads it.")

    print(f"\n  WHAT REMAINS OPEN, and it is the entry's substantive half: the "
          f"dominant stored outcome is INDETERMINATE_NOT_INTERCEPTED, so "
          f"whether 2 of 319 refutations is low because findings are sound or "
          f"low because falsifiers do not discriminate is now COMPUTABLE from "
          f"the archive and is not computed here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
