"""The note-standard stamp belongs at the foot of a note, not its head.

HIS OBJECTION, 2026-10-24 (annotation 4 of
`Why_sv_Was_Blocked_And_Twelve_Lost_Annotations_2026-10-19.txt`): *"You also break
with convention by listing the note standard at the head of this tts file, rather
than at the end? If there is a valid reason for either of these, please discuss
them with me."*

There was no valid reason. The project's own vocabulary already named it the
FOOT-LINE convention, and it was measured before a threshold was chosen: of 582
stamped notes, 559 (0.9605) place the stamp in the final 10% of non-blank lines.
The rule therefore costs 23 findings over 582 files, not the 357 of 536 an earlier
unmeasured rule produced.

These tests CALL the rule over temporary files rather than reading its source.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"

spec = importlib.util.spec_from_file_location("_nvl_foot", LINT)
NVL = importlib.util.module_from_spec(spec)
sys.modules["_nvl_foot"] = NVL
spec.loader.exec_module(NVL)

BODY = "\n".join(f"Paragraph {i} of ordinary prose, with 12 words and no vagueness."
                 for i in range(1, 25))
STAMP = f"Written under CDSFL note standard {NVL.CURRENT_NOTE_STANDARD}."


def _note(tmp_path: pathlib.Path, text: str, name="Note_2026-10-25.md"):
    d = tmp_path / "experimental_notes"     # the rule is path-scoped by design
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text(text, encoding="utf-8")
    return f


def _placement(findings):
    return [f for f in findings if "placement" in str(f[2])]


def test_a_stamp_at_the_foot_is_clean(tmp_path):
    f = _note(tmp_path, BODY + "\n\n" + STAMP + "\n")
    assert _placement(NVL.missing_standard_stamp(f)) == []


def test_a_stamp_at_the_head_is_reported(tmp_path):
    """HIS CASE. The exact shape he objected to."""
    f = _note(tmp_path, STAMP + "\n\n" + BODY + "\n")
    hits = _placement(NVL.missing_standard_stamp(f))
    assert len(hits) == 1, f"the head stamp was not reported: {hits}"
    assert "at the HEAD" in hits[0][1]


def test_a_stamp_in_the_middle_is_reported(tmp_path):
    half = BODY.splitlines()
    mid = "\n".join(half[:12]) + "\n\n" + STAMP + "\n\n" + "\n".join(half[12:])
    f = _note(tmp_path, mid + "\n")
    hits = _placement(NVL.missing_standard_stamp(f))
    assert len(hits) == 1
    assert "of the way through" in hits[0][1], hits[0][1]


def test_a_short_file_is_exempt(tmp_path):
    """Under 10 non-blank lines there is no meaningful head or foot.

    Without this, a 3-line note would be reported for a stamp that cannot be
    anywhere else, which is the noise that gets a rule switched off.
    """
    f = _note(tmp_path, f"{STAMP}\nOne line of prose here.\n")
    assert _placement(NVL.missing_standard_stamp(f)) == []


def test_placement_survives_an_archival_version_stamp(tmp_path):
    """A correctly-stamped OLD standard at the head is still misplaced.

    The version check returns early for an archival stamp; if the placement
    finding were built after that return it would be silently dropped.
    """
    old = sorted(NVL.ARCHIVAL_NOTE_STANDARDS)[0]
    f = _note(tmp_path, f"Written under CDSFL note standard {old}.\n\n" + BODY + "\n")
    hits = _placement(NVL.missing_standard_stamp(f))
    assert len(hits) == 1, (
        "the placement finding was dropped on the archival-version path")


def test_placement_survives_an_invented_version_stamp(tmp_path):
    """Same, for the final return path."""
    f = _note(tmp_path, "Written under CDSFL note standard v99.9.\n\n" + BODY + "\n")
    fr = NVL.missing_standard_stamp(f)
    assert len(_placement(fr)) == 1, "placement dropped on the invented-version path"
    assert any("NOT A STANDARD THIS" in str(r[1]) for r in fr), \
        "the version finding was lost"


def test_a_file_outside_a_note_folder_is_untouched(tmp_path):
    """`additive-standard`: the rule must not widen past its scope."""
    f = tmp_path / "README.md"
    f.write_text(STAMP + "\n\n" + BODY + "\n", encoding="utf-8")
    assert NVL.missing_standard_stamp(f) == []


def test_the_measured_rate_still_holds():
    """The calibration is a committed claim and must stay true.

    23 of 582 = 0.0395 as measured on 2026-10-25. A material drift means either
    the archive changed or the rule did, and either way the threshold needs
    rechecking before it is trusted.
    """
    roots = [REPO / "experimental_notes"]
    roots += [p for p in (pathlib.Path.home() / "Desktop").glob("*_tts") if p.is_dir()]
    stamped = flagged = 0
    for root in roots:
        if not root.is_dir():
            continue
        for f in root.rglob("*"):
            if f.suffix.lower() not in (".md", ".txt") or not f.is_file():
                continue
            try:
                txt = f.read_bytes().decode("utf-8", "ignore")
            except OSError:
                continue
            if not NVL.NOTE_STANDARD_STAMP.search(txt):
                continue
            stamped += 1
            if _placement(NVL.missing_standard_stamp(f)):
                flagged += 1
    if stamped < 400:
        pytest.skip(f"only {stamped} stamped notes visible; not the measured corpus")
    rate = flagged / stamped
    assert rate < 0.10, (
        f"placement findings are {flagged} of {stamped} = {rate:.4f}, well above "
        f"the measured 0.0395. A rule this noisy gets switched off; recheck the "
        f"threshold before trusting it.")
