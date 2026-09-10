"""The founder's words must never gate his input. Proven, not promised.

His ruling, verbatim, 2026-09-09: *"the problem you clearly identified is
treating me like a machine, and building things that mark my inputs as 'vague'.
I don't think I am vague at all. In fact overall I think I am remarkably specific
... It is you who are clearly vague ... Refusing work from me because it does not
fit your own 'anti-vagueness' standards is clearly nonsensical and probably very
unhelpful going forward."*

THE RECORD SUPPORTS HIM WITHOUT QUALIFICATION. Of 1183 findings across 376 notes,
1181 are in the assistant's own prose and 2 fall inside a quotation of anyone at
all -- 99.83%, Wilson [99.39%, 99.95%]. The linter has found the founder vague
twice, in passing, and the assistant vague 1181 times.

WHY THIS BECAME URGENT rather than cosmetic. Task 7.2 made the linter BLOCKING at
commit time, per his 2026-09-04 ruling that findings are blocking rather than
advisory. From that moment a false positive inside a quotation of his would leave
2 choices: edit his words, or bypass the guard. Both are wrong.

THE RULE THIS FILE ENFORCES: his text is DATA to be preserved exactly, never
INPUT to be corrected. A paraphrase of him is the assistant's own prose and is
linted normally -- that distinction is the point, not a loophole.
"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / "scripts" / "note_vagueness_lint.py"

#: Engineered to trip the 2 rules the linter enforces hardest: a spelled number
#: (Rule 27) and an unnamed subject. If the exemptions were vacuous this sentence
#: would prove nothing, so the control below asserts it DOES fire on its own.
TRIPPING = ("I want you to fix twenty-nine problems in the system before the "
            "process runs again")


@pytest.fixture(scope="module")
def N():
    spec = importlib.util.spec_from_file_location("nvl", LINT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _counted_and_exempt(N, body: str):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as f:
        f.write("# Note\n\nline 2.\n\n" + body + "\n")
        p = Path(f.name)
    try:
        hits = N.lint(p)
        ex = N.verbatim_paragraphs(p.read_text(encoding="utf-8"))
        return ([h for h in hits if h[0] not in ex],
                [h for h in hits if h[0] in ex])
    finally:
        p.unlink(missing_ok=True)


class TestTheControlProvesTheLinterCanFire:
    def test_the_same_sentence_in_the_assistants_own_prose_is_caught(self, N):
        """Without this, every exemption below could be vacuous."""
        counted, _ = _counted_and_exempt(N, f"I will {TRIPPING}.")
        kinds = {h[1] for h in counted}
        assert any("SPELLED NUMBER" in k for k in kinds), counted
        assert any("UNNAMED SUBJECT" in k for k in kinds), counted


class TestHisWordsAreNeverCounted:
    def test_an_inline_double_quotation_of_him_counts_nothing(self, N):
        counted, _ = _counted_and_exempt(
            N, f'The founder ruled, verbatim: *"{TRIPPING}."*')
        assert counted == [], (
            f"a quotation of the founder produced {len(counted)} counted "
            f"finding(s); at commit time that would force editing his words")

    def test_a_verbatim_region_reports_but_does_not_count(self, N):
        """Reported, so nothing is hidden. Not counted, so nothing is gated."""
        counted, exempt = _counted_and_exempt(
            N, f"<!-- verbatim-begin: the founder -->\n\n{TRIPPING}.\n\n"
               f"<!-- verbatim-end -->")
        assert counted == [], counted
        assert len(exempt) >= 2, (
            "the findings must still be REPORTED inside the region -- an "
            "exemption a reader cannot see is a checker that missed something")

    @pytest.mark.parametrize("sentence", [
        "Fix them all, or at least those that a technical reader would be "
        "likely to find insufficient in the interests of reproducibility",
        "You need to give me clear instructions how to do this!",
        "We will begin another simulated run once all these remaining issues "
        "have been addressed",
        "So again what is the fix? Did you consult the other models yet?",
    ])
    def test_real_rulings_of_his_pass_clean(self, N, sentence):
        counted, _ = _counted_and_exempt(N, f'He ruled: *"{sentence}"*')
        assert counted == [], f"{sentence!r} -> {counted}"


class TestAParaphraseIsTheAssistantsOwnProse:
    def test_a_paraphrase_of_him_is_still_linted(self, N):
        """NOT a loophole -- the distinction is the whole rule.

        His TEXT is data to be preserved exactly. A sentence the assistant wrote
        ABOUT him is the assistant's writing and is held to the standard like any
        other. Exempting paraphrase would let any prose escape by naming him.
        """
        counted, _ = _counted_and_exempt(N, f"The founder wants {TRIPPING}.")
        assert counted, (
            "a paraphrase escaped the linter by mentioning the founder, which "
            "would make the exemption a bypass rather than a boundary")


class TestTheCommitGateCannotRefuseHisWords:
    def test_a_note_that_is_only_his_words_lints_to_zero(self, N):
        """The end-to-end case: the per-file ratchet counts what lint() counts."""
        body = "\n\n".join(f'He ruled: *"{s}"*' for s in (
            TRIPPING,
            "I don't think I am vague at all",
            "Refusing work from me because it does not fit your own standards "
            "is clearly nonsensical"))
        counted, _ = _counted_and_exempt(N, body)
        assert counted == [], (
            f"a note consisting only of his quoted words produced "
            f"{len(counted)} finding(s), so the commit hook would refuse it and "
            f"the only remedies would be editing him or bypassing the guard")
