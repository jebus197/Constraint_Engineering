#!/usr/bin/env python3
"""FALSIFIER: the sandbox-fallback gate verifies a declaration, not the severance.

THE CLAIM UNDER TEST. The morning report (SS5) says the runner "resolves and
compares [CDSFL_SANDBOX_ROOT] against its own root rather than trusting it, so
a stale or hostile value naming another directory unlocks nothing". True for a
value naming ANOTHER directory -- but a value naming THIS root unlocks the
fallback even when the tree is a REAL git checkout, i.e. exactly when the
fallback's own justification ("history already severed, protection already in
force") is false. The refusal-to-copy downgrade can then be triggered in a
live checkout by exporting one variable, whenever `git worktree` fails for an
unrelated reason (corrupt .git, worktree limit, git missing from PATH).

WHAT THIS SCRIPT DOES. It extracts the `_in_sandbox` predicate TEXT from the
real `bench/tools/run_simulated_experiment.py` (not a retyped copy), and
evaluates it in a controlled namespace against a temp directory that HAS a
`.git` directory, with CDSFL_SANDBOX_ROOT naming that same directory.

  - Defect present : predicate returns True  -> AssertionError (exit 1)
  - Defect repaired: predicate returns False -> and the positive control
    (same setup WITHOUT `.git`) must still return True, else exit 1.

Run:  python3 scripts/sandbox_gate_predicate_falsifier_2026-09-22.py
"""

from __future__ import annotations

import os
import pathlib
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def extract_predicate() -> str:
    """The `_declared`/`_in_sandbox` assignments, byte-for-byte from the shipped file."""
    text = RUNNER.read_text()
    m = re.search(r"^([ \t]*)_declared = os\.environ\.get\(\"CDSFL_SANDBOX_ROOT\", \"\"\)"
                  r"(.*?)(?=\n[ \t]*if not _in_sandbox)", text, re.S | re.M)
    if not m:
        raise SystemExit("could not locate the _in_sandbox assignment")
    indent = m.group(1)
    block = m.group(0)
    return "\n".join(ln[len(indent):] if ln.startswith(indent) else ln
                     for ln in block.splitlines())


def evaluate(tmp: Path, declared: str) -> bool:
    ns = {"os": os, "pathlib": pathlib, "REPO": tmp}
    env_backup = os.environ.get("CDSFL_SANDBOX_ROOT")
    try:
        os.environ["CDSFL_SANDBOX_ROOT"] = declared
        exec(extract_predicate(), ns)
    finally:
        if env_backup is None:
            os.environ.pop("CDSFL_SANDBOX_ROOT", None)
        else:
            os.environ["CDSFL_SANDBOX_ROOT"] = env_backup
    return bool(ns["_in_sandbox"])


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td).resolve()
        # Case 1: a REAL checkout (.git present), variable naming this root.
        (tmp / ".git").mkdir()
        unlocked = evaluate(tmp, str(tmp))
        print(f"checkout with .git + declared root -> _in_sandbox={unlocked}")
        assert not unlocked, (
            "FALSIFIED: the fallback unlocks inside a real git checkout when "
            "CDSFL_SANDBOX_ROOT names the root -- the predicate verifies the "
            "declaration, not the severed history its justification rests on")
        # Positive control: genuine sandbox (no .git) must still unlock.
        (tmp / ".git").rmdir()
        ok = evaluate(tmp, str(tmp))
        print(f"severed tree (no .git) + declared root -> _in_sandbox={ok}")
        assert ok, "REGRESSION: the genuine sandbox no longer unlocks the fallback"
    print("clean exit: gate requires BOTH the declaration and the severed history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
