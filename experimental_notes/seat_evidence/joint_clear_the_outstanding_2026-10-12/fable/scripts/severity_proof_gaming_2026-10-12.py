# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3f93991c7a20d5d4921bb2af1e5777f0c13f8bb3cd6be8662c3d3cf5f84bbf73
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Can severity_is_proven be gamed by self-consistent but WRONG inputs? Measured.

JOINT ROUND J3, 2026-10-12 — the decisive attack on the consolidated severity-
gate answer, executed against the real module. Two levels, both land:

LEVEL 1 — INPUT PROVENANCE. `_validate_rk_computation` recomputes R_k from the
model's OWN STATED inputs (R_old, q or eta*d*p, S_k, nu_eff) and compares with
the model's stated R_k. Nothing cross-checks those inputs against any registry
fact or tool measurement, so an invented-but-arithmetically-consistent block
passes: R_old=0.30, q=0.648, R_k=0.1312 -> PASS (recomputed 0.13108...,
cross-checked by SymPy and by Wolfram Language, local Wolfram Engine:
0.13108242303872889771...).

LEVEL 2 — THE PROVEN QUANTITY IS NOT THE GATED QUANTITY. `severity_is_proven`
reads only the proof STATUS. Nothing ties the proof's R_k to the entry's
severity float, so a proof whose own content is R_k = 0.95 — a HIGH residual
risk, consistently derived — buys the A4 release of a 0.45 severity float.
Measured below: A4 goes 1 -> 0 on exactly that proof.

WHAT THE GAMING BUYS, PRECISELY. The enforcement is one-directional by design:
a proof can only release a SUB-CRITICAL (float < 0.7, the model's own choice)
from blocking convergence; it cannot confirm, close, refute or demote. So the
gate does real work against HONEST noise (an unproven float still blocks at
its claimed value) and is gameable by an ADVERSARIAL seat — but an adversarial
seat already controls the float itself. The gate demonstrates USE of the
mathematical model, which is the founder's 2026-09-06 formulation; it does not
demonstrate that the inputs are true, and it does not demonstrate that the
float it releases has anything to do with the arithmetic shown.

Usage: python3 scripts/severity_proof_gaming_2026-10-12.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402

answer_help(__doc__)

import bench.reference_runner_v3 as rr  # noqa: E402


def main() -> int:
    blk1 = """
R_old = 0.30
q = 0.90 x 0.80 x 0.90 = 0.648
R_k = 0.30 * (1 - 0.648) / (1 - 0.648*0.30) = 0.1312
"""
    print("LEVEL 1, invented-but-consistent inputs:",
          rr._validate_rk_computation(blk1))

    blk2 = """
R_old = 0.95
q = 0.0
R_k = 0.95 * (1 - 0.0) / (1 - 0.0*0.95) = 0.95
"""
    st, mrk, rec = rr._validate_rk_computation(blk2)
    print("LEVEL 2, proof computing R_k = 0.95:", (st, mrk, rec))
    e = {
        "canonical_id": "C9100", "status": "UNCONFIRMED", "severity": 0.45,
        "description": "x", "falsifier_code": "", "falsifier_verdict": "",
        "verdicts": [], "open_since_round": 0, "last_status_change_round": 0,
        "severity_proof": {"status": st, "model_rk": mrk, "recomputed_rk": rec,
                           "delta": abs(mrk - rec), "round": 0},
    }
    print("severity_is_proven on a 0.95-risk proof excusing a 0.45 float:",
          rr.severity_is_proven(e))
    reg = rr.FindingRegistry()
    reg.entries["C9100"] = e
    a4_gamed = reg.unverified_critical_count()
    e2 = {k: v for k, v in e.items() if k != "severity_proof"}
    reg2 = rr.FindingRegistry()
    reg2.entries["C9100"] = e2
    a4_honest = reg2.unverified_critical_count()
    print(f"A4 with the gamed proof: {a4_gamed} | without any proof: {a4_honest}")
    if a4_gamed == 0 and a4_honest == 1:
        print("-> GAMEABLE at both levels; the release is bought by arithmetic "
              "about a quantity the gate never compares with the float it "
              "releases. Repair direction needs the founder's ruling on WHAT "
              "severity must be computed FROM.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
