# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4b7f9576eb0bb173bbeabfea031e63987b2d845f5006f2912fc2ac86fe66b66f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A CORRECT computable sub-claim in a finding's DESCRIPTION admits a fix the
tools never examined.

FREE PANEL, 2026-11-10, the falsification the dispatch brief asked for by
name: PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE reappearing on the domain side.

THE MECHANISM, confirmed by execution. `bench/reference_runner_v3.py`'s
apply-back gate for a non-Python target calls
`domain_immune.domain_verification_set(domain, _FindingView(finding))` and
returns `True` -- the fix is ADMITTED -- when `admits` is set.
`domain_verification_set` evaluates `finding.description`, and `_FindingView`
exposes description-first prose. So the text the tools reduce is the CLAIM
prose, while the artefact admitted is the PROPOSED FIX, and nothing requires
the two to be about the same thing.

MEASURED, this script: a description carrying 1 true formula claim and a fix
the tools cannot see ("delete the retry loop") sets `admits=True` through
`chemistry_structure`'s COMPARING molecular-formula branch -- the branch the
branch gate correctly RETAINS, because it discriminates on the sub-claim.
Discrimination of the sub-claim is not relevance of the sub-claim to the fix.
The false twin is REJECTED, so the gate's own 5-of-5 / 7-of-7 scoring is not
contradicted; the hole is orthogonal to truth-blindness.

WHY NO REPAIR IS SHIPPED WITH THIS. The candidate repairs each change whose
text is the admissible basis (description, fix prose, or both), and that
scoping is governed by his B88 ruling of 2026-11-10 on what the topic's tools
are for. Choosing it is his; demonstrating the hole is ours.

Exit 0 iff the exploit is demonstrated (true-irrelevant admits, false twin
refused). Exit 1 means the hole has since been closed -- then DELETE this
producer or convert it to the guard for the closure.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import domain_immune as di  # noqa: E402


class _FV:
    def __init__(self, d: str) -> None:
        self.description = d


BAD_FIX_TAIL = ", therefore the retry loop should be deleted"


def main() -> int:
    true_irrelevant = di.domain_verification_set(
        "chemistry", _FV("the molecule 'CCO' has formula C2H6O" + BAD_FIX_TAIL))
    false_twin = di.domain_verification_set(
        "chemistry", _FV("the molecule 'CCO' has formula C3H8O" + BAD_FIX_TAIL))
    print("true formula, unexamined fix :",
          true_irrelevant["admits"], "|", true_irrelevant["detail"])
    print("false formula, same fix      :",
          false_twin["admits"], "|", false_twin["detail"])
    exploit_live = bool(true_irrelevant["admits"]) and not false_twin["admits"]
    print("\nEXPLOIT", "DEMONSTRATED: a true sub-claim admits a fix the tools "
          "never examined." if exploit_live else
          "NOT demonstrated -- the hole appears closed; retire or convert "
          "this producer.")
    return 0 if exploit_live else 1


if __name__ == "__main__":
    raise SystemExit(main())
