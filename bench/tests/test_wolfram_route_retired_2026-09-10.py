"""The WolframCloud MCP route is retired, and the retirement must be reachable.

Task 0.2. The additive standard permits removal ONLY when "a COMMITTED
MEASUREMENT showing the replacement dominates on a named property" exists -- "a
judgement that something is better is not evidence that it is". The named
property is availability, the replacement is the local Engine reached through
`wolframscript`, and the measurement is `scripts/wolfram_route_health_2026-09-10.py`.

WHAT THE MEASUREMENT FOUND, and it is stronger than the entry that asked for it.
The route did not always fail. Across 34 log files and 64 connection attempts:
before 2026-09-04, 1 failed of 21; from 2026-09-04, 42 failed of 43, with exactly
1 successful attach in that whole period. Fisher exact p = 2.199086e-14.

Entry 0.2 had said "39 connection failures ... against 2 successes in the whole
log". There are 21 successful attaches, not 2 -- the conclusion was right and the
arithmetic was not, which is the reason the script is committed beside it.

These tests EXECUTE the script and drive its classifier against synthetic logs.
None asserts on its source text.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "wolfram_route_health_2026-09-10.py"
BOX = ROOT / ".claude" / "CLAUDE.md"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("wolfram_health", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheScriptRuns:
    def test_it_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"{r.stdout[-1200:]}\n{r.stderr[-1200:]}"

    def test_a_machine_with_no_logs_is_a_skip_not_a_zero(self, mod, tmp_path, monkeypatch):
        """A rate needs a denominator. 0 of 0 is not 'the route is healthy'."""
        monkeypatch.setattr(mod, "LOGDIR", tmp_path / "nowhere")
        monkeypatch.setattr(sys, "argv", ["w"])
        assert mod.main() == 0
        assert mod.scan() == ([], [], [])


class TestTheClassifierCountsATTEMPTS:
    """The first version counted every MENTION and got a meaningless 13.27%."""

    def _log(self, tmp_path, lines):
        d = tmp_path / "Logs"
        d.mkdir(exist_ok=True)
        (d / "main.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return d

    def test_routine_lines_are_not_attempts(self, mod, tmp_path, monkeypatch):
        d = self._log(tmp_path, [
            "2026-09-01 10:00:00 [info] Shutting down MCP Server: WolframCloud",
            "2026-09-01 10:00:01 [info] [LocalMcpServerManager] Closing WolframCloud",
            "2026-09-01 10:00:02 [info] MCP Server connection requested for: WolframCloud",
        ])
        monkeypatch.setattr(mod, "LOGDIR", d)
        fails, oks, _ = mod.scan()
        assert (fails, oks) == ([], []), (
            "shutdown and request lines are not connection attempts; counting "
            "them is what produced the meaningless first figure")

    def test_an_announced_attach_is_a_success(self, mod, tmp_path, monkeypatch):
        d = self._log(tmp_path, [
            "2026-09-01 10:00:00 [info] [localMcpBridge] announcing WolframCloud: 3 tool(s)"])
        monkeypatch.setattr(mod, "LOGDIR", d)
        fails, oks, _ = mod.scan()
        assert len(oks) == 1 and not fails

    @pytest.mark.parametrize("line", [
        "2026-09-05 11:00:00 [error] [LocalMcpServerManager] Failed to connect to WolframCloud: Connection closed",
        "2026-09-05 11:00:01 [warn] [MCP] MCP server WolframCloud went away before the attach completed",
    ])
    def test_both_failure_shapes_are_counted(self, mod, tmp_path, monkeypatch, line):
        d = self._log(tmp_path, [line])
        monkeypatch.setattr(mod, "LOGDIR", d)
        fails, oks, _ = mod.scan()
        assert len(fails) == 1 and not oks, line

    def test_a_line_about_another_server_is_ignored(self, mod, tmp_path, monkeypatch):
        d = self._log(tmp_path, [
            "2026-09-05 11:00:00 [error] Failed to connect to SomeOtherServer: Connection closed"])
        monkeypatch.setattr(mod, "LOGDIR", d)
        assert mod.scan() == ([], [], [])


class TestTheRetirementIsRecorded:
    def test_the_constraint_box_marks_it_retired(self):
        box = BOX.read_text(encoding="utf-8")
        assert "WolframCloud` MCP server — RETIRED" in box, (
            "the tool constraint box still offers a route measured at 97.67% "
            "failure; an agent reading it would use the dead endpoint")

    def test_the_local_engine_is_named_as_the_route(self):
        box = BOX.read_text(encoding="utf-8")
        assert "ONLY Wolfram route" in box

    def test_the_retirement_cites_its_producing_script(self):
        """`measured-rate-travels-with-its-script`, applied to a REMOVAL.

        A removal justified by prose is exactly what the additive standard
        forbids: "a judgement that something is better is not evidence that it
        is." The script must be named where the removal is recorded.
        """
        box = BOX.read_text(encoding="utf-8")
        assert "scripts/wolfram_route_health_2026-09-10.py" in box
        assert SCRIPT.is_file()
