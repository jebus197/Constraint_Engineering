"""A simulated run cannot test what it never imports or spawns.

HIS AIM, 2026-11-03: *"A wider aim of these experiments should be to test all
fixes/additional features you have produced since I first interacted with you
yesterday morning too."* The producer this guards answers whether a simulated
run CAN do that, so a run is not authorised on an assumption.

MEASURED: of 12 product-module changes since 2026-11-02, 5 are reachable by a
simulated run -- 0.416667, Wilson 95% [0.193260, 0.680489], Clopper-Pearson
[0.151652, 0.723330]. The other 7 are 5 product modules a run never touches and
2 session hooks that fire on commits and stops. The guards and producers changed
in the same window are the COMMIT BOARD's job, which already runs them.

THE LOAD-BEARING PROPERTY IS THE SPAWN ROUTE. An import closure alone gives 68
modules and MISSES everything the runner launches as a subprocess -- including
`scripts/cy_watchdog_2026-10-02.py`, the subject of this session's own watchdog
repair, which the runner starts with `subprocess.Popen([sys.executable,
str(script), ...])` so its name appears only as a string literal. With the spawn
route the closure is 76. A reachability measurement that knows only imports
reports the watchdog as unreachable, which is how the first version of this
measurement understated the answer.

AND THE VERDICT SURVIVES ITS OWN FALSIFICATION rather than being asserted: of
the 7 modules the closure misses, 2 are referenced anywhere inside it and BOTH
references are inside comments, not calls.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = (REPO / "scripts"
        / "what_a_simulated_run_would_actually_test_2026-11-03.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_simreach", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_simreach"] = m
    spec.loader.exec_module(m)
    return m


class TestTheSpawnRouteIsLoadBearing:
    def test_the_spawn_route_adds_modules_the_imports_miss(self, mod):
        index = mod._index()
        imported = mod._closure([mod.ENTRY.resolve()], index)
        spawned = mod._spawned(imported, index)
        extra = spawned - imported
        assert extra, (
            "the spawn route added nothing, so either the runner stopped "
            "launching subprocesses or the detector stopped seeing them -- "
            "either way this measurement is back to import-only and will "
            "report the watchdog as unreachable")

    def test_the_watchdog_is_reached_only_via_the_spawn_route(self, mod):
        """THE CASE THAT MOTIVATED THE ROUTE. The watchdog is this session's
        own repair subject and is spawned, never imported."""
        index = mod._index()
        imported = mod._closure([mod.ENTRY.resolve()], index)
        full = mod._closure(
            list(imported) + list(mod._spawned(imported, index)), index)
        wd = "scripts/cy_watchdog_2026-10-02.py"
        assert wd not in mod._rel(imported), (
            "the watchdog is now importable, so this test no longer pins the "
            "distinction it was written for -- check whether the runner "
            "changed how it starts the watch")
        assert wd in mod._rel(full), (
            "the watchdog is not reached even WITH the spawn route, so the "
            "runner no longer launches it and `cy` detection does not arm")


class TestTheProducerRunsAndReportsBothIntervals:
    def test_it_runs_clean(self):
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert r.returncode == 0, r.stderr[-800:]
        for needle in ("REACHABLE BY A SIMULATED RUN", "Wilson 95%",
                       "Clopper-Pearson 95%", "UPPER BOUND"):
            assert needle in r.stdout, f"the producer does not report {needle!r}"

    def test_it_states_that_reachability_is_an_upper_bound(self):
        """Reachability is necessary, not sufficient: a module on the path may
        hold a branch no run takes. Without that caveat the figure reads as a
        coverage claim, which is a figure answering a different question."""
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert "AT MOST" in r.stdout

    def test_the_dynamic_falsification_is_reported_not_skipped(self):
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert "DYNAMIC-REFERENCE FALSIFICATION" in r.stdout
        assert "INSIDE A COMMENT" in r.stdout, (
            "no commented reference was reported, so either the corpus changed "
            "or the comment test stopped running -- a bare count of references "
            "would wrongly read a comment as a call")


class TestTheHalvesStaySeparate:
    def test_guards_and_scripts_are_counted_apart_from_product(self, mod):
        """Summing them would say a run tests the guards, which it never does."""
        changed = mod._changed("2026-11-02 00:00")
        assert changed, "no changes in the window; the window may be wrong"
        tests = [c for c in changed if c.startswith("bench/tests/")]
        scripts = [c for c in changed if c.startswith("scripts/")]
        product = [c for c in changed
                   if not c.startswith("bench/tests/")
                   and not c.startswith("scripts/")]
        assert tests and scripts and product, (
            f"a category is empty: {len(tests)} tests, {len(scripts)} scripts, "
            f"{len(product)} product -- the partition is not exercising")
        assert len(tests) + len(scripts) + len(product) == len(changed)

    def test_a_session_hook_is_never_reachable_by_a_run(self, mod):
        index = mod._index()
        imported = mod._closure([mod.ENTRY.resolve()], index)
        full = mod._rel(mod._closure(
            list(imported) + list(mod._spawned(imported, index)), index))
        for hook in ("hooks/work_not_narrate.py", "hooks/cy_monitor_gate.py"):
            assert hook not in full, (
                f"{hook} is on a run's path, which would mean a session hook "
                f"runs inside an experiment")
