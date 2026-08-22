"""COMMISSIONING TESTS for the build experiment's acceptance gate.

The instrument inventory (2026-08-22) defines COMMISSIONED as: a test exists that
exercises the component with a KNOWN-GOOD and a KNOWN-BAD input and asserts it
answers differently. Of 34 instruments, the falsifier gate was found NOT
commissioned -- it accepts `print('FALSIFIED')` as a confirmation -- and that
single missing check is why 131 of 263 archived falsifiers keep firing after the
defect they accuse has been repaired.

This gate exists to replace that one. Shipping it without commissioning it would
repeat the exact failure it was built to end, so every branch below is driven with
an input constructed to trigger it.

Known-good: a patch whose test fails at the parent and passes with the patch.
Known-bad:  a test that always passes; a test that always fails; a patch that does
            not apply; a patch with no test at all; and a patch that passes its own
            test while breaking the suite.
"""
from __future__ import annotations

import pytest

from bench import build_acceptance as BA

# A harmless, stable target. The patch appends a function; the test imports it.
TARGET = "bench/dm/_types.py"
MARKER = "\n\ndef _commissioning_probe() -> int:\n    return 42\n"


def _patch(search: str, replace: str, path: str = TARGET) -> str:
    return f"<<<< SEARCH {path}\n{search}\n==== REPLACE\n{replace}\n>>>>\n"


def _test_block(src: str, path: str = "bench/tests/test_commissioning_probe_tmp.py") -> str:
    return f"TEST_FILE: {path}\n\n```python\n{src}\n```\n"


@pytest.fixture(scope="module")
def anchor() -> str:
    """The last line of the target, used as a SEARCH block that must match."""
    txt = (BA.REPO / TARGET).read_text(encoding="utf-8")
    lines = [ln for ln in txt.splitlines() if ln.strip()]
    return lines[-1]


# A small COMMITTED test file. It must be committed: the worktree is checked out
# at the parent, so naming an uncommitted file makes the suite step fail for a
# reason that has nothing to do with the patch. The first draft of this fixture
# did exactly that and the gate correctly reported REJECTED_SUITE_WENT_RED --
# a harness bug that rendered as an instrument failure, caught by commissioning.
FAST_SUITE = ["python3", "-m", "pytest", "bench/tests/test_diversity_metric.py",
              "-q", "--netguard-strict"]


def test_known_good_is_accepted(anchor):
    """A real patch with a test that fails before and passes after MUST pass."""
    resp = _patch(anchor, anchor + MARKER) + _test_block(
        "from bench.dm._types import _commissioning_probe\n"
        "def test_probe():\n    assert _commissioning_probe() == 42\n")
    v = BA.evaluate(resp, suite_cmd=FAST_SUITE)
    assert v.outcome == BA.ACCEPTED, f"{v.outcome}: {v.detail}"
    assert TARGET in v.files_touched


def test_a_test_that_always_passes_is_rejected(anchor):
    """The one-sided failure that broke the falsifier gate, in the other direction.

    A test asserting True proves nothing about any defect. It must be refused at
    step 1 -- BEFORE the patch is even applied.
    """
    resp = _patch(anchor, anchor + MARKER) + _test_block(
        "def test_vacuous():\n    assert True\n")
    v = BA.evaluate(resp, suite_cmd=FAST_SUITE)
    assert v.outcome == BA.REJ_TEST_PASSED_BEFORE, f"{v.outcome}: {v.detail}"


def test_a_test_that_always_fails_is_rejected(anchor):
    """The falsifier gate's actual defect: `assert False` looks like a demonstration.

    Here it fails at the parent (step 1 passes) and then still fails with the patch,
    so step 2 refuses it. This is the branch that makes the gate two-sided.
    """
    resp = _patch(anchor, anchor + MARKER) + _test_block(
        "def test_always_fails():\n    assert False, 'FALSIFIED'\n")
    v = BA.evaluate(resp, suite_cmd=FAST_SUITE)
    assert v.outcome == BA.REJ_TEST_FAILED_AFTER, f"{v.outcome}: {v.detail}"


def test_a_patch_that_does_not_apply_is_rejected():
    resp = _patch("this text is not in the file anywhere at all",
                  "replacement") + _test_block(
        "from bench.dm._types import _commissioning_probe\n"
        "def test_probe():\n    assert _commissioning_probe() == 42\n")
    v = BA.evaluate(resp, suite_cmd=FAST_SUITE)
    assert v.outcome == BA.REJ_PATCH_DID_NOT_APPLY, f"{v.outcome}: {v.detail}"


def test_a_patch_with_no_test_is_rejected(anchor):
    v = BA.evaluate(_patch(anchor, anchor + MARKER), suite_cmd=FAST_SUITE)
    assert v.outcome == BA.REJ_NO_TEST


def test_prose_with_no_patch_is_rejected():
    v = BA.evaluate("I think the right fix here is to change the threshold.",
                    suite_cmd=FAST_SUITE)
    assert v.outcome == BA.REJ_NO_PATCH


def test_a_patch_that_breaks_the_suite_is_rejected(anchor):
    """Step 3. The patch makes its own test pass and breaks something else.

    The 'suite' here is a command constructed to fail, which is the only way to
    drive this branch deterministically without shipping a real regression.
    """
    resp = _patch(anchor, anchor + MARKER) + _test_block(
        "from bench.dm._types import _commissioning_probe\n"
        "def test_probe():\n    assert _commissioning_probe() == 42\n")
    cmd = ["python3", "-c",
           "print('FAILED bench/tests/test_regressed.py::test_z'); import sys; sys.exit(1)"]
    BA._BASELINE[("HEAD", tuple(cmd))] = frozenset()   # parent is green for this cmd
    v = BA.evaluate(resp, parent="HEAD", suite_cmd=cmd)
    assert v.outcome == BA.REJ_SUITE_WENT_RED, f"{v.outcome}: {v.detail}"
    assert "test_regressed" in v.detail


def test_step_three_compares_against_the_parent_rather_than_assuming_green():
    """The defect that stopped the run on 2026-08-22, pinned so it cannot return.

    A pre-existing failure at the parent must NOT be blamed on the patch. Driven
    with a suite command that fails identically on both sides: if the gate compared
    against an assumption of green it would reject; comparing against the measured
    parent, it must accept.
    """
    txt = (BA.REPO / TARGET).read_text(encoding="utf-8")
    anchor_line = [ln for ln in txt.splitlines() if ln.strip()][-1]
    resp = _patch(anchor_line, anchor_line + MARKER) + _test_block(
        "from bench.dm._types import _commissioning_probe\n"
        "def test_probe():\n    assert _commissioning_probe() == 42\n")
    # A "suite" with one failure that exists on both sides, printed in pytest's
    # own FAILED format so the gate's parser sees it.
    always_red = ["python3", "-c",
                  "print('FAILED bench/tests/test_pre_existing.py::test_x'); "
                  "import sys; sys.exit(1)"]
    v = BA.evaluate(resp, suite_cmd=always_red)
    assert v.outcome == BA.ACCEPTED, (
        f"a failure present at the parent was blamed on the patch: {v.outcome} {v.detail}")


def test_a_new_suite_failure_is_still_rejected(anchor):
    """The other side of the same check: a failure the parent does NOT have.

    The baseline is computed with one command and the patched run with another that
    reports a DIFFERENT failing node-id, so the difference is a genuine regression.
    """
    resp = _patch(anchor, anchor + MARKER) + _test_block(
        "from bench.dm._types import _commissioning_probe\n"
        "def test_probe():\n    assert _commissioning_probe() == 42\n")
    key_cmd = ["python3", "-c",
               "print('FAILED bench/tests/test_brand_new.py::test_y'); "
               "import sys; sys.exit(1)"]
    # evaluate() keys the cache on the parent string IT IS GIVEN, so prime it with
    # the same literal. Priming under the resolved SHA was the first attempt and it
    # missed, causing a real 200s suite run against the wrong baseline.
    BA._BASELINE[("HEAD", tuple(key_cmd))] = frozenset()      # parent is green
    v = BA.evaluate(resp, parent="HEAD", suite_cmd=key_cmd)
    assert v.outcome == BA.REJ_SUITE_WENT_RED, f"{v.outcome}: {v.detail}"
    assert "test_brand_new" in v.detail


def test_no_model_vote_appears_anywhere_in_the_gate():
    """The gate must contain no path where agreement decides anything.

    Six model-vote paths to MERGED were found in this codebase on 2026-08-19. This
    asserts the replacement did not reintroduce one.
    """
    import ast, io, tokenize
    src = (BA.REPO / "bench/build_acceptance.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    # Blank every docstring, then strip comments with the tokenizer. Line-scanning
    # for a triple quote (the first attempt) missed the module docstring, which
    # discusses model votes precisely because the gate must not contain one.
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            d = ast.get_docstring(node, clean=False)
            if d:
                docstrings.add(d)
    body = src
    for d in docstrings:
        body = body.replace(d, "")
    code = "".join(
        tok.string if tok.type != tokenize.COMMENT else ""
        for tok in tokenize.generate_tokens(io.StringIO(body).readline))
    for banned in ("vote", "majority", "consensus", "quorum"):
        assert banned not in code.lower(), (
            f"{banned!r} appears in the gate's EXECUTABLE code")
