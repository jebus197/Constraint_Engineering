# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a440e6f7aefe31fc4e56f49a7a301b04c4d6ab3ee06ed172fc0846fa66619077
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Section 7.7's KEY PROPERTY must hold in the CRITICAL PARTITION, not only at the A4 door.

PANEL 2026-11-04. `docs/MATHEMATICAL_APPENDIX.md` section 7.7 states the key
property with no configuration attached: "Disproved findings always receive zero
severity, regardless of confidence." Before this test, two readers of the
critical partition -- `_settled_novelty_series` and `_corroborated_novelty_series`
-- read `e.get("severity")` RAW, so a tool-REFUTED finding counted as a critical
discovery, inflating the series `gamma_critical` is fitted to.

These tests EXECUTE the repaired path. They are not source-text assertions:
`bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py` caps those and
tells callers to prefer converting an assertion to one that executes.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import reference_runner_v3 as R  # noqa: E402

THR = R.CRITICAL_SEVERITY_THRESHOLD


class _Reg:
    """Duck-typed registry; both series functions reach entries via `.entries`."""

    def __init__(self, entries):
        self.entries = entries


def _entry(sev, verdict, rnd=0, cid="C0001"):
    return {"severity": sev, "falsifier_verdict": verdict,
            "open_since_round": rnd, "status": "OPEN", "canonical_id": cid}


# ---------------------------------------------------------------- the property

@pytest.mark.parametrize("verdict,expected", [
    ("REFUTED", 0.0),       # V(False) -- the key property
    ("CONFIRMED", 0.9),     # V(True)  -- untouched
    ("", 0.9),              # V(None)  -- untouched, DELIBERATELY (see below)
    ("UNTOOLABLE", 0.9),
    ("ERROR", 0.9),
    ("refuted", 0.0),       # case-insensitive
    ("  REFUTED  ", 0.0),   # whitespace-insensitive
])
def test_spec_critical_severity(verdict, expected):
    assert R.spec_critical_severity(_entry(0.9, verdict)) == expected


def test_key_property_annihilates_whatever_was_asserted():
    """A disproved finding scores 0 for EVERY asserted value, including 1.0."""
    for sev in (0.0, 0.3, 0.7, 0.9, 1.0):
        assert R.spec_critical_severity(_entry(sev, "REFUTED")) == 0.0


def test_non_numeric_severity_does_not_raise():
    assert R.spec_critical_severity({"severity": "high"}) == 0.0
    assert R.spec_critical_severity({}) == 0.0


# -------------------------------------------- the property reaches BOTH readers

@pytest.mark.parametrize("fn", [
    R._settled_novelty_series,
    R._corroborated_novelty_series,
])
def test_refuted_critical_is_not_counted_critical(fn):
    """The defect this repair closes, executed against each partition reader."""
    reg = _Reg({"C0001": _entry(0.9, "REFUTED")})
    all_s, crit_s = fn(reg, 0)
    assert all_s == [1], "a refuted finding is still a FINDING"
    assert crit_s == [0], "a refuted finding is NOT a critical discovery"


@pytest.mark.parametrize("fn", [
    R._settled_novelty_series,
    R._corroborated_novelty_series,
])
def test_unresolved_critical_is_still_counted_critical(fn):
    """V(None) must NOT de-escalate, and this is the load-bearing guard.

    Applying section 7.7's full `asserted * V` here would halve every unresolved
    finding, and since severity is bounded in [0, 1] while the cut is 0.7,
    `severity/2 >= 0.7` needs `severity >= 1.4` -- unreachable. Every unresolved
    finding would become sub-critical, which is exactly the population the A4
    fail-safe exists to block on. Measured consequence over 78 archived runs: the
    two-sided gate flips False -> True on 11 of them, all through the
    vacuous-curve branch. This test pins the restricted form against that.
    """
    reg = _Reg({"C0001": _entry(0.9, "")})
    all_s, crit_s = fn(reg, 0)
    assert all_s == [1]
    assert crit_s == [1], "an UNRESOLVED critical must keep blocking"


def test_full_product_would_manufacture_a_vacuous_curve():
    """Executed disproof of the candidate this repair rejected.

    Shows the refuted alternative really is refuted, rather than asserting it.
    """
    entries = {"C000%d" % i: _entry(0.9, "", rnd=i) for i in range(4)}
    reg_restricted = _Reg(entries)
    _, crit_restricted = R._settled_novelty_series(reg_restricted, 3)

    full = {}
    for cid, e in entries.items():
        c = dict(e)
        c["severity"] = float(e["severity"]) * R.spec_verification_factor(e)
        full[cid] = c
    _, crit_full = R._settled_novelty_series(_Reg(full), 3)

    assert crit_restricted == [1, 1, 1, 1], crit_restricted
    assert crit_full == [0, 0, 0, 0], crit_full
    # and that all-zero series is what trips the vacuous-curve branch
    cfg = R.RunnerConfig()
    conv_full, reason_full = R._check_gamma_alt_convergence(
        round_idx=3, gamma=0.0, novel_critical_history=crit_full, cfg=cfg,
        unresolved_critical=0, contested=0,
        gamma_critical=R._estimate_gamma(crit_full), total_findings=4)
    conv_res, _ = R._check_gamma_alt_convergence(
        round_idx=3, gamma=0.0, novel_critical_history=crit_restricted, cfg=cfg,
        unresolved_critical=0, contested=0,
        gamma_critical=R._estimate_gamma(crit_restricted), total_findings=4)
    assert conv_full is True and "VACUOUS CURVE" in reason_full, reason_full
    assert conv_res is False, "the restricted form must NOT converge here"


def test_all_severity_series_is_severity_independent():
    """`all_s` is untouched by the repair, by construction and by execution."""
    for verdict in ("REFUTED", "CONFIRMED", ""):
        all_s, _ = R._settled_novelty_series(_Reg({"C1": _entry(0.9, verdict)}), 0)
        assert all_s == [1]


def test_effective_severity_default_path_unchanged():
    """The repair must not disturb the other section 7.7 consumer."""
    assert R._SEVERITY_SPEC.get("on") is False, "module default must stay OFF"
    assert R.effective_severity(_entry(0.9, "REFUTED")) == 0.9
