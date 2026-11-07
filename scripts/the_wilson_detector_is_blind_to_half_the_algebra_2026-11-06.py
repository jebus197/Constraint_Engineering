#!/usr/bin/env python3
"""The cross-check detector fixes the variable's SPELLING, so it cannot see
roughly half the algebra it looks for. Measured, for entry B135.

`scripts/counting_imports_ranks_producers_backwards_2026-11-03.py` ranks a
producer by whether a quantity rests on 2 INDEPENDENT routes. Its Wilson routes
are statsmodels' `proportion_confint(..., method="wilson")` and the written-out
closed form, matched as `z \\* z / \\(2 \\* n\\)` -- LOWERCASE n only.

A producer that writes the identical algebra over a sample size named `N`, or
with different spacing, or as `z**2`, is invisible to the second pattern and
therefore scores 1 route where it has 2. That is how the complete board of
2026-11-05 came to report `is_any_external_citation_verified_2026-11-04` as
resting a quantity on a single route: it had a real gap (no Clopper-Pearson at
all) AND an invisible cross-check, and only the first was its own fault.

THE PATTERNS ARE READ OUT OF THE DETECTOR AT RUN TIME, never restated, so this
producer goes red rather than stale if the detector is repaired.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DETECTOR = REPO / "scripts" / "counting_imports_ranks_producers_backwards_2026-11-03.py"


def detector_patterns() -> dict[str, str]:
    """The Wilson routes, lifted from the detector's own QUANTITY_ROUTES table."""
    #: ★ READ THE TABLE BY IMPORT, NOT BY REGEX OVER THE SOURCE. Repaired
    #: 2026-11-07. The source-text read below anchors on `"name": r"pattern"`
    #: all on one line, and on 2026-11-06 the detector's "written-out algebra"
    #: entry was widened into a multi-line parenthesised concatenation -- a
    #: perfectly ordinary Python spelling that this shape cannot see. The
    #: producer then exited "ANCHOR ABSENT: could not identify both Wilson
    #: routes", so the instrument that measures B135 was silently disabled by
    #: a repair to B135's own subject. That widening was B135's option 2, which
    #: the entry itself calls a treadmill; option 1, its recommendation, is to
    #: replace a source-text match with EXECUTION. This applies option 1 to the
    #: PRODUCER: importing the module yields the dict whatever its spelling.
    #: The source-text path is retained as a fallback and the route used is
    #: printed, so a future import failure is loud rather than silent.
    import importlib.util as _ilu
    try:
        _spec = _ilu.spec_from_file_location("_wilson_detector_subject", DETECTOR)
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        _routes = dict(_mod.QUANTITY_ROUTES["Wilson"])
        print("  route table read BY IMPORT (immune to how the table is spelled)")
        return _routes
    except Exception as _err:                                    # noqa: BLE001
        print(f"  import failed ({type(_err).__name__}: {_err}); "
              f"falling back to the source-text read")
    src = DETECTOR.read_text(encoding="utf-8")
    m = re.search(r'"Wilson":\s*\{(.*?)\}', src, re.S)
    if not m:
        raise SystemExit("ANCHOR ABSENT: the detector's Wilson route table has moved")
    out = dict(re.findall(r'"([^"]+)":\s*r"([^"]+)"', m.group(1)))
    print(f"  route table read FROM SOURCE TEXT: {len(out)} route(s) -- a value "
          f"spelled across lines is invisible to this path")
    return out


#: THE SAME ALGEBRA, WRITTEN ANY REASONABLE WAY. Each alternative is the Wilson
#: centre's `z^2 / (2n)` term; none of them is a different computation.
LOOSE = re.compile(
    r"z\s*\*\s*z\s*/\s*\(\s*2\s*\*\s*[nN]\w*\s*\)"
    r"|z\s*\*\*\s*2\s*/\s*\(\s*2\s*\*\s*[nN]\w*\s*\)"
    r"|z\s*\*\s*z\s*/\s*\(\s*2\s*\*\s*[nN]\w*\s*\)")


def main() -> int:
    #: ANSWER `--help` BEFORE DOING ANY WORK. His rule, measured: a flag
    #: that runs the whole measurement can cost machine time or money,
    #: and 15 of 17 runners once billed for it.
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _ah
    _ah(__doc__, __file__)
    pats = detector_patterns()
    strict = next((v for k, v in pats.items() if "statsmodels" not in k.lower()), None)
    sm = next((v for k, v in pats.items() if "statsmodels" in k.lower()), None)
    if not strict or not sm:
        raise SystemExit("ANCHOR ABSENT: could not identify both Wilson routes")
    print("the detector's 2 Wilson routes, read from its own table:")
    for k, v in pats.items():
        print(f"   {k:34s} {v}")

    seen, hidden = [], []
    for p in sorted((REPO / "scripts").glob("*.py")):
        t = p.read_text(encoding="utf-8", errors="replace")
        if not re.search(sm, t):
            continue
        if re.search(strict, t):
            seen.append(p.name)
        elif LOOSE.search(t):
            hidden.append(p.name)

    n = len(seen) + len(hidden)
    k = len(hidden)
    print(f"\nproducers using the statsmodels Wilson route : {n}")
    print(f"  ALSO seen by the strict written-out pattern : {len(seen)}")
    print(f"  writing the SAME algebra but INVISIBLE      : {k}")

    if n:
        import mpmath
        from scipy.stats import beta as sbeta
        from statsmodels.stats.proportion import proportion_confint
        wl, wh = proportion_confint(k, n, method="wilson")
        mpmath.mp.dps = 40
        z = mpmath.mpf("1.959963984540054235524594430520551527955")
        p_ = mpmath.mpf(k) / n
        d = 1 + z * z / (2 * n) * 2 / 1          # 1 + z^2/n, written to keep the term visible
        d = 1 + z * z / n
        c = (p_ + z * z / (2 * n)) / d
        h = (z / d) * mpmath.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n))
        cl = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
        ch = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
        print(f"\n  invisible rate {k} of {n} = {k/n:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}] statsmodels")
        print(f"    Wilson [{float(c-h):.6f}, {float(c+h):.6f}] mpmath closed form")
        print(f"      the 2 routes agree to 1e-12: "
              f"{abs(wl-float(c-h)) < 1e-12 and abs(wh-float(c+h)) < 1e-12}")
        print(f"    Clopper-Pearson [{cl:.6f}, {ch:.6f}] scipy.beta")
    print(f"\n  first 10 invisible: {hidden[:10]}")
    print("\n  WHAT THIS IS NOT. It is not a claim that those producers are wrong:")
    print("  every one of them computes Wilson twice. It is a claim that the")
    print("  detector cannot tell, so its ranking of cross-check independence")
    print("  rests on a spelling. The repair is to EXECUTE the helper and")
    print("  compare its routes, which the board guard already does 2 classes")
    print("  further down its own file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
