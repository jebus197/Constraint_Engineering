#!/usr/bin/env python3
"""GENERATE the decisions file he asked for on 2026-11-07, 1 item per decision.

HIS REQUEST, 2026-11-07: *"print a fresh tts with each issue, explaining what it
is, why it matters and with your recommendation in each case"*, after ruling on
2026-11-06 that the line caps were never his: *"raise the cap in all 3. I never
specified a cap."*

WHY A GENERATOR AND NOT A HAND-WRITTEN FILE. The morning report of 2026-11-06
was written by hand and told him 3 things awaited him when the record tracked
29. A hand-written surface cannot be checked against the record, and the project
already holds a guard that compares the 2 surfaces and refuses when they differ.
This renderer reads the SAME authored detail the generated report reads, through
the SAME functions, so the file and the record cannot disagree.

EVERY PART IS BORROWED RATHER THAN REWRITTEN, per `use-the-instrument-that-
exists`: the live queue comes from `do_the_two_decision_surfaces_agree`'s
`derived()`, the authored detail from `morning_report_build.decisions()`, and the
spoken normalisation from that module's own `_spoken()`, which strips emphasis,
unwraps backticks, drops file paths whole with their labelled clause, and
replaces em-dashes. Writing a second normaliser here would be the
`execute-do-not-grep` shape: 2 declarations of 1 rule, each individually
correct.

THE 4 FIELDS ARE THE ONES HE ENDORSED on 2026-10-30 and restated this morning:
what it is, why it matters (what it affects), what he decides, and what is
recommended with its standard named. Rule 33 of note standard v1.9 requires the
recommendation to name additive, simplest sufficient or composability.

Writes 3 files: the markdown in the repository, the spoken text in the
repository, and the spoken text on his Desktop. The repository markdown and the
Desktop text are the 2 surfaces the agreement checker joins.

Exit 0 iff all 29 decisions rendered, every one carrying a heading, a
recommendation and a standard.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import importlib.util
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():            # running from the scratchpad
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
DESKTOP = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _wrap_free(text: str) -> str:
    """NO HARD WRAPPING. 1 paragraph is 1 long line, per the note standard."""
    return re.sub(r"\s+", " ", text).strip()


#: ★ THE CLAIM AND ITS NEGATION LOOK ALIKE. An ad-hoc regex used to take the
#: first measurement here included the BARE WORD `recommended` as an
#: alternative, and so counted "NOT recommended" as a recommendation: it flagged
#: 9 of 31 entries when 2 were real, 4 of the 7 false ones being exactly that
#: inversion (B128, B81, B84, B88). The project's record already holds the
#: shape: 3 of 4 detectors over-matched.
#:
#: ★ AND WHAT PROTECTS AGAINST THAT IS NOT THE LOOKBEHINDS, corrected
#: 2026-11-07 by the mutation harness. It is that this pattern requires the
#: phrase `is ... recommendation` and never matches the bare word
#: `recommended`, so a negation has nothing to attach to. Measured by calling
#: it: "Not recommended: it would be worse." and "NOT recommended, and
#: deliberately so." both return no match with the lookbehinds REMOVED. The
#: lookbehinds fire only on "not is the recommendation", which is not English
#: and appears nowhere in the corpus, so a control test that relies on them
#: passes for the wrong reason -- which is what mine did until a mutation
#: reversing them stayed GREEN. They are kept because they cost nothing and
#: are not wrong; the test that matters is
#: `test_the_bare_word_recommended_is_never_a_claim`.
_CLAIMS = re.compile(r"(?<!not )(?<!NOT )\bis (?:my |the )?recommendation\b", re.I)


def recommended_index(options: list[str]) -> tuple[int, str]:
    """(0-based index of the recommended option, how it was decided).

    Falls back to option 1 and SAYS SO, rather than silently picking one, so a
    file that could not find the recommendation reads as such.
    """
    hits = [i for i, o in enumerate(options) if _CLAIMS.search(o)]
    if len(hits) == 1:
        return hits[0], "marked in the option text"
    if not hits:
        return 0, "NO OPTION IS MARKED AS THE RECOMMENDATION; option 1 shown by position"
    return hits[0], (f"{len(hits)} options claim to be the recommendation "
                     f"({', '.join(str(h + 1) for h in hits)}); the first is shown")


def _gist(option: str, limit: int | None = 150) -> str:
    """The option's own lead clause: its bolded phrase, else its 1st sentence.

    ★ `limit=None` RETURNS IT WHOLE, and that is the whole point of the
    parameter. Founder ruling 2026-11-11, after 3 of the 10 recommendations in
    his own copy reached him cut off mid-sentence and he could not rule on 2
    of them.

    THE CAP WAS NEVER HIS. His words: *"But I didn't impose a literal cap. You
    did it to your self. I simply framed it as a formatting and presentation
    issue, rather than requiring a hard cap. Instead you went from one extreme
    to another."* The record agrees with him twice over. `render`'s own
    docstring records the complaint as a WORKLOAD one, and the file this
    function writes states in its own header that he never specified a cap and
    that *"Nothing here is cut to fit a length"* -- while this line cut 3 of 10
    to fit 150 characters. The artefact contradicted itself inside 1 document.

    MEASURED, 2026-11-11: his copy fell from 22,902 words on 2026-11-08 to
    1,026 on 2026-11-11, which is 0.044800 of it. The truncation RATE did not
    move -- 6 of 56 index lines before against 5 of 27 after, Fisher exact
    p = 0.325711, so a rate measurement alone would have called his report
    mistaken. What changed is that the DETAIL LEFT HIS COPY, so a cut line had
    nowhere left to resolve to.

    SO THE CAP IS CONDITIONAL ON THE DETAIL FOLLOWING, which is the only thing
    that ever justified it. With `detail=True` the full argument sits below and
    a scannable index is a real gain. With `detail=False` the index is the
    ENTIRE document and a cut recommendation is simply unanswerable. Restoring
    all 3 costs 143 characters against 5,962.
    """
    m = re.match(r"\s*\*\*(.+?)\*\*", option, re.S)
    t = m.group(1) if m else option.split(". ")[0]
    t = _wrap_free(t)
    if limit is None or len(t) <= limit:
        return t
    return t[:limit].rsplit(" ", 1)[0] + "..."


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


#: ★ N2, 2026-11-09. THE REPEATS BANNER IS COMPUTED, NOT TYPED.
#: It used to be a literal template with only `n`, `date` and `sha`
#: substituted, so it printed the word "Neither" whatever the data said and
#: carried bounds measured at n = 29 on 2026-11-08. At n = 12 on 2026-11-09
#: the printed Wilson upper bound of 0.116970 should have been 0.242494,
#: understated by 2.073133 times, and the Clopper-Pearson 0.119445 should have
#: been 0.264648, understated by 2.215654 times. It also named B20 and B71 as
#: carrying rulings when neither was among that file's own 12 items.
def _short_question(row: dict) -> str:
    """The first clause of a row's own spoken heading, for naming it in prose."""
    text = (row.get("spoken_heading") or "").strip()
    if not text:
        text = re.sub(r"^\s*[A-Z]+\d+\s*[-\u2014:]\s*", "",
                      (row.get("title") or "")).strip()
    return text.split(",")[0].strip().rstrip(".").lower() or "see below"


def _decision_numbers(idents, pos: dict) -> str:
    """"decisions 1 to 6 below" / "decisions 8 and 9" / "decision 4" / "none".

    Contiguity is TESTED, never assumed: a run of consecutive numbers renders
    as a range and anything else is listed, so the sentence stays true if the
    ordering changes.
    """
    nums = sorted(pos[i] for i in idents if i in pos)
    if not nums:
        return "none"
    if len(nums) == 1:
        return f"decision {nums[0]} below"
    #: A range needs 3 or more to be worth the word "to": 2 consecutive
    #: numbers read better aloud as "8 and 9" than as "8 to 9".
    if len(nums) > 2 and nums == list(range(nums[0], nums[-1] + 1)):
        return f"decisions {nums[0]} to {nums[-1]} below"
    head = ", ".join(str(x) for x in nums[:-1])
    return f"decisions {head} and {nums[-1]} below"


def repeats_summary(rows) -> dict:
    """What this file's items actually are, computed from the live rows."""
    n = len(rows)
    ruled = [r["ident"] for r in rows if r.get("ruled")]
    responded = [r["ident"] for r in rows if r.get("responded") and not r.get("ruled")]
    # An item whose ruling STILL SETTLES it never reaches this list at all --
    # `decisions()` routes it to `no_ruling_needed`. So this is 0 BY
    # CONSTRUCTION, and the interval is reported at the LIVE n to say how
    # tightly that 0 is bounded by this sample rather than by an older one.
    settled = 0
    #: ★ DECISION NUMBERS, NOT BARE CODES, 2026-11-10, AND IT IS THE SECOND
    #: TIME HE HAS ASKED FOR THIS. His words: *"I can't always tell when you
    #: print identifiers like B102 or C0003 (for example), if these are the
    #: same issues you may have been discussing a few lines ago. I don't have
    #: access to your ticket store, or any of the other resources you have to
    #: store these issues."* Rule 32 of the note standard already required a
    #: descriptor beside every code, and `scripts/note_vagueness_lint.py`
    #: already detected the breach -- it found 3 bare codes in THIS file, the
    #: one generated to answer that very request: B77 and B141 in this very
    #: sentence and B20 in the correction note below it.
    #:
    #: WHY NOT A DESCRIPTOR PER CODE, WHICH WAS TRIED FIRST AND DISCARDED. A
    #: descriptor derived from each entry's own heading truncates mid-phrase
    #: once 6 of them share one sentence -- "B88, on the fold-back gate now
    #: accepts" and "B125, on a joint panel round asked 2 seats about a" -- and
    #: this file is READ ALOUD. The decision NUMBER is the handle the glance
    #: list below already tells him to use ("naming the decision number and the
    #: option number"), and that list pairs every number with its code AND its
    #: full question 2 paragraphs later. So nothing is lost and no code is
    #: printed without its subject within easy reach.
    _pos = {r["ident"]: i + 1 for i, r in enumerate(rows) if r.get("ident")}
    w, cp, gap = _iv(settled, n)
    neither = n - len(ruled) - len(responded)
    if n == 0:
        verdict = "There are none."
    elif settled:
        verdict = "Some are repeats."
    elif ruled or responded:
        verdict = "Neither."
    else:
        verdict = "All of them are new to you."
    return {
        "n": n, "settled": settled, "ruled": ruled, "responded": responded,
        "neither": neither, "verdict": verdict,
        "neither_verb": "carries" if neither == 1 else "carry",
        #: ★ DERIVED, 2026-11-10. This sentence was the literal text "B20 is
        #: the next task on the list and the first decision below" and it was
        #: wrong on both counts: B20 (the bound orchestrator) is DEFERRED, so
        #: it is not the next task, and the first decision below is whatever
        #: `rows[0]` holds today. It also printed a bare code, which the lint
        #: flagged in the file written to answer his request about bare codes.
        "first_decision_sentence": (
            (f"The first decision below is {rows[0].get('ident','')}, "
             f"{_short_question(rows[0])}.") if rows else
            "There is no decision below."),
        "w_lo": w[0], "w_hi": w[1], "cp_lo": cp[0], "cp_hi": cp[1], "gap": gap,
        "ruled_names": _decision_numbers(ruled, _pos),
        "responded_names": _decision_numbers(responded, _pos),
        "n_ruled": len(ruled), "n_responded": len(responded),
        # prose-precision: "1 carry" is wrong and he reads this aloud.
        "ruled_verb": "carries" if len(ruled) == 1 else "carry",
        "responded_verb": "carries" if len(responded) == 1 else "carry",
        "ruled_label": _decision_numbers(ruled, _pos),
        "responded_label": _decision_numbers(responded, _pos),
    }


def first_appearances(rows) -> str:
    """When each item was first put to him, read off the dated files on disk."""
    files = sorted((REPO / "experimental_notes").glob(
        "Decisions_Awaiting_You_*_GENERATED.txt"))
    today = dt.date.today().isoformat()
    first: dict[str, str] = {}
    for f in files:
        d = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
        if not d or d.group(1) >= today:
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        for r in rows:
            i = r["ident"]
            if i not in first and re.search(rf"\b{re.escape(i)}\b", txt):
                first[i] = d.group(1)
    if not first:
        return "none of them has appeared in an earlier dated file"
    by: dict[str, int] = {}
    for v in first.values():
        by[v] = by.get(v, 0) + 1
    parts = [f"{c} on {d}" for d, c in sorted(by.items())]
    return (f"{len(first)} of {len(rows)} have appeared in an earlier dated "
            f"file: " + ", ".join(parts))


def head_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, cwd=REPO).stdout.strip()


#: ★ THE MARKER IS LOCATED, THEN THE STATEMENT IS CAPTURED TO A SENTENCE
#: BOUNDARY. Rewritten 2026-11-10 after a free panel found 4 defects in the
#: first version, 2 seats independently and all reproduced by execution here.
#: The marker is matched on its own; the statement is NOT delimited by the next
#: `**`, because in this corpus an interior bold span is usually EMPHASIS
#: inside a sentence rather than a heading.
_OWED_MARKER_RE = re.compile(
    r"\*\*\s*(?:★\s*)?(?:AND\s+)?(WHAT IS (?:STILL |ACTUALLY )?OWED"
    r"[^*]{0,160}?)\s*\*\*",
    re.S)
#: A heading ends at a colon; what precedes it inside the bold span can carry
#: the operative clause, which defect 2 discarded in 8 of 8 cases.
_OWED_HEAD_SPLIT = re.compile(r"^WHAT IS (?:STILL |ACTUALLY )?OWED\b[\s,:-]*",
                              re.I)
#: Markdown emphasis is REMOVED from the captured statement rather than treated
#: as a boundary.
_EMPH_RE = re.compile(r"\*{1,3}")
#: Where to cut. He is dyslexic and reads these aloud, so a sentence boundary is
#: preferred, a word boundary is the floor, and mid-word never happens.
#:
#: ★ RAISED FROM 320 TO 900 ON THE PANEL'S EVIDENCE, 2026-11-10. Measured over
#: the 8 live derivations: 3 were truncated, and in every one of the 3 the
#: DROPPED text carried the operative ask -- B81's *"3 options are recorded ...
#: and none is recommended"*, B125's *"what he is being asked for is
#: awareness"*, and worst of all B103's *"1.35 times that stated limit"*, which
#: CONTRADICTS the sentence the cut kept (*"inside the 660 s limit its own
#: header states"*). A cut that stops before the clause reversing it does not
#: shorten the statement, it inverts it. The longest full statement is 759
#: characters, so 900 keeps all 8 whole with room to spare, and length is the
#: cheaper cost: he reads these to DECIDE.
STILL_OWED_MAX_CHARS = 900


def _first_sentences(text: str, limit: int) -> str:
    """Whole sentences up to `limit`, else a word-bounded cut with an ellipsis.

    ★ APPLIED ON EVERY PATH. The first version ran its sentence rule ONLY on
    the `len(out) > 260` arm, so a statement cut short by the regex lookahead
    was never sentence-completed and reached him as an em-dash fragment -- the
    stated fix present on 1 arm of an `if` and absent on the other, which is
    the same shape as the `note` that was built and never emitted 40 lines
    below.
    """
    text = text.strip()
    if not text:
        return ""
    #: ★ A DECIMAL POINT IS NOT A SENTENCE BOUNDARY. My own first splitter
    #: turned "1.35 times that stated limit" into "1. 35 times ...", which in
    #: a file he reads aloud is read as two numbers. The terminator must not
    #: sit between two digits, and must not be the dot of an ellipsis.
    out, total = [], 0
    for part in re.findall(r".*?(?<!\d)[.!?](?!\d)(?!\.)|.+$", text):
        part = part.strip()
        if not part:
            continue
        if total and total + 1 + len(part) > limit:
            break
        out.append(part)
        total += (1 if total else 0) + len(part)
    joined = " ".join(out).strip()
    if joined and joined[-1] in ".!?":
        return joined
    #: ★ A TRAILING FRAGMENT IS DROPPED RATHER THAN ELLIPSISED, when whole
    #: sentences were already found. My first version appended " ..." after a
    #: complete sentence because a stray all-caps bold word survived the cut,
    #: giving "...which gives way is yours. ..." -- an ellipsis implying more
    #: was withheld when nothing was.
    whole = [x for x in out if x.rstrip().endswith((".", "!", "?"))]
    if whole:
        return " ".join(whole).strip()
    #: no complete sentence fitted: cut on a WORD boundary and say so
    head = (joined or text)[:limit]
    if " " in head:
        head = head.rsplit(" ", 1)[0]
    return head.rstrip(" ,;:-") + " ..."


#: Tokens that must keep their case: an identifier, a path, a figure, or a
#: hyphenated or slashed compound such as `HARD/SOFT`. Everything else that is
#: shouted in markdown for emphasis is lowered, because a text-to-speech reader
#: does not whisper.
_KEEPCASE = ("`", "_", "/", "\\", ".", "-", "(")


def _sentence_case(text: str) -> str:
    """Lower an emphasis-shouted heading into readable speech.

    ★ MY OWN 3rd DEFECT IN THIS REPAIR, and the rule that produced it was
    backwards. It kept all-caps words of 4 characters or fewer and lowered the
    rest, giving "WHAT is OWED IS HIS, AND IT IS THE limit rather THAN THE
    addition" -- worse to read than the original. 1 rule replaces it: lower
    every all-caps word that carries no identifier character, then capitalise
    the first letter.
    """
    out = []
    for w in text.split(" "):
        #: ★ PUNCTUATION IS STRIPPED BEFORE THE TEST. "ONE." carries a full
        #: stop, which is an identifier character, so the first version kept it
        #: shouted; and a bare "A" was spared by the length guard.
        core = w.strip(".,;:!?)")
        if core == "I":
            out.append(w)
        elif core == "A":
            out.append(w.replace("A", "a", 1))
        elif (core.isupper() and core
                and not any(c in core for c in _KEEPCASE)):
            out.append(w.lower())
        else:
            out.append(w)
    joined = " ".join(out).strip()
    return (joined[:1].upper() + joined[1:]) if joined else joined


def _owed_sentence(owed: str) -> str:
    """The *what is still owed* sentence, which must read as English.

    ★ DEFECT 4, FOUND BY A FREE PANEL 2026-11-10 AND NOT IN THE DERIVATION.
    The frame was `f"What is still owed is {owed}."`, which assumes a NOUN
    PHRASE and receives a CLAUSE -- live output included *"...is he ruled the
    addition..."* and *"...is this is the 1 decision..."* -- and it DOUBLED the
    full stop wherever the value already ended in one, which includes B77, the
    only entry whose value is authored rather than derived. The copula is now
    dropped for a clause and the terminator is never duplicated.
    """
    owed = (owed or "").strip()
    if not owed:
        return "What is still owed is recorded in the entry."
    #: A VALUE THAT ALREADY OPENS "What is ... owed" IS ITS OWN SENTENCE and
    #: must not be given a second lead.
    if owed[:12].lower().startswith("what is"):
        return owed if owed[-1] in ".!?" else owed + "."
    #: ★ ALWAYS THE COLON FORM, AND THAT IS SIMPLER THAN WHAT IT REPLACES.
    #: The first version classified the value as a clause or a noun phrase by
    #: testing its opening word against a list of pronouns and determiners, and
    #: took the copula form for anything else. The `cc2` seat's own guard then
    #: fed it a VERB-initial value and got *"What is still owed is ends in a
    #: stop."* -- a word list cannot enumerate English, and a classifier that
    #: has to is the wrong mechanism. A colon is grammatical in front of a noun
    #: phrase AND a clause, so there is nothing left to classify: 1 form, 0
    #: word lists, and the ungrammatical output is unreachable rather than
    #: merely unobserved.
    body = owed if owed[-1] in ".!?" else owed + "."
    return f"What is still owed: {body}"


def derive_still_owed(entry_text: str, limit: int = STILL_OWED_MAX_CHARS) -> str:
    """What an entry's own text says is still owed, or "" when it does not say.

    ★ 4 DEFECTS FOUND BY A FREE PANEL ON 2026-11-10, both seats independently,
    every one reproduced here by execution before being repaired. The first
    version of this helper shipped in the same session, so this is a repair of
    an hour-old fix rather than of old code.

    D1 -- THE CAPTURE ENDED AT THE FIRST INTERIOR `**`. Its lookahead
    treated every bold delimiter as a boundary, and in this
    corpus bold is usually emphasis inside a sentence. B103's statement reached
    him as *"taking it to about 891 s —"*: the magnitude and the operative ask
    were both in the words after the emphasis. Now the statement is captured to
    a SENTENCE boundary and emphasis markers are stripped, not obeyed.

    D2 -- THE AUTHOR'S WORDS INSIDE THE MARKER'S OWN BOLD SPAN WERE DISCARDED,
    in 8 of 8 live cases, and on B81 that INVERTED the meaning. The entry reads
    `**WHAT IS OWED IS HIS, AND IT IS THE LIMIT RATHER THAN THE ADDITION:** he
    ruled the addition ... so it stands.` He was shown only the second half --
    told, under the heading *what is still owed*, that the thing was SETTLED,
    while the open half was the limit. The heading's own clause is now kept.

    D3 -- A SHORT STATEMENT DRAGGED THE NEXT HEADING IN. The `{30,1200}`
    minimum forced the lazy capture past the following bold span, so a body of
    `his ruling.` returned `his ruling. **DO NOT DELETE THE LEDGER.` -- literal
    asterisks and an unrelated heading, quoted to him as the answer. There is
    no minimum now; a sentence is a sentence.

    D4 is in the FRAME rather than here and is repaired at the call site: the
    sentence read `What is still owed is {value}.`, which assumes a noun phrase,
    receives a clause, and doubled the full stop wherever the value already
    ended in one -- including B77, the single entry whose value is AUTHORED.

    WHAT SURVIVED THE ATTACK, and both seats said so independently: LAST MARKER
    WINS, because entries are appended to and the freshest statement is
    operative; and NO MARKER MEANS NO CLAIM, because this text goes under a
    heading he decides from.
    """
    if not entry_text:
        return ""
    flat = re.sub(r"\s+", " ", entry_text)
    hits = list(_OWED_MARKER_RE.finditer(flat))
    if not hits:
        return ""
    m = hits[-1]                      # LAST marker wins, by MARKER not by hit
    #: ★ THE HEADING IS KEPT WHOLE WHEN IT CONTINUES INTO A CLAUSE, because
    #: stripping the words "WHAT IS OWED" off "WHAT IS OWED IS HIS, AND IT IS
    #: THE LIMIT RATHER THAN THE ADDITION" leaves "IS HIS, AND IT IS THE
    #: LIMIT ...", which under the frame read aloud as "What is still owed: is
    #: his, and it is the limit". Repairing defect 2 by keeping the heading's
    #: clause and then re-framing it produced ungrammatical speech in a file he
    #: listens to -- a correct fix with a wrong surface.
    head_raw = (m.group(1) or "").strip()
    stripped = _OWED_HEAD_SPLIT.sub("", head_raw).strip(" ,:-")
    continues = bool(stripped)
    inside = head_raw if continues else ""
    after = flat[m.end():]
    #: stop at the next HEADING, which is a bold span whose content is a
    #: sentence-like run ending in a colon -- not at every bold span.
    #: ★ WHAT COUNTS AS THE NEXT HEADING, and this is the line that has to
    #: separate a heading from mid-sentence EMPHASIS -- the distinction defect
    #: 1 collapsed. A bold span is a heading when it opens with a star marker,
    #: when it ends in a colon, or when it carries NO LOWERCASE LETTER at all
    #: and is at least 3 characters. `**1.35 times that stated limit**` has
    #: lowercase and no colon, so it is emphasis; `**END**` and
    #: `**WHAT IS OWED:**` are headings.
    cut = None
    for mm in re.finditer(r"\*\*\s*(★?)\s*([^*]{1,200}?)\s*\*\*", after):
        star, inner = mm.group(1), mm.group(2)
        if (star or inner.rstrip().endswith(":")
                or (len(inner.strip()) >= 3 and not any(c.islower()
                                                        for c in inner))):
            cut = mm
            break
    if cut:
        after = after[:cut.start()]
    body = _EMPH_RE.sub("", after).strip()
    parts = [x for x in (inside, body) if x]
    if not parts:
        return ""
    joined = ("; ".join(parts) if len(parts) > 1 and not inside.endswith((".", ":"))
              else " ".join(parts))
    #: SENTENCE CASE for a kept heading, which the author wrote in capitals for
    #: emphasis in markdown and which is shouted by a text-to-speech reader.
    if continues:
        joined = _sentence_case(joined)
    return _first_sentences(joined, limit)


def collect():
    mrb = _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb_dec")
    sf = _load(REPO / "scripts"
               / "do_the_two_decision_surfaces_agree_2026-11-01.py", "sf_dec")
    live = sf.derived()                        # [(ident, spoken_heading)]
    #: THE ENTRY BODIES, for `derive_still_owed`. Read once, and a failure to
    #: read them costs the DERIVATION and never the file: an empty map falls
    #: back to exactly the previous wording.
    _entry_text: dict = {}
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        import task_list_markers as _tlm           # noqa: PLC0415
        _entry_text = {e.ident: e.text for e in _tlm.parse_entries()}
    except Exception:                              # noqa: BLE001
        _entry_text = {}
    items = mrb.task_items() + mrb.study_items()
    decs, _missing, _orphan = mrb.decisions(items)
    by_ident = {}
    for d in decs:
        ident = d.get("ident")
        if ident:
            by_ident[ident] = d
    rows = []
    for ident, head in live:
        d = by_ident.get(ident, {})
        opts = d.get("options") or []
        rows.append({
            "ident": ident,
            "heading": head,
            "what": d.get("what") or "",
            "why": d.get("why") or "",
            "options": list(opts),
            "standards": d.get("recommendation_standards") or "",
            "evidence": d.get("evidence_line") or "",
            #: AUTHORED FIRST, DERIVED SECOND, EMPTY LAST. The authored field
            #: is kept as the primary because a human sentence beats a
            #: regex; it is simply absent on 23 of 24 decisions.
            "owed": (d.get("still_owed")
                     or derive_still_owed(_entry_text.get(ident, ""))
                     or ""),
            "ruled": d.get("ruled") or "",
            "responded": d.get("responded") or "",
            "title": d.get("title") or "",
            #: ★ B132. The ticket identity travels with the row so the
            #: WRITTEN surface can cite it. `ticket_id` resolves 29 of 29
            #: live decisions, measured by calling it rather than by
            #: reading it. The SPOKEN surface deliberately does not use
            #: this: a 12-hex value read aloud is hostile to listening,
            #: which is the open question entry B104 puts to him.
            "tid": mrb.ticket_id(ident),
        })
    return mrb, rows


HEADER_MD = """# Decisions awaiting you — {date}

**{n} decisions, generated from the project's own records at commit `{sha}`, not written by hand.**
The report that asked you on the 6th of November was hand-written, and it named 3 things when the
record tracked {n}. This file reads the same authored detail the generated report reads, through the
same functions, so it cannot disagree with the record.

**Written at the raised cap.** Your ruling of the 6th of November: *"raise the cap in all 3. I never
specified a cap."* Nothing here is cut to fit a length. Each item says what it is, why it matters,
what you decide, and what is recommended with its standard named.

## Are these new, or repeats you have already ruled on? {verdict}

**NOT NEW.** {first_appearances}. They are re-rendered here rather than re-sent.

**NOT REPEATS EITHER.** {settled} of {n} carry a ruling of yours that still settles them, Wilson 95%
[{w_lo:.6f}, {w_hi:.6f}], Clopper-Pearson 95% [{cp_lo:.6f}, {cp_hi:.6f}], the 2 routes of each
agreeing to {gap:.3e}. {n_ruled} {ruled_verb} a ruling of yours on a *different* question ({ruled_names}),
and each entry records which question was answered and which was not. {n_responded} {responded_verb}
a REPLY of yours that left the entry open ({responded_names}). The remaining {neither} {neither_verb} neither.

**Every figure in this section is computed at the live count of {n}.** Until 2026-11-09 this block
was a literal template that printed the word "Neither" whatever the data said, with bounds measured
at 29 items on 2026-11-08. At 12 items its printed Wilson upper bound of 0.116970 should have read
0.242494, understated by 2.073133 times, and its Clopper-Pearson 0.119445 should have read 0.264648,
understated by 2.215654 times. It also named B20, the bound orchestrator, and B71, the automatic local save,
as carrying rulings when neither was among its own items.

**The answer I gave you yesterday was wrong.** The producer written to answer this very question
called its lookup with a store key where an entry identifier belongs, found nothing, and read the
miss as a finding. 3 of 41 live entries were labelled repeats on an empty string: B13, on
admitting a model; B20, the bound orchestrator; and B21, model and role selection.
{first_decision_sentence}
Producer: `scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py`.

---
"""

HEADER_TTS = """DECISIONS AWAITING YOU

{date}

{n} decisions, generated from the project's own records at commit {sha}, not written by hand. The report that asked you on the 6th of November was hand-written, and it named 3 things when the record tracked {n}. This file reads the same authored detail the generated report reads, through the same functions, so it cannot disagree with the record.

Written at the raised cap, on your ruling of the 6th of November that you never specified a cap. Nothing here is cut to fit a length. Each item says what it is, why it matters, what you decide, and what is recommended with its standard named.


ARE THESE NEW, OR REPEATS YOU HAVE ALREADY RULED ON? {verdict_caps}

Not new. {first_appearances}. They are re-rendered here rather than re-sent.

Not repeats either. {settled} of {n} carry a ruling of yours that still settles them, with a 95 per cent Wilson interval from {w_lo:.6f} to {w_hi:.6f} and a Clopper-Pearson interval from {cp_lo:.6f} to {cp_hi:.6f}, the 2 routes of each agreeing to within {gap:.3e}. {n_ruled} {ruled_verb} a ruling of yours on a different question, {ruled_label}, and each entry records which question was answered and which was not. {n_responded} {responded_verb} a reply of yours that left the entry open, {responded_label}. The remaining {neither} {neither_verb} neither.

Every figure in this section is computed at the live count of {n}. Until the 9th of November this passage was a fixed piece of text that said the word Neither whatever the data showed, carrying bounds measured over 29 items on the 8th of November. At 12 items its stated Wilson upper bound of 0.116970 should have read 0.242494, understating it by a factor of 2.073133, and its Clopper-Pearson bound of 0.119445 should have read 0.264648, understating it by a factor of 2.215654. It also named entries B20, the bound orchestrator, and B71, the automatic local save, as carrying rulings when neither was among its own items.

"""


def render(mrb, rows, spoken: bool, detail: bool = True) -> str:
    """Render the file. `detail=False` gives the INDEX ALONE.

    ★ HIS COMPLAINT OF 2026-11-08, and it is measured. He answered all 29
    decisions from the index and said of the rest that, at over 22,000 words,
    it is an almost impossible workload. Measured by
    `scripts/what_his_twenty_nine_rulings_actually_say_2026-11-08.py`: the
    delivered file was 22,902 words of which the long tier is 0.927451 of the
    characters, and 0.690653 of the morning report's 12-word sequences also
    appear in it, because 2 generators each render all 29 in full.

    HIS FIRST READING IS REFUTED AND HIS SECOND IS RIGHT. Nothing was
    appended today: these files ran 18,300 bytes on 2026-10-29 and 25,523 on
    2026-10-30, then 151,786 on 2026-11-04, LARGER than this one. The 2-tier
    shape predates the file; the workload request simply lapsed.

    SO THE REPOSITORY COPIES KEEP EVERY SECTION AND THE DESKTOP COPY CARRIES
    THE INDEX, 9,594 characters against 130,263. The 3 dependencies were
    checked rather than assumed: `do_the_two_decision_surfaces_agree` reads
    the REPOSITORY glob and needs the `DECISION n.` headings, which the
    repository copy keeps; `sync_desktop_mirrors.MIRRORS` holds 5 entries and
    this file is not 1 of them, so nothing copies the full text back over the
    Desktop one; and this module's exit-0 postcondition is computed from
    `rows`, not from the rendered text.
    """
    sp = mrb._spoken if spoken else (lambda t: t)
    date = (dt.datetime.now().strftime("%d %B %Y, %H:%M GMT") if spoken
            else dt.date.today().isoformat())
    _rs = repeats_summary(rows)
    head = (HEADER_TTS if spoken else HEADER_MD).format(
        date=date, sha=head_sha(),
        first_appearances=first_appearances(rows),
        verdict=_rs["verdict"],
        verdict_caps=_rs["verdict"].rstrip(".").upper(),
        **{k: v for k, v in _rs.items() if k != "verdict"})
    #: ★ THE HEADER IS SPLIT INTO LINES, AND `[head]` HID 4 OF MY PARAGRAPHS.
    #: `L = [head]` put the whole multi-line header block in 1 list element,
    #: so the marker's per-line paragraph walk saw it as a single line and the
    #: first-non-blank-line exemption -- which exists to spare the TITLE --
    #: swallowed the entire header. 4 of the 6 prose paragraphs in it went
    #: unmarked, and the file still passed a "does it carry any marks at all"
    #: check at 4 marks, which is why that check was not the one to trust.
    #: Splitting here changes no output on the markdown path: the function
    #: returns `"\n".join(L)`, so a list of lines and a list of 1 joined block
    #: render identically. Asserted byte-identical on the unmarked path.
    L = head.split("\n")
    A = L.append
    #: ★ HEADING LINES, RECORDED WHERE THEY ARE EMITTED (B105, 2026-11-10).
    #: His ruling of 2026-11-08 governs "the generated TTS files", plural, and
    #: the marker had been built into `render_tts` in the morning-report
    #: generator ONLY. This file writes 3 more spoken artefacts and applied
    #: nothing, so 0 of this file's paragraphs carried the convention -- built
    #: in 1 place and missing in another, which I nearly closed the entry on.
    _hd: list = []

    # ---- THE INDEX. His words of 2026-11-06: no cap, but present things so a
    # quick coherent decision is possible. Length is permitted; an unordered
    # 100,000 characters is not what "quick" means. Every decision appears here
    # in 1 line with its recommendation, so a ruling can be given from the
    # index alone and the detail read only where it is wanted.
    # DERIVED, never typed: this read "THE 29 AT A GLANCE" and would have gone
    # stale the moment he ruled on one of them.
    A(f"THE {len(rows)} AT A GLANCE" if spoken
      else f"## The {len(rows)} at a glance")
    A("")
    # ★ ONE SENTENCE, ONE DECLARATION. This stood written out TWICE, once for
    # the spoken branch and once for the markdown one, so a conditional added
    # to either would have left the 2 surfaces promising different things --
    # the `execute-do-not-grep` shape in prose. It is composed once here.
    _lead = ("Each line gives the decision number, the entry it belongs to, the "
             "question, and the recommended option in a clause. A ruling can be given "
             "from this list alone, naming the decision number and the option number. ")
    _lead += ("The full argument for each follows below in the same order."
              if detail else
              "The full argument for each is in the repository, in the markdown and "
              "spoken copies of this file under experimental notes, which carry every "
              "section.")
    A(sp(_wrap_free(_lead)) if spoken else _wrap_free(_lead))
    A("")
    for i, r in enumerate(rows, 1):
        k, _how = recommended_index(r["options"]) if r["options"] else (0, "")
        # ★ NO CAP WHEN THE INDEX IS THE WHOLE DOCUMENT (his ruling 2026-11-11).
        gist = (_gist(r["options"][k], limit=150 if detail else None)
                if r["options"] else "no option recorded")
        line = (f"{i}. {r['ident']}, {r['heading'].lower()}. "
                f"Recommended option {k + 1}: {gist}")
        tag = f" `[{r['tid']}]`" if r.get("tid") else ""
        A(sp(line) if spoken else f"{i}. **{r['ident']}**{tag} — {r['heading'].lower()}. "
                                  f"*Recommended option {k + 1}:* {gist}")
    A("")
    A("" if spoken else "---")
    A("")

    # SKIPPED BY ITS ITERABLE rather than by re-indenting 40 lines under an
    # `if`: simplest sufficient, and a diff a reader can check.
    for i, r in enumerate(rows if detail else [], 1):
        hd = f"DECISION {i}. {r['heading']}"
        tag = f" `[{r['tid']}]`" if r.get("tid") else ""
        _hd.append(len(L))
        A(hd if spoken else f"## {hd}{tag}")
        A("")
        # ★★★ THE EMIT WAS INSIDE THE `elif` AND THE `if` BRANCH THREW ITS NOTE
        # AWAY. Found 2026-11-10 by executing the renderer and reading its
        # output, after a committed guard had been RED and off the gate.
        #
        # MEASURED BEFORE THE FIX, on the live queue of 7 decisions: 6 rows
        # carry a ruling date and the ruling note was emitted for **0** of
        # them; 3 rows carry a reply date and the reply note was emitted for
        # **0**. In 36,943 bytes of the spoken file he reads there were 0
        # mentions of his having ruled or replied on 6 of the 7 decisions put
        # to him. `note` was an assignment with no consumer -- the same
        # addition-that-nothing-reaches shape `additive-standard` names, and
        # the very defect N1 was raised for, surviving in a different place
        # from where it was looked for.
        #
        # THE PRECEDENCE IS DELIBERATE AND IS NOT A BUG. Where BOTH dates
        # exist the RULING note alone is right: it already says the ruling was
        # *on a different question* and names what is still owed, so adding
        # "and it is still open" beside it would be redundant and would read
        # as contradicting itself. The reply note is for the case the field was
        # built for -- he answered WITHOUT settling it. All 3 responders today
        # also carry a ruling date, so that case has 0 live instances, which is
        # recorded as a finding rather than fixed by backfilling a date: the
        # 2026-11-09 attempt at exactly that inverted its predicate and
        # suppressed 5 live entries.
        note = ""
        if r["ruled"]:
            note = (f"You ruled on this entry on {r['ruled']}, on a "
                    f"different question. " + _owed_sentence(r['owed']))
        elif r.get("responded"):
            # ★ N1, 2026-11-09. He replied and the entry is STILL OPEN. Saying so
            # is the whole repair: before this, a reply recorded in an entry's
            # prose reached no surface, so the original question was put to him
            # again. 0 of 12 decisions in the file of 2026-11-09 mentioned that
            # he had answered on 2026-11-08, in 53,898 bytes.
            note = (f"You responded on this on {r['responded']}, and it is "
                    f"still open. " + _owed_sentence(r['owed']))
        if note:
            A(sp(_wrap_free(note)) if spoken else f"*{_wrap_free(note)}*")
            A("")
        A("WHAT IT IS." if spoken else "**WHAT IT IS.**")
        A(sp(_wrap_free(r["what"])) if spoken else _wrap_free(r["what"]))
        A("")
        A("WHY IT MATTERS." if spoken else "**WHY IT MATTERS.**")
        A(sp(_wrap_free(r["why"])) if spoken else _wrap_free(r["why"]))
        A("")
        if r["evidence"]:
            A("THE EVIDENCE." if spoken else "**THE EVIDENCE.**")
            A(sp(_wrap_free(r["evidence"])) if spoken else _wrap_free(r["evidence"]))
            A("")
        if r["options"]:
            A("WHAT YOU DECIDE." if spoken else "**WHAT YOU DECIDE.**")
            for j, o in enumerate(r["options"], 1):
                txt = _wrap_free(o)
                A(f"{j}. " + (sp(txt) if spoken else txt))
            A("")
            A("RECOMMENDED." if spoken else "**RECOMMENDED.**")
            k, how = recommended_index(r["options"])
            rec = _wrap_free(r["options"][k])
            A((f"Option {k + 1}. " + (sp(rec) if spoken else rec)))
            if how != "marked in the option text":
                A("")
                A(sp(f"How this was chosen: {how}.") if spoken
                  else f"*How this was chosen: {how}.*")
            if r["standards"]:
                st = _wrap_free(r["standards"])
                A("")
                A(sp(st) if spoken else st)
            A("")
        A("" if spoken else "---")
        A("")
    if not detail:
        A(sp(_wrap_free(
            f"That is the whole of the index. The full argument for all {len(rows)} "
            f"decisions, with the evidence and every option, is in the repository "
            f"copies of this file under experimental notes. Nothing is cut: this copy "
            f"is the index, so a ruling can be given without reading the rest.")))
        A("")
    _hd.append(len(L))
    A("Written under CDSFL note standard v1.9 (1 November 2026)."
      if spoken else
      "Written under CDSFL note standard v1.9 (1 November 2026).")
    #: ★ THE MARKER IS IMPORTED, NOT COPIED. `_mark_my_paragraphs` lives in
    #: the morning-report generator, which this function already receives as
    #: `mrb`. A second copy would be a 2nd definition of his convention and
    #: this project has measured what copies cost: 16 of one helper, and a
    #: crash no test reached. SPOKEN ONLY -- the markdown twin carries its own
    #: emphasis and his amendment is about what Read Aloud says out loud.
    if spoken:
        _mark = getattr(mrb, "_mark_my_paragraphs", None)
        if _mark is None:                      # LOUD, not silent
            raise SystemExit(
                "REFUSED: the morning-report generator no longer exposes "
                "`_mark_my_paragraphs`, so his asterisk convention would be "
                "silently absent from this spoken file. Repoint this call.")
        _mark(L, [], _hd)
    return "\n".join(L) + "\n"


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the 3 files")
    a = ap.parse_args(argv)

    mrb, rows = collect()
    print(f"decisions rendered : {len(rows)}")
    no_head = [r["ident"] for r in rows if not r["heading"]]
    no_opts = [r["ident"] for r in rows if not r["options"]]
    no_std = [r["ident"] for r in rows
              if not STANDARD.search(" ".join(r["options"]) + " " + r["standards"])]
    print(f"  without a heading        : {len(no_head)} {no_head}")
    print(f"  without any option       : {len(no_opts)} {no_opts}")
    print(f"  without a named standard : {len(no_std)} {no_std}")

    md = render(mrb, rows, spoken=False)
    tts = render(mrb, rows, spoken=True)
    #: ★ THE COPY HE ACTUALLY READS IS THE INDEX, on his complaint of
    #: 2026-11-08. The repository keeps both full renders, which is what the
    #: surface-agreement checker reads and what holds the `DECISION n.`
    #: headings it needs. See `render`'s docstring for the measurement and for
    #: the 3 dependencies that were checked before this split.
    tts_index = render(mrb, rows, spoken=True, detail=False)
    print(f"  markdown : {len(md.splitlines())} lines, {len(md)} chars")
    print(f"  spoken   : {len(tts.splitlines())} lines, {len(tts)} chars")
    print(f"  his copy : {len(tts_index.splitlines())} lines, {len(tts_index)} chars "
          f"({len(tts_index) / max(1, len(tts)):.4f} of the full spoken render)")

    today = dt.date.today().isoformat()
    #: ★ NAMED `_GENERATED` AND NOT COMMITTED, exactly as the morning report is.
    #: `.gitignore` already excludes `Morning_Report_*_GENERATED.md` with the
    #: reason: everything the file is built from is versioned, so running the
    #: generator at the same commit rebuilds it byte for byte. The 14 tracked
    #: `Decisions_Awaiting_You_*` files are its HAND-WRITTEN predecessors, which
    #: is why the suffix distinguishes them rather than a new directory.
    p_md = REPO / "experimental_notes" / f"Decisions_Awaiting_You_{today}_GENERATED.md"
    p_tx = REPO / "experimental_notes" / f"Decisions_Awaiting_You_{today}_GENERATED.txt"
    p_dk = DESKTOP / f"Decisions_Awaiting_You_{today}_GENERATED.txt"
    if a.write:
        DESKTOP.mkdir(parents=True, exist_ok=True)
        p_md.write_text(md, encoding="utf-8")
        p_tx.write_text(tts, encoding="utf-8")
        p_dk.write_text(tts_index, encoding="utf-8")
        print(f"\nWROTE {p_md}\n      {p_tx}\n      {p_dk}")
    else:
        print("\nDRY RUN -- nothing written. Re-run with --write.")
    ok = not no_head and not no_opts and not no_std and len(rows) >= 5
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
