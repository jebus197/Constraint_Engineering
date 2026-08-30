"""The discrimination control may not silently reverse a verdict.

FOUNDER RULING 2026-08-30, option A: "Go with option A" -- put the un-confirm
behind `discrimination_control_blocks`, the switch whose name already implies it.

THE DEFECT. `_apply_discrimination_control`'s DISC_FAILED branch ran
`registry.resolve(cid, "UNCONFIRMED", round_idx)` UNCONDITIONALLY, while
`discrimination_control_blocks` guarded a different site entirely. Both reviewing
models read the flag as governing this; it did not. CC2's third-pass review
stated the control "will record a discrimination outcome and change no verdict",
which was wrong on this branch, and the morning's LATENT note was right.

WHY IT IS DANGEROUS. The branch fires on the premise, stated in the code, that
"a finding's own proposed fix corrects THIS claim by construction". Measured at
commit adb566b over 246 archived findings, 126 fixes do NOT silence their own
falsifier: 51.2%, Wilson CI [45.0%, 57.4%], binomtest vs 0.5 p = 0.75 -- a coin
toss, where the code assumes zero. So about half the times this branch fires it
un-confirms a SOUND falsifier on a REAL defect.

WHAT IS DELIBERATELY NOT GATED: the finding is still marked NON_DISCRIMINATING,
still escalated, still flagged a mechanical fault, and still carries its reason
to a human. Only the reversal is a decision.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v2 as R

SRC = pathlib.Path(R.__file__).read_text(encoding="utf-8")


def _disc_fn():
    return next(n for n in ast.walk(ast.parse(SRC))
                if isinstance(n, ast.FunctionDef)
                and n.name == "_apply_discrimination_control")


class TestTheReversalIsGated:
    def test_the_unconfirm_sits_under_the_blocks_flag(self):
        """Targets the resolve() CALL by AST, not the word 'UNCONFIRMED'.

        The first draft searched the unparsed body for that word and matched the
        DOCSTRING, 3,265 characters before the code. A guard test that can pass
        on prose is not a guard test.
        """
        fn = _disc_fn()
        calls = [n for n in ast.walk(fn)
                 if isinstance(n, ast.Call)
                 and "registry.resolve" in ast.unparse(n.func)
                 and "UNCONFIRMED" in ast.unparse(n)]
        assert calls, "the un-confirm call has gone entirely"
        for call in calls:
            guards = [n for n in ast.walk(fn)
                      if isinstance(n, ast.If)
                      and n.lineno <= call.lineno <= (n.end_lineno or 0)
                      and "discrimination_control_blocks" in ast.unparse(n.test)]
            assert guards, (
                f"registry.resolve(..., 'UNCONFIRMED') at line {call.lineno} is "
                f"not inside a discrimination_control_blocks branch — a fix "
                f"defect can silently reverse a CONFIRMED verdict"
            )

    def test_the_default_does_not_reverse(self):
        assert R.RunnerConfig(
            experiment_name="t", test_article="x",
        ).discrimination_control_blocks is False


class TestEverythingElseStillHappens:
    """The ruling gates the REVERSAL, not the reporting."""

    def test_the_finding_is_still_marked_non_discriminating(self):
        body = ast.unparse(_disc_fn())
        assert "'NON_DISCRIMINATING'" in body or '"NON_DISCRIMINATING"' in body

    def test_the_finding_is_still_escalated_to_a_human(self):
        body = ast.unparse(_disc_fn())
        for key in ("escalated", "hil_escalated", "mechanical_fault", "hil_reason"):
            assert key in body, f"{key} no longer set — the human loses the signal"

    def test_those_are_not_themselves_behind_the_flag(self):
        """If the reporting were gated too, switching blocking off would hide the
        fault entirely, which is the opposite of the ruling."""
        body = ast.unparse(_disc_fn())
        i_fault = body.index("mechanical_fault")
        i_flag = body.index("discrimination_control_blocks")
        assert i_fault < i_flag, (
            "the mechanical-fault marking now sits after/inside the blocking "
            "gate; with blocking off the fault would go unreported"
        )


class TestTheOperatorIsTold:
    def test_a_suppressed_reversal_is_logged(self):
        body = ast.unparse(_disc_fn())
        assert "would UN-CONFIRM" in body, (
            "a suppressed reversal must say so; a silent non-action is how the "
            "flag went unnoticed for nine days"
        )
