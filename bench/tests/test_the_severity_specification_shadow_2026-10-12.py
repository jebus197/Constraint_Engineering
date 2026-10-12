"""The appendix's own severity formula, recorded beside the number the gate uses.

HIS RULING, 2026-10-12, VERBATIM: *"What was the original specification for the
severity gate? Severity was supposed to be calculated in accordance with our
existing maths model. If the models are asked to compute anything it should
surely be computed from our maths model and from what this already says about
severity surely, then they must provide a proof to demonstrate that they have
computed severity correctly, then the other machinery of the schema should apply
a working falsifier/use tools to check that this number makes sense and checks
out. This does not qualify as a 'vote'. Indeed it is the very opposite of a
vote."*

HE IS RIGHT ON ALL THREE COUNTS AND THE RECORD VINDICATES HIM.
docs/MATHEMATICAL_APPENDIX.md section 7.7 specifies

    Sev(f) = W(class) . confidence . V(verification)
    W(HARD)=1.0  W(SOFT)=0.5;  V(True)=1.0  V(None)=0.5  V(False)=0.0

and states as the section's KEY PROPERTY that "disproved findings always receive
zero severity, regardless of confidence". Two of those three factors belong to
the HARNESS, not the model, and a tool outcome can annihilate the model's
number. That is structurally the opposite of a vote.

IT WAS NEVER IMPLEMENTED, AND TWO OF ITS INPUTS WERE NEVER EVEN COLLECTED.
Across 3,298 archived entries `confidence` appears on 0 and no field carries a
HARD/SOFT class. `bench/reference_runner_v3.py:6682` reads the model's asserted
float directly. So the 2026-09-06 case for removing the severity test was sound
about the implementation and wrong about the specification: the remedy it
licensed was removal, and the remedy the specification licenses is to compute it.

WHAT IS BUILT HERE GATES NOTHING, DELIBERATELY. The verification factor is the
only one of the three available without a schema change, and the measured
movement is large: the share at or above the 0.7 cut falls from 41.6313%
(Wilson [39.9596%, 43.3225%]) to 16.3129% ([15.0912%, 17.6130%]), with 835 of
3,298 crossing downward -- 25.3184%, Wilson [23.8636%, 26.8306%]. A 25-point
reclassification is replay-invalidating, so promotion is the founder's and needs
non-distortion evidence from a RUN first. Producers:
scripts/the_verification_factor_shadow_2026-10-12.py,
scripts/severity_was_never_computed_from_the_model_2026-10-12.py.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

import bench.reference_runner_v3 as rr  # noqa: E402

_LIVE = (Path(__file__).resolve().parents[1] / "logs"
         / "study_run1b_2026-10-03_20261003T100439Z" / "runner_state.json")


def _reg(entries):
    r = rr.FindingRegistry()
    r.entries = entries
    return r


def _e(severity, verdict=""):
    return {"status": "UNCONFIRMED", "severity": severity,
            "falsifier_verdict": verdict}


def test_a_disproved_finding_is_counted_as_a_key_property_violation():
    """The appendix's own key property, as an executable check."""
    r = _reg({"C1": _e(0.9, "REFUTED")})
    s = r.severity_spec_shadow()
    assert s["key_property_violations"] == ["C1"], (
        "a disproved finding carrying non-zero severity was not reported; "
        "section 7.7 forbids it by construction")
    assert s["V_false"] == 1


def test_a_disproved_finding_at_zero_is_NOT_a_violation():
    """Anti-vacuity: the check must distinguish, not flag everything."""
    r = _reg({"C1": _e(0.0, "REFUTED")})
    assert r.severity_spec_shadow()["key_property_violations"] == []


def test_an_unverified_critical_crosses_the_cut_downward():
    """V(None)=0.5 halves it, which is the bulk of the measured movement."""
    r = _reg({"C1": _e(0.9, "")})
    s = r.severity_spec_shadow()
    assert s["V_none"] == 1
    assert s["critical_asserted"] == 1
    assert s["critical_spec"] == 0
    assert s["crossed_downward"] == ["C1"]


def test_a_verified_critical_does_NOT_move():
    """V(True)=1.0 leaves the number alone. The shadow is not a blanket cut."""
    r = _reg({"C1": _e(0.9, "CONFIRMED")})
    s = r.severity_spec_shadow()
    assert s["V_true"] == 1
    assert s["critical_asserted"] == 1 and s["critical_spec"] == 1
    assert s["crossed_downward"] == []


def test_it_gates_NOTHING():
    """The blocker count must be identical with and without the shadow.

    This is the property that makes the shadow safe to ship before his ruling
    on promotion, and it is asserted by EXECUTION rather than by the docstring
    saying so.
    """
    entries = {"C1": _e(0.9, ""), "C2": _e(0.8, "REFUTED")}
    r = _reg(dict(entries))
    before = r.unverified_critical_count()
    r.severity_spec_shadow()
    assert r.unverified_critical_count() == before, (
        "calling the shadow changed the blocker count, so it is not a shadow")
    assert r.entries == entries, "the shadow mutated the registry"


@pytest.mark.skipif(not _LIVE.exists(), reason="archived run not present")
def test_it_runs_on_the_live_registry_and_finds_the_violations():
    with open(_LIVE) as fh:
        r = rr.FindingRegistry.from_dict(json.load(fh)["registry"])
    s = r.severity_spec_shadow()
    assert s["V_true"] + s["V_none"] + s["V_false"] == 75, (
        f"expected all 75 entries classified, got {s}")
    assert len(s["key_property_violations"]) == 3, (
        f"study_run1b carries 3 disproved findings with non-zero severity; "
        f"got {s['key_property_violations']}")


def test_the_shadow_is_WIRED_into_the_round_telemetry():
    """An addition nothing reaches is not additive.

    Asserted by resolving the call through the delegation helper rather than
    grepping, so a renamed wrapper cannot hide the wiring.
    """
    import ast
    src = (Path(__file__).resolve().parents[1]
           / "reference_runner_v3.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    # `_delegation.callers_of` matches BARE-NAME calls only, and this is a
    # METHOD call on the registry, so using it here would report "no caller"
    # for wiring that exists -- which is what the first version of this test
    # did. Resolve attribute calls directly.
    callers = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for c in ast.walk(fn):
            if (isinstance(c, ast.Call)
                    and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "severity_spec_shadow"):
                callers.add(fn.name)
    assert callers, (
        "severity_spec_shadow is called by nothing, so no run will ever "
        "record it and the founder's promotion evidence never arrives")
    assert callers != {"severity_spec_shadow"}, "only calls itself"
