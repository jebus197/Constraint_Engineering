"""A probe that cannot answer must cost neither coverage nor silence.

THE DEFECT, MEASURED IN THE JOINT ROUND OF 2026-10-12 BY BOTH FREE SEATS.
`_secondary_interpreter_roots` probes each interpreter by running it, and
cached the result for the life of the process. On a loaded machine every probe
timed out, the function returned 0 roots, and the cache made that permanent:
one 10-second load spike at the first falsifier returned the integrity gate to
refusing EVERY spawned-interpreter falsifier for the whole run. Measured
end to end on the unfixed tree, a C0050-class falsifier went CONFIRMED ->
INTEGRITY_VIOLATION and stayed there after the load cleared.

THE TWO SEATS PROPOSED DIFFERENT REPAIRS AND BOTH WERE RIGHT ABOUT SOMETHING.
cc2 made the failure TRANSIENT: never cache an incomplete discovery, and retry.
fable made the failure HARMLESS: on probe failure, derive the interpreter's
roots structurally from its own path, which cannot time out. Measured, fable's
fallback yields 41 roots under total probe failure against 39 healthy, so
coverage is not merely preserved but exceeded -- which is why cc2's retry was
NOT taken: it buys no coverage and costs up to 30 seconds per falsifier on an
8 GiB machine. But cc2 was right that permanence is a defect in its own right:
the fallback set is a structural guess and WIDER than what the interpreters
report, and caching it would persist that wider allow set long after the spike.

COMPOSED, AND THE COMPOSITION IS THE POINT: fall back so the moment is
harmless, decline to cache so the moment stays a moment, and NAME the
interpreters whose roots are guesses so a refusal against one of them is not
read as a verdict. The naming is cc2's excluded-implies-reported discipline,
from the founder's 2026-10-02 key-access ruling.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.falsifier_verify as fv  # noqa: E402


def _cold():
    fv._SECONDARY_ROOTS_CACHE = None
    fv._SECONDARY_ROOTS_RAN = False


def _with_dead_probes(fn):
    """Run fn with every probe raising a timeout, then restore."""
    real = subprocess.run

    def dead(*a, **k):
        raise subprocess.TimeoutExpired(cmd="probe", timeout=10)

    subprocess.run = dead
    try:
        return fn()
    finally:
        subprocess.run = real


def test_total_probe_failure_does_not_cost_coverage():
    _cold()
    healthy = len(fv._interpreter_roots())
    _cold()
    degraded = len(_with_dead_probes(lambda: fv._interpreter_roots()))
    assert degraded >= healthy, (
        f"a loaded machine cost the carve-out: {degraded} roots against "
        f"{healthy} healthy. Every spawned-interpreter falsifier is now "
        f"refused on its import bootstrap.")


def test_a_fallback_result_is_not_cached():
    """cc2's half. The wider structural set must not outlive the load spike."""
    _cold()
    _with_dead_probes(lambda: fv._interpreter_roots())
    assert fv._SECONDARY_ROOTS_CACHE is None, (
        "the fallback result was cached, so a wider allow set now persists "
        "for the life of the process")
    healthy_again = len(fv._interpreter_roots())
    _cold()
    assert healthy_again == len(fv._interpreter_roots()), (
        "the next call did not return to the probed roots")


def test_the_healthy_path_still_caches():
    """Not caching at all would pay the probe cost on every falsifier."""
    _cold()
    fv._interpreter_roots()
    assert fv._SECONDARY_ROOTS_CACHE is not None, (
        "the healthy result is no longer cached; every falsifier now pays "
        "the full probe sweep")


def test_the_fallback_is_NAMED_not_silent():
    """An allowance derived from a guess must say that it is a guess."""
    _cold()
    named = _with_dead_probes(
        lambda: (fv._interpreter_roots(),
                 fv.secondary_interpreter_discovery_fell_back())[1])
    assert named, (
        "every probe failed and the reader named nothing; a false refusal "
        "against one of these interpreters would look like a verdict")


def test_the_reader_is_silent_when_there_is_nothing_to_say():
    _cold()
    fv._interpreter_roots()
    assert fv.secondary_interpreter_discovery_fell_back() == [], (
        "every probe answered, so the reader must say nothing")


def test_the_reader_does_not_overwrite_what_it_reports():
    """THE DEFECT THIS PINS WAS MINE, 2026-10-12, AND SO WAS THE FIRST VERSION
    OF THIS TEST, WHICH DID NOT CATCH IT.

    The reader first keyed on the CACHE being populated. A pass that fell back
    does not populate the cache, so calling the reader re-ran discovery -- and
    if the load had cleared by then, it re-ran HEALTHILY and returned an empty
    list for a failure it had just observed.

    THE FIRST VERSION OF THIS TEST READ THE REPORT WHILE THE PROBES WERE STILL
    DEAD, so the re-run fell back too, named the same interpreters, and the
    mutation was invisible: reverting the reader to key on the cache left all 6
    tests green. The sequence that exposes it is the real one -- the failure
    happens, the machine RECOVERS, and only then does something ask what
    happened. Verified by mutation 2026-10-12: keying on the cache again turns
    this red.
    """
    _cold()
    during = _with_dead_probes(
        lambda: (fv._interpreter_roots(),
                 fv.secondary_interpreter_discovery_fell_back())[1])
    assert during, "every probe failed and nothing was named during the failure"
    # The load clears. Nothing else runs. Now ask what happened.
    after = fv.secondary_interpreter_discovery_fell_back()
    assert after == during, (
        f"the reader re-ran discovery and overwrote its own record: it named "
        f"{during} during the failure and {after} once the probes recovered")
