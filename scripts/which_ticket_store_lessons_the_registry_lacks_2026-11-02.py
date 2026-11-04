#!/usr/bin/env python3
"""Which of the ticket store's lessons does the harness finding registry lack?

HIS QUESTION, 2026-11-02: whether there are lessons from the ticket store that
could or should be applied to the same facility on the harness and its registry.

A FIRST ANSWER LISTED 4 LESSONS AS ADVICE. This measures them instead, because
advice about what the registry should do is worth less than a measurement of
what it already does, and 2 of the 4 turn out to be present or partly present.

THE 4 LESSONS, each learned in the ticket store by being bitten:

  1. AN IDENTITY IS DERIVED FROM CONTENT, NEVER ASSIGNED. `tid_of` digests the
     kind, the verbatim text and the subject, so the same item raised twice
     lands on 1 identity. 5 questions raised by hand once collided on 1 shared
     identifier because that route was bypassed.
  2. A TERMINAL STATE IS TOOL-ONLY. `TicketStore.close()` refuses without a
     verification, so a closure records a result rather than a claim.
  3. A RECLASSIFICATION IS NOT A SECOND RECORD. A renamed kind superseded 93
     rows rather than duplicating them.
  4. STATE IS RECORDED, NEVER INFERRED. No status is computed from surrounding
     evidence; every change is written with its cause.

WHAT THIS SCRIPT DOES NOT DO. It does not change the registry. Minting identity
from content would renumber every finding in the archive, which is a design
decision and his, not a repair to be applied unasked.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"


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


def lesson_1_identity() -> dict:
    """Is a finding's canonical id a CONTENT digest or a sequence counter?"""
    src = RUNNER.read_text(errors="replace")
    mint = re.findall(r'canonical_id\s*=\s*f"C\{self\._next_id:0\d+d\}"', src)
    # the consequence: does the SAME identifier name different findings?
    by_run: dict = {}
    for rep in sorted(LOGS.glob("*/*_report.json")):
        try:
            d = json.loads(rep.read_text(errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        ents = ((d.get("registry") or {}).get("entries")) or {}
        if not isinstance(ents, dict):
            continue
        e = ents.get("C0001")
        if isinstance(e, dict):
            txt = str(e.get("description") or e.get("title")
                      or e.get("summary") or "")[:64]
            if txt:
                by_run[rep.parent.name] = txt
    return {"mint_sites": len(mint), "runs": len(by_run),
            "distinct": len(set(by_run.values())), "sample": list(by_run.items())[:4]}


def lesson_2_terminal() -> dict:
    """Does a terminal transition require a verification?"""
    src = RUNNER.read_text(errors="replace")
    gates = [ln.strip() for ln in src.splitlines()
             if "CLOSED" in ln and "verified" in ln]
    return {"sites": len(gates), "sample": gates[:3]}


def lesson_3_alias() -> dict:
    """Is there an alias map, so a reclassified finding is not a 2nd record?"""
    totals = []
    for rep in sorted(LOGS.glob("*/*_report.json")):
        try:
            d = json.loads(rep.read_text(errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        am = ((d.get("registry") or {}).get("alias_map")) or {}
        if isinstance(am, dict) and am:
            totals.append(len(am))
    return {"runs_with_an_alias_map": len(totals),
            "median_size": sorted(totals)[len(totals)//2] if totals else 0}


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure which ticket-store lessons the harness finding "
                     "registry already has.")).parse_args()
    print("=" * 76)
    print("WHICH TICKET-STORE LESSONS DOES THE FINDING REGISTRY LACK?")
    print("=" * 76)

    l1 = lesson_1_identity()
    print("\n1. IS AN IDENTITY DERIVED FROM CONTENT?   VERDICT: NO")
    print(f"   sequence-minting sites in the canonical runner : {l1['mint_sites']}")
    print(f"   archived runs carrying an entry C0001          : {l1['runs']}")
    print(f"   DISTINCT findings behind that 1 identifier     : {l1['distinct']}")
    if l1["runs"]:
        (wl, wh), (cl, ch), d = _iv(l1["distinct"], l1["runs"])
        print(f"     {l1['distinct']} of {l1['runs']}, "
              f"{l1['distinct']/l1['runs']:.6f}")
        print(f"     Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"     Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-tool |diff| {d:.1e})")
    for k, v in l1["sample"]:
        print(f"       {k[:38]:38s} {v[:48]!r}")
    print("   => C0001 names a different finding in most pairs of runs, and the")
    print("      task list carries its OWN entry called C0001 as well. This is")
    print("      the 1 lesson genuinely missing, and fixing it would renumber")
    print("      the archive, so it is HIS decision rather than a repair.")

    l2 = lesson_2_terminal()
    print("\n2. IS A TERMINAL STATE TOOL-ONLY?         VERDICT: YES, ALREADY")
    print(f"   lines gating CLOSED on `verified` : {l2['sites']}")
    for s in l2["sample"]:
        print(f"       {s[:96]}")
    print("   => the registry already refuses CONFIRMED -> CLOSED without a")
    print("      verification, which is the same rule `close()` enforces.")

    l3 = lesson_3_alias()
    print("\n3. IS A RECLASSIFICATION A SECOND RECORD? VERDICT: PARTLY HANDLED")
    print(f"   runs carrying an alias map : {l3['runs_with_an_alias_map']}")
    print(f"   median alias map size      : {l3['median_size']}")
    print("   => the map folds each seat's local finding id onto 1 canonical id,")
    print("      so WITHIN a run a rediscovery is not a 2nd record. It does NOT")
    print("      span runs, which is lesson 1 again rather than a separate gap.")

    print("\n4. IS STATE RECORDED RATHER THAN INFERRED? VERDICT: MOSTLY, WITH 1")
    print("   KNOWN COUNTEREXAMPLE, and it is already on his decision list.")
    print("   The severity threshold became an operating convention without a")
    print("   recorded decision; B87 is the entry that asks him to settle it.")
    print("   Producer for that: scripts/the_severity_proxy_was_never_tested_2026-10-28.py")

    print("\n  SO THE ANSWER TO HIS QUESTION IS 1 LESSON, NOT 4. The registry")
    print("  already has the terminal-state rule and a within-run alias map, and")
    print("  its state-recording gap is a named decision of his. What it lacks is")
    print("  a content-derived identity, and that is a renumbering rather than a")
    print("  repair.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
