"""A record of someone else's words must not be editable-to-order by a linter.

THE CONFLICT, and it is real rather than anticipated. The Personalisation
directive requires panel output to be preserved *"in full and in unfiltered
format"* and says *"Never summarise in place of the full output"*. Task V3 made
`scripts/note_vagueness_lint.py` BLOCKING at commit time, as a per-file ratchet:
a new note whose finding count rises above 0 refuses the commit.

`experimental_notes/Panel_Round4_FULL_RECORD_2026-09-10.md` reproduces 2 panel
seats verbatim. It carries 4 findings and every one is inside quoted model
output, including a seat writing "nine figures", which violates `no-word-numbers`.
The only way to commit it was to edit what the models actually said. **Editing a
record to satisfy a checker falsifies the record**, which is a worse defect than
any vagueness inside it.

The founder's standing rule already contains the principle: the linter is never
applied to his words and never gates his input. `mask_quoted` carries that for
inline double quotes and cannot carry a 20,000-character transcript.

WHAT THE EXEMPTION IS NOT. It is not whole-file, it is not silent, and it is not
implicit. It is scoped to explicitly marked regions, findings inside them are
still printed under their own heading, and prose outside them is linted normally
so a note cannot buy amnesty for its own writing by quoting someone.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / "scripts" / "note_vagueness_lint.py"
RECORD = ROOT / "experimental_notes" / "Panel_Round4_FULL_RECORD_2026-09-10.md"

_spec = importlib.util.spec_from_file_location("nvl", LINT)
nvl = importlib.util.module_from_spec(_spec)
sys.modules["nvl"] = nvl
_spec.loader.exec_module(nvl)

#: A sentence the linter reliably flags: a spelled number, Rule 27.
VIOLATION = "The panel returned twenty-nine findings in total."


def _write(tmp_path, body: str) -> Path:
    f = tmp_path / "note.md"
    f.write_text(body, encoding="utf-8")
    return f


def _run(path: Path):
    return subprocess.run([sys.executable, str(LINT), str(path)],
                          cwd=ROOT, capture_output=True, text=True, timeout=180)


def _counted(out: str) -> int:
    """The number the commit hook's ratchet reads."""
    import re
    m = re.findall(r"^\s*(\d+) finding\(s\)\. Reported", out, re.M)
    assert m, f"no total line in:\n{out}"
    return int(m[-1])


class TestTheExemptionIsScoped:
    def test_a_violation_outside_the_markers_is_still_counted(self, tmp_path):
        """The load-bearing case. Without this the exemption is an amnesty."""
        body = (f"# Note\n\n{VIOLATION}\n\n"
                "<!-- verbatim-begin: someone else -->\n\nquoted prose here.\n\n"
                "<!-- verbatim-end -->\n")
        out = _run(_write(tmp_path, body)).stdout
        assert _counted(out) >= 1, (
            "a violation in the note's OWN prose was exempted; the region "
            "scoping is not working and the exemption is whole-file")

    def test_a_violation_inside_the_markers_is_not_counted(self, tmp_path):
        body = ("# Note\n\nClean prose with 29 findings.\n\n"
                "<!-- verbatim-begin: someone else -->\n\n"
                f"{VIOLATION}\n\n<!-- verbatim-end -->\n")
        out = _run(_write(tmp_path, body)).stdout
        assert _counted(out) == 0, out

    def test_it_is_reported_even_though_it_is_not_counted(self, tmp_path):
        """An exemption a reader cannot see is a checker that missed something."""
        body = ("# Note\n\nClean prose with 29 findings.\n\n"
                "<!-- verbatim-begin: someone else -->\n\n"
                f"{VIOLATION}\n\n<!-- verbatim-end -->\n")
        out = _run(_write(tmp_path, body)).stdout
        assert "inside a verbatim region" in out
        assert "[verbatim]" in out
        assert "twenty-nine" in out, (
            "the exempted finding must still be printed in full")

    def test_the_region_closes(self, tmp_path):
        """A violation AFTER the end marker must be counted again."""
        body = ("# Note\n\n<!-- verbatim-begin: someone else -->\n\n"
                "quoted prose.\n\n<!-- verbatim-end -->\n\n"
                f"{VIOLATION}\n")
        out = _run(_write(tmp_path, body)).stdout
        assert _counted(out) >= 1, (
            "the region did not close; everything after a verbatim block would "
            "be exempt forever")

    def test_a_file_with_no_markers_is_unaffected(self, tmp_path):
        out = _run(_write(tmp_path, f"# Note\n\n{VIOLATION}\n")).stdout
        assert _counted(out) >= 1, (
            "adding the mechanism changed the behaviour of notes that do not "
            "use it — that is a regression, not an addition")

    def test_an_unclosed_region_does_not_silently_swallow_the_rest(self, tmp_path):
        """Stated honestly: an unclosed region DOES extend to the end of file.

        That is the safe direction for a record — a truncated marker cannot make
        a quoted violation count — but it must be a known property rather than a
        surprise, so it is pinned here.
        """
        body = ("# Note\n\n<!-- verbatim-begin: someone else -->\n\n"
                f"{VIOLATION}\n\nand more.\n")
        out = _run(_write(tmp_path, body)).stdout
        assert _counted(out) == 0
        assert "[verbatim]" in out


class TestTheRealRecord:
    def test_the_panel_record_counts_zero_and_reports_four(self):
        if not RECORD.is_file():
            pytest.skip("the round-4 record is not present in this clone")
        out = _run(RECORD).stdout
        assert _counted(out) == 0, (
            "the verbatim panel record cannot be committed under the blocking "
            "note-lint guard, and editing it would falsify it")
        assert "inside a verbatim region" in out

    def test_the_record_still_carries_its_markers_in_pairs(self):
        if not RECORD.is_file():
            pytest.skip("the round-4 record is not present in this clone")
        text = RECORD.read_text(encoding="utf-8")
        begins = len(nvl.VERBATIM_BEGIN.findall(text))
        ends = len(nvl.VERBATIM_END.findall(text))
        assert begins == ends and begins >= 2, (
            f"{begins} begin marker(s) and {ends} end marker(s); an unmatched "
            f"pair silently exempts the rest of the file")
