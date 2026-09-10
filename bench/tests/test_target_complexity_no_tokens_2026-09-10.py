"""Round 8: `target_complexity` recorded gamma 1.0 beside prose saying 0.5.

THE DEFECT. `bench/reference_runner_v3.py`'s `target_complexity` block keys its
`fit` flag on `n_windows >= MIN_WINDOWS`, which is the RIGHT key. But it then
described every not-measured case as "the module's assumed default of 0.5",
and one not-measured case does not return 0.5. When a target tokenises to
nothing, `input_complexity.compute_gamma_input` returns early
(input_complexity.py:211) with `n_windows=0, beta=0.0, gamma=1.0` -- it never
reaches the assumed-default branch at :232. The report then carried
`gamma_input: 1.0`, the extreme "maximally simple" end of the scale, under a
`reading` asserting 0.5.

WHY IT IS ABOVE THRESHOLD. `gamma_input` is informative-only and reaches no
gate, so nothing is admitted or refused because of it. What it does reach is
the report a human reads. A run recording a value it did not measure, with
prose contradicting the value, is the failure this project spent 2026-09-09
naming: a fallback that looks like a measurement.

HOW THIS FILE TESTS THE REAL BLOCK RATHER THAN A COPY. The block is inline
inside a 13,000-line function, so it cannot be imported. It is therefore
LIFTED OUT OF THE SOURCE BY `ast` AND EXECUTED -- the actual statement node
from the actual file, compiled and run. Retyping the logic here would test the
retyping, which is the precise defect found in this round's C0053 control.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "bench" / "reference_runner_v3.py"
sys.path.insert(0, str(ROOT / "bench"))

from input_complexity import (  # noqa: E402
    MIN_WINDOWS as _IC_MIN_WINDOWS,
    WINDOW_SIZE_CHARS as _IC_WINDOW_CHARS,
    compute_gamma_input,
    tokenize as _ic_tokenize,
)

#: A target that tokenises to nothing. `tokenize` keeps only
#: `[a-zA-Z_][a-zA-Z0-9_]*` runs of more than 2 characters that are not
#: stopwords, so this is not a contrived string -- it is any non-Latin source.
NO_TOKEN_TARGET = "四七八九 五六 一二三 " * 500


def _lift_block():
    """Return the real `if "target_complexity" not in result:` node, compiled.

    Located by MATCHING THE SOURCE, not by line number, so the test does not
    rot the next time anything above it moves.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        t = node.test
        if (isinstance(t, ast.Compare)
                and isinstance(t.left, ast.Constant)
                and t.left.value == "target_complexity"
                and any(isinstance(o, ast.NotIn) for o in t.ops)):
            mod = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(mod)
            return compile(mod, str(RUNNER), "exec")
    raise AssertionError(
        "the `target_complexity` block is no longer an `if \"target_complexity\" "
        "not in result:` statement in reference_runner_v3.py -- this test can "
        "no longer find the code it checks and must be repointed, not deleted")


def _run_block(text: str) -> dict:
    """Execute the lifted block against `text`, supplying only its free names."""
    target = ROOT / "bench" / "tests" / "_no_token_target.tmp"
    target.write_text(text, encoding="utf-8")
    try:
        env = {
            "result": {},
            "_tgt_p": target,
            "_IC_WINDOW_CHARS": _IC_WINDOW_CHARS,
            "_IC_MIN_WINDOWS": _IC_MIN_WINDOWS,
            "compute_gamma_input": compute_gamma_input,
            "_ic_tokenize": _ic_tokenize,
            "round_idx": 0,
        }
        exec(_lift_block(), env)          # noqa: S102 - the point of the test
        return env["result"]["target_complexity"]
    finally:
        target.unlink(missing_ok=True)


class TestThePremiseIsReachable:
    def test_a_non_latin_target_tokenises_to_nothing(self):
        assert _ic_tokenize(NO_TOKEN_TARGET) == []

    def test_and_the_module_then_returns_gamma_one_not_half(self):
        """THE FALSIFIER for the premise. If this fails there is no defect."""
        cx = compute_gamma_input(NO_TOKEN_TARGET)
        assert cx.n_windows == 0
        assert cx.gamma == 1.0, (
            f"compute_gamma_input now returns gamma {cx.gamma} on empty input, "
            f"not 1.0, so the mismatch this file guards cannot arise")


class TestTheRealBlockNoLongerMisreportsIt:
    def test_the_prose_does_not_claim_a_number_the_field_does_not_hold(self):
        """THE FALSIFIER. Fails iff the report contradicts itself again."""
        tc = _run_block(NO_TOKEN_TARGET)
        gamma = tc["gamma_input"]
        assert gamma == 1.0, f"premise moved: gamma_input is {gamma}"
        assert "0.5" not in tc["reading"], (
            f"the reading still asserts 0.5 while gamma_input is {gamma}: "
            f"{tc['reading']!r}")
        assert str(gamma) in tc["reading"], (
            "the reading no longer quotes the value it sits beside, so the "
            "two can drift apart again silently")

    def test_the_not_measured_state_is_still_flagged(self):
        """The fix must not have bought consistency by claiming a measurement."""
        tc = _run_block(NO_TOKEN_TARGET)
        assert tc["fit"] == "NO_TOKENS", tc["fit"]
        assert tc["fit"] != "measured"
        assert tc["informative_only"] is True

    def test_a_real_code_target_is_still_reported_as_measured(self):
        """The additive standard: the fix must not disable the working path."""
        tc = _run_block((ROOT / "bench" / "dm" / "_memory.py")
                        .read_text(encoding="utf-8"))
        assert tc["fit"] == "measured", tc
        assert tc["n_windows"] >= _IC_MIN_WINDOWS
        assert 0.0 < tc["gamma_input"] < 1.0

    def test_a_short_target_still_says_assumed_default(self):
        """The THIRD state must survive: few-but-nonzero windows is not
        NO_TOKENS, and its prose must still quote 0.5 because that IS what the
        module returns there."""
        tc = _run_block("alpha bravo charlie delta")
        assert tc["fit"] == "ASSUMED_DEFAULT", tc
        assert tc["gamma_input"] == 0.5
        assert "0.5" in tc["reading"]


class TestTheBlockCatchesWhatItCanRaise:
    def test_an_unreadable_target_is_recorded_loudly_not_dropped(self):
        env_missing = ROOT / "bench" / "tests" / "_definitely_absent.tmp"
        assert not env_missing.exists()
        env = {
            "result": {}, "_tgt_p": env_missing,
            "_IC_WINDOW_CHARS": _IC_WINDOW_CHARS,
            "_IC_MIN_WINDOWS": _IC_MIN_WINDOWS,
            "compute_gamma_input": compute_gamma_input,
            "_ic_tokenize": _ic_tokenize, "round_idx": 0,
        }
        exec(_lift_block(), env)          # noqa: S102
        tc = env["result"]["target_complexity"]
        assert "error" in tc and "FileNotFoundError" in tc["error"], tc
        assert tc["informative_only"] is True

    def test_an_arithmetic_failure_is_caught_rather_than_killing_the_run(self):
        """`_fit_heaps` calls `math.exp(log_K)` on an UNCLAMPED beta
        (input_complexity.py:168), so an OverflowError is expressible from
        that path. OverflowError is an ArithmeticError and is NOT a subclass
        of ValueError, so the original `except (OSError, ValueError)` would
        have let it out of the block and ended the run at round 0 over an
        informative-only statistic."""
        def _boom(*_a, **_k):
            raise OverflowError("math range error")
        env = {
            "result": {}, "_tgt_p": ROOT / "bench" / "dm" / "_memory.py",
            "_IC_WINDOW_CHARS": _IC_WINDOW_CHARS,
            "_IC_MIN_WINDOWS": _IC_MIN_WINDOWS,
            "compute_gamma_input": _boom,
            "_ic_tokenize": _ic_tokenize, "round_idx": 0,
        }
        exec(_lift_block(), env)          # noqa: S102
        tc = env["result"]["target_complexity"]
        assert "OverflowError" in tc["error"], tc
