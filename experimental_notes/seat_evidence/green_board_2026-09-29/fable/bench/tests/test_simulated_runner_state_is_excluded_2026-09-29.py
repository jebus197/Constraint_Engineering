# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'green_board_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3a81ccbeec17a0341cdc4ff62da5f0bb7c99f1d9dd8757bce5ec5d4f28eecf0a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A simulated run's runner_state.json must not witness the archive.

FOUND 2026-09-29 (panel, item 2/3 of the green-board brief), diagnosed to root
cause rather than to the failing assertion. The quarantine-rule test reported
`critical_boundary_census: verdict SILENT_BUT_RAN but first_committed=1788252544
against newest archive mtime 1787788906`. Neither the rule nor the archive's
dates were wrong, and no row is excluded here to make anything green. The
recorded verdict was wrong, and the corruption was one step upstream, in the
evidence base:

  * `_is_simulated` read three authoritative signals -- `severity_provenance`,
    `_simulated`, and the top-level `models` list -- plus the directory name.
  * A `runner_state.json` is report-shaped (`runner_version` + `registry`) so
    it enters `_archive()`, and it carries NONE of those three keys.
  * The 4 `commissioning_arm*` rehearsals of 2026-09-21/22 are simulated
    (their sibling reports say `severity_provenance: "simulated"`, every model
    label ends `-SIM`) -- but "commissioning" defeats the directory heuristic,
    so each rehearsal's runner_state.json was ADMITTED, and the age baseline
    moved 26 days forward on a rehearsal. The audit's own words: a simulated
    run is a rehearsal of the machinery, not a sighting in the field.

The fix reads the model labels the state file DOES carry, runner-written, in
its per-model instrument blocks (`itc_model_state`, `novelty_counts_per_model`,
`raw_counts_per_model`). Parse first, classify second -- no text window.

EXECUTE, DO NOT GREP: every test below drives `_is_simulated` / `_archive`
against real files on disk or constructed documents; none asserts on source.
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import latent_control_audit as A  # noqa: E402

#: The rehearsal that actually moved the baseline (mtime 1790060648,
#: 2026-09-22) while the newest REAL report sits at 1787788906 (2026-08-27).
ARM4_STATE = (REPO / "bench" / "logs"
              / "commissioning_arm4_prose_20260922T053349Z" / "runner_state.json")
#: A real run's state file: the exclusion must not eat genuine evidence.
REAL_DIRS = sorted((REPO / "bench" / "logs").glob("exp*"))


class TestTheRealFilesOnDisk:
    """Assert admission and exclusion on files on disk, not a copy of the rule
    -- the same standard TestTheProvenanceRuleIsCheckedAgainstRealFiles set."""

    def test_every_commissioning_state_file_is_excluded(self):
        states = sorted((REPO / "bench" / "logs")
                        .glob("commissioning_*/runner_state.json"))
        if not states:
            pytest.skip("no commissioning rehearsals in this checkout")
        admitted = []
        for fp in states:
            doc = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
            if not A._is_simulated(doc, fp):
                admitted.append(str(fp.relative_to(REPO)))
        assert admitted == [], (
            "simulated runner_state.json admitted as archive evidence -- the "
            f"age baseline is movable by a rehearsal again: {admitted}")

    def test_the_commissioning_reports_stay_excluded_too(self):
        """The sibling reports were already caught by severity_provenance;
        pinned so the state-file fix cannot regress the report path."""
        reports = sorted((REPO / "bench" / "logs")
                         .glob("commissioning_*/*report*.json"))
        if not reports:
            pytest.skip("no commissioning rehearsals in this checkout")
        for fp in reports:
            doc = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
            assert A._is_simulated(doc, fp), fp.name

    def test_a_real_runs_state_file_is_still_admitted(self):
        """The unsafe direction of the same fix, checked: widening the
        exclusion must not shrink the REAL evidence base."""
        checked = 0
        for d in REAL_DIRS:
            fp = d / "runner_state.json"
            if not fp.is_file():
                continue
            try:
                doc = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
            except ValueError:
                continue
            if not isinstance(doc, dict):
                continue
            assert not A._is_simulated(doc, fp), (
                f"{fp.relative_to(REPO)}: a REAL run's state file is now "
                "classified simulated -- the evidence base shrank")
            checked += 1
        assert checked > 0, "no real runner_state.json found to test against"

    def test_the_baseline_is_not_movable_by_a_rehearsal(self):
        """THE CONSEQUENCE, executed end to end: the newest admitted mtime out
        of `_archive()` must not reach the newest simulated artefact. This is
        the exact disagreement that took the quarantine-rule test red: the
        test's mirror said 2026-08-27 and the audit said 2026-09-22."""
        _, newest = A._archive()
        newest_sim = 0
        for pat in ("commissioning_*/*.json", "sim*/*.json"):
            for fp in (REPO / "bench" / "logs").glob(pat):
                newest_sim = max(newest_sim, int(fp.stat().st_mtime))
        if not newest_sim:
            pytest.skip("no simulated artefacts in this checkout")
        # Every real report predates the newest simulated artefact in this
        # archive (2026-08-27 vs 2026-09-22), so an admitted rehearsal is
        # visible as newest >= newest_sim.
        assert newest < newest_sim, (
            f"_archive() newest mtime {newest} reaches the newest simulated "
            f"artefact {newest_sim}: a rehearsal is in the witness set")


class TestTheConstructedBoundary:
    """The rule itself, pinned from both sides on constructed documents."""

    def test_a_state_shaped_doc_with_sim_model_blocks_is_simulated(self):
        doc = {"runner_version": "v3.2", "registry": {"entries": {}},
               "itc_model_state": {"CC2-SIM": {}, "Gemini-SIM": {}}}
        fake = REPO / "bench" / "logs" / "rehearsal_x" / "runner_state.json"
        assert A._is_simulated(doc, fake)

    def test_a_state_shaped_doc_with_live_model_blocks_is_not(self):
        doc = {"runner_version": "v3.2", "registry": {"entries": {}},
               "itc_model_state": {"CC2": {}, "Gemini": {}},
               "novelty_counts_per_model": {"CC2": 3}}
        fake = REPO / "bench" / "logs" / "exp98_real" / "runner_state.json"
        assert not A._is_simulated(doc, fake)

    def test_prose_mentioning_sim_still_does_not_exclude(self):
        """The 2026-09-02 repair is not undone: a real report QUOTING -SIM in
        a finding stays admitted. The new check reads dict KEYS the runner
        writes, never prose values."""
        doc = {"converged_at": 3, "runner_version": "v3.2",
               "registry": {"entries": {"C0001": {
                   "description": "routing.py mislabels CC2-SIM seats"}}}}
        fake = REPO / "bench" / "logs" / "exp99_pretend" / "r.json"
        assert not A._is_simulated(doc, fake)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
