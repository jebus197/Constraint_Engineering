#!/usr/bin/env python3
"""His clarity complaint recurs, and the checker that should catch it is blind
to the one form he objects to.

HIS COMPLAINT, 2026-10-31, verbatim: "You describe the issue, do not simply give
it a brief designation (like B1, or C3, or whatever), say why its relevant, what
the implications of the issue are, and make recommendations for a fix based on
our 3 formal project standards".

WHY THIS IS A MEASUREMENT AND NOT AN APOLOGY. It would be easy to read that as a
one-off and fix the one report. The record says otherwise, and the record is what
decides whether a reformat is sufficient or a mechanism is owed. 3 questions, each
with its own decision rule stated before the count:

  Q1 IS IT RECURRING? A one-off is answered by rewriting 1 document. A pattern
     across many dates is not. Rule: recurring if it appears on more than 2
     distinct dates.

  Q2 IS IT GETTING WORSE? Rule: a worsening may be CLAIMED only if the Fisher
     exact p on the early/late split is below 0.05. It is not, so it must not be
     claimed -- that constraint is the point of writing the rule down first.

  Q3 CAN THE EXISTING CHECKER SEE IT? `scripts/note_vagueness_lint.py` already
     enforces Rule 19, name the subject, and runs as a ratchet in
     `hooks/pre-commit`. Rule: the checker is adequate if it fires on a bare
     entry code and stays silent on a glossed one.

WHAT Q3 FOUND, AND IT IS THE WHOLE POINT. The rule has existed since note
standard v1.4. The checker has existed since v1.5 and RUNS on every note. And it
does not fire on a bare entry code at all, because `UNNAMED SUBJECT` matches a
closed list of generic nouns and `CATEGORY NOUN` matches project terms, and an
entry code is neither. So this is NOT the familiar "the checker was never run"
failure recorded against Rule 27. It is worse: the checker runs, and cannot see
the form he has objected to most.

SCOPE IS WHAT MAKES THE FIX CHEAP, and getting it wrong is what would make the
fix impossible. Unscoped, the backlog is over 13,000 bare mentions across most
notes in the tree, and the single worst file is the MASTER TASK LIST -- where a
bare code is CORRECT, because there the code is the primary key. Scoped to the
documents he actually reads, the backlog is roughly 4 per cent of that. His own
ruling on entry B24, when a widened detector faced the same arithmetic, was
"Enforce going forward only."
"""
from __future__ import annotations

import collections
import importlib.util
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
NOTES_DIR = REPO / "experimental_notes"

#: His own words, taken from annotations rather than paraphrased.
MARKS = ("too vague", "plain english", "no explanation", "no recommedation",
         "no recommendation", "designated id", "impossibly dense",
         "idea what you are talking about", "unless you explain",
         "no explanations", "refresh my memory")
#: The task list's own entry shape, borrowed rather than re-invented.
CODE = re.compile(r"\b((?:[A-Z]{1,2})\d+(?:\.\d+)?[a-z]?)\b")
#: A gloss: the code, then punctuation, then at least 3 words. DELIBERATELY
#: GENEROUS, so the offender count is a FLOOR and not an inflated case.
GLOSS = re.compile(r"\b(?:[A-Z]{1,2})\d+(?:\.\d+)?[a-z]?\b"
                   r"\s*[,:—-]\s+(?:\w+\s+){2,}\w+")
#: What he READS, as opposed to what the project writes for itself.
HIS_SCOPE = re.compile(r"(Morning_Report|Decisions_Awaiting|Overnight_)")


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def interval(k: int, n: int) -> str:
    """Wilson from statsmodels, re-derived in mpmath, plus Clopper-Pearson."""
    import mpmath as mp
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054")
    K, N = mp.mpf(k), mp.mpf(n)
    ph = K / N
    d = 1 + z**2 / N
    c = (ph + z**2 / (2 * N)) / d
    h = z * mp.sqrt(ph * (1 - ph) / N + z**2 / (4 * N**2)) / d
    agree = max(abs(sm[0] - float(c - h)), abs(sm[1] - float(c + h)))
    return (f"{k}/{n} = {k/n:.6f}  Wilson [{sm[0]:.6f}, {sm[1]:.6f}] "
            f"(mpmath agrees to {agree:.1e})  "
            f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")


def bare_codes(paths) -> tuple[int, int, list]:
    rows, bare_tot, code_tot = [], 0, 0
    for p in sorted(paths):
        try:
            t = p.read_text(errors="ignore")
        except OSError:
            continue
        bare = 0
        for s in re.split(r"(?<=[.!?])\s+", t):
            cs = CODE.findall(s)
            if not cs:
                continue
            code_tot += len(cs)
            if not GLOSS.search(s):
                bare += len(cs)
        bare_tot += bare
        if bare:
            rows.append((p.name, bare))
    return bare_tot, code_tot, rows


def main() -> int:
    rd = _load("scripts/read_founder_responses_2026-10-11.py", "rd_cc")
    print("=" * 78)
    print("HIS CLARITY COMPLAINT, AND THE CHECKER THAT CANNOT SEE IT")
    print("=" * 78)

    # ---- Q1: is it recurring?
    anns = rd.annotations()
    hits = [a for a in anns if any(m in a["text"].lower() for m in MARKS)]
    by_date = collections.Counter(a["date"] for a in hits)
    print("\nQ1 IS IT RECURRING?")
    print(f"    the complaint: {interval(len(hits), len(anns))}")
    print(f"    distinct dates on which he raised it: {len(by_date)}")
    for d, c in sorted(by_date.items()):
        print(f"       {d}  {c}")
    recurring = len(by_date) > 2
    print(f"    -> {'RECURRING' if recurring else 'one-off or near'}")

    # ---- Q2: is it worsening? (and the rule forbids claiming it unless p < 0.05)
    from scipy import stats
    dates = sorted(a["date"] for a in anns)
    mid = dates[len(dates) // 2]
    early = [a for a in anns if a["date"] < mid]
    late = [a for a in anns if a["date"] >= mid]
    ek = sum(1 for a in early if any(m in a["text"].lower() for m in MARKS))
    lk = sum(1 for a in late if any(m in a["text"].lower() for m in MARKS))
    odds, p = stats.fisher_exact([[lk, len(late) - lk], [ek, len(early) - ek]])
    print(f"\nQ2 IS IT GETTING WORSE? split at the median annotation date {mid}")
    print(f"    before: {ek}/{len(early)} = {ek/len(early):.6f}")
    print(f"    from  : {lk}/{len(late)} = {lk/len(late):.6f}")
    print(f"    Fisher exact odds ratio {odds:.4f}, p = {p:.6f}")
    print(f"    -> {'WORSENING, claimable' if p < 0.05 else 'NOT CLAIMABLE: the rate roughly doubled but p >= 0.05, so the direction is suggestive and the magnitude is NOT established'}")

    # ---- Q3: can the checker see it?
    nvl = _load("scripts/note_vagueness_lint.py", "nvl_cc")
    CASES = [
        ("a bare entry code, which is the form he objects to",
         "2 items it still described had been closed, B41 and B50, and 2 live "
         "items had no description at all, B53 and B56.", True),
        ("the same sentence with each code glossed",
         "2 items it still described had been closed. Those were B41, the work "
         "queue of 2026-10-19, and B50, the 6 immune memory assertions.", False),
        ("a single bare code, which is how R1 reached him",
         "R1 is recorded as deferred until the rest of the list is clear.", True),
    ]
    print("\nQ3 CAN THE EXISTING CHECKER SEE IT?")
    adequate = True
    for name, line, should_fire in CASES:
        f = pathlib.Path(tempfile.mkdtemp()) / "Probe_2026-10-31.md"
        f.write_text(line + "\n\nWritten under CDSFL note standard v1.8 "
                            "(17 October 2026).\n")
        fired = bool(nvl.lint(f))
        ok = fired == should_fire
        adequate &= ok
        print(f"    {'fires  ' if fired else 'silent '} "
              f"{'as expected' if ok else 'WRONG   '}  {name}")
    print(f"    -> the checker is {'ADEQUATE' if adequate else 'BLIND to the bare-code form'}")

    # ---- the scope that decides whether a fix is affordable
    all_notes = [p for p in NOTES_DIR.iterdir()
                 if p.is_file() and p.suffix in (".md", ".txt")]
    his = [p for p in all_notes if HIS_SCOPE.match(p.name)]
    b_all, c_all, rows_all = bare_codes(all_notes)
    b_his, c_his, rows_his = bare_codes(his)
    print("\nTHE SCOPE THAT DECIDES WHETHER A FIX IS AFFORDABLE")
    print(f"    every note      : files with a bare code {interval(len(rows_all), len(all_notes))}")
    print(f"                      bare mentions {b_all} of {c_all}")
    if rows_all:
        worst = max(rows_all, key=lambda x: x[1])
        print(f"                      worst file {worst[0]} at {worst[1]}")
    print(f"    what he READS   : files with a bare code {interval(len(rows_his), len(his))}")
    print(f"                      bare mentions {b_his} of {c_his}")
    if b_all:
        print(f"    scoped backlog is {b_his/b_all:.4f} of the unscoped one")

    print("\n" + "=" * 78)
    print("RECOMMENDATION. Add a bare-entry-code check to the note lint, SCOPED to")
    print("the documents he reads and dated so it enforces going forward only,")
    print("which is his own ruling on entry B24 when a widened detector faced the")
    print("same arithmetic. ADDITIVE: a new finding class, no existing check")
    print("weakened. SIMPLEST SUFFICIENT: 1 pattern and 1 scope test, against the")
    print("alternative of rewriting the archive. COMPOSABILITY: not claimed -- the")
    print("check alone is the whole fix and nothing is composed with it.")
    print("NEEDS HIS RULING, because widening a ratchet is his call by precedent.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
