#!/usr/bin/env python3
"""Which runners delete a directory a model wrote in, and do they save it first?

FOUNDER RULING (j), 2026-09-17: *"make sure this is how all future panel reviews
and experiments (both paid and simulated) work in the future too. Take care when
a panel review or an experiment completes however that the sandbox does not
simply get automatically deleted and that the results do not end up simply being
discarded, as has happened in the recent past."*

The panel dispatcher was the site of the measured loss and is fixed. This asks
the wider question the ruling asks, and answers it with a count rather than an
impression: across `bench/`, every call that removes a directory tree is found by
parsing the source (`ast`, never a regular expression over text), and each is
classified by WHAT it removes:

  SEAT_TREE     -- a `panel_sandbox.build()` copy, or a directory the code hands
                   to a model as its working directory. Deleting 1 of these can
                   discard results, which is the ruling's subject.
  SCRATCH       -- a temporary directory the runner itself created and used for
                   its own bookkeeping (an overlay, a staging area, a git
                   worktree it made and populated). Nothing a model wrote.
  UNKNOWN       -- the target could not be resolved from the source alone.

A SEAT_TREE site is then checked for a harvest -- a `release(`, `harvest(`,
`changes(` or an explicit copy-out -- in the same function.

Read-only. Prints a table and a JSON summary; writes nothing unless --json.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BENCH = REPO / "bench"

REMOVERS = {"rmtree", "teardown"}
HARVEST_MARKERS = ("release", "harvest", "changes", "copytree", "copy2", "extract")
#: Names that say the thing being removed is a model's working copy.
SEAT_WORDS = ("sandbox", "seat", "panel_cwd", "worktree_for", "agent_dir")
#: The function gives the directory to a model to work in, so what is inside it
#: when it is removed is a model's output, not the runner's bookkeeping.
HANDS_TO_A_MODEL = ("panel_cwd", "set_panel_cwd", "seat_environment", "confine_this_thread")
SCRATCH_WORDS = ("tmpdir", "tmp_dir", "overlay", "staging", "scratch", "td", "wt",
                 "workdir", "tmp_cwd", "obs_dir", "holder")


def _name(node: ast.AST) -> str:
    """A readable name for whatever expression is being removed."""
    try:
        return ast.unparse(node)
    except Exception:                                   # noqa: BLE001
        return "<unparsable>"


def sites(root: pathlib.Path = BENCH) -> list[dict]:
    found = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(REPO)
        if "tests/" in str(rel) or str(rel).startswith("bench/logs"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        funcs = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                body = ast.unparse(node) if not isinstance(node, ast.Module) else ""
                for child in ast.walk(node):
                    funcs[id(child)] = (getattr(node, "name", "<module>"), body)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            label = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if label not in REMOVERS or not node.args:
                continue
            target = _name(node.args[0])
            low = target.lower()
            func_name, func_src = funcs.get(id(node), ("<module>", ""))
            # WHAT THE FUNCTION DOES WITH THE PATH BEATS WHAT THE VARIABLE IS
            # CALLED. The first version of this script classified by name alone
            # and MISSED the real site: `run_simulated_experiment` builds a git
            # worktree, assigns it to `cfg.panel_cwd` -- so the seats work in it
            # -- and removes it in a `finally`, but the variable is `_wt_parent`,
            # which reads as scratch. A function that hands a model a working
            # directory is handling a seat tree whatever it names the variable.
            hands_it_to_a_model = any(w in func_src for w in HANDS_TO_A_MODEL)
            if any(w in low for w in SEAT_WORDS) or hands_it_to_a_model:
                kind = "SEAT_TREE"
            elif any(w in low for w in SCRATCH_WORDS):
                kind = "SCRATCH"
            else:
                kind = "UNKNOWN"
            found.append({
                "file": str(rel), "line": node.lineno, "call": f"{label}({target})",
                "kind": kind, "function": func_name,
                "harvest_in_the_same_function": any(m + "(" in func_src
                                                    for m in HARVEST_MARKERS),
            })
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=pathlib.Path)
    ap.add_argument("--kind", choices=("SEAT_TREE", "SCRATCH", "UNKNOWN"))
    a = ap.parse_args(argv)

    rows = sites()
    shown = [r for r in rows if not a.kind or r["kind"] == a.kind]
    width = max((len(r["file"]) for r in shown), default=10)
    for r in shown:
        flag = "" if r["kind"] != "SEAT_TREE" or r["harvest_in_the_same_function"] else "  <-- NO HARVEST"
        print(f"{r['file']:<{width}} :{r['line']:<5} {r['kind']:<9} {r['call'][:60]}{flag}")
    counts = {k: sum(1 for r in rows if r["kind"] == k)
              for k in ("SEAT_TREE", "SCRATCH", "UNKNOWN")}
    unharvested = [r for r in rows if r["kind"] == "SEAT_TREE"
                   and not r["harvest_in_the_same_function"]]
    summary = {"total_removal_calls": len(rows), "by_kind": counts,
               "seat_trees_deleted_without_a_harvest": len(unharvested),
               "the_sites_that_need_the_ruling_applied": unharvested}
    print("\n" + json.dumps(summary, indent=2))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"summary": summary, "sites": rows}, indent=2) + "\n",
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
