#!/usr/bin/env python3
"""FALSIFIER: the A19 flag `sk_score_prose_listings` is unreachable through the runner.

THE CLAIM UNDER TEST. Task A19 is the founder's third outcome: a purely prose
target records NO_SCORE ("nothing to compute") while reducible fenced listings
INSIDE a prose target are still scored. The flag exists (`RunnerConfig.
sk_score_prose_listings`, reference_runner_v3.py:1492), is threaded to
`compute_sk` (10881), and `compute_sk` honours it (10938). But
`run_experiment` forces `sk_enabled=False` for EVERY non-Python target
(13090-13102) BEFORE the only call site that reads the flag (14731,
`if cfg.sk_enabled:`), so through the runner the flag can never take effect:

  * kind == python  -> `_scoring_prose` requires kind != python  -> flag inert;
  * kind != python  -> sk pipeline forced off -> evaluator never called.

That is the "addition nothing reaches" defect class of the additive standard
(11 confirmed since 2026-08-01). Arm 4's own report records the force:
`"sk_enabled_requested": true, "sk_enabled_effective": false,
"sk_forced_off_by_target_kind": true`.

TWO CHECKS, both executed:

  1. DOWNSTREAM WORKS. `compute_sk` on the real arm-4 target with
     score_prose_listings=True does NOT return NO_SCORE (and does with False)
     -- so the only blocker is the call-site gate.
  2. THE GATE NEVER CONSULTS THE FLAG. AST-walk the runner, find the
     `sk_forced_off = True` assignment, and test whether
     `sk_score_prose_listings` is consulted anywhere in the guarding
     if-chain. If it is not, the flag is dead through the runner: print
     FALSIFIED.

Fails (prints FALSIFIED, exit 1) iff the defect is present; exits cleanly
once the forced-off gate consults the flag.

Run:  python3 scripts/falsify_a19_unreachable_2026-09-22.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    SK_NO_SCORE, compute_sk, _capture_baseline,
)

TARGET = REPO / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
RUNNER = REPO / "bench" / "reference_runner_v3.py"


def check_downstream_works() -> None:
    """compute_sk honours the flag when it is actually handed to it."""
    source = TARGET.read_text(encoding="utf-8")
    baseline = _capture_baseline(source, source_path=str(TARGET))
    fix = "no blocks here"
    off = compute_sk(fix, source, str(TARGET), baseline=baseline,
                     score_prose_listings=False)
    on = compute_sk(fix, source, str(TARGET), baseline=baseline,
                    score_prose_listings=True)
    assert off.tristate == SK_NO_SCORE, (
        f"expected NO_SCORE with the flag off, got {off.tristate}")
    assert on.tristate != SK_NO_SCORE, (
        "compute_sk ignored score_prose_listings=True on a listing-bearing "
        "prose target -- the downstream is broken, not just the call site")
    print(f"  downstream: flag off -> {off.tristate}; flag on -> {on.tristate} "
          f"(short-circuit bypassed) -- compute_sk honours the flag")


def gate_consults_flag() -> bool:
    """Does the code path that sets sk_forced_off consult the A19 flag?"""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))

    class Finder(ast.NodeVisitor):
        def __init__(self) -> None:
            self.hit_ifs = []
            self._stack = []

        def visit_If(self, node):
            self._stack.append(node)
            self.generic_visit(node)
            self._stack.pop()

        def visit_Assign(self, node):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "sk_forced_off":
                    if (isinstance(node.value, ast.Constant)
                            and node.value.value is True and self._stack):
                        self.hit_ifs.extend(self._stack)
            self.generic_visit(node)

    f = Finder()
    f.visit(tree)
    assert f.hit_ifs, ("`sk_forced_off = True` no longer exists under an if -- "
                       "this falsifier is stale, re-derive it")
    guard_src = "\n".join(ast.unparse(i.test) for i in f.hit_ifs)
    chain_src = "\n".join(ast.unparse(i) for i in f.hit_ifs)
    consulted = "sk_score_prose_listings" in chain_src
    print(f"  gate guard(s): {guard_src}")
    print(f"  gate consults sk_score_prose_listings: {consulted}")
    return consulted


def main() -> int:
    check_downstream_works()
    if not gate_consults_flag():
        print("FALSIFIED: run_experiment forces sk_enabled=False for every "
              "non-Python target without consulting sk_score_prose_listings, "
              "and the flag's only call site sits behind `if cfg.sk_enabled:` "
              "(reference_runner_v3.py:14731). The A19 flag is unreachable "
              "through the runner -- an addition nothing reaches.")
        return 1
    print("OK: the forced-off gate consults the A19 flag; the third outcome "
          "is reachable through the runner.")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole falsifier. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
