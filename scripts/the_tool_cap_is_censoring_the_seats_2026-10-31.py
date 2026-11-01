#!/usr/bin/env python3
"""The paid seats are being cut off by our own tool-iteration cap, not by a
lack of tools.

HIS CONCERN, 2026-10-31: that remote models "might not always have access to
every available tool either". The record says the opposite, and this script is
the measurement.

WHAT THE ARCHITECTURE ALREADY DOES. `bench/openrouter_tools.py` states the
problem in its own docstring -- the 4 API seats "have no tool execution unless
the host wires structured function-calling" -- and then wires it. THE HOST
EXECUTES THE TOOL, NOT THE MODEL: the seat emits a function call, the host runs
it in a subprocess-isolated verifier under an AST blocklist, and appends the
result as a role="tool" message. So a remote seat needs nothing installed, and
every seat runs the same version of the same tool.

MY OWN FIRST MEASUREMENT OF THIS WAS A FALSE ZERO, recorded because it is the
shape this project keeps meeting. Counting `{seat}.tools.attempt*.json.txt`
sidecars gave 0 of 64 remote replies using tools, against 53 of 264 local. That
sidecar is the CLI convention; the API path records tool use INSIDE the reply as
`tool_calls` / `n_tool_calls`. Counting either convention gives 34 of 64 remote
against 161 of 264 local, Fisher p = 0.2595 -- NOT distinguishable. The seats
were using tools all along.

THE REAL CONSTRAINT IS OURS. Of the 30 remote replies that record an iteration
count, 23 stopped with `max_iterations_harvested`. The demand is RIGHT-CENSORED
at whatever the cap was: 3 pile up at the old 10 and 20 at 16. So a mean or a
max over these numbers measures the CAP, not the demand, and the right
instrument is a survival curve rather than an average.

AND THE CLOCK DOES NOT BOUND IT. `timeout=300` is per HTTP REQUEST, not per
dispatch: 1 capped reply elapsed 496.4 s across its round trips. The binding
constraint is cost, which is why his spend approval is the governing number.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
LOCAL = ("cc2", "fable")
REMOTE = ("cx", "ge", "cgpt", "ds")
#: The 3 cost anchors `bench/confer_maths_panel_2026-09-05.py` records, measured
#: against live OpenRouter pricing across the 4 paid seats.
COST_ANCHORS = ((10.0, 1.64), (16.0, 3.56), (20.0, 5.23))


def interval(k: int, n: int) -> str:
    import mpmath as mp
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054")
    K, N = mp.mpf(k), mp.mpf(n)
    ph = K / N
    d = 1 + z**2 / N
    c = (ph + z**2 / (2 * N)) / d
    h = z * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2)) / d
    agree = max(abs(sm[0] - float(c - h)), abs(sm[1] - float(c + h)))
    return (f"{k}/{n} = {k/n:.6f}  Wilson [{sm[0]:.6f}, {sm[1]:.6f}] "
            f"(mpmath agrees to {agree:.1e})  "
            f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")


def _as_float(v) -> float:
    """`elapsed_s` is NOT always numeric. 1 archived reply carries the string
    'long-retry', so a bare float() raises part-way through the census and the
    whole measurement is lost. Coerced defensively and the non-numeric cases are
    reported rather than silently zeroed, because a 0 that means "unparseable"
    would drag the medians down without saying so."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def _replies():
    skipped: list[str] = []
    import re
    out = []
    for d in sorted(LOGS.iterdir()):
        if not d.is_dir():
            continue
        for s in LOCAL + REMOTE:
            p = d / f"{s}.json"
            if not p.exists():
                continue
            calls = 0
            for f in d.glob(f"{s}.tools.attempt*.json.txt"):
                calls += len(re.findall(r'"(?:name|tool|tool_name)"\s*:',
                                        f.read_text(errors="replace")))
            obj = {}
            try:
                o = json.loads(p.read_text(errors="replace"))
                if isinstance(o, dict):
                    obj = o
                    calls += int(o.get("n_tool_calls") or 0)
            except Exception as exc:  # noqa: BLE001
                # ★ A SWALLOWED FAILURE LEAVES NO TRACE, which is how a run with
                # unreadable seat files reports 0 tool calls and looks like a
                # seat that was simply quiet. The cause is now carried on the
                # row, so a 0 can be told apart from a 0 nobody could read.
                skipped.append(f"{p.name}: {type(exc).__name__}: {exc}")
            out.append({"run": d.name, "seat": s,
                        "route": "local" if s in LOCAL else "remote",
                        "calls": calls,
                        "iters": obj.get("tool_iterations"),
                        "stop": obj.get("stopped_reason"),
                        "elapsed": _as_float(obj.get("elapsed_s"))})
    # ★ RETURNED, NOT JUST COLLECTED. An accumulator nothing reads is the
    # addition-reaching-nothing failure this project has confirmed 11 times,
    # and it would be especially sharp here: the whole point of recording a
    # swallowed read error is that a 0 tool-call row can be told apart from a
    # row nobody could parse.
    return out, skipped


def main() -> int:
    import numpy as np
    import sympy as sp
    from statsmodels.duration.survfunc import SurvfuncRight

    rows, unreadable = _replies()
    if unreadable:
        print(f"UNREADABLE SEAT FILES: {len(unreadable)} — a 0 below from one of")
        print("  these runs is a 0 nobody could read, not a quiet seat:")
        for line in unreadable[:10]:
            print(f"    {line}")
        if len(unreadable) > 10:
            print(f"    + {len(unreadable) - 10} more")
        print()
    print("=" * 78)
    print("THE TOOL CAP IS CENSORING THE PAID SEATS")
    print("=" * 78)

    print("\n1. DO REMOTE SEATS USE TOOLS AT ALL? (either recording convention)")
    for route in ("local", "remote"):
        r = [x for x in rows if x["route"] == route]
        used = [x for x in r if x["calls"]]
        tot = sum(x["calls"] for x in r)
        print(f"    {route:6}: replies with tool evidence {interval(len(used), len(r))}")
        print(f"            total tool calls {tot}, mean per tool-using reply "
              f"{tot/len(used) if used else 0:.4f}")
    from scipy import stats
    lr = [x for x in rows if x["route"] == "local"]
    rr = [x for x in rows if x["route"] == "remote"]
    lu = sum(1 for x in lr if x["calls"]); ru = sum(1 for x in rr if x["calls"])
    odds, p = stats.fisher_exact([[ru, len(rr) - ru], [lu, len(lr) - lu]])
    print(f"    remote vs local, Fisher exact: odds ratio {odds:.4f}, p = {p:.6f}")
    print(f"    -> {'NOT distinguishable' if p >= 0.05 else 'distinguishable'}")

    print("\n2. WHY THEY STOP")
    it = [x for x in rows if x["iters"] is not None]
    cut = [x for x in it if x["stop"] != "finish"]
    print(f"    replies recording an iteration count: {len(it)}")
    print(f"    cut off rather than finished: {interval(len(cut), len(it))}")
    print(f"    iterations when cut off : {sorted(x['iters'] for x in cut)}")
    print(f"    iterations when finished: {sorted(x['iters'] for x in it if x not in cut)}")

    print("\n3. THE DEMAND IS RIGHT-CENSORED, SO USE A SURVIVAL CURVE")
    dur = np.array([float(x["iters"]) for x in it])
    evt = np.array([0 if x["stop"] != "finish" else 1 for x in it])
    sf = SurvfuncRight(dur, evt)
    for t, s, nr in zip(sf.surv_times, sf.surv_prob, sf.n_risk):
        print(f"      S({t:4.0f}) = {s:.6f}   at risk {nr:.0f}")
    print(f"    the curve bottoms at {sf.surv_prob[-1]:.6f} and never reaches 0,")
    print("    so the share still working when the cap fires is at least that,")
    print("    and the upper tail of demand is UNRESOLVED. No value for the cap")
    print("    can be derived from this data; it can only be shown too low.")

    print("\n4. THE CLOCK DOES NOT BOUND THE DISPATCH")
    el_raw = np.array([x["elapsed"] for x in cut])
    bad = int(np.isnan(el_raw).sum())
    el = el_raw[~np.isnan(el_raw)]
    iters = np.array([x["iters"] for x in cut], dtype=float)[~np.isnan(el_raw)]
    spi = np.median(el / iters)
    if bad:
        print(f"    {bad} capped reply/replies carry a NON-NUMERIC elapsed_s and are")
        print("    excluded from the timings rather than counted as 0")
    print(f"    capped replies: median elapsed {np.median(el):.1f} s, max {el.max():.1f} s")
    print(f"    median seconds per iteration {spi:.2f}")
    print(f"    the per-request timeout is 300 s and 1 reply elapsed {el.max():.1f} s,")
    print("    so the timeout is PER REQUEST and imposes no total bound.")

    print("\n5. COST, FROM THE 3 LIVE-PRICED ANCHORS THE PANEL FILE RECORDS")
    X = np.array([a for a, _ in COST_ANCHORS]); Y = np.array([b for _, b in COST_ANCHORS])
    c_np = np.polyfit(X, Y, 2)
    a_, b_, c_ = sp.symbols("a b c")
    sol = sp.solve([a_*sp.Rational(str(x))**2 + b_*sp.Rational(str(x)) + c_
                    - sp.Rational(str(y)) for x, y in zip(X, Y)],
                   [a_, b_, c_], dict=True)[0]
    diff = max(abs(c_np[0] - float(sol[a_])), abs(c_np[1] - float(sol[b_])),
               abs(c_np[2] - float(sol[c_])))
    print(f"    quadratic fits all 3 anchors exactly; NumPy and SymPy agree to {diff:.1e}")
    print(f"    cost(n) = {float(sol[a_]):.5f} n^2 + {float(sol[b_]):.5f} n "
          f"+ {float(sol[c_]):.5f}")
    for v in (16, 20, 24, 32):
        print(f"      {v:2} iterations -> {float(np.polyval(c_np, v)):7.4f} GBP worst case")
    print("    his spend approval of 2026-09-20: up to 10 pounds, cheaper better.")
    print("    24 costs 7.2120 and is inside it; 32 costs 12.1120 and is excluded")
    print("    BY THE APPROVAL rather than by any judgement.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
