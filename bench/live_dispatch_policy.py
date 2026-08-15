"""Single source of truth for "may this process dispatch to a live model?".

Why this module exists (2026-07-31)
-----------------------------------
Measurement on 2026-07-31 established that `python3 -m pytest bench/tests/`
was making live outbound model calls on any machine where the `claude` CLI is
installed and authenticated. 17 tests reached
`bench/immune_agents.py::_active_llm_classify`, which shells out to
`claude -p ... --model <haiku>` with a 15 s timeout under a global lock:
93 dispatches per full suite run, up to ~1,395 s of serialised model time,
paid for out of the founder's Max subscription, with test outcomes depending
on what the model happened to say that day.

The dispatch sites were *already* written to fail open: every one of them is
guarded by `if not _get_claude_cli(): return <fallback>`. On a machine with no
CLI the suite has always been silently offline. This module makes that same,
already-exercised offline branch the DEFAULT under pytest, so the suite behaves
identically everywhere instead of differing by whether a binary happens to be
on PATH.

Contract
--------
`live_dispatch_allowed()` is False when running under pytest, True otherwise.
Setting ``CDSFL_ALLOW_LIVE_DISPATCH=1`` restores live dispatch under pytest —
the live path is disabled by default, never made unreachable:

    CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/test_exp29_integration.py

The same environment variable also disables the network guard installed by
``bench/tests/conftest.py``, so one switch turns the whole suite live.

Scope boundary
--------------
This is a *policy* gate, not a *containment* mechanism. It closes the one
measured dispatch chain at its source. Containment for every other outbound
path — the scholarly APIs reached by the ouroboros cell, the huggingface hub,
and any dispatch site added in future — is the conftest guard's job. Do not
add per-module copies of this check; import this function.
"""

from __future__ import annotations

import logging
import os
import sys

__all__ = ["live_dispatch_allowed", "under_pytest", "OPT_IN_ENV"]

OPT_IN_ENV = "CDSFL_ALLOW_LIVE_DISPATCH"

_logger = logging.getLogger(__name__)
_warned = False


def under_pytest() -> bool:
    """True when this process is a pytest run.

    Three independent signals, because each covers a gap in the others:
      * ``PYTEST_CURRENT_TEST`` — set by pytest per test, but NOT during
        collection or module import, which is when several dispatch sites
        would first be reached.
      * ``pytest`` in ``sys.modules`` — covers collection and import time,
        and is set before any conftest runs.
      * ``CDSFL_UNDER_PYTEST`` — explicit override, set by the conftest, so a
        subprocess spawned by a test inherits the policy rather than deciding
        it is a production run.
    """
    return (
        "PYTEST_CURRENT_TEST" in os.environ
        or "pytest" in sys.modules
        or os.environ.get("CDSFL_UNDER_PYTEST") == "1"
    )


def live_dispatch_allowed() -> bool:
    """False under pytest unless ``CDSFL_ALLOW_LIVE_DISPATCH=1`` is set."""
    global _warned
    if os.environ.get(OPT_IN_ENV) == "1":
        return True
    if not under_pytest():
        return True
    if not _warned:
        _warned = True
        # Logged, never silent: if a real experiment ever imports pytest and
        # is throttled by this gate, the reason is in the log rather than
        # showing up as an unexplained absence of model calls.
        _logger.info(
            "live model dispatch disabled: running under pytest. "
            "Set %s=1 to re-enable.", OPT_IN_ENV,
        )
    return False
