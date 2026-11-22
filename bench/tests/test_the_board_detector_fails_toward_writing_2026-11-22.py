"""The board detector and the monitor gate need OPPOSITE fail-safe directions.

RAISED BY THE PANEL 2026-11-22 AND VERIFIED BEFORE ADOPTION, which is the
founder's standing instruction: a panel's proposal is tested, never adopted
because a panel proposed it. Under the project's own no-model-voting rule a
seat's verdict is not evidence; the producer named below is.

WHAT WAS WRONG. `scripts/blocker_triage.py:a_commit_board_is_running` documents
itself as *"FAIL-SAFE TOWARD WRITING: any failure of this predicate returns '',
so a fault here costs the protection and never the triage."* Every exclusion it
depends on is a `ps` question -- `_own_process_chain` walks parents, `cy._is_shell`
reads the command name -- and both are documented to fail toward DETECTING a
run. With `ps` unable to answer and `pgrep` still answering, both exclusions let
everything through and a bare pid came back.

WHY IT IS ABOVE THRESHOLD. `hooks/work_not_narrate.py` stands its ENTIRE Stop
gate down when this predicate is truthy, so an over-report switches off the gate
that compels continued work. That is disabling a feature, which the additive
standard forbids.

TWO CORRECTIONS TO THE REPORT THAT RAISED IT, both established by running the
experiment rather than by reading it:

  1. THE DEFECT PREDATES THE B205(c) REPAIR it was attributed to. Running the
     same probe against HEAD's own copy of the function gives identical results,
     and the ancestry exclusion B205(c) added can only make the predicate return
     '' more often, never less.
  2. THE SECOND ARM DOES NOT REPRODUCE. The report had a shell detected as a
     board while `ps` was answering normally. `/bin/zsh -c "sleep 90"` is a
     single command, so zsh exec-optimises itself away and `ps -o comm=` reports
     `sleep`: the plant was never a shell. With a plant that stays a shell, that
     arm returns ''.

Producer: `scripts/does_the_board_detector_hold_its_polarity_2026-11-22.py`.
"""
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TRIAGE = REPO / "scripts" / "blocker_triage.py"
CYGATE = REPO / "hooks" / "cy_monitor_gate.py"
PRODUCER = REPO / "scripts" / "does_the_board_detector_hold_its_polarity_2026-11-22.py"


def _stub_dir(d: pathlib.Path, *, pgrep_pid: str | None, ps_works: bool):
    if pgrep_pid is not None:
        f = d / "pgrep"
        f.write_text(f"#!/bin/sh\necho {pgrep_pid}\nexit 0\n")
        f.chmod(0o755)
    f = d / "ps"
    f.write_text('#!/bin/sh\nexec /bin/ps "$@"\n' if ps_works else '#!/bin/sh\nexit 1\n')
    f.chmod(0o755)


def _probe(code: str, *, pgrep_pid=None, ps_works=True) -> str:
    """Run `code` with pgrep/ps controlled by a PATH stub; return its stdout."""
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _stub_dir(d, pgrep_pid=pgrep_pid, ps_works=ps_works)
        env = dict(os.environ)
        env["PATH"] = f"{d}:{env.get('PATH', '')}"
        env.pop("CDSFL_BT_BOARD", None)
        out = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                             capture_output=True, text=True, timeout=120, env=env)
        assert out.returncode == 0, out.stderr[-400:]
        return out.stdout.strip()


LOAD_TRIAGE = f'''
import os, sys, importlib.util
os.environ.pop("CDSFL_BT_BOARD", None)
spec = importlib.util.spec_from_file_location("bt", r"{TRIAGE}")
m = importlib.util.module_from_spec(spec); sys.modules["bt"] = m
spec.loader.exec_module(m)
'''

LOAD_CY = f'''
import sys, importlib.util
spec = importlib.util.spec_from_file_location("cy", r"{CYGATE}")
m = importlib.util.module_from_spec(spec); sys.modules["cy"] = m
spec.loader.exec_module(m)
'''


# ------------------------------------------------------------ _ps_can_answer

def test_ps_can_answer_is_true_on_a_working_machine():
    assert _probe(LOAD_TRIAGE + "print(m._ps_can_answer())") == "True"


def test_ps_can_answer_is_false_when_ps_is_denied():
    """The matching direction, so the test cannot pass by always saying True."""
    assert _probe(LOAD_TRIAGE + "print(m._ps_can_answer())", ps_works=False) == "False"


# ------------------------------------- the triage fails toward WRITING ('')

def test_the_triage_returns_empty_when_ps_cannot_answer():
    got = _probe(LOAD_TRIAGE + "print(repr(m.a_commit_board_is_running()))",
                 pgrep_pid="99999", ps_works=False)
    assert got == "''", (
        f"the predicate returned {got} where its docstring promises '' -- "
        "the Stop gate in hooks/work_not_narrate.py stands down on this value")


def test_the_triage_still_detects_a_real_board_when_ps_works():
    """ANTI-VACUITY. A predicate repaired into always saying '' is not repaired."""
    board = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        got = _probe(LOAD_TRIAGE + "print(repr(m.a_commit_board_is_running()))",
                     pgrep_pid=str(board.pid), ps_works=True)
        assert got.strip("'\"") == str(board.pid), got
    finally:
        board.terminate()
        try:
            board.wait(timeout=5)
        except Exception:                                    # noqa: BLE001
            board.kill()


def test_a_shell_is_not_a_board_when_ps_can_identify_it():
    """The arm the panel reported as failing. With a plant that STAYS a shell
    -- a loop, not a single command zsh can exec-optimise away -- it passes."""
    sh = subprocess.Popen(["/bin/zsh", "-c", "while true; do sleep 1; done"])
    try:
        comm = subprocess.run(["ps", "-p", str(sh.pid), "-o", "comm="],
                              capture_output=True, text=True).stdout.strip()
        if comm.rsplit("/", 1)[-1] not in ("zsh", "bash", "sh"):
            pytest.skip(f"plant is not a shell on this machine: {comm!r}")
        got = _probe(LOAD_TRIAGE + "print(repr(m.a_commit_board_is_running()))",
                     pgrep_pid=str(sh.pid), ps_works=True)
        assert got == "''", got
    finally:
        sh.terminate()
        try:
            sh.wait(timeout=5)
        except Exception:                                    # noqa: BLE001
            sh.kill()


# ------------------------- the monitor gate keeps the OPPOSITE direction

def test_the_monitor_gate_still_detects_when_ps_cannot_answer():
    """PINNED DELIBERATELY, SO A UNIFYING REFACTOR GOES RED.

    `hooks/cy_monitor_gate.py` enforces his 60-second monitoring directive, and
    its cost of under-firing is an unobserved 3-hour run while the cost of
    over-firing is one prod. So it must KEEP detecting where `ps` fails -- the
    opposite of the triage. The two files share `_own_process_chain` and the
    `pytest.*bench/tests` pattern by duplication, which makes unifying them
    look attractive; this test is why that cannot be done as a single helper.
    """
    got = _probe(LOAD_CY + "print(m.runner_processes())",
                 pgrep_pid="99999", ps_works=False)
    assert "99999" in got, (
        f"the monitor gate stopped detecting under a denied ps: {got} -- its "
        "polarity is deliberately opposite to the triage's")


# --------------------------------------------------------------- producer

def test_the_producer_runs_and_passes():
    """measured-rate-travels-with-its-script: the figures need their script."""
    out = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                         capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stdout[-900:] + out.stderr[-400:]
    assert "arm C" in out.stdout, "the anti-vacuity arm did not run"
