#!/usr/bin/env python3
"""Flag a note's technical noun phrases that NAME NOTHING IN THIS PROJECT.

THE DEFECT THIS EXISTS FOR, measured 2026-09-28. Of 13 terms examined from CC1's
own reports to the founder, 8 were faults: 7 coined outright, and 1 worse -- a
term already meaning something else in 7 files. His complaint, verbatim: *"It
can't be the case that I wake up to a tts report and struggle to know what you
are talking about!"* Note standard Rule 28 forbids a DESCRIPTION where a NAME
exists and Rule 19 forbids an UNNAMED subject; neither forbids INVENTING a name
where none existed, and `note_vagueness_lint.py` passed every faulty term at 0
findings.

THE OBVIOUS OBJECTION, WHICH IS WHY THIS SCRIPT MEASURES ITSELF. Novelty alone
cannot be the test: every legitimate new name is novel on the day it is coined,
so a novelty detector fires on the good case and the bad case alike. Run with
--measure to get the false-positive rate of BOTH candidate rules over the
existing notes corpus, and pick on the numbers rather than on this docstring.

  RULE A (novelty): flag a phrase appearing 0 times in the repo outside the note.
  RULE B (novelty AND no introduction): also require that the note never
          INTRODUCES the phrase -- no gloss, no definition, no "which is".

Rule B is the hypothesis that the discriminator is not newness but newness
ASSERTED AS SHARED KNOWLEDGE. A term the writer defines is a name being coined;
a term used bare is one the writer believes the reader already holds.

*** THAT HYPOTHESIS IS REFUTED, and the refutation is the point of --measure. ***
Over 40 of the 427 accepted notes: rule A fires on 27/40 = 67.5000% of notes,
Wilson 95% [52.0177%, 79.9155%], 78 phrases; rule B on 26/40 = 65.0000%, Wilson
[49.5059%, 77.8655%], 71 phrases. Rule B removes just 8.9744% of findings. The
introduction markers discriminate almost nothing, because notes about new work
legitimately name new machinery without formal "which is" glosses.

WHAT THAT MEANS FOR HOW THIS IS USED, and the first framing here was wrong too.
This file originally judged itself by "a rule firing on most accepted notes is
noise" -- the correct bar for a BLOCKING lint, and the wrong one for an ADVISORY.
The figure that decides an advisory is DENSITY: 71 phrases over 40 notes is 1.7750
per note, and a 2-item review list before delivering a report is cheap. On the
report that caused the founder's complaint it returns 3 phrases, 1 of which
(`prose scoring flag`) he had independently identified as a fault.

SO: NOT FIT as a blocking gate, FIT as an advisory. It is deliberately NOT wired
into any commit hook or suite gate, and `main()` returns 1 on findings only so a
human can see them in a pipeline.

KNOWN BLIND SPOT, and it is the worst of the 8 faults. This test cannot see a
COLLISION -- a phrase that DOES exist in the repo while meaning something else,
as `blocking gate` did in 7 files. Novelty is 0 for a collision, so nothing
fires. It also goes blind to any term retrospectively, the moment that term is
written into the repository by any later note. Both limits are structural, not
tuning: verified 2026-09-28, a fixture using `prose conviction rule`,
`blocking gate` and `severity ladder` returns 0 findings for exactly this reason,
while `critics order` is still caught and the legitimately-introduced
`absorb rule` is correctly passed over.

THE DESIGN THE MEASUREMENT POINTS AT, for the founder's ruling rather than for
CC1 to choose: anchor on `docs/GLOSSARY.md`, which already exists to hold "every
term, acronym, Greek letter defined". A machinery phrase absent from the glossary
is either a term that should use the glossary's name, or a term that should be
ADDED to the glossary. That turns a novelty heuristic into a question with a
remedy, and it makes the shared vocabulary the arbiter instead of the repository's
incidental word counts.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: A NAME FOR MACHINERY, not any noun phrase. FIRST DESIGN WAS FALSIFIED BY ITS
#: OWN MEASUREMENT, 2026-09-28: matching any 2-4 adjacent lowercase words over
#: the report that caused the complaint returned 24 findings, of which the great
#: majority were sentence fragments -- `write returned`, `outcome stands`,
#: `cc1 owes` -- and it MISSED the faults it was built for. Adjacency is not
#: grammar, and no stopword list repairs that, because the defect is structural.
#:
#: The 8 real faults share a shape the noise does not: each CLAIMED TO NAME A
#: MECHANISM. `the blocking gate`, `the critics order`, `the prose conviction
#: rule`, `the prose scoring flag` -- determiner, modifiers, then a head noun
#: from this project's own machinery vocabulary. That head noun set is closed and
#: enumerable, which is what makes the pattern tight enough to be a check rather
#: than noise.
_HEADS = (
    "gate|gates|rule|rules|flag|flags|check|checks|checker|order|orders|"
    "mechanism|mechanisms|guard|guards|hook|hooks|layer|layers|pass|passes|"
    "stage|stages|threshold|thresholds|detector|detectors|scorer|scorers|"
    "filter|filters|ladder|ladders|sweep|sweeps|band|bands|gateway|"
    "criterion|criteria|policy|policies|protocol|protocols|convention|"
    "conventions|discipline|invariant|invariants|predicate|predicates|"
    "adapter|adapters|harness|harnesses|instrument|instruments|"
    "phase|phases|tier|tiers|arm|arms|rung|rungs|seat|seats|"
    "veto|vetoes|branch|branches|clause|clauses|ceiling|floor|cap|caps"
)
_CAND = re.compile(
    r"\bthe ((?:[a-z][a-z0-9_-]*[ -]){1,3}(?:" + _HEADS + r"))\b"
)

#: A NAME'S MODIFIERS ARE NEVER VERBS. Measured 2026-09-28 on this report: the
#: head-noun pattern alone still returned 6 findings of which 5 crossed a clause
#: boundary -- `appendix retired that rule`, `decision precedes the branch`,
#: `dispatcher passes seats`. Without a part-of-speech tagger the cheap proxy is a
#: closed verb list, chosen from what actually appeared rather than from a corpus.
_VERBY = {
    "is", "are", "was", "were", "be", "been", "being", "has", "have", "had",
    "does", "do", "did", "can", "could", "will", "would", "should", "may",
    "might", "must", "retired", "passes", "passed", "precedes", "preceded",
    "returns", "returned", "fires", "fired", "carries", "carried", "reports",
    "reported", "states", "stated", "gives", "gave", "holds", "held", "makes",
    "made", "takes", "took", "uses", "used", "needs", "needed", "shows",
    "showed", "says", "said", "means", "meant", "comes", "came", "goes", "went",
    "runs", "ran", "reads", "writes", "wrote", "adds", "added", "removes",
    "removed", "found", "finds", "sees", "saw", "asks", "asked", "tells",
    "told", "keeps", "kept", "leaves", "left", "puts", "sets", "gets", "got",
    "convicts", "convicted", "decides", "decided", "applies", "applied",
    "requires", "required", "produces", "produced", "becomes", "became",
    "remains", "remained", "exists", "existed", "appears", "appeared",
}


#: Modifiers that make a phrase ordinary English rather than a coined name.
_STOP = {
    "same", "next", "last", "first", "second", "third", "other", "another",
    "this", "that", "these", "those", "each", "every", "any", "all", "both",
    "one", "two", "three", "four", "five", "own", "new", "old", "current",
    "above", "below", "following", "whole", "only", "very", "more", "most",
    "such", "which", "what", "some", "few", "many", "real", "wrong", "right",
}


#: Markers that a phrase is being INTRODUCED rather than assumed. A term the
#: writer defines is a name being coined, which the standard permits; a term used
#: bare is one the writer believes the reader already holds, which is the fault.
_INTRO = re.compile(
    r"(?:\bwhich (?:is|are|means?)\b|\bthat is\b|\bi\.e\.|\bnamely\b"
    r"|\bcall(?:ed|s|ing)? (?:it|this|these)\b|\bdefined? as\b|\bmeaning\b"
    r"|\bin other words\b|\bby which\b|\bthe term\b|\bfor short\b"
    r"|\bwhat (?:i|we) (?:call|mean)\b|\bshorthand for\b|\breferred to as\b)",
    re.I,
)
_INTRO_WINDOW = 160


def _strip(text: str) -> str:
    """Remove fenced code, inline code, paths and URLs: not prose, not names."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\b[\w./-]+\.(?:py|md|txt|json|toml|yaml|yml|html|js|sh)\b", " ", text)
    return text


def candidates(text: str) -> dict[str, int]:
    """Phrases that CLAIM TO NAME A MECHANISM, mapped to first-use offset."""
    out: dict[str, int] = {}
    for m in _CAND.finditer(_strip(text).lower()):
        phrase = " ".join(m.group(1).replace("-", " ").split())
        words = phrase.split()
        #: A phrase that is only a stopword plus a head names nothing new --
        #: "the same gate", "the next stage" are ordinary English.
        if words[0] in _STOP and len(words) == 2:
            continue
        #: A verb anywhere before the head means the match crossed a clause.
        if any(w in _VERBY for w in words[:-1]):
            continue
        out.setdefault(phrase, m.start(1))
    return out


def repo_hits(phrase: str, exclude: Path | None) -> int:
    """How many FILES in the repo carry this phrase, excluding the note itself.

    Uses `git grep` so the question is asked of tracked content, and asks it
    case-insensitively with a fixed string so a phrase is never read as a regex.
    """
    cmd = ["git", "grep", "-lFi", "--", phrase]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return -1
    if r.returncode not in (0, 1):
        return -1
    files = [f for f in r.stdout.splitlines() if f.strip()]
    if exclude is not None:
        try:
            rel = str(exclude.resolve().relative_to(ROOT))
        except ValueError:
            rel = None
        if rel:
            files = [f for f in files if f != rel]
    return len(files)


def introduced(text: str, phrase: str, at: int) -> bool:
    """Does the note INTRODUCE this phrase near its first use?"""
    low = _strip(text).lower()
    lo = max(0, at - _INTRO_WINDOW)
    hi = min(len(low), at + len(phrase) + _INTRO_WINDOW)
    return bool(_INTRO.search(low[lo:hi]))


def check(path: Path, rule: str = "B") -> list[tuple[str, int, bool]]:
    """Findings for one note: (phrase, repo file hits, was-introduced)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found = []
    for phrase, at in candidates(text).items():
        hits = repo_hits(phrase, exclude=path)
        if hits != 0:
            continue
        intro = introduced(text, phrase, at)
        if rule == "B" and intro:
            continue
        found.append((phrase, hits, intro))
    return sorted(found)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--rule", choices=["A", "B"], default="B")
    ap.add_argument("--measure", action="store_true",
                    help="false-positive rate of both rules over the notes corpus")
    a = ap.parse_args(argv)

    if a.measure:
        return measure()

    if not a.paths:
        ap.error("give at least one note, or --measure")

    total = 0
    for p in a.paths:
        hits = check(p, rule=a.rule)
        total += len(hits)
        print(f"{p}: {len(hits)} finding(s) under rule {a.rule}")
        for phrase, _, intro in hits:
            tail = " (introduced)" if intro else ""
            print(f"    NAMES NOTHING: {phrase!r}{tail}")
    return 1 if total else 0


def measure() -> int:
    """Both rules against the existing notes corpus, reported as rates.

    THE CORPUS IS THE FALSIFIER. These notes were accepted, so a rule firing on
    a large share of them is a rule that would have blocked accepted work.
    """
    notes = sorted((ROOT / "experimental_notes").glob("*.md"))
    if not notes:
        print("no notes corpus found", file=sys.stderr)
        return 2
    import random
    random.seed(20260928)
    sample = notes if len(notes) <= 40 else random.sample(notes, 40)
    sample = sorted(sample)

    a_hits = b_hits = 0
    a_notes = b_notes = 0
    for p in sample:
        ra = check(p, rule="A")
        rb = check(p, rule="B")
        a_hits += len(ra)
        b_hits += len(rb)
        a_notes += 1 if ra else 0
        b_notes += 1 if rb else 0

    n = len(sample)
    try:
        from statsmodels.stats.proportion import proportion_confint
        wa = proportion_confint(a_notes, n, method="wilson")
        wb = proportion_confint(b_notes, n, method="wilson")
    except Exception:
        wa = wb = (float("nan"), float("nan"))

    print("NOTE NAMING CHECK -- rule comparison over the accepted notes corpus")
    print(f"  corpus sampled        {n} of {len(notes)} notes in experimental_notes/")
    print(f"  RULE A (novel)        fires on {a_notes}/{n} = {100.0*a_notes/n:.4f}% of notes,"
          f" {a_hits} phrase(s) total")
    print(f"      Wilson 95%        [{100*wa[0]:.4f}%, {100*wa[1]:.4f}%]")
    print(f"  RULE B (novel+bare)   fires on {b_notes}/{n} = {100.0*b_notes/n:.4f}% of notes,"
          f" {b_hits} phrase(s) total")
    print(f"      Wilson 95%        [{100*wb[0]:.4f}%, {100*wb[1]:.4f}%]")
    if a_hits:
        print(f"  reduction A -> B      {100.0*(a_hits-b_hits)/a_hits:.4f}% of phrase findings removed")
    print(f"  DENSITY under rule B  {b_hits/n:.4f} phrase(s) per note"
          f"  <- the figure that decides an ADVISORY")
    print()
    print("  A rule firing on most accepted notes cannot BLOCK. Density decides whether")
    print("  it can ADVISE, and 2-3 phrases per note is a review list, not noise.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
