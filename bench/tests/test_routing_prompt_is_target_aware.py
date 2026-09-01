"""The routing ladder must be told what it is looking at.

WHY THIS FILE EXISTS
--------------------
The routing ladder is the ONLY absorber between the falsifier gate and the HIL
queue. Until 2026-08-01 its prompt was code-only: the system message told the
model to ``from bench.cdsfl_registry import <mod>``, and the finding dict passed
to it carried id / description / source_model / severity and nothing else. No
target path. No target text.

So a model asked to demonstrate a defect in "Listing A" of a markdown document
was told to import a module that does not exist, and was never told where the
document was. Both rungs failed, and the runner recorded
``hil_reason = "routing ladder exhausted (no model produced a runnable test)"``.
That sentence was false. No model was ever given the target.

MEASURED, from the run archives, before the fix:
  * Exp 48 (chemistry) + Exp 49 (engineering) — prose, NO fenced listings, zero
    listing-referencing findings: routing resolved 16/37 and 25/38. **41 for 41.**
  * Exp 53 control — prose WITH 7 fenced listings, 23 and 14 listing-referencing
    findings: routing resolved **0 for 25**; 25 findings locked irreducible
    against a bound of 2; the run halted at round 3 of 16.

A 14-line falsifier that merely opens the control document BY PATH, extracts the
TokenBucket listing and calls ``allow(-10)`` returns CONFIRMED from the runner's
own ``reverify_falsifier`` — for a finding this ladder had locked as impossible.

The defect was found by an offline falsification pass roughly two months after
the ladder shipped, and it was on no queue. Neither prompt had a single test.
That is what this file is for.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import (  # noqa: E402
    TARGET_KIND_PROSE,
    TARGET_KIND_PYTHON,
    _routing_resolve_prompt,
    _routing_sentinels,
    _routing_system,
)

FINDING = {
    "id": "C0031",
    "description": (
        "Listing A's TokenBucket.allow accepts a negative cost, which withdraws "
        "from the bucket rather than adding to it."
    ),
    "source_model": "deepseek",
    "severity": 0.72,
}

DOC = """# SW-21-REF-04 — Rate limiter design reference

## 2. Reference implementations

```python
class TokenBucket:
    def allow(self, cost=1.0):
        self.tokens -= cost
        return self.tokens >= 0
```

The bucket refills at 0.29 mm per tick, which is a typo retained deliberately.
"""


class TestTheProseBranchNamesTheTarget:
    """The one property whose absence produced 25 false 'irreducible' locks."""

    def test_the_document_path_reaches_the_model(self):
        prompt = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        assert "SW-21-REF-04.md" in prompt, (
            "the model cannot open a document it is never told the name of — "
            "this is the exact omission that locked 25 findings as irreducible")

    def test_the_document_text_reaches_the_model(self):
        prompt = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        assert "class TokenBucket" in prompt
        assert "self.tokens -= cost" in prompt, (
            "the listing the finding is ABOUT must be in the prompt")

    def test_it_is_told_to_open_by_path_not_to_import(self):
        prompt = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        assert "open(" in prompt
        low = prompt.lower()
        assert "import the real module" not in low, (
            "there is no module to import; instructing an import is what made "
            "every rung fail")

    def test_the_system_message_does_not_send_it_to_the_registry(self):
        sysmsg = _routing_system(TARGET_KIND_PROSE)
        assert "cdsfl_registry" not in sysmsg
        assert "PROSE DOCUMENT" in sysmsg
        assert "no module to import" in sysmsg.lower()

    def test_it_is_told_listings_can_be_extracted_and_run(self):
        prompt = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        low = prompt.lower()
        assert "extract" in low and "listing" in low, (
            "a claim about a printed listing is resolved by extracting and "
            "exercising it — the 14-line falsifier that settled C0031 did "
            "exactly that")


class TestTheDelimiterCannotBeEndedByTheDocument:
    """A markdown target carries its own ``` fences, so a fence cannot delimit it."""

    def test_the_document_is_sentinel_delimited_not_fenced(self):
        prompt = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        begin, end = _routing_sentinels(DOC)
        assert begin in prompt and end in prompt
        assert prompt.index(begin) < prompt.index("class TokenBucket") < prompt.index(end)

    def test_the_sentinel_never_occurs_in_the_source(self):
        begin, end = _routing_sentinels(DOC)
        assert begin not in DOC and end not in DOC

    def test_a_document_quoting_the_sentinel_still_gets_a_clean_one(self):
        b0, _ = _routing_sentinels("")
        hostile = f"the sentinel is {b0} and also {b0} again"
        begin, end = _routing_sentinels(hostile)
        assert begin not in hostile and end not in hostile

    def test_the_prompt_warns_against_a_nested_fence(self):
        # Measured on the fixtures: 2 of 5 prose falsifiers carried their own
        # fence and were truncated in transport, returning ERROR. ERROR on a
        # critical sets escalated=True and feeds the A4 convergence block.
        for kind in (TARGET_KIND_PROSE, TARGET_KIND_PYTHON):
            prompt = _routing_resolve_prompt(FINDING, "t.md", DOC, kind)
            assert "nested" in prompt.lower()


class TestThePythonBranchIsUnchanged:
    """A code target must behave exactly as it did. This change is prose-only."""

    def test_it_still_says_import_the_real_module(self):
        prompt = _routing_resolve_prompt(
            FINDING, "bench/cdsfl_registry/composer.py", "x = 1", TARGET_KIND_PYTHON)
        assert "imports the REAL module" in prompt
        assert "inspect" in prompt

    def test_the_python_system_message_is_the_original(self):
        sysmsg = _routing_system(TARGET_KIND_PYTHON)
        assert "cdsfl_registry" in sysmsg
        assert "inspect" in sysmsg

    def test_the_python_branch_does_not_paste_the_module(self):
        # The code path reads source via inspect inside the tool loop; pasting
        # a 60K module into every rung of every ladder would be a real cost.
        prompt = _routing_resolve_prompt(
            FINDING, "m.py", "SECRET_MODULE_BODY = 1", TARGET_KIND_PYTHON)
        assert "SECRET_MODULE_BODY" not in prompt

    def test_the_default_call_still_produces_the_code_prompt(self):
        # Back-compat: an un-updated caller must get the old prompt, not a broken one.
        assert "imports the REAL module" in _routing_resolve_prompt(FINDING)


class TestTheReasonStringSaysOnlyWhatWasObserved:
    """`no model produced a runnable test` was false on every prose target."""

    def test_the_runner_no_longer_asserts_models_were_given_the_target(self):
        # Checked against STRING CONSTANTS, not raw source: the comment above the
        # repair quotes the old phrasing deliberately, and a raw substring test
        # would fire on the explanation rather than on the behaviour. (Written
        # first as a raw substring test, which duly failed on its own comment.)
        import ast
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        tree = ast.parse(src)
        offenders = [
            n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and "no model produced a runnable test" in n.value
        ]
        assert not offenders, (
            "that phrasing claims the models were asked and failed. Until "
            f"2026-08-01 they were never given the target at all. Found in: {offenders}")
        assert "rung(s) reached a model" in src


class TestTheTwoPromptsAgree:
    """The sweep prompt was made prose-aware and this one was not. That asymmetry
    WAS the defect, so it is now pinned: both must branch on target kind."""

    def test_both_prompts_branch_on_target_kind(self):
        from bench.reference_runner_v3 import _sweep_prompt
        residuals = {"C0031": dict(FINDING, status="CONFIRMED")}
        sweep = _sweep_prompt(residuals, "SW-21-REF-04.md", DOC)
        route = _routing_resolve_prompt(
            FINDING, "SW-21-REF-04.md", DOC, TARGET_KIND_PROSE)
        for name, prompt in (("sweep", sweep), ("routing", route)):
            assert "SW-21-REF-04.md" in prompt, f"{name} lost the target path"
            assert "class TokenBucket" in prompt, f"{name} lost the target text"
            assert "PROSE DOCUMENT" in prompt, f"{name} lost the prose label"
