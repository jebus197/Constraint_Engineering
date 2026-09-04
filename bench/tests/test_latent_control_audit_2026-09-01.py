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

    def test_the_comparison_at_the_boundary_is_strict(self):
        """A key committed EXACTLY at the baseline is not newer than it.

        CC2, panel review 2026-09-01: the pinned baseline sits hours from the
        keys' commit times and the negative control sits 74 years away, so
        nothing constrained behaviour AT the boundary -- `>`, `>=` and
        `> newest + 1` were all indistinguishable to this suite. That is the
        same class of untested boundary that produced the 0.70 problem.

        Pinning `registry`'s own commit epoch as the baseline makes the
        comparison decidable: strict `>` leaves it unquarantined, `>=` would
        quarantine it.
        """
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--as-of",
             str(REGISTRY_KEY_FIRST_COMMIT)],
            cwd=str(REPO), capture_output=True, text=True, timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        rows = {r["key"]: r for r in json.loads(out.stdout)["rows"]}
        row = rows["registry"]
        assert row["first_committed"] == REGISTRY_KEY_FIRST_COMMIT
        assert row["verdict"] != "TOO_NEW", (
            "a key committed exactly AT the baseline was quarantined, so the "
            "comparison is >= rather than >. Equal is not newer.")

    def test_one_second_past_the_boundary_does_quarantine(self):
        """The other side of the same boundary, so `>` is pinned from both ends."""
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--as-of",
             str(REGISTRY_KEY_FIRST_COMMIT - 1)],
            cwd=str(REPO), capture_output=True, text=True, timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        rows = {r["key"]: r for r in json.loads(out.stdout)["rows"]}
        assert rows["registry"]["verdict"] == "TOO_NEW", (
            "one second before the key's commit it is genuinely newer than the "
            "archive and must be quarantined; it was not, so the comparison is "
            "slack at the boundary")

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

class TestTheProvenanceRuleIsCheckedAgainstRealFiles:
    """Assert admission and exclusion on files on disk, not a copy of the rule.

    The previous test for this re-implemented the predicate VERBATIM, so it
    could detect drift from the rule but never that the rule was wrong. CC2,
    panel review 2026-09-02: "No test asserts a known-real file is admitted or a
    known-sim file excluded." It passed over both of its counterexamples.

    The rule it was guarding read the first 4,000 characters and excluded
    anything containing "-SIM". Measured: 9 real panel transcripts on disk were
    excluded purely for DISCUSSING simulation, one hitting the marker 76
    characters from the window boundary -- while the runner's own authoritative
    provenance keys sat at character 494,477 and 503,114, far outside the window
    the audit looked in.
    """

    def _classify(self, path: Path):
        import json as _json
        sys.path.insert(0, str(REPO / "scripts"))
        import latent_control_audit as A
        doc = _json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return A._is_simulated(doc, path)

    def test_a_real_run_report_is_admitted(self):
        """The evidence base must not shrink because a reviewer said "-SIM"."""
        reals = [p for p in (REPO / "bench" / "logs").glob("exp*/**/*report*.json")]
        assert reals, "no real experiment reports found to test against"
        wrongly = [p for p in reals if self._classify(p)]
        assert not wrongly, (
            "real run reports classified as simulated:\n  "
            + "\n  ".join(str(p.relative_to(REPO)) for p in wrongly[:6]))

    def test_a_simulated_run_report_is_excluded(self):
        sims = [p for p in (REPO / "bench" / "logs").glob("sim*/**/*report*.json")]
        assert sims, "no simulated reports found to test against"
        missed = [p for p in sims if not self._classify(p)]
        assert not missed, (
            "simulated reports admitted as evidence:\n  "
            + "\n  ".join(str(p.relative_to(REPO)) for p in missed[:6]))

    def test_prose_mentioning_the_marker_does_not_exclude_a_real_run(self):
        """The exact false positive: a real report quoting "-SIM" in a finding."""
        import json as _json
        sys.path.insert(0, str(REPO / "scripts"))
        import latent_control_audit as A
        doc = {"converged_at": 3, "runner_version": "v3.2",
               "registry": {"entries": {"C0001": {
                   "description": "routing.py mislabels CC2-SIM seats"}}}}
        fake = REPO / "bench" / "logs" / "exp99_pretend" / "r.json"
        assert not A._is_simulated(doc, fake), (
            "a real report was excluded for quoting the -SIM marker in a "
            "finding; that is how a run reviewing routing.py excludes itself")

    def test_the_authoritative_key_is_what_decides(self):
        import json as _json
        sys.path.insert(0, str(REPO / "scripts"))
        import latent_control_audit as A
        fake = REPO / "bench" / "logs" / "exp99_pretend" / "r.json"
        doc = {"severity_admissibility": {"severity_provenance": "simulated"}}
        assert A._is_simulated(doc, fake), (
            "the runner writes severity_provenance and the audit must read it "
            "rather than reimplementing a weaker string test")


class TestTheClassificationRuleItselfIsPinned:
    """The verdict the tool calls "actionable" was entirely unpinned.

    CC2, panel review 2026-09-02: mutating `elif w["gated"]:` to
    `elif not w["gated"]:` flips 16 of 51 verdicts -- every AMBIGUOUS and every
    UNREACHABLE -- and the whole suite stayed green. Every existing test
    exercised the AGE control or the witness rule; nothing asserted that a gated
    key without a witness is AMBIGUOUS rather than UNREACHABLE, which is the one
    distinction the tool exists to draw.

    The rule, from the module docstring:
      unconditional write, 0 occurrences        -> UNREACHABLE
      gated write, unconditional sibling seen    -> SILENT_BUT_RAN
      gated write, no sibling, 0 occurrences     -> AMBIGUOUS  (the actionable one)

    These pin one representative of each class against the live tree, so
    inverting the gatedness test cannot pass.
    """

    def test_an_unconditional_unseen_key_is_unreachable(self, result):
        rows = {r["key"]: r for r in result["rows"]}
        row = rows.get("stalled")
        assert row is not None, "`stalled` is no longer written by the runner"
        assert row["verdict"] == "UNREACHABLE", (
            f"`stalled` is written unconditionally and appears in no report, so "
            f"it is unreachable as configured; got {row['verdict']}")
        assert row["gated"] is False

    def test_a_gated_key_with_a_witness_is_silent_not_dead(self, result):
        """REPRESENTATIVE CHANGED 2026-09-04, and the reason matters.

        This used `target_integrity_events`, which was gated at the time. It was
        then made UNCONDITIONAL -- the repair this very script recommends in its
        own header -- so it is no longer a representative of the gated class. The
        RULE is unchanged; only the example moved. `hil_status` is gated, unseen,
        and witnessed by `registry`.
        """
        rows = {r["key"]: r for r in result["rows"]}
        row = rows["hil_status"]
        assert row["verdict"] == "SILENT_BUT_RAN"
        assert row["gated"] is True and row["sibling"], (
            "the witness is what separates a silent guard from a dead one")

    def test_an_unconditional_key_with_a_witness_is_also_silent_not_dead(self, result):
        """The rule widened on 2026-09-04, and this pins the widening.

        The sibling check ran only for gated writes, so an UNCONDITIONAL write
        that was unseen fell through to UNREACHABLE even when a witnessed
        sibling proved the surrounding code had run. That misfired on the
        script's own recommended repair: giving `target_integrity_events` an
        unconditional declaration flipped it from SILENT_BUT_RAN to UNREACHABLE,
        so the tool reported a regression for taking its own advice.

        The age control cannot cover this case. `_key_first_committed` dates the
        KEY NAME with `git log -S`, so a key that has existed for months but
        became unconditional today still reads as old and never reaches TOO_NEW.
        """
        rows = {r["key"]: r for r in result["rows"]}
        row = rows["target_integrity_events"]
        assert row["gated"] is False, (
            "this key is the unconditional representative; if it is gated again "
            "the test above is the one that applies")
        assert row["sibling"], "target_hashes is written beside it, unconditionally"
        assert row["verdict"] == "SILENT_BUT_RAN", (
            f"a witnessed sibling proves the code ran, and that proof does not "
            f"depend on whether THIS write is gated; got {row['verdict']}")

    def test_a_gated_key_without_a_witness_is_ambiguous(self, result):
        """The only actionable verdict, and the one the mutation erased."""
        rows = {r["key"]: r for r in result["rows"]}
        row = rows.get("burst_phases")
        assert row is not None, "`burst_phases` is no longer written"
        assert row["verdict"] == "AMBIGUOUS", (
            f"a gated key with no unconditional sibling and no sightings is "
            f"genuinely ambiguous -- it is the only class needing work; got "
            f"{row['verdict']}")
        assert row["gated"] is True and not row["sibling"]

    def test_the_three_classes_are_all_populated(self, result):
        """If any class empties, one of the pins above is silently vacuous."""
        from collections import Counter
        c = Counter(r["verdict"] for r in result["rows"])
        for verdict in ("UNREACHABLE", "SILENT_BUT_RAN", "AMBIGUOUS", "SEEN"):
            assert c[verdict] > 0, f"no key classified {verdict}"


class TestItOverReportsRatherThanUnderReports:
    def test_the_output_does_not_claim_work_it_never_did(self, result):
        """It used to announce `aliases_applied` while applying nothing.

        fable, 2026-09-02: the map "is never applied -- the docstring's alias
        resolution design constraint is echoed into output and enforced by
        nothing." And the test that guarded it asserted the ECHO rather than the
        behaviour, which is exactly how it survived a review.

        Alias resolution is a real constraint for a CONFIG-FLAG audit. This tool
        audits REPORT KEYS, which have no legacy aliases, so the honest fix was
        to drop the claim rather than fake the work.
        """
        assert "aliases_applied" not in result, (
            "the output again claims aliases were applied; either apply them or "
            "do not say so")
        assert "report keys" in result.get("audited_object", ""), (
            "the output must name what it actually audits, so nobody imports a "
            "config-flag constraint into it again")

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
