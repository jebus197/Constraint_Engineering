# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_role_layer_b21_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fdbe92031281328c6c5d5e26eb14660add03701c4b939bc892c54f089910e66d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The structural role vocabulary is declared twice and must not fork silently.

ESTABLISHED BY EXECUTION, panel round `the_role_layer_b21_2026-10-30`: the 3
structural role concepts are declared in 2 unlinked places --
`bench/experiment_11_orchestrator.py:59` as
`Role = Literal["collator", "player_manager", "participant"]`, and
`bench/dm/_types.py:311` as `Role(enum.Enum)` with members PM / COL / PAR, the
declaration that carries the reassignment semantics (PM static for the run,
HARD constraint C3; COL and PAR reassignable between rounds by
`RoleAssignment.reassign`). Nothing mapped the two, and the `Literal` is not
enforced at runtime: `bench/tools/run_simulated_experiment.py:638` and
`bench/tools/gemini_tool_switch_test.py:72` passed `role="player"`, a 4th value
outside the declared vocabulary, to live `ModelConfig` constructions. No code
compares `== "player"` anywhere (measured 2026-10-31: the only live role
comparisons are `!= "collator"` at `bench/reference_runner_v3.py:13189`/
`:13269` and `player_manager` in `bench/run_exp20_confer.py`), so the stray
value changed no behaviour -- which is exactly why nothing noticed it.

WHY THIS GUARD EXISTS. Entry B21 asks whether the structural vocabulary should
be renamed to the founder's functional one. Whatever he rules, a rename applied
to ONE declaration and not the other would silently detach the reassignment
semantics from the vocabulary used at dispatch. This test makes that fork loud:

  1. the two declarations must stay in explicit bijection;
  2. every quoted `role=` value passed to `ModelConfig` in live bench code
     must be a member of the declared `Literal`.

It pins the CORRESPONDENCE, not the words -- if both declarations are renamed
together, update CORRESPONDENCE here in the same change and the guard holds
the new vocabulary instead.
"""
from __future__ import annotations

import ast
import pathlib
import typing

import pytest

from bench import experiment_11_orchestrator as orch
from bench.dm._types import Role as DmRole

REPO = pathlib.Path(__file__).resolve().parents[2]

#: The asserted bijection between the orchestrator's string vocabulary and the
#: dm enum's members. A rename of either side alone fails test 1 and names the
#: other side as the thing left behind.
CORRESPONDENCE = {
    "collator": "COL",
    "player_manager": "PM",
    "participant": "PAR",
}


def test_the_two_declarations_are_in_bijection():
    literal_values = set(typing.get_args(orch.Role))
    enum_values = {m.value for m in DmRole}
    assert literal_values == set(CORRESPONDENCE), (
        f"the orchestrator Literal changed to {sorted(literal_values)} without "
        f"updating the correspondence to bench/dm/_types.py Role; the "
        f"reassignment semantics (PM static, HARD C3) live on the OTHER "
        f"declaration and would silently detach")
    assert enum_values == set(CORRESPONDENCE.values()), (
        f"bench/dm/_types.py Role changed to {sorted(enum_values)} without "
        f"updating the correspondence to the orchestrator Literal used at "
        f"dispatch (mc.role reads in reference_runner_v3)")
    assert len(set(CORRESPONDENCE.values())) == len(CORRESPONDENCE), (
        "the correspondence is not a bijection")


def _live_python():
    """Live bench .py files: not tests, not logs, not archived harvests."""
    for p in (REPO / "bench").rglob("*.py"):
        rel = p.relative_to(REPO).as_posix()
        if "/logs/" in rel or rel.startswith("bench/tests/"):
            continue
        yield p


def _modelconfig_role_values(paths):
    """Every quoted value passed as `role=` to a ModelConfig(...) call."""
    out = []
    for p in paths:
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else "")
            if name != "ModelConfig":
                continue
            for kw in node.keywords:
                if kw.arg == "role" and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    try:
                        rel = p.relative_to(REPO).as_posix()
                    except ValueError:  # planted file outside the repo
                        rel = p.name
                    out.append((rel, kw.value.lineno, kw.value.value))
    return out


def test_every_live_modelconfig_role_is_in_the_declared_vocabulary():
    declared = set(typing.get_args(orch.Role))
    strays = [(f, ln, v) for f, ln, v in
              _modelconfig_role_values(_live_python()) if v not in declared]
    assert not strays, (
        "live code passes role values outside the declared Literal, which is "
        "unenforced at runtime, so the vocabulary has forked silently:\n"
        + "\n".join(f"    {f}:{ln}  role={v!r}" for f, ln, v in strays))


def test_the_scanner_can_see_a_planted_stray(tmp_path):
    """ANTI-VACUITY: a scanner that misses a planted stray proves nothing."""
    planted = tmp_path / "planted.py"
    planted.write_text(
        "mc = ModelConfig(label='x', role='striker')\n", encoding="utf-8")
    vals = _modelconfig_role_values([planted])
    assert ("planted.py" in vals[0][0] if vals else False) or any(
        v == "striker" for _, _, v in vals), (
        "a planted out-of-vocabulary role was not seen, so a real one would "
        "pass too")


def test_the_scanner_reads_real_sites():
    """A scan that finds 0 construction sites is scanning the wrong tree."""
    vals = _modelconfig_role_values(_live_python())
    assert len(vals) >= 3, (
        f"only {len(vals)} quoted ModelConfig role site(s) found in live "
        f"bench code; the vocabulary scan has gone blind")
