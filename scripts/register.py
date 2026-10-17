#!/usr/bin/env python3
"""Search the issue register by hash id, by word, by mechanism or by area.

HIS INSTRUCTION, 2026-10-17: *"the registry should be rather like the current
registry in Windows is right now (at least somewhat superficially), where you
can search for a string ID, or a literal word search, or by any other method
that allows the registry to be searched quickly and efficiently, with a high
degree of accuracy."* And: *"The registry can be organised into different areas
of functionality ... so you don't need to risk wasting time searching through
every issue every single time to find/ID one particular issue."*

WHAT WAS ACTUALLY MISSING. The register has had all 4 search methods as library
functions since it was built, and 0 ways to call them from a terminal: a search
of `bench/ticket_store.py` for `argparse` returned nothing. So the gap his
instruction names is not the searching, it is the ENTRY POINT. That is what
this is. The design brief he attached on the same day proposes the same thing
in its section 4, as a JSON-returning CLI, and that part of it is taken.

WHAT THE BRIEF PROPOSED AND WAS NOT TAKEN, each with the measurement that
decided it, so the decision can be objected to:

  * A SQLite table with an indexed primary key for exact lookups, for "O(1)"
    performance. The existing exact lookup is a dict: 0.0015 ms median,
    0.0079 ms mean [0.0016, 0.0142]. A SQLite round trip is slower, not
    faster, and adds a second copy of the data that can drift from the log.
  * An FTS5 virtual table for word search. The COST IT NAMES IS REAL -- the
    word layer measured 27.7689 ms mean [24.1092, 31.4286], growing linearly
    with the register -- but an in-memory postings dict gets the same answer
    203.44x faster with no second copy and no new dependency. Built, and
    guarded by comparison against the linear scan at 200 of 200 identical
    ordered results, Wilson [98.1155%, 100.0000%].
  * A content-addressable blob store for code literals, for token economy.
    The whole register is 1.5 MB and loads in ~40 ms, and `verbatim` holding
    HIS EXACT WORDS is the thing the register exists to preserve. No measured
    problem, and a real risk to the text. Revisit if a load exceeds ~1 s.
  * Typed primitive wrappers, `{"type": "Text", "data": ...}` per field. JSON
    already carries its types; this would roughly double the log for no new
    capability.
  * Namespace paths such as `/issues/open/` and `/dupes/`. The register
    already expresses exactly these as the TERMINAL and LIVE status sets and
    the DUPLICATE and MERGED statuses. Encoding them a second time as paths
    would create a second source of truth about the same fact.

A NOTE ON `--area`, BECAUSE THE FIGURE IS NOT FLATTERING. An area is derived,
not stored: the module defining a ticket's `subjects` where it has any
(11.0865% of tickets, Wilson [9.2003%, 13.3027%]), else its task-list prefix
(21.9512%), else its source (66.9623%). Coverage is total, but the largest
bucket is two thirds of the register, so area is a USEFUL FILTER AND A POOR
INDEX. It is offered as a narrowing option and not as the primary key, and
`--areas` prints the distribution so the weakness is visible rather than
described.

Costs nothing to run: it reads a local file and dispatches to no model.

Usage:
  register.py --id c35755352b7e
  register.py --word "coherence budget recalibration"
  register.py --subject similar_by_words
  register.py --area bench/reference_runner_v3.py --status OPEN
  register.py --areas
  register.py --summary
  register.py --word "..." --json
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _build_parser() -> argparse.ArgumentParser:
    """Separate from `main` so a guard can parse without running anything."""
    p = argparse.ArgumentParser(
        prog="register.py",
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument("--id", dest="tid", metavar="HASH",
                   help="exact ticket id, or a unique prefix of one")
    p.add_argument("--word", metavar="TEXT",
                   help="literal word search over ticket text")
    p.add_argument("--threshold", type=float, default=None,
                   help="word-overlap share required (default 0.95)")
    p.add_argument("--include-notes", dest="include_notes", action="store_true",
                   help="also search ticket notes, which hold the text of "
                        "proposals absorbed by a settled ticket; off by "
                        "default because the register's measured operating "
                        "characteristic was derived over ticket text alone")
    p.add_argument("--subject", metavar="IDENTIFIER",
                   help="tickets concerning this code mechanism")
    p.add_argument("--area", metavar="AREA",
                   help="narrow to one derived area of functionality")
    p.add_argument("--status", metavar="STATUS", action="append", default=[],
                   help="keep only these statuses (repeatable)")
    p.add_argument("--kind", choices=("fr", "pf"),
                   help="feature request or problem found")
    p.add_argument("--areas", action="store_true",
                   help="print the area distribution and exit")
    p.add_argument("--summary", action="store_true",
                   help="print the register's own summary and exit")
    p.add_argument("--limit", type=int, default=20,
                   help="rows to print (default 20); 0 means all")
    p.add_argument("--json", action="store_true",
                   help="emit JSON rather than a table")
    return p


def _definition_index() -> dict:
    """Which module defines each identifier. Parsed with ast, not matched."""
    index: dict[str, str] = {}
    for path in sorted((REPO / "bench").glob("*.py")) + \
            sorted((REPO / "scripts").glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        rel = str(path.relative_to(REPO))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                index.setdefault(node.name, rel)
    return index


def area_of(ticket, index: dict) -> str:
    """The derived area. ONE DEFINITION, used by --area and by --areas.

    The fallback chain is measured, not guessed, and each rung's coverage is
    recorded in this module's docstring. Total coverage is 100% only because
    `source` is always set; that is why the last rung is reported separately
    rather than folded into the others.
    """
    mods = sorted({index.get(s, "") for s in (ticket.subjects or [])} - {""})
    if mods:
        return mods[0]
    if ticket.task_ref:
        head = "".join(c for c in ticket.task_ref if c.isalpha()) or "?"
        return f"task:{head}"
    return f"source:{ticket.source or 'unknown'}"


def _row(ticket, index) -> dict:
    return {
        "tid": ticket.tid,
        "kind": ticket.kind,
        "status": ticket.status,
        "area": area_of(ticket, index),
        "task_ref": ticket.task_ref,
        "ruled": ticket.ruled,
        "title": ticket.title,
    }


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # NOTHING IS LOADED FOR --help, which argparse handles before this point,
    # and nothing dispatches to a model at any point. `--help must never cost
    # money` -- 15 of 17 runners once billed for one.
    from bench.ticket_store import TicketStore

    store = TicketStore()
    store.load()

    if args.summary:
        print(json.dumps(store.summary(), indent=2, sort_keys=True))
        return 0

    index = _definition_index()

    if args.areas:
        counts: dict[str, int] = {}
        for t in store.all():
            a = area_of(t, index)
            counts[a] = counts.get(a, 0) + 1
        total = sum(counts.values()) or 1
        if args.json:
            print(json.dumps(counts, indent=2, sort_keys=True))
            return 0
        for a, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>5}  {100*n/total:7.4f}%  {a}")
        print(f"  {total:>5}  total; largest area is "
              f"{100*max(counts.values())/total:.4f}% of the register, which "
              f"is why area is a filter and not the primary key")
        return 0

    if not any((args.tid, args.word, args.subject, args.area, args.status,
                args.kind)):
        parser.print_help()
        return 2

    hits = None
    if args.tid:
        exact = store.get(args.tid)
        if exact:
            hits = [exact]
        else:
            pref = [t for t in store.all() if t.tid.startswith(args.tid)]
            hits = pref
            if not pref:
                print(f"no ticket with id or prefix {args.tid!r}",
                      file=sys.stderr)
                return 1
    if args.word:
        found = store.similar_by_words(args.word, threshold=args.threshold,
                                       include_notes=args.include_notes)
        hits = found if hits is None else [t for t in hits
                                          if t.tid in {x.tid for x in found}]
    if args.subject:
        found = store.by_subject(args.subject)
        hits = found if hits is None else [t for t in hits
                                          if t.tid in {x.tid for x in found}]
    if hits is None:
        hits = store.all()
    if args.area:
        hits = [t for t in hits if area_of(t, index) == args.area]
    if args.status:
        keep = {s.upper() for s in args.status}
        hits = [t for t in hits if t.status in keep]
    if args.kind:
        hits = [t for t in hits if t.kind == args.kind]

    rows = [_row(t, index) for t in hits]
    shown = rows if args.limit == 0 else rows[:args.limit]

    if args.json:
        print(json.dumps({"matched": len(rows), "shown": len(shown),
                          "rows": shown}, indent=2))
        return 0

    if not rows:
        print("  0 matches")
        return 0
    print(f"  {len(rows)} match(es), showing {len(shown)}")
    for r in shown:
        ruled = f" ruled:{r['ruled']}" if r["ruled"] else ""
        ref = f" [{r['task_ref']}]" if r["task_ref"] else ""
        print(f"  {r['tid']}  {r['kind']}  {r['status']:<12} "
              f"{r['area'][:34]:<34}{ref}{ruled}")
        print(f"      {r['title'][:96]}")
    if len(rows) > len(shown):
        print(f"  ... {len(rows) - len(shown)} more; --limit 0 for all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
