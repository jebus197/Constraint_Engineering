"""A bold span opening with a digit must not be read as a task entry.

THE SAME MISTAKE 4 TIMES IN ONE DAY, WHICH IS WHY THIS IS A CHECKER AND NOT A
FIFTH NOTE. Writing a paragraph that begins `**3 GUARDS ...**` or `**4 FAULTS
...**` at the start of a line makes `parse_entries` read it as an entry heading
and mint a phantom entry with the identifier `3` or `4`. It happened on
2026-11-01 while adding entries, was recorded in memory as a lesson after the
second occurrence, and happened twice more after that. A rule restated and
broken again is the shape `additive-standard` names: the fix is a mechanism, not
another restatement.

WHY A BARE INTEGER IS THE RIGHT SIGNATURE, MEASURED BEFORE THE RULE WAS WRITTEN.
Over 209 live entries: **0 carry a bare-integer identifier**, 36 carry a dotted
numeric one (0.1, 1.1, 10.2 — the project's original numbering) and 173 carry a
lettered one. So a bare integer is never a legitimate entry and always a
phantom, while the dotted scheme is untouched. A looser rule banning every
numeric identifier would have accused 36 correct entries, which is the
guard-accusing-correct-material class measured at 9 of 36 on 2026-10-28.

WHAT A PHANTOM COSTS. It inflates the entry count, it carries no marker so its
state is unknown, and the resume pointer and every closure measurement read it
as real work. It is also invisible in prose: the paragraph looks right.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as TLM  # noqa: E402

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
_BARE_INT = re.compile(r"^\d+$")


def test_no_entry_identifier_is_a_bare_integer():
    phantoms = [e.ident for e in TLM.parse_entries(LIST)
                if _BARE_INT.match(e.ident)]
    assert not phantoms, (
        f"{len(phantoms)} phantom entry/entries minted by a bold span opening "
        f"with a digit: {phantoms}. Reword the paragraph so it does not begin "
        f"`**<digit>` at the start of a line — for example 'THERE ARE 4 FAULTS' "
        f"rather than '4 FAULTS'. The identifier tells you which number to look "
        f"for.")


def test_the_dotted_numbering_scheme_is_untouched():
    """ANTI-VACUITY WITH TEETH. The project's own entries 0.1 through 10.2 are
    numeric and legitimate. A rule banning numeric identifiers outright would
    accuse all of them, so this asserts they survive."""
    ids = [e.ident for e in TLM.parse_entries(LIST)]
    dotted = [i for i in ids if re.fullmatch(r"\d+\.\d+[a-z]?", i)]
    assert len(dotted) >= 30, (
        f"only {len(dotted)} dotted numeric entries remain of the 36 measured "
        f"on 2026-11-01; if the scheme was retired, relax this test "
        f"deliberately rather than letting it pass on an absence")


def test_a_planted_phantom_is_caught(tmp_path):
    """THE TEETH. Without this the test above passes on a clean file and would
    keep passing if `parse_entries` stopped recognising headings at all."""
    f = tmp_path / "list.md"
    f.write_text(
        "**A1. A real entry.**\n"
        "<!-- task: A1 | state: OPEN | status: PROPOSED -->\n\n"
        "**3 GUARDS THAT PINNED THE DEFECT ARE INVERTED.** Prose, not an entry.\n\n",
        encoding="utf-8")
    idents = [e.ident for e in TLM.parse_entries(f)]
    assert "3" in idents, (
        "the parser no longer mints a phantom from this shape, so the rule "
        "above is guarding nothing — verify that before deleting it")
    assert [i for i in idents if _BARE_INT.match(i)] == ["3"]


def test_the_reworded_form_is_not_caught(tmp_path):
    """And the remedy the message recommends actually works."""
    f = tmp_path / "list.md"
    f.write_text(
        "**A1. A real entry.**\n"
        "<!-- task: A1 | state: OPEN | status: PROPOSED -->\n\n"
        "**THERE ARE 3 GUARDS AND THEY ARE INVERTED.** Prose, not an entry.\n\n",
        encoding="utf-8")
    idents = [e.ident for e in TLM.parse_entries(f)]
    assert not [i for i in idents if _BARE_INT.match(i)], idents
