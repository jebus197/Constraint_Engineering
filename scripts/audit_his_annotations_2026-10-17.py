#!/usr/bin/env python3
"""B25: the per-annotation verdict record entry C0 reached and never wrote down.

WHY THIS EXISTS. Entry C0 audited 302 of his annotations and found 20 gaps. It
NAMES NO PRODUCING SCRIPT, so its figures are a claim about evidence rather
than evidence, and its coverage cannot be mapped onto the register's annotation
tickets: the window holds 306 against C0's claimed 302, and a count cannot say
WHICH items it covered. His own instruction of 2026-10-16 is to pin a set and
not a count, because a count cannot say what moved and a set catches a swap.

SO THE VERDICTS ARE RECORDED AS DATA, one row per annotation anchor, in
`experimental_notes/data/annotation_verdicts_2026-10-17.json`. Each row carries
the anchor, the annotation's own words, a verdict, and the EVIDENCE that
establishes it. Nothing here is a judgement that cannot be checked by reading
what it names.

THE VERDICTS, AND THE DISTINCTIONS MATTER MORE THAN THE LABELS:

  TRACKED  -- a task entry quotes this annotation and that entry's own state
              governs it. Evidence: the entry identifier.
  ACTED_ON -- the instruction was carried out and something committed proves
              it. Evidence: a test file, a script, or a commit.
  GAP      -- nothing carries it. Evidence: what was searched and came back
              empty. A GAP is raised as a task entry, which then supersedes
              this row.
  RULING   -- a question HE must decide, so no work of mine settles it and the
              ticket stays live until he rules. Evidence: what is owed and from
              whom.
  NOTED    -- a decision, agreement or priority HE has already given. Nothing
              is owed from anyone, so it settles. The distinction from RULING
              is not cosmetic: conflating them either leaves his settled
              agreements counted as outstanding for ever, or quietly settles
              questions he has not yet answered. Evidence: the annotation
              itself, which is the whole of it.
  UNDECIDABLE -- its words cannot be attributed, because his short verdicts
              repeat verbatim and the referent lives in the surrounding report.
              This is NOT a soft GAP: it is a statement that this instrument
              cannot answer, and saying so is the point.

WHY IT IS INCREMENTAL AND NOT A SINGLE SWEEP. 311 annotations need a judgement
each, and the referent of "Same answer" or "Then this must be fixed" lives in
the report it annotates. Auditing FILE BY FILE is what makes it tractable: one
file is one report, read once, and its annotations judged against it. A partial
record is useful and an unfinished sweep is not, so the record is additive and
this script reports what is covered and what is not.

Costs nothing: reads local text and dispatches to no model.

Usage:
  audit_his_annotations_2026-10-17.py                  # coverage report
  audit_his_annotations_2026-10-17.py --file <name>    # one file's rows
  audit_his_annotations_2026-10-17.py --close          # settle the register
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RECORD = ROOT / "experimental_notes" / "data" / "annotation_verdicts_2026-10-17.json"
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
WINDOW_FROM = "2026-10-01"

VERDICTS = ("TRACKED", "ACTED_ON", "GAP", "RULING", "NOTED", "UNDECIDABLE")
#: Verdicts that SETTLE a register ticket. A GAP does not: it becomes a task
#: entry, and the entry's own state governs it from then on. A RULING does not:
#: nothing I do settles a question of his.
SETTLING = ("TRACKED", "ACTED_ON", "NOTED", "UNDECIDABLE")


def _reader():
    spec = importlib.util.spec_from_file_location("_fr", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_record() -> dict:
    if not RECORD.is_file():
        return {"window_from": WINDOW_FROM, "rows": []}
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save_record(rec: dict) -> None:
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")


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
          f"CP [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%] "
          f"scipy agrees {p['agrees']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--file", help="show the rows and gaps for one file")
    parser.add_argument("--close", action="store_true",
                        help="settle register tickets for every SETTLING row")
    args = parser.parse_args(argv)

    rec = load_record()
    rows = {r["anchor"]: r for r in rec.get("rows", [])}
    reader = _reader()
    ann = [a for a in reader.annotations()
           if str(a.get("date", "")) >= WINDOW_FROM]

    print("THE RECORD AGAINST THE WINDOW")
    print(f"  annotations dated {WINDOW_FROM} or later : {len(ann)}")
    print(f"  verdict rows recorded                     : {len(rows)}")
    bad = [a for a in rows.values() if a["verdict"] not in VERDICTS]
    assert not bad, f"unknown verdict(s): {[b['verdict'] for b in bad][:3]}"
    counts = {}
    for r in rows.values():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    for v in VERDICTS:
        if counts.get(v):
            _say(f"  {v:<12}", _proportion(counts[v], len(ann)))
    _say("ANY VERDICT AT ALL", _proportion(len(rows), len(ann)))
    print("  Every row names the evidence that establishes it, so the figure")
    print("  above is a SET and not a count: anyone can check any row.")

    if args.file:
        here = [a for a in ann if a["file"] == args.file]
        print(f"\n{args.file}: {len(here)} annotation(s) in the window")
        for a in here:
            key = f"{a['file']}#{a.get('line_index', '?')}"
            got = next((r for r in rows.values()
                        if r["anchor"].startswith(a["file"])
                        and r["text"].strip() == a["text"].strip()), None)
            tag = got["verdict"] if got else "NO VERDICT"
            print(f"  [{tag:<11}] {a['text'][:86]}")
        return 0

    if args.close:
        from bench.ticket_store import TicketStore, LIVE
        store = TicketStore()
        store.load()
        #: MATCHED ON THE FILE AND HIS OWN WORDS, not on the anchor. A verdict
        #: row's anchor is minted by this script and a ticket's anchor by the
        #: harvester, so the 2 are not the same string and matching them found
        #: NOTHING on the first attempt -- a close that silently settles 0
        #: tickets while reporting success is the shape this project keeps
        #: finding.
        def _k(f, text):
            return (f.split("#")[0], " ".join(str(text).split()).lower())
        #: A COLLIDING TEXT MUST REFUSE, NOT PICK ONE. 37 of his annotations
        #: across 12 files share their exact text with a sibling in the SAME
        #: file -- "Do it." appears twice in one report with different
        #: referents, and "Already ruled above." 3 times in another. Keying a
        #: close on the text alone would settle an arbitrary one of them and
        #: look successful, so a collision is reported and skipped.
        unc, collided = {}, set()
        for ticket in store.unconfirmed():
            k = _k(ticket.anchor, ticket.verbatim or ticket.title)
            if k in unc:
                collided.add(k)
            unc[k] = ticket
        closed = 0
        for r in rows.values():
            if r["verdict"] not in SETTLING:
                continue
            #: A TRACKED ROW SETTLES ONLY WHEN ITS ENTRY IS DONE. The verdict
            #: says an entry governs the annotation; it does not say the entry
            #: is finished. Closing a ticket governed by an OPEN entry would
            #: record an instruction of his as settled while the work is still
            #: outstanding, which is the direction that cannot be caught later.
            if r["verdict"] == "TRACKED" and "is DONE" not in r["evidence"]:
                print(f"    left open: tracked by an entry that is not DONE -- "
                      f"{r['text'][:52]}")
                continue
            k = _k(r["file"], r["text"])
            if k in collided:
                print(f"    AMBIGUOUS, not settled: {r['text'][:52]} -- its "
                      f"text repeats in the same file, so a close would pick "
                      f"an arbitrary one")
                continue
            t = unc.get(k)
            if t is None:
                continue
            store.close(t.tid,
                        f"{r['verdict']}: {r.get('why', '')}"[:400],
                        verification=r["evidence"][:400])
            closed += 1
        print(f"\n  settled {closed} register ticket(s) from the record")
        return 0

    missing = [a for a in ann
               if not any(r["anchor"].startswith(a["file"])
                          and r["text"].strip() == a["text"].strip()
                          for r in rows.values())]
    byfile = {}
    for a in missing:
        byfile[a["file"]] = byfile.get(a["file"], 0) + 1
    print(f"\n  WITHOUT A VERDICT YET: {len(missing)}, across "
          f"{len(byfile)} file(s)")
    for f, n in sorted(byfile.items(), key=lambda kv: -kv[1])[:10]:
        print(f"    {n:>4}  {f}")
    print("  Auditing proceeds FILE BY FILE, because one file is one report and")
    print("  the referent of a short verdict of his lives in the report it")
    print("  annotates. A partial record is useful; an unfinished sweep is not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
