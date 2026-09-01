"""A simulated run's severity-derived numbers are not results.

STANDING RULING, panel-converged 2026-09-01. Both reviewers reached it
independently and for the same measured reasons:

  * The boundary sits on a spike. 401 of 6,865 archived findings (5.84%) sit
    EXACTLY on 0.70 and 72.1% are quantised to a 0.05 step, so severity is
    ordinal. A ~0.12 mean rating shift converts MECHANICALLY into a ~7.8x
    critical-count ratio — which is precisely how a modest calibration gap was
    misdiagnosed as a fidelity crisis on 2026-09-01.
  * Calibration buys DELTAS, never LEVELS: applying the measured +0.156
    correction moves the simulated cluster 0.46 -> 0.62, still under 0.70.

The demotion is therefore PERMANENT, not "until calibrated". What a simulated
run remains valid for is unchanged and substantial: machinery validation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402


def _cfg(*labels):
    cfg = type("Cfg", (), {})()
    cfg.models = [type("M", (), {"label": l})() for l in labels]
    return cfg


class TestTheDetectorUsesTheMandatedMarker:

    def test_a_sim_panel_is_detected(self):
        assert R.run_is_simulated(_cfg("CC2-SIM", "Fable-SIM")) is True

    def test_a_real_panel_is_not(self):
        assert R.run_is_simulated(_cfg("CC2", "Gemini", "Codex")) is False

    def test_one_sim_seat_is_enough(self):
        """There is no mixed panel; one -SIM seat means the run is a rehearsal."""
        assert R.run_is_simulated(_cfg("CC2", "Gemini", "Fable-SIM")) is True

    def test_plain_string_labels_work_too(self):
        assert R.run_is_simulated(_cfg("CC2-SIM")) is True

    def test_a_vendor_merely_CONTAINING_sim_is_not_a_match(self):
        """The marker is a SUFFIX. 'Simulacrum' is not a simulated seat."""
        assert R.run_is_simulated(_cfg("Simulacrum", "SIMBA")) is False

    def test_an_empty_or_absent_roster_is_treated_as_real(self):
        """Fail toward ADMISSIBLE only when there is no evidence of simulation;
        a bare config must not silently demote a real run's findings."""
        assert R.run_is_simulated(_cfg()) is False
        assert R.run_is_simulated(type("C", (), {})()) is False


class TestTheNoticeSaysWhatMayBeClaimed:

    def test_a_sim_run_is_marked_inadmissible(self):
        n = R.severity_demotion_notice(_cfg("CC2-SIM"))
        assert n["severity_provenance"] == "simulated"
        assert n["severity_magnitudes_calibrated"] is False
        assert "uncalibrated" in n["caveat_when_simulated"].lower()

    def test_a_real_run_is_marked_calibrated(self):
        n = R.severity_demotion_notice(_cfg("CC2", "Gemini"))
        assert n["severity_provenance"] == "real"
        assert n["severity_magnitudes_calibrated"] is True

    def test_readiness_reporting_is_explicitly_permitted(self):
        """FOUNDER RULING 2026-09-01, and the point of the whole exercise.

        The notice previously listed "convergence verdicts as evidence" among
        things barred for a simulated run. That clause blocked a straight answer
        to the only question the simulation exists to answer -- is this runner
        fit to take into a real experiment -- and it had no standing: it arrived
        as a two-model panel convergence, the runway itself recorded it as
        "needs a standing ruling", and it was then written into a commit message
        AS a standing ruling without ever reaching HIL.

        The founder: "remove that clause that prevents you from reporting when
        that is the case. It seems to serve no purpose other than to confuse you
        and me."
        """
        n = R.severity_demotion_notice(_cfg("CC2-SIM"))
        assert "PERMITTED" in n["readiness_reporting"]
        joined = json.dumps(n).lower()
        assert "convergence verdicts as evidence" not in joined, (
            "the withdrawn clause is back; a simulated run must be citable as "
            "evidence of whether the runner is ready")

    def test_the_caveat_that_survives_is_about_magnitudes_not_conclusions(self):
        """What was always true stays: sim severity numbers do not transfer."""
        n = R.severity_demotion_notice(_cfg("CC2-SIM"))
        c = n["caveat_when_simulated"].lower()
        assert "magnitudes" in c and "do not transfer" in c
        assert "machinery" in c, (
            "the caveat must say what is NOT caveated, or it reads as 'the "
            "rehearsal is worthless'")

    def test_it_cites_a_basis_that_is_actually_a_ruling(self):
        n = R.severity_demotion_notice(_cfg("CC2-SIM"))
        b = n["basis"].lower()
        assert "founder ruling" in b, (
            "the basis must name the HIL ruling. A panel convergence is a model "
            "vote, and this project does not confirm findings by model vote.")
        assert "never ratified" in b, (
            "the record should say plainly that the superseded item never had "
            "the standing it was given")


class TestTheGuardIsWiredIntoTheReport:

    def test_the_runner_stamps_it(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert 'result["severity_admissibility"]' in src, (
            "the demotion must reach the REPORT; a ruling nobody can read from "
            "the artefact is a ruling that will be forgotten")

    def test_it_does_not_alter_the_gate(self):
        """The demotion is a statement about admissibility, not a behaviour
        change. A simulated run still converges on its own evidence."""
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        gate = src[src.index("def _check_gamma_alt_convergence"):][:6000] \
            if "def _check_gamma_alt_convergence" in src else ""
        assert "run_is_simulated" not in gate, (
            "the gate must not branch on provenance; that would make simulated "
            "and real runs behave differently and destroy comparability")
