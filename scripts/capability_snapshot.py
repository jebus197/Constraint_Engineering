#!/usr/bin/env python3
"""Derive the project's named capability set. Never typed — always derived.

The additive standard's removal half needs something to compare against, and a
hand-maintained list is the failure this project has already recorded 10 times in
the memory ledger: a number a person types that code already knows. So the set is
computed from the source on every run, and the SNAPSHOT is the only stored part.

Capabilities counted, because each is a thing a user or a config can ask for:
  * RunnerConfig fields          — every switch a run can be given
  * MC commands                  — every instruction the founder can type
  * vault_keys.sh subcommands    — every key operation available
  * runner public entry points   — module-level defs not prefixed with underscore

Usage:
  python3 scripts/capability_snapshot.py            # print the set
  python3 scripts/capability_snapshot.py --write    # refresh the stored snapshot
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "bench" / "tests" / "data" / "capability_snapshot.json"


def capabilities() -> dict:
    out: dict[str, list[str]] = {}
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(runner)

    fields = []
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n.name == "RunnerConfig":
            for st in n.body:
                if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    fields.append(st.target.id)
    out["runner_config_fields"] = sorted(fields)

    out["runner_public_entry_points"] = sorted(
        n.name for n in tree.body
        if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
    )

    hook = (REPO / "hooks" / "mc_commands.py").read_text()
    known = re.search(r"_KNOWN = \{(.*?)\}", hook, re.S)
    out["mc_commands"] = sorted(set(re.findall(r'"([a-z0-9]{1,4})"', known.group(1))))

    vault = (REPO / "bench" / "vault_keys.sh").read_text()
    case = vault[vault.index('case "${1:-status}" in'):]
    out["vault_subcommands"] = sorted(set(
        re.findall(r"^\s{2}([a-z-]+)\)", case[:case.index("esac")], re.M)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    caps = capabilities()
    if args.write:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(caps, indent=2, sort_keys=True) + "\n")
        print(f"wrote {SNAPSHOT}")
    total = sum(len(v) for v in caps.values())
    for k, v in sorted(caps.items()):
        print(f"  {k:28s} {len(v)}")
    print(f"  {'TOTAL':28s} {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
