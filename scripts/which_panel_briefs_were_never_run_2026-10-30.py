#!/usr/bin/env python3
"""Which panel reviews were prepared and never run, and which entry each belongs to.

THE CHALLENGE THIS ANSWERS, verbatim, 2026-10-30: *"There are several panel
requests outstanding on your master task list as I recall. Not all of them are
likely to be stale. They have simply not yet been done as far as I can tell? So
your reading should take this into account and you should decide which are
genuinely outstanding and which may no longer be required?"*

HE IS RIGHT AND THE EARLIER FRAMING WAS WRONG. The consolidated file of
2026-10-30 said the panel backlog was *"almost certainly stale recording rather
than undone work"*. That claim was about 30 tickets carrying a panel-requested
label, and it was reached by tracing each ticket to a task entry and observing
that the entries had closed. It never asked the simpler question: is there a
BRIEF on disk that no seat ever answered?

WHY THAT IS THE RIGHT QUESTION. A written brief is the dispatchable artefact. If
one exists and no seat replied, the review was prepared and not run -- which is
undone work, not a recording error, whatever the ticket says. This measures the
artefacts rather than the labels.

THE PREDICATE. A directory under `bench/logs/` holding a `BRIEF.md` is a
prepared review. It RAN if it holds at least 1 seat reply -- a top-level JSON
that is not one of the known bookkeeping files -- or a `sandbox_harvest/`
directory with anything in it. Both routes are checked because the dispatcher
has written replies in both shapes over the project's history, and requiring
only one of them would undercount runs and overstate the backlog.

This is a CENSUS of every brief directory in the tree, so the proportions
reported carry no confidence interval. There is no sampling step to be
uncertain about.

Read-only. Runs no experiment, spends nothing, calls no model.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOGS = REPO / "bench" / "logs"
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: Files the dispatcher writes for its own bookkeeping. None is a seat's answer.
BOOKKEEPING = {
    "canonical_attribution.json", "canonical_touched.json", "round.json",
    "manifest.json", "meta.json", "config.json", "sandbox_manifest.json",
    "topology.json", "completion_barrier.json", "control_plane_touched.json",
}


def brief_dirs() -> list[Path]:
    if not LOGS.is_dir():
        return []
    return sorted(d for d in LOGS.iterdir() if d.is_dir() and (d / "BRIEF.md").exists())


def seat_replies(d: Path) -> list[str]:
    return sorted(p.name for p in d.glob("*.json") if p.name not in BOOKKEEPING)


def harvest_count(d: Path) -> int:
    h = d / "sandbox_harvest"
    return len(list(h.iterdir())) if h.is_dir() else 0


def entries_for(d: Path) -> tuple[str, list[str]]:
    """Which task entries this brief concerns, read from the brief itself.

    Returns (primary, all_mentioned). `primary` is only set from an EXPLICIT
    "entry B21" phrasing; a bare identifier appearing in the prose is recorded
    among the mentions but never promoted, because a brief that argues about 4
    entries is not an attribution to the first one the regex happens to reach.
    The first version of this function did promote it, and attributed the
    3-mechanism-repairs brief to B32 alone when it concerns B29, B31, B32 and
    B33, and bucketed 4 unattributed briefs together as though they were 4
    briefs on 1 question.
    """
    try:
        text = (d / "BRIEF.md").read_text(errors="replace")
    except OSError:
        return "", []
    mentions = sorted(set(re.findall(r"\b([ABCRVW]\d{1,2})\b(?=[ .:,)\]])", text)))
    m = re.search(r"\b[Ee]ntry\s+([A-Z]+\d+)\b", text)
    return (m.group(1) if m else ""), mentions


def entry_states() -> dict[str, str]:
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm  # noqa: E402
    return {e.ident: (e.state or "?") for e in tlm.parse_entries(TASK_LIST)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Census every prepared panel brief and say which never ran. "
                    "Read-only; spends nothing.")
    ap.add_argument("--show-ran", type=int, default=6,
                    help="how many of the most recent RAN rounds to print for contrast")
    args = ap.parse_args(argv)

    dirs = brief_dirs()
    states = entry_states()
    unrun, ran = [], []
    for d in dirs:
        seats = seat_replies(d)
        nh = harvest_count(d)
        primary, mentions = entries_for(d)
        row = {"name": d.name, "seats": seats, "harvest": nh,
               "entry": primary, "mentions": mentions,
               "brief_mtime": (d / "BRIEF.md").stat().st_mtime}
        (unrun if (not seats and nh == 0) else ran).append(row)

    print("=" * 74)
    print("PREPARED PANEL REVIEWS THAT NEVER RAN")
    print("=" * 74)
    print(f"\ndirectories carrying a BRIEF.md            : {len(dirs)}")
    print(f"with no seat reply and no sandbox harvest  : {len(unrun)}")
    print(f"with at least one                          : {len(ran)}")
    print("   Census of the whole tree, so no interval is attached.")

    print(f"\nTHE {len(unrun)} THAT NEVER RAN, newest first:")
    print(f"   {'brief written':<18} {'entry':<6} {'state':<10} {'mentions':<22} round")
    for r in sorted(unrun, key=lambda r: -r["brief_mtime"]):
        when = dt.datetime.fromtimestamp(r["brief_mtime"]).strftime("%Y-%m-%d %H:%M")
        ident = r["entry"] or "-"
        ment = ",".join(r["mentions"][:5]) or "-"
        print(f"   {when:<18} {ident:<6} {states.get(ident, '-'):<10} {ment:<22} {r['name']}")

    #: Count by entry over EVERY entry a brief mentions, not just an explicit
    #: primary, so a question carrying several briefs is visible. Briefs naming
    #: no entry are reported separately and never pooled as one question.
    by_entry: dict[str, list[str]] = {}
    unattributed: list[str] = []
    for r in unrun:
        ids = r["mentions"] or ([r["entry"]] if r["entry"] else [])
        if not ids:
            unattributed.append(r["name"])
        for i in ids:
            by_entry.setdefault(i, []).append(r["name"])
    print("\nUNRUN BRIEFS PER ENTRY MENTIONED:")
    for k, names in sorted(by_entry.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        note = "  <- several briefs on one question" if len(names) > 1 else ""
        print(f"   {k:<6} {states.get(k, '-'):<10} {len(names)}{note}")
    if any(len(v) > 1 for v in by_entry.values()):
        print("   Where an entry carries more than 1 unrun brief, nothing on disk")
        print("   records which is canonical, so dispatching needs that chosen first.")
    print(f"\n   naming no entry at all: {len(unattributed)}")
    for n in unattributed:
        print(f"      {n}")

    print(f"\nFOR CONTRAST, the {args.show_ran} most recent rounds that DID get replies:")
    for r in sorted(ran, key=lambda r: -r["brief_mtime"])[:args.show_ran]:
        when = dt.datetime.fromtimestamp(r["brief_mtime"]).strftime("%Y-%m-%d %H:%M")
        print(f"   {when}  seats={len(r['seats']):<2} harvest={r['harvest']:<2} {r['name']}")

    print("\nWHAT THIS DOES AND DOES NOT SETTLE.")
    print("   It settles that the review was never run: no seat ever answered.")
    print("   It does not settle whether it is still WANTED. An entry that has")
    print("   since closed may make its review moot, and that is his call.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
