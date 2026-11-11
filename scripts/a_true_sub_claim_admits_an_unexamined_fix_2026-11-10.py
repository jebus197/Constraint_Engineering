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

★ CONVERTED TO THE GUARD FOR ITS OWN CLOSURE, 2026-11-11, which is what this
docstring's last line asked for. The founder ruled on the admissible basis:
*"Keep both the claim prose, and the proposed fix."* `domain_verification_set`
now runs the topic's tools over BOTH and requires both, and `_FindingView`
exposes `proposed_fix` -- whose absence was the actual bug, since the view's
own docstring had claimed to carry the fix while reading only the description.

THE PRODUCER IS KEPT RATHER THAN DELETED because it is the only executable
record of what the hole WAS, and `additive-standard` permits removal only
where a committed measurement shows a replacement dominates. Its polarity is
inverted instead: it now exits 0 when the hole is CLOSED and 1 if it REOPENS.

Exit 0 iff the exploit is REFUSED (the true-irrelevant pair no longer admits,
and the false twin still does not). Exit 1 means the hole has REOPENED.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import domain_immune as di  # noqa: E402


class _FV:
    #: ★ THE PROBE NOW SEPARATES THE 2 TEXTS, because the repair does. The
    #: seat's original concatenated the bad-fix prose onto the DESCRIPTION,
    #: which was the only shape available when `_FindingView` exposed no
    #: `proposed_fix` at all. Keeping the concatenated form would test a shape
    #: the live adapter no longer produces, and would pass for the wrong reason.
    def __init__(self, d: str, fix: str = "") -> None:
        self.description = d
        self.proposed_fix = fix


BAD_FIX = "delete the retry loop"


def main(argv=None) -> int:
    #: ★ ADDED ON ADOPTION, 2026-11-10. This producer was DELIVERED BY THE
    #: `fable` SEAT in the free round and had no argument parsing, so `--help`
    #: ran the whole measurement -- which this project's own guard
    #: `bench/tests/test_help_is_answered_2026-09-11.py` refuses, on his
    #: standing rule that a `--help` must never cost minutes. The seat's work
    #: is kept in full; only the flag is answered. It was the commit gate that
    #: caught this, which is the gate earning its place on a file I adopted
    #: from somewhere else without checking it against the local rules.
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0]).parse_args(argv)

    true_irrelevant = di.domain_verification_set(
        "chemistry", _FV("the molecule 'CCO' has formula C2H6O", BAD_FIX))
    false_twin = di.domain_verification_set(
        "chemistry", _FV("the molecule 'CCO' has formula C3H8O", BAD_FIX))
    #: ★ THE CAPABILITY PROBE, added with the closure. A guard that only shows
    #: the hole shut cannot tell a repair from a mechanism switched off, and
    #: `additive-standard` forbids buying a refusal with a lost capability.
    both_verify = di.domain_verification_set(
        "chemistry", _FV("the molecule 'CCO' has formula C2H6O",
                         "correct it to: the molecule 'CCO' has formula C2H6O"))
    print("true formula, unexamined fix :",
          true_irrelevant["admits"], "|", true_irrelevant["detail"])
    print("false formula, same fix      :",
          false_twin["admits"], "|", false_twin["detail"])
    print("true formula, VERIFIABLE fix :",
          both_verify["admits"], "|", both_verify["detail"])
    exploit_live = bool(true_irrelevant["admits"])
    capability_kept = bool(both_verify["admits"])
    print()
    if exploit_live:
        print("EXPLOIT REOPENED: a true sub-claim again admits a fix the "
              "tools never examined.")
        return 1
    if not capability_kept:
        print("HOLE CLOSED BUT THE CAPABILITY WENT WITH IT: a fix the tools "
              "DO verify is now refused too, so the route is inert. That is "
              "additive-standard's removal clause broken by the repair.")
        return 1
    print("CLOSED, AND THE CAPABILITY IS INTACT: the unexamined fix is "
          "refused, the false twin is refused, and a fix the tools verify "
          "still admits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
