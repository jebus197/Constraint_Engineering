"""The 4 interface roles the UX brief specifies must be offerable, and the map must be honest.

★ WHAT WAS WRONG. B142, the settings-surface entry, measured that
`bench/model_catalogue.known_roles()` returned `['collator', 'participant',
'player_manager']` while section 10 of the authoritative UX design brief and
the mockup `html_sources/v6/08_settings.html` both specify **Orchestrator,
Worker, Researcher, Classifier**. The role half of the model-and-role selector
could not be populated as designed.

★ WHY IT COULD NOT SIMPLY BE RENAMED. The panel round of 2026-10-31, recorded
in `experimental_notes/Panel_FULL_RECORD_Role_Layer_B21_2026-10-31.md`, measured
that the structural and functional vocabularies are 2 DISTINCT DIMENSIONS whose
reconciliation is lossy in both directions, and that at most 1 new layer is ever
warranted. `classifier` names no seat position; `collator` names the HARNESS
rather than a seat.

★ WHAT HIS RULING SUPPLIED. 2026-11-12, verbatim: *"Verdict. Yes do both. stm"*.
That is the policy B21 recorded as owed by him.

★ THE PROPERTY THIS FILE EXISTS TO HOLD, and it is the one a careless repair
breaks: **the 2 holes in the map must stay holes.** `classifier` and
`researcher` map to no structural role. A repair that quietly pointed them at
`participant` would look tidier and would invent the policy the layer exists not
to invent, and nothing else in the tree would notice.

EXECUTES the accessors. It does not read their source text.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from bench import model_catalogue as mc  # noqa: E402

THE_4 = ("orchestrator", "worker", "researcher", "classifier")
THE_3 = ("collator", "participant", "player_manager")


def test_all_4_interface_roles_are_offerable():
    functional = mc.known_roles("functional")
    for r in THE_4:
        assert r in functional, (
            f"{r} is not offerable, so the selector cannot present the 4 roles "
            f"the UX brief specifies")
    assert len(functional) == 4


def test_the_3_structural_roles_are_unchanged():
    assert sorted(mc.known_roles("structural")) == sorted(THE_3)


def test_the_default_call_still_returns_every_role():
    """B21's own step-5 guard calls `known_roles()` bare; it must keep working."""
    assert sorted(mc.known_roles()) == sorted(THE_3 + THE_4)


def test_the_2_axes_partition_with_nothing_in_both_and_nothing_in_neither():
    allr, s, f = set(mc.known_roles()), set(mc.known_roles("structural")), set(mc.known_roles("functional"))
    assert s | f == allr
    assert not (s & f)


def test_an_unknown_axis_returns_empty_rather_than_everything():
    """A typo in the axis must not silently yield the unfiltered list."""
    assert mc.known_roles("strcutural") == []


def test_the_2_mapped_roles_map_where_the_panel_measured():
    assert mc.structural_for("orchestrator") == "player_manager"
    assert mc.structural_for("worker") == "participant"


def test_the_2_unmapped_roles_stay_unmapped():
    """★ THE LOAD-BEARING ONE. A tidy guess here would invent his policy."""
    assert mc.structural_for("classifier") is None, (
        "classifier was given a structural counterpart. The 2026-10-31 panel "
        "measured that it names no seat position; pointing it at participant "
        "invents policy B21 records as the founder's.")
    assert mc.structural_for("researcher") is None, (
        "researcher was given a structural counterpart. It is newer than the "
        "panel that measured the other 3 and has no counterpart measured.")


def test_a_name_outside_his_4_raises_rather_than_returning_none():
    """None must mean 'measured to have no counterpart', never 'unknown name'.

    ★ STRENGTHENED 2026-11-14 BECAUSE THE MUTATION HARNESS EXPOSED IT AS WEAK.
    `pytest.raises(KeyError)` alone passes whether the error is the EXPLICIT
    one or an incidental `KeyError` from the bare dict lookup, so it could not
    tell the deliberate refusal from an accident. The explicit raise exists so
    the message says WHY, and the message is now asserted.
    """
    for bad in ("participant", "typo"):
        with pytest.raises(KeyError) as ei:
            mc.structural_for(bad)
        msg = str(ei.value)
        assert "4 interface roles" in msg, (
            f"{bad!r} raised a bare KeyError rather than the explicit refusal; "
            f"a caller cannot tell an unknown name from a measured hole")
        for r in THE_4:
            assert r in msg, "the refusal does not name the 4 roles it accepts"


def test_the_reverse_map_names_the_structural_role_his_list_has_no_word_for():
    assert mc.STRUCTURAL_TO_FUNCTIONAL["collator"] is None, (
        "collator was given a functional counterpart. The 2026-10-31 panel "
        "measured that it names the harness and not a seat.")
    assert mc.STRUCTURAL_TO_FUNCTIONAL["player_manager"] == "orchestrator"
    assert mc.STRUCTURAL_TO_FUNCTIONAL["participant"] == "worker"


def test_the_axis_is_read_from_the_file_and_not_from_a_list_in_the_module():
    """A role added to the registry must not be invisible to the accessor.

    This is the defect `bench/cdsfl_registry/registry.py` records at its layer
    walk: a 3-item hardcoded list left layer 5 unvalidated the day it was
    created. Asserted by creating a real role file and calling the accessor.
    """
    probe = REPO / "bench" / "cdsfl_registry" / "roles" / "zz_axis_probe.toml"
    assert not probe.exists(), "the probe path is occupied; refusing to overwrite"
    probe.write_text('[role]\nname = "zz_axis_probe"\naxis = "functional"\n',
                     encoding="utf-8")
    try:
        assert mc.role_axis("zz_axis_probe") == "functional"
        assert "zz_axis_probe" in mc.known_roles("functional")
    finally:
        probe.unlink()
    assert "zz_axis_probe" not in mc.known_roles(), "the probe was not removed"


def test_the_renderer_reports_the_2_vocabularies_separately():
    """Mixing 7 names from 2 non-reconciling vocabularies on 1 line is the defect."""
    out = mc.render([])
    assert "structural:" in out and "functional" in out
    assert "orchestrator" in out and "player_manager" in out


def test_dispatch_is_untouched_by_the_functional_names():
    """NON-VACUITY ON THE BOUNDARY the entry claims: the scorer uses the ENUM.

    If a functional name ever became a member of the dispatch `Role`, this
    repair would have changed how a run selects models -- which B142 says it
    does not, and which B21 records as the founder's to decide.
    """
    from bench.dm._types import Role
    members = {r.value for r in Role}
    for r in THE_4:
        assert r not in members, (
            f"{r} has entered the dispatch Role enum. The settings-surface "
            f"ruling does not authorise changing model selection.")
