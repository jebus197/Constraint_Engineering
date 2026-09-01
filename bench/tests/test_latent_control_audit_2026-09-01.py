"""The audit that enumerates controls nobody has seen fire.

Built to CC2's answer to Q3 of the 2026-09-01 panel review: build the static
audit before the next run, because it costs seconds and it independently
rediscovered every latent control that had been found by hand.

These tests pin the two design constraints CC2 named, both of which a draft of
the tool got wrong, and the one refutation the tool exists to make mechanical.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "latent_control_audit.py"


@pytest.fixture(scope="module")
def result():
    out = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                         cwd=str(REPO), capture_output=True, text=True,
                         timeout=280)
    assert out.returncode == 0, out.stderr[-800:]
    return json.loads(out.stdout)


def _row(result, key):
    for r in result["rows"]:
        if r["key"] == key:
            return r
    return None


class TestItReproducesTheRefutation:
    """The error the tool exists to prevent, made mechanical.

    The mid-run target guard was recorded as never having fired, on 0 of 83 run
    directories carrying `target_integrity_events`. That is the violation-gated
    key; the unconditional sibling `target_hashes` sits one line below it. CC2
    caught it by hand. The tool must catch it without being told.
    """

    def test_the_target_guard_is_classified_as_silent_not_dead(self, result):
        row = _row(result, "target_integrity_events")
        assert row is not None, "the guard's key is no longer detected at all"
        assert row["verdict"] == "SILENT_BUT_RAN", (
            f"classified {row['verdict']}; a guard with a witnessed "
            f"unconditional sibling has demonstrably run")
        assert row["sibling"] == "target_hashes"


class TestAgeControl:
    """A key committed today is absent from older runs for a boring reason.

    Without this the tool reports the session's own work as dead code, and gets
    disbelieved the first time anyone runs it.
    """

    def test_keys_committed_after_the_newest_run_are_quarantined(self, result):
        fresh = [r["key"] for r in result["rows"] if r["verdict"] == "TOO_NEW"]
        assert fresh, (
            "nothing is TOO_NEW. Either age control is broken or no key has "
            "been added since the newest archived run -- check before assuming "
            "the second.")

    def test_no_recently_added_key_is_called_unreachable(self, result):
        for r in result["rows"]:
            if r["verdict"] in ("UNREACHABLE", "AMBIGUOUS"):
                assert r["verdict"] != "TOO_NEW"


class TestItOverReportsRatherThanUnderReports:
    def test_the_alias_map_is_carried_in_the_output(self, result):
        """A control enabled under a legacy key must not read as never-enabled."""
        assert result["aliases_applied"].get("take_up_slack_enabled") == \
            "routing_enabled"

    def test_the_archive_was_actually_read(self, result):
        assert result["reports"] > 50, (
            f"only {result['reports']} reports found; the audit's conclusions "
            f"are only as good as the archive it read")

    def test_most_keys_are_seen_and_need_nothing(self, result):
        """A tool that flags everything is a tool nobody runs."""
        seen = sum(1 for r in result["rows"] if r["verdict"] == "SEEN")
        assert seen > len(result["rows"]) / 2, (
            "more than half the runner's report keys are unaccounted for; "
            "that is a tool defect before it is a codebase finding")


def test_help_costs_nothing():
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and "never" in r.stdout.lower()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
