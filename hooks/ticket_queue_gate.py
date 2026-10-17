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

    h = head()
    STATE.mkdir(parents=True, exist_ok=True)
    marker = STATE / "last_refusal"
    if h and marker.is_file() and marker.read_text(encoding="utf-8").strip() == h:
        return 0                      # already prodded at this commit
    if h:
        marker.write_text(h, encoding="utf-8")

    nxt = sorted(open_t, key=lambda t: (t.ruled or "9999", t.task_ref or "zz", t.tid))[0]
    by_kind = {}
    for t in open_t:
        by_kind[t.kind] = by_kind.get(t.kind, 0) + 1

    print(
        f"[ticket-gate] {len(open_t)} OPEN ticket(s) remain "
        f"(fr {by_kind.get('fr', 0)}, pr {by_kind.get('pr', 0)}); "
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
        f"  This gate refuses at most once per commit, so it cannot loop. If the "
        f"remaining work is genuinely blocked, say so in one line and continue.\n",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                               # noqa: BLE001
        sys.exit(0)
