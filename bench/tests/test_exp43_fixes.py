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

    def test_subcritical_untoolable_routed_once(self, monkeypatch):
        """SUPERSEDED assertion (T04, founder ruling 2026-08-22). This used to
        assert calls == [] — "only ERROR verdicts qualify for sub-critical
        routing". The ruling widens FIX 2: ERROR (the test crashed) and
        UNTOOLABLE (there was no test) are the same equipment failure, and
        both are subject to re-routing. The one-attempt error_routed guard is
        unchanged; see test_equipment_error_not_terminal.py."""
        unresolved = SimpleNamespace(verdict="", resolved=False,
                                     duplicate_of=None, falsifier_code="",
                                     model_used="")
        calls, exp_config, cfg = self._setup(monkeypatch, unresolved)
        reg = FindingRegistry()
        cid = _register(reg, "F011", 0.3, "UNCONFIRMED", "UNTOOLABLE")
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == [cid], "UNTOOLABLE sub-critical must be re-routed"

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


# ── Exp 44 post-run: verdict-reader hygiene (C0025/C0034/C0009) ──────────────

class TestVerdictReaderHygiene:
    """Verdict-reading logic, exercised at its own boundary.

    Retargeted 2026-08-12. These four previously stubbed ``subprocess.run`` and
    called ``reverify_falsifier``. That stopped working when the sandbox gained a
    runtime observer: with no real child process the observer cannot install, so
    the sandbox correctly refused with INTEGRITY_VIOLATION and the tests went red.

    The refusal was right and the tests were asking the wrong question. What they
    check is how a verdict is READ from a completed run's output, which is
    ``_read_verdict`` — pure, no I/O, and the exact unit under test. Stubbing out
    the process layer to reach it was always indirection; this removes it.

    The end-to-end path is covered separately by tests that run real children, and
    was independently re-verified across all seven verdict shapes on 2026-08-12.
    """

    def test_not_falsified_is_refuted(self):
        """C0025/C0034: an honest negative report must never CONFIRM."""
        from bench.falsifier_verify import _read_verdict
        assert _read_verdict("NOT FALSIFIED: defect absent", "", 0) == "REFUTED"

    def test_setup_guard_assertion_is_error(self):
        """C0009: a setup-guard AssertionError is instrument breakage."""
        from bench.falsifier_verify import _read_verdict
        assert _read_verdict(
            "", "AssertionError: test setup failed: policy was not mutated", 1) == "ERROR"

    def test_genuine_falsified_still_confirms(self):
        from bench.falsifier_verify import _read_verdict
        assert _read_verdict("FALSIFIED: guard skipped on empty hash", "", 0) == "CONFIRMED"

    def test_genuine_assertion_still_confirms(self):
        from bench.falsifier_verify import _read_verdict
        assert _read_verdict("", "AssertionError: accepted tampered record", 1) == "CONFIRMED"

    def test_the_sandbox_still_refuses_a_run_with_no_observer(self):
        """Pins the behaviour that made the four above fail.

        A falsifier whose observer never installed ran with no boundary and no
        measurement, so nothing about it can decide anything. That refusal is the
        correct outcome and must not be softened to make tests convenient.
        """
        import subprocess as sp
        from bench.falsifier_verify import reverify_falsifier

        class _R:
            stdout, stderr, returncode = "FALSIFIED: x", "", 0

        import pytest as _pytest
        _mp = _pytest.MonkeyPatch()
        try:
            _mp.setattr(sp, "run", lambda *a, **k: _R())
            assert reverify_falsifier("print('x')") == "INTEGRITY_VIOLATION"
        finally:
            _mp.undo()


# ── Post-convergence sweep (founder-approved 2026-07-28) ─────────────────────

class TestPostConvergenceSweep:
    def _run(self, monkeypatch, reg, response, sweep_rounds=2, reverify="CONFIRMED"):
        import bench.reference_runner_v2 as rv2
        import bench.falsifier_verify as fv
        calls = []
        def fake_dispatch(mc, prompt, system, enable_tools=False):
            calls.append(getattr(mc, "label", str(mc)))
            return response, 0.1
        monkeypatch.setattr(rv2, "dispatch_to_model", fake_dispatch)
        monkeypatch.setattr(fv, "reverify_falsifier",
                            lambda code, repo_root=None: reverify)
        cfg = RunnerConfig(post_convergence_sweep_rounds=sweep_rounds,
                           test_article="bench/dm/_memory.py")
        exp_config = SimpleNamespace(models=[SimpleNamespace(label="CC2")])
        stats = rv2._post_convergence_sweep(reg, exp_config, cfg, 5)
        return stats, calls

    def test_disabled_is_noop(self, monkeypatch):
        import bench.reference_runner_v2 as rv2
        reg = FindingRegistry()
        _register(reg, "F030", 0.4, "OPEN")
        cfg = RunnerConfig(post_convergence_sweep_rounds=0)
        assert rv2._post_convergence_sweep(reg, SimpleNamespace(models=[]), cfg, 5) == {}

    def test_falsifier_reattachment_clears_residual(self, monkeypatch):
        reg = FindingRegistry()
        cid = _register(reg, "F031", 0.5, "OPEN")
        resp = f"FALSIFIER: {cid}\n```python\nimport bench.dm._memory\nassert False\n```"
        stats, _ = self._run(monkeypatch, reg, resp, reverify="CONFIRMED")
        assert reg.entries[cid]["status"] == "CONFIRMED"
        assert reg.entries[cid]["resolved_by_sweep"] == "CC2"
        assert stats["cleared"] == 1 and stats["remaining"] == 0

    def test_withdrawal_subcritical_only(self, monkeypatch):
        reg = FindingRegistry()
        sub = _register(reg, "F032", 0.4, "OPEN")
        crit = _register(reg, "F033", 0.9, "OPEN")
        resp = (f"WITHDRAW {sub}: duplicate of established behaviour\n"
                f"WITHDRAW {crit}: also withdrawing this one")
        stats, _ = self._run(monkeypatch, reg, resp)
        assert reg.entries[sub]["status"] == "REFUTED"
        assert reg.entries[sub]["withdraw_reason"].startswith("duplicate")
        assert reg.entries[crit]["status"] == "OPEN", "criticals cannot be withdrawn"
        assert stats["withdrawn"] == 1 and stats["remaining"] == 1

    def test_new_findings_ignored(self, monkeypatch):
        reg = FindingRegistry()
        _register(reg, "F034", 0.4, "OPEN")
        n0 = len(reg.entries)
        resp = ("FINDING_ID: F999\nSEVERITY: 0.9\nDESCRIPTION: brand new claim\n"
                "WITHDRAW C9999: no such id")
        stats, _ = self._run(monkeypatch, reg, resp, reverify="ERROR")
        assert len(reg.entries) == n0, "sweep must register no new findings"
        assert stats["cleared"] == 0 and stats["withdrawn"] == 0

    def test_bounded_rounds_reports_remaining(self, monkeypatch):
        reg = FindingRegistry()
        _register(reg, "F035", 0.4, "OPEN")
        stats, calls = self._run(monkeypatch, reg, "no compliance at all",
                                 sweep_rounds=2)
        assert stats["rounds"] == 2 and stats["remaining"] == 1
        assert len(calls) == 2  # one model, two bounded rounds

    def test_launcher_passthrough(self):
        from bench.launcher_core import build_runner_config_from_dict
        rc = build_runner_config_from_dict(
            {"experiment_name": "t", "models": ["CC2"], "test_article": "x.py",
             "post_convergence_sweep_rounds": 2},
            SimpleNamespace(resume=False))
        assert rc.post_convergence_sweep_rounds == 2


# ── ImmuneMemory staged wiring (founder-approved 2026-07-28) ─────────────────

class TestImmuneMemoryWiring:
    def test_launcher_passthrough(self):
        from bench.launcher_core import build_runner_config_from_dict
        rc = build_runner_config_from_dict(
            {"experiment_name": "t", "models": ["CC2"], "test_article": "x.py",
             "immune_memory_enabled": True,
             "immune_memory_path": "bench/state/test_mem.json"},
            SimpleNamespace(resume=False))
        assert rc.immune_memory_enabled is True
        assert rc.immune_memory_path == "bench/state/test_mem.json"

    def test_recording_tallies_from_registry(self, tmp_path):
        """The run-end hook's tally logic: CONFIRMED/CLOSED count as confirmed,
        REFUTED as rejected, per flaw class — verified through ImmuneMemory."""
        from bench.dm._memory import ImmuneMemory
        reg = FindingRegistry()
        a = _register(reg, "F040", 0.8, "CLOSED", "CONFIRMED")
        b = _register(reg, "F041", 0.4, "CONFIRMED", "CONFIRMED")
        c = _register(reg, "F042", 0.4, "REFUTED", "REFUTED")
        reg.entries[a]["flaw_class"] = 1
        reg.entries[b]["flaw_class"] = 1
        reg.entries[c]["flaw_class"] = 2
        counts = {}
        for e in reg.entries.values():
            cell = counts.setdefault(int(e.get("flaw_class") or 0), [0, 0])
            if e["status"] in ("CONFIRMED", "CLOSED"):
                cell[0] += 1
            elif e["status"] == "REFUTED":
                cell[1] += 1
        mem = ImmuneMemory()
        mem.record_experiment("test", {k: (v[0], v[1]) for k, v in counts.items()})
        p = tmp_path / "mem.json"
        mem.save(str(p))
        back = ImmuneMemory.load(str(p))
        assert back.pi_mem(1) > 0.6, "2 confirmed, 0 rejected -> high prior"
        assert back.pi_mem(2) < 0.4, "0 confirmed, 1 rejected -> low prior"


class TestDomainClaimPatternsPrePass:
    """One-shot arc (2026-07-29): domain TOML claim_patterns now classify
    FIRST for non-software domains — deterministic exam routing."""

    def _classify(self, desc, domain):
        from bench.immune_agents import _classify_claim_v2
        from bench.dm._types import Finding
        f = Finding(finding_id="T1", model_id="X", round_idx=0, flaw_class=1,
                    severity=0.5, abstraction_index=0.3, description=desc,
                    verified=False, origin_type="model")
        ct, _, conf = _classify_claim_v2(f, domain=domain)
        return ct.value, conf

    def test_chemistry_stoichiometry_claim_deterministic(self):
        ct, conf = self._classify(
            "The molar ratio of the stoichiometric coefficients balances at 4.",
            "chemistry")
        assert ct == "mathematical" and conf >= 0.85

    def test_chemistry_logical_claim_deterministic(self):
        ct, _ = self._classify(
            "If the pressure is increased then the equilibrium implies a shift.",
            "chemistry")
        assert ct == "logical"

    def test_software_domain_unchanged(self):
        ct, _ = self._classify(
            "If the flag is set then the invariant implies a contradiction.",
            "software")
        assert ct == "logical"  # generic pattern path, not the TOML pre-pass
