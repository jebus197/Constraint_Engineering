"""The routing falsifier extractor must lose no block a model actually sends.

TWO DEFECTS, ONE FUNCTION, BOTH MEASURED ON 2026-08-30.

Round 0 (original): the closing fence could match ANYWHERE, including mid-line
inside a string. A falsifier quoting a fenced listing -- the only shape available
for a claim about a document that prints code -- was truncated at its own first
inner backtick, and the fragment still parsed and still carried an assert, so it
passed every runnability check.

Round 1 (my repair): required the closing fence to sit alone on its line. That
fixed the self-fenced case and CC2 measured it as a NET REGRESSION: with a
malformed first closer the non-greedy body scanned past it, past the SECOND
block's opening fence, and paired with the second block's closer. One trailing
word destroyed EVERY block in the reply. Old pattern 2 blocks, new pattern 0.

Round 2 (block-by-block with a permissive fallback) recovered the malformed
closers and broke the self-fenced fixtures again, because the fallback grabs the
falsifier's own inner backticks.

The requirements only conflict per-block, not per-reply. The strict reading of
the WHOLE reply is taken first; the permissive reading is used only when the
strict one yields no runnable candidate at all. A self-fenced falsifier is
strict-readable and never reaches the fallback; a reply with malformed closers
is not, so it does.

This matters because the consumer is the routing ladder, whose failure mode is a
silent "ladder exhausted" -- the exact defect the extractor exists to prevent.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v2 as R

BODY = "import x\nassert False, 'FALSIFIED'"

SHAPES = {
    "clean closer":               f"```python\n{BODY}\n```\n",
    "closer with trailing text":  f"```python\n{BODY}\n``` — run that.\n",
    "closer glued to last line":  f"```python\n{BODY}```\n",
    "closer followed by a dot":   f"```python\n{BODY}\n```.\n",
    "two blocks, first bad":      f"```python\n{BODY}\n``` — run that.\n\n```python\n{BODY}\n```\n",
    "CRLF and indented closer":   f"```python\r\n{BODY}\r\n   ```\r\n",
    "no language tag":            f"```\n{BODY}\n```\n",
}


@pytest.mark.parametrize("shape", list(SHAPES), ids=list(SHAPES))
def test_no_shape_is_silently_lost(shape):
    kept = R._extract_routing_falsifier(SHAPES[shape])
    assert kept.strip(), (
        f"{shape!r} produced NO falsifier. The routing ladder records that as "
        f"'ladder exhausted' with no error, which is the silent loss this "
        f"function exists to prevent."
    )


def test_the_cascade_case_recovers_the_well_formed_block():
    """One malformed closer must cost its own block and nothing else."""
    kept = R._extract_routing_falsifier(SHAPES["two blocks, first bad"])
    assert kept.strip() == BODY


def test_prose_with_no_fence_yields_nothing():
    assert R._extract_routing_falsifier("no fences here at all") == ""


def test_a_non_runnable_block_is_not_accepted():
    assert R._extract_routing_falsifier("```python\nx = 1\n```\n") == ""


class TestTheSelfFencedFalsifierStillSurvives:
    """Round 0's defect must not return while fixing round 1's."""

    def _fixtures(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tp", pathlib.Path(__file__).resolve().parent / "test_prose_acceptance_stem.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["tp"] = m
        try:
            spec.loader.exec_module(m)
        except Exception:  # noqa: BLE001
            pytest.skip("prose fixtures unavailable")
        return [x for x in m.FIXTURES if x.key in m._SELF_FENCED]

    def test_a_falsifier_carrying_its_own_fence_survives_byte_for_byte(self):
        found = self._fixtures()
        assert found, "the self-fenced fixtures have gone"
        for f in found:
            src = f.falsifier(f.doc_path)
            kept = R._extract_routing_falsifier("```python\n" + src + "\n```\n")
            assert kept.strip() == src.strip(), f"{f.key} was truncated in transport"
