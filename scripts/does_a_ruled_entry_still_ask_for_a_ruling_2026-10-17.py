#!/usr/bin/env python3
"""Does any entry carry his ruling date while its text still asks him to rule?

WHY THIS EXISTS, AND IT IS A DEFECT THAT CAME BACK ONE LEVEL UP. The `ruled:`
field was added to the task-list marker on 2026-10-16 for a measured reason: the
zero-plant control was ruled *"restart it"* on 2026-08-07 and again on
2026-09-06, and 70 days later it was still appearing under decisions that needed
him, because neither the task list nor the report generator could express the
statement "he has already decided this".

The field fixed the REPORT. It did not fix the ENTRY. A marker records the DATE
he ruled; the entry's prose still carries whatever question was put to him, and
nothing reconciles the two. So a reader -- including the assistant -- reads the
prose, sees *"NEEDS HIS RULING"*, and puts a settled question to him again. That
happened on 2026-10-17 with task B12: its 3 options were put to him in a brief,
he answered them on 2026-10-16 by rejecting all 3 and naming a fourth, and the
entry still said "NEEDS HIS RULING" so the question was re-presented.

MEASURED 2026-10-17: of 151 entries, 45 carry a `ruled:` date, and **11 of those
45 -- 24.4444%, Wilson [14.2355%, 38.6734%], Clopper-Pearson [12.8823%,
39.5371%]** -- still ask for a ruling in their own text. 3 of the 11 are marked
DONE, so the prose outlived the work as well as the ruling.

WHAT WOULD SETTLE IT. An entry that records a ruling should record WHAT he ruled,
not only when. This script names the 11 so each can be reconciled against his
actual words through `scripts/read_founder_responses_2026-10-11.py`, and
`bench/tests/test_a_ruled_entry_does_not_still_ask_2026-10-17.py` refuses to let
the set grow.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: Phrases by which an entry's own text asks the founder to decide. Listed
#: rather than inferred, so adding one is a deliberate act.
ASKS_FOR_A_RULING = (
    "NEEDS HIS RULING", "NEEDS YOUR RULING", "needs his ruling",
    "awaiting his ruling", "THE CHOICE IS HIS", "the choice is his",
    "is the founder's call", "STILL HIS",
)

#: Phrases by which an entry RECORDS what he ruled, as opposed to its date.
#:
#: WHY THIS SECOND LIST EXISTS, and it is an accuracy repair rather than a
#: loosening. The first version of this check flagged every entry that had a
#: `ruled:` date and still asked. Reconciling B11 showed that is too strong: B11
#: has 2 questions, (b) the forward normalisation of model-supplied identifiers
#: and (c) what the baseline should be after a run lands. He ruled (b) on
#: 2026-10-16 -- *"We normalise going forward, since recording vendor names is
#: purely a recording statistic"* -- and has not ruled (c), so B11 legitimately
#: carries a ruling date AND legitimately still asks.
#:
#: The defect is narrower than "asks while ruled". It is an entry that asks
#: while recording NO ruling at all, so a reader cannot tell a settled question
#: from an open one -- which is how task B12's answered question was put to him
#: again on 2026-10-17. An entry that quotes what he ruled and then names what
#: remains is doing exactly the right thing.
RECORDS_A_RULING = (
    "HIS RULING", "HIS WORDS", "He ruled", "he ruled", "HE RULED",
    "HIS RULING WAS GIVEN", "RULED ON", "his ruling of", "HIS DESIGN POINT",
    "FOUNDER DESIGN POINT", "HIS LIST", "HIS QUESTION", "HIS ANSWER",
)


def asks(body: str) -> bool:
    """Does the entry's own text ask him to rule?"""
    return any(p in body for p in ASKS_FOR_A_RULING)


def records(body: str) -> bool:
    """Does it record WHAT he ruled, as distinct from asking for a ruling?

    THE ASKING PHRASES ARE REMOVED FIRST, and this is the whole correctness of
    the check. `RECORDS_A_RULING` contains "HIS RULING", which is a SUBSTRING of
    "NEEDS HIS RULING". Without the removal every asking entry also counted as
    recording one, so the detector reported 0 problems whatever the task list
    said -- vacuous, and it reported exactly that on its first run after this
    second list was added. Caught by the anti-vacuity assertion in
    `bench/tests/test_a_ruled_entry_does_not_still_ask_2026-10-17.py`, which
    plants a known-bad entry rather than relying on the live data being broken.
    """
    stripped = body
    for p in ASKS_FOR_A_RULING:
        stripped = stripped.replace(p, " ")
    return any(p in stripped for p in RECORDS_A_RULING)


def entry_bodies() -> dict[str, str]:
    """ident -> the entry's own text, heading to the next heading."""
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import ENTRY
    lines = TASKLIST.read_text(encoding="utf-8").splitlines()
    marks = [(i, ENTRY.match(l).group(1)) for i, l in enumerate(lines)
             if ENTRY.match(l)]
    out = {}
    for n, (i, ident) in enumerate(marks):
        j = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
        out[ident] = "\n".join(lines[i:j])
    return out


def still_asking() -> tuple[list, int, int]:
    """(entries whose text still asks, how many are ruled, how many in total)."""
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries
    entries = parse_entries(TASKLIST)
    bodies = entry_bodies()
    ruled = [e for e in entries if e.ruled]
    bad = [e for e in ruled
           if asks(bodies.get(e.ident, ""))
           and not records(bodies.get(e.ident, ""))]
    return bad, len(ruled), len(entries)


def asks_at_all() -> list:
    """Every ruled entry whose text asks, WHETHER OR NOT it records a ruling.

    Kept alongside `still_asking` so the stricter original measurement stays
    reproducible: it was 11 of 45 on 2026-10-17, and the narrower one is the
    subset of those that record no ruling at all.
    """
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries
    bodies = entry_bodies()
    return [e for e in parse_entries(TASKLIST) if e.ruled
            and asks(bodies.get(e.ident, ""))]


def main() -> int:
    answer_help(__doc__, __file__)
    if not TASKLIST.is_file():
        print(f"FATAL: {TASKLIST} does not exist.")
        return 2
    bad, n_ruled, n_all = still_asking()
    print("A RULING RECORDED, A QUESTION STILL ASKED")
    print(f"  entries in the task list        : {n_all}")
    print(f"  carrying a `ruled:` date        : {n_ruled}")
    asking = asks_at_all()
    print(f"  whose own text asks at all      : {len(asking)}")
    print(f"  AND records no ruling at all    : {len(bad)}   <-- the defect")
    if n_ruled:
        from statsmodels.stats.proportion import proportion_confint
        import scipy.stats as st
        k = len(bad)
        w = proportion_confint(k, n_ruled, method="wilson")
        b = proportion_confint(k, n_ruled, method="beta")
        cp_hi = 1.0 if k == n_ruled else float(
            st.beta.ppf(0.975, k + 1, n_ruled - k))
        print(f"  {k} of {n_ruled} = {100*k/n_ruled:.4f}%")
        print(f"    Wilson          [{w[0]*100:.4f}%, {w[1]*100:.4f}%]")
        print(f"    Clopper-Pearson [{b[0]*100:.4f}%, {b[1]*100:.4f}%]")
        print(f"    scipy agrees on the upper bound: "
              f"{abs(b[1] - cp_hi) < 1e-9}")

    bodies = entry_bodies()
    print("\n  EACH ONE, WITH THE PHRASE THAT ASKS, so it can be reconciled")
    print("  against his actual words rather than against a recollection:")
    for e in bad:
        body = bodies.get(e.ident, "")
        found = [p for p in ASKS_FOR_A_RULING if p in body]
        print(f"    {e.ident:<5} {e.state:<9} ruled {e.ruled}   "
              f"asks via {found[0]!r}")
        head = body.splitlines()[0]
        print(f"          {head[:104]}")
    done_too = [e for e in bad if e.state == "DONE"]
    if done_too:
        print(f"\n  {len(done_too)} of these are marked DONE, so the prose has "
              f"outlived the work as well as the ruling:")
        print("      " + ", ".join(e.ident for e in done_too))
    print("\n  READ HIS WORDS WITH THE READER, NEVER WITH grep:")
    print("      python3 scripts/read_founder_responses_2026-10-11.py --json")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
