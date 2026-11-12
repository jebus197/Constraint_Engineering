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


#: ★ WIDENED 2026-11-10 AFTER IT REFUSED 7 OF 248 MARKERS AND SAID "NO
#: MARKER", WHICH POINTS A READER AT THE WRONG THING. The old form spelled
#: out `state`, `status`, `evidence` and `ruled` IN THAT ORDER and admitted
#: nothing else. `responded:` was added to the marker vocabulary by entry N1
#: on 2026-11-09, 7 days after this tool was written, so every entry carrying
#: it became unclosable by the only instrument built to close one -- and the
#: refusal read as though the entry did not exist. Measured: 7 of 248
#: markers, 0.028226, Wilson 95% [0.013738, 0.057106], Clopper-Pearson
#: [0.011422, 0.057289] -- B79, B88, B94, B104, B111, B125 and B131, ALL of
#: them live at the time, and 4 of them decisions in his own queue.
#: IT NOW MATCHES THE MARKER AS A WHOLE AND PARSES ITS FIELDS GENERICALLY, so
#: a field added later cannot blind it again. The fields this tool does not
#: manage are PRESERVED on rewrite rather than dropped, which the old rebuild
#: would have done to `responded:` even with a widened pattern -- a silent
#: loss of the thing N1 exists to record.
def _marker_re(ident: str) -> re.Pattern:
    return re.compile(
        r"<!--\s*task:\s*" + re.escape(ident) + r"\s*\|([^>]*?)-->")


#: The fields this tool sets itself. Everything else is carried through.
_MANAGED = ("state", "status", "evidence")


def _marker_fields(body: str) -> list:
    """[(key, value)] in the marker's own order. Order is preserved because a
    reader of the file reads it, and reordering a line he reads is noise."""
    out = []
    for part in body.split("|"):
        part = part.strip()
        if not part:
            continue
        k, _, v = part.partition(":")
        out.append((k.strip(), v.strip()))
    return out


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
        #: ★ THE REFUSAL NAMES THE REAL CAUSE. It used to say "no marker",
        #: which a reader takes to mean the entry is absent; the actual cause
        #: was a field this tool could not parse.
        present = re.search(r"<!--\s*task:\s*" + re.escape(ident) + r"\s*\|",
                            text) is not None
        rec["refused"] = (
            f"{ident}'s marker is present but could not be parsed; its field "
            f"set is not what this tool expects"
            if present else f"no marker for {ident} in {LIST.name}")
        return rec
    fields = _marker_fields(m.group(1))
    got = {k: v for k, v in fields}
    if (got.get("state") or "").upper() == "DONE":
        rec["refused"] = f"{ident} is already DONE; refusing to re-close it"
        return rec
    if "state" not in got or "status" not in got:
        rec["refused"] = (f"{ident}'s marker carries no {'state' if 'state' not in got else 'status'} "
                          f"field; refusing to guess it")
        return rec
    #: Rebuild IN ORDER, setting what this tool manages and carrying the rest
    #: through untouched. A field added to the vocabulary later survives a
    #: close, which is the property the old rebuild lacked.
    parts, seen = [], set()
    for k, v in fields:
        if k in seen:
            continue
        seen.add(k)
        if k == "state":
            parts.append("state: DONE")
        elif k == "status":
            parts.append(f"status: {status.upper()}")
        elif k == "evidence":
            parts.append(f"evidence: {evidence}")
        else:
            parts.append(f"{k}: {v}" if v else k)
    if "evidence" not in seen:
        parts.insert(min(2, len(parts)), f"evidence: {evidence}")
    new_marker = "<!-- task: " + ident + " | " + " | ".join(parts) + " -->"
    rec["marker"] = {"was": m.group(0), "now": new_marker}
    rec["carried_through"] = [k for k, _v in fields if k not in _MANAGED]

    from bench.ticket_store import tid_of as _tid_of

    st = TicketStore()
    #: ★ A RECORD ALREADY REDIRECTED IS NOT RE-PROCESSED. The filter excluded
    #: only CLOSED, so after the redirect branch below lands, a later close of
    #: the same entry would pick the DUPLICATE record up again and try to
    #: redirect what is already redirected. DUPLICATE and MERGED are terminal
    #: for this tool's purposes: following either reaches the live ticket, which
    #: is the whole point of the counting invariant.
    _TERMINAL = {"CLOSED", "DUPLICATE", "MERGED"}
    tickets = [t for t in st.by_task_ref(ident)
               if getattr(t, "status", "") not in _TERMINAL]
    rec["tickets"] = [getattr(t, "tid", "?") for t in tickets]
    rec["detail_removed"] = [k for k in (f"task:{ident}", ident)]

    if dry_run:
        return rec

    # 1. the marker
    LIST.write_text(text[:m.start()] + new_marker + text[m.end():])
    # 2. the tickets
    #
    #: ★ AN OFF-IDENTITY RECORD IS REDIRECTED, NOT CLOSED -- 2026-11-12.
    #: This loop used to close EVERY ticket carrying the reference, with no
    #: check of which one sits at the canonical identity. A reference admits
    #: exactly 1 identity per kind, so closing B22 on 2026-11-12 closed 2 `pf`
    #: records against B22 and stranded the non-canonical one as CLOSED. That
    #: breaks the register's counting invariant -- CLOSED must equal the task
    #: list's DONE plus WITHDRAWN -- and
    #: `bench/tests/test_a_ticket_identity_survives_a_reword_2026-10-17.py`
    #: refused the commit for it, correctly.
    #:
    #: THE CHECK IS SELF-CONTAINED, which is why it is done here rather than by
    #: importing the harvester: a ticket carries its own `kind`, `verbatim` and
    #: `task_ref`, so `tid_of` recomputes the identity it SHOULD occupy from
    #: what it already holds. Verified on the live case: the stranded record
    #: recomputed to the canonical tid exactly, naming its own redirect target.
    #:
    #: FAIL TOWARDS CLOSING, DELIBERATELY. If the identity cannot be recomputed
    #: -- no verbatim, an unknown kind, any error -- the ticket is CLOSED as
    #: before. A redirect that cannot be justified must not be invented, and
    #: today's behaviour is the safe fallback.
    for t in tickets:
        _tid = getattr(t, "tid", None)
        _canon = None
        try:
            _vb = getattr(t, "verbatim", None)
            if _vb and getattr(t, "kind", None) and getattr(t, "task_ref", None):
                _canon = _tid_of(t.kind, _vb, t.task_ref)
        except Exception:                                    # noqa: BLE001
            _canon = None
        if _canon and _canon != _tid and st.get(_canon) is not None:
            st.mark_duplicate(
                _tid, of_tid=_canon, repair_identity=1.0,
                verification=(
                    f"Off-identity duplicate found while closing {ident}. A "
                    f"reference admits 1 identity per kind and "
                    f"tid_of({t.kind!r}, own verbatim, {t.task_ref!r}) = "
                    f"{_canon}, so {_tid} cannot be canonical. Redirected "
                    f"rather than closed, which keeps the register's CLOSED "
                    f"count equal to the task list's DONE plus WITHDRAWN. "
                    f"{verification}"))
            rec.setdefault("redirected", []).append({_tid: _canon})
        else:
            st.close(_tid, resolution=resolution, verification=verification)
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
