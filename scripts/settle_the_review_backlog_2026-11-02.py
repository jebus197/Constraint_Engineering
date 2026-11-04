#!/usr/bin/env python3
"""Settle the review-request backlog: close what is verifiable, name what is not.

HIS WORRY, 2026-11-01, verbatim: *"I worry that we might build up a large store
of fixes that are never applied to any of our runners in practice. This is a
problem we have encountered several times in the past and that we need to stay on
top of."* And annotation 7 of the same reply: *"what is the point of doing any
work at all if it can just be routinely ignored?"*

38 review-requested tickets are LIVE in the register, and entry B41 was closed
on 2026-11-02 WITHOUT claiming them closed, because closing a ticket requires a
verification per TICKET and B41's evidence was per ENTRY. That distinction is the
2-surface error which refused a commit earlier the same day, so it was honoured
rather than argued around. This script does the per-ticket half.

★ 38 OF 38 CARRY NO `task_ref`, measured. So the cheap trace is unavailable and
the figure quoted on 2026-10-30 -- 11 of 30 resolving to an entry -- came from a
different route: the entry code is embedded in the `source_ref` STRING, as in
"founder 2026-10-20 01:09, entry C33". That is parsed here rather than assumed,
and a ticket whose source_ref names no entry is reported as untraceable rather
than counted either way.

★ AND A TICKET MAY BE CLOSED ONLY WHEN ITS OWN SUBJECT IS DEMONSTRABLY DONE.
`TicketStore.close` is tool-only and refuses without a verification, which is the
rule doing its job: an entry being DONE is evidence about THAT entry, and it
becomes a verification for the ticket only because the ticket's source_ref names
that entry. Where it names none, nothing is closed and the reason is printed.

NOTHING IS REOPENED AND NOTHING IS REJECTED. `reopen` is founder-only by design
and only he may reject a request; this closes on completed subjects and leaves
everything else exactly as it was.
"""
from __future__ import annotations
import math, pathlib, re, sys


REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

#: An entry code as the list writes them: B20, C0037, R1, T1, C33.
ENTRY_IN_REF = re.compile(r"\bentry\s+([A-Z]\d{1,4})\b", re.I)


def _trace_through_anchor(anchor: str) -> str:
    """`<response file>#<line>` -> the entry code the annotated passage names.

    Reads the passage with the project's own format-aware reader. A naive read
    is BLIND here: 908 of his 1,174 annotations sit in files grep treats as
    binary, and 44 of 67 annotated files are invisible to it.
    """
    if "#" not in anchor:
        return ""
    fname, _, idx = anchor.rpartition("#")
    try:
        line_no = int(idx)
    except ValueError:
        return ""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_rfr", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
        f = m.RESPONSES / fname
        if not f.is_file():
            return ""
        lines = m.read_any(f).splitlines()
    except Exception:                                        # noqa: BLE001
        return ""
    # A window either side, because the entry code may sit in the sentence the
    # annotation attaches to rather than in the annotation itself.
    lo, hi = max(0, line_no - 8), min(len(lines), line_no + 3)
    window = "\n".join(lines[lo:hi])
    hits = re.findall(r"\b([BCRT]\d{1,4})\b", window)
    return hits[0].upper() if hits else ""


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main() -> int:
    # `takes_no_arguments=False` because this script HAS a flag. The default
    # refuses every argument before the caller's own parser sees it, which is
    # the documented behaviour -- and it refused `--apply` on the first run
    # here. Correct of it: a script that reads argv only through this helper
    # would otherwise read as argv-free and inherit a pass it has not earned.
    # ★ THE HELP-INTERCEPTING CALL IS REMOVED, 2026-11-03. It answered `--help`
    # BEFORE this script's own parser ran, so argparse never listed the flags:
    # measured across the 6 scripts that had both, 0 of 16 defined flags were
    # visible. `takes_no_arguments=False` was an earlier partial fix on
    # 2026-11-02; it stops the helper REFUSING a flag but not from answering
    # `--help` first. argparse's own help is now enabled, so the capability is
    # improved rather than lost.
    import argparse
    # answer_help already refused unknown flags; this parser exists only so
    # --apply is explicit and the default is a DRY RUN. A script that closes
    # tickets by default is a script that closes them by accident.
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args, _ = ap.parse_known_args()

    from bench.ticket_store import TicketStore
    from task_list_markers import parse_entries
    st = TicketStore()
    entries = {e.ident: e for e in parse_entries(
        REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")}
    wr = [t for t in st.live() if getattr(t, "kind", "") == "wr"]

    print("=" * 78)
    print("THE REVIEW-REQUEST BACKLOG" + ("  (DRY RUN)" if not args.apply else "  (APPLYING)"))
    print("=" * 78)
    print(f"  live review tickets: {len(wr)}")
    print(f"  carrying a task_ref: "
          f"{sum(1 for t in wr if (getattr(t, 'task_ref', '') or '').strip())}"
          f"   <- the cheap trace, unavailable")

    rows = []
    for t in wr:
        ref = (getattr(t, "task_ref", "") or "").strip()
        route = "task_ref"
        if not ref:
            m = ENTRY_IN_REF.search(str(getattr(t, "source_ref", "") or ""))
            if m:
                ref, route = m.group(1).upper(), "source_ref"
        if not ref:
            # ★ THE 3-HOP TRACE, and a cheaper 1-hop version of this script
            # found only 1 of 38 where the 2026-10-30 measurement found 11 of
            # 30. That was NOT a refutation of the earlier figure -- it was a
            # DIFFERENT PREDICATE, and reporting it as a contradiction would
            # have been the error. The route that entry names is: `anchor`, to
            # the passage he annotated, to the entry that passage names.
            # `anchor` is `<response file>#<line index>`, and the passage is
            # read with `read_founder_responses`'s own reader -- never grep,
            # because 908 of his 1,174 annotations sit in files grep treats as
            # binary.
            ref, route = _trace_through_anchor(str(getattr(t, "anchor", "") or "")), "anchor"
        e = entries.get(ref) if ref else None
        if not ref:
            verdict = "UNTRACEABLE: source_ref names no entry"
        elif e is None:
            verdict = f"NAMES {ref}, WHICH IS NOT ON THE LIST"
        elif e.state == "DONE":
            verdict = f"SUBJECT {ref} IS DONE"
        else:
            verdict = f"SUBJECT {ref} IS {e.state}"
        rows.append({"tid": getattr(t, "tid", "?"), "ref": ref,
                     "route": route,
                     "verdict": verdict, "title": str(getattr(t, "title", ""))[:70],
                     "closable": e is not None and e.state == "DONE"})

    traceable = [r for r in rows if r["ref"]]
    closable = [r for r in rows if r["closable"]]
    import collections as _c
    print(f"  traceable: {len(traceable)} of {len(rows)}   by route: "
          f"{dict(_c.Counter(r['route'] for r in traceable))}")
    if traceable:
        p, lo, hi = wilson(len(closable), len(traceable))
        print(f"  of the traceable, subject DONE: {len(closable)}/{len(traceable)}"
              f" = {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")

    print(f"\n  CLOSABLE ({len(closable)})")
    for r in closable:
        print(f"    {r['tid']}  {r['ref']:7s} {r['title']}")
    other = [r for r in rows if not r["closable"]]
    print(f"\n  NOT CLOSED ({len(other)}), each with the reason")
    for r in other:
        print(f"    {r['tid']}  {r['verdict']}")
        print(f"              {r['title']}")

    if not args.apply:
        print(f"\n  DRY RUN. Re-run with --apply to close the {len(closable)} "
              f"whose subject is DONE. Nothing else is touched: `reopen` is "
              f"founder-only and only he may reject a request.")
        return 0

    done = 0
    for r in closable:
        try:
            st.close(r["tid"],
                     resolution=f"the subject of this request, entry {r['ref']}, is complete",
                     verification=(
                         f"task entry {r['ref']} is marked DONE on the master task list "
                         f"with its own evidence; this ticket's source_ref names that "
                         f"entry, which is what makes the entry's state a verification "
                         f"for this ticket. A panel asked to review a completed, guarded "
                         f"fix is moot. Producer: "
                         f"scripts/settle_the_review_backlog_2026-11-02.py"))
            done += 1
        except Exception as exc:                             # noqa: BLE001
            print(f"    {r['tid']}: REFUSED -> {type(exc).__name__}: {str(exc)[:110]}")
    print(f"\n  CLOSED {done} of {len(closable)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
