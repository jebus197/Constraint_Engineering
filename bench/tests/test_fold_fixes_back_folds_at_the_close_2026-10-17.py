"""His fold-fixes-back ruling of 2026-10-11, held by execution on both halves.

HIS RULING, verbatim: "Folding fixes forward should be on by default, providing
that means folding forward at the end of an experiment and not during it so that
the target under study does not keep constantly changing. We had problems with
this in the past, where because the models were looking at a constantly moving
target, convergence effectively became impossible."

It is 1 ruling with 2 conditions and they had to be built together, timing
first. Flipping the default while the promotion still fired between rounds would
have put the moving target he ruled against onto EVERY run.

A THIRD CONDITION HE DID NOT STATE, found by measurement on 2026-10-17, without
which the other 2 are empty. Across every archived run log, 8 of 8 promotion
attempts were REJECTED -- 100.0000%, Clopper-Pearson [63.0583%, 100.0000%], the
closed form agreeing to 0.00e+00 -- all with the identical cause
`ast:unterminated string literal (detected at line 47)`. The target was
`prose_with_computable_listings.md`, a 56-line prose document whose line 47 reads
"over-read a single round's movement than one who sees only a central value." An
apostrophe inside a quoted sentence is an unterminated string to `ast.parse`,
because it was parsing English as Python. So the facility was enabled in the
simulated launcher, attempted promotions in all 3 shakedown legs, and folded
NOTHING. `bugzilla_loop.is_python_target` already existed for this decision and
the runner did not import it.

HOW PLACEMENT IS CHECKED. By parsing the runner with `ast` and walking the tree,
not by matching source text. `execute-do-not-grep` exists because a test that
asserts on source text only proves the source describes itself consistently;
walking a real parse tree is an execution over the real structure, and the
structure IS the property under test here -- "is this call inside that loop" has
no run-time observable short of a full experiment.
"""
from __future__ import annotations

import ast
import dataclasses
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def runner():
    from bench import reference_runner_v3 as m
    return m


@pytest.fixture(scope="module")
def tree():
    return ast.parse(RUNNER.read_text(encoding="utf-8"))


def _config_defaults(mod) -> dict:
    cls = next(o for o in (getattr(mod, n) for n in dir(mod))
               if dataclasses.is_dataclass(o)
               and any(f.name == "apply_fixes_back_enabled"
                       for f in dataclasses.fields(o)))
    return {f.name: f.default for f in dataclasses.fields(cls)}


# --------------------------------------------------- condition 1: on by default

def test_folding_is_on_by_default(runner):
    d = _config_defaults(runner)
    assert d["apply_fixes_back_enabled"] is True, (
        "his ruling of 2026-10-11 is that folding is ON BY DEFAULT. It was False "
        "for 6 days after he gave it.")


# ------------------------------------------- condition 2: at the close, not during

def _promote_calls_inside_round_loops(tree) -> list[int]:
    """Line numbers of `_apply_back_promote` calls lexically inside a per-round
    `for` loop, found by walking the parse tree."""
    offenders: list[int] = []

    class Walker(ast.NodeVisitor):
        def __init__(self):
            self.round_loop_depth = 0

        def visit_For(self, node: ast.For):
            is_round = (isinstance(node.target, ast.Name)
                        and node.target.id == "round_idx")
            if is_round:
                self.round_loop_depth += 1
            self.generic_visit(node)
            if is_round:
                self.round_loop_depth -= 1

        def visit_Call(self, node: ast.Call):
            fn = node.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if name == "_apply_back_promote" and self.round_loop_depth > 0:
                offenders.append(node.lineno)
            self.generic_visit(node)

    Walker().visit(tree)
    return offenders


def test_the_promotion_is_not_inside_a_per_round_loop(tree):
    offenders = _promote_calls_inside_round_loops(tree)
    assert not offenders, (
        f"`_apply_back_promote` is called inside a per-round loop at line(s) "
        f"{offenders}. That is the moving target his ruling of 2026-10-11 "
        "forbids: every round would review an artefact the previous round "
        "changed, and he recorded that this made convergence unreachable.")


def test_the_promotion_still_exists_somewhere(tree):
    """The additive standard, the other way round: a facility nothing reaches is
    not additive either. Removing the in-loop call left 0 call sites until the
    closing-stage call was added, and 0 is a defect, not a fix."""
    calls = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and (getattr(n.func, "id", None) == "_apply_back_promote")]
    assert calls, (
        "`_apply_back_promote` is defined but never called. His ruling asks for "
        "folding AT THE CLOSE, not for folding to be deleted.")


# ---------------------------------- condition 3: the gate must not parse prose

def test_the_gate_does_not_parse_prose_as_python(runner):
    """The measured cause of 8 of 8 rejections."""
    prose = ("A reader who sees only a mean will over-read a single round's "
             "movement than one who sees only a central value.")
    ok, why = runner._apply_back_gate(prose, "prose_with_computable_listings.md", "")
    assert not ok, "a prose target has no suite, so it must still be refused"
    assert "ast:" not in why, (
        f"the gate reported a Python syntax error on prose: {why!r}. This is the "
        "defect that made 8 of 8 promotions fail with "
        "`ast:unterminated string literal` on an apostrophe in English.")
    assert "non-Python" in why or "falsifier" in why, (
        f"the refusal must SAY WHY so a reader is not told the models wrote "
        f"broken code; got {why!r}")


def test_the_gate_still_rejects_broken_python(runner):
    """Anti-vacuity: making the check conditional must not disable it."""
    ok, why = runner._apply_back_gate("def f(:\n", "bench/thing.py", "")
    assert not ok and why.startswith("ast:"), (
        f"a Python target with a syntax error must still be refused by the "
        f"parser; got ({ok}, {why!r})")


def test_the_gate_accepts_valid_python_to_the_suite_stage(runner):
    ok, why = runner._apply_back_gate("x = 1\n", "bench/thing.py", "")
    assert not ok, "with no test_cmd there is nothing to gate on, so refuse"
    assert "test_cmd" in why, (
        f"valid Python must reach the SUITE stage, not be refused earlier; "
        f"got {why!r}")


def test_the_runner_imports_the_target_type_predicate(runner):
    assert hasattr(runner, "is_python_target"), (
        "the runner must use `bugzilla_loop.is_python_target` rather than "
        "deciding target type itself; it existed for this and was unimported "
        "while 8 of 8 promotions failed")
    assert runner.is_python_target("prose_with_computable_listings.md") is False
    assert runner.is_python_target("bench/reference_runner_v3.py") is True
