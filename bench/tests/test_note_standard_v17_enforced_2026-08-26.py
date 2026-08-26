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


def _v17_notes():
    out = []
    for p in sorted(NOTES.glob("*.md")):
        m = FOOTLINE.search(p.read_text(encoding="utf-8", errors="replace"))
        if m and (int(m.group(1)), int(m.group(2))) >= (1, 7):
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
        hits = [(n, k, t) for n, k, t, _ in lint.lint(path)
                if RULE_27 in k or RULE_28 in k]
        assert not hits, (
            f"{path.name} declares v1.7 and violates it:\n"
            + "\n".join(f"    para {n}  {k}  {t!r}" for n, k, t in hits)
        )
