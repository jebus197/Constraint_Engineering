#!/usr/bin/env python3
"""Does one shared code identifier let a settled ticket hide a new proposal?

FOUND BY THE REGISTER REFUSING MY OWN WORK, 2026-10-17. A genuinely new feature
request -- Gemini Web's proposal of namespace paths such as `/issues/open` --
was NOT CREATED. `propose` returned `subject-settled` and handed back the
ticket for the register's new command-line entry point, which had been closed
minutes earlier. The two items share exactly 1 code identifier, `area_of`, and
nothing else: not the fault, not the repair, not the hash.

WHY THAT IS THE DANGEROUS DIRECTION, in the code's own words at
`bench/ticket_store.py`: "Over-merging hides the open item behind the closed
one, which is worse than the rediscovery this store exists to prevent." The
comment goes on: "Two entries about the same mechanism are still 2 entries."

THAT IS THE INTENT. THE BEHAVIOUR DIFFERS, and conditionally: the protection
runs through `_distinct`, which can only answer "these are different items"
when the CALLER SUPPLIES a `task_ref` or an `anchor`. A proposal arriving with
neither -- which is every proposal raised from a document rather than from the
task list -- gets no protection at all, and one shared identifier decides.

HIS DUPLICATE TEST, verbatim, 2026-10-17: *"if it's the same issue and the
fix/proposed feature etc is the same (and now also if its hash value is the
same), then it can/should be marked as a dupe."* Three elements. A shared code
identifier satisfies none of them on its own.

This measures the exposure 4 ways before anything is changed:

  1. how many tickets have no task_ref and no anchor, so are unprotected;
  2. how many distinct subjects already have a settled ticket, so could decide;
  3. how many EXISTING tickets would have been blocked had they been raised
     without a task_ref, which is the counterfactual that matters;
  4. whether requiring corroboration from the word layer -- his "same fix" --
     would change any decision the archive actually recorded.

Usage: python3 scripts/can_a_shared_mechanism_hide_a_new_item_2026-10-17.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def _say(label, p):
    if p is None:
        print(f"  {label}: no denominator")
        return
    print(f"  {label}: {p['k']} of {p['n']} = {p['pct']:.4f}%  "
          f"Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"CP [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%] scipy agrees {p['agrees']}")


def _parse(argv=None) -> None:
    """A REAL PARSER, so an unknown flag FAILS instead of being ignored.

    A hand-rolled `if "--help" in sys.argv` answers help and accepts anything
    else silently, which is this project's "118-day no-op" shape. This
    measurement takes no options, so saying so explicitly is the whole of it.
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.parse_args(argv)


def main() -> int:
    _parse()
    from bench.ticket_store import TicketStore, TERMINAL

    store = TicketStore()
    store.load()
    tickets = store.all()
    print(f"  register: {len(tickets)} tickets\n")

    print("1. HOW MANY TICKETS CARRY NO PROTECTION AT ALL")
    unprotected = [t for t in tickets if not t.task_ref and not t.anchor]
    _say("no task_ref and no anchor", _proportion(len(unprotected), len(tickets)))
    print("   Those are the ones `_distinct` cannot defend, because it has")
    print("   nothing to compare. A proposal raised from a document rather")
    print("   than from the task list arrives in exactly this state.\n")

    print("2. HOW MANY SUBJECTS ALREADY HAVE A SETTLED TICKET")
    subs = store.subjects()
    deciding = [s for s in subs if store.settled_on_subject(s)]
    _say("subjects that would decide", _proportion(len(deciding), len(subs)))
    print("   Any new proposal naming one of these, without a task_ref, is")
    print("   handed the settled ticket instead of being raised.\n")

    print("3. THE COUNTERFACTUAL: EXISTING TICKETS THAT WOULD HAVE BEEN BLOCKED")
    print("   For each ticket, ask: if it had been proposed WITHOUT its")
    print("   task_ref, would a settled ticket on one of its subjects have")
    print("   absorbed it? Only tickets with subjects can be tested.")
    with_subjects = [t for t in tickets if t.subjects]
    blocked, blocked_by_different = [], []
    for t in with_subjects:
        for sub in t.subjects:
            settled = [x for x in store.settled_on_subject(sub)
                       if x.tid != t.tid]
            if not settled:
                continue
            other = settled[0]
            blocked.append(t)
            # Would his 3-element test have called them the same? Compare the
            # texts through the register's own word layer rather than by eye.
            same_words = any(
                x.tid == other.tid
                for x in store.similar_by_words(t.verbatim or t.title or ""))
            same_hash = (t.nid == other.nid)
            if not (same_words or same_hash):
                blocked_by_different.append((t.tid, other.tid, sub))
            break
    _say("would have been absorbed", _proportion(len(blocked), len(with_subjects)))
    _say("absorbed by a DIFFERENT item", 
         _proportion(len(blocked_by_different), len(with_subjects)))
    print("   The second figure is the defect rate: a ticket absorbed by a")
    print("   settled ticket that shares neither its words nor its hash is a")
    print("   DISTINCT ITEM being hidden, which is the failure the code's own")
    print("   comment names as worse than rediscovery.")
    for a, b, sub in blocked_by_different[:8]:
        print(f"     {a} would be hidden behind {b} over subject {sub!r}")
    # A CAPPED LISTING STATES ITS REMAINDER -- 2026-10-28. A list cut to N under a heading that reads as complete is a silent falsehood.
    _withheld = max(0, len(blocked_by_different) - 8)
    if _withheld:
        print(f"      ... and {_withheld} more not shown "
              f"(of {len(blocked_by_different)} total)")

    print("\n4. WOULD REQUIRING CORROBORATION CHANGE A RECORDED DECISION?")
    print("   The proposed repair: a subject match may decide ONLY if the word")
    print("   layer or the normalised hash agrees -- his 'same issue AND same")
    print("   fix AND same hash'. Otherwise it SURFACES and a separate ticket")
    print("   is created, exactly as the word layer already behaves.")
    would_change = len(blocked_by_different)
    _say("decisions the repair would reverse",
         _proportion(would_change, max(len(blocked), 1)))
    print("   A reversal here means a ticket gets RAISED that is currently")
    print("   dropped. No existing ticket is removed or re-merged, so the")
    print("   change is additive in the strict sense: it can only increase")
    print("   what the register holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
