"""In-loop wiring tests for _apply_take_up_slack (gated, mocked dispatch).

Pins the runner-side wiring (not the module logic, which test_take_up_slack covers):
gated-off is a no-op; a strong-writer CONFIRMED resolves an escalated critical and
clears the HIL; a duplicate of an already-CONFIRMED finding short-circuits before
any dispatch.
"""
from __future__ import annotations

import bench.reference_runner_v2 as rr
from bench.dm._types import Finding


def _escalated_registry():
    reg = rr.FindingRegistry()
    cid = reg.register(
        Finding(finding_id="f1", model_id="DeepSeek", round_idx=0, flaw_class=2,
                severity=0.9, abstraction_index=0.5,
                description="compose mutates the HARD situation packet in place",
                falsifier_code=""),
        "DeepSeek")
    e = reg.entries[cid]
    e["escalated"] = True            # the gate escalated it to HIL
    e["status"] = "UNCONFIRMED"
    e["source_model"] = "DeepSeek"
    return reg, cid


class _MC:
    def __init__(self, label):
        self.label = label


def _exp_config():
    return type("EC", (), {"models": [_MC("CC2"), _MC("Codex"), _MC("DeepSeek")]})()


def test_gated_off_is_noop():
    reg, cid = _escalated_registry()
    cfg = rr.RunnerConfig(falsifier_gate_enabled=True, take_up_slack_enabled=False)
    rr._apply_take_up_slack(reg, 1, _exp_config(), cfg=cfg, repo_root=".")
    assert reg.entries[cid]["status"] == "UNCONFIRMED"
    assert reg.entries[cid]["escalated"] is True


def test_strong_writer_resolves_and_clears_hil(monkeypatch):
    reg, cid = _escalated_registry()
    # CC2 (first rung) returns a realistic falsifier (imports the real module) the
    # runner's reverify CONFIRMS (raises). The extractor requires an `import`.
    monkeypatch.setattr(
        rr, "dispatch_to_model",
        lambda mc, p, s, enable_tools=False: (
            "```python\nimport bench.cdsfl_registry.composer  # noqa\n"
            "raise AssertionError('demonstrated defect')\n```", 0.1))
    cfg = rr.RunnerConfig(falsifier_gate_enabled=True, take_up_slack_enabled=True)
    rr._apply_take_up_slack(reg, 1, _exp_config(), cfg=cfg, repo_root=".")
    e = reg.entries[cid]
    assert e["status"] == "CONFIRMED"
    assert e["falsifier_verdict"] == "CONFIRMED"
    assert e.get("verified") is True
    assert e["escalated"] is False
    assert e["resolved_by_takeup"] == "CC2"  # routed to the strongest writer


def test_dedup_short_circuits_before_dispatch(monkeypatch):
    reg, cid = _escalated_registry()
    twin = reg.register(
        Finding(finding_id="f2", model_id="Codex", round_idx=0, flaw_class=2,
                severity=0.9, abstraction_index=0.5,
                description="compose mutates the HARD situation packet in place",
                falsifier_code="x"),
        "Codex")
    reg.entries[twin]["falsifier_verdict"] = "CONFIRMED"
    reg.entries[twin]["status"] = "CONFIRMED"
    dispatched = []
    monkeypatch.setattr(rr, "dispatch_to_model",
                        lambda *a, **k: dispatched.append(1) or ("", 0.0))
    cfg = rr.RunnerConfig(falsifier_gate_enabled=True, take_up_slack_enabled=True)
    rr._apply_take_up_slack(reg, 1, _exp_config(), cfg=cfg, repo_root=".")
    e = reg.entries[cid]
    assert e["status"] == "MERGED" and e.get("takeup_duplicate_of") == twin
    assert dispatched == []  # dedup caught it before any model dispatch
