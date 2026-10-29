#!/usr/bin/env python3
"""Do Options 3 and 1 of entry B29 compose? His question of 2026-10-19, measured.

HIS WORDS, 2026-10-19, ruling on B29: *"Verdict: Option 3. Dut do Options 3 and
1 compose, if an event occurs where a save operation does not complete cleanly?"*
(*Dut* is *But*.)

THE 3 OPTIONS HE WAS CHOOSING BETWEEN, from
`experimental_notes/data/morning_report_decisions.json`, key `task:B29`:
  1. Have the save RECORD whether its own conditions passed, and have the memory
     check skip back to the last save that finished cleanly.
  2. Put it to the free panel.
  3. Run the staleness check BEFORE invoking the save rather than after it
     refuses. "Costs under a third of a second and turns 2 saves into 1."

WHY THE QUESTION IS SHARP AND NOT RHETORICAL. Option 3 is PREVENTION: it stops
the save that would have failed its own recovery-currency condition. Option 1 is
a REMEDY: it lets the second save through when a first one did not finish
cleanly for ANY reason. So 3 reduces how often the second save is needed, and 1
fixes the second save when it is needed anyway. They are redundant only if
EVERY follow-up save is caused by the condition Option 3 pre-checks. That is a
measurable claim, and this script measures it.

METHOD. Take the same pairs the parent producer takes -- imported, not
reimplemented, so the denominators agree exactly -- and classify each sub-15
-minute follow-up by whether its own commit subject names the A23 recovery guard,
the SESSION STATE block, or a missing producer/suite-figure citation. Those are
the class Option 3 pre-checks. Everything else is a follow-up Option 3 cannot
see, and only Option 1 helps there.

WHAT WOULD FALSIFY "THEY COMPOSE": a count of 0 in the not-preventable column.
Then Option 3 alone would cover every observed occasion and Option 1 would be
an addition nothing reaches, which the additive standard forbids.

THE INSTRUMENT'S LIMIT, STATED RATHER THAN BURIED, and it is the parent
producer's limit too: a commit subject is what a save SAYS about itself, not an
observation of which gate fired. Git does not record the gate. So every figure
here bounds exposure and classifies intent; it does not count realised
refusals. Each classified commit is PRINTED with its verdict so a reader can
check the classification instead of trusting it.

USAGE
    python3 scripts/do_options_three_and_one_compose_2026-10-29.py
    python3 scripts/do_options_three_and_one_compose_2026-10-29.py --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from datetime import timedelta

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The subject shapes that name the condition Option 3 pre-checks. Deliberately
#: anchored on the guard's own name and on the 2 phrases the A23 guard's
#: failures produce -- a missing producer citation and a stale/unnamed session
#: state block -- rather than on a loose keyword such as "recovery", which also
#: appears in unrelated save subjects.
OPTION_3_CLASS = re.compile(
    r"\bA23\b"
    r"|session[ _]state"
    r"|suite citation"
    r"|name(?:d|s)? (?:no |the )?producers?"
    r"|named no producer"
    r"|re-runnable producer",
    re.IGNORECASE)


def _parent(root: pathlib.Path):
    """The parent producer, imported so the pair set is IDENTICAL, not parallel.

    IT TAKES `root` RATHER THAN USING THIS FILE'S OWN LOCATION, so `--root`
    governs both halves. Deriving it from `__file__` made the 2 disagree the
    moment this script was run from anywhere but the repository.
    """
    p = root / "scripts" / "how_often_is_a_second_sv_refused_2026-10-17.py"
    spec = importlib.util.spec_from_file_location("parent", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _subject(sha: str, root: pathlib.Path) -> str:
    p = subprocess.run(["git", "log", "-1", "--format=%s", sha],
                       cwd=root, capture_output=True, text=True, timeout=30)
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()

    P = _parent(root)
    rows = P.sv_commits(root)
    all_pairs = list(zip(rows, rows[1:]))
    pairs = [(x, y) for x, y in all_pairs if y[1] >= P.CHECK_BORN]
    quick = [(x, y) for x, y in pairs if (y[1] - x[1]) <= timedelta(minutes=15)]

    classified = []
    for first, second in quick:
        subj = _subject(second[0], root)
        hit = OPTION_3_CLASS.search(subj)
        classified.append({
            "first": first[0], "second": second[0],
            "gap_min": round((second[1] - first[1]).total_seconds() / 60.0, 1),
            "prevented_by_option_3": bool(hit),
            "matched_on": hit.group(0) if hit else None,
            "subject": subj[:160],
        })

    k3 = sum(1 for c in classified if c["prevented_by_option_3"])
    k1 = len(classified) - k3
    n = len(classified)
    lo3, hi3 = P.wilson(k3, n) if n else (0.0, 1.0)
    lo1, hi1 = P.wilson(k1, n) if n else (0.0, 1.0)

    res = {
        "pairs_after_the_check_was_born": len(pairs),
        "follow_ups_within_15_min": n,
        "prevented_by_option_3": k3,
        "prevented_by_option_3_share": round(k3 / n, 6) if n else None,
        "prevented_by_option_3_wilson": [round(lo3, 6), round(hi3, 6)],
        "NOT_prevented_by_option_3": k1,
        "NOT_prevented_share": round(k1 / n, 6) if n else None,
        "NOT_prevented_wilson": [round(lo1, 6), round(hi1, 6)],
        "classified": classified,
    }
    res["verdict"] = (
        "THEY COMPOSE, AND NEITHER IS REDUNDANT. "
        f"{k3} of {n} follow-up saves name the condition Option 3 pre-checks, so "
        f"Option 3 removes that share of the occasions. The other {k1} of {n} name "
        "something else -- a different postcondition, or substantive work -- which "
        "a staleness pre-check cannot see, and for those the memory baseline still "
        "refuses the second save. Option 1 is the only one of the 2 that helps "
        "there, which is exactly the event his question names."
        if k1 else
        "OPTION 3 ALONE COVERS EVERY OBSERVED OCCASION. Option 1 would be an "
        "addition nothing reaches, which the additive standard forbids.")

    if a.json:
        print(json.dumps(res, indent=2))
        return 0

    print(__doc__.split("USAGE")[0].rstrip())
    print()
    print(f"  pairs after the check was born:      {len(pairs)}")
    print(f"  follow-ups within 15 minutes:        {n}")
    print(f"  Option 3 pre-checks this condition:  {k3}  "
          f"{100.0 * k3 / n:.4f}%  Wilson [{100 * lo3:.4f}%, {100 * hi3:.4f}%]"
          if n else "  no follow-ups")
    print(f"  Option 3 CANNOT see this:            {k1}  "
          f"{100.0 * k1 / n:.4f}%  Wilson [{100 * lo1:.4f}%, {100 * hi1:.4f}%]"
          if n else "")
    print()
    print("  EVERY CLASSIFICATION, so it can be checked rather than trusted:")
    for c in classified:
        mark = "OPT3" if c["prevented_by_option_3"] else " -- "
        on = f" [{c['matched_on']}]" if c["matched_on"] else ""
        print(f"    {mark} {c['second']}  {c['gap_min']:>5.1f} min{on}")
        print(f"         {c['subject'][:118]}")
    print()
    print(f"  {res['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
