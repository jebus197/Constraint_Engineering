"""A declared figure printed only inside its own retraction must not be accepted.

ENTRY B174, found 2026-11-13. `check_declared_figures` re-executes a brief's
declared figures and accepted one when its token appeared anywhere in the
producer's output. A producer that WITHDRAWS a figure necessarily QUOTES it --
that is what makes the retraction legible -- so a withdrawn number kept passing
validation, and a brief could cite a figure the project had formally refuted and
validate clean.

MEASURED WHEN IT WAS FOUND: a brief declaring 3 retracted figures was accepted on
all 3. After the repair all 3 are reported, and with their own message.

WHY A SEPARATE MESSAGE AND NOT `does not print it`. The 2 send a reader to
OPPOSITE actions: `does not print it` says restore the figure to the producer,
while a retraction says re-issue the brief and leave the producer alone.
Collapsing them would be a worse defect than the one being fixed.

HOW IT WAS FOUND, kept because it is the instructive part: a hand-written audit
of this exact question made the IDENTICAL error first, reporting both retracted
figures as reproducing, and the defect became visible only because that verdict
contradicted what the producer plainly said on the line above.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent


def _pbv():
    sys.path.insert(0, str(REPO / "scripts"))
    import panel_brief_validate as m
    return m


@pytest.fixture(scope="module")
def pbv():
    return _pbv()


def _producer(tmp_path, body: str) -> pathlib.Path:
    d = tmp_path / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "p.py"
    p.write_text("print(r'''" + body + "''')\n")
    return p


def _brief(value: str) -> str:
    return ("x" * 450 + "\n\n<!-- figure: lbl | scripts/p.py | " + value + " -->\n")


def test_a_figure_printed_only_on_a_refuted_line_is_reported(pbv, tmp_path):
    """The case the entry was raised for."""
    _producer(tmp_path, "THE FIGURE STOOD HERE IS REFUTED: `gamma = 0.4137`\nall done")
    probs = pbv.check_declared_figures(_brief("gamma = 0.4137"),
                                       repo=tmp_path, timeout=60)
    assert probs, (
        "a figure printed only inside its own retraction was ACCEPTED. A "
        "withdrawn number can then keep passing validation forever.")
    assert any("REFUTED by its own producer" in p for p in probs), (
        f"reported, but not as a retraction: {probs}")


@pytest.mark.parametrize("marker", ["REFUTED", "WITHDRAWN", "SUPERSEDED"])
def test_every_retraction_marker_is_recognised(pbv, tmp_path, marker):
    _producer(tmp_path, f"{marker}: `rate = 0.2941` -> see below\nother output")
    probs = pbv.check_declared_figures(_brief("rate = 0.2941"),
                                       repo=tmp_path, timeout=60)
    assert any(f"{marker} by its own producer" in p for p in probs), (
        f"marker {marker!r} not recognised as a retraction: {probs}")


def test_the_retraction_message_differs_from_the_absent_message(pbv, tmp_path):
    """They send a reader to opposite actions, so they must not read alike."""
    _producer(tmp_path, "REFUTED: `gamma = 0.4137` was withdrawn\ndone")
    retracted = pbv.check_declared_figures(_brief("gamma = 0.4137"),
                                           repo=tmp_path, timeout=60)
    _producer(tmp_path, "nothing relevant here at all\ndone")
    absent = pbv.check_declared_figures(_brief("gamma = 0.4137"),
                                        repo=tmp_path, timeout=60)
    assert retracted and absent, "both cases must be reported"
    assert retracted != absent, (
        "a retracted figure and an absent one produce the SAME message, so a "
        "reader is told to restore a figure that was deliberately withdrawn")
    assert "do NOT restore" in " ".join(retracted), (
        "the retraction message must tell the reader not to restore the figure")


def test_a_figure_that_genuinely_prints_is_still_accepted(pbv, tmp_path):
    """The boundary. A check that accuses correct output stops being run."""
    _producer(tmp_path, "gamma = 0.4137\nand some REFUTED prose about something else")
    assert pbv.check_declared_figures(_brief("gamma = 0.4137"),
                                      repo=tmp_path, timeout=60) == [], (
        "a figure that genuinely prints was refused because the output "
        "contained a retraction marker ELSEWHERE. That is the false positive "
        "that gets a guard switched off.")


def test_the_stated_limit_holds_and_is_documented(pbv, tmp_path):
    """The check fires only when the figure appears EXCLUSIVELY on marked lines.

    This is a deliberate conservatism, not an oversight, and the test pins it so
    that nobody later 'fixes' it into a false-positive generator.
    """
    _producer(tmp_path, "REFUTED: `gamma = 0.4137`\nit read `gamma = 0.4137` before")
    assert pbv.check_declared_figures(_brief("gamma = 0.4137"),
                                      repo=tmp_path, timeout=60) == [], (
        "the check fired although the figure also appears on an UNMARKED line. "
        "Treating a passing mention as a retraction would accuse producers that "
        "still print the figure.")
    src = (REPO / "scripts" / "panel_brief_validate.py").read_text()
    assert "THE STATED LIMIT" in src, (
        "the conservatism above is undocumented, which is how a reader comes to "
        "trust a check further than it goes")
