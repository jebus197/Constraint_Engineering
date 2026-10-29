#!/usr/bin/env python3
"""The identityless count CAN be walked back, and B49's claim that it cannot is
withdrawn with the measurement that replaces it.

WHAT B49 TOLD HIM, and it is quoted here so the correction cannot drift: the
count of tickets carrying neither a `task_ref` nor an `anchor` *"cannot be
brought back down"*, evidenced by raising a bare ticket (320 -> 321) and then
migrating it (321 -> 322), because a migration leaves the old record behind as a
MERGED marker which is itself without an identity.

THAT MEASUREMENT REPRODUCES AND THE INFERENCE FROM IT DOES NOT. It measures the
only 2 operations that existed. `TicketStore.adopt_identity`, built on his ruling
of 2026-10-29, fills the missing field in place without re-keying the record, and
the count falls by 1 per adoption.

WHY THE 3 REAL OFFENDERS WERE STILL NOT WALKED BACK. All 3 are refused, and the
refusal is correct rather than a limitation: each already has a
correctly-identified twin at the digest its anchor implies, so adopting that
anchor would make 2 tickets answer to 1 identity. That is reported below against
the live register, read-only.

READ-ONLY ON THE LIVE REGISTER. Every mutation happens in a temporary copy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore, tid_of  # noqa: E402

CUT = "2026-10-28T02:10:18"
VERBATIM = "a bare proposal raised through propose instead of propose_from_chat"
ANCHOR = "chat#2026-10-29T16:00:00#deadbeef"
VERIF = "producer an_identity_can_now_be_walked_back_2026-10-29.py"


def identityless(store: TicketStore) -> int:
    return len([t for t in store.all() if not t.task_ref and not t.anchor])


def contrast() -> dict[str, int]:
    """Migration against adoption, both EXECUTED on a scratch store."""
    out: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as d:
        s = TicketStore(path=pathlib.Path(d) / "m.jsonl")
        out["empty"] = identityless(s)
        t, _ = s.propose("pf", "bare", VERBATIM, source="chat",
                         created="2026-10-29T16:00:00")
        out["after_raising_bare"] = identityless(s)
        s.migrate_identity(t.tid, tid_of("pf", VERBATIM, "", "other#1"), VERIF)
        out["after_migrating"] = identityless(s)
    with tempfile.TemporaryDirectory() as d:
        s = TicketStore(path=pathlib.Path(d) / "a.jsonl")
        t, _ = s.propose("pf", "bare", VERBATIM, source="chat",
                         created="2026-10-29T16:00:00")
        out["after_raising_bare_again"] = identityless(s)
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        out["after_adopting"] = identityless(s)
        reloaded = TicketStore(path=s.path)
        out["after_reload"] = identityless(reloaded)
    return out


def live_offenders() -> list[dict[str, object]]:
    """What happens if adoption is attempted on the 3 real breaches. Read-only."""
    live = TicketStore()
    live.load()
    rows: list[dict[str, object]] = []
    targets = [t for t in live.all()
               if not t.task_ref and not t.anchor and (t.created or "") > CUT]
    for t in targets:
        digest = hashlib.sha256(str(t.verbatim).encode()).hexdigest()[:8]
        anchor = f"chat#{t.created}#{digest}"
        implied = tid_of(t.kind, t.verbatim, "", anchor)
        held = live.get(implied)
        rows.append({
            "tid": f"{t.kind}:{t.tid}",
            "status": t.status,
            "duplicate_of": t.duplicate_of,
            "implied": implied,
            "implied_is_held_by": f"{held.kind}:{held.tid}" if held else None,
            "adoption": "REFUSED: the implied identity is already held"
                        if held is not None and held.tid != t.tid else "would succeed",
        })
    return rows


def collapse_damage() -> list[dict[str, object]]:
    """The live consequence of `tid_of` admitting 1 ticket per kind+task_ref.

    THE FIRST VERSION OF THIS FUNCTION MEASURED THE WRONG THING and is corrected
    here rather than quietly replaced. It asked `by_task_ref` for every reference
    holding more than 1 ticket of a kind, and returned 30 pairs. **None of them is
    a collapse.** `migrate_identity` copies the record with `asdict`, so the moved
    record and the MERGED marker both carry the same `task_ref`, and every pair it
    found was a migration. Worse, the predicate CANNOT detect the thing it was
    named for: a genuine collapse OVERWRITES the loser in the index, so it leaves
    no pair to find. A detector that returns a number it cannot have measured is
    the flattering-measure failure this project has recorded 3 times.

    THE PREDICATE THAT CAN SEE IT, AND THE SECOND THING IT HAD TO LEARN. The
    store is append-only and the index keeps only the last record per tid, so an
    overwritten record still exists ON DISK. Keying on a differing `verbatim`
    alone still over-reports, because a task-list entry is REWORDED every time an
    addendum is written and `tid_of` deliberately excludes the text where a
    reference exists -- that is the documented design, not a defect, and it
    accounted for 6 of the 7 rows the second version returned. The
    discriminator is a differing TITLE: a restatement of 1 item keeps its title,
    and 2 distinct faults filed against 1 reference do not. Both counts are
    reported, because conflating them is how the second version flattered itself.
    """
    live = TicketStore()
    rows = []
    if not live.path.exists():
        return rows
    by_tid: dict[str, list[dict]] = {}
    for line in live.path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        by_tid.setdefault(d["tid"], []).append(d)
    for tid, records in by_tid.items():
        if len(records) < 2:
            continue
        if any("identity migrated to" in (r.get("resolution") or "") for r in records):
            continue
        texts = {" ".join((r.get("verbatim") or "").split()) for r in records}
        titles = [r.get("title", "") for r in records]
        distinct_titles = {" ".join(t.split()) for t in titles}
        if len(texts) < 2 and len(distinct_titles) < 2:
            continue
        #: WORD OVERLAP BETWEEN THE TITLES, reported rather than thresholded.
        #: A reworded title shares most of its vocabulary with the original; 2
        #: distinct faults share almost none. No cutoff is imposed, because
        #: picking one here would be the undocumented numeric gate that the
        #: 2026-05-18 pre-registration exists to forbid. The reader sees the
        #: figure and decides.
        overlap = None
        if len(distinct_titles) > 1:
            sets = [set(t.lower().split()) for t in distinct_titles]
            pairs = [(len(a & b) / len(a | b)) for i, a in enumerate(sets)
                     for b in sets[i + 1:] if (a | b)]
            overlap = min(pairs) if pairs else None
        rows.append({
            "tid": tid,
            "kind": records[-1].get("kind"),
            "task_ref": records[-1].get("task_ref"),
            "distinct_texts": len(texts),
            "distinct_titles": len(distinct_titles),
            "collapse": len(distinct_titles) > 1,
            "title_word_overlap": overlap,
            "titles": sorted(distinct_titles),
            "surviving_title": " ".join(titles[-1].split()),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    c = contrast()
    offenders = live_offenders()
    collapses = collapse_damage()
    live = TicketStore(); live.load()
    report = {
        "contrast": c,
        "migration_delta": c["after_migrating"] - c["after_raising_bare"],
        "adoption_delta": c["after_adopting"] - c["after_raising_bare_again"],
        "live_total": len(live.all()),
        "live_identityless": identityless(live),
        "offenders": offenders,
        "kind_plus_ref_collapses": collapses,
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("== can the identityless count be walked back? ==")
    print("   EXECUTED on scratch stores, 1 bare ticket each:")
    print(f"     empty store                     {c['empty']}")
    print(f"     after raising 1 bare ticket     {c['after_raising_bare']}")
    print(f"     after migrate_identity          {c['after_migrating']}   "
          f"delta {report['migration_delta']:+d}")
    print(f"     after raising 1 bare ticket     {c['after_raising_bare_again']}")
    print(f"     after adopt_identity            {c['after_adopting']}   "
          f"delta {report['adoption_delta']:+d}")
    print(f"     after reloading from disk       {c['after_reload']}")
    print()
    print(f"   LIVE REGISTER (read-only): {report['live_identityless']} of "
          f"{report['live_total']} tickets carry no identity.")
    print(f"   the {len(offenders)} breach(es) since {CUT}:")
    for r in offenders:
        print(f"     {r['tid']}  {r['status']}")
        print(f"        implied {r['implied']} held by {r['implied_is_held_by']}")
        print(f"        -> {r['adoption']}")
    print()
    reworded = [r for r in collapses if not r["collapse"]]
    genuine = [r for r in collapses if r["collapse"]]
    print(f"   1 identity holding 2 or more RECORDS, from the append-only log:")
    print(f"     reworded, same title  {len(reworded):>3}  "
          f"BY DESIGN: tid_of excludes the text where a reference exists")
    print(f"     DIFFERENT titles      {len(genuine):>3}  "
          f"1 identity carried 2 titles; the loser was overwritten")
    print("     Word overlap separates a REWORDED title from a DIFFERENT fault.")
    print("     It is reported, not thresholded: an undocumented numeric cut is")
    print("     exactly what the 2026-05-18 pre-registration forbids.")
    print("     ★ THIS FIGURE BOUNDS EXPOSURE AND DOES NOT COUNT COLLAPSES, and")
    print("       the reason is documented in tid_of's own docstring: an addendum")
    print("       recording a NEIGHBOUR entry as built sits ABOVE the entry in a")
    print("       shared block and changes the text the title extractor reads, so")
    print("       a LOW overlap is produced by a cause that is not a collapse.")
    print("       Separating the 2 requires reading each pair. Exactly 1 case is")
    print("       confirmed by reading: pf:2835f264ae18, which carries entry")
    print("       B50's reference and a different fault's title.")
    for r in sorted(genuine, key=lambda x: (x["title_word_overlap"] or 0)):
        ov = r["title_word_overlap"]
        print(f"     {r['kind']}:{r['tid']}  task_ref={r['task_ref']!r}  "
              f"title overlap {ov:.4f}" if ov is not None else
              f"     {r['kind']}:{r['tid']}  task_ref={r['task_ref']!r}")
        for t in r["titles"]:
            mark = "  <- SURVIVING" if t == r["surviving_title"] else "  <- OVERWRITTEN"
            print(f"        {t[:84]}{mark}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
