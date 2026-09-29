#!/usr/bin/env python3
"""rho is computed BEFORE the settle pass that corrects its own numerator.

THE DEFECT. `reference_runner_v3.run_experiment` computes rho at the registration
site and appends it to `rho_history`:

    :14591  rho_current, rho_avg, rho_churn = _compute_rho(novelty_counts, raw_counts, cfg)
    :14592  rho_history.append(rho_current)

691 lines later, AFTER apply_falsifier_verdicts and the specialist verifier have
run, the SAME round's novelty is recomputed from the settled registry and the
history entry is overwritten:

    :15282  novel_this_round = _settled_all[round_idx]
    :15284      novelty_counts[-1] = _settled_all[round_idx]

`_compute_rho` has exactly 1 call site and `rho_history` is thereafter only
cleared on an ITC restart or serialised. The correction therefore reaches
`novelty_counts` and NEVER reaches `rho`: the archived state carries a numerator
and a rho that disagree BY CONSTRUCTION.

This script proves it from the archive alone. It recomputes rho from each run's
OWN stored novelty_counts / raw_counts using the runner's OWN formula and
compares against that run's OWN recorded rho_history. No model, no judgement.

TOLERANCE, AND A MEASUREMENT ERROR THIS SCRIPT ONCE MADE. `rho_history` is
serialised as `round(r, 6)` (:15547). A first pass compared at 1e-9 and reported
220 of 406 rounds mismatching, 94 of them "understatements" whose largest delta
was 1e-9 -- pure storage rounding read as signal. At the stored precision the
figure is 25 of 406 and the direction is unanimous. The 1e-6 tolerance below is
the fix; anything tighter measures the JSON writer, not the runner.

Cross-verification per the 2026-04-21 rule: every ratio is computed twice, in
float64 via numpy and exactly via fractions.Fraction, and must agree to 1e-12.
Every proportion carries a Wilson 95% interval from statsmodels AND from a local
closed form, and the two are printed so they can be seen to agree.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import statistics
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]

#: rho_history is stored round(r, 6). Below this, a difference is the writer.
TOL = 1e-6


def wilson_local(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def wilson_statsmodels(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (0.0, 0.0)
    return tuple(proportion_confint(k, n, alpha=0.05, method="wilson"))


def report_proportion(label: str, k: int, n: int) -> None:
    lo_l, hi_l = wilson_local(k, n)
    try:
        lo_s, hi_s = wilson_statsmodels(k, n)
        agree = max(abs(lo_l - lo_s), abs(hi_l - hi_s))
    except Exception as exc:                              # noqa: BLE001
        lo_s = hi_s = float("nan")
        agree = float("nan")
        print(f"  (statsmodels unavailable: {exc})")
    pct = 100.0 * k / n if n else 0.0
    print(f"{label}: {k} of {n} = {pct:.4f}%")
    print(f"    Wilson 95% local       [{100*lo_l:.4f}%, {100*hi_l:.4f}%]")
    print(f"    Wilson 95% statsmodels [{100*lo_s:.4f}%, {100*hi_s:.4f}%]")
    print(f"    two implementations agree to {agree:.3e}")


def runner_defaults():
    """Read the rho config defaults out of the runner rather than assuming."""
    src = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
    def d(name, cast):
        m = re.search(rf"{name}:\s*\w+\s*=\s*([0-9.]+)", src)
        return cast(m.group(1)) if m else None
    return (int(d("rho_rolling_window", float) or 3),
            d("rho_threshold", float) or 0.25,
            int(d("rho_earliest_round", float) or 12))


def state_paths():
    ps = sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json")))
    shake = REPO / "bench/logs/shakedown_2026-09-29/arm1_harvest/runner_state.json"
    if shake.is_file():
        ps.append(str(shake))
    return ps


def rolling_avg(series, win):
    out = []
    for i in range(len(series)):
        w = series[max(0, i + 1 - win): i + 1]
        out.append(sum(w) / len(w) if w else 0.0)
    return out


def main() -> int:
    # ANSWERS --help WITHOUT DOING THE WORK. `A --help must never cost money`
    # (founder ruling; 15 of 17 runners once billed a live dispatch on an
    # unrecognised argument). This script spends nothing, but it does read the
    # whole archive, and `bench/tests/test_help_is_answered_2026-09-11.py`
    # requires every measurement script to answer the flag rather than ignore it.
    # It refused this commit until this was added, which is the guard working.
    ap = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="Compare each archived run's recorded rho against its own stored numerator.",
        epilog="Takes no arguments: it reads bench/logs/*/runner_state.json and "
               "prints its findings. Exit 0 on success, 2 on a cross-tool "
               "disagreement above 1e-12.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    WIN, THR, EAR = runner_defaults()
    print("=" * 78)
    print("rho RECORDED vs rho RECOMPUTED FROM THE RUN'S OWN SETTLED NUMERATOR")
    print("=" * 78)
    print(f"runner defaults read from source: rolling_window={WIN} "
          f"threshold={THR} earliest_round={EAR}   tolerance={TOL}")
    print()

    rows = []
    n_rounds = over = under = same = 0
    deltas = []
    churn_flips = []
    max_dev_global = 0.0

    for p in state_paths():
        try:
            st = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        nov = st.get("novelty_counts") or []
        raw = st.get("raw_counts") or []
        rec = st.get("rho_history") or []
        n = min(len(nov), len(raw), len(rec))
        if n == 0:
            continue
        name = Path(p).parent.name

        # two independent recomputations of the same ratio
        arr_n = np.asarray(nov[:n], dtype=np.float64)
        arr_r = np.asarray(raw[:n], dtype=np.float64)
        with np.errstate(divide="ignore", invalid="ignore"):
            f_np = np.where(arr_r > 0, arr_n / np.where(arr_r > 0, arr_r, 1.0), 0.0)
        f_ex = [float(Fraction(int(nov[i]), int(raw[i]))) if raw[i] > 0 else 0.0
                for i in range(n)]
        dev = max((abs(a - b) for a, b in zip(f_np.tolist(), f_ex)), default=0.0)
        max_dev_global = max(max_dev_global, dev)
        if dev > 1e-12:
            print(f"  !! numpy/Fraction disagree by {dev:.3e} in {name}")
            return 2

        recd = [float(x) for x in rec[:n]]
        mism = []
        for i in range(n):
            n_rounds += 1
            d = f_ex[i] - recd[i]
            if abs(d) <= TOL:
                same += 1
            else:
                deltas.append(d)
                mism.append(i)
                if d < 0:
                    over += 1
                else:
                    under += 1

        a_rec = rolling_avg(recd, WIN)
        a_new = rolling_avg(f_ex, WIN)
        for i in range(n):
            rn = i + 1
            c_rec = a_rec[i] < THR and rn >= EAR
            c_new = a_new[i] < THR and rn >= EAR
            if c_rec != c_new:
                churn_flips.append((name, i, a_rec[i], a_new[i], c_rec, c_new))

        rows.append((name, n, len(mism), nov[:n], raw[:n], recd, f_ex, mism))

    print(f"{'run':46s} {'rounds':>6s} {'mismatch':>9s}")
    print("-" * 78)
    for (name, n, nm, *_rest) in rows:
        print(f"{name[:46]:46s} {n:6d} {nm:9d}")
    print("-" * 78)
    print(f"{'TOTAL':46s} {n_rounds:6d} {over+under:9d}")
    print()
    print(f"numpy vs Fraction, worst deviation across every ratio: {max_dev_global:.3e}")
    print()

    report_proportion("MISMATCH RATE (rounds beyond storage rounding)",
                      over + under, n_rounds)
    print()
    if over + under:
        report_proportion("  of those, recorded rho is an OVERSTATEMENT",
                          over, over + under)
        print()
        a = np.array(deltas)
        print(f"delta (recomputed - recorded) over {len(a)} mismatching rounds:")
        print(f"  numpy       mean {a.mean():.8f}  min {a.min():.8f}  "
              f"max {a.max():.8f}  median {float(np.median(a)):.8f}")
        print(f"  statistics  mean {statistics.fmean(deltas):.8f}  "
              f"median {statistics.median(deltas):.8f}")
        print(f"  cross-tool agreement on the mean: "
              f"{abs(a.mean()-statistics.fmean(deltas)):.3e}")
        print()

    affected = sum(1 for r in rows if r[2] > 0)
    report_proportion("RUNS WITH AT LEAST 1 MISMATCHING ROUND", affected, len(rows))
    print()

    print("=" * 78)
    print("DID IT MOVE A CONVERGENCE DECISION? churn is blocking condition (d)")
    print("=" * 78)
    report_proportion("CHURN FLAG FLIPS", len(churn_flips), n_rounds)
    if churn_flips:
        for f in churn_flips:
            print(f"   {f[0][:44]:44s} r{f[1]:<3d} rho_avg {f[2]:.4f} -> "
                  f"{f[3]:.4f}   churn {f[4]} -> {f[5]}")
    else:
        print("    none. Every mismatch sits in an early round, and churn requires")
        print(f"    round_number >= {EAR}. The defect corrupts a REPORTED metric and")
        print("    the saturation diagnostic; on this archive it flipped no verdict.")
        print("    That is a property of this corpus, NOT a guarantee for future runs.")
    print()

    print("=" * 78)
    print("PER-ROUND DETAIL FOR EVERY RUN THAT MISMATCHES")
    print("=" * 78)
    for (name, n, nm, nov, raw, recd, f_ex, mism) in rows:
        if not nm:
            continue
        print()
        print(f"--- {name}  ({nm} of {n} rounds mismatch) ---")
        print(f"  {'r':>3s} {'settled':>8s} {'raw':>5s} {'recomputed':>11s} "
              f"{'recorded':>9s} {'delta':>9s}")
        for i in range(n):
            d = f_ex[i] - recd[i]
            flag = "  <-- MISMATCH" if i in mism else ""
            print(f"  {i:3d} {nov[i]:8d} {raw[i]:5d} {f_ex[i]:11.4f} "
                  f"{recd[i]:9.4f} {d:+9.4f}{flag}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
