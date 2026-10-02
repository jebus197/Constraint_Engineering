# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b1660f77449099bcd8fa241c3bc68e55f42b4fbab03113695b6b80280e0533d1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A key-access refusal leaves BOTH convergence counters, and is RECORDED.

PANEL ROUND 2, 2026-10-02, disputes D3, D4 and D6. Round 1 produced two
different implementations of the same ruling and each was measured unsafe in a
direction the other covers:

  seat fable  `integrity_unobserved` carve-out, one shared predicate across both
              counters -- and NO record coupled to the exclusion. Its reporting
              channel is the post-run forensics advisory, which is SILENT exactly
              in run 1b's case (all 10 gate refusals there were VOCABULARY
              matches on `seeded_fault`, so the artefact scan finds no access and
              `end_of_run_advisory` returns None). Executed on fable's own
              harvested module: run 1b advisory SILENT. So the critical is
              excused from both counters and nothing says so.

  seat cc2    the paired record and a distinct `integrity_refused` flag -- and NO
              cause carve-out (0 occurrences of any observer check in its
              harvested source), so an observer-did-not-install failure, which is
              machine-wide when it happens, releases every critical and converges
              a run on which nothing was tested. Its record also gates on
              `severity >= 0.7` while the counter it shadows stopped gating on
              severity on 2026-09-06, so a release at severity 0.5 is silent.

They are COMPLEMENTARY, not duplicates and not in conflict. `_integrity_refused`
composes both halves and adds the third thing neither covered: the LADDER-side
field. These tests pin all three, each with an anti-vacuity control.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    INTEGRITY_REFUSED_VERDICT,
    LADDER_VERDICT_FIELD,
    FindingRegistry,
    _integrity_refused,
    _irreducible_queue_split,
)


def test_the_verdict_string_is_pinned_to_the_gates_own_constant():
    """A rename in falsifier_verify must fail a test, not silently un-handle the
    verdict here."""
    from bench.falsifier_verify import INTEGRITY_VIOLATION
    assert INTEGRITY_REFUSED_VERDICT == INTEGRITY_VIOLATION


class _Reg:
    """The registry fixture shape test_panel_five_fixes_2026-09-07.py uses: a
    plain object owning only `.entries`, so the unbound readers can be borrowed
    onto it without constructing a runner."""

    def __init__(self, entries):
        self.entries = entries

    integrity_refused_criticals = FindingRegistry.integrity_refused_criticals
    unverified_critical_count = FindingRegistry.unverified_critical_count


def _entry(**kw):
    e = {"status": "UNCONFIRMED", "severity": 0.8, "falsifier_verdict": ""}
    e.update(kw)
    return e


# ── the release, both counters, one predicate ────────────────────────────────

def test_a_key_access_refusal_leaves_both_counters_and_lands_in_the_record():
    reg = _Reg({"C0001": _entry(falsifier_verdict=INTEGRITY_REFUSED_VERDICT)})
    assert _irreducible_queue_split(reg.entries) == (0, 0)
    assert reg.unverified_critical_count() == 0
    assert reg.integrity_refused_criticals() == ["C0001"], (
        "released from both counters and invisible to every reader -- this is "
        "the silent false convergence, not a fix"
    )


def test_without_the_refusal_it_still_blocks_so_the_test_above_is_not_vacuous():
    """THE CONTROL. A test asserting `count == 0` passes just as well against a
    counter that ignores the verdict outright."""
    reg = _Reg({"C0001": _entry(falsifier_verdict="")})
    assert reg.unverified_critical_count() == 1
    assert reg.integrity_refused_criticals() == []


# ── D3: the cause carve-out (fable's half) ───────────────────────────────────

def test_an_unobserved_run_keeps_blocking():
    """The equipment fault must NOT be released. If a broken sitecustomize made
    every falsifier return INTEGRITY_VIOLATION and this were released, a run
    could converge with zero verified criticals."""
    reg = _Reg({f"C{i:04d}": _entry(falsifier_verdict=INTEGRITY_REFUSED_VERDICT,
                                    integrity_unobserved=True)
                for i in range(1, 6)})
    assert reg.unverified_critical_count() == 5
    assert _irreducible_queue_split(reg.entries) == (0, 0)  # not escalated here
    assert reg.integrity_refused_criticals() == [], (
        "an unobserved run is not a key access and must not be reported as one"
    )


def test_the_carve_out_is_the_only_difference_between_the_two_cases():
    """ANTI-VACUITY for the carve-out: the two entries differ in one key."""
    refused = _entry(falsifier_verdict=INTEGRITY_REFUSED_VERDICT)
    unobserved = dict(refused, integrity_unobserved=True)
    assert _integrity_refused(refused) is True
    assert _integrity_refused(unobserved) is False
    assert set(unobserved) - set(refused) == {"integrity_unobserved"}


# ── D6: the ladder-side refusal neither seat covered ─────────────────────────

def test_a_ladder_side_refusal_is_covered_too():
    """Run 1b's C0029, verbatim from the archive: the ENTRY says CONFIRMED and
    `routing_deferred`, and the refusal exists only at
    `routing_verdict_unreconciled`. Both round-1 predicates read
    `falsifier_verdict` only, so neither saw it and it fed the halt bound."""
    c0029 = _entry(status="OPEN", severity=0.8, falsifier_verdict="UNTOOLABLE",
                   routing_deferred=True,
                   **{LADDER_VERDICT_FIELD: INTEGRITY_REFUSED_VERDICT})
    assert _integrity_refused(c0029) is True
    reg = _Reg({"C0029": c0029})
    assert _irreducible_queue_split(reg.entries) == (0, 0), (
        "the ladder-side refusal is still in the halt bound; run 1b halted at "
        "round 2 with both halves of the convergence gate already satisfied"
    )
    assert reg.integrity_refused_criticals() == ["C0029"]


def test_reading_only_the_entry_verdict_misses_it():
    """ANTI-VACUITY for the field above, stated as the round-1 predicates were."""
    c0029 = _entry(status="OPEN", falsifier_verdict="UNTOOLABLE",
                   routing_deferred=True,
                   **{LADDER_VERDICT_FIELD: INTEGRITY_REFUSED_VERDICT})
    entry_verdict_only = (
        (c0029.get("falsifier_verdict") or "").strip().upper()
        == INTEGRITY_REFUSED_VERDICT)
    assert entry_verdict_only is False, (
        "if this is True the two seats' predicates did cover C0029 and D6's "
        "residual was already closed"
    )


# ── D4/D3: the record must be at least as wide as the release ────────────────

def test_the_record_does_not_gate_on_severity_while_a4_does_not():
    """SEAT cc2's RESIDUAL, EXECUTED. An UNCONFIRMED entry below the severity
    threshold is released by A4 (which stopped gating on severity on 2026-09-06)
    and must therefore also appear in the record. A record narrower than the
    release it documents produces exactly the silence it exists to prevent."""
    low = _entry(severity=0.5, falsifier_verdict=INTEGRITY_REFUSED_VERDICT)
    reg = _Reg({"C0007": low})
    assert low["severity"] < CRITICAL_SEVERITY_THRESHOLD
    control = _Reg({"C0007": _entry(severity=0.5, falsifier_verdict="")})
    assert control.unverified_critical_count() == 1, (
        "A4 must count a low-severity UNCONFIRMED entry, else this test is "
        "measuring nothing"
    )
    assert reg.unverified_critical_count() == 0        # released
    assert reg.integrity_refused_criticals() == ["C0007"]   # and recorded


def test_an_adjudicated_finding_is_not_reported_as_outstanding():
    """Silent means silent. A refusal on a finding that later reached a terminal
    status is resolved and must leave the record, or every converged run carries
    a permanent advisory and the signal stops meaning anything."""
    for status in ("CONFIRMED", "CLOSED", "REFUTED", "DUPLICATE", "MERGED"):
        reg = _Reg({"C0001": _entry(status=status,
                                    falsifier_verdict=INTEGRITY_REFUSED_VERDICT)})
        assert reg.integrity_refused_criticals() == [], status
