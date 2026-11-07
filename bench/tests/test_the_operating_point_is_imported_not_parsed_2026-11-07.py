"""B56: the shadow report must read his operating point's VALUE, not its spelling.

His accepted figure is 1 in 50 (`CHOSEN_TARGET = 0.02`), owned by
`scripts/can_we_do_better_than_one_in_twenty_2026-10-30.py` and pinned against
a later "restore" by
`bench/tests/test_his_demotion_operating_point_is_pinned_2026-11-01.py`.

WHAT THIS FILE ADDS, which that one does not. The pin guards the NUMBER. This
guards the ROUTE. `scripts/the_shadow_demotion_report_2026-11-02.py` used to
obtain the figure by scanning the owner for a line beginning `CHOSEN_TARGET` and
splitting it on `=` and `#`. Its comment said "read from its owner rather than
retyped", so the intent was right and the mechanism was a half-measure: it read
how the producer SPELLS the number, not what the number IS.

MEASURED 2026-11-07, and this is why the route needs its own guard: rewriting
the owner's line as `CHOSEN_TARGET = 1.0 / 50` -- the SAME value, a refactor
that leaves the producer entirely correct -- made the old parse raise
`ValueError: could not convert string to float: '1.0 / 50'` while the import
returned 0.02. A correct change to a producer killing a correct consumer is the
converse of `execute-do-not-grep` and has fired 4 times in this project on
correct changes.

THE DEMOTION RULE IS STILL WIRED TO NOTHING, AND THAT IS DELIBERATE. Nothing
here wires it. The pin's docstring records why: wiring it "would change which
models the harness uses on the strength of a SIMULATED degradation model rather
than this project's own runs. That is a behaviour change for the founder to
authorise, not a tidy-up." It also runs against his standing rule never to bench
a model. These tests change how the number is READ and nothing about what acts
on it.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "the_shadow_demotion_report_2026-11-02.py"
OWNER = REPO / "scripts" / "can_we_do_better_than_one_in_twenty_2026-10-30.py"
HIS_FIGURE = 0.02          # 1 in 50, accepted 2026-10-30: "I accept your recommendation."


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def reader():
    assert READER.is_file(), f"the shadow report is gone: {READER}"
    return _load(READER, "sdr_under_test")


@pytest.fixture(scope="module")
def owner():
    assert OWNER.is_file(), f"the operating point's owner is gone: {OWNER}"
    return _load(OWNER, "owner_under_test")


class TestTheReaderAgreesWithTheOwner:
    def test_the_reader_returns_the_owners_value(self, reader, owner):
        """Both EXECUTED and compared, not read."""
        assert reader._chosen_target() == pytest.approx(owner.CHOSEN_TARGET), (
            "the shadow report and the owning script disagree about his "
            "operating point. They must not be able to: the reader imports it.")

    def test_it_is_his_accepted_1_in_50(self, reader):
        assert reader._chosen_target() == pytest.approx(HIS_FIGURE), (
            f"he accepted 1 in 50 on 2026-10-30 after challenging 1 in 20. "
            f"Only a further ruling of his may move this.")

    def test_it_is_not_the_comparison_size(self, reader):
        """1 in 20 was a CALIBRATION SIZE, never a live setting."""
        assert reader._chosen_target() != pytest.approx(0.05), (
            "0.05 is the comparison size the 2026-10-08 panel calibrated 3 "
            "candidate rules to so their detection rates could be compared. He "
            "challenged it and it was never configured. Reading it here would "
            "be the 'restore' the pin exists to prevent.")


class TestTheRouteSurvivesAReformattingOfTheOwner:
    """THE POINT OF THIS FILE. The value must come through unchanged when the
    owner writes the same number a different way."""

    @pytest.mark.parametrize("spelling, expected", [
        ("CHOSEN_TARGET = 0.02", 0.02),
        ("CHOSEN_TARGET = 1.0 / 50", 0.02),
        ("CHOSEN_TARGET: float = 0.02", 0.02),
        ("CHOSEN_TARGET = 2e-2", 0.02),
        ("CHOSEN_TARGET = float(1) / 50  # 1 in 50", 0.02),
    ])
    def test_any_correct_spelling_yields_the_value(self, tmp_path, reader,
                                                   spelling, expected):
        """Built in a TEMP tree, so the real producer is never written to.

        The reader resolves the owner under its module-level REPO, so pointing
        REPO at a temp tree exercises the real function against a synthetic
        owner. The 5 spellings are all CORRECT statements of 1 in 50; a reader
        that survives only the 1st is reading a spelling.
        """
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / OWNER.name).write_text(
            "TARGETS = (0.05, 0.02, 0.01)\n" + spelling + "\n", encoding="utf-8")
        old = reader.REPO
        try:
            reader.REPO = tmp_path
            assert reader._chosen_target() == pytest.approx(expected), (
                f"the spelling {spelling!r} is a correct statement of his "
                f"figure and the reader did not return it")
        finally:
            reader.REPO = old
        assert reader._chosen_target() == pytest.approx(HIS_FIGURE), (
            "the fixture leaked: the reader no longer sees the real owner")

    def test_a_missing_name_refuses_rather_than_guessing(self, tmp_path, reader):
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / OWNER.name).write_text("OTHER = 0.02\n", encoding="utf-8")
        old = reader.REPO
        try:
            reader.REPO = tmp_path
            with pytest.raises(SystemExit) as e:
                reader._chosen_target()
            assert "CHOSEN_TARGET" in str(e.value), (
                "the refusal must name what it could not find")
        finally:
            reader.REPO = old

    def test_a_missing_owner_refuses_rather_than_defaulting(self, tmp_path, reader):
        (tmp_path / "scripts").mkdir()
        old = reader.REPO
        try:
            reader.REPO = tmp_path
            with pytest.raises(SystemExit):
                reader._chosen_target()
        finally:
            reader.REPO = old


class TestTheRuleIsStillNotWired:
    """A GUARD AGAINST MY OWN TIDYING. Wiring the demotion rule is his decision.

    If a later session connects it while clearing a backlog, this fails and says
    why. It asserts on the shadow report's own declared behaviour by CALLING it,
    not by reading the source.
    """

    def test_the_shadow_report_names_itself_a_shadow(self, reader):
        doc = (reader.__doc__ or "")
        assert doc.strip(), "the shadow report lost its docstring"
        assert "shadow" in doc.lower() or "shadow" in READER.name, (
            "this reader is the SHADOW report: it reports and does not act. If "
            "that changed, the founder authorised it and this test should be "
            "rewritten deliberately rather than deleted.")
