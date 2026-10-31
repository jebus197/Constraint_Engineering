#!/usr/bin/env python3
"""The outstanding work in the order he ruled it should run.

HIS RULING, 2026-10-30, verbatim from his annotation of
`Decisions_Awaiting_You_2026-10-30.txt` line 28:

    "So if they are on the master task list and are still relevant, then run
    them in the order in which they were added. Thee may be tasks on the list
    that intersperse these panel reviews, so everything that is still
    outstanding should simply be run in the historical order in which it was
    added. Any fixes emerging from these briefs should be tested with a, f,
    sy, before folding back into the runners and to the project at large. ds"

And at line 32, against the 3 briefs whose entries have since been completed:

    "if you are sure about this then that's fine. But please check anyway
    before proceeding. ds"

So this script answers 3 questions and refuses to guess any of them:

  1. WHICH entries are still outstanding -- read from the markers, not from
     prose, because a marker is the recorded state and prose is a claim about
     it.
  2. WHEN each was added. 83 of the entries carry an explicit `Added
     <timestamp>`; the rest do not, so for those the addition date is the
     FIRST COMMIT that introduced the entry's marker, read from git. An entry
     with neither is reported as UNDATED rather than given a default, because
     a default would silently sort it.
  3. WHICH outstanding entries have a panel brief already written, and for
     each brief whether any seat replied. This is the half his line-32 ruling
     requires: a brief belonging to a completed entry is CHECKED here rather
     than assumed moot.

WHAT THIS SCRIPT DOES NOT DO. It does not dispatch anything. The order is the
product; running it is a separate act, and under his standing ruling a free
panel runs when he says to run it.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
LOGS = REPO / "bench" / "logs"

#: ★ ANCHORED TO ITS OWN LINE, because a marker QUOTED INSIDE AN ENTRY'S PROSE
#: is not a marker that is in force. C16's body quotes R1's superseded marker
#: verbatim -- `state: BLOCKED | ruled: 2026-08-07` -- to record the
#: contradiction it found, and an unanchored search read that quotation as a
#: live entry. The first run of this script therefore reported R1 TWICE, once
#: BLOCKED from 2026-09-09 and once OPEN from 2026-10-29, and would have put a
#: phantom BLOCKED R1 at the head of his run order. This is the same shape the
#: harvester already guards in chat: a marker inside a quotation is being
#: cited, not issued.
MARKER = re.compile(
    r"^\s*<!--\s*task:\s*([A-Z]+\d+)\s*\|\s*state:\s*(\w+)\s*\|"
    r"\s*status:\s*(\w+)")
ADDED = re.compile(r"Added\s+(2026-\d{2}-\d{2}(?:T[\d:+-]+)?)")
OUTSTANDING = ("OPEN", "DEFERRED", "BLOCKED")

#: ★ THE "DID A SEAT REPLY" PREDICATE IS IMPORTED, NOT REWRITTEN. The first
#: version of this script kept its own list of bookkeeping filenames and
#: therefore disagreed with the census that already existed: it reported 7
#: unrun briefs against the census's 8, because
#: `general_purpose_stem_calculator_2026-10-18` holds a 675-byte `console.log`
#: which an any-file-is-a-reply rule counts as seat output. The census was
#: right. 2 instruments answering 1 question is the defect, so there is now 1.
_CENSUS = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location(
        "brief_census",
        pathlib.Path(__file__).resolve().parents[1] / "scripts" /
        "which_panel_briefs_were_never_run_2026-10-30.py"))
_CENSUS.__spec__.loader.exec_module(_CENSUS)


def entries() -> list[dict]:
    text = LIST.read_text(errors="replace")
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = MARKER.search(line)
        if not m:
            continue
        task, state, status = m.group(1), m.group(2), m.group(3)
        # The body is the paragraph ABOVE the marker, which is where the
        # `Added` stamp and the title live.
        body = "\n".join(lines[max(0, i - 6):i])
        am = ADDED.search(body)
        title = ""
        for back in range(i - 1, max(0, i - 8), -1):
            if lines[back].strip().startswith("**"):
                title = lines[back].strip()[:110]
                break
        out.append({"task": task, "state": state, "status": status,
                    "line": i + 1, "added_declared": am.group(1) if am else "",
                    "title": title})
    return out


def first_commit_date(task: str) -> str:
    """The date the entry's marker first appeared, from git."""
    try:
        r = subprocess.run(
            ["git", "log", "--reverse", "--format=%cI", "-S", f"task: {task} ",
             "--", str(LIST.relative_to(REPO))],
            capture_output=True, text=True, cwd=str(REPO), timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def briefs() -> list[dict]:
    out = []
    for d in sorted(LOGS.glob("*/")):
        bf = d / "BRIEF.md"
        if not bf.is_file():
            continue
        text = bf.read_text(errors="replace")
        m = re.search(r"\b[Ee]ntry\s+([A-Z]+\d+)\b", text)
        mentions = sorted(set(re.findall(r"\b([ABCRVW]\d{1,2})\b(?=[ .:,)\]])",
                                         text)))
        seats = _CENSUS.seat_replies(d)
        nh = _CENSUS.harvest_count(d)
        # ★ A RETIRED BRIEF IS NOT OWED WORK, 2026-10-31. A `RETIRED.md` beside
        # the brief states his ruling and names the superseding round, so it is
        # neither run nor outstanding. Reported separately rather than counted
        # as a backlog, which is the over-reporting he named.
        retired = (d / "RETIRED.md").is_file()
        out.append({"dir": d.name,
                    "entry": m.group(1) if m else "",
                    "mentions": mentions,
                    "mtime": bf.stat().st_mtime,
                    "seats": seats,
                    "harvest": nh,
                    "retired": retired,
                    "ran": bool(seats) or nh > 0})
    return out


def main() -> int:
    ents = entries()
    out_ents = [e for e in ents if e["state"] in OUTSTANDING]
    for e in out_ents:
        e["added_git"] = first_commit_date(e["task"])
        e["added"] = e["added_declared"] or e["added_git"]
        e["dated"] = bool(e["added"])

    dated = [e for e in out_ents if e["dated"]]
    undated = [e for e in out_ents if not e["dated"]]
    dated.sort(key=lambda e: e["added"])

    bs = briefs()
    by_entry = collections.defaultdict(list)
    for b in bs:
        if b["entry"]:
            by_entry[b["entry"]].append(b)

    state_by_task = {e["task"]: e["state"] for e in ents}
    unrun = [b for b in bs if not b["ran"] and not b.get("retired")]
    retired_bs = [b for b in bs if not b["ran"] and b.get("retired")]

    print("=" * 74)
    print("THE OUTSTANDING WORK, IN THE ORDER HE RULED IT SHOULD RUN")
    print("=" * 74)
    print(f"entries on the list: {len(ents)}; outstanding "
          f"(OPEN/DEFERRED/BLOCKED): {len(out_ents)}")
    print(f"dated: {len(dated)}; UNDATED and therefore unsorted: {len(undated)}")
    print()
    for n, e in enumerate(dated, 1):
        bb = by_entry.get(e["task"], [])
        tag = ""
        if bb:
            def _mark(x):
                if x["ran"]:
                    return "/run"
                return "/RETIRED" if x.get("retired") else "/UNRUN"
            tag = (f"  [brief x{len(bb)}: "
                   f"{', '.join(b['dir'] + _mark(b) for b in bb)}]")
        print(f"{n:2}. {e['task']:5} {e['state']:9} added {e['added'][:19]}{tag}")
        if e["title"]:
            print(f"        {e['title']}")
    if undated:
        print("\nUNDATED (reported, NOT sorted into the order above):")
        for e in undated:
            print(f"    {e['task']:5} {e['state']:9} line {e['line']}")

    print()
    print("-" * 74)
    print("HIS LINE-32 CHECK: every brief with no seat reply, and its entry's state")
    print("-" * 74)
    print(f"brief directories: {len(bs)}; with no seat output: {len(unrun)}; "
          f"retired on his ruling: {len(retired_bs)}")
    for b in sorted(unrun, key=lambda x: x["mtime"]):
        ent = b["entry"] or "(names no entry)"
        st = state_by_task.get(b["entry"], "UNKNOWN") if b["entry"] else "n/a"
        verdict = ("STILL OWED" if st in OUTSTANDING
                   else "entry is " + st + " -- check before treating as moot")
        print(f"    {b['dir']}")
        print(f"        entry {ent} state {st} -> {verdict}")
        if b["mentions"]:
            print(f"        mentions: {', '.join(b['mentions'][:10])}")

    print()
    print(json.dumps({"outstanding": len(out_ents), "dated": len(dated),
                      "undated": [e["task"] for e in undated],
                      "order": [e["task"] for e in dated],
                      "briefs": len(bs), "unrun": len(unrun),
                      "unrun_dirs": [b["dir"] for b in
                                     sorted(unrun, key=lambda x: x["mtime"])]},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
