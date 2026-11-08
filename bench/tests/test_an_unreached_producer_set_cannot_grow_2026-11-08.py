"""A producer that nothing runs may not be ADDED, whatever date it carries.

HIS INSTRUCTION, 2026-11-08, was to extend the reached-producers rule to today's
date. Surveying the tree first showed why that alone is not the fix: 247 of 557
dated producers were reached by nothing, spread over 37 of 46 dates, so a 3rd
dated guard would close 18 and leave 229. This file is the date-independent half.

IT PINS A SET, NOT A COUNT, and that distinction is a recorded defect of mine
rather than a style choice. A count ratchet ("no more than 247 unreached")
is satisfied by deleting one unreached producer and adding another, because the
total never moves -- so the new debt is invisible at a constant total. The pin
is therefore the SET of names, held at
``experimental_notes/data/unreached_producers_2026-11-08.json``, OUTSIDE both
``scripts/`` and ``bench/tests/``, because a pin that lives inside what it
measures moves when its subject moves.

MEMBERSHIP IS A DEBT ADMITTED, NOT A PERMISSION. The set may SHRINK freely --
paying a debt must never fail a board -- and a name that is unreached and NOT in
the set is refused. That asymmetry is the whole mechanism.

THE PREDICATE IS IMPORTED, NEVER REIMPLEMENTED. ``survey`` lives in
``scripts/the_unreached_producer_debt_is_not_todays_2026-11-08.py`` and is called
here, so the pin and the measurement cannot drift into 2 definitions of
"reached" that are each individually correct -- the shape that let a producer and
a consumer disagree 4 times in this project's record.

THE HONEST LIMIT OF THIS HALF, stated because it is the reason the fix is
composed. ``survey``'s reached predicate is TEXTUAL: it asks whether a
producer's filename appears in any file under ``bench/tests/``. It cannot tell a
producer that is EXECUTED from one that is merely mentioned, so a producer that
stops working keeps its mention and passes here. The dated sibling
``test_tonights_producers_are_reached_2026-11-08.py`` is what actually runs them.
Neither half subsumes the other, and the dominance is measured by
``scripts/the_composed_producer_fix_dominates_either_part_2026-11-08.py``.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PIN = REPO / "experimental_notes/data/unreached_producers_2026-11-08.json"
SURVEYOR = REPO / "scripts/the_unreached_producer_debt_is_not_todays_2026-11-08.py"


def _surveyor():
    spec = importlib.util.spec_from_file_location("_cdsfl_surveyor", SURVEYOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pinned() -> set[str]:
    """The SET of unreached producers this tree has admitted to."""
    return set(json.loads(PIN.read_text())["unreached"])


def unreached_now(repo: pathlib.Path = REPO) -> set[str]:
    """The SET of dated producers no test under bench/tests names, right now."""
    _reached, unreached, _by_date = _surveyor().survey(repo)
    return set(unreached)


def verdict(now: set[str], pin: set[str]) -> tuple[set[str], set[str]]:
    """(newly unreached, debts discharged). THE DECISION, as a callable.

    Exposed so the composition measurement can EXECUTE this rule rather than
    assert about its source text. A non-empty first element is a refusal.
    """
    return (set(now) - set(pin), set(pin) - set(now))


def test_the_pin_exists_and_names_its_predicate():
    assert PIN.is_file(), f"the pinned set is missing: {PIN}"
    doc = json.loads(PIN.read_text())
    assert doc["unreached"], "the pin is empty, so it constrains nothing"
    assert "survey" in doc["_predicate"], (
        "the pin does not name the predicate that produced it, so a reader "
        "cannot tell what 'unreached' meant when it was written")
    assert doc["_pinned_at_commit"], "the pin names no commit"


def test_no_producer_is_unreached_outside_the_pin():
    """THE RATCHET. A producer nothing runs may not be added.

    This is the addition-nothing-reaches half of the additive standard, which
    this project has confirmed 11 times against 0 confirmed removals of
    something needed.
    """
    if not SURVEYOR.is_file():
        pytest.skip("the surveyor is not in this checkout")
    new, _discharged = verdict(unreached_now(), pinned())
    assert not new, (
        f"{len(new)} producer(s) are reached by NO test and are not in the "
        f"admitted set: {sorted(new)}\n"
        f"Either have a test execute them, or -- if one is deliberately "
        f"exempt -- say so beside the exemption, as the dated guards do. "
        f"Re-pinning to silence this is how a ratchet becomes a rubber stamp.")


def test_paying_a_debt_never_fails_the_board():
    """The set may SHRINK freely. A guard that punishes progress gets removed."""
    pin = pinned()
    shrunk = set(sorted(pin)[1:]) if len(pin) > 1 else set()
    new, discharged = verdict(shrunk, pin)
    assert not new, "shrinking the unreached set must not be a refusal"
    assert discharged, "a discharged debt must be reported as discharged"


def test_a_swap_at_a_constant_total_is_refused():
    """ANTI-VACUITY, and the reason this is a SET and not a COUNT.

    EXECUTED against the real decision function, not asserted about its text. A
    count ratchet passes this case, which is exactly why a count was rejected:
    one debt is discharged and one is created, the total is unchanged, and the
    new debt is invisible.
    """
    pin = pinned()
    assert len(pin) >= 2, "this case needs at least 2 pinned names"
    ordered = sorted(pin)
    swapped = set(ordered[1:]) | {"a_producer_that_nothing_runs_2099-01-01.py"}
    assert len(swapped) == len(pin), (
        "the synthetic swap must hold the TOTAL constant, or it tests nothing "
        "a count ratchet would not also catch")
    new, discharged = verdict(swapped, pin)
    assert new == {"a_producer_that_nothing_runs_2099-01-01.py"}, (
        "a swap at a constant total was NOT refused, so this is a count "
        "ratchet wearing a set's name")
    assert discharged == {ordered[0]}


def test_the_pin_is_not_padded_with_names_that_do_not_exist():
    """A pin listing files that are absent would admit debts freely.

    Deletion is legitimate progress, so absence is REPORTED rather than
    refused -- but a pin where most names are absent has stopped describing
    this tree and must be re-derived.
    """
    pin = pinned()
    on_disk = {p.name for p in (REPO / "scripts").glob("*.py")}
    absent = pin - on_disk
    assert len(absent) < len(pin) / 2, (
        f"{len(absent)} of {len(pin)} pinned names are not on disk, so the pin "
        f"no longer describes this tree; re-derive it from the surveyor")


def test_todays_producers_are_no_longer_in_the_debt():
    """His instruction, checked as an outcome rather than as an intention.

    The dated sibling lists 2026-11-08's producers, so the textual predicate
    now finds them. If this fails, that guard was written and the debt it was
    meant to pay is still outstanding.
    """
    if not SURVEYOR.is_file():
        pytest.skip("the surveyor is not in this checkout")
    today = {n for n in unreached_now() if "2026-11-08" in n}
    assert not today, (
        f"{len(today)} producer(s) dated 2026-11-08 are still reached by "
        f"nothing: {sorted(today)}")

def test_the_survey_actually_sees_this_tree():
    """ANTI-VACUITY, and it closes a hole found by this file's own P-pass.

    Every other test here routes through ``verdict``, which is pure. If
    ``unreached_now`` returned an EMPTY set -- a broken glob, a wrong repo root,
    an exception swallowed into a default -- the ratchet would pass for the
    wrong reason and nothing above would notice. A verification that passes
    because it measured nothing is this project's most expensive recurring
    defect, so the survey is required to actually see a tree.

    These are FLOORS, deliberately, not exact pins. The producer count only
    grows, and an exact pin on a growing quantity fails on the next commit and
    teaches the next reader to re-pin rather than to look -- which is how 3
    figures in the instruction files drifted twice in 6 days.
    """
    if not SURVEYOR.is_file():
        pytest.skip("the surveyor is not in this checkout")
    reached, unreached, by_date = _surveyor().survey(REPO)
    total = len(reached) + len(unreached)
    assert total >= 400, (
        f"the survey saw only {total} dated producers; it is not looking at "
        f"this tree, so every verdict here is vacuous")
    assert len(reached) >= 200, (
        f"the survey found only {len(reached)} producers reached by anything; "
        f"the reached predicate has stopped matching")
    assert len(by_date) >= 30, (
        f"the survey saw only {len(by_date)} distinct dates")
