# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5632c50b289800c235650204a4648092b68397ab9531f375aa2444c8d7fbc1c7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The GENERAL falsifier template: repointable, delegating, and unable to lie still.

THE FOUNDER'S QUESTION, 2026-10-02: falsifiers are sometimes too specific --
"our primary falsifiers after all are tools, and these tools are already
general?" Measured the same day (scripts/falsifier_supply_decomposition):
86.37% of 499 distinct archived falsifier bodies hand-roll their assertions,
13.63% delegate to a general instrument, and 31.46% hard-code a concrete
file path, which is the stratum that ERRORS at OR 4.31 (Fisher p = 2.43e-04,
scripts/repro_supply_causes_2026-10-02.py). This module is the supply-side
answer: ONE falsifier shape that is general over targets because the target
is a PARAMETER, general over instruments because the check is a delegated
callable, and -- the part that earns its existence -- STRUCTURALLY unable to
pass vacuously.

THE NAMED HAZARD, AND WHY THE GUARD IS NOT OPTIONAL. A general falsifier
that cannot fail is worse than none, and this project has shipped that
twice: `check_sk_threshold` hardwired to `return True` passed 321 tests, and
A19's `e4_bandit` returned no metrics on prose and reported 0 HIGH forever
at the heaviest weight. Both share one shape: the instrument's answer did
not depend on its input. So the template requires a CONTROL TRANSFORM -- a
version of the target with the claimed defect corrected or neutralised --
and refuses to return any verdict when the predicate answers the SAME on
pristine and control. That is the stem-fixtures bidirectional contract
(CONFIRMED on the planted claim, REFUTED once corrected) promoted from the
test corpus to the live supply, which is exactly the wiring gap
scripts/falsify_prose_falsifier_supply_2026-09-30.py measures.

This works on PROSE as well as code: the predicate parses the document and
re-derives the claim (regex + sympy/mpmath), the control transform applies
the correction, and the decider stays `tools decide` -- the verdict is the
executed comparison, never an assertion.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

__all__ = ["FalsifierCannotFail", "run_general_falsifier"]

CONFIRMED = "CONFIRMED"
REFUTED = "REFUTED"


class FalsifierCannotFail(AssertionError):
    """The predicate's answer did not depend on its input.

    Raised -- never returned -- so a vacuous instrument can only ever
    surface as an ERROR in the routing ladder, where ERROR already has a
    remedy (next rung, then HIL). It must not surface as REFUTED, which
    would silently clear a finding, nor as CONFIRMED, which would silently
    sustain one. The check_sk_threshold and e4_bandit incidents are both
    this exception, thrown at authoring time instead of discovered months
    later at the heaviest weight.
    """


def run_general_falsifier(
    target: str | Path,
    defect_predicate: Callable[[str], bool],
    control_transform: Callable[[str], str],
) -> str:
    """Decide a claimed defect bidirectionally. Returns CONFIRMED or REFUTED.

    ``target``            -- the artefact under review. A PARAMETER, so the
                             same falsifier repoints to a sibling, a staged
                             copy, or next week's revision without edits;
                             bodies that hard-code this are the 31.46%
                             stratum that cannot be repointed.
    ``defect_predicate``  -- text -> True iff the claimed defect is present.
                             Delegate to a general instrument here (ast,
                             sympy, ruff via subprocess, a re-derivation);
                             the judgement must be the tool's.
    ``control_transform`` -- text -> the same artefact with the claimed
                             defect corrected or neutralised. This is the
                             falsifier's own falsifier: it is what makes a
                             vacuous predicate DETECTABLE.

    Raises FalsifierCannotFail when predicate(pristine) == predicate(control)
    -- including the e4_bandit shape where the instrument silently measures
    nothing and answers alike everywhere. Raises on a missing target rather
    than guessing: an unreadable artefact is ERROR, not REFUTED.
    """
    pristine = Path(target).read_text(encoding="utf-8")
    control = control_transform(pristine)
    if control == pristine:
        raise FalsifierCannotFail(
            "the control transform returned the artefact unchanged, so the "
            "comparison below could only ever agree: there is no control")
    on_pristine = bool(defect_predicate(pristine))
    on_control = bool(defect_predicate(control))
    if on_pristine == on_control:
        raise FalsifierCannotFail(
            f"the predicate answered {on_pristine} on BOTH the artefact and "
            f"its corrected control. An instrument whose answer does not "
            f"depend on its input measures nothing (the check_sk_threshold / "
            f"e4_bandit shape); no verdict is returned")
    return CONFIRMED if on_pristine else REFUTED
