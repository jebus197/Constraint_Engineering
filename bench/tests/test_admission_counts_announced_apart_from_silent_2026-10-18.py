#!/usr/bin/env python3
"""An ANNOUNCED default is not a SILENT one, and the instrument must tell them apart.

HIS QUESTION, behind entry B13: whether admitting a model is trivial, and what the
cost of getting it wrong is. The producer
`scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py` answers it, and
its own conclusion is that *"the real problem is not the count, it is the failure
mode ... making admission trivial therefore means making the misses LOUD first."*

THE DEFECT, MEASURED 2026-10-18. Entry C18 then made 3 of those lookups loud --
they still return the default, because raising would turn a degradation into a
dead run, but every fallback is now recorded against the model's stable identity.
The producer's count did not move. Each lookup had been RE-IMPLEMENTED inside the
producer as a bare dictionary `get`, so the instrument measured the TABLE's shape
rather than the live code path: 2 forms of one lookup, each individually correct,
disagreeing about what happens. That is the `execute-do-not-grep` defect in the
script that measures it.

AFTER THE REPAIR the lambdas call the live resolver and read its ledger, and the
silent count falls from 9 of 10 to 6 of 10 with 3 reported as ANNOUNCED DEFAULT.

WHAT THIS FILE GUARDS. Not the number -- the number may move again, and should,
as more lookups are made loud. It guards that the DISTINCTION exists, that the
producer reads the LIVE ledger rather than a re-implementation, and that an
announced default is never counted as silent.
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import routing as R  # noqa: E402

PRODUCER = (REPO / "scripts"
            / "how_many_places_must_change_to_add_a_model_2026-10-16.py")


def _load():
    spec = importlib.util.spec_from_file_location("admission_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_live_resolver_records_a_fallback_so_the_ledger_can_be_read():
    """The mechanism the producer now depends on, exercised directly."""
    R.reset_lookup_misses()
    got = R.resolve_or_alarm({"known": 1}, "a-new-model", "some table", default=0)
    assert got == 0, "the default must still be returned; behaviour is unchanged"
    assert len(R.lookup_misses()) == 1, (
        "the fallback was not recorded, so no instrument could tell an announced "
        "default from a silent one")


def test_a_present_key_records_nothing_so_a_hit_is_not_counted_as_a_miss():
    R.reset_lookup_misses()
    R.resolve_or_alarm({"known": 1}, "known", "some table", default=0)
    assert R.lookup_misses() == []


def test_the_producer_distinguishes_announced_from_silent():
    mod = _load()
    res = mod.method_b(["Kimi"]) if hasattr(mod, "method_b") else None
    if res is None:
        pytest.skip("the producer's shape has moved; re-derive this check")
    outcomes = [s["outcome"] for s in res["steps"]]
    assert "ANNOUNCED DEFAULT" in outcomes, (
        "no step reports ANNOUNCED DEFAULT, so entry C18's 3 loud lookups are "
        "still being counted as silent and the instrument cannot see the repair")
    assert "SILENT DEFAULT" in outcomes, (
        "every step reports as announced, which would mean the distinction has "
        "collapsed the other way and the instrument has stopped discriminating")
    # An announced default must NOT be inside the silent tally.
    silent = res["silent"]
    announced = sum(1 for o in outcomes if o == "ANNOUNCED DEFAULT")
    assert announced >= 1
    assert silent == sum(1 for o in outcomes
                         if o in ("SILENT DEFAULT", "SILENT DEGRADE")), (
        f"the silent tally ({silent}) does not equal the silent outcomes; an "
        f"announced default is being counted as silent")


def test_the_producer_calls_the_live_resolver_and_does_not_reimplement_it():
    """STRUCTURAL: the defect was a re-implementation, so the shape is pinned.

    Each lookup C18 made loud must appear inside a `resolve_or_alarm` call in the
    producer. A bare `.get` on one of those tables would mean the instrument has
    drifted back to measuring the table rather than the path.
    """
    tree = ast.parse(PRODUCER.read_text(errors="ignore"))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "resolve_or_alarm"]
    assert len(calls) >= 3, (
        f"the producer makes only {len(calls)} live-resolver call(s); the 3 "
        f"lookups C18 made loud must each go through it, or the count it prints "
        f"is about the tables and not about the code that runs")

    # and no bare .get with a default on those same tables
    guarded = {"COMPOSER_MODEL_MAP", "MODEL_COHERENCE_BUDGETS",
               "PHENOTYPE_TRANSFORMS"}
    bare = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and len(n.args) >= 2):
            v = n.func.value
            name = (v.attr if isinstance(v, ast.Attribute)
                    else v.id if isinstance(v, ast.Name) else "")
            if name in guarded:
                bare.append((name, n.lineno))
    assert bare == [], (
        f"the producer still reads {bare} with a bare get and a default, so it "
        f"would report an announced default as silent")
