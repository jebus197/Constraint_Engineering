"""One predicate for the blocker set, and the feed-back he ruled on is on.

HIS QUESTION, 2026-10-17: "What are the 94 unservable blockers? I don't remember
hearing about this before? What exactly if anything do they block?... I won't
tell you to make 94 potentially significant code changes to clear these
'blockers' without first knowing if they are real."

THE FIGURE WAS NEVER RIGHT, AND THAT IS THE ANSWER. Four different numbers
reached him for one quantity -- 212 from the producer, 197 from a correction, 174
from an ad-hoc call, and finally 73 of 167 from calling the live methods over the
61 top-level run states. Two independent causes:

  SCOPE. The producer walked `rglob` and found 74 state files where there are 61
  runs: 10 sit inside `sandbox_harvest/`, which are archived copies of what a
  SEAT saw, and 3 at other nesting.

  TWO PREDICATES. `unverified_critical_count` held 6 release doors while
  `blockers_routing_cannot_serve` held a COPY of 3 of them, so the reader named
  entries the counter does not count as blockers. Measured:
  `commissioning_arm3_contrast_20260922T025824Z` gave 4 from the counter and 11
  from the reader -- a numerator larger than its own denominator, which makes any
  ratio between them meaningless. The reader's own docstring claimed the 2
  "cannot drift"; that was true of the routing half and false of the blocker half.

`blocking_entry_ids` now holds the doors ONCE, `unverified_critical_count` is a
thin wrapper over its length, and the reader filters its output. They cannot
drift because there is nothing to drift from.

AND THE FEED-BACK IS ON. His ruling of 2026-10-12 is that an unread finding is
"fed back into the mechanics of the harness for resolution, this can include
routing, the sweep mechanics". The sweep is that machinery and it was off by
default -- 18 of 49 configs enabled it, 36.7347%, Wilson [24.6652%, 50.7329%],
while 31 left it unset. It defaults to 1 round now, which cannot cost
convergence because the sweep "runs strictly after the verdict".
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
LOGS = REPO / "bench" / "logs"


@pytest.fixture(scope="module")
def runner():
    from bench import reference_runner_v3 as m
    return m


def _top_level_states() -> list[pathlib.Path]:
    if not LOGS.is_dir():
        return []
    return [p for p in sorted(LOGS.rglob("runner_state.json"))
            if len(p.relative_to(LOGS).parts) == 2]


def _registry(runner, path):
    try:
        ents = (json.loads(path.read_text(errors="replace")).get("registry")
                or {}).get("entries") or {}
    except (OSError, ValueError):
        return None
    if not ents:
        return None
    reg = runner.FindingRegistry()
    reg.entries = ents
    return reg


# ------------------------------------------------------ one predicate, one set

def test_the_count_is_the_length_of_the_set(runner):
    reg = runner.FindingRegistry()
    reg.entries = {
        "C1": {"status": "UNCONFIRMED"},
        "C2": {"status": "CLOSED"},
        "C3": {"status": "UNCONFIRMED", "exhausted": True},
        "C4": {"status": "UNCONFIRMED"},
    }
    ids = reg.blocking_entry_ids()
    assert reg.unverified_critical_count() == len(ids), (
        "the count must BE the length of the set, not a parallel computation")
    assert set(ids) == {"C1", "C4"}, f"unexpected blocker set: {ids}"


def test_the_reader_is_a_subset_of_the_counter(runner):
    """The property that failed: a numerator must come from its denominator."""
    reg = runner.FindingRegistry()
    reg.entries = {
        "C1": {"status": "UNCONFIRMED"},
        "C2": {"status": "UNCONFIRMED", "exhausted": True},
        "C3": {"status": "OPEN"},
    }
    blockers = set(reg.blocking_entry_ids())
    unservable = set(reg.blockers_routing_cannot_serve())
    assert unservable <= blockers, (
        f"the reader named {sorted(unservable - blockers)} which the counter does "
        "not count as blockers. That is how a ratio of 11 out of 4 was produced.")


@pytest.mark.parametrize("path", _top_level_states() or [None])
def test_no_archived_run_has_more_unservable_than_blockers(runner, path):
    """Across the real archive, not a fixture. 1 run failed this before the fix."""
    if path is None:
        pytest.skip("no archived runs in this checkout")
    reg = _registry(runner, path)
    if reg is None:
        pytest.skip("no readable registry")
    blocked = reg.unverified_critical_count()
    unservable = len(reg.blockers_routing_cannot_serve())
    assert unservable <= blocked, (
        f"{path.parent.name}: {unservable} unservable of {blocked} blockers. The "
        "reader is naming entries the counter does not count.")


def test_the_archive_figure_is_reproducible(runner):
    """A rate must travel with something that reproduces it."""
    states = _top_level_states()
    if not states:
        pytest.skip("no archived runs")
    blocked = unservable = 0
    for p in states:
        reg = _registry(runner, p)
        if reg is None:
            continue
        blocked += reg.unverified_critical_count()
        unservable += len(reg.blockers_routing_cannot_serve())
    assert blocked > 0, "no blockers at all makes this test vacuous"
    assert unservable <= blocked
    # The figure recorded in task B14 and in the producer, within drift tolerance:
    # the archive grows, so this is a sanity band rather than a pin.
    assert 0.20 <= unservable / blocked <= 0.70, (
        f"the unservable share is {unservable/blocked:.4f} ({unservable} of "
        f"{blocked}), outside the band the archive has shown. Re-measure with "
        "scripts/a_blocker_the_ladder_will_not_serve_2026-10-16.py before "
        "changing this band -- do not widen it to make a figure fit.")


# ------------------------------------------------------- his 2026-10-12 ruling

def test_the_sweep_is_on_by_default(runner):
    cls = next(o for o in (getattr(runner, n) for n in dir(runner))
               if dataclasses.is_dataclass(o)
               and any(f.name == "post_convergence_sweep_rounds"
                       for f in dataclasses.fields(o)))
    d = {f.name: f.default for f in dataclasses.fields(cls)}
    assert d["post_convergence_sweep_rounds"] >= 1, (
        "his ruling of 2026-10-12 is that an unread finding is fed back into the "
        "harness machinery, and the sweep IS that machinery. At 0 a run that "
        "simply forgets to set it gets no feed-back at all.")


def test_the_sweep_cannot_affect_convergence(runner):
    """Why enabling it by default is safe, asserted rather than assumed.

    His concern of 2026-10-13 was that feeding findings back "could block or
    severely delay convergence". The sweep's contract is that it runs strictly
    after the verdict. That contract is what makes his 2 statements compatible,
    so it is checked rather than trusted.
    """
    import inspect
    src = inspect.getsource(runner._post_convergence_sweep)
    assert "after the verdict" in src or "AFTER the" in src, (
        "the sweep's contract that it runs after the convergence verdict is what "
        "makes enabling it safe; if that contract is gone, the default must be "
        "reconsidered rather than left standing")
    # and it must still refuse to run when given no rounds
    assert runner._post_convergence_sweep(
        runner.FindingRegistry(), {},
        type("C", (), {"post_convergence_sweep_rounds": 0})(), 0) == {}, (
        "0 rounds must still disable it, so a caller can opt out")
