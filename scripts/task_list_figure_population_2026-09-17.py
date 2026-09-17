#!/usr/bin/env python3
"""V4's figure sweep over HEADING LINES versus entry BLOCKS, at any revision.

PANEL ROUND 16, 2026-09-17. Task V4's guard,
`bench/tests/test_task_list_figures_have_producers_2026-09-10.py`, applied its
FIGURE and SCRIPT expressions to `Entry.text`, which `parse_entries` sets to the
heading line only. So "18 entries carrying a percentage or p-value" was 18
heading lines, and a figure in an entry's body was invisible to it.

This module is now the ONE definition of that sweep. The guard imports `sweep`
and runs it on the working tree; `main()` runs the same function on the task list
at any revision and prints 3 populations:

  heading lines           the population the guard read until 2026-09-17
  entry blocks            heading to the next heading, marker line included
  blocks without markers  the same, with every `<!-- task: ... -->` line removed

WHAT IT TESTS IS CO-OCCURRENCE, NOT PRODUCTION. An entry passes when any path
under scripts/ or bench/tests/ that exists appears in the same text as the figure.
It does not check that the script prints the figure. With the marker line
included, a marker's `evidence:` field satisfies it for every entry that has one,
which is why the 3rd population exists.

Read-only: at a revision the list is read with `git show <rev>:<path>` and script
existence with `git cat-file -e <rev>:<path>`, so no checkout is touched. Block
boundaries come from the CURRENT `task_list_markers.end_of_entries`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
LIST_REL = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"
FIGURE = re.compile(r"\b\d{1,3}\.\d+\s*%|\bp\s*=\s*[\d.]+e?-?\d*")
SCRIPT = re.compile(r"(scripts/[\w./-]+\.py|bench/tests/[\w./-]+\.py)")
UNITS = ("heading lines", "entry blocks", "blocks without markers")


def _tlm():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers
    return task_list_markers


def sweep(list_text: str, exists: Callable[[str], bool],
          unit: str) -> tuple[list[str], list[str]]:
    """Return (identifiers carrying a figure, those naming no existing script)."""
    if unit not in UNITS:
        raise ValueError(f"unit must be one of {UNITS}, not {unit!r}")
    tlm = _tlm()
    with tempfile.TemporaryDirectory() as d:
        lst = Path(d) / "list.md"
        lst.write_text(list_text, encoding="utf-8")
        entries = sorted(tlm.parse_entries(lst), key=lambda e: e.line_no)
    lines = list_text.splitlines()
    end = tlm.end_of_entries(lines)
    carrying: list[str] = []
    orphans: list[str] = []
    for k, e in enumerate(entries):
        stop = entries[k + 1].line_no - 1 if k + 1 < len(entries) else end
        block = lines[e.line_no - 1:stop]
        if unit == "heading lines":
            text = e.text
        elif unit == "entry blocks":
            text = "\n".join(block)
        else:
            text = "\n".join(ln for ln in block if not tlm.MARKER.match(ln))
        if not FIGURE.findall(text):
            continue
        carrying.append(e.ident)
        if not any(exists(s) for s in SCRIPT.findall(text)):
            orphans.append(e.ident)
    return carrying, orphans


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rev", default="HEAD",
                    help="revision whose task list and scripts are read (default HEAD)")
    a = ap.parse_args()
    r = _git("show", f"{a.rev}:{LIST_REL}")
    if r.returncode != 0:
        print(f"REFUSING: git cannot read {LIST_REL} at {a.rev}: {r.stderr.strip()}",
              file=sys.stderr)
        return 2
    cache: dict[str, bool] = {}

    def exists(p: str) -> bool:
        if p not in cache:
            cache[p] = _git("cat-file", "-e", f"{a.rev}:{p}").returncode == 0
        return cache[p]

    from statsmodels.stats.proportion import proportion_confint
    print(f"revision {a.rev}")
    for unit in UNITS:
        carrying, orphans = sweep(r.stdout, exists, unit)
        n, k = len(carrying), len(orphans)
        lo, hi = proportion_confint(k, n, method="wilson") if n else (0.0, 0.0)
        print(f"  {unit:22s}: {n} carry a figure, {k} name no existing script "
              f"{orphans} = {k / n if n else 0:.4%}, Wilson [{lo:.4%}, {hi:.4%}]")
    print("  A script path anywhere in the text satisfies the sweep: it tests "
          "co-occurrence, not production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
