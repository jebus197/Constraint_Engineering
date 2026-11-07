#!/usr/bin/env python3
"""Stamp every artefact a panel brief quotes with its sha256 at dispatch time.

★ THE UNBUILT FIX FOR B125, SPECIFIED BY A FREE PANEL SEAT ON 2026-11-04. That
seat called the joint brief the most consequential defective instrument of the
set: the brief refers to files by path, but each seat's sandbox is a PHOTOGRAPH
taken when its copy was staged. The joint round tested both seats against an
artefact state that postdated their answers by 5 hours, and in doing so
"converts two *correct* findings into apparent fabrications". The seat could not
write the repair -- the staged tree is read-only -- so it specified it:

    record `sha256` + `mtime` per named artefact into the brief header.

B125 is OPEN and its fix has never been built. This is that fix.

WHY A STAMP AND NOT A GATE, in the seat's own reasoning: the defect is a
time-of-check/time-of-use mismatch between the brief's prose and the staged
target. A stamp closes it -- a reader can tell whether a seat's negative result
was correct against what it was GIVEN -- without adding a gate that could refuse
a dispatch. Simplest sufficient, and nothing is removed.

THE PATHS ARE EXTRACTED FROM THE PROSE, not from a hand-kept list, because the
brief names its artefacts in sentences and a parallel list would be a second
place for the brief to disagree with itself.
"""
from __future__ import annotations
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

#: a repo-relative path as the briefs actually write them: inside backticks, or
#: bare with a known top-level directory and a file extension.
PATH = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:py|md|json|jsonl|txt|toml|cfg|sh))`"
    r"|\b((?:bench|scripts|docs|resources|experimental_notes|hooks)"
    r"/[A-Za-z0-9_./-]+\.(?:py|md|json|jsonl|txt|toml|cfg|sh))\b")


#: ★ BARE FILENAMES ARE RESOLVED, added after the first run. The briefs name 4
#: of their artefacts by BASENAME inside backticks -- `cdsfl_operational.md`,
#: `reference_runner_v3.py` and 2 more -- which are not repo-relative and so
#: resolved to nothing. Reporting them as absent would have understated the
#: stamped set by more than half and, worse, read as 4 missing files when all 4
#: are present. A basename is stamped only when exactly ONE file in the tree
#: carries it, outside the log harvests; an ambiguous basename is left
#: unresolved and reported, because guessing which copy a seat was given is the
#: very ambiguity this stamp exists to remove.
_IGNORE = ("bench/logs/", "/sandbox_harvest/", "/panel_worktree_harvest/")

def resolve(rel: str, repo: Path = REPO) -> str | None:
    if (repo / rel).is_file():
        return rel
    if "/" in rel:
        return None
    hits = [p for p in repo.rglob(rel)
            if p.is_file() and not any(k in str(p) for k in _IGNORE)]
    if len(hits) == 1:
        return str(hits[0].relative_to(repo))
    return None


def named_artefacts(text: str, repo: Path = REPO) -> list[str]:
    """Repo-relative paths the brief names AND that resolve, in first-seen order."""
    seen, out = set(), []
    for m in PATH.finditer(text):
        raw = (m.group(1) or m.group(2) or "").strip()
        if not raw or raw in seen:
            continue
        seen.add(raw)
        got = resolve(raw, repo)
        if got and got not in out:
            out.append(got)
    return out


def unresolved(text: str, repo: Path = REPO) -> list[str]:
    """Named but not resolvable: genuinely absent, or an ambiguous basename."""
    bad, seen = [], set()
    for m in PATH.finditer(text):
        raw = (m.group(1) or m.group(2) or "").strip()
        if not raw or raw in seen:
            continue
        seen.add(raw)
        if resolve(raw, repo) is None:
            bad.append(raw)
    return bad


def stamp(rel: str, repo: Path = REPO) -> dict:
    p = repo / rel
    b = p.read_bytes()
    st = p.stat()
    return {
        "path": rel,
        "sha256": hashlib.sha256(b).hexdigest(),
        "bytes": len(b),
        "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc)
                         .isoformat(timespec="seconds"),
    }


def stamp_block(text: str, repo: Path = REPO) -> str:
    """The header block to prepend to a brief, naming what each seat was given."""
    arts = named_artefacts(text, repo)
    if not arts:
        return ""
    lines = [
        "## ARTEFACT STAMPS AT DISPATCH",
        "",
        "Each seat's copy is a photograph taken when its sandbox was staged. These",
        "are the sha256 digests and modification times of every artefact this brief",
        "names, AS DISPATCHED. If an artefact has changed since, a seat's reading of",
        "it was correct against the state below and must not be read as an error",
        "against a later state. Recompute with `sha256sum <path>` to compare.",
        "",
        "| artefact | sha256 (first 16) | bytes | modified (UTC) |",
        "|---|---|---|---|",
    ]
    for rel in arts:
        s = stamp(rel, repo)
        lines.append(f"| `{s['path']}` | `{s['sha256'][:16]}` | {s['bytes']} | {s['mtime']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    #: ANSWER `--help` BEFORE DOING ANY WORK. His rule, measured: a flag
    #: that runs the whole measurement can cost machine time or money,
    #: and 15 of 17 runners once billed for it.
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _ah
    _ah(__doc__, __file__)
    brief = REPO / "bench" / "logs" / "joint_the_period_reviewed_2026-11-04" / "BRIEF.md"
    if not brief.is_file():
        print(f"no brief at {brief}"); return 2
    text = brief.read_text(encoding="utf-8")
    arts = named_artefacts(text)
    print(f"brief            : {brief.relative_to(REPO)}  ({len(text)} chars)")
    print(f"paths named      : {len(set(m.group(1) or m.group(2) for m in PATH.finditer(text)))}")
    print(f"of those, EXIST  : {len(arts)}")
    missing = unresolved(text)
    print(f"named but absent : {len(missing)}")
    for r in missing[:8]:
        print(f"    {r}")
    #: ★ STATE THE REMAINDER. A listing cut to 8 under a heading that
    #: reads as complete is a silent falsehood, and 3 of these shipped in
    #: 1 night's work. The total is printed, so the reader can see the cut.
    if len(missing) > 8:
        print(f"    ... and {len(missing) - 8} more not shown (of {len(missing)} total)")
    blk = stamp_block(text)
    print(f"\nstamp block      : {len(blk.splitlines())} lines, "
          f"{len(blk)} chars for {len(arts)} artefacts")
    print("\n" + "\n".join(blk.splitlines()[:14]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
