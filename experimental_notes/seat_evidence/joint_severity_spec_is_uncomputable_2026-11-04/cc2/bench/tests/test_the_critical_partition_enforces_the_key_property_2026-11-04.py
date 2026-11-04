# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 987f4dc95e6f29ec6a8ac42c98ddbb699ea83b0fde0cc05ea1331c4ee8615097
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The critical partition enforces appendix section 7.7's KEY PROPERTY.

Every assertion here EXECUTES the shipped functions. There is no source-text
assertion in this file, on the instruction
`bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py` prints when it
trips: *"Prefer CONVERTING an assertion to one that executes over raising this
ceiling."*

Pins three things the 2026-11-04 joint severity panel measured:
  * `spec_critical_severity` annihilates on V == 0 and on NOTHING else, so the
    V(None) = 0.5 halving -- the manufactured-convergence direction, 11 of 67
    archived runs under `asserted * V` -- cannot act on the partition;
  * a tool-owned CONFIRMED status outranks a stale REFUTED verdict field (1 of
    3,170 archived entries is in that state);
  * the annihilation is RECOMPUTED per read, never stamped, because
    REFUTED -> CONFIRMED is reachable in the live reattachment path.
"""
import pytest

from bench.reference_runner_v3 import (
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, RunnerConfig,
    _check_gamma_alt_convergence, _corroborated_novelty_series,
    _settled_novelty_series, effective_severity,
    record_in_round_falsifier_reattachments, spec_critical_severity,
    wire_module_mirrors,
)

READERS = (_settled_novelty_series, _corroborated_novelty_series)
READER_IDS = ("settled", "corroborated")


def _registry(**over):
    e = {"canonical_id": "C0001", "source_model": "SEAT", "source_aliases": [],
         "severity": 0.9, "description": "probe", "proposed_fix": "",
         "status": "OPEN", "open_since_round": 0,
         "last_status_change_round": 0, "verdicts": [], "verified": False,
         "escalated": False, "flaw_class": 1}
    e.update(over)
    reg = FindingRegistry()
    reg.entries = {"C0001": e}
    return reg


@pytest.mark.parametrize("reader", READERS, ids=READER_IDS)
def test_a_disproved_finding_is_not_a_critical_discovery(reader):
    all_s, crit_s = reader(_registry(falsifier_verdict="REFUTED"), 0)
    assert crit_s == [0]
    assert all_s == [1], "a refuted finding is still a finding"


@pytest.mark.parametrize("reader", READERS, ids=READER_IDS)
def test_an_unresolved_critical_still_counts(reader):
    _all, crit_s = reader(_registry(), 0)
    assert crit_s == [1], "V(None) must not de-escalate the partition"


@pytest.mark.parametrize("reader", READERS, ids=READER_IDS)
def test_a_confirmed_critical_still_counts(reader):
    _all, crit_s = reader(_registry(falsifier_verdict="CONFIRMED"), 0)
    assert crit_s == [1]


@pytest.mark.parametrize("reader", READERS, ids=READER_IDS)
def test_a_tool_confirmed_status_outranks_a_stale_refuted_verdict(reader):
    reg = _registry(falsifier_verdict="REFUTED", status="CONFIRMED")
    _all, crit_s = reader(reg, 0)
    assert crit_s == [1]


@pytest.mark.parametrize("asserted", [0.0, 0.3, 0.7, 0.9, 1.0])
def test_the_key_property_annihilates_whatever_was_asserted(asserted):
    assert spec_critical_severity(
        {"severity": asserted, "falsifier_verdict": "REFUTED"}) == 0.0


@pytest.mark.parametrize("verdict", ["", None, "UNTOOLABLE", "ERROR",
                                     "NON_DISCRIMINATING", "CONFIRMED"])
def test_nothing_but_a_refutation_is_annihilated(verdict):
    assert spec_critical_severity(
        {"severity": 0.9, "falsifier_verdict": verdict}) == 0.9


def test_the_annihilation_is_recomputed_not_stamped():
    """REFUTED -> CONFIRMED is reachable live, so a stamped zero would be wrong."""
    e = {"severity": 0.9, "falsifier_verdict": "REFUTED", "status": "OPEN"}
    assert spec_critical_severity(e) == 0.0
    e["falsifier_verdict"] = "CONFIRMED"
    assert spec_critical_severity(e) == 0.9
    assert "sev_f" not in e and "spec_severity" not in e


def test_the_live_reattachment_path_moves_refuted_to_confirmed():
    """The transition the recompute exists for, through the REAL function."""
    reg = _registry(falsifier_verdict="REFUTED", falsifier_code="assert True")
    stats = record_in_round_falsifier_reattachments(
        reg, {"SEAT": "FALSIFIER: C0001\n```python\nassert False, 'defect'\n```"},
        1)
    assert stats["executed"] == 1
    assert reg.entries["C0001"]["falsifier_verdict"] == "CONFIRMED"
    _all, crit_s = _settled_novelty_series(reg, 0)
    assert crit_s == [1], "the restored verdict restores the critical count"


def test_it_is_not_effective_severity_and_the_difference_is_v_none():
    """`effective_severity` halves an unresolved finding; this must not."""
    e = {"severity": 0.9}
    wire_module_mirrors(RunnerConfig(severity_spec_enabled=True))
    try:
        assert effective_severity(e) == pytest.approx(0.45)
        assert effective_severity(e) < CRITICAL_SEVERITY_THRESHOLD
        assert spec_critical_severity(e) == 0.9
        assert spec_critical_severity(e) >= CRITICAL_SEVERITY_THRESHOLD
    finally:
        wire_module_mirrors(RunnerConfig())
    assert effective_severity(e) == 0.9


def test_the_a4_fail_safe_still_blocks_an_unresolved_critical():
    """The gate, called for real, must not converge on an unresolved critical."""
    cfg = RunnerConfig()
    converged, reason = _check_gamma_alt_convergence(
        6, 0.9, [0, 0, 0], cfg, unresolved_critical=1, contested=0,
        gamma_critical=0.9, total_findings=5)
    assert converged is False
    assert "A4 BLOCK" in reason


def test_a_refuted_only_run_does_not_reach_the_vacuous_curve_by_halving():
    """Three unresolved criticals keep the series non-zero under the repair.

    This is the mechanism the 11 archived False -> True flips travelled:
    `asserted * V` drives the whole critical series to zero, the cumulative
    count hits zero, and the vacuous-curve branch converges. Under the repair
    the series is unchanged, so the branch is not reached.
    """
    reg = FindingRegistry()
    reg.entries = {
        f"C000{i}": {"canonical_id": f"C000{i}", "severity": 0.9,
                     "status": "OPEN", "open_since_round": i,
                     "source_model": "SEAT", "verdicts": []}
        for i in range(3)}
    _all, crit_s = _settled_novelty_series(reg, 2)
    assert crit_s == [1, 1, 1]
    cfg = RunnerConfig()
    converged, reason = _check_gamma_alt_convergence(
        2, 0.5, list(crit_s), cfg, gamma_critical=0.0, total_findings=3)
    assert converged is False
    assert "VACUOUS" not in reason
