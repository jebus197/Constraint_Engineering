"""The `cy` watchdog must treat SILENCE as an event, not as health.

THE FAILURE THIS GUARDS, and it is the founder's own account of 2026-10-02:
*"last night it meant you let a run carry on for a full 9 hours without
monitoring or repairing anything, so you may have to create a mechanical
trigger for cy to wake you up so this cannot happen again."*

The hole was not a missing alarm. It was an alarm with nothing to say. A watcher
that only greps for trouble stays mute through a hang, a kill, or a crashloop,
and mute is indistinguishable from healthy — the Monitor tool's own
documentation makes the same point: "silence is not success." So the properties
tested here are the ABSENCE signals: a log that stops growing, and a process
that stops existing. Neither depends on the run choosing to write anything.

The assistant's previous explanation — that its monitors cap at 30 minutes — was
half true. The cap bounds ONE arming, and expiry notifies so it can be re-armed.
That is why the cadence belongs in a mechanical poller and the escalation in the
model, which is the split this script implements.

These tests RUN the watchdog as a subprocess. A test asserting on its source
text would only confirm it describes itself consistently.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WD = ROOT / "scripts" / "cy_watchdog_2026-10-02.py"

pytestmark = pytest.mark.skipif(not WD.is_file(), reason="watchdog absent")


def _run(args, timeout=60):
    r = subprocess.run([sys.executable, str(WD), *args],
                       capture_output=True, text=True, timeout=timeout)
    return r


class TestSilenceIsAnEvent:

    def test_a_stalled_log_is_reported(self, tmp_path):
        """THE 9-HOUR HOLE. No new bytes must become a spoken event."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        time.sleep(1.2)
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "1", "--once", "--interval", "1"])
        assert "STALLED" in r.stdout, r.stdout
        assert "SILENCE IS NOT SUCCESS" in r.stdout

    def test_a_healthy_quiet_run_is_NOT_reported_as_stalled(self, tmp_path):
        """ANTI-FALSE-POSITIVE: quiet inside the threshold is not an alarm."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "STALLED" not in r.stdout, r.stdout
        assert "TROUBLE" not in r.stdout

    def test_a_dead_process_is_reported_and_ends_the_watch(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid),
                  "--once", "--interval", "1"])
        assert "PROCESS GONE" in r.stdout, r.stdout
        # THE EXIT CODE IS UNCHANGED, on the cc2 seat's call: a run that ended
        # is a clean watchdog exit, and the VERDICT travels in the OUTCOME line.
        # An earlier version here returned a code per outcome, and the Monitor
        # then reported "script failed (exit 3)" for an ordinary finish.
        assert r.returncode == 0, f"a run that ended must exit 0: {r.returncode}"
        assert "OUTCOME NO_SIGNAL" in r.stdout

    def test_a_live_process_is_not_called_gone(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "PROCESS GONE" not in r.stdout
        assert r.returncode == 1, "the watch did not end, so the exit must differ"


class TestTroubleAndProgressAreSpoken:

    @pytest.mark.parametrize("line", [
        "Traceback (most recent call last):",
        "HALTED_IRREDUCIBLE_QUEUE_ALARM at round 0",
        "openai.RateLimitError: 429",
        "Killed",
        "PermissionError: [Errno 1] Operation not permitted",
        "UNRECORDED_STOP (the round loop exited)",
    ])
    def test_each_trouble_signature_wakes_the_model(self, tmp_path, line):
        log = tmp_path / "run.log"
        log.write_text("", encoding="utf-8")
        # the watchdog reads from offset 0 on its first probe
        log.write_text(line + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" in r.stdout, f"{line!r} did not wake it: {r.stdout}"

    @pytest.mark.parametrize("green", [
        "suite: GREEN at 1cfc30e - 8,878 passed, 0 failed",
        "501 passed in 31.04s",
        "9375 passed, 8 skipped, 0 failed",
    ])
    def test_a_green_result_is_not_trouble(self, tmp_path, green):
        """A COUNT OF ZERO IS NOT TROUBLE. The bare word `failed` matched
        '0 failed' on this watchdog's first live outing, turning a GREEN suite
        result into an alarm. An alarm that cries wolf trains its reader to
        ignore it, which is the 9-hour hole again by another route."""
        log = tmp_path / "run.log"
        log.write_text(green + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, r.stdout

    @pytest.mark.parametrize("benign", [
        # A TIMESTAMP IS NOT A STATUS CODE. `401` matched inside
        # `20261002T064011Z` on a live run, so every artefact saved at such a
        # second raised an alarm. Digit boundaries fixed the timestamp and
        # still matched "429 findings", because a boundary cannot tell a code
        # from a count -- so bare status codes are gone entirely.
        "[07:40:11]   Saved: .../r2_chatgpt-sim_20261002T064011Z.json",
        "Saved round_04.json at 20261002T040329Z",
        "elapsed 4293.1s, 429 findings total",
        "Round 3: 403 findings, 2932.4s",
        "dispatching seat cc2-sim at 20261002T040112Z",
    ])
    def test_a_digit_run_is_not_mistaken_for_a_status_code(self, tmp_path, benign):
        log = tmp_path / "run.log"
        log.write_text(benign + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, (
            f"{benign[:50]!r} cried wolf; an ignored channel is the 9-hour "
            f"hole again: {r.stdout}")

    @pytest.mark.parametrize("red", [
        "3 failed, 9372 passed in 3217.53s",
        "1 failed, 500 passed",
        "FAILED bench/tests/test_x.py::test_y",
        "2 errors in 4.1s",
        "HTTP 429 Too Many Requests: rate limit exceeded",
        "502 Server Error",
    ])
    def test_a_real_failure_count_still_wakes_the_model(self, tmp_path, red):
        """THE ANTI-REGRESSION for the narrowing above."""
        log = tmp_path / "run.log"
        log.write_text(red + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" in r.stdout, f"{red!r} did not wake it: {r.stdout}"

    def test_an_ordinary_line_does_not_wake_the_model(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("dispatching seat cc2-sim, 4 of 5\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, r.stdout

    def test_a_landed_round_is_reported_from_the_artefact_not_the_prose(self, tmp_path):
        """Rounds are counted from round_*.json, so a lying log cannot inflate them."""
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        (tmp_path / "round_00.json").write_text("{}", encoding="utf-8")
        (tmp_path / "round_01.json").write_text("{}", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "ARMED" in r.stdout
        assert "2 round(s) landed" in r.stdout, r.stdout


class TestItCannotItselfBecomeTheSilentWatcher:

    def test_a_missing_log_is_announced_rather_than_tolerated(self, tmp_path):
        r = _run(["--log", str(tmp_path / "never.log"), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "does not exist yet" in r.stdout, r.stdout
        assert "a run that never starts is itself an event" in r.stdout

    def test_it_always_announces_that_it_armed(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--once", "--interval", "1"])
        assert r.stdout.splitlines()[0].startswith("[cy "), r.stdout
        assert "ARMED" in r.stdout

    def test_it_always_announces_that_it_closed(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--once", "--interval", "1"])
        assert "CLOSED" in r.stdout, (
            "a watchdog that exits silently is the defect it exists to prevent")

    def test_help_costs_nothing_and_exits_zero(self):
        r = _run(["--help"])
        assert r.returncode == 0 and "usage" in r.stdout.lower()

    def test_an_unreadable_pid_file_does_not_crash_it(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        bad = tmp_path / "bad.pid"
        bad.write_text("not-a-pid\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid-file", str(bad),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "ARMED" in r.stdout and "CLOSED" in r.stdout

class TestQuietButWorkingIsNotAStall:
    """A process that is silent AND busy must not be called stalled.

    THE FIRST LIVE FALSE POSITIVE, 2026-10-02. This watchdog fired STALLED on a
    panel dispatch whose 2 seats were healthy: `claude -p` writes nothing to the
    dispatcher's log until a seat finishes, and the previous round measured
    1720.7 s to first output, so 900 s of silence was normal.

    RAISING THE THRESHOLD WOULD HAVE BEEN THE WRONG FIX, which is why this class
    exists rather than a bigger default. A larger threshold buys quiet by going
    blind: a seat hung at second 30 becomes indistinguishable from one thinking
    at second 1700. CPU PERCENT cannot separate them either, because a seat
    blocked on network I/O sits near 0.3%. Cumulative CPU TIME can: it advances
    for a streaming process and not for a hung one.
    """

    def test_a_busy_silent_process_reports_working_not_stalled(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        burner = subprocess.Popen(
            [sys.executable, "-c",
             "import time\nt=time.time()\nwhile time.time()-t<45: pass"])
        try:
            time.sleep(3)          # let it bank measurable CPU time
            r = _run(["--log", str(log), "--pid", str(burner.pid),
                      "--stall-seconds", "1", "--interval", "2",
                      "--heartbeat-minutes", "99", "--max-hours", "0.0028"],
                     timeout=120)
        finally:
            burner.kill(); burner.wait()
        assert "QUIET BUT WORKING" in r.stdout, (
            f"a busy silent process was misreported; stdout: {r.stdout}")
        # The burner outlives the watchdog by design: a fixture that expires
        # mid-run makes the watchdog correctly report a stall and the test
        # wrongly report a bug. That happened on the first attempt here.
        assert "STALLED" not in r.stdout, (
            f"a busy process was called stalled; stdout: {r.stdout}")

    def test_a_truly_idle_silent_process_is_still_called_stalled(self, tmp_path):
        """THE ANTI-REGRESSION. Silence is still an event when nothing is doing
        anything, or this fix has simply disabled the alarm."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        idle = subprocess.Popen([sys.executable, "-c",
                                 "import time; time.sleep(60)"])
        try:
            time.sleep(3)
            r = _run(["--log", str(log), "--pid", str(idle.pid),
                      "--stall-seconds", "1", "--interval", "2",
                      "--heartbeat-minutes", "99", "--max-hours", "0.0028"],
                     timeout=120)
        finally:
            idle.kill(); idle.wait()
        assert "STALLED" in r.stdout, (
            f"an idle silent process was NOT reported, so the alarm is now "
            f"blind; stdout: {r.stdout}")

    def test_cpu_seconds_parses_the_platform_format_and_degrades_to_none(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("cywd", WD)
        m = importlib.util.module_from_spec(spec)
        sys.modules["cywd"] = m
        spec.loader.exec_module(m)
        mine = m._cpu_seconds(os.getpid())
        assert mine is not None and mine >= 0.0, mine
        assert m._cpu_seconds(None) is None
        assert m._cpu_seconds(9999999) is None, "a dead pid must not fabricate a time"


class TestTheOutcomeIsReadNotInferred:
    """A halt and a convergence must NOT look alike. Panel finding, 2026-10-02.

    cc2, verbatim: *"it goes silent whenever the run TERMINATES WITHOUT WRITING
    A TROUBLE TOKEN INTO THE LOG — and then it reports that silence as success.
    A halted-INCOMPLETE run and a clean convergence produced byte-identical
    output and the same exit code 0."* Reproduced on live code before the fix.
    """

    def _ended_run(self, tmp_path, signal):
        tmp_path.mkdir(parents=True, exist_ok=True)
        (tmp_path / "round_00.json").write_text("{}", encoding="utf-8")
        if signal is not None:
            (tmp_path / "completion_signal.json").write_text(
                json.dumps(signal), encoding="utf-8")
        log = tmp_path / "run.log"
        log.write_text("dispatching seats\nround 0 complete\nwriting report\n",
                       encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        return _run(["--log", str(log), "--pid", str(dead.pid),
                     "--once", "--interval", "1", "--stall-seconds", "3600"])

    def test_a_clean_convergence_is_reported_clean(self, tmp_path):
        r = self._ended_run(tmp_path, {"status": "CONVERGED",
                                       "reason": "CRITICAL_QUIESCENCE_CONVERGED"})
        assert "OUTCOME CLEAN" in r.stdout, r.stdout
        assert r.returncode == 0

    def test_a_halt_is_reported_bad_and_does_not_exit_zero(self, tmp_path):
        r = self._ended_run(tmp_path, {"status": "INCOMPLETE",
                                       "reason": "HALTED_IRREDUCIBLE_QUEUE_ALARM"})
        assert "OUTCOME BAD" in r.stdout, r.stdout
        assert r.returncode == 0, (
            "the exit contract is untouched; a halt is distinguished by its "
            "OUTCOME line, which is what wakes the model")

    def test_the_two_are_distinguishable(self, tmp_path):
        """THE EXACT COMPARISON THE SEAT MADE. Before the fix these were equal."""
        a = self._ended_run(tmp_path / "a", {"status": "CONVERGED",
                                             "reason": "CRITICAL_QUIESCENCE_CONVERGED"})
        b = self._ended_run(tmp_path / "b", {"status": "INCOMPLETE",
                                             "reason": "HALTED_IRREDUCIBLE_QUEUE_ALARM"})
        assert "OUTCOME CLEAN" in a.stdout and "OUTCOME BAD" in b.stdout
        assert a.stdout != b.stdout, (
            "a halt and a convergence are still indistinguishable")

    def test_an_unrecorded_verdict_is_its_own_third_class(self, tmp_path):
        """NO_SIGNAL is not a kind of BAD: an unrecorded end cannot be acted on."""
        r = self._ended_run(tmp_path, None)
        assert "OUTCOME NO_SIGNAL" in r.stdout, r.stdout

    def test_a_corrupt_verdict_file_is_reported_not_guessed(self, tmp_path):
        (tmp_path / "round_00.json").write_text("{}", encoding="utf-8")
        (tmp_path / "completion_signal.json").write_text("{not json",
                                                         encoding="utf-8")
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid), "--once",
                  "--interval", "1", "--stall-seconds", "3600"])
        assert "OUTCOME UNREADABLE" in r.stdout, r.stdout

    def test_the_outcome_is_spoken_even_when_the_watchdog_gives_up(self, tmp_path):
        """Every exit path, not just the tidy one."""
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--interval", "1",
                  "--heartbeat-minutes", "99", "--max-hours", "0.0004"],
                 timeout=90)
        assert "OUTCOME" in r.stdout, r.stdout
        assert r.returncode == 1, "gave up without the run ending"


class TestTheVerdictCanLiveElsewhere:
    """The run's verdict is not always beside the console log.

    `run_simulated_experiment.py` writes its artefacts into a TIMESTAMPED
    directory it names itself, while the console log sits wherever the operator
    redirected it. Assuming they share a parent reported NO_SIGNAL for a clean
    convergence -- the false-negative twin of the defect the cc2 seat found,
    caught on the first real launch before the run ended rather than after.
    """

    def test_the_outcome_is_read_from_the_named_directory(self, tmp_path):
        logdir, rundir = tmp_path / "console", tmp_path / "run_20261002T0351Z"
        logdir.mkdir(); rundir.mkdir()
        log = logdir / "run.log"
        log.write_text("dispatching\n", encoding="utf-8")
        (rundir / "completion_signal.json").write_text(
            json.dumps({"status": "CONVERGED",
                        "reason": "CRITICAL_QUIESCENCE_CONVERGED"}),
            encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid), "--once",
                  "--interval", "1", "--stall-seconds", "3600",
                  "--outcome-dir", str(rundir)])
        assert "OUTCOME CLEAN" in r.stdout, r.stdout

    def test_without_the_flag_it_still_reads_the_logs_own_directory(self, tmp_path):
        """ANTI-REGRESSION: the default must not have moved."""
        (tmp_path / "completion_signal.json").write_text(
            json.dumps({"status": "INCOMPLETE", "reason": "HALTED_X"}),
            encoding="utf-8")
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid), "--once",
                  "--interval", "1", "--stall-seconds", "3600"])
        assert "OUTCOME BAD" in r.stdout, r.stdout

    def test_a_wrong_outcome_dir_says_no_signal_rather_than_guessing(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid), "--once",
                  "--interval", "1", "--stall-seconds", "3600",
                  "--outcome-dir", str(tmp_path / "nowhere")])
        assert "OUTCOME NO_SIGNAL" in r.stdout, r.stdout

    def test_rounds_are_counted_in_the_runs_own_directory(self, tmp_path):
        """THE TWIN OF THE OUTCOME DEFECT, found from a live heartbeat.

        A heartbeat reported "0 round(s) landed" while the console showed the
        run in ROUND 1, because the artefacts live in the run's own timestamped
        directory and this counted beside the console log. Fixing `read_outcome`
        alone left its twin, which is the shape this project keeps finding: a
        monitoring channel reporting a false number is the defect the whole
        script exists to remove.
        """
        import importlib.util
        logdir, rundir = tmp_path / "console", tmp_path / "run_20261002T0442Z"
        logdir.mkdir(); rundir.mkdir()
        log = logdir / "run.log"
        log.write_text("x\n", encoding="utf-8")
        (rundir / "round_00.json").write_text("{}", encoding="utf-8")
        (rundir / "round_01.json").write_text("{}", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("cywd_rc", WD)
        m = importlib.util.module_from_spec(spec)
        sys.modules["cywd_rc"] = m
        spec.loader.exec_module(m)
        assert m._round_count(log) == 0, "the console directory holds no rounds"
        assert m._round_count(log, rundir) == 2, (
            "rounds are not read from the run's own directory")

    def test_the_heartbeat_reports_the_real_round_count(self, tmp_path):
        logdir, rundir = tmp_path / "c", tmp_path / "r"
        logdir.mkdir(); rundir.mkdir()
        log = logdir / "run.log"
        log.write_text("x\n", encoding="utf-8")
        (rundir / "round_00.json").write_text("{}", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid), "--once",
                  "--interval", "1", "--stall-seconds", "3600",
                  "--outcome-dir", str(rundir)])
        assert "1 round(s) landed" in r.stdout, r.stdout



def _probe_module():
    """Import the watchdog so its functions can be CALLED, not described.

    The subprocess tests above cover the end-to-end channel. These call
    `probe` directly because the property under test is a DIFFERENCE between
    two argument values (`first=True` vs `first=False`) on identical input,
    and a differential is the only form of evidence that a narrowing actually
    narrowed something.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("cyw", str(WD))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestABacklogIsSummarisedNotReplayed:
    """RE-ARMING MUST NOT FLOOD. Measured on run 1b: arming replayed all 28
    matching lines of a 42,695-byte log, the notification was cut with
    "...(truncated)", and because the replay runs oldest-first the lines it
    dropped were the NEWEST. Re-arming every 30 minutes is by design, so the
    loss recurred every 30 minutes."""

    def _log_with(self, tmp_path, n):
        log = tmp_path / "run.log"
        log.write_text("".join(f"Traceback: historical failure {i}\n"
                               for i in range(n)), encoding="utf-8")
        return log

    def test_a_large_backlog_is_summarised_on_the_arming_probe(self, tmp_path, capsys):
        m = _probe_module()
        log = self._log_with(tmp_path, 28)
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=True)
        out = capsys.readouterr().out
        assert "BACKLOG: the log already held 28 problem line(s)" in out, out
        assert out.count("BACKLOG LINE") == 3, out
        assert "TROUBLE" not in out, (
            "the arming probe still replayed the backlog line by line, which "
            f"is the lossy flood this guards: {out}")

    def test_the_three_named_lines_are_the_NEWEST_not_the_oldest(self, tmp_path, capsys):
        """THE WHOLE POINT. A truncated flood keeps the oldest and drops the
        newest; the summary must do the opposite."""
        m = _probe_module()
        log = self._log_with(tmp_path, 28)
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=True)
        out = capsys.readouterr().out
        # ANCHORED TO END-OF-LINE. The first version of this assertion used a
        # bare `in` and failed: "historical failure 2" is a SUBSTRING of
        # "historical failure 25", so the test reported the oldest lines as
        # present when they were absent. Same wrong-predicate shape as the
        # inventory substring collisions already on this project's record --
        # the instrument was wrong, not the subject.
        import re as _re
        for i in (25, 26, 27):
            assert _re.search(rf"historical failure {i}$", out, _re.M), (
                f"newest line {i} missing: {out}")
        for i in (0, 1, 2):
            assert not _re.search(rf"historical failure {i}$", out, _re.M), (
                f"oldest line {i} kept instead of the newest: {out}")

    def test_a_small_backlog_is_STILL_replayed_verbatim(self, tmp_path, capsys):
        """NOT VACUOUS. 14 regex tests above write ONE line before arming and
        assert on the event. Summarising at any size would make every one of
        them assert against a channel nothing reaches."""
        m = _probe_module()
        log = self._log_with(tmp_path, 1)
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=True)
        out = capsys.readouterr().out
        assert "TROUBLE" in out and "BACKLOG" not in out, out

    def test_growth_after_arming_is_never_summarised(self, tmp_path, capsys):
        """A live crashloop writing 28 lines mid-run must produce 28 events.
        The summary is an ARMING concession, not a volume cap."""
        m = _probe_module()
        log = self._log_with(tmp_path, 28)
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=False)
        out = capsys.readouterr().out
        assert out.count("TROUBLE") == 28, out
        assert "BACKLOG" not in out, out

    def test_the_old_behaviour_is_demonstrably_GONE(self, tmp_path, capsys):
        """MUTATION-STYLE. If `first` changed nothing, these two counts agree
        and this file would have passed over the defect."""
        m = _probe_module()
        log = self._log_with(tmp_path, 28)
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=True)
        armed = capsys.readouterr().out.count("TROUBLE")
        m.probe(log, os.getpid(), 0, 0, time.time(), 0, 3600, None, None, first=False)
        live = capsys.readouterr().out.count("TROUBLE")
        assert armed == 0 and live == 28, (
            f"arming emitted {armed} and live emitted {live}; equal counts mean "
            f"the `first` argument is wired to nothing")

    def test_a_post_arm_failure_still_wakes_end_to_end(self, tmp_path):
        """THE CHANNEL THAT MATTERS, through the real subprocess. A summarised
        backlog must not cost the live alarm."""
        log = self._log_with(tmp_path, 8)
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            wd = subprocess.Popen(
                [sys.executable, str(WD), "--log", str(log), "--pid", str(child.pid),
                 "--stall-seconds", "3600", "--interval", "1"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(2.5)
            with log.open("a", encoding="utf-8") as fh:
                fh.write("Traceback (most recent call last):\n")
                fh.write("RuntimeError: the seat died after the watch armed\n")
            time.sleep(3.0)
            child.terminate()
            child.wait(timeout=10)      # REAP: an unreaped child is a zombie,
            # and a zombie is covered by its own test below.
            out, _ = wd.communicate(timeout=30)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)
        assert "BACKLOG: the log already held 8 problem line(s)" in out, out
        assert "TROUBLE" in out, f"the post-arm crash did not wake it: {out}"
        assert "after the watch armed" in out, out
        assert "PROCESS GONE" in out, out


class TestProseIsNotAnAlarm:
    """A token that is also ordinary English is not evidence. Third and fourth
    instances of the shape, after `0 failed` and `401`-inside-a-timestamp."""

    @pytest.mark.parametrize("prose", [
        # all six measured in run 1b's own log, all benign
        "refused. This is NOT a verdict: the finding is neither confirmed nor",
        "[07:06:47]   corrected copies: 9 accepted, 0 refused, 7 unmatched",
        "[06:40:09]   gamma_critical: 0.000 (continuous decay-curve diagnostic)",
        "[06:40:09]   gamma-alt: critical-quiescence too early (round 0 < 3)",
        "the control cannot reach the target it reads and cannot test whether",
        "bench/decay_analysis.py:54: OptimizeWarning: Covariance of the "
        "parameters could not be estimated",
    ])
    def test_the_runs_own_explanatory_prose_is_not_an_alarm(self, tmp_path, prose):
        log = tmp_path / "run.log"
        log.write_text(prose + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, (
            f"{prose[:60]!r} cried wolf: {r.stdout}")

    @pytest.mark.parametrize("real", [
        "[06:05:53]   corrected copy REFUSED C0007 from Fable-SIM",
        "CRITICAL:immune.pipeline:the pipeline aborted",
        "HALTED_IRREDUCIBLE_QUEUE_ALARM at round 0",
    ])
    def test_the_uppercase_machine_token_still_speaks(self, tmp_path, real):
        """THE ANTI-REGRESSION. Both narrowed tokens have a real uppercase
        form and both must survive; `(?-i:)` keeps it while dropping prose."""
        log = tmp_path / "run.log"
        log.write_text(real + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" in r.stdout, f"{real!r} went silent: {r.stdout}"

    def test_what_the_narrowing_GIVES_UP_is_recorded_as_intended(self, tmp_path):
        """STATED, NOT DISCOVERED. A line whose only evidence is the bare word
        "cannot" no longer speaks. This test exists so that the loss is a
        decision on the record rather than a surprise in six weeks."""
        log = tmp_path / "run.log"
        log.write_text("the allocator cannot find a free page\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, r.stdout
        # the same failure WITH an error token is still caught
        log.write_text("MemoryError: the allocator cannot find a free page\n",
                       encoding="utf-8")
        r2 = _run(["--log", str(log), "--pid", str(os.getpid()),
                   "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" in r2.stdout, r2.stdout


class TestAFinishedRunIsNotAliveBecauseItsPidLingers:
    """A ZOMBIE PASSES `os.kill(pid, 0)`. An exited process whose parent has
    not reaped it keeps its pid and accepts signal 0, so the liveness check
    called a FINISHED run alive. Found by the end-to-end test above hanging
    for its full timeout waiting for a PROCESS GONE that could not come."""

    def test_an_unreaped_exited_process_is_reported_GONE(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            child.terminate()
            time.sleep(0.5)             # exited, deliberately NOT reaped
            r = _run(["--log", str(log), "--pid", str(child.pid),
                      "--stall-seconds", "3600", "--interval", "1"], timeout=30)
            assert "PROCESS GONE" in r.stdout, (
                f"a zombie was read as a live run, so the end of a run goes "
                f"unreported until the stall threshold expires: {r.stdout}")
        finally:
            child.wait(timeout=10)

    def test_a_genuinely_running_process_is_NOT_reported_gone(self, tmp_path):
        """ANTI-FALSE-POSITIVE. The state check must not call a live run dead;
        `S`, `R`, `SN` and `R+` are all running states."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "PROCESS GONE" not in r.stdout, r.stdout
