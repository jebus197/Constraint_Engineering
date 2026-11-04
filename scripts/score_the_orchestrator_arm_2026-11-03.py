#!/usr/bin/env python3
"""Score the bound-orchestrator arm's 3 pre-registered predictions.

DRAFT. The arm has not been run and this is deliberately not wired to it yet.

WHY A SCORER IS WRITTEN BEFORE THE RUN. The 2026-09-02 blind audit holds 286
first-pass and 108 second-pass verdicts and names NO SCORER, and its
`ground_truth` field holds the withheld severity NUMBERS rather than labels, so
a result there is attributed to nobody. A prediction with no scorer is scored by
nobody, and that is a provenance gap rather than an inconvenience.

WHY IT RUNS AGAINST THE ARCHIVE AND NOT ONLY AGAINST THE ARM. A scorer exercised
only on the output of the experiment it was written for is UNTESTED until that
experiment runs, so its first use is also its first trial -- which is the worst
moment to discover it counts the wrong thing. This one takes `--run` and scores
any archived run directory, so every predicate here can be exercised today
against runs that already exist. The arm, when it exists, is just another
directory.

WHAT IT DOES NOT DO. It does not decide whether the arm is worth running: the
founder's ruling on ticket 72f1d6095d83 places 1 simulated run on the severity
mechanics ahead of the orchestrator work. It does not register the
pre-registration. And it takes no verdict on O1's threshold of 0.80, which is a
chosen decision boundary and his to set.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: O1's decision boundary. CHOSEN, not derived: it sits below the prior
#: measurement's Wilson lower bound of 0.912314 so that a pass does not merely
#: restate the prior, and it is the founder's to set or reject.
O1_FLOOR = 0.80


def _iv(k: int, n: int):
    """Wilson on 2 routes and Clopper-Pearson on 2 routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p, d = k / n, 1 + stats.norm.ppf(0.975) ** 2 / n
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


def _report(run: pathlib.Path) -> dict:
    for pat in ("*_report.json", "*report*.json"):
        for f in sorted(run.glob(pat)):
            try:
                return json.loads(f.read_text(errors="replace"))
            except Exception:                                # noqa: BLE001
                continue
    return {}


def _state(run: pathlib.Path) -> dict:
    f = run / "runner_state.json"
    try:
        return json.loads(f.read_text(errors="replace"))
    except Exception:                                        # noqa: BLE001
        return {}


def _classifier():
    """The canonical adjudication classifier, IMPORTED rather than re-written.

    THE FIRST DRAFT OF THIS FILE GOT THE PREDICATE WRONG IN THE EXACT WAY THE
    CANONICAL PRODUCER RECORDS ITS OWN FIRST VERSION GETTING IT WRONG. This
    scored on a `mechanism` field, read from `*_report.json`, and treated
    anything not naming a quorum as tool-made. All 3 are wrong: the fields are
    `status_adjudicator` and `status_mechanism`, they live in
    `runner_state.json`, and the ADJUDICATOR is the authority -- the producer's
    own comment records that scoring on tool OUTPUT instead returned 79 of 79
    and failed to reproduce the 77 the figure rests on, because carrying a
    tool's output is not the same as having been DECIDED by one.

    Exercising this scorer against the archive before the arm existed is what
    caught it: O1 read NOT SCORABLE in 347 of 347 archived runs, which is a
    probe looking in the wrong place and not a property of the archive.

    So the predicate is imported from the committed producer. 2 surfaces
    holding 1 fact with no comparator is the drift shape this project has met
    repeatedly, and the producer's figure is already cited in entry B20.
    """
    import importlib.util
    src = (REPO / "scripts"
           / "were_the_shakedown_adjudications_tool_made_2026-10-17.py")
    spec = importlib.util.spec_from_file_location("_adj_canon", src)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.classify_adjudication


def score_o1(run: pathlib.Path) -> dict:
    """O1: the tool-made share of adjudications.

    TOOL-MADE means `status_adjudicator == "tool"`. The 2 non-tool adjudications
    across the shakedown legs read `status_adjudicator == "runner"` with
    mechanism `model_confirm_quorum (3/1 independent)` -- settled by a quorum of
    models asserting, not by anything executable.
    """
    classify = _classifier()
    s = _state(run)
    ents = ((s.get("registry") or {}).get("entries")) or {}
    tool = assertion = 0
    unknown = []
    for cid, e in (ents.items() if isinstance(ents, dict) else []):
        if not isinstance(e, dict):
            continue
        verdict = classify(e)
        if verdict == "tool":
            tool += 1
        elif verdict == "assertion":
            assertion += 1
        else:
            unknown.append(cid)
    n = tool + assertion
    out = {"prediction": "O1", "tool_made": tool, "assertion_made": assertion,
           "n": n, "no_mechanism_recorded": len(unknown)}
    if n == 0:
        out["verdict"] = "NOT SCORABLE"
        out["why"] = ("0 adjudications in this run record a mechanism, so the "
                      "share has no denominator. A 0 here is a 0 of NOTHING "
                      "and must not be read as 0 tool-made.")
        return out
    (wl, wh), (cl, ch), diff = _iv(tool, n)
    # 3-VALUED, AND THE 2-VALUED VERSION WAS WRONG IN A WAY THE ARCHIVE PROVED.
    # The first rule read `HOLDS if wl >= floor else FALSIFIED`, which falsifies
    # a run for having too FEW adjudications rather than too few tool-made ones:
    # across the archive it called 10 of 28 runs FALSIFIED, and 7 of those 10
    # have a point estimate of EXACTLY 1.0 with n between 8 and 15. A run whose
    # every adjudication is tool-made first clears a 0.80 Wilson floor at
    # n = 16, so the rule was measuring sample size.
    #
    # To CLAIM the share is below the floor the interval must exclude the floor
    # from above, which is the same one-sided form the project's own P3
    # pre-registered prediction uses when it requires its interval to exclude
    # 0.5. Anything straddling the floor is INDETERMINATE: not enough
    # adjudications to decide, which is a fact about the run and not a verdict
    # on the hypothesis.
    verdict = ("HOLDS" if wl >= O1_FLOOR
               else "FALSIFIED" if wh < O1_FLOOR
               else "INDETERMINATE")
    out.update({"share": tool / n, "wilson": [wl, wh],
                "clopper_pearson": [cl, ch], "two_route_diff": diff,
                "floor": O1_FLOOR, "verdict": verdict})
    if verdict == "INDETERMINATE":
        out["why"] = (f"the 95% interval [{wl:.6f}, {wh:.6f}] straddles the "
                      f"floor of {O1_FLOOR}, so {n} adjudication(s) cannot "
                      f"decide it either way")
    return out


def score_o2(run: pathlib.Path) -> dict:
    """O2: convergence by the two-sided gate, evaluable per round."""
    s = _state(run)
    gh = list(s.get("gamma_history") or [])
    gate = list(s.get("gate_history") or [])
    out = {"prediction": "O2", "rounds_with_gamma": len(gh),
           "rounds_with_gate": len(gate)}
    if not gh and not gate:
        out["verdict"] = "NOT SCORABLE"
        out["why"] = ("neither gamma_history nor gate_history is present, so "
                      "no round boundary can be evaluated")
        return out
    out["gate_passed_rounds"] = sum(1 for g in gate if g)
    out["converged_at"] = s.get("converged_at")
    out["verdict"] = "HOLDS" if s.get("converged_at") is not None else "OPEN"
    out["why"] = ("a run still in progress is OPEN rather than falsified; only "
                  "exhausting the ceiling without convergence falsifies O2")
    return out


def score_o3(run: pathlib.Path) -> dict:
    """O3: 0 applied changes without a recorded verification.

    Reads the actuator's own decision log, whose first guarantee is exactly
    this, plus any orchestrator change log the arm writes.
    """
    rows = []
    f = run / "actuator_decisions.jsonl"
    if f.is_file():
        for ln in f.read_text(errors="replace").splitlines():
            try:
                rows.append(json.loads(ln))
            except Exception:                                # noqa: BLE001
                continue
    acted = [r for r in rows if r.get("acted")]
    unrecorded = [r for r in acted if not (r.get("reason") and r.get("evidence"))]
    out = {"prediction": "O3", "decisions": len(rows), "acted": len(acted),
           "acted_without_a_record": len(unrecorded)}
    if not rows:
        out["verdict"] = "NOT SCORABLE"
        out["why"] = ("no actuator decision log exists for this run, so there "
                      "is nothing to check. This is the expected result for "
                      "every run archived before 2026-11-03.")
        return out
    out["verdict"] = "HOLDS" if not unrecorded else "FALSIFIED"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Score the bound-orchestrator arm's 3 pre-registered "
                     "predictions against any run directory."))
    ap.add_argument("--run", help="a run directory under bench/logs")
    ap.add_argument("--survey", action="store_true",
                    help="score every archived run, to exercise the scorer "
                         "before the arm exists")
    args = ap.parse_args()

    if args.survey:
        runs = sorted(p for p in LOGS.glob("*") if p.is_dir())
        tally: dict = {}
        for r in runs:
            for fn in (score_o1, score_o2, score_o3):
                v = fn(r)["verdict"]
                tally.setdefault(fn.__name__, {}).setdefault(v, 0)
                tally[fn.__name__][v] += 1
        print("=" * 76)
        print(f"SCORER EXERCISED AGAINST {len(runs)} ARCHIVED RUN DIRECTORIES")
        print("=" * 76)
        for name in sorted(tally):
            print(f"  {name}: " + ", ".join(
                f"{v}={c}" for v, c in sorted(tally[name].items())))
        print()
        print("  WHAT THIS SHOWS. It shows the scorer RUNS and which predicates")
        print("  have data to run on. It does NOT score the arm, which has not")
        print("  been run. A predicate reporting NOT SCORABLE everywhere is a")
        print("  predicate whose data the archive does not carry -- that is")
        print("  information about the predicate, not about the arm.")
        return 0

    if not args.run:
        print("pass --run <dir> or --survey")
        return 2
    run = pathlib.Path(args.run)
    if not run.is_dir():
        run = LOGS / args.run
    if not run.is_dir():
        print(f"no such run directory: {args.run}")
        return 2
    print("=" * 76)
    print(f"SCORING {run.name}")
    print("=" * 76)
    for fn in (score_o1, score_o2, score_o3):
        print(json.dumps(fn(run), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
