"""Static-queue closure + small-queue alarm (2026-06-09).

Convergence may close while handing a SMALL queue of ladder-exhausted irreducible
criticals to the human; a LARGE queue is a mechanical-failure alarm that refuses
convergence. Irreducible criticals are excluded from the A4 'unverified pending' blocker.
"""
import bench.reference_runner_v2 as rr
from bench.dm._types import Finding


def _series_with_three_zeros():
    # last 3 rounds zero-new-critical -> the quiescence trigger
    return [3, 1, 0, 0, 0]


def test_small_queue_converges_large_alarms():
    cfg = rr.RunnerConfig()  # max_irreducible_queue=2, window=3
    s = _series_with_three_zeros()
    conv0, _ = rr._check_gamma_alt_convergence(4, 0.5, s, cfg, irreducible_queue=0)
    assert conv0, "empty queue + 3 zeros must converge"
    conv2, _ = rr._check_gamma_alt_convergence(4, 0.5, s, cfg, irreducible_queue=2)
    assert conv2, "queue at the bound (2) is handed to HIL and still converges"
    conv3, reason = rr._check_gamma_alt_convergence(4, 0.5, s, cfg, irreducible_queue=3)
    assert not conv3 and "ALARM" in reason, "queue over the bound must raise the alarm, not converge"


def test_registry_irreducible_excluded_from_a4_blocker():
    reg = rr.FindingRegistry()
    cid = reg.register(
        Finding(finding_id="f1", model_id="DeepSeek", round_idx=0, flaw_class=2,
                severity=0.9, abstraction_index=0.5, description="x", falsifier_code=""),
        "DeepSeek")
    e = reg.entries[cid]
    e["status"] = "UNCONFIRMED"
    assert reg.unverified_critical_count() == 1   # pending verification -> blocks
    assert reg.irreducible_queue_count() == 0
    # ladder exhausted -> locked irreducible, handed to HIL
    e["irreducible_escalation"] = True
    assert reg.unverified_critical_count() == 0   # no longer blocks the loop
    assert reg.irreducible_queue_count() == 1     # now in the static queue
