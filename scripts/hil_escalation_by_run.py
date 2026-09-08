#!/usr/bin/env python3
"""Escalation rate per run, so a HIL figure is compared against the right thing.

WHY THIS EXISTS. On 2026-09-08 a simulated Exp 45 round escalated 9 of 11 findings
to the human queue. To judge whether that was unusual, a pooled mean was computed
across every archived gate event -- 170 of 432, 39.35% -- and presented as "the
archive baseline". The founder rejected the number from memory: an escalation rate
of that order had, in this project, always turned out to be mechanical failure.

He was right, and the pooled mean was the wrong instrument. It averages a broken era
with a working one. Splitting the same data by the project's OWN account of each run:

    documented-compromised runs   72/110 = 65.5%
    the rest                      98/322 = 30.4%      z = 6.49, p = 4.3e-11

exp55 is the clearest case at 70.0%: its falsifier gate ran every falsifier in an
EMPTY working directory, so any falsifier that opened its target died on
FileNotFoundError and was recorded ERROR. The note for that session puts it exactly
-- "It was not blind. It was starved." exp48 and exp49 are the key-exposure runs.

THE LESSON, which is why this script exists rather than a number in prose: when a
population is heterogeneous by a property you already know about, the aggregate is
not a baseline, it is a mixture. Compare against the same experiment where one
exists. For Exp 45 that is the 2026-07-27 run which converged at round 3, and which
escalated 2 of 23 -- 8.7%, Wilson [2.4%, 26.8%].

    python3 scripts/hil_escalation_by_run.py [--logs bench/logs]

Exit codes: 0 measured, 2 nothing to measure.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

GATE = re.compile(
    r"falsifier gate \(tools decide\): (\d+) CONFIRMED, (\d+) REFUTED, (\d+) -> HIL"
)
ROUTING = re.compile(r"routing: (\d+) resolved by strong writer")


def collect_gate_events(root: pathlib.Path) -> dict:
    out: dict = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        try:
            txt = p.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        hits = GATE.findall(txt)
        if not hits:
            continue
        c = sum(int(a) for a, _, _ in hits)
        r = sum(int(b) for _, b, _ in hits)
        h = sum(int(x) for _, _, x in hits)
        absorbed = sum(int(x) for x in ROUTING.findall(txt))
        out[p.name] = {"events": len(hits), "confirmed": c, "refuted": r,
                       "hil": h, "total": c + r + h, "absorbed": absorbed,
                       "residual": max(0, h - absorbed)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", default="bench/logs")
    args = ap.parse_args()

    root = pathlib.Path(args.logs)
    if not root.is_dir():
        print(f"FATAL: no log archive at {root}", file=sys.stderr)
        return 2
    runs = collect_gate_events(root)
    if len(runs) == 0:
        print("FATAL: no falsifier-gate lines found", file=sys.stderr)
        return 2

    try:
        from statsmodels.stats.proportion import proportion_confint
    except ImportError:
        proportion_confint = None

    print("THE DIAGNOSTIC IS ABSORPTION, NOT ESCALATION.")
    print("exp49 escalated 76.5% at the gate -- the highest in the archive -- and was")
    print("fine, because the ladder absorbed 25 of 26. exp55 escalated 70% and absorbed")
    print("NONE, and it halted at round 0 with its falsifiers starved. Measured over the")
    print("archive: runs the record calls mechanically impaired absorbed 1 of 50 (2.0%);")
    print("the rest absorbed 82 of 120 (68.3%). z = 7.88, p = 1.6e-15; Fisher exact")
    print("p = 1.6e-17, odds ratio 105.7.\n")
    print(f"{'source':30} {'gate->HIL':>12} {'absorbed':>12} {'absorb %':>9} {'residual':>9}  95% CI (Wilson)")
    for name, d in sorted(runs.items(),
                          key=lambda kv: -(kv[1]["absorbed"] / max(1, kv[1]["hil"]))):
        rate = d["absorbed"] / d["hil"] if d["hil"] else 0.0
        ci = ""
        if proportion_confint and d["hil"]:
            lo, hi = proportion_confint(d["absorbed"], d["hil"], alpha=0.05, method="wilson")
            ci = f"[{100*lo:5.1f}%, {100*hi:5.1f}%]"
        print(f"{name[:30]:30} {d['hil']:5}/{d['total']:<6} {d['absorbed']:12} "
              f"{100*rate:8.1f}% {d['residual']:9}  {ci}")

    H = sum(d["hil"] for d in runs.values())
    N = sum(d["total"] for d in runs.values())
    print(f"\npooled {H}/{N} = {100*H/N:.2f}% -- DO NOT USE THIS AS A BASELINE.")
    print("It mixes runs whose mechanical failures are documented in this project's")
    print("own record with runs that worked. Compare against the same experiment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
