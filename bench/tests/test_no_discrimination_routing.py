"""T01 — discrimination failures must reach the routing ladder (2026-08-22).

A falsifier that fails the discrimination control fired against a CORRECTED
copy of the target: the INSTRUMENT is broken, not the claim. The control's
helper already un-confirms and escalates such a finding, and the routing
ladder already exists exactly for un-demonstrated findings whose first
falsifier failed (FIX 2 routes sub-critical ERROR falsifiers once). But the
sub-critical admission in ``_apply_routing`` admitted ONLY ``ERROR``, so a
sub-critical NO_DISCRIMINATION finding was escalated and then never routed —
permanent HIL limbo, with the one mechanism built to absorb it standing idle.
Founder ruling 2026-08-22: use the mechanism that exists.

The state fed to routing here is produced by RUNNING the real gate
(``apply_falsifier_verdicts``) with only the sandbox boundary mocked
(reverify + the control's measurement), so the tests pin the shape the gate
actually leaves, not a hand-crafted imitation of it.
"""
from __future__ import annotations

import bench.falsifier_verify as fv
import bench.reference_runner_v2 as rr
from bench.dm._types import Finding


ROUTED_FALSIFIER = (
    "```python\nimport bench.cdsfl_registry.composer  # noqa\n"
    "raise AssertionError('demonstrated defect')\n```"
)

DISC_FAILED_REC = {
    "outcome": rr.DISC_FAILED,
    "detail": "the falsifier fires just as hard against a CORRECTED copy",
    "falsifier_sha": "", "corrected_sha": "",
    "baseline_verdict": "CONFIRMED", "corrected_verdict": "CONFIRMED",
    "intercepted": True, "deterministic": True,
    "retarget_substitutions": 1, "target": "",
}


class _MC:
    def __init__(self, label):
        self.label = label


def _exp_config():
    return type("EC", (), {"models": [_MC("CC2"), _MC("Codex"), _MC("DeepSeek")]})()


def _cfg():
    return rr.RunnerConfig(falsifier_gate_enabled=True, routing_enabled=True)


def _gate_leaves_mechanical_fault(monkeypatch, severity):
    """Run the REAL gate on a firing falsifier whose control says DISC_FAILED."""
    reg = rr.FindingRegistry()
    cid = reg.register(
        Finding(finding_id="f1", model_id="DeepSeek", round_idx=0, flaw_class=2,
                severity=severity, abstraction_index=0.5,
                description="a claim whose falsifier fires on everything",
                falsifier_code="print('FALSIFIED')"),
        "DeepSeek")
    e = reg.entries[cid]
    e["status"] = "CONFIRMED"
    e["source_model"] = "DeepSeek"
    e["corrected_copy"] = "the corrected passage"
    monkeypatch.setattr(fv, "reverify_falsifier", lambda code, **k: "CONFIRMED")
    monkeypatch.setattr(rr, "run_discrimination_control",
                        lambda *a, **k: dict(DISC_FAILED_REC))
    rr.apply_falsifier_verdicts(reg, 1, cfg=_cfg(), repo_root=".")
    # Sanity: this IS the gate's real post-control shape, not an assumption.
    assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
    assert e["escalated"] is True and e["mechanical_fault"] is True
    return reg, cid


def _route(monkeypatch, reg, rung_verdict):
    """Run _apply_routing with the model boundary mocked; return dispatch count."""
    dispatched = []
    monkeypatch.setattr(
        rr, "dispatch_to_model",
        lambda mc, p, s, enable_tools=False: (
            dispatched.append(mc.label) or (ROUTED_FALSIFIER, 0.1)))
    monkeypatch.setattr(fv, "reverify_falsifier",
                        lambda code, **k: rung_verdict)
    rr._apply_routing(reg, 1, _exp_config(), cfg=_cfg(), repo_root=".")
    return dispatched


class TestNoDiscriminationReachesTheLadder:
    def test_subcritical_mechanical_fault_is_routed_and_resolved(self, monkeypatch):
        """THE T01 DEFECT. A sub-critical NO_DISCRIMINATION finding is escalated
        by the control but was never admitted to the ladder — the sub-critical
        branch admitted only ERROR. It must be routed to a stronger writer, and
        a CONFIRMED from that writer's falsifier must resolve it."""
        reg, cid = _gate_leaves_mechanical_fault(monkeypatch, severity=0.5)
        dispatched = _route(monkeypatch, reg, "CONFIRMED")
        e = reg.entries[cid]
        assert dispatched, (
            "a NO_DISCRIMINATION falsifier never reached the routing ladder — "
            "the finding sat in HIL limbo with the absorber standing idle")
        assert e["resolved_by_routing"] == "Codex"  # strongest rung, source excluded
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert e["status"] == "CONFIRMED" and e.get("verified") is True
        assert e["escalated"] is False
        assert e["hil_escalated"] is False and e["irreducible_escalation"] is False

    def test_exhausted_ladder_consumes_one_attempt_then_hil(self, monkeypatch):
        """When no rung can demonstrate it, the finding goes to HIL with the
        MECHANICAL FAULT diagnosis intact, and the single sub-critical attempt
        is consumed (FIX 2's error_routed guard) so it cannot eat the ladder
        round after round."""
        reg, cid = _gate_leaves_mechanical_fault(monkeypatch, severity=0.5)
        dispatched = _route(monkeypatch, reg, "REFUTED")
        e = reg.entries[cid]
        assert len(dispatched) == 2, "both rungs must be tried before HIL"
        assert e.get("error_routed") is True, "the one attempt must be consumed"
        assert e["irreducible_escalation"] is True and e["hil_escalated"] is True
        assert "MECHANICAL FAULT" in e.get("hil_reason", "")
        # One attempt only: a second pass must not dispatch again.
        dispatched2 = _route(monkeypatch, reg, "REFUTED")
        assert dispatched2 == []

    def test_critical_mechanical_fault_still_routed(self, monkeypatch):
        """Regression guard: the critical path already reached the ladder
        (escalated + verdict != CONFIRMED) and must keep doing so."""
        reg, cid = _gate_leaves_mechanical_fault(monkeypatch, severity=0.9)
        dispatched = _route(monkeypatch, reg, "CONFIRMED")
        assert dispatched
        assert reg.entries[cid]["resolved_by_routing"] == "Codex"

    def test_untoolable_subcritical_still_not_routed(self, monkeypatch):
        """Guard against over-widening: admitting NON_DISCRIMINATING must not
        open the sub-critical gate to every un-demonstrated verdict."""
        reg = rr.FindingRegistry()
        cid = reg.register(
            Finding(finding_id="f2", model_id="DeepSeek", round_idx=0,
                    flaw_class=2, severity=0.5, abstraction_index=0.5,
                    description="no falsifier at all", falsifier_code=""),
            "DeepSeek")
        reg.entries[cid]["escalated"] = True
        reg.entries[cid]["falsifier_verdict"] = "UNTOOLABLE"
        dispatched = _route(monkeypatch, reg, "CONFIRMED")
        assert dispatched == []
