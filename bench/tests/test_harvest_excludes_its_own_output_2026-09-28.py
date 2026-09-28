"""The harvest must not record the dispatcher's own log output as seat work.

FOUNDER, 2026-09-28: *"You can test the harvest mechanism in the above panel
review and make sure it works properly."* It did not work properly, and the round
he asked about is the evidence.

WHAT WAS MEASURED. On `founder_verdicts_2026-09-28` both seats failed at
authentication with 0 tool calls and wrote NOTHING. The run still printed "seats
proposed edits to 8 file(s)" and "harvested 3394 byte(s) of seat-written files".
All 9 captured paths were dispatcher or harvest artefacts; the only difference in
the diff was `elapsed_s` varying by 0.9 between the canonical log and the
sandbox's copy of it; and `sandbox_harvest/cc2/attempt-1/changes.diff` appeared
INSIDE the harvested files, the harvest harvesting itself.

WHY IT IS A PROVENANCE DEFECT AND NOT UNTIDINESS. A reader of that log concludes
2 seats did work on a round where neither ran. This project's own record already
holds the same shape once: on 2026-09-20 the harvest copied 112 MB of `.git`
objects out as seat-written work, which is why `_is_vcs_metadata` exists. This is
that defect recurring through a different directory.

EVERY CASE BELOW IS EXECUTED against the real `harvest()` with a real sandbox on
disk. The point of the class is the pair: the dispatcher's own writes must be
dropped AND a genuine seat file must still be taken. A harvest that takes nothing
is not a fix.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SANDBOX_MOD = ROOT / "bench" / "panel_sandbox.py"


@pytest.fixture
def ps():
    sys.path.insert(0, str(ROOT / "bench"))
    spec = importlib.util.spec_from_file_location("panel_sandbox_ut", SANDBOX_MOD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["panel_sandbox_ut"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def repo_and_copy(tmp_path):
    """A tiny real git repo and a modified copy of it, both on disk."""
    repo = tmp_path / "repo"
    (repo / "bench" / "logs" / "myround").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "existing.py").write_text("print(1)\n", encoding="utf-8")
    (repo / "bench" / "logs" / "myround" / "cc2.json").write_text(
        '{"elapsed_s": 18.7}\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo, check=True)

    copy = tmp_path / "copy"
    copy.mkdir()
    for rel in ("scripts/existing.py", "bench/logs/myround/cc2.json"):
        (copy / rel).parent.mkdir(parents=True, exist_ok=True)
        (copy / rel).write_text((repo / rel).read_text(), encoding="utf-8")

    # The DISPATCHER's own drift inside the copy: the same field, a different value.
    (copy / "bench" / "logs" / "myround" / "cc2.json").write_text(
        '{"elapsed_s": 17.8}\n', encoding="utf-8")
    # The HARVEST's own output, inside the copy.
    own = copy / "bench" / "logs" / "myround" / "sandbox_harvest" / "cc2" / "attempt-1"
    own.mkdir(parents=True)
    (own / "changes.diff").write_text("### noise\n", encoding="utf-8")
    # A GENUINE seat deliverable, which must survive.
    (copy / "scripts" / "seat_wrote_this.py").write_text(
        "# a real falsifier\nassert True\n", encoding="utf-8")
    return repo, copy


def _dest(repo: Path) -> Path:
    """Where the dispatcher puts a harvest: <repo>/bench/logs/<run>/sandbox_harvest/<seat>/attempt-N."""
    return repo / "bench" / "logs" / "myround" / "sandbox_harvest" / "cc2" / "attempt-1"


class TestTheDispatchersOwnOutputIsDropped:
    def test_the_runs_own_log_file_is_not_harvested(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        m = ps.harvest(copy, repo, _dest(repo))
        assert "bench/logs/myround/cc2.json" not in m["files_taken"]

    def test_the_harvests_own_output_is_not_harvested(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        m = ps.harvest(copy, repo, _dest(repo))
        assert not any("sandbox_harvest" in r for r in m["files_taken"]), m["files_taken"]

    def test_the_manifest_says_how_many_it_dropped(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        m = ps.harvest(copy, repo, _dest(repo))
        assert m["skipped_own_log_output"] >= 1
        assert m["changed_including_excluded"] > m["changed"]

    def test_the_diff_does_not_carry_them_either(self, ps, repo_and_copy):
        """The 8-file claim came from changes.diff, so excluding only the COPY
        would have left the false count in place."""
        repo, copy = repo_and_copy
        ps.harvest(copy, repo, _dest(repo))
        d = _dest(repo) / "changes.diff"
        if d.is_file():
            text = d.read_text(encoding="utf-8")
            assert "bench/logs/myround/cc2.json" not in text
            assert "sandbox_harvest" not in text


class TestGenuineSeatWorkStillSurvives:
    """ANTI-VACUITY. A harvest that takes nothing would pass the class above."""

    def test_a_seat_written_script_is_taken(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        m = ps.harvest(copy, repo, _dest(repo))
        assert "scripts/seat_wrote_this.py" in m["files_taken"], m["files_taken"]
        landed = _dest(repo) / "files" / "scripts" / "seat_wrote_this.py"
        assert landed.is_file()
        assert "a real falsifier" in landed.read_text(encoding="utf-8")

    def test_bytes_taken_counts_only_the_real_file(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        m = ps.harvest(copy, repo, _dest(repo))
        real = (copy / "scripts" / "seat_wrote_this.py").stat().st_size
        assert m["bytes"] == real, (
            f"harvested {m['bytes']} bytes but the only seat file is {real}"
        )

    def test_the_seat_diff_is_still_written(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        ps.harvest(copy, repo, _dest(repo))
        d = _dest(repo) / "changes.diff"
        assert d.is_file(), "a real seat change must still produce a diff"
        assert "seat_wrote_this.py" in d.read_text(encoding="utf-8")


class TestTheExclusionIsScopedToThisRun:
    """Excluding `bench/logs/` wholesale would discard a measurement a seat was
    ASKED to write there. Only the current run's directory is excluded."""

    def test_another_runs_log_directory_is_still_harvested(self, ps, repo_and_copy):
        repo, copy = repo_and_copy
        other = copy / "bench" / "logs" / "a_different_round"
        other.mkdir(parents=True)
        (other / "seat_measurement.json").write_text('{"n": 1}\n', encoding="utf-8")
        m = ps.harvest(copy, repo, _dest(repo))
        assert "bench/logs/a_different_round/seat_measurement.json" in m["files_taken"]

    def test_the_predicate_is_false_without_a_run_directory(self, ps):
        assert ps._is_dispatcher_own_output("bench/logs/x/y.json", None) is False

    def test_the_predicate_does_not_match_a_sibling_by_prefix(self, ps):
        """`myround2` must not be swallowed by `myround`."""
        assert ps._is_dispatcher_own_output(
            "bench/logs/myround2/cc2.json", "bench/logs/myround") is False
        assert ps._is_dispatcher_own_output(
            "bench/logs/myround/cc2.json", "bench/logs/myround") is True


class TestAllThreeHarvestShapesResolveTheSameRunDirectory:
    """THE BUG THESE TESTS MISSED, added the moment it was found.

    The first fix derived the run directory as `dest.parents[2]`, which is correct
    only for the dispatcher's deepest shape. The other 2 callers are shallower, so
    the same expression resolved to `bench/logs` for one and `bench` for the other
    -- excluding the ENTIRE bench tree from every simulated run's harvest, and
    silently, because a harvest that takes less prints a smaller number rather
    than an error. It was found by tracing the 3 call sites, not by these tests,
    which is the reason this class exists.

    The 3 real destinations, each with its calling module:
      <run>/sandbox_harvest/<seat>/attempt-N   bench/confer_maths_panel_2026-09-05.py
      <run>/worktree_harvest/<tag>             bench/confer_convergence_panel_2026-08-23.py
                                               bench/build_experiment_run.py
      <run>/panel_worktree_harvest             bench/tools/run_simulated_experiment.py
    """

    @pytest.mark.parametrize("tail", [
        ("sandbox_harvest", "cc2", "attempt-1"),
        ("worktree_harvest", "some_tag"),
        ("panel_worktree_harvest",),
    ])
    def test_every_shape_resolves_to_the_run_directory(self, ps, tmp_path, tail):
        repo = tmp_path / "repo"
        run = repo / "bench" / "logs" / "myround"
        dest = run.joinpath(*tail)
        dest.mkdir(parents=True)
        assert ps._run_log_dir(dest, repo) == "bench/logs/myround", (
            f"shape {'/'.join(tail)} resolved wrongly"
        )

    def test_no_shape_ever_resolves_to_the_whole_bench_tree(self, ps, tmp_path):
        """The specific catastrophe: excluding `bench` or `bench/logs` wholesale."""
        repo = tmp_path / "repo"
        for tail in (("sandbox_harvest", "cc2", "attempt-1"),
                     ("worktree_harvest", "t"), ("panel_worktree_harvest",)):
            dest = repo.joinpath("bench", "logs", "myround", *tail)
            dest.mkdir(parents=True, exist_ok=True)
            got = ps._run_log_dir(dest, repo)
            assert got not in ("bench", "bench/logs"), (
                f"{'/'.join(tail)} would exclude {got!r} from every harvest"
            )

    def test_a_destination_outside_any_logs_directory_excludes_nothing(self, ps, tmp_path):
        """None means the old behaviour. Over-harvesting is untidy; under-harvesting
        loses seat work, so None is the safe direction for an unknown shape."""
        repo = tmp_path / "repo"
        dest = repo / "somewhere" / "else"
        dest.mkdir(parents=True)
        assert ps._run_log_dir(dest, repo) is None

    def test_the_shallowest_shape_still_drops_the_runs_own_log(self, ps, tmp_path):
        """EXECUTED end to end on the shape the broken version got wrong, because
        resolving the path correctly and HARVESTING correctly are 2 claims."""
        repo = tmp_path / "repo"
        (repo / "bench" / "logs" / "r1").mkdir(parents=True)
        (repo / "bench" / "cell.py").write_text("x = 1\n", encoding="utf-8")
        (repo / "bench" / "logs" / "r1" / "run.log").write_text("a\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "i"], cwd=repo, check=True)

        copy = tmp_path / "copy"
        (copy / "bench" / "logs" / "r1").mkdir(parents=True)
        (copy / "bench" / "cell.py").write_text("x = 1\n", encoding="utf-8")
        (copy / "bench" / "logs" / "r1" / "run.log").write_text("a\nb\n", encoding="utf-8")
        # A seat file inside bench/, which the broken version would have dropped.
        (copy / "bench" / "seat_added.py").write_text("# real\n", encoding="utf-8")

        m = ps.harvest(copy, repo, repo / "bench" / "logs" / "r1" / "panel_worktree_harvest")
        assert "bench/logs/r1/run.log" not in m["files_taken"]
        assert "bench/seat_added.py" in m["files_taken"], (
            "a seat file under bench/ was dropped -- the exclusion is too wide"
        )
