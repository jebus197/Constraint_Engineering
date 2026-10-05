# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ee347647e479381e475e8223c9d3b4ff8f4af3169f0e2f5c595e38602551ee21
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""`co_names` is a different proxy from source text, not a strictly stronger one.

THE QUESTION. On 2026-10-05 three source-text assertions were converted to read
`run_experiment.__code__.co_names` and `.co_consts` instead of matching strings in
`bench/reference_runner_v3.py`
(`bench/tests/test_in_round_falsifier_clears_only_on_execution_2026-10-05.py`,
class `TestItIsWiredIntoTheRoundLoop`, whose stated purpose is "An addition
nothing reaches is not additive"). Is reading the compiled code object genuinely
stronger, or is it one proxy swapped for another?

THE ANSWER, demonstrated below on 7 synthetic functions rather than argued.

STRONGER, on the axis it was chosen for. `co_names` holds the global names the
compiled function references and `co_consts` its literal constants, so a comment,
a docstring, or a commented-out call cannot satisfy either. That is exactly the
failure the conversion was made to escape, and it escapes it.

NOT STRONGER on two other axes, and one of them is the axis the test's own
sentence is about:

  * IT CANNOT DISTINGUISH REFERENCE FROM INVOCATION. A name on a branch that is
    never taken is still in `co_names`. So a mechanism gated behind a config flag
    that is False in every real config passes the probe while doing nothing --
    which is precisely "an addition nothing reaches", the class this project has
    confirmed 11 times since 2026-08-01. A source-text match has the same blind
    spot, so nothing is gained here; the point is that nothing is gained, while
    the test's wording claims the property.
  * IT IS SCOPED TO ONE CODE OBJECT, where a source-text match is scoped to the
    file. Moving the call into a helper, a nested function, or a generator
    expression leaves behaviour identical and turns the probe red. That is a NEW
    fragility in the same family as the one the conversion was escaping: a
    correct change reddens a guard that asserts nothing about it.

WHAT WOULD BE SUFFICIENT, stated because the boundary should not be left implied:
only execution settles "the round loop calls it". No test in `bench/tests/`
executes `run_experiment`, in-process or as a subprocess, so that instrument does
not exist today and building it is a real piece of work -- `bench/tests/
conftest.py` denies the network softly, so a run under pytest would exercise the
offline fallbacks rather than the dispatch path, and `bench/tools/
sim_dispatch_shim.py` is the seam that would have to be driven instead.

Run:  python3 scripts/co_names_is_a_different_proxy_2026-10-05.py
"""
from __future__ import annotations

import argparse
import sys

NAME = "record_in_round_falsifier_reattachments"
KEY = "round_falsifier_reattachments"


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="co_names_is_a_different_proxy_2026-10-05.py",
        description=(__doc__ or "").strip().split("\n\n")[0])
    return p.parse_args(argv)


# ---------------------------------------------------------------- probe subjects
def dead_branch(cfg, recorder):
    """The call is gated on a flag. 17 of 49 real configs do not arm
    `inround_reask_enabled`; a gate like that is how an addition reaches nothing."""
    if cfg.get("inround_reask_enabled"):
        recorder(record_in_round_falsifier_reattachments)
    return {"round_falsifier_reattachments": []}


def reference_without_call():
    """The name is loaded and thrown away, and the key only appears in an error."""
    fn = record_in_round_falsifier_reattachments        # noqa: F821 — probe subject
    del fn
    raise KeyError("round_falsifier_reattachments")


def moved_into_a_helper():
    """Correct wiring, one hop away. Behaviour identical, probe blind."""
    return _helper()


def _helper():
    return record_in_round_falsifier_reattachments()    # noqa: F821 — probe subject


def inside_a_generator_expression():
    """A genexp has its own code object in every CPython to date."""
    return list(record_in_round_falsifier_reattachments(x) for x in ())  # noqa: F821


def key_assembled_at_runtime(v):
    return {"round_falsifier_" + "".join(["reatt", "achments"]): v}


def key_as_a_keyword_argument(v):
    """`dict(k=v)` stores the keyword NAMES as a tuple constant, so membership of
    the bare string fails."""
    return dict(round_falsifier_reattachments=v)


_CASES = [
    ("FALSE PASS", "a call on a branch never taken", lambda: NAME in dead_branch.__code__.co_names),
    ("FALSE PASS", "a name referenced and never called", lambda: NAME in reference_without_call.__code__.co_names),
    ("FALSE PASS", "the key only in a raise message", lambda: KEY in reference_without_call.__code__.co_consts),
    ("FALSE FAIL", "the call moved into a helper", lambda: NAME not in moved_into_a_helper.__code__.co_names),
    ("FALSE FAIL", "the call inside a generator expression", lambda: NAME not in inside_a_generator_expression.__code__.co_names),
    ("FALSE FAIL", "the key assembled at runtime", lambda: KEY not in key_assembled_at_runtime.__code__.co_consts),
    ("FALSE FAIL", "the key passed as a keyword argument", lambda: KEY not in key_as_a_keyword_argument.__code__.co_consts),
]


def main(argv=None) -> int:
    _parse_args(argv)
    print(f"python {sys.version.split()[0]}")
    print("=" * 78)
    print("co_names / co_consts MEMBERSHIP: 7 CASES WHERE IT GIVES THE WRONG ANSWER")
    print("=" * 78)
    print(f"  {'kind':<11}{'case':<44}{'demonstrated':>13}")
    failures = 0
    for kind, label, probe in _CASES:
        got = bool(probe())
        if not got:
            failures += 1
        print(f"  {kind:<11}{label:<44}{'yes' if got else 'NO':>13}")
    print()
    print("-" * 78)
    print("CONTROL: the dead branch really does not execute")
    print("-" * 78)
    calls = []
    dead_branch({}, lambda fn: calls.append(fn))
    print(f"  times the recorder was invoked            : {len(calls)}")
    print(f"  name present in co_names regardless       : "
          f"{NAME in dead_branch.__code__.co_names}")
    print("  So the probe answers 'wired' for a mechanism that did nothing.")
    print()
    if failures:
        print(f"  *** {failures} case(s) did not reproduce on this interpreter.")
        print("  *** The CPython detail they rest on may have changed; the claim")
        print("  *** above is UNVERIFIED on this build and must be re-derived.")
        return 1
    print("  All 7 reproduce. co_names/co_consts is immune to comments and")
    print("  docstrings and blind to reachability and to scope. It is a different")
    print("  proxy, better on one axis and worse on another, and the test's")
    print("  sentence 'an addition nothing reaches is not additive' asks for a")
    print("  property no static probe can supply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
