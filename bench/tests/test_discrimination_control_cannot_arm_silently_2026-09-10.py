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

WHAT IT DOES NOT DO, stated so it is not over-read. The note rule is a TEST-TIME
LINT over the committed configs. `RunnerConfig.from_json` reads the file and hands
it to `from_dict`, which does not refuse an armed config with no note (executed
2026-09-17 on an in-memory armed copy of the Exp 53 config: the flag loads True).
Arming is caught when the suite runs, not made impossible.

STRENGTHENED 2026-09-17 (task R3 correction, panel round 16). 4 gaps found by
execution:
  1. The note rule had no positive control. It is now a helper, `_unjustified`,
     exercised on synthetic configs that must be refused and accepted.
  2. It covered 7 of the 47 committed configs, in 3 of the 17 `bench/exp*_configs/`
     directories, and was blind to `bench/exp53_configs/53_control_zero_live.json`.
     It now reads every `bench/exp*_configs/*.json`, with a floor on the count.
  3. It accepted an incidental mention. Armed in memory,
     `bench/exp55_configs/55_v3_control.json` passed on its pre-registration text
     alone. The reason must now name the flag, or name the control and say armed,
     in 1 field; every committed config is armed in memory and must be refused.
  4. The control-off behaviour was checked by 2 substrings of runner source. It is
     now EXECUTED through the gate. The harness `_gate` starts findings OPEN and so
     never reaches the gated un-confirm; `_gate_from_confirmed` starts one
     CONFIRMED, which does.
The gate on the un-confirm is now held by EXECUTION here as well as by the AST test
in `test_discrimination_unconfirm_is_gated_2026-08-30.py`: on a runner copy with
`registry.resolve(cid, "UNCONFIRMED", round_idx)` moved after the flag's if/else,
`test_a_confirmed_finding_is_not_reversed_and_the_run_says_so` and the AST test
both fail, while the 400-character window below still passes.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CONFIG_GLOBS = ("bench/exp*_configs/*.json",)
#: 47 config files existed on 2026-09-17. The population may grow; it may not
#: silently shrink, which is how a glob stops covering the config a run needs.
CONFIG_FLOOR = 47
FLAG = "discrimination_control_blocks"
_ARMED = re.compile(r"\barm(?:s|ed|ing)?\b", re.IGNORECASE)

# The gate harness, loaded under a private name so its Test classes are not
# collected a second time here. `mini_repo` is re-exported as a fixture.
_HARNESS_PATH = ROOT / "bench" / "tests" / "test_discrimination_control.py"
_spec = importlib.util.spec_from_file_location("_discrimination_gate_harness", _HARNESS_PATH)
_harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_harness)
mini_repo = _harness.mini_repo


def _configs():
    out = []
    for g in CONFIG_GLOBS:
        out += sorted(ROOT.glob(g))
    return out


def _unjustified(d: dict) -> bool:
    """True when a config ARMS the flag and records no reason naming it.

    The reason is read from the VALUES of `_`-prefixed string fields only. A key
    that names the control does not count: `{"_discrimination_note": "armed for
    exp53"}` is refused, because its text does not say what was armed.

    TIGHTENED 2026-09-17. The first form accepted any `_` value containing the
    word "discrimination", pooled across every note in the file. Arming
    `bench/exp55_configs/55_v3_control.json` in memory showed the hole: its
    pre-registration predicts "THE DISCRIMINATION CONTROL FIRES AT LEAST ONCE",
    which says nothing about arming, and the rule accepted it. A reason must now
    sit in 1 field that names the flag, or names the discrimination control AND
    says it is armed.
    """
    if not d.get(FLAG):
        return False                    # absent or false: nothing to justify
    for k, v in d.items():
        if not (k.startswith("_") and isinstance(v, str)):
            continue
        if FLAG in v or ("discrimination" in v.lower() and _ARMED.search(v)):
            return False
    return True


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

        A source-text assertion, and a weak one: it is a 400-character window
        and passes on a runner copy with the un-confirm hoisted out of the flag's
        branch. The AST test in `test_discrimination_unconfirm_is_gated_2026-08-30.py`
        is the one that fails on that copy. This window is kept as a second,
        cheaper tripwire, not as the proof.
        """
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index('registry.resolve(cid, "UNCONFIRMED"')
        window = src[max(0, i - 400):i]
        assert FLAG in window, (
            "the UNCONFIRM call is no longer inside the flag's branch, which is "
            "exactly the defect option A was ruled to fix")


def _assert_stamped(e: dict) -> None:
    assert e.get("discrimination", {}).get("outcome") == _harness.DISC_FAILED, e.get("discrimination")
    assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
    assert e["escalated"] is True
    assert e["hil_escalated"] is True
    assert e["mechanical_fault"] is True
    assert isinstance(e.get("hil_reason"), str) and e["hil_reason"].strip()


def _gate_from_confirmed(repo, blocks: bool) -> dict:
    """The gate on a finding that ENTERS it already CONFIRMED.

    The ruled site -- `registry.resolve(cid, "UNCONFIRMED", round_idx)` inside
    `_apply_discrimination_control` -- runs only when `status == "CONFIRMED"` at the
    moment the control fires: a finding the vote pass confirmed, or one confirmed in
    an earlier round. `_harness._gate` starts every finding OPEN, so it never reaches
    that site (observed 2026-09-17: blocks=True leaves it OPEN, not UNCONFIRMED).
    """
    entry = {"severity": 0.85, "falsifier_code": _harness.NON_DISCRIMINATING_FALSIFIER,
             "description": "the stated clearance is the retracted value",
             "corrected_copy": _harness.CORRECTED, "status": "CONFIRMED"}
    reg = _harness._registry_with("C0001", entry)
    cfg = _harness.RunnerConfig(test_article=_harness.TARGET_REL,
                                falsifier_gate_enabled=True,
                                discrimination_control_blocks=blocks)
    _harness.apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(repo))
    return reg.entries["C0001"]


class TestEverythingElseStillHappensWhenItIsOff:
    """EXECUTED through the gate, replacing a 2-substring check of runner source.

    With the flag off and a falsifier that fires on the corrected copy, the finding
    must keep its verdict AND still be marked, escalated and reported. Every value
    asserted here was observed at HEAD 989f32f before this test was written.
    """

    STAYS = "the finding stays CONFIRMED and is escalated to a human instead."

    def test_a_new_finding_is_marked_escalated_and_closed(self, mini_repo):
        """The harness path, starting OPEN, as the correction specified."""
        _reg, e = _harness._gate(mini_repo, _harness.NON_DISCRIMINATING_FALSIFIER,
                                 _harness.CORRECTED, blocks=False)
        _assert_stamped(e)
        assert e["status"] == "CONFIRMED", e["status"]
        assert e["verified"] is True

    def test_a_confirmed_finding_is_not_reversed_and_the_run_says_so(self, mini_repo, capsys):
        """The path that actually reaches the gated un-confirm, with the flag off."""
        e = _gate_from_confirmed(mini_repo, blocks=False)
        _assert_stamped(e)
        # THE TRANSITION LOG, NOT ONLY THE FINAL STATUS. With the flag off the
        # caller re-confirms the finding later in the same round, so an ungated
        # un-confirm ends CONFIRMED too. Observed 2026-09-17 on a runner copy with
        # the un-confirm hoisted out of the flag: final status CONFIRMED, and a
        # CONFIRMED -> UNCONFIRMED -> CONFIRMED pair in `status_log`.
        reversals = [t for t in e.get("status_log", []) if t.get("to") == "UNCONFIRMED"]
        assert not reversals, (
            f"the flag is off and the verdict was reversed in the log: {reversals}")
        assert e["status"] == "CONFIRMED", (
            f"the flag is off and the verdict was reversed anyway: {e['status']}")
        assert e["verified"] is True
        assert self.STAYS in capsys.readouterr().err, (
            "with the control off the run no longer says the finding stays "
            "CONFIRMED and goes to a human")

    def test_armed_the_same_confirmed_finding_is_reversed(self, mini_repo, capsys):
        """CONTROL: the flag is the only difference, so the test above can fail."""
        e = _gate_from_confirmed(mini_repo, blocks=True)
        _assert_stamped(e)
        assert e["status"] == "UNCONFIRMED" and e["verified"] is False, (
            e["status"], e["verified"])
        assert any(t.get("from") == "CONFIRMED" and t.get("to") == "UNCONFIRMED"
                   for t in e.get("status_log", [])), e.get("status_log")
        assert self.STAYS not in capsys.readouterr().err


class TestTheNoteRuleCanFail:
    """Positive and negative controls on synthetic configs. No committed config is armed."""

    def test_armed_with_no_note_is_refused(self):
        assert _unjustified({FLAG: True}) is True

    def test_armed_with_a_note_naming_the_control_is_accepted(self):
        assert _unjustified({
            FLAG: True,
            "_note_disc": "discrimination control armed for <run> by founder ruling <date>",
        }) is False

    def test_unarmed_configs_pass(self):
        assert _unjustified({}) is False
        assert _unjustified({FLAG: False}) is False

    def test_a_key_that_names_it_is_not_a_reason(self):
        assert _unjustified({FLAG: True, "_discrimination_note": "armed for exp53"}) is True

    def test_a_non_underscore_field_is_not_a_reason(self):
        assert _unjustified({FLAG: True, "note": "discrimination control armed"}) is True

    def test_an_incidental_mention_is_not_a_reason(self):
        """The exp55 shape: the control is named, arming is not."""
        assert _unjustified({
            FLAG: True,
            "_pre_registration": "THE DISCRIMINATION CONTROL FIRES AT LEAST ONCE",
        }) is True

    def test_the_two_halves_must_sit_in_one_field(self):
        assert _unjustified({FLAG: True, "_a": "discrimination records kept",
                             "_b": "armed guards on the gate"}) is True

    def test_arm_must_be_a_word(self):
        assert _unjustified({FLAG: True, "_n": "discrimination control: no harm done"}) is True

    def test_the_flag_name_alone_is_a_reason(self):
        assert _unjustified({FLAG: True, "_n": "discrimination_control_blocks set for R1"}) is False


class TestItCannotBeArmedSilently:
    def test_every_config_directory_is_covered(self):
        cfgs = _configs()
        assert len(cfgs) >= CONFIG_FLOOR, (
            f"only {len(cfgs)} configs found against a floor of {CONFIG_FLOOR}; "
            f"the note rule has stopped covering configs it used to")
        names = {str(p.relative_to(ROOT)) for p in cfgs}
        assert "bench/exp53_configs/53_control_zero_live.json" in names, (
            "the Exp 53 config that task R1 needs is outside the rule again")

    @pytest.mark.parametrize("cfg", _configs(),
                             ids=lambda p: f"{Path(p).parent.name}/{Path(p).name}")
    def test_a_config_that_arms_it_must_say_why(self, cfg):
        """The deliverable of R3. Arming is his to authorise, in writing."""
        d = json.loads(Path(cfg).read_text(encoding="utf-8"))
        assert not _unjustified(d), (
            f"{Path(cfg).name} arms {FLAG} and no `_note` field in it explains "
            f"why. His ruling was that this cannot reverse a result until he says "
            f"so; an armed flag with no recorded decision is exactly that")

    def test_no_committed_note_would_justify_arming_by_accident(self):
        """Arm every committed config IN MEMORY; each must then be refused.

        A config whose existing notes already satisfy the rule could be armed by
        flipping 1 value, with no new reason written. No file is modified.
        """
        accepted = []
        for c in _configs():
            d = json.loads(Path(c).read_text(encoding="utf-8"))
            if d.get(FLAG):
                continue                # armed on disk: the parametrized test owns it
            if not _unjustified(dict(d, **{FLAG: True})):
                accepted.append(str(Path(c).relative_to(ROOT)))
        assert accepted == [], (
            f"{accepted} already carry a note the rule accepts, so arming them "
            f"would need no new recorded decision")

    def test_no_config_arms_it_today(self):
        """The run has not happened, and his instruction was: not before."""
        armed = [Path(c).name for c in _configs()
                 if json.loads(Path(c).read_text(encoding="utf-8")).get(FLAG)]
        assert armed == [], (
            f"{armed} arm the discrimination control before the run needs it. If "
            f"that was deliberate, record the decision in the config and update "
            f"this test in the same change")
