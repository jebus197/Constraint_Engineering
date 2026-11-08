"""B87's figure, produced: does ANY archived finding carry a `confidence` field?

WHY THIS SCRIPT EXISTS. Entry B87 tells the founder that `confidence` appears
on **0 of 3,311** archived findings, Wilson 95% [0.000000, 0.001159], and
argues from that figure that the directive's `d_tool` gate -- *"must come from
actual tool execution ... not from self-assessed confidence"* -- is WORKING
rather than that a quantity is missing. The figure carried no committed
producer, so under `measured-rate-travels-with-its-script` it was a claim about
evidence rather than evidence. Measured 2026-11-08: 11 of 35 figure-bearing
authored items name no producer, 0.314286, Wilson [0.185508, 0.479798]; this
closes 1 of them. Whether the remaining 10 should be produced or labelled
unmeasured is `qs:dfd9167bbf1b`, which is the founder's.

THE FRAME IS THE SAME ONE THE SEVERITY WORK USES, and that is deliberate
rather than convenient: `bench/logs/*/runner_state.json`, the registry entries
inside each, which is the glob
`scripts/the_severity_proxy_was_never_tested_2026-10-28.py` calls its "real
sampling frame". Using a different frame would give a different denominator and
the 2 figures would then disagree for no reason a reader could see.

THE NUMERATOR AND THE DENOMINATOR COUNT DIFFERENT PREDICATES ON PURPOSE. The
denominator is entries carrying a NUMERIC severity, because that is what B87's
sibling figures are drawn over. The numerator is entries carrying a
`confidence` KEY AT ALL -- present-and-null still counts as present, since the
claim is that the field never appears, not that it is never set. Counting only
non-null values would make a null field invisible and the 0 unfalsifiable.

A 0 IS ONLY WORTH REPORTING IF SOMETHING COULD HAVE MADE IT NON-ZERO, so this
prints the keys actually seen across the frame. If `confidence` is absent from
that list the 0 is real; if the field were present under another spelling the
list shows it, and the claim would need restating rather than re-asserting.
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
FRAME_GLOB = "*/runner_state.json"
FIELD = "confidence"

mp.mp.dps = 40
_Z = mp.mpf("1.959963984540054235524594430520551527955")


def _interval(k: int, n: int) -> dict:
    """Wilson on 2 routes and Clopper-Pearson on 2, with the disagreement."""
    wl, wh = proportion_confint(k, n, 0.05, method="wilson")
    p, N = mp.mpf(k) / n, mp.mpf(n)
    den = 1 + _Z**2 / N
    cen = (p + _Z**2 / (2 * N)) / den
    half = (_Z / den) * mp.sqrt(p * (1 - p) / N + _Z**2 / (4 * N**2))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y  # noqa: E731
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        return float((lo + hi) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(wl - float(cen - half)), abs(wh - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return {"k": k, "n": n, "wilson": (wl, wh), "clopper_pearson": (cl, ch),
            "route_disagreement": dis}


def scan(root: pathlib.Path = REPO) -> dict:
    """Walk the frame once and report both predicates plus the key census."""
    logs = root / "bench" / "logs"
    files = unreadable = severities = carriers = 0
    keys: Counter[str] = Counter()
    for p in sorted(logs.glob(FRAME_GLOB)):
        files += 1
        try:
            entries = (json.loads(p.read_text(encoding="utf-8"))
                       .get("registry", {}).get("entries", {}))
        except (OSError, ValueError):
            unreadable += 1      # an unreadable run must not silence the rest
            continue
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            keys.update(e.keys())
            if isinstance(e.get("severity"), (int, float)):
                severities += 1
            if FIELD in e:
                carriers += 1
    return {"frame_glob": FRAME_GLOB, "frame_files": files,
            "unreadable_files": unreadable, "denominator": severities,
            "carriers": carriers, "keys": keys}


def main() -> int:
    r = scan()
    n, k = r["denominator"], r["carriers"]
    print("B87's FIGURE, PRODUCED")
    print(f"  frame                      : bench/logs/{FRAME_GLOB}")
    print(f"  frame files                : {r['frame_files']}"
          f"  (unreadable {r['unreadable_files']})")
    print(f"  entries with a numeric severity : {n}   <- the denominator")
    print(f"  entries carrying `{FIELD}`  : {k}   <- the numerator")
    if not n:
        print("  REFUSING to report a rate on an empty frame.")
        return 1
    iv = _interval(k, n)
    wl, wh = iv["wilson"]
    cl, ch = iv["clopper_pearson"]
    print(f"  {k} of {n} = {k / n:.6f}")
    print(f"    Wilson          [{wl:.6f}, {wh:.6f}]  statsmodels / mpmath")
    print(f"    Clopper-Pearson [{cl:.6f}, {ch:.6f}]  scipy / mpmath")
    print(f"    4-term route disagreement {iv['route_disagreement']:.3e}")
    assert iv["route_disagreement"] < 1e-6, "the 2 route pairs disagree"

    print()
    print("  ANTI-VACUITY -- what a 0 here is a 0 OF.")
    print(f"    distinct keys seen across the frame : {len(r['keys'])}")
    near = sorted(x for x in r["keys"] if "conf" in x.lower())
    print(f"    keys containing 'conf'              : {near or 'NONE'}")
    top = ", ".join(f"{x}={c}" for x, c in r["keys"].most_common(6))
    print(f"    most common keys                    : {top}")
    if k == 0 and not near:
        print("    So the field is ABSENT, not merely unset: no spelling of it")
        print("    appears anywhere in the frame.")
    print()
    print("  B87 records 0 of 3,311 with Wilson [0.000000, 0.001159].")
    print(f"  This run: {k} of {n}. Denominator drift {n - 3311:+d}.")
    return 0


if __name__ == "__main__":
    #: ★ `--help` MUST NOT RUN THE MEASUREMENT. Without this the flag
    #: was ignored and the whole archive walk ran, which
    #: `bench/tests/test_help_is_answered_2026-09-11.py` refused -- and
    #: rightly: it is the 5th instance of this shape tonight. The block
    #: carries its OWN `sys` import because a module-level one that the
    #: body never uses is removed by ruff, and then this needs it back.
    #: It sits INSIDE the main guard, not at module level, because
    #: `takes_no_arguments=True` refuses any non-empty argv and at module
    #: level that refuses every import made by a test runner.
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main())
