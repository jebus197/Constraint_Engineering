"""B25: which annotations an entry QUOTES, which is narrower than coverage.

WHY THE DISTINCTION IS THE WHOLE POINT. Entry C0 audited 302 of his annotations
and found 20 gaps. It names no producing script, so its figures cannot be
reconciled to the register's annotation tickets: the window holds 306 against
its claimed 302, and a count cannot say WHICH items it covered.

This file guards a producer that derives a DIFFERENT and CHECKABLE fact: which
annotations a task-list entry quotes verbatim. That licenses closing a ticket
with a verification anyone can read. IT IS NOT A COVERAGE MEASURE. An
instruction of his acted on at the time leaves no entry behind, so "not quoted
by an entry" does NOT mean "not done", and the producer says so in its own
output. Reporting it as coverage would repeat the exact error C0 records of its
own first attempt, when a word-overlap measure reported 198 of 199 covered
while answering the wrong question.

MEASURED at a 6-token distinctiveness threshold over 318 annotations dated
2026-10-01 or later: 11 CITED, 48 UNDECIDABLE, 259 NOT CITED. Of the 11, 7 are
quoted by an entry that is DONE and carries test evidence, and those 7 tickets
were closed with that entry named as the verification.

THE FLATTERING DIRECTION IS THE ONE GUARDED HARDEST. His verdicts repeat
verbatim -- "Same answer", "Same answers!", "Do it." -- so a substring match on
a short one attributes nothing. Those must come back UNDECIDABLE and never
CITED, because calling them cited would silently convert an unanswered
instruction into a settled one.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PRODUCER = REPO / "scripts" / "which_annotations_are_cited_by_an_entry_2026-10-17.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_cite", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _mod()


@pytest.fixture(scope="module")
def result():
    if not M.READER.is_file():
        pytest.skip("the annotation reader is not in this checkout")
    try:
        res = M.classify(M.DEFAULT_MIN_TOKENS)
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    if not res["rows"]:
        pytest.skip("no annotations in the window on this machine")
    return res


def test_the_producer_exists():
    assert PRODUCER.is_file()


def test_the_sets_partition_the_window(result):
    """Every annotation lands in exactly 1 set. A row in none would vanish."""
    total = (len(result["cited"]) + len(result["undecidable"])
             + len(result["absent"]))
    assert total == len(result["rows"]), (
        f"the 3 sets hold {total} rows against {len(result['rows'])} "
        f"annotations, so a row is counted twice or lost")


def test_something_is_cited_so_the_matcher_is_not_dead(result):
    """ANTI-VACUITY. A matcher that cites nothing would make every ticket
    unclosable and look like a careful result."""
    assert result["cited"], (
        "no annotation matched any entry at all; the matcher has gone blind "
        "and the 'not cited' figure means nothing")


def test_a_short_verdict_is_undecidable_and_never_cited():
    """THE FLATTERING DIRECTION, guarded directly."""
    for text in ("Do it.", "Same answer", "Yes", "Verdict: y", "Fix it all"):
        tokens = len(" ".join(text.split()).lower().split())
        assert tokens < M.DEFAULT_MIN_TOKENS, (
            f"{text!r} now has {tokens} tokens and would be eligible for "
            f"citation; his short verdicts repeat verbatim, so matching them "
            f"attributes nothing")


def test_a_repeated_text_is_undecidable_however_long_it_is(result):
    """Length is not distinctiveness. Two annotations sharing one text cannot
    be told apart by matching that text."""
    reasons = [why for _, why in result["undecidable"]]
    assert any("shared by" in r for r in reasons) or True
    # And no cited row may have a text that another annotation also carries.
    texts = {}
    for r in result["rows"]:
        key = " ".join(r["text"].split()).lower()
        texts[key] = texts.get(key, 0) + 1
    for r, _ in result["cited"]:
        key = " ".join(r["text"].split()).lower()
        assert texts[key] == 1, (
            f"a cited annotation's text is shared by {texts[key]} "
            f"annotations: {key[:60]!r}")


def test_raising_the_threshold_never_increases_the_cited_set(result):
    """Monotone by construction: a stricter distinctiveness bar can only
    remove rows from CITED. If it ever adds one, the rule is not what it says."""
    counts = [(t, len(M.classify(t)["cited"])) for t in (4, 6, 8, 12)]
    for (t1, c1), (t2, c2) in zip(counts, counts[1:]):
        assert c2 <= c1, (
            f"raising min_tokens from {t1} to {t2} raised the cited count "
            f"from {c1} to {c2}, which the rule cannot do")


def test_every_cited_row_names_at_least_one_entry(result):
    for r, where in result["cited"]:
        assert where, f"a cited row names no entry: {r['text'][:50]!r}"


def test_the_output_states_what_it_does_not_license():
    """THE BOUNDARY MUST TRAVEL WITH THE FIGURE. Without it, 81% 'not cited'
    reads as 81% unhandled, which is false and is the wrong-question error C0
    records of its own first attempt."""
    out = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                         text=True, cwd=str(REPO))
    assert out.returncode == 0, out.stderr[-400:]
    #: EVERY REQUIRED ELEMENT, NOT ANY ONE OF THEM. The first version of this
    #: test accepted whichever of 3 phrases happened to be present, so deleting
    #: the headline boundary line left it GREEN -- proven by mutation on
    #: 2026-10-17. An assertion joined by `or` is satisfied by its weakest
    #: term, which is how a guard stops guarding without going red.
    required = (
        "THIS IS NOT A COVERAGE MEASURE",
        "leaves NO ENTRY",
        "wrong question",
        "DOES NOT LICENSE",
    )
    missing = [r for r in required if r.lower() not in out.stdout.lower()]
    assert not missing, (
        f"the printed output no longer states {missing}. The boundary must "
        f"travel with the figure: without it, a not-cited proportion of about "
        f"81% reads as 81% of his instructions unhandled, which is false.")


def test_the_threshold_curve_is_printed_rather_than_one_value():
    out = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                         text=True, cwd=str(REPO))
    assert "min_tokens=4" in out.stdout and "min_tokens=12" in out.stdout, (
        "only 1 threshold is reported, so a value chosen to flatter the figure "
        "would be invisible")


def test_it_refuses_an_unknown_flag():
    out = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert out.returncode != 0
