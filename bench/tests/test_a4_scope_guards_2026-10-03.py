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
    """REPORTED BY ONE READER, NOT TWO (MERGE round 2026-10-03).

    SUPERSEDED IMPLEMENTATION, and the four properties below are the SAME four
    this class shipped with. What changed is only WHICH reader names the
    drain. As delivered, this class called a sibling
    `FindingRegistry.integrity_refused_subcriticals()` and additionally pinned
    `integrity_refused_criticals() == []` for a sub-critical entry. That last
    assertion is in DIRECT logical contradiction with the committed oracle
    bench/tests/test_one_predicate_excludes_and_reports_2026-10-02.py
    ::test_a_terminal_entry_is_neither_and_a_subcritical_one_IS_REPORTED,
    which asserts `== ["C2", "C3"]` with C2 at severity 0.1 -- so one of the
    two had to be retired on the merits rather than on taste.

    WHICH STANDARD DECIDED IT: SIMPLEST SUFFICIENT. Both forms discharge the
    requirement ("whatever the A4 counter drops, a report names"), so the
    simpler wins. Widening the reader that is ALREADY wired costs one
    disjunct and returns a strict superset of what it returned before; the
    sibling form costs a second method, a second report key, a second log
    line, and makes the invariant hold only as the UNION of two scopes that a
    later edit can drift apart, where the single reader makes it hold BY
    CONSTRUCTION. COMPOSABILITY was tested and REFUSED: with the criticals
    reader widened, every id the sibling would return is already named, so
    keeping both prints the same id under two advisory headings -- no
    demonstrated advantage over either alone, and the founder's rule is then
    to prefer the single fix. ADDITIVE is neutral: both readers are wired, and
    nothing a reader could see before stops being visible.

    Verbatim text of the superseded assertions is kept in each method below,
    so this is a retirement with a reason on the record, not a deletion.
    """

    def test_a_subcritical_refusal_is_named(self):
        # SUPERSEDED:
        #     assert r.integrity_refused_criticals() == []      # criticals reader: no
        #     assert r.integrity_refused_subcriticals() == ["C0000"]  # named HERE
        e = {"status": "UNCONFIRMED", "severity": 0.5,
             "integrity_refused": True}
        r = _reg(e)
        assert r.unverified_critical_count() == 0  # drained (ruling)
        assert r.integrity_refused_criticals() == ["C0000"]  # named, one reader

    def test_scope_is_the_a4_counters_own(self):
        """Only entries the A4 counter actually drops. A sub-critical that is
        not UNCONFIRMED never entered that counter, so naming it would
        overstate."""
        # SUPERSEDED: assert r.integrity_refused_subcriticals() == []
        opened = {"status": "OPEN", "severity": 0.5, "integrity_refused": True}
        critical = {"status": "UNCONFIRMED", "severity": 0.9,
                    "integrity_refused": True}
        r = _reg(opened, critical)
        # C0000 (OPEN, sub-critical) is outside both counters -> not named.
        # C0001 (UNCONFIRMED, critical) was dropped -> named.
        assert r.integrity_refused_criticals() == ["C0001"]

    def test_verdict_route_is_covered_too(self):
        """Excluded-by-VERDICT (never passed the routing branch) is the shape
        the 2026-10-02 merge itself missed once; same predicate here."""
        # SUPERSEDED: assert _reg(e).integrity_refused_subcriticals() == ["C0000"]
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION"}
        assert _reg(e).integrity_refused_criticals() == ["C0000"]

    def test_unobserved_subcritical_is_not_reported_as_excused(self):
        """The carve-out wins: an unobserved entry is NOT excluded, so it
        must not be reported as excused either."""
        # SUPERSEDED: assert _reg(e).integrity_refused_subcriticals() == []
        e = {"status": "UNCONFIRMED", "severity": 0.3,
             "falsifier_verdict": "INTEGRITY_VIOLATION",
             "integrity_unobserved": True}
        assert _reg(e).integrity_refused_criticals() == []

    def test_no_second_reader_was_left_behind(self):
        """ANTI-DRIFT. The sibling reader was retired, not merely unused: if a
        later edit re-adds it, this file must be revisited rather than quietly
        carrying two scopes again."""
        assert not hasattr(rv.FindingRegistry, "integrity_refused_subcriticals")


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
