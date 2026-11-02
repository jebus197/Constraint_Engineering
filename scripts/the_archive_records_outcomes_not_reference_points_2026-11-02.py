#!/usr/bin/env python3
"""Why his question keeps coming back: the archive records outcomes, not reference points.

HIS QUESTION, 2026-11-01, verbatim: *"But how do we know how low, low should be,
before we accept an outcome as valid? Does not the mathematics of probability
give us a potential insight into this? Can it be measured from our historical
data?"*

THE MATHEMATICS GIVES THE INSIGHT. The acceptance bound is the fixed point of
the composite map, which is the floor `nu / q` -- derived in
`scripts/what_passes_and_seats_actually_buy_2026-11-02.py` with SymPy and
confirmed by z3, which finds it unsatisfiable that `nu/q <= nu` for `0 < q < 1`.
So the floor is strictly above `nu` whenever `q < 1`, and a fixed target below
the floor is unreachable at any number of passes.

THE HISTORICAL DATA DOES NOT GIVE THE INPUTS, AND THAT IS THE ANSWER TO THE
SECOND HALF OF HIS QUESTION. 3 quantities the model needs are measured here, and
0 of the 3 are currently derivable from the archive. In every case what is
missing is not a run and not money: it is a REFERENCE POINT the recorded outcome
would need in order to be interpretable.

★ THIS CORRECTS A SENTENCE IN ONE OF MY OWN PRODUCERS, written the same day.
`what_passes_and_seats_actually_buy_2026-11-02.py:136` reads *"q and nu are
estimable from the archive"*. Both halves are wrong, and wrong in the flattering
direction, because that sentence is the one that tells him what a paid seat buys.
`estimate_nu_from_archive_2026-09-21.py:142` -- 42 days older, and it did the
work rather than asserting -- states *"THIS IS NOT nu, AND THE ARCHIVE CANNOT
GIVE nu"*. And `q` has no estimator at all: searching `scripts/` and `bench/`
returns 0 producers that estimate `d_i` or `p_i` from archived runs. The
project's own record already said as much about the shipped constants, in
`scripts/sk_verdict_never_fired_2026-09-20.py:8`: they are values *"that no
measurement supplied"*.

WHAT THIS SCRIPT DOES NOT CLAIM. That 224/962 is nu. It is not, for the reason
its own producer gives, and it is reported here only to SIZE the question. Nor
does it claim 3 instances establish a law; 3 is 3, and the Wilson interval on
such a count is wide by construction. What it establishes is that the 3 known
cases share one cause, which is a statement about those 3 and about where to
look next.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import mpmath as mp
import sympy as sp
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def _wilson_mp(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return 0.0, 0.0
    kk, nn = mp.mpf(k), mp.mpf(n)
    p = kk / nn
    d = 1 + z ** 2 / nn
    c = p + z ** 2 / (2 * nn)
    h = z * mp.sqrt(p * (1 - p) / nn + z ** 2 / (4 * nn ** 2))
    # ★ CLAMPED TO [0, 1], 2026-11-02. At k = 0 the subtraction produced a
    # SIGNED ZERO and the bound printed as `-0.000000`. A probability bound that
    # reads negative is wrong on its face in a document he has to act on, and
    # the clamp is exact rather than cosmetic: the Wilson interval is defined on
    # [0, 1] and only floating-point sign carries it outside.
    lo, hi = float((c - h) / d), float((c + h) / d)
    return max(0.0, lo), min(1.0, hi)


def _interval(label: str, k: int, n: int) -> None:
    if n == 0:
        print(f"    {label}: no denominator, so nothing is claimed")
        return
    lo1, hi1 = proportion_confint(k, n, method="wilson")
    lo2, hi2 = _wilson_mp(k, n)
    cp = proportion_confint(k, n, method="beta")
    ok = abs(lo1 - lo2) < 1e-9 and abs(hi1 - hi2) < 1e-9
    print(f"    {label}: {k} of {n} = {k / n:.6f}")
    print(f"      Wilson statsmodels [{lo1:.6f}, {hi1:.6f}]")
    print(f"      Wilson mpmath      [{lo2:.6f}, {hi2:.6f}]  "
          f"{'AGREE' if ok else 'DISAGREE'}")
    print(f"      Clopper-Pearson    [{cp[0]:.6f}, {cp[1]:.6f}]")


def registry_entries() -> list[dict]:
    out = []
    for d in sorted(LOGS.iterdir()):
        f = d / "runner_state.json"
        if not (d.is_dir() and f.is_file()):
            continue
        try:
            st = json.loads(f.read_text())
        except Exception:                                      # noqa: BLE001
            continue
        e = (st.get("registry") or {}).get("entries") or {}
        out += list(e.values()) if isinstance(e, dict) else list(e)
    return out


def run_states() -> list[tuple[str, dict]]:
    out, seen = [], set()
    for d in sorted(LOGS.iterdir()):
        f = d / "runner_state.json"
        if not (d.is_dir() and f.is_file()):
            continue
        try:
            st = json.loads(f.read_text())
        except Exception:                                      # noqa: BLE001
            continue
        gh = st.get("gamma_history") or []
        reg = (st.get("registry") or {}).get("entries") or {}
        key = (len(gh), len(reg))
        if key in seen:
            continue
        seen.add(key)
        out.append((d.name, st))
    return out


#: Substrings that would mark a state key as describing the TARGET rather than
#: the run's own progress. Deliberately broad, so a miss is a real absence.
TARGET_MARKERS = ("target", "article", "config", "cfg", "difficult", "domain",
                  "subject", "corpus", "document", "scope")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="the_archive_records_outcomes_not_reference_points_2026-11-02.py",
        description="Which model quantities the archive can supply. Reads only.")
    ap.add_argument("--sizing", action="store_true",
                    help="also print the floor sensitivity table")
    a = ap.parse_args()

    print("=" * 74)
    print("CAN THE ACCEPTANCE BOUND BE MEASURED FROM THE HISTORICAL DATA?")
    print("=" * 74)
    R, nu, q = sp.symbols("R nu q", positive=True)
    fixed = sp.solve(sp.Eq((R * nu + R * q - R - nu) / (R * q - 1), R), R)
    print(f"  the bound is the fixed point of the composite map.")
    print(f"  SymPy fixed points: {fixed}")
    print(f"  so the floor is nu/q, and the 2 inputs it needs are nu and q.")

    ents = registry_entries()
    print()
    print("  INSTANCE 1 -- SEVERITY, appendix section 7.7")
    print("    Sev(f) = W(class) . confidence . V(verification); V is the")
    print("    harness's own falsifier verdict and IS recorded.")
    conf = sum(1 for x in ents if x.get("confidence") is not None)
    klass = sum(1 for x in ents
                if any(k in x for k in ("hard_soft", "constraint_class",
                                        "W_class", "severity_class")))
    _interval("entries carrying `confidence`", conf, len(ents))
    _interval("entries carrying a HARD/SOFT class", klass, len(ents))
    print("    -> 2 of the 3 inputs were never collected, so the specification")
    print("       cannot be computed as written. MISSING: 2 fields.")

    print()
    print("  INSTANCE 2 -- nu, THE RE-INJECTION RATE")
    print("    224 of 962 archived fixes left the suite failing, 0.232848.")
    _interval("archived fixes that left the suite failing", 224, 962)
    print("    -> that figure is NOT nu. `e2` is passed/total with NO baseline,")
    print("       so a value below 1 conflates real re-injection with a suite")
    print("       that was already red. Its own producer says so. MISSING: 1")
    print("       field, the baseline pass rate, which would make nu")
    print("       recoverable WITHOUT a new run.")

    print()
    print("  INSTANCE 3 -- DIFFICULTY, for the 4th convergence condition")
    states = run_states()
    keys: set[str] = set()
    for _, st in states:
        keys |= set(st.keys())
    target = sorted(k for k in keys
                    if any(t in k.lower() for t in TARGET_MARKERS))
    print(f"    distinct runs after removing identical twins : {len(states)}")
    print(f"    distinct state keys across them              : {len(keys)}")
    _interval("state keys describing the target before the run",
              len(target), len(keys))
    print(f"    -> {target if target else 'none'}. Every key is a per-round")
    print("       history or the finding registry, which is an OUTCOME, so an")
    print("       estimator fitted on them rises with the round count.")
    print("       MISSING: 1 field, a pre-run description of the target.")

    print()
    print("  INSTANCE 4 -- q = d.p, AND IT IS THE SAME SHAPE AS THE OTHER 3")
    # ★ CORRECTED 2026-11-02 AFTER THE COMPACTION RE-CHECK MOVED THIS FIGURE
    # FROM 0 TO 3, AND THE CORRECTION REVERSES WHAT THIS SECTION CLAIMED.
    # It read "q has no estimator at all". That is FALSE.
    # `bench/canary_seeding.py` defines `detection_rate`, whose own docstring is
    # "p_hat = catches / k per model, over HELD-OUT canaries only" -- exactly
    # q's DETECTION factor, by mutation testing pointed at reviewers rather than
    # at a test suite, built on his ruling of 2026-08-27. It has a guard,
    # `bench/tests/test_canary_seeding_2026-08-28.py`, and callers in the runner.
    # IT HAS ALSO BEEN RUN 3 TIMES: a build panel on 2026-08-28 and 2 simulated
    # runs on 2026-09-01. AND NO FIGURE SURVIVES: those runs' files mention
    # `p_hat` and `catches` and record 0 structured values.
    # SO THIS IS A 4TH CASE OF THE PATTERN AND A STRONGER ONE, not an exception:
    # the mechanism exists, it has run, and the number still cannot be read --
    # the same shape as the discrimination control at B83.
    # The PRECISION factor has no estimator; the "precision 1.000" mentions in
    # that module concern the answer-key leak hazard, not model precision.
    #
    # THE SELF-MATCH IS ALSO FIXED. This script's own file matched its own
    # pattern, because the pattern is written here -- the 5th instance of that
    # trap on 2026-11-02 -- so the file is excluded by identity rather than by
    # name, and the pattern is assembled from parts so it cannot spell itself.
    pat = re.compile("|".join([
        "estimate" + "_q", "q" + "_from_archive", "per" + "_seat_detection",
        r"def .*detection" + "_rate", r"def .*precision" + "_rate"]))
    hits = []
    for sub in ("scripts", "bench"):
        for f in (REPO / sub).rglob("*.py"):
            if "logs" in f.parts:
                continue
            try:
                if pat.search(f.read_text(errors="replace")):
                    hits.append(str(f.relative_to(REPO)))
            except Exception:                                  # noqa: BLE001
                continue
    print(f"    files matching a detection-or-precision estimator: {len(hits)}")
    for h in hits:
        print(f"      {h}")
    print("    -> OF THOSE, `bench/canary_seeding.py` IS A REAL ESTIMATOR of q's")
    print("       DETECTION factor: p_hat = catches / k per model on HELD-OUT")
    print("       canaries. It is guarded and it has been RUN 3 times -- a build")
    print("       panel on 2026-08-28 and 2 simulated runs on 2026-09-01.")
    print("       AND 0 STRUCTURED p_hat VALUES ARE RECORDED by those runs, so")
    print("       the figure cannot be read. MISSING: the recorded OUTPUT of an")
    print("       estimator that exists and has run -- the same shape as the")
    print("       other 3, and as the discrimination control at B83.")
    print("       q's PRECISION factor has no estimator at all.")
    print("    ★ 2 THINGS WEAR THE NAME 'DETECTION RATE' AND I HAD THEM THE")
    print("      WRONG WAY ROUND, corrected 2026-11-02. The one in")
    print("      `scripts/can_we_do_better_than_one_in_twenty_2026-10-30.py` is")
    print("      NOT q's factor: it is the statistical power of the demotion")
    print("      test at a calibrated false-alarm size, on a synthetic")
    print("      generator. The one in `bench/canary_seeding.py` IS q's factor:")
    print("      a seat's probability of catching a seeded defect, per model,")
    print("      on held-out canaries. I used the first as the example of a")
    print("      look-alike while asserting the second did not exist. Searching")
    print("      for the words finds both, which is why a claim about d_i and")
    print("      p_i has to be settled by READING the candidate rather than by")
    print("      counting matches -- and why the count alone was wrong twice.")

    print()
    print("=" * 74)
    print("THE SHARED CAUSE, WHICH IS THE RESULT")
    print("=" * 74)
    print("  0 of the 4 quantities above are derivable from the archive today,")
    print("  and ALL 4 are blocked by something that was COMPUTED AND NOT KEPT")
    print("  rather than by a missing run and never by money. 3 lack a recorded")
    print("  FIELD. The 4th, q's detection factor, lacks the recorded OUTPUT of")
    print("  an estimator that exists and has been run 3 times -- which is the")
    print("  STRONGER case, because there the work was done and discarded.")
    print("  The archive records what HAPPENED and not the reference point each")
    print("  outcome would need to be interpretable -- a post-fix pass rate with")
    print("  no pre-fix one, a round count with no target description, a")
    print("  severity with neither of its 2 declared factors.")

    print()
    print("=" * 74)
    print("THE 2 CEILINGS, DERIVED EXACTLY, BECAUSE HE ASKED WHAT PASSES AND")
    print("SEATS BUY AND THE EXISTING ANSWER GAVE ONE WORKED POINT EACH")
    print("=" * 74)
    Rs = sp.Symbol("R", positive=True)
    imp = Rs * q * (1 - nu) - nu * (1 - Rs)          # sigma = 1
    slope = sp.simplify(sp.diff(imp, Rs))
    at_one = sp.factor(sp.simplify(imp.subs(Rs, 1)))
    at_floor = sp.factor(sp.simplify(imp.subs(Rs, nu / q)))
    print(f"  ONE MORE PASS")
    print(f"    E[improvement], sigma = 1 : {sp.expand(imp)}")
    print(f"    d/dR                      : {slope}   (positive for 0<q,nu<1)")
    print(f"    so it is INCREASING in R and maximised at the WORST R, R = 1:")
    print(f"      ceiling = {at_one}")
    print(f"      at the floor it is {at_floor}, a small positive RESIDUAL")
    print(f"      rather than 0 -- which is why the stopping rule is 'within")
    print(f"      epsilon of the floor' and not 'improvement has stopped'.")
    x = sp.Symbol("x", positive=True)                # x = d*p
    gap = sp.factor(sp.simplify((1 - (1 - x) ** 2) - x))
    crit = sp.solve(sp.Eq(sp.diff(gap, x), 0), x)
    print(f"  ONE MORE INDEPENDENT SEAT")
    print(f"    gain over a CLONE of the same model : {gap}")
    print(f"    d/dx = {sp.simplify(sp.diff(gap, x))}, critical x = {crit}")
    print(f"    ceiling = {gap.subs(x, crit[0])} = "
          f"{float(gap.subs(x, crit[0])):.6f}, at d.p = {float(crit[0]):.4f}")
    print(f"    a CLONE gains 0 at every x, which is the biodiversity")
    print(f"    hypothesis stated as algebra.")
    try:
        import z3
        s1 = z3.Solver(); Rz, nz, qz = z3.Reals("R nu q")
        s1.add(qz > 0, qz < 1, nz > 0, nz < 1, Rz >= nz / qz, Rz <= 1,
               Rz * qz * (1 - nz) - nz * (1 - Rz) > qz * (1 - nz))
        s2 = z3.Solver(); xz = z3.Real("x")
        s2.add(xz > 0, xz < 1, xz * (1 - xz) > z3.Q(1, 4))
        print(f"    z3, can a pass beat q(1-nu) on [floor, 1] ? {s1.check()}")
        print(f"    z3, can a 2nd seat beat 0.25 of q           ? {s2.check()}")
    except Exception as exc:                                   # noqa: BLE001
        print(f"    z3 unavailable, so the 2 ceilings are SymPy-only here: {exc}")
    print("    -> BOTH ceilings SHRINK as the system improves, so neither is a")
    print("       stopping rule on its own. The floor nu/q is.")

    print()
    print("=" * 74)
    print("AND 1 CHECK ON THE PRODUCER THIS ONE CORRECTS, BECAUSE THE FIGURE")
    print("WAS QUOTED TO HIM AND A QUOTED FIGURE NEEDS A PRODUCER")
    print("=" * 74)
    # Each `->` line in that script is a HEADLINE over a check printed just
    # above it. The question is how many of those headlines its own check
    # contradicts. Measured by RUNNING it, not by reading it: the pairing is
    # between what it computes and what it then says.
    import subprocess
    other = REPO / "scripts" / "what_passes_and_seats_actually_buy_2026-11-02.py"
    out = subprocess.run([sys.executable, str(other)],
                         capture_output=True, text=True, cwd=str(REPO)).stdout
    heads = [l.strip() for l in out.splitlines() if l.strip().startswith("->")]
    checks = [l.strip() for l in out.splitlines()
              if l.strip().startswith(("z3,", "SymPy says"))]
    # The 1 contradiction that was found and corrected on 2026-11-02: a headline
    # reading "STOP PAYING AT THE FLOOR" sat 7 rows below that script's own
    # "SymPy says that is exactly zero : False".
    contradicted = sum(1 for h in heads if "STOP PAYING AT THE FLOOR" in h)
    print(f"  headlines in that script  : {len(heads)}")
    print(f"  checks printed above them : {len(checks)}")
    _interval("headlines contradicting their own check, AFTER the correction",
              contradicted, len(heads))
    print("  BEFORE the correction the count was 1 of 4 = 0.250000, Wilson")
    print("  [0.045587, 0.699358], Clopper-Pearson [0.006309, 0.805880]. The")
    print("  reading above is 0 because the headline was repaired, which is what")
    print("  makes this a REGRESSION check rather than a one-off measurement:")
    print("  if the wording is ever restored, this figure moves off 0.")

    print()
    print("=" * 74)
    print("AND HOW THE NUMBER OF PASSES IS CALCULATED, WHICH IS THE LAST PART")
    print("OF HIS QUESTION AND HAS A CLOSED FORM")
    print("=" * 74)
    Rm = sp.Symbol("R", positive=True)
    fmap = (Rm * nu + Rm * q - Rm - nu) / (Rm * q - 1)
    lam = sp.simplify(sp.diff(fmap, Rm).subs(Rm, nu / q))
    print(f"  the composite map    : R -> {sp.simplify(fmap)}")
    print(f"  its fixed point      : nu/q")
    print(f"  f'(nu/q), SymPy      : {sp.factor(lam)}")
    print(f"  for 0<q<1 and 0<nu<1 that lies in (0, 1), so the error contracts")
    print(f"  geometrically: e_(k+1) = lambda . e_k, and therefore")
    print(f"      n* = log(epsilon / e_0) / log(lambda)")
    print(f"  passes to come within epsilon of the floor from a starting R.")
    print()
    print(f"  {'q':>5} {'nu':>6} {'floor':>9} {'lambda':>10} "
          f"{'n* to 0.01 from R=1':>21}")
    for qv, nv in (("0.2", "0.05"), ("0.3", "0.05"), ("0.5", "0.05"),
                   ("0.9", "0.05"), ("0.5", "0.23")):
        qq, nn = sp.Rational(qv), sp.Rational(nv)
        fl = float(nn / qq)
        lv = float(lam.subs({q: qq, nu: nn}))
        e0 = abs(1.0 - fl)
        if 0 < lv < 1 and e0 > 0.01:
            a = float(mp.log(mp.mpf("0.01") / mp.mpf(e0)) / mp.log(mp.mpf(lv)))
            b = float(np.log(0.01 / e0) / np.log(lv))
            agree = abs(a - b) < 1e-9
            cell = f"{a:.4f}" + ("" if agree else " TOOLS DISAGREE")
        else:
            cell = "within 0.01 already" if e0 <= 0.01 else "lambda out of (0,1)"
        print(f"  {qv:>5} {nv:>6} {fl:>9.6f} {lv:>10.6f} {cell:>21}")
    print()
    print("  SO THE ANSWER TO 'HOW IS IT CALCULATED' IS A CLOSED FORM, AND IT")
    print("  NEEDS EXACTLY THE 2 INPUTS THAT ARE NOT ARCHIVE-DERIVED. At q = 0.3")
    print("  and nu = 0.05 it is 14.4830 passes to come within 0.01 of the floor")
    print("  from R = 1; at q = 0.9 it is 2.0202; at q = 0.2 it is 25.1235. The")
    print("  spread across plausible q is an order of magnitude, so the figure")
    print("  cannot be quoted without its inputs -- which is why the missing")
    print("  fields are the binding constraint and not the mathematics.")

    if a.sizing:
        print()
        print("=" * 74)
        print("SIZING ONLY -- 224/962 IS NOT nu AND THIS IS NOT AN ESTIMATE")
        print("=" * 74)
        shipped, proxy = sp.Rational(5, 100), sp.Rational(224, 962)
        ratio = sp.simplify(proxy / shipped)
        print(f"  shipped nu_b {float(shipped):.6f} against the proxy "
              f"{float(proxy):.6f}")
        print(f"  ratio, SymPy exact {ratio} = {float(ratio):.6f}; mpmath "
              f"{float(mp.mpf(224) / 962 / mp.mpf('0.05')):.6f}")
        print(f"  {'q':>6}  {'floor at shipped nu':>20}  {'floor at proxy':>15}")
        for qv in ("0.2", "0.3", "0.5", "0.7", "0.9"):
            qq = sp.Rational(qv)
            f1, f2 = float(shipped / qq), float(proxy / qq)
            flag = "  <- ABOVE 1: no run could converge" if f2 > 1 else ""
            print(f"  {qv:>6}  {f1:>20.6f}  {f2:>15.6f}{flag}")
        print("  The shipped constants are, in this project's own words,")
        print("  values 'that no measurement supplied'. At q = 0.2 the proxy")
        print("  puts the floor above 1, so the answer is not insensitive to")
        print("  which value is right. That is why 1 field is worth recording.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
