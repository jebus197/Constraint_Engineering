"""Task A22: the panel dispatcher must be importable, and must still refuse to run.

WHAT WAS WRONG. `bench/confer_maths_panel_2026-09-05.py` read `sys.argv[1]` at
MODULE LEVEL, required a `BRIEF.md` beside it, and raised `SystemExit(2)` when
either was missing. So nothing could import it -- not a test wanting to inspect a
function, not a tool, not a reader. The guard for the per-seat sandboxes had to
set `sys.argv` and `PANEL_BRIEF_UNCHECKED=1` around its import to get in, which
is a test working around the code rather than testing it.

IT IS THE SAME CLASS AS `compose_all_2026-08-23.py`, fixed under task A2 the day
before: a module-level read of a file that need not exist, taking every importer
down with it. It is also why `--help` printed `no BRIEF.md in .../logs/--help`
rather than usage -- the flag was consumed as a directory name, which is the
defect task A16 found in 5 other scripts the same night.

WHAT MUST NOT CHANGE, and this is the half that matters. THIS FILE SPENDS MONEY
WHEN IT RUNS. A refactor that made it importable and also made it easier to
dispatch by accident would be a bad trade. So a real run still requires the
argument, still requires the brief, still exits 2 on either, and prints the same
messages; only the BINDING moved from import time into `main()`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"


class TestItImportsWithNothingSupplied:
    def test_no_argv_no_brief_no_systemexit(self, monkeypatch):
        """The whole point. A bare import must not exit the interpreter."""
        monkeypatch.setattr(sys, "argv", ["pytest"])
        sys.path.insert(0, str(ROOT / "bench"))
        spec = importlib.util.spec_from_file_location("panel_a22", DISPATCHER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["panel_a22"] = mod
        spec.loader.exec_module(mod)          # must not raise
        assert mod.LOGS is None and mod.BRIEF is None and mod.PROMPT == ""
        assert callable(mod.resolve_brief)
        assert callable(mod.confine_this_thread)

    def test_the_binding_happens_in_main_not_at_import(self):
        """An addition nothing reaches is not additive: `resolve_brief` could be
        perfect and never called, and a real run would then have no brief."""
        import ast
        tree = ast.parse(DISPATCHER.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                called = {getattr(c.func, "id", None)
                          for c in ast.walk(node) if isinstance(c, ast.Call)}
                assert "resolve_brief" in called, (
                    "main() no longer binds the brief, so a real run would "
                    "dispatch against an empty PROMPT")
                return
        raise AssertionError("the dispatcher has no main()")


class TestRunningItStillRefuses:
    """THIS FILE SPENDS MONEY. Importability must not have loosened the gate."""

    def test_no_argument_exits_two(self):
        r = subprocess.run([sys.executable, str(DISPATCHER)], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 2, (r.returncode, r.stderr[-200:])
        assert "usage:" in r.stderr

    def test_a_missing_brief_exits_two(self):
        r = subprocess.run(
            [sys.executable, str(DISPATCHER), "a_run_dir_that_does_not_exist"],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
        assert r.returncode == 2, (r.returncode, r.stderr[-200:])
        assert "no BRIEF.md" in r.stderr

    def test_help_answers_instead_of_being_eaten(self):
        r = subprocess.run([sys.executable, str(DISPATCHER), "--help"], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (r.returncode, r.stderr[-200:])
        assert "usage:" in r.stderr
        assert "no BRIEF.md" not in r.stderr, (
            "`--help` is being consumed as a directory name again")


class TestResolveBriefItself:
    def test_it_binds_from_a_real_run_directory(self, monkeypatch):
        mod = sys.modules.get("panel_a22")
        if mod is None:
            pytest.skip("the import test has not run in this session")
        runs = sorted((ROOT / "bench" / "logs").glob("panel_round*/BRIEF.md"))
        if not runs:
            pytest.skip("no panel round with a BRIEF.md in this checkout")
        name = runs[-1].parent.name
        mod.resolve_brief(["prog", name])
        try:
            assert mod.LOGS.name == name
            assert mod.PROMPT, "the brief bound empty"
        finally:
            mod.LOGS = mod.BRIEF = None
            mod.PROMPT = ""

    def test_it_refuses_a_missing_brief(self, monkeypatch):
        mod = sys.modules.get("panel_a22")
        if mod is None:
            pytest.skip("the import test has not run in this session")
        with pytest.raises(SystemExit) as exc:
            mod.resolve_brief(["prog", "definitely_not_a_run_dir"])
        assert exc.value.code == 2
