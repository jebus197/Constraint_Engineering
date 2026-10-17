#!/usr/bin/env python3
"""Move every task-list ticket onto its reference-keyed identity.

WHY. Until 2026-10-17 a ticket's identity digested the entry's TEXT as well as
its reference, so the identity moved whenever the entry was reworded -- and an
entry is reworded every time an addendum is written above it. Two consequences
were measured rather than predicted: 5 references (R10, 3.2, 6.2, B15, B20)
already carried 2 tickets each, and improving the extraction rule alone
re-minted 114 of 141 identities in a single step. A register that must be
searched before any work is proposed cannot have identities that drift.

WHAT THIS DOES. For each reference whose ticket still sits at a text-derived
identity, the record is copied to the reference-keyed identity with its status,
resolution and verification intact, and the old record is marked MERGED naming
its successor. Nothing is rewritten in place, so an identifier already cited
still resolves.

WHAT IT REFUSES TO DO. It will not touch a reference that already has a
reference-keyed ticket, it will not create one where the task list has no such
entry, and the store itself refuses any migration that would move a status or a
verbatim. Run with --dry-run first; that is the default.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from bench.ticket_store import TicketStore, tid_of, TERMINAL, REJECTED  # noqa: E402


def _harvester():
    spec = importlib.util.spec_from_file_location(
        "harvest_tickets", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["harvest_tickets"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the migration (default is a dry run)")
    ap.add_argument("--sweep-stale", action="store_true",
                    help="also merge LIVE tickets left at a superseded identity "
                         "into their reference's canonical ticket")
    a = ap.parse_args()

    H = _harvester()
    rows = {r["task_ref"]: r for r in H.from_task_list() if r.get("task_ref")}
    store = TicketStore()

    by_ref = collections.defaultdict(list)
    for t in store.all():
        if t.task_ref:
            by_ref[t.task_ref].append(t)

    plan, already, orphan, mixed = [], [], [], []
    for ref, r in sorted(rows.items()):
        want = tid_of(r["kind"], r["verbatim"], ref)
        held = by_ref.get(ref, [])
        if any(t.tid == want for t in held):
            already.append(ref)
            continue
        live = [t for t in held if t.status not in TERMINAL and t.status != REJECTED]
        settled = [t for t in held if t.status in TERMINAL or t.status == REJECTED]
        if live and settled:
            # REFUSE RATHER THAN CHOOSE. Migrating the settled one and leaving
            # the live one behind would put a CLOSED record at the reference
            # and strand open work at an identity nothing looks up -- the
            # over-merge hazard inverted. Measured 0 such references on
            # 2026-10-17, so this guard costs nothing today and is the one
            # that matters if the condition ever arises.
            mixed.append((ref, [(t.tid, t.status) for t in held]))
            continue
        src = (settled or live)
        if not src:
            orphan.append(ref)
            continue
        plan.append((ref, src[-1], want))

    print(f"references in the task list            : {len(rows)}")
    print(f"  already at a reference-keyed identity: {len(already)}")
    print(f"  to migrate                           : {len(plan)}")
    print(f"  no existing ticket at all            : {len(orphan)} {orphan[:8]}")
    print(f"  holding BOTH live and settled        : {len(mixed)}")
    if mixed:
        print("\nREFUSING: these references hold a live AND a settled ticket, so")
        print("choosing one would strand the other. Resolve them by hand first.")
        for ref, held in sorted(mixed):
            print(f"  {ref:<6} {held}")
        return 2

    if not a.apply:
        print("\n--dry-run (default). First 10 of the plan:")
        for ref, old, want in plan[:10]:
            print(f"  {ref:<6} {old.tid} [{old.status}] -> {want}")
        print("\nRe-run with --apply to write it.")
        return 0

    moved = collections.Counter()
    for ref, old, want in plan:
        store.migrate_identity(
            old.tid, want,
            "identity rule changed 2026-10-17: a reference is the whole identity; "
            "migrated by scripts/migrate_ticket_identity_to_the_reference_2026-10-17.py")
        moved[old.status] += 1
    print(f"\nmigrated {sum(moved.values())} ticket(s), by status carried across:")
    for k, v in sorted(moved.items()):
        print(f"  {k:<12} {v}")

    if a.sweep_stale:
        print(_sweep(store, rows))
    return 0


def _sweep(store: TicketStore, rows: dict) -> str:
    """Merge live tickets stranded at a superseded identity.

    A reference whose identity moved can be left with its OLD record still
    live, because only the record chosen for migration was retired. Measured
    2026-10-17: 17 such records, each duplicating its reference's canonical
    ticket AT THE SAME STATUS, 2 of them the pre-existing B15 and B20
    duplicates. Left alone they make the register over-report open work --
    46 OPEN against 31 live references -- which is the failure mode that makes
    a count untrustworthy.

    MERGED is the correct verb and the store demands a verification for it:
    these are not merely similar items but the SAME task entry, so the fault
    and the repair are identical by construction, which is the 2-element test
    the founder set for a merge.
    """
    canon = {ref: tid_of(r["kind"], r["verbatim"], ref) for ref, r in rows.items()}
    stale = []
    for t in store.all():
        if not t.task_ref:
            continue
        want = canon.get(t.task_ref)
        # ANY record away from the canonical identity, not merely a live one.
        # The first form swept only live records, which left 73 CLOSED
        # duplicates behind -- so the register reported 257 settled tickets
        # against 111 settled task entries. A register whose counts are wrong
        # is the thing it was built to replace. MERGED and DUPLICATE are
        # skipped because they ARE the retirement marker: re-merging a redirect
        # would loop.
        if (want and t.tid != want
                and t.status not in ("MERGED", "DUPLICATE")
                and t.status != REJECTED):
            stale.append((t, want))
    for t, want in stale:
        target = store.get(want)
        if target is None or target.status != t.status:
            # A status difference means these are NOT the same state of the
            # same item, so the 2-element test fails and the merge is refused.
            continue
        store.merge(t.tid, want,
                    f"same task entry {t.task_ref}: identity superseded "
                    f"2026-10-17, status {t.status} identical on both records")
    return (f"\nswept {len(stale)} record(s) away from the canonical identity "
            f"into their reference's canonical ticket")



if __name__ == "__main__":
    raise SystemExit(main())
