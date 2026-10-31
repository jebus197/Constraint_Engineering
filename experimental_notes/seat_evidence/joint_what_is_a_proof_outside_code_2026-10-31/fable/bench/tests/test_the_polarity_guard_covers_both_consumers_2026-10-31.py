# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 70a948d4663954c839c9775dc30d76d3515937273f2b52bbca6c27c72df1afd3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The declared-polarity guard must cover BOTH deciding consumers of
`falsifier_verdict`: `spec_verification_factor` (severity) AND
`apply_falsifier_verdicts` (status). Round 2 of
what_is_a_proof_outside_code_b22: seat cc2's round-1 guard covered the first;
the executed falsifier `falsifier_the_status_channel_is_polarity_blind_...`
showed the second still resolved declared-proof entries. This pins the
composed repair and the untouched default path.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from bench.dm._types import Finding
from bench.reference_runner_v3 import (
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts,
    spec_verification_factor,
)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

HELD = "assert abs((0.0392**2+0.0049**2+0.1206**2)**0.5 - 0.1269) < 5e-4\nprint('held')\n"
FAILED = "assert abs((0.0392**2+0.0049**2+0.1206**2)**0.5 - 0.165) < 5e-4, 'FALSIFIED'\n"


def _f(fid, sev):
    return Finding(finding_id=fid, model_id="m", round_idx=0, flaw_class=2,
                   severity=sev, abstraction_index=0.5, description=fid)


def _gate(entries):
    reg = FindingRegistry()
    cids = []
    for fid, sev, code, pol in entries:
        cid = reg.register(_f(fid, sev), "m")
        reg.entries[cid]["falsifier_code"] = code
        if pol:
            reg.entries[cid]["verification_polarity"] = pol
        cids.append(cid)
    apply_falsifier_verdicts(reg, round_idx=1,
                             cfg=RunnerConfig(falsifier_gate_enabled=True),
                             repo_root=REPO)
    return reg, cids


def test_declared_proof_noncritical_is_not_silently_retired():
    reg, (cid,) = _gate([("p1", 0.5, HELD, "proof")])
    e = reg.entries[cid]
    assert e.get("status") != "REFUTED"
    assert e.get("proof_tristate") == "ADMISSIBLE"


def test_declared_mistaken_proof_critical_is_not_confirmed():
    reg, (cid,) = _gate([("p2", 0.85, FAILED, "proof")])
    e = reg.entries[cid]
    assert e.get("status") != "CONFIRMED" and not e.get("verified")
    assert e.get("falsifier_verdict") == "UNTOOLABLE"  # no finding falsifier ran
    assert e.get("escalated") is True                  # critical -> HIL
    assert e.get("proof_tristate") == "REJECTED"


def test_undeclared_entries_take_the_historical_path_unchanged():
    # A real defect-polarity falsifier that FIRES: CONFIRMED, as ever.
    reg, (cid,) = _gate([("p3", 0.85, FAILED, None)])
    e = reg.entries[cid]
    assert e.get("falsifier_verdict") == "CONFIRMED"
    assert e.get("status") == "CONFIRMED" and e.get("verified") is True
    # Severity consumer likewise untouched without a declaration.
    assert spec_verification_factor({"falsifier_verdict": "CONFIRMED"}) == 1.0
    assert spec_verification_factor({"falsifier_verdict": "REFUTED"}) == 0.0
