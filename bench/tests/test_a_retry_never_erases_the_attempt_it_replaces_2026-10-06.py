#!/usr/bin/env python3
"""A re-dispatch must not destroy the record of the attempt it replaces.

THE FOUNDER'S RULING, 2026-10-06: *"We need to ensure all failures are recorded, both
here in the review rounds and more formally in the registry in both the simulated and
real experimental branches. But in review rounds we just record them appropriately, as
these clearly don't have any registry to write to. The purpose of recording failures is
that a researcher should be able to retrace all their steps to understand exactly what
happened."*

WHAT WAS DESTROYED, MEASURED. On 2026-10-06 the fable seat's first joint dispatch
returned 0 words after 435.9 s and 19 tool calls, ending in `BrokenPipeError: [Errno 32]
Broken pipe`. The re-dispatch overwrote `fable.json`. The surviving file records
`attempts: [{"attempt": 1}]` with `ok: true`, so the round's own artefacts assert a clean
single-attempt success and the failure is simply gone. A researcher retracing that round
would find no evidence the first dispatch happened at all.

IT WAS RECOVERED ONLY BY ACCIDENT, which is the argument for the fix rather than against
it. The seat's sandbox was built at 07:32:34, BEFORE the overwrite, so its copy still
held the failed file and the end-of-run `seat_proposals.diff` captured it. That recovery
is PARTIAL: the diff truncates long tool-call previews, so the `+` side does not parse as
JSON and the 19-call array is unrecoverable. Preserved at
`fable.attempt1.PARTIAL.json.txt` with its provenance and its gaps named.

THE SUFFIX IS LOAD-BEARING. A preserved `fable.attempt1.json` was counted as a REPLY by
the Section P guard while the compliance script did not count it, and the 2 populations
diverged by exactly 1 (145 against 144). `.json.txt` follows the project's existing
archival convention -- `experimental_notes/evidence/` stores seat code as `.py.txt` and
briefs as `.md.txt` -- so an archival copy stays out of the scanners that walk live
artefacts.
"""
import importlib
import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
os.environ.setdefault("PANEL_BRIEF_UNCHECKED", "1")

PANEL = importlib.import_module("confer_maths_panel_2026-09-05")


class TestTheAttemptIsKept:
    def test_a_prior_reply_is_moved_aside_not_overwritten(self, tmp_path):
        f = tmp_path / "fable.json"
        f.write_text(json.dumps({"ok": False, "error": "BrokenPipeError",
                                 "response": ""}), encoding="utf-8")
        moved = PANEL._preserve_prior_attempt(f)
        assert moved is not None and moved.is_file()
        assert not f.exists(), "the original was left in place, so a write would "\
                               "still overwrite it"
        assert json.loads(moved.read_text())["error"] == "BrokenPipeError"

    def test_the_preserved_copy_carries_the_archival_suffix(self, tmp_path):
        """REGRESSION. `.json` made the Section P guard count a preserved attempt
        as a reply, diverging from the compliance script by exactly 1."""
        f = tmp_path / "cc2.json"
        f.write_text("{}", encoding="utf-8")
        moved = PANEL._preserve_prior_attempt(f)
        assert moved.name.endswith(".json.txt"), (
            f"preserved as {moved.name!r}; a bare .json is walked by every reader "
            f"that enumerates replies")

    def test_repeated_dispatches_do_not_collide(self, tmp_path):
        f = tmp_path / "cc2.json"
        names = []
        for i in range(3):
            f.write_text(json.dumps({"attempt": i}), encoding="utf-8")
            names.append(PANEL._preserve_prior_attempt(f).name)
        assert len(set(names)) == 3, f"attempts overwrote each other: {names}"
        assert sorted(names) == sorted(
            [f"cc2.attempt{n}.json.txt" for n in (1, 2, 3)])

    def test_nothing_to_preserve_is_not_an_error(self, tmp_path):
        assert PANEL._preserve_prior_attempt(tmp_path / "absent.json") is None

    def test_the_write_site_calls_it(self):
        """An addition nothing reaches is not additive."""
        import ast
        src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text(
            encoding="utf-8")
        calls = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)
                 and (getattr(n.func, "id", None)
                      or getattr(n.func, "attr", None)) == "_preserve_prior_attempt"]
        assert len(calls) >= 2, (
            f"only {len(calls)} call(s); both the reply and the tools log must be "
            f"preserved, or half the trace is still erased")


class TestThePreservedCopyIsInvisibleToReaders:
    def test_it_is_not_counted_as_a_landed_seat(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "st_for_retry", REPO / "bench" / "star_topology_2026-10-06.py")
        st = importlib.util.module_from_spec(spec)
        sys.modules["st_for_retry"] = st
        spec.loader.exec_module(st)
        d = tmp_path / "round"
        d.mkdir()
        (d / "BRIEF.md").write_text("Q", encoding="utf-8")
        (d / "fable.json").write_text(
            json.dumps({"response": "the good reply here"}), encoding="utf-8")
        (d / "fable.attempt1.json.txt").write_text(
            json.dumps({"response": "the failed one"}), encoding="utf-8")
        assert st.landed_seats(d) == {"fable"}, (
            "a preserved attempt was counted as a seat that answered")


class TestTheRecoveredAttemptIsOnDiskAndHonest:
    PATH = (REPO / "bench" / "logs" / "capability_ladder_joint_2026-10-06"
            / "fable.attempt1.PARTIAL.json.txt")

    def test_the_destroyed_attempt_was_preserved(self):
        if not self.PATH.is_file():
            pytest.skip("the 2026-10-06 joint round is no longer on disk")
        d = json.loads(self.PATH.read_text(encoding="utf-8"))
        assert d["ok"] is False
        assert "BrokenPipeError" in (d.get("error") or "")

    def test_it_declares_itself_partial_and_names_what_is_lost(self):
        """A recovered artefact that did not say it was partial would be worse
        than none: a reader would take the gaps for facts."""
        if not self.PATH.is_file():
            pytest.skip("the 2026-10-06 joint round is no longer on disk")
        d = json.loads(self.PATH.read_text(encoding="utf-8"))
        meta = d.get("_THIS_IS_A_PARTIAL_RECOVERY")
        assert meta, "the recovered file does not declare itself a partial recovery"
        assert meta.get("recovered_from"), "no provenance"
        assert meta.get("not_recoverable"), "it does not name what could not be "\
                                            "recovered"
