#!/usr/bin/env python3
"""The dry-run arm's scorer must not report a pass it has not earned.

DRAFTED 2026-11-22; destination `bench/tests/`, and onto `GUARDS`.

WHY. `scripts/score_the_dry_run_arm_2026-11-22.py` decides whether the bound
orchestrator's dry-run arm behaved. Its `--survey` mode, run against the 375
archived run directories BEFORE the arm was ever launched, found 2 defects in
the scorer itself. Both are pinned here, because a defect found once and not
guarded is a defect that returns.

  1. P2 REPORTED "HELD" ON 375 RUNS THAT RECORDED 0 DECISIONS. "0 of 0 acted"
     proves nothing. P2 is the predicate that tests whether CC1 was right to
     judge this arm its own to run, so a vacuous pass there is the worst
     possible place for one.

  2. P4 REPORTED "FALSIFIED" ON 12 RUNS AND 11 WERE FALSE. It scanned for a
     paid host NAME, and `tickets.jsonl` -- a harvested copy of the repository's
     ticket store -- carries `api.anthropic.com` as ticket TEXT. Among the 12
     was `severity_bounds_validation_20261102T004713Z`, the run this project
     records as unpaid. A substring is not a call.

★ EVERY CASE IS CONSTRUCTED, NOT DRAWN FROM THE ARCHIVE. A guard that reads
`bench/logs` would change its verdict whenever a run lands, and would be
guarding the archive rather than the scorer.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _find_repo()
SCORER = pathlib.Path(os.environ.get(
    "CDSFL_DRYRUN_SCORER",
    REPO / "scripts" / "score_the_dry_run_arm_2026-11-22.py"))

FIELDS = ["exit_code", "pid", "pid_alive", "pid_known", "pulse_present",
          "pulse_age_s", "pulse_ended", "rounds", "events"]


@pytest.fixture(scope="module")
def sc():
    spec = importlib.util.spec_from_file_location("dryrun_scorer", SCORER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["dryrun_scorer"] = m
    spec.loader.exec_module(m)
    return m


def _decision(**over) -> dict:
    """The REAL recorded shape, verified against `classify()` on 2026-11-22.

    ★ THE FIRST VERSION OF THIS FIXTURE WAS FLAT and invented a shape the code
    never produces, so every test here passed against a fiction. `classify()`
    returns {decision, evidence, reason} and `record()` preserves it, so the 9
    fields sit UNDER `evidence`. A fixture that does not match its subject tests
    nothing, however green it is.
    """
    ev = {f: 0 for f in FIELDS}
    ev.update({"exit_code": 42, "pid_alive": False, "pid_known": True,
               "pulse_present": True, "pulse_ended": True})
    top = {"decision": "RESUME", "acted": False, "reason": "", "evidence": ev}
    for k, v in over.items():
        (ev if k in FIELDS else top)[k] = v
    return top


def _run(tmp_path, decisions=None, console=""):
    d = tmp_path / "run"
    d.mkdir(exist_ok=True)
    if decisions is not None:
        (d / "actuator_decisions.jsonl").write_text(
            "".join(json.dumps(x) + "\n" for x in decisions))
    if console:
        (d / "console.log").write_text(console)
    return d


class TestP2CannotPassVacuously:
    def test_zero_decisions_is_NOT_TESTABLE_not_HELD(self, sc, tmp_path):
        """DEFECT 1, PINNED. This returned HELD on all 375 archived runs."""
        verdict, why = sc.p2([], invocations=None)
        assert verdict == "NOT TESTABLE", (
            f"0 decisions must not read as a pass; got {verdict}: {why}")

    def test_a_real_zero_still_holds(self, sc):
        """ANTI-OVER-CORRECTION. With decisions present and none acted, HELD."""
        verdict, _ = sc.p2([_decision(), _decision()], invocations=1)
        assert verdict == "HELD"

    def test_an_action_falsifies_and_names_the_overstep(self, sc):
        verdict, why = sc.p2([_decision(acted=True)], invocations=1)
        assert verdict == "FALSIFIED"
        assert "WRONG" in why or "not a switch" in why, (
            "P2 is the test of CC1's autonomy call; its refusal must say so")

    def test_a_second_invocation_falsifies(self, sc):
        verdict, _ = sc.p2([_decision()], invocations=2)
        assert verdict == "FALSIFIED"


class TestP4NeedsADispatchNotASubstring:
    def test_a_harvested_ticket_store_is_not_a_dispatch(self, sc, tmp_path):
        """DEFECT 2, PINNED. 11 of 12 false positives were exactly this."""
        d = _run(tmp_path, console="seats: CC2-SIM ChatGPT-SIM\nrun complete\n")
        (d / "tickets.jsonl").write_text(
            json.dumps({"title": "the route to api.anthropic.com is paid"}) + "\n")
        verdict, why = sc.p4(d)
        assert verdict != "FALSIFIED", (
            f"a ticket body naming a paid host is TEXT, not a call; got {why}")

    def test_the_tripwire_raising_does_falsify(self, sc, tmp_path):
        """ANTI-VACUITY: P4 must still be able to fail, or it proves nothing."""
        d = _run(tmp_path, console=(
            "seats: CC2-SIM\n"
            "RuntimeError: SIMULATED RUN ATTEMPTED A PAID DISPATCH to api.x.com\n"))
        verdict, _ = sc.p4(d)
        assert verdict == "FALSIFIED"

    def test_no_tripwire_evidence_is_NOT_TESTABLE(self, sc, tmp_path):
        """Silence from a guard that was never installed proves nothing."""
        d = _run(tmp_path, console="an ordinary paid run, no shim\n")
        verdict, _ = sc.p4(d)
        assert verdict == "NOT TESTABLE"

    def test_installed_and_silent_holds(self, sc, tmp_path):
        d = _run(tmp_path, console="seats: CC2-SIM Gemini-SIM\ncomplete\n")
        verdict, _ = sc.p4(d)
        assert verdict == "HELD"


class TestTheOtherThree:
    def test_p1_requires_every_field(self, sc):
        short = _decision(); short["evidence"].pop("events")
        verdict, why = sc.p1([short])
        assert verdict == "FALSIFIED" and "events" in why

    def test_p1_holds_on_a_complete_record(self, sc):
        assert sc.p1([_decision()])[0] == "HELD"

    def test_p3_is_NOT_TESTABLE_outside_its_state(self, sc):
        verdict, why = sc.p3([_decision(exit_code=0, pulse_present=False)])
        assert verdict == "NOT TESTABLE"
        assert "UNINFORMATIVE" in why, (
            "an arm that observed nothing must not read as reassurance")

    def test_p3_falsifies_on_a_hold_in_its_own_state(self, sc):
        assert sc.p3([_decision(decision="HOLD")])[0] == "FALSIFIED"

    def test_p5_catches_a_shrunk_log(self, sc, tmp_path):
        before = [_decision(), _decision()]
        d = _run(tmp_path, decisions=[_decision()])
        verdict, why = sc.p5(d, before)
        assert verdict == "FALSIFIED" and "SHRANK" in why

    def test_p5_catches_a_rewritten_row(self, sc, tmp_path):
        before = [_decision(rounds=1)]
        d = _run(tmp_path, decisions=[_decision(rounds=99)])
        verdict, why = sc.p5(d, before)
        assert verdict == "FALSIFIED" and "append-only" in why

    def test_p5_holds_on_a_pure_append(self, sc, tmp_path):
        before = [_decision(rounds=1)]
        d = _run(tmp_path, decisions=[_decision(rounds=1), _decision(rounds=2)])
        assert sc.p5(d, before)[0] == "HELD"


class TestTheScorerRefusesToGradeTheDecision:
    def test_it_never_claims_a_resume_was_right(self, sc):
        """Its own docstring says this is the founder's ruling. Executed, not
        grepped: no predicate may return a verdict word implying correctness."""
        verdicts = set()
        for fn, args in [(sc.p1, ([_decision()],)), (sc.p2, ([_decision()], 1)),
                         (sc.p3, ([_decision()],))]:
            verdicts.add(fn(*args)[0])
        assert verdicts <= {"HELD", "FALSIFIED", "NOT TESTABLE"}, (
            f"a verdict outside the 3 permitted values appeared: {verdicts}")
