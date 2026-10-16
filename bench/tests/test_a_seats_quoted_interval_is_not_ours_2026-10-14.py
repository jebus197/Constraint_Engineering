"""The interval checker skips VERBATIM spans and nothing else.

WHY. A FULL RECORD reproduces panel replies between `<!-- verbatim-begin -->`
and `<!-- verbatim-end -->`, under the founder's standing instruction that they
be presented "in full and in unfiltered format". On 2026-10-14 a seat quoted
[0.0%, 8.4495%] for 0 of 41 where Wilson gives 8.5668%, and
`scripts/wilson_interval_consistency.py` refused the commit over a number nobody
here may correct. Editing it would make the record a paraphrase; bypassing the
gate would disable it for every other figure.

THE CONVENTION ALREADY EXISTED in `scripts/note_vagueness_lint.py`. This asserts
the interval checker now shares it, and -- the half that matters -- that the
exemption is NARROW: a figure in the project's own voice is still checked, before
and after a verbatim block alike.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "wilson_interval_consistency.py"

#: ★ THE WRONG INTERVAL IS BUILT, NOT WRITTEN, AND THAT IS DELIBERATE.
#:
#: A literal `[0.0%, 8.4495%]` in this source would be scanned by the very
#: checker under test and reported as a disagreement -- which is what happened
#: on the first version of this file, and it refused the commit. The script
#: already skips ITSELF for the same reason, its own comment saying its
#: docstring "carries worked examples OF the defect" so "scanning them is a
#: guaranteed false positive".
#:
#: IT IS NOT HIDDEN BEHIND THE VERBATIM EXEMPTION THIS FILE TESTS. Using that
#: exemption to conceal this file's own fixtures from the checker the exemption
#: governs would be circular: the test would pass because of the mechanism it is
#: supposed to be able to falsify. Assembling the string from parts keeps the
#: fixture out of the scanner's reach without touching the thing under test.
_BAD_HI = "8.4495"          # the seat's figure; Wilson's upper is 8.5668
_PAIR = "[0.0%, " + _BAD_HI + "%]"

OWN = f"In our own voice: 0 of 41, Wilson {_PAIR}.\n"
QUOTED = ("<!-- verbatim-begin: seat -->\n\n"
          f"A seat says 0 of 41, Wilson {_PAIR}.\n\n"
          "<!-- verbatim-end -->\n")


@pytest.fixture(scope="module")
def W():
    spec = importlib.util.spec_from_file_location("_wic", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_wic"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_a_quoted_interval_inside_the_markers_is_skipped(W):
    assert W.scan_text("r.md", QUOTED, []) == []


def test_the_same_interval_in_our_own_voice_is_still_caught(W):
    found = W.scan_text("r.md", OWN, [])
    assert len(found) == 1, found


def test_a_figure_AFTER_the_block_is_still_caught(W):
    """The boundary. A span that swallowed the rest of the file would exempt
    everything written after the first reply, which is most of a FULL RECORD."""
    found = W.scan_text("r.md", QUOTED + "\n" + OWN, [])
    assert len(found) == 1, found


def test_line_numbers_survive_the_blanking(W):
    """A finding must point at the real line, so the span is blanked rather than
    deleted -- its newlines are kept."""
    text = OWN + "\n" + QUOTED + "\n" + OWN
    found = W.scan_text("r.md", text, [])
    assert len(found) == 2, found
    lines = [f.line for f in found]
    assert lines[0] == 1, lines
    assert lines[1] == text.splitlines().index(OWN.strip()) + 1 or lines[1] > 5, lines


def test_an_unclosed_marker_does_not_exempt_the_whole_file(W):
    """FAIL CLOSED. An opening marker with no close must not silently exempt
    everything after it; the regex requires both ends."""
    found = W.scan_text("r.md", "<!-- verbatim-begin: seat -->\n\n" + OWN, [])
    assert len(found) == 1, found


# ───────── the seat-TREE exemption, added 2026-10-16, and its narrowness ─────

def test_a_harvested_seat_file_is_skipped(tmp_path):
    """A harvested seat file is verbatim seat output and is not ours to edit.

    On 2026-10-16 the fable seat delivered a test file stating
    [48.4039%, 74.7631%] for 30 of 48. Wilson is [48.3628%, 74.7847%], and no
    standard method gives the seat's figure. It is a real defect in that seat's
    work, recorded in the task list in THIS project's voice and corrected before
    the fix is adopted -- but the harvested copy is the record of what the seat
    wrote.
    """
    # ★ BUILT, NOT WRITTEN -- and this file's own docstring already said so.
    # A literal interval here is scanned by the very checker under test and
    # reported as a disagreement, which is exactly what happened to the first
    # version of this file and then happened AGAIN on 2026-10-16 when this case
    # was added with the seat's figure spelled out. The numbers are assembled
    # at run time so the source carries no scannable pair.
    _k, _n = 30, 48
    _lo, _hi = "48." + "4039", "74." + "7631"
    bad = (f"states {_k} of {_n}, 62.5000%, Wilson "
           f"[{_lo}%, {_hi}%]\n")
    for tree in ("sandbox_harvest", "seat_evidence"):
        d = tmp_path / "bench" / "logs" / "round" / tree / "fable"
        d.mkdir(parents=True)
        (d / "seat_test.py").write_text(bad)
    ours = tmp_path / "experimental_notes"
    ours.mkdir(parents=True)
    (ours / "ours.md").write_text(bad)

    import subprocess
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)],
                       capture_output=True, text=True, timeout=120)
    out = r.stdout
    assert "harvested seat file(s) skipped" in out, out[:400]
    # OUR copy of the same text must still be reported.
    assert "experimental_notes/ours.md" in out or "ours.md" in out, (
        "the same figure in THIS project's voice was not reported, so the "
        "exemption is too wide:\n" + out[:800])
    assert r.returncode != 0, (
        "a narrowed interval in our own voice no longer fails the checker:\n"
        + out[:800])
    # And the seat copies must NOT be reported.
    assert "seat_test.py" not in out, (
        "a harvested seat file was reported, so the exemption did not apply:\n"
        + out[:800])


def test_the_exemption_does_not_silence_the_canonical_copies():
    """Our own files appear inside a harvest as copies; they must still be
    checked where they really live, or the exemption would hide a live defect
    in the project's own source."""
    import subprocess
    r = subprocess.run([sys.executable, str(SCRIPT), str(REPO)],
                       capture_output=True, text=True, timeout=600)
    assert "files scanned" in r.stdout
    scanned = int(r.stdout.split("--", 1)[1].split("files scanned")[0]
                  .strip().split()[0])
    assert scanned > 2000, (
        f"only {scanned} files scanned; the exemption is swallowing the tree")
    # The loose-but-valid notes come from canonical paths, which proves the
    # canonical tree is still being read.
    assert "bench/runner_core.py" in r.stdout, r.stdout[:600]
