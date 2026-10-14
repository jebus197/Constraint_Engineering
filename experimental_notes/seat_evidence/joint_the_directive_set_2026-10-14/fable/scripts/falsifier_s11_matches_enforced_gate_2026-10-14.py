# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 25a148a4f96d59dcbcbbcf5c9d3b235a3744bf0688b737692bb008ae454099cb
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER (J6, 2026-10-14 joint panel): does the proposed directive section
'Worked Proofs' state the requirement the runner ACTUALLY enforces?

The enforced gate (bench/dm/_rk_proof.py + bench/reference_runner_v3.py,
'SEVERITY MUST BE A CALCULATION, NOT A VOTE'):
  - scope: per-FINDING severity, via a CORROBORATION block;
  - parameter list: taken here from the EXECUTED output of
    build_proof_requests (imports the real target; never retyped);
  - direction: one-directional -- an unproven severity still BLOCKS and cannot
    be used to demote, clear or close (looser-direction wording is a defect:
    it would let a model clear the convergence gate by omitting arithmetic).

RED  on the unpatched tree: no corrected proposal exists, so this evaluates the
     v1 draft reconstructed from the round's seat_proposals.diff -> FALSIFIED.
GREEN after: experimental_notes/S11_Worked_Proofs_Corrected_2026-10-14.md
     exists and passes every check -> clean exit.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bench"))
from dm._rk_proof import build_proof_requests  # REAL target, not a copy

CORRECTED = "experimental_notes/S11_Worked_Proofs_Corrected_2026-10-14.md"
DIFF = "bench/logs/the_directive_set_and_capability_2026-10-14/seat_proposals.diff"
LOOSER = "does not count toward any convergence-relevant series"


def canonical_params() -> list:
    """Execute the real gate and parse the parameter list from its OUTPUT."""
    out = build_proof_requests([("C9999", "ABSENT", None, None)])
    m = re.search(r"^\s*(R_old,.*R_k)\s*$", out, re.M)
    assert m, "parameter line not found in build_proof_requests output"
    return [t.strip() for t in m.group(1).replace("= eta*d*p", "").split(",") if t.strip()]


def v1_from_diff() -> str:
    lines, on = [], False
    for ln in open(DIFF, encoding="utf-8"):
        if ln.startswith("+## 11. Worked Proofs"):
            on = True
        elif on and (ln.startswith("+## ") or ln.startswith("### ")):
            break
        if on and ln.startswith("+"):
            lines.append(ln[1:])
    return "".join(lines)


def check(text: str) -> list:
    fails = []
    missing = [p for p in canonical_params() if p not in text]
    if missing:
        fails.append(f"A: parameter list incomplete, missing {missing}")
    low = text.lower()
    if not (("block" in low) and ("demote" in low) and ("cannot" in low)):
        fails.append("B: one-directional blocking property not stated")
    if LOOSER in re.sub(r"\s+", " ", text):
        fails.append("C: states the LOOSER direction (unproven claim 'does not count') "
                     "-- the exact loophole the runner comment names")
    if "CORROBORATION" not in text:
        fails.append("D: does not name the CORROBORATION block the runner checks")
    return fails


def main() -> int:
    if os.path.exists(CORRECTED):
        text, which = open(CORRECTED, encoding="utf-8").read(), CORRECTED
    else:
        text, which = v1_from_diff(), f"v1 draft (from {DIFF})"
    fails = check(text)
    print(f"candidate: {which}")
    for f in fails:
        print("  FAIL", f)
    if fails:
        print("FALSIFIED")
        return 1
    print("  all checks pass: section states the enforced gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
