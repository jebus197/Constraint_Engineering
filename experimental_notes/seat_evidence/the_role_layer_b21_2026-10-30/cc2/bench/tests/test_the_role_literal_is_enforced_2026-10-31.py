# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_role_layer_b21_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ffacb54b72579f822fd38e07d5e491654add7efd169160232b32512bfd74bdf3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""`Role` is enforced at construction, and the enforcement preserves behaviour.

Panel round `the_role_layer_b21_2026-10-30`. Before this, `Role` at
`bench/experiment_11_orchestrator.py:59` was a `Literal` annotation that no
runtime check read, and an AST scan of every live `ModelConfig(role=...)` site
(`scripts/how_many_role_values_does_the_code_construct_2026-10-31.py`) found 4
spellings against 3 declared members: `player` at 9 sites and `reviewer` at 4.

These tests pin the 3 properties that matter and NOT the alias table's contents,
which are the founder's to extend:

  1. the enforcement reaches every construction, because it is in `__post_init__`
  2. it is behaviour-PRESERVING at every live read, so it is not a change of
     dispatch disguised as a type fix
  3. `Role` is the single source of truth -- `canonical_role` reads
     `get_args(Role)` rather than a second list that could drift
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.experiment_11_orchestrator import (  # noqa: E402
    ExperimentConfig,
    ModelConfig,
    ROLE_ALIASES,
    Role,
    canonical_role,
)


def _mc(role: str) -> ModelConfig:
    return ModelConfig(label="T", model_id="sim", api="sim",
                       role=role, system_prompt_path=None)


def test_every_declared_member_round_trips():
    for member in get_args(Role):
        assert canonical_role(member) == member
        assert _mc(member).role == member


def test_an_undeclared_spelling_cannot_survive_construction():
    """The defect: a spelling outside `Role` reaching a reader unchanged."""
    for spelling in ("goalkeeper", "striker", "", "Participant"):
        with pytest.raises(ValueError, match="unknown ModelConfig role"):
            _mc(spelling)


def test_every_alias_resolves_to_a_declared_member():
    """Pins the INVARIANT, not the table. An alias naming a non-member would
    reintroduce the drift through the mechanism built to close it."""
    assert ROLE_ALIASES, "an empty alias table is an addition nothing reaches"
    for alias, target in ROLE_ALIASES.items():
        assert alias not in get_args(Role), f"{alias!r} is a member, not an alias"
        assert target in get_args(Role), f"alias {alias!r} -> non-member {target!r}"
        assert _mc(alias).role == target


def test_normalisation_preserves_every_live_read():
    """The 2 reads the brief cites plus the confer split and the role lookup.

    `reference_runner_v3.py:13189`/`:13269` and 16 siblings: `!= "collator"`.
    `run_exp20_confer.py:253`/`:533`: `== "player_manager"`.
    Behaviour must be identical before and after normalisation for every alias.
    """
    for alias, target in ROLE_ALIASES.items():
        assert (alias != "collator") == (target != "collator")
        assert (alias == "player_manager") == (target == "player_manager")


def test_an_aliased_seat_is_now_found_by_a_role_keyed_lookup():
    """This is the only behaviour that CHANGES, and it changes in one direction.

    `ExperimentConfig.get_by_role` compares for equality, so before
    normalisation a seat constructed as `player` was invisible to
    `get_by_role("participant")` while still being dispatched by the
    `!= "collator"` filter. A role-KEYED policy layer would inherit that
    asymmetry.
    """
    cfg = ExperimentConfig(models=[_mc("player"), _mc("participant")])
    assert len(cfg.get_by_role("participant")) == 2
    assert cfg.get_by_role("collator") == []


def test_canonical_role_reads_the_literal_not_a_copy():
    """No second hand-written member list anywhere in the module source."""
    src = (Path(__file__).resolve().parents[1]
           / "experiment_11_orchestrator.py").read_text(encoding="utf-8")
    assert "get_args(Role)" in src, "members must be derived from `Role` itself"
    # The members appear in exactly one place: the `Role` assignment.
    assert src.count('"collator", "player_manager", "participant"') == 1
