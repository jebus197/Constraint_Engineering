"""A `--help` on an experiment runner must never cost the reader money.

Found 2026-08-07 by a cold-start drill: an agent given only this repository's
documentation, told to behave like an outside researcher, ran
``python3 bench/run_exp36_evidence.py --help``. Fifteen of the seventeen
``run_exp*.py`` scripts hand-parse ``sys.argv``, silently ignore anything they
do not recognise, and fall through to ``mode = "run"``, whose first action is a
live preflight dispatch to five paid models. It happened twice before the drill
worked out why. ``docs/REPRODUCING.md`` pointed researchers at five of those
scripts and said "Most runners accept CLI flags".

These tests are structural rather than behavioural on purpose: they must not
execute a runner, because executing a runner is the defect.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BENCH = REPO / "bench"
GUARD = "guard_argv"


def _runners() -> list[Path]:
    return sorted(BENCH.glob("run_exp*.py")) + [BENCH / "run_experiment.py"]


def _uses_argparse(src: str) -> bool:
    return "argparse" in src


def _entry_body(tree: ast.Module) -> list[ast.stmt] | None:
    """The statements of `def main():`, or of the `if __name__ == "__main__":`
    block when a runner has no main() — the two shapes in this repository."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node.body
    for node in tree.body:
        if (isinstance(node, ast.If)
                and ast.dump(node.test).find("__name__") != -1):
            return node.body
    return None


def _calls_guard_first(body: list[ast.stmt]) -> bool:
    """The guard must run before ANYTHING else in the entry point.

    This is the assertion that actually matters. A guard placed after
    ``source_env()`` or after a config load is a guard that runs too late —
    everything below it in these runners can reach a paid model, and the whole
    point is to stop before the first one.
    """
    for stmt in body:
        # An import of the guard is allowed to precede the call.
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            if isinstance(stmt, ast.ImportFrom) and "runner_argv_guard" in (stmt.module or ""):
                continue
            return False
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            fn = stmt.value.func
            name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
            return name == GUARD
        return False
    return False


@pytest.mark.parametrize("path", _runners(), ids=lambda p: p.name)
def test_every_runner_refuses_help_before_it_can_dispatch(path: Path) -> None:
    src = path.read_text(encoding="utf-8")
    if _uses_argparse(src):
        pytest.skip(f"{path.name} uses argparse, which handles --help itself")
    assert GUARD in src, (
        f"{path.name} hand-parses sys.argv and does not call {GUARD}. "
        f"An unrecognised argument — including --help — will fall through to a "
        f"live dispatch and bill whoever ran it."
    )
    body = _entry_body(ast.parse(src))
    assert body is not None, f"{path.name}: no main() and no __main__ block found"
    assert _calls_guard_first(body), (
        f"{path.name} calls {GUARD}, but not as the FIRST statement of its entry "
        f"point. Anything preceding it can reach a paid model, so a late guard "
        f"is no guard."
    )


class TestTheGuardItself:
    """Behaviour, exercised directly so no runner has to be executed."""

    def _run(self, known, argv):
        from bench.runner_argv_guard import guard_argv
        import io
        codes, out = [], io.StringIO()
        guard_argv(known, "USAGE LINE", argv, exit_fn=codes.append, out=out)
        return codes, out.getvalue()

    @pytest.mark.parametrize("flag", ["-h", "--help", "help", "--usage"])
    def test_help_exits_zero_and_prints_usage(self, flag):
        codes, out = self._run(["run", "--resume"], [flag])
        assert codes == [0]
        assert "USAGE LINE" in out

    def test_an_unrecognised_option_refuses_with_a_reason(self):
        codes, out = self._run(["run", "--resume"], ["--dry-run"])
        assert codes == [2]
        assert "--dry-run" in out and "REFUSING TO START" in out
        assert "paid models" in out, "the refusal must say WHY it refused"

    def test_a_valid_invocation_is_untouched(self):
        codes, out = self._run(["run", "--resume", "--pattern"], ["run", "--resume"])
        assert codes == [], "the guard must not interfere with a real run"
        assert out == ""

    def test_a_value_following_a_flag_is_not_policed(self):
        """`--pattern star`: the runner validates `star` itself, loudly. A guard
        that rejected it would break valid invocations — a worse failure than
        the one being fixed."""
        codes, _ = self._run(["--pattern"], ["--pattern", "star"])
        assert codes == []

    def test_help_wins_even_when_mixed_with_other_arguments(self):
        codes, out = self._run(["run"], ["run", "--help"])
        assert codes == [0] and "USAGE LINE" in out
