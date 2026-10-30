#!/usr/bin/env python3
"""A kind change RE-CLASSIFIES an annotation; it does not raise a second one.

THE DEFECT, OBSERVED 2026-10-30 AND SELF-INFLICTED. His ruling of that day
replaced the harvester's unconditional `pf` default with 2 rules -- `qs` where
the annotation ends in a question mark, `ds` otherwise. `tid_of` digests the
KIND, by his own 2026-10-19 ruling, so re-harvesting minted a SECOND ticket for
every re-classified annotation instead of moving the first. Measured
immediately after the change: 95 of 2,308 anchors carried more than 1 kind, and
190 rows across those anchors were still open, so the Stop gate would prod
about the same sentence twice.

That is precisely the over-reporting he complained of the day before, verbatim:
*"But is it earning it's keep?"* and *"How do we avoid it?"* -- so a change made
to answer his complaint created 95 more instances of it.

THE REPAIR, AND WHY IT IS NOT A DELETION. The anchor is the identity of an
annotation: file, text digest and ordinal. 2 rows sharing an anchor are 2
classifications of 1 sentence, and exactly 1 of them is current. The stale one
is DEPRECATED through the store's own `deprecate`, which records
`superseded_by` and the evidence, so the row survives and leaves the queue.
Nothing is removed and no identity is rewritten.

WHICH ROW WINS IS DERIVED, NOT CHOSEN. The current kind is recomputed from the
annotation's own text by the live reader and the live harvester -- his trailing
marker if he wrote one, else his default rule -- so this script cannot prefer a
kind by fiat. A row whose kind is the recomputed one survives; the others are
deprecated in its favour. An anchor whose rows do not include the recomputed
kind is REPORTED and left alone, because that is a case this reasoning does not
cover.

AN EXPLICIT MARKER OF HIS IS NEVER OVERRIDDEN. Where his text carries a
trailing marker, that marker IS the recomputed kind, so an annotation he marked
`pf` keeps its `pf` row and any default-derived sibling is the one deprecated.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import pathlib
import subprocess
import sys

from statsmodels.stats.proportion import proportion_confint
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wilson(k: int, n: int) -> tuple[tuple[float, float], tuple[float, float]]:
    if n == 0:
        return (float("nan"),) * 2, (float("nan"),) * 2
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p, d = k / n, 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (float(sm[0]), float(sm[1])), ((c - h) / d, (c + h) / d)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the deprecations; omit for a dry run")
    a = ap.parse_args()

    reader = _load(REPO / "scripts" / "read_founder_responses_2026-10-11.py", "rdr")
    harv = _load(REPO / "scripts" / "harvest_tickets_2026-10-17.py", "harv")
    from bench.ticket_store import TicketStore

    # `LIVE` is the frozenset of live STATUSES, not a path; the default store
    # path is the one `TicketStore()` already resolves.
    store = TicketStore()
    rows = store.all()
    by_anchor: dict[str, list] = collections.defaultdict(list)
    for t in rows:
        if getattr(t, "anchor", ""):
            by_anchor[t.anchor].append(t)

    # ★ HIS MARKER MAY BE OWN-LINE, AND AN OWN-LINE MARKER IS NOT IN THE
    # VERBATIM. Corrected 2026-10-30 after the first version of this script
    # recomputed R1's annotation as `ds` when he had marked it `wr`: the
    # reader attaches an own-line marker to the annotation ABOVE it, so the
    # marker never appears in the annotation's own text. Deriving the kind
    # from the text alone therefore silently overrides an explicit marker of
    # his, which is the one thing this script must never do. The reader's
    # marker field is consulted first and the text only as a fallback.
    by_text: dict[str, str] = {}
    try:
        out = subprocess.run(
            [sys.executable,
             str(REPO / "scripts" / "read_founder_responses_2026-10-11.py"),
             "--since", "2026-01-01", "--json"],
            capture_output=True, text=True, cwd=str(REPO), check=True)
        for v in json.loads(out.stdout)["annotations"]:
            mk = str(v.get("marker") or "").split(",")[0].strip().lower()
            if mk:
                # WHITESPACE-NORMALISED JOIN KEY. A stored verbatim has been
                # normalised on the way in -- 276 characters in the reader
                # against 273 in the store for the 1 annotation this mattered
                # for -- so an exact-string lookup silently misses and the
                # marker falls back to a guess.
                by_text[" ".join(v["text"].split())] = mk
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"  reader unavailable ({exc}); falling back to text only")

    def current_kind(text: str) -> str:
        explicit = by_text.get(" ".join(str(text or "").split()))
        if explicit:
            return explicit
        mk = reader._marker_of(text)
        first = mk.split(",")[0].strip().lower() if mk else ""
        return first or harv._unmarked_kind(text)

    plan, unmatched = [], []
    for anchor, ts in by_anchor.items():
        kinds = {t.kind for t in ts}
        if len(kinds) < 2:
            continue
        want = current_kind(ts[0].verbatim)
        winners = [t for t in ts if t.kind == want]
        if not winners:
            unmatched.append({"anchor": anchor, "kinds": sorted(kinds),
                              "recomputed": want})
            continue
        win = winners[0]
        for t in ts:
            if t.tid == win.tid or t.kind == want:
                continue
            if t.status in ("CLOSED", "REJECTED", "DEPRECATED"):
                continue
            plan.append({"stale": t.tid, "stale_kind": t.kind,
                         "winner": win.tid, "winner_kind": win.kind,
                         "anchor": anchor, "status": t.status})

    n_anchor = len(by_anchor)
    multi = sum(1 for v in by_anchor.values() if len({t.kind for t in v}) > 1)
    sm, cf = wilson(multi, n_anchor)
    print(f"anchors: {n_anchor}; carrying >1 kind: {multi} "
          f"({multi / n_anchor:.6f}), Wilson statsmodels "
          f"[{sm[0]:.6f}, {sm[1]:.6f}], closed form [{cf[0]:.6f}, {cf[1]:.6f}]")
    print(f"deprecations planned: {len(plan)}")
    print(f"anchors whose rows do not include the recomputed kind: "
          f"{len(unmatched)} (reported, untouched)")
    print("by stale kind:",
          dict(collections.Counter(p["stale_kind"] for p in plan)))

    if a.apply:
        done = 0
        for p in plan:
            ev = (f"RE-CLASSIFICATION, not a second finding. Anchor "
                  f"{p['anchor']} is 1 annotation of his. Its kind was "
                  f"recomputed from his own text by the live reader and "
                  f"harvester as `{p['winner_kind']}` under his ruling of "
                  f"2026-10-30; this row carries the superseded kind "
                  f"`{p['stale_kind']}`, which the unconditional `pf` default "
                  f"produced. Producer: "
                  f"scripts/a_reclassification_is_not_a_second_ticket_2026-10-30.py")
            try:
                store.deprecate(p["stale"], p["winner"], ev)
                done += 1
            except (KeyError, ValueError) as exc:
                print(f"  refused {p['stale']}: {exc}")
        print(f"deprecated: {done} of {len(plan)}")
    else:
        print("DRY RUN -- pass --apply to write")
    print(json.dumps({"planned": len(plan), "unmatched": len(unmatched),
                      "multi_kind_anchors": multi, "anchors": n_anchor},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
