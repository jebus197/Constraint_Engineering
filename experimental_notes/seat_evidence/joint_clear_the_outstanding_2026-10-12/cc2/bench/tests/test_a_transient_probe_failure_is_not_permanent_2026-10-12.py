# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a55773241753f6cff1e211d0972b3f5984798423d2d9e46fa272810de0f437f5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A transient interpreter-probe failure must not refuse correct falsifiers for ever.

WHAT IS UNDER TEST. `falsifier_verify._secondary_interpreter_roots` probes every
`python3` on the machine for its own installation roots and adds them to the
integrity gate's allow set, so a falsifier that legitimately spawns a second
interpreter is not refused on its import bootstrap. Each probe is a
`subprocess.run` with a 10s timeout and the result is memoised in a
module-level cache populated ONCE per process.

THE DEFECT THESE TESTS PIN. The fail-closed direction is correct -- an
interpreter that does not answer contributes no roots and the gate stays as
strict as before. But the result was CACHED whether or not discovery completed,
so a SINGLE transient timeout (one interpreter slow to start under load) kept a
partial root list for the LIFE of the runner process. Every later falsifier
spawning that interpreter was then refused with INTEGRITY_VIOLATION long after
the machine recovered -- reinstating exactly the false-refusal class the probe
exists to remove. EXECUTED 2026-10-12: one simulated TimeoutExpired on
/usr/bin/python3 dropped the root count from 22 to 15 and took a CORRECT
falsifier from CONFIRMED to INTEGRITY_VIOLATION on 13 bootstrap reads.
Producer: scripts/secondary_root_discovery_failure_is_not_permanent_2026-10-12.py.

NOTHING IS WEAKENED. The deny regions, the protected-key digests and the
refuse-on-denial behaviour are untouched; what changes is only whether an
INCOMPLETE discovery is remembered as if it were whole.
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import bench.falsifier_verify as fv  # noqa: E402

TARGET = "/usr/bin/python3"


@pytest.fixture(autouse=True)
def _reset_discovery_state():
    """Each test starts from an unprobed module and leaves it unprobed."""
    saved = (fv._SECONDARY_ROOTS_CACHE, fv._SECONDARY_ROOTS_ATTEMPTS,
             fv._SECONDARY_ROOTS_UNPROBEABLE)
    fv._SECONDARY_ROOTS_CACHE = None
    fv._SECONDARY_ROOTS_ATTEMPTS = 0
    fv._SECONDARY_ROOTS_UNPROBEABLE = []
    yield
    (fv._SECONDARY_ROOTS_CACHE, fv._SECONDARY_ROOTS_ATTEMPTS,
     fv._SECONDARY_ROOTS_UNPROBEABLE) = saved


def _timeout_for(target):
    real = subprocess.run

    def flaky(*a, **k):
        cmd = a[0] if a else k.get("args")
        if isinstance(cmd, (list, tuple)) and cmd and str(cmd[0]) == target:
            raise subprocess.TimeoutExpired(cmd=target, timeout=10)
        return real(*a, **k)
    return real, flaky


def test_the_retry_bound_is_declared_and_reachable():
    """A bound nothing reaches is not additive either."""
    assert fv.SECONDARY_ROOTS_DISCOVERY_ATTEMPTS >= 2, (
        "a bound of 1 is the unrepaired behaviour: no retry at all"
    )
    assert hasattr(fv, "secondary_interpreter_discovery_incomplete")


def test_a_complete_discovery_is_cached_exactly_once():
    """The ordinary path is unchanged: one probe pass per process."""
    first = fv._secondary_interpreter_roots()
    assert fv._SECONDARY_ROOTS_CACHE is not None, (
        "a discovery in which every candidate answered must still be cached, "
        "or every falsifier pays for a fresh probe sweep"
    )
    assert fv._SECONDARY_ROOTS_ATTEMPTS == 1
    assert fv._secondary_interpreter_roots() == first
    assert fv._SECONDARY_ROOTS_ATTEMPTS == 1, "the cache was not served"


@pytest.mark.skipif(not os.path.isfile(TARGET),
                    reason=f"{TARGET} absent; this defect class cannot arise")
def test_an_incomplete_discovery_is_not_cached():
    """THE DEFECT. One timeout must not be remembered as a complete answer."""
    real, flaky = _timeout_for(TARGET)
    subprocess.run = flaky
    try:
        partial = fv._secondary_interpreter_roots()
    finally:
        subprocess.run = real
    assert fv._SECONDARY_ROOTS_CACHE is None, (
        "an incomplete discovery was cached, so a transient probe timeout "
        "refuses correct falsifiers for the life of the process"
    )
    # And the gate did stay strict during the transient, which is the correct
    # fail-closed direction and is NOT what is being changed.
    assert TARGET in fv._SECONDARY_ROOTS_UNPROBEABLE
    # The machine has recovered; the gate must recover with it.
    full = fv._secondary_interpreter_roots()
    assert len(full) > len(partial), (
        "discovery was not retried after the transient passed"
    )
    assert fv._SECONDARY_ROOTS_CACHE is not None
    assert fv.secondary_interpreter_discovery_incomplete() == []


@pytest.mark.skipif(not os.path.isfile(TARGET),
                    reason=f"{TARGET} absent; this defect class cannot arise")
def test_a_permanently_unprobeable_interpreter_is_accepted_and_NAMED():
    """The bound must terminate, and the exclusion must never be silent."""
    real, flaky = _timeout_for(TARGET)
    subprocess.run = flaky
    try:
        for _ in range(fv.SECONDARY_ROOTS_DISCOVERY_ATTEMPTS):
            fv._secondary_interpreter_roots()
    finally:
        subprocess.run = real
    assert fv._SECONDARY_ROOTS_CACHE is not None, (
        "discovery must stop retrying a permanently dead interpreter, or "
        "every falsifier pays a 10s timeout for it"
    )
    assert fv._SECONDARY_ROOTS_ATTEMPTS == fv.SECONDARY_ROOTS_DISCOVERY_ATTEMPTS
    assert TARGET in fv.secondary_interpreter_discovery_incomplete(), (
        "an interpreter whose roots are missing must be NAMED, so an "
        "INTEGRITY_VIOLATION against a falsifier spawning it is readable as a "
        "false refusal rather than as a verdict"
    )


@pytest.mark.skipif(not os.path.isfile(TARGET),
                    reason=f"{TARGET} absent; this defect class cannot arise")
def test_end_to_end_a_correct_falsifier_survives_a_transient_timeout():
    """The consequence, through the real gate rather than the root count."""
    falsifier = (
        "import subprocess\n"
        f"p = subprocess.run(['{TARGET}', '-c', 'import json, ssl, sysconfig'],"
        " capture_output=True, text=True)\n"
        "assert p.returncode == 0, p.stderr[-300:]\n"
        "print('FALSIFIED')\n"
    )
    repo = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    healthy = fv.reverify_falsifier(falsifier, repo_root=repo, timeout=120)
    if healthy != "CONFIRMED":
        pytest.skip(f"healthy baseline is {healthy}, not CONFIRMED; this "
                    "machine cannot measure the transient")

    fv._SECONDARY_ROOTS_CACHE = None
    fv._SECONDARY_ROOTS_ATTEMPTS = 0
    real, flaky = _timeout_for(TARGET)
    subprocess.run = flaky
    try:
        fv._secondary_interpreter_roots()
    finally:
        subprocess.run = real
    after = fv.reverify_falsifier(falsifier, repo_root=repo, timeout=120)
    assert after == "CONFIRMED", (
        f"a CORRECT falsifier went CONFIRMED -> {after} because one probe "
        "timed out once; the false-refusal class is reinstated"
    )
