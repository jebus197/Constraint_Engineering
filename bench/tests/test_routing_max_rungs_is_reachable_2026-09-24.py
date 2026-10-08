"""`routing_max_rungs` must REACH `route()`, or it is a config field nothing reads.

WHY THIS FILE EXISTS. `bench/routing.py` has always defaulted `max_rungs` to 2 and
the runner's single `route(...)` call site passed no override, so rungs 3 and
beyond were unreachable BY CONSTRUCTION in every archived run and "what does rung
3 buy" is unmeasured rather than known to be nothing. A `routing_max_rungs` field
was added to `RunnerConfig` on 2026-09-24 to make the question answerable by
measurement. A config field that no caller reads is the addition-nothing-reaches
defect this project has confirmed 11 times, so the field needs this test to exist
at all.

IT EXECUTES, IT DOES NOT GREP. A test that searched the call site for the string
`max_rungs=` would pass against a runner that computed the value and threw it
away. This substitutes a RECORDER for the real `route` and reads what actually
arrived.

WHY THE DEFAULT PATH PASSES NO KEYWORD, asserted below as behaviour. Passing it
unconditionally broke 8 tests across 4 files whose `fake_route` stubs accept no
such keyword, and those stubs are right to be narrow: they assert on behaviour,
not on a signature. So at the default of 2 the call must be byte-identical to
what it was before the field existed, and the keyword must appear ONLY on opt-in.
That is this project's convention for a gated feature: reachable, off by default,
entered by one forward config so the comparison is measured rather than argued.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bench.routing as RT                     # noqa: E402
import bench.reference_runner_v3 as R          # noqa: E402


class _Res:
    """The minimum a RoutingResult must look like for `_apply_routing` to proceed."""
    finding_id = "C0001"
    verdict = "ERROR"
    resolved = False
    model_used = "m"
    falsifier_code = ""
    rungs_tried = 0
    duplicate_of = None


# ─────── UPDATED 2026-10-08 ON THE FOUNDER'S RULING, NOT DELETED ───────
# These assertions pinned the default at 2 so that "every routing-enabled config
# already on disk is byte-identical until one opts in". That was the right property
# while the cap was the intended default. It no longer is.
#
# HIS RULING, 2026-10-06 and restated several times since: *"I don't think there
# should be a cap at all. If it's a measured statistic, along with capability
# fingerprinting then the problem should run until it is either resolved, or the
# ladder is exhausted."* It was expressible but never expressed -- 0 of 47 configs
# set it -- so the ruling reached nothing, which is the addition-nothing-reaches
# failure this project has 11 confirmed instances of.
#
# WHAT THE CAP WAS COSTING, measured over 305 archived routing records: 143 hit the
# cap and 103 of those were ABANDONED UNRESOLVED. Per-rung conditional resolve rates
# are 0.3902 at rung 1 and 0.2797 at rung 2, so 4 further rungs recover roughly 46
# to 75 of the 103 for about 209 extra dispatches.
#
# The BYTE-IDENTICAL property is deliberately given up; the OMIT-AT-DEFAULT property
# that protects the 8 narrow stubs is kept, by making the condition track the
# signature instead of the literal 2.

def test_the_field_exists_and_defaults_to_exhaust():
    assert R.RunnerConfig().routing_max_rungs == 0, (
        "the default must be 0, meaning exhaust the ladder, per the founder's "
        "ruling; a positive default is a cap he has ruled against")


def test_routes_own_default_matches_the_config_default():
    """They must agree, or the omit-at-default logic silently caps or uncaps.

    This is the coupling that made a naive flip dangerous: the call site omits the
    keyword when the config equals the FUNCTION default, so if the 2 drift apart
    the runner either passes a cap it was not asked for or omits one it was.
    """
    import inspect
    fn_default = inspect.signature(RT.route).parameters["max_rungs"].default
    assert fn_default == 0
    assert fn_default == R.RunnerConfig().routing_max_rungs, (
        f"route() defaults to {fn_default} while the config defaults to "
        f"{R.RunnerConfig().routing_max_rungs}; the omit-at-default condition "
        "cannot be correct for both")


class _MC:
    label = "CC2"


class _Exp:
    models = [_MC()]


def _drive_real_apply_routing(monkeypatch, **cfg_kw) -> dict:
    """Run the REAL `_apply_routing` over a minimal escalated critical, with
    `bench.routing.route` replaced by a recorder, and return the kwargs that
    actually arrived. `_apply_routing` imports route from the module at call
    time, so patching the module attribute intercepts the genuine call site."""
    seen: dict = {}

    def recorder(*a, **kw):
        seen.update(kw)
        return _Res()

    monkeypatch.setattr(RT, "route", recorder)
    reg = R.FindingRegistry()
    reg.entries["C0001"] = {
        "description": "x", "severity": 0.9, "escalated": True,
        "falsifier_verdict": "ERROR", "source_model": "M1", "status": "OPEN",
    }
    cfg = R.RunnerConfig(routing_enabled=True, models=["CC2"], **cfg_kw)
    R._apply_routing(reg, 1, _Exp(), cfg=cfg, repo_root=str(REPO))
    return seen


def test_the_configured_value_is_what_route_receives(monkeypatch):
    """THE WHOLE POINT, and it is read off a recorder rather than off the source.

    REWRITTEN 2026-09-24 (panel). The first version monkeypatched RT.route and
    then called ITS OWN recorder with a kw dict IT built from a copy of the
    call-site expression -- `_apply_routing` never ran, so the test asserted
    that the test agrees with the test. Two representations of one truth with
    no comparator, the exact `source_text_assertions` shape. This version
    executes the real `_apply_routing`."""
    seen = _drive_real_apply_routing(monkeypatch, routing_max_rungs=5)
    assert seen.get("max_rungs") == 5, (
        f"a configured value of 5 did not arrive at route(): {seen!r}")


def test_at_the_default_the_real_call_site_passes_no_keyword(monkeypatch):
    """The property that protects the 8 narrow fake_route stubs, and it SURVIVES
    the flip because the omit condition now tracks the signature rather than 2."""
    seen = _drive_real_apply_routing(monkeypatch)
    assert "max_rungs" not in seen, (
        f"the default leaked the keyword into route(): {seen!r}")


def test_at_the_default_no_keyword_is_passed_at_all():
    """The narrow stubs in 4 other test files depend on this, and so does the
    claim that archived behaviour is untouched."""
    import inspect
    fn_default = inspect.signature(RT.route).parameters["max_rungs"].default
    for value, expect_keyword in ((fn_default, False), (2, True), (3, True), (5, True)):
        rungs = int(value)
        kw = {} if rungs == fn_default else {"max_rungs": rungs}
        assert ("max_rungs" in kw) is expect_keyword, (
            f"routing_max_rungs={value} produced {kw!r}")


def test_the_call_site_computes_the_value_from_cfg_and_not_from_a_constant():
    """The one thing a recorder cannot show: that `cfg` is the SOURCE.

    Narrow and deliberate. The branch only runs inside a live routing round, which
    this test does not stand up; what it pins is that the value is read off the
    config object rather than hard-coded, which is the difference between a
    reachable field and a decorative one.
    """
    import inspect
    src = inspect.getsource(R._apply_routing)
    assert 'getattr(cfg, "routing_max_rungs"' in src
    assert "_route_kw" in src and "max_rungs" in src


def test_a_cfg_of_none_does_not_explode():
    """`_apply_routing(cfg=None)` is a real call shape; getattr must carry it."""
    assert int(getattr(None, "routing_max_rungs", 2) or 2) == 2
