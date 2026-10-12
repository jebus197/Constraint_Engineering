# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d07bdd6c8fd8fa5bd5f19be696e6288fcf750b788b8267cf22cdf27f6fa352cd
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A transport-dead serve must not mint a ruling-shaped record nor burn the admission.

THE FOURTH LADDER OUTCOME (joint round J1, 2026-10-12). The composition repair
distinguished SERVED-AND-NO-READING / SERVED-AND-RULED / RESOLVED by the
routing_history record's verdict string. But the live ladder NEVER emits the
no-reading sentinels ("", "UNRESOLVED") -- measured by
scripts/transport_dead_serve_blocks_for_ever_2026-10-12.py, the reachable
verdict set of bench.routing.route intersected with NO_READING_ROUTING_VERDICTS
is EMPTY -- and a serve on a DEAD TRANSPORT (every rung's dispatch failed, no
model reached) returned verdict "ERROR", which the door read as a ruling. The
entry was then blocked for ever: door closed by the ERROR record, serve
admission consumed by the non-empty routing_history. The exact composed defect
the 2026-10-12 repair removed, one failure class over.

THE REPAIR PINNED HERE: (1) the transport-dead path reclassifies its own
just-appended ERROR record to "UNRESOLVED" with rungs_reached=0 -- the write
the NO_READING_ROUTING_VERDICTS comment always described; (2) the serve
admission keys on `_routing_ladder_never_served` itself, so a no-reading serve
does not consume the one admission; (3) `error_routed` -- stamped only when a
rung genuinely reached a model -- is a conjunct of the door, so the one-attempt
guard is unchanged wherever a model answered, and the 68 archived entries that
carry error_routed with no routing_history can never be released as unserved.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.reference_runner_v3 as rr  # noqa: E402
import bench.routing as routing  # noqa: E402

EXP = {"models": [{"label": "X-SIM"}, {"label": "Y-SIM"}]}
LATER = 9


def _entry(cid="C9001"):
    return {
        "canonical_id": cid, "status": "UNCONFIRMED", "severity": 0.45,
        "description": "never served", "source_model": "X-SIM",
        "falsifier_code": "", "falsifier_verdict": "", "verdicts": [],
        "escalated": False, "verified": False,
        "open_since_round": 5, "last_status_change_round": 5,
    }


class _DeadTransport:
    """What resolve_via_routing returns when no rung's dispatch succeeds.

    Shape derived by executing the real function with the runner's own
    resolve_fn contract (a failed dispatch returns ""): verdict ERROR,
    resolved False, no code. SIM labels only; no dispatch leaves the machine.
    """

    def __init__(self):
        self.verdict = "ERROR"
        self.resolved = False
        self.falsifier_code = ""
        self.model_used = "Y-SIM"
        self.duplicate_of = None
        self.rungs_tried = 1
        self.ladder_was_empty = False


def _serve(reg, round_idx, result=None):
    with mock.patch.object(routing, "route", return_value=result or _DeadTransport()):
        rr._apply_routing(reg, round_idx, EXP,
                          cfg=rr.RunnerConfig(routing_enabled=True),
                          repo_root=str(Path(__file__).resolve().parents[2]))


def test_a_dead_transport_record_is_reclassified_to_no_reading():
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _entry()
    _serve(reg, 7)
    rec = reg.entries["C9001"]["routing_history"][0]
    assert rec["verdict"] == "UNRESOLVED", (
        "a serve no model answered wrote a ruling-shaped verdict; the door "
        "will read it as instrument contact that never happened")
    assert rec["rungs_reached"] == 0
    assert rec["resolved"] is False


def test_the_entry_is_released_AND_named_not_blocked_for_ever():
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _entry()
    _serve(reg, 7)
    assert reg.unverified_critical_count(LATER) == 0
    assert reg.ladder_unserved_findings(LATER) == ["C9001"]


def test_the_admission_is_not_burnt_the_ladder_retries_next_round():
    """The transport-dead guard's own promise: 'must not burn the attempt'."""
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _entry()
    _serve(reg, 7)
    _serve(reg, 8)
    assert len(reg.entries["C9001"]["routing_history"]) == 2, (
        "the failed serve consumed the one admission; a later round with a "
        "healed transport can never decide this finding")


def test_a_ruling_verdict_is_NOT_reclassified():
    """UNTOOLABLE on a mocked serve keeps its ruling semantics and blocks."""
    dead = _DeadTransport()
    dead.verdict = "UNTOOLABLE"
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _entry()
    _serve(reg, 7, result=dead)
    assert reg.entries["C9001"]["routing_history"][0]["verdict"] == "UNTOOLABLE"
    assert reg.unverified_critical_count(LATER) == 1
    assert reg.ladder_unserved_findings(LATER) == []


def test_error_routed_alone_closes_the_door():
    """The named untested instrument-contact field (cc2's standing refutation
    condition). 68 archived entries carry error_routed=True with an empty
    routing_history -- the flag predates the history field by six weeks."""
    e = _entry()
    e["error_routed"] = True
    assert rr._routing_ladder_never_served(e) is False


def test_a_served_and_answered_entry_is_not_readmitted():
    """One-attempt guard unchanged where a model answered: error_routed set,
    predicate False, so the serve admission refuses it."""
    e = _entry()
    e["error_routed"] = True
    e["routing_history"] = [{"round": 7, "verdict": "ERROR", "resolved": False}]
    assert rr._routing_ladder_never_served(e) is False
