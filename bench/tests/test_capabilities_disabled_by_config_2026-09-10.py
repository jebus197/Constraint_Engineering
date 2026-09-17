"""Task 3.3: nothing had ever looked for siblings of the exp56 off-switches.

`routing_enabled: false` and `post_convergence_sweep_rounds: 0` were found BY
ACCIDENT. A capability that exists, is tested, and is switched off in a config
file is invisible to the suite: every test passes and the feature never runs.
That is the additive standard's own failure mode hiding in data rather than code.

WHAT THE SWEEP FINDS NOW, across the 3 exp56 arm configs, and the counts are
pinned by `TestTheClassificationIsPinned` below rather than typed here, because
the figures this docstring used to carry drifted when `sk_enabled` was turned ON
in all 3 arms on 2026-09-10 and nothing noticed. The runner READS 4 of the 5
distinct off-switch fields -- `hardened_gate_enabled`, `apply_fixes_back_enabled`,
`merge_arbitration_enabled` and `immune_memory_enabled`, each false in all 3 arms.
It does not read `_ouroboros.max_papers_per_round`, which is 0 in all 3.

2 INSTRUMENT DEFECTS WERE CORRECTED ON 2026-09-17 (panel round 16). (1) The
scanner resolved `cfg.field` but not `getattr(cfg, "field", ...)`, so it reported
`merge_arbitration_enabled` and `immune_memory_enabled` as read by nobody, and
this file PINNED that blind spot as a finding. Task A18's `readers_of()` had
already shown both are read; the 2 instruments are now compared by execution.
(2) The note lookup read only top-level `_<field>_note` keys, so it missed the
`_ouroboros` block's own `_note` and the `_convergence_criteria.description` that
records `hardened_gate_enabled=false`. Every off-switch now has a note or a cited
record in its own file.

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

        The first version read only `reference_runner_v3.py` and reported fields
        as unread that `launcher_core.py` and the launchers read -- a false claim
        about absence, which is the hardest kind to notice and the easiest kind
        to publish. It now reads every module under `bench/` outside `tests/`
        and `logs/`. The module count moves as the tree grows, so it is not
        typed here; this asserts only the floor and the modules that matter.
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

    def test_the_two_capabilities_once_called_unread_are_read_through_getattr(
            self, mod):
        """REPLACES `test_two_capabilities_are_switched_off_and_read_by_nobody`.

        That test asserted `merge_arbitration_enabled` and `immune_memory_enabled`
        were read by nobody. Both are read, as `getattr(cfg, "...", False)` in
        `bench/reference_runner_v3.py`, which task A18 showed; the old assertion
        passed only because the scanner could not see that form. It is replaced,
        not loosened: this asserts the opposite, and the control below shows the
        assertion goes red when the string form is not resolved.
        """
        read = set()
        for p in mod.runner_sources():
            read |= mod.read_fields(p.read_text(encoding="utf-8", errors="replace"))
        for name in ("merge_arbitration_enabled", "immune_memory_enabled"):
            assert name in read, f"{name} is not resolved as read"

    def test_without_getattr_resolution_both_drop_to_unread(self, mod, monkeypatch):
        """Control: the historic blind spot, restored in memory, hides both reads."""
        monkeypatch.setattr(mod, "_getattr_string_read", lambda n: None)
        read = set()
        for p in mod.runner_sources():
            read |= mod.read_fields(p.read_text(encoding="utf-8", errors="replace"))
        for name in ("merge_arbitration_enabled", "immune_memory_enabled"):
            assert name not in read, (
                f"{name} is still found with getattr resolution disabled, so the "
                f"assertion above would not detect the blind spot returning")


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


A18 = ROOT / "scripts" / "config_fields_are_read_2026-09-11.py"
ARMS = ("d9_single_model_with_agents.json", "d9_multi_model_panel.json",
        "d11_seat_contrast_diversity_arm.json")


@pytest.fixture(scope="module")
def surveyed(mod):
    return mod.survey()


def _arm_data(name):
    import json
    f = ROOT / "bench" / "exp56_configs" / name
    if not f.is_file():
        pytest.skip(f"{name} not present")
    return json.loads(f.read_text(encoding="utf-8"))


class TestTheClassificationIsPinned:
    """ADDED 2026-09-17 (task 3.3, panel round 16). Executes the script's own
    `survey()` and `classify()`, the functions `main()` prints from."""

    def _exp56(self, surveyed):
        rows = [r for r in surveyed["rows"]
                if r["file"].startswith("bench/exp56_configs/")]
        if not rows:
            pytest.skip("no exp56 arm configs in this clone")
        return rows

    def test_the_two_read_instruments_agree_on_every_off_switch_field(
            self, surveyed):
        """2 independent resolvers, executed and compared: this script's
        `read_fields` and task A18's `readers_of`, over the same scope."""
        spec = importlib.util.spec_from_file_location("a18_for_33", A18)
        a18 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(a18)
        leaves = sorted({r["leaf"] for r in surveyed["rows"]})
        assert leaves, "no off-switch found; the comparison would be vacuous"
        for leaf in leaves:
            sites = [s for s in a18.readers_of(leaf)
                     if s.startswith("bench/") and "/logs/" not in s]
            mine = {r["read"] for r in surveyed["rows"] if r["leaf"] == leaf}
            assert mine == {bool(sites)}, (leaf, mine, sites)

    def test_only_max_papers_per_round_is_unread_and_its_block_explains_it(
            self, surveyed):
        rows = self._exp56(surveyed)
        unread = sorted((r["file"], r["path"]) for r in rows if not r["read"])
        assert unread == sorted(
            (f"bench/exp56_configs/{a}", "_ouroboros.max_papers_per_round")
            for a in ARMS), unread
        for r in rows:
            if not r["read"]:
                note = _arm_data(r["file"].rsplit("/", 1)[1])["_ouroboros"]["_note"]
                assert r["status"] == "DOCUMENTED" and r["why"] == note.strip()

    def test_the_counts_the_script_prints(self, surveyed):
        """15 off-switches, 12 read. Pinned so a config edit cannot move the
        figure without this going red, which is what happened on 2026-09-10."""
        rows = self._exp56(surveyed)
        assert len(rows) == 15, len(rows)
        assert sum(r["read"] for r in rows) == 12

    def test_no_off_switch_has_neither_a_note_nor_a_cited_record(self, surveyed):
        rows = self._exp56(surveyed)
        assert [r for r in rows if r["status"] == "UNEXPLAINED"] == []
        cited = sorted((r["file"], r["path"]) for r in rows if r["status"] == "CITED")
        assert cited == sorted((f"bench/exp56_configs/{a}", "hardened_gate_enabled")
                               for a in ARMS), cited
        for r in rows:
            if r["status"] == "CITED":
                assert r["cited"].startswith("_convergence_criteria.description: ")

    def test_deleting_the_block_note_makes_that_row_unexplained(self, mod, surveyed):
        """Control: the block-level lookup is what explains the row."""
        import copy
        data = copy.deepcopy(_arm_data(ARMS[0]))
        del data["_ouroboros"]["_note"]
        rows = {r["path"]: r for r in mod.classify(data, "x", surveyed["read"])}
        assert rows["_ouroboros.max_papers_per_round"]["status"] == "UNEXPLAINED"
        assert rows["merge_arbitration_enabled"]["status"] == "DOCUMENTED"

    def test_deleting_the_citation_makes_hardened_gate_unexplained(
            self, mod, surveyed):
        """Control: the cited record is what keeps the row from UNEXPLAINED."""
        import copy
        data = copy.deepcopy(_arm_data(ARMS[0]))
        data["_convergence_criteria"]["description"] = "TWO-SIDED GATE."
        rows = {r["path"]: r for r in mod.classify(data, "x", surveyed["read"])}
        assert rows["hardened_gate_enabled"]["status"] == "UNEXPLAINED"

    def test_the_lookups_on_constructed_configs(self, mod):
        data = {"a": [{"b": {"x_enabled": False, "_note": "why b"}}],
                "y_enabled": False,
                "z_enabled": False,
                "_doc": "y_enabled=true; not_z_enabled=false"}
        rows = {r["path"]: r for r in mod.classify(data, "x", {"x_enabled"})}
        assert rows["a[0].b.x_enabled"]["status"] == "DOCUMENTED"
        assert rows["a[0].b.x_enabled"]["why"] == "why b"
        assert rows["a[0].b.x_enabled"]["read"] is True
        assert rows["y_enabled"]["status"] == "UNEXPLAINED", "a different value is not a citation"
        assert rows["z_enabled"]["status"] == "UNEXPLAINED", "a longer name is not a citation"
