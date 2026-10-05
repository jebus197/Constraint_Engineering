# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 17cdbc6739fa40dd8893d21daeacb48fa5ddddf9f46fdebfc2ed5d8109439d0d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The raised routing rung budget must stay inside the simulated launcher.

WHY THIS EXISTS (panel review 2026-10-05, claude seat).

On 2026-10-05 `bench/tools/run_simulated_experiment.py` raised
`routing_max_rungs` from the `RunnerConfig` default of 2 to 4, so that the rungs
the simulated ladder actually tries span more than one stand-in model. The
rationale in that file states the added rungs "are only ever reached for a
critical that rungs 1 and 2 failed to resolve, which is the case the ladder exists
for".

MEASURED, and the premise is understated rather than wrong. Over 460
`routing_history` records in `bench/logs/` (every archived routing attempt that
recorded its rungs):

    rungs_tried = 0, unresolved : 42     (the ladder had no eligible rung)
    rungs_tried = 1, resolved   : 165
    rungs_tried = 1, unresolved : 6
    rungs_tried = 2, resolved   : 63
    rungs_tried = 2, unresolved : 184    <-- would climb to rung 3 at a budget > 2

Maximum `rungs_tried` ever observed is 2, i.e. the cap, and 184 of 460 attempts
(40.0%) exhausted the budget without resolving. So rungs 3 and 4 are NOT a rare
corner: at a budget of 4 they would be entered in two of every five routing
attempts, and the conditional confirm rate at rung 2 given rung 1 did not confirm
is 63/247 = 25.5%. Raising the budget therefore absorbs a substantial share of
what currently escalates to HIL, and an escalated critical is what
`unverified_critical_count` uses to BLOCK convergence.

That is a real change to the simulated run's convergence behaviour, in the one
direction `bench/tools/sim_dispatch_shim.py`'s own comment calls "the one
direction that makes it useless" -- the simulated run looks cleaner than the real
one will. The divergence may well be the right trade for rehearsing a mixed
ladder, which is a founder call, but it must not leak into a real config, where
it would also multiply frontier-model dispatches per unresolved critical.

THIS GUARD pins exactly that boundary: real configs stay on the default, the
simulated launcher is the only divergence, and the divergence is a known number
rather than drift. It takes no position on whether 4 is the right value.

Every assertion PARSES or IMPORTS. None matches free source text.
"""
import ast
import dataclasses
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SIM_LAUNCHER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def _runner_default() -> int:
    from bench.reference_runner_v3 import RunnerConfig
    for f in dataclasses.fields(RunnerConfig):
        if f.name == "routing_max_rungs":
            return f.default
    raise AssertionError("RunnerConfig no longer has routing_max_rungs")


def _sim_launcher_value():
    """The literal the simulated launcher passes, read by parsing its AST."""
    found = []
    for node in ast.walk(ast.parse(SIM_LAUNCHER.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and (
                getattr(node.func, "attr", None)
                or getattr(node.func, "id", None)) == "RunnerConfig":
            for kw in node.keywords:
                if kw.arg == "routing_max_rungs":
                    found.append(ast.literal_eval(kw.value))
    return found


class TestTheDefaultIsUntouched:
    def test_runner_config_still_defaults_to_two(self):
        assert _runner_default() == 2, (
            "the RunnerConfig default changed; every archived routing path was "
            "recorded at 2 and the Exp 42 validation that reached 7 of 7 was a "
            "2-rung ladder")

    def test_routes_own_default_is_still_two(self):
        import inspect

        from bench.routing import resolve_via_routing, route
        for fn in (route, resolve_via_routing):
            assert inspect.signature(fn).parameters["max_rungs"].default == 2, fn


class TestNoRealConfigRaisesIt:
    def test_no_archived_experiment_config_sets_it(self):
        """A real config carrying 4 would quadruple frontier dispatches per
        unresolved critical AND change production convergence."""
        cfgs = sorted(REPO.glob("bench/exp*_configs/*.json")) + \
            sorted(REPO.glob("bench/exp*_config.json"))
        if not cfgs:
            pytest.skip("no experiment configs in this checkout")
        offenders = []
        for p in cfgs:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            v = d.get("routing_max_rungs")
            if v is not None and int(v) != _runner_default():
                offenders.append(f"{p.relative_to(REPO)}={v}")
        assert not offenders, (
            "real experiment config(s) raise the routing rung budget: "
            f"{offenders}. The raised budget is a SIMULATION-ONLY divergence "
            "introduced to rehearse a mixed-model ladder; in a real config it "
            "changes production convergence and spend.")

    def test_the_population_is_not_empty(self):
        """ANTI-VACUITY: a scan of 0 configs reports clean for a population it
        could not read."""
        cfgs = sorted(REPO.glob("bench/exp*_configs/*.json"))
        assert len(cfgs) >= 10, (
            f"only {len(cfgs)} experiment configs found; the guard guards nothing")


class TestTheSimulatedLauncherIsTheOnlyDivergence:
    def test_the_simulated_launcher_declares_a_single_raised_value(self):
        vals = _sim_launcher_value()
        assert len(vals) == 1, (
            f"the simulated launcher passes routing_max_rungs {len(vals)} times "
            f"({vals}); a second call site makes the divergence unreadable")
        assert vals[0] > _runner_default(), (
            "the simulated launcher no longer raises the budget, so this guard "
            "and the mixed-ladder rationale in that file are both stale")

    def test_the_raised_value_is_reachable_through_the_real_call_site(self):
        """EXECUTED. The budget is threaded only when it differs from 2, so a
        raised value that the call site drops would be an addition nothing
        reaches."""
        from bench.routing import resolve_via_routing
        budget = _sim_launcher_value()[0]
        tried = []

        def _resolve(model, finding):
            tried.append(model)
            return ""          # never supply a falsifier -> never resolve

        res = resolve_via_routing(
            {"id": "C0001"}, [f"M{i}" for i in range(8)], _resolve,
            lambda code: "CONFIRMED", max_rungs=budget)
        assert len(tried) == budget and res.rungs_tried == budget, (
            f"the ladder tried {tried} at a budget of {budget}")
