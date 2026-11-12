"""A confidence derived from tool output is admissible for severity. B87.

HIS RULING, 2026-11-08: narrow the directive's refusal to permit a confidence
that is itself a function of tool output.

THE GAP, PRECISELY. `docs/MATHEMATICAL_APPENDIX.md` section 7.7 defines
``Sev(f) = W(class) . confidence . V(verification)``. The operational directive's
``d_tool`` gate already governs a tool-derived quantity and already gives the
worked examples -- "I am certain" inadmissible, "9 of 10 relevant tests caught
the flaw class" admissible -- but it names only the detection probability ``d``
entering ``q = eta . d . p``. The severity formula's own ``confidence`` factor
was named by NO gate, so it had no lawful source, and it was recorded on 0 of
3,311 archived findings, Wilson 95% [0.000000, 0.001159]. The clause added on
2026-11-08 binds it to the same rule.

THIS FILE EXECUTES THE CONCATENATION RATHER THAN READING ONE FILE. The clause
lives in ``cdsfl_operational.md``, but that file is not what a seat receives:
``bench/reference_runner_v3.py`` builds the seat text as
``cdsfl_core_formal.md`` PLUS ``cdsfl_operational.md``, and a separate loader,
``composer._load_universal_directive``, returns ONLY ``cdsfl_core_formal.md``.
Checking the wrong one of those 2 is how a clause can be believed to reach
seats when it does not -- it was checked against the composer first while
writing this, the clause was absent, and the alarm was a lookup against the
wrong assembler rather than a real gap. So the assembly is reproduced here.

THE DIRECTION THAT MATTERS IS THE SECOND ONE. A narrowing that permits
tool-derived confidence must NOT also delete the refusal of self-assessed
confidence, because that would turn a gate into a rubber stamp. Both refusals
are asserted present.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
UNIVERSAL = REPO / "bench/directives/universal"
CORE = UNIVERSAL / "cdsfl_core_formal.md"
OPERATIONAL = UNIVERSAL / "cdsfl_operational.md"

#: The clause added on his ruling.
CLAUSE = "confidence in Sev(f)"
#: The 2 refusals that must SURVIVE the narrowing.
REFUSALS = (
    "not from self-assessed confidence",
    "Self-reported confidence is not accepted.",
)


def seat_text() -> str:
    """What a seat actually receives, assembled as reference_runner_v3 does it.

    bench/reference_runner_v3.py:22523-22533 reads the core formal directive and
    then appends the operational one. Reproduced rather than imported because
    importing the runner executes a 20,000-line module for 2 file reads.
    """
    text = CORE.read_text(encoding="utf-8")
    if OPERATIONAL.exists():
        text += "\n\n" + OPERATIONAL.read_text(encoding="utf-8")
    return text


def test_the_runner_still_assembles_both_files():
    """If this concatenation goes, the clause stops reaching seats silently.

    ★ CONVERTED FROM A SOURCE LITERAL TO A PARSED TREE, 2026-11-12, entry B158.
    This matched one exact line of `reference_runner_v3`, including its
    `encoding="utf-8"` keyword. That is the fragile shape this guard's own
    census exists to count: 4 guards of this class broke on CORRECT changes in a
    single day, and reformatting the keyword, splitting the line, or renaming
    the local would all have turned it red while the behaviour was intact.

    ★ WHAT IT GUARDS IS A REPRODUCTION, WHICH IS WHY IT CANNOT SIMPLY EXECUTE.
    `seat_text()` above REPRODUCES the runner's assembly rather than importing
    it, for the reason its own docstring gives: importing the runner executes a
    20,000-line module for 2 file reads. So this test's job is to detect the
    reproduction DRIFTING from the original, and the question it must ask is
    structural -- does the runner still append the operational file to the seat
    text -- not whether one line is spelled a particular way.
    """
    import ast                                                 # noqa: PLC0415

    tree = ast.parse((REPO / "bench/reference_runner_v3.py").read_text(
        encoding="utf-8"))
    appends = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.AugAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "cdsfl_text"):
            continue
        reads = [c for c in ast.walk(node.value)
                 if isinstance(c, ast.Call)
                 and isinstance(c.func, ast.Attribute)
                 and c.func.attr == "read_text"]
        if reads:
            appends.append(node.lineno)
    assert appends, (
        "reference_runner_v3 no longer appends a file's contents to "
        "`cdsfl_text`, so the operational directive reaches no seat and every "
        "clause in it reaches nobody -- `seat_text()` in this file reproduces "
        "an assembly the runner no longer performs")


def test_the_clause_reaches_a_seat():
    """THE ADDITION IS WIRED. Asserted on the assembled text, not on 1 file."""
    assert CLAUSE in seat_text(), (
        f"{CLAUSE!r} is not in the text a seat receives, so the permission he "
        f"ruled on is an addition nothing reaches")


def test_the_clause_is_absent_from_the_core_file_alone():
    """ANTI-VACUITY for the test above.

    If the clause happened to be in BOTH files, the assembled-text assertion
    would pass without proving that the operational half is included. This
    pins which file carries it, so the concatenation is load-bearing.
    """
    assert CLAUSE not in CORE.read_text(encoding="utf-8"), (
        "the clause is in the core file too, so the test above no longer "
        "proves that the operational directive is assembled in")
    assert CLAUSE in OPERATIONAL.read_text(encoding="utf-8")


@pytest.mark.parametrize("refusal", REFUSALS)
def test_the_refusal_of_self_assessed_confidence_survives(refusal):
    """THE DIRECTION THAT MATTERS. A narrowing must not become a deletion."""
    assert refusal in seat_text(), (
        f"{refusal!r} is gone from the seat text. Permitting a tool-derived "
        f"confidence must not also permit a self-assessed one; without this "
        f"refusal the gate accepts 'I am certain' as a number.")


def test_the_clause_states_both_halves():
    """A permission that does not say what stays refused is read as a licence."""
    body = OPERATIONAL.read_text(encoding="utf-8")
    start = body.index(CLAUSE)
    window = body[start:start + 2000]
    assert "ADMISSIBLE" in window, "the clause does not say what is permitted"
    assert "INADMISSIBLE" in window, (
        "the clause does not say what stays refused, so a reader cannot tell "
        "that self-assessment is still excluded")
    assert "independent variable" in window, (
        "the clause does not warn that this file is an experimental "
        "independent variable, so a reader comparing runs across this date "
        "has no way to know the instructions changed")


def test_the_seat_text_is_not_empty():
    """ANTI-VACUITY. Every assertion above is a substring test, and they would
    all behave oddly on an empty string, so the frame is checked."""
    t = seat_text()
    assert len(t) > 50_000, f"the assembled seat text is only {len(t)} chars"
