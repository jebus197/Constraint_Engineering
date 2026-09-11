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


FRAGMENT = "# n\n\nprose\n\n```python\n    return 0\n```\n"
GOOD_LISTING = "# n\n\nprose\n\n```python\ndef f():\n    return 0\n```\n"


class TestAnAbsoluteGateDoesNotConvictAFixForAPreExistingFault:
    """g1 and g2 are ABSOLUTE where e2, e3 and e4 are all DELTAS.

    On a Python module that is harmless -- the repository's own source parses.
    On a prose target a listing is routinely an ILLUSTRATIVE FRAGMENT that never
    parsed on its own and never will, so A = g1*g2 = 0 and every fix is
    REJECTED for a failure that is NOT ATTRIBUTABLE TO IT.
    """

    def test_a_correct_fix_on_an_unparseable_fragment_is_not_rejected(self):
        base = R._capture_baseline(FRAGMENT, source_path="notes/x.md")
        r = R.compute_sk(
            "<<<< SEARCH\n    return 0\n====\n    return 1\n>>>> REPLACE\n",
            FRAGMENT, "notes/x.md", baseline=base, score_prose_listings=True)
        assert r.tristate != "REJECTED", (r.tristate, r.gate_details)

    def test_a_fix_that_breaks_working_code_is_still_rejected(self):
        """THE GUARD IS NOT A LICENCE. If this stops firing, the abstention has
        become a blanket pass and the hard gates are gone."""
        base = R._capture_baseline(GOOD_LISTING, source_path="notes/x.md")
        r = R.compute_sk(
            "<<<< SEARCH\ndef f():\n    return 0\n====\n"
            "def f():\n    return (((\n>>>> REPLACE\n",
            GOOD_LISTING, "notes/x.md", baseline=base, score_prose_listings=True)
        assert r.tristate == "REJECTED", (r.tristate, r.gate_details)

    def test_the_baseline_check_uses_the_gate_s_own_compiler(self):
        """`ast.parse("return 0")` SUCCEEDS while `compile(...)` raises. A
        baseline tested with one and a gate run with the other is 2 expressions
        of one question with no comparator -- inside the guard written to stop
        exactly that."""
        assert R._baseline_code_is_parseable(FRAGMENT, "notes/x.md") is True
        assert R._baseline_code_is_parseable(
            FRAGMENT, "notes/x.md",
            compiler=lambda t: compile(t, "x", "exec")) is False

    def test_absolute_behaviour_is_unchanged_without_an_original(self):
        """No existing caller changes: the default reproduces the old gate."""
        bad = "# n\n\n```python\ndef f():\n    return (((\n```\n"
        assert R._run_hard_gate_ast(bad, "notes/x.md")[0] == 0
        assert R._run_hard_gate_compile(bad, "notes/x.md")[0] == 0


class TestAFixThatDeletesEveryListingHasFailed:
    """It has not become unscoreable. The target was admitted to the scoring
    branch BECAUSE it carried reducible code; removing all of it is a removal
    with no measured replacement."""

    def test_deleting_the_listing_is_rejected_not_escalated(self):
        doc = "# n\n\nprose\n\n```python\nx = 1\n```\n\nmore prose\n"
        base = R._capture_baseline(doc, source_path="notes/x.md")
        r = R.compute_sk(
            "<<<< SEARCH\n```python\nx = 1\n```\n====\n(removed)\n>>>> REPLACE\n",
            doc, "notes/x.md", baseline=base, score_prose_listings=True)
        assert r.tristate == "REJECTED", (r.tristate, r.gate_details)
        assert r.gate_details.get("g0_code_retained", {}).get("score") == 0

    def test_an_ordinary_fix_keeps_the_listing_and_passes_g0(self):
        doc = "# n\n\nprose\n\n```python\nx = 1\n```\n\nmore prose\n"
        base = R._capture_baseline(doc, source_path="notes/x.md")
        r = R.compute_sk("<<<< SEARCH\nx = 1\n====\nx = 2\n>>>> REPLACE\n",
                         doc, "notes/x.md", baseline=base,
                         score_prose_listings=True)
        assert r.gate_details.get("g0_code_retained", {}).get("score") == 1

    def test_g0_does_not_run_with_the_flag_off(self):
        """The gate belongs to the prose-scoring path and must not appear on a
        Python target or on an unflagged run."""
        doc = "# n\n\n```python\nx = 1\n```\n"
        base = R._capture_baseline(doc, source_path="notes/x.md")
        r = R.compute_sk("<<<< SEARCH\nx = 1\n====\nx = 2\n>>>> REPLACE\n",
                         doc, "notes/x.md", baseline=base)
        assert "g0_code_retained" not in (r.gate_details or {})
