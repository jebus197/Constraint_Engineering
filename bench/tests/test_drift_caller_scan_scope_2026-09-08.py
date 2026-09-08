"""The drift-caller scan must ignore archived run output and nothing else.

Written 2026-09-08 18:30 BST after the full suite went red on
`test_update_drift_has_no_production_caller`. The cause was NOT a new production
caller. It was 22 snapshots of a file a panel seat had rewritten, committed into
`bench/logs/target_mutation_watch_2026-09-08/snapshots/` as evidence, one of
which calls `is_drifting`. The scanner globbed `bench/**/*.py` and read archived
model-written code as production source.

`bench/logs/` was ALREADY excluded by the two sibling scanners
(`test_panel_sandbox_2026-09-07.py`, `test_python_floor_2026-09-07.py`); this
one alone lacked it. Measured at the time: 29 of the 492 files matching
`bench/**/*.py` sit under `bench/logs/`, and 7 of those 29 predate the commit
that exposed it -- 2 of them inside a directory named
`QUARANTINE_T01_model_written`, quarantined *because* a model wrote it. So the
scanner had been reading quarantined model output as production all along and
simply had not yet found anything there to trip on.

The danger in the fix is the opposite one: an exclusion broad enough to hide a
real caller would silently retire the guard. Every test below therefore CALLS
`find_drift_callers` against a temporary tree and checks both directions.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
_spec = importlib.util.spec_from_file_location(
    "_imm_eval", Path(__file__).resolve().parent / "test_immune_memory_evaluation.py")
_imm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_imm)

find_drift_callers = _imm.find_drift_callers
REPO = Path(__file__).resolve().parents[2]

CALLER_SRC = (
    "class C:\n"
    "    def go(self, mem, k):\n"
    "        mem.update_drift(k, 0.5)\n"
    "        return mem.is_drifting(k)\n"
)


def _tree(root: Path, rel: str, src: str = CALLER_SRC) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src)


# --- The guard must still fire on a REAL caller. ------------------------------

def test_a_production_caller_is_still_found(tmp_path):
    _tree(tmp_path, "bench/dm/live_module.py")
    found = find_drift_callers(str(tmp_path))
    assert len(found) == 2, f"both call sites must be reported, got {found}"
    assert all(f.startswith("bench/dm/live_module.py:") for f in found)


def test_a_caller_nested_deep_in_production_is_still_found(tmp_path):
    _tree(tmp_path, "bench/a/b/c/d/deep.py")
    assert find_drift_callers(str(tmp_path)), "the glob must stay recursive"


# --- The exclusions, each checked on its own. --------------------------------

@pytest.mark.parametrize("rel", [
    "bench/logs/run_2026-09-08/snapshots/seat_output.py",
    "bench/logs/QUARANTINE_T01_model_written/test_written_by_a_model.py",
    "bench/tests/test_something.py",
    "bench/dm/__pycache__/live_module.py",
])
def test_excluded_locations_are_ignored(tmp_path, rel):
    _tree(tmp_path, rel)
    assert find_drift_callers(str(tmp_path)) == [], f"{rel} must not count as production"


# --- The exclusion must not be broader than it says. -------------------------

@pytest.mark.parametrize("rel", [
    "bench/dm/logsmith.py",          # name merely STARTS with "logs"
    "bench/dm/catalogs.py",          # name merely CONTAINS "logs"
    "bench/logsink/writer.py",       # directory name contains "logs" but is not "logs"
    "bench/dm/testicles.py",         # name contains "test" but is not a tests directory
])
def test_names_that_merely_contain_an_excluded_word_are_still_scanned(tmp_path, rel):
    _tree(tmp_path, rel)
    found = find_drift_callers(str(tmp_path))
    assert found, (
        f"{rel} is production code whose NAME resembles an excluded directory; "
        f"excluding it would silently retire the guard")


def test_a_logs_directory_outside_bench_is_irrelevant(tmp_path):
    """The scan is rooted at <root>/bench, so a top-level logs/ is out of scope
    either way. Pinned so a future 'fix' does not widen the root."""
    _tree(tmp_path, "logs/whatever.py")
    assert find_drift_callers(str(tmp_path)) == []


# --- The live claim itself. --------------------------------------------------

def test_this_repository_currently_has_no_production_caller():
    assert find_drift_callers(str(REPO)) == []


def test_the_archived_seat_snapshot_is_present_but_not_counted():
    """The evidence must stay on disk. It is the fact that a seat wrote this
    that matters; it simply is not production source."""
    snap = REPO / "bench/logs/target_mutation_watch_2026-09-08/snapshots/SEAT_064003_03845310.py"
    if not snap.exists():
        pytest.skip("archive not present in this checkout")
    assert "is_drifting" in snap.read_text(), "the snapshot really does call it"
    assert not any("SEAT_064003" in c for c in find_drift_callers(str(REPO)))
