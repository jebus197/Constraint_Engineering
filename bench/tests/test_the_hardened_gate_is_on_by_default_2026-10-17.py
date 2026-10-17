#!/usr/bin/env python3
"""The hardened convergence gate is on by default, in every runner.

HIS RULING, 2026-10-05: *"Then this should also be on, by default in all our
runners."* It stayed off for 12 days. `hardened_gate_enabled` defaulted to
False, 4 archived experiment configs set it true, the remainder set it false
explicitly, and the only place that turned it on unconditionally was
`bench/tools/run_simulated_experiment.py` -- so it was on in the SIMULATED
runner and off everywhere else, which is the opposite of what he ruled.

WHY THE DEFAULT IS SINGLE-SOURCED. The rule previously lived in 4 places: the
dataclass field and 3 `getattr(cfg, "hardened_gate_enabled", False)` fallbacks.
A fallback is the path a stub config takes, so leaving them at False would have
let a config object without the field keep the superseded behaviour -- silently,
which is the `silent defaulting` class this project records. `HARDENED_GATE_DEFAULT`
is now the only expression of it, and these tests fail if a second one appears.

WHAT THE GATE DOES, stated because turning it on is a behaviour change and not
merely a threshold move. It becomes the CONJUNCTION of a sustained,
leave-one-round-out-robust critical gamma and N consecutive settled rounds
carrying no novel critical, computed on the settled post-reconciliation
registry; the legacy gamma-alt path is bypassed and all-novelty gamma is kept as
a diagnostic. The evidence that it converges rather than stalling is the 3
shakedown legs, which all ran with it ON and converged at rounds 3, 4 and 4,
each reaching 1.000 on the decay curve.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _cfg(**kw):
    return R.RunnerConfig(experiment_name="t", models=["A"],
                          test_article="bench/dm/_memory.py", **kw)


def test_the_constant_is_true():
    assert R.HARDENED_GATE_DEFAULT is True, (
        "his ruling of 2026-10-05 is that the hardened gate is on by default in "
        "all runners. Turning it off again is a behaviour change needing his "
        "ruling, not a default edit.")


def test_a_config_that_names_nothing_gets_the_gate_on():
    """The ordinary case: a runner started without touching the flag."""
    assert _cfg().hardened_gate_enabled is True


def test_an_explicit_false_is_still_honoured():
    """A per-experiment choice must still be possible, or this is not a default.

    His ruling sets the DEFAULT. An experiment that deliberately runs the legacy
    gate -- to reproduce an archived run, for instance -- must still be able to,
    or replay becomes impossible and that is a cost he did not agree to.
    """
    assert _cfg(hardened_gate_enabled=False).hardened_gate_enabled is False


def test_the_default_has_exactly_one_expression():
    """A second literal default is how a stub config diverges silently.

    Parsed rather than grepped: every `getattr` on this field in the runner must
    take its fallback from the constant, and the dataclass field must too.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    literal_fallbacks = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == "getattr"
                and len(node.args) == 3
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == "hardened_gate_enabled"):
            third = node.args[2]
            if not (isinstance(third, ast.Name)
                    and third.id == "HARDENED_GATE_DEFAULT"):
                literal_fallbacks.append(ast.dump(third)[:60])
    assert not literal_fallbacks, (
        f"{len(literal_fallbacks)} getattr fallback(s) for this field do not "
        f"read HARDENED_GATE_DEFAULT: {literal_fallbacks}. A second expression "
        f"of one default is how a stub config silently keeps the superseded "
        f"behaviour.")


def test_the_dataclass_field_reads_the_constant():
    """PARSED, because for a bool the runtime check is vacuous.

    The first form compared `fields[...].default is R.HARDENED_GATE_DEFAULT`.
    Both are `True`, and `True` is a singleton, so the comparison held even with
    the field written as a bare literal -- mutation testing showed replacing it
    with `True` left all 7 tests green. Whether a rule has ONE expression is a
    property of the source and can only be checked there; the BEHAVIOUR is
    covered separately by the tests above, so both forms are present rather than
    one standing in for the other.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    found = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.ClassDef) and node.name == "RunnerConfig"):
            for stmt in node.body:
                if (isinstance(stmt, ast.AnnAssign)
                        and isinstance(stmt.target, ast.Name)
                        and stmt.target.id == "hardened_gate_enabled"):
                    found = stmt.value
    assert found is not None, "the field has gone missing from RunnerConfig"
    assert isinstance(found, ast.Name) and found.id == "HARDENED_GATE_DEFAULT", (
        f"the field's default is written as {ast.dump(found)[:60]} rather than "
        f"reading HARDENED_GATE_DEFAULT. A second expression of one default is "
        f"how the dataclass and a stub config come to disagree.")


def test_the_gate_is_actually_consulted():
    """An addition nothing reaches is not additive: the flag must be read."""
    src = inspect.getsource(R)
    assert src.count("hardened_gate_enabled") >= 3, (
        "the flag appears fewer times than the field, the record and the gate "
        "require; verify it is still wired")
    # and the gate function it guards must exist and be callable
    assert callable(getattr(R, "_check_hardened_convergence", None)), (
        "the gate the flag enables is missing, so turning it on by default "
        "would enable nothing")


def test_the_simulated_runner_no_longer_needs_its_override():
    """It may keep it -- point, never prune -- but it must not CONTRADICT."""
    sim = REPO / "bench" / "tools" / "run_simulated_experiment.py"
    text = sim.read_text(encoding="utf-8")
    assert "hardened_gate_enabled=False" not in text, (
        "the simulated runner disables the gate his ruling turns on")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
