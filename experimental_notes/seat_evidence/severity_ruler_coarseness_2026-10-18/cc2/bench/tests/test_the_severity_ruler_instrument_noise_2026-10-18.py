# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_ruler_coarseness_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d8785e3979184f874965b0cd9b9c8562be7f92f312c4935c2fa72d9e478afd25
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Falsifiers for `bench/severity_instrument.py` (C4, free panel 2026-10-18).

WHAT EACH TEST WOULD PRINT IF THE FIX WERE WRONG is written into its own
assertion message, because a falsifier that cannot say what failure looks like
is not a falsifier. Every test here runs against the REAL archived finding
catalogues under `bench/logs/`, not against a fixture, and drives the REAL
production caller `gamma_threshold_profile`.
"""

import glob
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import bench.reference_runner_v3 as R  # noqa: E402
from bench.severity_instrument import (  # noqa: E402
    SEVERITY_INSTRUMENT_SIGMA,
    critical_weight,
    expected_critical_series,
    instrument_noise_profile,
    tail_is_quiescent_soft,
)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class _Reg:
    """Minimal stand-in exposing only `.entries`, which is all the producers read."""

    def __init__(self, entries):
        self.entries = entries


def _catalogues():
    pat = os.path.join(_ROOT, "bench", "logs", "**", "*finding_catalogue.jsonl")
    out = []
    for p in sorted(glob.glob(pat, recursive=True)):
        rows = [json.loads(l) for l in open(p) if l.strip()]
        if not rows:
            continue
        mx = max((e.get("open_since_round") or 0) for e in rows)
        out.append((os.path.basename(os.path.dirname(p)), rows, mx))
    return out


def test_the_archive_is_actually_present():
    """Guard: every test below is vacuous if the archive is not there."""
    cats = _catalogues()
    assert len(cats) >= 20, (
        f"only {len(cats)} archived finding catalogues found under bench/logs -- "
        "the measurements below would pass vacuously on an empty corpus")


def test_sigma_zero_reproduces_the_live_critical_series_exactly():
    """THE ADDITIVE PROPERTY, EXECUTED. sigma=0 IS the live ruler, value for value.

    If the fix were wrong -- a sign error, a `>` where the live rule has `>=`, a
    different population filter -- this prints the run name and the two series
    side by side and fails.
    """
    checked = 0
    for name, rows, mx in _catalogues():
        _all, live_crit = R._settled_novelty_series(_Reg({
            e["canonical_id"]: e for e in rows}), mx)
        mine = expected_critical_series(
            rows, mx, R._NON_NOVEL_TERMINAL_STATUSES,
            R.CRITICAL_SEVERITY_THRESHOLD, sigma=0.0)
        assert [int(c) for c in mine] == list(live_crit), (
            f"{name}: sigma=0 does NOT reproduce the live critical series.\n"
            f"  live `_settled_novelty_series`: {list(live_crit)}\n"
            f"  instrument at sigma=0        : {[int(c) for c in mine]}\n"
            "The current ruler must be the sigma=0 member of this family; it is "
            "not, so this is a REPLACEMENT and not an addition.")
        checked += 1
    assert checked >= 20, f"only {checked} runs checked"


def test_the_soft_quiescence_rule_is_one_way_on_every_archived_run():
    """THE DIRECTION-OF-EFFECT PROPERTY, measured, not judged.

    `soft_quiescent => hard_quiescent`, so the instrument can only ever make
    convergence HARDER or leave it unchanged. If the fix were wrong this prints
    the run on which the soft rule PERMITTED a convergence the hard rule
    refused -- the direction the brief says must be argued for -- and fails.
    """
    differ, easier, total = [], [], 0
    for name, rows, mx in _catalogues():
        if mx + 1 < 3:
            continue
        total += 1
        prof = instrument_noise_profile(
            rows, mx, R._NON_NOVEL_TERMINAL_STATUSES,
            R.CRITICAL_SEVERITY_THRESHOLD, R._estimate_gamma)
        soft_q = prof["tail_is_quiescent_soft"]
        hard_q = prof["tail_is_quiescent_hard"]
        if soft_q != hard_q:
            differ.append(name)
        if soft_q and not hard_q:
            easier.append((name, prof["expected_critical_tail"],
                           prof["hard_critical_series_at_sigma_zero"]))
    assert not easier, (
        "ONE-WAY PROPERTY VIOLATED -- the soft rule permitted a convergence the "
        f"hard rule refused on {len(easier)} run(s): {easier}. The module "
        "docstring's proof (a countable finding at sev>=theta forces w>=Phi(0)="
        "0.5) is therefore false of this implementation, and the fix makes "
        "convergence EASIER, which this brief forbids without a measurement.")
    assert total >= 19, f"only {total} runs with >=3 rounds"
    # The instrument must REACH something; an addition nothing reaches is not
    # additive. This is the measured 5 of 19.
    assert len(differ) >= 1, (
        "the instrument changed the quiescence verdict on 0 archived runs, so it "
        f"reaches nothing: differ={differ}, total={total}")
    print(f"\nquiescence verdict differs on {len(differ)}/{total}: {differ}")


def test_refuted_is_annihilated_exactly_on_the_real_leg3_entries():
    """Section 7.7's key property, EXACTLY 0.0 and not Phi's 4.1e-7 tail."""
    p = os.path.join(_ROOT, "bench", "logs",
                     "leg3_final_shakedown_20261015T220118Z",
                     "leg3_final_shakedown_finding_catalogue.jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    ref = [e for e in rows if e.get("falsifier_verdict") == "REFUTED"]
    assert len(ref) == 2, f"expected the 2 archived REFUTED findings, got {len(ref)}"
    for e in ref:
        w = critical_weight(e, R.CRITICAL_SEVERITY_THRESHOLD)
        assert w == 0.0, (
            f"{e['canonical_id']} (severity {e['severity']}, REFUTED) got weight "
            f"{w!r}, not exactly 0.0. A disproved finding must be ANNIHILATED, "
            "not merely reduced -- that is the appendix's key property, and "
            f"Phi's own tail here is {0.5 * (1 + __import__('math').erf((e['severity'] - 0.7) / (SEVERITY_INSTRUMENT_SIGMA * 2 ** 0.5))):.3e}.")


def test_the_unresolved_population_cannot_be_critical_under_the_spec():
    """The collapse, executed on the real archive rather than argued.

    z3 proves `asserted*V >= 0.7` is identically `V==1 and asserted>=0.7`. This
    shows it on real entries: with the specification ON, NO entry whose falsifier
    has not resolved reaches the threshold, however high its asserted number.
    If this failed it would print the entry that did, refuting the collapse.
    """
    rows = []
    for _n, rs, _m in _catalogues():
        rows.extend(rs)
    unresolved = [e for e in rows
                  if str(e.get("falsifier_verdict") or "").strip().upper()
                  not in ("CONFIRMED", "REFUTED")]
    assert len(unresolved) >= 50, f"only {len(unresolved)} unresolved entries"
    hi = [e for e in unresolved
          if float(e.get("severity") or 0.0) >= R.CRITICAL_SEVERITY_THRESHOLD]
    R._SEVERITY_SPEC["on"] = True
    try:
        offenders = [(e["canonical_id"], e["severity"], R.effective_severity(e))
                     for e in unresolved
                     if R.effective_severity(e) >= R.CRITICAL_SEVERITY_THRESHOLD]
    finally:
        R._SEVERITY_SPEC["on"] = False
    assert not offenders, (
        "COLLAPSE REFUTED: an unresolved entry reached the critical threshold "
        f"under the specification: {offenders[:5]}")
    print(f"\n{len(hi)} of {len(unresolved)} unresolved entries are "
          f"asserted-critical; 0 are specification-critical (collapse holds)")


def test_the_profile_is_reached_by_the_production_caller():
    """WIRED TO A CALLER, not a dead function. Drives `gamma_threshold_profile`.

    If the wiring were absent this prints the keys the production producer
    actually returned and fails -- which is exactly the failure mode this
    project has shipped 11 times.
    """
    p = os.path.join(_ROOT, "bench", "logs",
                     "leg3_final_shakedown_20261015T220118Z",
                     "leg3_final_shakedown_finding_catalogue.jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    mx = max((e.get("open_since_round") or 0) for e in rows)
    out = R.gamma_threshold_profile(
        _Reg({e["canonical_id"]: e for e in rows}), mx, 3)
    assert "instrument_noise_profile" in out, (
        "gamma_threshold_profile does not report the instrument noise profile, "
        f"so nothing reaches it. Keys returned: {sorted(out)}")
    prof = out["instrument_noise_profile"]
    assert "error" not in prof, f"producer raised: {prof.get('error')}"
    assert prof["sigma"] == SEVERITY_INSTRUMENT_SIGMA
    assert prof["gamma_critical_hard"] == 1.0, prof
    assert 0.9 < prof["gamma_critical_soft"] < 1.0, prof
    print(f"\nleg3 via production caller: gamma_hard={prof['gamma_critical_hard']}, "
          f"gamma_soft={prof['gamma_critical_soft']}, "
          f"soft tail={prof['expected_critical_tail']}, "
          f"differs={prof['quiescence_verdict_differs']}")


@pytest.mark.parametrize("sev,expect", [
    (0.70, 0.5),      # exactly on the line -> exactly half a critical
])
def test_a_finding_on_the_line_is_worth_half_a_critical(sev, expect):
    """Phi(theta)=1/2 for every sigma>0 -- the honest value of a coin toss."""
    assert critical_weight({"severity": sev}, 0.7) == pytest.approx(expect, abs=1e-12)
    assert not tail_is_quiescent_soft([0.5]), (
        "a round containing one finding exactly on the line must NOT read as "
        "quiescent; 0.5 is the rounding boundary and `< 0.5` is strict")
