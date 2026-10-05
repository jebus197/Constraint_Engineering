#!/usr/bin/env python3
"""Which of the closing sweep's disposition channels can reach the convergence gate?

THE QUESTION. `_post_convergence_sweep` disposes of residual findings through
several channels: it re-attaches runnable falsifiers and re-runs them, it accepts
corrected copies, it accepts reasoned withdrawals, and it records computed evidence
for criticals a falsifier refuted. On the last simulated run it cleared 16 findings
and withdrew 4. Every one of those dispositions happened AFTER `converged` was
assigned, so none of them could move the gate.

The founder's position, 2026-10-04: *"The closing sweep is part of the convergence
mechanics of the schema ... It is not just an 'afterthought'"*, and doing it the other
way *"just makes the closing sweep an unfalsifiable loose cannon"*.

WHAT THIS SCRIPT ESTABLISHES, by AST attribution rather than by reading: for each
channel, (1) how many live call sites it has, (2) which function encloses each, and
(3) whether that function is reachable from the round loop or only after the verdict.
A channel reachable ONLY post-verdict is work the gate can never see.

The before/after boundary is taken from the source itself: the line at which the
`converged` name is bound in the orchestrator, and the line at which
`_post_convergence_sweep` is called.

Run:  python3 scripts/sweep_channels_are_post_verdict_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"

#: The sweep's disposition channels, by the token that identifies each in source.
#: Each is a way a finding's fate can change.
CHANNELS = {
    "falsifier re-run (executes code)": "reverify_falsifier",
    "corrected-copy ingest": "_extract_corrected_copies",
    "reasoned withdrawal (prose)": "_WITHDRAW_RE_OR_LITERAL",
    "computed-evidence record": "_record_computed_evidence",
    "status resolution": "registry.resolve",
}

#: The labelled form the sweep parses for re-attachment. A finding can only gain a
#: falsifier from a model reply through a site that parses this.
REATTACH_PATTERN = r"FALSIFIER:\s*(C\d{4})"


def _parse_args(argv=None) -> int:
    """A --help must never cost money and must never run the measurement."""
    p = argparse.ArgumentParser(
        prog="sweep_channels_are_post_verdict_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--runner", default=str(RUNNER),
                   help="runner to analyse (default: bench/reference_runner_v3.py)")
    args = p.parse_args(argv)
    return args


def _enclosing(tree: ast.AST, lineno: int) -> str:
    """The innermost function or class enclosing `lineno`, or '<module>'."""
    best, best_span = "<module>", None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
            continue
        end = getattr(node, "end_lineno", None)
        if end is None or not (node.lineno <= lineno <= end):
            continue
        span = end - node.lineno
        if best_span is None or span < best_span:
            best, best_span = node.name, span
    return best


def main(argv=None) -> int:
    args = _parse_args(argv)
    path = pathlib.Path(args.runner)
    src = path.read_text(encoding="utf-8")
    lines = src.split("\n")
    tree = ast.parse(src)

    # --- the before/after boundary, read from source, not assumed -------------
    sweep_call = [i + 1 for i, ln in enumerate(lines)
                  if "_post_convergence_sweep(" in ln and "def " not in ln]
    sweep_def = [n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef)
                 and n.name == "_post_convergence_sweep"]
    if not sweep_def:
        print("FAIL: no _post_convergence_sweep in this runner")
        return 1
    sd = sweep_def[0]
    sweep_span = (sd.lineno, sd.end_lineno)

    print("=" * 78)
    print("THE CLOSING SWEEP'S CHANNELS, AND WHICH SIDE OF THE VERDICT THEY SIT ON")
    print("=" * 78)
    print(f"runner            : {path.relative_to(REPO)}")
    print(f"sweep defined at  : lines {sweep_span[0]}-{sweep_span[1]}")
    print(f"sweep CALLED at   : {sweep_call if sweep_call else 'NOWHERE'}")
    print()

    def _in_sweep(lineno: int) -> bool:
        return sweep_span[0] <= lineno <= sweep_span[1]

    # --- channel attribution --------------------------------------------------
    print("-" * 78)
    print("CHANNEL CALL SITES, attributed to the enclosing function by AST")
    print("-" * 78)
    rows = []
    for name, token in CHANNELS.items():
        if token == "_WITHDRAW_RE_OR_LITERAL":
            hits = [i + 1 for i, ln in enumerate(lines)
                    if "WITHDRAW" in ln and "\\s+(C" in ln]
        else:
            hits = [i + 1 for i, ln in enumerate(lines)
                    if token in ln and not ln.lstrip().startswith("#")
                    and "def " not in ln and "import " not in ln]
        inside = [h for h in hits if _in_sweep(h)]
        outside = [h for h in hits if not _in_sweep(h)]
        fns = sorted({_enclosing(tree, h) for h in outside})
        rows.append((name, len(hits), len(inside), len(outside), fns))
        print(f"\n{name}")
        print(f"  total live sites      : {len(hits)}")
        print(f"  inside the sweep      : {len(inside)}  {inside}")
        print(f"  elsewhere             : {len(outside)}")
        if fns:
            for fn in fns:
                where = [h for h in outside if _enclosing(tree, h) == fn]
                print(f"      {fn}  at {where}")
        else:
            print("      *** NOWHERE ELSE — this channel exists ONLY in the sweep ***")

    # --- the re-attachment parse, the narrowest channel -----------------------
    print()
    print("-" * 78)
    print("THE RE-ATTACHMENT PARSE — how a finding can GAIN a falsifier from a reply")
    print("-" * 78)
    reattach = [i + 1 for i, ln in enumerate(lines) if REATTACH_PATTERN in ln]
    print(f"sites parsing {REATTACH_PATTERN!r}: {len(reattach)}  {reattach}")
    for h in reattach:
        print(f"    line {h}: enclosed by {_enclosing(tree, h)}  "
              f"(in sweep: {_in_sweep(h)})")
    if len(reattach) == 1 and _in_sweep(reattach[0]):
        print()
        print("  VERDICT: the ONLY site that can attach a falsifier from a model")
        print("  reply is inside the post-verdict sweep. A finding that would be")
        print("  cleared by a re-attached falsifier CANNOT be cleared in-round,")
        print("  so it sits in the A4 blocker count for every round of the run")
        print("  and is only resolved once the gate has already decided.")

    # --- summary --------------------------------------------------------------
    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    only_sweep = [r[0] for r in rows if r[3] == 0]
    shared = [r[0] for r in rows if r[3] > 0]
    print(f"channels that exist ONLY post-verdict : {len(only_sweep)} of {len(rows)}")
    for n in only_sweep:
        print(f"    - {n}")
    print(f"channels also reachable in-round      : {len(shared)} of {len(rows)}")
    for n in shared:
        print(f"    - {n}")
    print()
    print("A channel in the first list is falsification work the convergence gate")
    print("is structurally unable to see. That is the defect to close.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
