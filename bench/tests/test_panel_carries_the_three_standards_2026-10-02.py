"""Every panel dispatch carries all 3 of the founder's formal standards.

FOUNDER'S INSTRUCTION, 2026-10-02, verbatim: "These principles should be
mechanically written into all panel dispatches and not just this single
dispatch. Is this already happening?"

IT WAS NOT. Measured when he asked, over
`bench/confer_maths_panel_2026-09-05.py`: "additive" appeared 7 times,
"simplest sufficient" 0 times and "composab" 0 times. So 1 of the 3 standards
reached the seats and 2 did not, and every panel round run before that date was
briefed without them.

WHY THIS TEST IMPORTS THE MODULE RATHER THAN GREPPING IT. The standards have to
be in the SYSTEM STRING THE SEATS ACTUALLY RECEIVE, not merely somewhere in the
file. A comment quoting a standard would satisfy a text scan while reaching no
seat -- the addition-that-nothing-reaches failure the additive standard itself
names, and the reason `execute-do-not-grep` exists.

COMPOSABILITY IS THE ONE MOST EASILY MIS-STATED, so its content is asserted and
not just its name. His definition is NOT "two fixes may coexist": it is that
composition is justified only by a DEMONSTRATED advantage over either fix alone,
and that a single fix which performs as well is preferred.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"

pytestmark = pytest.mark.skipif(not DISPATCHER.is_file(), reason="dispatcher absent")


@pytest.fixture(scope="module")
def system_prompt():
    sys.path.insert(0, str(ROOT / "bench"))
    spec = importlib.util.spec_from_file_location("panel_under_test", DISPATCHER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["panel_under_test"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    s = getattr(m, "SYSTEM", None)
    assert isinstance(s, str) and s, "the dispatcher exposes no SYSTEM string"
    return s


class TestAllThreeReachTheSeat:

    @pytest.mark.parametrize("standard", [
        "ADDITIVE STANDARD", "SIMPLEST SUFFICIENT", "COMPOSABILITY"])
    def test_the_standard_is_in_the_prompt_the_seats_receive(self, system_prompt, standard):
        assert standard in system_prompt, (
            f"{standard} reaches no seat; a standard that is not in the SYSTEM "
            f"string is a standard the panel was never briefed on")

    def test_composability_is_not_stated_as_mere_coexistence(self, system_prompt):
        """THE MIS-STATEMENT THE FOUNDER WARNED AGAINST, pinned.

        His words: "Composability doesn't mean composing two solutions just
        because they can be composed." A brief that says only "compose your
        fixes" licenses exactly the thing he excluded.
        """
        i = system_prompt.find("COMPOSABILITY")
        block = system_prompt[i:i + 1400]
        assert "demonstrably" in block or "demonstrated" in block, (
            "composability is stated without the DEMONSTRATION requirement, so "
            "it reads as 'compose when you can' rather than 'compose when "
            "measured to be better'")
        assert "in isolation" in block or "alone" in block, (
            "the comparison against each fix ALONE is missing, which is the "
            "whole content of the standard")
        assert "prefer" in block.lower(), (
            "the rule that a single fix which performs as well is PREFERRED is "
            "missing")

    def test_simplest_sufficient_keeps_its_exception(self, system_prompt):
        """`simplicity-default` carries an exception for prose, graphics and UX.
        Dropping it would brief seats to strip expression that serves the task."""
        i = system_prompt.find("SIMPLEST SUFFICIENT")
        block = system_prompt[i:i + 900]
        assert "prose" in block.lower(), "the prose/graphics/UX exception is gone"

    def test_the_standards_survive_alongside_each_other(self, system_prompt):
        """ANTI-REGRESSION on the additive standard's own terms: adding 2
        standards must not have displaced the first, and the schema must still
        be there."""
        for required in ("ADDITIVE STANDARD", "SIMPLEST SUFFICIENT",
                         "COMPOSABILITY", "no compelled convergence"):
            assert required.lower() in system_prompt.lower(), required
