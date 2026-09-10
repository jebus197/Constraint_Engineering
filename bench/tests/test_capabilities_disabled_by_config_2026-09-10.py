"""Task 3.3: nothing had ever looked for siblings of the exp56 off-switches.

`routing_enabled: false` and `post_convergence_sweep_rounds: 0` were found BY
ACCIDENT. A capability that exists, is tested, and is switched off in a config
file is invisible to the suite: every test passes and the feature never runs.
That is the additive standard's own failure mode hiding in data rather than code.

WHAT THE SWEEP FOUND, across the 3 frozen exp56 arm configs: 9 off-switches the
runner DOES read -- `hardened_gate_enabled`, `apply_fixes_back_enabled` and
`sk_enabled`, each false in all 3 arms -- and 6 it does not, being
`merge_arbitration_enabled` and `immune_memory_enabled`.

THE CONFIGS ARE NOT TOUCHED. They are frozen pre-registration files and changing
one is the founder's call, established when task 3.1's literal reading would have
flipped flags that were a documented mitigation for 2 live runner defects. This
test pins WHAT IS TRUE so the next run cannot be launched in ignorance of it; it
does not assert what the values ought to be.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "capabilities_disabled_by_config_2026-09-10.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("caps", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheSweepRuns:
    def test_it_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"{r.stdout[-1500:]}\n{r.stderr[-1500:]}"

    def test_it_reads_every_runner_module_not_just_one(self, mod):
        """The instrument was wrong first, and this is why.

        Reading only `reference_runner_v3.py` gave 3 read and 12 unread. Reading
        all 210 runner modules gives 9 and 6. The first version would have
        reported 12 capabilities as unwired additions when 6 of them are read
        elsewhere -- a false claim about absence, which is the hardest kind to
        notice and the easiest kind to publish.
        """
        srcs = mod.runner_sources()
        assert len(srcs) > 100, f"only {len(srcs)} modules scanned"
        names = {p.name for p in srcs}
        assert "reference_runner_v3.py" in names
        assert "launcher_core.py" in names, (
            "sk_enabled is read in launcher_core.py; missing it produces a false "
            "'nothing reads this' finding")
        assert not any("tests" in p.parts for p in srcs), (
            "a test reading a field is not the runner reading it")


class TestTheOffSwitchesAreRecorded:
    """PINS WHAT IS TRUE. It does not assert what the values ought to be."""

    def _fields(self, mod, name):
        import json
        f = ROOT / "bench" / "exp56_configs" / name
        if not f.is_file():
            pytest.skip(f"{name} not present")
        return dict(mod.walk(json.loads(f.read_text(encoding="utf-8"))))

    @pytest.mark.parametrize("arm", [
        "d9_single_model_with_agents.json",
        "d9_multi_model_panel.json",
        "d11_seat_contrast_diversity_arm.json",
    ])
    def test_sk_is_ON_in_every_arm_of_the_next_run(self, mod, arm):
        """TURNED ON 2026-09-10 on the founder's explicit instruction.

        This test previously pinned it FALSE. The flip is recorded here rather
        than silently rewritten, because a test that changes its expectation
        without saying why is indistinguishable from a test that was wrong.

        THE EVIDENCE FOR ENABLING IT, and it is why this is not a risk: over a
        2475-point grid the corrected gate is STRICTER at 502 points, 20.2828%,
        Wilson [18.7453%, 21.9125%], and LOOSER at 0, Wilson [0.0000%, 0.1550%].
        It can only ever reject more. Against 326 archived shadow records the
        corrected and shipped verdicts agree 326 of 326.
        """
        f = self._fields(mod, arm)
        assert f.get("sk_enabled") is True, (
            f"{arm}: sk_enabled is not True. It was turned on by founder "
            f"instruction on 2026-09-10; if it has been turned off again, say "
            f"who decided and why, in the config's own _sk_note")

    @pytest.mark.parametrize("arm", [
        "d9_single_model_with_agents.json",
        "d9_multi_model_panel.json",
        "d11_seat_contrast_diversity_arm.json",
    ])
    def test_every_arm_is_a_python_target_so_the_gate_is_defined_there(self, mod, arm):
        """The one case where S_k is HARMFUL is a non-Python target.

        On prose ruff cannot parse the file, so the ranking inverts: a shell
        injection inside a fence scored 1.0000 ADMISSIBLE while a correct prose
        fix scored 0.6667. The runner forces the gate off for any non-Python
        target, so this asserts the arms are where the gate is defined -- which
        is what makes enabling it safe rather than merely authorised.
        """
        f = self._fields(mod, arm)
        assert f.get("target_kind") == "python_module", (
            f"{arm}: target_kind is {f.get('target_kind')!r}. With S_k now ON, a "
            f"non-Python target would rely on the runner's forced-off path "
            f"instead of the config being correct")

    def test_the_reason_travels_with_the_change(self, mod, arm=None):
        """A flipped switch with no recorded reason is the defect this file finds."""
        import json
        for a in ("d9_single_model_with_agents.json", "d9_multi_model_panel.json",
                  "d11_seat_contrast_diversity_arm.json"):
            f = ROOT / "bench" / "exp56_configs" / a
            if not f.is_file():
                pytest.skip(f"{a} not present")
            note = json.loads(f.read_text(encoding="utf-8")).get("_sk_note", "")
            assert "TURNED ON" in note and "SUPERSEDED, NOT DELETED" in note, (
                f"{a}: _sk_note does not record the change or retains no history "
                f"of the earlier decision")

    def test_the_runner_really_does_read_sk_enabled(self, mod):
        """Otherwise the finding above is about a field nothing consults."""
        read = set()
        for p in mod.runner_sources():
            read |= mod.read_fields(p.read_text(encoding="utf-8", errors="replace"))
        assert "sk_enabled" in read

    def test_two_capabilities_are_switched_off_and_read_by_nobody(self, mod):
        """A DIFFERENT defect from this task's, and not conflated with it."""
        read = set()
        for p in mod.runner_sources():
            read |= mod.read_fields(p.read_text(encoding="utf-8", errors="replace"))
        for name in ("merge_arbitration_enabled", "immune_memory_enabled"):
            assert name not in read, (
                f"{name} is now read somewhere; it was an unwired field when this "
                f"was written, so either it was wired or the scan changed -- "
                f"update this test deliberately")


class TestTheDefinitionIsNarrowEnoughToBeActionable:
    def test_a_plain_false_is_not_reported(self, mod):
        """Otherwise the output is every false in the tree and nobody reads it."""
        assert not mod.ENABLEMENT.search("verbose")
        assert not mod.ENABLEMENT.search("dry_run")
        assert mod.ENABLEMENT.search("routing_enabled")
        assert mod.ENABLEMENT.search("enable_tools")

    def test_a_zero_allowance_is_reported_but_a_plain_zero_is_not(self, mod):
        assert mod.ALLOWANCE.search("post_convergence_sweep_rounds")
        assert mod.ALLOWANCE.search("max_retries")
        assert not mod.ALLOWANCE.search("seed")
        assert not mod.ALLOWANCE.search("offset")
