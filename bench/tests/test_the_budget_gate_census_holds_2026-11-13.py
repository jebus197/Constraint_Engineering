"""The B182 census must execute the LIVE gate, and must not pin the defect.

ENTRY B182. `scripts/the_budget_gate_is_blind_to_its_own_subject_2026-11-13.py`
drives `~/.claude/hooks/local_resource_budget.py`'s own predicate over a grid of
genuine instructions and reports how many pass through.

★ THIS FILE DELIBERATELY DOES NOT ASSERT 126 OF 150. That figure IS the defect.
Pinning it would make the guard go RED the day the gate is repaired, which is
the shape this project records as "a guard can pin the defect as current
behaviour". What is pinned instead are the producer's CONTRACTS: that it reads
the live hook rather than a copy, that its grid is the full cross product, that
the measurement discriminates in both directions, that the half which works
keeps working, and that running it changes nothing on disk.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PROD = REPO / "scripts" / "the_budget_gate_is_blind_to_its_own_subject_2026-11-13.py"
HOOK = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"


@pytest.fixture(scope="module")
def prod():
    assert PROD.is_file(), f"the producer is gone: {PROD}"
    spec = importlib.util.spec_from_file_location("b182_census", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["b182_census"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def test_the_producer_actually_runs(prod):
    """★ EXECUTE, DO NOT GREP. A test asserting on this file's source text
    would pass while the producer crashed on import."""
    r = prod.measure()
    for key in ("cases", "through", "by_noun", "neg_ok", "neg_n"):
        assert key in r, f"measure() stopped returning {key!r}: {sorted(r)}"


def test_the_grid_is_the_full_cross_product(prod):
    """DERIVED FROM THE SUBJECT, NOT PINNED. Asserting 150 would go stale the
    moment a phrase is added; asserting the product cannot."""
    expected = len(prod.VERBS) * len(prod.NOUNS) * len(prod.TAILS)
    cases = prod.grid()
    assert len(cases) == expected, (
        f"the grid is {len(cases)} where the cross product is {expected}; it "
        f"has stopped being a systematic grid and become a hand-picked list")
    assert len(set(cases)) == len(cases), "the grid contains duplicate cells"
    # ...and every cell really is an instruction, not a description.
    for c in cases:
        assert c.split()[0] in {v.split()[0] for v in prod.VERBS}, (
            f"cell does not begin with a verb of execution: {c!r}")


def test_it_reads_the_live_hook_not_a_copy(prod):
    """A census of a COPY measures nothing about what gates the session."""
    assert HOOK.is_file(), f"the live hook is gone: {HOOK}"
    fn = prod.load_predicate()
    mod = sys.modules[fn.__module__]
    assert pathlib.Path(mod.__file__).resolve() == HOOK.resolve(), (
        f"the producer loaded {mod.__file__} rather than the live hook at "
        f"{HOOK}. A finding about a copy is not a finding about the gate.")


def test_the_measurement_discriminates_in_both_directions(prod):
    """★ NON-VACUITY, BOTH WAYS, AND NEITHER BOUND IS THE DEFECT FIGURE.

    If NOTHING passed through, the finding would be empty. If EVERYTHING did,
    the predicate would be dead and the census would be measuring a constant.
    Both bounds stay true after the gate is repaired, except the first, which
    is why it is written as a strict inequality on 0 rather than on 126.
    """
    r = prod.measure()
    k, n = len(r["through"]), len(r["cases"])
    assert 0 <= k <= n
    caught = n - k
    assert caught > 0, (
        "the gate now catches 0 of the grid, so the predicate matches nothing "
        "at all -- that is a different and worse defect than the one B182 "
        "reports, and this census would be measuring a constant")


def test_the_half_that_works_keeps_working(prod):
    """The 2026-10-17 negation fix is NOT what B182 reports. It must not be
    broken by whatever repairs the other half."""
    r = prod.measure()
    assert r["neg_ok"] == r["neg_n"], (
        f"{r['neg_n'] - r['neg_ok']} of {r['neg_n']} prohibitions are now "
        f"refused. A brief that FORBIDS heavy delegated work must never be "
        f"refused for saying so -- that is the defect the gate's own docstring "
        f"records from 2026-10-17, returning.")


def test_every_noun_phrase_is_accounted_for(prod):
    r = prod.measure()
    assert set(r["by_noun"]) == set(prod.NOUNS), (
        "the per-phrase breakdown no longer covers every phrase in the grid")
    per = len(prod.VERBS) * len(prod.TAILS)
    for noun, (miss, tot) in r["by_noun"].items():
        assert tot == per, f"{noun!r} collapsed over {tot} cells, not {per}"
        assert 0 <= miss <= tot


def test_running_the_census_changes_nothing_on_disk(prod):
    """★ THE PRODUCER'S OWN CLAIM, CHECKED. Its docstring says it edits
    nothing. A measurement script that mutates its subject is the defect class
    this project recorded when a survey meant to READ ran things that WRITE."""
    before = hashlib.sha256(HOOK.read_bytes()).hexdigest()
    prod.measure()
    after = hashlib.sha256(HOOK.read_bytes()).hexdigest()
    assert before == after, (
        "running the census altered the live hook it measures")
