"""The delegation resolver must still FAIL when the behaviour is really gone.

THE RISK THIS ADDRESSES. On 2026-10-11 three source-text guards were repaired by
teaching them to follow a thin wrapper to its delegate (`bench/tests/_delegation.py`),
after a split on 2026-10-07 left all three red for 4 days while the system was sound.
The obvious way to get them green is to widen what the assertion looks at until it
cannot fail -- which would convert 3 red guards into 3 vacuous ones and lose the
property outright. This file is the ratchet against that: every assertion below
MUTATES the source so the marker is genuinely absent, and requires the resolver to
report its absence.

`execute-do-not-grep` applied to the repair itself: these tests CALL the resolver
against synthesised trees rather than reading it.
"""
from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from _delegation import callers_of, delegate_names, delegated_source  # noqa: E402

WRAPPER_SPLIT = '''
def _records_seat_completion(f):
    return f

@_records_seat_completion
def _dispatch_single_model(mc, prompt):
    return _dispatch_single_model_inner(mc, prompt)

def _dispatch_single_model_inner(mc, prompt):
    if _ASK_CORRECTED_COPY["on"]:
        pass
    else:
        print("NO ask: the gate is off")
    return dispatch_to_model(mc, prompt)

def _unrelated_helper(x):
    return _ASK_CORRECTED_COPY_SOMETHING_ELSE
'''


class TestItFindsWhatMoved:
    def test_the_marker_in_the_delegate_is_found_through_the_wrapper(self):
        body = delegated_source(ast.parse(WRAPPER_SPLIT), "_dispatch_single_model")
        assert "_ASK_CORRECTED_COPY" in body
        assert "NO ask" in body

    def test_the_delegate_is_named(self):
        names = delegate_names(ast.parse(WRAPPER_SPLIT), "_dispatch_single_model")
        assert names == ["_dispatch_single_model_inner"]

    def test_the_wrapper_is_credited_as_a_caller_of_the_primitive(self):
        assert "_dispatch_single_model" in callers_of(
            ast.parse(WRAPPER_SPLIT), "dispatch_to_model")


class TestItStillFailsWhenTheBehaviourIsGone:
    def test_deleting_the_marker_from_the_delegate_is_detected(self):
        mutated = WRAPPER_SPLIT.replace('if _ASK_CORRECTED_COPY["on"]:', "if True:")
        body = delegated_source(ast.parse(mutated), "_dispatch_single_model")
        assert "_ASK_CORRECTED_COPY" not in body, (
            "the resolver reports a marker that is no longer on the dispatch path")

    def test_deleting_the_announcement_is_detected(self):
        mutated = WRAPPER_SPLIT.replace('print("NO ask: the gate is off")', "pass")
        body = delegated_source(ast.parse(mutated), "_dispatch_single_model")
        assert "NO ask" not in body

    def test_removing_the_primitive_call_is_detected(self):
        mutated = WRAPPER_SPLIT.replace(
            "return dispatch_to_model(mc, prompt)", "return None")
        assert "_dispatch_single_model" not in callers_of(
            ast.parse(mutated), "dispatch_to_model")

    def test_a_renamed_function_is_a_loud_failure_not_a_silent_pass(self):
        mutated = WRAPPER_SPLIT.replace("def _dispatch_single_model(", "def _renamed(")
        assert delegated_source(ast.parse(mutated), "_dispatch_single_model") == "", (
            "a renamed function must return empty so the guard's own "
            "'is gone — renamed, not merely split' assertion fires")


class TestItDoesNotSweepInEverything:
    def test_an_unrelated_function_is_not_included(self):
        body = delegated_source(ast.parse(WRAPPER_SPLIT), "_dispatch_single_model")
        assert "_unrelated_helper" not in body, (
            "the resolver is returning unrelated source, which would make every "
            "assertion pass for the wrong reason")

    def test_following_delegation_is_what_does_the_work(self):
        """Without the follow, the wrapper is NOT a caller — proving the repair
        is load-bearing rather than cosmetic."""
        tree = ast.parse(WRAPPER_SPLIT)
        assert "_dispatch_single_model" not in callers_of(
            tree, "dispatch_to_model", follow_delegation=False)
        assert "_dispatch_single_model" in callers_of(
            tree, "dispatch_to_model", follow_delegation=True)

    def test_a_non_delegate_call_is_not_followed(self):
        """Only a callee whose name EXTENDS the caller's counts, so an ordinary
        helper call cannot drag arbitrary source in."""
        src = ('def f(x):\n    return some_other_function(x)\n'
               'def some_other_function(x):\n    return "MARKER"\n')
        assert delegate_names(ast.parse(src), "f") == []
        assert "MARKER" not in delegated_source(ast.parse(src), "f")


class TestTheRealRunnerStillHoldsTheProperty:
    def test_the_live_dispatch_path_reaches_the_primitive(self):
        import reference_runner_v3 as R
        tree = ast.parse(pathlib.Path(R.__file__).read_text(encoding="utf-8"))
        assert "_dispatch_single_model" in callers_of(tree, "dispatch_to_model")

    def test_the_live_shim_signature_matches_the_live_primitive(self):
        """The 2026-10-11 defect in one line: the primitive gained
        `require_substance` and the shim did not."""
        import inspect
        import reference_runner_v3 as R
        from bench.tools import sim_dispatch_shim as S
        assert (list(inspect.signature(R.dispatch_to_model).parameters)
                == list(inspect.signature(S.make_shim()).parameters))
