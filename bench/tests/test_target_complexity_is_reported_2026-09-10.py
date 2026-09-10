"""Tasks 4.3 and R11: complexity is REPORTED and reaches no decision.

HIS RULING, VERBATIM, 2026-09-09: "Yes we should measure complexity and make it a
reported statistic in our reported results at the end of each experiment. But
maybe as an informative statistic only, since I don't think you are saying if
measuring it should also change behaviour too?"

BOTH HALVES ARE HELD HERE, because either alone is worthless. That the statistic
is produced, and that it does NOT reach the fix-admission gate. A statistic that
were quietly wired into a decision would satisfy the first and violate the
ruling.

WHAT THIS TEST DOES NOT DO, said plainly rather than implied. It does not drive a
full experiment, which needs live model dispatch. Reachability is established by
AST -- the project's own idiom, chosen on 2026-09-09 after a grep matched
`sk_enabled` inside `inround_reask_enabled` -- and the statistic's substance is
established by EXECUTING the measuring function on real text.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "bench" / "reference_runner_v3.py"
SCRIPT = ROOT / "scripts" / "nu_carries_complexity_moves_the_gate_2026-09-10.py"
sys.path.insert(0, str(ROOT / "bench"))


@pytest.fixture(scope="module")
def tree():
    return ast.parse(RUNNER.read_text(encoding="utf-8"))


def _calls(tree, name):
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and ((isinstance(n.func, ast.Name) and n.func.id == name)
                 or (isinstance(n.func, ast.Attribute) and n.func.attr == name))]


class TestItIsActuallyReached:
    def test_compute_gamma_input_now_has_a_call_site(self, tree):
        """It was IMPORTED at :221 and called nowhere.

        An addition nothing reaches is not additive -- the standard's symmetric
        half, and task 4.3's own words: "its measuring module is unreached".
        """
        assert _calls(tree, "compute_gamma_input"), (
            "compute_gamma_input is imported by the live runner and never "
            "called, which is the exact defect 4.3 was raised for")

    def test_the_statistic_is_written_into_the_result(self, tree):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"target_complexity"' in src
        assert 'result["target_complexity"]' in src, (
            "the statistic is computed and not stored, so it reaches no report")


class TestItReachesNoDecision:
    def test_the_gate_never_receives_the_complexity_value(self, tree):
        """THE RULING'S OTHER HALF. gamma_input must not feed the gate.

        Every call to the fix-admission gate is inspected and none may pass an
        argument derived from the complexity measurement.
        """
        forbidden = {"gamma_input", "target_complexity", "_cx"}
        for call in (_calls(tree, "check_sk_threshold_corrected")
                     + _calls(tree, "check_sk_threshold")):
            names = {n.id for n in ast.walk(call) if isinstance(n, ast.Name)}
            names |= {n.attr for n in ast.walk(call) if isinstance(n, ast.Attribute)}
            leak = names & forbidden
            assert not leak, (
                f"the fix-admission gate receives {sorted(leak)}, so complexity "
                f"is no longer informative-only and his ruling is violated")

    def test_an_assumed_value_cannot_be_read_as_a_measurement(self):
        """The near-miss this task actually produced.

        Below MIN_WINDOWS the measuring function returns an ASSUMED beta of 0.5
        with r_squared 0. Every ordinary code target is below that threshold at
        the default window, so the report would have carried gamma_input 0.5 in
        a field a reader takes as measured. The record must distinguish them.
        """
        src = RUNNER.read_text(encoding="utf-8")
        # THREE STATES SINCE ROUND 8 (2026-09-10), and this assert must match
        # the code it guards or it guards nothing: a zero-token target takes
        # the module's EMPTY-INPUT return of gamma 1.0, not the 0.5
        # assumed-default, so "ASSUMED_DEFAULT" would have promised a value
        # the field does not hold. The prior exact-string assert pinned the
        # two-state form and went red the moment the fix landed -- caught by
        # the second round-8 seat running this file after the first seat's
        # fix; the fix and its guard must move together.
        assert '"fit": ("measured" if _measured' in src, (
            "the stored record no longer distinguishes a fit from a default")
        assert '"NO_TOKENS"' in src and '"ASSUMED_DEFAULT"' in src, (
            "the record no longer separates the zero-token empty-input value "
            "from the below-window assumed default; one of them is lying")
        assert "NOT MEASURED" in src, (
            "the reading shipped beside an assumed value no longer says it is "
            "assumed")

    def test_the_stored_record_says_so_in_its_own_fields(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"informative_only": True' in src, (
            "the record does not declare itself informative-only, so a later "
            "reader cannot tell the ruling from an accident")


class TestTheSubstanceIsExecuted:
    def test_high_gamma_really_does_mean_simple(self):
        """The direction is counter-intuitive, so it is executed, not asserted.

        A repetitive text saturates its vocabulary and scores HIGH; a text whose
        vocabulary keeps growing scores LOW. If this ever inverts, every
        interpretation written beside the number becomes wrong.
        """
        from input_complexity import MIN_WINDOWS, compute_gamma_input
        repetitive = ("the cat sat on the mat " * 400)
        novel = " ".join(f"word{i} token{i} lexeme{i}" for i in range(1200))
        # SIZED SO A FIT ACTUALLY HAPPENS. At the default 10,000-char window
        # both texts fell below MIN_WINDOWS and BOTH returned the assumed 0.5,
        # so the first version of this test compared 2 defaults to each other
        # and would have passed for any direction at all.
        from input_complexity import tokenize
        def fit(text):
            n = len(tokenize(text))
            return compute_gamma_input(
                text, window_size=max(4, (4 * n) // (MIN_WINDOWS * 2)))
        simple, complex_ = fit(repetitive), fit(novel)
        assert simple.n_windows >= MIN_WINDOWS, simple
        assert complex_.n_windows >= MIN_WINDOWS, complex_
        # r_squared is NOT the test of a real fit, and asserting it was wrong.
        # The repetitive text saturates at a constant 3-word vocabulary, so the
        # regression has zero variance to explain and returns r_squared 0.0
        # while beta 0.0 and gamma 1.0 are exactly correct. `n_windows` against
        # MIN_WINDOWS is what separates a fit from the assumed default, which is
        # why the runner keys its ASSUMED_DEFAULT flag on that and not on this.
        assert simple.gamma > complex_.gamma, (
            f"repetitive text scored {simple.gamma:.4f} and novel text "
            f"{complex_.gamma:.4f}; the reading shipped beside the statistic "
            f"says high gamma is simple")

    def test_it_returns_a_usable_number_on_a_real_target(self):
        from input_complexity import MIN_WINDOWS, compute_gamma_input
        target = ROOT / "bench" / "dm" / "_memory.py"
        assert target.is_file()
        text = target.read_text(encoding="utf-8")
        # THE DEFAULT WINDOW CANNOT FIT AN ORDINARY TARGET, and that is the
        # point of this test rather than an inconvenience. 20,605 bytes against
        # a 10,000-char window is under MIN_WINDOWS, so the default returns the
        # ASSUMED 0.5. The runner therefore re-windows; this asserts that the
        # default really does fail, so the re-windowing is not decoration.
        at_default = compute_gamma_input(text)
        assert at_default.n_windows < MIN_WINDOWS, (
            "the default window now fits this target, so the runner's "
            "re-windowing may no longer be needed -- check before removing it")
        assert at_default.gamma == 0.5 and at_default.r_squared == 0.0, (
            "the below-threshold fallback is no longer the assumed 0.5; the "
            "runner's 'ASSUMED_DEFAULT' flag is keyed to that value")
        from input_complexity import tokenize
        n_tokens = len(tokenize(text))
        # THE RATIO IS NOT 4:1 AND THAT IS WHY THE WINDOW IS COUNTED, NOT GUESSED.
        assert len(text) / n_tokens > 8, (
            "this repository's code no longer runs far from the module's assumed "
            "4:1 chars-to-tokens, so the runner's re-windowing rationale changed")
        r = compute_gamma_input(
            text, window_size=max(4, (4 * n_tokens) // (MIN_WINDOWS * 2)))
        assert r.n_windows >= MIN_WINDOWS, r
        assert 0.0 <= r.gamma <= 1.0, r
        assert r.r_squared > 0.9, f"re-windowing produced a poor fit: {r}"


class TestTheFigureBehindTheDecision:
    def test_the_84_percent_now_has_a_producing_script(self):
        assert SCRIPT.is_file()

    def test_it_reproduces_the_recorded_figure(self):
        """570 of 676 was prose until 2026-09-10. It is now executed.

        The first attempt to check it swept the wrong box and got 645 of 676,
        and was about to report that the recorded figure did not reproduce. It
        does. This test pins the box as well as the count, because the box is
        what the first attempt got wrong.
        """
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-500:]
        assert "570 of 676" in r.stdout or "differs from the shipped verdict: 570" in r.stdout
        assert "84.3%" in r.stdout
        assert "[0, 0.5] squared" in r.stdout, "the box is no longer stated"

    def test_the_conclusion_survives_the_other_box(self):
        """If it only held on one box, the box would be doing the work."""
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert "645 of 676" in r.stdout and "95.4%" in r.stdout
