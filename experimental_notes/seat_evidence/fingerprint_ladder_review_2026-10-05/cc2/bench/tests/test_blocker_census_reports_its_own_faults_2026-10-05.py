# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: edb36390c32e5b97a8af5f09f7e10c656775dae3478038d6728706f855d62d77
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The blocker census must report a fault in its own counter, not absorb it.

WHY THIS FILE EXISTS. On 2026-10-05 the leave-one-out handler in
`scripts/the_blockers_are_shown_as_settled_2026-10-05.py` was repaired from
`except Exception: pass` to a recorded `probe_errors` entry. THREE LINES ABOVE
that repair, the outer whole-registry call carried `except Exception: continue`
-- the same defect, in the same loop, surviving the repair that named it.

MEASURED BEFORE REPAIR, by making `FindingRegistry.unverified_critical_count`
raise on the whole-registry call only, on `bench/logs/exp36_evidence_latest`:

    BASELINE  blockers attributed by leave-one-out : 7
    FAULTED   blockers attributed by leave-one-out : 0
    both      archived registries read             : 1
    both      leave-one-out probes that raised     : 0 (so the attribution is
                                                        complete, not a lower bound)

So the measurement lost its entire population, kept the denominator it had
already incremented, and still asserted completeness. That is the verification-
integrity class: the headline rate would have read BETTER than the truth with
nothing on the page to say a run had been dropped.

WHY A TARGETED TEST AND NOT A WIDER LINT.
`test_operational_scripts.py::test_no_bare_or_silently_swallowed_exception_handlers`
flags only handlers whose body is exactly `pass`, so it cannot see
`except Exception: continue`. Widening it was measured first: 57 handlers across
the 281-script population are `except Exception: continue/break` with no name
binding. Turning 57 pre-existing sites red is not additive and is more elaborate
than this problem requires, so the guard stays as it is and the script whose
figure is quoted gets an executing test instead. The 57 are recorded in
`scripts/swallowed_continue_census_2026-10-05.py` for whoever wants the wider job.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "the_blockers_are_shown_as_settled_2026-10-05.py"
#: 217 entries, 7 blockers -- small and present in every checkout that carries logs.
RUN = REPO / "bench" / "logs" / "exp36_evidence_latest"


@pytest.fixture(scope="module")
def census():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("blocker_census", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(mod, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main(argv)
    return rc, buf.getvalue()


requires_run = pytest.mark.skipif(
    not (RUN / "runner_state.json").is_file(),
    reason=f"{RUN.name} is not in this checkout, so the fault cannot be injected "
           f"OR refuted here -- run where bench/logs/ is populated")


@requires_run
class TestACounterFaultIsVisible:

    def test_the_baseline_attributes_blockers(self, census):
        """ANTI-VACUITY. If this run attributed 0 blockers the injection below
        would prove nothing, because 0 is also the faulted answer."""
        rc, out = _run(census, ["--run", str(RUN)])
        assert rc == 0
        n = [l for l in out.splitlines() if "blockers attributed by leave-one-out" in l]
        assert n, out[-900:]
        assert int(n[0].split(":")[1].strip()) > 0, n[0]
        assert "runs dropped by a counter fault           : 0" in out

    def test_a_raising_counter_is_REPORTED_and_not_absorbed(self, census, monkeypatch):
        """THE PROPERTY. A fault in the counter must appear on the page."""
        from bench.reference_runner_v3 import FindingRegistry
        orig = FindingRegistry.unverified_critical_count
        seen_max = {"n": 0}

        def flaky(self):
            n = len(self.entries)
            seen_max["n"] = max(seen_max["n"], n)
            if n >= seen_max["n"]:       # the whole-registry call, not a probe
                raise RuntimeError("injected counter fault")
            return orig(self)

        monkeypatch.setattr(FindingRegistry, "unverified_critical_count", flaky)
        rc, out = _run(census, ["--run", str(RUN)])
        assert rc == 0, "the census must still finish and say what happened"
        assert "run(s) were DROPPED" in out, (
            "a fault in the A4 counter left no trace: the run vanished from every "
            "numerator while the denominator kept it, and the page still read as a "
            "complete measurement.\n" + out[-1200:])
        assert "LOWER BOUND over a REDUCED population" in out, out[-1200:]

    def test_the_dropped_run_does_not_inflate_the_denominator(self, census, monkeypatch):
        """`runs_total += 1` used to happen BEFORE the counter call, so a dropped
        run still counted in `archived registries read`."""
        from bench.reference_runner_v3 import FindingRegistry
        orig = FindingRegistry.unverified_critical_count
        seen_max = {"n": 0}

        def flaky(self):
            n = len(self.entries)
            seen_max["n"] = max(seen_max["n"], n)
            if n >= seen_max["n"]:
                raise RuntimeError("injected counter fault")
            return orig(self)

        monkeypatch.setattr(FindingRegistry, "unverified_critical_count", flaky)
        _rc, out = _run(census, ["--run", str(RUN)])
        line = [l for l in out.splitlines() if "archived registries read" in l]
        assert line, out[-600:]
        assert int(line[0].split(":")[1].strip()) == 0, (
            "a run the counter could not score was still counted as read, so the "
            "'runs with >=1' rate is computed over a denominator that includes "
            "runs contributing to no numerator: " + line[0])


class TestAnEmptyDenominatorIsNotAToolDisagreement:
    """`nan != nan`, so the two-tool agreement check fired UNVERIFIED on a
    population with no members -- the instrument blaming scipy and statsmodels
    for a fault in its own reading loop."""

    def test_zero_of_zero_says_so(self, census):
        s = census._ci(0, 0, "probe")
        assert "NO DENOMINATOR" in s, s
        assert "THE TWO TOOLS DISAGREE" not in s, s
        assert "nan" not in s, s

    def test_a_real_denominator_still_gets_an_interval(self, census):
        """POSITIVE CONTROL: the n == 0 early return must not shadow real work."""
        s = census._ci(7, 7, "probe")
        assert "Wilson [" in s and "statsmodels [" in s, s
        assert "THE TWO TOOLS DISAGREE" not in s, s
