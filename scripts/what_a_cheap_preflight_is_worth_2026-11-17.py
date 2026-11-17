#!/usr/bin/env python3
"""What a cheap pre-flight is worth, and why the wide one can never pay.

Measured on the night of 2026-11-17, when 2 commit boards refused in a row and
a 3rd passed. Each refusal costs a full board and produces nothing, so a cheap
subset of guards run BEFORE the board is worth whatever it saves minus what it
costs. That trade is arithmetic and is computed here rather than argued.

THE DECISIVE RESULT IS THE NEGATIVE ONE. A 16-file pre-flight measured at
1044.15 s would have to catch MORE THAN ALL refusals to break even, which is
impossible, so it is refused on arithmetic and not on taste. The 4-file version
at 122.64 s needs about 1 refusal in 7.

WHAT IS MEASURED AND WHAT IS NOT, STATED BECAUSE THE DIFFERENCE IS THE WHOLE
HONESTY OF THE THING. The COSTS are measured: 122.64 s and 1044.15 s, both
timed by wall clock on this machine. The refusal RATE is measured from the
gate's own ledger. The CATCH RATE is NOT measured: the 4 files were chosen
AFTER seeing which guards refused the 2 boards, so "it caught both" is a
post-hoc fit and carries no predictive weight. What the script therefore
reports is the break-even catch rate -- the share of refusals the subset must
catch to pay for itself -- which needs no estimate of how often it will.

Run: python3 scripts/what_a_cheap_preflight_is_worth_2026-11-17.py
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / ".cdsfl_tmp" / "precommit_durations.jsonl"

#: Rows under this are indeterminate, not fast refusals: a board killed by hand
#: records a short duration and exit 1, shape-identical to a quick refusal, so
#: counting them reports an interruption as a verdict. Same constant the cost
#: producer has used since commit fc0b2e60.
INTERRUPTED_UNDER_SECONDS = 120

#: Wall-clock costs timed on 2026-11-17 on this machine.
CANDIDATES = {
    "4 files, 88 tests": 122.64,
    "16 files, 2255 tests": 1044.15,
}


def _cli(doc: str) -> None:
    """Answer --help WITHOUT reading the ledger or computing anything."""
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the measurement.",
    ).parse_args()


def determinate_rows() -> list[dict]:
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        s = r.get("seconds")
        if isinstance(s, (int, float)) and float(s) >= INTERRUPTED_UNDER_SECONDS:
            out.append(r)
    return out


def break_even(cost_s: float, mean_board_s: float, refusal_rate: float) -> float:
    """Share OF REFUSALS the subset must catch to pay for itself.

    Running it on every board costs `cost_s` per board. Catching a refusal saves
    a whole board. So it breaks even when
        cost_s = P(caught) * mean_board_s
    and P(caught) = refusal_rate * catch_rate, giving
        catch_rate = cost_s / (mean_board_s * refusal_rate).
    A value above 1 is unreachable: the subset cannot pay for itself even if it
    caught every refusal there is.
    """
    return cost_s / (mean_board_s * refusal_rate)


def main(argv: list[str] | None = None) -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()

    rows = determinate_rows()
    if not rows:
        print("  the ledger is absent or holds no determinate row; nothing to compute")
        return 1

    import numpy as np                                     # noqa: PLC0415
    from statsmodels.stats.proportion import proportion_confint  # noqa: PLC0415
    import mpmath as mp                                    # noqa: PLC0415
    mp.mp.dps = 40

    d = np.array([float(r["seconds"]) for r in rows])
    refused = sum(1 for r in rows if r.get("exit") not in (0, None))
    n = len(rows)
    rate = refused / n

    print(f"== the gate's own ledger, {n} determinate row(s) ==")
    print(f"   mean board   {d.mean():.2f} s = {d.mean() / 60:.2f} min")
    print(f"   median board {float(np.median(d)):.1f} s = {float(np.median(d)) / 60:.2f} min")
    w = proportion_confint(refused, n, method="wilson")
    c = proportion_confint(refused, n, method="beta")
    print(f"   REFUSED {refused} of {n} = {rate:.6f}")
    print(f"     Wilson [{w[0]:.6f}, {w[1]:.6f}]  Clopper-Pearson [{c[0]:.6f}, {c[1]:.6f}]")

    def tail_le(q, k, nn):
        return mp.fsum([mp.binomial(nn, i) * mp.mpf(q) ** i * (1 - mp.mpf(q)) ** (nn - i)
                        for i in range(0, k + 1)])

    def bisect(f, lo, hi, it=200):
        for _ in range(it):
            m = (lo + hi) / 2
            if f(m) < 0:
                lo = m
            else:
                hi = m
        return float((lo + hi) / 2)

    hi2 = 1.0 if refused == n else bisect(
        lambda q: float(mp.mpf("0.025") - tail_le(q, refused, n)), 0.0, 1.0)
    print(f"     mpmath exact upper tail {hi2:.6f} (agrees to {abs(hi2 - c[1]):.2e})")
    print()

    print("== break-even catch rate for each candidate ==")
    print("   (the share OF REFUSALS it must catch to pay for itself)")
    verdicts = {}
    for name, cost in CANDIDATES.items():
        be = break_even(cost, float(d.mean()), rate)
        reachable = be < 1.0
        verdicts[name] = (cost, be, reachable)
        note = (f"needs 1 refusal in {1 / be:.1f}" if reachable
                else "UNREACHABLE -- costs more than every refusal is worth")
        print(f"   {name:24s} {cost:8.2f} s  break-even {be:.6f}  {note}")
    print()

    #: sympy as an independent route to the same ratio, per the 2-tool rule.
    import sympy as sp                                     # noqa: PLC0415
    for name, (cost, be, _) in verdicts.items():
        exact = sp.Rational(str(cost)) / (sp.Rational(str(round(float(d.mean()), 6)))
                                          * sp.Rational(refused, n))
        agree = abs(float(exact) - be)
        print(f"   {name:24s} sympy exact {float(exact):.6f}  agrees to {agree:.2e}")
    print()

    print("== VERDICT ==")
    narrow = verdicts["4 files, 88 tests"]
    wide = verdicts["16 files, 2255 tests"]
    print(f"   the narrow subset can pay for itself : {narrow[2]}")
    print(f"   the wide subset can pay for itself   : {wide[2]}")
    print(f"   the wide one is {wide[0] / narrow[0]:.2f}x the cost and "
          f"{wide[1] / narrow[1]:.2f}x the required catch rate")
    print()
    print("   NOT MEASURED: the actual catch rate. The 4 files were selected after")
    print("   seeing which guards refused 2 boards on 2026-11-17, so no predictive")
    print("   claim is made here and none should be quoted from it.")
    ok = narrow[2] and not wide[2]
    print(f"   both verdicts established: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
