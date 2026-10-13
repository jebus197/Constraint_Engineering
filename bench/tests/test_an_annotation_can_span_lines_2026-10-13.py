"""An annotation of his that continues on a later line must be read in full.

HIS INSTRUCTION, 2026-10-13: *"Make sure you can parse my responses in full."*
THE SECOND TIME HE HAS HAD TO SAY IT. On 2026-10-11 the reader decoded his
files with `errors="ignore"` and silently dropped every curly apostrophe -- 256
characters across 14 of 29 plain-text files. That was repaired. This is a
different defect in the same reader, found by obeying the same instruction.

THE DEFECT. `_annotations_in` walked the decoded text line by line and treated
each line beginning with '#' as a whole annotation. An annotation CONTINUING on
a later line lost everything after the first, because the continuation does not
itself begin with '#'.

MEASURED ON THE FILE THAT EXPOSED IT. His first annotation on
Morning_Report_2026-10-13.txt occupies lines 23, 25 and 27 of a Mac OS Roman,
CR-terminated file: the hash line, then 819 characters re-quoting his own
earlier ruling, then its 127-character tail. The reader returned 97 of 1,053
characters. **The lost text carried the operative clause** -- "But propose your
own fixes first" -- which changes the ORDER of the work, and it survived only
because the file was also read directly.

THE RULE IS HIS OWN CONVENTION. A LEADING hash opens an annotation; a TRAILING
hash says a quotation follows. The continuation then runs until the report
resumes, and "the report" is read from the generated original in
~/Desktop/CDSFL_tts where one survives, so the boundary is an ORACLE rather
than a guess. Measured: 1 of 522 annotations ends with a trailing hash,
0.1916%, Wilson 95% [0.0338%, 1.0771%]. A rule capturing ANY following prose
line would have swallowed 367 further lines, mostly the reports' own sentences.

CORPUS INVARIANCE, MEASURED: 522 annotations before and after, 946 characters
recovered, and exactly ONE annotation's length changed. A reader fix that moved
any other annotation would be changing the record rather than reading it.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
LIVE = (pathlib.Path.home() / "Developer_Projects" / "Responses"
        / "Morning_Report_2026-10-13.txt")


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location("rfr_span", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfr_span"] = mod
    spec.loader.exec_module(mod)
    return mod


def _ann(R, needle):
    return [a for a in R.annotations() if needle in (a.get("text") or "")]


@pytest.mark.skipif(not LIVE.exists(), reason="his annotated response absent")
def test_the_operative_clause_is_not_lost(R):
    """The clause that changes the order of the work must survive the reader."""
    hits = _ann(R, "I did just give you")
    assert hits, "his Decision-1 annotation is not being read at all"
    text = hits[0]["text"]
    for clause in ("What was the original specification for the severity gate",
                   "This does not qualify as a",
                   "ask the panel to help you settle it",
                   "propose your own fixes first"):
        assert clause in text, (
            f"the reader dropped {clause!r} from his annotation; he asked to be "
            f"parsed IN FULL and this is the clause that changes the work")


@pytest.mark.skipif(not LIVE.exists(), reason="his annotated response absent")
def test_the_whole_annotation_is_recovered_not_merely_more_of_it(R):
    """97 characters was the defect; a partial recovery is still a defect."""
    text = _ann(R, "I did just give you")[0]["text"]
    assert len(text) > 1000, (
        f"recovered only {len(text)} characters of a 1,053-character "
        f"annotation; the tail is still being dropped")


@pytest.mark.skipif(not LIVE.exists(), reason="his annotated response absent")
def test_no_report_text_is_captured(R):
    """The opposite failure, and the reason the rule is narrow.

    A looser continuation rule would absorb the report's own sentences into his
    words, which is worse than truncation: it would put statements in his mouth.
    """
    text = _ann(R, "I did just give you")[0]["text"]
    for report_phrase in ("DECISION 2.",
                          "The ruling was that a finding nothing ever read",
                          "A consequence of decision 2 rather than"):
        assert report_phrase not in text, (
            f"the reader absorbed the report's own sentence {report_phrase!r} "
            f"into his annotation, which attributes our words to him")


def test_no_annotation_anywhere_absorbs_a_generated_REPORT_LINE(R):
    """THE OVER-CAPTURE PROPERTY, CHECKED ACROSS THE WHOLE CORPUS.

    The first version of this test asserted that at most 3 annotations exceed
    900 characters, on the assumption that his are short. MEASURED, 26 of 522
    exceed it -- he writes long -- so the assumption was wrong and the test was
    wrong with it. That is the same shape as the defects it guards: a threshold
    assumed instead of measured.

    The property that actually matters is not length but PROVENANCE. A
    continuation rule that over-captured would pull the report's own sentences
    into his annotation, which is worse than truncation because it attributes
    our words to him. So: no annotation may contain, verbatim, a line from any
    report this project generated.
    """
    originals = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
    if not originals.is_dir():
        pytest.skip("no generated originals to compare against")
    report_lines = set()
    for orig in originals.glob("*.txt"):
        try:
            text = R.read_any(orig)
        except Exception:                                 # noqa: BLE001
            continue
        for line in (text or "").splitlines():
            s = line.strip()
            # Only lines long enough to be distinctive. A short line like a
            # date or a heading fragment can coincide innocently.
            if len(s) >= 120:
                report_lines.add(s)
    assert report_lines, "no distinctive report lines collected; test is void"

    offenders = []
    for a in R.annotations():
        txt = a.get("text") or ""
        for rl in report_lines:
            if rl in txt:
                offenders.append((a["file"], a["line_index"], rl[:70]))
                break
    assert not offenders, (
        f"{len(offenders)} annotation(s) absorbed a generated report line, so "
        f"the reader is attributing our sentences to him: {offenders[:3]}")


def test_the_corpus_count_is_unchanged_by_the_fix(R):
    """A reader fix must change what is READ, never how much there is."""
    assert len(R.annotations()) == 522, (
        "the annotation COUNT moved; joining or splitting his annotations "
        "changes the record rather than reading it")
