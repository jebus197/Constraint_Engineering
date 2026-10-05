# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 359bd05477141fd3b2940fa1fd13b305d16fdd9bf59a37c4aaa0883ccb5c92ee
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""`co_names` is a different proxy, not a stronger one. Here is what it misses.

CONTEXT. `test_in_round_falsifier_clears_only_on_execution_2026-10-05.py` moved
its two wiring checks off source-text matching and onto
`run_experiment.__code__.co_names` / `.co_consts`, on the stated ground that
"a comment, a docstring or a commented-out call cannot satisfy either". That part
is TRUE and is a real gain. The claim that it establishes the call is REACHED is
not, and the swap also introduces a false-FAIL surface the source-text version
did not have.

MEASURED 2026-10-05 by compiling seven one-function modules and reading the code
object (producer: `scripts/co_names_probe_is_a_proxy_2026-10-05.py`):

    shape                              in co_names   in co_consts
    if False: f(1)                     True          False   <- FALSE PASS
    if cfg.never_true: f(1)            True          False   <- FALSE PASS
    bare name `f`, never called        True          False   <- FALSE PASS
    cfg.f  (attribute, unrelated obj)  True          False   <- FALSE PASS
    call moved into a helper           False         False   <- FALSE FAIL
    call moved into a lambda           False         False   <- FALSE FAIL
    getattr(mod, "f")(cfg)             False         True    <- FALSE PASS on consts

So, precisely:

FALSE PASS for `test_the_round_loop_calls_it`. CPython keeps the name in
`co_names` even for an `if False:` block it eliminates, and keeps it for a
dead-flag branch, a bare mention, or an attribute of ANY object that happens to
share the name. None of the four is a call, and the test's message claims
"it is defined and never called" is excluded. It is not.

FALSE FAIL for the same test. `co_names` is per-code-object. Moving the call into
a module-level helper, a nested function, a lambda or a comprehension -- every
one a behaviour-preserving refactor -- empties the name from
`run_experiment.__code__.co_names` and reds the test. A grep over the same file
would have survived all four. This is the identical fragility class the
conversion was made to escape, relocated rather than removed.

FALSE PASS for `test_its_record_is_persisted`. `co_consts` proves the string
`"round_falsifier_reattachments"` is a literal in that one code object. It does
not prove persistence. The same literal in a log line, an error message, a
discarded dict, or a `getattr` lookup satisfies it identically.

WHAT THIS FILE ADDS, and it is one function. `_calls(code, name)` requires a
CALL-family opcode to consume the loaded global, which closes the bare-mention
and the attribute cases, and is pinned below against all seven shapes so its own
limits are measured rather than assumed. IT DOES NOT CLOSE THE DEAD-BRANCH CASE.
A reachability proof needs execution, and `run_experiment` cannot be executed in
a unit test; the honest statement is that the dead-branch false pass remains open
for every static idiom, `co_names` and this one alike.

NOTHING IS REMOVED. The two `co_names` checks stand; this is the stronger
predicate beside them, wired to the same real target.
"""
from __future__ import annotations

import dis

import pytest

#: Opcodes that consume a callable from the stack, across the 3.11-3.13 range.
_CALL_OPS = {"CALL", "CALL_FUNCTION_EX", "CALL_KW", "CALL_FUNCTION",
             "CALL_METHOD", "PRECALL"}
#: Opcodes that prove the loaded value went somewhere OTHER than a call.
_SINKS = {"STORE_FAST", "STORE_NAME", "STORE_GLOBAL", "STORE_ATTR",
          "STORE_SUBSCR", "POP_TOP", "RETURN_VALUE", "YIELD_VALUE"}


def _calls(code, name: str) -> bool:
    """Is `name` loaded as a GLOBAL and then consumed by a CALL?

    Forward scan from each `LOAD_GLOBAL name` to the first call-family opcode,
    abandoning that occurrence if a non-call sink intervenes. `LOAD_ATTR` is
    deliberately NOT accepted as the load, which is what rejects the
    `cfg.<name>` shape that `co_names` cannot distinguish.
    """
    instrs = list(dis.get_instructions(code))
    for i, ins in enumerate(instrs):
        if ins.opname != "LOAD_GLOBAL" or ins.argval != name:
            continue
        for nxt in instrs[i + 1:]:
            if nxt.opname in _CALL_OPS:
                return True
            if nxt.opname in _SINKS:
                break
    return False


_SHAPES = {
    "dead_if_false":  "def f(cfg):\n    if False:\n        target(1)\n    return 1\n",
    "dead_flag":      "def f(cfg):\n    if cfg.never_true:\n        target(1)\n    return 1\n",
    "bare_mention":   "def f(cfg):\n    target\n    return 1\n",
    "attribute":      "def f(cfg):\n    return cfg.target\n",
    "real_call":      "def f(cfg):\n    return target(cfg)\n",
    "moved_to_helper": "def h(cfg):\n    target(cfg)\ndef f(cfg):\n    return h(cfg)\n",
    "moved_to_lambda": "def f(cfg):\n    g = lambda c: target(c)\n    return g(cfg)\n",
}


def _compile(src):
    ns = {}
    exec(compile(src, "<probe>", "exec"), ns)
    return ns["f"].__code__


class TestTheStrongerPredicateIsPinned:
    """Every shape measured, including the two this predicate still cannot see."""

    @pytest.mark.parametrize("shape", ["bare_mention", "attribute"])
    def test_it_rejects_what_co_names_accepts(self, shape):
        co = _compile(_SHAPES[shape])
        assert "target" in co.co_names, (
            f"{shape} must still be in co_names, or this comparison is not about "
            f"the idiom under review")
        assert not _calls(co, "target"), f"{shape} is not a call and was accepted"

    def test_it_accepts_a_real_call(self):
        """ANTI-VACUITY. A predicate that rejected everything would red the real
        target below and look like a finding."""
        assert _calls(_compile(_SHAPES["real_call"]), "target")

    @pytest.mark.parametrize("shape", ["dead_if_false", "dead_flag"])
    def test_the_dead_branch_case_is_OPEN_and_recorded_as_open(self, shape):
        """NOT a bug in `_calls` -- a limit of every static idiom, asserted so
        that nobody reads this file as a reachability proof. `if False:` has its
        block eliminated, so `_calls` rejects it; the dead FLAG branch compiles a
        real CALL and is accepted. Only execution separates the second from a
        live call."""
        co = _compile(_SHAPES[shape])
        if shape == "dead_flag":
            assert _calls(co, "target"), (
                "a branch on a flag that is never True is indistinguishable from "
                "a live call in bytecode; if this ever stops holding, the claim "
                "in this file's docstring must be corrected")
        else:
            assert not _calls(co, "target")

    @pytest.mark.parametrize("shape", ["moved_to_helper", "moved_to_lambda"])
    def test_a_behaviour_preserving_refactor_breaks_BOTH_idioms(self, shape):
        """THE FALSE-FAIL SURFACE THE SWAP INTRODUCED, pinned. A grep over the
        same file survives both of these; `co_names` and `_calls` do not."""
        co = _compile(_SHAPES[shape])
        assert "target" not in co.co_names
        assert not _calls(co, "target")


class TestTheRealTargetSatisfiesTheStrongerPredicate:
    def test_the_round_loop_actually_CALLS_the_reattachment_recorder(self):
        from bench.reference_runner_v3 import run_experiment
        assert _calls(run_experiment.__code__,
                      "record_in_round_falsifier_reattachments"), (
            "the name is in co_names but no CALL consumes it, so the wiring check "
            "beside this one is satisfied by a mention rather than by a call")

    def test_the_sibling_recorder_is_also_a_call(self):
        from bench.reference_runner_v3 import run_experiment
        assert _calls(run_experiment.__code__, "record_in_round_withdrawals")

    def test_a_name_no_runner_references_is_rejected(self):
        from bench.reference_runner_v3 import run_experiment
        assert not _calls(run_experiment.__code__,
                          "a_name_no_runner_would_ever_reference")
