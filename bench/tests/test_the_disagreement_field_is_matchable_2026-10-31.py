#!/usr/bin/env python3
"""The brief validator must be able to see the field name the template prescribes.

THE DEFECT, OBSERVED 2026-10-31 BY BEING REFUSED BY IT.
`scripts/panel_brief_validate.py` required the output section to mention a
disagreement, searching for `r"\\bdisagree"`. The field name every compliant
brief uses -- and the one
`bench/directives/universal/panel_brief_template.md` describes -- is
`strongest_disagreement`. `\\b` does NOT match between the underscore and the
`d`, because an underscore is a word character. So a brief naming the field
EXACTLY as the template prescribes was REFUSED unless the surrounding prose
happened to repeat the word with a space in front of it.

WHY THAT IS WORSE THAN A MISSED MATCH. The check's own message reads: *"name
disagreement as a FIELD in the output section, not as prose elsewhere"*. As
written it could only ever be satisfied BY prose. A checker whose message
contradicts its predicate teaches the wrong lesson to everyone it refuses, and
it refused the B21 joint brief on 2026-10-31 for a brief that was compliant.

THE FIX IS THE LEADING BOUNDARY REMOVED, NOT THE CHECK WEAKENED. The right-hand
side is unchanged, so an unrelated word cannot run on from it, and the
underlying property -- that the output section names a disagreement field -- is
asserted here in both directions: a brief naming it passes, and a brief with an
output section that names no disagreement at all is still refused.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
TEMPLATE = (REPO / "bench" / "directives" / "universal"
            / "panel_brief_template.md")

_COMPLIANT = (
    "# A brief\n\n"
    "## REQUIRED SECTION 1 - the question\n"
    "What is X, and what would refute the answer?\n\n"
    "## REQUIRED OUTPUT SHAPE\n\n"
    "- `verdict` - one of A or B\n"
    "- `reasoning` - the derivation, naming each instrument\n"
    "- `falsifier` - the falsifier written, the command, its executed output\n"
    "- `strongest_disagreement` - with this brief's own framing\n\n"
    "## REQUIRED - termination\n"
    "Stop when a further pass adds nothing.\n"
)

_NO_DISAGREEMENT = _COMPLIANT.replace(
    "- `strongest_disagreement` - with this brief's own framing\n", "")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("brief_validate", VALIDATOR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheFieldNameIsMatchable:
    def test_the_underscored_field_name_satisfies_the_check(self, mod):
        """The exact shape that was refused."""
        body = mod._section(_COMPLIANT, r"output|deliverable|what to return")
        assert body is not None, "the output section was not even found"
        assert re.search(r"disagree", body, re.I), (
            "`strongest_disagreement` does not satisfy the predicate, so a "
            "brief naming the field as the template prescribes is refused")

    def test_the_old_predicate_really_did_refuse_it(self):
        """So this file is not passing on a change that never mattered."""
        import importlib.util as u
        spec = u.spec_from_file_location("bv2", VALIDATOR)
        m = u.module_from_spec(spec); spec.loader.exec_module(m)
        body = m._section(_COMPLIANT, r"output|deliverable|what to return")
        assert not re.search(r"\bdisagree", body, re.I), (
            "the old leading-boundary predicate MATCHES this brief, so the "
            "defect this file records did not exist and the repair is noise")

    def test_the_predicate_has_no_leading_word_boundary(self, mod):
        """A ratchet: re-adding `\\b` reintroduces the defect silently."""
        src = VALIDATOR.read_text()
        assert r'r"\bdisagree"' not in src, (
            "the leading word boundary is back, so `strongest_disagreement` is "
            "invisible again")


class TestTheCheckIsNotWeakened:
    """★ A MUTATION SURVIVED THE FIRST VERSION OF THIS CLASS. Deleting the
    disagreement check outright left every test here GREEN, because they
    asserted on `re.search` against a section rather than on what `validate`
    actually REFUSES. A test that re-runs the predicate is not testing the
    checker. These call `validate` and read its problem list."""

    #: THE EXACT MESSAGE, because 2 different branches emit text containing the
    #: word. Matching the substring alone let "the check is removed entirely"
    #: SURVIVE: with the branch disabled the chain falls through to
    #: `_field_the_detector_can_read`, whose message also says disagreement, so
    #: a loose predicate reported the check as present when it was gone. A test
    #: that cannot tell 2 checks apart cannot tell whether either is there.
    MESSAGE = "requires the seat to state its DISAGREEMENT"

    def test_validate_refuses_a_brief_whose_output_names_no_disagreement(self, mod):
        problems = mod.validate(_NO_DISAGREEMENT)
        assert any(self.MESSAGE in str(x) for x in problems), (
            "validate() raised no disagreement problem for a brief whose "
            "output section names none, so the check is gone rather than "
            "repaired: %r" % (problems,))

    def test_validate_accepts_the_underscored_field_name(self, mod):
        """The whole point: the compliant brief must NOT be refused for this."""
        problems = mod.validate(_COMPLIANT)
        assert not any(self.MESSAGE in str(x) for x in problems), (
            "validate() still refuses a brief naming `strongest_disagreement` "
            "as a field: %r" % (problems,))

    def test_the_two_disagreement_checks_are_distinguishable(self, mod):
        """So this file cannot be fooled by the fall-through again."""
        problems = [str(x) for x in mod.validate(_NO_DISAGREEMENT)]
        mine = [x for x in problems if self.MESSAGE in x]
        other = [x for x in problems
                 if "disagree" in x.lower() and self.MESSAGE not in x]
        assert len(mine) == 1, (
            "the specific message appears %d times: %r" % (len(mine), mine))
        assert not other or all(self.MESSAGE not in x for x in other)

    def test_the_section_scoped_predicate_still_rejects_outside_prose(self, mod):
        body = mod._section(_NO_DISAGREEMENT, r"output|deliverable|what to return")
        assert body is not None
        assert not re.search(r"disagree", body, re.I), (
            "a brief whose output section names no disagreement now matches, so "
            "the check has been weakened rather than repaired")

    def test_prose_outside_the_output_section_does_not_count(self, mod):
        """Section scoping is the property added 2026-09-09 and must survive."""
        brief = _NO_DISAGREEMENT.replace(
            "What is X, and what would refute the answer?",
            "What is X? State your strongest disagreement somewhere.")
        body = mod._section(brief, r"output|deliverable|what to return")
        assert not re.search(r"disagree", body, re.I), (
            "a mention OUTSIDE the output section satisfied the check, so "
            "section scoping is broken")

    def test_the_template_still_prescribes_this_field(self):
        """If the template renames it, this whole file is about the wrong name."""
        assert TEMPLATE.is_file(), TEMPLATE
        assert "disagreement" in TEMPLATE.read_text().lower(), (
            "the template no longer asks for a disagreement, so the check and "
            "this guard both need rethinking rather than repairing")


class TestTheRealBriefsPass:
    @pytest.mark.parametrize("name", [
        "joint_the_role_layer_b21_2026-10-31",
        "joint_what_is_a_proof_outside_code_2026-10-31",
    ])
    def test_tonights_joint_briefs_satisfy_it(self, mod, name):
        brief = REPO / "bench" / "logs" / name / "BRIEF.md"
        assert brief.is_file(), brief
        body = mod._section(brief.read_text(),
                            r"output|deliverable|what to return")
        assert body is not None, f"{name} has no output section"
        assert re.search(r"disagree", body, re.I), (
            f"{name} would be refused by the disagreement check")
