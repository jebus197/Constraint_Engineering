#!/usr/bin/env python3
"""Replay option 3 against the corroboration a real run ACTUALLY recorded.

WHAT THIS ANSWERS. Option 3 (founder ruling 2026-09-29) counts novelty from the
`occasions` overlap record and lets that record grow on corroboration. The
question it has to survive is not "does the new code run" but "does it move rho
on real data, using only evidence the run already produced".

WHY A REPLAY AND NOT A DIRECT READ. The archived registries were written by the
OLD code, so their `occasions` lists hold only `via="register"` entries -- all 53
of length 1, which is the defect. The corroboration itself was recorded, in the
`codiscovery` field, by `record_codiscovery`. This script reconstructs the
occasion the new code WOULD write from that field and nothing else, then calls
the shipped `_corroborated_novelty_series` on the result. No figure here is
invented: every discount traces to a codiscovery record the run wrote itself.

ANTI-VACUITY. The script asserts that the reconstruction actually changes
something. If a run recorded no corroboration, it is reported as UNAFFECTED
rather than silently passing, so this cannot report success by doing nothing.

THE LIMIT OF WHAT THIS PROVES, AND IT MATTERS. The series here are recomputed
from each run's FINAL registry. The live runner recomputes rho once per round,
from the registry AS IT STOOD IN THAT ROUND, so it cannot see a status that
settled later or a corroboration recorded in a later round. These figures are
therefore an UPPER BOUND on the live effect, not a prediction of it.

Two distinct figures follow from that and must not be conflated:
  * `rho_computed_before_the_settle_2026-09-29.py` compares each recorded rho
    against ITS OWN round's stored numerator -- the pure timing defect, 25 of 406
    rounds, 6.1576%, Wilson [4.2053%, 8.9318%].
  * this script compares against a final-registry recomputation -- timing PLUS
    retroactive settling PLUS corroboration, 242 of 406 rounds.
The live per-round effect lies between them. Only a live run settles it, which is
why the shakedown is re-run rather than this being treated as the verification.

Cross-verification per the 2026-04-21 rule: each rho is computed in float64 via
numpy and exactly via fractions.Fraction and the two must agree to 1e-12; every
proportion carries a Wilson 95% interval from statsmodels and a local closed form.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (                      # noqa: E402
    _corroborated_discounts, _corroborated_novelty_series,
    _settled_novelty_series,
)


class ReplayRegistry:
    """Minimal stand-in exposing only `.entries`, which is all the series read."""

    def __init__(self, entries):
        self.entries = entries


def wilson_local(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def wilson_sm(k, n):
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (0.0, 0.0)
    return tuple(proportion_confint(k, n, alpha=0.05, method="wilson"))


def report_proportion(label, k, n):
    lo_l, hi_l = wilson_local(k, n)
    try:
        lo_s, hi_s = wilson_sm(k, n)
        agree = max(abs(lo_l - lo_s), abs(hi_l - hi_s))
    except Exception as exc:                                  # noqa: BLE001
        lo_s = hi_s = float("nan"); agree = float("nan")
        print(f"  (statsmodels unavailable: {exc})")
    print(f"{label}: {k} of {n} = {100.0*k/n if n else 0.0:.4f}%")
    print(f"    Wilson 95% local       [{100*lo_l:.4f}%, {100*hi_l:.4f}%]")
    print(f"    Wilson 95% statsmodels [{100*lo_s:.4f}%, {100*hi_s:.4f}%]")
    print(f"    agree to {agree:.3e}")


def reconstruct(entries, alias_map):
    """Add the codiscovery occasion the NEW code would write. Nothing else."""
    added = 0
    for cid, e in entries.items():
        if not isinstance(e, dict):
            continue
        for cd in e.get("codiscovery") or []:
            model = cd.get("model") or ""
            fid = cd.get("finding_id") or ""
            e.setdefault("occasions", []).append({
                "model": model,
                "round": e.get("open_since_round", 0),
                "alias": fid,
                "from_canonical": alias_map.get(f"{model}:{fid}", cid),
                "via": "codiscovery",
                "similarity": cd.get("similarity", 0.0),
            })
            added += 1
    return added


def ratio_two_ways(num, den):
    if den <= 0:
        return 0.0, 0.0
    f = float(np.float64(num) / np.float64(den))
    x = float(Fraction(int(num), int(den)))
    return f, x


def main() -> int:
    # ANSWERS --help WITHOUT DOING THE WORK. `A --help must never cost money`
    # (founder ruling; 15 of 17 runners once billed a live dispatch on an
    # unrecognised argument). This script spends nothing, but it does read the
    # whole archive, and `bench/tests/test_help_is_answered_2026-09-11.py`
    # requires every measurement script to answer the flag rather than ignore it.
    # It refused this commit until this was added, which is the guard working.
    ap = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="Replay option 3 on the corroboration each archived run actually recorded.",
        epilog="Takes no arguments: it reads bench/logs/*/runner_state.json and "
               "prints its findings. Exit 0 on success, 2 on a cross-tool "
               "disagreement above 1e-12.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    paths = sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json")))
    shake = REPO / "bench/logs/shakedown_2026-09-29/arm1_harvest/runner_state.json"
    if shake.is_file():
        paths.append(str(shake))

    print("=" * 78)
    print("OPTION 3 REPLAYED ON THE CORROBORATION EACH RUN ACTUALLY RECORDED")
    print("=" * 78)
    print()

    affected = 0
    examined = 0
    rounds_total = 0
    rounds_moved = 0
    worst_dev = 0.0
    detail = []

    for p in paths:
        try:
            st = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        reg = st.get("registry") or {}
        entries = reg.get("entries")
        if not isinstance(entries, dict) or not entries:
            continue
        alias_map = reg.get("alias_map") or {}
        raw = st.get("raw_counts") or []
        rec = st.get("rho_history") or []
        if not raw or not rec:
            continue
        name = Path(p).parent.name
        examined += 1
        max_round = max(len(raw), len(rec)) - 1

        ents = json.loads(json.dumps(entries))       # deep copy
        n_cd = reconstruct(ents, alias_map)
        rr = ReplayRegistry(ents)
        settled, _ = _settled_novelty_series(rr, max_round)
        corr, _ = _corroborated_novelty_series(rr, max_round)
        disc = _corroborated_discounts(rr)

        n = min(len(raw), len(rec), len(corr), len(settled))
        if n == 0:
            continue
        moved = []
        rows = []
        for i in range(n):
            rounds_total += 1
            f_s, x_s = ratio_two_ways(settled[i], raw[i])
            f_c, x_c = ratio_two_ways(corr[i], raw[i])
            worst_dev = max(worst_dev, abs(f_s - x_s), abs(f_c - x_c))
            recd = float(rec[i])
            if abs(x_c - recd) > 1e-6:
                moved.append(i)
                rounds_moved += 1
            rows.append((i, raw[i], settled[i], corr[i], x_s, x_c, recd))
        if n_cd == 0:
            print(f"{name[:52]:52s} UNAFFECTED (0 corroboration records)")
            continue
        affected += 1
        detail.append((name, n_cd, len(disc), rows, moved))
        print(f"{name[:52]:52s} {n_cd:3d} corroboration record(s), "
              f"{len(disc)} discount(s), {len(moved)} round(s) move")

    print()
    report_proportion("RUNS CARRYING CORROBORATION TO REPLAY", affected, examined)
    print()
    report_proportion("ROUNDS WHERE OPTION 3 MOVES rho OFF ITS RECORDED VALUE",
                      rounds_moved, rounds_total)
    print("    UPPER BOUND. Recomputed from each run's FINAL registry, so it")
    print("    includes statuses that settled after the round and corroboration")
    print("    recorded later. The live runner sees only what the round knew.")
    print()
    print(f"numpy vs Fraction, worst deviation across every ratio: {worst_dev:.3e}")
    if worst_dev > 1e-12:
        print("  !! cross-tool disagreement above 1e-12 — figures NOT verified")
        return 2
    print()

    print("=" * 78)
    print("PER-ROUND DETAIL")
    print("=" * 78)
    for (name, n_cd, n_disc, rows, moved) in detail:
        print()
        print(f"--- {name}  ({n_cd} corroboration records, {n_disc} discounts) ---")
        print(f"  {'r':>3s} {'raw':>5s} {'settled':>8s} {'option3':>8s} "
              f"{'rho settled':>12s} {'rho option3':>12s} {'rho recorded':>13s}")
        for (i, rw, s, c, xs, xc, recd) in rows:
            flag = "  <-- MOVES" if i in moved else ""
            print(f"  {i:3d} {rw:5d} {s:8d} {c:8d} {xs:12.4f} {xc:12.4f} "
                  f"{recd:13.4f}{flag}")
        print(f"  rho recorded : {[round(r[6],4) for r in rows]}")
        print(f"  rho option 3 : {[round(r[5],4) for r in rows]}")
    print()

    if affected == 0:
        print("NOTHING WAS REPLAYED. Option 3 is unverified by this script.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
