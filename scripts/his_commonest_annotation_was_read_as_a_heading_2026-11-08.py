"""His commonest annotation form was discarded as a heading. 57 recovered. B105.

HIS RULING, 2026-11-08: adopt the marker rule. And in the same breath, an
instruction that partly reverses the option's second clause: *"because a double
asterisk *like this* can be misread in some situations, change this so that your
messages open with an asterisk *like this but do not close with one."* That half
is a writing rule for the generated files, not a mechanism, and is recorded
separately.

THE DEFECT, AND IT IS THE WORST SHAPE A HEURISTIC CAN FAIL IN. The response
reader classified a single-hash line as a markdown heading when the line was
short and did not end in sentence punctuation:

    len(body) <= 120 and not body.rstrip().endswith((".", "?", "!"))

His commonest annotation is "I accept your recommendation. stm". It ends in a
TICKET MARKER rather than in punctuation, so the second condition held; and it
is short, so the first held. Both conditions for "this is a heading" were
therefore satisfied by the single most frequent thing he writes, and the line
was dropped as not his.

MEASURED ACROSS THE WHOLE CORPUS: 67 response files, 57 lines recovered. Of
those 57, every one falls in a file whose GENERATED ORIGINAL still exists, so
each is checkable against ground truth rather than against a shape: 57 of 57 are
genuinely his and 0 are report lines, precision 1.000000, Wilson 95%
[0.936861, 1.000000], Clopper-Pearson [0.937333, 1.000000].

WHAT WAS BEING LOST WAS INSTRUCTIONS, NOT COMMENTARY. Among the 57:
"Permission is granted. stm", "Build and implement option 1. fr", "Repair the
two as you suggest. stm", "Has that task already been run? If not you should run
it. qs". A reader that drops those is a reader that loses work he has asked for.

WHY THE MARKER SET IS IMPORTED RATHER THAN SPELLED. It comes from
`ticket_store.KINDS`, so a 7th kind is recognised without editing the reader --
the addition-nothing-reaches failure in reverse. The match requires a WORD
BOUNDARY on both sides, which keeps `disc` out of "discussion" and `ds` out of
"Methods", and it is CASE-INSENSITIVE because 3 of his annotations carry `Qs`
and `Stm` with a leading capital and a case-sensitive pattern drops exactly
those 3.
"""
from __future__ import annotations

import argparse
import math
import pathlib

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

READER = REPO / "scripts/read_founder_responses_2026-10-11.py"
RESPONSES = pathlib.Path.home() / "Developer_Projects/Responses"


def _reader():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_cdsfl_rfr", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _predicate_before_the_fix(mod, line: str) -> bool:
    """The reader's heading test AS IT STOOD before 2026-11-08.

    Reproduced so the recovery can be measured as a DIFFERENCE rather than
    asserted. It is the 2-or-more-hashes rule of 2026-11-02 plus the shape
    test, with the marker clause absent.
    """
    if not mod._MD_HEADING.match(line):
        return False
    s = line.lstrip()
    if len(s) - len(s.lstrip("#")) >= 2:
        return True
    body = line.lstrip("#").strip()
    return len(body) <= 120 and not body.rstrip().endswith((".", "?", "!"))


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


def survey(responses: pathlib.Path = RESPONSES):
    """(recovered, his, report_lines, files) over every response file.

    `his` and `report_lines` partition the ORACLE-BACKED recoveries only: a
    response file is a copy of a generated report with his '#' insertions, so a
    line present in the surviving original is the report's and a line absent
    from it is his. Where no original survives the recovery is counted but not
    adjudicated, because a shape heuristic is not ground truth.
    """
    mod = _reader()
    recovered, his, report = [], [], []
    files = 0
    for p in sorted(responses.glob("*.txt")) + sorted(responses.glob("*.md")):
        try:
            text = mod.read_any(p)
        except Exception:                                 # noqa: BLE001
            continue
        files += 1
        orig = mod._TTS_ORIGINALS / p.name
        oracle = ({l.strip() for l in mod.read_any(orig).splitlines() if l.strip()}
                  if orig.is_file() else None)
        for ln in text.splitlines():
            if not mod._MD_HEADING.match(ln):
                continue
            was = _predicate_before_the_fix(mod, ln)
            now = mod._looks_like_a_markdown_heading(ln)
            if not (was and not now):
                continue
            recovered.append((p.name, ln.strip()))
            if oracle is None:
                continue
            (report if ln.strip() in oracle else his).append((p.name, ln.strip()))
    return recovered, his, report, files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", type=int, default=10,
                    help="how many recovered lines to print")
    args = ap.parse_args()

    if not READER.is_file():
        print(f"REFUSED: {READER} is not in this checkout")
        return 1
    if not RESPONSES.is_dir():
        print(f"SKIPPED: {RESPONSES} is not on this machine, so the corpus "
              f"this figure is measured over is absent and nothing is claimed.")
        return 0

    mod = _reader()
    print(f"marker set, imported from ticket_store : {tuple(mod._HIS_KINDS)}")
    print(f"pattern                                : {mod._ENDS_IN_HIS_MARKER.pattern}")

    recovered, his, report, files = survey()
    adjudicated = len(his) + len(report)
    print(f"\nresponse files read                      : {files}")
    print(f"lines RECOVERED by the marker rule       : {len(recovered)}")
    print(f"  of which oracle-backed (adjudicable)   : {adjudicated}")
    print(f"    genuinely HIS                        : {len(his)}")
    print(f"    report lines wrongly admitted        : {len(report)}")

    if adjudicated:
        (wl, wh), (cl, ch), diff = _iv(len(his), adjudicated)
        print(f"\n  precision {len(his)} of {adjudicated} = "
              f"{len(his) / adjudicated:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
        print(f"    the 2 routes of each agree to {diff:.2e}")

    print(f"\n  what was being lost (first {args.show}):")
    for n, l in recovered[:args.show]:
        print(f"    {n[:42]:42s} | {l[:86]}")
    if len(recovered) > args.show:
        print(f"    ... and {len(recovered) - args.show} more")

    print()
    if report:
        print(f"  WARNING: {len(report)} report line(s) are now read as his. "
              f"The rule is too loose and must be narrowed before use.")
        return 1
    if his:
        print(f"  THE RULE IS SOUND ON THE EVIDENCE AVAILABLE: every one of the "
              f"{len(his)} adjudicable recoveries is his, and 0 report lines "
              f"were admitted. The bound is the interval above, not the point.")
    print(f"\n  FALSE-POSITIVE CONTROL, so this is not a flattering measure: "
          f"the same predicate is put 5 real heading shapes that END IN A "
          f"MARKER-LIKE SUBSTRING but not in a marker -- 'Methods', "
          f"'Discussion', 'discard', 'disclose', 'Next steps' -- and all 5 must "
          f"stay classified as headings.")
    controls = ("Methods", "Discussion", "discard", "disclose", "Next steps")
    kept = [c for c in controls if mod._looks_like_a_markdown_heading("# " + c)]
    print(f"    still headings: {len(kept)} of {len(controls)}  {kept}")
    if len(kept) != len(controls):
        print("    REFUSED: the word boundary is not holding.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
