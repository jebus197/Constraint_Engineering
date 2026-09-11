"""A note must not be able to buy amnesty for its OWN prose. Two ways it could.

TASK V8'S LOAD-BEARING CLAIM was that the verbatim exemption is SCOPED: "prose
outside the markers is linted normally, so a note cannot buy amnesty for its own
writing by quoting someone". BOTH PANEL SEATS BROKE IT INDEPENDENTLY on
2026-09-11, in separate sandboxes -- which is the first round where that
independence was real, because until the same day every seat shared one writable
copy. Both were reproduced here before either fix was accepted.

  1. ONE SPACE ON A BLANK LINE. `sentences()` split paragraphs on a literal
     2-newline string; `verbatim_paragraphs()` split on a whitespace-tolerant
     regular expression. A blank line carrying a space is a break to the second
     and not to the first, so the two paragraph NUMBERINGS drift -- and the
     exempt set, computed by the second, is applied to findings numbered by the
     first. A Rule 27 violation AFTER `verbatim-end`, in the note's own voice,
     counted 0 and was tagged [verbatim]. The count is what the blocking
     pre-commit ratchet reads, so the note commits.

  2. A MARKER INSIDE A CODE FENCE. A note DOCUMENTING this syntax in a fenced
     block opened a real region and exempted everything after it.
     `sentences()` already skips fenced paragraphs; the marker scan did not.

BOTH ARE THE SAME SHAPE AND IT IS THE PROJECT'S OWN: two hand-written
expressions of one rule with no comparator, sitting inside the exemption whose
entire claim is that it is scoped. `verbatim_paragraphs`' docstring asserted the
numberings *"agree by construction rather than by coincidence"*. They agreed by
coincidence: **20 of 730 markdown files in this tree already break it, 2.7397%,
Wilson [1.7804%, 4.1938%], Clopper-Pearson [1.6814%, 4.1997%]**.

THE REPAIR MOVES NOTHING ELSE, measured rather than assumed: across all 730
markdown files the total finding count is **1770 before and 1770 after**, and
**0 files** change count. The amnesty closes without disturbing any existing
measurement or any ratchet baseline.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LINT = ROOT / "scripts" / "note_vagueness_lint.py"


@pytest.fixture(scope="module")
def nvl():
    spec = importlib.util.spec_from_file_location("nvl", LINT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["nvl"] = m
    spec.loader.exec_module(m)
    return m


def _write(tmp_path, name, body):
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    return f


def counted(nvl, f):
    """The findings that COUNT -- what the blocking ratchet actually reads.

    `lint()` reports everything and the exemption is applied by `main()`, which
    subtracts the verbatim paragraphs from the TOTAL. A first version of this
    file asserted on `lint()` alone and so tested the reporting half while
    claiming to test the counting half -- the exact confusion this file exists
    to prevent, made while writing it.
    """
    exempt = nvl.verbatim_paragraphs(f.read_text(encoding="utf-8"))
    return [x for x in nvl.lint(f) if x[0] not in exempt]


class TestTheExemptionDoesNotLeakPastTheEndMarker:
    def test_a_whitespace_blank_line_does_not_buy_amnesty(self, nvl, tmp_path):
        f = _write(tmp_path, "amnesty.md",
                   "Intro paragraph, clean.\n \n"
                   "<!-- verbatim-begin: a seat -->\n"
                   "Quoted material here.\n"
                   "<!-- verbatim-end -->\n\n"
                   "The panel returned twenty-nine findings in total.\n")
        findings = counted(nvl, f)
        assert len(findings) == 1, (
            f"the note's own sentence after verbatim-end was exempted: {findings}")

    def test_the_control_without_the_space_behaves_identically(self, nvl, tmp_path):
        """SAME BYTES BUT FOR THE SPACE. If these 2 ever disagree again, the
        splitters have diverged again."""
        body = ("Intro paragraph, clean.\n{}\n"
                "<!-- verbatim-begin: a seat -->\n"
                "Quoted material here.\n"
                "<!-- verbatim-end -->\n\n"
                "The panel returned twenty-nine findings in total.\n")
        a = counted(nvl, _write(tmp_path, "a.md", body.format(" ")))
        b = counted(nvl, _write(tmp_path, "b.md", body.format("")))
        assert len(a) == len(b) == 1, (len(a), len(b))

    def test_there_is_exactly_one_paragraph_splitter(self, nvl):
        """The root cause, pinned. Two expressions of one rule is what broke it."""
        src = LINT.read_text(encoding="utf-8")
        body = src[src.index("def sentences("):]
        body = body[:body.index("\ndef lint(")]
        assert 'split("\\n\\n")' not in body, (
            "a second literal paragraph split has reappeared inside the "
            "sentence/verbatim pair")
        assert src.count("PARAGRAPH_BREAK = re.compile") == 1


class TestAMarkerInsideAFenceIsDocumentationNotAnInstruction:
    def test_a_fenced_begin_marker_opens_nothing(self, nvl, tmp_path):
        f = _write(tmp_path, "fence.md",
                   "Intro, clean.\n\nThe syntax is documented here:\n\n"
                   "```\n<!-- verbatim-begin: whoever -->\n```\n\n"
                   "The panel returned twenty-nine findings in total.\n")
        assert len(counted(nvl, f)) == 1, "a fenced marker opened a real region"

    def test_a_fenced_end_marker_INSIDE_a_region_does_not_close_it(self, nvl, tmp_path):
        """The other direction. A fence inside an open region is QUOTED TEXT.

        THIS TEST PASSED FOR THE WRONG REASON AT FIRST and only a mutation said
        so. The implementation stripped fences only while OUTSIDE a region, so
        with a region open the fenced `verbatim-end` was scanned, the region
        closed at it, and the paragraph after -- still meant to be quoted --
        stopped being exempt. The fixture did not notice because that paragraph's
        violation was suppressed by a colon and never counted either way.
        Removing the condition entirely changed nothing and every test stayed
        green: a control that cannot fail is not a control. The fixture now
        carries a violation that DOES count, and the stripping is unconditional.
        """
        f = _write(tmp_path, "nested.md",
                   "Intro.\n\n<!-- verbatim-begin: seat -->\n"
                   "Quoted, and it shows the syntax.\n\n"
                   "```\n<!-- verbatim-end -->\n```\n\n"
                   "Still quoted, twenty-nine findings in all.\n\n"
                   "<!-- verbatim-end -->\n\n"
                   "Own prose with thirty-one in it.\n")
        exempt = nvl.verbatim_paragraphs(f.read_text())
        findings = counted(nvl, f)
        assert len(findings) == 1, (
            f"expected only the note's own prose to count, got {findings}; "
            f"exempt paragraphs were {sorted(exempt)}")
        assert "thirty-one" in findings[0][2], findings


class TestTheExemptionStillWorks:
    """THE ADDITIVE HALF. A fix that closed the exemption entirely would pass
    every test above and destroy the capability V8 exists to provide."""

    def test_a_quoted_spelled_number_is_still_exempt(self, nvl, tmp_path):
        f = _write(tmp_path, "record.md",
                   "Intro, clean.\n\n"
                   "<!-- verbatim-begin: a seat -->\n"
                   "The seat wrote: the panel returned twenty-nine findings.\n"
                   "<!-- verbatim-end -->\n\n"
                   "Everything here is in digits: 29.\n")
        assert counted(nvl, f) == [], (
            "the verbatim region is no longer exempt at all; V8's capability is "
            "gone, which no measurement here justifies")

    def test_the_exempted_finding_is_still_REPORTED(self, nvl, tmp_path):
        """An exemption a reader cannot see is indistinguishable from a checker
        that missed something."""
        f = _write(tmp_path, "record2.md",
                   "<!-- verbatim-begin: a seat -->\n"
                   "The panel returned twenty-nine findings.\n"
                   "<!-- verbatim-end -->\n")
        marked = nvl.verbatim_paragraphs(f.read_text())
        assert marked, "nothing is marked verbatim, so nothing would be reported"


class TestTheMeasurementBehindTheFix:
    def test_the_two_old_splitters_really_do_disagree_in_this_tree(self):
        """ANTI-VACUITY for the whole file. If no file in the tree had a
        whitespace-bearing blank line, the defect would be unreachable and every
        test above would be theatre."""
        files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]
        dis = 0
        for p in files:
            try:
                t = p.read_text(errors="replace")
            except OSError:
                continue
            if len(t.split("\n\n")) != len(re.split(r"\n\s*\n", t)):
                dis += 1
        assert dis >= 5, (
            f"only {dis} of {len(files)} files carry the divergence; the "
            f"2.7397% figure in this docstring needs re-measuring")
