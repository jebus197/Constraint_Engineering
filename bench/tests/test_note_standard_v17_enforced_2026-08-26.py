"""Notes written under v1.7 must actually obey Rules 27 and 28.

WHY THIS FILE EXISTS AND WHY IT IS A TEST RATHER THAN A RULE. The founder has
asked repeatedly to stop spelling numbers out in text-to-speech files. Measured
2026-08-26 across the three TTS files written in the previous 24 hours:
59 violations, including "three thousand eight hundred and seventy eight passed"
for 3878, "one hundred and seventy eight thousand nine hundred and seventy one
bytes" for 178,971, "one point five six two five hertz" for 1.5625, and
"five six four" for rho = 0.564 -- a decimal turned into three spoken digits.

THE ROOT CAUSE WAS A GENERALISATION WRITTEN INTO A TOOL AS FACT. The standard
has never required spelling. v1.5 says a value may be "spelled or in digits".
Rule 11 governs SCIENTIFIC-NOTATION EXPONENTS ONLY. The blanket habit was
invented by generalising Rule 11, and then scripts/note_vagueness_lint.py
recorded the invention in a comment reading "TTS files write numbers as words by
standard" -- so the tool taught the habit back to whoever read it next.

AND THE LINT WAS RUN AGAINST NOTHING. It had a unit test and no user: the same
"tested but not commissioned" shape this project keeps finding. A guard wired to
nothing is a guard that gets forgotten, which is exactly what happened.

SCOPE. Only notes whose foot-line declares v1.7 or later are held to Rules 27
and 28. Earlier notes were compliant when written and are not retroactively
wrong; rewriting history to satisfy a new rule would destroy the record this
project keeps.
"""
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
NOTES = REPO / "experimental_notes"
sys.path.insert(0, str(REPO / "scripts"))
import note_vagueness_lint as lint  # noqa: E402

FOOTLINE = re.compile(r"CDSFL note standard v(\d+)\.(\d+)")
RULE_27 = "SPELLED NUMBER"
RULE_28 = "CATEGORY NOUN"

#: A LINE SHAPED LIKE A FOOT-LINE, however it is dressed (added 2026-09-17).
#: `FOOTLINE` above matches "CDSFL note standard vX.Y" ANYWHERE and `search`
#: returns the FIRST mention, so a note quoting an older version in its prose
#: before its own v1.7 foot-line was classified by the quotation and silently
#: exempted from this enforcement. `FOOTLINE` itself is kept because the
#: lint-reach script keys its cached fast path on that pattern's text.
#:
#: TOLERANT ON PURPOSE. List markers, HTML tags and comments, heading marks,
#: backticks, bold or italic, "the", other whitespace, letter case, and a short
#: preamble ending in a full stop -- a date stamp such as "2026-08-16, 04:10 BST."
#: or a list number "1." -- all still count. A reader stricter than the text it
#: reads exempts every format it did not foresee, and 2 rounds of independent
#: review found this fix doing exactly that: first for list, HTML, heading,
#: backtick and non-breaking-space forms, then, once the prefix was possessive,
#: for a foot-line inside an HTML comment and for the date-stamped shape 4
#: existing notes already use. STILL NOT READ, although the first-mention rule
#: read it: a label before the foot-line, "Footer: Written under ...". A real note
#: in that shape would lose enforcement, and the direction-aware check in
#: test_footline_is_read_from_the_footline_2026-09-17.py fails on exactly that.
#:
#: 3 PARTS, EACH BOUNDED, SO NO INPUT CAN STALL IT.
#:   preamble   (?:[^.\n]{0,60}\.\s+)?  -- at most 60 characters.
#:   prefix     possessive, and a tag may contain neither "written" nor "<" and is
#:              at most 200 characters. Without the possessive, "<" matched both
#:              branches and a line of 20 "<!-- -->" took 0.254 s, growing about
#:              15 times per 4 more, so about 30 on 1 line would have tripped the
#:              suite's 300 s timeout. Without the "written" exclusion, the
#:              possessive tag branch swallowed a whole "<!-- Written under ... -->"
#:              and never gave it back.
#:   the words  (?a:written) folds case in ASCII only, as `git grep -i` does, so
#:              the live selector and the revision reader agree on every letter.
FOOTLINE_LINE = re.compile(
    r"^(?:[^.\n]{0,60}\.\s+)?"
    r"(?:<(?:(?!written)[^<>]){0,200}>|[\W_])*+"
    r"(?a:written)\s+under\W+(?:the\s+)?CDSFL\s+note\s+standard\s+v(\d+)(?:\.(\d+))?",
    re.IGNORECASE)


def footline_version(line: str) -> tuple[int, int] | None:
    """The version 1 line declares, if that line is shaped like a foot-line."""
    m = FOOTLINE_LINE.match(line)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else None


def declared_version(text: str) -> tuple[int, int] | None:
    """The version a note is HELD to: the highest any foot-line-shaped line declares.

    THE HIGHEST, NOT THE LAST, because the 2 ways to be wrong are not equally bad.
    Under-enforcement is SILENT: a v1.7 note escapes Rules 27 and 28 and nothing
    reports it. Over-enforcement is LOUD: an older note is linted, fails, and a
    person looks. So the rule fails closed. The first version of this fix took
    the LAST foot-line, and an independent review showed that a quoted older
    foot-line placed after the real one then exempted the note.

    Mentions in the middle of a sentence never count, so prose discussing the
    standard -- "this will move to v1.7" -- cannot promote an older note.

    ONE RULE, EVALUATED LINE BY LINE, so the revision reader in
    scripts/lint_reach_over_notes_2026-09-10.py applies it to `git grep` output
    and gets exactly the answer this gives on the whole file. Lines are split on
    "\\n" only, which is git's line model; `splitlines` also breaks on U+2028 and
    form feeds, which git does not.

    MEASURED BEFORE ADOPTION: the same 61 notes as the first-mention rule, and the
    same 29 of 379 at b593500, both printed by the lint-reach script, with its
    per-line and whole-file answers identical at both revisions.
    """
    versions = [v for v in (footline_version(line) for line in text.split("\n")) if v]
    return max(versions) if versions else None


def _v17_notes():
    out = []
    # RECURSIVE (2026-09-08). `glob` saw only the top level, so the 10 notes in
    # subdirectories -- panel_results/, panel_briefs/, data/ and 2 READMEs --
    # could never fail this enforcement. 0 of them declare v1.7 today, so the
    # gap was latent rather than active; a nested note adopting the standard
    # would have been exempt from it silently. Same bounded-traversal shape as
    # the vault, arc and QC defects repaired the same night.
    for p in sorted(NOTES.rglob("*.md")):
        v = declared_version(p.read_text(encoding="utf-8", errors="replace"))
        if v and v >= (1, 7):
            out.append(p)
    return out


class TestTheCheckerDiscriminates:
    """Commissioned before trusted. A checker that fires on everything is as
    useless as one that fires on nothing, and the founder's own note says a
    linter with false positives gets ignored."""

    @pytest.mark.parametrize("bad", [
        "The suite returned three thousand eight hundred and seventy eight passed.",
        "The mirror is one hundred and seventy eight thousand bytes.",
        "Correlation reached zero point five six four across the runs.",
        "Eighteen of the branch's fifty nine commits are cited by hash.",
        "The run began at fourteen forty six on the twenty third.",
    ])
    def test_known_bad_a_spelled_quantity_is_reported(self, bad, tmp_path):
        f = tmp_path / "n.md"; f.write_text(bad, encoding="utf-8")
        kinds = [k for _, k, _, _ in lint.lint(f)]
        assert any(RULE_27 in k for k in kinds), f"not reported: {bad!r}"

    @pytest.mark.parametrize("good", [
        "The suite returned 3878 passed, 1 failed, 34 skipped.",
        "The mirror is 178,971 bytes against the repository's 180,043.",
        "Correlation reached rho = 0.564 across 289 observations.",
        "One command fixes it, and three fixes landed today.",
        "The hold was recorded on the twenty sixth of August.",
        "It reclaimed 95 MB across 17,874 entries.",
    ])
    def test_known_good_digits_and_ordinary_prose_pass(self, good, tmp_path):
        f = tmp_path / "n.md"; f.write_text(good, encoding="utf-8")
        kinds = [k for _, k, _, _ in lint.lint(f)]
        assert not any(RULE_27 in k for k in kinds), (
            f"false positive on {good!r}; a linter that fires on prose gets ignored"
        )

    def test_a_category_noun_is_reported(self, tmp_path):
        f = tmp_path / "n.md"
        f.write_text("The save routine refused to count and said so.", encoding="utf-8")
        kinds = [k for _, k, _, _ in lint.lint(f)]
        assert any(RULE_28 in k for k in kinds), (
            "'the save routine' passed; the founder types sv daily and the note "
            "should say sv"
        )

    def test_the_two_answers_differ(self, tmp_path):
        f = tmp_path / "n.md"
        f.write_text("It returned three thousand eight hundred and seventy eight.", encoding="utf-8")
        bad = any(RULE_27 in k for _, k, _, _ in lint.lint(f))
        f.write_text("It returned 3878.", encoding="utf-8")
        good = any(RULE_27 in k for _, k, _, _ in lint.lint(f))
        assert bad and not good, "the checker gives the same answer to both forms"


class TestTheRealNotes:
    def test_the_lint_still_finds_nothing_wrong_with_plain_digits(self):
        """Guards the guard: if WORD_NUMBER were broadened until it fired on
        everything, this would fail."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "n.md"
            f.write_text("Suite 4138 passed, 1 failed, 34 skipped in 221.88 s. "
                         "Reclaimed 95 MB from 17,874 entries.", encoding="utf-8")
            assert not lint.lint(f), f"plain digits reported: {lint.lint(f)}"

    @pytest.mark.parametrize("path", _v17_notes() or [None],
                             ids=lambda p: p.name if p else "no-v17-notes-yet")
    def test_v17_notes_obey_rules_27_and_28(self, path):
        if path is None:
            pytest.skip("no note declares v1.7 yet; this activates with the first")
        # `blocking`, NOT `lint`. `lint` reports everything it sees, including
        # what a panel seat wrote inside a verbatim region -- and this guard once
        # failed the whole suite on a sentence `fable` wrote inside
        # `<!-- verbatim-begin: fable -->` in Panel_Roster_Round2_FULL_RECORD.
        # Task V8 exists so a seat's words reach the record unedited; a guard
        # that blocks on them defeats the mechanism it shares a repository with.
        # `blocking` is the SAME function the CLI counts with, not a second one
        # asserted to agree with it.
        hits = [(n, k, t) for n, k, t, _ in lint.blocking(path)
                if RULE_27 in k or RULE_28 in k]
        assert not hits, (
            f"{path.name} declares v1.7 and violates it:\n"
            + "\n".join(f"    para {n}  {k}  {t!r}" for n, k, t in hits)
        )
