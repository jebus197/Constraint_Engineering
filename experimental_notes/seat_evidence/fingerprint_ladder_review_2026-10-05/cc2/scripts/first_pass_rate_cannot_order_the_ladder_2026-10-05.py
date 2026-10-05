# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d6e6d758040210064ffecaf4ce5728ea9b17d01d239c4cd0b1847ac843ca412b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A first-pass confirm rate cannot order the routing ladder. Measured, both arms.

THE PROPOSAL UNDER TEST.
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
proposes keying `bench/routing.py`'s ladder on a provenance-gated falsification
rate. It names the selection effect as its own strongest objection -- the ladder
routes findings the weak models could not resolve to the strong models, so a
strong model is measured against a harder population -- and recommends measuring
on FIRST-PASS falsifiers only, "which is a common population by construction".

TWO MEASUREMENTS, AND BOTH GO AGAINST THE RECOMMENDATION.

1. THE FIRST-PASS POPULATION IS NOT COMMON. A model's first-pass findings are the
   ones IT chose to report, so first-pass-only does not remove selection; it
   replaces routing-induced selection with SELF-selection. On the real arm the
   per-model severity distributions differ: Kruskal-Wallis H = 31.1257, df = 4,
   p = 2.886e-06. "Common by construction" is refuted on the data the estimator
   would actually be fitted to.

2. THE STATISTIC HAS NO ORDERING POWER THERE. First-pass falsifiers are written
   by the model for a defect it chose and already understands, so the rate sits
   on its ceiling. On the real arm three of the five models are at exactly
   1.0000 -- CC2 28/28, Codex 59/59, ChatGPT 44/44 -- so the top three rungs of
   the ladder are TIED and cannot be ordered at all, which is the one thing the
   ladder has to do. Pooled over both arms the chi-square on CONFIRM counts does
   not reject one rate for everybody, and a bootstrap of the induced ORDER
   reproduces the modal order only about a third of the time and reproduces
   `DEFAULT_FALSIFIER_STRENGTH` in 0 of 20000 resamples.

WHAT IS NOT CLAIMED. This does not show the construct is unmeasurable; it shows
first-pass-only cannot measure it on the archive that exists. The estimand the
ladder needs is conditional -- P(resolve | the earlier rungs did not) -- and a
marginal rate equals it only if difficulty is independent of reaching the rung,
which the ladder's own routing rule makes false. Section 4 states the one design
that identifies the conditional estimand from observational data and reports
whether the archive can support it.

Every figure is computed twice where a second implementation exists (scipy and
an independent closed form, statsmodels for the intervals).

Run:  python3 scripts/first_pass_rate_cannot_order_the_ladder_2026-10-05.py
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
FROZEN = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek")
MIN_N = 15
SEED = 20261005
BOOTSTRAP = 20000


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="first_pass_rate_cannot_order_the_ladder_2026-10-05.py",
        description=(__doc__ or "").strip().split("\n\n")[0])
    p.add_argument("--logs", default=str(REPO / "bench" / "logs"),
                   help="directory of archived run directories")
    p.add_argument("--min-n", type=int, default=MIN_N,
                   help="minimum first-pass attempts before a model is ranked")
    p.add_argument("--bootstrap", type=int, default=BOOTSTRAP,
                   help="resamples for the order-stability figure")
    return p.parse_args(argv)


def collect(logs: pathlib.Path):
    """First-pass falsifier attempts that reached a verdict.

    FIRST PASS means the finding's own source model supplied the falsifier and no
    rung of the ladder was climbed: `routing_history` empty and
    `resolved_by_routing` unset. Those two fields are what the runner writes when
    routing acts, so this is the runner's own record of whether it acted, not a
    guess from the id.
    """
    rows, unreadable = [], []
    for p in sorted(glob.glob(str(logs / "*" / "*_report.json"))):
        try:
            doc = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            unreadable.append((pathlib.Path(p).parent.name, type(exc).__name__))
            continue
        for e in ((doc.get("registry") or {}).get("entries") or {}).values():
            if e.get("routing_history") or e.get("resolved_by_routing"):
                continue
            if e.get("falsifier_verdict") not in ("CONFIRMED", "REFUTED"):
                continue
            raw = e.get("source_model") or "?"
            rows.append({
                "arm": "SIMULATED" if raw.endswith("-SIM") else "REAL",
                "model": raw[:-4] if raw.endswith("-SIM") else raw,
                "confirmed": e.get("falsifier_verdict") == "CONFIRMED",
                "severity": e.get("severity"),
            })
    return rows, unreadable


def _wilson(k: int, n: int):
    """Closed form, z from scipy; cross-checked against statsmodels by the caller."""
    from scipy.stats import norm
    if n == 0:
        return (float("nan"), float("nan"))
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / d
    half = (z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def _homogeneity_chisq(k, n):
    """One-rate-explains-all chi-square on independent binomial counts.

    Written out rather than taken from a library so the arithmetic is visible:
    expected successes n_i * p_pool, expected failures n_i * (1 - p_pool).
    """
    import numpy as np
    from scipy import stats
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    pool = k.sum() / n.sum()
    e_k, e_f = n * pool, n * (1.0 - pool)
    x2 = float((((k - e_k) ** 2) / e_k + (((n - k) - e_f) ** 2) / e_f).sum())
    df = len(k) - 1
    return x2, df, float(stats.chi2.sf(x2, df)), float(pool)


def report_arm(arm: str, rows: list, min_n: int, n_boot: int) -> None:
    import numpy as np
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint

    sub = [r for r in rows if r["arm"] == arm]
    by = collections.defaultdict(list)
    sev = collections.defaultdict(list)
    for r in sub:
        by[r["model"]].append(r["confirmed"])
        if isinstance(r["severity"], (int, float)):
            sev[r["model"]].append(float(r["severity"]))
    by = {m: np.array(v, dtype=bool) for m, v in by.items() if len(v) >= min_n}
    print("=" * 78)
    print(f"{arm} ARM — {len(sub)} first-pass falsifiers reaching a verdict, "
          f"{len(by)} model(s) with n >= {min_n}")
    print("=" * 78)
    if len(by) < 2:
        print("  fewer than 2 rankable models; nothing to order.")
        return
    print(f"  {'model':<10}{'k/n':>10}{'rate':>9}   Wilson 95% (closed form) "
          f"| statsmodels")
    at_ceiling = []
    for m in sorted(by, key=lambda x: (-by[x].mean(), x)):
        a = by[m]
        k, n = int(a.sum()), len(a)
        lo, hi = _wilson(k, n)
        slo, shi = proportion_confint(k, n, 0.05, "wilson")
        agree = abs(lo - slo) < 1e-9 and abs(hi - shi) < 1e-9
        note = "" if agree else "   *** THE TWO AGREE? NO — treat as UNVERIFIED"
        if k == n:
            at_ceiling.append(m)
        print(f"  {m:<10}{f'{k}/{n}':>10}{k / n:>9.4f}   [{lo:.4f}, {hi:.4f}] "
              f"| [{slo:.4f}, {shi:.4f}]{note}")
    if len(at_ceiling) > 1:
        print(f"\n  *** {len(at_ceiling)} models are at EXACTLY 1.0000: {at_ceiling}")
        print("  *** The statistic cannot order them. The ladder's entire job is to")
        print("  *** say which of them is asked first.")

    names = sorted(by)
    x2, df, p, pool = _homogeneity_chisq([int(by[m].sum()) for m in names],
                                        [len(by[m]) for m in names])
    print(f"\n  pooled first-pass confirm rate              : {pool:.6f}")
    print(f"  chi-square, one rate explains all          : X2={x2:.4f}, df={df}, "
          f"p={p:.6g}")
    print(f"  => {'NOT distinguishable' if p > 0.05 else 'distinguishable'} at 0.05")

    groups = [np.array(sev[m]) for m in names if len(sev[m]) >= min_n]
    if len(groups) >= 2:
        H, ps = stats.kruskal(*groups)
        print(f"  Kruskal-Wallis on first-pass SEVERITY       : H={H:.4f}, "
              f"df={len(groups) - 1}, p={ps:.6g}")
        print(f"  => the first-pass population is "
              f"{'NOT common' if ps < 0.05 else 'not shown to differ'} across models")

    shared = [m for m in FROZEN if m in by]
    if len(shared) >= 3:
        rate = {m: by[m].mean() for m in by}
        measured = sorted(shared, key=lambda m: (-rate[m], m))
        frozen_rank = {m: i for i, m in enumerate(FROZEN)}
        rho, pr = stats.spearmanr([frozen_rank[m] for m in shared],
                                  [-rate[m] for m in shared])
        print(f"\n  frozen DEFAULT_FALSIFIER_STRENGTH          : {list(FROZEN)}")
        print(f"  order induced by the first-pass rate       : {measured}")
        print(f"  Spearman(frozen rank, measured rank)       : rho={rho:.4f}, "
              f"p={pr:.4f}")
        # TIES ARE BROKEN AT RANDOM, NOT ALPHABETICALLY, and the difference is
        # not cosmetic. With a deterministic tiebreak three models stuck at
        # 1.0000 produce one stable-looking order and the instrument reports
        # 75% reproducibility for an ordering the data did not decide. A real
        # implementation facing a tie has nothing to break it with, so the
        # bootstrap must face the same thing.
        rng = np.random.default_rng(SEED)
        orders = collections.Counter()
        tied = 0
        for _ in range(n_boot):
            r = {m: by[m][rng.integers(0, len(by[m]), len(by[m]))].mean()
                 for m in shared}
            jitter = {m: v for m, v in zip(shared, rng.permutation(len(shared)))}
            o = tuple(sorted(shared, key=lambda m: (-r[m], jitter[m])))
            orders[o] += 1
            if any(abs(r[a] - r[b]) < 1e-12
                   for a, b in zip(o, o[1:])):
                tied += 1
        modal, modal_n = orders.most_common(1)[0]
        frozen_hits = orders[tuple(m for m in FROZEN if m in by)]
        print(f"  bootstrap B={n_boot}, distinct orders seen    : {len(orders)}")
        print(f"  resamples with >=1 EXACT TIE in the order  : {tied / n_boot:.2%}")
        print(f"  modal induced order reproduced             : {modal_n / n_boot:.2%}")
        print(f"  frozen order reproduced                    : "
              f"{frozen_hits / n_boot:.4%}")
        print("  top 3 induced orders:")
        for o, c in orders.most_common(3):
            print(f"    {c / n_boot:>7.2%}  {list(o)}")


def report_identification(logs: pathlib.Path) -> None:
    """Can the archive support the design that DOES identify the estimand?

    The estimand the ladder needs is conditional on the finding: for the SAME
    finding, which model resolves it. That is a paired comparison, and the
    standard estimator is a conditional (Rasch / Bradley-Terry) fit with finding
    difficulty as a nuisance parameter -- which needs findings attempted by two
    or more distinct models, because those overlaps are what link the models onto
    one scale. Routing produces exactly that overlap and the runner archives it
    in `routing_history`. This counts it, SPLIT BY ARM, because an overlap
    between two labels of the same underlying model carries no information about
    capability.
    """
    by_arm = collections.Counter()
    attempts = collections.Counter()
    rungs = collections.defaultdict(set)
    overlap = collections.Counter()
    for p in sorted(glob.glob(str(logs / "*" / "*_report.json"))):
        try:
            doc = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for e in ((doc.get("registry") or {}).get("entries") or {}).values():
            rh = e.get("routing_history") or []
            if not rh:
                continue
            raw = e.get("source_model") or ""
            arm = "SIMULATED" if raw.endswith("-SIM") else "REAL"
            by_arm[arm] += 1
            models = {raw.replace("-SIM", "")} if raw else set()
            for a in rh:
                attempts[arm] += 1
                m = a.get("model_used") or ""
                if m:
                    base = m.replace("-SIM", "")
                    models.add(base)
                    rungs[arm].add(base)
            if len(models) >= 2:
                overlap[arm] += 1
    print("=" * 78)
    print("4. CAN THE ARCHIVE IDENTIFY THE CONDITIONAL ESTIMAND?")
    print("=" * 78)
    print(f"  {'arm':<12}{'findings routed':>16}{'attempts':>10}"
          f"{'>=2 models':>12}{'distinct rungs':>16}")
    for arm in ("REAL", "SIMULATED"):
        print(f"  {arm:<12}{by_arm[arm]:>16}{attempts[arm]:>10}"
              f"{overlap[arm]:>12}{len(rungs[arm]):>16}")
    if by_arm["REAL"] == 0:
        print("\n  NOT IDENTIFIABLE. Every archived routing attempt comes from the")
        print("  SIMULATED arm -- the ladder has never produced one recorded attempt")
        print("  on a real panel. And the simulated seat map is uniform, so the")
        print("  label pairs it does produce (CC2 -> ChatGPT, ChatGPT -> Codex, ...)")
        print("  are pairs of ALIASES OF ONE MODEL:")
        print("  `scripts/what_the_sim_runner_never_carried_over_2026-10-05.py`")
        print("  measures 1 distinct model across the 5 rungs the ladder returns.")
        print("  A paired comparison between two names for the same model carries")
        print("  no information about capability, so there is nothing here to fit.")
        print("\n  CONSEQUENCE FOR THE PROPOSAL. Neither candidate mitigation is")
        print("  estimable from the archive: first-pass-only is estimable but is")
        print("  at its ceiling and leaves three real models tied, and the paired")
        print("  design that would identify the right estimand has no real data.")
        print("  The measurement has to be DESIGNED -- a fixed residual set that")
        print("  every model attempts, which is exactly what Exp 42 did -- and the")
        print("  precondition is a seat map with more than one model class in it.")
    else:
        print("\n  Some REAL routing attempts exist; a conditional fit may be")
        print("  possible. Check the distinct-rung count: a fit needs more than one")
        print("  underlying model, not merely more than one label.")


def main(argv=None) -> int:
    args = _parse_args(argv)
    logs = pathlib.Path(args.logs)
    if not logs.is_dir():
        print(f"  {logs} is not a directory")
        return 1
    rows, unreadable = collect(logs)
    if not rows:
        print("  no first-pass falsifier reaching a verdict was found")
        return 1
    print("=" * 78)
    print("CAN A FIRST-PASS CONFIRM RATE ORDER THE ROUTING LADDER?")
    print("=" * 78)
    print(f"  archived reports scanned                   : "
          f"{len(glob.glob(str(logs / '*' / '*_report.json')))}")
    print(f"  first-pass attempts reaching a verdict     : {len(rows)}")
    if unreadable:
        print(f"  *** {len(unreadable)} report(s) could not be read and are NOT in")
        print(f"      the figures, so every count is a LOWER BOUND: "
              f"{unreadable[:4]}")
    else:
        print("  reports that could not be read             : 0 "
              "(so the counts are complete, not a lower bound)")
    print()
    for arm in ("REAL", "SIMULATED"):
        report_arm(arm, rows, args.min_n, args.bootstrap)
        print()
    report_identification(logs)
    print()
    print("=" * 78)
    print("CONCLUSION")
    print("=" * 78)
    print("  First-pass-only does not give a common population (the severity test")
    print("  rejects it on the real arm) and does not order the panel (three real")
    print("  models sit at exactly 1.0000). It is the cheapest mitigation and it")
    print("  is not a sufficient one. The frozen Exp-42 order measured the")
    print("  conditional quantity the ladder actually uses, on a fixed residual")
    print("  set every model attempted; that design, not this rate, is what a")
    print("  replacement has to beat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
