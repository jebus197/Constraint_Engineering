"""Latent-tagger — the producer severity calibration was missing (2026-07-31).

These tests exercise the tagger WHERE IT LIVES: against the real
``FindingRegistry``, the real ``_is_demotion_eligible`` / ``_calibrate_finding_
severity`` / ``_apply_severity_calibration``, the real convergence gate, and —
in ``TestAgainstArchivalCorpus`` — the real 293 findings from the six completed
live runs. A tagger that passes in isolation and misbehaves next to the falsifier
gate would be the fifth control in a row to break on contact, so the isolation
tests here are the minority and the integration tests are the point.

Both regression classes below were found by auditing what the tagger actually
demoted on the corpus, not by writing tests against the design:

  * ``test_never_reached_describing_the_bug_is_not_latent`` — Exp 47 C0024.
  * ``test_plural_wrong_results_still_hits_the_interlock`` — same finding.
"""

from __future__ import annotations

import copy
import glob
import json
import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bench.latent_tagger import (  # noqa: E402
    NEVER_DEMOTE_CATEGORIES,
    classify_category,
    tag_entry,
    tag_registry,
)
from bench.reference_runner_v2 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _apply_severity_calibration,
    _estimate_gamma,
    _is_demotion_eligible,
    _settled_novelty_series,
)

ARCHIVAL_GLOB = os.path.join(
    _ROOT, "bench", "logs", "exp4[4-9]_*", "exp*_report.json"
)


def _entry(**kw):
    e = {
        "canonical_id": "C0001",
        "severity": 0.85,
        "description": "Some defect in the parser.",
        "proposed_fix": "",
        "falsifier_verdict": "CONFIRMED",
        "status": "CONFIRMED",
        "open_since_round": 0,
    }
    e.update(kw)
    return e


def _cfg(**kw):
    cfg = RunnerConfig(experiment_name="latent", models=["CC2"])
    for k, v in kw.items():
        setattr(cfg, k, v)
    return cfg


# ── Fail-safe: silence means reachable ──────────────────────────────────────


class TestFailSafe:
    def test_no_evidence_means_not_latent(self):
        e = _entry(description="`parse()` drops the final token when n is odd.")
        assert tag_entry(e) is False
        assert e["latent"] is False
        assert e["latent_source"] == "default_reachable"

    def test_every_entry_gets_a_tag_and_a_category(self):
        e = _entry()
        tag_entry(e)
        assert "latent" in e and "finding_category" in e
        assert "latent_source" in e and "latent_evidence" in e

    def test_external_adjudication_outranks_the_classifier(self):
        """A HIL or upstream cell that already ruled is not overwritten."""
        e = _entry(latent=True, description="No latency language whatsoever.")
        assert tag_entry(e) is True
        assert e["latent_source"] == "external"

    def test_tagging_is_idempotent(self):
        e = _entry(description="module is shadow/observation-only")
        first = tag_entry(e)
        snapshot = dict(e)
        assert tag_entry(e) == first
        assert e["latent"] == snapshot["latent"]


# ── Source 1: the explicit field a schema change would supply ───────────────


class TestExplicitField:
    @pytest.mark.parametrize("line", [
        "REACHABILITY: no in-repo caller reaches this branch",
        "TRIGGER: non-default configuration only",
        "LATENT: true",
    ])
    def test_explicit_latent_field_is_honoured(self, line):
        e = _entry(description=f"F001 defect.\n{line}\nFIND: ...")
        assert tag_entry(e) is True
        assert e["latent_source"] == "explicit_field"

    @pytest.mark.parametrize("line", [
        "REACHABILITY: reachable from the default ingestion path",
        "TRIGGER: any call to verify()",
        "LATENT: false",
    ])
    def test_explicit_reachable_field_blocks_the_tag(self, line):
        e = _entry(description=f"F001 defect.\n{line}\nFIND: ...")
        assert tag_entry(e) is False

    def test_explicit_field_outranks_prose(self):
        e = _entry(description=(
            "REACHABILITY: reachable on the live path\n"
            "The module is shadow/observation-only."
        ))
        assert tag_entry(e) is False


# ── Source 2: prose, and the traps it sets ──────────────────────────────────


class TestProseMarkers:
    def test_shadow_only_module_is_latent(self):
        e = _entry(description="Module is shadow/observation-only and never gates.")
        assert tag_entry(e) is True
        assert e["latent_source"] == "prose"

    def test_no_caller_is_latent(self):
        e = _entry(description="There is no in-repo caller for this overload.")
        assert tag_entry(e) is True

    # ── regression: Exp 47 C0024 ────────────────────────────────────────
    def test_never_reached_describing_the_bug_is_not_latent(self):
        """"never reached" is usually the DEFECT, not a reason to discount it.

        Exp 47 C0024, severity 0.75, falsifier CONFIRMED: "silently wrong
        results; the severe penalty tier is never reached". The tier was
        supposed to fire. An earlier marker set read that as a latency claim
        and demoted a demonstrated critical.
        """
        e = _entry(severity=0.75, description=(
            "SEVERITY: 0.75 (HIGH — silently wrong results; the severe "
            "penalty tier is never reached) FLAW_CLASS: 5"
        ))
        assert tag_entry(e) is False, "dead-code-as-bug must not read as latent"

    @pytest.mark.parametrize("phrase", [
        "the else branch is unreachable",
        "this validation is never invoked",
        "the handler is never called",
        "this is dead code",
    ])
    def test_ambiguous_dead_code_phrases_do_not_tag(self, phrase):
        assert tag_entry(_entry(description=phrase)) is False

    # ── regression: falsifier boilerplate ───────────────────────────────
    @pytest.mark.parametrize("phrase", [
        "This script prints FALSIFIED only if the defect is present.",
        "Exits clean otherwise; fails only if CH-27 claims argon shifts yield.",
        "Raises AssertionError if and only if the target still contains it.",
    ])
    def test_falsifier_boilerplate_does_not_tag(self, phrase):
        """The dominant false positive for any conditional-language matcher:
        3 of the 4 corpus-wide hits on a naive marker set were this idiom."""
        assert tag_entry(_entry(description=phrase)) is False

    def test_falsifier_code_is_not_read(self):
        """Reachability inferred from the falsifier's source was REFUTED on the
        corpus (test scaffolding, not usage contract). It must stay unread."""
        e = _entry(
            description="Defect on the ingestion path.",
            falsifier_code="store._chain = FakeChain()  # no caller does this",
        )
        assert tag_entry(e) is False


# ── The never-demote interlock ──────────────────────────────────────────────


class TestCategoryInterlock:
    @pytest.mark.parametrize("text,expected", [
        ("SQL injection via unsanitised input", "security"),
        ("silently drops the last record", "data_loss"),
        ("unsafe under concurrent access", "safety"),
        ("produces a wrong result for n=0", "core_functionality"),
        ("corrupts the evidence chain", "data_loss"),
        ("renames a local for clarity", ""),
    ])
    def test_classification(self, text, expected):
        assert classify_category(text) == expected

    # ── regression: Exp 47 C0024 ────────────────────────────────────────
    def test_plural_wrong_results_still_hits_the_interlock(self):
        """A singular-only pattern let "silently wrong results" through the
        safety veto while "wrong result" caught it — a plural typo in an
        interlock, which is the worst place for one."""
        assert classify_category("silently wrong results") in NEVER_DEMOTE_CATEGORIES
        assert classify_category("wrong values are returned") in NEVER_DEMOTE_CATEGORIES
        assert classify_category("wrong outputs downstream") in NEVER_DEMOTE_CATEGORIES

    def test_latent_plus_never_demote_category_is_not_demoted(self):
        """The veto wins over the latency tag. This is the whole safety story:
        a latent SAFETY defect stays critical."""
        e = _entry(description=(
            "There is no in-repo caller, but it corrupts the evidence chain."
        ))
        assert tag_entry(e) is True
        assert e["finding_category"] in NEVER_DEMOTE_CATEGORIES
        assert _is_demotion_eligible(e) is False


# ── Structural guarantee: the unearned class is unreachable ─────────────────


class TestUnearnedVerdictsAreNeverDemoted:
    @pytest.mark.parametrize("verdict", ["REFUTED", "UNTOOLABLE", "ERROR", ""])
    def test_only_confirmed_is_demotable(self, verdict):
        """Condition (2) of the calibrator. This is why calibration scores zero
        recall against "severity the falsifier never earned": that class is
        defined by NOT being CONFIRMED, and only CONFIRMED is demotable.
        The guard exists because 2 of 3 REFUTED criticals in the Exp 42 audit
        were FALSE refutations masking real defects."""
        e = _entry(falsifier_verdict=verdict,
                   description="no in-repo caller reaches this")
        tag_entry(e)
        assert e["latent"] is True
        assert _is_demotion_eligible(e) is False

    def test_confirmed_and_latent_is_demotable(self):
        e = _entry(falsifier_verdict="CONFIRMED",
                   description="no in-repo caller reaches this")
        tag_entry(e)
        assert _is_demotion_eligible(e) is True


# ── In-system: tagger + calibrator + real convergence gate ──────────────────


class TestInSystem:
    def _registry(self):
        reg = FindingRegistry()
        reg.entries = {
            # round 0: two demonstrated criticals, one of them latent
            "C1": _entry(canonical_id="C1", severity=0.85, open_since_round=0,
                         description="Wrong result for n=0 on the live path."),
            "C2": _entry(canonical_id="C2", severity=0.90, open_since_round=0,
                         description="There is no in-repo caller for this path; "
                                     "the helper is unused surface."),
            # round 1: one demonstrated critical, latent
            "C3": _entry(canonical_id="C3", severity=0.80, open_since_round=1,
                         description="Module is shadow/observation-only, never "
                                     "gates the verdict."),
        }
        return reg

    def test_tagger_off_is_byte_identical(self):
        """The runner call site is gated. With the gate off nothing is written,
        so no entry can become eligible."""
        reg = self._registry()
        before = copy.deepcopy(reg.entries)
        cfg = _cfg(latent_tagger_enabled=False,
                   severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, 1) == 0
        assert reg.entries == before

    def test_tagger_on_calibration_off_changes_no_severity(self):
        """Enabling the producer alone must be observational."""
        reg = self._registry()
        sev_before = {k: v["severity"] for k, v in reg.entries.items()}
        assert tag_registry(reg) == 2
        cfg = _cfg(severity_calibration_enabled=False)
        assert _apply_severity_calibration(reg, cfg, 1) == 0
        assert {k: v["severity"] for k, v in reg.entries.items()} == sev_before

    def test_full_path_demotes_only_the_latent_non_veto_critical(self):
        reg = self._registry()
        tag_registry(reg)
        cfg = _cfg(severity_calibration_enabled=True,
                   severity_calibration_floor=0.69)
        n = _apply_severity_calibration(reg, cfg, 1)
        assert n == 2, "C2 and C3 are latent and uncategorised"
        assert reg.entries["C1"]["severity"] == 0.85, "wrong-result veto held"
        assert reg.entries["C2"]["severity"] == 0.69
        assert reg.entries["C3"]["severity"] == 0.69
        # never deleted, always auditable
        assert reg.entries["C2"]["severity_original"] == 0.90
        assert "latent" in reg.entries["C2"]["calibration_reason"].lower()

    def test_demotion_actually_reaches_the_convergence_series(self):
        """The point of the mechanism: a demoted finding must leave the
        critical-novelty series the gate reads. Uses the real
        _settled_novelty_series, not a stand-in."""
        reg = self._registry()
        _, crit_off = _settled_novelty_series(reg, 1)
        assert crit_off == [2, 1]
        tag_registry(reg)
        _apply_severity_calibration(
            reg, _cfg(severity_calibration_enabled=True), 1)
        _, crit_on = _settled_novelty_series(reg, 1)
        assert crit_on == [1, 0], "demoted criticals must drop out of the series"
        # and that propagates to gamma, which the two-sided gate reads
        assert _estimate_gamma(crit_on, 2) != _estimate_gamma(crit_off, 2)

    def test_ordering_tagger_runs_before_calibration_in_the_round_loop(self):
        """Order is load-bearing: tags written after the sweep would be read a
        round late. Asserts the real call sites, in the real file."""
        src = open(os.path.join(_ROOT, "bench", "reference_runner_v2.py"),
                   encoding="utf-8").read()
        tag_at = src.index("from bench.latent_tagger import tag_registry")
        calib_at = src.index("_sev_calib_n = _apply_severity_calibration")
        verdict_at = src.index(
            "apply_falsifier_verdicts(registry, round_idx, cfg=cfg")
        assert verdict_at < tag_at < calib_at


# ── Both config-ingestion boundaries (the recurring drop bug) ───────────────


class TestConfigIngestion:
    """Five instances to date of a runner flag honoured on one ingestion path
    and silently dropped on the other. Every new flag gets both paths traced."""

    def test_runner_config_from_dict(self):
        cfg = RunnerConfig.from_dict({
            "experiment_name": "x", "models": ["CC2"],
            "latent_tagger_enabled": True,
            "severity_calibration_enabled": True,
            "severity_calibration_floor": 0.5,
        })
        assert cfg.latent_tagger_enabled is True
        assert cfg.severity_calibration_enabled is True
        assert cfg.severity_calibration_floor == 0.5

    @staticmethod
    def _launcher(extra):
        from argparse import Namespace
        from bench.launcher_core import build_runner_config_from_dict
        base = {"experiment_name": "x", "models": ["CC2"],
                "test_article": "bench/evidence.py"}
        base.update(extra)
        return build_runner_config_from_dict(base, Namespace(resume=False))

    def test_launcher_core_path(self):
        cfg = self._launcher({
            "latent_tagger_enabled": True,
            "severity_calibration_enabled": True,
            "severity_calibration_floor": 0.5,
        })
        assert cfg.latent_tagger_enabled is True
        assert cfg.severity_calibration_enabled is True, (
            "severity_calibration_enabled was dropped on the launcher path — "
            "the 5th instance of this bug class"
        )
        assert cfg.severity_calibration_floor == 0.5

    def test_defaults_are_off_on_both_paths(self):
        base = {"experiment_name": "x", "models": ["CC2"]}
        for cfg in (RunnerConfig.from_dict(base), self._launcher({})):
            assert cfg.latent_tagger_enabled is False
            assert cfg.severity_calibration_enabled is False


# ── The real corpus ─────────────────────────────────────────────────────────


def _archival_reports():
    return sorted(glob.glob(ARCHIVAL_GLOB))


@pytest.mark.skipif(not _archival_reports(),
                    reason="archival Exp 44-49 logs not present")
class TestAgainstArchivalCorpus:
    """293 real findings, five-model panel, six completed live runs.

    These lock in the MEASURED result. If a future change to the marker set
    starts demoting real criticals, this is what catches it.
    """

    @staticmethod
    def _load():
        out = []
        for path in _archival_reports():
            name = os.path.basename(os.path.dirname(path)).split("_")[0]
            with open(path, encoding="utf-8") as fh:
                out.append((name, json.load(fh)))
        return out

    def test_corpus_size(self):
        runs = self._load()
        assert len(runs) == 6
        assert sum(len(r["registry"]["entries"]) for _, r in runs) == 293

    def test_tagger_demotes_nothing_on_the_real_corpus(self):
        """Measured 2026-07-31: zero demotions across all 293 findings. The
        panel does not state reachability, so there is nothing to read."""
        demoted = []
        for name, report in self._load():
            reg = FindingRegistry.from_dict(copy.deepcopy(report["registry"]))
            tag_registry(reg)
            for cid, e in reg.entries.items():
                if _is_demotion_eligible(e):
                    demoted.append(f"{name}/{cid} sev={e['severity']}")
        assert demoted == [], (
            "the tagger demoted real findings it did not demote when measured; "
            f"review each by hand before loosening anything: {demoted}"
        )

    def test_no_demonstrated_critical_is_ever_demoted(self):
        """The one failure this subsystem must never cause."""
        for name, report in self._load():
            reg = FindingRegistry.from_dict(copy.deepcopy(report["registry"]))
            tag_registry(reg)
            _apply_severity_calibration(
                reg, _cfg(severity_calibration_enabled=True), 99)
            for cid, e in reg.entries.items():
                if e.get("severity_calibrated"):
                    assert e.get("falsifier_verdict") == "CONFIRMED"
                    assert e.get("finding_category") not in NEVER_DEMOTE_CATEGORIES

    def test_unearned_criticals_are_structurally_unreachable(self):
        """Ceiling test. Tag EVERY finding latent — the most aggressive tagger
        that could ever exist — and the calibrator still demotes none of the
        criticals whose severity the falsifier never earned. Recall against
        that class is 0 by construction, not by weak tagging."""
        reached = 0
        population = 0
        for _, report in self._load():
            for e in report["registry"]["entries"].values():
                if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
                    continue
                if e.get("falsifier_verdict") not in {"REFUTED", "UNTOOLABLE",
                                                      "ERROR"}:
                    continue
                population += 1
                forced = dict(e, latent=True, finding_category="")
                if _is_demotion_eligible(forced):
                    reached += 1
        assert population == 3, "3 unearned criticals in the corpus"
        assert reached == 0, "an unearned critical became demotable"
