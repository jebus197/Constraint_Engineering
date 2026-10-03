# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'merge_adjudication_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a4487800d69303ef4996eb9b3b717092db4d716121eb13400d0f2d5acfdda589
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A4 consumer-scope guards (STAR round 2026-10-03; MERGED 2026-10-03).

Written by seat 'fable'; TestDB AMENDED at merge adjudication (seat: fable-3,
merge round 2026-10-03). TestDC and TestD3 are fable's originals, verbatim.

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
    """The exact state _apply_routing leaves on an unobserved critical.

    After the merged stamp-side fix, _apply_routing no longer WRITES this
    state (it stamps routing_deferred) -- but archived registries written by
    the pre-fix code still CARRY it, which is exactly why the consumer-side
    guard exists and why this fixture constructs the state directly."""
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
    """AMENDED AT MERGE ADJUDICATION, 2026-10-03, and the amendment is the
    adjudication. The defect (D-B: a sub-critical UNCONFIRMED refusal drained
    from A4 and named nowhere) was confirmed by BOTH seats' executed
    falsifiers. The two fixes disagreed on STRUCTURE, not on the requirement:

        fable : a SECOND reader, integrity_refused_subcriticals(), plus a
                second advisory line -- sub-criticals named there, and the
                criticals reader asserted to stay narrow.
        cc2   : widen the ONE wired reader (integrity_refused_criticals) to
                the A4 counter's own scope, so "whatever the counter drops,
                this names" holds BY CONSTRUCTION.

    SUPERSEDED ASSERTIONS, preserved verbatim rather than deleted:

        assert r.integrity_refused_criticals() == []  # criticals reader: no
        assert r.integrity_refused_subcriticals() == ["C0000"]  # named HERE
        ...
        assert r.integrity_refused_subcriticals() == []
        ...
        assert _reg(e).integrity_refused_subcriticals() == ["C0000"]

    WHY RETIRED. Both structures discharge the material requirement (no
    silent exclusion), so SIMPLEST SUFFICIENT decides: one widened scope
    expression on the already-wired reader, against a second method + second
    advisory + two scope expressions kept in sync by hand. COMPOSABILITY
    refuses keeping both: no committed measurement shows the two-reader form
    dominating the widened single reader on any named property, and under
    the widened reader the superseded `integrity_refused_criticals() == []`
    assertion is not merely inconvenient but WRONG -- it pins the report
    to a scope narrower than the counter it exists to mirror, which is the
    exact shape of the defect this class fixes. The committed oracles
    (test_one_predicate_excludes_and_reports_2026-10-02.py,
    test_key_access_advisory_2026-10-02.py) pin the widened scope by
    execution over randomised registries. The INTENT of every superseded
    assertion -- the drain is named; the naming does not overstate -- is
    re-asserted below against the single reader.
    """

    def test_a_subcritical_refusal_is_named(self):
        e = {"status": "UNCONFIRMED", "severity": 0.5,
             "integrity_refused": True}
        r = _reg(e)
        assert r.unverified_critical_count() == 0  # drained (ruling)
        assert r.integrity_refused_criticals() == ["C0000"], (
            "the A4 blocker dropped a sub-critical key-access refusal and "
            "the wired report does not name it -- a silent exclusion")

    def test_scope_is_the_a4_counters_own(self):
        """Only UNCONFIRMED sub-criticals: other statuses never drained
        from A4, so naming them would overstate."""
        opened = {"status": "OPEN", "severity": 0.5, "integrity_refused": True}
        critical = {"status": "UNCONFIRMED", "severity": 0.9,
                    "integrity_refused": True}
        r = _reg(opened, critical)
        assert r.integrity_refused_criticals() == ["C0001"], (
            "an OPEN sub-critical was never dropped by the A4 counter; "
            "naming it overstates")

    def test_verdict_route_is_covered_too(self):
        """Excluded-by-VERDICT (never passed the routing branch) is the shape
        the 2026-10-02 merge itself missed once; same predicate here."""
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION"}
        assert _reg(e).integrity_refused_criticals() == ["C0000"]

    def test_unobserved_subcritical_is_not_reported_as_excused(self):
        """The carve-out wins: an unobserved entry is NOT excluded, so it
        must not be reported as excused either."""
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION",
             "integrity_unobserved": True}
        assert _reg(e).integrity_refused_criticals() == []


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
