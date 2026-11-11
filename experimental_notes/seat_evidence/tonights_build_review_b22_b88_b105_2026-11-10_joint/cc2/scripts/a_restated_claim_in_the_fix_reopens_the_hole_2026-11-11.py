# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 91a3c685baf04b2e4ee9b8b782ccb636d83680ad251765d5710855873a821f68
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The fold-back domain route still admits a fix the tools have not examined.

WHAT THE 2026-11-11 REPAIR DID. `bench/domain_immune.py:599-671` runs the
domain's assigned tools TWICE -- once over `finding.description` and once over
`finding.proposed_fix` -- and requires both sides to carry a discriminating
favourable verdict (`out["admits"]` at line 670). The committed exploit
`scripts/a_true_sub_claim_admits_an_unexamined_fix_2026-11-10.py` no longer
reproduces against it.

WHY THAT IS NOT A CLOSURE. The verifiers are EXTRACTORS: each one scans the
text for a token it can parse, evaluates that token, and ignores every other
character. `bench/immune_agents.py:2518 _verify_chemistry_structure` returns
    'rdkit: CHEM_VALID: SMILES=CCO formula=C2H6O matches claim'
BYTE-IDENTICALLY for

    "the molecule 'CCO' has formula C2H6O"

and for that same sentence with an arbitrary instruction appended. So
`_walk(text)` answers "does this text CONTAIN a true computable statement?",
never "is this text true?". For a claim those are close enough -- the claim IS
the statement. For a proposed fix they are not: the fix's operative content is
an instruction, and the tool's verdict is about an incidental substring.

THE GENERAL RESULT, derived rather than asserted. Let F be any proposed fix
text and T any tool the domain assigns that has a comparing branch. Let s be
any statement T confirms. Then F' = s + ", therefore " + F proposes exactly
what F proposes, and `_walk(F')` contains T's favourable verdict. Hence

    for every F there is a semantically equivalent F' with fix_computing != 0

so the conjunct `bool(fix_computing)` imposes NO restriction on what may be
proposed. A gate satisfiable by prepending a constant to any input is not a
gate. The corollary is that NO conjunct of the form "some tool confirmed
something in text X" can gate X while the verifiers extract-and-ignore.

TWO CARRIER SHAPES ARE PROBED, both of which the 2026-11-11 repair admits:
  CARRIER-1  the fix restates the claim verbatim and appends the instruction
  CARRIER-2  the fix carries a DIFFERENT true fact and appends the instruction
CARRIER-2 matters because it survives any test that compares the fix against
the claim.

FALSIFIER CONTRACT. Imports the real `bench/domain_immune.py`; nothing is
retyped. Raises AssertionError / prints FALSIFIED when either carrier is
ADMITTED. Exits 0 silently when both are refused. Reads nothing but the
repository's own modules.

Run:  python3 scripts/a_restated_claim_in_the_fix_reopens_the_hole_2026-11-11.py
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import domain_immune as di                                   # noqa: E402


class _FindingView:
    """The two attributes `domain_verification_set` reads. Nothing else."""

    def __init__(self, description: str, proposed_fix: str = "") -> None:
        self.description = description
        self.proposed_fix = proposed_fix


#: A statement the chemistry verifier CONFIRMS on its comparing branch, so it
#: clears `BRANCH_GATED_ADMISSION["chemistry_structure"] == "matches claim"`
#: at `bench/domain_immune.py:475-478`.
TRUE_CLAIM = "the molecule 'CCO' has formula C2H6O"
#: A DIFFERENT true statement the same branch confirms.
OTHER_TRUE = "the molecule 'CCC' has formula C3H8"
#: The artefact no tool in the chemistry verification set can evaluate.
UNEXAMINED = "delete the retry loop in reference_runner_v3.py"

CASES = [
    ("CARRIER-1 fix restates the claim, then appends the instruction",
     TRUE_CLAIM, f"{TRUE_CLAIM}, therefore {UNEXAMINED}"),
    ("CARRIER-2 fix carries a DIFFERENT true fact, then the instruction",
     TRUE_CLAIM, f"{OTHER_TRUE}, so {UNEXAMINED}"),
]

#: Controls. These must behave as the repair's own verification set says, or
#: this probe is measuring something other than the live route.
CONTROLS = [
    ("control: bare instruction as the fix must REFUSE",
     TRUE_CLAIM, UNEXAMINED, False),
    ("control: absent fix must REFUSE (fail closed)",
     TRUE_CLAIM, "", False),
    ("control: a false claim must REFUSE on both texts",
     "the molecule 'CCO' has formula C3H8O",
     "the molecule 'CCO' has formula C3H8O", False),
]


def main() -> int:
    bad = []

    print("CONTROLS -- the repair's own stated behaviour")
    for label, claim, fix, want in CONTROLS:
        got = di.domain_verification_set("chemistry",
                                         _FindingView(claim, fix))["admits"]
        flag = "ok " if got is want else "DRIFT"
        print(f"  [{flag}] admits={got!s:5s} want={want!s:5s}  {label}")
        if got is not want:
            bad.append(f"control drifted: {label}")
    if bad:
        for line in bad:
            print("DRIFT:", line)
        print("the route does not behave as its verification set records; "
              "this probe would be measuring a different artefact")
        return 2

    print("\nCARRIERS -- a fix the tools have NOT examined")
    admitted = []
    for label, claim, fix in CASES:
        r = di.domain_verification_set("chemistry", _FindingView(claim, fix))
        print(f"  admits={r['admits']!s:5s}  {label}")
        print(f"      fix text  : {fix!r}")
        print(f"      detail    : {r['detail']}")
        if r["admits"]:
            admitted.append(label)

    #: The evidence identity is the mechanism, printed so the reader can see
    #: that the tool returned the SAME string for the clean claim and for the
    #: carrier -- i.e. it never looked at the instruction.
    import immune_agents as _ia                              # noqa: PLC0415
    e_clean = _ia._verify_chemistry_structure(TRUE_CLAIM).evidence
    e_carry = _ia._verify_chemistry_structure(CASES[0][2]).evidence
    print(f"\n  evidence(clean claim) : {e_clean!r}")
    print(f"  evidence(carrier fix) : {e_carry!r}")
    print(f"  byte-identical        : {e_clean == e_carry}")

    if admitted:
        print("\nFALSIFIED")
        print(f"{len(admitted)} of {len(CASES)} carrier shapes were ADMITTED "
              f"by the fold-back domain route:")
        for label in admitted:
            print(f"  - {label}")
        raise AssertionError(
            "domain_verification_set admitted a proposed fix whose operative "
            "content no tool evaluated")

    print("\nCLEAN -- both carrier shapes refused")
    return 0


if __name__ == "__main__":
    sys.exit(main())
