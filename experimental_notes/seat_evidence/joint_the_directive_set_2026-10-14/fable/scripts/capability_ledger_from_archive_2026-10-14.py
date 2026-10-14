# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 30952faf37118775a217802dd4fdbaf27bb054202e3e4fc831a42d0c167bff5e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Capability ledger from the ARCHIVE -- the minimal additive wiring (J4).

`bench/capability_identity.py` was built by both blind seats and adopted by
neither the orchestrator nor this joint round, because wiring measured
capability into seat selection is a design change on the model-names question
(the founder's ruling to apply). What IS additive without touching dispatch:
the accumulating MEASUREMENT that ruling will need. The archive already
records, per registry entry, the authoring identity (`source_model`) and the
runner's independent re-execution verdict (`falsifier_verdict`). This producer
turns that into the capability ledger: per identity, determinate outcomes,
confirms, point rate, and the Wilson LOWER BOUND the ranking must use so a
lucky 1/1 cannot outrank a seasoned mid-rate identity.

It changes which seat gets which work in NO way. It reads logs and prints.

DECLARED LIMITS (named, not hidden):
  - no admissibility bit exists in the archive schema, so this is the
    confirm rate, an UPPER BOUND on the admissible-confirm rate;
  - `source_model` is the FINDING's author; where a falsifier had a different
    author the archive does not say so;
  - identities with fewer than 43 determinate outcomes (n >= z^2/delta^2 at
    delta=0.3; SymPy and Wolfram Language both give 42.6829 -> 43) are
    printed UNRANKED -- cold-start policy is the routing ladder's question,
    not this ledger's.
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys

_Z = 1.959963984540054
MIN_OUTCOMES = 43


def wilson_lb(k: int, n: int) -> float:
    if n == 0:
        return 0.0
    p = k / n
    den = 1 + _Z * _Z / n
    centre = p + _Z * _Z / (2 * n)
    half = _Z * math.sqrt(p * (1 - p) / n + _Z * _Z / (4 * n * n))
    return (centre - half) / den


def build_ledger(logs_glob: str = "bench/logs/*/runner_state.json") -> dict:
    seen, ledger = set(), {}
    for p in sorted(glob.glob(logs_glob)):
        rp = os.path.realpath(p)
        if rp in seen:            # exp36_evidence_latest symlink class
            continue
        seen.add(rp)
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for v in d.get("registry", {}).get("entries", {}).values():
            if not isinstance(v, dict):
                continue
            verdict = str(v.get("falsifier_verdict") or "").upper()
            if not verdict.startswith(("CONFIRMED", "REFUTED")):
                continue
            ident = str(v.get("source_model") or "UNATTRIBUTED")
            n, k = ledger.get(ident, (0, 0))
            ledger[ident] = (n + 1, k + (1 if verdict.startswith("CONFIRMED") else 0))
    return ledger


def main() -> int:
    ledger = build_ledger()
    if not ledger:
        print("no determinate outcomes found"); return 1
    rows = [(ident, n, k, k / n, wilson_lb(k, n)) for ident, (n, k) in ledger.items()]
    measured = sorted((r for r in rows if r[1] >= MIN_OUTCOMES), key=lambda r: -r[4])
    cold = sorted((r for r in rows if r[1] < MIN_OUTCOMES), key=lambda r: -r[1])
    print(f"=== CAPABILITY LEDGER (archive, symlink-deduplicated; "
          f"{sum(n for n, _ in ledger.values())} determinate outcomes) ===")
    print("RANKED (n >= 43, by Wilson lower bound -- never the point estimate):")
    for ident, n, k, pt, lb in measured:
        print(f"  {ident:<16} k/n={k}/{n:<4} point={pt:.4f}  wilson_lb={lb:.4f}")
    print("UNRANKED (cold start, n < 43 -- ordering is the routing ladder's call):")
    for ident, n, k, pt, lb in cold:
        print(f"  {ident:<16} k/n={k}/{n:<4} point={pt:.4f}  wilson_lb={lb:.4f}")
    print("\nCaveats: confirm rate is an UPPER BOUND on admissible-confirm rate "
          "(no admissibility bit in archive schema); identity = source_model.\n"
          "MEASURED 2026-10-14: the ranking is NOT robust to the denominator -- "
          "counting ERROR verdicts as failures reorders it (Fable-SIM first vs "
          "CC2-SIM first). The founder rules on the outcome definition BEFORE "
          "any ranking is wired anywhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
