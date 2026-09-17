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

Read-only: it runs `git grep` and `git ls-files` and writes nothing, except the
manifest when `--manifest` names a path for it.
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


def cited_paths(rev: str | None = None) -> dict[str, set[str]]:
    """Every bench/logs path named by a tracked file, and who names it.

    With `rev`, the citing files are read as they stand at that commit rather
    than in the working tree, so a manifest built at a named commit can be
    re-derived exactly later, whatever has been cited since.
    """
    out: dict[str, set[str]] = collections.defaultdict(set)
    # THE SOURCES MUST EXCLUDE bench/logs ITSELF. 6,462 files under bench/logs
    # are tracked despite `.gitignore:41`, and a log file naming its own sibling
    # paths is not a CITATION -- one archived transcript alone contains 1,047
    # such strings. Sweeping them in measures the extractor, not the corpus,
    # which is the defect task A8's own entry records ("206 of 290 -- a figure
    # about the extractor"). Committed 2026-09-17 after making it a second time.
    raw = _git("grep", "-I", "-o", "-E", CITE.pattern, *([rev] if rev else []), "--",
               ":(exclude)bench/logs", ".")
    for line in raw.splitlines():
        if rev:
            line = line.removeprefix(f"{rev}:")
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


def tracked(rev: str | None = None) -> set[str]:
    if rev:
        return set(_git("ls-tree", "-r", "--name-only", rev).splitlines())
    return set(_git("ls-files").splitlines())


#: A cited string that is a placeholder rather than a path: `XX`, an ellipsis, a
#: glob, or a `<name>` or `{name}` slot.
TEMPLATE = re.compile(r"XX|\.\.\.|\*|<|\{")

#: Every state a cited path can be in, in the order `disposition` tests them.
STATES = ("tracked", "local_only", "directory", "template", "prefix", "missing")


def disposition(path: str, tracked_paths: set[str], root: Path = REPO) -> str:
    """Exactly 1 of STATES for a cited path.

    REPAIRED 2026-09-17. The first version had 3 states and called anything that
    was not a file MISSING, "never kept". Of the 335 rows it so labelled, 194
    were directories that exist, 78 were truncated prefixes of existing paths,
    such as `bench/logs/exp45_` in a glob, and 14 were templates. 49 were
    absent. A label saying "never kept" about a directory that is on disk is
    the false statement the manifest exists to prevent.

    `directory` and `prefix` describe THIS machine, as `local_only` always has:
    a directory of untracked logs exists here and nowhere else. `missing` now
    means what it says, absent from this machine.
    """
    if path in tracked_paths:
        return "tracked"
    p = root / path
    if p.is_file():
        return "local_only"
    if p.is_dir():
        return "directory"
    if TEMPLATE.search(path):
        return "template"
    stem = path.rstrip("/").rsplit("/", 1)[-1]
    if p.parent.is_dir() and any(c.name.startswith(stem) for c in p.parent.iterdir()):
        return "prefix"
    return "missing"


def era(path: str) -> str | None:
    m = DATE.search(path)
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--manifest", metavar="PATH",
                    help="write the disposition of every cited path as JSON, 1 of "
                         + ", ".join(STATES) + ". This is the LABEL half of the "
                         "founder's accept-and-label ruling.")
    ap.add_argument("--at", metavar="REV", default=None,
                    help="derive the citations and the tracked set at this commit "
                         "rather than from the working tree; the manifest records it")
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

    rev = _git("rev-parse", args.at).strip() if args.at else None
    cites = cited_paths(rev)
    tr = tracked(rev)
    if rev:
        print(f"citations and tracked set as at {rev[:7]}")
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
    counts = collections.Counter(disposition(p, tr) for p in cites)
    print(f"\nDISPOSITION OF EVERY CITED PATH")
    for state in STATES:
        print(f"  {state:10s}: {wilson(counts[state], len(cites))}")
    # A path absent here may still be recoverable from git. Only one that no ref's
    # history contains needs a backup to recover, which is the founder's question.
    absent = [p for p in cites if disposition(p, tr) == "missing"]
    in_history = [p for p in absent if _git("log", "--all", "--format=%h", "-1", "--", p).strip()]
    print(f"  missing and in no git ref's history: {len(absent) - len(in_history)} of {len(absent)}")
    if args.manifest:
        import json
        rev = rev or _git("rev-parse", "HEAD").strip()
        at_cites, at_tracked = cited_paths(rev), tracked(rev)
        rows = {path: {"cited_by": sorted(kinds), "state": disposition(path, at_tracked)}
                for path, kinds in sorted(at_cites.items())}
        Path(args.manifest).write_text(json.dumps(
            {"generated_at_commit": rev, "states": list(STATES), "rows": rows},
            indent=2) + "\n", encoding="utf-8")
        print(f"\n  manifest written: {args.manifest} ({len(rows)} paths at {rev[:7]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
