"""The `cy` watchdog must report WHETHER THE RUN WAS RIGHT, not only that it ended.

THE SILENT STATE, MEASURED 2026-10-02 BEFORE THE SCRIPT WAS TOUCHED. Two run
directories differing in `completion_signal.json` ALONE:

    halted     {"status": "INCOMPLETE",
                "reason": "HALTED_IRREDUCIBLE_QUEUE_ALARM", "total_rounds": 1}
    converged  {"status": "COMPLETE", "reason": "CONVERGED", "total_rounds": 4}

produced BYTE-IDENTICAL stdout and the same exit code 0:

    [cy] PROCESS GONE: pid 51401 is no longer running; the run has ended
    [cy] CLOSED: watchdog exiting; 1 round(s) landed; run_ended=True
    exit=0

`_round_count` reads `round_*.json` and `runner_state.json`; TROUBLE/PROGRESS
read the log. NOTHING read `completion_signal.json` -- the one artefact that
records `status` and `reason`. So the state in which the run is DEAD OR WRONG
and this script stays silent is: the run terminates without writing a TROUBLE
token into the log. Three real ways in:

  1. It halts cleanly, as both archived prose runs did at round 0, and the
     halt reaches the report and the signal rather than a matching log line.
  2. The OOM reaper or an external kill takes it; it writes nothing at all.
  3. Its traceback goes to a stderr the launcher did not tee into `--log`.

In every one the terminal event is "the run has ended" at exit 0 -- which the
script's own docstring offers as the way to tell "a quiet watchdog from a
finished one". It does tell finished from quiet. It does not tell SUCCEEDED
from FAILED, and the founder's criterion is 3 consecutive CLEAN CONVERGENCES.

THE FIX IS ONE MORE EVENT LINE, which under the Monitor tool is one more wake.
The EXIT CODE IS DELIBERATELY UNCHANGED: returning 2 on a bad outcome turned
`test_a_dead_process_is_reported_and_ends_the_watch:74` red, and amending a
committed oracle to admit a new feature is forbidden. That residue is recorded
in the script and here rather than closed.

HOW THE FIX FAILS:
  * It reports BAD only from what the run WROTE. A run that writes
    `status: COMPLETE, reason: CONVERGED` and is wrong anyway reads CLEAN --
    this watches the signal, not the mathematics.
  * `NO_SIGNAL` is a third verdict and is NOT folded into BAD, so a run that
    ended without recording why is distinguishable from a named halt. A caller
    that treats every non-CLEAN alike loses that, which is why the verdict
    token and not just a boolean is on the line.
  * `CLEAN_REASONS` is a substring match on an uppercased reason. A future
    reason string containing "CONVERGED" inside a FAILURE name would read CLEAN.
    Pinned below by `test_a_reason_that_merely_mentions_convergence_is_not_clean`,
    which fails if the match is ever loosened past `status == COMPLETE`.

MUTATIONS USED (both verified red):
  W1  `read_outcome` always returns ("CLEAN", "")
      -> test_a_halted_run_is_reported_as_BAD fails
  W2  delete the `say(f"OUTCOME {verdict}", detail)` call
      -> every test in TestTheOutcomeIsAnEvent fails
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WD = ROOT / "scripts" / "cy_watchdog_2026-10-02.py"

pytestmark = pytest.mark.skipif(not WD.is_file(), reason=f"missing {WD}")


def _dead_pid() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def _run_once(d: Path):
    log = d / "run.log"
    if not log.exists():
        log.write_text("[00:00:01] starting\n", encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(WD), "--log", str(log),
         "--pid", str(_dead_pid()), "--once", "--interval", "1"],
        capture_output=True, text=True, timeout=120)


def _signal(d: Path, **kw):
    (d / "completion_signal.json").write_text(json.dumps(kw), encoding="utf-8")


class TestTheOutcomeIsAnEvent:
    def test_a_halted_run_is_reported_as_BAD(self, tmp_path):
        _signal(tmp_path, status="INCOMPLETE",
                reason="HALTED_IRREDUCIBLE_QUEUE_ALARM", total_rounds=1)
        r = _run_once(tmp_path)
        assert "OUTCOME BAD" in r.stdout, r.stdout
        assert "HALTED_IRREDUCIBLE_QUEUE_ALARM" in r.stdout

    def test_a_converged_run_is_reported_as_CLEAN(self, tmp_path):
        _signal(tmp_path, status="COMPLETE", reason="CONVERGED", total_rounds=4)
        r = _run_once(tmp_path)
        assert "OUTCOME CLEAN" in r.stdout, r.stdout

    def test_the_two_are_no_longer_indistinguishable(self, tmp_path):
        """THE MEASUREMENT THIS FILE EXISTS FOR. Shipped: identical stdout."""
        halted, conv = tmp_path / "h", tmp_path / "c"
        for d in (halted, conv):
            d.mkdir()
        _signal(halted, status="INCOMPLETE",
                reason="HALTED_IRREDUCIBLE_QUEUE_ALARM", total_rounds=1)
        _signal(conv, status="COMPLETE", reason="CONVERGED", total_rounds=4)
        a, b = _run_once(halted), _run_once(conv)

        def _evts(out):
            return [l.split("] ", 1)[-1] for l in out.splitlines()]
        assert _evts(a.stdout) != _evts(b.stdout), (
            "a halted run and a converged run produced the same events")

    def test_a_run_that_recorded_nothing_is_its_own_third_verdict(self, tmp_path):
        """'The run ended without recording why' is worse than any named halt
        and must not read as one."""
        r = _run_once(tmp_path)
        assert "OUTCOME NO_SIGNAL" in r.stdout, r.stdout
        assert "OUTCOME BAD" not in r.stdout

    def test_an_unreadable_signal_is_not_silently_clean(self, tmp_path):
        (tmp_path / "completion_signal.json").write_text("{not json",
                                                         encoding="utf-8")
        r = _run_once(tmp_path)
        assert "OUTCOME UNREADABLE" in r.stdout, r.stdout

    def test_a_reason_that_merely_mentions_convergence_is_not_clean(self, tmp_path):
        """`status == COMPLETE` is load-bearing, not decoration."""
        _signal(tmp_path, status="INCOMPLETE",
                reason="HALTED_BEFORE_CONVERGED", total_rounds=0)
        r = _run_once(tmp_path)
        assert "OUTCOME BAD" in r.stdout, r.stdout

    def test_the_closing_line_carries_the_outcome_too(self, tmp_path):
        """A reader who sees only the last line still learns the verdict."""
        _signal(tmp_path, status="INCOMPLETE", reason="HALTED_X", total_rounds=1)
        r = _run_once(tmp_path)
        closed = [l for l in r.stdout.splitlines() if "CLOSED:" in l]
        assert closed and "outcome=BAD" in closed[-1], r.stdout


class TestNothingWasRemoved:
    def test_the_exit_code_contract_is_untouched(self, tmp_path):
        """A dead process is still a clean watchdog exit, which is what
        `test_a_dead_process_is_reported_and_ends_the_watch` asserts. Changing
        it is a REMOVAL and has no committed measurement behind it."""
        _signal(tmp_path, status="INCOMPLETE", reason="HALTED_X", total_rounds=1)
        r = _run_once(tmp_path)
        assert r.returncode == 0, r.stdout

    def test_process_gone_and_closed_still_fire(self, tmp_path):
        r = _run_once(tmp_path)
        assert "PROCESS GONE" in r.stdout
        assert "CLOSED" in r.stdout

    def test_read_outcome_never_raises_on_a_hostile_directory(self, tmp_path):
        sys.path.insert(0, str(ROOT / "scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("cy_wd", WD)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for payload in ("[]", "null", '"text"', "", "{}"):
            (tmp_path / "completion_signal.json").write_text(payload,
                                                             encoding="utf-8")
            v, _d = m.read_outcome(tmp_path / "run.log")
            assert v in ("CLEAN", "BAD", "NO_SIGNAL", "UNREADABLE"), payload
