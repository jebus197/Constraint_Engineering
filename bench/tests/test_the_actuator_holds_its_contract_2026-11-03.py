"""The actuator may not resume a run except on the one state that permits it.

WHAT THIS GUARDS. `bench/tools/cy_actuator_2026-11-03.py` is a thin outer
supervisor that drives the resume of a run which paused itself for human review.
It declares 4 assumptions and 5 guarantees as DATA (`ASSUMES`, `GUARANTEES`),
and this file EXECUTES the behaviour rather than asserting on the source text --
`execute-do-not-grep`: a test that reads a module's own description establishes
only that the module describes itself consistently.

THE LOAD-BEARING PAIR IS `test_resume_fires_on_the_permitting_state` TOGETHER
WITH `test_no_other_state_reaches_resume`. Either alone is satisfiable by a
constant: a classifier hard-wired to HOLD passes the second, and one hard-wired
to RESUME passes the first. Only the pair establishes that the exit code and the
process state are what decide.

WHY THE UNKNOWN CASE HAS ITS OWN TEST. The P-pass of the actuator found a defect
in it: with no pulse on disk the decision was correct (HOLD) but the recorded
reason asserted that the process was still alive, which was not measured --
`_pid_alive(None)` returns True as a fail-safe and the reason reported the
fail-safe as a fact. The decision and the RECORD are therefore guarded
separately, because a right decision with a false reason still corrupts G1.

WHY `GUARANTEES` IS ITERATED. A contract declared only in prose is an addition
nothing reaches. `test_every_guarantee_has_a_test` fails if a guarantee is added
to the module without a test named for it, so the declaration cannot drift ahead
of what is actually held.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
ACT = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"

#: A pid that cannot be live. `os.kill(pid, 0)` raises ProcessLookupError.
DEAD_PID = 999999


@pytest.fixture(scope="module")
def A():
    if not ACT.is_file():
        pytest.fail(f"the actuator is not at {ACT}")
    spec = importlib.util.spec_from_file_location("_actuator_guard", ACT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_actuator_guard"] = m
    spec.loader.exec_module(m)
    return m


def _pulse(**kw):
    d = {"written_at": 1e9}
    d.update(kw)
    return d


class TestG2NeverResumesALiveRun:
    def test_resume_fires_on_the_permitting_state(self, A):
        """ANTI-VACUITY HALF 1: the permitting state must actually permit."""
        r = A.classify(A.PAUSED, _pulse(pid=DEAD_PID))
        assert r["decision"] == "RESUME", (
            f"a run that paused with its process gone must be resumable, got "
            f"{r['decision']}: {r['reason']}")

    def test_a_live_process_is_never_resumed(self, A):
        r = A.classify(A.PAUSED, _pulse(pid=os.getpid()))
        assert r["decision"] == "HOLD"
        assert r["evidence"]["pid_alive"] is True

    def test_an_unknown_process_is_never_resumed(self, A):
        """No pulse means the process state is UNKNOWN, not known-exited."""
        r = A.classify(A.PAUSED, {})
        assert r["decision"] == "HOLD"

    def test_the_unknown_case_does_not_claim_the_process_is_alive(self, A):
        """THE DEFECT THE P-PASS FOUND. The 2 HOLDs are different facts and may
        not share a reason: one observed a live pid, the other observed nothing.
        """
        unknown = A.classify(A.PAUSED, {})["reason"]
        known = A.classify(A.PAUSED, _pulse(pid=os.getpid()))["reason"]
        assert unknown != known, (
            "the unknown-process HOLD reuses the known-alive reason, so the "
            "record states as fact something that was never measured")
        assert "unknown" in unknown.lower()


class TestG4AnythingUnrecognisedHolds:
    def test_no_other_state_reaches_resume(self, A):
        """ANTI-VACUITY HALF 2: nothing but the permitting state permits."""
        leaked = []
        for code in list(range(-8, 64)) + [None, 130, 143, 255, "42"]:
            if code in (0, A.PAUSED):
                continue
            if A.classify(code, _pulse(pid=DEAD_PID))["decision"] == "RESUME":
                leaked.append(code)
        assert not leaked, f"these exit codes reached RESUME: {leaked}"

    def test_a_failure_exit_holds_and_says_it_was_a_failure(self, A):
        r = A.classify(1, _pulse(pid=DEAD_PID))
        assert r["decision"] == "HOLD"
        assert "failure" in r["reason"]

    def test_a_clean_exit_the_watch_did_not_see_holds(self, A):
        """Runner and watch disagreeing is a state to stop on, not to drive."""
        r = A.classify(0, _pulse(pid=DEAD_PID, ended=False))
        assert r["decision"] == "HOLD"

    def test_a_clean_exit_the_watch_confirms_is_done(self, A):
        r = A.classify(0, _pulse(pid=DEAD_PID, ended=True))
        assert r["decision"] == "DONE"

    def test_a_clean_exit_with_no_watch_says_nothing_corroborates_it(self, A):
        r = A.classify(0, {})
        assert r["decision"] == "DONE"
        assert "corroborat" in r["reason"], (
            "a DONE resting on the exit code alone must say so, or a reader "
            "cannot tell it from one the watch confirmed")


class _CappedRunner:
    """A fake runner that REFUSES past a hard cap, so an unbounded loop fails
    by assertion rather than by hanging.

    WHY THIS SHAPE. The first version of these tests used an unconditional
    `lambda: PAUSED`. That detects a missing budget only because `drive` then
    loops for ever and pytest is eventually killed -- and a guard whose red
    signal is a TIMEOUT is one this project has already been bitten by: a
    sibling Stop hook decided correctly for weeks and was killed by the 15 s
    hook timeout in 153 of 360 invocations. A timeout red is slow, depends on a
    timeout being configured at all, and is indistinguishable from an unrelated
    hang. The cap converts it into an immediate, legible failure.
    """

    def __init__(self, code, cap):
        self.code, self.cap, self.calls = code, cap, []

    def __call__(self, argv):
        self.calls.append(list(argv))
        if len(self.calls) > self.cap:
            raise AssertionError(
                f"the actuator launched {len(self.calls)} times against a hard "
                f"cap of {self.cap}; the resume budget is not bounding the loop")
        return self.code


class TestG1EveryActionIsRecorded:
    def test_a_launch_without_a_recorded_decision_cannot_happen(self, A, tmp_path):
        (tmp_path / "cy_pulse.json").write_text(json.dumps(_pulse(pid=DEAD_PID)))
        # CAPPED, like the budget tests and for the same reason. An
        # unconditional runner here made the WHOLE FILE hang under the mutation
        # that removes the resume bound, so the mutation harness recorded that
        # mutation as caught by a pytest TIMEOUT. The budget tests were capped
        # first and it did not help, because this test was the one looping --
        # fixing the symptom that was visible rather than tracing which test
        # actually hung.
        r = _CappedRunner(A.PAUSED, cap=6)
        A.drive(["python3", "x.py"], tmp_path, tmp_path, max_resumes=3,
                act=True, _runner=r)
        rows = [json.loads(ln) for ln
                in (tmp_path / "actuator_decisions.jsonl").read_text().splitlines()]
        assert len(rows) == len(r.calls) and r.calls, (
            f"{len(r.calls)} launch(es) produced {len(rows)} recorded decision(s)")

    def test_every_row_carries_its_evidence_and_a_reason(self, A, tmp_path):
        (tmp_path / "cy_pulse.json").write_text(json.dumps(_pulse(pid=DEAD_PID)))
        A.drive(["python3", "x.py"], tmp_path, tmp_path, max_resumes=1,
                act=True, _runner=_CappedRunner(A.PAUSED, cap=4))
        rows = [json.loads(ln) for ln
                in (tmp_path / "actuator_decisions.jsonl").read_text().splitlines()]
        assert rows
        for r in rows:
            assert r.get("reason"), f"a row carries no reason: {r}"
            assert r.get("evidence"), f"a row carries no evidence: {r}"
            assert "recorded_at" in r

    def test_the_timestamp_is_taken_from_the_clock_not_typed(self, A, tmp_path):
        """A typed time cannot be detected by a linter, so it is pinned here:
        the epoch stamp must bracket the call."""
        import time
        t0 = time.time()
        A.record(tmp_path, {"decision": "HOLD", "reason": "x", "evidence": {}})
        t1 = time.time()
        row = json.loads((tmp_path / "actuator_decisions.jsonl").read_text().strip())
        assert t0 <= row["recorded_at_epoch"] <= t1


class TestG3ItIsBounded:
    def test_the_resume_budget_is_enforced(self, A, tmp_path):
        (tmp_path / "cy_pulse.json").write_text(json.dumps(_pulse(pid=DEAD_PID)))
        # The cap is the budget's own permitted launch count plus 2, so a
        # correct actuator never reaches it and a budget-less one trips it at
        # once instead of spinning.
        r = _CappedRunner(A.PAUSED, cap=6)
        res = A.drive(["python3", "x.py"], tmp_path, tmp_path, max_resumes=3,
                      act=True, _runner=r)
        assert res["resumes_driven"] == 3
        assert res["final"] == "HOLD"
        assert len(r.calls) == 4, (
            f"a budget of 3 resumes permits 4 launches, saw {len(r.calls)}")

    def test_the_resume_flag_never_accumulates(self, A, tmp_path):
        (tmp_path / "cy_pulse.json").write_text(json.dumps(_pulse(pid=DEAD_PID)))
        r = _CappedRunner(A.PAUSED, cap=8)
        A.drive(["python3", "x.py"], tmp_path, tmp_path, max_resumes=4, act=True,
                _runner=r)
        worst = max(c.count("--resume") for c in r.calls)
        assert worst <= 1, f"--resume accumulated to {worst} copies"

    def test_without_act_nothing_is_reinvoked(self, A, tmp_path):
        """The acting is OPT-IN. Fixes reach HIL and are never auto-applied;
        the same rule governs driving a run."""
        (tmp_path / "cy_pulse.json").write_text(json.dumps(_pulse(pid=DEAD_PID)))
        calls = []
        res = A.drive(["python3", "x.py"], tmp_path, tmp_path, act=False,
                      _runner=lambda a: (calls.append(list(a)), A.PAUSED)[1])
        assert len(calls) == 1 and res["resumes_driven"] == 0
        assert res["final"] == "RESUME", (
            "the decision must still be reported without --act, or the dry run "
            "tells the operator nothing")


class TestG5TheLogIsAppendOnly:
    def test_a_second_decision_does_not_overwrite_the_first(self, A, tmp_path):
        A.record(tmp_path, {"decision": "HOLD", "reason": "first", "evidence": {}})
        A.record(tmp_path, {"decision": "DONE", "reason": "second", "evidence": {}})
        lines = (tmp_path / "actuator_decisions.jsonl").read_text().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["reason"] == "first"


class TestTheContractIsReachable:
    def test_every_guarantee_has_a_test(self, A):
        """The declaration may not drift ahead of what is held.

        Each key of `GUARANTEES` must appear in a class name in THIS file, so
        adding a guarantee without a test fails here rather than passing
        silently.
        """
        text = pathlib.Path(__file__).read_text()
        classes = [ln for ln in text.splitlines() if ln.startswith("class ")]
        missing = [k for k in A.GUARANTEES
                   if not any(k in c for c in classes)]
        assert not missing, (
            f"these guarantees are declared but no test class names them: "
            f"{missing}")

    def test_the_contract_is_not_empty(self, A):
        assert len(A.ASSUMES) >= 4 and len(A.GUARANTEES) >= 5

    def test_the_assumed_line_citations_resolve(self, A):
        """A2 and A3 cite exact lines in the runner and the launcher. A citation
        that has drifted is worse than none, because it reads as verified."""
        import re
        cites = re.findall(r"([a-z_0-9]+\.py):(\d+)", " ".join(A.ASSUMES.values()))
        assert cites, "A2/A3 cite no line, so this test would be vacuous"
        for name, ln in cites:
            hits = list(REPO.rglob(name))
            hits = [h for h in hits if ".orig" not in h.name]
            if not hits:
                pytest.skip(f"{name} is not present here")
            src = hits[0].read_text(errors="replace").splitlines()
            assert int(ln) <= len(src), (
                f"{name}:{ln} is past the end of a {len(src)}-line file")
