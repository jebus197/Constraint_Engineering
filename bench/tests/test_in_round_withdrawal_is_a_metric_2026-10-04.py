#!/usr/bin/env python3
"""A seat's reasoned withdrawal is recorded DURING the round, and blocks nothing.

FOUNDER RULING, 2026-10-04, verbatim: *"I said it should simply be a recorded metric,
and should not block anything."* And on the sweep: *"The schema itself is capable of
doing what the sweep does inside a run, so why not just do that?"*

WHAT THIS REPAIRS, measured on study_run1b. `WITHDRAW Cxxxx: reason` was parsed at
exactly 1 site in `bench/reference_runner_v3.py`, inside `_post_convergence_sweep`,
which runs after `converged` is assigned. Both findings that held that run short of
convergence -- C0066 at severity 0.45 and C0073 at 0.50 -- carried
`computed_evidence` with `kinds=['reasoned_withdrawal']`, so the seats HAD reviewed
them and said so, and the record did not exist until after the verdict that needed
it. Two panel seats each proposed a repair reading that evidence; neither could have
changed a live run, because in a live run the evidence is not yet written.

THE TWO PROPERTIES THESE TESTS HOLD, and the second is the ruling:
  1. the withdrawal is recorded while the run is still going, and
  2. recording it moves NOTHING the convergence gate reads.

`unverified_critical_count` is the A4 blocker. If it moves here, the metric has become
a closure bought with model prose, which is the one thing the sweep's own severity
guard exists to prevent and which this must never do.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R  # noqa: E402


def _registry():
    reg = R.FindingRegistry()
    reg.entries = {
        # the run-1b shape: sub-critical, unconfirmed, never reviewed by a tool
        "C0066": {"status": "UNCONFIRMED", "severity": 0.45, "verdicts": [],
                  "last_status_change_round": 5, "falsifier_code": "",
                  "falsifier_verdict": ""},
        # a critical, to prove severity buys nothing here either way
        "C0050": {"status": "UNCONFIRMED", "severity": 0.90, "verdicts": [],
                  "last_status_change_round": 2, "falsifier_code": "",
                  "falsifier_verdict": ""},
        # terminal: must be skipped
        "C0069": {"status": "CLOSED", "severity": 0.45, "verdicts": [],
                  "last_status_change_round": 3, "falsifier_code": "",
                  "falsifier_verdict": ""},
    }
    return reg


class TestItRecords:
    def test_a_withdrawal_is_recorded_in_the_round_it_was_written(self):
        reg = _registry()
        st = R.record_in_round_withdrawals(
            reg, {"Fable-SIM": "WITHDRAW C0066: same origin claim as C0055"}, 5)
        assert st["recorded"] == 1
        rows = reg.entries["C0066"].get("computed_evidence") or []
        assert [r.get("kind") for r in rows] == ["reasoned_withdrawal"]
        assert reg.entries["C0066"]["withdrawal_round"] == 5

    def test_the_reason_travels_with_it(self):
        reg = _registry()
        R.record_in_round_withdrawals(
            reg, {"CC2-SIM": "WITHDRAW C0066: the cited path is not repo-relative"}, 4)
        rows = reg.entries["C0066"]["computed_evidence"]
        assert "not repo-relative" in str(rows[0])

    def test_two_different_seats_are_both_recorded(self):
        reg = _registry()
        st = R.record_in_round_withdrawals(reg, {
            "Fable-SIM": "WITHDRAW C0066: reason one here",
            "CC2-SIM": "WITHDRAW C0066: reason two here",
        }, 5)
        assert st["recorded"] == 2
        assert st["by_model"] == {"Fable-SIM": 1, "CC2-SIM": 1}

    def test_one_seat_repeating_itself_is_recorded_once(self):
        """A re-emission must not inflate a metric the founder will read."""
        reg = _registry()
        st = R.record_in_round_withdrawals(reg, {
            "Codex-SIM": "WITHDRAW C0066: dup\nWITHDRAW C0066: dup"}, 5)
        assert st["recorded"] == 1


class TestItBlocksNothing:
    """The ruling. Every assertion here is the ruling restated as a property."""

    @pytest.mark.parametrize("cid,sev", [("C0066", 0.45), ("C0050", 0.90)])
    def test_the_a4_blocker_does_not_move(self, cid, sev):
        reg = _registry()
        before = reg.unverified_critical_count()
        st = R.record_in_round_withdrawals(
            reg, {"Fable-SIM": f"WITHDRAW {cid}: a reasoned withdrawal here"}, 7)
        assert st["recorded"] == 1, "premise dead: nothing was recorded"
        assert reg.unverified_critical_count() == before, (
            f"recording a withdrawal on {cid} (severity {sev}) moved the A4 blocker "
            f"from {before}. The founder ruled this is a METRIC that blocks nothing; "
            f"a count that moves is a closure bought with model prose."
        )

    def test_no_status_changes(self):
        reg = _registry()
        before = {k: v["status"] for k, v in reg.entries.items()}
        R.record_in_round_withdrawals(reg, {
            "Fable-SIM": "WITHDRAW C0066: x\nWITHDRAW C0050: y"}, 7)
        after = {k: v["status"] for k, v in reg.entries.items()}
        assert after == before, f"statuses moved: {before} -> {after}"

    def test_the_exhausted_valve_flag_is_not_set(self):
        reg = _registry()
        R.record_in_round_withdrawals(reg, {"Fable-SIM": "WITHDRAW C0050: x"}, 7)
        assert "exhausted" not in reg.entries["C0050"], (
            "the recorder set the valve flag; releasing is the valve's job, not this"
        )

    def test_a_critical_is_not_retired(self):
        reg = _registry()
        R.record_in_round_withdrawals(reg, {"Fable-SIM": "WITHDRAW C0050: x"}, 7)
        assert reg.entries["C0050"]["status"] == "UNCONFIRMED"


class TestItSkipsWhatItShould:
    def test_a_terminal_finding_is_skipped(self):
        reg = _registry()
        st = R.record_in_round_withdrawals(
            reg, {"CC2-SIM": "WITHDRAW C0069: already closed"}, 5)
        assert st["recorded"] == 0 and st["skipped_terminal"] == 1
        assert "computed_evidence" not in reg.entries["C0069"]

    def test_an_unknown_id_is_counted_not_crashed_on(self):
        reg = _registry()
        st = R.record_in_round_withdrawals(
            reg, {"CC2-SIM": "WITHDRAW C9999: no such finding"}, 5)
        assert st["recorded"] == 0 and st["skipped_unknown"] == 1

    def test_empty_and_non_string_responses_are_safe(self):
        reg = _registry()
        st = R.record_in_round_withdrawals(reg, {"A": None, "B": "", "C": 17}, 5)
        assert st["recorded"] == 0


class TestTheMutation:
    def test_without_the_WITHDRAW_token_nothing_is_recorded(self):
        """If the parse were ignored and everything recorded, this would fail. It is
        the check that the pattern is doing the work."""
        reg = _registry()
        st = R.record_in_round_withdrawals(
            reg, {"Fable-SIM": "I think C0066 is probably wrong, honestly"}, 5)
        assert st["recorded"] == 0 and st["seen"] == 0

    def test_the_metric_is_persisted_in_the_state_payload(self):
        """An addition nothing reaches is not additive. The per-round counts must
        survive into the saved state or the metric cannot be read later."""
        import ast
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v3.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        payloads = [n for n in ast.walk(tree) if isinstance(n, ast.Dict)
                    and {"registry", "gamma_history"} <= {
                        k.value for k in n.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)}]
        assert payloads, "could not locate the state payload"
        for p in payloads:
            keys = {k.value for k in p.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            assert "round_withdrawals" in keys, (
                "the in-round withdrawal metric is not persisted, so nothing can "
                "read it after the run"
            )
