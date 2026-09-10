"""R3: the discrimination control may not reverse a verdict without him saying so.

His ruling, 2026-08-30: *"Go with option A"* -- option A being that the block sits
behind a switch which CANNOT SILENTLY REVERSE A RESULT until he says so. And the
task's own instruction: raise it when the run needs it, NOT BEFORE.

WHY THE SWITCH EXISTS. The un-confirm used to run UNCONDITIONALLY while the
switch everyone assumed governed it guarded a different site -- both reviewing
models read it as gated and it was not. The branch fires on the premise that "a
finding's own proposed fix corrects THIS claim by construction". Measured at
commit adb566b across 246 archived findings, 126 of those fixes do NOT silence
their own falsifier: 51.2%, Wilson [45.0%, 57.4%], p = 0.75 against a coin toss.
So roughly half the time it fired, it was un-confirming a SOUND falsifier on a
REAL defect.

WHAT THIS FILE ADDS. Verifying the flag is off is not the deliverable -- his
ruling asks that it cannot be armed SILENTLY. So a config that arms it must say
why, in the config, and these tests refuse one that does not.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CONFIG_GLOBS = ("bench/exp56_configs/*.json", "bench/exp50_configs/*.json",
                "bench/exp51_configs/*.json")
FLAG = "discrimination_control_blocks"


def _configs():
    out = []
    for g in CONFIG_GLOBS:
        out += sorted(ROOT.glob(g))
    return out


class TestTheSwitchIsOffAndGated:
    def test_the_default_is_off(self):
        from bench.reference_runner_v3 import RunnerConfig
        f = {x.name: x for x in dataclasses.fields(RunnerConfig)}
        assert FLAG in f, "the switch is gone; the un-confirm may be unconditional again"
        assert f[FLAG].default is False, (
            "the default arms the control, so a run that says nothing would "
            "silently reverse verdicts")

    def test_the_unconfirm_is_actually_behind_the_flag(self):
        """The original defect was the switch guarding a DIFFERENT site.

        This is the one source-text assertion here and it is deliberate: the
        property is a control-flow adjacency, and the alternative -- driving a
        full round to observe a reversal -- would need a live registry and would
        test far more than the gate.
        """
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index('registry.resolve(cid, "UNCONFIRMED"')
        window = src[max(0, i - 400):i]
        assert FLAG in window, (
            "the UNCONFIRM call is no longer inside the flag's branch, which is "
            "exactly the defect option A was ruled to fix")

    def test_everything_else_still_happens_when_it_is_off(self):
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "the finding stays " in src and "escalated to a human instead" in src, (
            "with the control off the finding must still be marked, escalated and "
            "reported; only the silent reversal is withheld")


class TestItCannotBeArmedSilently:
    @pytest.mark.parametrize("cfg", _configs(), ids=lambda p: Path(p).name)
    def test_a_config_that_arms_it_must_say_why(self, cfg):
        """The deliverable of R3. Arming is his to authorise, in writing."""
        d = json.loads(Path(cfg).read_text(encoding="utf-8"))
        if not d.get(FLAG):
            return                      # absent or false: nothing to justify
        note = " ".join(str(v) for k, v in d.items()
                        if k.startswith("_") and isinstance(v, str))
        assert FLAG in note or "discrimination" in note.lower(), (
            f"{Path(cfg).name} arms {FLAG} and no `_note` field in it explains "
            f"why. His ruling was that this cannot reverse a result until he says "
            f"so; an armed flag with no recorded decision is exactly that")

    def test_no_config_arms_it_today(self):
        """The run has not happened, and his instruction was: not before."""
        armed = [Path(c).name for c in _configs()
                 if json.loads(Path(c).read_text(encoding="utf-8")).get(FLAG)]
        assert armed == [], (
            f"{armed} arm the discrimination control before the run needs it. If "
            f"that was deliberate, record the decision in the config and update "
            f"this test in the same change")
