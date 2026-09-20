#!/usr/bin/env python3
"""Which figures quoted in the round-3 panel brief can actually be reproduced?

WHY THIS EXISTS. The project rule `measured-rate-travels-with-its-script` says a
measured rate may be cited only if the script that produced it is committed
alongside it. The round-3 brief (bench/logs/maths_panel_2026-09-20_r3/BRIEF.md)
presented several figures to 7 seats as SETTLED. This script asks, of each one,
the only question that matters: is there a committed producer that regenerates
it, and does running that producer give the stated number?

THE FAILURE THIS FOUND, and it was CC1's. The brief's Section 4 T3 stated
"75.8%, Wilson [74.2%, 77.3%]" over 2,880 grid points as settled, executed
evidence. It came from the fable seat's round-1 prose. fable's delivered script,
maths_revision_seat_checks_2026-09-20.py, runs 23 of 23 checks green and does not
contain that measurement at all. Nobody re-ran it -- in round 3 fable itself
wrote that its own 75.8% figure was "accepted as settled per the brief, not
re-executed here". Two further seats, cx and cgpt, correctly marked it
UNVERIFIED and accepted it only on the brief's authority.

So an unreproducible figure was promoted into a brief as settled and travelled
to 7 seats. The seats behaved correctly; the brief did not. That is the rule
working in reverse, and it is recorded here rather than quietly dropped.

Run:  python3 scripts/panel_figure_provenance_2026-09-20.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "bench/logs/maths_panel_2026-09-20"
R3 = ROOT / "bench/logs/maths_panel_2026-09-20_r3"

# Each entry: the figure, where the brief got it, and the candidate producer.
FIGURES = [
    {
        "label": "over-refusal 75.8% over 2,880 points",
        "pattern": r"75\.8|0\.7579",
        "source": "fable round-1 prose (brief Section 4, T3)",
        "producer": R1 / "sandbox_harvest/fable/attempt-1/files/scripts/maths_revision_seat_checks_2026-09-20.py",
    },
    {
        "label": "over-refusal 10.4882% over 28,880 points",
        "pattern": r"10\.4882",
        "source": "cc2 round-3, delivered script",
        "producer": R3 / "sandbox_harvest/cc2/attempt-1/files/scripts/phase2_interpolation_overstates_risk_2026-09-20.py",
    },
    {
        "label": "gate threshold 0.504931170970423 and closure at nu_b = 1/4",
        "pattern": r"0\.504931170970423",
        "source": "cc2 round-3, delivered script",
        "producer": R3 / "sandbox_harvest/cc2/attempt-1/files/scripts/gate_collapses_to_one_constant_2026-09-20.py",
    },
    {
        "label": "degeneracy is a line, 1 free direction",
        "pattern": r"1 free direction",
        "source": "CC1, committed producer",
        "producer": ROOT / "scripts/free_parameter_degeneracy_2026-09-20.py",
    },
]


def run(producer: Path) -> tuple[bool, str]:
    if not producer.exists():
        return False, f"producer absent: {producer}"
    try:
        p = subprocess.run([sys.executable, str(producer)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return False, "producer timed out"
    return p.returncode == 0, (p.stdout or "") + (p.stderr or "")


def main(argv: list | None = None) -> int:
    # `--help` MUST NEVER COST MONEY, and must never run a measurement either.
    # argparse is constructed and parsed BEFORE any archive walk or subprocess,
    # so the flag is answered rather than consumed as a positional argument.
    # This project already carries the rule in its strong form, written after 15
    # of 17 runners billed a live dispatch on an unrecognised argument.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    print("PANEL FIGURE PROVENANCE, round 3, 2026-09-20")
    print("A figure is REPRODUCIBLE only if a committed producer regenerates it.")
    print()
    reproducible, orphaned = [], []
    for fig in FIGURES:
        ok, out = run(fig["producer"])
        found = bool(re.search(fig["pattern"], out)) if ok else False
        status = "REPRODUCED" if found else ("RAN, FIGURE ABSENT" if ok else "PRODUCER FAILED")
        print(f"  {status:20s}  {fig['label']}")
        print(f"      source  : {fig['source']}")
        print(f"      producer: {fig['producer'].relative_to(ROOT)}")
        if ok and not found:
            print("      note    : the script runs clean but does not compute this figure.")
        print()
        (reproducible if found else orphaned).append(fig["label"])

    print("-" * 70)
    print(f"Reproducible from a committed producer : {len(reproducible)}")
    for x in reproducible:
        print(f"    {x}")
    print(f"Cited but with no producer that makes it: {len(orphaned)}")
    for x in orphaned:
        print(f"    {x}")
    print()
    if orphaned:
        print("An orphaned figure is a claim about evidence, not evidence. The brief")
        print("presented at least one as settled, and it travelled to 7 seats on that")
        print("authority. The rule is not that the figure is wrong; it is that nothing")
        print("in the repository can tell us whether it is right.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
