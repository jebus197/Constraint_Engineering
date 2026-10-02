# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 77508085ec03181111670a7d6f57c295e428b7cfc94140ef34377f0f788ce4cd
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Founder ruling 2026-10-02: the key-access check is reporting, not machinery.

    "Just make it accurate. If a key was accessed and read, report it at the
    end of a run. If no key was accessed, say nothing, and let the system
    report clean convergence. But convergence should not be blocked and runs
    should not be terminated even if a key was read."

Three design pieces, each executed here rather than described:

  D1  the pre-execution gate refuses ACCESS evidence only; vocabulary-only
      matches stop being refusals, and `seeded_faults` joins the access field
      list so reading the build-bot planted set is still refused.
  D2  INTEGRITY_VIOLATION leaves the convergence machinery: it feeds neither
      `irreducible_queue_count` (the halt) nor `unverified_critical_count`
      (the A4 blocker). The UNOBSERVED carve-out keeps blocking, because a
      machine-wide observer failure must not read as a clean convergence.
  D3  the post-run scanner resolves repo-relative declared targets, suppresses
      verbatim self-quotes inside harvested copies of the detector's own
      source, and sources an end-of-run advisory: silent when clean, loud when
      a key was actually read, zero weight on convergence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from bench.falsifier_verify import scan_falsifier_source, scan_falsifier_output  # noqa: E402
import bench.reference_runner_v3 as rr  # noqa: E402

LOGS = REPO_ROOT / "bench" / "logs"
EXP48 = LOGS / "exp48_chemistry_exam_live_20260729T044134Z"
RUN1B = LOGS / "prose_convergence_run1b_2026-10-02_20261002T044234Z"
# The repo root the ARCHIVED artefacts name. On the live machine this equals
# the working tree; in a sandbox copy it does not, so it is passed explicitly.
LIVE_ROOT = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


# ── D1: access-only gate ─────────────────────────────────────────────────────

def test_the_real_exploit_is_still_refused_by_multiple_access_rules():
    state = json.loads((EXP48 / "runner_state.json").read_text())
    exploit = state["registry"]["entries"]["C0012"]["falsifier_code"]
    violations = scan_falsifier_source(exploit)
    reasons = {r for r, _ in violations}
    assert len(reasons) >= 3, f"the Exp 48 exploit is no longer multiply caught: {reasons}"
    assert any("answer-key" in r for r in reasons)
    assert any("subscripted" in r for r in reasons)


@pytest.mark.parametrize("code", [
    'f = task["seeded_faults"]',
    "f = task.get('seeded_faults', [])",
    'f = task["seeded_fault"]',
])
def test_access_to_the_planted_fault_field_is_refused(code):
    assert scan_falsifier_source(code), f"planted-set access allowed: {code}"


@pytest.mark.parametrize("code", [
    # A set-literal naming required schema keys — mention, not access.
    'REQUIRED = {"task_id", "seeded_faults", "files"}\nassert REQUIRED <= keys',
    # Honest prose about the field.
    '# each task carries seeded_faults metadata\nassert "seeded_faults" in text',
    # The C0035 shape from run 1b: an assertion about the DOCUMENT's text.
    'text = open("BUILD_BOT_TEST_BENCH_FIX_SPEC.md").read()\n'
    'assert "seeded_faults" in text, "spec no longer names the field"',
])
def test_mention_of_the_planted_fault_field_is_not_refused(code):
    assert scan_falsifier_source(code) == [], (
        "a vocabulary-only mention was refused; the 2026-10-02 access-only "
        "ruling has regressed")


def test_the_output_net_still_withholds_a_printed_plant_set():
    assert scan_falsifier_output("planted_false set: ['CH-11', 'CH-13']")


# ── D2: INTEGRITY_VIOLATION leaves the convergence machinery ────────────────

def _entry(verdict=None, sev=0.9, status="UNCONFIRMED", **kw):
    e = {"status": status, "severity": sev}
    if verdict is not None:
        e["falsifier_verdict"] = verdict
    e.update(kw)
    return e


def _cfg(**kw):
    class C:  # noqa: D401 — minimal duck-typed config
        pass
    c = C()
    c.max_irreducible_queue = 2
    c.gamma_alt_earliest_round = 2
    c.gamma_alt_consecutive_zero_crit = 3
    c.gamma_alt_threshold = 0.30
    c.rho_threshold = 0.05
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def test_integrity_violations_feed_neither_counter():
    reg = rr.FindingRegistry()
    reg.entries = {
        "C1": _entry("INTEGRITY_VIOLATION", irreducible_escalation=True),
        "C2": _entry("INTEGRITY_VIOLATION", routing_deferred=True),
        "C3": _entry("INTEGRITY_VIOLATION"),
    }
    assert reg.irreducible_queue_count() == 0
    assert reg.unverified_critical_count() == 0
    assert rr.build_irreducible_queue_alarm(reg, _cfg(), 2) is None


def test_the_unobserved_carveout_still_blocks():
    """A machine-wide observer failure must not read as clean convergence."""
    reg = rr.FindingRegistry()
    reg.entries = {"C1": _entry("INTEGRITY_VIOLATION", integrity_unobserved=True)}
    assert reg.unverified_critical_count() == 1


def test_equipment_failures_still_count_and_still_halt():
    reg = rr.FindingRegistry()
    reg.entries = {
        "C1": _entry("ERROR", routing_deferred=True),
        "C2": _entry("UNTOOLABLE", routing_deferred=True),
        "C3": _entry("ERROR", irreducible_escalation=True),
    }
    assert reg.irreducible_queue_count() == 3
    alarm = rr.build_irreducible_queue_alarm(reg, _cfg(), 1)
    assert alarm is not None, "a genuine over-bound queue no longer halts"
    assert len(alarm["evidence"]) == 3, "bundle does not match the count"


def test_the_gate_conditions_themselves_are_untouched():
    """D2 changes the A4 INPUT; the two-sided gate's own conditions —
    gamma_critical >= threshold and the zero-new-critical streak — decide."""
    # IV-only registry: A4 input 0, gate converges on its own conditions.
    conv, reason = rr._check_gamma_alt_convergence(
        5, 0.4, [0, 0, 0], _cfg(), unresolved_critical=0, contested=0,
        rho_churn=False, irreducible_queue=0, gamma_critical=0.336,
        total_findings=10)
    assert conv, reason
    # Below the gamma threshold the gate still refuses — the history must
    # carry PRIOR criticals, or the vacuous-curve carve-out (2026-07-29)
    # legitimately satisfies the gamma side on an all-zero series.
    conv2, reason2 = rr._check_gamma_alt_convergence(
        5, 0.4, [2, 1, 0, 0, 0], _cfg(), unresolved_critical=0, contested=0,
        rho_churn=False, irreducible_queue=0, gamma_critical=0.10,
        total_findings=10)
    assert not conv2, reason2
    # An unresolved critical still blocks via A4.
    conv3, _ = rr._check_gamma_alt_convergence(
        5, 0.4, [0, 0, 0], _cfg(), unresolved_critical=1, contested=0,
        rho_churn=False, irreducible_queue=0, gamma_critical=0.336,
        total_findings=10)
    assert not conv3


def test_run_1b_shape_no_longer_halts():
    """The halt-time queue was {UNTOOLABLE-deferred, ERROR-deferred,
    INTEGRITY_VIOLATION} = 3 > bound 2. Excluding the IV leaves 2 <= 2."""
    reg = rr.FindingRegistry()
    reg.entries = {
        "C0029": _entry("UNTOOLABLE", routing_deferred=True),
        "C0032": _entry("ERROR", routing_deferred=True),
        "C0035": _entry("INTEGRITY_VIOLATION", irreducible_escalation=True),
    }
    assert reg.irreducible_queue_count() == 2
    assert rr.build_irreducible_queue_alarm(reg, _cfg(), 2) is None


# ── D3: the scanner and the advisory ─────────────────────────────────────────

needs_archive = pytest.mark.skipif(
    not (EXP48 / "runner_state.json").exists() or not (RUN1B / "runner_state.json").exists(),
    reason="archived runs not present")


@needs_archive
def test_exp48_still_detected_and_advisory_fires():
    from bench.key_access_forensics import scan_run, end_of_run_advisory
    rep = scan_run(EXP48, repo_root=LIVE_ROOT)
    c0012 = [h for h in rep.confirmed if h.finding == "C0012"]
    assert len(c0012) >= 10, "the real breach is no longer detected at CONFIRMED"
    assert rep.repo_in_scope is False, (
        "an EXAM run put the repository in scope — the 2026-07-29 confinement "
        "has been reopened")
    adv = end_of_run_advisory(EXP48, repo_root=LIVE_ROOT)
    assert adv and "C0012" in adv


@needs_archive
def test_run_1b_scans_clean_and_advisory_is_silent():
    from bench.key_access_forensics import scan_run, end_of_run_advisory
    rep = scan_run(RUN1B, repo_root=LIVE_ROOT)
    assert rep.confirmed == [], (
        f"{len(rep.confirmed)} false CONFIRMED on a run where no key was read")
    assert rep.repo_in_scope is True
    assert end_of_run_advisory(RUN1B, repo_root=LIVE_ROOT) is None


@needs_archive
def test_detector_copy_suppression_requires_a_verbatim_quote(tmp_path):
    """An exploit ADDED to a harvested detector copy is still reported."""
    from bench.key_access_forensics import scan_run
    run = tmp_path / "fake_run"
    dest = run / "panel_worktree_harvest" / "files" / "bench"
    dest.mkdir(parents=True)
    real = (REPO_ROOT / "bench" / "falsifier_verify.py").read_text()
    planted = real + "\nk = json.load(open('/Users/x/exp99_answer_key.json'))\n"
    (dest / "falsifier_verify.py").write_text(planted)
    rep = scan_run(run)
    assert any("exp99_answer_key" in h.snippet for h in rep.confirmed), (
        "a planted exploit inside a detector copy was suppressed")
    assert rep.suppressed_detector_copy > 0, (
        "the detector's own quoted rules were not suppressed")


def test_the_advisory_is_wired_into_the_runner_finalize():
    """Additive standard: an entry point nothing reaches is not additive.
    The runner's finalize must call the advisory and only ever REPORT it."""
    src = (REPO_ROOT / "bench" / "reference_runner_v3.py").read_text()
    assert "end_of_run_advisory" in src
    seg = src[src.index("END-OF-RUN KEY-ACCESS ADVISORY"):][:1500]
    assert 'result["key_access_advisory"]' in seg
    for forbidden in ("converged", "irreducible", "unverified_critical"):
        assert forbidden not in seg, (
            f"the advisory block touches {forbidden!r}; it must carry zero "
            f"weight on convergence")
