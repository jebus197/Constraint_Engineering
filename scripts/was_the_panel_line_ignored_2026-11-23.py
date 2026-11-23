#!/usr/bin/env python3
"""How many recent commits landed with NO free panel round behind them?

DESTINATION `scripts/`. Written 2026-11-23.

WHY THIS EXISTS. His standing instruction of 2026-11-21 is that every
meaningful batch of work goes to a free panel before it is adopted, and a
commit is the unit of a batch under his 2026-11-10 ruling. `hooks/pre-commit`
already asks the question at every commit, through
`was_this_batch_reviewed_2026-11-22.py`, and REPORTS rather than refuses. Its
own comment names the escalation trigger: "If the line turns out to be ignored,
THAT is the evidence for escalating it to a refusal."

NOTHING MEASURED WHETHER IT WAS IGNORED. That is what this measures, and the
answer decides whether the line should refuse.

IT IMPORTS THE GATE'S OWN PREDICATE rather than re-implementing it. A second
implementation of "was this batch reviewed" would be a producer and a consumer
that can disagree while each describes itself consistently -- the defect class
`execute-do-not-grep` names, found 4 times in this project by executing 2 forms
against each other and 0 times by reading.

THE BOUNDARY, STATED. This reproduces the GATE'S predicate, which asks for
rounds completing between the previous commit and this one. A round dispatched
before a commit but completing after it reviewed that work in substance and is
counted here as UNCOVERED, because the gate would not have seen it either. The
question being answered is "was the line ignored", not "was the work reviewed
by any means", and those are different questions.

EVERY PROPORTION ON 2 ROUTES, per the 21 April 2026 rule.
"""
from __future__ import annotations
import argparse
import importlib.util
import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GATE_PREDICATE = REPO / "scripts" / "was_this_batch_reviewed_2026-11-22.py"


def load_gate_predicate():
    """Import the gate's own module. Never re-implement its decision."""
    spec = importlib.util.spec_from_file_location("_wtbr", GATE_PREDICATE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {GATE_PREDICATE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(REPO),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} exited {r.returncode}: "
                           f"{r.stderr.strip()}")
    return r.stdout.strip()


def commits_in(rng: str):
    """[(sha, committer_epoch, subject)] oldest first for a revision range."""
    out = git("log", "--reverse", "--format=%H%x1f%ct%x1f%s", rng)
    rows = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        sha, ct, subj = line.split("\x1f", 2)
        rows.append((sha, int(ct), subj))
    return rows


def wilson_two_routes(k: int, n: int):
    """(statsmodels, mpmath closed form). Both must agree."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    from scipy import stats as sstats
    mp.mp.dps = 40
    lo_a, hi_a = proportion_confint(k, n, method="wilson")
    z = mp.mpf(str(sstats.norm.ppf(0.975)))
    N, K = mp.mpf(n), mp.mpf(k)
    ph = K / N
    den = 1 + z**2 / N
    ctr = (ph + z**2 / (2 * N)) / den
    hw = (z / den) * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2))
    return (float(lo_a), float(hi_a)), (float(ctr - hw), float(ctr + hw))


def _binom_tail_ge(k: int, n: int, p: float) -> float:
    """P(X >= k) with integer binomials. Independent of any stats library."""
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))


def _binom_tail_le(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))


def _bisect(f, lo: float, hi: float, target: float) -> float:
    """Solve f(p) = target on [lo, hi]. BRACKETED, and the domain is asserted.

    A solver handed an unbracketed interval returns whatever its last iterate
    happened to be, which in this project has produced an INVERTED interval and
    a probability above 1 that a sibling ordering assertion then passed.
    """
    assert 0.0 <= lo <= hi <= 1.0, f"domain violated: [{lo}, {hi}]"
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    out = (lo + hi) / 2
    assert 0.0 <= out <= 1.0, f"solver left the domain: {out}"
    return out


def clopper_pearson_two_routes(k: int, n: int):
    """(statsmodels beta, exact-tail bisection with math.comb)."""
    from statsmodels.stats.proportion import proportion_confint
    lo_a, hi_a = proportion_confint(k, n, method="beta")
    lo_b = 0.0 if k == 0 else _bisect(
        lambda p: _binom_tail_ge(k, n, p), 0.0, 1.0, 0.025)
    hi_b = 1.0 if k == n else _bisect(
        lambda p: -_binom_tail_le(k, n, p), 0.0, 1.0, -0.025)
    return (float(lo_a), float(hi_a)), (lo_b, hi_b)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--range", default="HEAD~10..HEAD",
                    help="git revision range to measure (default HEAD~10..HEAD)")
    ap.add_argument("--quiet", action="store_true",
                    help="print only the headline proportion")
    a = ap.parse_args(argv)

    gate = load_gate_predicate()
    rows = commits_in(a.range)
    if not rows:
        print(f"no commits in range {a.range}")
        return 0

    # The window for the OLDEST commit in the range opens at its own parent.
    first_parent_time = int(git("log", "-1", "--format=%ct", f"{rows[0][0]}^"))

    results = []
    prev_time = first_parent_time
    for sha, ct, subj in rows:
        rounds = [r for r in gate.rounds_since(prev_time) if r["mtime"] <= ct]
        useful = [r for r in rounds if r["ok"]]
        results.append({"sha": sha[:8], "subject": subj, "rounds": len(rounds),
                        "useful": len(useful),
                        "covered": bool(useful),
                        "names": [r["dir"] for r in useful]})
        prev_time = ct

    n = len(results)
    uncovered = sum(1 for r in results if not r["covered"])

    if not a.quiet:
        print("=" * 74)
        print("WAS THE COMMIT GATE'S PANEL LINE IGNORED?")
        print("=" * 74)
        print(f"\n  range   : {a.range}")
        print(f"  commits : {n}")
        print(f"  predicate imported from: {GATE_PREDICATE.name}\n")
        for r in results:
            mark = "COVERED  " if r["covered"] else "UNCOVERED"
            print(f"  {mark} {r['sha']}  {r['subject'][:52]}")
            if r["covered"]:
                for nm in r["names"]:
                    print(f"              round: {nm}")

    p = uncovered / n
    print(f"\n  UNCOVERED: {uncovered} of {n} commit(s) landed with no useful "
          f"panel round = {p:.6f}")

    (w_lo, w_hi), (m_lo, m_hi) = wilson_two_routes(uncovered, n)
    (c_lo, c_hi), (b_lo, b_hi) = clopper_pearson_two_routes(uncovered, n)
    w_diff = max(abs(w_lo - m_lo), abs(w_hi - m_hi))
    c_diff = max(abs(c_lo - b_lo), abs(c_hi - b_hi))
    print(f"  Wilson 95%          : [{w_lo:.6f}, {w_hi:.6f}]"
          f"   (statsmodels; mpmath closed form agrees to {w_diff:.2e})")
    print(f"  Clopper-Pearson 95% : [{c_lo:.6f}, {c_hi:.6f}]"
          f"   (statsmodels; math.comb exact-tail bisection agrees to {c_diff:.2e})")
    assert w_lo <= p <= w_hi, "the point estimate fell outside its own Wilson interval"
    assert c_lo <= p <= c_hi, "the point estimate fell outside its own CP interval"
    assert w_diff < 1e-9, f"the 2 Wilson routes disagree by {w_diff}"
    assert c_diff < 1e-6, f"the 2 Clopper-Pearson routes disagree by {c_diff}"

    if not a.quiet:
        print("\n  WHAT THIS DOES AND DOES NOT SUPPORT.")
        print("    It measures the GATE'S predicate, so it answers whether the")
        print("    advisory line was ignored. It does NOT establish that the work")
        print("    was unreviewed by any means: a round completing after a commit")
        print("    reviewed that work in substance and is counted UNCOVERED here,")
        print("    because the gate would not have counted it either.")
    return 0


if __name__ == "__main__":
    # ★ `answer_help` BELONGS INSIDE `__main__`, NOT AT MODULE LEVEL. At module
    # level it runs ON IMPORT and reads the IMPORTING process's argv. B212.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        #: ★ `takes_no_arguments=False` IS LOAD-BEARING, NOT COSMETIC. The
        #: default is True, and with it `answer_help` REFUSES every flag with
        #: exit 2 BEFORE this script's own parser is reached -- so each flag
        #: declared below would be unreachable, which is `additive-standard`'s
        #: symmetric form: an addition nothing reaches is not additive. Found
        #: 2026-11-23 by a test written for a sibling script, which reported
        #: "This script takes no arguments" for a script that has some.
        answer_help(__doc__, __file__,
                    takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
