"""A falsifier run against an absent or empty document must ABSTAIN, not decide.

WHY THIS EXISTS, and it is the founder's instruction of 2026-09-30 ("Do it!") on
a control the cc2 panel seat proposed: *"a falsifier run against a document whose
bytes are gone must not return REFUTED."*

WHAT THE SEAT MEASURED, reproduced here exactly before the repair: through the
project's own decider `falsifier_verify.reverify_falsifier` against an empty file,
`structural` and `metrology` returned **REFUTED** and the other 3 returned
**CONFIRMED** -- 3 of 5 passing the seat's control, Wilson [23.0724%, 88.2379%].

THE CONTROL AS PROPOSED IS TOO WEAK, WHICH IS THE ADDITION THIS FILE MAKES.
REFUTED on a blank document is the dangerous half: REFUTED means the claim is no
longer there, so a fix that DELETES the target reads as a successful correction.
But CONFIRMED on a blank document is also wrong -- it asserts the false claim is
PRESENT in a document with no text. Both are verdicts about a document that is not
there. Measured: 0 of 5 abstained. So the correct property is not "not REFUTED"
but ERROR, and this file requires it of all 5 rather than of the 2 the weaker
control caught.

AND THE REPAIR MUST NOT COST THE PROPERTY THE CORPUS EXISTS TO PROVE. The anchor
being absent from a document that DOES have content is a different case and still
means NOT FALSIFIED, hence REFUTED -- that is exactly what makes this corpus
bidirectional. Every case below is therefore checked together: pristine CONFIRMED,
corrected REFUTED, blank ERROR, missing ERROR. Checking the new property alone
would let a guard pass while destroying the old one.

A DEFECT IN THE FIRST ATTEMPT AT THIS REPAIR, recorded because it is the reason
this file checks the pristine case too. The first guard used a `\\n` escape that
resolved to a real newline inside the template string, so every generated
falsifier was an unterminated string literal and ALL 5 returned ERROR --
including pristine. The blank-target property passed perfectly while the corpus
was entirely broken.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))

import stem_fixtures as S  # noqa: E402
from bench.falsifier_verify import reverify_falsifier  # noqa: E402


def _verdict(code: str) -> str:
    r = reverify_falsifier(code, repo_root=str(REPO))
    return r if isinstance(r, str) else getattr(r, "verdict", repr(r))


@pytest.fixture(scope="module")
def fixtures():
    fx = S.load_all()
    assert len(fx) >= 5, f"only {len(fx)} fixtures loaded; the corpus is the population"
    return fx


@pytest.mark.parametrize("key", [f.key for f in S.load_all()])
class TestEveryFalsifierHandlesAllFourTargetStates:
    def _fx(self, fixtures, key):
        return next(f for f in fixtures if f.key == key)

    def test_pristine_is_CONFIRMED(self, fixtures, key):
        """The planted false claim must still be caught. Guards the guard."""
        fx = self._fx(fixtures, key)
        v = _verdict(fx.falsifier())
        assert v == "CONFIRMED", (
            f"{key}: pristine document returned {v}, not CONFIRMED. The falsifier no "
            f"longer detects the claim it was written for -- check the generated "
            f"source compiles before blaming the document.")

    def test_corrected_is_REFUTED(self, fixtures, key, tmp_path):
        """The bidirectional property the corpus exists to prove."""
        fx = self._fx(fixtures, key)
        doc = tmp_path / fx.doc_name
        doc.write_text(fx.apply(fx.correct_fix), encoding="utf-8")
        v = _verdict(fx.falsifier(doc))
        assert v == "REFUTED", (
            f"{key}: the CORRECTED document returned {v}, not REFUTED. An absent "
            f"anchor in a document that HAS content is the corrected case and must "
            f"stay REFUTED; if the absent-target guard is firing here it is scoped "
            f"too widely.")

    def test_an_empty_document_ABSTAINS(self, fixtures, key, tmp_path):
        fx = self._fx(fixtures, key)
        doc = tmp_path / fx.doc_name
        doc.write_text("", encoding="utf-8")
        v = _verdict(fx.falsifier(doc))
        assert v == "ERROR", (
            f"{key}: an EMPTY document returned {v}. REFUTED would let a fix that "
            f"deletes the target read as a successful correction; CONFIRMED would "
            f"assert the false claim is present in no text. Neither is a verdict a "
            f"falsifier is entitled to on an absent document.")

    def test_a_missing_document_ABSTAINS(self, fixtures, key, tmp_path):
        fx = self._fx(fixtures, key)
        v = _verdict(fx.falsifier(tmp_path / ("absent_" + fx.doc_name)))
        assert v == "ERROR", (
            f"{key}: a MISSING document returned {v}, not ERROR")


class TestTheExistsBranchEarnsItsPlace:
    """The `exists` check would otherwise be an addition that does nothing.

    FOUND BY P-PASSING THIS FILE: deleting the `_os.path.exists(DOC)` branch left
    all 22 tests green, because the `open(DOC)` below it raises FileNotFoundError,
    which exits non-zero, which the decider already reads as ERROR. The verdict is
    identical either way. By the project's own additive standard an addition
    nothing reaches is not additive, so the branch has to change something a test
    can see, or go.

    What it changes is the RECORD a human reads: a legible one-line reason instead
    of a traceback. So that is what is asserted here, by running the generated
    falsifier directly and reading its stderr -- the decider returns only a
    verdict string and cannot carry this.
    """

    def test_a_missing_target_reports_a_reason_not_a_traceback(self, tmp_path):
        import subprocess
        fx = S.load_all()[0]
        src = tmp_path / "f.py"
        src.write_text(fx.falsifier(tmp_path / "absent.md"), encoding="utf-8")
        r = subprocess.run([sys.executable, str(src)], capture_output=True, text=True)
        assert r.returncode != 0, "a missing target exited 0; the decider would read REFUTED"
        assert "does not exist" in r.stderr, (
            f"stderr carries no stated reason: {r.stderr[-200:]!r}")
        assert "Traceback" not in r.stderr, (
            "a missing target produced a traceback rather than a stated reason; the "
            "exists branch is not doing the one thing that justifies it")

    def test_an_empty_target_reports_its_own_distinct_reason(self, tmp_path):
        import subprocess
        fx = S.load_all()[0]
        doc = tmp_path / fx.doc_name
        doc.write_text("", encoding="utf-8")
        src = tmp_path / "f2.py"
        src.write_text(fx.falsifier(doc), encoding="utf-8")
        r = subprocess.run([sys.executable, str(src)], capture_output=True, text=True)
        assert r.returncode != 0
        assert "is empty" in r.stderr, (
            f"an empty target did not report emptiness distinctly from absence: "
            f"{r.stderr[-200:]!r}")


class TestTheCheckIsNotVacuous:
    def test_the_decider_can_return_each_verdict_we_rely_on(self):
        """If the decider only ever said ERROR, every abstention test would pass."""
        fx = S.load_all()[0]
        assert _verdict(fx.falsifier()) == "CONFIRMED", (
            "the decider never returns CONFIRMED here, so the abstention assertions "
            "above are not distinguishing anything")

    def test_whitespace_only_counts_as_empty(self, tmp_path):
        """A document of blanks is as absent as a document of nothing."""
        fx = S.load_all()[0]
        doc = tmp_path / fx.doc_name
        doc.write_text("   \n\n\t\n", encoding="utf-8")
        assert _verdict(fx.falsifier(doc)) == "ERROR", (
            "a whitespace-only document was decided rather than abstained on; the "
            "guard must strip before testing emptiness")
