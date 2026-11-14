"""B194. A block marked not-in-force must reach 0 prompts; its siblings must not.

WHY THIS FILE EXISTS. The `cc2` seat was asked, in the joint round of
2026-11-14, to write the paragraph the founder would paste for his proposed 4th
formal standard. It DECLINED to write it where the brief pointed and said why: a
draft split into 2 blocks -- a `PROPOSED -- NOT IN FORCE` header and a directive
body -- classifies the body as HARD on the word MUST and the header as SOFT,
because the header carries none of `_HARD_BLOCK_MARKERS`. In the minimal render
only HARD blocks are carried, so the binding sentence would reach every seat and
the sentence saying it is not binding would reach none of them.

WHAT IS ASSERTED BY EXECUTION RATHER THAN BY READING. The 2 strings the seat
named are driven through the project's OWN hard predicate, so the defect is
reproduced here rather than quoted. The strip is then driven end-to-end through
both live read paths against a directive file written into a temporary tree, so
nothing in the repository is touched.

THE ANTI-VACUITY CASES ARE THE POINT. A stripper that removed everything would
pass a test asserting only that the draft is gone, so every removal case has a
sibling that must SURVIVE, and the no-marker case asserts BYTE identity.
"""
from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CORE = ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"

#: The 2 strings `cc2` named, reproduced verbatim from its reply.
DRAFT_HEADER = ("# PROPOSED 4th FORMAL STANDARD -- NOT IN FORCE -- AWAITS THE "
                "FOUNDER'S RULING")
DRAFT_BODY = ("real-world-applicability: A claim of real-world applicability "
              "MUST name the consequence for the human in the loop.")


@pytest.fixture(scope="module")
def comp():
    return importlib.import_module("bench.cdsfl_registry.composer")


class TestTheDefectIsReproduced:
    def test_the_header_is_soft_and_the_body_is_hard(self, comp):
        """THE DEFECT, by calling the predicate rather than citing the seat."""
        assert comp._block_is_hard(DRAFT_BODY) is True, (
            "the draft body is not HARD, so the defect this file guards cannot "
            "arise and the fixture no longer reproduces what cc2 found")
        assert comp._block_is_hard(DRAFT_HEADER) is False, (
            "the not-in-force header is now HARD, which would mean the warning "
            "travels with the draft and this guard's premise has moved")

    def test_the_minimal_render_carries_only_hard_blocks(self, comp):
        """WHY SOFT MEANS GONE rather than merely deprioritised, in the render
        the seat was writing for."""
        text = DRAFT_HEADER + "\n\n" + DRAFT_BODY
        blocks = comp._split_packet_directives(text)
        hard = [b for b in blocks if comp._block_is_hard(b)]
        assert any(DRAFT_BODY in b for b in hard)
        assert not any("NOT IN FORCE" in b for b in hard)


class TestThePredicate:
    def test_it_sees_the_marker_in_either_case(self, comp):
        m = comp._NOT_IN_FORCE_MARKER
        assert comp.block_is_not_in_force(f"x {m} y")
        assert comp.block_is_not_in_force(f"x {m.lower()} y")

    def test_it_does_not_fire_on_prose_about_drafts(self, comp):
        """A SENTENCE DESCRIBING A DRAFT IS NOT A DRAFT. The marker is an
        explicit sentinel for exactly this reason: `NOT IN FORCE` as a phrase
        appears in prose that discusses ratification."""
        assert not comp.block_is_not_in_force(
            "This paragraph explains that an unratified standard is not in "
            "force until the founder rules on it.")
        assert not comp.block_is_not_in_force(DRAFT_HEADER)


class TestTheStrip:
    def test_text_with_no_marker_is_returned_BYTE_IDENTICAL(self, comp):
        """THE PROPERTY THAT PROTECTS EVERY MODEL. The full specification is
        delivered verbatim, so a stripper that re-shaped whitespace would change
        what 5 of 5 models receive for a defect none of them has."""
        raw = CORE.read_text(encoding="utf-8")
        assert comp.strip_not_in_force(raw) == raw
        assert comp.strip_not_in_force("") == ""
        odd = "a\n \nb\n\t\nc\n\n\nd\n"
        assert comp.strip_not_in_force(odd) == odd

    def test_a_marked_block_goes_and_its_siblings_stay(self, comp):
        m = comp._NOT_IN_FORCE_MARKER
        text = (f"KEEP ONE: this MUST happen.\n\n"
                f"{m} DRAFT: this MUST NOT happen yet.\n\n"
                f"KEEP TWO: this MUST also happen.\n")
        out = comp.strip_not_in_force(text)
        assert "DRAFT:" not in out
        assert m not in out
        assert "KEEP ONE" in out and "KEEP TWO" in out

    def test_every_block_of_a_multi_block_draft_needs_its_own_marker(self, comp):
        """THE DOCUMENTED LIMIT, asserted so it cannot be mistaken for a bug.
        The marker is per block because a region needs a closing marker and an
        unbalanced region is a live failure mode in this project's own linter.
        """
        m = comp._NOT_IN_FORCE_MARKER
        text = f"{m} DRAFT part 1 MUST wait.\n\nDRAFT part 2 MUST wait.\n"
        out = comp.strip_not_in_force(text)
        assert "part 1" not in out
        assert "part 2" in out, (
            "an unmarked second paragraph survived, which is the documented "
            "per-block semantics; if this changes, the docstring must change")


class TestItReachesZeroPrompts:
    @staticmethod
    def _tree(tmp_path, body: str) -> pathlib.Path:
        d = tmp_path / "directives" / "universal"
        d.mkdir(parents=True)
        (d / "cdsfl_core_formal.md").write_text(body, encoding="utf-8")
        return tmp_path / "directives"

    def test_the_full_path_drops_the_draft_and_keeps_the_sibling(
            self, comp, tmp_path, monkeypatch):
        m = comp._NOT_IN_FORCE_MARKER
        body = (f"LIVE RULE: a finding MUST carry a falsifier.\n\n"
                f"{m} DRAFT RULE: a claim MUST name its consequence.\n")
        monkeypatch.setattr(comp, "DIRECTIVES_DIR",
                            self._tree(tmp_path, body))
        pk = comp._load_universal_directive("cc2")
        assert "DRAFT RULE" not in pk.text, (
            "an unratified block reached a seat's prompt through the full path")
        assert "LIVE RULE" in pk.text, (
            "the live sibling was removed too, so the strip is over-broad")

    def test_the_minimal_path_drops_the_draft_and_keeps_the_sibling(
            self, comp, tmp_path, monkeypatch):
        m = comp._NOT_IN_FORCE_MARKER
        body = (f"LIVE RULE: a finding MUST carry a falsifier.\n\n"
                f"{m} DRAFT RULE: a claim MUST name its consequence.\n")
        monkeypatch.setattr(comp, "DIRECTIVES_DIR",
                            self._tree(tmp_path, body))
        out = comp._render_universal_minimal()
        assert "DRAFT RULE" not in out, (
            "an unratified HARD block was carried verbatim into the minimal "
            "render, which is the defect cc2 found")
        assert "LIVE RULE" in out, (
            "the live sibling vanished from the minimal render")

    def test_without_the_marker_the_draft_WOULD_reach_the_prompt(
            self, comp, tmp_path, monkeypatch):
        """THE FAILING INPUT, kept. A defence tested only on text it removes
        proves nothing about the hazard it exists for."""
        body = (f"LIVE RULE: a finding MUST carry a falsifier.\n\n"
                f"{DRAFT_HEADER}\n\n{DRAFT_BODY}\n")
        monkeypatch.setattr(comp, "DIRECTIVES_DIR",
                            self._tree(tmp_path, body))
        out = comp._render_universal_minimal()
        assert DRAFT_BODY in out, (
            "the unmarked draft body no longer reaches the minimal render, so "
            "something else now suppresses it and this guard is vacuous")
        assert "NOT IN FORCE" not in out, (
            "the warning now travels with the draft, which would mean the "
            "defect is fixed elsewhere and this file should say so")


class TestItIsDiscoverable:
    def test_the_core_directive_tells_an_author_the_marker_exists(self):
        """cc2's REFUSED WORKAROUND IS THE REASON. Rewording a draft to dodge
        the keywords was refused because *"the next author would not know to"*,
        and a marker nothing documents has the same fault.
        """
        text = CORE.read_text(encoding="utf-8")
        assert "not-in-force" in text.lower(), (
            "the canonical directive does not mention the not-in-force "
            "mechanism, so an author drafting in it cannot know it exists")
        assert "composer.py" in text, (
            "the directive does not say where the sentinel is defined, so an "
            "author is told a mechanism exists without being told its spelling")

    def test_the_directive_does_NOT_spell_the_sentinel(self, comp):
        """A FILE THAT SPELLS THE SENTINEL DELETES ITS OWN DOCUMENTATION, which
        is the 3rd instance of this class tonight -- see B189, where 2 clauses
        of an entry's own prose were read by the asking predicate as live asks.
        """
        text = CORE.read_text(encoding="utf-8")
        assert comp._NOT_IN_FORCE_MARKER not in text.upper(), (
            "the directive spells the sentinel literally, so the block "
            "documenting the mechanism is stripped by the mechanism")
