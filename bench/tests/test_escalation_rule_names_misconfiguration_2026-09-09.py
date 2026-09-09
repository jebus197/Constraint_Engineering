"""The irreducible-queue alarm must name MISCONFIGURATION, and point at it first.

Task 4.1. Founder ruling 2026-09-09, verbatim: *"Verdict, do it, test it, then
same answer as above, then test the fixes under f, and sy and then apply them to
the simulation experimental runner if they check out."*

WHY THE RULE WAS INCOMPLETE, and the evidence arrived the same day. The alarm
offered a human 2 explanations for a large irreducible queue: broken machinery,
or an unusually hard document. The empty-ladder defect is neither. In the exp56
1-seat arm the routing ladder is EMPTY BY CONSTRUCTION, because `route` excludes
the finding's own source model and the arm declares 1 seat, so criticals
accumulate while the machinery works exactly as designed and the document is
irrelevant. The cause is the arm's configuration. A human reading the old wording
would hunt a mechanical fault that is not there, which is the most expensive kind
of wrong pointer: it sends the reader into the code.

MISCONFIGURATION IS CHECKED FIRST because it is the cheapest of the 3 to rule out
-- 3 config values, read without opening a source file.

THESE TESTS CALL `build_irreducible_queue_alarm` AND ASSERT ON WHAT IT RETURNS.
The task specified this and the reason is `execute-do-not-grep`: a source-text
test over the runner would pass on a docstring that says the right thing while
the emitted string says the old thing, because each description is individually
consistent. The string a human reads is the artefact under test.
"""

import re
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    FindingRegistry, RunnerConfig, build_irreducible_queue_alarm,
)


def _over_bound_registry(n=4):
    reg = FindingRegistry()
    for i in range(n):
        cid = f"C{i:04d}"
        reg.entries[cid] = {
            "canonical_id": cid, "status": "OPEN", "severity": 0.9,
            "description": f"a locked critical numbered {i}",
            "falsifier_code": "", "verdicts": [],
            "irreducible_escalation": True, "open_since_round": 0,
        }
    return reg


@pytest.fixture
def notify():
    cfg = RunnerConfig(test_article="x")
    alarm = build_irreducible_queue_alarm(_over_bound_registry(), cfg, 3)
    assert alarm is not None, "the fixture must actually trip the alarm"
    return alarm["notify"]


def test_the_alarm_actually_fires_for_this_fixture():
    """Guards against every assertion below passing on an empty string."""
    cfg = RunnerConfig(test_article="x")
    assert build_irreducible_queue_alarm(_over_bound_registry(), cfg, 3) is not None
    assert build_irreducible_queue_alarm(FindingRegistry(), cfg, 3) is None


def test_it_names_misconfiguration(notify):
    assert "MISCONFIGURATION" in notify, (
        "the rule offers a human only broken machinery or a hard document, and "
        "the empty-ladder cause is neither")


def test_it_names_misconfiguration_before_mechanical_failure(notify):
    """ORDER IS THE POINT, not mere presence. Cheapest cause first."""
    i_cfg = notify.index("MISCONFIGURATION")
    i_mech = notify.index("MECHANICAL")
    assert i_cfg < i_mech, (
        f"misconfiguration appears at {i_cfg} and mechanical failure at "
        f"{i_mech}; the reader is sent into the code before checking 3 config "
        f"values")


def test_it_points_at_where_the_fault_might_lie(notify):
    """A cause named without a place to look is not a pointer."""
    for needle in ("routing_enabled", "post_convergence_sweep_rounds", "models"):
        assert needle in notify, f"{needle} is not named as a thing to read"


def test_it_explains_the_empty_ladder_rather_than_only_asserting_it(notify):
    assert "EMPTY BY CONSTRUCTION" in notify
    assert "1 seat" in notify, (
        "the condition under which the ladder is empty must be stated, or the "
        "reader cannot tell whether it applies to their run")


def test_the_hard_document_is_still_named_and_still_last(notify):
    """The amendment must not delete the cause it de-prioritises."""
    assert "unusually hard document" in notify
    i_doc = notify.index("unusually hard document")
    assert i_doc > notify.index("MECHANICAL"), "the rarest cause is not last"


def test_the_old_suppression_warning_survives(notify):
    """The amendment must be additive: this line records 2 wrong calls."""
    assert "Do NOT raise max_irreducible_queue" in notify


def test_the_three_causes_are_numbered_so_they_read_as_an_order(notify):
    assert re.search(r"\n\s*1\..*MISCONFIGURATION", notify)
    assert re.search(r"\n\s*2\..*MECHANICAL", notify)
    assert re.search(r"\n\s*3\.", notify)
