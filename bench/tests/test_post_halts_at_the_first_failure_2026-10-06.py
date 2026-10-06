#!/usr/bin/env python3
"""The preflight POST prints pass/fail per check and HALTS at the first failure.

THE FOUNDER'S RULING, 2026-10-06, verbatim: *"on a bios screen when 'booting up' it
prints a simple message against each check, which is just 'pass or fail'. If a test
passes then the next check fails, the system is halted, giving the user an
opportunity to investigate. This fits an early paradigm as CDSFL as an 'operating
system', that can operate over many models and many systems independently of the
underlying system itself."*

It overrules the first version of `preflight_health_check_2026-10-06.py`, which
reported 3 states (GREEN/AMBER/RED) and deliberately did not block. The reasoning
given there was that "a health check that silently blocks is worse than none". A HALT
is not silent: it names the failing check, stops, and hands the operator the machine.

AND THE 3-STATE SCHEME WAS HIDING A DEFECT OF EXACTLY THE KIND THE CHECK EXISTS FOR.
AMBER never set the exit code, and a check whose own code raised was mapped to AMBER,
so A BROKEN CHECK BOOTED -- measured at exit 0 by
`scripts/post_semantics_2026-10-06.py` part 1 against the previous version. A guard
that cannot fail is not a guard. `test_a_check_that_raises_is_a_failure` below is the
regression test for that, and it fails against the old behaviour.

EVERY ASSERTION CALLS THE CHECK. None reads its source for a claim about behaviour;
the 2 that parse source are asserting that a CALLER EXISTS, which is a structural
claim and the only kind source-reading can settle.
"""
import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SEATS = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM", "Gemini-SIM",
         "Fable-SIM"]


def _fresh():
    """A fresh module each time: the tests mutate CHECKS and must not leak."""
    spec = importlib.util.spec_from_file_location(
        "cdsfl_post_under_test",
        REPO / "scripts" / "preflight_health_check_2026-10-06.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def post():
    return _fresh()


class TestTheBootHalts:
    def test_a_failure_stops_the_checks_after_it(self, post):
        real = list(post.CHECKS)
        post.CHECKS = [
            real[0],
            ("injected", lambda: (post.FAIL, "injected failure", []), False),
            real[2], real[3], real[4],
        ]
        rows = post.run_checks(SEATS)
        statuses = [r[1] for r in rows]
        assert statuses[1] == post.FAIL
        assert statuses[2:] == [post.NOT_RUN] * 3, (
            f"the boot continued past a failure: {statuses}. The founder's ruling "
            f"is that the system halts so the operator can investigate.")

    def test_a_halt_exits_non_zero(self, post):
        post.CHECKS = [("injected", lambda: (post.FAIL, "x", []), False)]
        assert post.main([f"--seats={','.join(SEATS)}"]) == 1

    def test_not_run_is_not_counted_as_a_pass(self, post):
        real = list(post.CHECKS)
        post.CHECKS = [("injected", lambda: (post.FAIL, "x", []), False), real[1]]
        rows = post.run_checks(SEATS)
        assert post.PASS not in [r[1] for r in rows], (
            "a row that never ran was reported as a pass")


class TestABrokenCheckCannotBoot:
    def test_a_check_that_raises_is_a_failure(self, post):
        """REGRESSION. The previous version mapped this to a 3rd state and exited 0."""
        def explodes():
            raise RuntimeError("this check's own code is broken")
        post.CHECKS = [("broken", explodes, False)]
        rows = post.run_checks(SEATS)
        assert rows[0][1] == post.FAIL, (
            "a check whose own code raised did not fail the boot, so a broken "
            "guard guards nothing")
        assert post.main([f"--seats={','.join(SEATS)}"]) == 1

    def test_the_raising_check_names_its_exception(self, post):
        def explodes():
            raise KeyError("a_missing_key")
        post.CHECKS = [("broken", explodes, False)]
        _, _, headline, _ = post.run_checks(SEATS)[0]
        assert "KeyError" in headline, (
            f"the operator is not told what broke: {headline!r}")


class TestDiagnosticMode:
    def test_all_runs_every_check_despite_an_early_failure(self, post):
        real = list(post.CHECKS)
        post.CHECKS = [("injected", lambda: (post.FAIL, "x", []), False)] + real[1:]
        rows = post.run_checks(SEATS, run_all=True)
        assert post.NOT_RUN not in [r[1] for r in rows]
        assert post.FAIL in [r[1] for r in rows], (
            "diagnostic mode hid the failure it exists to enumerate")


class TestTheLadderCheckMeasuresTheRunNotADefault:
    def test_uniform_seat_models_fails(self, post):
        st, head, _ = post.check_capability_ladder_climbs(
            SEATS, seat_models="uniform")
        assert st == post.FAIL and "cannot climb" in head

    def test_ladder_seat_models_passes(self, post):
        st, _, _ = post.check_capability_ladder_climbs(SEATS, seat_models="ladder")
        assert st == post.PASS

    def test_the_resolved_value_beats_the_declared_default(self, post):
        """A caller that overrode the flag must not be judged on the default.

        This is the error the check itself exists to catch -- measuring a
        configuration other than the one about to run -- and it was committed
        twice in this file's own history before being caught.
        """
        declared = post._launcher_seat_models()
        other = "ladder" if declared != "ladder" else "uniform"
        a, _, _ = post.check_capability_ladder_climbs(SEATS, seat_models=declared)
        b, _, _ = post.check_capability_ladder_climbs(SEATS, seat_models=other)
        assert a != b, (
            f"passing seat_models={other!r} gave the same verdict as the declared "
            f"default {declared!r}, so the resolved value is being ignored")

    def test_a_deliberate_uniform_control_arm_is_a_pass(self, post):
        st, head, _ = post.check_capability_ladder_climbs(
            SEATS, seat_models="uniform", expect_uniform=True)
        assert st == post.PASS and "BY REQUEST" in head

    def test_a_uniform_ladder_mapping_fails_even_in_ladder_mode(self, post):
        """ANTI-VACUITY. If every rung resolves to 1 model the ladder is inert
        however the flag is set, and the check must still say so."""
        from bench.tools import sim_dispatch_shim as SHIM
        saved = dict(SHIM.DEFAULT_LADDER)
        try:
            for k in SHIM.DEFAULT_LADDER:
                SHIM.DEFAULT_LADDER[k] = "opus"
            st, _, _ = post.check_capability_ladder_climbs(
                SEATS, seat_models="ladder")
            assert st == post.FAIL
        finally:
            SHIM.DEFAULT_LADDER.clear()
            SHIM.DEFAULT_LADDER.update(saved)

    def test_a_single_seat_roster_is_not_a_failure(self, post):
        st, head, _ = post.check_capability_ladder_climbs(
            ["Fable-SIM"], seat_models="ladder")
        assert st == post.PASS, (
            "a 1-seat roster has no rung above the source, which is a legitimate "
            "pre-registered arm, not an inert ladder")


class TestTheLauncherActuallyRunsIt:
    """An addition nothing reaches is not additive. Parsed, because the claim is
    structural: does a caller exist at all."""

    def test_the_simulated_runner_calls_the_post(self):
        src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
            encoding="utf-8")
        calls = [n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.Call)
                 and (getattr(n.func, "id", None)
                      or getattr(n.func, "attr", None)) == "_run_post"]
        assert calls, (
            "run_simulated_experiment.py never calls _run_post, so the POST is a "
            "script an operator must remember to run rather than a gate")

    def test_the_launcher_passes_its_own_resolved_seat_models(self):
        """EXECUTED, not read. The launcher is CALLED and the argv it hands POST is
        captured, because a source match proves only that the module describes
        itself consistently -- it cannot catch a producer and a consumer that
        disagree."""
        sys.path.insert(0, str(REPO / "bench" / "tools"))
        import importlib
        mod = importlib.import_module("run_simulated_experiment")
        seen = {}

        class _Args:
            seat_models = "ladder"
            expect_uniform_ladder = False

        import importlib.util as _iu
        real_spec = _iu.spec_from_file_location
        captured = []

        def _fake_exec(mod_obj):
            mod_obj.main = lambda argv: captured.append(list(argv)) or 0

        # Intercept the POST module the launcher loads, and record its argv.
        class _FakeSpec:
            def __init__(self, loader):
                self.loader = loader

        def _spec(name, path):
            sp = real_spec(name, path)
            orig = sp.loader.exec_module

            def exec_module(m):
                orig(m)
                m.main = lambda argv: (captured.append(list(argv)), 0)[1]
            sp.loader.exec_module = exec_module
            return sp

        _iu.spec_from_file_location = _spec
        try:
            rc = mod._run_post(["A-SIM", "B-SIM"], _Args())
        finally:
            _iu.spec_from_file_location = real_spec
        assert captured, "the launcher never invoked the POST module's main()"
        argv = captured[-1]
        assert "--seat-models=ladder" in argv, (
            f"the launcher did not pass its RESOLVED seat-models value; argv was "
            f"{argv}. Letting POST re-derive it from a declared default is wrong "
            f"the moment the flag is overridden.")
        assert rc == 0

    def test_a_post_that_cannot_load_is_not_a_pass(self):
        """The trap re-set one level up: swallowing an import error and booting."""
        sys.path.insert(0, str(REPO / "bench" / "tools"))
        import importlib
        mod = importlib.import_module("run_simulated_experiment")

        class _Args:
            seat_models = "ladder"
            expect_uniform_ladder = False

        real = mod.REPO
        try:
            mod.REPO = REPO / "no" / "such" / "place"
            assert mod._run_post(SEATS, _Args()) != 0, (
                "a POST that could not be loaded returned success")
        finally:
            mod.REPO = real


class TestTheOrderIsSound:
    def test_the_post_order_is_topological(self):
        spec = importlib.util.spec_from_file_location(
            "post_semantics", REPO / "scripts" / "post_semantics_2026-10-06.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert m.part2_order_is_topological() is True

    def test_a_scrambled_order_is_rejected(self):
        """ANTI-VACUITY: the ordering check must be able to say no."""
        spec = importlib.util.spec_from_file_location(
            "post_semantics", REPO / "scripts" / "post_semantics_2026-10-06.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        bad = list(reversed(m.POST_ORDER))
        assert m.part2_order_is_topological(bad) is False

    def test_the_live_checks_match_the_declared_order(self):
        post = _fresh()
        spec = importlib.util.spec_from_file_location(
            "post_semantics", REPO / "scripts" / "post_semantics_2026-10-06.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert [c[0] for c in post.CHECKS] == m.POST_ORDER, (
            "the order z3 verified is not the order the checks run in")
