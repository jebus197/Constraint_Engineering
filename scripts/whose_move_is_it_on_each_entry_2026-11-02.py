#!/usr/bin/env python3
"""Whose move is it on each live entry: his, or mine?

WHY THIS EXISTS. The Stop gate reports "N items are still OPEN and nothing is
blocking" and names the next unstarted entry. That is his own 2026-09-10
criterion and it is the right one for BLOCKING -- *"Does it prevent further
progress on the task list?"* But "the next action on this entry is HIS" is a
DIFFERENT property, and nothing measured it. Counting OPEN markers makes a list
of his pending decisions look like a list of my pending work.

EVERY ROUTE IS DERIVED FROM AN ARTEFACT, NOT FROM MY JUDGEMENT, because a
hand-authored table of who-owns-what is a claim about evidence rather than
evidence (`measured-rate-travels-with-its-script`). The 4 routes:

  1. A DECISION SLOT -- the entry appears in the generated decision list, which
     is read by running the project's own agreement producer rather than by
     reimplementing its derivation.
  2. AN OPEN QUESTION OR PROPOSAL IN THE REGISTER -- a ticket whose `task_ref`
     is this entry and whose state is not terminal.
  3. AN ASKING SENTENCE IN ITS OWN TEXT -- reusing the `ASKS` pattern and the
     ask-masking helper from the ruling-status producer, so the 2 cannot drift.
  4. PARKED -- the entry is named in the parked file, which by his 2026-09-10
     ruling means queued for him and explicitly NOT a reason to stop.

AN ENTRY WITH NO ROUTE AT ALL IS MINE, and those are reported by name rather
than as a count, because they are the actionable list.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
AGREE = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
RULING = (REPO / "scripts"
          / "which_entries_ask_for_a_ruling_he_has_given_2026-11-01.py")

#: Markers the list actually uses. DONE and WITHDRAWN are terminal.
LIVE_STATES = ("OPEN", "BLOCKED", "DEFERRED")
MARKER = re.compile(
    r"<!-- task: ([A-Z0-9]+) \| state: ([A-Z_]+) \| status: ([A-Z_]+)")


def _live_entries() -> dict:
    """Every entry whose LAST marker carries a live state.

    THE LAST MARKER WINS. An entry may carry more than one marker when an
    addendum quotes it, and an earlier copy can disagree with the current one;
    taking the last is what the list's own ordering means.
    """
    text = TASK_LIST.read_text(errors="replace")
    state: dict = {}
    for m in MARKER.finditer(text):
        state[m.group(1)] = (m.group(2), m.group(3))
    return {k: v for k, v in state.items() if v[0] in LIVE_STATES}


def _decision_slots() -> set:
    """Entry codes the generated decision list carries.

    Read by RUNNING the agreement producer, so this script cannot disagree with
    the surface he is actually shown.
    """
    r = subprocess.run([sys.executable, str(AGREE)], capture_output=True,
                       text=True, cwd=str(REPO), timeout=600)
    out = r.stdout + r.stderr
    block = out.split("generated report")[-1].split("spoken file")[0]
    return set(re.findall(r"^\s+([A-Z0-9]+)\s+->", block, re.M))


def _open_tickets(codes) -> dict:
    """code -> its LIVE tickets, using the store's own liveness definition.

    `TicketStore.live()` and `by_task_ref()` are the instruments that exist;
    re-deriving terminality here would be a second definition of CLOSED, and
    the store's own `TERMINAL` set already names 7 statuses plus REJECTED.
    """
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore  # noqa: E402
    store = TicketStore()
    live_ids = {t.tid for t in store.live()}
    out: dict = {}
    for code in codes:
        for t in store.by_task_ref(code):
            if t.tid in live_ids:
                out.setdefault(code, []).append((t.kind, t.tid, t.status))
    return out


def _still_asks():
    """The report builder's own LIVE-asking predicate, not the raw pattern.

    `ASKS` over a whole entry body matches HISTORICAL asking sentences that his
    later ruling already answered, which would credit an answered entry as
    still waiting on him. `morning_report_build.still_asks` is the predicate
    the report itself uses, and its docstring says so: "1 predicate, 2
    callers". Reusing it is what keeps this script and the surface he reads
    from disagreeing.
    """
    import importlib.util
    path = REPO / "scripts" / "morning_report_build_2026-10-12.py"
    spec = importlib.util.spec_from_file_location("_mrb_probe", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_mrb_probe"] = mod
    sys.path.insert(0, str(REPO / "bench"))
    spec.loader.exec_module(mod)
    # ★ FAIL-OPEN IS CORRECT FOR THE REPORT AND WRONG AS OWNERSHIP EVIDENCE.
    # `still_asks` returns True for an entry it cannot resolve, twice over --
    # "unknown entry: fail open" and "cannot tell: fail open" -- which is right
    # for the report, because silencing a question you cannot classify is the
    # worse error there. Used HERE it would credit an unresolvable entry to HIM
    # by default, which is the fault
    # `feedback_do_not_attribute_a_default_to_him_2026-10-30` records at 180 of
    # 680, where he then blamed himself for a default I had assigned.
    #
    # MEASURED 2026-11-02: 0 of the 19 live entries are unresolvable, so this
    # changes no figure today. It is wired because without it `--check` CANNOT
    # FAIL -- a fabricated code returns True and gets a route -- and a check
    # that cannot fail is the unwired-addition half of the additive standard.
    # Found by injecting a routeless entry and watching `--check` exit 0.
    import importlib as _il
    _tlm = _il.import_module("task_list_markers")
    _dp = _load_entry_text_producer()
    _known = {e.ident for e in _tlm.parse_entries()}
    _bodies = _dp.bodies()

    def resolvable_still_asks(ident: str):
        if ident not in _known or ident not in _bodies:
            return None          # NOT a route: the predicate cannot speak
        return mod.still_asks(ident)

    return resolvable_still_asks


def _load_entry_text_producer():
    """The classifier that owns `bodies()`; loaded once, by its real path."""
    import importlib.util
    path = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
    spec = importlib.util.spec_from_file_location("_wm_dp", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_wm_dp"] = mod
    spec.loader.exec_module(mod)
    return mod


def _entry_bodies() -> dict:
    """code -> the text from its heading to the next entry heading."""
    text = TASK_LIST.read_text(errors="replace")
    bodies: dict = {}
    for m in re.finditer(r"^\*\*([A-Z]*[0-9]+)\.", text, re.M):
        nxt = re.compile(r"^\*\*[A-Z]*[0-9]+\.", re.M).search(text, m.end())
        bodies[m.group(1)] = text[m.start():nxt.start() if nxt else len(text)]
    return bodies


def _parked_codes() -> set:
    """Codes the parked file names in a HEADING, which is how it marks an item.

    MATCHING ANYWHERE IN THE FILE OVER-COUNTS, measured 2026-11-02: 17 codes
    appear somewhere in the prose against 11 named in a heading, so 6 were
    being credited as parked because another item's write-up mentioned them.
    That is the mention-versus-declaration fault `blocker_triage.py` already
    solved for dependencies -- a code appearing in a body says what the text is
    ABOUT, not what is parked. Headings carrying 2 codes ("C0036 and C0054")
    legitimately park both, so the whole heading line is scanned.
    """
    if not PARKED.is_file():
        return set()
    out: set = set()
    for head in re.findall(r"^#{2,}\s+(.+)$", PARKED.read_text(errors="replace"),
                           re.M):
        out |= set(re.findall(r"\b([BCRT]\d{1,4})\b", head))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Whose move is it on each live task-list entry: his or mine?")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any live entry has no derivable route")
    args = ap.parse_args()

    live = _live_entries()
    slots = _decision_slots()
    tickets = _open_tickets(sorted(live))
    still_asks = _still_asks()
    bodies = _entry_bodies()
    parked = _parked_codes()

    rows = []
    unresolvable: list = []
    for code in sorted(live):
        st, status = live[code]
        routes = []
        if code in slots:
            routes.append("decision slot in the report he is shown")
        tk = tickets.get(code) or []
        qs = [t for t in tk if t[0] == "qs"]
        pf = [t for t in tk if t[0] != "qs"]
        if qs:
            routes.append(f"open question {qs[0][0]}:{qs[0][1]}")
        body = bodies.get(code, "")
        asks = still_asks(code)
        if asks is None:
            # NOT a route. The predicate cannot speak for this entry, and
            # silence is not assent on his behalf.
            unresolvable.append(code)
        elif asks:
            routes.append("a LIVE asking sentence in its own text")
        if code in parked:
            routes.append("parked for him")
        if not routes and pf:
            routes.append(f"open proposal {pf[0][0]}:{pf[0][1]} and nothing else")
        rows.append((code, st, status, routes))

    his = [r for r in rows if any(not x.startswith("parked") for x in r[3])]
    parked_only = [r for r in rows if r[3] and all(x.startswith("parked") for x in r[3])]
    mine = [r for r in rows if not r[3]]

    print("=" * 76)
    print("WHOSE MOVE IS IT ON EACH LIVE ENTRY?")
    print("=" * 76)
    for code, st, status, routes in rows:
        if not routes:
            tag = "MINE"
        elif all(x.startswith("parked") for x in routes):
            tag = "park"
        else:
            tag = "HIS "
        print(f"  [{tag}] {code:7s} {st:9s} {status:10s} "
              f"{'; '.join(routes) if routes else 'no route in any artefact'}")

    n = len(rows)
    print(f"\n  live entries                  : {n}")
    print(f"  his move, by some artefact    : {len(his)}")
    print(f"  parked for him and nothing more: {len(parked_only)}")
    print(f"  MINE -- no route at all       : {len(mine)}"
          f"  {[r[0] for r in mine]}")
    print(f"  UNRESOLVABLE by the ask predicate: {len(unresolvable)}"
          f"  {unresolvable}")

    if n:
        from scipy import stats
        from statsmodels.stats.proportion import proportion_confint

        def iv(k, n, label):
            lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
            clo = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
            chi = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
            print(f"\n  {label}: {k} of {n}, {k/n:.6f}")
            print(f"    Wilson 95%          [{lo:.6f}, {hi:.6f}]")
            print(f"    Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]")

        # ★ PARKED IS REPORTED SEPARATELY AND NOT FOLDED IN, because folding it
        # into "waiting on him" is the flattering reading and it is wrong on at
        # least 1 entry. Parked means NON-BLOCKING and queued for discussion,
        # per his 2026-09-10 ruling -- it does NOT establish that the next
        # action is his. B20 is the counter-example: it is parked AND its
        # remaining work (the fix comparator, the monitoring loop) is mine to
        # build, placed after the rest of the list by his own ruling rather
        # than waiting on a decision from him.
        iv(len(his), n, "next action HIS, by a named artefact")
        iv(len(parked_only), n, "parked only -- queued, ownership not established")
        iv(len(mine), n, "MINE with no route at all")

    print("\n  WHAT THIS IS NOT. It does not say an entry needs no work -- several")
    print("  of his decisions have the work already built and tested behind them.")
    print("  It says where the NEXT action sits, which is the thing the OPEN count")
    print("  cannot distinguish.")

    if args.check and unresolvable:
        print(f"\n  {len(unresolvable)} live entr(ies) cannot be read by the ask "
              f"predicate: {unresolvable}")
        return 1
    if args.check and mine:
        print(f"\n  {len(mine)} live entr(ies) have no derivable route: "
              f"{[r[0] for r in mine]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
