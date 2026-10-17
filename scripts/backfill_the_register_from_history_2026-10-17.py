#!/usr/bin/env python3
"""Task B23: populate the register with every piece of work since the outset.

HIS INSTRUCTION, 2026-10-17, verbatim: *"I feel I should have been more
explicit in my instructions when I told you to build your Bugzilla registry,
and should have told you to fully populate it with everything that had been
done up until then, from the outset of the project. But that is probably a very
large task and I don't want you to interrupt your workflow to do i[t], so you
should probably mark it as one outstanding task, after all your current master
task list/work-flow is complete."*

THE UNIT OF WORK DONE IS A COMMIT, and that is a choice worth defending rather
than assuming. A commit is the project's own record of a discrete piece of
work: it carries its own text, its own date, and a stable identifier, and it
cannot be invented after the fact. Any finer unit (a hunk, a file) would
multiply rows without adding an answerable question; any coarser unit (a day, a
session) would merge work that was separately decided.

EACH TICKET IS ANCHORED BY ITS COMMIT SHA, and that is load-bearing. The
register's subject tier DECIDES: a proposal sharing one code identifier with a
settled ticket is handed that ticket instead of being raised, and 291 of 907
existing tickets carry neither a task reference nor an anchor, so this path is
common. A backfill arriving without anchors would have been absorbed wholesale
into existing tickets -- measured on 2026-10-17 at 118 of 181 subject-carrying
tickets absorbed by a ticket sharing NEITHER their words NOR their hash,
65.1934% Wilson [58.0031%, 71.7521%]. `_distinct` is the designed escape
hatch: a caller naming an anchor the matched ticket does not own gets its own
ticket. So every backfilled row names `commit:<sha>`.

THE KIND IS A STATED HEURISTIC, NOT A JUDGEMENT. `fr` and `fh` cannot be
inferred reliably from a commit subject, so the rule is written down here and
the split is REPORTED: a subject whose first word is one of the additive verbs
is recorded as a feature request, everything else as a problem found. Each
backfilled ticket says in its own text that its kind came from this rule, so
nobody mistakes it for a classification someone made.

THE BOUNDARY IS STATED: this backfills commits REACHABLE FROM THE CURRENT
BRANCH. `git rev-list --count --all` is larger, and the difference is work on
refs this branch does not contain. The script reports both numbers so the gap
is visible rather than silently excluded.

IT IS IDEMPOTENT. Re-running adds nothing, because a commit already anchored is
skipped, and the check is made against the live store rather than a marker
file.

Usage:
  backfill_the_register_from_history_2026-10-17.py              # dry run
  backfill_the_register_from_history_2026-10-17.py --apply
  backfill_the_register_from_history_2026-10-17.py --apply --limit 50
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: A subject opening with one of these is recorded as a feature request. The
#: rule is deliberately crude AND WRITTEN DOWN, because a crude rule a reader
#: can check beats a subtle one they cannot.
ADDITIVE_VERBS = ("add", "adds", "added", "implement", "implements",
                  "implemented", "build", "builds", "built", "introduce",
                  "introduces", "create", "creates", "new", "wire", "wires",
                  "support", "supports", "extend", "extends", "enable",
                  "enables")

SEP = "\x1e"


def commits(limit: int | None = None) -> list[dict]:
    """Every commit reachable from HEAD, oldest first."""
    fmt = SEP.join(("%H", "%ad", "%an", "%s", "%b")) + "\x1d"
    out = subprocess.run(
        ["git", "log", "--reverse", "--date=short", f"--format={fmt}"],
        capture_output=True, text=True, cwd=str(ROOT))
    rows = []
    for chunk in out.stdout.split("\x1d"):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        parts = chunk.split(SEP)
        if len(parts) < 4:
            continue
        sha, date, author, subject = parts[0], parts[1], parts[2], parts[3]
        body = parts[4] if len(parts) > 4 else ""
        rows.append({"sha": sha.strip(), "date": date.strip(),
                     "author": author.strip(), "subject": subject.strip(),
                     "body": body.strip()})
        if limit and len(rows) >= limit:
            break
    return rows


def kind_of(subject: str) -> str:
    first = (subject.split() or [""])[0].strip().lower().strip(":,.")
    return "fr" if first in ADDITIVE_VERBS else "pf"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write the tickets; omit for a dry run")
    parser.add_argument("--limit", type=int, default=0,
                        help="only the first N commits (0 = all)")
    parser.add_argument("--progress", type=int, default=200,
                        help="report every N commits while applying")
    args = parser.parse_args(argv)

    from bench.ticket_store import TicketStore

    store = TicketStore()
    store.load()
    before = len(store.all())
    already = {t.anchor for t in store.all() if t.anchor.startswith("commit:")}

    rows = commits(args.limit or None)
    all_refs = subprocess.run(["git", "rev-list", "--count", "--all"],
                              capture_output=True, text=True,
                              cwd=str(ROOT)).stdout.strip()
    todo = [r for r in rows if f"commit:{r['sha']}" not in already]

    print("THE SCOPE")
    print(f"  commits reachable from HEAD   : {len(rows)}")
    print(f"  commits on all refs           : {all_refs}")
    print(f"    the difference is work on refs this branch does not contain,")
    print(f"    excluded here and named so the gap is visible.")
    print(f"  register before                : {before} tickets")
    print(f"  already backfilled             : {len(rows) - len(todo)}")
    print(f"  to raise                       : {len(todo)}")

    frs = sum(1 for r in todo if kind_of(r["subject"]) == "fr")
    print(f"\nTHE KIND SPLIT, from the stated rule and not from a judgement")
    print(f"  feature requests (additive verb first) : {frs}")
    print(f"  problems found (everything else)       : {len(todo) - frs}")
    if todo:
        from statsmodels.stats.proportion import proportion_confint
        import scipy.stats as st
        w = proportion_confint(frs, len(todo), method="wilson")
        b = proportion_confint(frs, len(todo), method="beta")
        cp = (1.0 if frs == len(todo)
              else float(st.beta.ppf(0.975, frs + 1, len(todo) - frs)))
        print(f"  = {100*frs/len(todo):.4f}%  Wilson [{w[0]*100:.4f}%, "
              f"{w[1]*100:.4f}%]  Clopper-Pearson [{b[0]*100:.4f}%, "
              f"{b[1]*100:.4f}%]  scipy agrees {abs(b[1]-cp) < 1e-9}")

    if not args.apply:
        print("\n  DRY RUN. Nothing written. Re-run with --apply.")
        for r in todo[:5]:
            print(f"    would raise [{kind_of(r['subject'])}] {r['date']} "
                  f"{r['sha'][:10]} {r['subject'][:60]}")
        return 0

    print(f"\nAPPLYING")
    raised = absorbed = closed = 0
    for n, r in enumerate(todo, 1):
        verbatim = (r["subject"] + ("\n\n" + r["body"] if r["body"] else ""))
        note = (f"BACKFILLED from project history on his instruction of "
                f"2026-10-17. Kind {kind_of(r['subject'])!r} comes from the "
                f"stated first-word rule in "
                f"scripts/backfill_the_register_from_history_2026-10-17.py, "
                f"not from anyone's classification. Author: {r['author']}.")
        ticket, outcome = store.propose(
            kind_of(r["subject"]),
            r["subject"][:200] or f"commit {r['sha'][:10]}",
            verbatim + "\n\n" + note,
            source="code",
            source_ref=f"{r['sha']} {r['date']}",
            created=r["date"],
            anchor=f"commit:{r['sha']}")
        if outcome == "created":
            raised += 1
            store.close(ticket.tid,
                        "work already done and committed",
                        verification=f"commit {r['sha']}")
            closed += 1
        else:
            absorbed += 1
        if args.progress and n % args.progress == 0:
            print(f"  {n}/{len(todo)}  raised={raised} closed={closed} "
                  f"absorbed={absorbed}")

    after = TicketStore()
    after.load()
    print(f"\nRESULT")
    print(f"  raised and closed : {raised}")
    print(f"  absorbed instead  : {absorbed}")
    print(f"  register after    : {len(after.all())} tickets "
          f"(was {before})")
    anchored = sum(1 for t in after.all() if t.anchor.startswith("commit:"))
    print(f"  commit-anchored   : {anchored} of {len(rows)} commits")
    if absorbed:
        print("  ABSORBED ROWS ARE A DEFECT, NOT A SAVING: an anchor is meant")
        print("  to guarantee a separate ticket, so any absorption means the")
        print("  escape hatch did not hold and those commits are now recorded")
        print("  only as notes on another ticket.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
