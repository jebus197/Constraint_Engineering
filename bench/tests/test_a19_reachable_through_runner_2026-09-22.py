#!/usr/bin/env python3
"""Task A19's flag must be REACHABLE: the prose forced-off gate consults it.

THE DEFECT THIS PINS. `RunnerConfig.sk_score_prose_listings` (the founder's
third outcome: purely prose -> NO_SCORE, fenced listings inside prose ->
scored) was wired end to end -- config field, call-site kwarg, compute_sk
branch -- yet unreachable through the runner: `run_experiment` forced
`sk_enabled=False` for every non-Python target BEFORE the flag's only call
site (`if cfg.sk_enabled:`), so no configuration could ever execute the A19
branch. An addition nothing reaches, the additive standard's most-confirmed
defect class (11 since 2026-08-01). Demonstrated by execution in
`scripts/falsify_a19_unreachable_2026-09-22.py` before the repair; this test
keeps it repaired.

INVARIANTS PINNED, each executed:
  1. The if-chain that sets `sk_forced_off = True` consults
     `sk_score_prose_listings` (AST, not substring-in-file, so a comment
     cannot satisfy it).
  2. With the flag OFF (every existing config), the forced-off override is
     still present with its original guard -- the safety default is unchanged.
  3. Downstream, `compute_sk` still honours the flag on the real arm-4
     target: NO_SCORE with it off, not-NO_SCORE with it on.

Run:  python3 -m pytest bench/tests/test_a19_reachable_through_runner_2026-09-22.py -q
"""
from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    SK_NO_SCORE, RunnerConfig, compute_sk, _capture_baseline,
)

RUNNER = REPO / "bench" / "reference_runner_v3.py"
TARGET = REPO / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"


def _forced_off_if_chain() -> list:
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    hits: list = []

    class Finder(ast.NodeVisitor):
        def __init__(self) -> None:
            self._stack: list = []

        def visit_If(self, node) -> None:
            self._stack.append(node)
            self.generic_visit(node)
            self._stack.pop()

        def visit_Assign(self, node) -> None:
            for t in node.targets:
                if (isinstance(t, ast.Name) and t.id == "sk_forced_off"
                        and isinstance(node.value, ast.Constant)
                        and node.value.value is True and self._stack):
                    hits.extend(self._stack)
            self.generic_visit(node)

    Finder().visit(tree)
    assert hits, "sk_forced_off = True vanished; re-derive this test"
    return hits


def test_gate_consults_the_a19_flag():
    chain = "\n".join(ast.unparse(i) for i in _forced_off_if_chain())
    assert "sk_score_prose_listings" in chain, (
        "the forced-off if-chain never consults sk_score_prose_listings: "
        "the A19 flag is unreachable through the runner again")


def test_default_off_keeps_the_forced_off_override():
    """The safety override survives for every config that does not opt in."""
    assert RunnerConfig.__dataclass_fields__[
        "sk_score_prose_listings"].default is False
    chain = "\n".join(ast.unparse(i.test) for i in _forced_off_if_chain())
    assert "target_kind != TARGET_KIND_PYTHON" in chain
    assert "cfg.sk_enabled" in chain


def test_compute_sk_still_honours_the_flag_downstream():
    source = TARGET.read_text(encoding="utf-8")
    baseline = _capture_baseline(source, source_path=str(TARGET))
    off = compute_sk("no blocks", source, str(TARGET), baseline=baseline,
                     score_prose_listings=False)
    on = compute_sk("no blocks", source, str(TARGET), baseline=baseline,
                    score_prose_listings=True)
    assert off.tristate == SK_NO_SCORE
    assert on.tristate != SK_NO_SCORE
