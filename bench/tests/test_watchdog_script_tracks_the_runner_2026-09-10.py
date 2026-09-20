"""The 6.2 instrument must track the runner it claims to read.

FOUND BY PANEL ROUND 4 (CC2, finding F2), 2026-09-10. Two defects, one shape.

1. `scripts/watchdog_vs_retry_budget_2026-09-09.py` read the 2 multipliers out of
   `bench/reference_runner_v3.py` by regex and then TYPED the operator that
   combines them with the retry budget. A seat mutated the runner's `max` to
   `min` and the instrument still printed "fits" for every seat and
   "truncated: 0 of 5", while the runner truncated Gemini from 1500 s to 900 s.
   An instrument that hardcodes half the expression it claims to read cannot
   detect that expression regressing.

2. NOTHING EXECUTED THE SCRIPT AT ALL. `grep -rn watchdog_vs_retry_budget bench/`
   returned 1 hit, a docstring mention. That is why it sat exiting 1 for a whole
   day, in the same commit that created it, while task 6.2 cited its figures.
   Under the additive standard an addition nothing reaches is not additive, so
   this file is the caller that reaches it.

THE TESTS DRIVE THE SCRIPT AGAINST SYNTHETIC RUNNER SOURCES. The canonical tree
is never mutated: `RUNNER` is redirected at a temporary file, which is what lets
a regressed form be exercised without regressing the repository.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "watchdog_vs_retry_budget_2026-09-09.py"
RUNNER = ROOT / "bench" / "reference_runner_v3.py"

POST_FORM = '''
    _mult = 5 if base_model_label(mc.label) == "CC2" else 3
    _retry_budget = mc.timeout * max(1, int(getattr(mc, "max_retries", 1) or 1))
    wall_limit = {op}(mc.timeout * _mult, _retry_budget)
'''

PRE_FORM = '''
    wall_limit = (mc.timeout * 5 if base_model_label(mc.label) == "CC2"
                  else mc.timeout * 3)
'''

ABSENT_FORM = '''
    wall_limit = compute_the_wall_limit(mc)
'''


def _load():
    spec = importlib.util.spec_from_file_location("wd", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def wd():
    return _load()


def _point_at(mod, tmp_path: Path, body: str) -> None:
    src = tmp_path / "fake_runner.py"
    src.write_text(body, encoding="utf-8")
    mod.RUNNER = src


class TestItRunsAtHeadAtAll:
    """The failure that started this: the script exited 1 and produced nothing."""

    def test_the_script_exits_zero_against_the_real_runner(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (
            f"the instrument task 6.2 cites does not run: exit {r.returncode}\n"
            f"{r.stdout}\n{r.stderr}")
        import importlib.util as _il
        _s = _il.spec_from_file_location("wd_probe", SCRIPT)
        _m = _il.module_from_spec(_s); _s.loader.exec_module(_m)
        assert f"truncated: 0 of {_m.EXPECTED_SEATS}" in r.stdout, (
            "at HEAD the runner takes max(multiplier cap, retry budget), so no "
            "seat can be truncated; the script reported otherwise.\n"
            f"{r.stdout}")

    def test_it_names_the_form_it_found(self, wd):
        _, _, form, op = wd.multipliers()
        assert form.startswith("post-2026-09-09"), form
        assert op == "max", "HEAD combines with max; the script read something else"


class TestTheOperatorIsReadNotTyped:
    """The regression CC2 demonstrated, reproduced here so it cannot return."""

    def test_a_min_runner_is_reported_as_truncating(self, wd, tmp_path, capsys):
        _point_at(wd, tmp_path, POST_FORM.format(op="min"))
        cc2, other, form, op = wd.multipliers()
        assert (cc2, other, op) == (5, 3, "min"), (
            "the script did not read `min` out of the runner — the operator is "
            "still typed into the instrument")
        wd.main()
        out = capsys.readouterr().out
        assert "TRUNCATED" in out, (
            "with the runner combining by `min`, Gemini's 1500 s budget is cut "
            "to 900 s and the instrument must say so")
        assert f"truncated: 1 of {wd.EXPECTED_SEATS}" in out, out

    def test_a_max_runner_reports_no_truncation(self, wd, tmp_path, capsys):
        """The negative control: the same code path must be able to say 'fits'."""
        _point_at(wd, tmp_path, POST_FORM.format(op="max"))
        wd.main()
        out = capsys.readouterr().out
        assert f"truncated: 0 of {wd.EXPECTED_SEATS}" in out, out
        assert "TRUNCATED" not in out

    def test_the_two_operators_give_different_answers(self, wd, tmp_path, capsys):
        """If they agreed, neither case would be evidence about the other."""
        answers = {}
        for op in ("max", "min"):
            _point_at(wd, tmp_path, POST_FORM.format(op=op))
            wd.main()
            answers[op] = capsys.readouterr().out
        assert answers["max"] != answers["min"], (
            "the instrument produced identical output for max and min, so it is "
            "not reading the operator at all")


class TestTheOtherFormsStillBehave:
    def test_the_pre_fix_form_is_recognised_and_carries_no_operator(self, wd, tmp_path):
        _point_at(wd, tmp_path, PRE_FORM)
        cc2, other, form, op = wd.multipliers()
        assert (cc2, other) == (5, 3)
        assert form.startswith("pre-2026-09-09")
        assert op is None, (
            "the pre-fix form has no combining operator; inventing one would "
            "model a cap the shipped code never computed")

    def test_the_pre_fix_form_reports_the_historical_truncation(self, wd, tmp_path, capsys):
        _point_at(wd, tmp_path, PRE_FORM)
        wd.main()
        out = capsys.readouterr().out
        # THE NUMERATOR IS THE CLAIM; THE DENOMINATOR IS THE ROSTER SIZE.
        # Task 6.2 quotes "1 of 5" and that was measured against a 5-seat
        # panel. Fable joined on 2026-09-20, so the same pre-fix form over the
        # same runner now reports 1 of 6. The count of TRUNCATED seats -- 1,
        # Gemini -- is what 6.2 actually established, and it is unchanged.
        assert f"truncated: 1 of {wd.EXPECTED_SEATS}" in out, (
            f"6.2 quotes 1 truncated before the fix, over a roster that was 5 "
            f"seats then and is {wd.EXPECTED_SEATS} now; the script must "
            f"reproduce the COUNT against the pre-fix form.\n{out}")
        assert "Gemini" in out and "TRUNCATED" in out

    def test_an_absent_form_still_refuses(self, wd, tmp_path):
        """Trap 2 of the round-4 brief: a script that accepts anything cannot fail.

        The refusal existed and nothing executed it, so its status was unmeasured
        rather than verified. This is the execution.
        """
        _point_at(wd, tmp_path, ABSENT_FORM)
        with pytest.raises(SystemExit) as exc:
            wd.multipliers()
        assert "has moved" in str(exc.value)


class TestSeatOmissionIsLoud:
    """fable's F3: a seat outside the slice window vanished silently."""

    def test_the_real_orchestrator_yields_the_expected_seats(self, wd):
        got = wd.seats()
        assert len(got) == wd.EXPECTED_SEATS, [g[0] for g in got]

    def test_a_short_window_is_announced_on_stderr(self, wd, tmp_path, capsys):
        trimmed = tmp_path / "orch.py"
        trimmed.write_text(
            'x = ModelConfig(label="CC2", timeout=900, max_retries=1)\n'
            'y = ModelConfig(label="Codex", timeout=300, max_retries=3)\n'
            'def later(): pass\n', encoding="utf-8")
        wd.ORCH = trimmed
        got = wd.seats()
        err = capsys.readouterr().err
        assert len(got) == 2
        assert f"not {wd.EXPECTED_SEATS}" in err and "partial" in err, (
            "a partial seat list must be announced; a silent shrinking "
            "denominator is how a proportion becomes wrong without notice")
