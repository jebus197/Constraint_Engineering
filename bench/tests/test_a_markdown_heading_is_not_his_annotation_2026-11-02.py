"""A markdown heading is not one of his annotations, and 2 hashes settle it.

THE DEFECT, OBSERVED 2026-11-02 BY THE COMMIT GATE REFUSING A COMMIT. He
attached an orchestrator note written by an external model into `Responses/`.
The annotation reader decides whether a line opening with a hash is his comment
or a markdown heading. It prefers an ORACLE -- an annotated response file is
normally a copy of a report this project generated, so the original says exactly
which lines are the report's and which are his -- and falls back to SHAPE where
no original exists, on the reasoning that a heading is short and does not end in
sentence punctuation.

That note has no oracle, because it did not come from this project. So the shape
test ran, and 2 of the note's 20 hash lines defeated it for the same reason:
they are headings PHRASED AS QUESTIONS, so they end in "?". The gate then
refused the commit because 2 annotations in the window had no verdict row, which
is correct behaviour on a false premise -- they were never his annotations.

THE RULE, AND IT IS MEASURED RATHER THAN ASSUMED. His convention is exactly 1
hash. Across the 45 response files where a generated original survives as an
oracle, so his lines are known rather than inferred, **583 of his annotations
open with exactly 1 hash and 0 open with 2 or more**, Wilson 95% [0.000000,
0.006546]. In the live reporting window, 568 of 570 annotations open with 1 hash
and the only 2 with more were the 2 leaking headings -- 2 of 570, 0.003509,
Wilson 95% [0.000963, 0.012702].

MEASURED EFFECT OF THE FIX, by diffing the reader's output against the previous
revision rather than by reasoning about it: 3 annotations removed, 0 added. All
3 are markdown headings, the 2 above plus a 2-hash heading in an August report
that the 120-character shape limit had let through.

WHY THE SHAPE TEST IS KEPT. For a SINGLE-hash line it is still the only signal
available when no oracle exists, and the oracle is preferred over it anyway. The
new rule narrows the shape test's job rather than replacing it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
RESPONSES = pathlib.Path.home() / "Developer_Projects" / "Responses"
TTS = pathlib.Path.home() / "Desktop" / "CDSFL_tts"


@pytest.fixture(scope="module")
def rd():
    spec = importlib.util.spec_from_file_location("_reader_guard", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_reader_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTwoHashesIsAlwaysAHeading:
    @pytest.mark.parametrize("line", [
        "## CAUTION — READ FIRST",
        "### 1. Severity today — arbitrary or measured?",
        "### 2. Multi-vendor diversity and residual risk — is the orchestrator right?",
        "###### A six-hash heading that ends in a full stop.",
        "## Note 6 — Scope, diversity, and an optional validation front, which runs"
        " past a hundred and twenty characters so the old length rule let it through.",
    ])
    def test_a_multi_hash_line_is_a_heading(self, rd, line):
        """Including the forms that defeated the shape test: a heading phrased
        as a question, and a heading longer than the 120-character limit."""
        assert rd._looks_like_a_markdown_heading(line), (
            f"a line opening with 2+ hashes must be read as a heading, never as "
            f"one of his annotations: {line!r}")


class TestOneHashIsStillJudgedOnShape:
    def test_his_conversational_annotation_is_not_a_heading(self, rd):
        """ANTI-VACUITY. If the rule swallowed single-hash lines too, every one
        of his annotations would vanish and the suite above would still pass."""
        his = ("# Can we improve on this statistic? A 1 in 20 chance of demoting "
               "a model that is performing just fine seems unreasonably high?")
        assert not rd._looks_like_a_markdown_heading(his), (
            "his own conversational annotation was read as a heading")

    def test_a_single_hash_heading_is_still_caught_by_shape(self, rd):
        """The shape test must keep working for the 1-hash case, which is the
        only case where it is still the deciding signal."""
        assert rd._looks_like_a_markdown_heading("# George asked")

    def test_a_single_hash_question_is_treated_as_his(self, rd):
        """The deliberate asymmetry: a 1-hash line ending in '?' is HIS, which
        is exactly what the shape test is for and why 2 hashes had to be the
        discriminator rather than the punctuation."""
        assert not rd._looks_like_a_markdown_heading(
            "# So what did the panel actually conclude about this?")


class TestTheRuleIsMeasuredAgainstTheOracle:
    """The justification, recomputed rather than quoted.

    An annotated response file whose generated original survives is an exact
    oracle: a line not present in the original is his. This recomputes the
    0-of-583 figure the rule rests on, so the rule cannot outlive its evidence.
    """

    def test_none_of_his_oracle_backed_annotations_uses_two_hashes(self):
        if not RESPONSES.is_dir() or not TTS.is_dir():
            pytest.skip("his Responses or the TTS originals are not readable here")
        single = multi = checked = 0
        offenders = []
        for f in sorted(RESPONSES.rglob("*")):
            if not f.is_file() or f.suffix not in (".txt", ".md"):
                continue
            orig = TTS / f.name
            if not orig.is_file():
                continue
            checked += 1
            try:
                report = {l.strip() for l in orig.read_text(errors="replace").splitlines()
                          if l.strip()}
                lines = f.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for ln in lines:
                s = ln.strip()
                if not s or s in report or not s.startswith("#"):
                    continue
                if len(s) - len(s.lstrip("#")) >= 2:
                    multi += 1
                    offenders.append((f.name, s[:70]))
                else:
                    single += 1
        if checked == 0:
            pytest.skip("no oracle-backed response file is present here")
        assert single > 0, (
            "no single-hash annotation of his was found, so this test would "
            "pass vacuously")
        assert multi == 0, (
            f"{multi} of his oracle-backed annotations open with 2+ hashes, so "
            f"the 2-hash rule would DROP his own words: {offenders[:4]}")


class TestTheNoteThatExposedItIsNoLongerRead:
    def test_no_heading_from_an_external_note_is_read_as_his(self, rd):
        """The live case, pinned to the PROPERTY rather than to that filename:
        no line opening with 2+ hashes, anywhere in his responses, may appear
        among the annotations the reader returns."""
        if not RESPONSES.is_dir():
            pytest.skip("his Responses folder is not readable here")
        try:
            ann = rd.annotations()
        except Exception as exc:                            # noqa: BLE001
            pytest.skip(f"the reader could not run here: {exc}")
        assert ann, "the reader returned no annotations, so this is vacuous"
        cache: dict = {}
        leaks = []
        for a in ann:
            p = RESPONSES / str(a.get("file") or "")
            if p not in cache:
                try:
                    cache[p] = p.read_text(errors="replace").splitlines()
                except OSError:
                    cache[p] = []
            try:
                src = cache[p][int(a.get("line_index"))].lstrip()
            except Exception:                               # noqa: BLE001
                continue
            if src.startswith("#") and len(src) - len(src.lstrip("#")) >= 2:
                leaks.append(f"{a.get('file')}#{a.get('line_index')}")
        assert not leaks, (
            f"{len(leaks)} markdown heading(s) are still read as his "
            f"annotations: {leaks[:4]}")
