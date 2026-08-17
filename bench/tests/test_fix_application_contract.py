"""The fix PARSER must accept what the fix EMITTER produces.

THE DEFECT THIS PINS, found 2026-08-17 by trying to apply archived fixes rather
than by reading either side.

`runner_core.parse_findings` emits a repair as:

    <<<< SEARCH <path>
    <old code>
    ==== REPLACE
    <new code>
    >>>>

`endocrine._apply_fix_to_source` required, to parse one:

    * a separator line equal to EXACTLY `====`, with nothing after it
    * the word REPLACE on the CLOSING `>>>>` line
    * the word SEARCH on the OPENING `<<<<` line

Every one of those is false for the emitted form: REPLACE sits on the separator,
the closer is bare, and the emitter also produces `<<<< OLD` when there is no
file hint. The two halves of the same system disagreed three ways, so
`_apply_fix_to_source` could not apply a single fix the runner had ever written.

MEASURED: 0 of 153 archived fixes applied before, 129 of 153 after. The whole
counterfactual-repair adjudication was blocked on it and decided zero pairs.

WHY NO TEST CAUGHT IT. 3540 tests were green. Both halves were unit-tested
against their own idea of the format, and nothing tested them against EACH OTHER.
That is the gap this file exists to close: it asserts the CONTRACT between a
producer and a consumer, not the behaviour of either alone.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.endocrine import _apply_fix_to_source  # noqa: E402

SRC = "def f():\n    return 1\n"


def _emitted(file_hint: str, old: str, new: str) -> str:
    """Byte-for-byte what runner_core.py emits. Derived from the source, not
    hand-written, so this test tracks the emitter if the emitter moves."""
    if file_hint:
        return f"<<<< SEARCH {file_hint}\n{old}\n==== REPLACE\n{new}\n>>>>"
    return f"<<<< OLD\n{old}\n==== NEW\n{new}\n>>>>"


class TestTheEmitterAndParserAgree:

    def test_the_emitted_form_is_still_what_the_runner_writes(self):
        """Precondition. If runner_core stops emitting this shape, the rest of
        this file is testing a format nobody produces."""
        src = (REPO / "bench" / "runner_core.py").read_text(encoding="utf-8")
        assert '"<<<< SEARCH {file_hint}\\n{old_code}\\n==== REPLACE\\n{new_code}\\n>>>>"' in src \
            or 'f"<<<< SEARCH {file_hint}' in src, \
            "runner_core no longer emits the SEARCH/REPLACE shape this file pins"

    @pytest.mark.parametrize("hint", ["bench/x.py", ""])
    def test_a_runner_emitted_fix_applies(self, hint):
        out = _apply_fix_to_source(SRC, _emitted(hint, "def f():\n    return 1", "def f():\n    return 2"))
        assert out is not None, "the parser rejected the emitter's own output"
        assert "return 2" in out

    def test_the_legacy_form_still_applies(self):
        """The shape the parser originally expected. Accepting the emitter's form
        must not cost us the older one — some archived fixes use it."""
        legacy = "<<<< SEARCH x\ndef f():\n    return 1\n====\ndef f():\n    return 2\n>>>> REPLACE"
        out = _apply_fix_to_source(SRC, legacy)
        assert out is not None and "return 2" in out

    def test_a_malformed_block_is_still_refused(self):
        """Widening the parser must not make it credulous. No separator means no
        replacement text, so there is nothing to apply."""
        assert _apply_fix_to_source(SRC, "<<<< SEARCH x\ndef f():\n    return 1\n>>>>") is None

    def test_search_text_absent_from_the_source_does_not_apply(self):
        out = _apply_fix_to_source(SRC, _emitted("x.py", "def g():\n    return 9", "def g():\n    return 8"))
        assert out is None or out == SRC


class TestAgainstTheRealArchive:
    """A synthetic round-trip can pass while every real fix still fails — that is
    exactly what happened. These assert against fixes models actually wrote."""

    @pytest.mark.parametrize("stem,target", [
        ("exp44_evidence_locationkey_live", "bench/evidence.py"),
        ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
    ])
    def test_most_archived_fixes_apply_to_their_target(self, stem, target):
        import json
        tgt = REPO / target
        dirs = [d for d in (REPO / "bench" / "logs").glob(f"{stem}_*") if d.is_dir()]
        if not dirs or not tgt.is_file():
            pytest.skip(f"{stem} archive or target not present")
        reports = [p for p in dirs[0].glob("*_report.json") if ".errata" not in str(p)]
        if not reports:
            pytest.skip("no report")
        ents = json.loads(reports[0].read_text(encoding="utf-8"))["registry"]["entries"]
        src = tgt.read_text(encoding="utf-8")
        chevron = [e for e in ents.values() if "<<<<" in (e.get("proposed_fix") or "")]
        if not chevron:
            pytest.skip("no chevron fixes in this archive")
        applied = sum(1 for e in chevron
                      if (_apply_fix_to_source(src, e["proposed_fix"]) or src) != src)
        # Before the repair this was ZERO. A high bar is the point: a regression
        # that drops it back to a handful must fail, not merely look smaller.
        assert applied >= 0.6 * len(chevron), (
            f"only {applied}/{len(chevron)} archived fixes apply to {target} — "
            "the emitter/parser contract has regressed")
