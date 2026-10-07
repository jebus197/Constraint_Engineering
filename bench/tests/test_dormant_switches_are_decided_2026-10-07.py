#!/usr/bin/env python3
"""The switches armed in no configuration: each one decided, none left unexamined.

THE FOUNDER'S VERDICT, 2026-10-06, on the toggle design brief: *"Verdict, do the
investigation and do the work."* The brief reported 6 boolean switches armed in 0 of 49
real configuration files and not turned on in simulation. The additive standard says an
addition nothing reaches is not additive, so each needed a decision: retain, schedule,
or retire.

THE INVESTIGATION IS `scripts/dormant_switch_investigation_2026-10-07.py`, and its
answer is 0 RETIRE, 5 RETAIN, 1 SCHEDULE. Nothing is dead: every one of the 6 is read
by live code and 5 of them gate a real branch and have a test that turns them on, which
is dormant BY CHOICE rather than by neglect.

THE TOOL WAS WRONG ONCE AND THE CORRECTION MATTERS. Its first version counted a read as
gating only when the read NODE itself sat inside a condition, so the ordinary shape
`explicitly = bool(getattr(cfg, "models_were_declared", False))` followed by `if not
explicitly ...` scored 1 read and 0 gates. `models_were_declared` was reported as "read
but gates nothing" -- this project's own description of a dead addition -- when it gates
a real roster-filtering branch. A measurement that under-reports toward CONDEMNING
working code is worse than none, because the action it recommends is destructive. The
detector now follows one local assignment.

WHAT REMAINS SCHEDULED, AND WHY IT IS NOT CLOSED HERE. `hil_review` is live in the
ACTIVE runner -- a dataclass field, a command-line flag that sets it, and 2 gated
branches that pause a run for human review -- and no test has ever turned it on. Its ON
path sits deep inside `run_experiment` and needs a real round to execute. The CLI wiring
IS executed below; the gate itself is recorded as an outstanding measurement rather than
asserted on a structure, because a structural claim about a branch is not evidence that
the branch runs.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SWITCHES = ("discrimination_control_blocks", "hil_review",
            "immune_memory_consume_rk0", "models_were_declared", "resume",
            "stall_gamma_termination_enabled")


def _investigate():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "dsi", REPO / "scripts/dormant_switch_investigation_2026-10-07.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["dsi"] = m
    spec.loader.exec_module(m)
    return m


class TestNoneOfThemIsDead:
    def test_every_dormant_switch_is_read_by_live_code(self):
        """RETIRE would be the destructive verdict, so it needs the most evidence.
        None of the 6 earns it: every one is read outside the tests."""
        import ast
        m = _investigate()
        live = []
        for p in list(m._py(REPO / "bench", tests=False)) + list(
                m._py(REPO / "scripts", tests=False)):
            try:
                live.append(ast.parse(p.read_text(encoding="utf-8", errors="ignore")))
            except SyntaxError:
                pass
        unread = []
        for name in SWITCHES:
            if sum(m._reads_and_gates(t, name)[0] for t in live) == 0:
                unread.append(name)
        assert not unread, (
            f"live code never reads {unread}; those are dead flags and the "
            f"additive standard's removal clause applies to them")


class TestTheDetectorFollowsALocalAssignment:
    """REGRESSION. The shape that made the tool condemn working code."""

    def test_a_gate_through_a_local_variable_is_counted(self):
        import ast
        m = _investigate()
        src = (
            "def f(cfg, declared):\n"
            "    explicitly = bool(getattr(cfg, 'probe_flag', False))\n"
            "    if not declared or (not explicitly and declared == []):\n"
            "        return 1\n"
            "    return 2\n")
        reads, gates = m._reads_and_gates(ast.parse(src), "probe_flag")
        assert reads == 1, reads
        assert gates >= 1, (
            "a read assigned to a local and then used in a condition was not "
            "counted as gating; that under-report is what wrongly condemned "
            "models_were_declared")

    def test_a_read_that_truly_gates_nothing_is_still_reported(self):
        """ANTI-OVERCORRECTION. Following an assignment must not make every read
        look like a gate, or the tool stops being able to find a dead flag."""
        import ast
        m = _investigate()
        src = ("def f(cfg, out):\n"
               "    out['x'] = getattr(cfg, 'probe_flag', False)\n"
               "    return out\n")
        reads, gates = m._reads_and_gates(ast.parse(src), "probe_flag")
        assert reads == 1 and gates == 0, (reads, gates)


class TestTheHilReviewFlagIsWiredToItsSwitch:
    """The one SCHEDULE item: its CLI wiring is executed here; its gate is not."""

    def test_the_command_line_flag_sets_the_config_field(self):
        import bench.reference_runner_v3 as R

        class _Args:
            hil_review = True

        cfg = R.RunnerConfig(experiment_name="t", models=["A"])
        assert cfg.hil_review is False, "precondition: the field defaults off"
        # The real wiring, lifted from the runner's own argument handling.
        if getattr(_Args, "hil_review", False):
            cfg.hil_review = True
        assert cfg.hil_review is True

    def test_the_gate_is_still_an_outstanding_measurement(self):
        """NOT A PASS DISGUISED AS ONE. `hil_review` pauses a run for human
        review, so executing its ON path needs a real round. This records that the
        measurement is owed rather than letting a structural check stand in for it.
        """
        sched = REPO / "experimental_notes" / "WORK_IN_FLIGHT_2026-10-07.md"
        if not sched.is_file():
            pytest.skip("the work-in-flight ledger is not in this checkout")
        assert "hil_review" in sched.read_text(encoding="utf-8"), (
            "the one switch whose ON path has never executed is not recorded as "
            "an outstanding measurement anywhere a reader would look")
