"""Static-queue closure + the irreducible-queue alarm (2026-06-09; A7 2026-08-01).

Convergence may close while handing a SMALL queue of ladder-exhausted irreducible
criticals to the human. Irreducible criticals are excluded from the A4
'unverified pending' blocker so the loop can close around them.

WHAT CHANGED ON 2026-08-01 (A7)
-------------------------------
A LARGE queue is still an alarm, and the alarm still fires at the same bound
(default 2). What changed is what the alarm DOES.

Before: ``_check_gamma_alt_convergence`` returned "not converged" and nothing
else. That response cost the project two suppressions of a correct alarm. On the
zero-plant control the S_k hard gates were parsing prose as Python, so no fix
could be admitted, so nothing could close, so thirteen criticals locked as
irreducible — a mechanical failure the alarm named correctly. Because the only
thing it did was deny a finish, without evidence and without stopping the run,
the bound was raised twice to get past it.

After: the alarm HALTS the run, NOTIFIES with a formatted message, and ATTACHES
a per-finding evidence bundle to the report. It fires from the round loop, ahead
of every gate, so no gate arrangement can route around it — and the γ-alt
checker no longer refuses convergence on this condition, because a silent veto
is the behaviour that got it turned off.
"""
import bench.reference_runner_v3 as rr
from bench.dm._types import Finding


def _series_with_three_zeros():
    # last 3 rounds zero-new-critical -> the quiescence trigger
    return [3, 1, 0, 0, 0]


def _registry_with_irreducibles(n, sk_tristate="REJECTED", falsifier=""):
    reg = rr.FindingRegistry()
    for i in range(n):
        cid = reg.register(
            Finding(finding_id=f"f{i}", model_id="DeepSeek", round_idx=0,
                    flaw_class=2, severity=0.9, abstraction_index=0.5,
                    description=f"claim {i} could not be settled",
                    falsifier_code=falsifier),
            "DeepSeek")
        e = reg.entries[cid]
        e["status"] = "UNCONFIRMED"
        e["irreducible_escalation"] = True
        if sk_tristate:
            e["sk_result"] = {"tristate": sk_tristate,
                              "gate_details": {"g1_ast": {"score": 0}}}
    return reg


class TestQueueSizeStillDecidesTheAlarm:
    def test_small_queue_still_converges(self):
        cfg = rr.RunnerConfig()  # max_irreducible_queue=2, window=3
        s = _series_with_three_zeros()
        conv0, _ = rr._check_gamma_alt_convergence(4, 0.5, s, cfg, irreducible_queue=0)
        assert conv0, "empty queue + 3 zeros must converge"
        conv2, _ = rr._check_gamma_alt_convergence(4, 0.5, s, cfg, irreducible_queue=2)
        assert conv2, "queue at the bound (2) is handed to HIL and still converges"

    def test_the_bound_is_still_two(self):
        """The default was raised to suppress this alarm twice. It is back at 2."""
        assert rr.RunnerConfig().max_irreducible_queue == 2

    def test_alarm_fires_above_the_bound_and_not_at_it(self):
        cfg = rr.RunnerConfig()
        assert rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(2), cfg, 4) is None
        assert rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(3), cfg, 4) is not None

    def test_alarm_respects_a_configured_bound(self):
        cfg = rr.RunnerConfig(max_irreducible_queue=8)
        assert rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(8), cfg, 4) is None
        alarm = rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(9), cfg, 4)
        assert alarm is not None and alarm["bound"] == 8 and alarm["count"] == 9


class TestTheAlarmNoLongerSilentlyRefusesAFinish:
    """A7's whole point: it must stay loud, and stop being a quiet veto."""

    def test_gamma_alt_does_not_refuse_convergence_on_queue_size(self):
        cfg = rr.RunnerConfig()
        conv, reason = rr._check_gamma_alt_convergence(
            4, 0.5, _series_with_three_zeros(), cfg, irreducible_queue=13)
        assert conv, (
            "the γ-alt checker must no longer veto on queue size — the run-loop "
            "alarm halts first, and a second silent veto here is the behaviour "
            "that got this alarm suppressed twice")

    def test_but_the_reason_string_still_names_the_queue(self):
        """Loud, not silent: a reader of the reason must see the number."""
        cfg = rr.RunnerConfig()
        _, reason = rr._check_gamma_alt_convergence(
            4, 0.5, _series_with_three_zeros(), cfg, irreducible_queue=13)
        assert "13" in reason and "irreducible queue" in reason


class TestTheAlarmHaltsNotifiesAndAttaches:
    def test_it_asks_for_a_halt_not_a_veto(self):
        alarm = rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(5), rr.RunnerConfig(), 4)
        assert alarm["action"] == "halt_notify_attach"
        assert rr.IRREDUCIBLE_QUEUE_HALT == "HALTED_IRREDUCIBLE_QUEUE_ALARM"

    def test_notification_names_count_bound_round_and_the_suppression(self):
        alarm = rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(13), rr.RunnerConfig(), 4)
        n = alarm["notify"]
        assert "13" in n and "bound of 2" in n and "round 4" in n
        assert "HALTED" in n
        # The instruction that stops this being suppressed a third time.
        assert "Do NOT raise max_irreducible_queue" in n

    def test_evidence_carries_one_entry_per_queued_critical(self):
        alarm = rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(5), rr.RunnerConfig(), 4)
        assert len(alarm["evidence"]) == 5
        item = alarm["evidence"][0]
        for key in ("canonical_id", "status", "severity", "description",
                    "falsifier_present", "falsifier_verdict", "sk_tristate",
                    "verdicts", "routing_history"):
            assert key in item, f"evidence bundle is missing {key}"

    def test_evidence_surfaces_the_shared_mechanism(self):
        """The 2026-08-01 signature: every item rejected by the same gate."""
        alarm = rr.build_irreducible_queue_alarm(
            _registry_with_irreducibles(13, sk_tristate="REJECTED"),
            rr.RunnerConfig(), 4)
        assert alarm["sk_states_in_queue"] == ["REJECTED"]
        assert alarm["items_without_falsifier"] == 13
        assert "REJECTED" in alarm["notify"]

    def test_evidence_carries_no_rk_value(self):
        """The bundle is diagnostic. R_k must not travel in it."""
        reg = _registry_with_irreducibles(3)
        for e in reg.entries.values():
            e["sk_result"]["R_old"] = 0.5
            e["sk_result"]["R_new"] = 0.62
        alarm = rr.build_irreducible_queue_alarm(reg, rr.RunnerConfig(), 4)
        blob = repr(alarm)
        assert "R_new" not in blob and "0.62" not in blob

    def test_terminal_entries_do_not_trip_the_alarm(self):
        """A later routing success closes an entry; a stale stamp must not fire."""
        reg = _registry_with_irreducibles(5)
        for e in reg.entries.values():
            e["status"] = "CLOSED"
        assert rr.build_irreducible_queue_alarm(reg, rr.RunnerConfig(), 4) is None

    def test_subcritical_irreducibles_do_not_trip_the_alarm(self):
        reg = _registry_with_irreducibles(5)
        for e in reg.entries.values():
            e["severity"] = 0.4
        assert rr.build_irreducible_queue_alarm(reg, rr.RunnerConfig(), 4) is None


class TestRunLoopWiring:
    """The alarm is useless if the loop can reach a verdict without consulting it."""

    def test_the_loop_halts_on_the_alarm(self):
        import ast
        import inspect
        import textwrap
        src = inspect.getsource(rr.run_experiment)
        tree = ast.parse(textwrap.dedent(src))
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "build_irreducible_queue_alarm"]
        assert calls, "run_experiment never builds the alarm"
        assert 'result["convergence_reason"] = IRREDUCIBLE_QUEUE_HALT' in src
        assert 'result["irreducible_queue_alarm"] = _irq_alarm' in src
        assert 'result["halted"] = True' in src

    def test_the_alarm_is_checked_before_the_convergence_action_block(self):
        """Placement is the property: a halt that runs after the loop has
        already acted on `converged` is not a halt."""
        import inspect
        src = inspect.getsource(rr.run_experiment)
        alarm_at = src.index("_irq_alarm = build_irreducible_queue_alarm")
        action_at = src.index(
            "if converged or stall_result.get(\"terminate\") or churn_transition:")
        hil_at = src.index("if cfg.hil_review and not (burst_plan and burst_state):")
        assert alarm_at < action_at, "the alarm must precede the convergence action"
        assert alarm_at < hil_at, "the alarm must precede the HIL pause"


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
