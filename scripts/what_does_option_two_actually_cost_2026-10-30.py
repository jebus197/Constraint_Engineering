#!/usr/bin/env python3
"""How many live runs must accumulate before B50's option (2) can be measured?

B50 offers 3 dispositions for the assertions a reset re-armed, and option (2) --
*"re-measure all 4 against the post-reset memory as it fills, accepting that they
assert nothing until enough live runs have accumulated"* -- carries no number for
"enough". This prices it. It does NOT choose between the options: that ruling is
the founder's, and nothing here is applied.

WHY THE QUESTION IS ANSWERABLE AT ALL. `test_the_evidence_base_is_thin_and_here_is
_how_thin` states its own thresholds in code: `totals[1] >= 50 and totals[5] >= 50`,
over RAW undecayed counts read from the run reports, plus `8 in singletons`. A
sibling, `test_the_live_memory_file_still_loads`, requires the record set to be
exactly [1, 2, 3, 4, 5, 6, 8]. Those are arithmetic conditions on an accumulating
population, so the run count they imply is derivable rather than a matter of taste.

THE BASIS IS 1 RUN, AND THAT IS THE DOMINANT UNCERTAINTY. Only
`free_run3_no_spec_20261028T235529Z` has written since the reset of 2026-10-17, so
every per-run rate here rests on a single observation and the intervals are wide by
construction. They are reported wide rather than narrowed by borrowing the
pre-reset runs, whose per-run detail the archive does not retain.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib

import mpmath as mp
import numpy as np
import sympy as sp
from scipy import stats as sst

REPO = pathlib.Path(__file__).resolve().parents[1]
LIVE = REPO / "bench" / "state" / "immune_memory.json"
ARCHIVE = REPO / "bench" / "state" / "immune_memory_archive"
THRESHOLD = 50           # the test's own literal, for classes 1 and 5
REQUIRED = [1, 2, 3, 4, 5, 6, 8]


def live_store() -> dict:
    return json.loads(LIVE.read_text(encoding="utf-8"))


def archived_stores() -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(ARCHIVE / "immune_memory_*.json"))):
        if f.endswith(".why.json"):
            continue
        out.append(json.loads(pathlib.Path(f).read_text(encoding="utf-8")))
    return out


def per_run_yield(store: dict) -> dict[int, float]:
    """Observations per class in the live store.

    With `experiment_count == 1` no decay step has been applied, so these are raw
    counts; the function refuses rather than guessing if that stops being true.
    """
    n = store.get("experiment_count")
    if n != 1:
        raise ValueError(
            f"experiment_count is {n}, not 1, so the stored weights are decayed "
            f"and cannot be read as raw counts. Re-derive from the run reports.")
    return {int(k): v["confirmed"] + v["rejected"] for k, v in store["records"].items()}


def runs_to_threshold(observed: float, threshold: int = THRESHOLD) -> dict:
    """Runs needed to reach `threshold`, with an exact Poisson interval on the rate.

    A single run produced `observed` observations of this class. Treating that as
    one draw from Poisson(lambda), the exact 95% interval on lambda inverts the
    Poisson tails; runs needed is threshold/lambda, so the interval INVERTS -- the
    low rate gives the high run count.
    """
    k = int(round(observed))
    lo = 0.0 if k == 0 else sst.chi2.ppf(0.025, 2 * k) / 2.0
    hi = sst.chi2.ppf(0.975, 2 * (k + 1)) / 2.0

    #: INDEPENDENT CROSS-CHECK THROUGH THE GAMMA RELATION, and the first version
    #: of it was WRONG -- it inverted the 0.975 tail and returned 8.767273 where
    #: scipy gave 1.089865, a disagreement of about 8x. The identities are
    #: P(X >= k | lam) = regularized lower incomplete gamma P(k, lam), so the
    #: lower limit solves P(k, lam) = 0.025, and P(X <= k | lam) = regularized
    #: upper incomplete gamma Q(k+1, lam), so the upper limit solves
    #: Q(k+1, lam) = 0.025. A cross-check that disagrees leaves the figure
    #: UNVERIFIED, which is why this is asserted rather than printed.
    lo_mp = 0.0 if k == 0 else float(mp.findroot(
        lambda L: mp.gammainc(k, 0, L, regularized=True) - mp.mpf("0.025"),
        max(k, 0.5)))
    hi_mp = float(mp.findroot(
        lambda L: mp.gammainc(k + 1, L, mp.inf, regularized=True) - mp.mpf("0.025"),
        k + 1.0))
    assert abs(lo_mp - lo) < 1e-6, f"lower limit unverified: scipy {lo} vs mpmath {lo_mp}"
    assert abs(hi_mp - hi) < 1e-6, f"upper limit unverified: scipy {hi} vs mpmath {hi_mp}"
    point = math.inf if observed <= 0 else threshold / observed
    return {
        "observed": observed, "lambda_lo": lo, "lambda_hi": hi,
        "lambda_lo_mpmath": lo_mp, "lambda_hi_mpmath": hi_mp,
        "runs_point": point,
        "runs_lo": threshold / hi if hi > 0 else math.inf,
        "runs_hi": math.inf if lo <= 0 else threshold / lo,
    }


def runs_to_see_a_rare_class(seen_in: int, of: int, confidence: float = 0.95) -> dict:
    """Runs needed to observe a class at least once with `confidence`.

    Flaw class 8 appeared in 1 experiment of the archived population. The run count
    solves 1 - (1 - p)^n >= confidence, derived symbolically so the closed form is
    checked rather than asserted.
    """
    p = sp.Rational(seen_in, of)
    n = sp.symbols("n", positive=True)
    closed = sp.solve(sp.Eq(1 - (1 - p) ** n, sp.Rational(int(confidence * 100), 100)), n)
    n_closed = float(closed[0]) if closed else float("nan")
    n_num = math.log(1 - confidence) / math.log(1 - float(p))
    #: SECOND TOOL on the same quantity: a direct simulation, so the closed form
    #: is checked against sampling rather than against its own rearrangement.
    rng = np.random.default_rng(20261030)
    n_runs = math.ceil(n_num)
    hit = (rng.random((40000, n_runs)) < float(p)).any(axis=1).mean()
    assert hit >= confidence - 0.01, f"simulation {hit:.4f} below {confidence}"
    return {"p": float(p), "n_closed_form": n_closed, "n_numeric": n_num,
            "n_runs": n_runs, "simulated_coverage_at_n_runs": float(hit)}


def report() -> dict:
    live = live_store()
    arch = archived_stores()
    y = per_run_yield(live)
    res = {"live_run": live["experiment_ids"], "per_run_yield": y,
           "classes_present": sorted(y), "classes_missing": [c for c in REQUIRED if c not in y]}
    res["thresholds"] = {c: runs_to_threshold(y.get(c, 0.0)) for c in (1, 5)}

    # the archive's own count disagrees with its id list; both denominators reported
    a = arch[0] if arch else {}
    res["archive_count"] = a.get("experiment_count")
    res["archive_ids"] = len(a.get("experiment_ids") or [])
    seen8 = int((a.get("records", {}).get("8", {}) or {}).get("experiments_seen", 0))
    res["class8"] = {
        "seen_in": seen8,
        "against_experiment_count": runs_to_see_a_rare_class(seen8, a.get("experiment_count", 6)),
        "against_id_list": runs_to_see_a_rare_class(seen8, max(1, len(a.get("experiment_ids") or [1]))),
    }
    binding = max(res["thresholds"][1]["runs_point"], res["thresholds"][5]["runs_point"],
                  res["class8"]["against_experiment_count"]["n_runs"])
    res["binding_runs"] = binding
    return res


def main(argv: list[str] | None = None) -> int:
    #: ARGPARSE FIRST, SO --help COSTS NOTHING. The pre-commit gate refused this
    #: file's first version for exactly that: it ran the whole measurement and
    #: exited 0 with no usage line, so `--help` was silently ignored. This
    #: project's rule is that a --help must never cost anything, measured after
    #: 15 of 17 runners were found to bill for it.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true",
                    help="emit the report as JSON instead of prose")
    args = ap.parse_args(argv)
    r = report()
    if args.json:
        print(json.dumps(r, indent=2, default=float))
        return 0
    print(__doc__.split("\n")[0])
    print("=" * 78)
    print(f"post-reset runs on record : {r['live_run']}")
    print(f"per-run observations      : {r['per_run_yield']}")
    print(f"classes present / missing : {r['classes_present']} / {r['classes_missing']}")
    print()
    for c in (1, 5):
        t = r["thresholds"][c]
        print(f"flaw class {c}: {t['observed']:.0f} observations in 1 run; "
              f"{THRESHOLD} needed")
        print(f"   lambda 95% exact [{t['lambda_lo']:.6f}, {t['lambda_hi']:.6f}] "
              f"(mpmath lower {t['lambda_lo_mpmath']:.6f})")
        print(f"   runs needed: point {t['runs_point']:.4f}, "
              f"95% [{t['runs_lo']:.4f}, {t['runs_hi']:.4f}]")
    c8 = r["class8"]
    print(f"\nflaw class 8 appeared in {c8['seen_in']} experiment(s); it must appear at all")
    for label in ("against_experiment_count", "against_id_list"):
        d = c8[label]
        print(f"   {label}: p={d['p']:.6f}, closed form {d['n_closed_form']:.4f}, "
              f"numeric {d['n_numeric']:.4f} -> {d['n_runs']} runs for 0.95 confidence")
    print(f"\nARCHIVE DENOMINATOR IS AMBIGUOUS: experiment_count {r['archive_count']} "
          f"against {r['archive_ids']} retained ids, so p for a rare class is not single-valued.")
    print(f"\nBINDING: about {r['binding_runs']:.0f} live runs before option (2) can be measured.")
    print("Nothing here chooses an option. The ruling is the founder's.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
