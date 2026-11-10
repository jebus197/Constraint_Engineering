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
        # RESOLVED EXPLICITLY, NEVER BY SEARCHING THE REPOSITORY.
        #
        # This used to be `REPO.rglob(name)` with `hits[0]`. For
        # `reference_runner_v3.py` that is 75 matches, 74 of them sandbox
        # copies under `bench/logs/`, so the file this test validated against
        # was decided by directory traversal order. It happened to pick the
        # real one; nothing made it do so. A guard whose subject depends on
        # iteration order can validate a citation against a 5-week-old copy
        # and report success.
        KNOWN = {
            "reference_runner_v3.py": REPO / "bench" / "reference_runner_v3.py",
            "launch_exp39.py": REPO / "bench" / "launch_exp39.py",
        }
        for name, ln in cites:
            path = KNOWN.get(name)
            assert path is not None, (
                f"A2/A3 cite {name}, which this test has no explicit path for. "
                f"Add it to KNOWN rather than searching for it: a repository "
                f"search finds sandbox copies and picks one by traversal order.")
            if not path.is_file():
                pytest.skip(f"{name} is not present here")
            src = path.read_text(errors="replace").splitlines()
            assert int(ln) <= len(src), (
                f"{name}:{ln} is past the end of a {len(src)}-line file")


class TestTheDeclaredCitationsStillPointAtWhatTheyName:
    """`CITATIONS` is checked, because the prose version of it had drifted.

    WHY THIS EXISTS. A2 and A3 used to carry their line numbers as prose. Of
    the 4 line numbers in A2, 1 was exact, 1 sat a single line off on the
    comment explaining the gate, and 2 had DRIFTED -- `:21274` by 23 lines
    onto a `_log("")` call and `:21368` by 7 onto a phase-name log. A3 named
    `is_hil_paused()`, a symbol which appeared nowhere in the project except
    in that sentence; the real symbol is the property `hil_paused`. Nothing
    checked any of it, inside a declaration whose entire purpose is to be
    checkable.

    So the numbers moved into a dict and this class reads it. Drift is now
    caught by the commit that causes it rather than by a reader months later.
    """

    def test_the_citations_dict_exists_and_is_not_empty(self, A):
        cites = getattr(A, "CITATIONS", None)
        assert isinstance(cites, dict) and cites, (
            "CITATIONS is missing or empty, so the declaration's line numbers "
            "are unverified again and this guard measures nothing")
        assert len(cites) >= 9, (
            f"only {len(cites)} citation(s); each was added for a statement "
            f"the declaration makes, and removing one removes a check")

    def test_every_citation_points_at_a_line_holding_its_substring(self, A):
        """The whole point: an exact check, not an adjacency allowance.

        An adjacency window is what let `:21298` look acceptable while sitting
        on a comment. A declaration can afford to be exact, because this test
        tells it the moment it is not.
        """
        wrong = []
        for label, (rel, lineno, expect) in sorted(A.CITATIONS.items()):
            path = REPO / rel
            if not path.is_file():
                wrong.append(f"{label}: {rel} does not exist")
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            if not (0 < lineno <= len(lines)):
                wrong.append(
                    f"{label}: {rel}:{lineno} is outside the file "
                    f"({len(lines)} lines)")
                continue
            got = lines[lineno - 1]
            if expect not in got:
                near = [i + 1 for i, l in enumerate(lines) if expect in l]
                wrong.append(
                    f"{label}: {rel}:{lineno} does not hold {expect!r}; "
                    f"it holds {got.strip()[:50]!r}. "
                    + (f"That text is now at line(s) {near[:4]}."
                       if near else "That text is nowhere in the file."))
        assert not wrong, (
            f"{len(wrong)} of {len(A.CITATIONS)} declared citation(s) "
            f"no longer point at what they name:\n  " + "\n  ".join(wrong))

    def test_the_named_symbols_exist_where_claimed(self, A):
        """A2 and A3 name symbols, not only lines. Check the symbols too.

        `is_hil_paused()` was named by the declaration and existed nowhere.
        A citation can be line-correct and still name a thing that is not
        there, so the symbol is checked separately from the line.
        """
        must_exist = {
            "cfg.hil_review": "bench/reference_runner_v3.py",
            "hil_paused": "bench/launch_exp39.py",
        }
        missing = []
        for sym, rel in must_exist.items():
            path = REPO / rel
            if not path.is_file() or sym not in path.read_text(encoding="utf-8"):
                missing.append(f"{sym!r} is not in {rel}")
        assert not missing, "; ".join(missing)

        # POSITIVE, not negative. The correction note in the declaration
        # legitimately mentions the invented name in order to record that it
        # was invented, so asserting that name's absence would be brittle.
        # What matters is that the REAL symbol is the one named as the symbol.
        src = ACT.read_text(encoding="utf-8")
        assert "`hil_paused`" in src, (
            "the declaration no longer names the real symbol `hil_paused`")
        assert "A3.property" in A.CITATIONS, (
            "A3's symbol is no longer carried as a checkable citation")

class TestTheRemedyForADriftedCitation:
    """The guard above DETECTS drift. This is the thing that REPAIRS it.

    `scripts/repoint_the_actuator_citations_2026-11-09.py` exists because the 6
    A2 citations moved twice on 2026-11-09, +144 and then +15, and the
    arithmetic was done by hand both times. `sys.exit(42)` occurs at the round
    site AND the phase site, so a re-pointer that takes the first match leaves
    one citation on the WRONG block while this guard goes green -- a worse
    outcome than the red it replaces.

    A remedy nothing calls is the addition-nothing-reaches half of the additive
    standard, so it is executed here.
    """

    def _mod(self):
        import importlib.util
        p = (pathlib.Path(__file__).resolve().parents[2]
             / "scripts/repoint_the_actuator_citations_2026-11-09.py")
        assert p.exists(), "the remedy for a drifted citation is not present"
        spec = importlib.util.spec_from_file_location("_repoint", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_it_reports_no_drift_on_the_current_tree(self):
        """EXECUTED, not grepped: the citations are correct right now."""
        m = self._mod()
        src = m.ACTUATOR.read_text(encoding="utf-8")
        plan = m._plan(src)
        assert plan, "the citation table's shape has changed"
        drifted = [(e[0].group("key"), e[1], e[2]) for e in plan if e[1] != e[2]]
        assert not drifted, (
            f"these citations no longer point at their substring: {drifted}. "
            f"Run scripts/repoint_the_actuator_citations_2026-11-09.py --apply "
            f"and READ the distinct-delta line before accepting it.")

    def test_an_identical_substring_resolves_by_block_order(self):
        """THE WHOLE POINT. 2 sites, 1 substring, and order decides.

        Both A2 exit citations hold `sys.exit(42)`. A re-pointer that searched
        from the top of the file for each would map BOTH to the round site.
        """
        m = self._mod()
        src = m.ACTUATOR.read_text(encoding="utf-8")
        plan = m._plan(src)
        exits = [(e[0].group("key"), e[2]) for e in plan
                 if e[3] == "sys.exit(42)"
                 and e[0].group("path") == "bench/reference_runner_v3.py"]
        assert len(exits) == 2, f"expected 2 sys.exit(42) citations, got {exits}"
        keys = [k for k, _ in exits]
        lines = [n for _, n in exits]
        assert keys == ["A2.exit.round", "A2.exit.phase"], keys
        assert lines[0] < lines[1], (
            f"the round and phase exits resolved to {lines}; they must be "
            f"distinct and in block order, or one citation is on the wrong "
            f"block with this guard still green")

    def test_the_drifted_case_is_what_the_floor_is_for(self):
        """RE-RUN THE INPUT THAT FAILED, not the one that passes.

        The sibling test above asserts the 2 `sys.exit(42)` citations resolve
        in block order, and it was VACUOUS when written: with the citations
        already correct, nearest-match alone returns each one's own line and
        the floor never bites. Removing the floor left it green.

        The floor bites on the DRIFTED input. Before the +144 shift the 2
        exits were cited at 21354 and 21424 while the true sites were 21498
        and 21568. Nearest-match maps 21354 -> 21498 correctly, then maps
        21424 -> 21498 as well, because 74 is nearer than 144. Both citations
        land on the ROUND site, the phase citation is wrong, and the contract
        guard goes GREEN because the line it names does hold `sys.exit(42)`.
        That is the exact failure this script was written to prevent, so it is
        the input the test has to use.
        """
        m = self._mod()
        #: ★ 21513, 21583 -> 21613, 21683 ON 2026-11-09. B21 step 1 added a
        #: 100-line policy block to bench/reference_runner_v3.py ABOVE these
        #: 2 sites, so both shifted by exactly 100. The repointer reported
        #: "distinct deltas: [100] -- a clean block shift, nothing moved
        #: WITHIN the block", which is the condition under which a repoint
        #: is a renumbering rather than a change of meaning. The substrings
        #: are unchanged and the sibling test resolves them live.
        true_round, true_phase = 21613, 21683
        stale_round, stale_phase = true_round - 159, true_phase - 159
        synthetic = (
            'CITATIONS = {\n'
            f'    "A2.exit.round":   ("bench/reference_runner_v3.py", {stale_round},\n'
            '                        "sys.exit(42)"),\n'
            f'    "A2.exit.phase":   ("bench/reference_runner_v3.py", {stale_phase},\n'
            '                        "sys.exit(42)"),\n'
            '}\n')
        plan = m._plan(synthetic)
        got = {e[0].group("key"): e[2] for e in plan}
        assert got.get("A2.exit.round") == true_round, got
        assert got.get("A2.exit.phase") == true_phase, (
            f"the phase exit resolved to {got.get('A2.exit.phase')} instead of "
            f"{true_phase}: both citations collapsed onto the nearer site, "
            f"which is a wrong citation that the contract guard cannot see")
        assert got["A2.exit.round"] < got["A2.exit.phase"], got

    def test_a_new_occurrence_inside_the_block_does_not_capture_the_citation(
            self, tmp_path, monkeypatch):
        """WHY NEAREST-MATCH AND NOT MERELY FIRST-MATCH-ABOVE-THE-FLOOR.

        A 3rd reversion came back GREEN: replacing nearest-match with
        `cands[0]` changed nothing, because on the current table the floor
        alone already separates the 2 `sys.exit(42)` sites. So nearest-match
        looked redundant -- and it is redundant ON THAT INPUT, which is
        precisely why that input cannot decide whether to keep it.

        It stops being redundant on the edit that actually happens: a NEW
        occurrence of the substring added INSIDE the block, between the floor
        and the true site. First-match then captures the citation onto the new
        line, which holds the substring, so the contract guard stays green
        while the citation names code that has nothing to do with the claim.

        The target here is synthetic because the behaviour needs an
        interposed occurrence that the real runner does not have. The synthetic
        file is the SUBJECT, not an artefact of where the probe runs.
        """
        m = self._mod()
        target = tmp_path / "synthetic_runner.py"
        lines = ["# filler"] * 120
        lines[29] = "        sys.exit(42)      # the round site, line 30"
        lines[59] = "        sys.exit(42)      # INTERPOSED later, line 60"
        lines[99] = "        sys.exit(42)      # the phase site, line 100"
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        monkeypatch.setattr(m, "REPO", tmp_path)

        synthetic = (
            'CITATIONS = {\n'
            '    "X.round": ("synthetic_runner.py", 30,\n'
            '                "sys.exit(42)"),\n'
            '    "X.phase": ("synthetic_runner.py", 100,\n'
            '                "sys.exit(42)"),\n'
            '}\n')
        got = {e[0].group("key"): e[2] for e in m._plan(synthetic)}
        assert got.get("X.round") == 30, got
        assert got.get("X.phase") == 100, (
            f"the phase citation resolved to {got.get('X.phase')} instead of "
            f"100: a line inserted inside the block captured it. The line it "
            f"names does hold the substring, so the contract guard cannot see "
            f"that the citation is now wrong.")

    def test_a_citation_whose_file_is_gone_is_reported_not_passed_over(self):
        """THE BRANCH NOTHING ON THE CURRENT TABLE REACHES.

        A 5th reversion came back green -- making a vanished file report
        no-drift changed nothing, because every citation on the table names a
        file that exists. An unreached branch is not a tested one, and this is
        the branch that tells a human a citation CANNOT be repaired
        mechanically. Reported as no-drift, a deleted subject reads as a
        healthy citation.
        """
        m = self._mod()
        synthetic = (
            'CITATIONS = {\n'
            '    "X.gone": ("bench/a_file_that_does_not_exist_2026-11-09.py", 7,\n'
            '               "anything at all"),\n'
            '}\n')
        plan = m._plan(synthetic)
        assert len(plan) == 1, plan
        _, old_line, new_line, _, why = plan[0]
        assert new_line is None, (
            "a citation whose file is gone was given a line number, so it "
            "reports as repaired rather than as needing a human")
        assert old_line == 7
        assert "gone" in why or "not found" in why, why

    def test_reporting_is_the_default_and_writing_is_opt_in(self):
        """A REMEDY THAT WRITES BY DEFAULT CAN DESTROY WORK.

        Recorded 2026-11-04: an instrument's own remedy pointed at
        destruction. This one must say what it would do unless asked to act.
        """
        m = self._mod()
        import argparse, inspect
        src = inspect.getsource(m.main)
        assert '"--apply"' in src, "there is no opt-in flag at all"
        assert 'action="store_true"' in src, (
            "--apply is not a flag, so it cannot default to off")
        assert "if args.apply and moved:" in src, (
            "the write is not gated on --apply")

