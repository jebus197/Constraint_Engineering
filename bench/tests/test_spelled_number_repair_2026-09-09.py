"""The spelled-number repair must refuse everything it cannot parse exactly.

Task 7.1, bounded slice. `no-word-numbers` is a founder ruling restated after
repeated violation, and a spelled quantity is a reproducibility problem: "fifty
seven tests green" cannot be grepped or compared, "57 tests green" can.

THE DANGER IS NOT MISSING A CONVERSION, IT IS MAKING A WRONG ONE. A wrong number
is worse than a spelled one, because it reads as a measurement. The first dry run
over 379 notes produced 3 distinct classes of false figure, every one of them
caught by reading the proposals before writing anything:

  "ten thousand million million"      -> 2010000   stacked scales
  "reaches zero three times"          -> "3 times" 2 bare units side by side
  "between fifteen and twenty five thousand" -> 40000   a RANGE summed

Each is now refused. The tests below are written around those 3 cases rather than
around the happy path, because the happy path was never the risk.

QUOTATIONS ARE SAFE BY CONSTRUCTION: candidates come from the linter, whose
exemption masks double-quoted spans, and the substitution is anchored on the
flagged sentence rather than on the file's first match -- so a token that also
appears inside a verbatim founder quotation earlier in the file cannot be
rewritten.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "repair", REPO / "scripts" / "spelled_number_repair_2026-09-09.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


@pytest.mark.parametrize("phrase,expected", [
    ("twenty five", 25),
    ("twenty-five", 25),
    ("fifty seven", 57),
    ("one hundred and sixty five", 165),
    ("one thousand and two", 1002),
    ("twenty-five thousand", 25000),
    ("three thousand four hundred and eighty four", 3484),
    ("two thousand five hundred and thirty eight", 2538),
    ("ten million", 10000000),
])
def test_clean_numerals_parse(phrase, expected):
    assert R.parse_words(phrase) == expected


@pytest.mark.parametrize("phrase,why", [
    ("ten thousand million million", "stacked scales: a left-to-right sum gave 2010000"),
    ("zero three", "2 bare units: 'reaches zero three times' is not 3 times"),
    ("seven one", "2 bare units: 'point seven one' is 0.71"),
    ("forty and two", "a price range, 1 pound 40 to 2 pounds 30"),
    ("fifteen and twenty five thousand", "a range, 15000 to 25000, summed to 40000"),
    ("thousand thousand", "a repeated scale"),
    ("banana", "not a numeral at all"),
])
def test_ambiguous_phrases_are_REFUSED(phrase, why):
    """EVERY ONE OF THESE WAS A REAL PROPOSAL BEFORE THE GUARDS EXISTED."""
    assert R.parse_words(phrase) is None, why


def test_and_is_allowed_only_after_a_scale():
    """The rule that separates 165 from a range."""
    assert R.parse_words("one hundred and sixty five") == 165
    assert R.parse_words("fifty and sixty") is None


def test_the_corpus_dry_run_makes_no_unparseable_conversion():
    """RUN OVER THE REAL NOTES, not a fixture.

    Every candidate the linter offers is either converted to a value that parses
    cleanly, or refused. A candidate that converted to None would be a crash
    waiting for the writer."""
    notes = sorted((REPO / "experimental_notes").rglob("*.md"))
    assert notes, "no notes found, the test would be vacuous"
    converted = refused = 0
    for p, token, sentence in R.sites(notes):
        idx = sentence.lower().find(token.lower())
        before = sentence[:idx] if idx >= 0 else ""
        value = R.parse_words(token)
        if value is None or R.REFUSE_BEFORE.search(before):
            refused += 1
            continue
        assert isinstance(value, int) and value >= 0, (token, value)
        converted += 1
    assert converted + refused > 0
    assert refused > 0, (
        "nothing was refused across the whole corpus, which means the guards "
        "stopped discriminating")


def test_the_script_writes_nothing_without_apply(tmp_path, monkeypatch, capsys):
    """A repair that edits on a dry run is not a dry run."""
    note = tmp_path / "n.md"
    body = ("# n\n\nThe run recorded fifty seven findings and 3 rounds.\n\n"
            "Written under CDSFL note standard v1.7 (26 August 2026).\n")
    note.write_text(body, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["repair", str(note)])
    R.main()
    assert note.read_text(encoding="utf-8") == body, "the dry run modified a file"
    assert "DRY RUN" in capsys.readouterr().out


def test_apply_converts_and_leaves_the_rest_alone(tmp_path, monkeypatch):
    note = tmp_path / "n.md"
    note.write_text("# n\n\nThe run recorded fifty seven findings and 3 rounds.\n\n"
                    "Written under CDSFL note standard v1.7 (26 August 2026).\n",
                    encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["repair", "--apply", str(note)])
    R.main()
    out = note.read_text(encoding="utf-8")
    assert "57 findings" in out, out
    assert "3 rounds" in out
    assert "fifty seven" not in out


def test_a_token_inside_a_quotation_is_never_rewritten(tmp_path, monkeypatch):
    """THE PROPERTY THAT PROTECTS THE FOUNDER'S WORDS.

    The same spelled form appears twice: once inside a verbatim quotation, which
    the linter exempts, and once in the assistant's own prose. Only the second
    may change, and it must change even though the first occurrence in the file
    is the quoted one."""
    note = tmp_path / "n.md"
    note.write_text(
        '# n\n\nThe founder wrote, verbatim: "there were fifty seven of them". '
        'The assistant then recorded fifty seven findings in its own prose.\n\n'
        "Written under CDSFL note standard v1.7 (26 August 2026).\n",
        encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["repair", "--apply", str(note)])
    R.main()
    out = note.read_text(encoding="utf-8")
    assert '"there were fifty seven of them"' in out, (
        "the verbatim quotation was rewritten")
    assert "recorded 57 findings" in out, out
