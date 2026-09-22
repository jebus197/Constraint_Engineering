#!/usr/bin/env python3
"""FALSIFIER: the sandbox-fallback gate verifies path IDENTITY but not the
sandbox's defining property (severed git history), so in a LIVE repository
with CDSFL_SANDBOX_ROOT exported the gate is satisfied and only git's own
success stands between a git hiccup (index.lock, stale worktree, disk) and
the escape hatch opening where the variable "is unset" was claimed.

Executes the REAL gate expression, lifted verbatim from
bench/tools/run_simulated_experiment.py at run time (not retyped), against:
  (a) a root that still has .git  -> a live checkout: gate must be False
      even when the marker names it;
  (b) a root with no .git         -> a severed sandbox: gate must be True.

Fails (FALSIFIED/AssertionError) iff case (a) unlocks.
"""
import os
import pathlib
import re
import sys
import tempfile

# `scripts/` is not on the path for a file one level down, so put it there
# before importing the shared help helper.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text()

m = re.search(
    r"_declared = os\.environ\.get\(\"CDSFL_SANDBOX_ROOT\", \"\"\)\n"
    r"(?:\s*#[^\n]*\n)*"
    r"\s*_in_sandbox = (.+?)\n\s*if not _in_sandbox", SRC, re.DOTALL)
assert m, "gate expression not found in runner source"
gate_expr = m.group(1)

def gate(root: pathlib.Path, declared: str) -> bool:
    ns = {"os": os, "pathlib": pathlib, "REPO": root,
          "_declared": declared}
    return bool(eval(compile(gate_expr, "<runner-gate>", "eval"), ns))

def main() -> None:
    # RESTRUCTURED 2026-09-22 (CC1). This work ran at MODULE level, so
    # merely importing the file spawned subprocesses and built trees.
    # It still fires when RUN, which is how a diagnostic falsifier is
    # used; it no longer fires when something merely inspects it.
    with tempfile.TemporaryDirectory() as td:
        live = pathlib.Path(td) / "live"; (live / ".git").mkdir(parents=True)
        sand = pathlib.Path(td) / "sand"; sand.mkdir()

        unlocked_in_live = gate(live, str(live))
        unlocked_in_sandbox = gate(sand, str(sand))

        assert unlocked_in_sandbox, \
            "gate must still unlock inside a genuine severed-history sandbox"
        if unlocked_in_live:
            print("FALSIFIED")
            raise AssertionError(
                "the fallback gate unlocks in a LIVE checkout (.git present) when "
                "CDSFL_SANDBOX_ROOT names it; the refusal then rests solely on "
                "git succeeding")
    print("clean: gate refuses a root that still has .git, unlocks a severed one")


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    main()
