"""B209: THE cy GATE MUST RELEASE ON THE SHAPE THE BOARD ACTUALLY HAS.

WHY A SECOND GUARD EXISTS BESIDE `test_the_cy_refusal_budget_binds_2026-11-22`
-----------------------------------------------------------------------------
That guard drives `spend()` with key strings IT CONSTRUCTS. B209's defect was
never in `spend()`; it was in the KEY handed to it, built inline in `main()`.
A test that supplies its own churning keys MANUFACTURES the precondition a
key-side repair removes, so it cannot observe such a repair and its 2 strict
xfails stay on however the key is fixed. Same family as
`feedback_a_falsifier_on_a_satisfied_precondition_proves_nothing_2026-11-23`.
THAT GUARD IS NOT WRONG AND IS NOT REPLACED: `spend()`'s behaviour on a key that
genuinely changes is a real property worth holding. This one tests the LAYER
THAT DECIDES -- `main()`'s exit code -- which is the only layer whose verdict
reaches the session (`feedback_verify_the_deciding_layer`).

THE SCENARIOS ARE DERIVED FROM THE OBSERVED SHAPE, NOT INVENTED. B215's record:
the live board is a STABLE PRIMARY PID plus CHURNING SUB-SECOND CHILDREN.
Earlier candidate tables modelled full replacement and an observed-idle reset
only -- real adversarial shapes, kept here as L3 and L5 rather than dropped.

ANCHORS COME FROM THE SUBJECT. The horizon and the expected release points are
read off the module under test, never typed here
(`feedback_derive_the_anchor_never_the_expectation_2026-11-10`).

NON-VACUITY IS PROVEN, NOT ASSERTED. `test_this_guard_is_red_against_the_known_
defective_form` runs the same predicate against the pre-repair gate recorded in
git and requires it to FAIL. A guard that cannot fail is not a guard
(`feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31`).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys

import pytest

def _repo_root() -> pathlib.Path:
    """Walk up for the marker rather than counting directory levels.

    `parents[2]` silently resolves to the wrong tree the moment the file
    is run from anywhere else, which is how a probe ends up measuring a
    temp directory instead of the subject
    (`feedback_a_probes_location_can_manufacture_the_failure_2026-11-02`).
    """
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "cy_monitor_gate.py").is_file():
                return d
    raise RuntimeError("cannot locate the repository root from "
                       f"{__file__!r} or cwd {pathlib.Path.cwd()!r}")


REPO = _repo_root()
LIVE = REPO / "hooks" / "cy_monitor_gate.py"
#: The seam: a candidate gate can be scored without touching the live one.
GATE = pathlib.Path(os.environ.get("CDSFL_CY_GATE_PATH", "").strip() or LIVE)
#: The last commit whose gate predates the B209 repair. Used ONLY by the
#: non-vacuity test, which must stay red against it.
PRE_REPAIR_REV = "HEAD"


def _load(path: pathlib.Path, tag: str):
    spec = importlib.util.spec_from_file_location(f"cyg_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: How many Stop events to drive before declaring a gate TRAPPED. Derived from
#: the subject's own per-activity budget and NOTHING ELSE.
#:
#: ★ IT USED TO READ `MAX_REFUSALS_PER_SESSION` AND THAT COULD HANG THE BOARD.
#: A variant built to isolate one half of the repair set that constant to 10**9
#: to disable the ceiling, and this function dutifully returned a horizon of
#: 1,000,000,020 events. The run was still going 35 min later and had to be
#: killed by pid. A guard on the board must have a bound that NO property of the
#: thing it measures can inflate (`feedback_cap_the_test_that_hangs_...`).
#:
#: 5x the per-activity budget is not arbitrary: the accepted design's own
#: ceiling is 3x, releasing at 3x + 1, so 5x admits it with room while refusing
#: a gate that needs more than 5x its own stated budget to let go. Such a gate
#: traps the session for practical purposes, and this guard should FAIL on it
#: rather than run for ever trying to be fair to it.
_HORIZON_MULTIPLE = 5


def _horizon(mod) -> int:
    per_key = int(getattr(mod, "MAX_REFUSALS", 60))
    return _HORIZON_MULTIPLE * per_key + 20


def _step(mod, live, unwatched, pids, session_id) -> int:
    mod.live_runs = lambda: (live, unwatched)
    mod.runner_processes = lambda: pids
    mod.parked = lambda: False
    old = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"session_id": session_id}))
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return mod.main()
    finally:
        sys.stdin = old


def _pids(name: str, i: int) -> list[str]:
    if name == "L1":
        return ["100"]                       # stable single pid
    if name in ("L2", "L3", "L4"):
        return ["100", str(200 + i)]         # STABLE PRIMARY + CHURNING CHILD
    return [str(300 + i)]                    # L5: no overlap at all


def _run(path: pathlib.Path, tag: str, name: str, state: pathlib.Path) -> dict:
    os.environ["CDSFL_CY_STATE"] = str(state)
    mod = _load(path, f"{tag}_{name}")
    first, release, ev, extra = None, None, 0, {}
    for i in range(_horizon(mod)):
        if name == "L3" and i and i % 20 == 0:          # an OBSERVED idle
            _step(mod, [], [], [], "S1")
            if hasattr(mod, "note_idle"):
                mod.note_idle()
            continue
        rc = _step(mod, [], [], _pids(name, i), "S1")
        ev += 1
        if first is None:
            first = rc == 2
        if rc == 0 and release is None:
            release = ev
            if name == "L4":
                extra["new_session_refuses"] = _step(
                    mod, [], [], ["900", "901"], "S2-NEW") == 2
            break
    return {"first_refuse": first, "release_at": release, "events": ev, **extra}


def _scores(path: pathlib.Path, tag: str, tmp: pathlib.Path) -> dict:
    return {n: _run(path, tag, n, tmp / f"{tag}_{n}.json")
            for n in ("L1", "L2", "L3", "L4", "L5")}


#: THE DECISION RULE, as a mapping of NAME -> PREDICATE. It is a module-level
#: constant so the criterion NAMES exist without any score being evaluated:
#: building them by calling the predicates on a stub is how a collection-time
#: KeyError gets mistaken for a broken subject.
CRITERIA = {
    "still a gate: refuses on event 1 of L1":
        lambda s: s["L1"]["first_refuse"] is True,
    "still a gate: refuses on event 1 of L2":
        lambda s: s["L2"]["first_refuse"] is True,
    "bounded: releases on L2 (the live shape)":
        lambda s: s["L2"]["release_at"] is not None,
    "bounded: releases on L3 (live + idle)":
        lambda s: s["L3"]["release_at"] is not None,
    "bounded: releases on L5 (full replacement)":
        lambda s: s["L5"]["release_at"] is not None,
    "separates: a NEW session refuses again":
        lambda s: s["L4"].get("new_session_refuses") is True,
}


def _criteria(s: dict) -> dict:
    return {name: bool(fn(s)) for name, fn in CRITERIA.items()}


@pytest.fixture(scope="module")
def scored(tmp_path_factory):
    return _scores(GATE, "sub", tmp_path_factory.mktemp("cy_live_shape"))


@pytest.mark.parametrize("crit", list(CRITERIA))
def test_each_admissibility_criterion_holds(scored, crit):
    """Each criterion is its OWN test, so a failure names which property broke."""
    got = _criteria(scored)
    assert got[crit], (
        f"{GATE} fails: {crit}\n"
        f"scores: {json.dumps(scored, indent=2)}")


def test_the_live_shape_escapes_no_later_than_the_per_activity_budget(scored):
    """THE POINT OF THE REPAIR: on the measured shape the per-activity budget
    must be what binds, not the far looser session ceiling. Anchor derived."""
    mod = _load(GATE, "anchor")
    expect = int(getattr(mod, "MAX_REFUSALS", 60)) + 1
    got = scored["L2"]["release_at"]
    assert got == expect, (
        f"on the LIVE shape the gate released at event {got}, not {expect}. "
        f"Releasing later means the activity key is still churning and only a "
        f"coarser ceiling is catching it.")


def test_this_guard_is_red_against_the_known_defective_form(tmp_path):
    """NON-VACUITY. The pre-repair gate must FAIL this guard's own predicate.

    Reads the gate from git rather than from the tree, so the proof does not
    depend on an uncommitted file and cannot be quietly satisfied by the
    repaired form (`feedback_a_grep_verdict_cannot_see_its_subject_removed`).
    """
    rel = LIVE.relative_to(REPO).as_posix()
    blob = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{PRE_REPAIR_REV}:{rel}"],
        capture_output=True, text=True)
    if blob.returncode != 0:
        pytest.skip(f"cannot read {PRE_REPAIR_REV}:{rel} from git")
    old = tmp_path / "pre_repair_gate.py"
    old.write_text(blob.stdout, encoding="utf-8")
    if "MAX_REFUSALS_PER_SESSION" in blob.stdout and "def refusal_key" in blob.stdout:
        pytest.skip(f"{PRE_REPAIR_REV} already carries the repair; "
                    f"re-point PRE_REPAIR_REV at a commit that predates it")
    failed = [k for k, v in _criteria(_scores(old, "pre", tmp_path)).items() if not v]
    assert failed, (
        "the PRE-REPAIR gate passed every criterion, so this guard asserts "
        "nothing. Either the scenarios no longer reproduce B209 or the wrong "
        "revision is pinned.")
