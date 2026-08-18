"""A merge must not delete a finding into a phantom, itself, or a cycle.

THE DEFECTS THIS PINS, all measured on the archive 2026-08-18.

1. ALIAS-KEY NORMALISATION. `_resolve_merge_source` stripped any model prefix
   from the id it was given, then looked the result up in an alias map that is
   keyed on the PREFIXED form. `parse_findings` mints `Codex_F001`, so
   `register()` writes `Codex:Codex_F001`, and the lookup asked for `Codex:F001`.
   Both forms a model can plausibly write therefore failed:

       MERGE C0001 <- F001        -> None   (the form FINDING_FORMAT teaches)
       MERGE C0001 <- Codex_F001  -> None   (the form the runner itself mints)

   An unresolved source is NOT dropped — `cdsfl_topology_formal.md:126-127`
   mandates recasting it as a CONFIRM on the target. So the failure was silent
   and it INVERTED the verdict: a model saying "these two are the same defect"
   was recorded as that model agreeing the target was real.

2. NO MERGE GUARDS. The spec requires the target to exist and be live
   (`:110-111`) and the merge graph to be acyclic (`:129-131`). Neither was
   enforced. exp37 carries a finding merged into ITSELF at severity 0.86; 21 of
   exp36's 86 merged entries sit inside a cycle, where the pointer chain never
   reaches a surviving entry and the family vanishes from the gate.

WHY A REFUSAL IS THE SAFE DIRECTION. A refused merge leaves the finding OPEN and
visible. A merge into a phantom, a self, or a cycle silently deletes a finding
that may be real. When in doubt the gate should see MORE, not less.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v2 import FindingRegistry, _resolve_merge_source  # noqa: E402
from bench.runner_core import parse_findings  # noqa: E402


def _registry(n: int = 3) -> FindingRegistry:
    reg = FindingRegistry()
    for i in range(1, n + 1):
        f = parse_findings(
            "M", 0,
            f"FINDING_ID: F00{i}\nSEVERITY: 0.90\n"
            f"DESCRIPTION: defect number {i} in the module under review.\n")[0]
        reg.register(f, "M")
    return reg


class TestAliasKeyNormalisation:

    @pytest.fixture
    def reg(self):
        reg = FindingRegistry()
        f = parse_findings(
            "Codex", 0,
            "FINDING_ID: F001\nSEVERITY: 0.90\n"
            "DESCRIPTION: verify() caches the first verifier and never rechecks.\n")[0]
        reg.register(f, "Codex")
        return reg

    def test_the_alias_map_is_keyed_on_the_prefixed_id(self, reg):
        """The precondition. If ids stop being minted pre-prefixed, the bug this
        file pins no longer exists in this form and the fix should be re-derived
        rather than trusted."""
        assert any(k.endswith("Codex_F001") for k in reg._alias_map)

    @pytest.mark.parametrize("written", ["F001", "Codex_F001", "C0001"])
    def test_every_form_a_model_may_write_resolves(self, reg, written):
        assert _resolve_merge_source(written, "Codex", reg) == "C0001"

    def test_an_unknown_id_still_resolves_to_nothing(self, reg):
        """Widening the lookup must not make it credulous."""
        assert _resolve_merge_source("F999", "Codex", reg) is None


class TestMergeGuards:

    def test_a_finding_cannot_be_merged_into_itself(self):
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C0001")
        assert reg.entries["C0001"].get("merged_into") is None
        assert reg.entries["C0001"]["status"] != "MERGED"

    def test_a_merge_into_a_phantom_target_is_refused(self):
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C9999")
        assert reg.entries["C0001"].get("merged_into") is None

    def test_a_two_cycle_is_refused(self):
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C0002")
        reg.resolve("C0002", "MERGED", 1, merged_into="C0001")
        assert reg.entries["C0002"].get("merged_into") is None

    def test_a_longer_cycle_is_refused(self):
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C0002")
        reg.resolve("C0002", "MERGED", 1, merged_into="C0003")
        reg.resolve("C0003", "MERGED", 1, merged_into="C0001")
        assert reg.entries["C0003"].get("merged_into") is None

    def test_a_legitimate_merge_still_applies(self):
        """The guards must refuse the pathological cases and nothing else."""
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C0002")
        assert reg.entries["C0001"]["merged_into"] == "C0002"
        assert reg.entries["C0001"]["status"] == "MERGED"

    def test_a_legitimate_chain_still_applies(self):
        reg = _registry()
        reg.resolve("C0001", "MERGED", 1, merged_into="C0002")
        reg.resolve("C0002", "MERGED", 1, merged_into="C0003")
        assert reg.entries["C0002"]["merged_into"] == "C0003"

    def test_a_non_merge_resolve_is_untouched(self):
        reg = _registry()
        reg.resolve("C0001", "CLOSED", 2)
        assert reg.entries["C0001"]["status"] == "CLOSED"
        assert reg.entries["C0001"]["last_status_change_round"] == 2


class TestTheArchiveStillReproduces:
    """The guards change future runs. They must not change the replay of past
    ones, because every measurement this week rests on that replay."""

    def test_the_replay_exit_test_still_passes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "replay_accounting", REPO / "scripts" / "replay_accounting.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.verify() == 0, "the replay no longer reproduces the archive"
