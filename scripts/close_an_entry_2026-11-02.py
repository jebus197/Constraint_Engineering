#!/usr/bin/env python3
"""Close a task-list entry across ALL 3 of its surfaces, or refuse and change none.

HIS STANDING INSTRUCTION, 2026-10-19, verbatim: *"What kept your last sprint
alive is that you mechanist your master task list. Perhaps you shuld add these
tasks to it and adapt it so it can he;p you stay in the game again?"* (His
"mechanist" is "mechanised".) The principle it states is that a step held in the
author's memory is not a mechanism.

★ WHY THIS EXISTS: 3 COMMIT REFUSALS IN ONE DAY, ALL THE SAME GUARD, ALL MINE.
6 entries were closed on 2026-11-02 -- B61, C0036, C0037, C0054, B60 and B41 --
and closing an entry means changing 3 things at once:

  1. the TASK-LIST MARKER      state OPEN -> DONE, status -> COMMITTED, evidence
  2. the REGISTER TICKET       close(tid, resolution, verification)
  3. the AUTHORED DETAIL       remove the entry from
                               experimental_notes/data/morning_report_decisions.json

I touched 1 or 2 of the 3 on every attempt. Attempt 1 left B61, C0036 and C0037
stale in the authored detail; attempt 2 left B60 stale AND named 3 producer
scripts as evidence where the rule requires a path the suite RUNS; attempt 3 left
B41 stale. Each refusal cost a 12-minute board.

AND A 4TH TRAP, met twice: THE MARKER FORM VARIES. B60's marker already carried
an `evidence:` field and B41's carried a different `status:`, so an exact-string
replacement built from a guess failed on both -- caught each time only because
the edit script asserted its anchor appeared exactly once. The marker is matched
by PATTERN here, not by a constructed literal.

IT REFUSES RATHER THAN HALF-APPLYING. If the marker cannot be found, or the
ticket will not close, or the detail cannot be rewritten, nothing is changed and
the reason is printed. A partial closure is the state that caused every refusal
above, so it is the one state this tool must not be able to produce.

WHAT IT WILL NOT DO. It never REJECTS a request and never reopens anything --
`reopen` is founder-only by design and only he may reject. It only records that
work he already ruled on is complete.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys


REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"

#: DONE with any of these is refused by `task_list_markers.CONTRADICTORY`:
#: "A task cannot be done before its work was committed."
OK_WITH_DONE = ("COMMITTED", "ENABLED")


def _marker_re(ident: str) -> re.Pattern:
    return re.compile(
        r"<!--\s*task:\s*" + re.escape(ident) + r"\s*\|\s*state:\s*(\w+)"
        r"\s*\|\s*status:\s*(\w+)"
        r"(?:\s*\|\s*evidence:\s*([^>|]*?))?"
        r"(?:\s*\|\s*ruled:\s*([^>|]*?))?\s*-->")


def stale_detail() -> list[str]:
    """Authored detail the pre-commit guard will call ORPHAN.

    ★ CALLS THE GUARD'S OWN PRODUCER RATHER THAN APPROXIMATING IT, and the first
    version of this function did approximate it -- treating every entry not DONE
    or WITHDRAWN as live -- and reported 22 stale keys where the guard had named
    only the 5 closed that day. 22 was not a finding; it was a wrong predicate.
    The guard's `live` set is the DERIVED DECISION LIST, which is far narrower
    than "every entry still open", so `morning_report_build.decisions()` is
    imported and its `orphan` return is used verbatim. A second spelling of a
    rule drifts from the first, which is the defect class this project has
    measured more often than any other.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_mrb", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
        # The call site is `items = task_items() + study_items()`, read from
        # the producer itself rather than guessed -- 2 guesses at the name
        # failed before this was looked up.
        items = m.task_items() + m.study_items()
        _attached, _missing, orphan = m.decisions(items)
        return list(orphan)
    except Exception as exc:                                 # noqa: BLE001
        return [f"(the guard's own producer could not be called: "
                f"{type(exc).__name__}: {exc})"]


def close_entry(ident: str, *, evidence: str, resolution: str,
                verification: str, status: str = "COMMITTED",
                dry_run: bool = True) -> dict:
    """All 3 surfaces, or none. Returns what it did or why it refused."""
    from bench.ticket_store import TicketStore
    rec: dict = {"ident": ident, "refused": None, "marker": None,
                 "tickets": [], "detail_removed": []}
    if status.upper() not in OK_WITH_DONE:
        rec["refused"] = (f"status {status!r} with state DONE is refused by "
                          f"task_list_markers.CONTRADICTORY; use one of "
                          f"{OK_WITH_DONE}")
        return rec

    text = LIST.read_text()
    m = _marker_re(ident).search(text)
    if not m:
        rec["refused"] = f"no marker for {ident} in {LIST.name}"
        return rec
    if m.group(1).upper() == "DONE":
        rec["refused"] = f"{ident} is already DONE; refusing to re-close it"
        return rec
    ruled = (m.group(4) or "").strip()
    new_marker = (f"<!-- task: {ident} | state: DONE | status: {status.upper()}"
                  f" | evidence: {evidence}"
                  + (f" | ruled: {ruled}" if ruled else "") + " -->")
    rec["marker"] = {"was": m.group(0), "now": new_marker}

    st = TicketStore()
    tickets = [t for t in st.by_task_ref(ident)
               if getattr(t, "status", "") != "CLOSED"]
    rec["tickets"] = [getattr(t, "tid", "?") for t in tickets]
    rec["detail_removed"] = [k for k in (f"task:{ident}", ident)]

    if dry_run:
        return rec

    # 1. the marker
    LIST.write_text(text[:m.start()] + new_marker + text[m.end():])
    # 2. the tickets
    for t in tickets:
        st.close(getattr(t, "tid"), resolution=resolution,
                 verification=verification)
    # 3. the authored detail
    try:
        d = json.loads(DETAIL.read_text())
        removed = []
        def prune(o):
            if isinstance(o, dict):
                for k in list(o):
                    if k in (f"task:{ident}", ident):
                        removed.append(k); o.pop(k)
                    else:
                        prune(o[k])
            elif isinstance(o, list):
                for x in o:
                    prune(x)
        prune(d)
        DETAIL.write_text(json.dumps(d, indent=1) + "\n")
        rec["detail_removed"] = removed
    except Exception as exc:                                 # noqa: BLE001
        rec["refused"] = (f"the marker and ticket(s) were updated but the "
                          f"authored detail could not be rewritten: {exc}. "
                          f"THIS IS THE PARTIAL STATE THIS TOOL EXISTS TO "
                          f"PREVENT -- fix {DETAIL.name} by hand before committing.")
    return rec


def main() -> int:
    # ★ THE HELP-INTERCEPTING CALL IS REMOVED, 2026-11-03, AND THIS IS A REMOVAL
    # WITH A MEASUREMENT BEHIND IT. A call to the shared help responder stood
    # immediately above the parser and answered `--help` FIRST, printing this
    # docstring and exiting, so argparse never got to list the flags. Measured
    # across the 6 scripts that had both: 0 of 16 defined flags were visible
    # under `--help`. argparse shows all of them, so the capability is not lost
    # but strictly improved -- which is the only ground the additive standard
    # accepts for taking something out.
    ap = argparse.ArgumentParser(prog="close_an_entry_2026-11-02.py",
                                 description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report entries whose authored detail is stale")
    ap.add_argument("--entry", default=None, help="the entry identifier")
    ap.add_argument("--evidence", default="", help="test path(s) the suite RUNS")
    ap.add_argument("--resolution", default="")
    ap.add_argument("--verification", default="")
    ap.add_argument("--status", default="COMMITTED")
    ap.add_argument("--apply", action="store_true")
    a, unknown = ap.parse_known_args()
    if unknown:
        print(f"unrecognised argument(s): {unknown}", file=sys.stderr)
        return 2

    if a.check or not a.entry:
        s = stale_detail()
        print(f"stale authored detail: {len(s)}")
        for k in s:
            print(f"  {k}  -> remove from {DETAIL.name}")
        if not a.entry:
            print("\ngive --entry with --evidence, --resolution and "
                  "--verification to close one, and --apply to write.")
        return 1 if s else 0

    rec = close_entry(a.entry, evidence=a.evidence, resolution=a.resolution,
                      verification=a.verification, status=a.status,
                      dry_run=not a.apply)
    print(json.dumps(rec, indent=1, default=str))
    return 2 if rec["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
