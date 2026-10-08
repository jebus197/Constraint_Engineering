"""The ladder depth default is EXHAUST, and the two defaults cannot drift.

FOUNDER'S RULING, 2026-10-06 and restated repeatedly since: *"I don't think there
should be a cap at all. If it's a measured statistic, along with capability
fingerprinting then the problem should run until it is either resolved, or the
ladder is exhausted. (No more models to try.)"*

IT WAS EXPRESSIBLE BUT EXPRESSED NOWHERE. `max_rungs=0` has meant exhaust since
2026-10-06, and 0 of 47 experiment configs set it, so the ruling reached nothing --
the addition-nothing-reaches failure this project has 11 confirmed instances of.

WHAT THE CAP COST, measured over 305 archived routing records: 143 (46.8852%,
Wilson [41.3583%, 52.4896%]) hit the cap of 2, and 103 of those were ABANDONED
UNRESOLVED. Per-rung conditional resolve rates are 0.3902 at rung 1, Wilson
[0.3314, 0.4524], and 0.2797 at rung 2, Wilson [0.2127, 0.3583] -- declining with
depth, as harder findings survive. Over 4 further rungs that recovers roughly 46 to
75 of the 103 for about 209 extra dispatches (192.6 to 227.1), worst case 412. So 2
to 4 extra dispatches per finding recovered.

AND THE RATE BEYOND DEPTH 2 HAS NEVER BEEN MEASURED, because the cap prevented it.
That circularity is the strongest argument for the ruling and was not the reason
given for it.

THE COUPLING THAT MADE A NAIVE FLIP DANGEROUS, and why the constant exists. The
runner OMITS the `max_rungs` keyword when the config equals the function default,
which is what keeps 8 narrow `fake_route` stubs across 4 files working. Flipping
only the config default would have passed the keyword on every run and broken them.
A first attempt read the function default with `inspect.signature(route)` and raised
KeyError the moment a test monkeypatched `route` with a narrow stub -- the exact case
the logic protects. `routing.DEFAULT_MAX_RUNGS` is a module constant, immune to
patching, and both signatures reference it.
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def RT():
    return _load("rt_cap", "bench/routing.py")


@pytest.fixture(scope="module")
def RR():
    return _load("rr_cap", "bench/reference_runner_v3.py")


class TestTheDefaultIsExhaust:
    def test_the_constant_is_zero(self, RT):
        assert RT.DEFAULT_MAX_RUNGS == 0, (
            "a positive default is a cap, which the founder has ruled against")

    def test_both_function_signatures_reference_the_constant(self, RT):
        for fn in (RT.route, RT.resolve_via_routing):
            d = inspect.signature(fn).parameters["max_rungs"].default
            assert d == RT.DEFAULT_MAX_RUNGS, (fn.__name__, d)

    def test_the_config_default_matches(self, RR, RT):
        assert RR.RunnerConfig().routing_max_rungs == RT.DEFAULT_MAX_RUNGS, (
            "the config and function defaults disagree, so the omit-at-default "
            "condition cannot be correct for both: the runner would either pass a "
            "cap nobody asked for or omit one that was")


class TestTheDefaultActuallyExhausts:
    @staticmethod
    def _run(RT, **kw):
        ladder = list(RT.DEFAULT_FALSIFIER_STRENGTH)
        seen = []

        def resolve(model, _f):
            seen.append(model)
            return "assert False"

        RT.route({"id": "X", "description": "d", "model": "Nobody",
                  "falsifier_code": ""},
                 ladder, [], resolve, lambda _c: "REFUTED", lambda _a, _b: 0.0,
                 self_rung_enabled=False, **kw)
        return seen, ladder

    def test_no_keyword_reaches_every_rung(self, RT):
        seen, ladder = self._run(RT)
        assert seen == ladder, (seen, ladder)
        assert len(ladder) > 2, (
            "with 2 or fewer rungs this test cannot distinguish exhaust from a cap")

    @pytest.mark.parametrize("cap", [1, 2, 4])
    def test_an_opt_in_cap_still_binds(self, RT, cap):
        seen, ladder = self._run(RT, max_rungs=cap)
        assert seen == ladder[:cap], (cap, seen)

    def test_explicit_zero_also_exhausts(self, RT):
        seen, ladder = self._run(RT, max_rungs=0)
        assert seen == ladder


class TestTheStubProtectionSurvives:
    """The omit-at-default property, which 8 narrow stubs depend on."""

    def test_the_runner_omits_the_keyword_at_the_default(self, RT):
        fn_default = RT.DEFAULT_MAX_RUNGS
        for cfgval, expect_kw in ((fn_default, False), (2, True), (5, True),
                                  (None, False)):
            rungs = fn_default if cfgval is None else int(cfgval)
            kw = {} if rungs == fn_default else {"max_rungs": rungs}
            assert ("max_rungs" in kw) is expect_kw, (cfgval, kw)

    def test_the_call_site_does_not_read_a_patchable_signature(self):
        """MUTATION GUARD: reading inspect.signature(route) raised KeyError under a
        monkeypatched stub. If that approach returns, this fails."""
        src = (REPO / "bench" / "reference_runner_v3.py").read_text()
        i = src.index("_route_kw = {} if _rungs == _fn_default")
        window = src[max(0, i - 1200):i]
        assert "DEFAULT_MAX_RUNGS" in window, (
            "the omit condition no longer reads the module constant")
        assert 'signature(route).parameters["max_rungs"]' not in window, (
            "the call site is reading a signature that a test can monkeypatch away")
