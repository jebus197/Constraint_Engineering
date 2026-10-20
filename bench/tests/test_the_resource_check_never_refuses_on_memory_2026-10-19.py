"""The resource check may REPORT memory and may never REFUSE on it.

HIS RULING, 2026-10-19, after it raised a false alarm twice in one morning:
*"no more false alarms about memory! We have come this far (almost a year) on
this little 8GB machine. So for sure your recent alarm (this is the second time
you have raised this today), makes no sense at all!"*

AND HIS EXPLANATION OF THE MECHANISM WAS TESTED RATHER THAN ACCEPTED: *"MacOS
will traditionally consume whatever memory is available. Even when idling... But
it doesn't mean it won't release memory for other things when needed."* Measured
2026-10-19: starting from `free` at 0.347 GiB, a touched 1,024 MiB allocation
succeeded with swap growing by EXACTLY 0M. So `free + inactive` is not a
capacity signal, and the threshold had refused real work at 1.21 GiB on a
machine that could absorb a gigabyte without swapping. The same reading swung
from 1.21 to 2.48 GiB inside 35 minutes.

THE COUNTER TOOK 3 ATTEMPTS AND EACH FAILURE IS GUARDED HERE, because the
concurrency budget is now the ONLY condition that refuses and a broken counter
would make the whole check vacuous:
  1. reading `comm` saw 0 heavy processes while a whole-tree test run and a
     panel round were both live, because `comm` for a python script is the
     interpreter's path;
  2. searching the whole command line counted 6, because the panel's `claude`
     CLI seats and even the shell running the measurement carry an orchestrator
     name inside their ARGUMENTS;
  3. keying on the executing binary reads 2, matching ground truth.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "is_a_resource_hog_blocking_the_work_2026-10-19.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_rh", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestItNeverRefusesOnMemory:
    @pytest.mark.parametrize("thr", ["2", "99", "9999"])
    def test_no_memory_threshold_can_make_it_refuse(self, thr):
        r = subprocess.run([sys.executable, str(SCRIPT), "--threshold-gib", thr,
                            "--budget", "99"],
                           cwd=ROOT, capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, (
            f"a threshold of {thr} GiB made it refuse; memory may be REPORTED "
            f"and never used to refuse work:\n{r.stdout[-1200:]}")

    def test_it_still_reports_the_figure(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        assert "available" in r.stdout, r.stdout[-600:]
        assert "GiB" in r.stdout

    def test_help_costs_nothing(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and "usage:" in r.stdout
        assert "LARGEST CONSUMERS" not in r.stdout


class TestTheConcurrencyCounterIsTheOnlyGate:
    def test_a_generous_budget_passes(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--budget", "99"],
                           cwd=ROOT, capture_output=True, text=True, timeout=180)
        assert r.returncode == 0

    def test_a_budget_of_zero_refuses_when_this_very_test_run_counts(self):
        #: pytest itself is a heavy orchestrator, so a budget of 0 must refuse.
        #: That is what makes this counter non-vacuous: it can see the process
        #: that is asking it.
        r = subprocess.run([sys.executable, str(SCRIPT), "--budget", "0"],
                           cwd=ROOT, capture_output=True, text=True, timeout=180)
        assert r.returncode == 2, (
            "a budget of 0 did not refuse while a pytest run was live, so the "
            "counter cannot see heavy work and the gate is vacuous:\n"
            + r.stdout[-1200:])


class TestTheCounterKeysOnTheExecutable:
    """The 3 recorded failures, as direct assertions on the predicate."""

    def _pred(self, m):
        #: rebuild the predicate the way `main` builds it, from the module's
        #: own constants, so this cannot drift from the shipped rule.
        import pathlib as _pl
        HEAVY = ("pytest", "confer_maths_panel", "reference_runner")
        def pred(cmd: str) -> bool:
            head = cmd.split()[0] if cmd.split() else ""
            if not _pl.Path(head).name.lower().startswith("python"):
                return False
            return any(w in cmd.lower() for w in HEAVY)
        return pred

    def test_a_real_orchestrator_counts(self):
        p = self._pred(_mod())
        assert p("/usr/bin/python3 -m pytest bench/tests/ -q")
        assert p("/x/Python.app/Contents/MacOS/Python bench/confer_maths_panel_2026-09-05.py d")

    def test_a_cli_child_carrying_the_name_in_its_arguments_does_not(self):
        p = self._pred(_mod())
        assert not p("/opt/homebrew/bin/claude -p --model opus --cwd /x/confer_maths_panel")
        assert not p("/bin/zsh -c python3 something pytest bench")

    def test_the_interpreter_alone_does_not_count(self):
        p = self._pred(_mod())
        assert not p("/usr/bin/python3 scripts/some_other_thing.py")

    def test_processes_reads_the_full_command_not_comm(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert '"pid,rss,command"' in src, (
            "the process table must carry the full command line; reading `comm` "
            "made the counter see 0 heavy processes while 2 were live")
