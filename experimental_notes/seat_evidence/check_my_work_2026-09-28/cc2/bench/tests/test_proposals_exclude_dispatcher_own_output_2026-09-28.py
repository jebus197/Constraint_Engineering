# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cbc83dd3cd0c8d3dc8fa719d53f34d0baae9e839c21a5a92f85f4e8a26370088
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""`seat_proposals.diff` must not count the dispatcher's own log output.

THE HALF-FIX THIS CLOSES. `panel_sandbox._is_dispatcher_own_output` (2026-09-28)
cites TWO symptoms from the `founder_verdicts_2026-09-28` round, on which BOTH
seats failed at authentication with 0 tool calls and wrote nothing at all:

    "harvested 3394 byte(s) of seat-written files"
    "seats proposed edits to 8 file(s)"

Only the first flows through `harvest()`. The second is built at
`confer_maths_panel_2026-09-05.py` by calling `panel_sandbox.changes()` directly,
with no run-log filter -- so it kept counting the dispatcher's own
`bench/logs/<run>/` writes as seat proposals, and wrote them into
`seat_proposals.diff`, which is precisely the file a reader opens to find out
what the seats proposed. The provenance defect the fix was written to kill
survived in the louder of the two numbers.

NOT TOO WIDE, AND THAT IS THE HALF THAT COULD DO REAL DAMAGE. A seat asked to
write a measurement under `bench/logs/` -- but OUTSIDE this run's directory --
must still be reported. `TestASeatsOwnWriteUnderBenchLogsSurvives` is the case
that would catch an over-wide exclusion, and it is the case the founder's brief
asked for by name.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
import panel_sandbox as ps  # noqa: E402


@pytest.fixture
def repo_and_copy(tmp_path):
    """A canonical tree and a seat's copy of it, as the dispatcher makes them."""
    repo = tmp_path / "repo"
    (repo / "bench" / "logs" / "thisrun").mkdir(parents=True)
    (repo / "bench" / "logs" / "otherrun").mkdir(parents=True)
    (repo / "bench" / "dm").mkdir(parents=True)
    (repo / "bench" / "dm" / "_convergence.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "bench" / "logs" / "thisrun" / "cc2.json").write_text(
        '{"elapsed_s": 11.0}\n', encoding="utf-8")

    copy = tmp_path / "copy"
    copy.mkdir()
    for p in repo.rglob("*"):
        t = copy / p.relative_to(repo)
        t.parent.mkdir(parents=True, exist_ok=True)
        if p.is_file():
            t.write_bytes(p.read_bytes())
    return repo, copy


class TestTheDispatchersOwnWriteIsNotASeatProposal:
    def test_a_run_log_write_is_excluded(self, repo_and_copy):
        """THE 0-WORK ROUND. The seat wrote nothing; only `elapsed_s` drifted."""
        repo, copy = repo_and_copy
        (copy / "bench" / "logs" / "thisrun" / "cc2.json").write_text(
            '{"elapsed_s": 11.9}\n', encoding="utf-8")

        run_log_rel = ps._run_log_dir(repo / "bench" / "logs" / "thisrun", repo)
        assert run_log_rel == "bench/logs/thisrun"

        raw = ps.changes(copy, repo)
        assert "bench/logs/thisrun/cc2.json" in raw, (
            "precondition failed: changes() should see the drifted log; without "
            "it this test proves nothing"
        )
        kept = {r for r in raw if not ps._is_dispatcher_own_output(r, run_log_rel)}
        assert kept == set(), (
            f"a round on which the seat wrote nothing still reports proposals: {kept}"
        )


class TestASeatsOwnWriteUnderBenchLogsSurvives:
    """NOT TOO WIDE. The exclusion CC1's first attempt would have made -- the whole
    of `bench/` -- is the failure this guards. So is excluding `bench/logs/`
    wholesale."""

    def test_a_seat_measurement_in_another_run_directory_is_kept(self, repo_and_copy):
        repo, copy = repo_and_copy
        (copy / "bench" / "logs" / "otherrun").mkdir(parents=True, exist_ok=True)
        (copy / "bench" / "logs" / "otherrun" / "seat_measurement.json").write_text(
            '{"wilson": [0.1, 0.2]}\n', encoding="utf-8")
        run_log_rel = ps._run_log_dir(repo / "bench" / "logs" / "thisrun", repo)
        raw = ps.changes(copy, repo)
        kept = {r for r in raw if not ps._is_dispatcher_own_output(r, run_log_rel)}
        assert "bench/logs/otherrun/seat_measurement.json" in kept, (
            "a seat's measurement written under bench/logs/ but outside this run "
            "was dropped; the exclusion is too wide"
        )

    def test_ordinary_seat_code_under_bench_is_kept(self, repo_and_copy):
        """`parents[2]` would have excluded all of `bench/`. This is that case."""
        repo, copy = repo_and_copy
        (copy / "bench" / "dm" / "_convergence.py").write_text("x = 2\n", encoding="utf-8")
        run_log_rel = ps._run_log_dir(repo / "bench" / "logs" / "thisrun", repo)
        raw = ps.changes(copy, repo)
        kept = {r for r in raw if not ps._is_dispatcher_own_output(r, run_log_rel)}
        assert "bench/dm/_convergence.py" in kept

    def test_a_prefix_collision_is_not_swallowed(self, repo_and_copy):
        """`thisrun2` must not be eaten by the exclusion for `thisrun`."""
        repo, copy = repo_and_copy
        (copy / "bench" / "logs" / "thisrun2").mkdir(parents=True, exist_ok=True)
        (copy / "bench" / "logs" / "thisrun2" / "seat.json").write_text("{}\n",
                                                                       encoding="utf-8")
        run_log_rel = ps._run_log_dir(repo / "bench" / "logs" / "thisrun", repo)
        assert not ps._is_dispatcher_own_output("bench/logs/thisrun2/seat.json",
                                                run_log_rel)


class TestTheFourthDestinationShape:
    """The brief asked for a 4th shape CC1's docstring did not enumerate. It is
    the run directory ITSELF, which is what the proposals call site passes: the
    docstring lists only the three HARVEST tails, all of which sit BELOW the run
    directory. `_run_log_dir` happens to handle it, because it tests `dest`
    before `dest.parents` -- but that was never asserted anywhere, so it was luck
    rather than a property. It is asserted now."""

    @pytest.mark.parametrize("tail", [
        "bench/logs/myround/sandbox_harvest/cc2/attempt-1",
        "bench/logs/myround/worktree_harvest/some_model",
        "bench/logs/myround/panel_worktree_harvest",
        "bench/logs/myround",                      # <- the 4th: the run dir itself
    ])
    def test_every_shape_resolves_to_the_same_run_directory(self, tmp_path, tail):
        repo = tmp_path / "repo"
        (repo / tail).mkdir(parents=True)
        assert ps._run_log_dir(repo / tail, repo) == "bench/logs/myround"


class TestTheCallSiteIsActuallyWired:
    """An unreached guard guards nothing -- the additive standard's own words."""

    def test_the_proposals_block_filters_through_the_shared_rule(self):
        src = (ROOT / "bench" / "confer_maths_panel_2026-09-05.py").read_text(
            encoding="utf-8")
        i = src.index("proposals = {}")
        block = src[i:src.index("seats proposed edits to", i)]
        assert "_is_dispatcher_own_output" in block, (
            "the proposals block still calls changes() unfiltered; the harvest fix "
            "repairs one of the two numbers its own docstring names"
        )
        assert "_run_log_dir" in block
