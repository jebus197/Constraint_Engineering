"""BR2 task files must not carry their own answers.

RUNWAY ITEM 4B.1. Each of the 27 encodings in bench/tasks_frontier/ held its
answer in `ground_truth_notes`, in the same JSON object as the `prompt`. That is
the structure that removed exp48 and exp49 from every headline figure and burned
exp55's target three days before it ran.

Split 2026-08-27 into CDSFL_experiment_keys/br2_keys/, outside any git tree:
14,528 characters of answer text across 27 files.

THE FIELD IS DELIBERATELY RETAINED, holding a pointer rather than an answer.
run_benchmark.py:242 and run_round_robin.py:152 validate that the key is
PRESENT, so deleting it would break both loaders and the 14 test files that
touch them. A pointer keeps validation green and makes any read of the value a
loud, visible failure instead of a silent wrong answer.

WHAT THIS DOES NOT FIX, stated because the split reads like a closure and is
not one. Measured 2026-08-27: all 27 answer-bearing files have been on the
PUBLIC GitHub repository since 2026-03-18 -- 162 days. Splitting them stops the
exposure growing; it does not reverse it. Whether BR2 is still a valid blind
experiment on these tasks is a founder decision and it is open.
"""
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TASKS = REPO / "bench" / "tasks_frontier"
STORE = REPO.parent / "CDSFL_experiment_keys" / "br2_keys"
POINTER_PREFIX = "MOVED OUT OF THE REPOSITORY"


def _tasks():
    return sorted(TASKS.glob("ft-*.json"))


def test_all_27_tasks_are_present():
    assert len(_tasks()) == 27, f"expected 27 frontier tasks, found {len(_tasks())}"


@pytest.mark.parametrize("path", _tasks(), ids=lambda p: p.stem)
def test_no_task_file_carries_its_own_answer(path):
    """KNOWN-BAD is any real answer text sitting beside the prompt."""
    d = json.loads(path.read_text(encoding="utf-8"))
    gt = d.get("ground_truth_notes")
    assert gt is not None, (
        f"{path.name}: the field was DELETED, not pointered. "
        "run_benchmark.py:242 and run_round_robin.py:152 require it to be present."
    )
    assert isinstance(gt, str) and gt.startswith(POINTER_PREFIX), (
        f"{path.name} carries answer text beside its prompt again "
        f"({len(str(gt))} chars). This is the exposure class that cost exp48, "
        "exp49 and exp55's target."
    )


@pytest.mark.parametrize("path", _tasks(), ids=lambda p: p.stem)
def test_the_prompt_is_still_intact(path):
    """The split must not have damaged what the models actually receive."""
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d.get("prompt"), f"{path.name} has no prompt"
    assert len(d["prompt"]) > 200, (
        f"{path.name} prompt is only {len(d['prompt'])} chars — the split may "
        "have truncated it"
    )


@pytest.mark.skipif(not STORE.is_dir(),
                    reason="key store is outside the repo and absent on this machine")
class TestTheKeysSurvivedTheMove:
    def test_every_task_has_a_key_file(self):
        missing = [p.stem for p in _tasks()
                   if not (STORE / f"{p.stem}_KEY.json").is_file()]
        assert not missing, f"answers lost in the split for: {missing}"

    def test_each_key_holds_real_answer_text(self):
        """A split that moved empty strings would pass the test above and have
        destroyed the answers."""
        thin = []
        for p in _tasks():
            k = json.loads((STORE / f"{p.stem}_KEY.json").read_text(encoding="utf-8"))
            gt = k.get("ground_truth_notes", "")
            if not isinstance(gt, str) or len(gt) < 50:
                thin.append((p.stem, len(str(gt))))
        assert not thin, f"key files with implausibly short answers: {thin}"

    def test_each_key_points_back_at_its_source(self):
        for p in _tasks():
            k = json.loads((STORE / f"{p.stem}_KEY.json").read_text(encoding="utf-8"))
            assert k.get("source_task_file", "").endswith(p.name), (
                f"{p.stem}_KEY.json does not name its source task file"
            )


def test_the_key_store_warns_that_the_split_is_not_a_closure():
    """The README must say the answers are already public. A split that reads
    as a closure is worse than no split, because it invites treating BR2 as
    blind when it is not."""
    if not STORE.is_dir():
        pytest.skip("key store absent on this machine")
    readme = (STORE / "README.md").read_text(encoding="utf-8")
    assert "162 days" in readme and "does not reverse it" in readme, (
        "the key-store README no longer states that the answers were already "
        "public before the split"
    )
