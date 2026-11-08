"""The run state records a PRE-RUN description of its target. B84 field 1.

HIS RULING, 2026-11-08: *"I accept your recommendation. stm"*, against the
recommendation to record the class of missing reference points.

THE DEFECT, MEASURED. Across 65 archived run directories carrying a structured
state, 59 distinct after removing identical twins, the state holds 21 keys and
**0 of them describe the target before the run began**. Every key is a
per-round history or the finding registry. A difficulty estimator therefore has
nothing to learn from except OUTCOMES of the run itself, and rounds against
findings correlate at Pearson r = 0.836787, p = 1.533183e-16 -- so an estimator
fitted on them returns a number that rises with however many rounds a run
happened to take. A round counter wearing the name of a confidence measure,
which is the failure his own words named when he set the priority.

WHY ONLY 1 OF THE ENTRY'S 4 FIELDS IS BUILT HERE, STATED RATHER THAN QUIETLY
NARROWED. This one costs nothing to run: 1 read of a file, on the first
checkpoint only. The other 3 each need something this build cannot supply --
a baseline pass rate needs an extra suite execution, and the severity class and
confidence each need a SOURCE that does not exist yet, since no field carries a
HARD/SOFT classification and B87's narrowing only made a tool-derived
confidence admissible rather than available. His machine is a fixed resource,
and spending an execution budget on it is his call, not a detail of a field.

THE LOAD-BEARING PROPERTY IS THE CACHE, AND IT IS THE ONE WORTH TESTING.
`_apply_back_gate` can fold a CLOSED fix back into the working copy of the
target, so the file on disk is NOT the pre-run file at a later round. A reading
taken at round 7 and stored under a pre-run name would be a post-fix
measurement wearing the wrong label -- worse than no field at all, because an
absent value is visible and a mislabelled one is not.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench/reference_runner_v3.py"


@pytest.fixture(scope="module")
def describe():
    """`pre_run_target_description`, compiled ALONE.

    Importing the runner executes a 20,000-line module for 1 pure function.
    The function and the module constant it needs are compiled into a fresh
    namespace instead, so it is genuinely EXECUTED rather than inspected.
    """
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    seg = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and \
                node.name == "pre_run_target_description":
            seg = ast.get_source_segment(src, node)
            break
    if seg is None:
        pytest.fail("the runner defines no pre_run_target_description, so his "
                    "ruling produced nothing")
    ns = {"REPO_ROOT": REPO, "pathlib": pathlib,
          "_PRE_RUN_TARGET": {}}
    exec(compile(seg, "<pre_run_target>", "exec"), ns)      # noqa: S102
    return ns["pre_run_target_description"], ns


def _cfg(article="", kind=""):
    return types.SimpleNamespace(test_article=article, target_kind=kind)


def test_it_describes_a_real_file(describe, tmp_path):
    fn, _ = describe
    rel = "bench/reference_runner_v3.py"
    out = fn(_cfg(rel, "software"), tmp_path / "a.json")
    assert out["path"] == rel
    assert out["kind"] == "software"
    assert out["bytes"] and out["bytes"] > 100_000, out
    assert out["lines"] and out["lines"] > 1_000, out
    assert out["sha256"] and len(out["sha256"]) == 64, out
    assert out["why_absent"] == "", out


def test_the_description_is_captured_once_and_never_overwritten(describe, tmp_path):
    """THE PROPERTY THAT MATTERS. A fold-back must not relabel the target.

    The same checkpoint path is asked twice with DIFFERENT files behind it. The
    second answer must be the first, because a later round re-reading the file
    would store a post-fix reading under a pre-run name.
    """
    fn, _ = describe
    small = tmp_path / "t.py"
    small.write_text("x = 1\n")
    ckpt = tmp_path / "runner_state.json"
    first = fn(_cfg(str(small)), ckpt)
    assert first["bytes"] == 6, first
    small.write_text("x = 1\n" + "# a fix was folded back\n" * 50)
    second = fn(_cfg(str(small)), ckpt)
    assert second == first, (
        "the description changed after the target file changed, so a "
        "post-fold-back reading is being stored under a pre-run name")
    assert second["bytes"] == 6


def test_a_different_run_gets_its_own_description(describe, tmp_path):
    """ANTI-VACUITY for the cache. A cache keyed on nothing would return the
    first run's target for every later run, which is worse than no cache."""
    fn, _ = describe
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("x = 1\n")
    b.write_text("y = 2\n" * 10)
    one = fn(_cfg(str(a)), tmp_path / "run1.json")
    two = fn(_cfg(str(b)), tmp_path / "run2.json")
    assert one["bytes"] != two["bytes"], (
        f"2 different runs with different targets got the same description: "
        f"{one} against {two}")


def test_an_unreadable_target_is_a_NAMED_failure_not_a_zero(describe, tmp_path):
    """A 0 size would be read as a measurement. A reason cannot be."""
    fn, _ = describe
    out = fn(_cfg(str(tmp_path / "does-not-exist.py")), tmp_path / "x.json")
    assert out["bytes"] is None, "an unreadable target reported a size"
    assert out["why_absent"], "it failed silently"
    assert "Error" in out["why_absent"] or "FileNotFound" in out["why_absent"], \
        out["why_absent"]


def test_an_empty_target_says_so_rather_than_omitting_the_key(describe, tmp_path):
    """An omitted key cannot be told from a key nobody wrote."""
    fn, _ = describe
    out = fn(_cfg(""), tmp_path / "y.json")
    assert out["path"] == ""
    assert out["why_absent"], "a run naming no target recorded no reason"
    assert "test_article" in out["why_absent"]


def test_the_checkpoint_actually_writes_it():
    """AN ADDITION NOTHING REACHES IS NOT ADDITIVE."""
    src = RUNNER.read_text(encoding="utf-8")
    assert '"pre_run_target": pre_run_target_description(' in src, (
        "the checkpoint does not write pre_run_target, so the field he ruled "
        "on reaches no archived run")
    # and it must be inside the serialised dict, not somewhere harmless
    i = src.index('"pre_run_target": pre_run_target_description(')
    head = src[:i]
    assert head.rfind("_ckpt_data = json.dumps({") > head.rfind("def "), (
        "the write is not inside the checkpoint's own json.dumps call")
