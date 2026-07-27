"""Regression tests for the Exp 43 contested-convergence fixes (2026-07-22).

Covers the post-Exp-43 fix tranche folded into the runner for Exp 44:

* FIX 1 — ``contested_count()`` excludes UN-DEMONSTRATED SUB-CRITICAL
  findings (UNCONFIRMED, severity < 0.7, falsifier errored/absent), which
  in Exp 43 (C0013 falsifier-ERROR, C0040 no-falsifier leak) held veto
  power over the gate. Criticals keep full protection.
* FIX 1 residual queue — ``undemonstrated_subcritical_ids()`` surfaces
  exactly the excluded set.
* FIX 2 — ``_apply_routing`` routes a falsifier-ERROR finding of ANY
  severity ONCE (``error_routed`` guard), instead of critical-only.
* FIX 3 — the ``runner_core`` parser fallback no longer registers
  registry-referential prose (round-review summaries citing C-ids) as a
  finding; genuine unstructured findings still fall back.
* Exp-43 replay — a registry shaped like the real blocked rounds now
  yields contested == 0 (the sy-simulation counterfactual, pinned).

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_exp43_fixes.py -v
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._types import Finding
from bench.reference_runner_v2 import (
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _apply_routing,
)
from bench.runner_core import _parse_findings_core


def _mk_finding(fid: str, severity: float) -> Finding:
    return Finding(
        finding_id=fid,
        model_id="DeepSeek",
        round_idx=1,
        flaw_class=1,
        severity=severity,
        abstraction_index=0.3,
        description=f"test finding {fid}",
        verified=False,
        origin_type="model",
    )


def _register(reg: FindingRegistry, fid: str, severity: float,
              status: str, falsifier_verdict: str = "",
              last_change: int = 5) -> str:
    cid = reg.register(_mk_finding(fid, severity), "DeepSeek")
    e = reg.entries[cid]
    e["status"] = status
    e["falsifier_verdict"] = falsifier_verdict
    e["last_status_change_round"] = last_change
    return cid


# ── FIX 1: sub-critical exclusion ────────────────────────────────────────────

class TestFix1SubcriticalExclusion:
    def test_unconfirmed_subcritical_error_excluded(self):
        """C0013 class: sub-critical, falsifier ERROR, inside grace — must NOT count."""
        reg = FindingRegistry()
        _register(reg, "F001", 0.3, "UNCONFIRMED", "ERROR", last_change=5)
        assert reg.contested_count(current_round=6, subcritical_exclusion=True) == 0
        # FM-2 pin: default-off keeps legacy gate-off behaviour byte-identical
        assert reg.contested_count(current_round=6) == 1

    def test_unconfirmed_subcritical_absent_falsifier_excluded(self):
        """C0040 class: sub-critical, no falsifier at all — must NOT count."""
        reg = FindingRegistry()
        _register(reg, "F002", 0.3, "UNCONFIRMED", "", last_change=5)
        assert reg.contested_count(current_round=6, subcritical_exclusion=True) == 0

    def test_unconfirmed_critical_still_counted_in_grace(self):
        """Criticals keep full protection: UNCONFIRMED critical in grace counts."""
        reg = FindingRegistry()
        _register(reg, "F003", 0.9, "UNCONFIRMED", "ERROR", last_change=5)
        assert reg.contested_count(current_round=6, subcritical_exclusion=True) == 1

    def test_fm1_challenge_carrying_subcritical_never_excluded(self):
        """FM-1 pin: a sub-critical parked UNCONFIRMED that still carries an
        UNRESOLVED CHALLENGE is genuine disagreement — counted even with the
        exclusion active."""
        reg = FindingRegistry()
        cid = _register(reg, "F014", 0.5, "UNCONFIRMED", "", last_change=5)
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=4)
        assert reg.contested_count(current_round=6, subcritical_exclusion=True) == 1

    def test_challenge_contested_open_still_counted(self):
        """Genuine model disagreement (unresolved CHALLENGE) still gates."""
        reg = FindingRegistry()
        cid = _register(reg, "F004", 0.5, "OPEN")
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=2)
        assert reg.contested_count(current_round=6) == 1

    def test_threshold_boundary_is_critical(self):
        """severity == 0.7 is critical (>= threshold) — still counted."""
        reg = FindingRegistry()
        _register(reg, "F005", CRITICAL_SEVERITY_THRESHOLD, "UNCONFIRMED",
                  "ERROR", last_change=5)
        assert reg.contested_count(current_round=6) == 1

    def test_residual_queue_surfaces_exactly_the_excluded(self):
        reg = FindingRegistry()
        c1 = _register(reg, "F006", 0.3, "UNCONFIRMED", "ERROR")
        c2 = _register(reg, "F007", 0.3, "UNCONFIRMED", "")
        _register(reg, "F008", 0.9, "UNCONFIRMED", "ERROR")   # critical: not residual
        _register(reg, "F009", 0.3, "CONFIRMED", "CONFIRMED")  # terminal: not residual
        assert set(reg.undemonstrated_subcritical_ids()) == {c1, c2}


# ── Exp-43 replay counterfactual ─────────────────────────────────────────────

class TestExp43Replay:
    def test_blocked_round_shape_now_clears(self):
        """The real late-round shape (C0013 + C0040 UNCONFIRMED sub-criticals,
        zero CHALLENGEs, criticals settled) must produce contested == 0 —
        the sy-verified counterfactual that converges the run at R6."""
        reg = FindingRegistry()
        _register(reg, "C0013x", 0.3, "UNCONFIRMED", "ERROR", last_change=9)
        _register(reg, "C0040x", 0.3, "UNCONFIRMED", "", last_change=8)
        for i, fid in enumerate(["K1", "K2", "K3"]):
            cid = _register(reg, fid, 0.9, "CONFIRMED", "CONFIRMED")
        assert reg.contested_count(current_round=10, subcritical_exclusion=True) == 0


# ── FIX 2: ERROR routing, once, any severity ─────────────────────────────────

class TestFix2ErrorRouting:
    def _setup(self, monkeypatch, verdict_obj):
        calls = []

        def fake_route(finding, models, confirmed, resolve_fn, reverify, sim):
            calls.append(finding["id"])
            return verdict_obj

        import bench.routing as routing_mod
        monkeypatch.setattr(routing_mod, "route", fake_route)
        exp_config = SimpleNamespace(models=[SimpleNamespace(label="CC2")])
        cfg = RunnerConfig(routing_enabled=True)
        return calls, exp_config, cfg

    def test_subcritical_error_routed_once(self, monkeypatch):
        unresolved = SimpleNamespace(verdict="", resolved=False,
                                     duplicate_of=None, falsifier_code="",
                                     model_used="")
        calls, exp_config, cfg = self._setup(monkeypatch, unresolved)
        reg = FindingRegistry()
        cid = _register(reg, "F010", 0.3, "UNCONFIRMED", "ERROR")
        reg.entries[cid]["escalated"] = True

        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == [cid], "sub-critical ERROR finding must be routed"
        # Adversarial-pass repair: no model was actually reached (stub route
        # never invokes resolve_fn), so the one attempt is NOT consumed and a
        # later healthy round may retry — transport-dead rounds don't burn it.
        assert "error_routed" not in reg.entries[cid]
        _apply_routing(reg, 7, exp_config, cfg=cfg)
        assert calls == [cid, cid], "retry allowed while no model was reached"

    def test_subcritical_untoolable_not_routed(self, monkeypatch):
        unresolved = SimpleNamespace(verdict="", resolved=False,
                                     duplicate_of=None, falsifier_code="",
                                     model_used="")
        calls, exp_config, cfg = self._setup(monkeypatch, unresolved)
        reg = FindingRegistry()
        cid = _register(reg, "F011", 0.3, "UNCONFIRMED", "UNTOOLABLE")
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == [], "only ERROR verdicts qualify for sub-critical routing"

    def test_routing_disabled_is_noop(self, monkeypatch):
        unresolved = SimpleNamespace(verdict="", resolved=False,
                                     duplicate_of=None, falsifier_code="",
                                     model_used="")
        calls, exp_config, _ = self._setup(monkeypatch, unresolved)
        reg = FindingRegistry()
        cid = _register(reg, "F012", 0.3, "UNCONFIRMED", "ERROR")
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=RunnerConfig(routing_enabled=False))
        assert calls == []
        assert "error_routed" not in reg.entries[cid]

    def test_resolved_subcritical_confirms(self, monkeypatch):
        resolved = SimpleNamespace(verdict="CONFIRMED", resolved=True,
                                   duplicate_of=None, falsifier_code="assert 1",
                                   model_used="CC2")
        calls, exp_config, cfg = self._setup(monkeypatch, resolved)
        reg = FindingRegistry()
        cid = _register(reg, "F013", 0.3, "UNCONFIRMED", "ERROR")
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        e = reg.entries[cid]
        assert e["status"] == "CONFIRMED" and e["falsifier_verdict"] == "CONFIRMED"


# ── FIX 3: fallback hardening ────────────────────────────────────────────────

class TestFix3FallbackHardening:
    def test_c0040_style_review_summary_suppressed(self):
        text = ("Round 8 Review — `bench/macrophage_cell.py`\n\n"
                "I have systematically inspected the code after the six applied "
                "fixes (C0019, C0020, C0026, C0027, C0036, C0010) and "
                "cross-referenced every open or unconfirmed registry entry.")
        assert _parse_findings_core("DeepSeek", 8, text) == []

    def test_registry_citing_prose_suppressed_without_header(self):
        text = ("After reviewing everything again I believe C0012 and C0031 "
                "cover all remaining concerns and no further issues exist in "
                "the module at this time.")
        assert _parse_findings_core("DeepSeek", 9, text) == []

    def test_genuine_unstructured_finding_still_falls_back(self):
        text = ("The compute_ratio helper divides by the raw count without "
                "guarding zero, so an empty batch crashes the pipeline when "
                "invoked from the aggregation path.")
        out = _parse_findings_core("DeepSeek", 2, text)
        assert len(out) == 1 and out[0].finding_id.endswith("_UNSTRUCTURED")

    def test_fenced_cid_quotes_do_not_suppress(self):
        """FM1 pin (exp36 r43 class): C-ids inside fenced patch code are quotes,
        not registry cross-references — the fallback must still capture."""
        text = ("The verify_bundle path accepts tampered record content when the "
                "proof chain hash matches the bundle root, bypassing integrity.\n"
                "```python\n# C0009/C0173: check list lengths match\nassert ok\n```")
        out = _parse_findings_core("Codex", 43, text)
        assert len(out) == 1 and out[0].finding_id.endswith("_UNSTRUCTURED")

    def test_structured_findings_unaffected(self):
        text = ("FINDING_ID: F001\nSEVERITY: 0.8\nFLAW_CLASS: 2\n"
                "DESCRIPTION: off-by-one in window slice bounds\n"
                "VERIFIED: FALSE\n")
        out = _parse_findings_core("CC2", 1, text)
        assert len(out) == 1 and out[0].severity == pytest.approx(0.8)


# ── Exp 44 post-run fixes: stale irreducible flags (2026-07-27) ──────────────

class TestExp44StaleFlagFixes:
    def test_terminal_entries_leave_the_irreducible_queue(self):
        """The 6-stale-flags episode: a CLOSED, routing-resolved entry must not
        count in the irreducible queue (was 6 where truth was 0)."""
        reg = FindingRegistry()
        cid = _register(reg, "F020", 0.9, "CLOSED", "CONFIRMED")
        reg.entries[cid]["irreducible_escalation"] = True  # stale stamp
        assert reg.irreducible_queue_count() == 0

    def test_open_irreducible_still_counts(self):
        reg = FindingRegistry()
        cid = _register(reg, "F021", 0.9, "UNCONFIRMED", "UNTOOLABLE")
        reg.entries[cid]["irreducible_escalation"] = True
        assert reg.irreducible_queue_count() == 1

    def test_routing_resolution_clears_stale_stamps(self, monkeypatch):
        resolved = SimpleNamespace(verdict="CONFIRMED", resolved=True,
                                   duplicate_of=None, falsifier_code="assert 1",
                                   model_used="CC2")
        calls = []
        def fake_route(finding, models, confirmed, resolve_fn, reverify, sim):
            calls.append(finding["id"]); return resolved
        import bench.routing as routing_mod
        monkeypatch.setattr(routing_mod, "route", fake_route)
        reg = FindingRegistry()
        cid = _register(reg, "F022", 0.9, "UNCONFIRMED", "ERROR")
        e = reg.entries[cid]
        e["escalated"] = True
        e["irreducible_escalation"] = True   # from an earlier exhausted round
        e["hil_escalated"] = True
        e["hil_reason"] = "routing ladder exhausted"
        _apply_routing(reg, 9, SimpleNamespace(models=[SimpleNamespace(label="CC2")]),
                       cfg=RunnerConfig(routing_enabled=True))
        assert e["status"] == "CONFIRMED"
        assert e["irreducible_escalation"] is False
        assert e["hil_escalated"] is False and "hil_reason" not in e
        assert reg.irreducible_queue_count() == 0


class TestGeminiJsonFindKey:
    def test_json_find_key_maps_to_description(self):
        """Exp 44 C0007-9: Gemini JSON findings carry FIND, not DESCRIPTION —
        the description must be harvested, not silently dropped."""
        text = ('```json\n[{"FINDING_ID": "F001", "SEVERITY": 1.0, "FLAW_CLASS": 1,'
                ' "ABSTRACTION_INDEX": 0.2,'
                ' "FIND": "verify_bundle skips the chain_hash mismatch check",'
                ' "FOLLOW": "attacker can modify records", "VERIFIED": false}]\n```')
        out = _parse_findings_core("Gemini", 0, text)
        assert len(out) == 1
        assert "chain_hash" in out[0].description
