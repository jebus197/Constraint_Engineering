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
Over 40 of the 428 accepted notes: rule A fires on 27/40 = 67.5000% of notes,
Wilson 95% [52.0177%, 79.9155%], 79 phrases; rule B on 26/40 = 65.0000%, Wilson
[49.5059%, 77.8655%], 72 phrases. Rule B removes just 8.8608% of findings. The
introduction markers discriminate almost nothing, because notes about new work
legitimately name new machinery without formal "which is" glosses.

THE PHRASE COUNTS DRIFT BY DESIGN, so a mismatch is not a defect. `measure()`
draws 40 notes with `random.sample` over a sorted list, so adding one note
reshuffles the whole draw: the first run of this file, at 427 notes, reported 78
and 71 phrases and density 1.7750 where 428 notes give 79, 72 and 1.8000. The
note-level rates were unmoved. Reproduce with `--measure`, and read the corpus
size the run prints beside the figures rather than assuming this paragraph is
current.

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

A THIRD BLIND SPOT, WHICH THIS FILE SHIPPED WITH AND DID NOT DOCUMENT: THE
SEARCH BACKEND FAILING WAS READ AS THE PHRASE BEING KNOWN. `repo_hits` returned
-1 when `git grep` failed, and `check()` filtered on `hits != 0`, so -1 dropped
the phrase in silence. Two fabrication modes were then EXECUTED on 2026-09-28,
in opposite directions, both exiting 0 with a Wilson interval printed round the
fabricated rate:

  NO GIT TREE   (every panel sandbox: `panel_sandbox.build()` strips the store
                 by design) -- `git grep` exits 128, every count is -1, every
                 phrase is dropped, and a git-less copy of this repo printed
                 `RULE A 0/5 = 0.0000%`, density 0.0000.
  EMPTY INDEX   (`git init` with nothing added; also a broken or partial index)
                 -- `git grep` exits 1, which is NOT an error, so every count is
                 a legitimate-looking 0, every phrase becomes a finding, and the
                 same corpus printed `RULE A 5/5 = 100.0000%`, density 5.8000.

That is the shape the founder's own 2026-09-28 reports named five times over:
a probe that re-derives or invents a value instead of extracting the one the
code owns. It is now closed three ways -- a `/usr/bin/grep` fallback so a
git-less tree can still be searched, `check()` raising `Unsearchable` instead of
dropping the phrase, and `--measure` refusing with exit 3 unless a term that
saturates this project is actually found. `<= 0` rather than `< 0` on that
sentinel is what makes it catch the empty-index mode as well as the git-less
one.

WHAT THE SUBSTITUTION COSTS, MEASURED BY `--compare-backends` RATHER THAN
ASSERTED. The 2 backends ask about different file sets -- tracked content against
the working tree minus the caches -- so the counts differ and only the zero-or-not
answer matters, because that is all `check()` reads. Over 296 candidate phrases
harvested from 60 notes, of which 51 are zero under `git grep`: agreement
296/296 = 100.0000%, Wilson 95% [98.7188%, 100.0000%]. Reproduce with
`python3 scripts/note_naming_check_2026-09-28.py --compare-backends --limit 296`,
which completed in under 11 minutes on this machine -- and that bound is loose,
because another search was running beside it -- since each fallback search walks
the tree rather than an index. THE
STRATUM IS THE POINT: a pooled rate over phrases both backends find easily would
be near 100% whatever the fallback did, so the 51 zero-stratum phrases are what
the figure rests on. Both `--measure` runs over the real repository, before and
after this fix, printed identical figures -- 27/40, 79 phrases, density 1.8000 --
so the git path is unchanged and only the git-less path gained an answer.

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
import functools
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


class Unsearchable(RuntimeError):
    """No backend could answer, so novelty is UNKNOWN -- which is not 0.

    Its own class rather than a bare RuntimeError so a caller can tell "this
    tree cannot be searched" apart from any other failure, and so `main()` can
    map it to a distinct exit code instead of the exit 1 that means FINDINGS.
    """


#: DIRECTORIES THE FALLBACK SKIPS, and the list is measured rather than tidy.
#: `.ruff_cache` alone holds 7,740 files that git never tracked, so skipping
#: the caches makes the fallback CLOSER to `git grep`, not further from it.
#: `logs` is the one real concession: `bench/logs` holds 6,483 of the repo's
#: 9,147 tracked files (70.9000%), because `.gitignore`'s `bench/logs/**` rule
#: stops future growth only and leaves the existing logs tracked -- so skipping
#: it does narrow the population git grep would have asked about. The cost is
#: measured rather than argued: `--compare-backends` puts the 2 backends side by
#: side over 296 phrases and they agree on zero-or-not 296/296 = 100.0000%,
#: Wilson 95% [98.7188%, 100.0000%], the exclusions included. The speed is why
#: they are there at all: `time /usr/bin/grep -rlFi --exclude-dir=.git --
#: "additive standard" .` took 20.375 s against 5.058 s with this list, measured
#: 2026-09-28 on a 1.0 GB tree. Drift direction if a future `.gitignore` adds
#: bulk this list does not name: the fallback then sees MORE files than git and
#: SUPPRESSES findings -- quieter, not falsely alarming -- and
#: `--compare-backends` is the thing that would show it.
_EXCLUDE_DIRS = (
    ".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    ".cdsfl_tmp", ".mutants", "logs", "results",
)

#: A phrase that MUST be found in any tree holding this project. `--measure`
#: refuses unless it is, because both fabrication modes below are invisible to
#: a per-phrase check and visible to this one.
SENTINEL = "additive standard"


@functools.lru_cache(maxsize=None)
def _search_files(phrase: str) -> tuple[tuple[str, ...], str]:
    """Files carrying `phrase`, and WHICH BACKEND answered: git, grep or none.

    CACHED BECAUSE `measure()` ASKS EVERY QUESTION TWICE. It calls `check()` once
    per rule over the same note, so every search ran twice for an answer that
    cannot have changed between them. Measured on the real repository: `--measure`
    fell from 3 min 11.41 s to 1 min 37.16 s, 49.2% off, with every printed figure
    identical. The cache is an extraction cache and holds no derived value; a
    caller that needs a fresh look calls `_search_files.cache_clear()`.

    ONE DECIDER. The backend name is returned by the call that made the choice
    rather than re-derived by anyone who wants to label output, because a probe
    that re-derives a value the code owns is the defect shape that shipped five
    times on 2026-09-28.

    `git grep` first, so the question is asked of tracked content, fixed-string
    and case-insensitive so a phrase is never read as a regex. A PLAIN TREE
    GREP SECOND, because every panel sandbox arrives with `.git` severed by
    design and the old code returned -1 there, which `check()` read as "already
    known" -- so every phrase was dropped and `--measure` printed 0.0000% with
    a Wilson interval round it. Executed 2026-09-28 in a git-less copy of this
    tree: RULE A 0/5 = 0.0000%, exit 0, no warning.

    A non-empty result from a failing grep is kept as a LOWER BOUND rather than
    discarded. Measured cause, 2026-09-28: a concurrent write elsewhere in the
    tree made one plain grep exit 2 after printing a correct match, and the
    same phrase exited 0 on retry. Discarding that would refuse on a tree that
    is merely busy. An empty result from a failing grep stays unknowable,
    because "found nothing" and "died before looking" are then the same string.
    """
    files = _git_grep(phrase)
    if files is not None:
        return files, "git"
    files = _plain_grep(phrase)
    if files is not None:
        return files, "grep"
    return (), "none"


def _git_grep(phrase: str) -> tuple[str, ...] | None:
    """Tracked files carrying `phrase`, or None if git could not answer."""
    try:
        r = subprocess.run(["git", "grep", "-lFi", "--", phrase],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode not in (0, 1):
        return None
    return tuple(f for f in r.stdout.splitlines() if f.strip())


def _plain_grep(phrase: str) -> tuple[str, ...] | None:
    """Working-tree files carrying `phrase`, or None if grep could not answer.

    SEPARATE FROM `_git_grep` SO A TEST CAN EXECUTE IT WHERE GIT WORKS. When the
    fallback was inline, the only way to reach it was to break git, so a mutation
    adding `experimental_notes` to `_EXCLUDE_DIRS` -- which would hide the notes
    corpus from the fallback entirely -- passed all 20 tests. Reachable code is
    testable code.
    """
    excl = [f"--exclude-dir={d}" for d in _EXCLUDE_DIRS]
    try:
        r = subprocess.run(["/usr/bin/grep", "-rlFi", *excl, "--", phrase, "."],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.TimeoutExpired):
        return None
    files = tuple(f.removeprefix("./") for f in r.stdout.splitlines() if f.strip())
    #: A non-empty result from a failing grep is a LOWER BOUND, not a failure.
    if r.returncode in (0, 1) or files:
        return files
    return None


def repo_hits_detail(phrase: str, exclude: Path | None) -> tuple[int, str]:
    """(file count, backend) -- count is -1 exactly when the backend is "none"."""
    files, backend = _search_files(phrase)
    if backend == "none":
        return -1, backend
    if exclude is not None:
        try:
            rel = str(exclude.resolve().relative_to(ROOT))
        except ValueError:
            rel = None
        if rel:
            files = tuple(f for f in files if f != rel)
    return len(files), backend


def repo_hits(phrase: str, exclude: Path | None) -> int:
    """How many FILES in the repo carry this phrase, excluding the note itself.

    -1 means UNKNOWABLE, never 0. `check()` refuses on it; see `Unsearchable`.
    """
    return repo_hits_detail(phrase, exclude)[0]


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
        #: -1 IS AN ERROR, NOT A COUNT. `if hits != 0: continue` read a failed
        #: search as "the phrase is already known" and DROPPED it silently.
        if hits < 0:
            raise Unsearchable(
                f"novelty of {phrase!r} is unknowable in {ROOT}: neither "
                "`git grep` nor `/usr/bin/grep` could answer. That is not 0 "
                "findings, so this check refuses rather than reassure.")
        if hits != 0:
            continue
        intro = introduced(text, phrase, at)
        if rule == "B" and intro:
            continue
        found.append((phrase, hits, intro))
    return sorted(found)


#: EXIT CODES, and 3 exists because of a collision the fix would otherwise have
#: introduced. An uncaught exception leaves Python at exit 1, which is this
#: tool's code for FINDINGS -- so a total refusal to run would have arrived at a
#: caller indistinguishable from "1 phrase names nothing". Refusal gets its own
#: code, and `main()` catches rather than propagates for exactly that reason.
EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE, EXIT_REFUSED = 0, 1, 2, 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--rule", choices=["A", "B"], default="B")
    ap.add_argument("--measure", action="store_true",
                    help="false-positive rate of both rules over the notes corpus")
    ap.add_argument("--compare-backends", action="store_true",
                    help="do git grep and the plain-grep fallback agree on zero-ness?")
    ap.add_argument("--limit", type=int, default=60,
                    help="phrases to compare under --compare-backends")
    a = ap.parse_args(argv)

    if not (a.measure or a.compare_backends or a.paths):
        ap.error("give at least one note, or --measure, or --compare-backends")

    try:
        if a.measure:
            return measure()
        if a.compare_backends:
            return compare_backends(limit=a.limit)
        return _report(a.paths, a.rule)
    except Unsearchable as exc:
        #: ONE CATCH POINT FOR ALL THREE MODES. A mid-run backend failure inside
        #: measure() or compare_backends() would otherwise escape as a traceback
        #: and leave Python at exit 1 -- this tool's code for FINDINGS.
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSED


def _report(paths, rule: str) -> int:
    total = 0
    for p in paths:
        hits = check(p, rule=rule)
        total += len(hits)
        print(f"{p}: {len(hits)} finding(s) under rule {rule}")
        for phrase, _, intro in hits:
            tail = " (introduced)" if intro else ""
            print(f"    NAMES NOTHING: {phrase!r}{tail}")
    return EXIT_FINDINGS if total else EXIT_CLEAN


def compare_backends(limit: int = 60) -> int:
    """Do the 2 backends give the same ZERO-OR-NOT answer? Measured, not assumed.

    THE RATE TRAVELS WITH THIS FUNCTION. The fallback searches the working tree
    while `git grep` searches tracked content, so the 2 ask about different file
    sets, and the docstring's claim that the substitution is safe is only worth
    the measurement behind it. `check()` asks nothing finer than `hits != 0`, so
    zero-ness is the whole question -- an exact-count comparison would fail on
    differences that change no decision.

    Stratification matters and its absence would make the figure vacuous: over
    296 phrases harvested from 60 notes only 51 were zero under `git grep`, so a
    pooled agreement rate is dominated by phrases both backends find easily.
    """
    import random
    notes = sorted((ROOT / "experimental_notes").glob("*.md"))
    if not notes:
        print("no notes corpus found", file=sys.stderr)
        return EXIT_USAGE

    git_files, backend = _search_files(SENTINEL)
    if backend != "git" or not git_files:
        print(f"REFUSING TO COMPARE: this tree answered {SENTINEL!r} with backend "
              f"{backend!r} and {len(git_files)} files. The comparison needs BOTH "
              "backends working, so it can only run from a populated git checkout.",
              file=sys.stderr)
        return EXIT_REFUSED

    random.seed(20260928)
    phrases: set[str] = set()
    for p in random.sample(notes, min(60, len(notes))):
        phrases |= set(candidates(p.read_text(encoding="utf-8", errors="replace")))
    keys = sorted(phrases)
    random.seed(1)
    random.shuffle(keys)
    keys = keys[:max(1, limit)]

    excl = [f"--exclude-dir={d}" for d in _EXCLUDE_DIRS]
    agree = 0
    disagree: list[tuple[str, int, int]] = []
    zero_git = 0
    for ph in keys:
        g = subprocess.run(["git", "grep", "-lFi", "--", ph], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        n = subprocess.run(["/usr/bin/grep", "-rlFi", *excl, "--", ph, "."],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
        gc = len([x for x in g.stdout.splitlines() if x.strip()])
        nc = len([x for x in n.stdout.splitlines() if x.strip()])
        zero_git += (gc == 0)
        if (gc == 0) == (nc == 0):
            agree += 1
        else:
            disagree.append((ph, gc, nc))

    n_tot = len(keys)
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(agree, n_tot, method="wilson")
    except Exception:
        lo = hi = float("nan")

    print("BACKEND AGREEMENT -- git grep against the plain-grep fallback")
    print(f"  phrases compared      {n_tot}")
    print(f"  zero under git grep   {zero_git}  <- the stratum that produces findings")
    print(f"  ZERO-NESS agreement   {agree}/{n_tot} = {100.0*agree/n_tot:.4f}%")
    print(f"      Wilson 95%        [{100*lo:.4f}%, {100*hi:.4f}%]")
    for ph, gc, nc in disagree:
        print(f"    DISAGREE {ph!r}: git {gc} files, fallback {nc} files")
    if not disagree:
        print("  No phrase changed its answer, so the fallback substitutes for the")
        print("  decision `check()` actually makes. It is NOT the same population.")
    return EXIT_CLEAN


def measure() -> int:
    """Both rules against the existing notes corpus, reported as rates.

    THE CORPUS IS THE FALSIFIER. These notes were accepted, so a rule firing on
    a large share of them is a rule that would have blocked accepted work.
    """
    notes = sorted((ROOT / "experimental_notes").glob("*.md"))
    if not notes:
        print("no notes corpus found", file=sys.stderr)
        return EXIT_USAGE

    #: SENTINEL BEFORE SAMPLING, and it is `<= 0` rather than `< 0` because TWO
    #: fabrication modes were executed on 2026-09-28 and only the pair is
    #: caught by the weaker test:
    #:   git ABSENT   -- every count is -1, every phrase dropped, printed
    #:                   `RULE A 0/5 = 0.0000%`, exit 0. Reassuring.
    #:   index EMPTY  -- `git init` with nothing added: `git grep` exits 1, not
    #:                   128, so every count is a legitimate-looking 0 and the
    #:                   run printed `RULE A 5/5 = 100.0000%`, density 5.8000,
    #:                   exit 0. Alarming, and equally fabricated.
    #: A term that saturates the real repository is 0 in both. Refusing costs a
    #: rate that could not be computed anyway.
    #:
    #: THE SENTINEL COUNT IS PRINTED, AND IT IS THE CALIBRATION TO READ. `<= 0`
    #: cannot distinguish a full checkout from a handful of files that happen to
    #: mention the term: a 6-file stub returns 1 and passes. A panel sandbox is a
    #: whole-tree copy and returns 143, so the guard fits the deployment it was
    #: built for -- but a run reporting a single-digit sentinel is a run over
    #: something that is not this project, whatever rate it goes on to print. No
    #: arbitrary count threshold is imposed, because none is measured.
    sentinel_hits, backend = repo_hits_detail(SENTINEL, exclude=None)
    if sentinel_hits <= 0:
        print(f"REFUSING TO MEASURE: {SENTINEL!r} returned {sentinel_hits} files "
              f"(backend: {backend}). A term that saturates this project cannot "
              "be missing, so no novelty count here is answerable and every rate "
              "would be fabricated. Run from a populated checkout.",
              file=sys.stderr)
        return EXIT_REFUSED

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
    print(f"  search backend        {backend}"
          f"   (sentinel {SENTINEL!r}: {sentinel_hits} files)")
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
    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
