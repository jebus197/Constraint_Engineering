# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2f517702ea9f8414a35970b92d0bbb1cf3832888fe3c2a89e2cb5cd6f3c4372e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The general falsifier pattern, ON THE LIVE REVIEW PATH, with its cannot-fail guard.

ANSWERS Q3 OF THE 2026-10-02 BRIEF: "design the general falsifier template, or
argue against one." The argument against designing one is that THIS PROJECT
ALREADY OWNS IT, and the measured defect is reach, not absence.

WHAT THE MEASUREMENT SAYS, and nothing here is new machinery:

  * `bench/tests/fixtures/stem/stem_fixtures.py` carries 5 prose STEM documents,
    29 ground-truth-tagged claims, and one `falsifier_template` each, already
    parametrised by the token `<<DOC_PATH>>`. Re-run by the project's own decider
    `falsifier_verify.reverify_falsifier`, all 5 CONFIRM on the pristine document
    and REFUTE on the corrected one: 5/5 BIDIRECTIONAL.
    (`scripts/falsify_prose_falsifier_supply_2026-09-30.py`, part 1.)
  * Live-path modules importing that corpus, before this file: 0. A working
    mechanism nothing reaches is, by the project's own additive standard, an
    addition that does nothing -- 11 of this project's confirmed defects since
    2026-08-01 are exactly that, and 0 were removals of something needed.
  * The supply gap is where the brief said it was, but the ERROR excess is in the
    LOGIC, not the PATH. Adjudicated 2026-10-02 over 567 post-feature criticals
    carrying a body: a body naming a RELATIVE file errors at 12/79 = 15.19%
    against 10/353 = 2.83% for a body naming none, Fisher OR 6.1433,
    p = 8.831828e-05. A body naming an ABSOLUTE path shows NO excess at all --
    6/132 = 4.55%, OR 0.8874, p = 1.000. So parametrising the target is the
    correct generalisation and hard-coding it is NOT the measured fault.
    (`scripts/supply_cause1_is_path_portability_2026-10-02.py`.)

SO THE TEMPLATE IS: take the target as a PARAMETER, assert on it, and prove the
assertion discriminates. Three lines of contract, no framework:

    1. resolve the target at run time (`<<DOC_PATH>>`, or the runner's
       `falsifier_verify.set_falsifier_target`), never as a literal path;
    2. import the REAL module under test rather than retyping it (core directive
       §"Runnable Falsifiers", condition 1);
    3. pass :func:`bidirectional`, below.

THE CANNOT-FAIL GUARD, WHICH IS THE WHOLE POINT. The brief names the hazard
exactly: "a general falsifier that cannot fail is worse than none", and this
project shipped that twice -- `check_sk_threshold` hardwired to `return True`
passed 321 tests, and A19's `e4_bandit` reported 0 HIGH forever at the heaviest
weight. A template makes that hazard WORSE, because one unfalsifiable pattern
copied into every finding is 321 silent passes instead of one.

The guard is not a style rule and not a review checklist. It is a SECOND
EXECUTION: a falsifier is admissible only if it CONFIRMS on the artefact as given
AND REFUTES on an artefact where the defect has been repaired. `return True`
confirms on both and is refused. That is cheap -- one extra subprocess -- it needs
no knowledge of the defect, and it cannot be satisfied by a falsifier that does
not actually read its target. It is also already proven: 5/5 on the committed
corpus.

Nothing here decides a verdict. `reverify_falsifier` remains the only decider --
tools decide, not votes, and not this module.
"""
from __future__ import annotations

import pathlib
import sys
from typing import Callable

# THE CORPUS, IMPORTED FROM THE LIVE PATH. This import is the fix that
# `falsify_prose_falsifier_supply_2026-09-30.py` part 2 asks for: it is what makes
# `grep -l stem_fixtures bench/cdsfl_registry/*.py` non-empty. Kept lazy, because
# the registry is imported by the runner on every run and the corpus is only
# needed when a falsifier is being supplied or checked -- and because a hard
# import failure here would take the whole policy engine down with it.
_FIXTURES_DIR = (pathlib.Path(__file__).resolve().parents[2]
                 / "bench" / "tests" / "fixtures" / "stem")

#: The token a general falsifier uses in place of a literal target path.
DOC_PATH_TOKEN = "<<DOC_PATH>>"

__all__ = ["DOC_PATH_TOKEN", "load_corpus", "general_templates",
           "bidirectional", "BidirectionalResult"]


def load_corpus():
    """The committed prose-falsifier corpus, or None if it is not installed.

    Returns the `stem_fixtures` module. None rather than raising, so a trimmed
    checkout degrades to "no supply available" instead of breaking the runner.
    """
    if str(_FIXTURES_DIR) not in sys.path:
        sys.path.insert(0, str(_FIXTURES_DIR))
    try:
        import stem_fixtures  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return None
    return stem_fixtures


def general_templates() -> dict[str, str]:
    """{fixture key: falsifier template}, each still carrying DOC_PATH_TOKEN.

    These are the patterns a seat should be shown. Every one is unbound to any
    path, so repointing it at another document is a string substitution.
    """
    sf = load_corpus()
    if sf is None:
        return {}
    return {f.key: f.falsifier_template for f in sf.FIXTURES}


class BidirectionalResult:
    """Why a falsifier was admitted or refused. Carries both verdicts."""

    __slots__ = ("admissible", "on_artefact", "on_repaired", "reason")

    def __init__(self, admissible: bool, on_artefact: str,
                 on_repaired: str, reason: str) -> None:
        self.admissible = admissible
        self.on_artefact = on_artefact
        self.on_repaired = on_repaired
        self.reason = reason

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return (f"BidirectionalResult(admissible={self.admissible!r}, "
                f"on_artefact={self.on_artefact!r}, "
                f"on_repaired={self.on_repaired!r}, reason={self.reason!r})")


def bidirectional(render: Callable[[pathlib.Path | None], str],
                  repaired: pathlib.Path,
                  decide: Callable[[str], str]) -> BidirectionalResult:
    """THE CANNOT-FAIL GUARD. Admit a falsifier only if it DISCRIMINATES.

    ``render``   (target_path | None) -> falsifier source. None means "the
                 artefact as given"; a path means "this repaired copy".
    ``repaired`` a copy of the artefact with the defect fixed.
    ``decide``   the project's real decider, `reverify_falsifier`. Passed in
                 rather than imported, so this module never becomes a second
                 decider -- tools decide, and there is exactly one tool.

    Admissible iff CONFIRMED on the artefact AND REFUTED on the repair. Every
    other combination is refused, and the reason names which:

      CONFIRMED / CONFIRMED  cannot fail -- the `return True` family. The single
                             failure mode this guard exists for.
      CONFIRMED / anything else but REFUTED  did not demonstrably clear once
                             repaired, so it is not evidence about the defect.
      not CONFIRMED / *      did not demonstrate the defect at all.
    """
    v_art = decide(render(None))
    v_rep = decide(render(repaired))
    if v_art == "CONFIRMED" and v_rep == "REFUTED":
        return BidirectionalResult(True, v_art, v_rep, "discriminates")
    if v_art == "CONFIRMED" and v_rep == "CONFIRMED":
        return BidirectionalResult(
            False, v_art, v_rep,
            "CANNOT FAIL: confirms on the repaired artefact too, so it is not "
            "reading the defect. This is the check_sk_threshold `return True` "
            "family, which passed 321 tests.")
    if v_art == "CONFIRMED":
        return BidirectionalResult(
            False, v_art, v_rep,
            f"did not REFUTE once repaired (got {v_rep}); not evidence about "
            "this defect")
    return BidirectionalResult(
        False, v_art, v_rep, f"did not demonstrate the defect (got {v_art})")
