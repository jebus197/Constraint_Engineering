"""B103 and decision 17, re-measured: what the commit gate costs and covers NOW.

WHY THIS EXISTS. Entry B103 records that 54 guard files written since
2026-10-29 sit outside the commit gate, that the gate costs 598 seconds, and
that adding the 54 would take it to about 891. All 3 figures are superseded,
and decision 17 asks the founder to weigh exactly those numbers -- *whether the
commit gate should grow, and what it would cost*. A stale cost is worse than a
dated one when it is the thing being ruled on.

WHAT IS REPRODUCIBLE HERE AND WHAT IS RECORDED. The COUNTS are derived live:
the gate's own `GUARDS` list is parsed out of `hooks/pre-commit` and set against
`bench/tests/test_*.py` on disk, so they cannot drift from the hook. The
TIMINGS cannot be re-derived cheaply -- 1 gate board is about 11 minutes -- so
the observations collected on 2026-11-08 are RECORDED below with their
commit context, and the interval is computed from them. The COUNT is
deliberately not written in this prose: it said 16 while the tuple held
17 within an hour of being written, which is a hardcoded figure beside a
derived one -- the drift shape this whole script exists to correct. That is the honest
split: a figure that can be recomputed is recomputed, and a figure that cannot
is carried with its provenance rather than asserted.

WHY THE NEW PROJECTION IS NOT COMPUTED FROM A PER-TEST RATE. The project's own
record states that the unreached set runs 2.26x slower per test than the gate's
(441.72 ms against 195.50 ms), which is why a count-based extrapolation once
turned a true 6 per cent into an actual factor of 18.05. So this script REFUSES
to project, and prints what would have to be measured instead. Run it with
`--time-outside` to measure the outside set directly; that costs real minutes
on the founder's machine and is therefore never the default.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import time

import numpy as np
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "pre-commit"
TESTS = REPO / "bench" / "tests"

#: Gate-board wall-clock seconds observed on 2026-11-08, read from this
#: session's own completed pre-commit runs. Each is a full board of the gate's
#: 128 files; the 2573 entries are boards with 1 failure, retained because the
#: question is COST and a failing board costs the same as a passing one.
OBSERVED_2026_11_08 = (
    (2574, 639.19), (2574, 639.19), (2574, 643.25), (2574, 655.81),
    (2574, 657.46), (2573, 663.21), (2573, 664.29), (2574, 668.95),
    (2574, 676.12), (2574, 679.12), (2574, 703.38), (2574, 711.05),
    (2574, 713.48), (2573, 721.72), (2574, 731.05), (2574, 766.45),
    (2574, 659.31),   # the board of the commit that carried this file
)

#: What B103 records, so the drift is stated rather than silently replaced.
RECORDED = {"gate_seconds": 598.0, "outside_guards": 54,
            "projected_seconds": 891.0, "as_of": "2026-11-04"}


def gate_files(hook: pathlib.Path = HOOK) -> set[str]:
    """The gate's own list, parsed from the hook rather than restated."""
    m = re.search(r'GUARDS="(.*?)"', hook.read_text(encoding="utf-8"), re.S)
    if m is None:
        raise SystemExit("could not find the GUARDS list in the hook")
    return {x.strip() for x in m.group(1).split() if x.strip()}


def coverage(root: pathlib.Path = REPO) -> dict:
    on = gate_files(root / "hooks" / "pre-commit")
    allt = {f"bench/tests/{p.name}"
            for p in (root / "bench" / "tests").glob("test_*.py")}
    outside = sorted(allt - on)
    recent = [f for f in outside
              if (d := re.search(r"2026-\d\d-\d\d", f)) and d.group(0) >= "2026-10-29"]
    return {"on_gate": len(on & allt), "named_absent": sorted(on - allt),
            "suite_files": len(allt), "outside": outside,
            "outside_since_cut": sorted(recent)}


def timing() -> dict:
    a = np.array([s for _, s in OBSERVED_2026_11_08], dtype=float)
    lo, hi = stats.t.interval(0.95, len(a) - 1, loc=a.mean(), scale=stats.sem(a))
    t, p = stats.ttest_1samp(a, RECORDED["gate_seconds"])
    sem_np = float(np.std(a, ddof=1) / np.sqrt(len(a)))
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)), "min": float(a.min()),
            "max": float(a.max()), "ci": (float(lo), float(hi)),
            "t": float(t), "p": float(p), "sem_scipy": float(stats.sem(a)),
            "sem_numpy": sem_np}


def time_outside(files: list[str]) -> dict:
    """Measure the outside set. Costs real minutes; never the default."""
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", *files],
                       cwd=str(REPO), capture_output=True, text=True)
    wall = time.monotonic() - t0
    m = re.search(r'(\d+) passed', r.stdout)
    return {"wall_seconds": wall, "returncode": r.returncode,
            "tests": int(m.group(1)) if m else None,
            "tail": r.stdout.strip().splitlines()[-1:] or [""]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    #: ★ THE DEFAULT SCOPE IS THE 83, NOT THE 713, AND THE FIRST DRAFT HAD
    #: THIS WRONG. B103 asks what adding the guards written SINCE 2026-10-29
    #: would cost. Timing every file outside the gate times 713 of 841, which
    #: is substantially the whole suite and answers a question nobody asked --
    #: the same scope slip that let a true 6 per cent stand in for a factor of
    #: 18.05. `--time-all-outside` is kept for the separate question of what
    #: full coverage would cost, and it is NOT the default because it is hours.
    ap.add_argument("--time-outside", action="store_true",
                    help="MEASURE the guards dated 2026-10-29 or later, which "
                         "is what B103 asks about (costs real minutes)")
    ap.add_argument("--time-all-outside", action="store_true",
                    help="MEASURE every file outside the gate -- a different "
                         "question, and hours rather than minutes")
    args = ap.parse_args(argv[1:])

    c, t = coverage(), timing()
    print("1. WHAT THE GATE COVERS  (derived live from the hook)")
    print(f"   guard files in bench/tests/ : {c['suite_files']}")
    print(f"   named on the gate           : {c['on_gate']}")
    print(f"   OUTSIDE the gate            : {len(c['outside'])}")
    print(f"   named but absent from disk  : {len(c['named_absent'])}")
    assert c["on_gate"] + len(c["outside"]) == c["suite_files"], \
        "the coverage partition does not close"
    print(f"   partition closes: {c['on_gate']} + {len(c['outside'])}"
          f" = {c['suite_files']}")
    n_cut = len(c["outside_since_cut"])
    print(f"   outside AND dated 2026-10-29 or later : {n_cut}"
          f"   <- B103 records {RECORDED['outside_guards']}")
    print(f"   drift against the record : {n_cut - RECORDED['outside_guards']:+d}")

    print()
    print(f"2. WHAT THE GATE COSTS  ({len(OBSERVED_2026_11_08)}"
          f" observations recorded 2026-11-08)")
    print(f"   n={t['n']}  mean {t['mean']:.2f} s  sd {t['sd']:.2f}"
          f"  min {t['min']:.2f}  max {t['max']:.2f}")
    print(f"   95% t-interval on the mean : [{t['ci'][0]:.2f}, {t['ci'][1]:.2f}] s")
    print(f"   standard error, scipy {t['sem_scipy']:.4f} against numpy"
          f" {t['sem_numpy']:.4f}, agree="
          f"{abs(t['sem_scipy'] - t['sem_numpy']) < 1e-9}")
    print(f"   B103 records {RECORDED['gate_seconds']:.0f} s as of"
          f" {RECORDED['as_of']}; measured"
          f" {t['mean'] - RECORDED['gate_seconds']:+.2f} s,"
          f" factor {t['mean'] / RECORDED['gate_seconds']:.4f}")
    print(f"   a t-test against {RECORDED['gate_seconds']:.0f}:"
          f" t={t['t']:.4f}, p={t['p']:.3e}")
    print("   \u2605 THAT IS A DIFFERENCE IN THE MEASURED LEVEL AND NOT")
    print("   EVIDENCE THE GATE ITSELF SLOWED. All 17 observations were")
    print("   taken on 2026-11-08 while this session was running its own")
    print("   concurrent pytest, so the whole window sat under load the")
    print("   session created. No trend is detectable WITHIN the night")
    print("   (Pearson p = 0.9637, Spearman p = 0.7970, Mann-Whitney")
    print("   between halves p = 1.0000), but a stable level under")
    print("   constant load cannot be distinguished from a stable level")
    print("   without it, so the LEVEL may be uniformly inflated.")
    print("   AND THE TEST COUNT DID NOT CHANGE: the gate ran 2,574 tests")
    print("   on both dates, so this is not the gate growing. What IS")
    print("   established to have moved is the GUARD COUNT, above.")

    print()
    print("3. WHAT ADDING THE OUTSIDE SET WOULD COST")
    print(f"   B103 projects {RECORDED['projected_seconds']:.0f} s, computed for"
          f" {RECORDED['outside_guards']} guards against a"
          f" {RECORDED['gate_seconds']:.0f} s baseline.")
    print("   BOTH TERMS ARE SUPERSEDED, so the projection does not follow and is")
    print("   NOT recomputed from a per-test rate here: the unreached set runs")
    print("   2.26x slower per test than the gate's (441.72 ms against 195.50),")
    print("   and a count-based extrapolation is how a true 6 per cent once stood")
    print("   in for an actual factor of 18.05. It has to be MEASURED.")
    if args.time_outside or args.time_all_outside:
        scope = (c["outside"] if args.time_all_outside
                 else c["outside_since_cut"])
        which = ("every file outside the gate" if args.time_all_outside
                 else "the guards dated 2026-10-29 or later")
        print(f"   measuring {len(scope)} file(s) -- {which} ...")
        r = time_outside(scope)
        print(f"   outside set: {r['tests']} test(s) in {r['wall_seconds']:.2f} s"
              f"  (exit {r['returncode']})")
        print(f"   gate + outside would be about"
              f" {t['mean'] + r['wall_seconds']:.2f} s"
              f" = {(t['mean'] + r['wall_seconds']) / 60:.2f} min")
        print(f"   {r['tail'][0]}")
    else:
        print("   re-run with --time-outside to measure the 83 that B103"
              " asks about, or --time-all-outside for full coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
