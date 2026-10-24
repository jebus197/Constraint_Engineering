#!/usr/bin/env python3
"""Stop-event gate: prod until every ticket is resolved, and never silently.

HIS INSTRUCTION, 2026-10-17: "Your master task list should ... be mechanised in
such a way that it will prod you and will keep doing so until every task on your
list is marked complete/resolved within your new Bugzilla mechanics (once
built)."

WHY A STOP HOOK AND NOT A PROMPT HOOK. A UserPromptSubmit hook can only advise;
its text is injected and may be read or not. A Stop hook can REFUSE, by returning
2. Measured over 2026-10-16 and 2026-10-17, 5 Stop refusals fired in this project
and every one of them found a real defect: an owed falsification pass twice, an
owed save once, a DONE marker whose evidence was not a collected test once, and a
memory file that had never been written once. Advice was ignored; refusals were
not. So the prodding mechanism has to sit on Stop.

HOW IT AVOIDS BECOMING A DEADLOCK. It refuses at most once per commit, keyed on
HEAD, exactly as `sv_milestone_gate.py` does. So a turn that makes progress and
commits is prodded once at its end; a turn that does not commit is prodded once
and then left alone. The gate can therefore never trap the session in a loop, and
`sys.exit(0)` on any exception means a broken gate can never fell a session
either -- a recovery mechanism that breaks the thing it protects is worse than no
mechanism.

WHAT IT REPORTS. The count of genuinely OPEN tickets, the count of UNCONFIRMED
ones which need triage rather than work, and the next open ticket by its hashed
identifier so there is no ambiguity about which item is meant. UNCONFIRMED is
reported separately and never drives a refusal, because a harvested instruction
whose state is unknown is not open work -- conflating the 2 made the store report
306 open items on its first harvest when 36 was the honest figure.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
STATE = pathlib.Path.home() / ".claude" / ".ticket_queue"


def head() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        return 0

    store_path = REPO / "bench" / "tickets" / "tickets.jsonl"
    if not store_path.is_file():
        return 0                      # the store is not built yet; say nothing

    sys.path.insert(0, str(REPO))
    try:
        from bench.ticket_store import TicketStore
        store = TicketStore(store_path)
    except Exception as exc:                       # noqa: BLE001
        print(f"[ticket-gate] store unreadable ({type(exc).__name__}: {exc}); "
              f"not refusing. Repair bench/ticket_store.py before relying on it.",
              file=sys.stderr)
        return 0

    open_t = store.open_tickets()
    unconf = store.unconfirmed()
    settled = store.settled()
    if not open_t:
        return 0

    # ★ THE ONE-SHOT ESCAPE IS GONE, 2026-10-24, ON HIS RULING. It read
    # `if marker == HEAD: return 0  # already prodded at this commit`, so the gate
    # refused once and then PERMITTED every later stop. He asked how it was
    # possible to quit the list; that line is the whole answer. Over a session of
    # n stop attempts it blocked 1 and permitted n-1, which at 10 attempts is 90%
    # permitted, and on 2026-10-20 at 03:26 it is exactly what let the session end
    # with 60 open items and a finished panel round unread.
    #
    # HIS RULING, and it is also his DEFINITION of a blocker: *"If a blocker is a
    # true blocker, that would mean that no other work could proceed until that
    # blocker was cleared. Is that not what a 'blocker' is? If it doesn't block
    # work from continuing and can be addressed without detriment at the end of a
    # task list, then record it and present it clearly once all other tasks that
    # can be completed are completed. The master task list should continue to
    # execute until completion, as we originally agreed, but not blindly."*
    #
    # SO THE GATE NOW TURNS ON WHETHER WORK CAN PROCEED, not on how often it has
    # spoken. It refuses while anything is WORKABLE; it permits and PRESENTS when
    # only deferred items remain; and it permits and ESCALATES when a true blocker
    # is recorded -- which `declare_blocker` will not let you record while any
    # other ticket can still be worked.
    #
    # IT STILL CANNOT TRAP A SESSION. `sys.exit(0)` on any exception is unchanged,
    # and a stop is always available by deferring the item with a written reason
    # or by clearing it -- both of which leave a record, which is the point. What
    # is no longer available is a SILENT stop with workable items on the list.
    workable = store.workable()
    deferred = store.deferred_tickets()
    blocked = store.blockers()

    # ★ A PAUSE HE HAS ORDERED IS NOT A STOP THIS GATE MAY REFUSE, added
    # 2026-10-24 within an hour of the refusal rule itself, because the gate
    # caught the gap the moment it was armed: he had just written *"do not resume
    # the master task list until I tell you to do so"* and the gate refused the
    # stop anyway. Its 3 states -- workable, deferred, blocked -- had no room for
    # "the founder has paused this", so the mechanism was overruling the person it
    # exists to serve.
    #
    # THIS IS NOT AN ESCAPE HATCH, and it is shaped so it cannot become one. The
    # file must carry HIS VERBATIM WORDS and the date, the gate PRINTS them on
    # every pass so no use of it is silent, and nothing but his explicit
    # instruction removes it -- no timeout, no commit, no turn boundary. A pause
    # with no quoted instruction in it is ignored.
    pause = STATE / "paused_by_founder.json"
    if pause.is_file():
        try:
            info = json.loads(pause.read_text(encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            info = {}
        words = str(info.get("verbatim") or "").strip()
        if len(words) >= 40:
            print(f"[ticket-gate] THE LIST IS PAUSED ON HIS INSTRUCTION, so this "
                  f"gate stands down.\n"
                  f"  Paused {info.get('paused_at', 'at an unrecorded time')}: "
                  f"\"{words[:300]}\"\n"
                  f"  {len(workable)} workable, {len(deferred)} deferred, "
                  f"{len(blocked)} blocker(s) are waiting and NONE is lost.\n"
                  f"  Resuming takes his explicit word; delete\n"
                  f"    {pause}\n"
                  f"  only when he gives it.", file=sys.stderr)
            return 0
        print(f"[ticket-gate] a pause file exists at {pause} but carries no quoted "
              f"instruction of his, so it is IGNORED. A pause is his word or it is "
              f"nothing.", file=sys.stderr)

    # ★ `wr` IS DEFERRED WORK, NOT A QUESTION, SO IT NEVER BECOMES 'NEXT OPEN'
    # (2026-10-20). His instruction: "wr is a valid section in the Bugzilla
    # registry, and you should use it to track all remaining outstanding work,
    # and refer back to this before risking constantly referring back to me and
    # requesting my verdict". A wr ticket is settled work whose execution is
    # deferred behind other work; surfacing it as the next thing needing
    # resolution is exactly how R1 was put back to him for 66 days. It is still
    # COUNTED and still listed, so it cannot be lost -- it simply does not prod.
    # ── A TRUE BLOCKER: permit the stop and escalate, because by his definition
    # nothing else can proceed and it is his attention that is needed.
    if blocked and not workable:
        print("[ticket-gate] A TRUE BLOCKER IS RECORDED AND NOTHING ELSE CAN "
              "PROCEED.\n"
              "  This is the one case his ruling of 2026-10-24 says should reach "
              "him:\n" +
              "".join(f"    {b.tid} [{b.kind}] {b.title[:110]}\n"
                      f"      BLOCKS: {b.blocker[:200]}\n" for b in blocked) +
              f"  {len(deferred)} item(s) are deferred to the end of the list and "
              f"are listed below.\n" +
              "".join(f"    {d.tid} [{d.kind}] {d.title[:100]}\n" for d in deferred),
              file=sys.stderr)
        return 0

    # ── NOTHING WORKABLE, ONLY DEFERRED WORK: permit the stop and PRESENT it,
    # which is exactly what he asked for -- "record it and present it clearly once
    # all other tasks that can be completed are completed".
    if not workable:
        if deferred:
            print(f"[ticket-gate] ALL WORKABLE ITEMS ARE DONE. "
                  f"{len(deferred)} deferred item(s) remain, presented here as "
                  f"his ruling of 2026-10-24 requires:\n" +
                  "".join(f"    {d.tid} [{d.kind}] {d.title[:110]}\n"
                          f"      DEFERRED {d.deferred}: {d.deferred_reason[:180]}\n"
                          for d in deferred),
                  file=sys.stderr)
        return 0

    # ── WORK REMAINS: refuse, and keep refusing. `wr` still does not PROD, but a
    # wr ticket is workable, so it keeps the gate closed; it simply is not named
    # as NEXT OPEN, which is how R1 was put back to him for 66 days.
    prodding = [t for t in workable if t.kind != "wr"] or workable
    nxt = sorted(prodding, key=lambda t: (t.ruled or "9999", t.task_ref or "zz", t.tid))[0]
    by_kind = {}
    for t in open_t:
        by_kind[t.kind] = by_kind.get(t.kind, 0) + 1

    print(
        f"[ticket-gate] {len(open_t)} OPEN ticket(s) remain "
        # `pr` WAS NEVER A KIND. This line reported `by_kind.get('pr')` from the
        # day it was written, so the second figure has always been 0 whatever the
        # store held -- the kind is `pf`, renamed before the harvester shipped
        # precisely because `pr` collides with his panel-review command. A counter
        # that reads a key nothing writes is indistinguishable from a real zero,
        # which is the defect class this project keeps finding. Corrected
        # 2026-10-19, and `qs` added on his instruction of the same day.
        f"(fr {by_kind.get('fr', 0)}, pf {by_kind.get('pf', 0)}, "
        # `wr` IS NO LONGER CALLED "deferred" HERE. Until 2026-10-24 deferral was
        # inferred from the KIND, so this line said "wr 34 deferred" while the
        # count below said "0 deferred" -- 2 words for 2 different things in one
        # message. Deferral is now the `deferred` FIELD, and `wr` means only that
        # the item does not PROD.
        f"qs {by_kind.get('qs', 0)}, wr {by_kind.get('wr', 0)} non-prodding); "
        f"{len(unconf)} UNCONFIRMED awaiting triage; {len(settled)} settled.\n"
        f"  HIS INSTRUCTION, 2026-10-17: do not stop until every task is marked "
        f"complete or resolved in the ticket store.\n"
        f"  NEXT OPEN: {nxt.tid} [{nxt.kind}] "
        f"{('task ' + nxt.task_ref + ' ') if nxt.task_ref else ''}"
        f"{('ruled ' + nxt.ruled + ' ') if nxt.ruled else ''}\n"
        f"    {nxt.title[:150]}\n"
        f"  To resolve one, CLOSE it with the verification that settled it:\n"
        f"    python3 -c \"import sys; sys.path.insert(0,'.'); "
        f"from bench.ticket_store import TicketStore; s=TicketStore(); "
        f"s.close('{nxt.tid}','<what was done>','<the test or execution that proves it>')\"\n"
        f"  CLOSED is tool-only: an assertion is refused, a verification is required.\n"
        f"  UNCONFIRMED items need TRIAGE, not work -- establish the state, then "
        f"close or open them. They never drive this refusal.\n"
        f"  {len(workable)} workable, {len(deferred)} deferred, {len(blocked)} "
        f"declared blocker(s).\n"
        f"  ★ THIS GATE NO LONGER YIELDS AFTER ONE REFUSAL (his ruling "
        f"2026-10-24). There are 2 ways to a stop, and both leave a record:\n"
        f"    1. CLOSE the item with its verification, as above.\n"
        f"    2. DEFER it with a written reason, if it can wait without detriment:\n"
        f"       s.defer('{nxt.tid}','<why it can wait>','<date -Iseconds>')\n"
        f"    A TRUE BLOCKER -- one that stops ALL other work -- is declared with\n"
        f"    s.declare_blocker(tid, reason), and that call REFUSES while any\n"
        f"    other ticket is workable, because by his definition it would not\n"
        f"    then be a blocker.\n",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                               # noqa: BLE001
        sys.exit(0)
