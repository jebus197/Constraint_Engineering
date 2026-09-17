#!/usr/bin/env python3
"""The 97% removal rate must keep reproducing, or the record loses its producer.

`Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md` is where the 4-month suppression
defect was found, and it stated the rate 6 times while naming no script. A
producer now exists. This guard executes it, so the record's figures cannot
quietly stop reproducing -- which is the exact failure the producer was written
to end.

IT RUNS THE SCRIPT. Asserting on the script's source text would confirm only
that the script describes itself consistently.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "scripts" / "immune_removal_rate_exp46_2026-09-17.py"
RECORD = ROOT / "experimental_notes" / "Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md"


@pytest.fixture(scope="module")
def out():
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-800:] + r.stderr[-600:]
    return r.stdout


class TestTheRecordsFiguresReproduce:
    def test_the_population_is_the_one_the_record_names(self, out):
        assert "archived findings: 27" in out
        assert "pairs: 351" in out

    def test_every_declared_figure_matches(self, out):
        lines = [l for l in out.splitlines() if "declared" in l]
        assert len(lines) == 9, f"expected 9 declared figures, saw {len(lines)}"
        differs = [l.strip() for l in lines if "DIFFERS" in l]
        assert not differs, f"the record's figures no longer reproduce: {differs}"

    def test_no_cosine_is_negative(self, out):
        """The whole defect: half the output scale was reserved for a region the
        data never visits. If a negative ever appears, the premise has changed."""
        assert "negative: 0" in out


class TestItReportsRatherThanHides:
    def test_the_unreproduced_figure_is_still_named(self, out):
        """bench/dm/_similarity.py's comment claims clamping gave 15.8%, which
        matches neither scenario. A producer that dropped the figure it cannot
        reproduce would read as though everything checked out."""
        assert "UNREPRODUCED" in out and "15.8%" in out

    def test_the_two_scenarios_are_distinguished(self, out):
        """0.520 and 0.541 are both correct, for different sets. Collapsing them
        into a contradiction was an error made while writing this producer."""
        assert "HYPOTHETICAL" in out and "ACTUAL" in out


class TestTheRecordPointsAtIt:
    def test_the_record_names_the_producer(self):
        assert PRODUCER.name in RECORD.read_text(encoding="utf-8"), (
            "the record no longer names its producer, so a reader meeting the "
            "97% figure has no way to check it")

    def test_the_transcript_itself_was_not_rewritten(self):
        t = RECORD.read_text(encoding="utf-8")
        assert "Nothing above this line has been altered" in t
        assert t.index("Addendum, 2026-09-17") > t.index("Q6. THE 97%"), (
            "the addendum must sit after the transcript, not inside it")
