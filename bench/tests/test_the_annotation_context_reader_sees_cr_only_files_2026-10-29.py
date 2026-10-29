#!/usr/bin/env python3
"""The annotation-context reader must see a CR-only file, because 40 of 107 are.

WHY THIS TOOL EXISTS. `scripts/read_founder_responses_2026-10-11.py` returns the
founder's annotations and their anchors; it does not return what he was
ANNOTATING. Several of his questions are unanswerable without that, because the
subject sits in CC1's text above the `#` and not in his words -- *"What is the
significance of this?"*, *"What ruling do you expect from me?"*. 5 of the 11
explanations outstanding on 2026-10-29 were of exactly that shape.

WHY THIS GUARD EXISTS, AND IT IS NOT HYPOTHETICAL. The tool's FIRST version split
on `"\\n"` alone. 40 of 107 response files are CR-ONLY, so that returned the whole
file as 1 line, the search "found" the annotation at line 0 every time, and the
context printed was the document's opening paragraph. **That is the identical
blindness the reader module exists to prevent, reproduced inside a tool written to
consume the reader.** It was caught by reading the output rather than by any
check, which is why a check now exists.

AND IT CLOSES AN `additive-standard` GAP. On 2026-10-29
`scripts/scripts_are_reached_2026-09-11.py` reported exactly 1 unreached script
and it was this one: an addition nothing reaches is not additive, so the tool is
wired to a caller here.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "what_was_he_annotating_2026-10-29.py"


@pytest.fixture(scope="module")
def mod():
    assert TOOL.is_file(), f"the tool is missing: {TOOL}"
    spec = importlib.util.spec_from_file_location("what_was_he_annotating", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["what_was_he_annotating"] = m
    spec.loader.exec_module(m)
    return m


#: 3 paragraphs, an annotation in the middle, and NO newline anywhere: the exact
#: shape 40 of his response files have.
BODY = (
    "The opening paragraph, which a blind reader reports as the context for "
    "everything in the file.\r"
    "\r"
    "The paragraph that actually precedes his mark and is what the question is "
    "about.\r"
    "\r"
    "# What is the significance of this? Please explain in plain English.\r"
    "\r"
    "A later paragraph that must not be mistaken for the one above.\r"
)


def _write(mod, tmp_path, name, text, encoding="utf-8"):
    """Write a response file into a stand-in Responses directory."""
    d = tmp_path / "Responses"
    d.mkdir(exist_ok=True)
    (d / name).write_bytes(text.encode(encoding))
    return d


class TestItSeesACrOnlyFile:
    def test_the_fixture_really_has_no_newline(self):
        """If this ever fails the test below proves nothing."""
        assert "\n" not in BODY
        assert BODY.count("\r") >= 6

    def test_it_finds_the_paragraph_that_precedes_the_mark(self, mod, tmp_path, monkeypatch):
        reader = mod._reader()
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "CR_Only_2026-10-29.txt", BODY))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("CR_Only_2026-10-29.txt",
                              "What is the significance of this?", before=4, after=1)
        joined = "\n".join(out)
        assert "the paragraph that actually precedes his mark" in joined.lower(), joined[:400]
        assert any(line.startswith(">>") for line in out), (
            "the annotation line itself was not marked, so nothing was located")

    def test_it_does_not_report_the_whole_file_as_one_line(self, mod, tmp_path, monkeypatch):
        """THE DEFECT ITSELF. A blind split returns 1 line carrying everything."""
        reader = mod._reader()
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "CR_Only_2026-10-29.txt", BODY))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("CR_Only_2026-10-29.txt",
                              "What is the significance of this?", before=2, after=1)
        marked = [l for l in out if l.startswith(">>")]
        assert len(marked) == 1
        assert "The opening paragraph" not in marked[0], (
            "the marked line carries the document's opening paragraph, which means "
            "the file was read as a single line -- the exact defect this guards")

    def test_a_later_paragraph_is_not_offered_as_the_context(self, mod, tmp_path, monkeypatch):
        reader = mod._reader()
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "CR_Only_2026-10-29.txt", BODY))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("CR_Only_2026-10-29.txt",
                              "What is the significance of this?", before=4, after=0)
        assert "A later paragraph" not in "\n".join(out)


class TestItAlsoHandlesTheOrdinaryShapes:
    def test_a_crlf_file_works(self, mod, tmp_path, monkeypatch):
        reader = mod._reader()
        body = BODY.replace("\r", "\r\n")
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "CRLF_2026-10-29.txt", body))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("CRLF_2026-10-29.txt", "What is the significance of this?",
                              before=4, after=1)
        assert "the paragraph that actually precedes his mark" in "\n".join(out).lower()

    def test_an_lf_file_works(self, mod, tmp_path, monkeypatch):
        reader = mod._reader()
        body = BODY.replace("\r", "\n")
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "LF_2026-10-29.txt", body))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("LF_2026-10-29.txt", "What is the significance of this?",
                              before=4, after=1)
        assert "the paragraph that actually precedes his mark" in "\n".join(out).lower()


class TestItReportsRatherThanGuessing:
    def test_a_missing_file_is_reported(self, mod, tmp_path, monkeypatch):
        reader = mod._reader()
        monkeypatch.setattr(reader, "RESPONSES", tmp_path / "Responses_absent")
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("Nope_2026-10-29.txt", "anything")
        assert len(out) == 1 and "no such response file" in out[0]

    def test_an_unlocatable_annotation_says_so_with_its_search(self, mod, tmp_path, monkeypatch):
        """Silence would be read as 'there is no context', which is different."""
        reader = mod._reader()
        monkeypatch.setattr(reader, "RESPONSES", _write(mod, tmp_path, "CR_Only_2026-10-29.txt", BODY))
        monkeypatch.setattr(mod, "_reader", lambda: reader)
        out = mod.context_for("CR_Only_2026-10-29.txt", "a sentence he never wrote at all")
        assert len(out) == 1
        assert "annotation not located" in out[0]
        assert "line(s)" in out[0], "the report does not say how much was searched"
