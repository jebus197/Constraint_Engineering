#!/usr/bin/env python3
"""Who calls the steering surface, counted by AST and with name collisions named.

B161 records 2 of its 3 pieces as BUILT AND TESTED and the 3rd as a design
decision. That framing hides the thing that actually matters: the surface has no
production caller at all, so the 2 built pieces are additions nothing reaches and
a 3rd piece would be the same. `additive-standard`'s symmetric form is explicit
-- every new entry point must be wired to a caller and executed by a test -- and
this project has 11 confirmed defects of exactly that shape.

WHY AST AND NOT grep, AND WHY THE COLLISIONS ARE REPORTED. A textual search for
`accept(` finds any function of that name in any module. Driven over this tree it
reports a production caller in `bench/experiment_11_orchestrator.py`, which
defines its own `accept_reply_or_work` and a nested `_accept` for command-line
replies and has nothing to do with a researcher profile. `propose` collides
harder still: `bench/ticket_store.py` has a `propose` of its own, which is how a
count of 12 production callers appears for a function with none. So this script
resolves callers by MODULE as well as by name: a call counts only where the file
also imports the steering module, by `import`, by `from`, or by an importlib path
string. Both figures are printed so the collision stays visible.

WHAT IT DOES NOT ESTABLISH. It counts callers in this repository only. A surface
invoked from outside the tree -- a notebook, a shell wrapper, a future UX -- would
read as unreached here. That is stated rather than hedged over, because the claim
being made is about this tree.
"""
from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).resolve()
MODULE = "domain_proposer"
FUNCS = ("repair_turn", "explainer", "profile_mismatch", "accept", "propose")
ROOTS = ("bench", "scripts")


def _cli(doc: str) -> None:
    """Answer --help WITHOUT walking the tree."""
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the census.",
    ).parse_args()


def _is_test(p: pathlib.Path) -> bool:
    return p.name.startswith("test_") or "tests" in p.parts


def _sources() -> list[pathlib.Path]:
    out = []
    for r in ROOTS:
        for p in (REPO / r).rglob("*.py"):
            if "logs" in p.parts or "__pycache__" in p.parts:
                continue
            out.append(p)
    return sorted(out)


def imports_module(tree: ast.AST) -> bool:
    """Does this file reach the steering module at all?

    ★ 2 DEFECTS OF MINE ARE FIXED HERE AND NAMED, because the first version
    reported the surface as REACHED when it is not.
    (1) `from bench.cdsfl_registry import domain_proposer as dp` is an
        ImportFrom whose module is `bench.cdsfl_registry` and whose NAME is
        `domain_proposer`. The first version checked only `n.module`, so it
        missed the most natural import form -- and that is precisely how the
        real test file imports it, giving 7 calls by name and 0 resolved.
    (2) It matched itself, because this file spells `domain_proposer` in order
        to look for it. A detector that spells out its own pattern reads its
        own scar as a wound, which this project has recorded before, so the
        census now excludes its own path explicitly.
    """
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if n.module and MODULE in n.module:
                return True
            if any(MODULE in a.name for a in n.names):
                return True
        if isinstance(n, ast.Import) and any(MODULE in a.name for a in n.names):
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and MODULE in n.value:
            return True
    return False


def call_names(tree: ast.AST) -> list[str]:
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else f.id if isinstance(f, ast.Name) else None)
            if name in FUNCS:
                out.append(name)
    return out


def census() -> dict:
    by_name = {f: {"prod": 0, "test": 0} for f in FUNCS}
    resolved = {f: {"prod": 0, "test": 0} for f in FUNCS}
    importers = {"prod": [], "test": []}
    for p in _sources():
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        reaches = imports_module(tree)
        kind = "test" if _is_test(p) else "prod"
        #: the module itself, and THIS census, are not callers of it.
        if reaches and p.name != f"{MODULE}.py" and p.resolve() != SELF:
            importers[kind].append(p.relative_to(REPO).as_posix())
        for name in call_names(tree):
            by_name[name][kind] += 1
            if reaches:
                resolved[name][kind] += 1
    return {"by_name": by_name, "resolved": resolved, "importers": importers}


def main(argv: list[str] | None = None) -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()
    c = census()

    print(f"== callers of {MODULE}, by NAME alone (collisions included) ==")
    for f in FUNCS:
        b = c["by_name"][f]
        print(f"   {f:18s} production {b['prod']:3d}   tests {b['test']:3d}")
    print("   -> a name-only count is not a caller count: ticket_store defines its")
    print("      own `propose`, and experiment_11_orchestrator its own `accept`.")
    print()

    print(f"== callers RESOLVED to files that import {MODULE} ==")
    for f in FUNCS:
        r = c["resolved"][f]
        print(f"   {f:18s} production {r['prod']:3d}   tests {r['test']:3d}")
    print()

    print(f"== files that reach {MODULE} at all ==")
    for kind in ("prod", "test"):
        names = c["importers"][kind]
        print(f"   {kind:4s} {len(names)}: {names}")
    print()

    prod_total = sum(c["resolved"][f]["prod"] for f in FUNCS)
    test_total = sum(c["resolved"][f]["test"] for f in FUNCS)
    # a mutation harness is not a production caller: it exists to test the thing
    harnesses = [n for n in c["importers"]["prod"] if "mutation" in n]
    real_prod = [n for n in c["importers"]["prod"] if "mutation" not in n]
    print("== VERDICT ==")
    print(f"   resolved production call sites : {prod_total}")
    print(f"   resolved test call sites       : {test_total}")
    print(f"   non-test importers             : {c['importers']['prod']}")
    print(f"   of those, mutation harnesses   : {harnesses}")
    print(f"   genuine production importers   : {real_prod}")
    unreached = not real_prod
    print(f"   the steering surface is UNREACHED in this tree: {unreached}")
    if unreached:
        print("   -> so persisting its selection would be a 3rd addition nothing")
        print("      reaches, and the missing piece is a CALLER, not a store.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
