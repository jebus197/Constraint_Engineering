"""A simulated run that DIED cannot be admitted as field evidence.

THE SAME DEFECT FOR THE THIRD TIME, AND THIS IS THE DOOR THE PREVIOUS TWO FIXES
LEFT OPEN.

`scripts/latent_control_audit.py::_archive` admits any document carrying
`registry`, `converged_at` or `runner_version` into the witness set, and takes the
newest admitted document's recorded date as the age baseline. That baseline drives
the TOO_NEW quarantine: a control key committed after the newest archived run
cannot have been witnessed by it.

  * 2026-09-01: `_archive`'s simulated-run filter was `if <cond>: pass` -- a dead
    conditional that excluded nothing, so a simulated report counted as archive.
    Found by fable in panel review.
  * 2026-09-29 (earlier): `_simulated_run_dirs` closed the case where a simulated
    run's `runner_state.json` leaked in, by looking for a SIBLING document in the
    same directory that proves simulation. 4 files, baseline moved 26.3 days.
  * 2026-09-29 (this file): **a run that dies before writing its report has no
    such sibling.** `bench/logs/shakedown_2026-09-29/arm1_harvest/` is the harvest
    of a simulated run that died at round 5 of 8 when its launching session ended.
    It holds no report. `_is_simulated` returned False for its
    `runner_state.json`, `_simulated_run_dirs()` returned 21 directories and not
    that one, and the file was admitted. Recorded provenance 2026-09-29 moved the
    baseline from 2026-08-23 to 2026-09-29 -- **37.0 days** -- and
    `critical_boundary_census`, first committed 2026-09-01, scored SILENT_BUT_RAN
    where the rule says TOO_NEW.

THE REPAIR KEYS ON THE FILE'S OWN CONTENT, not on a sibling, a directory name, or
a report that was never written. `runner_state.json` carries
`novelty_counts_per_model` and `raw_counts_per_model`, and in a simulated run
every KEY of those maps is a `-SIM` seat. The old test read `doc["models"]`, a
LIST, which that file does not have -- so the labels were present the whole time
in a shape nothing looked at.

WHAT THIS FILE DELIBERATELY ALSO PROVES: the prose false positive does not come
back. Reading the first 4,000 characters for the string `-SIM` once excluded 9
real panel transcripts for merely DISCUSSING simulation. Seat labels are read from
named structural fields only.

These tests CALL the classifier (`execute-do-not-grep`, founder ruling
2026-09-04). The one assertion about the live archive runs the real audit.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "latent_control_audit.py"
HARVEST = REPO / "bench" / "logs" / "shakedown_2026-09-29" / "arm1_harvest"

#: 2026-08-23T00:00:00Z — the newest REAL archived run's recorded date.
REAL_NEWEST = 1787443200
#: 2026-09-29T00:00:00Z — the dead simulated harvest's recorded date.
DEAD_SIM_DATE = 1790640000


def _load():
    spec = importlib.util.spec_from_file_location("lca_guard", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lca_guard"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def lca():
    return _load()


#: The shape that actually leaked: per-model MAPS, no `models` list at all.
RUNNER_STATE_SHAPE = {
    "runner_version": "v3.2",
    "novelty_counts": [18, 7],
    "raw_counts": [22, 8],
    "novelty_counts_per_model": {
        "CC2-SIM": [4], "Codex-SIM": [4], "Gemini-SIM": [4],
        "DeepSeek-SIM": [3], "ChatGPT-SIM": [3]},
    "raw_counts_per_model": {
        "CC2-SIM": [5], "Codex-SIM": [5], "Gemini-SIM": [4],
        "DeepSeek-SIM": [4], "ChatGPT-SIM": [4]},
}

CHECKPOINT_SHAPE = {
    "converged": False,
    "converged_at": None,
    "active_models": ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM",
                      "DeepSeek-SIM", "Gemini-SIM"],
}

ROUND_SHAPE = {
    "runner_version": "v3.2",
    "round_idx": 0,
    "model_responses": {"Codex-SIM": "...", "CC2-SIM": "...",
                        "DeepSeek-SIM": "...", "ChatGPT-SIM": "...",
                        "Gemini-SIM": "..."},
}

REAL_RUN_SHAPE = {
    "runner_version": "v3.2",
    "models": ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"],
    "novelty_counts_per_model": {"CC2": [4], "ChatGPT": [3], "Codex": [4],
                                 "DeepSeek": [3], "Gemini": [4]},
    "model_responses": {"CC2": "...", "ChatGPT": "..."},
}


class TestTheInterruptedRunIsRecognisedFromItsOwnContent:
    """No sibling report, no telltale directory name — the file alone."""

    def test_per_model_map_keys_prove_simulation(self, lca):
        assert lca._has_sim_seat_label(RUNNER_STATE_SHAPE) is True

    def test_the_file_that_leaked_is_now_classified_simulated(self, lca):
        """A neutral directory name, so only content can decide."""
        fp = Path("/tmp/commissioning_arm1_panel_20260929T000000Z/runner_state.json")
        assert lca._is_simulated(RUNNER_STATE_SHAPE, fp) is True

    def test_a_truly_neutral_directory_still_works(self, lca):
        fp = Path("/tmp/arm1_harvest/runner_state.json")
        assert lca._is_simulated(RUNNER_STATE_SHAPE, fp) is True, (
            "with no sim marker in the path, the seat labels are the only "
            "evidence — and they are sufficient")

    def test_active_models_list_proves_simulation(self, lca):
        assert lca._has_sim_seat_label(CHECKPOINT_SHAPE) is True
        assert lca._is_simulated(CHECKPOINT_SHAPE, Path("/tmp/x/checkpoint.json")) is True

    def test_model_responses_map_proves_simulation(self, lca):
        assert lca._has_sim_seat_label(ROUND_SHAPE) is True

    def test_lowercase_seat_labels_are_caught(self, lca):
        """The runner writes `-SIM`; a reader must not depend on the case."""
        assert lca._has_sim_seat_label(
            {"active_models": ["cc2-sim", "codex-sim"]}) is True


class TestTheOldRuleWouldHaveMissedIt:
    """ANTI-VACUITY. A guard that passes against the broken code proves nothing."""

    def test_the_old_models_list_test_is_blind_to_the_leaking_shape(self):
        """Reproduces the pre-fix rule EXACTLY and shows it returns False."""
        doc = RUNNER_STATE_SHAPE
        models = doc.get("models") or doc.get("model_labels") or []
        old_verdict = isinstance(models, (list, tuple)) and any(
            isinstance(m, str) and m.upper().endswith("-SIM") for m in models)
        assert old_verdict is False, (
            "the old rule already caught this, so this guard is vacuous")

    def test_and_the_new_rule_catches_it(self, lca):
        assert lca._has_sim_seat_label(RUNNER_STATE_SHAPE) is True

    def test_the_old_rule_and_the_new_one_agree_on_a_real_run(self, lca):
        models = REAL_RUN_SHAPE["models"]
        old_verdict = any(m.upper().endswith("-SIM") for m in models)
        assert old_verdict is False
        assert lca._has_sim_seat_label(REAL_RUN_SHAPE) is False


class TestItCannotExcludeARealRun:
    """The opposite failure, and it has already happened once in this file's
    history: reading prose for `-SIM` excluded 9 real panel transcripts."""

    def test_a_real_runs_labels_are_not_simulated(self, lca):
        assert lca._has_sim_seat_label(REAL_RUN_SHAPE) is False

    def test_prose_mentioning_sim_does_not_exclude_a_real_run(self, lca):
        doc = dict(REAL_RUN_SHAPE)
        doc["findings"] = [{
            "description": "routing.py labels simulated seats CC2-SIM and "
                           "Codex-SIM; the -SIM suffix is mandated for stand-ins.",
        }]
        assert lca._has_sim_seat_label(doc) is False, (
            "a real run DISCUSSING simulation was excluded from its own evidence "
            "base — the 9-transcript false positive, resurrected")
        assert lca._is_simulated(doc, Path("/tmp/exp48_chemistry_live/report.json")) is False

    def test_an_empty_or_odd_document_is_not_simulated(self, lca):
        for doc in ({}, {"models": None}, {"models": "CC2-SIM"},
                    {"active_models": {}}, {"novelty_counts_per_model": []}):
            assert lca._has_sim_seat_label(doc) is False, doc

    def test_a_non_string_label_does_not_crash_it(self, lca):
        assert lca._has_sim_seat_label(
            {"active_models": [None, 3, {"a": 1}]}) is False


class TestTheLiveArchiveIsClean:
    """Executed against the real repository and the real audit."""

    def test_the_dead_harvest_is_in_the_simulated_set(self, lca):
        if not HARVEST.is_dir():
            pytest.skip("the 2026-09-29 harvest is not in this checkout")
        sim = {p.resolve() for p in lca._simulated_run_dirs()}
        assert HARVEST.resolve() in sim

    def test_every_harvest_document_is_classified_simulated(self, lca):
        if not HARVEST.is_dir():
            pytest.skip("the 2026-09-29 harvest is not in this checkout")
        missed = []
        for fp in sorted(HARVEST.glob("*.json")):
            try:
                d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
            except Exception:                                 # noqa: BLE001
                continue
            if not isinstance(d, dict):
                continue
            if not ("registry" in d or "converged_at" in d
                    or "runner_version" in d):
                continue
            if not lca._is_simulated(d, fp):
                missed.append(fp.name)
        assert missed == [], (
            f"{missed} would be admitted as real archived runs and would date "
            f"the archive to when the simulation ran")

    def test_the_baseline_is_not_the_dead_simulations_date(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                             cwd=str(REPO), capture_output=True, text=True,
                             timeout=280)
        assert out.returncode == 0, out.stderr[-800:]
        d = json.loads(out.stdout)
        assert d["baseline_mtime"] != DEAD_SIM_DATE, (
            "the age baseline is the date a SIMULATED run happened to be "
            "harvested; every control key committed before then is silently "
            "released from quarantine")
        assert d["baseline_mtime"] == REAL_NEWEST, (
            f"expected the newest REAL run's recorded date {REAL_NEWEST}, got "
            f"{d['baseline_mtime']}")

    def test_the_quarantine_is_not_empty_at_that_baseline(self):
        """The consequence, stated as a property rather than a count: a baseline
        of 2026-08-23 MUST quarantine keys committed in September."""
        out = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                             cwd=str(REPO), capture_output=True, text=True,
                             timeout=280)
        d = json.loads(out.stdout)
        too_new = {r["key"] for r in d["rows"] if r["verdict"] == "TOO_NEW"}
        assert "critical_boundary_census" in too_new, (
            "critical_boundary_census was first committed 2026-09-01, after the "
            "newest real archived run, so the rule says TOO_NEW")
