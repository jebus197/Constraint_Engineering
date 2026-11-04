#!/usr/bin/env python3
"""How many of 2026-11-03's stale guard comments actually changed a decision?

THE CLAIM THIS EXISTS TO SUPPORT. 4 guard comments were found on 2026-11-03 that
described behaviour their code no longer had, and in every case the stale text
argued for the OPPOSITE of what the code does. 3 of the 4 were then quoted to the
founder as having been LOAD-BEARING -- a decision was actually made on them. A
quoted proportion needs its producer, so this is it.

WHAT IS AND IS NOT MECHANICAL, STATED FIRST BECAUSE IT BOUNDS EVERYTHING BELOW.
Whether a comment is STALE is mechanical and is checked here by execution: each
item names a live predicate whose value contradicts the comment's claim. Whether
a stale comment CHANGED A DECISION is a judgement and cannot be derived, so it is
carried as recorded data with the decision named per item, not computed. The
proportion is therefore a count over an audited list, and its confidence interval
describes sampling of that list alone -- it does not license a general rate for
stale comments in this repository.

WHY THE DISTINCTION MATTERS HERE RATHER THAN BEING A FORMALITY. A rate of
"comments that mislead" would be the flattering kind of measure: it invites the
reading that stale comments are usually harmless, which the audited items
contradict. So the mechanical half and the judged half are reported separately
and the judged half names its evidence.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve()
while REPO.name != "Constraint_Engineering" and REPO.parent != REPO:
    REPO = REPO.parent
if REPO.name != "Constraint_Engineering":
    REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
sys.path.insert(0, str(REPO))

#: Each item: the file, a probe that proves the comment stale by EXECUTION, and
#: the decision it changed -- or None where it changed nothing.
ITEMS = [
    {
        "where": "scripts/blocker_triage.py",
        "claimed": "whether a free or simulated run needs permission is a 4th "
                   "category and therefore his to rule on, raised as a ticket",
        "contradicted_by": "he ruled on 2026-10-30; live ticket e41e1fdbc223",
        "probe": "ticket_ruled",
        "probe_arg": "e41e1fdbc223",
        "decision_changed": "a permission rule was nearly added that would have "
                            "contradicted that ruling; stopped by reading this "
                            "very comment, which was itself 4 days stale",
    },
    {
        "where": "scripts/scripts_are_reached_2026-09-11.py",
        "claimed": "excluding the parked note wholly would lose its producer "
                   "citations, so only its roll-call LINES are dropped",
        "contradicted_by": "the parked note is in INSTRUMENT, a WHOLE-FILE "
                           "exclusion, and in no other list",
        "probe": "parked_note_wholly_excluded",
        "probe_arg": "",
        "decision_changed": "a producer was cited in the parked note to wire it "
                            "and stayed unreached; the citation had to be moved "
                            "to a note the scan actually reads",
    },
    {
        "where": "hooks/work_not_narrate.py",
        "claimed": "stop_hook_active makes it exit 0 immediately, so it "
                   "interrupts at most one stop per turn",
        "contradicted_by": "MAX_REFUSALS_PER_TURN is 8, and the comment on that "
                           "constant records the 1-refusal cap AS the defect",
        "probe": "refusal_budget_exceeds_one",
        "probe_arg": "",
        "decision_changed": "a session concluded a correctly working gate was "
                            "malfunctioning after 6 refusals in 1 turn, and "
                            "spent reasoning on a non-existent defect",
    },
    {
        "where": ".claude/CLAUDE.md",
        "claimed": "it interrupts at most 1 stop per turn",
        "contradicted_by": "the same constant, 8",
        "probe": "refusal_budget_exceeds_one",
        "probe_arg": "",
        "decision_changed": None,
    },
]


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    import mpmath
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
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


def run_probe(name: str, arg: str) -> tuple[bool, str]:
    """EXECUTE the predicate. A comment is stale only if code says so."""
    if name == "ticket_ruled":
        from bench.ticket_store import TicketStore
        st = TicketStore()
        st.load()
        t = st.get(arg)
        if t is None:
            return False, f"ticket {arg} not found"
        return bool(t.ruled), f"ticket {arg} carries ruled={t.ruled or '-'}"
    if name == "parked_note_wholly_excluded":
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_sr", REPO / "scripts" / "scripts_are_reached_2026-09-11.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        pk = "experimental_notes/PARKED_FOR_THE_FOUNDER.md"
        whole = pk in tuple(getattr(m, "INSTRUMENT", ()))
        other = pk in tuple(getattr(m, "SELF_REFERENTIAL", ()))
        return (whole and not other), (
            f"INSTRUMENT={whole}, SELF_REFERENTIAL={other}")
    if name == "refusal_budget_exceeds_one":
        src = (REPO / "hooks" / "work_not_narrate.py").read_text()
        for line in src.splitlines():
            if line.startswith("MAX_REFUSALS_PER_TURN"):
                n = int(line.split("=")[1].strip())
                return n > 1, f"MAX_REFUSALS_PER_TURN = {n}"
        return False, "the constant was not found"
    raise ValueError(f"unknown probe {name!r}")


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure how many of the stale guard comments found on "
                     "2026-11-03 actually changed a decision.")).parse_args()

    print("=" * 78)
    print("WAS A STALE GUARD COMMENT LOAD-BEARING, OR MERELY LAGGING?")
    print("=" * 78)

    stale, unproven = [], []
    for it in ITEMS:
        ok, detail = run_probe(it["probe"], it["probe_arg"])
        (stale if ok else unproven).append(it)
        print(f"\n  {it['where']}")
        print(f"    claimed        : {it['claimed'][:66]}")
        print(f"    probe says     : {detail}")
        print(f"    STALE by execution: {ok}")
        print(f"    changed a decision: "
              f"{'YES -- ' + it['decision_changed'][:52] if it['decision_changed'] else 'no'}")

    if unproven:
        print(f"\n  REFUSED: {len(unproven)} item(s) could not be shown stale by "
              f"execution, so the count below would be a claim about evidence "
              f"rather than evidence: {[u['where'] for u in unproven]}")
        return 1

    n = len(stale)
    k = sum(1 for it in stale if it["decision_changed"])
    print(f"\n  ALL {n} CONFIRMED STALE BY EXECUTION, not by reading.")
    (wl, wh), (cl, ch), d = _iv(k, n)
    print(f"\n  changed a decision: {k} of {n}, {k / n:.6f}")
    print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  (2-route |diff| {d:.1e})")
    print("\n  THE INTERVAL BELONGS TO THIS AUDITED LIST OF 4 AND TO NOTHING")
    print("  ELSE. n = 4 and the classification is recorded judgement, not a")
    print("  derivation, so this does NOT estimate how often a stale comment in")
    print("  this repository misleads. What it does establish is that being")
    print("  load-bearing was the MAJORITY outcome among the 4 examined, which")
    print("  is the opposite of the comfortable reading.")
    print("\n  THE 1 THAT CHANGED NOTHING changed nothing only because its twin")
    print("  had already misled the same session, so even it is not evidence")
    print("  that a stale comment is harmless.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
