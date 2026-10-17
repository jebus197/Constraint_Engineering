#!/usr/bin/env python3
"""Were my 20 "confirmed gaps" already settled elsewhere? His challenge, 2026-10-17.

HIS CHALLENGE, verbatim: "Your routing ladder work is a rediscovery, we already
addressed this again just recently... You should take care in any case to ensure
that your other 'discoveries' are not also repeats/recoveries of already settled
work."

HE IS RIGHT ABOUT THE LADDER AND THE CAUSE IS IN MY OWN BRIEF. The audit of
2026-10-17 instructed 5 agents to check each of his instructions against ONE
artefact: experimental_notes/CDSFL_MASTER_TASK_LIST.md. Supersession is not
recorded there. It is recorded in the persistent-memory corpus, where
`cdsfl_the_ladder_still_cannot_climb_2026-10-06.md` carries the header
"SUPERSEDED ON ITS HEADLINE CLAIM" and the instruction "Do not raise either with
the founder again." An auditor confined to the task list cannot see that, so an
absence from the task list was reported as "untracked" when it was in fact
"settled and recorded in the other place".

So this script asks of each of the 20: does the SETTLED record already speak to
it? It searches the memory corpus and the notes written in the last 48 hours,
which is the window he set.

WHAT IT CAN AND CANNOT DECIDE. A hit means the subject is discussed somewhere in
the settled record, which makes the entry a REDISCOVERY CANDIDATE needing a human
read. It does NOT by itself prove the item is closed, because a note can discuss
a subject and leave it open. The output is therefore a triage list, not a verdict,
and it is labelled as such.

`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations
import argparse, json, pathlib, re, subprocess, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEM = pathlib.Path.home()/".claude/projects/-Users-georgejackson-Developer-Projects/memory"
NOTES = ROOT/"experimental_notes"
TASKLIST = NOTES/"CDSFL_MASTER_TASK_LIST.md"

#: Phrases that mark a settled item in this project's own vocabulary.
SETTLED_MARKERS = (
    "superseded", "do not raise", "do not raise either", "discharged",
    "no ruling owed", "already ruled", "struck permanently", "strike",
    "withdrawn", "retired", "resolved", "closed", "settled",
)

def entries() -> list[tuple[str, str, str]]:
    """(ident, severity, his words) for each C1..C20 in the task list."""
    text = TASKLIST.read_text(encoding="utf-8")
    out = []
    for para in text.split("\n\n"):
        m = re.match(r"\*\*(C\d+)\. ([A-Z ,]+?), dated ([0-9-]+)", para.strip())
        if not m or m.group(1) == "C0":
            continue
        q = re.search(r"\*\*HIS WORDS:\*\*(.*?)\*\*", para, re.DOTALL)
        words = " ".join((q.group(1) if q else "").split())
        out.append((m.group(1), m.group(2).strip(), words))
    return out

STOP = set("""the a an and or but if then than that this these those of to in on at by for with from
as is are was were be been being it its they them their there here what which who when where why how
all any both each few more most other some such no nor not only own same so too very can will just
should now have has had having would could may might must shall about above after again against below
between into through during before once under over further also yet still get got make made say said
see seen look think know want need work thing way lot bit yes ok please thanks verdict agree agreed
good call fix fixed done should also your my our his him her you me we us""".split())

def keywords(text: str, n: int = 8) -> list[str]:
    words = [w for w in re.findall(r"[a-z][a-z_]{4,}", text.lower()) if w not in STOP]
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); out.append(w)
    return out[:n]

#: MY OWN OUTPUT IS NOT THE SETTLED RECORD. The first version of this script
#: included every note modified in the last 48 hours, which includes the task
#: list itself -- so each entry matched its OWN text and the script reported
#: 90.0000% rediscovery candidates, a figure that measured nothing. This is the
#: 3rd measure of that family in 2 days; see the feedback memory of 2026-10-17.
SELF_AUTHORED = {
    "CDSFL_MASTER_TASK_LIST.md",
    "Pre_Build_Rulings_Needed_2026-10-17.md",
    "Final_Discussion_Before_Authorisation_2026-10-16.md",
    "Decisions_Consolidated_2026-10-16.md",
}

def corpus() -> list[tuple[str, str]]:
    files = sorted(MEM.glob("*.md"))
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=48)
    files += [p for p in sorted(NOTES.glob("*.md"))
              if datetime.datetime.fromtimestamp(p.stat().st_mtime) >= cutoff
              and p.name not in SELF_AUTHORED]
    out = []
    for p in files:
        try: out.append((p.name, p.read_text(encoding="utf-8", errors="ignore").lower()))
        except OSError: pass
    return out

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-hits", type=int, default=4,
                    help="distinctive words that must co-occur in one file (default 4)")
    a = ap.parse_args()

    C = entries()
    docs = corpus()
    print("=" * 78)
    print("ARE MY 20 'CONFIRMED GAPS' REDISCOVERIES? his challenge of 2026-10-17")
    print("=" * 78)
    print(f"\nentries examined : {len(C)}")
    print(f"settled record   : {len(docs)} documents "
          f"({len(list(MEM.glob('*.md')))} memory files + notes from the last 48 hours)")
    print(f"\nTHE AUDIT'S OWN BRIEF NAMED 1 ARTEFACT: the master task list. It did not")
    print(f"read the memory corpus, which is where supersession is recorded.\n")

    cand, clean = [], []
    for ident, sev, words in C:
        kws = keywords(words)
        best = None
        for name, body in docs:
            hits = [k for k in kws if k in body]
            if len(hits) >= a.min_hits:
                marks = [m for m in SETTLED_MARKERS if m in body]
                score = (len(hits), len(marks))
                if best is None or score > best[0]:
                    best = (score, name, hits, marks)
        if best:
            cand.append((ident, sev, best))
        else:
            clean.append((ident, sev, kws))

    print(f"REDISCOVERY CANDIDATES: {len(cand)} of {len(C)}")
    print(f"NO MATCH IN THE SETTLED RECORD: {len(clean)} of {len(C)}\n")

    print("CANDIDATES, each needing a human read before it stays on the list:")
    for ident, sev, (score, name, hits, marks) in sorted(cand):
        print(f"  {ident:>4s} [{sev[:28]:<28s}] -> {name}")
        print(f"        {score[0]} shared terms {hits[:5]}")
        if marks:
            print(f"        that document carries settled-markers: {marks[:5]}")

    print("\nNO MATCH -- most likely genuinely outstanding:")
    for ident, sev, kws in sorted(clean):
        print(f"  {ident:>4s} [{sev[:28]:<28s}] terms searched: {kws[:5]}")

    k, n = len(cand), len(C)
    try:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta
        lo, hi = proportion_confint(k, n, 0.05, "wilson")
        blo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n-k+1))
        bhi = 1.0 if k == n else float(beta.ppf(0.975, k+1, n-k))
        print(f"\nCANDIDATE RATE = {k} of {n} = {k/n*100:.4f}%")
        print(f"  Wilson (statsmodels)    [{lo*100:.4f}%, {hi*100:.4f}%]")
        print(f"  Clopper-Pearson (scipy) [{blo*100:.4f}%, {bhi*100:.4f}%]")
    except Exception as e:
        print(f"\ninterval unavailable: {e}")

    print("\n" + "=" * 78)
    print("THIS IS TRIAGE, NOT A VERDICT. A shared-term hit means the subject is")
    print("discussed in the settled record; it does not prove the item is closed.")
    print("Each candidate needs the note read before the entry is struck or kept.")
    print("=" * 78)
    return 0

if __name__ == "__main__":
    sys.exit(main())
