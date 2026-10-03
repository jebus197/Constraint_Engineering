# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_star_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ae0addd8dd368424d32ad0f67f6a85ca2f2c88f81007eaab3075bdd7071c9602
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A4 consumer-scope guards (STAR round 2026-10-03).

The 2026-10-02 merge asserted its invariant over the PREDICATE
(_integrity_violation_excluded); both defects fixed here lived in a
CONSUMER'S SCOPE. Demonstrated red-before/green-after by
bench/tests/falsifier_star_db_dc_2026-10-03.py, which drives the REAL
_apply_routing.

D-C: an integrity_unobserved entry is stamped irreducible_escalation by
_apply_routing's else branch, and unverified_critical_count skipped that
flag BEFORE consulting the carve-out -- so a machine-wide observer failure
drained every critical out of A4 and the run could converge with zero
verified criticals.

D-B: unverified_critical_count has had no severity gate since 2026-09-06,
so the integrity exclusion drains SUB-critical refusals from A4 too, while
integrity_refused_criticals gates at >= 0.7 -- the drain was named in no
report.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench import reference_runner_v3 as rv  # noqa: E402


def _reg(*entries):
    r = rv.FindingRegistry()
    for i, e in enumerate(entries):
        r.entries[f"C{i:04d}"] = e
    return r


def _unobserved_post_routing():
    """The exact state _apply_routing leaves on an unobserved critical."""
    return {"status": "UNCONFIRMED", "severity": 0.9,
            "falsifier_verdict": "INTEGRITY_VIOLATION",
            "integrity_unobserved": True, "irreducible_escalation": True,
            "hil_escalated": True, "falsifier_code": "assert True"}


class TestDC_UnobservedKeepsBlockingA4:

    def test_the_carveout_reaches_the_a4_consumer(self):
        r = _reg(_unobserved_post_routing(), _unobserved_post_routing())
        assert r.unverified_critical_count() == 2, (
            "integrity_unobserved entries must keep blocking A4 even when "
            "routing stamped irreducible_escalation")

    def test_the_block_is_releasable(self):
        """A transient observer fault must not block for the life of the run:
        the exhausted valve still opens."""
        e = _unobserved_post_routing()
        e["exhausted"] = True
        assert _reg(e).unverified_critical_count() == 0

    def test_a_plain_irreducible_entry_is_still_skipped(self):
        """The 2026-06-09 static-queue closure is untouched: ladder-exhausted
        WITHOUT the unobserved flag still leaves A4 (counted by the queue)."""
        e = _unobserved_post_routing()
        del e["integrity_unobserved"]
        del e["falsifier_verdict"]
        assert _reg(e).unverified_critical_count() == 0

    def test_a_key_access_refusal_still_leaves_a4(self):
        """Founder ruling 2026-10-02 intact: a refusal that is NOT an
        observer fault is excused from A4 (and reported)."""
        e = {"status": "UNCONFIRMED", "severity": 0.9,
             "integrity_refused": True, "falsifier_code": "assert True"}
        r = _reg(e)
        assert r.unverified_critical_count() == 0
        assert r.integrity_refused_criticals() == ["C0000"]

    def test_convergence_is_refused_under_observer_failure(self):
        r = _reg(_unobserved_post_routing(), _unobserved_post_routing())
        cfg = rv.RunnerConfig()
        converged, reason = rv._check_gamma_alt_convergence(
            5, 0.0, [0, 0, 0, 0, 0], cfg,
            unresolved_critical=r.unverified_critical_count(),
            contested=0, irreducible_queue=r.irreducible_queue_count(),
            gamma_critical=0.0, total_findings=2)
        assert not converged
        assert "A4 BLOCK" in reason


class TestDB_SubcriticalDrainIsReported:

    def test_a_subcritical_refusal_is_named(self):
        e = {"status": "UNCONFIRMED", "severity": 0.5,
             "integrity_refused": True}
        r = _reg(e)
        assert r.unverified_critical_count() == 0  # drained (ruling)
        assert r.integrity_refused_criticals() == []  # criticals reader: no
        assert r.integrity_refused_subcriticals() == ["C0000"]  # named HERE

    def test_scope_is_the_a4_counters_own(self):
        """Only UNCONFIRMED sub-criticals: other statuses never drained
        from A4, so naming them would overstate."""
        opened = {"status": "OPEN", "severity": 0.5, "integrity_refused": True}
        critical = {"status": "UNCONFIRMED", "severity": 0.9,
                    "integrity_refused": True}
        r = _reg(opened, critical)
        assert r.integrity_refused_subcriticals() == []

    def test_verdict_route_is_covered_too(self):
        """Excluded-by-VERDICT (never passed the routing branch) is the shape
        the 2026-10-02 merge itself missed once; same predicate here."""
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION"}
        assert _reg(e).integrity_refused_subcriticals() == ["C0000"]

    def test_unobserved_subcritical_is_not_reported_as_excused(self):
        """The carve-out wins: an unobserved entry is NOT excluded, so it
        must not be reported as excused either."""
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION",
             "integrity_unobserved": True}
        assert _reg(e).integrity_refused_subcriticals() == []


class TestD3_StaleIntegrityStampsAreRetracted:

    def test_a_verified_replacement_retracts_the_refusal_stamps(self):
        e = {"integrity_refused": True, "integrity_unobserved": True,
             "mechanical_fault": True}
        cleared = rv.clear_stale_resolution_stamps(e)
        assert "integrity_refused" in cleared
        assert "integrity_unobserved" in cleared
        assert not e["integrity_refused"] and not e["integrity_unobserved"]
        # the retraction is recorded, never silent
        assert e["stamp_retractions"][0]["cleared"] == cleared

    def test_a_reopened_critical_is_no_longer_falsely_excused(self):
        e = {"status": "REOPENED", "severity": 0.9, "integrity_refused": True}
        rv.clear_stale_resolution_stamps(e)
        assert not rv._integrity_violation_excluded(e)
