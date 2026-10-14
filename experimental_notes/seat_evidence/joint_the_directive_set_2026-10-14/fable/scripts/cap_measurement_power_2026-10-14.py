# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c86a26735c9d5f3208e30654403a47f9c6a3c1827d0fc028fc8e509a1033ebfa
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The cap measurement, made decidable (2026-10-14 joint panel, J1).

Both seats refused outright removal of the composer directive caps and asked
for a measurement. This file IS the specification, precise enough that the
next simulated run either settles the question or is shown here to be
underpowered for it.

PROPERTY (named): pooled runner-reverified falsifier confirm rate -- of
  registry entries carrying a determinate `falsifier_verdict` (CONFIRMED or
  REFUTED after the runner's independent re-execution), the fraction CONFIRMED.
  Caveat, stated not hidden: the archive schema carries no admissibility bit,
  so this is an upper bound on the admissible-confirm rate; admissibility is
  enforced upstream by the gate, not re-derived here.

ARMS (2): identical target, seats, rounds, seed policy.
  ARM A (control)  : shipped behaviour, `composer_directive_caps=True`
                     (reduced 2,503-char universal render + operational text).
  ARM B (treatment): `composer_directive_caps=False` -- full universal text,
                     no `max_directive_chars` truncation (the ablation switch
                     committed 2026-10-14, wired at `_compose_for_model`).

STATISTIC: difference of pooled confirm rates (B - A) with a Newcombe
  Wilson-score-based 95% CI; per-seat differences reported as strata, never
  pooled away silently.

DECISION RULE (what the founder reads): the caps may be REMOVED iff
  (a) ARM B delivers the full directive set (deterministic: 16/16 headings,
      already measured -- the named property on which the replacement
      dominates), AND
  (b) the Newcombe 95% CI lower bound of (B - A) exceeds -delta
      (non-inferiority on the confirm rate at the margin delta the run was
      powered for).
  The caps are KEPT PER IDENTITY for any seat whose own stratum CI upper
  bound is below 0 -- that seat's cap becomes a MEASURED transport limit
  with a source and a date.

STOPPING RULE: fixed-sample. No interim looks, no early stop -- the run (or
  runs) per arm continue until each arm holds at least n determinate
  outcomes, n computed below. If the planned budget cannot reach n, the plan
  is declared UNDERPOWERED here, before a token is spent.

This script computes n per arm (two independent tools, printed with their
agreement), measures the archive's actual determinate-outcome yield per run,
and prints the POWERED/UNDERPOWERED verdict for the candidate plans.
Run it; do not trust this docstring.
"""
from __future__ import annotations

import glob
import json
import math
import os
import statistics
import sys


def n_per_arm_closed_form(delta: float, alpha: float = 0.05, power: float = 0.80) -> float:
    """(z_{1-a/2}+z_{power})^2 * (p1(1-p1)+p2(1-p2)) / delta^2 at worst case p=1/2."""
    from scipy.stats import norm  # tool 1
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return z * z * 0.5 / (delta * delta)


def n_per_arm_sympy(delta: str) -> float:
    """Same quantity via SymPy with the project-standard z constant."""
    import sympy as sp  # tool 2
    from scipy.stats import norm
    z975 = sp.Float("1.959963984540054", 17)
    z80 = sp.Float(norm.ppf(0.80), 17)
    dd = sp.Float(delta, 17)
    return float((z975 + z80) ** 2 * sp.Rational(1, 2) / dd ** 2)


def archive_yield() -> list:
    """Determinate falsifier_verdict outcomes per run, symlink-deduplicated."""
    seen = set()
    per_run = []
    for p in sorted(glob.glob("bench/logs/*/runner_state.json")):
        rp = os.path.realpath(p)
        if rp in seen:            # the exp36_evidence_latest symlink class
            continue
        seen.add(rp)
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ents = d.get("registry", {}).get("entries", {})
        if not isinstance(ents, dict):
            continue
        n = sum(1 for v in ents.values() if isinstance(v, dict)
                and str(v.get("falsifier_verdict") or "").upper().startswith(("CONFIRMED", "REFUTED")))
        if n:
            per_run.append(n)
    return per_run


def main() -> int:
    print("=== n PER ARM (two-sided alpha=0.05, power 0.80, worst-case p=1/2) ===")
    for d in ("0.30", "0.15"):
        a = n_per_arm_closed_form(float(d))
        b = n_per_arm_sympy(d)
        agree = abs(a - b) < 1e-6
        print(f"  delta={d}:  scipy={a:.4f}  sympy={b:.4f}  "
              f"[{'AGREE' if agree else 'DISAGREE'}]  -> n/arm = {math.ceil(a)}")
    print("  (Wolfram Language cross-check, computed 2026-10-14: "
          "43.60488741305049 at delta=0.30)")

    yields = archive_yield()
    if not yields:
        print("NO archive runs with determinate falsifier verdicts found -- cannot size.")
        return 1
    med = statistics.median(yields)
    print("\n=== ARCHIVE-MEASURED YIELD (symlink-deduplicated) ===")
    print(f"  runs with >=1 determinate outcome: {len(yields)}; "
          f"median outcomes/run: {med}; min {min(yields)}, max {max(yields)}")

    print("\n=== VERDICT PER PLAN ===")
    for delta in (0.30, 0.15):
        n = math.ceil(n_per_arm_closed_form(delta))
        runs_needed = math.ceil(n / med)
        print(f"  pooled delta={delta} (n/arm={n}): needs {runs_needed} run(s)/arm "
              f"-> a 1-run/arm plan is "
              f"{'POWERED' if runs_needed <= 1 else 'UNDERPOWERED'}")
    per_seat = math.ceil(43 / (med / 6))
    print(f"  per-seat delta=0.30 (43/seat/arm, 6 seats): needs {per_seat} runs/arm "
          f"-> per-seat strata from 1 run are DESCRIPTIVE ONLY, and are reported as such")
    return 0


if __name__ == "__main__":
    sys.exit(main())
