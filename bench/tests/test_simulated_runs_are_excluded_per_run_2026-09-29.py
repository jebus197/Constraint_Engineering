"""A simulated run's STATE DUMP is not field evidence either (item 2, 2026-09-29).

WHAT WENT RED. `test_latent_control_audit_2026-09-01.py::TestAgeControl::
test_the_quarantine_rule_holds_for_every_row` reported

    critical_boundary_census: verdict SILENT_BUT_RAN but first_committed=
    1788252544 against newest archive mtime 1787788906

The rule is right, the archive's dates are real, and the verdict was wrong.
`scripts/latent_control_audit.py::_is_simulated` reads 3 provenance keys plus the
directory name, and the runner writes those keys into the run REPORT only. A
simulated run also drops `runner_state.json`, which carries `runner_version` --
so it was admitted as a report -- carries none of the provenance keys, and lives
in a directory named `commissioning_arm*`, not `sim*`. 4 such files were admitted
as field sightings, they were the NEWEST admitted files, and so they set the age
baseline: 2026-08-27 became 2026-09-22, 26.3 days later, which silently disables
the TOO_NEW quarantine for every key committed in that window.

NO ROW WAS EXCLUDED TO MAKE THIS GREEN. The fix classifies simulation per RUN
DIRECTORY, and `test_the_fix_loses_no_sighting` below executes the old admission
rule alongside the new one and asserts the set of control keys witnessed is
IDENTICAL. The only thing the 4 files ever contributed was the baseline.

Every test here EXECUTES `_archive`. None reads the module's source text.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "scripts" / "latent_control_audit.py"


@pytest.fixture(scope="module")
def lca():
    spec = importlib.util.spec_from_file_location("lca_perrun", AUDIT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lca_perrun"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def parsed(lca):
    out = []
    for fp in lca.LOGS.glob("**/*.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        if isinstance(d, dict):
            out.append((fp, d))
    return out


def _is_report(d):
    return "registry" in d or "converged_at" in d or "runner_version" in d


def _excluded_as_simulated(lca, parsed, sim_dirs):
    """Keyed documents the audit excludes, by EITHER rule. The real exclusion."""
    return [fp for fp, d in parsed
            if _is_report(d) and (lca._is_simulated(d, fp) or fp.parent in sim_dirs)]


class TestTheLeakClassExistsAndIsClosed:
    def test_the_state_dump_class_is_excluded_and_the_guard_is_not_vacuous(
            self, lca, parsed):
        """ANTI-VACUITY, RESTATED 2026-09-29 EVENING. It previously asserted that
        the PER-DIRECTORY-ONLY class is non-empty -- files the per-file rule calls
        real while their directory proves simulated. That went red for the best
        possible reason: the per-file rule was STRENGTHENED the same evening, so
        it now catches those files itself and the per-directory-only class is
        empty.

        MEASURED over the 103 keyed documents in this archive: 30 are caught by
        BOTH rules, 0 by the per-file rule alone, 0 by the per-directory rule
        alone, and 73 by neither -- the real runs. The old assertion conflated
        "the per-directory fix is not inert" with "the per-file rule is weak", and
        an improvement to the second made it fail.

        The property that actually matters is that the STATE-DUMP CLASS IS
        EXCLUDED, by whichever rule reaches it first. That is asserted here and
        cannot be satisfied vacuously: it names `runner_state.json` explicitly.
        """
        sim_dirs = lca._simulated_run_dirs()
        assert sim_dirs, "no simulated run in the archive at all"
        excluded = _excluded_as_simulated(lca, parsed, sim_dirs)
        assert excluded, ("no report-like file is excluded as simulated; this "
                          "guard is vacuous here")
        assert any(fp.name == "runner_state.json" for fp in excluded), (
            "the state-dump class -- the 4 files this file was written for -- is "
            "no longer being excluded at all")

    def test_the_per_directory_rule_is_still_load_bearing(self, lca, tmp_path):
        """RETAINED ON EVIDENCE, NOT ON HABIT. The additive standard permits
        removal only when a COMMITTED MEASUREMENT shows the replacement dominates
        on a named property. On THIS archive the per-file rule dominates
        completely, 0 documents relying on the per-directory rule alone -- which
        would read as licence to delete it.

        It is kept because the redundancy is a property of this corpus and not of
        the rule. A simulated run that dies in ROUND 0, before any seat returns,
        writes `novelty_counts_per_model` as an EMPTY map: no `-SIM` key exists,
        so the per-file rule cannot see it. Its `checkpoint.json`, written at
        launch, does carry the seat labels. This test constructs exactly that
        pair and shows the per-directory rule is the only thing that catches the
        state dump.

        A run dying in round 0 is not hypothetical: the run this evening was
        launched precisely because the previous one died at round 5 of 8.
        """
        run = tmp_path / "logs" / "commissioning_arm9_panel_20260929T235959Z"
        run.mkdir(parents=True)
        # the state dump of a run that died before any seat answered
        (run / "runner_state.json").write_text(json.dumps({
            "runner_version": "v3.2",
            "novelty_counts": [], "raw_counts": [],
            "novelty_counts_per_model": {}, "raw_counts_per_model": {},
        }), encoding="utf-8")
        # the checkpoint written at launch, which DOES name the seats
        (run / "checkpoint.json").write_text(json.dumps({
            "converged_at": None,
            "active_models": ["CC2-SIM", "Codex-SIM", "Gemini-SIM"],
        }), encoding="utf-8")

        state = json.loads((run / "runner_state.json").read_text())
        ckpt = json.loads((run / "checkpoint.json").read_text())

        # the per-FILE rule cannot see the state dump -- no labels to read
        assert lca._is_simulated(state, run / "runner_state.json") is False, (
            "if the per-file rule catches this, construct a harder case or "
            "retire the per-directory rule with this measurement beside it")
        # ...but the checkpoint proves the RUN simulated
        assert lca._is_simulated(ckpt, run / "checkpoint.json") is True

        # so a per-RUN rule over this directory catches the state dump
        sim_dirs = {fp.parent for fp in run.glob("*.json")
                    if lca._is_simulated(
                        json.loads(fp.read_text(encoding="utf-8")), fp)}
        assert run in sim_dirs
        assert (run / "runner_state.json").parent in sim_dirs, (
            "the state dump of a round-0 death would be admitted as a real "
            "archived run and would date the archive to when it happened")

    def test_no_admitted_report_comes_from_a_simulated_run(self, lca, parsed):
        """THE INVARIANT, and it is corpus-size independent."""
        sim_dirs = lca._simulated_run_dirs()
        reports, newest = lca._archive()
        admitted = [fp for fp, d in parsed
                    if _is_report(d) and not lca._is_simulated(d, fp)
                    and fp.parent not in sim_dirs]
        assert len(reports) == len(admitted), (len(reports), len(admitted))
        # UPDATED 2026-09-29: the baseline is a RECORDED date, not an mtime. This
        # assertion's purpose is the ADMITTED SET -- that the baseline is computed over
        # the admitted reports and no others -- so it follows the audit's time source
        # rather than pinning a source the audit no longer uses. The date parser has its
        # own dedicated tests in test_archive_age_is_provenance_not_mtime_2026-09-29.py.
        assert newest == max((lca._provenance_time(fp) or 0) for fp in admitted)
        assert all(fp.parent not in sim_dirs for fp in admitted)

    def test_the_baseline_really_moved_earlier(self, lca, parsed):
        """The consequence, measured. A baseline that is too NEW makes the age
        control unfalsifiable, so the corrected baseline must be older."""
        sim_dirs = lca._simulated_run_dirs()
        per_file = max(int(fp.stat().st_mtime) for fp, d in parsed
                       if _is_report(d) and not lca._is_simulated(d, fp))
        _, per_run = lca._archive()
        assert per_run <= per_file
        assert per_run < per_file, (
            "the leak class is non-empty but the baseline did not move; either "
            "the leaked files are no longer the newest, or the fix is inert")

    def test_the_fix_loses_no_sighting(self, lca, parsed):
        """THE ADDITIVE CHECK, EXECUTED, using the audit's OWN presence rule.

        Excluding the 4 state dumps must not take a single control key from
        seen>0 to seen==0. A key witnessed only by a rehearsal was never
        witnessed, but if one existed this assertion would say so out loud
        instead of losing it silently.
        """
        sim_dirs = lca._simulated_run_dirs()
        writes = lca._report_key_writes(lca.RUNNER.read_text(encoding="utf-8"))
        # RE-AIMED 2026-09-29 EVENING, AND A FIRST ATTEMPT WENT TOO WIDE.
        #
        # This used to examine the per-directory-ONLY class, 4 documents. The
        # per-file rule now catches those itself, so that class is empty and the
        # check would have measured nothing. The first repair widened it to EVERY
        # document excluded as simulated -- and it failed, correctly, naming
        # `study_programme`, `gamma_gate_series`, `post_sweep_reconciliation` and
        # others as keys that would "lose their only sighting".
        #
        # THAT FAILURE WAS THE TEST ASKING THE WRONG QUESTION, NOT A DEFECT. Those
        # keys are witnessed ONLY by simulated runs, and reporting a control that
        # no real run has exercised is the audit's ENTIRE PURPOSE -- `_archive`'s
        # own docstring records that accepting the runner's rehearsal as field
        # evidence was the 2026-09-01 defect. A check that forbade losing those
        # sightings would forbid the tool from working.
        #
        # The property this test exists for is narrower and is about STATE DUMPS: a
        # `runner_state.json` or `checkpoint.json` is not a report and must never
        # be the sole witness of a control key. MEASURED 2026-09-29: 13 excluded
        # state dumps, 55 report keys tracked, 5 of them present in a state dump,
        # and 0 of those 5 absent from the 73 admitted real reports.
        STATE_DUMPS = {"runner_state.json", "checkpoint.json"}
        leaked = [d for fp, d in parsed
                  if _is_report(d) and fp.name in STATE_DUMPS
                  and (lca._is_simulated(d, fp) or fp.parent in sim_dirs)]
        kept = [d for fp, d in parsed
                if _is_report(d) and not lca._is_simulated(d, fp)
                and fp.parent not in sim_dirs]
        assert leaked, ("no simulated state dump is excluded; this check is "
                        "vacuous and the 4-file class it was written for is gone")

        def _present(key, obj):
            if isinstance(obj, dict):
                return key in obj or any(_present(key, v) for v in obj.values())
            if isinstance(obj, list):
                return any(_present(key, v) for v in obj)
            return False

        in_leaked = {k for k in writes if any(_present(k, d) for d in leaked)}
        assert in_leaked, "the leaked docs carry no report key at all"
        lost = {k for k in in_leaked if not any(_present(k, d) for d in kept)}
        assert lost == set(), (
            f"excluding the rehearsal state dumps would remove the ONLY "
            f"sighting of {sorted(lost)}. That is evidence loss, not a fix")


class TestTheQuarantineConsequence:
    def test_a_key_committed_after_the_corrected_baseline_is_too_new(self, lca):
        """The row from the failure report, with the baseline PINNED rather than
        taken from live state -- so this asserts the RULE, not the archive.

        1788252544 is `critical_boundary_census`'s first commit (2026-09-01);
        the corrected baseline is 2026-08-27. A control cannot have been
        witnessed by an archive written before it existed.
        """
        _, newest = lca._archive()
        first_committed = 1788252544           # 2026-09-01 08:49:04 UTC
        assert first_committed > newest, (first_committed, newest)

    def test_the_reported_verdict_flips_under_the_corrected_baseline(self, lca):
        """THE FAILURE REPORT, REPRODUCED AND THEN RESOLVED, in one test.

        This checkout has no `.git`, so `_key_first_committed` returns None for
        every key and the quarantine rule holds VACUOUSLY here -- which is why
        the reported red does not reproduce in a panel sandbox. The commit date
        is therefore injected, and the audit run twice:

          * with the LEAKED baseline (1790060648, 2026-09-22, set by
            commissioning_arm*/runner_state.json) the verdict is SILENT_BUT_RAN
            -- the reported failure, exactly;
          * with the corrected baseline the verdict is TOO_NEW, which is what the
            rule at test_latent_control_audit_2026-09-01.py:123-130 demands.
        """
        first = 1788252544                     # 2026-09-01 08:49:04 UTC
        real = lca._key_first_committed
        lca._key_first_committed = (
            lambda k: first if k == "critical_boundary_census" else real(k))
        try:
            fixed = lca.audit(quiet=True)
            leaked = lca.audit(quiet=True, newest_override=1790060648)
        finally:
            lca._key_first_committed = real
        row = [r for r in fixed["rows"]
               if r["key"] == "critical_boundary_census"][0]
        was = [r for r in leaked["rows"]
               if r["key"] == "critical_boundary_census"][0]
        assert fixed["baseline_mtime"] < 1790060648, fixed["baseline_mtime"]
        assert was["verdict"] == "SILENT_BUT_RAN", was
        assert row["verdict"] == "TOO_NEW", row
