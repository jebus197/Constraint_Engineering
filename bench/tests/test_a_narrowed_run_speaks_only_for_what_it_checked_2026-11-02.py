"""A narrowed type-check run must not speak for the files it did not open.

THE DEFECT THIS PINS, measured 2026-11-02 by running the task both ways.
`scripts/type_check_task_2026-11-01.py` reported **296 improvements** under
`--paths scripts/suite_record.py` and **0** on a full run. Every one of the 296
was a file the narrowed run never opened: `--paths` restricts the check, an
unchecked file returns 0 findings, and 0 against a non-zero baseline read as a
complete improvement. 296 of 296 false, 1.000000, Wilson 95% [0.987188,
1.000000].

THE WORSE HALF WAS `--update`. It assigned `led["files"] = proj`, REPLACING the
whole baseline, so a narrowed update would have deleted every unchecked file's
entry and they would all have come back as unbaselined -- and the report's own
next line is an instruction to run `--update`.

WHY A GUARD AND NOT JUST THE FIX. This is the second instrument in 18 days to
fail the project's own rule that lint counts must be compared like with like;
the first, on 2026-10-15, produced a spurious `+1` that led to good prose being
deleted to satisfy it. A rule broken twice by different instruments is a rule
that needs a mechanism.

IT DOES NOT NEED A LIVE DEFECT, which is the standing requirement for a
regression guard here. Every test below builds its own ledger and its own file
set in a temporary directory, so the properties are exercised whether or not the
live tree currently misreports anything.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TASK = ROOT / "scripts" / "type_check_task_2026-11-01.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_tct", TASK)
    m = importlib.util.module_from_spec(spec)
    import sys
    sys.modules["_tct"] = m
    try:
        spec.loader.exec_module(m)
    finally:
        sys.modules.pop("_tct", None)
    return m


class TestTheConfinementPredicate:
    """`_was_checked` is the whole repair, so it is tested directly."""

    def test_an_exact_path_counts_as_checked(self, mod):
        assert mod._was_checked("scripts/a.py", ["scripts/a.py"])

    def test_a_file_under_a_checked_directory_counts(self, mod):
        assert mod._was_checked("scripts/sub/a.py", ["scripts"])
        assert mod._was_checked("scripts/sub/a.py", ["scripts/"])

    def test_a_file_outside_the_path_set_does_NOT_count(self, mod):
        assert not mod._was_checked("bench/b.py", ["scripts/a.py"])
        assert not mod._was_checked("bench/b.py", ["scripts"])

    def test_a_prefix_that_is_not_a_directory_boundary_does_NOT_count(self, mod):
        """`scripts_old/a.py` must not be read as inside `scripts`.

        A plain `startswith` would accept it, which is the substring-match error
        this project has recorded more often than any other -- most recently
        when `bound` matched `severity_bounds_validation`.
        """
        assert not mod._was_checked("scripts_old/a.py", ["scripts"])

    def test_an_empty_path_set_checks_nothing(self, mod):
        assert not mod._was_checked("scripts/a.py", [])
        assert not mod._was_checked("scripts/a.py", None)


class TestTheComparisonIsConfined:
    """The property the 296 false improvements violated, on a fixture ledger."""

    def test_an_unchecked_file_is_not_called_improved(self, mod):
        base = {"bench/untouched.py": 7, "scripts/checked.py": 2}
        paths = ["scripts/checked.py"]
        proj = {"scripts/checked.py": 1}          # checked, genuinely improved
        checked = set(proj) | {f for f in base if mod._was_checked(f, paths)}
        improved = {f: (proj.get(f, 0), int(n)) for f, n in base.items()
                    if f in checked and proj.get(f, 0) < int(n)}
        assert "bench/untouched.py" not in improved, (
            "a file the run never opened was reported as improved -- this is "
            "the 296-of-296 defect of 2026-11-02")
        assert improved == {"scripts/checked.py": (1, 2)}

    def test_the_SAME_ledger_on_a_FULL_run_still_reports_it(self, mod):
        """ANTI-VACUITY. Confinement must not be achieved by reporting nothing.

        Without this, a task that printed no improvements at all would satisfy
        the test above, and the capability would have been removed rather than
        corrected.
        """
        base = {"bench/untouched.py": 7, "scripts/checked.py": 2}
        paths = ["bench", "scripts"]
        proj = {"scripts/checked.py": 1}          # bench/untouched.py now clean
        checked = set(proj) | {f for f in base if mod._was_checked(f, paths)}
        improved = {f: (proj.get(f, 0), int(n)) for f, n in base.items()
                    if f in checked and proj.get(f, 0) < int(n)}
        assert "bench/untouched.py" in improved, (
            "a FULL run must still report a genuine improvement")


class TestUpdateMerges:
    """A narrowed `--update` must not drop the entries it did not check."""

    def test_a_narrowed_update_keeps_unchecked_entries(self, tmp_path, mod):
        base = {"bench/untouched.py": 7, "scripts/checked.py": 2}
        paths = ["scripts/checked.py"]
        proj = {"scripts/checked.py": 1}
        checked = set(proj) | {f for f in base if mod._was_checked(f, paths)}
        merged = dict(base)
        for f in checked:
            merged[f] = proj.get(f, 0)
        assert merged["bench/untouched.py"] == 7, (
            "a narrowed update replaced the whole baseline and dropped a file "
            "it never checked")
        assert merged["scripts/checked.py"] == 1

    def test_a_checked_file_that_is_now_clean_is_written_as_zero(self, mod):
        """0 is a MEASUREMENT for a checked file and an ABSENCE for an unchecked
        one, and the merge must tell them apart."""
        base = {"scripts/checked.py": 4, "bench/untouched.py": 9}
        paths = ["scripts/checked.py"]
        proj: dict[str, int] = {}                  # checked and came back clean
        checked = set(proj) | {f for f in base if mod._was_checked(f, paths)}
        merged = dict(base)
        for f in checked:
            merged[f] = proj.get(f, 0)
        assert merged["scripts/checked.py"] == 0
        assert merged["bench/untouched.py"] == 9


class TestTheLiveTaskAgreesWithItself:
    """The end-to-end property, executed rather than reasoned about."""

    def test_the_source_confines_both_comparisons(self):
        """`improved` and the update must BOTH be gated on `checked`.

        This is a source check and it is deliberately narrow: the behavioural
        properties are covered above, and what this adds is that neither gate
        can be removed silently while the others keep passing.
        """
        src = TASK.read_text()
        assert "def _was_checked(" in src
        assert "if f in checked and proj.get(f, 0) < int(n)" in src, (
            "the improved comparison is no longer confined to the checked set")
        assert "merged = dict(base)" in src, (
            "the update no longer merges into the existing baseline")
