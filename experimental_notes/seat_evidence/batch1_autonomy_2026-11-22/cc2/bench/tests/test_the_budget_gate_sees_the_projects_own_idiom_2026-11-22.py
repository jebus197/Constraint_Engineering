# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3c1095ea7edca4b7f74122ec0adb78cc8fa23010195214ccbad48d409583cff8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The heavy-work detector must see the sentences this project actually writes.

ENTRY B182, PANEL FINDING 2026-11-22. The B182 repair closed its 150-cell grid
to 0 blind. The grid is not the vocabulary: its 10 nouns were chosen by the
same hand that wrote the pattern, so the measurement could only report that the
listed phrasings are caught.

Counted over this repository's own .md/.py/.txt at the time of the finding:
bare "the board" 1816, "bench/tests" with no trailing slash 1048, "the guards"
525, unhyphenated "rerun" 398. All passed through. Two of them are sentences
the project writes AT ITSELF -- the hook's own refusal text says "run the board
ONCE yourself", and the 2026-11-21 panel brief says "Run the guards."

THE NEGATION ARM IS PINNED TOO. Widening an accepting predicate is exactly how
a gate starts refusing the briefs that FORBID the tooling, which is the failure
B182 was raised for in the first place.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "local_resource_budget.py"


@pytest.fixture(scope="module")
def instructs():
    spec = importlib.util.spec_from_file_location("lrb_vocab", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lrb_vocab"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m._instructs_heavy_verification


#: Each is a genuine instruction to run the project's heavy verification.
@pytest.mark.parametrize("text", [
    "run the board ONCE yourself, save the result",   # the hook's OWN remedy
    "Run the guards.",                                # the panel brief's own words
    "run the guards and report the result",
    "run the board's own 317 guards",
    "run the board",
    "run the whole board",
    "run the entire board",
    "rerun the full test suite",
    "rerunning the suite and tell me what fails",
    "run bench/tests and tell me what fails",
])
def test_a_real_instruction_is_refused(instructs, text):
    assert instructs(text.lower()), (
        f"{text!r} passed through the gate that exists to refuse it; this is a "
        "phrasing counted in the project's own corpus, not an invented one")


#: THE HALF THAT MUST NOT MOVE. A brief forbidding the tooling has to be
#: writable without tripping the guard that forbids it.
@pytest.mark.parametrize("text", [
    "do not run the full test suite",
    "do not run the board",
    "never rerun the suite",
    "you must not run the guards",
    "without running bench/tests",
    "rather than running the board, consult the cached result",
])
def test_a_prohibition_still_passes_through(instructs, text):
    assert not instructs(text.lower()), (
        f"{text!r} was refused; widening the noun and verb sides must not turn "
        "prohibitions into refusals -- that is the 2026-10-17 failure")


def test_ambiguity_is_still_allowed(instructs):
    """A bare noun with no verb and no negation stays AMBIGUOUS. Refusing on
    ambiguity produced both false positives of 2026-10-17."""
    assert not instructs("the board reported 18 failed and 5,131 passed")
