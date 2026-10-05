#!/usr/bin/env python3
"""Why the Max-plan allowance went from 17% to 100% in 4 days.

The founder's figures are the constraint any explanation has to fit: historically
under 30% of a weekly 20x allowance, with Ultracode and maximum reasoning ALWAYS on,
and simulated experiments that "barely registered". Fable stood at 34% at the reset
while the overall allowance stood at 100%. So the load is NOT spread evenly across
seats, and Ultracode cannot be the cause because Ultracode did not change.

THE STRUCTURAL CHANGE THE FOUNDER NAMED HIMSELF: the project moved from PAID runs,
where 5 of 6 seats are other vendors billed outside the Max plan, to SIMULATED runs.
`bench/tools/sim_dispatch_shim.py:108` -- `def make_shim(model: str = "opus", ...)`
-- answers EVERY seat with ONE stand-in model, defaulting to opus, and its own
comment records that it patches 8 call sites in 7 enclosing functions. So a
simulated run puts all 6 seats, plus routing, arbitration and the sweep, on the Max
plan as opus.

This counts the dispatches by their own timestamps and sizes. It does not estimate
prices: it reports volume, which is the part the archive can establish.
"""
import collections
import glob
import json
import pathlib
import re
import sys

import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
STAMP = re.compile(r"(20\d{6})T(\d{6})Z")


def wilson(k, n):
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 30
    z = mp.mpf("1.959963984540054235309065817"); ph = mp.mpf(k)/n; nn = mp.mpf(n)
    c = (ph + z**2/(2*nn))/(1 + z**2/nn)
    hw = (z/(1+z**2/nn))*mp.sqrt(ph*(1-ph)/nn + z**2/(4*nn**2))
    assert abs(float(c-hw)-lo) < 1e-9 and abs(float(c+hw)-hi) < 1e-9, \
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}"
    return round(100*lo, 4), round(100*hi, 4)


def main() -> int:
    by_day = collections.defaultdict(lambda: [0, 0])
    sim_days = collections.defaultdict(lambda: [0, 0])
    unreadable = 0
    for f in glob.glob(str(REPO / "bench" / "logs" / "**" / "*.json"), recursive=True):
        p = pathlib.Path(f)
        m = STAMP.search(p.name)
        if not m:
            continue                      # not a dispatch artefact
        try:
            d = json.loads(p.read_text(errors="replace"))
        except Exception:
            unreadable += 1
            continue
        if not isinstance(d, dict):
            continue
        txt = d.get("response")
        if not isinstance(txt, str):
            continue
        day = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"
        by_day[day][0] += 1
        by_day[day][1] += len(txt)
        if "-sim" in p.name.lower() or "-SIM" in p.name:
            sim_days[day][0] += 1
            sim_days[day][1] += len(txt)

    days = sorted(by_day)
    print(f"dispatch artefacts carrying a response and a timestamp: "
          f"{sum(v[0] for v in by_day.values())} over {len(days)} day(s); "
          f"unreadable {unreadable}")
    print()
    print("DISPATCHES PER DAY, newest 14 (each one is a model call):")
    print("  day          total   chars        of which SIMULATED seats")
    for day in days[-14:]:
        n, c = by_day[day]
        sn, sc = sim_days.get(day, [0, 0])
        print(f"  {day}  {n:5d}  {c:10,d}   {sn:5d}  {sc:10,d}")

    # the window the founder names against everything before it
    recent = [d for d in days if d >= "2026-10-01"]
    older = [d for d in days if d < "2026-10-01"]
    rn = sum(by_day[d][0] for d in recent); rc = sum(by_day[d][1] for d in recent)
    on = sum(by_day[d][0] for d in older);  oc = sum(by_day[d][1] for d in older)
    rs = sum(sim_days.get(d, [0, 0])[0] for d in recent)
    os_ = sum(sim_days.get(d, [0, 0])[0] for d in older)
    print()
    print(f"FROM 2026-10-01 : {rn:5d} dispatches, {rc:12,d} chars, "
          f"{rs} simulated ({100.0*rs/max(1,rn):.4f}%)")
    print(f"BEFORE          : {on:5d} dispatches, {oc:12,d} chars, "
          f"{os_} simulated ({100.0*os_/max(1,on):.4f}%)")
    if rn:
        lo, hi = wilson(rs, rn)
        print(f"  simulated share since 2026-10-01: {rs}/{rn} = "
              f"{100.0*rs/rn:.4f}%  Wilson [{lo}%, {hi}%]")
    if on:
        lo2, hi2 = wilson(os_, on)
        print(f"  simulated share before          : {os_}/{on} = "
              f"{100.0*os_/on:.4f}%  Wilson [{lo2}%, {hi2}%]")

    # per-day rate, two tools
    counts = np.array([by_day[d][0] for d in days], dtype=float)
    rec = np.array([by_day[d][0] for d in recent], dtype=float)
    old = np.array([by_day[d][0] for d in older], dtype=float)
    print()
    if rec.size and old.size:
        rm, om = float(rec.mean()), float(old.mean())
        ratio_np = rm / om if om else float("inf")
        ratio_mp = float(mp.mpf(rm) / mp.mpf(om)) if om else float("inf")
        assert abs(ratio_np - ratio_mp) < 1e-9, "numpy and mpmath disagree"
        print(f"dispatches per ACTIVE day: since 2026-10-01 mean {rm:.4f} "
              f"(median {np.median(rec):.1f}), before {om:.4f} "
              f"(median {np.median(old):.1f})")
        print(f"  ratio {ratio_np:.4f}x  (numpy == mpmath)")
    print()
    print("WHAT THIS DOES AND DOES NOT SHOW. It counts archived seat REPLIES, so it")
    print("measures the simulated runs and the panels. It cannot see this session's")
    print("own token use, nor the subagent dispatches, which are the other 2 arms.")
    print("Those are reported separately in the session record: 924,535 subagent")
    print("tokens for 2 agents on 2026-10-03/04, both explicitly set to opus.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
