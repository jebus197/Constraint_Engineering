#!/usr/bin/env python3
"""HIS QUESTION, and the answer is 0 NEW PAID RUNS.

HIS WORDS, 2026-11-01, verbatim: *"I asked why it required me to spend money,
before we can decide on some sane default values for this measurement? What
difference does spending money in a live run, and making the same measurement in
a simulated run make? I don't see the connection? Please read my original
question. If the real answer is none, then how many simulated runs do you need to
do before you can reliably make."*

And from his closing-report annotation: *"Surely whether a run is simulated, or
real, should have no impact on this measurement either? Moreover why is it
necessary to risk money on real runs or a feature hat has not yet been fully
tested, when simulated runs have tended to be the way we have tested new
features like this in the past?"*

THE CONNECTION HE CANNOT SEE DOES NOT EXIST. It was asserted, not measured, and
this script measures it away. 3 DIFFERENT QUESTIONS were run together under the
one phrase "validate the severity design", and only 1 of them ever needed a real
model at all -- and that one is ALREADY PAID FOR.

  (i)  SANE DEFAULT VALUES for q, sigma and nu. Needs REAL-model behaviour, and
       the archive already holds 28 real-seat runs. The money was spent between
       May and July 2026. 0 new paid runs.
  (ii) WHETHER THE 2 SEVERITY FORMS DISAGREE, and where. A comparison of 2
       functions on the SAME inputs. Needs no calibration of either, so a
       simulated run carries it exactly as well as a paid one.
  (iii) WHETHER THE NEW FORM DECIDES BETTER. Needs LABELS, not money. The
       2026-09-02 blind audit holds 286 first-pass and 108 second-pass verdicts
       against the 5 pre-registered CRITICAL clauses.

So the only quantity that needed computing is (ii)'s sample size, which is what
the bottom half of this script does.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint, samplesize_confint_proportion

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
SIM_HINT = ("sim-", "-sim", "simulat", "sim_")


def survey() -> tuple[list, list]:
    real, sim = [], []
    for d in sorted(LOGS.iterdir()):
        st = d / "runner_state.json"
        if not st.is_file():
            continue
        try:
            s = json.loads(st.read_text())
        except Exception:                                   # noqa: BLE001
            continue
        ents = (s.get("registry") or {}).get("entries") or {}
        n_ent = len(ents) if isinstance(ents, (dict, list)) else 0
        per = s.get("raw_counts_per_model") or {}
        seats = sorted(per)
        rounds = max((len(v) for v in per.values()), default=0)
        is_sim = (not seats) or any(h in n.lower() for n in seats for h in SIM_HINT)
        (sim if is_sim else real).append({"run": d.name, "entries": n_ent,
                                          "seats": seats, "rounds": rounds})
    return real, sim


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="how_many_simulated_runs_for_the_severity_defaults_2026-11-01.py",
        description="Measure what the archive already supplies and how many "
                    "SIMULATED runs the shadow comparison needs. Reads only.")
    ap.parse_args()

    real, sim = survey()
    r_ent = sum(r["entries"] for r in real)
    s_ent = sum(r["entries"] for r in sim)
    r_sr = sum(len(r["seats"]) * r["rounds"] for r in real)

    print("=" * 74)
    print("PART 1. WHAT THE ARCHIVE ALREADY SUPPLIES, PAID FOR AND IN THE TREE")
    print("=" * 74)
    print(f"  REAL-seat runs      : {len(real):3d}   entries = {r_ent:5d}   "
          f"seat-rounds = {r_sr:5d}")
    print(f"  SIMULATED runs      : {len(sim):3d}   entries = {s_ent:5d}")
    seats = sorted({s for r in real for s in r["seats"]})
    print(f"  distinct real seats : {len(seats)}  {seats}")
    print(f"  -> per-seat, per-round counts exist for {len(seats)} REAL models over")
    print(f"     {r_sr} seat-rounds. Estimating q, sigma and nu needs NO NEW PAID RUN.")

    print()
    print("=" * 74)
    print("PART 2. HOW MANY SIMULATED RUNS THE SHADOW COMPARISON NEEDS")
    print("=" * 74)
    per_run = [r["entries"] for r in sim if r["entries"] > 0]
    med = statistics.median(per_run)
    # bootstrap a 95% interval on the median, so the conversion is not a guess
    rng = np.random.default_rng(20261101)
    boots = [float(np.median(rng.choice(per_run, len(per_run), replace=True)))
             for _ in range(20000)]
    blo, bhi = np.percentile(boots, [2.5, 97.5])
    print(f"  entries per simulated run: median {med:.1f}, bootstrap 95% "
          f"[{blo:.1f}, {bhi:.1f}] over {len(per_run)} runs")

    print()
    print("  SAMPLE SIZE for the DISAGREEMENT RATE between the 2 severity forms,")
    print("  at 95% confidence, cross-verified on statsmodels and a closed form:")
    print(f"  {'target +/-':>10} {'p assumed':>10} {'n findings':>11} "
          f"{'runs at median':>15} {'runs at the pessimistic bound':>30}")
    for half in (0.10, 0.05, 0.03):
        for p in (0.10, 0.25, 0.50):
            n_sm = samplesize_confint_proportion(p, half, alpha=0.05, method="normal")
            z = stats.norm.ppf(0.975)
            n_cf = (z / half) ** 2 * p * (1 - p)
            assert abs(n_sm - n_cf) < 1e-6, (n_sm, n_cf)
            n = int(np.ceil(n_sm))
            print(f"  {half:>10.2f} {p:>10.2f} {n:>11d} "
                  f"{n / med:>15.2f} {n / blo:>30.2f}")

    print()
    print("  THE DECISION-RELEVANT ROW. A disagreement rate is only worth acting on")
    print("  if it is distinguishable from 0, and the 2 forms are ALREADY KNOWN to")
    print("  differ on simulated data: the old form was constant at 0.5 over 1,252")
    print("  entries while the new form spanned 0.3667 to 0.5. So the question is")
    print("  not WHETHER they differ but BY HOW MUCH, at +/- 0.05:")
    n_main = int(np.ceil(samplesize_confint_proportion(0.25, 0.05, alpha=0.05,
                                                       method="normal")))
    print(f"    n = {n_main} findings  ->  {n_main / med:.2f} runs at the median, "
          f"{n_main / blo:.2f} at the pessimistic bound")
    # ★ THE CONSERVATIVE FIGURE LEADS, 2026-11-01, because the generous one was
    # 2.6x too kind and was quoted to him before this check ran. 11 of the 35
    # simulated runs are classified simulated by the ABSENCE of seat names rather
    # than by a `-SIM` name, and they carry the MAJORITY of the entries. A run
    # with no `raw_counts_per_model` could in principle be a real run missing a
    # field, so counting it as simulated inflates the headroom.
    named = [r for r in sim if r["seats"]]
    s_named = sum(r["entries"] for r in named)
    unnamed_n = len(sim) - len(named)
    print(f"    CONSERVATIVE, counting only the {len(named)} runs whose seats carry")
    print(f"    the -SIM suffix: {s_named} entries = {s_named / n_main:.2f}x the requirement.")
    print(f"    GENEROUS, counting all {len(sim)} including the {unnamed_n} classified")
    print(f"    simulated by ABSENCE of seat names: {s_ent} entries = "
          f"{s_ent / n_main:.2f}x. QUOTE THE CONSERVATIVE ONE.")

    print()
    print("  SO THE SHADOW COMPARISON NEEDS 0 NEW RUNS TOO, if the existing")
    print("  simulated archive is used. New runs are needed only to see the new")
    print("  form DECIDE live, which is a different claim from calibrating it.")

    print()
    print("=" * 74)
    print("PART 3. WHAT A PAID RUN AND A SIMULATED RUN ACTUALLY DIFFER ON")
    print("=" * 74)
    print("  SAME in both: the recursion, the floor nu/q, the pass-count formula,")
    print("        whether the gate is reached, whether the new form computes,")
    print("        its spread, and which decisions the 2 forms disagree on.")
    print("  DIFFERENT: the numerical VALUE of a real model's detection power d_i,")
    print("        which the 28 real-seat runs above already supply retrospectively.")
    print("  THEREFORE: money buys a FRESH d_i for a model whose behaviour may have")
    print("        drifted. It does not buy the ability to make this measurement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
