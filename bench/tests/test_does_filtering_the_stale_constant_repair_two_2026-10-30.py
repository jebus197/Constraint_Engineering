#!/usr/bin/env python3
"""B50's mechanical repair fixes 1 assertion and breaks another, not 2 and 0.

WHAT WENT WRONG IN ENTRY B50. It partitions its 6 permanently failing assertions
as *"2 of them are a stale CONSTANT and are mechanically fixable"* against
*"the other 4 are EMPIRICAL CLAIMS about data the reset destroyed, and no filter
repairs them"*, and names the repair: filter `_RECORDING_RUNS` to runs that wrote
after the newest reset. Every run in that constant is pre-reset, so the filter
yields the empty list.

MEASURED 2026-10-30, the split is 1 and 5, and the repair has a price: it breaks
`test_the_evidence_base_is_thin_and_here_is_how_thin`, which passes today. That
test asserts some flaw class rests on a single observation; with no pre-reset
runs in the derivable set there is no such class, and it then reports *"the
memory has grown past the state this evaluation describes"*, which is false --
the memory did not grow, the constant was emptied. A repair whose diagnosis
misleads is worse than the failure it replaces.

A COUNT CANNOT SEE ANY OF THIS. Both sides are 6 failed, 28 passed -- the same
integers -- so a count-based comparison reports no change. Only the SET
comparison shows the trade. That is `feedback_pin_a_set_not_a_count` in its
purest form.

WHAT THIS FILE PINS. Not the totals, because his ruling on B50 will legitimately
change which assertions exist. It pins: that the producer's runtime patch leaves
the test file on disk UNMODIFIED, which is what makes it safe to run beside a
board; that the patch demonstrably TAKES EFFECT, because a silently failed plugin
would make the two runs identical and the whole measurement vacuous; that the
repaired, broken and unchanged sets are a genuine partition; and the finding
itself as a SET of node ids, with the message saying plainly that his ruling may
move it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PRODUCER = (REPO / "scripts"
            / "does_filtering_the_stale_constant_repair_two_2026-10-30.py")
SUBJECT = REPO / "bench" / "tests" / "test_immune_memory_evaluation.py"

#: THE FINDING, PINNED AS A SET. A count would read 6 on both sides.
REPAIRED_BY_THE_FILTER = {
    "TestWhatTheMemoryHolds::test_disk_memory_reproduces_from_its_recorded_run_reports",
}
BROKEN_BY_THE_FILTER = {
    "TestWhatTheMemoryHolds::test_the_evidence_base_is_thin_and_here_is_how_thin",
}


def _producer():
    assert PRODUCER.is_file(), f"producer absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("b50_filter_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _producer()


class TestTheRuntimePatchIsSafeAndReal:
    """The 2 properties the whole measurement rests on."""

    def test_the_patch_takes_effect(self, mod):
        """POSITIVE CONTROL. A plugin that silently did nothing would make the
        two runs identical and every conclusion below vacuous.

        Driven directly: import the subject, apply the plugin's own hook, and
        check the constant actually emptied.
        """
        with tempfile.TemporaryDirectory() as td:
            plug = pathlib.Path(td) / "_b50_filter_plugin.py"
            plug.write_text(mod._PLUGIN)
            sys.path.insert(0, td)
            try:
                import _b50_filter_plugin as P
                spec = importlib.util.spec_from_file_location(
                    "test_immune_memory_evaluation", SUBJECT)
                subject = importlib.util.module_from_spec(spec)
                sys.modules["test_immune_memory_evaluation"] = subject
                spec.loader.exec_module(subject)
                before = list(subject._RECORDING_RUNS)
                assert before, (
                    "`_RECORDING_RUNS` is already empty, so the filter this "
                    "measurement applies is a no-op and the comparison says "
                    "nothing")
                P.pytest_collection_finish(None)
                assert subject._RECORDING_RUNS == [], (
                    f"the plugin ran and left `_RECORDING_RUNS` as "
                    f"{subject._RECORDING_RUNS!r}; the 'after' run would be a "
                    f"plain rerun of 'before' and the measurement vacuous")
            finally:
                sys.modules.pop("test_immune_memory_evaluation", None)
                sys.modules.pop("_b50_filter_plugin", None)
                sys.path.remove(td)

    def test_the_producer_never_edits_the_subject_on_disk(self, mod):
        """It must be safe to run beside a board, and safe if interrupted."""
        before = SUBJECT.read_bytes()
        mod.measure()
        assert SUBJECT.read_bytes() == before, (
            "the producer modified the test file on disk. An earlier manual "
            "version of this experiment did exactly that, which is unsafe "
            "while a pre-commit board is running and leaves the tree dirty if "
            "the run is interrupted.")

    def test_the_subject_is_tracked_and_clean_after_a_measurement(self, mod):
        r = subprocess.run(["git", "status", "--porcelain", "--", str(SUBJECT)],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.stdout.strip() == "", (
            f"git reports the subject as modified: {r.stdout.strip()!r}")


class TestTheFindingItself:
    @pytest.fixture(scope="class")
    def m(self, mod):
        return mod.measure()

    def test_the_sets_are_a_genuine_partition(self, m):
        before, after = set(m["before"]), set(m["after"])
        assert set(m["repaired"]) == before - after
        assert set(m["broken"]) == after - before
        assert set(m["unchanged"]) == before & after
        assert not (set(m["repaired"]) & set(m["broken"]))

    def test_the_filter_repairs_the_recorded_one(self, m):
        assert set(m["repaired"]) == REPAIRED_BY_THE_FILTER, (
            f"the filter now repairs {sorted(m['repaired'])}, not "
            f"{sorted(REPAIRED_BY_THE_FILTER)}. If he has ruled on B50 this is "
            f"expected -- re-derive the pin from the new state rather than "
            f"restoring this one.")

    def test_the_filter_still_breaks_a_passing_assertion(self, m):
        assert set(m["broken"]) == BROKEN_BY_THE_FILTER, (
            f"the filter now breaks {sorted(m['broken'])}, not "
            f"{sorted(BROKEN_BY_THE_FILTER)}. B50 offered this filter as a free "
            f"mechanical repair; the whole correction is that it is not free, so "
            f"a change here changes what he is being asked to rule on.")

    def test_the_count_alone_would_have_said_nothing(self, m):
        """THE REASON THE SET IS PINNED AND THE COUNT IS NOT."""
        assert len(m["before"]) == len(m["after"]), (
            "the totals now differ, so a count WOULD have detected this. That "
            "is a better situation, not a worse one -- but the set comparison "
            "stays, because it says WHICH assertion moved and a count cannot.")
        assert m["repaired"] and m["broken"], (
            "equal totals with nothing repaired and nothing broken would mean "
            "the filter changed nothing at all")
