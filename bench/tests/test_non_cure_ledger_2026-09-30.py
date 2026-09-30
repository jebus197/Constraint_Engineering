"""The non-cure ledger (founder ruling 2026-09-30) is wired and correct.

Executes `collect_non_cure_ledger` -- the producer the report assembly calls --
against synthetic registry entries. Asserts the three properties the ruling
names: a measured non-cure IS recorded and flagged for HIL inspection; the
ledger neither rejects the finding nor blocks anything (it is informative
only, and the entry's own status travels unmodified); and an empty ledger
still distinguishes "probed, all cured" from "never probed".
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import collect_non_cure_ledger  # noqa: E402

FI = "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"


def test_measured_non_cure_is_recorded_and_hil_inspectable():
    entries = {
        "C1": {"source_model": "m1", "status": "CONFIRMED",
               "fix_efficacy": {"outcome": FI, "detail": "still demonstrates"}},
        "C2": {"source_model": "m2", "status": "CLOSED",
               "fix_efficacy": {"outcome": "FIX_CURES_ITS_OWN_FALSIFIER",
                                "detail": "quiet"}},
        "C3": {"source_model": "m3", "status": "OPEN"},  # never probed
    }
    led = collect_non_cure_ledger(entries)
    assert led["count"] == 1
    rec = led["entries"][0]
    assert rec["canonical_id"] == "C1"
    assert rec["hil_inspect"] is True
    # Neither plain REJECT nor plain ESCALATE: the entry's status is
    # REPORTED, not rewritten, and the source dict is untouched.
    assert rec["status"] == "CONFIRMED"
    assert entries["C1"]["status"] == "CONFIRMED"
    assert led["informative_only"] is True
    # Probed-vs-never-probed is not conflated.
    assert led["entries_probed"] == 2
    assert led["entries_total"] == 3


def test_zero_non_cures_is_not_zero_evidence():
    led_unprobed = collect_non_cure_ledger({"C1": {"status": "OPEN"}})
    led_cured = collect_non_cure_ledger(
        {"C1": {"status": "CLOSED",
                "fix_efficacy": {"outcome": "FIX_CURES_ITS_OWN_FALSIFIER"}}})
    assert led_unprobed["count"] == led_cured["count"] == 0
    assert led_unprobed["entries_probed"] == 0
    assert led_cured["entries_probed"] == 1


def test_empty_registry():
    led = collect_non_cure_ledger({})
    assert led["count"] == 0 and led["entries_total"] == 0
