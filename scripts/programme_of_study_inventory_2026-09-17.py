#!/usr/bin/env python3
"""The fix inventory behind the programme of study, derived at a named commit. Read-only.

Committed 2026-09-17 with the programme addendum that quotes it.

WHY. The programme of 2026-09-17 quotes 323 commits, 84 DONE entries, 151 new
test files and 6 group counts. None has a committed producer, the 3 counts
reproduce only at different commits, and the group counts reproduce from
nothing: they came from a command whose code was never saved. The founder asked
for the programme to be built "reliably", and a count that cannot be re-derived
is not reliable.

WHAT IT DERIVES, every value AT `--at`, never at whatever HEAD happens to be:
  * commits since `--since` (`git rev-list --count --since`);
  * DONE entries, parsed by scripts/task_list_markers.py from the task list AS
    COMMITTED at `--at`, each with its evidence files;
  * test files ADDED since `--since` (`git log --diff-filter=A`, path rule
    `bench/tests/test_*.py`, stated here so it cannot drift);
  * DONE entries grouped by their SECTION PREFIX (P, L, M, R, 0 to 10, A, V, W),
    which is structure the list already carries, not a keyword classifier.

It writes nothing unless `--json PATH` is given.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REPO = Path(__file__).resolve().parents[1]
LIST = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"
TEST_RULE = re.compile(r"^bench/tests/test_[^/]*\.py$")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


def section(ident: str) -> str:
    m = re.match(r"^([A-Z]{1,2})", ident)
    return m.group(1) if m else ident.split(".")[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    ap.add_argument("--at", default="HEAD", help="commit the inventory is taken at")
    ap.add_argument("--since", default="2026-09-03")
    ap.add_argument("--json", type=Path, help="also write the inventory here")
    a = ap.parse_args()
    repo = a.repo.resolve()
    sha = git(repo, "rev-parse", "--short", a.at).strip()

    commits = int(git(repo, "rev-list", "--count", f"--since={a.since}", a.at))
    added = sorted({p for p in git(repo, "log", f"--since={a.since}", "--diff-filter=A",
                                   "--name-only", "--format=", a.at).split()
                    if TEST_RULE.match(p)})

    sys.path.insert(0, str(repo / "scripts"))
    import task_list_markers as tlm
    with tempfile.TemporaryDirectory() as td:
        snap = Path(td) / "list.md"
        snap.write_text(git(repo, "show", f"{a.at}:{LIST}"), encoding="utf-8")
        entries = tlm.parse_entries(snap)
    done = [e for e in entries if e.state == "DONE"]
    groups = collections.Counter(section(e.ident) for e in done)

    print(f"inventory at {sha}, window since {a.since}")
    print(f"  commits                 : {commits}")
    print(f"  DONE entries            : {len(done)} of {len(entries)}")
    print(f"  test files added        : {len(added)}  (rule {TEST_RULE.pattern})")
    print("  DONE entries by section : " + ", ".join(
        f"{k} {v}" for k, v in sorted(groups.items())))
    if a.json:
        a.json.write_text(json.dumps({
            "at": sha, "since": a.since, "commits": commits,
            "done": [{"id": e.ident, "status": e.status, "evidence": list(e.evidence)}
                     for e in done],
            "tests_added": added, "done_by_section": dict(groups),
        }, indent=2) + "\n", encoding="utf-8")
        print(f"  written: {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
