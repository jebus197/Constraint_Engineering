#!/usr/bin/env python3
"""Write the FAILING SET of a pytest run to a committed manifest, not just a count.

READY TO DROP INTO `scripts/` AFTER THE BATCH 1 COMMIT.

WHY THIS EXISTS. On 2026-11-22, with a commit board running and a failure
visible at 77 per cent, the question "is this failure new?" could not be
answered. The last full-suite measurement — 32 failed, 17,760 passed, at
`6304f771` on 2026-11-14 — recorded its COUNT and not its COMPOSITION.
`experimental_notes/Suite_Triage_2026-11-14.md` names 4 test files, not 32
failures, and holds 0 occurrences of FIXED, RESOLVED, remain, still-fail or
pre-existing.

**A COUNT CANNOT BE DIFFERENCED.** Two runs reporting 32 failures may share 32,
or 0. Without the set, every failure must be re-run and re-read to learn
whether it is new, which is the concrete cost of B165 — the stale, non-green
full-suite measurement.

WHAT IT RECORDS. One JSON manifest per run: the node ids that FAILED and
ERRORED, the counts pytest itself reported, the commit, the branch, whether the
tree was dirty, and the log it was read from. The node id is the unit, not the
file, because a file with 60 tests can fail 1 and pass 59.

WHAT IT DOES NOT DO. It does not judge. Deciding whether a failure is
pre-existing is a comparison between 2 manifests, and `--diff` does exactly
that and nothing more.

USAGE
    record_the_failing_set_2026-11-22.py <pytest-log> [--out PATH]
    record_the_failing_set_2026-11-22.py --diff OLD.json NEW.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

#: pytest's own summary lines. ERROR is captured as well as FAILED: a collection
#: error is a red result that a FAILED-only filter reports as green, which is the
#: silence-reads-as-success failure this project has recorded more than once.
_NODE = re.compile(r"^(FAILED|ERROR)\s+(\S+)", re.M)
#: pytest's FINAL summary line only, e.g. "3 failed, 4226 passed, 12 skipped in 42s".
#: ★ ANCHORED AFTER A DEFECT IN THIS SCRIPT, 2026-11-22. The first version
#: matched the counts ANYWHERE in the log and scraped `sv`'s own prose citation
#: of a PAST run -- "17,760 passed, 32 failed, 40 skipped" -- reporting them as
#: this run's result. It also read `760` out of `17,760`, because a bare `\d+`
#: has no left boundary and a thousands separator ends the match. A CITATION IS
#: NOT AN EVENT, which is the same class this project records elsewhere.
_SUMMARY_LINE = re.compile(
    r"^=*\s*(?:[\d,]+ (?:passed|failed|error|errors|skipped|xfailed|xpassed)"
    r"(?:,\s*)?)+.*\bin\s[\d.]+s", re.M)
_TALLY = re.compile(r"(?<![\d,])([\d,]+)\s+(passed|failed|skipped|errors?|xfailed|xpassed)\b")


def _git(repo: pathlib.Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:                                        # noqa: BLE001
        return ""


def build(log: pathlib.Path, repo: pathlib.Path) -> dict:
    text = log.read_text(errors="ignore")
    nodes = sorted({f"{kind}:{node}" for kind, node in _NODE.findall(text)})
    # Read counts ONLY from pytest's own final summary line. If none is present
    # -- a partial or interrupted log -- the tally stays EMPTY rather than being
    # filled from prose, because an empty tally is visibly unknown while a wrong
    # one is indistinguishable from a right one.
    tally = {}
    lines = _SUMMARY_LINE.findall(text)
    summary = ""
    for m in _SUMMARY_LINE.finditer(text):
        summary = m.group(0)
    if summary:
        for m in _TALLY.finditer(summary):
            tally[m.group(2).rstrip("s") if m.group(2).startswith("error") else m.group(2)] = \
                int(m.group(1).replace(",", ""))
    return {
        "schema": 1,
        "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "log": str(log),
        "commit": _git(repo, "rev-parse", "HEAD"),
        "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "tree_dirty_files": len([l for l in _git(repo, "status", "--porcelain").splitlines() if l]),
        "reported_tally": tally,
        "failing_set": nodes,
        "failing_count": len(nodes),
        #: STATED, because the 2 can disagree and the disagreement is a finding:
        #: pytest's tally counts test CASES, the set counts summary LINES, and a
        #: truncated or interrupted log yields fewer lines than cases.
        "tally_vs_set_agree": tally.get("failed", 0) + tally.get("error", 0)
                              + tally.get("errors", 0) == len(nodes),
    }


def diff(old: pathlib.Path, new: pathlib.Path) -> int:
    a = json.loads(old.read_text()); b = json.loads(new.read_text())
    sa, sb = set(a["failing_set"]), set(b["failing_set"])
    fixed, fresh, carried = sorted(sa - sb), sorted(sb - sa), sorted(sa & sb)
    print(f"  OLD {a['commit'][:8]} {len(sa)} failing   NEW {b['commit'][:8]} {len(sb)} failing\n")
    print(f"  NEW failures ({len(fresh)}) — these are the ones to act on:")
    for n in fresh:
        print(f"    + {n}")
    print(f"\n  CARRIED OVER ({len(carried)}) — pre-existing, not this change:")
    for n in carried[:12]:
        print(f"    = {n}")
    if len(carried) > 12:
        print(f"    ... and {len(carried)-12} more")
    print(f"\n  NO LONGER FAILING ({len(fixed)}):")
    for n in fixed[:12]:
        print(f"    - {n}")
    if len(fixed) > 12:
        print(f"    ... and {len(fixed)-12} more")
    return 1 if fresh else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", nargs="?", help="a pytest output log to read")
    ap.add_argument("--out", default=None, help="where to write the manifest")
    ap.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"),
                    help="compare 2 manifests and name only what is NEW")
    args = ap.parse_args(argv)

    if args.diff:
        return diff(pathlib.Path(args.diff[0]), pathlib.Path(args.diff[1]))

    if not args.log:
        ap.error("a log is required unless --diff is given")
    log = pathlib.Path(args.log)
    if not log.is_file():
        print(f"no such log: {log}", file=sys.stderr)
        return 2

    repo = pathlib.Path(__file__).resolve().parents[1]
    if not (repo / ".git").exists():
        repo = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    rec = build(log, repo)

    out = pathlib.Path(args.out) if args.out else (
        repo / "experimental_notes" / "data" /
        f"failing_set_{rec['commit'][:8] or 'nocommit'}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1) + "\n")

    print(f"  log            : {log}")
    print(f"  commit/branch  : {rec['commit'][:8]} on {rec['branch']}")
    print(f"  reported tally : {rec['reported_tally']}")
    print(f"  failing set    : {rec['failing_count']} node id(s)")
    print(f"  tally agrees   : {rec['tally_vs_set_agree']}")
    for n in rec["failing_set"][:12]:
        print(f"      {n}")
    if rec["failing_count"] > 12:
        print(f"      ... and {rec['failing_count']-12} more")
    print(f"  written        : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
