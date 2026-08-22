"""T01 — a falsifier that FAILS the discrimination control must reach the ladder.

The discrimination control (founder ruling 2026-08-08) re-runs a CONFIRMED
falsifier against a CORRECTED copy of the target. A falsifier that fires there
too is testing nothing: the INSTRUMENT is broken, not the claim.
``_apply_discrimination_control`` therefore un-confirms the finding, stamps
``falsifier_verdict = NON_DISCRIMINATING`` and escalates it.

The routing ladder is the mechanism this project already owns for a finding
whose first falsifier failed — it hands the falsification to a stronger writer.
Its sub-critical admission read ONLY ``ERROR``, so a sub-critical mechanical
fault was escalated and then never routed: permanent HIL limbo with the one
absorber built for it standing idle. Founder ruling 2026-08-22: use the
mechanism that exists.

Second defect, same root: when the ladder DOES resolve such a finding it has
REPLACED the instrument, but ``mechanical_fault`` and the ``discrimination``
record of the discarded falsifier stayed attached to it. The control clears
neither on a later pass, so a repaired finding read as mechanically faulty for
ever — the stale-stamp class the Exp-44 fix three lines above already addresses
for ``irreducible_escalation`` / ``hil_escalated``.

The state fed to routing here is produced by RUNNING the real gate
(``apply_falsifier_verdicts``) with only two boundaries mocked — the sandbox
re-run and the model dispatch — so these tests pin the shape the runner really
produces rather than a hand-built imitation of it.
"""
from __future__ import annotations

import pytest

import bench.falsifier_verify as fv
import bench.reference_runner_v2 as rr
from bench.dm._types import Finding

SUBCRITICAL = rr.CRITICAL_SEVERITY_THRESHOLD - 0.2
CRITICAL = rr.CRITICAL_SEVERITY_THRESHOLD + 0.2

# A response the runner's own _extract_routing_falsifier accepts (it parses, and
# it can reach a verdict via ``raise``).
RUNG_RESPONSE = (
    "I read the module and reproduced it.\n\n"
    "```python\n"
    "import bench.routing  # noqa: F401\n"
    "raise AssertionError('FALSIFIED: the defect is present')\n"
    "```\n"
)

DISC_FAILED_RECORD = {
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
    # DeepSeek is the source model and is excluded from the ladder; Codex is the
    # strongest remaining rung (bench/routing.DEFAULT_FALSIFIER_STRENGTH).
    return type("EC", (), {"models": [_MC("CC2"), _MC("Codex"), _MC("DeepSeek")]})()


def _cfg(blocks: bool = False):
    return rr.RunnerConfig(
        falsifier_gate_enabled=True,
        routing_enabled=True,
        discrimination_control_blocks=blocks,
        test_article="bench/routing.py",
    )


def _gate_leaves_a_mechanical_fault(monkeypatch, severity, blocks=False):
    """Run the REAL gate on a firing falsifier whose control says NO_DISCRIMINATION."""
    reg = rr.FindingRegistry()
    cid = reg.register(
        Finding(finding_id="f1", model_id="DeepSeek", round_idx=0, flaw_class=2,
                severity=severity, abstraction_index=0.5,
                description="a claim whose falsifier fires on everything",
                falsifier_code="print('FALSIFIED')"),
        "DeepSeek")
    e = reg.entries[cid]
    e["corrected_copy"] = "the corrected passage"
    monkeypatch.setattr(fv, "reverify_falsifier", lambda code, **k: "CONFIRMED")
    monkeypatch.setattr(rr, "run_discrimination_control",
                        lambda *a, **k: dict(DISC_FAILED_RECORD))
    rr.apply_falsifier_verdicts(reg, 1, cfg=_cfg(blocks), repo_root=".")
    # Sanity: this IS the gate's real post-control shape, not an assumption.
    assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
    assert e["escalated"] is True
    assert e["mechanical_fault"] is True
    return reg, cid


def _route(monkeypatch, reg, rung_verdict, blocks=False):
    """Run the REAL _apply_routing with the model boundary mocked."""
    dispatched: list = []

    def _dispatch(mc, prompt, system, enable_tools=False):
        dispatched.append(mc.label)
        return RUNG_RESPONSE, 0.1

    monkeypatch.setattr(rr, "dispatch_to_model", _dispatch)
    monkeypatch.setattr(fv, "reverify_falsifier", lambda code, **k: rung_verdict)
    rr._apply_routing(reg, 2, _exp_config(), cfg=_cfg(blocks), repo_root=".")
    return dispatched


class TestDiscriminationFailureReachesTheLadder:

    @pytest.mark.parametrize("blocks", [False, True])
    def test_subcritical_no_discrimination_is_routed_and_resolved(
            self, monkeypatch, blocks):
        """THE T01 DEFECT. A sub-critical NO_DISCRIMINATION finding is escalated
        by the control and was then never admitted to the ladder, in EITHER
        control mode — the sub-critical branch admitted only ERROR. It must be
        routed to a stronger writer, and a CONFIRMED from the runner's decider
        on that writer's falsifier must resolve it."""
        reg, cid = _gate_leaves_a_mechanical_fault(
            monkeypatch, SUBCRITICAL, blocks=blocks)
        dispatched = _route(monkeypatch, reg, "CONFIRMED", blocks=blocks)
        e = reg.entries[cid]
        assert dispatched, (
            "a NO_DISCRIMINATION falsifier never reached the routing ladder: "
            "the finding sat in HIL limbo with the absorber standing idle")
        assert e["resolved_by_routing"] == "Codex"
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert "raise AssertionError" in e["falsifier_code"]
        assert e["status"] == "CONFIRMED" and e["verified"] is True
        assert e["escalated"] is False

    def test_the_ladder_clears_the_stamps_of_the_instrument_it_replaced(
            self, monkeypatch):
        """A resolved finding carries a NEW falsifier. The mechanical-fault stamp
        and the discrimination record both describe the falsifier that was just
        discarded, and nothing downstream ever clears them — the control does not
        clear them on a later pass. They must not ride the repaired finding.
        (Reachable on the critical path, which already routes today.)"""
        reg, cid = _gate_leaves_a_mechanical_fault(monkeypatch, CRITICAL)
        assert reg.entries[cid]["discrimination"]["outcome"] == rr.DISC_FAILED
        _route(monkeypatch, reg, "CONFIRMED")
        e = reg.entries[cid]
        assert e["resolved_by_routing"] == "Codex"
        assert not e.get("mechanical_fault"), (
            "the replaced instrument's fault stamp rode the repaired finding")
        assert not e.get("discrimination"), (
            "the discrimination record describes a falsifier no longer attached")
        assert e["hil_escalated"] is False and e["irreducible_escalation"] is False
        assert "hil_reason" not in e
        # The permanent trail is untouched: the diagnosis is still on the record.
        kinds = [c["kind"] for c in e.get("computed_evidence", [])]
        assert f"discrimination_control:{rr.DISC_FAILED}" in kinds

    def test_exhausted_ladder_consumes_one_attempt_then_hil(self, monkeypatch):
        """When no rung can demonstrate it, the finding goes to HIL with the
        MECHANICAL FAULT diagnosis intact, and the single sub-critical attempt is
        consumed (FIX 2's error_routed guard) so it cannot eat the ladder round
        after round."""
        reg, cid = _gate_leaves_a_mechanical_fault(monkeypatch, SUBCRITICAL)
        dispatched = _route(monkeypatch, reg, "REFUTED")
        e = reg.entries[cid]
        assert len(dispatched) == 2, "both rungs must be tried before HIL"
        assert e.get("error_routed") is True, "the one attempt must be consumed"
        assert e["mechanical_fault"] is True
        assert e["irreducible_escalation"] is True and e["hil_escalated"] is True
        assert "MECHANICAL FAULT" in e.get("hil_reason", "")
        assert _route(monkeypatch, reg, "REFUTED") == [], "one attempt only"

    def test_transport_dead_round_does_not_burn_the_attempt(self, monkeypatch):
        """If no rung reaches a model at all (the 402-cascade class), the single
        sub-critical attempt is NOT consumed and a later round retries."""
        reg, cid = _gate_leaves_a_mechanical_fault(monkeypatch, SUBCRITICAL)

        def _dead(mc, prompt, system, enable_tools=False):
            raise RuntimeError("402 payment required")

        monkeypatch.setattr(rr, "dispatch_to_model", _dead)
        monkeypatch.setattr(fv, "reverify_falsifier", lambda code, **k: "ERROR")
        rr._apply_routing(reg, 2, _exp_config(), cfg=_cfg(), repo_root=".")
        assert not reg.entries[cid].get("error_routed")
        assert reg.entries[cid]["falsifier_verdict"] == "NON_DISCRIMINATING"
        assert _route(monkeypatch, reg, "CONFIRMED"), "a later round must retry"

    def test_untoolable_subcritical_is_still_not_admitted(self, monkeypatch):
        """Guard against over-widening: admitting NON_DISCRIMINATING must not
        open the sub-critical gate to every un-demonstrated verdict."""
        reg = rr.FindingRegistry()
        cid = reg.register(
            Finding(finding_id="f2", model_id="DeepSeek", round_idx=0,
                    flaw_class=2, severity=SUBCRITICAL, abstraction_index=0.5,
                    description="no falsifier at all", falsifier_code=""),
            "DeepSeek")
        reg.entries[cid]["escalated"] = True
        reg.entries[cid]["falsifier_verdict"] = "UNTOOLABLE"
        assert _route(monkeypatch, reg, "CONFIRMED") == []
