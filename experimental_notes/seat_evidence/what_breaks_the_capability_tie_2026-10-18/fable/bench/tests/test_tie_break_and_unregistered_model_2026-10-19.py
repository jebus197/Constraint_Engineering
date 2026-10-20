# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'what_breaks_the_capability_tie_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5057829258cf46d5c13384abe915b734bd3a85a11a8f968ed1a61d8ede20f28e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Panel C (2026-10-19): the routing tie and the unregistered model.

Executes the two fixes delivered against C21/C15/B13:

1. B13 -- `load_effective_policy` with an UNREGISTERED model is LOUD AND
   NON-FATAL: it returns a policy byte-identical to the model=None result
   (which passed `_check_monotonicity` at every merge), records the miss in
   `bench.routing.lookup_misses()` against the model's stable
   `capability_identity`, and announces once. Monotonicity refusal of a
   weakened HARD constraint is unchanged -- that refusal is the property that
   makes arbitrary model admission safe at all.

2. C21 -- `resolve_via_routing` now records per-rung attempt outcomes
   (`RoutingResult.rung_attempts`), giving routed-resolution capability the
   denominator the archive lacks, and `ladder_evidence_from_registry` pools
   them per capability identity in the same shape the season machinery
   consumes. Recording only; no routing decision reads it.
"""
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.routing import (  # noqa: E402
    capability_identity, ladder_evidence_from_registry, lookup_misses,
    reset_lookup_misses, route,
)
from bench.cdsfl_registry.registry import (  # noqa: E402
    HARD_CONSTRAINTS, HARD_STRINGS, HARD_THRESHOLDS, PolicyViolationError,
    REGISTRY_DIR, _MISSING, _dotpath_get, load_effective_policy,
)


def test_unregistered_model_is_loud_and_non_fatal_2026_10_19():
    reset_lookup_misses()
    base = load_effective_policy("mathematics", model=None)
    got = load_effective_policy("mathematics", model="kimi_k2")
    # Non-fatal, and provably nothing weakened: byte-identical to layers 1..3.
    assert got == base
    for dotpath, required in HARD_CONSTRAINTS.items():
        assert _dotpath_get(got, dotpath) == required, dotpath
    for dotpath, floor in HARD_THRESHOLDS.items():
        val = _dotpath_get(got, dotpath)
        assert val is not _MISSING and val >= floor, dotpath
    for dotpath, required in HARD_STRINGS.items():
        assert _dotpath_get(got, dotpath) == required, dotpath
    # Loud: recorded against the stable identity, not a vendor name.
    misses = [m for m in lookup_misses()
              if m["key"] == "kimi_k2" and "layer 4" in m["what"]]
    assert misses, "the miss was not recorded"
    assert misses[0]["identity"] == capability_identity("", "kimi_k2")


def test_registered_model_records_no_miss_2026_10_19():
    reset_lookup_misses()
    load_effective_policy("mathematics", model="opus_4_6")
    assert not [m for m in lookup_misses() if "layer 4" in m["what"]]


def test_monotonicity_refusal_is_unchanged_2026_10_19():
    """Non-fatal admission must NOT leak into HARD enforcement."""
    tasks = REGISTRY_DIR / "tasks"
    tasks.mkdir(exist_ok=True)
    demo = tasks / "panel-c-weakening-demo.toml"
    demo.write_text("[constraints]\nfalsification_required = false\n")
    try:
        try:
            load_effective_policy("mathematics", task_id="panel-c-weakening-demo")
            raise AssertionError("a weakened universal HARD constraint was accepted")
        except PolicyViolationError:
            pass
    finally:
        demo.unlink()


def test_rung_attempts_are_recorded_in_dispatch_order_2026_10_19():
    def resolve_fn(model, finding):
        return "" if model == "A" else f"# falsifier by {model}"

    def reverify_fn(code):
        return "CONFIRMED" if "B" in code else "REFUTED"

    res = route(
        {"finding_id": "F1", "source_model": "S"},
        ["A", "B"], [], resolve_fn, reverify_fn,
        similarity_fn=lambda a, b: 0.0,
        strength_order=("A", "B"),
    )
    assert res.verdict == "CONFIRMED"
    assert res.rung_attempts == [
        {"model": "A", "verdict": "ERROR"},
        {"model": "B", "verdict": "CONFIRMED"},
    ]


def test_self_rung_attempt_is_recorded_2026_10_19():
    res = route(
        {"finding_id": "F2", "source_model": "S"},
        ["A"], [], lambda m, f: f"# by {m}", lambda c: "REFUTED",
        similarity_fn=lambda a, b: 0.0,
        strength_order=("A",),
    )
    assert res.resolved is False
    assert res.rung_attempts == [
        {"model": "A", "verdict": "REFUTED"},
        {"model": "S", "verdict": "REFUTED"},
    ]


def test_ladder_evidence_pools_per_identity_2026_10_19():
    class Shim:
        entries = {
            "c1": {"routing_history": [{"rung_attempts": [
                {"model": "Codex", "verdict": "CONFIRMED"},
                {"model": "Codex-SIM", "verdict": "REFUTED"},
                {"model": "Gemini", "verdict": "ERROR"},
            ]}]},
            # a pre-2026-10-19 record: no rung_attempts, contributes nothing
            "c2": {"routing_history": [{"rungs_tried": 1, "resolved": True}]},
        }
    pooled = ladder_evidence_from_registry(Shim())
    # Codex and Codex-SIM share one identity (the -SIM suffix is normalised off)
    assert pooled[capability_identity("", "Codex")] == (1, 2)
    assert pooled[capability_identity("", "Gemini")] == (0, 1)
    assert len(pooled) == 2


def test_archive_without_the_field_yields_nothing_2026_10_19():
    class Shim:
        entries = {"c": {"routing_history": [{"rungs_tried": 2}]}}
    assert ladder_evidence_from_registry(Shim()) == {}
