#!/usr/bin/env python3
"""The switches enabled in no configuration: retain, schedule, or retire?

THE FOUNDER'S VERDICT, 2026-10-06, on the toggle design brief: *"Verdict, do the
investigation and do the work."*

WHAT THE BRIEF REPORTED. 6 of the 25 boolean switches are armed in 0 of 49 real
configuration files and are not turned on in simulation. The additive standard says an
addition nothing reaches is not additive, so each needs a decision.

WHY A RAW REFERENCE COUNT CANNOT DECIDE IT. Grepping the name returns hundreds of hits
for every switch, because `resume` is a substring of `resumed` and `presume`, and
because a switch is discussed in comments far more often than it is read. The
discriminators that matter are narrower, and all 3 are structural facts an AST can
settle:

  READ BY LIVE CODE   — does any non-test module actually read the field?
  TURNED ON BY A TEST — does any test set it True? A switch no test ever enables has
                        never had its ON path executed, whatever the comments claim.
  GATES A BRANCH      — is the read used as a condition, or merely passed along?

A switch that is read, enabled by a test and gates a branch is DORMANT BY CHOICE and
should be retained. One that nothing enables has an unexercised ON path and should be
scheduled for study before anyone relies on it. One that live code never reads is dead.

Run: python3 scripts/dormant_switch_investigation_2026-10-07.py
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

SWITCHES = ("discrimination_control_blocks", "hil_review",
            "immune_memory_consume_rk0", "models_were_declared", "resume",
            "stall_gamma_termination_enabled")


def _py(root, tests: bool):
    for p in root.rglob("*.py"):
        rel = p.relative_to(REPO).as_posix()
        if ".claude/worktrees" in rel or "sandbox_harvest" in rel:
            continue
        if ("/tests/" in rel) == tests:
            yield p


def _reads_and_gates(tree, name):
    """(read_count, gate_count) for `X.name` or `getattr(X, "name", ...)`.

    A GATE IS COUNTED THROUGH ONE LOCAL ASSIGNMENT, and the first version of this
    tool was wrong for want of that. It counted a read as a gate only when the read
    NODE itself sat inside a condition, so the extremely common shape

        explicitly = bool(getattr(cfg, "models_were_declared", False))
        if not declared or (not explicitly and ...):

    scored 1 read and 0 gates, and the switch was reported as "read but gates
    nothing" -- the project's own name for a dead addition. It gates a real branch.
    A measurement that under-reports in the direction of condemning working code is
    worse than no measurement, because the recommended action is destructive.
    """
    reads = gates = 0
    conds = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While)):
            for sub in ast.walk(node.test):
                conds.add(id(sub))
        if isinstance(node, ast.IfExp):
            for sub in ast.walk(node.test):
                conds.add(id(sub))
    def _is_read(node):
        if isinstance(node, ast.Attribute) and node.attr == name:
            return True
        return (isinstance(node, ast.Call)
                and getattr(node.func, "id", None) == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == name)

    # Locals that carry the value of a read, so a condition on them is a gate.
    aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                _is_read(sub) for sub in ast.walk(node.value)):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    aliases.add(t.id)

    alias_in_cond = set()
    for node in ast.walk(tree):
        tests = []
        if isinstance(node, (ast.If, ast.While, ast.IfExp)):
            tests = [node.test]
        for t in tests:
            for sub in ast.walk(t):
                if isinstance(sub, ast.Name) and sub.id in aliases:
                    alias_in_cond.add(sub.id)

    for node in ast.walk(tree):
        if _is_read(node):
            reads += 1
            if id(node) in conds:
                gates += 1
    gates += len(alias_in_cond)
    return reads, gates


def _enabled_by_test(tree, name):
    """Does a test set this field True, by keyword or by assignment?"""
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == name:
            if isinstance(node.value, ast.Constant) and node.value.value is True:
                return True
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (isinstance(t, ast.Attribute) and t.attr == name
                        and isinstance(node.value, ast.Constant)
                        and node.value.value is True):
                    return True
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "setattr"
                and len(node.args) >= 3
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == name
                and isinstance(node.args[2], ast.Constant)
                and node.args[2].value is True):
            return True
        # dict literal: {"name": True}
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if (isinstance(k, ast.Constant) and k.value == name
                        and isinstance(v, ast.Constant) and v.value is True):
                    return True
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dormant_switch_investigation_2026-10-07.py",
        description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true")
    ap.parse_args(argv)

    live_trees, test_trees = [], []
    for p in _py(REPO / "bench", tests=False):
        try:
            live_trees.append(ast.parse(p.read_text(encoding="utf-8", errors="ignore")))
        except SyntaxError:
            pass
    for p in _py(REPO / "scripts", tests=False):
        try:
            live_trees.append(ast.parse(p.read_text(encoding="utf-8", errors="ignore")))
        except SyntaxError:
            pass
    for p in (REPO / "bench" / "tests").rglob("*.py"):
        try:
            test_trees.append(ast.parse(p.read_text(encoding="utf-8", errors="ignore")))
        except SyntaxError:
            pass

    print("=" * 86)
    print(f"{'switch':34s} {'live reads':>10s} {'gates':>6s} {'test turns it ON':>18s}  verdict")
    print("=" * 86)
    rows = []
    for name in SWITCHES:
        reads = gates = 0
        for t in live_trees:
            r, g = _reads_and_gates(t, name)
            reads += r
            gates += g
        on = any(_enabled_by_test(t, name) for t in test_trees)
        if reads == 0:
            verdict = "RETIRE — live code never reads it"
        elif not on:
            verdict = "SCHEDULE — ON path never executed"
        elif gates == 0:
            verdict = "SCHEDULE — read but gates nothing"
        else:
            verdict = "RETAIN — dormant by choice"
        rows.append((name, reads, gates, on, verdict))
        print(f"  {name:32s} {reads:>10d} {gates:>6d} {str(on):>18s}  {verdict}")
    print()
    for v in ("RETIRE", "SCHEDULE", "RETAIN"):
        n = sum(1 for r in rows if r[4].startswith(v))
        print(f"  {v:9s}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
