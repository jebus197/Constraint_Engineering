#!/usr/bin/env python3
"""Does the founder's prose-era hypothesis explain the untracked cited logs?

FOUNDER, 2026-09-16, on task A8: *"There may be a reason why the experimental
log directory cannot be tracked directly back to the experiments that generated
them, which could be that for a large initial part of the project, the project
itself existed as purely prose ... But for now, that is only a hypothesis. You
should look and see if it holds any water or not."*

THE TEST. If the hypothesis holds, the untracked cited paths should be OLD --
concentrated before the machinery existed. If they are spread evenly, or are
mostly RECENT, the hypothesis fails and the cause is something else.

Dates come from the path itself, which is how these directories are named:
`exp55_v3_control_20260823T153955Z`, `panel_round15_2026-09-11`, and so on.

Read-only: it runs `git grep` and `git ls-files` and writes nothing.
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CITE = re.compile(r"bench/logs/[A-Za-z0-9_][A-Za-z0-9_./-]*")
#: `20260823T153955Z` or `2026-08-23`, whichever the directory name carries.
DATE = re.compile(r"(20\d{2})-?(\d{2})-?(\d{2})")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True).stdout


def cited_paths() -> dict[str, set[str]]:
    """Every bench/logs path named by a tracked file, and who names it."""
    out: dict[str, set[str]] = collections.defaultdict(set)
    # THE SOURCES MUST EXCLUDE bench/logs ITSELF. 6,462 files under bench/logs
    # are tracked despite `.gitignore:41`, and a log file naming its own sibling
    # paths is not a CITATION -- one archived transcript alone contains 1,047
    # such strings. Sweeping them in measures the extractor, not the corpus,
    # which is the defect task A8's own entry records ("206 of 290 -- a figure
    # about the extractor"). Committed 2026-09-17 after making it a second time.
    raw = _git("grep", "-I", "-o", "-E", CITE.pattern, "--",
               ":(exclude)bench/logs", ".")
    for line in raw.splitlines():
        if ":" not in line:
            continue
        where, path = line.split(":", 1)
        path = path.strip().rstrip(".,);`'\"")
        if where.startswith("experimental_notes/"):
            kind = "NOTE"
        elif where.startswith("bench/tests/"):
            kind = "TEST"
        else:
            kind = "CODE"
        out[path].add(kind)
    return out


def tracked() -> set[str]:
    return set(_git("ls-files").splitlines())


def era(path: str) -> str | None:
    m = DATE.search(path)
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--manifest", metavar="PATH",
                    help="write the disposition of every cited path as JSON: "
                         "tracked, local_only, or missing. This is the LABEL "
                         "half of the founder's accept-and-label ruling.")
    args = ap.parse_args()

    import numpy as np
    import scipy.stats as st
    from statsmodels.stats.proportion import proportion_confint

    def wilson(k: int, n: int) -> str:
        if n == 0:
            return "n = 0"
        lo, hi = proportion_confint(k, n, method="wilson")
        z = st.norm.ppf(0.975); p = k / n; d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        assert abs(lo - (c - h)) < 1e-12, "statsmodels and scipy disagree"
        return f"{k}/{n} = {100*p:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"

    cites = cited_paths()
    tr = tracked()
    untracked = {p: k for p, k in cites.items() if p not in tr}
    print(f"cited bench/logs paths: {len(cites)}")
    print(f"  untracked: {wilson(len(untracked), len(cites))}")

    by_month: dict[str, list[str]] = collections.defaultdict(list)
    undated = []
    for p in untracked:
        e = era(p)
        (by_month[e].append(p) if e else undated.append(p))
    print(f"\nUNTRACKED BY MONTH (the hypothesis predicts the early months dominate):")
    for month in sorted(by_month):
        n = len(by_month[month])
        bar = "#" * min(n, 60)
        print(f"  {month}  {n:4d}  {bar}")
    print(f"  undated (no date in the path): {len(undated)}")

    note_only = {p for p, k in untracked.items() if "NOTE" in k}
    print(f"\ncited by a NOTE and untracked: {wilson(len(note_only), len(cites))}")
    nm = collections.Counter(era(p) or "undated" for p in note_only)
    for month, n in sorted(nm.items()):
        print(f"  {month}  {n}")

    dated = [p for p in untracked if era(p)]
    if dated:
        recent = [p for p in dated if era(p) >= "2026-09"]
        print(f"\nTHE VERDICT ON THE HYPOTHESIS")
        print(f"  untracked paths dated 2026-09 or later: {wilson(len(recent), len(dated))}")
        print("  The hypothesis predicts this share is SMALL. A large share means the"
              "\n  cause is current practice, not the project's prose era.")

    # THE LABEL HALF OF THE RULING. A cited path is in exactly 1 of 3 states,
    # and the 3rd is the one nobody had counted: the file was never kept, so it
    # cannot be opened on ANY machine, not merely on someone else's.
    missing = [p for p in untracked if not (REPO / p).is_file()]
    local_only = [p for p in untracked if (REPO / p).is_file()]
    print(f"\nDISPOSITION OF EVERY CITED PATH")
    print(f"  tracked in git            : {wilson(len(cites) - len(untracked), len(cites))}")
    print(f"  present but untracked     : {wilson(len(local_only), len(cites))}")
    print(f"  MISSING -- never kept     : {wilson(len(missing), len(cites))}")
    if args.manifest:
        import json
        rows = {}
        for path, kinds in sorted(cites.items()):
            state = ("tracked" if path not in untracked
                     else "local_only" if (REPO / path).is_file() else "missing")
            rows[path] = {"cited_by": sorted(kinds), "state": state}
        Path(args.manifest).write_text(
            json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        print(f"\n  manifest written: {args.manifest} ({len(rows)} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
