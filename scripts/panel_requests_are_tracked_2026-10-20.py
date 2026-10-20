#!/usr/bin/env python3
"""Every request of his for a panel review becomes a tracked ticket.

HIS FINDING, 2026-10-20: "none of the requested panel review tasks appear to be
on your master task list, or for some reason, you ignored them and failed to do
them anyway. This should not be possible."

MEASURED BEFORE BUILDING ANYTHING. Of his 747 annotations, 76 request a panel
review. 37 are in the ticket store, 3 are on the master task list, and 39 --
51.3158%, Wilson [40.2887%, 62.2163%] -- are reached by NOTHING.

WHY THEY WERE MISSED, and it is one cause. `scripts/harvest_tickets_2026-10-17.py`
harvests an annotation when it carries an explicit marker: fr, pf, qs or wr. Most
of his panel requests carry no marker, because he writes "ask the free panel" in
the body of an answer rather than filing a ticket. A request is an instruction
whether or not he marked it, so marker-gated harvesting cannot see it.

WHAT THIS DOES. It detects the request by its own words, checks whether anything
already covers it, and files the remainder as `wr` -- work remaining -- so the
Stop gate counts them and they can never silently go unrun again. It files
nothing it cannot anchor, and an anchor is the annotation's own file and line,
so a second run of this script produces no duplicates.

Run to measure:  python3 scripts/panel_requests_are_tracked_2026-10-20.py
Run to file:     python3 scripts/panel_requests_are_tracked_2026-10-20.py --file
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: HIS OWN PHRASINGS, collected from the annotations rather than imagined. Each
#: was present in at least 1 real request on 2026-10-20.
PANEL = re.compile(
    r"(ask|put\s+it\s+to|run|with)\s+(the\s+)?(free\s+)?panel"
    r"|(free\s+)?panel\s+review"
    r"|check\s+(your\s+work|it|the\s+fix)\s+with\s+the\s+(free\s+)?panel"
    r"|discuss\s+your\s+fix\s+with",
    re.I,
)


def _norm(s: str) -> str:
    return " ".join((s or "").split())


def _reader():
    spec = importlib.util.spec_from_file_location("_rfr", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rfr"] = mod
    spec.loader.exec_module(mod)
    return mod


def requests() -> list[dict]:
    """His annotations that ask for a panel, each with a stable anchor."""
    r = _reader()
    out = []
    for a in r.annotations():
        if PANEL.search(a["text"]):
            out.append({
                "anchor": f"{pathlib.Path(str(a['file'])).name}#{a['line_index']}",
                "text": a["text"],
                "date": a.get("date", ""),
                "file": pathlib.Path(str(a["file"])).name,
            })
    return out


def uncovered(reqs: list[dict], store) -> list[dict]:
    """Those nothing already tracks. A ticket counts only on a STRONG match.

    A prefix match was tried first and rejected: it called an item covered when
    only its opening clause matched, which is how 73 of 76 looked missing on a
    first pass that was too strict and would have looked covered on one that was
    too loose. The anchor is exact, so an anchored ticket is decisive; the text
    ratio is the fallback for tickets filed before anchors existed.
    """
    anchored = {t.anchor for t in store.all() if getattr(t, "anchor", "")}
    texts = [_norm(t.verbatim)[:160] for t in store.all()]
    tl = _norm(LIST.read_text(encoding="utf-8"))
    out = []
    for q in reqs:
        if q["anchor"] in anchored:
            continue
        probe = _norm(q["text"])
        if probe[:45] in tl:
            continue
        if any(difflib.SequenceMatcher(None, probe[:160], x).ratio() >= 0.85
               for x in texts):
            continue
        out.append(q)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", action="store_true",
                    help="file every uncovered request as a wr ticket")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore          # noqa: PLC0415
    store = TicketStore()

    reqs = requests()
    miss = uncovered(reqs, store)
    print(f"his annotations requesting a panel : {len(reqs)}")
    print(f"reached by nothing                 : {len(miss)}")
    if reqs:
        from statsmodels.stats.proportion import proportion_confint as ci  # noqa: PLC0415
        lo, hi = ci(len(miss), len(reqs), alpha=0.05, method="wilson")
        lo2, hi2 = ci(len(miss), len(reqs), alpha=0.05, method="beta")
        print(f"  {100*len(miss)/len(reqs):.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"
              f"  Clopper-Pearson [{100*lo2:.4f}%, {100*hi2:.4f}%]")

    if args.file:
        made = 0
        for q in miss:
            t, outcome = store.propose(
                kind="wr",
                title=f"PANEL REQUESTED: {_norm(q['text'])[:110]}",
                verbatim=q["text"],
                source=f"Responses/{q['file']}",
                source_ref=q["anchor"],
                anchor=q["anchor"],
                ruled=q["date"] or "",
            )
            made += outcome == "created"
        print(f"\nfiled as wr: {made}")
        return 0
    for q in miss[:12]:
        print(f"  {q['anchor']:>52s}  {_norm(q['text'])[:78]}")
    if len(miss) > 12:
        print(f"  ... and {len(miss)-12} more")
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
