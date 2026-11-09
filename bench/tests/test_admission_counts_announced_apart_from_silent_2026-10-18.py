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
    #: ★ THIS ASSERTION REQUIRED A LIVE DEFECT, AND IS REPLACED, 2026-10-29.
    #: It read `assert "SILENT DEFAULT" in outcomes`, whose stated purpose was to
    #: catch the distinction collapsing the other way. But it can only hold while
    #: a silent lookup still EXISTS in the tree, so it conflates "the instrument
    #: stopped discriminating" with "the defect was fixed" -- and this file's own
    #: docstring says the opposite: *"Not the number -- the number may move
    #: again, and should, as more lookups are made loud."*
    #:
    #: IT FIRED ON SUCCESS. On 2026-10-29 the last silent TABLE lookup was routed
    #: through the recording resolver and the admission count fell from 5 of 10
    #: to 1 of 10, leaving only a SILENT DEGRADE, which is not a table lookup at
    #: all. The commit was refused by a guard celebrating its own obsolescence.
    #:
    #: THE DISTINCTION IS NOW TESTED DIRECTLY, by
    #: `test_the_discriminator_still_tells_a_recorded_miss_from_an_unrecorded_one`
    #: below: a synthetic absent-key lookup through `resolve_or_alarm` records,
    #: and a bare `.get` on the same synthetic table does not. That is the exact
    #: predicate `record()` uses -- `announced = bool(_rt.lookup_misses())` -- so
    #: it tests the discriminator rather than the tree's current contents, and
    #: it keeps working however many lookups are made loud.
    #: ★★ IT FIRED ON SUCCESS A SECOND TIME, 2026-11-09, AND IS NOW OFF THE
    #: TREE ENTIRELY. The note above records the 2026-10-29 case, where the
    #: count fell from 5 of 10 to 1 of 10 and `assert "SILENT DEFAULT" in
    #: outcomes` refused the commit that earned it. The repair WIDENED the
    #: pattern to accept either silent label, which kept the identical
    #: property: it can only hold while a silent lookup STILL EXISTS IN THE
    #: TREE. On 2026-11-09 the last one -- the composer-fallback SILENT
    #: DEGRADE -- was made loud, the count fell to 0 of 10, and this line
    #: refused a 26-minute board for the second time in 11 days. Widening a
    #: pattern that should not have been looking at the tree is the treadmill
    #: shape, and this is what it costs.
    #:
    #: WHAT THE ASSERTION WAS FOR, KEPT, AND MOVED TO A SUBJECT THAT CANNOT
    #: GO AWAY. The intent is that the SILENT vocabulary stays REACHABLE, so a
    #: future silent lookup is reported as silent rather than mislabelled or
    #: dropped. That is a property of the CLASSIFIER, not of today's tree, and
    #: the producer exposes it: `counts` is keyed by its whole declared
    #: vocabulary and `silent` is the sum of both silent keys. So the checks
    #: below hold at 0 silent steps and at 10, which is the anti-staleness
    #: property this file's own docstring asks for -- *"the number may move
    #: again, and should, as more lookups are made loud."*
    #:
    #: THE 3RD CHECK IS THE ONE WITH A RECORDED DEFECT BEHIND IT: the producer
    #: once tallied 4 categories while emitting a 5th, so 1 of 10 steps was
    #: printed and never counted. Asserting the sum rather than the presence
    #: catches that, and it is strictly more than the old line could see.
    counts = res["counts"]
    assert {"SILENT DEFAULT", "SILENT DEGRADE"} <= set(counts), (
        f"the producer's outcome vocabulary has lost a silent label; it now "
        f"carries {sorted(counts)}. A silent lookup would be reported as "
        f"something else, or as unknown, and the distinction this file exists "
        f"to protect would be gone")
    assert sum(counts.values()) == res["step_total"], (
        f"the outcome partition does not close: {sum(counts.values())} counted "
        f"against {res['step_total']} steps, so some step's outcome is "
        f"uncounted")

    #: ★ THE TALLY IS EXERCISED ON CONSTRUCTED INPUT, BECAUSE THE LIVE RESULT
    #: CANNOT TEST IT. A first version of these checks asserted
    #: `res["silent"] == counts["SILENT DEFAULT"] + counts["SILENT DEGRADE"]`
    #: against the live result and was VACUOUS: with every silent count now 0,
    #: dropping either term changes nothing, and the mutation that removed one
    #: came back GREEN. A property only observable when a count is non-zero has
    #: to be put a non-zero input, so `tally` was extracted from `method_b` --
    #: 1 definition, 2 callers -- and is called here with synthetic steps.
    #: These hold whether the tree has 0 silent lookups or 10.
    assert mod.tally([{"outcome": "SILENT DEGRADE"}])["silent"] == 1, (
        "a SILENT DEGRADE step is not counted as silent, which is exactly the "
        "defect that once printed 1 of 10 steps without tallying it")
    assert mod.tally([{"outcome": "SILENT DEFAULT"}])["silent"] == 1, (
        "a SILENT DEFAULT step is not counted as silent")
    assert mod.tally([{"outcome": "SILENT DEFAULT"},
                      {"outcome": "SILENT DEGRADE"}])["silent"] == 2, (
        "the silent tally is not the SUM of both labels, so one of them is "
        "being dropped")
    assert mod.tally([{"outcome": "PASS"},
                      {"outcome": "ANNOUNCED DEFAULT"}])["silent"] == 0, (
        "a loud outcome is being counted as silent, which would make the "
        "headline figure unfalsifiable in the flattering direction")
    #: AND THE REFUSAL MUST NAME THE OFFENDER, not merely happen. A reversion
    #: that disabled the unknown-outcome check came back GREEN against a bare
    #: `pytest.raises(AssertionError)`, because the partition check then fired
    #: instead and the test could not tell the 2 apart. Matching the message
    #: makes it discriminate. (The partition check is provably redundant given
    #: the unknown check -- any outcome inside the vocabulary makes the counts
    #: sum to the step total by construction -- so it is kept as a cheap
    #: belt-and-braces assert and is NOT separately mutation-testable.)
    with pytest.raises(AssertionError, match="uncounted outcome"):
        mod.tally([{"outcome": "QUIET"}])
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

def test_the_discriminator_still_tells_a_recorded_miss_from_an_unrecorded_one():
    """THE DISTINCTION ITSELF, independent of what the live tree contains.

    `record()` classifies a step by exactly one predicate:
    `announced = bool(_rt.lookup_misses())`. So the question "can the instrument
    still tell an announced default from a silent one?" reduces to "does the
    ledger record a resolved miss and not record a bare one?", on a SYNTHETIC
    table that no repair can remove.

    This replaces an assertion that required a live silent lookup to exist. That
    one answered the same question only while the defect it measured survived,
    and it refused a commit on 2026-10-29 for the sole reason that the defect
    had been fixed.
    """
    table = {"present": 1}
    absent = "AbsentKeyForDiscriminationTest"

    # the ANNOUNCED path: an absent key through the resolver RECORDS
    R.reset_lookup_misses()
    got_resolved = R.resolve_or_alarm(table, absent, "a synthetic table", default=0)
    recorded = list(R.lookup_misses())
    assert got_resolved == 0, "the resolver stopped returning the default"
    assert len(recorded) == 1, (
        "an absent key through the resolver recorded nothing, so every step "
        "would now classify as SILENT and the instrument has stopped "
        "discriminating")

    # the SILENT path: the same absent key by a bare get RECORDS NOTHING
    R.reset_lookup_misses()
    got_bare = table.get(absent, 0)
    assert got_bare == 0
    assert R.lookup_misses() == [], (
        "a bare dict get recorded a miss, which would make every step classify "
        "as ANNOUNCED and the distinction would be vacuous")

    # and a PRESENT key records nothing either way, so a hit is never a miss
    R.reset_lookup_misses()
    assert R.resolve_or_alarm(table, "present", "a synthetic table", default=0) == 1
    assert R.lookup_misses() == []

