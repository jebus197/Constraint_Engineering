#!/usr/bin/env python3
"""The intra-round correlation, measured from the archive rather than assumed.

WHY THIS EXISTS. `bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py`
showed that the spurious-convergence factor for a shrinking roster is 8.49986
under INDEPENDENT seats and 1.9200 at a correlation of 0.3, so the magnitude of
the hazard turns on a quantity the panel brief had to leave as a parameter. The
brief says plainly that the correlation has never been measured here, and asks
the seats how it could be. This script answers that question with the archive.

WHAT IS MEASURED. For each archived round, which of the seats that RESPONDED
raised at least 1 new critical finding in that round. Critical is severity at or
above 0.7, which is the threshold the live runner uses at 4 separate sites. A
seat is credited for a round only if a finding's `source_model` names it and its
`open_since_round` equals that round.

TWO ESTIMATORS, because one would not be evidence:

  * PAIRWISE, the intraclass correlation for binary data. Over all ordered pairs
    of seats within a round, rho = (P(both raise) - q^2) / (q (1 - q)).
  * OVERDISPERSION, the method of moments on the Beta-Binomial. With x the count
    of raising seats in a round of n, Var(x) = n q (1-q) (1 + (n-1) rho), so rho
    follows from the observed variance.

They are computed from the same data by different routes and must agree. A
bootstrap over rounds gives the interval.

Run: python3 bench/the_intra_round_correlation_measured_2026-10-07.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

CRITICAL = 0.7          # live runner threshold, 4 sites in reference_runner_v3.py
Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def _norm(s) -> str:
    return str(s or "").strip().lower()


def collect_rounds(root: Path) -> list[tuple[int, int]]:
    """Return (n_responded, n_raising) per round across every archived report."""
    out: list[tuple[int, int]] = []
    seen_reports = 0
    for f in sorted(glob.glob(str(root / "bench" / "logs" / "**" / "*report*.json"),
                              recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        rounds = d.get("rounds")
        reg = d.get("registry")
        if not isinstance(rounds, list) or not isinstance(reg, dict):
            continue
        entries = reg.get("entries") if isinstance(reg.get("entries"), dict) else reg
        if not isinstance(entries, dict):
            continue
        seen_reports += 1
        # which seat raised a new critical in which round
        raised: dict[int, set[str]] = {}
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            try:
                sev = float(e.get("severity") or 0.0)
            except (TypeError, ValueError):
                continue
            if sev < CRITICAL:
                continue
            r = e.get("open_since_round")
            m = _norm(e.get("source_model"))
            if r is None or not m:
                continue
            try:
                raised.setdefault(int(r), set()).add(m)
            except (TypeError, ValueError):
                continue
        for rec in rounds:
            if not isinstance(rec, dict):
                continue
            resp = rec.get("models_responded")
            if not isinstance(resp, list) or len(resp) < 2:
                continue        # a pairwise correlation needs 2 seats
            try:
                rn = int(rec.get("round"))
            except (TypeError, ValueError):
                continue
            resp_n = {_norm(m) for m in resp}
            hits = len(resp_n & raised.get(rn, set()))
            out.append((len(resp_n), hits))
    return out, seen_reports


def rho_pairwise(rounds: list[tuple[int, int]]) -> tuple[float, float, int]:
    """ICC for binary data from within-round pairs. Returns (rho, q, n_pairs)."""
    both = pairs = raises = seats = 0
    for n, x in rounds:
        pairs += n * (n - 1)
        both += x * (x - 1)
        raises += x
        seats += n
    if not pairs or not seats:
        return (float("nan"), float("nan"), 0)
    q = raises / seats
    p_both = both / pairs
    denom = q * (1 - q)
    return (((p_both - q * q) / denom) if denom > 0 else float("nan"), q, pairs)


def rho_overdispersion(rounds: list[tuple[int, int]]) -> float:
    """Method of moments on the Beta-Binomial, pooled over equal-n rounds."""
    import numpy as np
    by_n: dict[int, list[int]] = {}
    for n, x in rounds:
        by_n.setdefault(n, []).append(x)
    num = den = 0.0
    for n, xs in by_n.items():
        if n < 2 or len(xs) < 3:
            continue
        a = np.asarray(xs, dtype=float)
        q = a.mean() / n
        if not (0 < q < 1):
            continue
        var_obs = a.var(ddof=1)
        var_ind = n * q * (1 - q)
        if var_ind <= 0:
            continue
        rho_n = (var_obs / var_ind - 1.0) / (n - 1)
        num += rho_n * len(xs)
        den += len(xs)
    return (num / den) if den else float("nan")


def bootstrap(rounds, reps=4000, seed=11) -> tuple[float, float]:
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = np.arange(len(rounds))
    vals = []
    for _ in range(reps):
        pick = rng.choice(idx, size=len(idx), replace=True)
        r, _q, _p = rho_pairwise([rounds[i] for i in pick])
        if r == r:                      # not NaN
            vals.append(r)
    if not vals:
        return (float("nan"), float("nan"))
    v = np.sort(np.asarray(vals))
    return (float(v[int(0.025 * len(v))]), float(v[int(0.975 * len(v)) - 1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reps", type=int, default=4000)
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]

    rounds, n_reports = collect_rounds(root)
    print(f"reports with both a rounds list and a registry: {n_reports}")
    print(f"rounds usable (2 or more responding seats): {len(rounds)}")
    if not rounds:
        print("NO USABLE ROUNDS -- the correlation stays UNMEASURED.")
        return 0

    rho_p, q, n_pairs = rho_pairwise(rounds)
    rho_o = rho_overdispersion(rounds)
    lo, hi = bootstrap(rounds, reps=a.reps)
    seats = sum(n for n, _ in rounds)
    raises = sum(x for _, x in rounds)
    qlo, qhi = wilson(raises, seats)

    print()
    print(f"seat-rounds: {seats};  seat-rounds raising a new critical: {raises}")
    print(f"q (per-seat-per-round new-critical rate) = {q:.6f}  "
          f"Wilson [{qlo:.6f}, {qhi:.6f}]")
    print(f"within-round ordered pairs: {n_pairs}")
    print()
    print(f"rho, PAIRWISE intraclass        = {rho_p:.6f}  "
          f"bootstrap [{lo:.6f}, {hi:.6f}]")
    print(f"rho, OVERDISPERSION moments     = {rho_o:.6f}")
    print(f"the 2 estimators agree to       {abs(rho_p - rho_o):.6f}"
          if rho_o == rho_o else "overdispersion estimator unavailable")
    print()
    # what that rho implies for the hazard, using the committed producer
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location(
        "corr_meas",
        root / "bench"
        / "the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py")
    C = importlib.util.module_from_spec(spec)
    sys.modules["corr_meas"] = C
    spec.loader.exec_module(C)
    use = max(0.0, min(0.95, rho_p if rho_p == rho_p else 0.0))
    print(f"AT THE MEASURED rho = {use:.4f}, the 6-seat-to-4-seat "
          f"spurious-convergence factor is "
          f"{C.ratio_exact_beta_binomial(use, q=max(0.01, min(0.99, q))):.4f}")
    print(f"  (independence would give "
          f"{C.ratio_independent(q=max(0.01, min(0.99, q))):.4f} at the same q)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
