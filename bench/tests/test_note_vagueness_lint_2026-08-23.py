"""The vagueness linter, and the two ways it broke while being written.

WHY IT EXISTS. The note standard has said since v1.2 that the failure mode is never
"too technical", it is "too vague to identify what is being discussed", and v1.4
Rule 19 says to name the subject. Both were in force on 2026-08-23 when a note still
read "all eight defects debited the models' measured competence -- the very quantity
this project exists to measure". The founder's reply: "I have no clear idea at all
what you are referring to... even though you already said several times that you had
fixed it". A rule restated and re-violated does not need restating. It needs a check.

THE MOTIVATING SENTENCE IS A TEST FIXTURE HERE. If the linter ever stops catching it,
the linter has stopped doing the only job it was built for.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
_spec = importlib.util.spec_from_file_location(
    "note_vagueness_lint", REPO / "scripts/note_vagueness_lint.py")
LINT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LINT)

MOTIVATING = ("Every one of them debited the models' measured competence, which is "
              "the precise quantity this project exists to measure.")


def _lint(text, tmp_path, name="n.txt"):
    p = tmp_path / name
    p.write_text(text)
    return LINT.lint(p)


class TestTheMotivatingSentence:
    def test_it_is_caught(self, tmp_path):
        hits = _lint(MOTIVATING, tmp_path)
        assert any(k == "QUANTITY WITHOUT A VALUE" for _, k, _, _ in hits), (
            "the linter no longer catches the sentence it was built for")

    def test_the_compliant_rewrite_is_NOT_caught(self, tmp_path):
        ok = ("All eleven defects lowered a model's falsifier-confirm rate below its "
              "true value. On Exp 55 that rate is what bench/routing.py uses to pick "
              "which model resolves the hardest findings: Gemini scored 2 of 2 and "
              "DeepSeek 0 of 2.")
        assert not _lint(ok, tmp_path), (
            "a sentence naming the quantity, the direction and real values must pass")


class TestTheTwoRegressionsMadeWhileWritingIt:
    def test_spelled_numbers_count_as_values(self, tmp_path):
        """A spelled value still SATISFIES the quantity check.

        NARROWED 2026-08-26. This assertion used to demand ZERO findings, on the
        docstring "TTS files spell numbers by standard" -- which was never the
        standard. v1.5 says a value may be "spelled or in digits" and Rule 11
        governs scientific-notation exponents only. The blanket habit was a
        generalisation of Rule 11, and it had been written into THREE places as
        fact: this docstring, a comment in note_vagueness_lint.py, and the habit
        itself. All three are now corrected.

        The original INTENT was right and is preserved: a spelled figure is
        still a figure, so an old compliant note is not retroactively vague.
        What changed is that Rule 27 (v1.7) now ALSO reports the sentence,
        because the founder reads by text-to-speech and "twenty nine of thirty
        four" is harder to follow aloud than "29 of 34", not easier.
        """
        s = "The correct open count is twenty nine of thirty four instruments."
        hits = _lint(s, tmp_path)
        assert not [h for h in hits if "QUANTITY WITHOUT A VALUE" in h[1]], (
            "a spelled-out value no longer satisfies the quantity check; an old "
            "compliant note would be retroactively marked vague"
        )
        assert [h for h in hits if "SPELLED NUMBER" in h[1]], (
            "Rule 27 did not fire on a spelled figure; the founder's repeated "
            "request would go unenforced again"
        )

    @pytest.mark.parametrize("word", ["one", "none", "half", "twice"])
    def test_common_words_do_NOT_count_as_values(self, tmp_path, word):
        """Including these made the linter miss its own motivating sentence."""
        s = f"Every {word} of them debited the models' measured competence here."
        assert _lint(s, tmp_path), (
            f"{word!r} is too common in prose to serve as evidence a value was quoted")


class TestTheTwoPatterns:
    @pytest.mark.parametrize("vague", [
        "The mechanism was repaired and behaves correctly now.",
        "One component was found to be misconfigured during the review.",
    ])
    def test_unnamed_subject_is_caught(self, tmp_path, vague):
        assert any(k == "UNNAMED SUBJECT" for _, k, _, _ in _lint(vague, tmp_path))

    def test_naming_something_clears_it(self, tmp_path):
        named = ("The mechanism in bench/routing.py was repaired and Codex now "
                 "resolves the finding correctly.")
        assert not any(k == "UNNAMED SUBJECT" for _, k, _, _ in _lint(named, tmp_path))

    def test_hedges_are_flagged(self, tmp_path):
        assert any(k == "HEDGE" for _, k, _, _ in
                   _lint("The result was somewhat better than the previous attempt.", tmp_path))

    def test_short_fragments_and_tables_are_skipped(self, tmp_path):
        assert not _lint("| a | b |\n\n# Heading\n\nToo short.", tmp_path)


class TestItIsAReportNotAGate:
    def test_main_exits_zero_even_with_findings(self, tmp_path, capsys, monkeypatch):
        p = tmp_path / "n.txt"
        p.write_text(MOTIVATING)
        monkeypatch.setattr(LINT.sys, "argv", ["x", str(p)])
        assert LINT.main() == 0, (
            "a linter that blocks gets worked around; this one is meant to be read")
        assert "not enforced" in capsys.readouterr().out


# ── The multi-sentence quote exemption (task L2, fixed 2026-09-09) ───────────

class TestAQuotationSpanningSentencesStaysExempt:
    """The exemption lapsed on exactly the LONGEST quotations, which here are
    the founder's.

    `lint` stripped balanced `"..."` pairs from each SENTENCE, but a quotation
    running across a sentence boundary is split first, so each fragment carries
    an unbalanced quote character and matches nothing. Measured on the master
    task list: 1 of 3 findings was a fragment of a verbatim founder quote.

    IT BECAME URGENT ON 2026-09-09, when a pre-commit guard made this linter
    BLOCKING. A false positive inside a quotation would leave 2 choices --
    editing the founder's words, or bypassing the guard -- and the standing rule
    is that the linter is never applied to his words and never gates his input.
    """

    def _findings(self, tmp_path, body):
        p = tmp_path / "n.md"
        p.write_text(body, encoding="utf-8")
        return LINT.lint(p)

    def test_a_single_sentence_quote_was_always_exempt(self, tmp_path):
        """The case that already worked, kept as the comparator."""
        body = ('The founder ruled, verbatim: "there were twenty-nine of them". '
                'The count is 29 and the rate is 0.5.\n')
        assert not [f for f in self._findings(tmp_path, body)
                    if "SPELLED" in str(f[1])]

    def test_a_quote_spanning_two_sentences_is_exempt_too(self, tmp_path):
        """THE DEFECT. Before the fix the spelled number in the 2nd sentence of
        the quotation was reported, because the fragment's quote was unbalanced."""
        body = ('The founder ruled, verbatim: "The first point stands. There '
                'were twenty-nine of them and that settles it." The count is 29.\n')
        spelled = [f for f in self._findings(tmp_path, body)
                   if "SPELLED" in str(f[1])]
        assert not spelled, (
            f"a spelled number inside a multi-sentence verbatim quotation was "
            f"reported: {spelled}")

    def test_the_same_violation_OUTSIDE_a_quote_is_still_reported(self, tmp_path):
        """DISCRIMINATION. An exemption that swallows everything is not an
        exemption, it is a disabled rule."""
        body = ('The founder ruled, verbatim: "The first point stands." There '
                'were twenty-nine of them in the assistant\'s own prose.\n')
        spelled = [f for f in self._findings(tmp_path, body)
                   if "SPELLED" in str(f[1])]
        assert spelled, "the rule stopped firing outside quotations"

    def test_the_quote_does_not_erase_the_subject_it_names(self, tmp_path):
        """THE REGRESSION THIS FIX CAUSED AND THEN REMOVED.

        A first version yielded the MASKED sentence, deleting the nouns inside
        the quotation, so sentences whose specificity was carried by the quote
        were newly reported as vague. Measured across 379 notes: 8 false
        positives removed and 3 introduced. The mask now guides the sentence
        SPLIT only; the text yielded is the original."""
        # THE FIGURE MUST LIVE INSIDE THE QUOTE AND NOWHERE ELSE, or this test
        # cannot see the regression. A first version left "12 items" outside it,
        # so `DIGIT.search` found a digit either way and the quantity rule was
        # skipped in both worlds -- the mutation survived and the test passed.
        # The 2 real instances measured across the corpus both had their only
        # figure inside the quotation.
        body = ('The "29 confirmed items" above is withdrawn as a confirmed '
                'count.\n')
        vague = [f for f in self._findings(tmp_path, body)
                 if "UNNAMED" in str(f[1]) or "WITHOUT A VALUE" in str(f[1])]
        assert not vague, (
            f"the quotation names the subject; masking it made the sentence "
            f"look vague: {vague}")
