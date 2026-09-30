"""Every available effect gate must produce DIFFERENT output for known-good and
known-bad input. A gate whose output does not vary with its input decides nothing.

WHY THIS EXISTS, and it is a control both free panel seats converged on
independently in the design review of 2026-09-30.

fable stated it as a tightening of the additive standard: *"every gate needs a
committed discrimination pair (known-good vs known-bad input producing different
outputs)"*. cc2 stated the same control from the other side: *"assert every
available gate's score varies across >= 2 fixes. A zero-variance available gate
is a defect, not a result."* Both named one defect class behind 3 separate
findings of that session -- **machinery whose output does not vary with its
input**: the constant `e2_regression` on a prose target, a proven falsifier corpus
reachable from 0 live-path modules, and the 11 recorded additions that did
nothing. The project's own record says this class dominates.

WHAT THE MOTIVATING DEFECT LOOKED LIKE. On 2026-09-30 `e2_regression` was
measured returning 52/55 = 0.9454545454545454 on a prose target whose bytes had
been DESTROYED -- byte-identical to the score on the intact document -- because
`Arm.argv()` dropped `--test-cmd` on a falsy guard and argparse substituted the
immune-memory suite for an unrelated Python module. The gate ran, returned a
number, and that number carried no information about the thing under review. No
existing test could see it: the guard that should have,
`test_commissioning_arms_carry_their_settings_2026-09-21.py`, asserts
`arm4.test_cmd is None` on the PRODUCER and never parses the argv with the real
consumer -- in a file whose own docstring cites `execute-do-not-grep`.

WHAT THIS FILE DOES, AND WHAT IT DELIBERATELY DOES NOT DO. It CALLS each gate
with a matched pair and compares the returned values. It does not read the gates'
source, and it does not assert any particular score: a gate is free to change how
it scores, and this test stays green as long as it still tells good from bad.
That is the property worth pinning, and it is the one `execute-do-not-grep` says
a source-text check cannot establish.

A gate that is UNAVAILABLE on a given input (returning ``None``) is not failing
this test -- abstention is a legitimate answer and is exactly what
`_run_effect_regression` should do when no test command is configured. What fails
is a gate that RETURNS A SCORE and returns the same one either way.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import (  # noqa: E402
    _run_effect_bandit, _run_effect_fix_efficacy, _run_effect_regression,
    _run_effect_ruff,
)
#: IMPORTED, NOT RETYPED. The first draft of this file guessed the outcome
#: labels ("CONFIRMED_FIXED", "STILL_BROKEN"), both unrecognised, so the
#: e1 pair SKIPPED -- a guard that does not guard, which is the very class this
#: file exists to catch. Importing the producer's own constants means the pair
#: cannot drift from them silently.
from fix_efficacy import (  # noqa: E402
    FIX_CURES, FIX_INEFFECTIVE, PROBE_BROKEN_AFTER_BASELINE,
)

#: A clean Python module and the same module with 1 new lint diagnostic.
CLEAN_PY = "def f(x):\n    return x + 1\n"
LINTY_PY = "import os\n\n\ndef f(x):\n    return x + 1\n"          # os unused -> F401

#: The same module with and without a bandit HIGH. A VARIABLE command is used
#: deliberately: bandit rates `shell=True` with a string LITERAL as LOW, which is
#: the exact blind spot recorded in the A19 entry, so a literal would not
#: exercise the HIGH path at all.
SAFE_PY = "import subprocess\n\n\ndef f(cmd):\n    return subprocess.run([cmd])\n"
UNSAFE_PY = "import subprocess\n\n\ndef f(cmd):\n    return subprocess.call(cmd, shell=True)\n"


def _pair_differs(name, good, bad):
    """Both scored, and different. Returns a legible reason when it does not."""
    if good is None or bad is None:
        return (f"{name}: one side is UNAVAILABLE (good={good}, bad={bad}), so this "
                f"pair cannot decide discrimination — pick inputs the gate can score")
    if good == bad:
        return (f"{name}: known-good and known-bad both scored {good}. A gate whose "
                f"output does not vary with its input decides nothing — this is the "
                f"constant-e2 defect class, reproduced.")
    return None


class TestEachGateTellsGoodFromBad:
    """One executed pair per gate. No source text is read."""

    def test_e3_ruff_discriminates(self):
        good, gd = _run_effect_ruff(CLEAN_PY, 0, source_path="m.py")
        bad, bd = _run_effect_ruff(LINTY_PY, 0, source_path="m.py")
        problem = _pair_differs("e3_ruff", good, bad)
        assert problem is None, f"{problem}\n  good detail: {gd}\n  bad detail: {bd}"

    def test_e4_bandit_discriminates(self):
        base = {"high": 0, "medium": 0}
        good, gd = _run_effect_bandit(SAFE_PY, base, source_path="m.py")
        bad, bd = _run_effect_bandit(UNSAFE_PY, base, source_path="m.py")
        problem = _pair_differs("e4_bandit", good, bad)
        assert problem is None, f"{problem}\n  good detail: {gd}\n  bad detail: {bd}"

    def test_e1_fix_efficacy_discriminates(self):
        """The only gate that asks whether the fix WORKED."""
        good, gd = _run_effect_fix_efficacy(FIX_CURES)
        bad, bd = _run_effect_fix_efficacy(FIX_INEFFECTIVE)
        problem = _pair_differs("e1_efficacy", good, bad)
        assert problem is None, f"{problem}\n  good detail: {gd}\n  bad detail: {bd}"

    def test_breaking_the_probe_never_scores_better_than_failing_it(self):
        """A MEASURED hazard, not a hypothetical one.

        `fix_efficacy.PROBE_BROKEN_AFTER_BASELINE` exists because dropping the
        broken-probe case from the weighted mean CREATED A GRADIENT THAT PAID FOR
        DESTROYING THE INSTRUMENT: the module's own comment records that letting
        the falsifier run and fail scored sk = 0.6 while crashing it scored
        sk = 1.0, a premium of +0.4000, turning `compute_rk(0.5, 0.3)` from
        risk-UP 0.516729 into risk-DOWN 0.441176. So the gate must never reward
        the crash over the honest failure.
        """
        failed, fd = _run_effect_fix_efficacy(FIX_INEFFECTIVE)
        broken, bd = _run_effect_fix_efficacy(PROBE_BROKEN_AFTER_BASELINE)
        assert failed == 0.0, f"expected a failing probe to score 0.0, got {failed} ({fd})"
        assert broken is None or broken <= failed, (
            f"breaking the probe scored {broken} ({bd}) against {failed} for honestly "
            f"failing it. That is a gradient that pays for destroying the instrument, "
            f"the +0.4000 premium this constant was introduced to remove.")


class TestAbstentionIsNotAFailure:
    """A gate that declines is behaving correctly and must not trip the check.

    This is the other half of the property, and without it the file would push
    toward gates that always answer — which is how a gate ends up answering with
    a constant. `_run_effect_regression` with no test command MUST abstain.
    """

    def test_regression_abstains_with_no_test_command(self):
        score, detail = _run_effect_regression(CLEAN_PY, "m.py", None)
        assert score is None, (
            f"with no test command configured the regression gate returned "
            f"{score} ({detail}). Abstention is the correct answer; a score here "
            f"is a number about something other than the fix.")

    def test_regression_abstains_on_a_target_outside_the_repository(self, tmp_path):
        outside = tmp_path / "m.py"
        outside.write_text(CLEAN_PY, encoding="utf-8")
        score, detail = _run_effect_regression(
            CLEAN_PY, str(outside), "python3 -c 'pass'")
        assert score is None, (
            f"a target outside REPO_ROOT was scored {score} ({detail}); "
            f"containment is the one kind-independent suppressor and it must hold")


class TestTheCheckIsNotVacuous:
    """A discrimination test that cannot fail is worth nothing.

    Verified by CONSTRUCTION rather than by assertion: `_pair_differs` is driven
    with the shapes it exists to catch, so if it ever stops catching them this
    class goes red before any real gate does.
    """

    def test_equal_scores_are_reported(self):
        assert _pair_differs("x", 1.0, 1.0) is not None
        assert _pair_differs("x", 0.0, 0.0) is not None

    def test_an_unavailable_side_is_reported(self):
        assert _pair_differs("x", None, 1.0) is not None
        assert _pair_differs("x", 1.0, None) is not None

    def test_differing_scores_pass(self):
        assert _pair_differs("x", 1.0, 0.5) is None

    def test_the_gates_are_actually_imported(self):
        """If an import silently became a stub every pair would pass forever."""
        for fn in (_run_effect_ruff, _run_effect_bandit, _run_effect_regression,
                   _run_effect_fix_efficacy):
            assert callable(fn), fn
            assert fn.__module__.endswith("reference_runner_v3"), fn.__module__
