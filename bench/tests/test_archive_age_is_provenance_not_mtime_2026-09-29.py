"""Experiment age must not change when files are copied.

RAISED BY AN EXTERNAL ASSESSMENT, 2026-09-29. `scripts/latent_control_audit.py`
took its age baseline from `fp.stat().st_mtime`, so the age classification of an
unchanged historical record was decided by filesystem metadata. The reviewer's
minimal closure, implemented here: *"use a preserved run timestamp or other
recorded run provenance, with an explicit unknown result when that provenance is
unavailable. Verify that touching or copying unchanged files cannot change the age
classification. Do not silently invent dates for historical records."*

REPRODUCED BEFORE THE FIX, against these same functions: touching one report with
0 bytes changed and an identical sha256 moved the baseline 58.0 days and flipped
the TOO_NEW predicate for a control first committed 2026-09-01 from True to False.
`cp`, `rsync`, a fresh checkout and a restore from backup all rewrite mtime.

WHY THE TEST EXECUTES RATHER THAN READS. `bench/tests/test_latent_control_audit_2026-09-01.py`
carries `_newest_archive_mtime()`, a hand-written MIRROR of `_archive()`. A mirror
cannot detect a producer and a consumer disagreeing, because each is internally
consistent -- the failure `execute-do-not-grep` names. Everything below calls the
real module.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def A():
    spec = importlib.util.spec_from_file_location(
        "lca_prov", REPO / "scripts" / "latent_control_audit.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["lca_prov"] = m
    spec.loader.exec_module(m)
    return m


def _ts(y: int, mo: int, d: int) -> int:
    return int(dt.datetime(y, mo, d, tzinfo=dt.timezone.utc).timestamp())


class TestProvenanceIsReadFromThePath:
    @pytest.mark.parametrize("path,want", [
        ("bench/logs/exp_20260921T222021Z/r.json", (2026, 9, 21)),
        ("bench/logs/a19_admits_harm_2026-09-22/r.json", (2026, 9, 22)),
        ("bench/logs/run_20260921_222021/r.json", (2026, 9, 21)),
        ("bench/logs/baseline_confer_run11_20260404/r.json", (2026, 4, 4)),
    ])
    def test_each_recorded_form_is_recognised(self, A, path, want):
        assert A._provenance_time(Path(path)) == _ts(*want)

    @pytest.mark.parametrize("path", [
        "bench/logs/run_99999999/r.json",      # not a date
        "bench/logs/run_20261332/r.json",      # month 13
        "bench/logs/run_20260230x9/r.json",    # trailing digit -> not a bare date
        "bench/logs/plain_name/r.json",        # nothing at all
    ])
    def test_a_non_date_is_UNKNOWN_rather_than_guessed(self, A, path):
        assert A._provenance_time(Path(path)) is None, (
            "inventing a date for a historical record is worse than reporting none")


class TestTouchingCannotChangeTheClassification:
    """The reviewer's explicit verification requirement."""

    def test_the_provenance_time_is_identical_before_and_after_a_touch(self, A, tmp_path):
        run = tmp_path / "logs" / "realrun_20260801T000000Z"
        run.mkdir(parents=True)
        fp = run / "report.json"
        fp.write_text(json.dumps({"runner_version": "v3.2", "registry": {}}))
        before_hash = hashlib.sha256(fp.read_bytes()).hexdigest()

        t0 = A._provenance_time(fp)
        for when in (_ts(2026, 1, 1), _ts(2026, 9, 28), int(time.time())):
            os.utime(fp, (when, when))
            assert A._provenance_time(fp) == t0, (
                "the recorded date moved when only the filesystem mtime changed")
        assert hashlib.sha256(fp.read_bytes()).hexdigest() == before_hash

    def test_a_copy_to_a_new_directory_keeps_its_recorded_date(self, A, tmp_path):
        """A copy preserves the NAME, which is where the provenance lives."""
        src = tmp_path / "a" / "realrun_20260801T000000Z"; src.mkdir(parents=True)
        (src / "r.json").write_text("{}")
        dst = tmp_path / "b" / "realrun_20260801T000000Z"; dst.mkdir(parents=True)
        (dst / "r.json").write_text("{}")
        now = int(time.time())
        os.utime(dst / "r.json", (now, now))
        assert A._provenance_time(src / "r.json") == A._provenance_time(dst / "r.json")


class TestTheLiveAuditNoLongerDependsOnMtime:
    def test_the_source_of_the_baseline_is_declared(self, A):
        d = A.audit(quiet=True)
        assert d["age_source"] in ("recorded_provenance", "UNKNOWN", "override")
        assert "reports_without_provenance" in d
        assert "age_conclusions_available" in d

    def test_the_live_archive_yields_recorded_provenance(self, A):
        d = A.audit(quiet=True)
        assert d["age_source"] == "recorded_provenance", d["age_source"]
        assert d["age_conclusions_available"] is True
        assert d["reports_without_provenance"] == [], (
            f"{len(d['reports_without_provenance'])} admitted report(s) have no "
            "recorded date; their age is UNKNOWN and must not be inferred")

    def test_an_override_is_still_honoured_and_declared(self, A):
        pinned = _ts(2026, 6, 1)
        d = A.audit(quiet=True, newest_override=pinned)
        assert d["baseline_mtime"] == pinned
        assert d["age_source"] == "override"

    def test_the_source_code_no_longer_reads_mtime_for_the_baseline(self):
        """The one grep this file makes, and it is a NEGATIVE: the old call is gone."""
        src = (REPO / "scripts" / "latent_control_audit.py").read_text()
        assert "newest = max(newest, int(fp.stat().st_mtime))" not in src, (
            "the mtime baseline is back")


class TestTheOldBehaviourIsGenuinelyDifferent:
    """A fix nothing can distinguish from the defect is not a fix."""

    def test_mtime_and_recorded_date_disagree_on_a_touched_file(self, A, tmp_path):
        run = tmp_path / "realrun_20260801T000000Z"; run.mkdir(parents=True)
        fp = run / "r.json"; fp.write_text("{}")
        touched = _ts(2026, 9, 28)
        os.utime(fp, (touched, touched))
        recorded = A._provenance_time(fp)
        assert int(fp.stat().st_mtime) == touched
        assert recorded == _ts(2026, 8, 1)
        assert abs(int(fp.stat().st_mtime) - recorded) > 30 * 86400, (
            "the two sources agree here, so this case cannot demonstrate the fix")
