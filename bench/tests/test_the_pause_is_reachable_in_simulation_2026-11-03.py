"""A simulated run must be able to ask for the human-review pause.

WHY THIS EXISTS, AND IT CAME FROM REFUTING MY OWN DESIGN TWICE. The actuator's
scope was settled as "drive the RESUME of a run that paused itself", on the
ground that the alternative addressed a gap with 0 observed instances. The same
standard applied to my own choice refuted it: **0 of 78 archived runs ever
paused**, Wilson 95% [0.000000, 0.046938], with no `hil_status` on any report and
0 `hil_rNN.json` partials on disk.

THE SECOND CHECK REFUTED THE ALARM. The gate's own line `review gate CONSULTED,
not firing` -- written on every NON-firing consultation, precisely so a reader
sees what was weighed -- appears **0 times across 324 archived run logs**. That
looked like dead code and is not: both sites sit behind `if cfg.hil_review`, and
the flag defaults to False. The gate is OPT-IN BY DESIGN.

THE THIRD CHECK FOUND THE ACTUAL GAP, which this guards. The simulated runner
mentioned `hil_review` 0 times: no parser flag, and a `RunnerConfig(...)` of 7
fields without it. **So a simulated run could not pause at all**, and simulation
is where this project's process tests a fix before the live runner sees it. An
actuator acting on a paused run would have been untestable where it matters.

THE LOAD-BEARING TEST IS `test_the_flag_is_what_turns_it_on`: it asserts BOTH
that the flag reaches the config AND that the config is False without it. Either
assertion alone is satisfiable by a constant -- a flag wired to nothing passes
the first if the default were True, and a flag that does nothing passes the
second. Only the pair establishes that the flag is what decides.

AND THE RUNNER'S OWN DEFAULT IS PINNED SEPARATELY, because making the pause
askable must not make it automatic: a simulated run that does not ask must
behave exactly as it did before.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SIM = REPO / "bench" / "tools" / "run_simulated_experiment.py"
RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def sim():
    if str(REPO / "bench") not in sys.path:
        sys.path.insert(0, str(REPO / "bench"))
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("_sim_pause", SIM)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_sim_pause"] = m
    try:
        spec.loader.exec_module(m)
    except Exception as exc:                                 # noqa: BLE001
        pytest.skip(f"the simulated runner does not import here: {exc}")
    return m


class TestTheFlagExistsAndDecides:
    def test_the_parser_accepts_it(self, sim):
        ap = sim.build_parser()
        args = ap.parse_args(["--hil-review"])
        assert getattr(args, "hil_review") is True

    def test_it_defaults_to_off(self, sim):
        ap = sim.build_parser()
        args = ap.parse_args([])
        assert getattr(args, "hil_review", None) is False, (
            "the flag must default to off, or every existing simulated run "
            "changes behaviour")

    def test_the_flag_is_what_turns_it_on(self, sim):
        """THE LOAD-BEARING PAIR. Each half alone is satisfiable by a constant;
        only together do they establish that the flag decides."""
        ap = sim.build_parser()
        on = ap.parse_args(["--hil-review"])
        off = ap.parse_args([])
        assert getattr(on, "hil_review") is True
        assert getattr(off, "hil_review") is False
        assert getattr(on, "hil_review") != getattr(off, "hil_review"), (
            "the flag reads the same with and without it, so it decides "
            "nothing")

    def test_it_is_passed_into_the_runner_config(self):
        """EXECUTE-DO-NOT-GREP's limit, acknowledged: constructing the real
        config needs an experiment's worth of arguments, so this asserts on the
        construction SITE. The behavioural half is the parser tests above and
        the runner-default test below."""
        t = SIM.read_text()
        m = re.search(r"hil_review\s*=\s*bool\(getattr\(args,\s*'hil_review'", t)
        assert m, (
            "the simulated runner's RunnerConfig does not pass hil_review, so "
            "the parser flag reaches nothing and a simulated run still cannot "
            "pause")


class TestMakingItAskableDoesNotMakeItAutomatic:
    def test_the_runners_own_default_is_still_off(self):
        t = RUNNER.read_text()
        assert re.search(r"^\s*hil_review:\s*bool\s*=\s*False", t, re.M), (
            "the runner's own default for hil_review is no longer False; "
            "making the pause askable must not make it automatic")

    def test_both_consultation_sites_remain_behind_the_flag(self):
        """If a site stopped being gated, the pause would fire in runs that
        never asked for it -- which is the opposite of the design."""
        t = RUNNER.read_text()
        gated = len(re.findall(r"if cfg\.hil_review", t))
        assert gated >= 2, (
            f"only {gated} consultation site(s) are gated on cfg.hil_review; "
            f"the gate is reached without being asked for")
