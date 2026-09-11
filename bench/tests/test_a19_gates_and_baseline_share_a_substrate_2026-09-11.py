"""Panel round 13: the gate that could not fail moved from e4 to e3, in the fix for e4.

BOTH SEATS FOUND THIS INDEPENDENTLY, in separate sandboxes, and it is mine.

Task A19 handed `_gateable_source` to `_run_effect_ruff` and `_run_effect_bandit`
so they would score the extracted Python rather than the English. It did NOT hand
it to `_capture_baseline`. So e3 subtracted two numbers taken over DIFFERENT
TEXTS:

    delta = max(0, violations(LISTINGS after the fix)
                   - violations(WHOLE PROSE before the fix))

Measured on `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`: baseline **311**, gate
**4**. The subtrahend is enormous and the minuend tiny, so the delta is 0 for
every reachable fix. One seat injected SEVEN real ruff diagnostics into a listing
and e3 scored **1.0**.

THAT IS VERBATIM THE PROPERTY THE A19 DOCSTRING CONDEMNS IN e4 -- "structurally
incapable of failing, which is worse than unavailable, because an unavailable
gate is excluded from the weighted mean and a gate that always passes drags it
up" -- reproduced in e3 by the commit that removed it from e4. Repairing one half
of a comparison and not the other is the same shape as the 2026-08-01 hard-gate
repair that left the effect gates reading prose for 41 days, and it recurred
within a day of that sentence being written into the entry.

IT RAN THE OTHER WAY TOO. Bandit could not parse the prose, so its baseline was a
false 0 HIGH / 0 MEDIUM, and a HIGH ALREADY PRESENT in a listing counted as NEW
-- a correct fix convicted for a pre-existing defect.

AND THE FENCE PATTERN MATCHED ONE SHAPE OF MARKDOWN. Verified across 7 real
shapes before the repair: `~~~`, CRLF and attribute-carrying fences extracted
NOTHING; indented and blockquoted fences extracted their markdown scaffolding, so
`ast.parse` raised and A = g1*g2 = 0 -- EVERY fix to such a document REJECTED. A
REJECT IS A CLAIM AND NO_SCORE IS AN ABSTENTION, so turning the flag on would
have made the instrument worse rather than silent, on the commonest shape in a
design note: a listing inside a numbered list.
"""
from __future__ import annotations

import ast
import importlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bench.reference_runner_v3 as R  # noqa: E402

SPEC = ROOT / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"


class TestTheBaselineAndTheGateMeasureTheSameText:
    def test_the_baseline_is_taken_over_the_listings(self):
        if not SPEC.is_file():
            pytest.skip("the measured file is not in this checkout")
        md = SPEC.read_text(encoding="utf-8", errors="replace")
        b = R._capture_baseline(md, source_path=str(SPEC))
        extracted, _why = R._gateable_source(md, str(SPEC))
        b2 = R._capture_baseline(extracted, source_path="x.py")
        assert b["ruff_violations"] == b2["ruff_violations"], (
            f"baseline over the document is {b['ruff_violations']} and over the "
            f"listings {b2['ruff_violations']}; e3 would subtract one from the "
            f"other and could never report a regression")

    def test_e3_can_now_fail_on_a_prose_target(self):
        """THE CONTROL THAT MATTERS. Adding bad code to a listing must score."""
        if not SPEC.is_file():
            pytest.skip("the measured file is not in this checkout")
        md = SPEC.read_text(encoding="utf-8", errors="replace")
        base = R._capture_baseline(md, source_path=str(SPEC))
        clean, _d = R._run_effect_ruff(md, base["ruff_violations"],
                                       source_path=str(SPEC))
        worse_src = md.replace("```python\n", "```python\nimport os,sys\nx=1;y=2\n", 1)
        worse, detail = R._run_effect_ruff(worse_src, base["ruff_violations"],
                                           source_path=str(SPEC))
        assert clean == 1.0, clean
        assert worse is not None and worse < 1.0, (
            f"e3 still cannot fail on a prose target: {worse} {detail}")

    def test_a_target_with_no_code_gets_no_baseline(self):
        """NOT a false zero. An unavailable gate is excluded from the weighted
        mean; a gate handed 0 is included and always passes."""
        b = R._capture_baseline("# note\n\nprose only, no listing.\n",
                                source_path="notes/x.md")
        assert b["ruff_violations"] is None and b["bandit_findings"] is None, b

    def test_a_python_target_is_untouched(self):
        py = (ROOT / "bench" / "repo_paths.py").read_text(encoding="utf-8")
        direct = R._capture_baseline(py, source_path="bench/repo_paths.py")
        assert direct["ruff_violations"] is not None


class TestTheFenceMatchesTheShapesRealNotesUse:
    SHAPES = {
        "plain": "# n\n\n```python\nx = 1\n```\n",
        "tilde": "# n\n\n~~~python\nx = 1\n~~~\n",
        "attrs": '# n\n\n```python title="a"\nx = 1\n```\n',
        "crlf": "# n\r\n\r\n```python\r\nx = 1\r\n```\r\n",
        "indented": "1. step\n\n    ```python\n    x = 1\n    ```\n",
        "blockquote": "> ```python\n> x = 1\n> ```\n",
    }

    @pytest.mark.parametrize("name", sorted(SHAPES))
    def test_it_extracts_parseable_python(self, name):
        src, why = R._gateable_source(self.SHAPES[name], "notes/x.md")
        assert src is not None, f"{name} extracted nothing: {why}"
        ast.parse(src)          # must not raise

    def test_the_listings_own_indentation_survives(self):
        """THE DEDENT MUST NOT FLATTEN PYTHON. Stripping the markdown indent and
        stripping the function body's indent are different operations."""
        md = "1. step\n\n    ```python\n    def f():\n        return 1\n    ```\n"
        src, _why = R._gateable_source(md, "notes/x.md")
        ast.parse(src)
        assert "    return 1" in src, src

    def test_pycon_still_abstains(self):
        """DELIBERATE. A doctest block interleaves source with output, and
        abstaining is right where convicting is not."""
        src, why = R._gateable_source("# n\n\n```pycon\n>>> x = 1\n```\n",
                                      "notes/x.md")
        assert src is None, (src, why)

    def test_a_document_with_no_fence_still_abstains(self):
        src, _why = R._gateable_source("# n\n\njust prose.\n", "notes/x.md")
        assert src is None
