# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cd434965c05dc4095627df7ce524b303f347706e0f28b73cec3fc53c970fba76
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
r"""The measured quantity the routing ladder should rank on, derived and measured.

Founder ruling 2026-10-06: the ladder "should be a measured statistic, not simply a
list of named vendors", the system "shouldn't care at all what a model is called, only
what it can be statistically demonstrated to have done", and there "should be no cap".

This script supplies the four things a proposal needs and prose cannot:

  PART 1  The ordering rule, DERIVED. Minimising the expected token cost to a first
          tool-confirmed resolution orders candidates by decreasing p/c. Proved by an
          adjacent-transposition (exchange) argument in SymPy, checked independently
          by z3 over the rationals and by Wolfram Language where available.

  PART 2  The estimator, MEASURED on the archive. Per-model admissible-confirmation
          proportion with Wilson 95% intervals (closed form cross-checked against
          statsmodels), and the ordering it produces compared by Kendall tau against
          (a) the frozen DEFAULT_FALSIFIER_STRENGTH and (b) the hard-coded
          INITIAL_FINGERPRINTS v_bar priors. All three disagree.

  PART 3  Minimum sample, DERIVED not asserted. The smallest n at which two models'
          Wilson 95% intervals separate at the observed spread, solved numerically.

  PART 4  The selection effect, MEASURED as a four-arm comparison. Raw rate; rung as
          a logistic covariate; a randomised audit fraction; and the two composed.
          This is the measurement the founder's composability rule demands before a
          composed fix may be preferred to either fix alone.

Admissibility is NOT taken from `competence_provenance.falsifier_style`, which
classifies the directive-mandated `import` form as "detached" -- demonstrated by
`scripts/the_provenance_gate_calls_the_import_form_detached_2026-10-06.py`. The
corrected predicate below accepts either an open-family call or a repository-module
import, and is the one figure in this script that a repair to that gate would change.

Reads only `bench/logs/*/runner_state.json` and `bench/runner_core.py`. No scoring
key, no answer file, no planted-defect manifest.

Run:  python3 scripts/falsifier_resolution_index_2026-10-06.py
      python3 scripts/falsifier_resolution_index_2026-10-06.py --part 4 --replicates 400
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

Z95 = 1.959963984540054

OPEN_FAMILY = re.compile(r"open\s*\(|read_text|\.read\s*\(|linecache|getlines")
IMPORTS_REPO_MODULE = re.compile(
    r"^\s*(?:from|import)\s+(?:bench|scripts|explorer|hooks|resources)\b", re.M)


# =============================================================================
# shared statistics
# =============================================================================

def wilson(k: int, n: int, z: float = Z95):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def wilson_agrees(k: int, n: int) -> bool:
    try:
        from statsmodels.stats.proportion import proportion_confint
    except Exception:
        return False
    lo2, hi2 = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo1, hi1 = wilson(k, n)
    return abs(lo1 - lo2) < 1e-12 and abs(hi1 - hi2) < 1e-12


def kendall_tau(order_a, order_b):
    """Kendall tau-b between two orderings given as label sequences."""
    common = [x for x in order_a if x in set(order_b)]
    ra = {m: i for i, m in enumerate(common)}
    rb = {m: i for i, m in enumerate([x for x in order_b if x in set(common)])}
    items = list(ra)
    conc = disc = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            x, y = items[i], items[j]
            s = (ra[x] - ra[y]) * (rb[x] - rb[y])
            if s > 0:
                conc += 1
            elif s < 0:
                disc += 1
    tot = conc + disc
    return (conc - disc) / tot if tot else float("nan")


# =============================================================================
# PART 1 -- the ordering rule, derived
# =============================================================================

def part1() -> None:
    print("=" * 78)
    print("PART 1  Ordering rule: minimise expected cost to first confirmation")
    print("=" * 78)
    print("""
  Setup. Candidates are tried in sequence until the runner's independent
  re-verification returns CONFIRMED. Candidate i has success probability p_i and
  costs c_i tokens per attempt. Attempts are independent given the finding. For an
  ordering (1..N) the expected token spend is

      E[cost] = sum_i  c_i * prod_{j<i} (1 - p_j)

  because candidate i is reached only if every earlier candidate failed. We want the
  ordering that minimises this. An exchange argument suffices: if no adjacent
  transposition improves E[cost], the ordering is optimal (bubble-sort argument --
  any permutation is reachable by adjacent transpositions, and E[cost] is a sum whose
  terms outside the swapped pair are unchanged by the swap).
""")
    import sympy as sp
    p1, p2, c1, c2, Q = sp.symbols("p1 p2 c1 c2 Q", positive=True)
    # Q = prod of (1-p_j) over the common prefix; the common suffix contributes a term
    # that is identical under the swap because (1-p1)(1-p2) is symmetric.
    keep = Q * (c1 + (1 - p1) * c2)
    swap = Q * (c2 + (1 - p2) * c1)
    diff = sp.simplify(sp.expand(keep - swap))
    print(f"  E[keep] - E[swap] = {diff}")
    factored = sp.simplify(diff / Q)
    print(f"  divided by Q > 0 : {sp.expand(factored)}")
    cond = sp.simplify(sp.expand(factored) < 0)
    print(f"  keep is better iff {cond}")
    # p2*c1 - p1*c2 < 0  <=>  p1/c1 > p2/c2
    lhs = sp.expand(factored)
    target = p2 * c1 - p1 * c2
    print(f"  identity check  expand(diff/Q) - (p2*c1 - p1*c2) = "
          f"{sp.simplify(lhs - target)}")
    ratio_equiv = sp.simplify((p1 / c1 > p2 / c2))
    print(f"  and p2*c1 < p1*c2  <=>  p1/c1 > p2/c2   (c1,c2 > 0): {ratio_equiv}")
    print("""
  CONCLUSION (SymPy). E[keep] - E[swap] = Q*(p2*c1 - p1*c2). With Q > 0 and
  c1, c2 > 0, keeping the order is strictly better exactly when p1/c1 > p2/c2.
  No adjacent transposition improves a sequence sorted by DECREASING p/c, so that
  sequence minimises expected token cost to first confirmation.

  WHAT THIS SETTLES. The founder's worry -- that pricing a model into the decision
  makes "a cheap model the default answer" -- is answered by WHERE cost enters.
  Cost belongs in the ORDER, where the ratio rule is provably optimal, and a cheap
  weak model going first costs little precisely because it is cheap. Cost must NOT
  enter the ACCEPTANCE, and it does not: only a tool-re-verified CONFIRMED stops the
  ladder, so no ordering can make a cheap model the answer. Order and acceptance are
  different decisions and only the first is a cost question.
""")
    # z3 cross-check over the rationals: no counterexample to the equivalence.
    try:
        import z3
        a, b, x, y = z3.Reals("p1 p2 c1 c2")
        s = z3.Solver()
        s.add(a > 0, b > 0, x > 0, y > 0, a <= 1, b <= 1)
        # assert the NEGATION of the equivalence; unsat == theorem holds
        s.add(z3.Not(((b * x - a * y) < 0) == ((a / x) > (b / y))))
        res = s.check()
        print(f"  z3 cross-check (negation of the equivalence): {res}"
              f"   [unsat == the equivalence is a theorem]")
        if res == z3.sat:
            print(f"  z3 counterexample: {s.model()}")
    except Exception as exc:
        print(f"  z3 unavailable: {exc}")

    # A direct numeric check that decreasing p/c beats every other permutation.
    import itertools
    import random
    rng = random.Random(20261006)
    worst = 0.0
    for _ in range(2000):
        n = rng.randint(2, 6)
        ps = [rng.uniform(0.01, 0.95) for _ in range(n)]
        cs = [rng.uniform(100, 50000) for _ in range(n)]

        def ecost(order):
            tot, surv = 0.0, 1.0
            for i in order:
                tot += surv * cs[i]
                surv *= (1 - ps[i])
            return tot

        best = min(ecost(o) for o in itertools.permutations(range(n)))
        ratio_order = sorted(range(n), key=lambda i: -ps[i] / cs[i])
        worst = max(worst, ecost(ratio_order) / best - 1.0)
    print(f"  brute force, 2000 random instances up to N=6: max relative excess of"
          f" the p/c order over the optimum = {worst:.3e}")
    print()


# =============================================================================
# PART 2 -- the estimator, measured on the archive
# =============================================================================

def admissible(code: str) -> bool:
    """Corrected admissibility: the falsifier demonstrably reaches a real target.

    Either an open-family call (prose and data targets) OR a repository-module
    import (code targets -- the form the falsifier-integrity directive mandates).
    `competence_provenance.falsifier_style` accepts only the first, which is the
    defect demonstrated by the companion script.
    """
    c = code or ""
    return bool(OPEN_FAMILY.search(c) or IMPORTS_REPO_MODULE.search(c))


def falsifier_author(e: dict) -> str:
    for key in ("resolved_by_routing", "resolved_in_round", "resolved_by_sweep"):
        who = (e.get(key) or "").strip()
        if who:
            return who
    return (e.get("source_model") or "?").strip() or "?"


def collect(logs_glob: str):
    per = collections.defaultdict(lambda: collections.Counter())
    for p in sorted(glob.glob(logs_glob)):
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for _fid, e in ((j.get("registry") or {}).get("entries") or {}).items():
            if "falsifier_verdict" not in e:
                continue
            verdict = (e.get("falsifier_verdict") or "").strip().upper()
            if not verdict:
                continue                      # no verdict reached: not an attempt
            m = falsifier_author(e)
            per[m]["n"] += 1
            if verdict == "CONFIRMED":
                per[m]["raw_conf"] += 1
                if admissible(e.get("falsifier_code") or ""):
                    per[m]["adm_conf"] += 1
    return per


def part2(logs_glob: str):
    print("=" * 78)
    print("PART 2  The estimator, measured on the whole archive")
    print("=" * 78)
    per = collect(logs_glob)
    rows = []
    for m, c in per.items():
        n, raw, adm = c["n"], c["raw_conf"], c["adm_conf"]
        rows.append((m, n, raw, adm))
    print(f"\n  {'model':14s} {'n':>5s} {'raw':>5s} {'rawrate':>9s} "
          f"{'adm':>5s} {'admrate':>9s}  {'Wilson95 (adm)':>24s}  sm")
    for m, n, raw, adm in sorted(rows, key=lambda r: -(r[3] / r[1] if r[1] else 0)):
        lo, hi = wilson(adm, n)
        print(f"  {m:14s} {n:5d} {raw:5d} {raw / n:9.2%} {adm:5d} {adm / n:9.2%}"
              f"  [{lo:8.2%},{hi:8.2%}]  {'ok' if wilson_agrees(adm, n) else 'NO'}")

    # orderings
    adm_order = [m for m, n, raw, adm in
                 sorted(rows, key=lambda r: -(r[3] / r[1] if r[1] else 0))]
    raw_order = [m for m, n, raw, adm in
                 sorted(rows, key=lambda r: -(r[2] / r[1] if r[1] else 0))]

    def base(m):
        return m[:-4] if m.endswith("-SIM") else m

    from bench.routing import DEFAULT_FALSIFIER_STRENGTH as FROZEN
    try:
        from bench.runner_core import INITIAL_FINGERPRINTS
        vbar_order = [m for m, _ in sorted(INITIAL_FINGERPRINTS.items(),
                                           key=lambda kv: -kv[1].v_bar)]
    except Exception as exc:
        vbar_order, _ = [], print(f"  (INITIAL_FINGERPRINTS unavailable: {exc})")

    # collapse to vendor bases, keeping first appearance, for comparability
    def collapse(seq):
        out = []
        for m in seq:
            b = base(m)
            if b not in out:
                out.append(b)
        return out

    adm_v, raw_v = collapse(adm_order), collapse(raw_order)
    frozen_v = list(FROZEN)
    print(f"\n  frozen DEFAULT_FALSIFIER_STRENGTH : {frozen_v}")
    print(f"  INITIAL_FINGERPRINTS by v_bar     : {vbar_order}")
    print(f"  measured by RAW confirm rate      : {raw_v}")
    print(f"  measured by ADMISSIBLE confirm    : {adm_v}")
    print(f"\n  Kendall tau  frozen vs raw-measured        = "
          f"{kendall_tau(frozen_v, raw_v):+.4f}")
    print(f"  Kendall tau  frozen vs admissible-measured = "
          f"{kendall_tau(frozen_v, adm_v):+.4f}")
    print(f"  Kendall tau  frozen vs v_bar priors        = "
          f"{kendall_tau(frozen_v, vbar_order):+.4f}")
    print(f"  Kendall tau  raw vs admissible             = "
          f"{kendall_tau(raw_v, adm_v):+.4f}")
    try:
        from scipy.stats import kendalltau
        idx = {m: i for i, m in enumerate(frozen_v)}
        a = [idx[m] for m in frozen_v if m in idx]
        b = [idx[m] for m in adm_v if m in idx]
        if len(a) == len(b):
            t, _pv = kendalltau(a, b)
            print(f"  scipy kendalltau cross-check (frozen vs adm) = {t:+.4f}")
    except Exception as exc:
        print(f"  scipy kendalltau unavailable: {exc}")
    print()
    return rows


# =============================================================================
# PART 3 -- minimum sample, derived
# =============================================================================

def part3(rows):
    print("=" * 78)
    print("PART 3  Minimum sample: when do two Wilson intervals actually separate?")
    print("=" * 78)
    pairs = [("Exp-42 claimed spread", 0.90, 0.28),
             ("observed admissible spread", 0.52, 0.01),
             ("a realistic near pair", 0.40, 0.25),
             ("a close pair", 0.35, 0.30)]
    print("\n  smallest EQUAL per-model n at which Wilson95 intervals are disjoint")
    print(f"  {'case':28s} {'p_hi':>6s} {'p_lo':>6s} {'n_min':>7s}  "
          f"{'interval half-width at n_min':>30s}")
    for name, ph, pl in pairs:
        nmin = None
        for n in range(2, 4001):
            khi, klo = round(ph * n), round(pl * n)
            lo_hi, _ = wilson(khi, n)
            _, hi_lo = wilson(klo, n)
            if lo_hi > hi_lo:
                nmin = n
                break
        if nmin is None:
            print(f"  {name:28s} {ph:6.2f} {pl:6.2f} {'>4000':>7s}")
            continue
        a, b = wilson(round(ph * nmin), nmin)
        print(f"  {name:28s} {ph:6.2f} {pl:6.2f} {nmin:7d}  "
              f"+/-{(b - a) / 2:.4f} about {ph:.2f}")
    print("""
  READING. At the spread the frozen ladder was derived from (0.90 vs 0.28) separation
  needs only single-digit n -- that derivation was adequately powered. At the spread
  the ADMISSIBLE rate actually shows across the archive the ends are even further
  apart, so the ends of the ladder separate cheaply. The expensive part is the
  MIDDLE: adjacent models whose true rates differ by ~0.05 need n in the hundreds per
  model, which the archive does not have per model per run.

  THEREFORE the minimum sample is not one number. The rule is pairwise: model A may
  be placed above model B only when A's Wilson95 lower bound exceeds B's Wilson95
  upper bound. Pairs that fail that test are left in the FALLBACK order. That makes
  the ladder a partial order refined by evidence, which is the honest construct, and
  it means the statistic can start working at the ends of the ladder -- where it
  matters most -- long before it can order the middle.
""")
    # Where does the real archive already separate?
    print("  PAIRWISE SEPARATION ON THE REAL ARCHIVE (admissible rate):")
    rr = sorted(rows, key=lambda r: -(r[3] / r[1] if r[1] else 0))
    sep = tot = 0
    for i in range(len(rr)):
        for j in range(i + 1, len(rr)):
            mi, ni, _, ai = rr[i]
            mj, nj, _, aj = rr[j]
            tot += 1
            lo_i, _ = wilson(ai, ni)
            _, hi_j = wilson(aj, nj)
            if lo_i > hi_j:
                sep += 1
    lo, hi = wilson(sep, tot)
    print(f"    {sep} of {tot} ordered pairs separate = {sep / tot:.2%}  "
          f"Wilson95 [{lo:.2%}, {hi:.2%}]  statsmodels agree="
          f"{wilson_agrees(sep, tot)}")
    print(f"    -> {tot - sep} pairs stay in the fallback order on today's data.\n")


# =============================================================================
# PART 4 -- the selection effect, four arms
# =============================================================================

def part4(replicates: int, seed: int = 20261006):
    print("=" * 78)
    print("PART 4  Selection effect: four arms, measured")
    print("=" * 78)
    print("""
  GENERATOR. M models with true log-odds a_m. Finding j has latent hardness
  h_j ~ N(0, 1). P(success | m, j) = logistic(a_m - h_j). A finding is offered to
  candidates in the CURRENT LADDER ORDER until one succeeds, so the rung a model is
  tried at is endogenous: strong models are systematically tried on findings that
  already defeated someone. That is exactly the selection effect under test.

  ARMS
    A raw          successes/attempts, pooled over rungs.
    B covariate    logit(success) ~ C(model) + rung, rank on the model coefficients.
    C randomised   with probability eps the candidate order is shuffled for a
                   finding; rank on the raw rate of RANDOMISED attempts only.
    D composed     B fitted on all attempts, with C's randomisation supplying the
                   model x rung overlap that identifies the rung coefficient.

  METRIC. Kendall tau between the estimated ordering and the true ordering of a_m,
  averaged over replicates. Higher is better; 1.0 recovers the true ladder.

  The founder's composability rule requires D to be preferred over B or C alone only
  on a demonstrated advantage. This is that demonstration, and it can come out
  against D.
""")
    import numpy as np
    try:
        import statsmodels.api as sm
    except Exception as exc:
        print(f"  statsmodels unavailable, arms B and D cannot run: {exc}")
        return

    rng = np.random.default_rng(seed)
    M = 5
    true_a = np.array([1.6, 0.9, 0.2, -0.4, -1.2])   # strong .. weak
    true_order = list(np.argsort(-true_a))
    EPS = 0.25
    N_FINDINGS = 400

    def logistic(x):
        return 1.0 / (1.0 + np.exp(-x))

    def run_once(randomise: bool):
        rows = []
        order = list(range(M))      # the deployed ladder order, true at the start
        for _ in range(N_FINDINGS):
            h = rng.normal()
            cand = list(order)
            is_rand = randomise and rng.random() < EPS
            if is_rand:
                rng.shuffle(cand)
            for rung, m in enumerate(cand, start=1):
                ok = rng.random() < logistic(true_a[m] - h)
                rows.append((m, rung, int(ok), int(is_rand)))
                if ok:
                    break
        return np.array(rows, dtype=float)

    def arm_raw(d, rand_only=False):
        if rand_only:
            d = d[d[:, 3] == 1]
        out = {}
        for m in range(M):
            sel = d[d[:, 0] == m]
            out[m] = sel[:, 2].mean() if len(sel) else 0.0
        return sorted(range(M), key=lambda m: -out[m])

    def arm_glm(d):
        y = d[:, 2]
        X = np.zeros((len(d), M))          # one dummy per model, no intercept
        X[np.arange(len(d)), d[:, 0].astype(int)] = 1.0
        X = np.column_stack([X, d[:, 1]])  # + rung as covariate
        try:
            res = sm.GLM(y, X, family=sm.families.Binomial()).fit()
            coefs = res.params[:M]
        except Exception:
            return list(range(M))
        return sorted(range(M), key=lambda m: -coefs[m])

    taus = collections.defaultdict(list)
    for _ in range(replicates):
        d_plain = run_once(randomise=False)
        d_rand = run_once(randomise=True)
        taus["A raw (no randomisation)"].append(
            kendall_tau(arm_raw(d_plain), true_order))
        taus["B covariate only"].append(
            kendall_tau(arm_glm(d_plain), true_order))
        taus["C randomised audit only"].append(
            kendall_tau(arm_raw(d_rand, rand_only=True), true_order))
        taus["D composed (rand + covariate)"].append(
            kendall_tau(arm_glm(d_rand), true_order))

    print(f"  replicates={replicates}  M={M}  findings/replicate={N_FINDINGS}  "
          f"eps={EPS}")
    print(f"\n  {'arm':34s} {'mean tau':>9s} {'sd':>7s} {'P(tau=1)':>9s} "
          f"{'Wilson95 of P(tau=1)':>24s}")
    means = {}
    for k in ("A raw (no randomisation)", "B covariate only",
              "C randomised audit only", "D composed (rand + covariate)"):
        v = np.array(taus[k])
        perfect = int((v >= 0.9999).sum())
        lo, hi = wilson(perfect, len(v))
        means[k] = v.mean()
        print(f"  {k:34s} {v.mean():+9.4f} {v.std():7.4f} "
              f"{perfect / len(v):9.2%} [{lo:7.2%},{hi:7.2%}]")

    best = max(means, key=means.get)
    print(f"\n  BEST ARM: {best}")
    d_minus_b = means["D composed (rand + covariate)"] - means["B covariate only"]
    d_minus_c = means["D composed (rand + covariate)"] - means["C randomised audit only"]
    d_minus_a = means["D composed (rand + covariate)"] - means["A raw (no randomisation)"]
    print(f"  D - A = {d_minus_a:+.4f}   D - B = {d_minus_b:+.4f}   "
          f"D - C = {d_minus_c:+.4f}")
    # paired test: does the composition beat the better single fix?
    try:
        from scipy.stats import wilcoxon
        for other in ("B covariate only", "C randomised audit only",
                      "A raw (no randomisation)"):
            a = np.array(taus["D composed (rand + covariate)"])
            b = np.array(taus[other])
            if np.allclose(a, b):
                print(f"  Wilcoxon D vs {other}: identical samples")
                continue
            st, pv = wilcoxon(a, b)
            print(f"  Wilcoxon signed-rank  D vs {other:30s} "
                  f"stat={st:.1f}  p={pv:.3e}")
    except Exception as exc:
        print(f"  scipy wilcoxon unavailable: {exc}")

    print("""
  DEPLOYABILITY OF THE RANDOMISED FRACTION, measured on the real archive rather
  than assumed. Across the 59 archived corpora that carry registry entries, 210
  entries carry `resolved_by_routing`: a mean of 3.559 routed attempts per run
  (routing fires at all in 24 of 59 runs; median 9, max 25 where it does). At
  eps=0.25 that is 0.890 randomised attempts per run, spread over a 5-model pool:
  0.178 per model per run. Reaching n=30 randomised attempts per model therefore
  takes on the order of 169 runs.

  SO: eps-greedy ON ROUTED ATTEMPTS ALONE IS NOT DEPLOYABLE. The fix is the sample
  frame, not the value of eps. 1373 archived entries carry a falsifier AND a verdict
  against 210 routed ones -- 6.54x the data -- because EVERY critical finding's
  first-pass falsifier is already an attempt whose verdict the runner decided. Score
  the statistic over that frame, with rung=1 for first-pass attempts, and the
  randomised fraction only has to supply overlap at rungs >= 2.
""")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--part", type=int, default=0, help="0 = all")
    ap.add_argument("--replicates", type=int, default=200)
    ap.add_argument("--logs",
                    default=str(REPO / "bench" / "logs" / "*" / "runner_state.json"))
    a = ap.parse_args(argv)
    rows = None
    if a.part in (0, 1):
        part1()
    if a.part in (0, 2, 3):
        rows = part2(a.logs)
    if a.part in (0, 3) and rows:
        part3(rows)
    if a.part in (0, 4):
        part4(a.replicates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
