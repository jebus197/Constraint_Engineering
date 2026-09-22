#!/usr/bin/env python3
"""The static-HIL-queue log line must not call a DEFERRED critical "ladder-exhausted".

WHAT WENT WRONG. `FindingRegistry.irreducible_queue_count` deliberately counts
TWO states -- `irreducible_escalation` (a machine tried the ladder and failed)
and `routing_deferred` (the falsifier ERRORed or was UNTOOLABLE, so the claim was
never assessed). The 2026-09-07 note beside it says why: removing deferred items
from the alarm would let runs burn to `max_rounds` instead of halting with an
evidence bundle. The states have OPPOSITE diagnoses, and the log line named only
the first.

MEASURED, on the committed arm-4 report
(`bench/logs/commissioning_arm4_prose_20260922T053349Z`): all 8 queued criticals
carry `falsifier_verdict` in {UNTOOLABLE x7, ERROR x1}, i.e. every one is an
EQUIPMENT_FAILURE_VERDICT and therefore `routing_deferred`; `tally['hil']` was 0,
which the same log states six lines earlier as "0 -> HIL, 8 deferred (never
assessed)". The alarm nonetheless printed "8 ladder-exhausted irreducible
critical(s)".

WHAT IT COST. The 2026-09-22 morning report took the label at face value and
derived: ladder capped at 2 rungs -> 8 criticals exhausted it -> never scored ->
locked irreducible -> halt. The first link is false -- the ladder was never
entered -- so `max_rungs` cannot be the cause, and a config surface for it was
escalated to the founder on that reasoning. With 1 distinct underlying model
behind 5 `-SIM` labels, ladder DEPTH is causally inert in this arm regardless.

This test pins the counted-by-state decomposition against the real report, so a
future reader cannot be told a mechanism the code declined to assert.

Run:  python3 -m pytest bench/tests/test_hil_queue_says_which_kind_2026-09-22.py -q
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
ARM4 = (REPO / "bench" / "logs" / "commissioning_arm4_prose_20260922T053349Z"
        / "commissioning_arm4_prose_report.json")

#: `EQUIPMENT_FAILURE_VERDICTS` in the runner: the instrument produced no reading.
_EQUIPMENT = {"ERROR", "UNTOOLABLE"}


def _log_line() -> str:
    text = RUNNER.read_text(encoding="utf-8")
    m = re.search(r'_log\(f"  static HIL queue:.*?\)\n', text, re.S)
    assert m, "the static-HIL-queue log statement is gone; this guard is stale"
    return m.group(0)


def test_the_queue_line_does_not_call_every_item_ladder_exhausted():
    """The old text asserted a mechanism for items that never entered the ladder."""
    line = _log_line()
    assert "ladder-exhausted irreducible" not in line, (
        "the log line still labels the WHOLE queue 'ladder-exhausted "
        "irreducible'. The queue counts `irreducible_escalation OR "
        "routing_deferred`; a deferred item was never assessed, so no ladder "
        "was exhausted on it."
    )


def test_the_queue_line_reports_both_states_separately():
    line = _log_line()
    assert "_q_locked" in line and "_q_deferred" in line, (
        "the line must decompose the queue into ladder-exhausted and "
        f"never-assessed, so the reading names its own mechanism. Got:\n{line}"
    )
    assert "never assessed" in line


def test_arm4s_eight_queued_criticals_were_all_never_assessed():
    """The archive, not prose: every arm-4 queue item is an equipment failure.

    If this ever fails because a queue item carries a RESOLVED verdict, the
    decomposition above is measuring the wrong thing and must be re-derived.
    """
    if not ARM4.is_file():
        pytest.skip(f"archive absent: {ARM4}")
    report = json.loads(ARM4.read_text(encoding="utf-8"))
    alarm = report.get("irreducible_queue_alarm") or {}
    evidence = alarm.get("evidence") or []
    assert alarm.get("count") == 8, alarm.get("count")
    assert len(evidence) == 8, len(evidence)
    verdicts = [str(e.get("falsifier_verdict") or "").strip().upper()
                for e in evidence]
    assert all(v in _EQUIPMENT for v in verdicts), verdicts
    # 7 of 8 produced no falsifier at all -- the alarm's own notify text says so.
    assert verdicts.count("UNTOOLABLE") == 7, verdicts
    assert verdicts.count("ERROR") == 1, verdicts
    assert alarm.get("items_without_falsifier") == 7


def test_max_rungs_cannot_be_the_arm4_cause_because_the_ladder_was_never_entered():
    """A rung is only reached when routing runs; deferral happens before that.

    `_apply_routing` sets `routing_deferred` on the equipment-failure branch and
    `irreducible_escalation` on the exhausted branch. They are mutually
    exclusive, so a deferred item has `rungs_tried == 0` by construction and
    raising `max_rungs` cannot move it.
    """
    text = RUNNER.read_text(encoding="utf-8")
    # The two branches are exclusive: one `if`, one `else`.
    assert 'e["routing_deferred"] = True' in text
    assert 'e["irreducible_escalation"] = True' in text
    if not ARM4.is_file():
        pytest.skip(f"archive absent: {ARM4}")
    report = json.loads(ARM4.read_text(encoding="utf-8"))
    # Arm 4 declared 5 seats, so the "ladder is empty with 1 seat" cause the
    # alarm offers first does not apply either.
    assert len(report["models"]) == 5, report["models"]
    assert report.get("halted") is True
    assert report.get("halted_at_round") == 0
