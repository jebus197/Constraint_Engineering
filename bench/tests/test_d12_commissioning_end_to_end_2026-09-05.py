"""D12: commission severity calibration and stall-based termination, END TO END.

FOUNDER RULING, 2026-09-05, verbatim: "Commissioning the 2 settings that are
switched off by design and reachable by no configuration: severity calibration
and stall based termination.  # Verdict: Do it."

A CORRECTION TO THE PREMISE, MEASURED BEFORE BUILDING THIS
----------------------------------------------------------
"reachable by no configuration" is no longer true, and the record says when it
stopped being true. An executing probe on 2026-09-05 drove a config dict through
the real launcher path (`build_runner_config_from_dict`) with every bool flipped
off its default: of 72 probed RunnerConfig fields, 71 arrived intact. The only
field that did not was `resume`, which is deliberately read from `args` rather
than the config and is not a defect. Both settings under this ruling were
HONOURED. The launcher-config-drop that once dropped them was fixed for the
gamma/stall trio on 2026-07-29 and for severity calibration on 2026-07-31
(`bench/launcher_core.py:236-256` and `:315-325` carry both incident notes).

SO WHAT WAS ACTUALLY OUTSTANDING. Not reachability. Measured the same day:
  * 0 shipped configs under bench/exp*_configs/ set severity_calibration_enabled
  * 0 shipped configs set stall_gamma_termination_enabled
  * severity calibration's PRODUCER, latent_tagger_enabled, is also default-off
  * 17 unit tests exist and pass, but none drives the LAUNCHER path
"Commissioned" in this project means there is evidence the mechanism works when
switched on, not merely that a flag exists. That evidence is what this file adds.

WHY IT GOES THROUGH THE LAUNCHER RATHER THAN CONSTRUCTING RunnerConfig DIRECTLY.
Per `execute-do-not-grep`: a test that builds RunnerConfig by hand asserts that
the runner honours a field, which was never in doubt. The defect class this
project keeps finding is a PRODUCER AND A CONSUMER THAT DISAGREE — a config key
the launcher silently drops before the runner ever sees it. Only a test that
starts from a config dict and ends at observed behaviour can see that, which is
exactly why five such drops shipped undetected.

Every test below compares ON against OFF. A test that only exercises the ON path
would pass against a mechanism wired to fire unconditionally.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench.launcher_core import build_runner_config_from_dict  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    _apply_severity_calibration,
    _check_stall_convergence,
)

TARGET = "bench/cdsfl_registry/targets/control_two_distinct_defects.md"


class _Args:
    """Stand-in for the argparse namespace; every attribute defaults to None."""

    def __getattr__(self, _name):
        return None


def _cfg(**overrides):
    """Build a RunnerConfig THROUGH THE LAUNCHER, as a real launch does."""
    base = {
        "experiment_name": "d12_commissioning_probe",
        "models": ["cc2"],
        "test_article": TARGET,
        "context_files": [],
        "domain": "software",
    }
    base.update(overrides)
    return build_runner_config_from_dict(base, _Args())


class _Registry:
    def __init__(self, entries):
        self.entries = entries


def _over_rated_critical():
    """A finding that IS demotion-eligible: critical, CONFIRMED real, latent.

    The conjunction is the safeguard in `_is_demotion_eligible`: proven-real by
    an independent falsifier AND explicitly conditional. Anything less is never
    demoted, which is the point of the mechanism.
    """
    return {
        "severity": 0.90,
        "falsifier_verdict": "CONFIRMED",
        "latent": True,
        "finding_category": "performance",
        "status": "OPEN",
    }


# ── Severity calibration ────────────────────────────────────────────────────


class TestSeverityCalibrationIsReachableFromAConfig:

    def test_the_flag_survives_the_launcher_path(self):
        assert _cfg(severity_calibration_enabled=True).severity_calibration_enabled is True
        assert _cfg().severity_calibration_enabled is False, (
            "the default changed — D12 commissioning assumed default-off"
        )

    def test_the_floor_survives_the_launcher_path(self):
        assert _cfg(severity_calibration_floor=0.55).severity_calibration_floor == 0.55

    def test_its_producer_the_latent_tagger_also_survives(self):
        """severity calibration demotes only entries flagged `latent`, and the
        latent tagger is what sets that flag. A consumer commissioned without its
        producer is inert — the exact reason the 2026-07-31 fix passed both keys
        through together."""
        assert _cfg(latent_tagger_enabled=True).latent_tagger_enabled is True


class TestSeverityCalibrationChangesBehaviourWhenOn:

    def test_enabled_demotes_an_eligible_over_rated_critical(self):
        reg = _Registry({"F-1": _over_rated_critical()})
        n = _apply_severity_calibration(reg, _cfg(severity_calibration_enabled=True), 3)
        assert n == 1
        assert reg.entries["F-1"]["severity"] < CRITICAL_SEVERITY_THRESHOLD
        assert reg.entries["F-1"]["severity_original"] == 0.90

    def test_disabled_is_a_byte_identical_no_op(self):
        """The OFF half. Without this the ON test cannot distinguish a working
        gate from one that fires unconditionally."""
        entry = _over_rated_critical()
        reg = _Registry({"F-1": entry})
        before = dict(entry)
        n = _apply_severity_calibration(reg, _cfg(), 3)
        assert n == 0
        assert reg.entries["F-1"] == before, "the default-off path mutated state"

    def test_the_finding_is_RETAINED_not_deleted(self):
        """Demotion must not lose the finding. Losing a real defect to make a
        gate converge would be the worst possible failure of this mechanism."""
        reg = _Registry({"F-1": _over_rated_critical()})
        _apply_severity_calibration(reg, _cfg(severity_calibration_enabled=True), 3)
        assert "F-1" in reg.entries
        assert reg.entries["F-1"]["severity_original"] == 0.90

    @pytest.mark.parametrize("category", ["safety", "security", "data_loss"])
    def test_never_demote_categories_survive_even_when_enabled(self, category):
        e = _over_rated_critical()
        e["finding_category"] = category
        reg = _Registry({"F-1": e})
        n = _apply_severity_calibration(reg, _cfg(severity_calibration_enabled=True), 3)
        assert n == 0, f"a {category} critical was demoted"
        assert reg.entries["F-1"]["severity"] == 0.90

    def test_an_unconfirmed_finding_is_never_demoted(self):
        """No falsifier CONFIRMED means the defect was never independently
        demonstrated real, so a broken falsifier could be masking it."""
        e = _over_rated_critical()
        e["falsifier_verdict"] = "UNVERIFIED"
        reg = _Registry({"F-1": e})
        assert _apply_severity_calibration(
            reg, _cfg(severity_calibration_enabled=True), 3) == 0

    def test_a_non_latent_finding_is_never_demoted(self):
        e = _over_rated_critical()
        e["latent"] = False
        reg = _Registry({"F-1": e})
        assert _apply_severity_calibration(
            reg, _cfg(severity_calibration_enabled=True), 3) == 0


# ── Stall-based termination ─────────────────────────────────────────────────


class _StallRegistry:
    """Minimal stand-in: _check_stall_convergence reads exactly these 2 counts."""

    def __init__(self, open_ch=2, contested=1):
        self._open_ch = open_ch
        self._contested = contested

    def open_crit_high_count(self):
        return self._open_ch

    def contested_count(self, round_idx, subcritical_exclusion=False):
        return self._contested


def _static_history(window, open_ch=2, contested=1):
    """window-1 entries: the function APPENDS the current round before testing."""
    return [{"open_ch": open_ch, "contested": contested} for _ in range(window - 1)]


def _stall_cfg(**over):
    base = dict(stall_gamma_terminate=0.45, stall_gamma_advisory=0.30,
                stall_window=3, stall_earliest_round=2)
    base.update(over)
    return _cfg(**base)


class TestStallTerminationIsReachableFromAConfig:

    def test_the_flag_survives_the_launcher_path(self):
        assert _cfg(stall_gamma_termination_enabled=True).stall_gamma_termination_enabled is True
        assert _cfg().stall_gamma_termination_enabled is False

    def test_its_thresholds_survive_the_launcher_path(self):
        c = _stall_cfg()
        assert (c.stall_gamma_terminate, c.stall_gamma_advisory, c.stall_window) == (0.45, 0.30, 3)


class TestStallTerminationChangesBehaviourWhenOn:
    """The load-bearing pair: identical inputs, opposite outcomes on the flag.

    GAMMA IS LOAD-BEARING is a standing directive, and this mechanism is one of
    the ways gamma closes a run. Terminating on a stall that is not real would end
    a run early and understate residual risk, so the OFF half matters as much as
    the ON half.
    """

    def _call(self, cfg, gamma=0.60, reg=None):
        return _check_stall_convergence(
            round_idx=8,
            registry=reg or _StallRegistry(),
            gamma=gamma,
            stall_history=_static_history(cfg.stall_window),
            cfg=cfg,
            consecutive_churn_rounds=0,
        )

    def test_enabled_terminates_on_a_static_window_with_high_gamma(self):
        r = self._call(_stall_cfg(stall_gamma_termination_enabled=True))
        assert r["stalled"] is True
        assert r["terminate"] is True
        assert r["tier"] == "terminate"
        assert "STALL_CONVERGED" in r["reason"]

    def test_disabled_detects_the_same_stall_but_does_NOT_terminate(self):
        r = self._call(_stall_cfg())
        assert r["stalled"] is True, "the stall itself should still be detected"
        assert not r.get("terminate"), "termination fired with the gate OFF"
        assert r["tier"] != "terminate"

    def test_the_two_outcomes_are_genuinely_different(self):
        """States the discrimination as one assertion, so a regression making both
        branches agree fails here legibly instead of quietly making the pair above
        vacuous."""
        on = self._call(_stall_cfg(stall_gamma_termination_enabled=True))
        off = self._call(_stall_cfg())
        assert bool(on.get("terminate")) != bool(off.get("terminate")), (
            "enabling stall_gamma_termination_enabled changed nothing — the flag "
            "is not wired to the behaviour it names"
        )

    def test_low_gamma_does_not_terminate_even_when_enabled(self):
        """Gamma is the second condition, not decoration."""
        r = self._call(_stall_cfg(stall_gamma_termination_enabled=True), gamma=0.10)
        assert not r.get("terminate")

    def test_a_moving_window_does_not_terminate_even_when_enabled(self):
        cfg = _stall_cfg(stall_gamma_termination_enabled=True)
        moving = [{"open_ch": 2, "contested": 1}, {"open_ch": 5, "contested": 1}]
        r = _check_stall_convergence(
            round_idx=8, registry=_StallRegistry(open_ch=3, contested=2),
            gamma=0.60, stall_history=moving, cfg=cfg, consecutive_churn_rounds=0)
        assert not r.get("terminate")

    def test_the_earliest_round_guard_still_holds_when_enabled(self):
        cfg = _stall_cfg(stall_gamma_termination_enabled=True, stall_earliest_round=20)
        r = _check_stall_convergence(
            round_idx=3, registry=_StallRegistry(), gamma=0.60,
            stall_history=_static_history(cfg.stall_window), cfg=cfg,
            consecutive_churn_rounds=0)
        assert not r.get("terminate")


class TestTheCommissioningGapThatRemains:
    """Names, in executable form, what commissioning does NOT establish.

    Both mechanisms are now reachable and demonstrated. Neither has ever run in a
    completed experiment, because no shipped config enables them. That is a
    deliberate scientific decision — switching either on changes the conditions
    under which a run converges — and it belongs to the founder, not to this file.
    """

    def test_no_shipped_config_enables_either_setting(self):
        import json
        enabled = []
        for cfg_path in sorted(REPO_ROOT.glob("bench/exp*_configs/*.json")):
            try:
                data = json.loads(cfg_path.read_text())
            except Exception:
                continue
            for key in ("severity_calibration_enabled", "stall_gamma_termination_enabled"):
                if data.get(key):
                    enabled.append(f"{cfg_path.name}:{key}")
        assert enabled == [], (
            "a shipped config now enables one of these. That is a change to "
            "experimental conditions and needs to be recorded deliberately, with "
            "the comparability of earlier runs restated: " + ", ".join(enabled)
        )
