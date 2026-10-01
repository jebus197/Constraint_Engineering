#!/usr/bin/env python3
"""A run's report says WHY the round loop stopped.

WHERE THIS CAME FROM. An external model (Grok) was asked about the round-cap
question and its recommendation ended: "Stop when the gate says convergence or
marginal novel-critical yield falls below a predeclared threshold or N_max is
hit -- and always record which reason fired." The founder asked whether that
input brought anything the panel had not already considered or discounted.

IT DID, AND IT WAS CHECKED RATHER THAN ACCEPTED. `brain.state.stop_reason` is
set on every exit path -- the runner even carries a fallback that names an
UNRECORDED_STOP rather than leaving it blank, added because "the runner did not
record why" is a different and worse condition than any named halt. But the
REPORT carried no stop field at all. Measured over
`commissioning_arm1_panel_20260929T214647Z`: its only stop-adjacent report keys
are `convergence_config`, `post_convergence_settled` and
`post_convergence_sweep`. The reason was computed in flight and discarded at the
edge.

WHY IT MATTERS HERE SPECIFICALLY. It is the difference between a run that
CONVERGED and a run that RAN OUT OF BUDGET -- exactly the distinction
`cap_recommendation` exists to surface, and exactly what the founder's ruling on
the round cap turns on. A reader of the artefact could not tell them apart.

Run:  python3 -m pytest bench/tests/test_stop_reason_reaches_the_report_2026-10-01.py -q
"""
from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    UNSET_STOP_REASON,
    stop_reason_fields,
)

RUNNER = REPO / "bench" / "reference_runner_v3.py"


class _State:
    def __init__(self, reason):
        self.stop_reason = reason


class TestANamedHaltIsRecordedAsOne:
    def test_a_named_reason_passes_through_verbatim(self):
        got = stop_reason_fields(_State("GAMMA_ALT_CONVERGED"))
        assert got["stop_reason"] == "GAMMA_ALT_CONVERGED"
        assert got["stop_reason_recorded"] is True

    def test_surrounding_whitespace_is_not_a_reason(self):
        got = stop_reason_fields(_State("  BURST_STALL  "))
        assert got["stop_reason"] == "BURST_STALL"
        assert got["stop_reason_recorded"] is True

    def test_the_irreducible_queue_halt_is_a_named_reason(self):
        got = stop_reason_fields(_State("IRREDUCIBLE_QUEUE_HALT"))
        assert got["stop_reason_recorded"] is True


class TestNotKnowingWhyIsNotTheSameAsAHalt:
    """The distinction the runner's own fallback comment insists on."""

    def test_the_unrecorded_fallback_is_not_counted_as_recorded(self):
        got = stop_reason_fields(_State(
            "UNRECORDED_STOP (the round loop exited by a path that names no "
            "reason; see the run log)"))
        assert got["stop_reason"].startswith("UNRECORDED_STOP")
        assert got["stop_reason_recorded"] is False, (
            "an unrecorded stop reads as a recorded one, so a run whose cause "
            "is unknown is indistinguishable from a clean convergence")

    def test_a_blank_reason_becomes_unset_and_is_not_recorded(self):
        for blank in ("", "   ", None):
            got = stop_reason_fields(_State(blank))
            assert got["stop_reason"] == UNSET_STOP_REASON, blank
            assert got["stop_reason_recorded"] is False, blank

    def test_a_missing_state_does_not_raise(self):
        got = stop_reason_fields(None)
        assert got["stop_reason"] == UNSET_STOP_REASON
        assert got["stop_reason_recorded"] is False

    def test_an_object_with_no_stop_reason_attribute_does_not_raise(self):
        got = stop_reason_fields(object())
        assert got["stop_reason_recorded"] is False


class TestItIsOnTheRunnersLivePath:
    """ANTI-UNREACHED-ADDITION, by PARSING the runner rather than reading it.

    A text search would match the helper's own definition and its comments.
    This finds a real call.
    """

    def test_the_runner_calls_the_helper(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name)
                 and n.func.id == "stop_reason_fields"]
        assert calls, (
            "nothing calls stop_reason_fields, so the report still carries no "
            "stop reason and this module is an addition nothing reaches")
        assert len(calls) >= 2, (
            f"only {len(calls)} call(s): the runner needs both the normal path "
            f"and the exception path, or a bookkeeping failure loses the field")

    def test_both_fields_are_merged_into_the_report_dict(self):
        """`result.update(...)` is how the 2 fields reach the report."""
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        merged = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == "update"
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "result"
            and any(isinstance(a, ast.Call) and isinstance(a.func, ast.Name)
                    and a.func.id == "stop_reason_fields" for a in n.args)
        ]
        assert merged, (
            "stop_reason_fields is called but its result never reaches "
            "`result`, so the report is unchanged")

    def test_the_helper_returns_exactly_the_two_documented_fields(self):
        got = stop_reason_fields(_State("X"))
        assert set(got) == {"stop_reason", "stop_reason_recorded"}, got
