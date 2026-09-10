"""Task A5: the canonical-tree alarm must say WHOSE doing it was.

THE DEFECT. The alarm fired on 14 files in panel round 2, 8 in round 8 and 11 in
round 9, and EVERY ONE was the operator's own concurrent edit. Confinement held
in all 3. But the alarm could not say so, so a human re-derived it from the tool
logs each time -- and "an alarm that fires on the ordinary case is on its way to
being ignored" is this project's own warning about its irreducible-queue alarm.

THE EVIDENCE WAS ALREADY ON DISK. Each seat's `*.tools.json` records every call
with an input preview. A seat that wrote to the canonical tree must have named
the path. The alarm now reads that instead of leaving it to a person.

TWO DEFECTS IN MY OWN FIRST ATTRIBUTION, both found by inspecting the hits rather
than trusting the boolean, and both would have produced a FALSE containment
failure -- the worst possible direction for this alarm:

  1. The sandbox root was not passed, so a seat editing its OWN copy at
     `/private/var/.../repo/scripts/sync_desktop_mirrors.py` was reported as
     touching the canonical file.
  2. A READ was counted as a write. Round 8 was reported attributable on the
     strength of a `sed -n '3733,3739p'` -- a seat READING a note.

With both fixed, rounds 8 and 9 report NOT ATTRIBUTABLE, which is what a human
verified by hand at the time.

IT IS CONSERVATIVE IN THE RIGHT DIRECTION. An unrecognised shell command counts
as capable of writing, because under-reporting is worse than over-reporting on
the escape half. And the verdict says "no seat is SHOWN to have touched it",
never "no seat did", because an input preview is truncated.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import panel_sandbox as ps  # noqa: E402

ROUND8 = ROOT / "bench" / "logs" / "panel_round8_2026-09-10"
ROUND9 = ROOT / "bench" / "logs" / "panel_round9_2026-09-10"
SBX8 = "/private/var/folders/cc/scptwd_s4cgclnjn5937fyjw0000gn/T/cdsfl_panel__sewni2b"
SBX9 = "/private/var/folders/cc/scptwd_s4cgclnjn5937fyjw0000gn/T/cdsfl_panel_ywfpe5hr"


class TestTheKnownFalseAlarmsAreCleared:
    @pytest.mark.parametrize("d,sbx", [(ROUND8, SBX8), (ROUND9, SBX9)],
                             ids=["round8", "round9"])
    def test_no_seat_is_shown_to_have_touched_the_canonical_tree(self, d, sbx):
        f = d / "canonical_touched.json"
        if not f.is_file():
            pytest.skip(f"{d.name} has no canonical_touched.json")
        touched = json.loads(f.read_text())
        assert touched, "the round recorded no touched files; nothing to attribute"
        a = ps.attribute_canonical_touch(touched, d, sandbox_root=sbx)
        assert a["_seats_examined"], "no tool logs were read, so the answer is vacuous"
        assert not a["_any_attributable"], (
            "a seat is now implicated in a round a human verified as clean: "
            + json.dumps({k: v["hits"] for k, v in a["_per_path"].items()
                          if v["attributable_to_a_seat"]})[:400])


class TestItCanActuallyFire:
    """Without this it reports 'clean' on any input, including a real escape."""

    def test_a_seat_that_edits_a_canonical_path_is_caught(self, tmp_path):
        (tmp_path / "seatx.tools.json").write_text(json.dumps({
            "model": "seatx",
            "calls": [{"name": "Edit",
                       "input_preview": '{"file_path": "/repo/bench/dm/_memory.py"}'}],
        }), encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path,
                                         sandbox_root="/tmp/sandbox")
        assert a["_any_attributable"] is True
        assert a["_per_path"]["bench/dm/_memory.py"]["hits"][0]["seat"] == "seatx"

    def test_a_shell_redirect_is_caught(self, tmp_path):
        (tmp_path / "seaty.tools.json").write_text(json.dumps({
            "calls": [{"name": "Bash",
                       "input_preview": '{"command": "echo x > bench/dm/_memory.py"}'}],
        }), encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path)
        assert a["_any_attributable"] is True


class TestItDoesNotCryWolf:
    def test_a_read_is_not_a_write(self, tmp_path):
        """Round 8's false positive, pinned."""
        (tmp_path / "s.tools.json").write_text(json.dumps({
            "calls": [{"name": "Bash",
                       "input_preview":
                           '{"command": "sed -n 1,5p bench/dm/_memory.py"}'}],
        }), encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path)
        assert a["_any_attributable"] is False, (
            "reading a file is reported as touching it, which is how an alarm "
            "earns a reputation for crying wolf")

    def test_an_edit_inside_the_sandbox_is_not_a_canonical_touch(self, tmp_path):
        """The other false positive: a seat editing its OWN copy."""
        sbx = "/private/var/folders/xx/cdsfl_panel_abc"
        (tmp_path / "s.tools.json").write_text(json.dumps({
            "calls": [{"name": "Edit",
                       "input_preview": '{"file_path": "%s/repo/bench/dm/_memory.py"}' % sbx}],
        }), encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path,
                                         sandbox_root=sbx)
        assert a["_any_attributable"] is False

    def test_an_unrecognised_command_is_treated_as_a_write(self, tmp_path):
        """Conservative in the right direction on the escape half."""
        (tmp_path / "s.tools.json").write_text(json.dumps({
            "calls": [{"name": "Bash",
                       "input_preview": '{"command": "frobnicate bench/dm/_memory.py"}'}],
        }), encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path)
        assert a["_any_attributable"] is True


class TestItStatesItsOwnLimit:
    def test_the_verdict_never_claims_certainty(self, tmp_path):
        (tmp_path / "s.tools.json").write_text(json.dumps({"calls": []}),
                                               encoding="utf-8")
        a = ps.attribute_canonical_touch(["bench/dm/_memory.py"], tmp_path)
        v = a["_per_path"]["bench/dm/_memory.py"]["verdict"]
        # "is SHOWN to have" is the load-bearing word: it reports the state of
        # the EVIDENCE, not the state of the world. "no seat touched it" would
        # be a claim this cannot support from truncated previews.
        assert "shown" in v, v
        assert "did not" not in v and "no seat touched" not in v, v
        assert "truncated" in a["_limit"]

    def test_the_alarm_calls_it(self):
        src = (ROOT / "bench" / "confer_maths_panel_2026-09-05.py").read_text(
            encoding="utf-8")
        assert "attribute_canonical_touch(" in src, (
            "the attribution exists and the alarm does not use it")
        assert "NO SEAT IS SHOWN TO HAVE TOUCHED" in src
        assert "This is the containment failure, not a false alarm" in src
