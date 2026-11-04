"""A TTS file carries no markup, and until 2026-11-04 nothing checked it.

THE DEFECT. The global TTS rule has always said a TTS plain-text file contains
ZERO markdown, because the founder reads these files with Firefox Read Aloud and
it speaks the asterisks. `scripts/note_vagueness_lint.py` -- the checker the
project's own rules require to be run on every note and every TTS file before
delivery -- had no rule for it. It reported
`~/Desktop/CDSFL_tts/Inventory_And_Answers_2026-11-04.txt` as 0 findings while
4 asterisks, 2 backticks and 1 em-dash sat in it.

HOW THEY GOT THERE, which is the generalisable part. A correction script applied
the same string replacement to a markdown note and its TTS companion and
stripped the markup from neither, so a sentence written as
`**The header ... said 8 ...**` with a backticked seat name and an em-dash went
into the spoken file verbatim. A TTS file and its markdown companion carry the
SAME CONTENT in DIFFERENT FORMS, so any edit applied to both must be re-rendered
for the spoken one, never copied.

WHY THE PATTERNS ARE NARROW, MEASURED BEFORE SHIPPING. Across 890 TTS files, 5
of 6 candidate predicates had confirmed false positives, and this file pins every
one of them so none is re-added:
  1. a bare `*` fires on multiplication, 252 files and 26,213 occurrences;
  2. a bare backtick fires on a SMILES string, 226 files;
  3. `^#` IS THE FOUNDER'S OWN ANNOTATION MARKER -- he opens a comment with a
     single hash, and his own format-test file states it -- 155 files;
  4. 2 or more `|` on a line fires on absolute-value bars, 147 files;
  5. `[x](y)` fires on the SMILES query for a carboxylic acid, 4 files.
What ships has 0 false positives in that corpus: a PAIRED bold span, a line
opening with an asterisk and a space, and an em-dash.

THE RULE IS REPORTED, NOT ENFORCED, and that is sufficient because running the
linter before delivering a note is already mandatory, and because the pre-commit
ratchet is a per-file DELTA -- so history reports without blocking, and a new
file must come in at 0.
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT_SRC = REPO / "scripts" / "note_vagueness_lint.py"
KIND = "MARKDOWN IN A TTS FILE"

_spec = importlib.util.spec_from_file_location("_nvl_md", LINT_SRC)
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)

HEAD = "CDSFL Markup Probe\n\n4 November 2026, 06:00 GMT\n\n"
FOOT = "\n\nWritten under CDSFL note standard v1.9 (1 November 2026).\n"


def _tts_file(tmp_path, body: str) -> pathlib.Path:
    """A path `_is_tts` recognises: any folder whose name ends `_tts`."""
    d = tmp_path / "Probe_tts"
    d.mkdir(exist_ok=True)
    f = d / "Probe_2026-11-04.txt"
    f.write_text(HEAD + body + FOOT, encoding="utf-8")
    return f


def _md_file(tmp_path, body: str) -> pathlib.Path:
    f = tmp_path / "Probe_2026-11-04.md"
    f.write_text(HEAD + body + FOOT, encoding="utf-8")
    return f


def _kinds(f):
    return [k for _, k, _, _ in lint.lint(f)]


# ------------------------------------------------------- it is not vacuous

def test_the_rule_exists_in_the_checker():
    """ANTI-VACUITY. Without the table every negative test below passes trivially."""
    assert hasattr(lint, "MARKDOWN_IN_TTS"), (
        "the markdown table is gone from the linter; every discrimination test "
        "in this file would pass for the wrong reason")
    assert len(lint.MARKDOWN_IN_TTS) >= 3


# ------------------------------------------------- the 3 forms are reported

@pytest.mark.parametrize("body,why", [
    ("**The header of this section said 8** and that is a bold span.",
     "paired bold, the exact form a correction script copied in"),
    ("* a bullet marker opens this line",
     "a bullet marker, spoken as an asterisk"),
    ("A sentence with an em-dash — right here.",
     "an em-dash, which the rule replaces with a comma or a full stop"),
])
def test_markup_in_a_tts_file_is_reported(body, why, tmp_path):
    assert any(KIND in k for k in _kinds(_tts_file(tmp_path, body))), (
        f"not reported: {why} -- {body!r}")


def test_the_exact_bytes_the_correction_script_wrote_are_reported(tmp_path):
    """The real defect, byte for byte, minus the backticked seat name.

    Kept separate from the parametrised cases so a future narrowing of the
    patterns cannot silently stop catching the thing that actually happened.
    """
    body = ("He asked for the inventory to be cross verified or refuted against "
            "every printed and saved source. 9 figures or claims did not survive "
            "that check, and all 9 were mine. **The header of this section said 8 "
            "against a list of 9 until the fable seat's recount caught it** "
            "— a header disagreeing with its own tally.")
    assert any(KIND in k for k in _kinds(_tts_file(tmp_path, body)))


# --------------------------------- the 5 refuted predicates must stay refuted

@pytest.mark.parametrize("body,source", [
    ("Ephemeral * SPK_B is the product, and the purpose is forward secrecy.",
     "multiplication, from the Signal protocol note"),
    ("Y_union of t equals the size of the union of all F_i of t * H_bar_union of t.",
     "multiplication, from the mathematical framework note"),
    ("The carboxylic acid query is CX3 =O OX2H1 in its own span.",
     "a SMILES string, which put backticks in 226 files"),
    ("# A comment of the founder's opens with a single hash symbol.",
     "HIS OWN ANNOTATION MARKER -- 155 files, and accusing it is the worst "
     "available outcome"),
    ("The update is KDF of root_key | salt | info, keyed on the shared secret.",
     "a pipe used as a separator, and absolute-value bars, 147 files"),
])
def test_a_refuted_predicate_is_not_reinstated(body, source, tmp_path):
    kinds = _kinds(_tts_file(tmp_path, body))
    assert not any(KIND in k for k in kinds), (
        f"the markdown rule now accuses {source}: {body!r} -> {kinds}")


# ------------------------------------------------------------ it is TTS-gated

def test_a_markdown_file_is_not_accused(tmp_path):
    """Bold in a .md note is CORRECT formatting, and this rule must not touch it."""
    body = "**The header of this section said 8** and that is correct in markdown."
    assert not any(KIND in k for k in _kinds(_md_file(tmp_path, body))), (
        "the TTS markup rule fired on a markdown note, where bold is correct")


def test_the_gate_is_the_same_predicate_the_stamp_rule_uses(tmp_path):
    """One declaration of what a TTS file is, not 2 that can drift apart."""
    f = _tts_file(tmp_path, "A plain sentence with no markup at all.")
    assert lint._is_tts(f) is True
    assert lint._is_tts(_md_file(tmp_path, "plain")) is False


# -------------------------------------------- the delivered files are clean

def test_the_notes_delivered_on_the_4th_carry_no_markup():
    """The files this rule was written for must themselves pass it.

    Skipped rather than failed where a Desktop mirror is absent, because the
    Desktop is not versioned and its absence is not a defect in the repository.
    """
    targets = [pathlib.Path.home() / "Desktop" / "CDSFL_tts"
               / "Inventory_And_Answers_2026-11-04.txt",
               pathlib.Path.home() / "Desktop" / "CDSFL_tts"
               / "Closing_Report_The_Period_2026-11-04.txt"]
    present = [t for t in targets if t.is_file()]
    if not present:
        pytest.skip("no Desktop TTS mirror on this machine")
    for t in present:
        bad = [k for _, k, _, _ in lint.lint(t) if KIND in k]
        assert not bad, f"{t.name} carries markup: {bad}"
