"""The verbatim exemption lived in `main`, so a guard that never read `main` blocked on a seat's words.

WHAT HAPPENED, 2026-09-11. A full-suite run in a fresh clone failed on
`Panel_Roster_Round2_FULL_RECORD_2026-09-09.md`. The offending sentence sits at
line 290, between `<!-- verbatim-begin: fable -->` (line 276) and its
`verbatim-end` (line 329) -- it is what the seat `fable` wrote, and task V8
exists precisely so a seat's words reach the record unedited.

THE SHAPE IS THIS SESSION'S RECURRING ONE: 2 consumers of 1 rule, and only 1
resolves it. `scripts/note_vagueness_lint.py`'s CLI computed
`verbatim_paragraphs()` and subtracted them; `test_note_standard_v17_enforced`
called `lint()` raw and subtracted nothing. Each was internally consistent, so
neither could detect the disagreement -- which is what `execute-do-not-grep` says
about source-text agreement.

THE FIX IS 1 IMPLEMENTATION, NOT 2 THAT AGREE. `partition()` owns the split and
`main` calls it, so the CLI cannot drift from what a guard gates on.

A SECOND, INDEPENDENT DEFECT WAS UNDER IT. `"the decay curve measure" in low` is
a bare substring test, and it fires on "the decay curve measureS the latter" --
a verb, using the founder's own term as a subject, which Rule 28 does not ban.
MEASURED over 402 notes: 28 substring matches, 27 bounded. The boundary drops
exactly 1 and it is that verb. The 2 defects are independent, and
`test_a_seat_quote_is_reported_but_does_not_gate` proves it by putting the NOUN
form inside a verbatim region: still reported, still not counted.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"

VIOLATION = "The decay curve measure reached 0.607 at round 6."


@pytest.fixture(scope="module")
def lint():
    spec = importlib.util.spec_from_file_location("nvl", LINT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _note(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "note.md"
    f.write_text(body, encoding="utf-8")
    return f


class TestTheExemptionIsOneImplementation:
    def test_the_cli_counts_exactly_what_blocking_returns(self, lint, tmp_path):
        """EXECUTE BOTH FORMS. The CLI is run as a subprocess and its printed
        total is compared with `len(blocking(...))` -- not with a claim about
        what it does. This is the check whose absence let the 2 drift."""
        note = _note(tmp_path, f"<!-- verbatim-begin: a seat -->\n\n{VIOLATION}\n\n"
                               f"<!-- verbatim-end -->\n\n{VIOLATION}\n")
        r = subprocess.run([sys.executable, str(LINT), str(note)],
                           capture_output=True, text=True, timeout=120)
        m = re.search(r"(\d+) finding\(s\)\. Reported", r.stdout)
        assert m, f"the CLI total line is gone; output was:\n{r.stdout[-800:]}"
        assert int(m.group(1)) == len(lint.blocking(note)), (
            f"the CLI counted {m.group(1)} and blocking() returned "
            f"{len(lint.blocking(note))}; they must be the same function")

    def test_main_does_not_re_derive_the_split(self, lint):
        """RATCHET, and it is a source check because it is about who CALLS what.
        The executing proof is the test above."""
        src = LINT.read_text(encoding="utf-8")
        body = src[src.index("def main("):]
        assert "partition(" in body, "main no longer calls partition()"
        assert "verbatim_paragraphs(" not in body, (
            "main computes the verbatim split itself again; that is the 2nd "
            "implementation this file exists to prevent")


class TestASeatsWordsDoNotGate:
    def test_a_seat_quote_is_reported_but_does_not_gate(self, lint, tmp_path):
        """ANTI-VACUITY. The NOUN form -- a genuine Rule 28 violation the
        boundary fix does NOT touch -- inside a verbatim region. `lint` must
        still SEE it (an exemption nobody can see is a checker that missed
        something) and `blocking` must not COUNT it."""
        note = _note(tmp_path, "<!-- verbatim-begin: a seat -->\n\n"
                               f"{VIOLATION}\n\n<!-- verbatim-end -->\n")
        assert [h for h in lint.lint(note) if "Rule 28" in h[1]], (
            "lint() no longer reports inside verbatim regions; the exemption "
            "has become a silent drop")
        assert not [h for h in lint.blocking(note) if "Rule 28" in h[1]]

    def test_the_same_violation_outside_a_region_still_gates(self, lint, tmp_path):
        """POSITIVE CONTROL. Without the markers the very same sentence must
        block, or the exemption is just a disabled rule."""
        note = _note(tmp_path, VIOLATION + "\n")
        assert [h for h in lint.blocking(note) if "Rule 28" in h[1]], (
            "a Rule 28 violation in the note's own voice is not counted; the "
            "exemption is leaking outside verbatim regions")

    def test_the_real_record_that_failed_is_clean_now(self, lint):
        """The note that actually broke the clone run."""
        note = REPO / "experimental_notes" / "Panel_Roster_Round2_FULL_RECORD_2026-09-09.md"
        if not note.is_file():
            pytest.skip("the record has been renamed or removed")
        assert not lint.blocking(note), (
            f"{note.name} counts findings again: {lint.blocking(note)}")


class TestTheMatcherIsBounded:
    def test_the_verb_form_is_not_a_category_noun(self, lint, tmp_path):
        note = _note(tmp_path, "Routing changes resolution, never discovery "
                               "attribution -- the decay curve measures the latter.\n")
        assert not [h for h in lint.lint(note) if "Rule 28" in h[1]]

    def test_an_inflection_is_not_the_noun(self, lint, tmp_path):
        note = _note(tmp_path, "the decay curve measurement was taken at round 6.\n")
        assert not [h for h in lint.lint(note) if "Rule 28" in h[1]]

    def test_the_noun_itself_is_still_caught(self, lint, tmp_path):
        """POSITIVE CONTROL for the boundary: the rule must still fire."""
        note = _note(tmp_path, VIOLATION + "\n")
        hits = [h for h in lint.lint(note) if "Rule 28" in h[1]]
        assert hits, "Rule 28 no longer fires at all; the boundary disabled it"
        assert "gamma" in hits[0][1], hits

    def test_every_phrase_still_matches_itself(self, lint, tmp_path):
        """A bounded pattern that matched nothing would pass every test above.
        Each phrase is fed back to the matcher it came from."""
        for phrase in lint.CATEGORY_NOUN:
            note = _note(tmp_path, f"A sentence using {phrase} in it.\n")
            assert [h for h in lint.lint(note) if "Rule 28" in h[1]], phrase
