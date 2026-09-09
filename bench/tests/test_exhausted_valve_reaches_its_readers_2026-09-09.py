"""The `exhausted` valve must survive a round tick for every status that reads it.

FOUND by cc2 in panel review 2026-09-09, extended by 1 status on verification,
and confirmed here by execution before the fix was applied.

The valve was added 2026-09-07 so that an unresolvable critical "cannot block for
ever". `_update_finding_statuses` set it only for OPEN, CONTESTED, CORROBORATED
and WITHHELD, and did `e.pop("exhausted", None)` for everything else. But 2
functions READ it, and between them they examine 6 statuses:

  open_crit_high_count        OPEN, CONTESTED, REOPENED, CORROBORATED, WITHHELD
  unverified_critical_count   UNCONFIRMED

So the flag was stripped from UNCONFIRMED -- the ONLY status the A4 counter looks
at -- and from REOPENED, by one ordinary round tick. Both readers' guards were
unreachable for part of their own population. cc2 found the UNCONFIRMED half;
the REOPENED half turned up on verification, which is why the fix derives the
population from the readers rather than adding a status by hand.

ITS ONLY TEST WAS A SOURCE GREP. `test_panel_five_fixes_2026-09-07.py:78`
asserted that the string `e.get("exhausted")` appears in the counter's body --
that the LINE EXISTS. It passed against dead code, which is exactly the
`execute-do-not-grep` ruling, inside the guard for this very valve. This file
replaces that assertion with execution; the grep is left in place because
asserting the line exists is still true and still cheap, and removing a guard to
replace it is not how this project adds one.

WHY IT BECAME LOAD-BEARING. The empty-ladder repair of the same day makes
`routing_deferred` the terminal state of every escalated critical in a 1-seat
arm, and `routing_deferred` is deliberately NOT excluded from the A4 blocker --
this valve was its bound.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    EXHAUSTED_VALVE_STATUSES, FindingRegistry, RunnerConfig,
    _update_finding_statuses,
)

READER_STATUSES = {
    "open_crit_high_count": ("OPEN", "CONTESTED", "REOPENED", "CORROBORATED",
                             "WITHHELD"),
    "unverified_critical_count": ("UNCONFIRMED",),
}


def _entry(status, **over):
    e = {
        "canonical_id": "C1", "status": status, "severity": 0.9,
        "description": "an unresolvable critical", "falsifier_code": "",
        "source_model": "X", "source_aliases": ["F1"],
        "verdicts": [{"model": "X", "verdict": "CONFIRM", "round": 0}],
        "open_since_round": 0, "last_status_change_round": 0,
    }
    e.update(over)
    return e


def _reg(status, **over):
    r = FindingRegistry()
    r.entries["C1"] = _entry(status, **over)
    return r


def _cfg(threshold=4):
    c = RunnerConfig(test_article="x")
    c.exhausted_round_threshold = threshold
    return c


@pytest.mark.parametrize(
    "status", sorted({s for v in READER_STATUSES.values() for s in v}))
def test_the_flag_survives_a_round_tick(status):
    """THE PROPERTY, per status. Before the fix, 2 of these came back None."""
    reg = _reg(status, exhausted=True)
    _update_finding_statuses(reg, 9, cfg=_cfg())
    assert reg.entries["C1"].get("exhausted") is True, (
        f"the valve was stripped from a {status} entry by one ordinary tick, so "
        f"the reader that examines {status} can never see it")


def test_the_valve_population_covers_every_reader_status():
    """DERIVED, not hand-kept. A list that drifts from its readers is how the
    valve died in the first place."""
    needed = {s for v in READER_STATUSES.values() for s in v}
    missing = sorted(needed - set(EXHAUSTED_VALVE_STATUSES))
    assert not missing, (
        f"{missing} are examined by a reader of `exhausted` but are not in the "
        f"valve's population, so the flag is stripped before that reader runs")


def test_the_a4_blocker_actually_releases():
    """The consequence, driven through the real counter rather than the flag."""
    reg = _reg("UNCONFIRMED", exhausted=True)
    assert reg.unverified_critical_count() == 0, "precondition: valve holds"
    _update_finding_statuses(reg, 9, cfg=_cfg())
    assert reg.unverified_critical_count() == 0, (
        "the A4 blocker rose after a tick, so an unresolvable critical blocks "
        "convergence for the life of the run")


def test_it_does_not_release_early():
    """The valve must not become a way to wave findings through."""
    reg = _reg("UNCONFIRMED")
    _update_finding_statuses(reg, 1, cfg=_cfg(threshold=4))
    assert not reg.entries["C1"].get("exhausted"), (
        "age 1 is below the threshold of 4; releasing here would excuse a "
        "finding nobody has finished assessing")
    assert reg.unverified_critical_count() == 1


def test_it_still_requires_review_activity():
    """`has_reviews` is part of the rule: an unreviewed finding is not exhausted."""
    reg = _reg("UNCONFIRMED", verdicts=[])
    _update_finding_statuses(reg, 9, cfg=_cfg())
    assert not reg.entries["C1"].get("exhausted")


def test_a_threshold_of_zero_disables_the_valve():
    """The documented off switch must stay off."""
    reg = _reg("UNCONFIRMED")
    _update_finding_statuses(reg, 99, cfg=_cfg(threshold=0))
    assert not reg.entries["C1"].get("exhausted")


def test_the_exp56_arms_cannot_reach_the_threshold_they_ship_with():
    """THE SECOND, INDEPENDENT KILL — a config one, so the code fix above is
    necessary and NOT sufficient.

    `exhausted_round_threshold` defaults to 8 and every exp56 arm sets
    `max_rounds: 8`, so rounds run 0..7 and the greatest reachable age is 7:
    `age >= 8` is unsatisfiable. This test asserts the arithmetic rather than a
    chosen remedy, because changing a frozen pre-registration config is the
    founder's call, not this file's."""
    import dataclasses
    import json
    fld = {f.name: f for f in dataclasses.fields(RunnerConfig)}["exhausted_round_threshold"]
    default = (fld.default if fld.default is not dataclasses.MISSING
               else fld.default_factory())
    arms = sorted((REPO / "bench" / "exp56_configs").glob("*.json"))
    assert arms, "no arm configs found, the test would be vacuous"
    unreachable = []
    for arm in arms:
        d = json.loads(arm.read_text())
        thr = d.get("exhausted_round_threshold", default)
        max_age = d["max_rounds"] - 1
        if max_age < thr:
            unreachable.append((arm.name, d["max_rounds"], thr, max_age))
    assert unreachable, (
        "every arm can now reach its exhausted threshold — if a config change "
        "landed, update this test to assert the new state rather than deleting it")
