# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_role_layer_b21_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a44757c55f446d1b33422d5d81c1837d5d4391ec334f0a7a725aa1cbfd81446f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Guard: the structural role vocabulary cannot fork silently (round B21).

Pins (1) the explicit bijection between the two unlinked structural Role
declarations -- experiment_11_orchestrator.Role (strings) and
bench/dm/_types.Role (PM/COL/PAR enum) -- and (2) that every quoted role=
passed to ModelConfig in live bench code (tests and logs excluded) is a
declared member of the orchestrator Literal. Anti-vacuity: a planted stray
must be caught; the scan must be non-empty.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import get_args

from bench.experiment_11_orchestrator import Role as OrchRole
from bench.dm._types import Role as DmRole

REPO = Path(__file__).resolve().parent.parent.parent
BENCH = REPO / "bench"
BIJECTION = {"collator": "COL", "player_manager": "PM", "participant": "PAR"}


def _scan_role_literals(root: Path, extra_file: Path | None = None):
    """Collect (path, lineno, value) for every string literal role= kwarg
    on a ModelConfig(...) call, including both arms of a conditional."""
    hits = []
    files = [
        p for p in root.rglob("*.py")
        if "logs" not in p.parts and "tests" not in p.parts
    ]
    if extra_file is not None:
        files.append(extra_file)
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
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
                if kw.arg != "role":
                    continue
                vals = []
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    vals = [kw.value.value]
                elif isinstance(kw.value, ast.IfExp):
                    for arm in (kw.value.body, kw.value.orelse):
                        if isinstance(arm, ast.Constant) and isinstance(arm.value, str):
                            vals.append(arm.value)
                for v in vals:
                    try:
                        shown = str(path.relative_to(REPO))
                    except ValueError:
                        shown = str(path)
                    hits.append((shown, node.lineno, v))
    return hits


def test_the_two_declarations_are_bijective():
    orch = set(get_args(OrchRole))
    dm = {m.value for m in DmRole}
    assert orch == set(BIJECTION.keys()), orch
    assert dm == set(BIJECTION.values()), dm
    assert len(set(BIJECTION.values())) == len(BIJECTION)


def test_no_stray_role_literal_in_live_bench_code():
    declared = set(get_args(OrchRole))
    strays = [h for h in _scan_role_literals(BENCH) if h[2] not in declared]
    assert not strays, f"undeclared role spellings in live code: {strays}"


def test_the_scan_is_live():
    assert len(_scan_role_literals(BENCH)) >= 1, "scanner found no ModelConfig role kwargs; vacuous"


def test_a_planted_stray_is_caught(tmp_path):
    planted = tmp_path / "planted_stray.py"
    planted.write_text(
        'from bench.experiment_11_orchestrator import ModelConfig\n'
        'mc = ModelConfig(label="x", model_id="x", api="sim", role="striker",\n'
        '                 system_prompt_path=None)\n'
    )
    hits = _scan_role_literals(BENCH, extra_file=planted)
    assert any(v == "striker" for _, _, v in hits), "planted stray not caught"
