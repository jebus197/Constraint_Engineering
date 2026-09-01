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
#: Newest archived report mtime at 2026-09-01 07:19:13, immediately before
#: the canary run landed and moved the baseline ten hours forward.
PRE_CANARY_BASELINE = 1788247153
#: First commit epoch for a long-lived report key, established from git
#: INDEPENDENTLY of the audit. Pinning it closes the hole fable found in panel
#: review: `test_the_quarantine_rule_holds_for_every_row` recomputes the
#: expected verdict from `first_committed` taken out of the tool's OWN output,
#: so it is self-consistent by construction and cannot detect a corrupted
#: provenance function. Mutating `min(stamps)` to `max(stamps)` in
#: `_key_first_committed` survived the whole suite while flipping 3 of 50
#: verdicts -- including `target_hashes`, the witness key from the original
#: refutation, quarantined by a corrupted date with nothing going red.
REGISTRY_KEY_FIRST_COMMIT = 1776397305
SCRIPT = REPO / "scripts" / "latent_control_audit.py"


def _newest_archive_mtime() -> int:
    """Newest mtime among archived run reports -- the audit's own age baseline.

    Mirrors scripts/latent_control_audit.py:_archive(). Kept here rather than
    imported because the test must be able to detect the audit drifting away
    from the rule it claims to apply.
    """
    newest = 0
    for fp in (REPO / "bench" / "logs").glob("**/*.json"):
        # Mirror the audit's simulated-run exclusion. Re-implemented rather than
        # imported: the test must be able to catch the audit drifting away from
        # the rule it claims to apply. Before 2026-09-01 the audit's own filter
        # was a dead conditional and excluded nothing, so this baseline and the
        # audit's disagreed and the rule test went red for the wrong reason.
        name = fp.parent.name.lower()
        if name.startswith("sim") or "_sim" in name or "simulated" in name:
            continue
        try:
            raw = fp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "-SIM" in raw[:4000]:
            continue
        try:
            d = json.loads(raw)
        except Exception:                                     # noqa: BLE001
            continue
        if isinstance(d, dict) and ("registry" in d or "converged_at" in d
                                    or "runner_version" in d):
            newest = max(newest, int(fp.stat().st_mtime))
    return newest


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

    def test_the_quarantine_rule_holds_for_every_row(self, result):
        """TOO_NEW iff the key post-dates the newest archived run. Always true.

        REWRITTEN 2026-09-01, having gone red the same day it was written. The
        original asserted that SOMETHING is currently TOO_NEW, which is a
        transient, not an invariant: it held only while the newest archived run
        pre-dated that day's three new keys. The canary run then landed in
        bench/logs, moved the baseline forward by roughly ten hours, and the
        quarantine set correctly emptied -- so a test meant to prove the age
        control works failed *because the age control worked*.

        The invariant is the rule itself, and it is checkable in any archive
        state including an empty one.
        """
        newest = _newest_archive_mtime()
        for row in result["rows"]:
            first = row.get("first_committed")
            expected_too_new = bool(first and newest and first > newest)
            assert (row["verdict"] == "TOO_NEW") == expected_too_new, (
                f"{row['key']}: verdict {row['verdict']} but first_committed="
                f"{first} against newest archive mtime {newest}. The quarantine "
                f"rule and the reported verdict disagree.")

    def test_the_dating_function_is_checked_against_git_not_itself(self):
        """The provenance input must be pinned independently, or it self-certifies.

        Found by fable, 2026-09-01: mutating `min(stamps)` to `max(stamps)` in
        `_key_first_committed` left all eight tests green while flipping three
        verdicts, because every other test reads `first_committed` out of the
        audit's own output and re-applies the comparison to it. Commissioning
        the comparison is not commissioning its input.

        `registry` is a long-lived key whose first and last commits are years
        apart, so min and max are far apart and the mutation cannot hide.
        """
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--as-of", str(PRE_CANARY_BASELINE)],
            cwd=str(REPO), capture_output=True, text=True, timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        rows = {r["key"]: r for r in json.loads(out.stdout)["rows"]}
        row = rows.get("registry")
        assert row is not None, "the runner no longer writes a `registry` key"
        assert row["first_committed"] == REGISTRY_KEY_FIRST_COMMIT, (
            f"`registry` is dated {row['first_committed']}, not "
            f"{REGISTRY_KEY_FIRST_COMMIT} as git reports. The dating function "
            f"is returning the wrong end of the commit range -- every age "
            f"verdict in this tool is computed from it.")

    def test_the_control_can_be_made_to_fire_on_demand(self):
        """COMMISSIONING. Pin the baseline and require quarantine to happen.

        The previous two versions of this test both passed while the age control
        was disabled outright. The first asserted a transient; the second
        asserted an invariant that holds vacuously whenever nothing is new. A
        mutation test on 2026-09-01 (`too_new = False`) left all nine green.

        This drives the control instead of observing it: pinned to the archive as
        it stood at 07:19:13 on 2026-09-01, the three keys committed later that
        day MUST be quarantined. That is a statement about a fixed past, so it
        cannot go quiet, and it fails the moment the rule stops being applied.
        """
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--as-of", str(PRE_CANARY_BASELINE)],
            cwd=str(REPO), capture_output=True, text=True, timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        d = json.loads(out.stdout)
        assert d["baseline_mtime"] == PRE_CANARY_BASELINE
        quarantined = {r["key"] for r in d["rows"] if r["verdict"] == "TOO_NEW"}
        for key in ("gamma_threshold_profile", "severity_admissibility",
                    "critical_boundary_census"):
            assert key in quarantined, (
                f"{key} was committed after {PRE_CANARY_BASELINE} and must be "
                f"quarantined at that baseline. Quarantined set: "
                f"{sorted(quarantined)}. If this is empty the age control is "
                f"not being applied at all.")

    def test_an_old_baseline_quarantines_nothing(self):
        """The other direction: with a baseline far in the future, nothing is new."""
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--as-of", "4102444800"],  # 2100
            cwd=str(REPO), capture_output=True, text=True, timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        d = json.loads(out.stdout)
        assert not [r for r in d["rows"] if r["verdict"] == "TOO_NEW"], (
            "keys are quarantined against a year-2100 baseline, so the "
            "comparison is not the one the rule claims")

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
