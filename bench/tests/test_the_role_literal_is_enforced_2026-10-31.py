"""FOLDED BACK 2026-11-01. Written by panel seat `cc2`, joint round 2026-10-31.

HIS ACCEPTANCE, verbatim: *"I accept the panel's recommendation on role
assignment."* Both seats converged on TWO DIMENSIONS ONE LAYER, and the second
seat applied this seat's repair verbatim in the joint round, so what was folded
back is the composed form rather than one seat's.

WHY THIS TEST COULD NOT BE FOLDED BEFORE TODAY, and the record said so: the
preservation step kept this test and NOT the implementation it tests, so folding
it would have added a permanently-red guard for code that did not exist.
`bench/tests/test_the_role_vocabulary_has_forked_2026-10-31.py` carried an
assertion to that effect whose own message read *"ROLE_ALIASES now exists in the
tree, so cc2's test is foldable and this test is stale"*. The implementation is
in the tree now, so that assertion is inverted and this test is live.

THE SEAT'S OWN DOCSTRING FOLLOWS, UNEDITED.

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

import pathlib

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


#: The 2 literals the live sites compare a seat role against directly.
_COMPARED = ("collator", "player_manager")


def test_normalisation_preserves_every_live_read():
    """The 2 reads the brief cites plus the confer split and the role lookup.

    `reference_runner_v3.py:13189`/`:13269` and 16 siblings: `!= "collator"`.
    `run_exp20_confer.py:253`/`:533`: `== "player_manager"`.

    ★ NARROWED 2026-11-08 ON A MEASUREMENT, NOT A JUDGEMENT, and the narrowing
    is recorded because it exists to let his ruling through. His ruling of
    decision 13 is *"Aliases only"*, entering `orchestrator`, `classifier` and
    `worker`. 2 of those 3 are aliases FOR the literals the live sites compare
    against, which `player` and `reviewer` never were, so the original form of
    this assertion refused them: `"orchestrator" == "player_manager"` is False
    while its target's is True.

    THE PROPERTY THAT ACTUALLY MATTERS is that a live read never SEES an
    un-normalised seat role, and that is asserted directly below instead of
    approximated by comparing strings. Measured 2026-11-08: `ModelConfig`
    normalises in `__post_init__`, and of the 6 raw `role` reads anywhere in
    `bench/` and `scripts/`, 0 are seat roles -- every one is a CHAT MESSAGE
    role compared against `assistant`, `tool`, `user` or a tool-call label. So
    the stricter form protected a path that does not exist, and refusing his
    ruling to keep it would have been the guard-accuses-correct-code shape.

    WHAT IS STILL REFUSED, so the narrowing is not a licence: an alias whose
    target is NOT one of the compared literals must still compare identically,
    because for those there is no normalisation step to rely on in a reader
    that compares the raw value.
    """
    for alias, target in ROLE_ALIASES.items():
        if target in _COMPARED:
            # The comparison cannot agree by construction; what must hold is
            # that construction normalises, so no reader sees the raw spelling.
            assert _mc(alias).role == target
            continue
        assert (alias != "collator") == (target != "collator")
        assert (alias == "player_manager") == (target == "player_manager")


def test_no_seat_role_is_read_without_being_normalised():
    """THE PROPERTY THE NARROWING ABOVE RESTS ON, asserted rather than assumed.

    If a raw seat-role read is ever introduced, the exemption above stops being
    safe and this fails. It counts raw `role` reads across the tree and requires
    every one to be a CHAT MESSAGE role -- established by what it is compared
    against, not by the variable's name.
    """
    import re
    root = pathlib.Path(__file__).resolve().parents[2]
    raw = []
    for d in ("bench", "scripts"):
        for f in sorted((root / d).glob("*.py")):
            txt = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'(\["role"\]|\.get\("role"\))', txt):
                line_no = txt[:m.start()].count("\n")
                window = "\n".join(txt.splitlines()[line_no:line_no + 6])
                raw.append((f.name, window))
    assert raw, "0 raw role reads found; the measurement this rests on is vacuous"
    seat = [(n, w) for n, w in raw
            if re.search(r'"(collator|player_manager|participant)"', w)]
    assert not seat, (
        f"{len(seat)} raw seat-role read(s) now exist, so an alias for a "
        f"compared literal can reach a live comparison un-normalised: "
        f"{[n for n, _ in seat][:3]}")


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
