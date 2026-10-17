"""A fix that edits only prose is unscored, even inside a document full of code.

TASK A19. HIS DESIGN POINT, 2026-09-10, verbatim: *"Having the admissibility
switch off for prose targets is also questionable, as clearly it should simply
mark a purely prose input as 'inadmissible', while still solving any
computationally reducible elements within that prose! This is STEM. No one will
be using CDSFL to write poetry!"*

THE OPERATIVE WORD IS ELEMENTS, and until 2026-10-17 the decision was made one
level too high. `_gateable_source` answers the TARGET question -- does this
document contain any Python -- and `_scoring_prose` used only that. So a single
fenced listing anywhere in a markdown file put EVERY fix on the gated path,
including fixes that touch nothing but prose. The flag is veto-only, so the cost
was not a wrong admission but a wrong CONVICTION: a correct prose-only edit could
be rejected by gates run over listings it never went near.

MEASURED ON THE PROJECT'S OWN ACCEPTANCE FIXTURES: of the 5 STEM fixtures in
`bench/tests/fixtures/stem/`, **4 have a `correct_fix` that edits only prose** --
structural, metrology, algorithms and numerical -- and 1, statistics, reaches a
listing. Before this change all 5 had the gates run over the document's listings
and the outcome recorded as "what the gates would have said" about them, when for
4 of the 5 it was never about them at all.

THE BUG I WROTE FIRST, pinned here because it was the exact reverse of the fix.
The new branch was written as an `elif` that set the reason and returned nothing,
which INTERCEPTED the case it was added for: with the flag on, a prose-only fix
fell through every branch to the gates and came back ESCALATE instead of
NO_SCORE. Found by executing `compute_sk` on a crafted prose-only fix, not by
reading the diff.

AN UNPLACEABLE EDIT IS TREATED AS REDUCIBLE, deliberately. Treating an edit whose
SEARCH text cannot be found as prose would turn a parse failure into an exemption
from every gate.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

DOC = """# A design note

Some prose explaining the idea, which a model might reword.

```python
def add(a, b):
    return a + b
```

More prose after the listing.
"""


def _blk(path: str, search: str, replace: str) -> str:
    return f"<<<< SEARCH {path}\n{search}\n==== REPLACE\n{replace}\n>>>>\n"


@pytest.fixture(scope="module")
def runner():
    import bench.reference_runner_v3 as mod
    return mod


@pytest.mark.parametrize("search,replace,expected,label", [
    ("    return a + b", "    return b + a", True, "edits the listing"),
    ("More prose after the listing.", "Revised.", False, "edits prose after"),
    ("Some prose explaining the idea, which a model might reword.",
     "Clearer prose.", False, "edits prose before"),
    ("text that is nowhere in the document", "whatever", True, "unplaceable"),
])
def test_the_classifier_answers_per_fix(runner, search, replace, expected,
                                        label):
    got, why = runner._fix_touches_reducible(
        _blk("note.md", search, replace), DOC, "note.md")
    assert got is expected, f"{label}: {why}"


def test_a_fix_touching_both_counts_as_reducible(runner):
    """One listing edit among prose edits is enough for the gates to speak."""
    both = (_blk("note.md", "More prose after the listing.", "Revised.")
            + _blk("note.md", "    return a + b", "    return b + a"))
    assert len(runner.parse_search_replace_blocks(both)) == 2
    got, why = runner._fix_touches_reducible(both, DOC, "note.md")
    assert got is True, why


def test_a_document_with_no_listing_is_never_reducible(runner):
    got, _ = runner._fix_touches_reducible(
        _blk("p.md", "x", "y"), "just prose, no code at all\n", "p.md")
    assert got is False


def test_a_python_target_is_always_reducible(runner):
    got, why = runner._fix_touches_reducible(
        _blk("m.py", "a + b", "b + a"), "def f(a, b):\n    return a + b\n",
        "m.py")
    assert got is True and "python target" in why


# --------------------------------------------------------------------------
# The behaviour that matters: what `compute_sk` returns.
# --------------------------------------------------------------------------

def _sk(runner, fix_text, flag, doc=DOC, path="note.md"):
    return runner.compute_sk(fix_text, doc, path, score_prose_listings=flag,
                             declared_target_kind="prose")


def test_a_prose_only_fix_is_unscored_whatever_the_flag_says(runner):
    """HIS "PURELY PROSE" CASE, one level down from the target.

    THIS IS THE ASSERTION THE FIRST DRAFT FAILED: it returned ESCALATE with the
    flag on, because the new branch set a reason without reaching the NO_SCORE
    return.
    """
    fix = _blk("note.md", "More prose after the listing.", "Revised.")
    for flag in (False, True):
        r = _sk(runner, fix, flag)
        assert r.tristate == runner.SK_NO_SCORE, (
            f"flag={flag}: a fix that edits no code was scored {r.tristate}")


def test_the_reason_says_why_sk_is_silent(runner):
    """Not a silent discard: the reason must name the cause."""
    fix = _blk("note.md", "More prose after the listing.", "Revised.")
    r = _sk(runner, fix, True)
    reason = (r.gate_details or {}).get("target_kind_reason", "")
    assert "touches prose only" in reason, reason
    assert "no opinion" in reason, reason


def test_a_listing_fix_still_reaches_the_gates_with_the_flag_on(runner):
    """The flag's measured, additive contribution is preserved.

    Without this the change could have silenced S_k on prose documents
    altogether, which would remove the one thing the flag does that is sound:
    convicting a fix that breaks a working listing.
    """
    fix = _blk("note.md", "    return a + b", "    return b + a")
    off = _sk(runner, fix, False)
    on = _sk(runner, fix, True)
    assert off.tristate == runner.SK_NO_SCORE
    assert on.tristate != runner.SK_NO_SCORE, (
        "with the flag on, a fix that edits a fenced listing must reach the "
        "gates; `_fix_touches_reducible` has silenced the flag entirely")


def test_a_python_target_is_untouched_by_any_of_this(runner):
    """ANTI-REGRESSION. The change may not alter the Python path."""
    fix = _blk("m.py", "    return a + b", "    return b + a")
    src = "def f(a, b):\n    return a + b\n"
    for flag in (False, True):
        r = runner.compute_sk(fix, src, "m.py", score_prose_listings=flag)
        assert r.tristate != runner.SK_NO_SCORE, (
            f"flag={flag}: a Python target became unscored, which this change "
            f"must never do")


def test_the_acceptance_fixtures_split_as_measured():
    """The 4-and-1 split is the evidence for the change; it must stay true.

    If the fixtures are edited so that all 5 reach a listing, the 4 prose-only
    assertions above stop testing anything about real data, and this says so.

    IT USES THE ACCEPTANCE SUITE'S OWN `_fix_text`, not a local reconstruction.
    The first version built the fix text by hand and classified every fixture as
    prose-only, because the hand-rolled format did not parse -- the same mistake
    as measuring with the wrong instrument and believing the result.
    """
    import bench.reference_runner_v3 as runner
    from bench.tests.test_prose_acceptance_stem import FIXTURES, _fix_text
    items = list(FIXTURES.values()) if isinstance(FIXTURES, dict) \
        else list(FIXTURES)
    assert items, "no acceptance fixtures loaded"
    prose_only, reaching = [], []
    for f in items:
        text = _fix_text(f, f.correct_fix, f.doc_path)
        assert runner.parse_search_replace_blocks(text), (
            f"{f.key}: the fix text did not parse, so this measurement would "
            f"be meaningless")
        got, _ = runner._fix_touches_reducible(text, f.document,
                                               str(f.doc_path))
        (reaching if got else prose_only).append(f.key)
    assert prose_only, (
        "no acceptance fixture has a prose-only correct fix any more, so the "
        "measured basis for task A19's per-fix classification is gone")
    assert reaching, (
        "no acceptance fixture reaches a listing any more, so the flag's "
        "convicting half is untested on real data")
    assert len(prose_only) == 4 and len(reaching) == 1, (
        f"the measured split was 4 prose-only against 1 reaching a listing; it "
        f"is now {len(prose_only)} against {len(reaching)} "
        f"(prose-only: {sorted(prose_only)}, reaching: {sorted(reaching)})")
