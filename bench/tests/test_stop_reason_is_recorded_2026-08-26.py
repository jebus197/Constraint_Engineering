"""A run that halts for a named cause must SAY so in completion_signal.json.

THE DEFECT, MEASURED 2026-08-26 across the whole archive. 20 of 31 completion
signals carry status INCOMPLETE with an EMPTY reason. In 7 of those the run
report DOES name the cause:

    exp35  EXTENSION_STALLED
    exp36  STATE_CONVERGED at round 45
    exp37  STATE_CONVERGED at round 15
    exp40  GAMMA_ALT_CONVERGED (gamma=0.305 >= 0.3 at round 7)
    exp40  HARDENED_CONVERGED (sparsity fallback)
    exp55  HALTED_IRREDUCIBLE_QUEUE_ALARM
    exp55  HALTED_IRREDUCIBLE_QUEUE_ALARM

MECHANISM. reference_runner_v2 writes the cause to its result dict, then copies
it to brain.state.convergence_reason ONLY inside `if converged:`. signal_complete
reads that field. So every non-convergence stop reached the report and never
reached the signal, and any tool reading the signal alone saw a run that halted
on a named alarm as a run that simply stopped.

The runner's own source names a related defect at reference_runner_v2.py:11002
and dates a partial fix to 2026-05-18 -- "post-mortem tooling read every
hardened convergence as INCOMPLETE". Runs from July and August still showed it,
so that fix corrected the instance and not the class.

WHY A SEPARATE FIELD. signal_complete derives STATUS from the CONTENTS of
convergence_reason ("BUDGET_EXHAUSTED" in ...). Widening what goes into that
field would make status depend on the wording of an unrelated stop. stop_reason
leaves the status logic untouched by construction rather than by argument, and
the tests below assert exactly that.
"""
import json

import pytest

from bench.dm._types import DynamicManagementConfig
from bench.insect_brain import InsectBrain


@pytest.fixture()
def brain(tmp_path):
    b = InsectBrain(config=DynamicManagementConfig(), logs_dir=tmp_path,
                    source_paths=["x.py"])
    b.initialise(["CC2", "Gemini", "DeepSeek", "Codex", "ChatGPT"])
    return b


class TestTheReasonSurvives:
    def test_known_bad_a_named_halt_no_longer_reports_an_empty_reason(self, brain):
        """The exp55 case, exactly: halted on an alarm, signal said nothing."""
        brain.state.stop_reason = "HALTED_IRREDUCIBLE_QUEUE_ALARM"
        sig = brain.signal_complete()
        assert sig["reason"] == "HALTED_IRREDUCIBLE_QUEUE_ALARM", (
            f"a named halt still reports reason={sig['reason']!r}. Both exp55 runs "
            "recorded this alarm in the report and an empty string in the signal."
        )

    def test_a_stop_reason_does_NOT_change_the_status(self, brain):
        """The property the separate field exists to protect. A stall is not a
        convergence and must not be promoted into one by naming it."""
        brain.state.stop_reason = "EXTENSION_STALLED"
        assert brain.signal_complete()["status"] == "INCOMPLETE"

    def test_a_stop_reason_containing_BUDGET_EXHAUSTED_still_does_not_flip_status(self, brain):
        """The adversarial case for the design choice. If stop_reason were
        merged into convergence_reason, this wording alone would relabel the
        run. It must not."""
        brain.state.stop_reason = "HALTED: downstream BUDGET_EXHAUSTED in a sub-task"
        sig = brain.signal_complete()
        assert sig["status"] == "INCOMPLETE", (
            f"status became {sig['status']!r} because of the WORDING of a stop "
            "reason. Status must derive from convergence_reason alone."
        )
        assert "BUDGET_EXHAUSTED" in sig["reason"], "the reason itself was lost"

    def test_a_genuine_budget_exhaustion_still_reports_BUDGET_EXHAUSTED(self, brain):
        """KNOWN-GOOD: the real path must be unchanged."""
        brain.state.convergence_reason = "BUDGET_EXHAUSTED(15)"
        assert brain.signal_complete()["status"] == "BUDGET_EXHAUSTED"

    def test_a_converged_run_is_unchanged(self, brain):
        brain.state.converged = True
        brain.state.convergence_reason = "CRITICAL_QUIESCENCE_CONVERGED (two-sided gate)"
        brain.state.stop_reason = "CRITICAL_QUIESCENCE_CONVERGED (two-sided gate)"
        sig = brain.signal_complete()
        assert sig["status"] == "CONVERGED"
        assert sig["reason"].startswith("CRITICAL_QUIESCENCE_CONVERGED")


class TestPrecedence:
    def test_convergence_reason_wins_over_stop_reason(self, brain):
        brain.state.converged = True
        brain.state.convergence_reason = "STATE_CONVERGED at round 12"
        brain.state.stop_reason = "loop exited"
        assert brain.signal_complete()["reason"] == "STATE_CONVERGED at round 12"

    def test_stop_reason_wins_over_failure_reason(self, brain):
        brain.state.stop_reason = "HALTED_IRREDUCIBLE_QUEUE_ALARM"
        brain.state.failure_reason = "generic"
        assert brain.signal_complete()["reason"] == "HALTED_IRREDUCIBLE_QUEUE_ALARM"

    def test_a_crash_still_reports_its_failure_reason(self, brain):
        brain.state.failed = True
        brain.state.failure_reason = "all models unreachable"
        sig = brain.signal_complete()
        assert sig["status"] == "FAILED" and sig["reason"] == "all models unreachable"

    def test_an_empty_reason_still_means_nothing_recorded_anywhere(self, brain):
        """This must remain possible and must remain visible. An empty reason
        now means the runner knew no cause -- a worse condition than any named
        stop, and one that should stay reportable rather than be papered over."""
        assert brain.signal_complete()["reason"] == ""


class TestItReachesDisk:
    def test_the_written_signal_carries_the_reason(self, brain, tmp_path):
        brain.state.stop_reason = "HALTED_IRREDUCIBLE_QUEUE_ALARM"
        brain.signal_complete()
        written = json.loads((tmp_path / "completion_signal.json").read_text())
        assert written["reason"] == "HALTED_IRREDUCIBLE_QUEUE_ALARM", (
            "the in-memory dict carries the reason but the file on disk does not; "
            "the file is what post-mortem tooling reads"
        )
        assert written["status"] == "INCOMPLETE"

    def test_stop_reason_survives_a_checkpoint_roundtrip(self, brain):
        """A resumed run must not lose why its predecessor stopped."""
        brain.state.stop_reason = "EXTENSION_STALLED"
        brain._save_checkpoint()
        brain.state.stop_reason = ""
        assert brain.load_checkpoint() is True
        assert brain.state.stop_reason == "EXTENSION_STALLED", (
            "stop_reason did not survive checkpoint save/load, so a resumed run "
            "reports an empty reason exactly as before"
        )


class TestTheRunnerActuallySetsIt:
    def test_both_propagation_sites_set_stop_reason_outside_the_converged_guard(self):
        """Pins the fix. If someone moves these back inside `if converged:` the
        defect returns silently, which is how it survived the 2026-05-18 fix."""
        import pathlib
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v2.py").read_text(encoding="utf-8")
        assert src.count("brain.state.stop_reason =") >= 2, (
            "fewer than two stop_reason assignments in the runner; one of the two "
            "stop paths no longer records its cause"
        )
        for marker in ("brain.state.stop_reason = f\"BURST_{reason_type}\"",
                       "brain.state.stop_reason = reason_str"):
            i = src.find(marker)
            assert i != -1, f"missing propagation: {marker}"
            # The assignment must come BEFORE the `if converged:` that follows it.
            after = src[i:i + 400]
            assert "if converged:" in after, f"no converged guard follows {marker}"
            assert after.index("if converged:") > 0, (
                f"{marker} sits inside the converged guard again"
            )
