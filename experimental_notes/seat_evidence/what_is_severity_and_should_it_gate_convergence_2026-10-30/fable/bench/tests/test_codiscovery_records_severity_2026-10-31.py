# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'what_is_severity_and_should_it_gate_convergence_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e3e30c66526c54cc6db9bfdcfbdf995b687a4b250103f21aa9f3c31436632395
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Co-discovery must RECORD the second assessor's severity and combine it.

THE DEFECT, measured by scripts/is_severity_noise_or_disagreement_2026-10-19.py
over 152 registry entries with 2+ independent same-run assessments: the merge
keeps whichever record happened to be the registration target and discards the
rest, so the kept severity equals the median of its inputs in 21.05% of cases,
and lies OUTSIDE [min, max] of the assessments it came from in 35 of 152,
23.03%, Wilson [17.05%, 30.33%]. The number the CRITICAL cut reads is therefore
not traceable to the assessments beneath it.

THE FIX this test executes: `record_codiscovery` accepts the co-discovering
finding's own severity, stores it in the codiscovery record, and writes
`severity_combined` = `combine_independent_severities(...)` (the median) on the
entry. `entry["severity"]` -- the value every gate channel reads -- is NOT
touched, so gate behaviour is byte-identical; the combined figure is recorded
beside it and reaches the archived report through the registry dump.

Run directly as a falsifier: raises AssertionError and prints FALSIFIED iff the
defect is present (no severity parameter, severity not recorded, combined value
absent or not a function of its inputs). Exits cleanly when the fix holds.
"""
from __future__ import annotations

import inspect
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    Finding,
    FindingRegistry,
)


def _mk(fid: str, model: str, sev: float) -> Finding:
    return Finding(
        finding_id=fid, model_id=model, round_idx=1, flaw_class=2,
        severity=sev, abstraction_index=0.5, description="same defect",
    )


def test_codiscovery_records_and_combines_severity() -> None:
    reg = FindingRegistry()
    cid = reg.register(_mk("f1", "m1", 0.5), "m1")

    sig = inspect.signature(reg.record_codiscovery)
    assert "severity" in sig.parameters, (
        "record_codiscovery takes no severity: the co-discovering model's "
        "independent assessment is discarded at exactly the point it arrives"
    )

    added = reg.record_codiscovery(cid, "m2", "f9", 0.9, round_idx=2,
                                   severity=0.8)
    assert added is True
    e = reg.entries[cid]

    recs = [c for c in e.get("codiscovery", []) if c.get("finding_id") == "f9"]
    assert recs and isinstance(recs[0].get("severity"), (int, float)), (
        "codiscovery record carries no severity field"
    )
    assert abs(recs[0]["severity"] - 0.8) < 1e-9

    inputs = [0.5, 0.8]
    comb = e.get("severity_combined")
    assert isinstance(comb, (int, float)), "severity_combined was not written"
    assert min(inputs) <= comb <= max(inputs), (
        f"combined severity {comb} lies outside the range of its inputs "
        f"{inputs} -- the archived defect shape (35 of 152 kept values)"
    )
    assert abs(comb - 0.65) < 1e-9, f"median of {inputs} is 0.65, got {comb}"

    # The gate input is untouched: byte-identical convergence behaviour.
    assert abs(e["severity"] - 0.5) < 1e-12, (
        "entry['severity'] moved -- the fix must be recording-only"
    )

    # A third assessor: combined stays the median of ALL assessments.
    reg.record_codiscovery(cid, "m3", "f17", 0.9, round_idx=3, severity=0.9)
    comb3 = reg.entries[cid]["severity_combined"]
    assert abs(comb3 - 0.8) < 1e-9, (
        f"median of [0.5, 0.8, 0.9] is 0.8, got {comb3}"
    )

    # A non-numeric / absent severity must not break the legacy call shape.
    reg.record_codiscovery(cid, "m4", "f23", 0.9, round_idx=4)
    assert abs(reg.entries[cid]["severity_combined"] - 0.8) < 1e-9


if __name__ == "__main__":
    try:
        test_codiscovery_records_and_combines_severity()
    except AssertionError as exc:
        print("FALSIFIED:", exc)
        raise
    print("clean: co-discovery records the assessor's severity; "
          "severity_combined is the median of its inputs; the gate input "
          "entry['severity'] is untouched")
