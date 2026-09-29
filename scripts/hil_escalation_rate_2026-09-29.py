#!/usr/bin/env python3
"""Per-round human-escalation rate from a run's own log, with intervals.

WHY THIS EXISTS. Founder standing observation, 2026-09-29, verbatim in substance:
an unusually high human-escalation queue has, across this project's whole record
so far, ALWAYS indicated broken machinery, has never matched the project's own
formal escalation criteria, and has always proved computationally reducible. So
escalation volume is a fault detector, and a fault detector needs a producer
rather than a glance at a log.

It also discharges `measured-rate-travels-with-its-script` (founder ruling
2026-09-04): a rate quoted to the founder must have a committed script behind it.
Every HIL figure reported for this shakedown comes from here.

WHAT IT MEASURES, AND WHAT IT DELIBERATELY DOES NOT. It reads the falsifier
gate's own tally line -- `falsifier gate (tools decide): N CONFIRMED, M REFUTED,
K -> HIL` -- and the routing line's own `K -> HIL`, because those are the run's
OWN counts of what it escalated, not a reconstruction. It does NOT judge whether
an escalation was correct; that is the reason text's job and the reasons are
printed beside the rate so a reader can see them.

THE RATE ALONE IS NOT THE SIGNAL, AND THIS IS THE TRAP THIS SCRIPT EXISTS TO
AVOID. On the 2026-09-29 arm 1 run, round 0 escalated 2 of 14 (14.2857%) and
round 1 escalated 2 of 6 (33.3333%) -- an apparent doubling that is nothing:
Fisher exact p = 0.5492, and the Wilson intervals [4.0094%, 39.9414%] and
[9.6771%, 70.0007%] overlap almost entirely. Reading a rise off 2 small rounds is
how a noise excursion becomes a reported finding. Every rate here therefore
carries an interval, and a between-round comparison carries a Fisher test.

Cross-verification per the 2026-04-21 rule: every interval is computed twice,
by statsmodels and by a local closed form, and both are printed.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The falsifier gate's own tally. The run writes this; it is not reconstructed.
_GATE = re.compile(
    r"falsifier gate \(tools decide\):\s*(\d+)\s+CONFIRMED,\s*(\d+)\s+REFUTED,"
    r"\s*(\d+)\s*->\s*HIL")
#: Routing's own tally, which escalates separately.
_ROUTING = re.compile(
    r"routing:.*?(\d+)\s*->\s*HIL", re.S)
_ROUND = re.compile(r"Round (\d+)/(\d+)")
#: Reasons, printed beside the rate so volume is never read without cause.
_REASON = re.compile(
    r"(MECHANICAL FAULT[^\n]*|ESCALATED to HIL[^\n]*|"
    r"Escalated \d+ UNCERTAIN[^\n]*|recommend HIL audit[^\n]*)")


def wilson_local(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def wilson_sm(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (0.0, 0.0)
    return tuple(proportion_confint(k, n, alpha=0.05, method="wilson"))


def report(label: str, k: int, n: int) -> None:
    lo_l, hi_l = wilson_local(k, n)
    try:
        lo_s, hi_s = wilson_sm(k, n)
        agree = max(abs(lo_l - lo_s), abs(hi_l - hi_s))
    except Exception as exc:                                  # noqa: BLE001
        lo_s = hi_s = float("nan"); agree = float("nan")
        print(f"    (statsmodels unavailable: {exc})")
    pct = 100.0 * k / n if n else 0.0
    print(f"{label}: {k} of {n} = {pct:.4f}%")
    print(f"    Wilson 95% local       [{100*lo_l:.4f}%, {100*hi_l:.4f}%]")
    print(f"    Wilson 95% statsmodels [{100*lo_s:.4f}%, {100*hi_s:.4f}%]")
    print(f"    two implementations agree to {agree:.3e}")


def parse(text: str):
    """Attribute each gate tally to the round it appeared in."""
    rounds: list[dict] = []
    current = None
    for line in text.splitlines():
        m = _ROUND.search(line)
        if m:
            current = {"round": int(m.group(1)), "confirmed": 0,
                       "refuted": 0, "hil": 0, "routing_hil": 0, "reasons": []}
            rounds.append(current)
            continue
        if current is None:
            continue
        g = _GATE.search(line)
        if g:
            current["confirmed"] += int(g.group(1))
            current["refuted"] += int(g.group(2))
            current["hil"] += int(g.group(3))
            continue
        r = _ROUTING.search(line)
        if r:
            current["routing_hil"] += int(r.group(1))
            continue
        rs = _REASON.search(line)
        if rs:
            current["reasons"].append(rs.group(1).strip()[:150])
    return rounds


def main() -> int:
    ap = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="Per-round HIL escalation rate from a run log, with Wilson "
                    "intervals and a between-round Fisher test.",
        epilog="Answers --help without reading anything. Exit 0 always unless a "
               "log is unreadable; a HIGH rate is reported, never enforced.")
    ap.add_argument("log", nargs="?",
                    default=str(REPO / "bench/logs/shakedown_2026-09-29"
                                       "/cycle2_arm1.log"),
                    help="run log to read")
    args = ap.parse_args()

    p = Path(args.log)
    if not p.is_file():
        print(f"no such log: {p}", file=sys.stderr)
        return 2
    rounds = parse(p.read_text(encoding="utf-8", errors="ignore"))
    if not rounds:
        print("no round boundary found; nothing to measure "
              "(this is a completed check, not a failure)")
        return 0

    print("=" * 74)
    print(f"HIL ESCALATION BY ROUND — {p.name}")
    print("=" * 74)
    print()
    tk = tn = 0
    assessed = []
    for r in rounds:
        n = r["confirmed"] + r["refuted"] + r["hil"]
        if n == 0:
            print(f"round {r['round']}: no gate tally yet\n")
            continue
        tk += r["hil"]; tn += n
        assessed.append((r["round"], r["hil"], n))
        report(f"round {r['round']} falsifier-gate escalation", r["hil"], n)
        if r["routing_hil"]:
            print(f"    routing escalated a further {r['routing_hil']}")
        for reason in r["reasons"]:
            print(f"    REASON: {reason}")
        print()

    if tn:
        report("CUMULATIVE", tk, tn)
        print()

    # A rise across 2 small rounds is usually noise. Say so with a test.
    if len(assessed) >= 2:
        from scipy.stats import fisher_exact
        (ra, ka, na), (rb, kb, nb) = assessed[-2], assessed[-1]
        odds, pv = fisher_exact([[ka, na - ka], [kb, nb - kb]])
        print(f"BETWEEN THE LAST 2 ROUNDS ({ra} vs {rb}), Fisher exact: "
              f"p = {pv:.4f}, odds ratio {odds:.4f}")
        print("    p above 0.05 means the apparent change is not distinguishable")
        print("    from noise at these round sizes. Do NOT report a rise from it.")
    print()
    print("REASONS ARE PRINTED ABOVE BECAUSE VOLUME WITHOUT CAUSE IS NOT A")
    print("FINDING. An escalation the discrimination control raised is that")
    print("control WORKING; a queue with no named mechanical cause is the")
    print("signature the founder named.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
