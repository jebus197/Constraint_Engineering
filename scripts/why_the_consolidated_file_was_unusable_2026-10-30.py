#!/usr/bin/env python3
"""Measure WHY the consolidated verdicts file of 2026-10-30 could not be ruled on.

THE COMPLAINT THIS ANSWERS. The founder, 2026-10-30, on
`experimental_notes/All_Verdicts_Consolidated_2026-10-30.txt`: *"many of your
responses are simply much too vague and do not respect my requirements that all
tts outputs should carry clear plain English explanations, should provide
recommendations that meet our 3 formal project standards and should strive to
avoid repetition of the same issues in the same file, while avoiding
over-narration. Consequently much of this file is impossible for me to offer
meaningful verdicts on."*

4 charges, each turned into a predicate a run can fail:

  1. NO PLAIN-ENGLISH EXPLANATION OF THE SUBJECT. For each decision the file
     asks him to take, does the file ever say what the thing IS? Measured 2
     independent ways against the canonical entry text in
     `experimental_notes/CDSFL_MASTER_TASK_LIST.md`: (a) does the file carry any
     contiguous 3-word phrase from the entry's own title, and (b) what share of
     the title's content words appear anywhere in the file. (a) is strict and
     (b) is lenient, so agreement between them is informative and disagreement
     localises the failure.

  2. NO RECOMMENDATION AGAINST THE 3 STANDARDS. The standards are named in the
     project's own directives as the additive standard, composability, and the
     simplest sufficient fix. Counted as a census of the delivered text.

  3. REPETITION OF THE SAME ISSUE IN ONE FILE. Near-duplicate sentence pairs by
     2 methods — token-set Jaccard and difflib's sequence ratio — reported with
     their agreement, because a single similarity threshold is a free parameter
     and 2 unrelated measures crossing the same pairs is not.

  4. OVER-NARRATION. The share of sentences whose subject is the author's own
     instruments and process rather than the decision in front of the reader.

AND A CONTROL, because a readability number on its own proves nothing. The same
2 readability indices are computed over the canonical task-list entries, which
are deliberately dense internal text. A file written as plain English for him
must score EASIER than its own dense source; scoring the same or harder is the
charge established rather than asserted.

CROSS-VERIFICATION. Flesch Reading Ease is syllable-based and Coleman-Liau is
character-based, so they share no intermediate quantity. Wilson intervals are
computed by a direct formula and by statsmodels. Proportions over a complete
enumeration are reported as censuses with no interval, per the project's rule
that a census gets none.

Read-only. Runs no experiment, spends nothing, calls no model.
"""
from __future__ import annotations

import argparse
import difflib
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DELIVERED = REPO / "experimental_notes" / "All_Verdicts_Consolidated_2026-10-30.txt"
ANNOTATED = Path("/Users/georgejackson/Developer_Projects/Responses/All_Verdicts_Consolidated_2026-10-30.txt")
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: The decisions the delivered file asks him to take, by the identifier it used.
#: These are the 6 OPEN entries of the master task list. The file names every
#: one of them by bare identifier.
DECISION_ENTRIES = ("B21", "B22", "B41", "B50", "C1", "R1")

#: The 3 standards his complaint names, as the directives spell them.
STANDARD_PATTERNS = {
    "additive": r"additive",
    "composability": r"composab",
    "simplest sufficient": r"simplest[ -]sufficient",
}

#: A sentence is narration about method when it names an instrument of the
#: author's rather than a property of the thing being decided.
INSTRUMENT_WORDS = (
    "producer", "script", "guard", "mutation", "wilson", "interval",
    "denominator", "census", "validator", "lint", "harvest", "ratchet",
    "re-measured", "remeasured", "measured today", "its own producer",
)
FIRST_PERSON = (" i ", " i'", "my ", " mine", " of mine", " me ", "i had", "i was")

STOPWORDS = {
    "the", "and", "that", "this", "with", "from", "they", "them", "then", "than",
    "have", "has", "had", "been", "were", "was", "are", "for", "not", "but",
    "its", "it's", "his", "her", "their", "which", "what", "when", "where",
    "into", "onto", "over", "under", "about", "there", "here", "also", "only",
    "does", "did", "doing", "because", "since", "while", "would", "could",
    "should", "will", "shall", "may", "might", "must", "one", "two", "all",
    "any", "each", "every", "more", "most", "less", "very", "such", "same",
    "other", "another", "both", "either", "neither", "nor", "yet", "still",
}


# --------------------------------------------------------------------------- #
# intervals
# --------------------------------------------------------------------------- #
def wilson_direct(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval by the closed formula. Cross-checked below."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return ((centre - half) / d, (centre + half) / d)


def wilson_statsmodels(k: int, n: int) -> tuple[float, float] | None:
    try:
        from statsmodels.stats.proportion import proportion_confint
    except Exception:
        return None
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return (float(lo), float(hi))


# --------------------------------------------------------------------------- #
# text handling
# --------------------------------------------------------------------------- #
def read_text_any_encoding(path: Path) -> str:
    """His annotated copies are CR-terminated and not valid UTF-8."""
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - latin-1 cannot fail
        txt = raw.decode("latin-1", errors="replace")
    return txt.replace("\r\n", "\n").replace("\r", "\n")


def sentences(text: str) -> list[str]:
    """Split on sentence-final punctuation, keeping it simple and auditable."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text)


def content_words(text: str) -> set[str]:
    return {w.lower() for w in words(text)
            if len(w) >= 4 and w.lower() not in STOPWORDS}


def syllables(word: str) -> int:
    """Vowel-group count with the standard silent-e and -le corrections."""
    w = word.lower().strip("'-")
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    if w.endswith("le") and len(w) > 2 and w[-3] not in "aeiouy":
        n = max(n, 1)
    return max(1, n)


def flesch_reading_ease(text: str) -> float:
    """Higher is easier. 60-70 is plain English; below 30 is very hard."""
    sents = sentences(text)
    ws = words(text)
    if not sents or not ws:
        return float("nan")
    syl = sum(syllables(w) for w in ws)
    return 206.835 - 1.015 * (len(ws) / len(sents)) - 84.6 * (syl / len(ws))


def coleman_liau(text: str) -> float:
    """US grade level from CHARACTERS and sentences only - no syllables."""
    sents = sentences(text)
    ws = words(text)
    if not sents or not ws:
        return float("nan")
    letters = sum(len(w) for w in ws)
    L = 100.0 * letters / len(ws)
    S = 100.0 * len(sents) / len(ws)
    return 0.0588 * L - 0.296 * S - 15.8


# --------------------------------------------------------------------------- #
# the canonical entry text, so the gloss test has something to test against
# --------------------------------------------------------------------------- #
def entry_titles() -> dict[str, str]:
    """Map identifier -> its own title sentence from the master task list."""
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm  # noqa: E402

    lines = TASK_LIST.read_text().splitlines()
    entries = tlm.parse_entries(TASK_LIST)
    starts = [e.line_no - 1 for e in entries]
    out: dict[str, str] = {}
    for k, e in enumerate(entries):
        if e.ident not in DECISION_ENTRIES:
            continue
        head = lines[starts[k]]
        # The title is the leading bold run, minus the identifier and its dot.
        m = re.match(r"\s*\*\*([A-Z]+\d*\.\s*)(.+?)\*\*", head)
        title = m.group(2) if m else head
        out[e.ident] = title.strip()
    return out


def entry_bodies() -> str:
    """All 6 decision entries' bodies, as the dense-text control."""
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm  # noqa: E402

    lines = TASK_LIST.read_text().splitlines()
    entries = tlm.parse_entries(TASK_LIST)
    starts = [e.line_no - 1 for e in entries]
    chunks = []
    for k, e in enumerate(entries):
        if e.ident in DECISION_ENTRIES:
            s, end = tlm.body_bounds(lines, starts, k)
            chunks.append("\n".join(lines[s:end]))
    return "\n\n".join(chunks)


def trigrams(text: str) -> set[tuple[str, ...]]:
    ws = [w.lower() for w in words(text)]
    return {tuple(ws[i:i + 3]) for i in range(len(ws) - 2)}


# --------------------------------------------------------------------------- #
# charge 1 - was the subject ever named
# --------------------------------------------------------------------------- #
def charge_subject_never_named(delivered: str) -> dict:
    titles = entry_titles()
    file_tris = trigrams(delivered)
    file_content = content_words(delivered)
    rows = []
    for ident in DECISION_ENTRIES:
        title = titles.get(ident, "")
        tris = trigrams(title)
        shared_tris = tris & file_tris
        tw = content_words(title)
        shared_cw = tw & file_content
        rows.append({
            "ident": ident,
            "title": title,
            "title_trigrams": len(tris),
            "trigrams_present": len(shared_tris),
            "example_trigram": " ".join(sorted(shared_tris)[0]) if shared_tris else "",
            "title_content_words": len(tw),
            "content_words_present": len(shared_cw),
            "content_word_share": (len(shared_cw) / len(tw)) if tw else float("nan"),
            "mentions_bare_id": bool(re.search(rf"\b{ident}\b", delivered)),
        })
    no_phrase = [r for r in rows if r["trigrams_present"] == 0]
    return {"rows": rows,
            "entries": len(rows),
            "no_shared_phrase": len(no_phrase),
            "named_by_bare_id": sum(1 for r in rows if r["mentions_bare_id"])}


# --------------------------------------------------------------------------- #
# charge 2 - the 3 standards
# --------------------------------------------------------------------------- #
def charge_standards_absent(delivered: str) -> dict:
    low = delivered.lower()
    return {name: len(re.findall(pat, low))
            for name, pat in STANDARD_PATTERNS.items()}


def _sections(delivered: str) -> dict[str, str]:
    """Attribute each paragraph to the identifier whose SECTION it sits in.

    CORRECTED 2026-10-30, because the first version accused correct text. It
    owned a paragraph only if that paragraph repeated the bare identifier, so a
    document that names an item once as a heading and then explains it over
    several paragraphs scored 0 recommendations while carrying one for every
    item. That is the guard-accusing-correct-code shape this project records 9
    instances of, committed by the checker.

    A paragraph opens a section when it STARTS with an identifier followed by a
    full stop; everything after it belongs to that identifier until the next
    such paragraph. Documents with no headings of that shape fall back to the
    paragraph-mention rule, so the older flat files still measure.
    """
    paras = [p for p in delivered.split("\n") if p.strip()]
    owned: dict[str, list[str]] = {i: [] for i in DECISION_ENTRIES}
    current: str | None = None
    #: A section also ENDS at the next document-level heading, or the last
    #: entry swallows everything after it -- which it did on the first run,
    #: reporting R1's section as 9,159 characters because it absorbed 4 later
    #: parts of the document. A rule with no terminator is not a rule.
    closes = re.compile(r"^\s*(PART\s+\d|APPENDIX|[A-Z][A-Z ,']{14,}$)")
    for p in paras:
        m = re.match(r"\s*([A-Z]+\d+)\.\s", p)
        if m and m.group(1) in owned:
            current = m.group(1)
        elif m:
            current = None  # a heading for something we are not tracking
        elif closes.match(p):
            current = None
        if current:
            owned[current].append(p)
    # Whether or not the document has headings, an item may be MENTIONED
    # outside its own section, so those paragraphs are swept in too. That one
    # sweep covers the heading-less case completely, which is why there is no
    # separate fallback: a mutation proved an `if not saw_heading` branch here
    # changed 0 outputs on both real documents and on a synthetic flat one, so
    # it was an addition nothing reached.
    for i in DECISION_ENTRIES:
        owned[i].extend(p for p in paras
                        if re.search(rf"\b{i}\b", p) and p not in owned[i])
    return {i: " ".join(ps) for i, ps in owned.items()}


def charge_recommendations(delivered: str) -> dict:
    """Does each decision's own SECTION carry a recommendation?"""
    sections = _sections(delivered)
    rows = []
    for ident in DECISION_ENTRIES:
        text = sections[ident].lower()
        rows.append({
            "ident": ident,
            "paragraphs": len([p for p in sections[ident].split("\n") if p.strip()]),
            "chars": len(sections[ident]),
            "has_recommendation": bool(re.search(
                r"recommend|i would|the advice is|my advice", text)),
            "names_the_standards": sum(
                1 for pat in STANDARD_PATTERNS.values() if re.search(pat, text)),
        })
    k = sum(1 for r in rows if r["has_recommendation"])
    return {"rows": rows, "with_recommendation": k, "of": len(rows)}


# --------------------------------------------------------------------------- #
# charge 3 - repetition
# --------------------------------------------------------------------------- #
def charge_repetition(delivered: str, jaccard_at: float = 0.60,
                      ratio_at: float = 0.75) -> dict:
    sents = [s for s in sentences(delivered) if len(words(s)) >= 6]
    sets = [content_words(s) for s in sents]
    by_jaccard: set[tuple[int, int]] = set()
    by_ratio: set[tuple[int, int]] = set()
    for i in range(len(sents)):
        for j in range(i + 1, len(sents)):
            a, b = sets[i], sets[j]
            if a or b:
                jac = len(a & b) / len(a | b)
                if jac >= jaccard_at:
                    by_jaccard.add((i, j))
            if difflib.SequenceMatcher(None, sents[i], sents[j]).ratio() >= ratio_at:
                by_ratio.add((i, j))
    both = by_jaccard & by_ratio
    pairs_possible = len(sents) * (len(sents) - 1) // 2
    # A TRUNCATED LIST STATES ITS REMAINDER. `examples` is a sample for a
    # reader, and `agreed_by_both` below is the full count, but a field named
    # `examples` beside a count is still a cap and must say so -- otherwise a
    # reader comparing the 2 cannot tell a sample from a complete list.
    _shown = 4
    examples = [(sents[i][:110], sents[j][:110]) for i, j in sorted(both)[:_shown]]
    return {"sentences": len(sents),
            "examples_shown": len(examples),
            "examples_withheld": max(0, len(both) - _shown),
            "pairs_possible": pairs_possible,
            "near_duplicate_by_jaccard": len(by_jaccard),
            "near_duplicate_by_difflib": len(by_ratio),
            "agreed_by_both": len(both),
            "examples": examples}


def most_repeated_phrase(delivered: str, n: int = 6) -> list[tuple[str, int]]:
    ws = [w.lower() for w in words(delivered)]
    counts: dict[tuple[str, ...], int] = {}
    for i in range(len(ws) - n + 1):
        g = tuple(ws[i:i + n])
        counts[g] = counts.get(g, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:5]
    return [(" ".join(g), c) for g, c in top if c > 1]


# --------------------------------------------------------------------------- #
# charge 4 - narration
# --------------------------------------------------------------------------- #
def charge_narration(delivered: str) -> dict:
    sents = sentences(delivered)
    narr = 0
    for s in sents:
        low = " " + s.lower() + " "
        if any(w in low for w in INSTRUMENT_WORDS) or any(f in low for f in FIRST_PERSON):
            narr += 1
    return {"sentences": len(sents), "narration_sentences": narr,
            "share": narr / len(sents) if sents else float("nan")}


# --------------------------------------------------------------------------- #
# the readability control
# --------------------------------------------------------------------------- #
def readability_against_control(delivered: str, control: str) -> dict:
    out = {}
    for label, text in (("delivered_file", delivered), ("dense_task_list_entries", control)):
        sents = sentences(text)
        ws = words(text)
        paras = [p for p in text.split("\n") if p.strip()]
        out[label] = {
            "flesch_reading_ease": flesch_reading_ease(text),
            "coleman_liau_grade": coleman_liau(text),
            "words": len(ws),
            "sentences": len(sents),
            "mean_words_per_sentence": len(ws) / len(sents) if sents else float("nan"),
            "paragraphs": len(paras),
            "longest_paragraph_chars": max((len(p) for p in paras), default=0),
            "paragraphs_over_400_chars": sum(1 for p in paras if len(p) > 400),
        }
    d, c = out["delivered_file"], out["dense_task_list_entries"]
    out["delivered_is_easier_than_its_source"] = bool(
        d["flesch_reading_ease"] > c["flesch_reading_ease"]
        and d["coleman_liau_grade"] < c["coleman_liau_grade"])
    out["both_indices_agree_on_direction"] = bool(
        (d["flesch_reading_ease"] > c["flesch_reading_ease"])
        == (d["coleman_liau_grade"] < c["coleman_liau_grade"]))
    return out


# --------------------------------------------------------------------------- #
# his own annotations, as the outcome measure
# --------------------------------------------------------------------------- #
def his_annotations_outcome() -> dict:
    """How many of his 27 annotations ask for an explanation rather than rule?"""
    if not ANNOTATED.exists():
        return {"available": False}
    txt = read_text_any_encoding(ANNOTATED)
    ann = [ln[1:].strip() for ln in txt.split("\n") if ln.lstrip().startswith("#")]
    asks_for_clarity = [a for a in ann if re.search(
        r"too vague|no explanation|no explanations|plain english|what are you "
        r"talking about|no idea what|tells me nothing|impossibly dense|"
        r"no recommend|no recommed|struggling to see", a, re.I)]
    gives_ruling = [a for a in ann if re.match(
        r"^(no\b|yes\b|y\b|already|if this matches|i think its safe|"
        r"build and implement|i accept)", a.strip(), re.I)]
    k, n = len(asks_for_clarity), len(ann)
    return {"available": True, "annotations": n,
            "asking_for_an_explanation": k,
            "share": k / n if n else float("nan"),
            "wilson_direct": wilson_direct(k, n),
            "wilson_statsmodels": wilson_statsmodels(k, n),
            "rulings_given_anyway": len(gives_ruling)}


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure why the consolidated verdicts file of 2026-10-30 "
                    "could not be ruled on. Read-only; spends nothing.")
    ap.add_argument("--file", type=Path, default=DELIVERED,
                    help="the delivered file to measure (default: the repo copy)")
    ap.add_argument("--jaccard-at", type=float, default=0.60)
    ap.add_argument("--ratio-at", type=float, default=0.75)
    args = ap.parse_args(argv)

    delivered = read_text_any_encoding(args.file)
    control = entry_bodies()

    print("=" * 74)
    print("WHY THE CONSOLIDATED FILE COULD NOT BE RULED ON")
    print(f"measured over: {args.file}")
    print("=" * 74)

    print("\n1. WAS THE SUBJECT EVER NAMED? (census of all 6 decision entries)")
    c1 = charge_subject_never_named(delivered)
    print(f"   entries named by bare identifier : {c1['named_by_bare_id']} of {c1['entries']}")
    print("   entries sharing NO 3-word phrase")
    print(f"   with their own canonical title   : {c1['no_shared_phrase']} of {c1['entries']}")
    print(f"   {'id':>4} {'tri shared':>11} {'content words':>14} {'share':>7}   title (truncated)")
    for r in c1["rows"]:
        print(f"   {r['ident']:>4} {r['trigrams_present']:>4}/{r['title_trigrams']:<6} "
              f"{r['content_words_present']:>5}/{r['title_content_words']:<8} "
              f"{r['content_word_share']:>7.4f}   {r['title'][:52]}")
    print("   A bare identifier is a pointer, not an explanation. The 3-word")
    print("   phrase test is strict; the content-word share is lenient. Where")
    print("   both are low, the file never told him what the item is.")

    print("\n2. DID ANY RECOMMENDATION MEET THE 3 STANDARDS? (census of the text)")
    c2 = charge_standards_absent(delivered)
    for name, n in c2.items():
        print(f"   mentions of {name:<22}: {n}")
    rec = charge_recommendations(delivered)
    print(f"   decision entries whose own SECTION carries a recommendation: "
          f"{rec['with_recommendation']} of {rec['of']}")
    for r in rec["rows"]:
        print(f"     {r['ident']:>4}  chars={r['chars']:<6} "
              f"recommendation={'YES' if r['has_recommendation'] else 'NO ':<4} "
              f"standards named={r['names_the_standards']} of 3")

    print("\n3. REPETITION WITHIN THE FILE (2 unrelated similarity measures)")
    c3 = charge_repetition(delivered, args.jaccard_at, args.ratio_at)
    print(f"   sentences of 6+ words            : {c3['sentences']}")
    print(f"   pairs examined                   : {c3['pairs_possible']}")
    print(f"   near-duplicate by token Jaccard  : {c3['near_duplicate_by_jaccard']}")
    print(f"   near-duplicate by difflib ratio  : {c3['near_duplicate_by_difflib']}")
    print(f"   pairs BOTH measures agree on     : {c3['agreed_by_both']}")
    for a, b in c3["examples"]:
        print(f"     - {a}")
        print(f"       {b}")
    for phrase, n in most_repeated_phrase(delivered):
        print(f"   repeated {n}x: \"{phrase}\"")

    print("\n4. OVER-NARRATION (census of this file's sentences)")
    c4 = charge_narration(delivered)
    print(f"   sentences                        : {c4['sentences']}")
    print(f"   sentences about instruments/self : {c4['narration_sentences']}")
    print(f"   share                            : {c4['share']:.4f}   (census, no interval)")

    print("\n5. READABILITY, AGAINST ITS OWN DENSE SOURCE AS A CONTROL")
    r = readability_against_control(delivered, control)
    for label in ("delivered_file", "dense_task_list_entries"):
        d = r[label]
        print(f"   {label}")
        print(f"      Flesch reading ease (higher=easier): {d['flesch_reading_ease']:>8.2f}")
        print(f"      Coleman-Liau grade (lower=easier)  : {d['coleman_liau_grade']:>8.2f}")
        print(f"      words / sentences / mean length    : {d['words']} / {d['sentences']} / {d['mean_words_per_sentence']:.1f}")
        print(f"      paragraphs, longest, over 400 chars: {d['paragraphs']} / {d['longest_paragraph_chars']} / {d['paragraphs_over_400_chars']}")
    print(f"   delivered file is easier than its source : {r['delivered_is_easier_than_its_source']}")
    print(f"   the 2 indices agree on the direction     : {r['both_indices_agree_on_direction']}")
    print("   The 2 indices share no intermediate quantity: one counts syllables,")
    print("   the other counts characters. Agreement is therefore informative.")

    print("\n6. HIS OWN ANNOTATIONS AS THE OUTCOME MEASURE")
    h = his_annotations_outcome()
    if not h.get("available"):
        print("   his annotated copy is not present on this machine")
    else:
        print(f"   annotations                      : {h['annotations']}")
        print(f"   asking for an explanation        : {h['asking_for_an_explanation']}")
        print(f"   share                            : {h['share']:.4f}")
        lo, hi = h["wilson_direct"]
        print(f"   Wilson 95% (direct formula)      : [{lo:.6f}, {hi:.6f}]")
        if h["wilson_statsmodels"]:
            lo2, hi2 = h["wilson_statsmodels"]
            print(f"   Wilson 95% (statsmodels)         : [{lo2:.6f}, {hi2:.6f}]")
            print(f"   the 2 agree to                   : {max(abs(lo-lo2), abs(hi-hi2)):.2e}")
        print(f"   rulings he gave despite that     : {h['rulings_given_anyway']}")
        print("   This is a sample of his reading of ONE file, so it carries an")
        print("   interval; it is not a census of his annotations in general.")

    print("\n" + "=" * 74)
    print("VERDICT ON THE 4 CHARGES")
    print("=" * 74)
    print(f"   subject never named          : {c1['no_shared_phrase']} of {c1['entries']} entries share no phrase with their own title")
    print(f"   standards never invoked      : {sum(c2.values())} total mentions of all 3 standards")
    print(f"   repetition                   : {c3['agreed_by_both']} sentence pairs both measures call near-duplicate")
    print(f"   narration                    : {c4['share']:.4f} of sentences")
    print(f"   plainer than its own source  : {r['delivered_is_easier_than_its_source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
