# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 05a5e28cc2a046e3a1d3a497bf01d097fcb8b084f230855f3cb3d93db717f72a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: the critical partition counts falsifier-REFUTED findings.

Imports the REAL readers. Builds a registry holding one entry whose severity is
asserted 0.9 and whose falsifier verdict is REFUTED while its STATUS is OPEN
(the status filter does not remove it). The appendix 7.7 KEY PROPERTY says a
disproved finding receives zero severity; if any of the three gating partition
readers counts it as a critical discovery, the defect is present: raise
AssertionError and print FALSIFIED. Exits clean iff the defect is absent.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as rr  # noqa: E402


def _reg(entries):
    r = rr.FindingRegistry()
    r.entries = entries
    return r


def main() -> int:
    e = {
        "canonical_id": "C0001", "severity": 0.9, "status": "OPEN",
        "falsifier_verdict": "REFUTED", "open_since_round": 1,
        "description": "`wilson_interval` mis-centres the numerator",
    }
    reg = _reg({"C0001": dict(e)})
    failures = []

    _, crit = rr._settled_novelty_series(reg, 3)
    if sum(crit) != 0:
        failures.append(f"_settled_novelty_series: REFUTED 0.9 -> crit_s {crit}")

    _, crit = rr._corroborated_novelty_series(reg, 3)
    if sum(crit) != 0:
        failures.append(f"_corroborated_novelty_series: REFUTED 0.9 -> crit_s {crit}")

    series = rr._location_keyed_critical_series(reg, 3, ["wilson_interval"])
    if sum(series) != 0:
        failures.append(
            f"_location_keyed_critical_series: REFUTED 0.9 -> series {series}")

    # The A4-relevant population must NOT be de-escalated: an UNRESOLVED
    # (verdict-less) 0.9 stays critical in every reader.
    e2 = dict(e, falsifier_verdict=None)
    reg2 = _reg({"C0001": e2})
    _, crit = rr._settled_novelty_series(reg2, 3)
    if sum(crit) != 1:
        failures.append(f"UNRESOLVED 0.9 de-escalated in settled series: {crit}")
    _, crit = rr._corroborated_novelty_series(reg2, 3)
    if sum(crit) != 1:
        failures.append(f"UNRESOLVED 0.9 de-escalated in corroborated series: {crit}")
    series = rr._location_keyed_critical_series(reg2, 3, ["wilson_interval"])
    if sum(series) != 1:
        failures.append(f"UNRESOLVED 0.9 de-escalated in location series: {series}")

    if failures:
        print("FALSIFIED")
        raise AssertionError("defect present: " + "; ".join(failures))
    print("defect NOT demonstrated: all three partition readers satisfy the "
          "key property and do not de-escalate unresolved criticals. EXIT=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
