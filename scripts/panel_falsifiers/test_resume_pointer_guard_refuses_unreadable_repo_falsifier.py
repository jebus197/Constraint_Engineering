#!/usr/bin/env python3
"""FALSIFIER: scripts/resume_pointer_truth_2026-09-21.py judges git claims
FALSE against a repository git cannot read at all.

The guard's own docstring for git_rc records the class: collapsing "error"
into "no" produces "a confident false statement about a repository git had
simply failed to read". That was fixed for merge-base --is-ancestor and left
live 3 lines above it: `git rev-parse --verify` returning EMPTY (not a repo,
git absent, corrupt object store) is read as "names HEAD X, which is not a
commit in this repository" -- verdict FALSE, exit 1. `head_now` empty is
never checked, and `ahead_now = int(... or 0)` turns git failure into
"0 ahead", indicting a truthful NOT-PUSHED pointer.

Imports the REAL script. Case A: a directory that is NOT a git repository,
holding a tracker with a live pointer -> the guard must REFUSE to measure
(exit 2), not convict (exit 1). Case B: a real git repo whose pointer names
its own HEAD truthfully -> must still exit 0 (the fix must not lock both
ways). Fails iff case A convicts or case B breaks.
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "resume_pointer_truth_2026-09-21.py"

sys.path.insert(0, str(REPO / "scripts"))

# WIRED 2026-09-22 (CC1). This falsifier does its work at MODULE level -- that is
# deliberate, it is what makes it fire at import while the defect is live -- so
# there is no main() for a help flag to intercept and `--help` ran the whole
# thing, including its subprocess calls and temporary trees. A help flag must
# ANSWER, never ACT. Answered here, before any work begins.
from _cli_help import answer_help  # noqa: E402

spec = importlib.util.spec_from_file_location("rpt", SCRIPT)
rpt = importlib.util.module_from_spec(spec)
sys.modules["rpt"] = rpt
spec.loader.exec_module(rpt)

TRACKER = "experimental_notes/CDSFL_Agent_Operational_Plan.md"
POINTER = ("# tracker\n\n## Session state\n"
           "HEAD `3381910`, main, working tree CLEAN, "
           "11 ahead of `origin/main` -- NOT PUSHED\n")

def run_in(root: Path) -> int:
    rpt.REPO = root
    try:
        return rpt.main()
    except SystemExit as e:
        return int(e.code or 0)

def main() -> None:
    # RESTRUCTURED 2026-09-22 (CC1). This work ran at MODULE level, so
    # merely importing the file spawned subprocesses and built trees.
    # It still fires when RUN, which is how a diagnostic falsifier is
    # used; it no longer fires when something merely inspects it.
    fails = []

    with tempfile.TemporaryDirectory() as td:
        nonrepo = Path(td) / "sev"
        (nonrepo / "experimental_notes").mkdir(parents=True)
        (nonrepo / TRACKER).write_text(POINTER)
        rc = run_in(nonrepo)
        if rc != 2:
            fails.append(
                f"non-repo: guard returned {rc}; it judged git claims in a tree "
                "git cannot read (want 2 = refuse to measure)")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "ok"
        (repo / "experimental_notes").mkdir(parents=True)
        for cmd in (["git", "init", "-q", "-b", "main"],
                    ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                     "commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(cmd, cwd=repo, check=True)
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo,
                              capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
                       cwd=repo, check=True)
        (repo / TRACKER).write_text(
            f"# tracker\n\n## Session state\nHEAD `{head}`, main, working tree CLEAN\n")
        rc = run_in(repo)
        if rc != 0:
            fails.append(f"healthy repo with truthful pointer: guard returned {rc}, want 0")

    if fails:
        print("FALSIFIED")
        for f in fails:
            print("  " + f)
        raise AssertionError("; ".join(fails))
    print("clean: refuses an unreadable repo (2), passes a truthful pointer (0)")


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    main()
