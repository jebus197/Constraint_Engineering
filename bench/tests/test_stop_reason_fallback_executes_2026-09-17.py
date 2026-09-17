"""Task 6.1, panel round 16: the stop-reason fallback, EXECUTED rather than read.

THE GAP. `test_stop_reason_on_every_exit_2026-09-09.py` proves the brain-level
half by execution, but its runner-level tests read `RUNNER.read_text()`. Pointed
at a copy of the runner whose guard reads `if False and not (...)`, that file
still gives 6 passed, and again with the sentinel replaced by `""`. Its last
assert compared 2 string literals and could not fail.

WHAT THIS FILE DOES. It selects, by AST, the statement immediately before
`signal = brain.signal_complete()` in `run_experiment`, requires it to be an
`if`, compiles that statement ALONE and executes it against a real `InsectBrain`.
The same checks are then run against in-memory copies of the runner carrying
each of the 2 semantic mutations above, and must fail on both.

WHAT THE GUARANTEE COVERS, AND WHAT IT DOES NOT. The fallback runs when the round
loop ends by `break` or by running out of rounds. It does NOT run on the 2 HIL
review pauses, which call `sys.exit(42)` inside the loop, nor on an exception
that escapes the loop, because no `try` encloses the loop or its call site. A
HIL pause is resumable and writes `hil_status = "paused_for_review"` to a partial
report rather than a completion signal. `TestTheExitInventory` pins the exits so
a new in-loop `sys.exit` turns this file red instead of silently bypassing the
fallback.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO))
from insect_brain import InsectBrain  # noqa: E402
from bench.dm._types import DynamicManagementConfig  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"
SENTINEL = "UNRECORDED_STOP"


def _brain(tmp_path, **state):
    """Built exactly as `_brain()` in the 2026-09-09 file builds one."""
    b = InsectBrain(config=DynamicManagementConfig(), logs_dir=tmp_path,
                    source_paths=["x.py"])
    b.initialise(["CC2-SIM"])
    for k, v in state.items():
        setattr(b.state, k, v)
    return b


def _run_experiment(tree: ast.Module) -> ast.FunctionDef:
    fns = [n for n in tree.body
           if isinstance(n, ast.FunctionDef) and n.name == "run_experiment"]
    assert len(fns) == 1, f"expected 1 top-level run_experiment, found {len(fns)}"
    return fns[0]


def fallback_if(src: str) -> ast.If:
    """The body statement immediately before `signal = brain.signal_complete()`."""
    fn = _run_experiment(ast.parse(src))
    idx = [i for i, s in enumerate(fn.body)
           if isinstance(s, ast.Assign)
           and ast.unparse(s) == "signal = brain.signal_complete()"]
    assert len(idx) == 1, f"expected 1 signal_complete assignment, found {len(idx)}"
    assert idx[0] > 0
    prev = fn.body[idx[0] - 1]
    assert isinstance(prev, ast.If), (
        "the statement before signal_complete() is no longer the fallback `if`: "
        + ast.unparse(prev)[:120])
    return prev


def irreducible_queue_halt(src: str) -> str:
    """The runner's own IRREDUCIBLE_QUEUE_HALT value, read from its assignment."""
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "IRREDUCIBLE_QUEUE_HALT"
                for t in n.targets):
            return ast.literal_eval(n.value)
    raise AssertionError("IRREDUCIBLE_QUEUE_HALT is not assigned at module level")


def execute(node: ast.If, brain, result: dict) -> str:
    code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                   str(RUNNER), "exec")
    exec(code, {"brain": brain, "result": result})
    return brain.signal_complete()["reason"]


def check_fallback(src: str, tmp_path: Path) -> None:
    """Every behaviour the entry claims for the fallback. Raises AssertionError."""
    node = fallback_if(src)
    halt = irreducible_queue_halt(src)

    b = _brain(tmp_path / "empty", converged=False, stop_reason="",
               convergence_reason="", failure_reason="")
    reason = execute(node, b, {})
    assert reason.startswith(SENTINEL), f"an unnamed exit wrote {reason!r}"
    assert b.state.stop_reason == reason
    assert halt not in reason and reason != halt, (
        "the unrecorded case must not look like the named irreducible-queue halt")

    b = _brain(tmp_path / "named", converged=False, stop_reason="   ",
               convergence_reason="", failure_reason="")
    assert execute(node, b, {"convergence_reason": "EXTENSION_STALLED"}) \
        == "EXTENSION_STALLED", "a blank stop_reason must take the result's reason"

    b = _brain(tmp_path / "failure", converged=False, stop_reason="",
               convergence_reason="", failure_reason="")
    assert execute(node, b, {"failure_reason": "  SEAT_TIMEOUT "}) == "SEAT_TIMEOUT"

    b = _brain(tmp_path / "kept", converged=False, stop_reason=halt,
               convergence_reason="", failure_reason="")
    assert execute(node, b, {"convergence_reason": "OTHER"}) == halt, (
        "an existing named halt must not be overwritten")


def _mutate(src: str, old: str, new: str) -> str:
    assert src.count(old) == 1, f"mutation site {old!r} occurs {src.count(old)} times"
    return src.replace(old, new)


@pytest.fixture(scope="module")
def src():
    return RUNNER.read_text(encoding="utf-8")


class TestTheFallbackExecutes:
    def test_the_fallback_at_head_does_what_the_entry_says(self, src, tmp_path):
        check_fallback(src, tmp_path)

    def test_the_checks_fail_when_the_guard_never_fires(self, src, tmp_path):
        mutant = _mutate(src, 'if not (getattr(brain.state, "stop_reason", "") or "").strip():',
                         'if False and not (getattr(brain.state, "stop_reason", "") or "").strip():')
        with pytest.raises(AssertionError):
            check_fallback(mutant, tmp_path)

    def test_the_checks_fail_when_the_sentinel_is_emptied(self, src, tmp_path):
        node = fallback_if(src)
        sentinel = [n for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and n.value.startswith(SENTINEL)]
        assert len(sentinel) == 1, "the sentinel string is not inside the fallback"
        mutant = _mutate(src, '"UNRECORDED_STOP (the round loop exited by a path that names no "\n'
                              '            "reason; see the run log)"', '""')
        with pytest.raises(AssertionError):
            check_fallback(mutant, tmp_path)


class TestTheExitInventory:
    """The fallback cannot see a `sys.exit` inside the loop. Pin every one."""

    @staticmethod
    def _is_sys_exit(node) -> bool:
        return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "exit" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "sys")

    @staticmethod
    def _sets_paused_for_review(stmts) -> bool:
        for s in stmts:
            if isinstance(s, ast.Assign) and isinstance(s.value, ast.Constant) \
                    and s.value.value == "paused_for_review":
                for t in s.targets:
                    if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                            and t.value.id == "result" \
                            and isinstance(t.slice, ast.Constant) \
                            and t.slice.value == "hil_status":
                        return True
        return False

    def inventory(self, src):
        fn = _run_experiment(ast.parse(src))
        exits = [n for n in ast.walk(fn) if self._is_sys_exit(n)]
        paused = []
        for parent in ast.walk(fn):
            for field in ("body", "orelse", "finalbody"):
                stmts = getattr(parent, field, None)
                if not isinstance(stmts, list):
                    continue
                for s in stmts:
                    if isinstance(s, ast.Expr) and self._is_sys_exit(s.value) \
                            and self._sets_paused_for_review(stmts):
                        paused.append(s.value)
        return exits, paused

    def check_inventory(self, src):
        exits, paused = self.inventory(src)
        assert {id(e) for e in exits} == {id(p) for p in paused}, (
            "a sys.exit in run_experiment is not a HIL pause; it bypasses the "
            "stop-reason fallback: lines "
            f"{sorted(e.lineno for e in exits if all(e is not p for p in paused))}")
        assert len(exits) == 2, [e.lineno for e in exits]
        for e in exits:
            assert [ast.literal_eval(a) for a in e.args] == [42], ast.unparse(e)

    def test_the_only_exits_in_run_experiment_are_the_2_hil_pauses(self, src):
        self.check_inventory(src)

    def test_a_new_exit_in_the_loop_turns_this_red(self, src):
        """Control: an added in-loop exit that is not a HIL pause is caught."""
        mutant = _mutate(src, "        # ── Phase transition or final convergence ──\n",
                         "        if round_idx > 10**9:\n            sys.exit(3)\n"
                         "        # ── Phase transition or final convergence ──\n")
        with pytest.raises(AssertionError, match="bypasses the stop-reason fallback"):
            self.check_inventory(mutant)
