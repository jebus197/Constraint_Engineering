"""Serving a never-served finding must not destroy the door that releases it.

THE CROSS-MODULE DEFECT THIS PINS, AND IT WAS INVISIBLE TO BOTH SEATS THAT
CAUSED IT. The free panel of 2026-10-12 sent two blind seats at one blocker --
a finding nothing ever served blocks convergence for the life of the run -- and
they returned two different mechanisms:

  the SERVE  (`_apply_routing`): a never-served UNCONFIRMED entry is admitted
             into the existing routing ladder exactly once, so that a TOOL can
             decide it. Appends to `routing_history`, which is the one-attempt
             guard.
  the DOOR   (`_routing_ladder_never_served` + `ladder_unserved_findings`):
             after a minimum age, an entry no instrument ever touched stops
             counting as a blocker and is NAMED in the round log, so that the
             exclusion is never silent.

Each passed its own falsifier and failed the other's. Composed, they were
STRICTLY WORSE THAN EITHER ALONE: an empty `routing_history` was one of the
emptiness facts the door required, so the serve CONSUMED THE DOOR'S OWN
TRIGGER. Measured on a C0066-shaped entry served to a ladder that returned
UNRESOLVED: before the serve (A4=0, door releases it), after the serve (A4=1,
door empty) -- blocking for ever again with neither mechanism able to release
it. Producer:
scripts/do_both_never_served_fixes_earn_their_place_2026-10-12.py.

Neither seat could see it. Each tested its own fix in isolation, and in
isolation each is correct. This is the class the adversarial brief names:
"constraint violations visible only at system level".

THE REPAIR distinguishes SERVED-AND-NO-READING from SERVED-AND-RULED, on the
`resolved` flag and an explicit `NO_READING_ROUTING_VERDICTS` sentinel set that
fails CLOSED -- any verdict string not in that tiny set is treated as a ruling.
So the three outcomes of a serve are now distinct, and this file pins all three.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.reference_runner_v3 as rr  # noqa: E402
import bench.routing as routing  # noqa: E402

EXP = {"models": [{"label": "X-SIM"}, {"label": "Y-SIM"}]}
LATER = 9


def _entry(cid="C9001", severity=0.45):
    return {
        "canonical_id": cid, "status": "UNCONFIRMED", "severity": severity,
        "description": "never served", "source_model": "X-SIM",
        "falsifier_code": "", "falsifier_verdict": "", "verdicts": [],
        "escalated": False, "verified": False,
        "open_since_round": 5, "last_status_change_round": 5,
    }


class _Outcome:
    """A ladder result. Mirrors the attributes `_apply_routing` reads."""

    def __init__(self, verdict, resolved, falsifier_code=""):
        self.verdict = verdict
        self.resolved = resolved
        self.falsifier_code = falsifier_code
        self.model_used = "Y-SIM"
        self.duplicate_of = None
        self.rungs_tried = 1
        self.ladder_was_empty = False


def _serve(outcome):
    """Run the REAL serve against a never-served entry; return the registry.

    The router is stubbed, so no dispatch leaves the machine and no seat is
    billed. The labels are SIM labels, never a vendor name.
    """
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _entry()
    with mock.patch.object(routing, "route", return_value=outcome):
        rr._apply_routing(reg, 7, EXP,
                          cfg=rr.RunnerConfig(routing_enabled=True),
                          repo_root=str(Path(__file__).resolve().parents[2]))
    return reg


def test_the_serve_actually_runs():
    """Guard the guard: a serve that no-ops would make every case below vacuous."""
    reg = _serve(_Outcome("UNRESOLVED", False))
    assert reg.entries["C9001"].get("routing_history"), (
        "the serve wrote no routing_history, so this file measures nothing")


def test_served_and_no_reading_KEEPS_BLOCKING_and_is_named_and_queued():
    """REPLACED ON HIS RULING, 2026-10-12, AND IT PINS 3 FACTS WHERE IT PINNED 1.

    This test used to assert that a finding served to a ladder which read
    nothing was RELEASED from the blocker count. He ruled against that
    directly, verbatim: "No. If a record exists that says a problem was never
    read by a model, this should simply be fed back into the mechanics of the
    harness for resolution, this can include routing, the sweep mechanics and
    the other machinery we have for dealing with problems of this nature."

    An exclusion is not a resolution. So the contract is now the stronger one:
    the finding KEEPS BLOCKING, it is NAMED in the report so nothing is
    silent, and it REACHES the halt-with-evidence-bundle machinery so a founder
    sees it rather than a run burning quietly to its round cap.
    """
    reg = _serve(_Outcome("UNRESOLVED", False))
    assert reg.unverified_critical_count(LATER) == 1, (
        "a finding nothing ever read was excused from the blocker count; his "
        "2026-10-12 ruling is that it must be worked, not excused")
    assert reg.ladder_unserved_findings(LATER) == ["C9001"], (
        "blocking but NOT named -- the founder cannot act on what the round "
        "log does not report")
    locked, deferred = rr._irreducible_queue_split(reg.entries)
    assert locked + deferred >= 1, (
        "the never-read finding did not reach the halt machinery, so a run "
        "carrying it burns to max_rounds instead of handing over a bundle")


def test_served_and_RULED_still_blocks():
    """UNTOOLABLE is a ruling by something that ran, not an absence of reading."""
    reg = _serve(_Outcome("UNTOOLABLE", False))
    assert reg.unverified_critical_count(LATER) == 1, (
        "an instrument ran and ruled; that must keep blocking")
    assert reg.ladder_unserved_findings(LATER) == []


def test_served_and_resolved_is_cleared_by_the_tool():
    """TOOLS DECIDE: a resolution clears A4 through the verdict, not the door."""
    reg = _serve(_Outcome("CONFIRMED", True, falsifier_code="assert False"))
    assert reg.unverified_critical_count(LATER) == 0
    assert reg.ladder_unserved_findings(LATER) == [], (
        "cleared by a tool verdict must not ALSO be reported as an exclusion")


def test_an_unrecognised_ladder_verdict_fails_CLOSED():
    """A verdict nobody anticipated must block, never release.

    This is the property that makes the sentinel set safe to be tiny: a new
    verdict added anywhere else in the harness closes this door rather than
    silently widening it.
    """
    reg = _serve(_Outcome("SOME_FUTURE_VERDICT", False))
    assert reg.unverified_critical_count(LATER) == 1
    assert reg.ladder_unserved_findings(LATER) == []


def test_the_sentinel_set_is_tiny_and_contains_no_ruling():
    rulings = {"UNTOOLABLE", "ERROR", "INTEGRITY_VIOLATION", "CONFIRMED",
               "REFUTED", "NON_DISCRIMINATING"}
    assert not (rr.NO_READING_ROUTING_VERDICTS & rulings), (
        "a ruling leaked into the no-reading set; the door is now too wide")


# ---------------------------------------------------------------------------
# THE HALT PATH HIS RULING ROUTES TO, EXERCISED IN THE LIVE SHAPE.
#
# Added 2026-10-12 after the full board refuted two earlier versions of the
# queue predicate. His ruling: "If a record exists that says a problem was
# never read by a model, this should simply be fed back into the mechanics of
# the harness for resolution, this can include routing, the sweep mechanics and
# the other machinery we have for dealing with problems of this nature."
#
# The halt-with-evidence-bundle alarm is that last machinery, and until this
# change it could not see a sub-critical at all: `_irreducible_queue_split`
# skipped everything below CRITICAL_SEVERITY_THRESHOLD, so a run carrying
# never-read sub-criticals could neither converge nor halt and burned to
# max_rounds. Two earlier attempts were each too wide and each was caught by an
# EXISTING test rather than by inspection: counting ladder-EXHAUSTED entries
# (test_subcritical_irreducibles_do_not_trip_the_alarm), then counting a
# critical awaiting its FIRST verification, which would have halted healthy
# runs at 3 fresh findings
# (test_registry_irreducible_excluded_from_a4_blocker).
#
# NON-DISTORTION, MEASURED: over the 69 archived registries, 8 are over the
# bound of 2 both before and after this change -- identical, because the
# archive predates the routing fix and holds no served-but-unread entry. The
# mechanism is forward-looking by construction and the next simulated run is
# what exercises it.
# ---------------------------------------------------------------------------

def test_an_empty_ladder_on_subcriticals_HALTS_with_a_bundle():
    """3 never-read sub-criticals must reach the founder, not burn the run."""
    reg = rr.FindingRegistry()
    for i in range(3):
        reg.entries[f"C900{i}"] = dict(_entry(cid=f"C900{i}"), severity=0.45)

    class _EmptyLadder(_Outcome):
        def __init__(self):
            super().__init__("ERROR", False)
            self.rungs_tried = 0
            self.ladder_was_empty = True
            self.model_used = None

    with mock.patch.object(routing, "route", return_value=_EmptyLadder()):
        rr._apply_routing(reg, 7, EXP,
                          cfg=rr.RunnerConfig(routing_enabled=True),
                          repo_root=str(Path(__file__).resolve().parents[2]))

    locked, deferred = rr._irreducible_queue_split(reg.entries)
    assert locked + deferred == 3, (
        f"the never-read sub-criticals did not reach the halt machinery: "
        f"locked={locked} deferred={deferred}. A run carrying them would "
        f"neither converge nor halt.")
    alarm = rr.build_irreducible_queue_alarm(reg, rr.RunnerConfig(), 9)
    assert alarm is not None, (
        "the alarm stayed silent, so the founder is never handed the bundle")
    assert alarm["count"] == 3 and alarm["bound"] == 2
    assert reg.unverified_critical_count(9) == 3, (
        "and they must still BLOCK -- fed back, not excused")


def test_a_LADDER_EXHAUSTED_subcritical_still_does_NOT_trip_it():
    """The boundary. An exhausted ladder IS instrument contact: every rung ran.

    This is the case the first version of the predicate got wrong, and it is
    held by test_static_queue_closure.py as well. Pinned here too because the
    two cases differ by one flag and the distinction is the whole design.
    """
    reg = rr.FindingRegistry()
    for i in range(5):
        reg.entries[f"C800{i}"] = dict(_entry(cid=f"C800{i}"), severity=0.4,
                                       irreducible_escalation=True)
    locked, deferred = rr._irreducible_queue_split(reg.entries)
    assert locked + deferred == 0, (
        f"an exhausted sub-critical reached the queue: locked={locked} "
        f"deferred={deferred}; that halts runs the ladder genuinely served")
