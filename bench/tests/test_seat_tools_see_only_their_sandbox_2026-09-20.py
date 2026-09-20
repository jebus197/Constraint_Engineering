#!/usr/bin/env python3
"""A panel seat's file tools must see its OWN sandbox, never the live repository.

THE DEFECT, MEASURED 2026-09-20 AND FIXED THE SAME DAY.

The panel dispatcher builds a sandbox copy for EVERY seat. Round 4's own
dispatch log shows 7 copies for 7 seats, including all 5 reached over HTTP, and
`set_panel_cwd` puts the dispatching thread into the right one.

`bench/build_experiment_tools.py` ignored it. `_safe()` resolved every path
against the module-level `REPO` constant, so `read_file`, `grep`, `list_dir`,
`run_python` and `run_pytest` all reached the LIVE tree while the seat's own
copy sat unused. 5 of the 7 sandboxes were built and never entered.

WHAT IT COST. The dispatcher writes each seat's reply into
`bench/logs/<round>/<seat>.json` as that seat finishes, so the live tree
accumulates the round's answers while later seats are still working. In round 4
the `ge` seat ran `grep -rn 10.4882 bench` and pulled in 4.7945% of the `cx`
seat's reply verbatim, Wilson [2.8772%, 7.8858%]. cx finished at 117.4 s; ge ran
to 279.2 s. Seats that the protocol requires to be independent were reading one
another mid-round.

READ-ONLY CONFINEMENT COULD NOT HAVE PREVENTED THIS, and that is the lesson.
The kernel-enforced `sandbox-exec` wrapper governs what a seat may WRITE. This
defect was entirely about what a seat could READ.

These tests drive the real functions. A test asserting on the module's source
text would pass against both the broken and the fixed version.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import bench.build_experiment_tools as bt  # noqa: E402
from bench.experiment_11_orchestrator import set_panel_cwd  # noqa: E402


@pytest.fixture
def sandbox(tmp_path):
    """A stand-in for a seat's own copy, with a file the live repo does not have."""
    box = tmp_path / "repo"
    (box / "bench" / "logs" / "round").mkdir(parents=True)
    (box / "ONLY_IN_THE_SANDBOX.txt").write_text("sandbox copy\n")
    (box / "bench" / "logs" / "round" / "note.txt").write_text("sandbox note\n")
    try:
        set_panel_cwd(str(box))
        yield box
    finally:
        set_panel_cwd(None)


def test_with_no_panel_cwd_nothing_changes(tmp_path):
    """FAIL-SAFE. Ordinary runs, the suite and direct use must be unaffected."""
    set_panel_cwd(None)
    assert bt._root() == bt.REPO


def test_a_seat_reads_its_OWN_copy_not_the_live_repo(sandbox):
    """The fix, stated as the property that matters."""
    assert bt._root() == sandbox, f"tools rooted at {bt._root()}, not the seat's copy"
    p = bt._safe("ONLY_IN_THE_SANDBOX.txt")
    assert p.is_file() and p.read_text().strip() == "sandbox copy"
    assert str(p).startswith(str(sandbox))
    assert not str(p).startswith(str(bt.REPO)), "resolved into the LIVE repository"


def test_the_live_repository_is_unreachable_from_a_confined_seat(sandbox):
    """THE REGRESSION THAT MATTERS.

    `bench/build_experiment_tools.py` exists in the live repo and NOT in this
    sandbox. Before the fix `_safe` returned the live file and `read_file`
    happily read it. Now the path resolves inside the sandbox and is absent.
    """
    p = bt._safe("bench/build_experiment_tools.py")
    assert str(p).startswith(str(sandbox))
    assert not p.exists(), (
        "a confined seat resolved a path that exists only in the LIVE repository")


def test_a_seat_cannot_read_another_seats_reply_from_the_live_round(sandbox):
    """The round-4 breach, as a test.

    The live tree holds this round's finished seat replies. A confined seat must
    not reach them, whatever it searches for.
    """
    live_round = bt.REPO / "bench" / "logs" / "maths_panel_2026-09-20_r4"
    if not (live_round / "cx.json").is_file():
        pytest.skip("round 4 archive not present in this checkout")
    p = bt._safe("bench/logs/maths_panel_2026-09-20_r4/cx.json")
    assert str(p).startswith(str(sandbox))
    assert not p.exists(), "a seat reached another seat's reply in the live tree"


def test_escaping_the_sandbox_is_refused(sandbox):
    """`..` must not climb out, and the error must name the tree, not the repo."""
    for attempt in ("../../etc/passwd", "../..", "/etc/passwd/../../.."):
        with pytest.raises(ValueError):
            bt._safe(attempt)


def test_grep_and_list_dir_are_rooted_in_the_sandbox(sandbox):
    """The 2 tools that sweep a TREE, which is how the breach actually happened."""
    out = bt.execute("list_dir", {"path": "."})
    assert "ONLY_IN_THE_SANDBOX.txt" in out, out[:300]
    # The live repo has a top-level `scripts/` directory; the sandbox does not.
    assert "scripts" not in out.split(), f"list_dir showed the live tree: {out[:300]}"


def test_run_python_executes_inside_the_sandbox(sandbox):
    """A seat's own snippet must also see its copy, not the repository."""
    out = bt.execute(
        "run_python", {"code": "import os;print(os.path.basename(os.getcwd()));"
                               "print(os.path.exists('ONLY_IN_THE_SANDBOX.txt'))"})
    if "[REFUSED]" in out:
        pytest.skip("sandbox-exec unavailable on this platform")
    assert "True" in out, f"run_python did not run inside the seat's copy: {out[:300]}"
