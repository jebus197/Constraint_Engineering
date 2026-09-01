"""The mid-run target mutation guard, exercised for the first time.

The guard hashes the experiment's target once per round and warns loudly if it
changes, because panel models are dispatched with Write and Edit in their
allowed tools and one mutated Exp 47's target mid-run on 2026-07-29, restored
it, and left no trace in git or the round files.

It has never fired. Zero of 83 archived run directories carry the
`target_integrity_events` field the guard writes. It sat inline in the round
loop of a 12,000-line function where nothing could reach it, and in that state
it accumulated a defect: the previous hash was a bare module global with no
per-run reset and no key, so a second experiment in the same process compared
its first round against the first experiment's last hash and reported a round-0
mutation with nothing mutated. The guard's first firing would have been a false
alarm -- in a project that has already absorbed 92 of those from the macrophage.

Extracted to `target_hash_event` on 2026-09-01 (runway 0C.9) so it can be run.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import reference_runner_v3 as R  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_guard_state():
    R._TARGET_HASH_PREV.clear()
    yield
    R._TARGET_HASH_PREV.clear()


@pytest.fixture
def target(tmp_path):
    p = tmp_path / "module_under_review.py"
    p.write_text("def f():\n    return 1\n")
    return p


class TestItDetectsARealMutation:
    def test_an_unchanged_target_raises_nothing(self, target):
        for _ in range(4):
            digest, previous = R.target_hash_event(target)
            assert previous is None
            assert len(digest) == 64

    def test_a_mid_run_edit_is_caught(self, target):
        first, _ = R.target_hash_event(target)
        target.write_text("def f():\n    return 2\n")   # the model writes
        second, previous = R.target_hash_event(target)
        assert previous == first, "the guard must report the prior hash"
        assert second != first

    def test_a_mutate_then_restore_is_caught_on_the_mutation(self, target):
        """The Exp 47 shape: written, then put back, invisible to git."""
        original = target.read_text()
        R.target_hash_event(target)
        target.write_text("def f():\n    return 99\n")
        _, previous = R.target_hash_event(target)
        assert previous is not None
        target.write_text(original)
        _, previous_after = R.target_hash_event(target)
        assert previous_after is not None, (
            "restoring is itself a change and must also be reported")


class TestItDoesNotFalselyAccuse:
    def test_two_targets_in_one_process_do_not_cross_contaminate(self, tmp_path):
        """The defect. Run 1 on target A, run 2 on target B, same process."""
        a = tmp_path / "a.py"; a.write_text("A" * 100)
        b = tmp_path / "b.py"; b.write_text("B" * 100)
        for _ in range(2):
            assert R.target_hash_event(a)[1] is None
        digest, previous = R.target_hash_event(b)     # run 2, round 0
        assert previous is None, (
            "a different target must not be compared against another's hash")

    def test_a_legitimate_edit_between_runs_is_not_a_mid_run_event(self, target):
        """What the per-run clear() buys: the runner calls it at run start."""
        R.target_hash_event(target)
        R._TARGET_HASH_PREV.clear()                    # runner does this per run
        target.write_text("# edited between runs, by a human\n")
        assert R.target_hash_event(target)[1] is None


class TestTheRunnerStillWiresItIn:
    """An extracted helper nothing calls is worse than an inline block."""

    def test_the_round_loop_calls_the_helper(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "_tgt_h, _prev_h = target_hash_event(_tgt_p)" in src
        assert "TARGET INTEGRITY WARNING" in src

    def test_the_runner_clears_state_at_run_start(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "_TARGET_HASH_PREV.clear()" in src, (
            "without the per-run clear, a between-run edit reads as mid-run")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
