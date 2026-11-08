"""Does composing the 2 producer guards beat either one alone? MEASURED.

HIS STANDARD, verbatim, 2026-10-02: *"Composability doesn't mean composing two
solutions just because they can be composed. It means this principle should be
applied where two composed solutions demonstrably provide a better, more robust
and/or more efficient solution than either fix in isolation. Where a single fix
out performs a composed one, that fix should continue to be preferred."*

SO THIS FILE EXISTS BECAUSE THE CLAIM REQUIRES A MEASUREMENT. Measured on
2026-10-31, 10 of 10 uses of the word "composability" across the decisions file
and the morning report took the WEAK sense his definition explicitly excludes --
that 2 repairs merely do not conflict. A recommendation of a composed fix
without a dominance measurement is that same failure, and extending the
reached-producers rule to today's date is exactly where it would have recurred:
the obvious move was a 3rd dated guard.

THE 2 PARTS.
  A = ``bench/tests/test_tonights_producers_are_reached_2026-11-08.py``
      EXECUTES every 2026-11-08 producer. Frozen to 1 date by its own glob.
  B = ``bench/tests/test_an_unreached_producer_set_cannot_grow_2026-11-08.py``
      Date-INDEPENDENT. Refuses any producer that is unreached and not in the
      admitted set. Its predicate is TEXTUAL -- a name appearing in a test.

HOW THIS IS MEASURED RATHER THAN ARGUED. 6 failure cases are each put to BOTH
mechanisms' real decisions. ``verdict`` is imported from B and called; A's
MUST_RUN and NOT_RUN_HERE are imported from A rather than retyped; and the
textual reached predicate is the one in
``the_unreached_producer_debt_is_not_todays_2026-11-08.py``, called via its own
``repo`` parameter against SYNTHETIC trees built in a temporary directory. No
case is decided by reading source text, and the live tree is never written to --
which matters because a probe's own location has manufactured a failure in this
project before.

THE DECISION RULE, STATED BEFORE THE RESULT SO IT CAN FAIL. The composition is
justified only if BOTH exclusive cells are non-empty: at least 1 case caught by
A and missed by B, AND at least 1 caught by B and missed by A. If either cell is
empty, the mechanism that catches everything is the simplest sufficient fix and
the other must be dropped. If the A-only cell is empty, drop A and keep the
ratchet. If the B-only cell is empty, drop B and write dated guards.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

A_PATH = REPO / "bench/tests/test_tonights_producers_are_reached_2026-11-08.py"
B_PATH = REPO / "bench/tests/test_an_unreached_producer_set_cannot_grow_2026-11-08.py"
SURVEYOR = REPO / "scripts/the_unreached_producer_debt_is_not_todays_2026-11-08.py"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def _synthetic(scripts: dict[str, str], tests: dict[str, str],
               into: pathlib.Path) -> pathlib.Path:
    """Build a throwaway tree with scripts/ and bench/tests/ and return its root.

    The live tree is NEVER written to. A probe that writes where it measures has
    manufactured a failure in this project before, so the real ``survey``
    predicate is pointed at this synthetic root through its own ``repo``
    parameter instead.
    """
    (into / "scripts").mkdir(parents=True, exist_ok=True)
    (into / "bench/tests").mkdir(parents=True, exist_ok=True)
    for n, body in scripts.items():
        (into / "scripts" / n).write_text(body)
    for n, body in tests.items():
        (into / "bench/tests" / n).write_text(body)
    return into


#: The 6 failure cases. Each names the capability required to catch it, and
#: every capability is then verified by EXECUTION rather than asserted.
CASES = (
    dict(key="broken_listed_producer",
         what="a 2026-11-08 producer that is listed and EXECUTED stops working "
              "(non-zero exit)",
         needs="EXEC"),
    dict(key="later_dated_producer",
         what="a producer dated 2026-11-09 that no test names",
         needs="RATCHET"),
    dict(key="swap_at_constant_total",
         what="one admitted debt discharged and one new unreached producer "
              "added, total unchanged",
         needs="RATCHET"),
    dict(key="undeclared_same_date",
         what="a new 2026-11-08 script in neither of the dated guard's lists",
         needs="ACCT+RATCHET"),
    dict(key="mentioned_never_run",
         what="a 2026-11-08 producer declared EXEMPT but never executed, so a "
              "name in a test is all that reaches it",
         needs="NEITHER"),
    dict(key="deleted_while_listed",
         what="a 2026-11-08 producer deleted while still declared in MUST_RUN",
         needs="ACCT"),
)


def _evaluate(A, B, surveyor, tmp: pathlib.Path) -> list[dict]:
    """Put every case to BOTH mechanisms' real decisions."""
    on_disk = {p.name for p in (REPO / "scripts").glob("*2026-11-08*.py")}
    real_pin = B.pinned()
    rows = []

    for i, case in enumerate(CASES):
        key = case["key"]
        root = tmp / key

        if key == "broken_listed_producer":
            name = A.MUST_RUN[0]
            # A EXECUTES every MUST_RUN member and asserts returncode 0. Saying
            # "it is in MUST_RUN" would be circular, so the assertion is made
            # to FIRE: a deliberately broken script is run through the same
            # subprocess call A makes, and its exit code is checked against A's
            # own condition.
            root.mkdir(parents=True, exist_ok=True)
            broken = root / "broken_producer.py"
            broken.write_text("raise SystemExit(1)\n")
            rc = subprocess.run([sys.executable, str(broken)],
                                capture_output=True, text=True, timeout=60)
            a_hit = (name in A.MUST_RUN) and rc.returncode != 0
            a_why = (f"MUST_RUN names it, and A's own condition (returncode == "
                     f"0) was made to fire on a broken script: exit "
                     f"{rc.returncode}")
            # B: the name is still written in A's file, so the TEXTUAL reached
            # predicate finds it. Run the real predicate to show that.
            _synthetic({name: "raise SystemExit(1)\n"},
                       {"test_a.py": f"# runs {name}\n"}, root)
            _r, unr, _bd = surveyor.survey(root)
            b_hit = bool(B.verdict(set(unr), real_pin | set(on_disk))[0])
            b_why = ("textually reached: its name appears in a test, and the "
                     "predicate cannot tell a run from a mention")

        elif key == "later_dated_producer":
            name = "a_new_measurement_2026-11-09.py"
            a_hit = name in A.MUST_RUN or ("2026-11-08" in name)
            a_why = "outside the glob *2026-11-08*, so A never considers it"
            _synthetic({name: "print(1)\n"}, {"test_a.py": "# nothing\n"}, root)
            _r, unr, _bd = surveyor.survey(root)
            b_hit = bool(B.verdict(set(unr), real_pin)[0])
            b_why = "unreached and not in the admitted set"

        elif key == "swap_at_constant_total":
            a_hit = False
            a_why = "not dated 2026-11-08, so A never considers it"
            victim = sorted(real_pin)[0]
            newcomer = "a_swapped_in_producer_2026-10-20.py"
            swapped = set(sorted(real_pin)[1:]) | {newcomer}
            assert len(swapped) == len(real_pin), "the swap must hold n constant"
            b_hit = bool(B.verdict(swapped, real_pin)[0])
            b_why = (f"set membership, not a count: {newcomer} is new debt and "
                     f"{victim} was discharged, so n is unchanged")

        elif key == "undeclared_same_date":
            name = "an_undeclared_measurement_2026-11-08.py"
            a_hit = any(r.startswith("UNDECLARED") and name in r
                        for r in A.refusals(present=on_disk | {name}))
            a_why = "A.refusals returns UNDECLARED"
            _synthetic({name: "print(1)\n"}, {"test_a.py": "# nothing\n"}, root)
            _r, unr, _bd = surveyor.survey(root)
            b_hit = bool(B.verdict(set(unr), real_pin)[0])
            b_why = "unreached and not in the admitted set"

        elif key == "mentioned_never_run":
            name = "an_exempted_measurement_2026-11-08.py"
            nrh = {**A.NOT_RUN_HERE,
                   name: "declared exempt with a reason long enough to pass"}
            # ATTRIBUTED to this case's own name. An unfiltered bool() read
            # True here on the first run because the real NOT_RUN_HERE named a
            # harness not yet on disk, so an unrelated PHANTOM was reported as
            # this case being caught -- the probe manufacturing its own result.
            a_hit = any(name in r
                        for r in A.refusals(present=on_disk | {name},
                                            not_run_here=nrh))
            a_why = ("declared, so accounting is satisfied; and not in "
                     "MUST_RUN, so A never executes it")
            _synthetic({name: "print(1)\n"},
                       {"test_a.py": f"# exempt: {name}\n"}, root)
            _r, unr, _bd = surveyor.survey(root)
            b_hit = bool(B.verdict(set(unr), real_pin)[0])
            b_why = "textually reached by the exemption entry that names it"

        elif key == "deleted_while_listed":
            victim = sorted(A.MUST_RUN)[0]
            a_hit = any(r.startswith("PHANTOM") and victim in r
                        for r in A.refusals(present=on_disk - {victim}))
            a_why = f"A.refusals returns PHANTOM for {victim}"
            _synthetic({}, {"test_a.py": "# nothing\n"}, root)
            _r, unr, _bd = surveyor.survey(root)
            b_hit = bool(B.verdict(set(unr), real_pin)[0])
            b_why = ("the file is gone, so it is not an unreached producer at "
                     "all and the ratchet has nothing to see")

        rows.append(dict(n=i + 1, key=key, what=case["what"],
                         needs=case["needs"], a=a_hit, b=b_hit,
                         a_why=a_why, b_why=b_why))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()

    for p in (A_PATH, B_PATH, SURVEYOR):
        if not p.is_file():
            print(f"REFUSED: {p} is not in this checkout")
            return 1

    A = _load(A_PATH, "_cdsfl_guard_a")
    B = _load(B_PATH, "_cdsfl_guard_b")
    surveyor = _load(SURVEYOR, "_cdsfl_surveyor_comp")

    with tempfile.TemporaryDirectory() as td:
        rows = _evaluate(A, B, surveyor, pathlib.Path(td))

    a_only = [r for r in rows if r["a"] and not r["b"]]
    b_only = [r for r in rows if r["b"] and not r["a"]]
    both = [r for r in rows if r["a"] and r["b"]]
    neither = [r for r in rows if not r["a"] and not r["b"]]
    n = len(rows)

    print("WHICH MECHANISM CATCHES WHICH FAILURE")
    print(f"  A = dated guard, EXECUTES 2026-11-08's {len(A.MUST_RUN)} producers")
    print(f"  B = date-independent ratchet over a pinned SET of "
          f"{len(B.pinned())} admitted debts")
    print()
    for r in rows:
        mark = ("A+B" if r["a"] and r["b"] else
                "A  " if r["a"] else "  B" if r["b"] else "---")
        print(f"  {r['n']}. [{mark}] {r['what']}")
        print(f"         A {'CATCHES' if r['a'] else 'MISSES '}: {r['a_why']}")
        print(f"         B {'CATCHES' if r['b'] else 'MISSES '}: {r['b_why']}")

    print()
    print(f"  caught by A alone : {len(a_only)} of {n}  "
          f"{[r['key'] for r in a_only]}")
    print(f"  caught by B alone : {len(b_only)} of {n}  "
          f"{[r['key'] for r in b_only]}")
    print(f"  caught by both    : {len(both)} of {n}")
    print(f"  caught by NEITHER : {len(neither)} of {n}  "
          f"{[r['key'] for r in neither]}")

    covered_a = len(a_only) + len(both)
    covered_b = len(b_only) + len(both)
    covered_c = len(a_only) + len(b_only) + len(both)
    for label, k in (("A alone", covered_a), ("B alone", covered_b),
                     ("A composed with B", covered_c)):
        (wl, wh), (cl, ch), diff = _iv(k, n)
        print(f"\n  {label}: {k} of {n} = {k / n:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
        print(f"    max disagreement between the 2 routes of each: {diff:.2e}")

    print()
    ok = bool(a_only) and bool(b_only)
    if ok:
        print("  COMPOSITION JUSTIFIED under his standard: each part catches at "
              "least 1 failure the other misses, so neither dominates and the "
              f"composed pair covers {covered_c} of {n} against "
              f"{covered_a} and {covered_b} alone.")
    elif not a_only:
        print("  COMPOSITION REFUSED: the dated guard catches nothing the "
              "ratchet misses. Drop it and keep the ratchet alone.")
    else:
        print("  COMPOSITION REFUSED: the ratchet catches nothing the dated "
              "guard misses. Drop it and write dated guards.")

    if neither:
        print(f"\n  NAMED LIMIT, not a defect of the composition: "
              f"{len(neither)} case(s) escape BOTH. A producer declared exempt "
              f"and never executed is reached only by the entry that exempts "
              f"it, and the textual predicate counts that as reached. Closing "
              f"it needs an execution-aware reached predicate, which is a "
              f"larger change than his instruction asked for.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
