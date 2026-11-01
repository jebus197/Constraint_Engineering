#!/usr/bin/env python3
"""The generated report and the spoken file must name the SAME decisions.

THE DEFECT THIS GUARDS, 2026-11-01. The generated report derived
{B21, B60, B61, B63}; the spoken file he was handed carried
{B21, B60, B61, B71}. Both said 4, so a count check passes and the sets differ:
1 real decision reached him and another did not. Nothing compared the 2
surfaces, which is the `execute-do-not-grep` shape -- 2 declarations of 1 fact
with no comparator.

AND THE SUPPRESSION THAT CAUSED HALF OF IT. B71 carries a ruling date of
2026-11-01 for the design he settled and was BLOCKED the same day on a
different question. The date comparison cannot separate 2 events on 1 day, so
the ruling was read as settling both. `ruling_is_spent` is the 1 predicate that
now decides this, in place of the same rule written out at 2 call sites.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CHECK = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
BUILD = REPO / "scripts" / "morning_report_build_2026-10-12.py"


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def surfaces():
    return _load(CHECK, "surfaces_guard")


@pytest.fixture(scope="module")
def mrb():
    return _load(BUILD, "mrb_guard")


class TestTheSurfacesAgree:
    def test_the_checker_passes_on_the_committed_state(self):
        r = subprocess.run([sys.executable, str(CHECK)], capture_output=True,
                           text=True, cwd=REPO)
        assert r.returncode == 0, (
            "the generated report and the spoken file name different decisions:\n"
            + r.stdout[-2000:])
        assert "AGREE on all" in r.stdout

    def test_every_live_decision_carries_a_join(self, surfaces):
        """A decision with no `spoken_heading` can never be checked."""
        missing = [i for i, h in surfaces.derived() if not h]
        assert not missing, (
            f"no spoken_heading, so unverifiable against the spoken file: {missing}")

    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(CHECK), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "DO THE 2 DECISION SURFACES AGREE?" not in r.stdout


class TestTheCheckerIsNotVacuous:
    """★ A CHECKER THAT CANNOT FAIL IS THE TRAP THIS PROJECT MET THE SAME DAY,
    when a rule written to stop vacuous decision reporting passed the first file
    it judged by finding 0 items. Each case below drives `main()` with a
    constructed disagreement and requires a non-zero exit."""

    def test_a_derived_decision_absent_from_the_spoken_file_is_caught(
            self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived",
                            lambda: [("B1", "ALPHA"), ("B2", "BETA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), [(1, "ALPHA")]))
        assert surfaces.main() != 0
        assert "DERIVED BUT NOT SPOKEN: BETA" in capsys.readouterr().out

    def test_a_spoken_decision_absent_from_the_record_is_caught(
            self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", "ALPHA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"),
                                     [(1, "ALPHA"), (2, "GAMMA")]))
        assert surfaces.main() != 0
        assert "SPOKEN BUT NOT DERIVED: GAMMA" in capsys.readouterr().out

    def test_a_missing_join_is_caught(self, surfaces, monkeypatch, capsys):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", None)])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), []))
        assert surfaces.main() != 0
        assert "NO JOIN FOR B1" in capsys.readouterr().out

    def test_equal_sets_pass(self, surfaces, monkeypatch):
        monkeypatch.setattr(surfaces, "derived", lambda: [("B1", "ALPHA")])
        monkeypatch.setattr(surfaces, "spoken",
                            lambda: (pathlib.Path("x.txt"), [(1, "ALPHA")]))
        assert surfaces.main() == 0

    def test_the_heading_pattern_reads_both_spellings(self, surfaces):
        """The spoken file writes a bare heading; the markdown writes `### `."""
        found = surfaces._HEADING.findall(
            "DECISION 1. ONE\n### DECISION 2. TWO\nnot a heading\n")
        assert [n for n, _ in found] == ["1", "2"]
        assert [h for _, h in found] == ["ONE", "TWO"]


class TestARulingIsSpentWhenTheEntryStillAsks:
    def test_no_ruling_is_never_spent(self, mrb):
        assert mrb.ruling_is_spent("B71", None, "BLOCKED") is False

    def test_blocked_and_still_asking_is_spent(self, mrb):
        """B71's own case: ruled and BLOCKED on the same day, different question."""
        assert mrb.ruling_is_spent("B71", "2026-11-01", "BLOCKED") is True

    def test_the_state_is_what_discriminates(self, mrb):
        """A bare still-asks test took the list from 4 to 12 earlier the same
        night, because a ruled entry keeps the sentence that was answered. Only
        BLOCKED entries are rescued by this branch."""
        assert mrb.ruling_is_spent("B71", "2026-11-01", "OPEN") is False
        assert mrb.ruling_is_spent("B71", "2026-11-01", "DONE") is False

    def test_the_entry_is_in_the_decision_list(self, mrb):
        items = mrb.task_items() + mrb.study_items()
        decs, missing, orphan = mrb.decisions(items)
        assert not missing and not orphan, (missing, orphan)
        b71 = [d for d in decs if d["key"] == "task:B71"]
        assert b71, "B71 is not even derived"
        assert not b71[0].get("no_ruling_needed"), (
            "B71 is routed to the work section, so he is never asked the "
            "permission it is blocked on")

    def test_the_asking_pattern_reads_a_permission(self, mrb):
        """The pattern had only ruling words, so a permission went unseen."""
        probe = _load(REPO / "scripts"
                      / "how_many_decisions_actually_need_him_2026-11-01.py",
                      "probe_guard")
        for phrase in ("CANNOT BE INSTALLED WITHOUT HIS PERMISSION",
                       "His confirmation of that reading is owed.",
                       "this needs your permission"):
            assert probe.ASKS.search(phrase), phrase
        for phrase in ("the file permission bits were widened",
                       "chmod changed the permissions on his home directory"):
            assert not probe.ASKS.search(phrase), f"false positive: {phrase}"
