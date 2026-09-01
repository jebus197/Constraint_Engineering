"""`_absolute_target` must accept the Path that `run_experiment` actually gives it.

FOUND 2026-08-30 by the first simulated run to drive `run_experiment()` itself.

`run_experiment` sets `target_rel = target_path.relative_to(REPO_ROOT)` — a
PosixPath. `_absolute_target` then did `(target_rel or "").strip()` and raised
`AttributeError: 'PosixPath' object has no attribute 'strip'`, on the
prompt-building path that every run must cross.

`_absolute_target` landed on 2026-08-23 and **no experiment has completed since**:
the only two runs after it, both `exp55_v3_control`, halted at round 0 on an
alarm. So the crash was never exercised, and Bench Run 2 would have met it.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R   # noqa: E402


def test_a_path_is_accepted():
    """The exact type run_experiment passes."""
    out = R._absolute_target(pathlib.Path("bench/dm/_memory.py"))
    assert out.endswith("bench/dm/_memory.py")
    assert pathlib.Path(out).is_absolute()


def test_a_str_still_works():
    out = R._absolute_target("bench/dm/_memory.py")
    assert out.endswith("bench/dm/_memory.py")


def test_a_path_and_an_equivalent_str_agree():
    rel = "bench/dm/_memory.py"
    assert R._absolute_target(pathlib.Path(rel)) == R._absolute_target(rel)


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_empty_inputs_still_return_empty(empty):
    assert R._absolute_target(empty) == ""


def test_an_already_absolute_path_is_returned_unchanged():
    abs_p = str(REPO / "bench" / "dm" / "_memory.py")
    assert R._absolute_target(pathlib.Path(abs_p)) == abs_p
