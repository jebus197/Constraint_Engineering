"""Both fingerprint loaders must honour the run's declared scope.

HIS RULING, 2026-10-16: "The fingerprints should be recomputed in the
first/blind run of any experiment anyway. So they should be reset after the next
live experiment runs."

THE DEFECT, measured 2026-10-16 by execution. Two loaders read
`bench/fingerprints/` inside one run:

  reference_runner_v3._load_fingerprints(scope)   honours the scope; under
      "experiment" it returns an EMPTY mapping and clears its own snapshot, so
      the run re-measures its seats in the blind round.
  run_exp17_immune._load_fingerprint_cache()      took NO scope. With the main
      path returning 0 records it returned 11.

The second is called from the decomposition futility guard, and the value it
hands out -- `max_successful_prompt_chars` times 0.9 -- is the ceiling that
decides whether a payload is SPLIT. So a run that believed it was measuring its
seats afresh was splitting payloads on a prior experiment's numbers, and 4 of the
5 paid seats shared the identical 465,206. The reset was total on the observation
path and bypassed on the splitting decision.

EVERY ASSERTION CALLS BOTH LOADERS. The defect was invisible to reading, because
each function was individually correct and consistent with its own docstring; it
was only visible by calling them in the same process under the same scope, which
is what `execute-do-not-grep` exists to force.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


@pytest.fixture()
def mods():
    from bench import reference_runner_v3 as runner
    from bench import run_exp17_immune as immune
    before = immune.fingerprint_scope()
    yield runner, immune
    immune.set_fingerprint_scope(before)      # never leak scope between tests


def test_the_persisting_scope_loads_records_at_all(mods):
    """Anti-vacuity: if nothing is on disk, agreement is meaningless."""
    runner, immune = mods
    immune.set_fingerprint_scope("persist")
    assert len(runner._load_fingerprints("persist")) > 0, (
        "no fingerprints on disk, so every assertion below would pass trivially")
    assert len(immune._load_fingerprint_cache()) > 0


def test_both_loaders_are_empty_under_experiment_scope(mods):
    runner, immune = mods
    immune.set_fingerprint_scope("experiment")
    main = runner._load_fingerprints("experiment")
    guard = immune._load_fingerprint_cache()
    assert main == {}, "the main observation path must return nothing"
    assert guard == {}, (
        "the decomposition guard's loader returned "
        f"{len(guard)} records under experiment scope. That is the partial reset: "
        "the run re-measures its seats while the SPLITTING decision still reads a "
        "prior experiment's capacities off disk.")


def test_both_loaders_agree_under_both_scopes(mods):
    runner, immune = mods
    for scope in ("persist", "experiment"):
        immune.set_fingerprint_scope(scope)
        main = len(runner._load_fingerprints(scope))
        guard = len(immune._load_fingerprint_cache())
        assert (main == 0) == (guard == 0), (
            f"under scope {scope!r} the main path has {main} records and the "
            f"decomposition guard has {guard}. One scope, 2 answers.")


def test_the_setter_drops_a_cache_already_populated(mods):
    """A setter that leaves a stale cache does nothing on its second call."""
    runner, immune = mods
    immune.set_fingerprint_scope("persist")
    assert len(immune._load_fingerprint_cache()) > 0      # populate it
    immune.set_fingerprint_scope("experiment")
    assert immune._load_fingerprint_cache() == {}, (
        "switching to experiment scope must drop observations already cached, "
        "or the first load of a process decides the whole run")


def test_the_setter_actually_drops_the_cache_object(mods):
    """The setter's contract, asserted DIRECTLY rather than through a loader.

    FOUND BY MUTATION on 2026-10-17: removing the invalidation from the setter
    left the suite green, because the experiment-scope check sits BEFORE the
    cache check and masks a stale cache in that direction. The direction it does
    NOT mask is persist -> persist, where a cache populated earlier in the
    process is returned unconditionally however the disk has changed since. So
    the contract has to be checked on the cache object itself.
    """
    _, immune = mods
    immune.set_fingerprint_scope("persist")
    assert immune._load_fingerprint_cache(), "populate the cache first"
    assert immune._fp_cache is not None, "the cache should now hold observations"
    immune.set_fingerprint_scope("persist")        # same scope, set again
    assert immune._fp_cache is None, (
        "set_fingerprint_scope must drop the cached observations. Without that, "
        "the first load of a process decides the whole run and a later change on "
        "disk is never seen.")


def test_the_scope_is_reportable_rather_than_assumed(mods):
    _, immune = mods
    immune.set_fingerprint_scope("experiment")
    assert immune.fingerprint_scope() == "experiment"
    immune.set_fingerprint_scope("persist")
    assert immune.fingerprint_scope() == "persist"


def test_an_empty_scope_falls_back_to_persisting(mods):
    """A missing scope must not silently become `experiment` and wipe the
    observations a live run depends on."""
    _, immune = mods
    immune.set_fingerprint_scope("")
    assert immune.fingerprint_scope() == "persist"
    assert len(immune._load_fingerprint_cache()) > 0


def test_the_runner_declares_the_scope_for_both_loaders(mods):
    runner, _ = mods
    assert hasattr(runner, "set_fingerprint_scope"), (
        "the runner must declare the scope once for both loaders; importing only "
        "the loader is how the 2 answers diverged")
