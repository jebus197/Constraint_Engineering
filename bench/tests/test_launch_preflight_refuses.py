"""A9 — refuse a doomed launch before the first paid dispatch.

The alternative to this check has been exercised: Exp 53 discovered its
configuration was doomed at round 3 of 16, with the money spent.

WHAT IT DOES *NOT* CHECK, AND WHY
---------------------------------
Everything the harness can correct by itself, it corrects by itself, and a
preflight that re-litigated those would be noise that gets switched off:

  * a declared target_kind disagreeing with the file  -> resolve_target_kind raises
  * sk_enabled on a non-Python target                 -> forced off, loudly, at run start
  * Python-source tools aimed at prose                -> bypassed by the specialist
                                                         router, reported NOT_APPLICABLE

What is left is the class the harness cannot correct at runtime: a missing
input, or a missing absorber. Three checks. That is the whole of it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import (  # noqa: E402
    TARGET_KIND_PROSE,
    TARGET_KIND_PYTHON,
    LaunchRefused,
    preflight_target_machinery,
    resolve_target_kind,
)


@dataclass
class Cfg:
    routing_enabled: bool = True
    falsifier_gate_enabled: bool = True


@pytest.fixture
def prose(tmp_path):
    f = tmp_path / "SW-21-REF-04.md"
    f.write_text("# A design reference\n\nA claim about a rate limiter.\n",
                 encoding="utf-8")
    return str(f)


class TestAMissingTargetIsRefused:
    """Five of the six prose targets named in the Exp 50/51/52 configs did not
    exist on disk on 2026-08-01. A launch would dispatch a panel at nothing."""

    def test_a_target_that_does_not_exist(self, tmp_path):
        r = preflight_target_machinery(
            Cfg(), str(tmp_path / "BX-14-REF-04.md"), TARGET_KIND_PROSE)
        assert len(r) == 1 and "does not exist" in r[0]

    def test_an_empty_target(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("   \n\n", encoding="utf-8")
        r = preflight_target_machinery(Cfg(), str(f), TARGET_KIND_PROSE)
        assert len(r) == 1 and "empty" in r[0]

    def test_a_directory_is_not_a_target(self, tmp_path):
        r = preflight_target_machinery(Cfg(), str(tmp_path), TARGET_KIND_PROSE)
        assert r, "a directory is not a file and must not pass"


class TestAProseRunWithoutAnAbsorberIsRefused:
    """Routing is the only thing between the falsifier gate and the human queue.
    Measured on Exp 53 with it enabled but blind: 50% of findings escalated."""

    def test_routing_off_on_prose(self, prose):
        r = preflight_target_machinery(
            Cfg(routing_enabled=False), prose, TARGET_KIND_PROSE)
        assert len(r) == 1
        assert "only absorber" in r[0]
        assert "take_up_slack_enabled" in r[0], (
            "name the legacy alias — seven of the eight live configs set it "
            "under that name, and a refusal that names only the new key sends "
            "a reader hunting for a flag they already have")

    def test_the_falsifier_gate_off_on_prose_leaves_no_route_to_terminal(self, prose):
        r = preflight_target_machinery(
            Cfg(falsifier_gate_enabled=False), prose, TARGET_KIND_PROSE)
        assert len(r) == 1
        assert "ONLY route to a terminal state" in r[0]

    def test_both_missing_are_both_reported(self, prose):
        r = preflight_target_machinery(
            Cfg(routing_enabled=False, falsifier_gate_enabled=False),
            prose, TARGET_KIND_PROSE)
        assert len(r) == 2, (
            "report every refusal at once — a preflight that surfaces one "
            "problem per launch costs one launch per problem")


class TestACodeRunIsUnaffected:
    def test_routing_off_on_a_python_target_is_not_refused(self):
        # On a code target S_k and fix-verification are live routes to closure,
        # so routing is a booster rather than the only absorber. This check must
        # not spread beyond the case that justifies it.
        r = preflight_target_machinery(
            Cfg(routing_enabled=False, falsifier_gate_enabled=False),
            str(Path(__file__).resolve().parents[1] / "reference_runner_v3.py"),
            TARGET_KIND_PYTHON)
        assert r == []

    def test_a_healthy_prose_run_passes(self, prose):
        assert preflight_target_machinery(Cfg(), prose, TARGET_KIND_PROSE) == []


class TestTheRefusalIsWiredAndFatal:
    def test_it_raises_rather_than_warns(self):
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        assert "raise LaunchRefused(" in src, (
            "a warning is a thing a tired person scrolls past at 2am; the "
            "point of A9 is that the run does not start")

    def test_it_runs_before_any_dispatch(self):
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        i_check = src.index("_refusals = preflight_target_machinery(")
        i_kind = src.index("target_kind, target_kind_reason = resolve_target_kind(")
        assert i_kind < i_check, "the check needs the resolved kind"
        # and it must precede the round loop entirely
        i_loop = src.index("for round_idx in range(", i_check)
        assert i_check < i_loop, "refuse before the first round, not during it"

    def test_every_refusal_is_logged_not_just_raised(self):
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        assert 'LAUNCH REFUSED: {_r}' in src

    def test_the_exception_names_the_target_and_the_kind(self):
        e = LaunchRefused("2 precondition(s) failed for target /x/y.md (kind=prose): a | b")
        assert "prose" in str(e) and "/x/y.md" in str(e)


class TestTheLiveConfigsWouldPass:
    """The eight queued configs were reported as failing 3/3 preflight checks.
    That figure predates A1/A2/A6; re-measure rather than repeat it."""

    def test_the_queued_configs_only_fail_on_missing_targets(self):
        import glob
        import json
        repo = Path(__file__).resolve().parents[2]
        failures = {}
        for f in sorted(glob.glob(str(repo / "bench/exp5*_configs/*.json"))):
            d = json.loads(Path(f).read_text())
            cfg = Cfg(
                routing_enabled=bool(
                    d.get("routing_enabled", d.get("take_up_slack_enabled", False))),
                falsifier_gate_enabled=bool(d.get("falsifier_gate_enabled", False)),
            )
            target = d.get("test_article") or d.get("target") or ""
            # RESOLVE THE KIND; DO NOT ASSUME IT. Until 2026-09-05 this line
            # passed TARGET_KIND_PROSE for every configuration it found. The A9
            # absorber refusal is GATED ON PROSE, so a config with a .py target
            # and routing_enabled off was reported as failing a refusal it could
            # never actually receive at launch.
            #
            # That is not a harmless over-strictness. It fired against the 3
            # Exp 56 arms, whose design switches routing OFF DELIBERATELY: with
            # a single seat in Arm A the routing ladder is built from the
            # orchestrator's full 5-seat roster and would pull in exactly the 4
            # vendors that arm exists to do without. Acting on this test's
            # refusal by enabling routing would have silently destroyed the
            # experiment it was meant to protect.
            #
            # Executing the real gate with the resolved kind returns 0 refusals
            # for all 3 arms.
            kind, _reason = resolve_target_kind(target)
            r = preflight_target_machinery(cfg, target, kind)
            machinery = [x for x in r if "does not exist" not in x
                         and "not readable" not in x and "empty" not in x]
            if machinery:
                failures[Path(f).name] = machinery
        assert not failures, (
            "every queued config has routing and the falsifier gate on (seven "
            f"via the legacy alias). Machinery refusals found: {failures}")
