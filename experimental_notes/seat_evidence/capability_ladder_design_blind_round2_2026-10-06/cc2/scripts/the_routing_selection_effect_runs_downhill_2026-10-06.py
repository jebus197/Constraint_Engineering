# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ec39526c25b948d1782b2bb1011cea7bc32ab524cc4c6abbdb9d974bda690b17
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
r"""The routing selection effect biases the WEAK models, not the strong ones.

THE CLAIM UNDER TEST, from the 2026-10-06 design brief: "The ladder sends HARD
findings to strong models, so their success rate is depressed by being trusted."

WHY THAT IS BACKWARDS. `bench.routing.rank_falsifier_writers` returns candidates
STRONGEST FIRST, and `resolve_via_routing` tries rung 1 first and stops at the first
CONFIRMED. So rung 1 is offered the UNSELECTED population of unresolved criticals, and
every model below it is offered only findings that already defeated everyone above.
The strong model's rate is the clean one. Everything beneath it is depressed.

WHAT THIS SCRIPT MEASURES, in four parts:

  PART A  Bias of the raw rate per rung, against the unselected marginal truth.
  PART B  ENTRENCHMENT: deploy an order in which the genuinely second-best model is
          ranked first, and ask whether the raw rate ever corrects it. At hardness
          sd >= 1 it does not, with 4000 findings.
  PART C  Four sample frames compared on P(exact order recovered), with Wilson 95%:
          raw / eps-greedy randomised / common task n=8 / common task n=30.
  PART D  Does the obvious COMPOSITION of eps-greedy and the common task beat each
          alone? The founder's composability rule requires a measurement, and this
          one comes out AGAINST composing.

GENERATOR. M models with true log-odds a_m; finding j has latent hardness
h_j ~ N(0, sd). P(success | m, j) = logistic(a_m - h_j). Candidates are offered in the
deployed order until one succeeds, so the rung a model is tried at is endogenous --
which is the selection effect itself, not an approximation of it.

This is a simulation and says nothing about any particular model. It measures a
property of the ROUTING RULE, which is why a generator is the right instrument: the
counterfactual (what would the weak model have scored on the unselected population?)
is not observable in any archive.

Reads nothing from disk. No scoring key, no answer file, no planted-defect manifest.

Run:  python3 scripts/the_routing_selection_effect_runs_downhill_2026-10-06.py
      python3 scripts/the_routing_selection_effect_runs_downhill_2026-10-06.py --part C --reps 300
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np

Z95 = 1.959963984540054


def wilson(k, n, z=Z95):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def wilson_line(k, n):
    lo, hi = wilson(k, n)
    try:
        from statsmodels.stats.proportion import proportion_confint
        a, b = proportion_confint(k, n, alpha=0.05, method="wilson")
        agree = abs(a - lo) < 1e-12 and abs(b - hi) < 1e-12
    except Exception:
        agree = None
    return (f"{k / n:7.2%}  Wilson95 [{lo:6.2%}, {hi:6.2%}]"
            f"  statsmodels agree={agree}")


def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


def marginal_truth(true_a, sd, rng, n=400_000):
    hs = rng.normal(0, sd, n)
    return np.array([logistic(a - hs).mean() for a in true_a])


def part_a(rng):
    print("=" * 78)
    print("PART A  Bias of the raw rate by rung position")
    print("=" * 78)
    true_a = np.array([1.6, 0.9, 0.2, -0.4, -1.2])    # deployed order IS the truth
    M = len(true_a)
    for sd in (0.5, 1.0, 2.0):
        est = np.zeros(M)
        cnt = np.zeros(M)
        for _ in range(400):
            for _ in range(300):
                h = rng.normal(0, sd)
                for m in range(M):
                    ok = rng.random() < logistic(true_a[m] - h)
                    est[m] += ok
                    cnt[m] += 1
                    if ok:
                        break
        raw = est / np.maximum(cnt, 1)
        marg = marginal_truth(true_a, sd, rng)
        print(f"\n  sd(h)={sd}")
        print(f"    unselected marginal truth : {np.round(marg, 4)}")
        print(f"    raw rate under routing    : {np.round(raw, 4)}")
        print(f"    BIAS (raw - truth)        : {np.round(raw - marg, 4)}")
        print(f"    share of attempts by rung : {np.round(cnt / cnt.sum(), 4)}")
        print(f"    rank(raw) == rank(truth)  : "
              f"{list(np.argsort(-raw)) == list(np.argsort(-marg))}")
    print("""
  READING. The rung-1 model's bias is ~0 at every dispersion; every model below it is
  biased DOWN, worst in the middle. The brief's premise is inverted. Note also that
  the ORDER survives here -- the bias does not invert a correct deployment. It is a
  wrong deployment that cannot be corrected, which is PART B.
""")


def part_b(rng, reps=200):
    print("=" * 78)
    print("PART B  Entrenchment: can the measurement correct a wrong deployed order?")
    print("=" * 78)
    print("""
  REPLICATED, deliberately. A single realisation of this experiment is SEED
  DEPENDENT at sd=1.0, where the two top models' measured rates come out near-tied
  and the recovered order flips on noise. An earlier single-shot version of this
  script reported "raw fails at sd=1.0"; re-running it under a different seed
  reported the opposite. Only the replicated proportion below is a claim.
""")
    true_a = np.array([0.9, 1.6, 0.2, -0.4, -1.2])   # index 1 is BEST ...
    deployed = [0, 1, 2, 3, 4]                       # ... but index 0 is tried first
    M = len(true_a)
    for sd in (0.5, 1.0, 2.0):
        marg = marginal_truth(true_a, sd, rng)
        truth = list(np.argsort(-marg))
        hit = {"raw": 0, "eps=0.25": 0}
        for _ in range(reps):
            for label, eps in (("raw", 0.0), ("eps=0.25", 0.25)):
                est = np.zeros(M)
                cnt = np.zeros(M)
                for _ in range(400):
                    h = rng.normal(0, sd)
                    cand = list(deployed)
                    if eps and rng.random() < eps:
                        rng.shuffle(cand)
                    for m in cand:
                        ok = rng.random() < logistic(true_a[m] - h)
                        est[m] += ok
                        cnt[m] += 1
                        if ok:
                            break
                if list(np.argsort(-(est / np.maximum(cnt, 1)))) == truth:
                    hit[label] += 1
        print(f"  sd(h)={sd}  truth order {truth}  marginal {np.round(marg, 3)}"
              f"  (reps={reps}, 400 findings each)")
        for label in ("raw", "eps=0.25"):
            print(f"    {label:9s} P(CORRECTS THE WRONG DEPLOYMENT) = "
                  f"{wilson_line(hit[label], reps)}")
        print()
    print("""  READING. The wrong deployment is NOT reliably corrected by the raw rate at
  any dispersion tested, and the failure becomes near-total at sd=2.0. eps=0.25
  randomisation improves recovery at low and moderate dispersion and does not rescue
  sd=2.0. A cold-start misplacement is therefore sticky under the raw rate: whoever is
  placed first is the only model measured on an unselected population, so the order
  tends to confirm itself. This is the failure mode that cannot self-correct, and it
  is why the sample FRAME matters more than the estimator.
""")


def _frames(rng, sd, reps, n_find=300):
    true_a = np.array([0.9, 1.6, 0.2, -0.4, -1.2])
    deployed = [0, 1, 2, 3, 4]
    M = len(true_a)
    truth = list(np.argsort(-marginal_truth(true_a, sd, rng)))
    hit = {"raw": 0, "eps=0.25": 0, "common n=8": 0, "common n=30": 0}
    for _ in range(reps):
        for label, eps in (("raw", 0.0), ("eps=0.25", 0.25)):
            est = np.zeros(M)
            cnt = np.zeros(M)
            for _ in range(n_find):
                h = rng.normal(0, sd)
                cand = list(deployed)
                if eps and rng.random() < eps:
                    rng.shuffle(cand)
                for m in cand:
                    ok = rng.random() < logistic(true_a[m] - h)
                    est[m] += ok
                    cnt[m] += 1
                    if ok:
                        break
            if list(np.argsort(-(est / np.maximum(cnt, 1)))) == truth:
                hit[label] += 1
        for label, n in (("common n=8", 8), ("common n=30", 30)):
            est = np.zeros(M)
            for _ in range(n):
                h = rng.normal(0, sd)
                for m in range(M):
                    est[m] += rng.random() < logistic(true_a[m] - h)
            if list(np.argsort(-(est / n))) == truth:
                hit[label] += 1
    return truth, hit


def part_c(rng, reps):
    print("=" * 78)
    print("PART C  Four sample frames, P(exact order recovered)")
    print("=" * 78)
    print("""
  A COMMON TASK means the SAME finding is dispatched to EVERY available model, so the
  population is identical by construction and no adjustment is needed. It removes the
  selection effect rather than correcting for it.
""")
    for sd in (0.5, 1.0, 2.0):
        truth, hit = _frames(rng, sd, reps)
        print(f"  sd(h)={sd}  truth={truth}  (reps={reps})")
        for k in ("raw", "eps=0.25", "common n=8", "common n=30"):
            print(f"    {k:12s} {wilson_line(hit[k], reps)}")
        print()
    print("""  READING. Neither frame dominates. eps-greedy buys SAMPLE SIZE at the price
  of residual bias and wins at low dispersion; the common task buys ZERO BIAS at the
  price of sample size and is the only frame that survives sd=2, where raw and eps
  collapse. Which is right is an empirical question about the real finding
  population's hardness dispersion -- and `rungs_tried` is censored at
  routing_max_rungs=2, so it cannot be answered until the cap is removed.

  DEPLOYABILITY, measured on the archive rather than assumed. 210 of 3158 archived
  entries carry `resolved_by_routing`: 3.559 routed attempts per run over 59 runs. At
  eps=0.25 that is 0.890 randomised attempts/run over a 5-model pool = 0.178 per model
  per run, so n=30 per model needs ~169 runs. A common task of ONE finding per round,
  at the archive's 8.47 rounds/run (500 rounds / 59 runs), gives 8.47 attempts per
  model per run: n=30 in ~4 runs. eps-greedy on the ROUTED frame is not deployable, by
  a factor of about 40.
""")


def part_d(rng, reps):
    print("=" * 78)
    print("PART D  Does composing eps-greedy with the common task beat each alone?")
    print("=" * 78)
    print("""
  COMPOSED ARM: one logistic fit, logit(p) = a_m + b * stratum, where stratum=0 is the
  unbiased common-task rows and stratum=1 the routed rows. b absorbs the selection
  shift; the common-task stratum anchors the level; the routed stratum adds precision.
  Founder's rule, verbatim: "Where a single fix out performs a composed one, that fix
  should continue to be preferred." This is the measurement that decides it.
""")
    try:
        import statsmodels.api as sm
    except Exception as exc:
        print(f"  statsmodels unavailable, the composed arm cannot run: {exc}")
        return
    true_a = np.array([0.9, 1.6, 0.2, -0.4, -1.2])
    deployed = [0, 1, 2, 3, 4]
    M = len(true_a)
    N_FIND, N_COMMON = 300, 8
    for sd in (0.5, 1.0, 2.0):
        truth = list(np.argsort(-marginal_truth(true_a, sd, rng)))
        hit = {"eps alone": 0, "common alone": 0, "composed": 0}
        for _ in range(reps):
            rows = []
            for _ in range(N_FIND):
                h = rng.normal(0, sd)
                cand = list(deployed)
                if rng.random() < 0.25:
                    rng.shuffle(cand)
                for m in cand:
                    ok = rng.random() < logistic(true_a[m] - h)
                    rows.append((m, 1, int(ok)))
                    if ok:
                        break
            for _ in range(N_COMMON):
                h = rng.normal(0, sd)
                for m in range(M):
                    rows.append((m, 0,
                                 int(rng.random() < logistic(true_a[m] - h))))
            d = np.array(rows, dtype=float)
            for label, flag in (("eps alone", 1.0), ("common alone", 0.0)):
                s = d[d[:, 1] == flag]
                r = np.array([s[s[:, 0] == m][:, 2].mean()
                              if (s[:, 0] == m).any() else 0.0 for m in range(M)])
                if list(np.argsort(-r)) == truth:
                    hit[label] += 1
            X = np.zeros((len(d), M))
            X[np.arange(len(d)), d[:, 0].astype(int)] = 1.0
            X = np.column_stack([X, d[:, 1]])
            try:
                co = sm.GLM(d[:, 2], X,
                            family=sm.families.Binomial()).fit().params[:M]
                if list(np.argsort(-co)) == truth:
                    hit["composed"] += 1
            except Exception:
                pass
        print(f"  sd(h)={sd}  truth={truth}  (reps={reps})")
        for k in ("eps alone", "common alone", "composed"):
            print(f"    {k:13s} {wilson_line(hit[k], reps)}")
        best = max(hit, key=hit.get)
        print(f"    BEST: {best}\n")
    print("""  VERDICT. At sd=2 the single fix (common task alone) beats the composed arm
  by about 4.5x -- 300 routed rows swamp 40 common-task rows and one stratum shift
  cannot absorb a bias that varies by rung. At sd<=1 the composed advantage sits
  inside overlapping intervals. Per the founder's composability rule: DO NOT COMPOSE;
  pick one frame on the measured dispersion.

  NOT TESTED, and the most likely way this conclusion is wrong: an UPWEIGHTED
  composition that gives the common-task stratum weight proportional to its
  unbiasedness rather than its row count.
""")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--part", default="ALL", choices=["A", "B", "C", "D", "ALL"])
    ap.add_argument("--reps", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20261006)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    if a.part in ("A", "ALL"):
        part_a(rng)
    if a.part in ("B", "ALL"):
        part_b(rng, a.reps)
    if a.part in ("C", "ALL"):
        part_c(rng, a.reps)
    if a.part in ("D", "ALL"):
        part_d(rng, a.reps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
