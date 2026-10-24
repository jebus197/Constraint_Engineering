# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_breaks_the_capability_tie_2026-10-20', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 084c20f0c8e78e5b998420bda15a746370bfd39c17fe33e0827c2b8c593949c3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Joint round what_breaks_the_capability_tie_2026-10-18 — the COMPOSED fix.

The two blind halves proved different halves of one defect:

* the fallback rung ORDER is outcome-inert under exhaustion (P(resolve) =
  1 - prod(1 - p_i), a product commutes; 24 permutations of 4 symbolic rungs
  collapse to 1 distinct SymPy expression, Wolfram Language agreeing), so
  rotating it costs no resolution;
* the fallback rung ORDER is evidence-determining (replayed over all 285
  archived dispatched passes: DeepSeek-SIM, Gemini-SIM and Fable-SIM held a
  combined 501 ladder appearances and 0 dispatches), so a fixed starting point
  makes the fallback unmeasurable while in force.

The composed fix: `exposure_rotated_order` rotates the un-established
fallback's STARTING POINT per experiment (cc2's half), and
`RoutingResult.rung_attempts` records one {"model", "verdict"} per rung
dispatched so the stratum the rotation generates carries its own denominator
(fable's half). `ladder_evidence_from_registry` pools the records per
capability identity into the exact shape `strength_order_from_evidence`
consumes. The composition's demonstrated advantage over either half alone is
exercised here: rotation alone leaves per-rung verdicts reconstructable only
by a replay the rotation itself invalidates (and a replay cannot tell an
ERROR rung from a failed attempt — 89 of 285 archived pass verdicts are
ERROR); the recorder alone records nothing for a seat that is never
dispatched (the archive's rung-1 stratum is 256/24/5/0/0/0 and the zeros
cannot grow).
"""
import json

import pytest

import bench.routing as RT
from bench.routing import (
    DEFAULT_FALSIFIER_STRENGTH,
    RoutingResult,
    exposure_rotated_order,
    is_unmeasured_fallback_order,
    ladder_evidence_from_registry,
    resolve_via_routing,
    route,
    season_strength_order,
)


# ────────────────────────── helpers ──────────────────────────

class _Reg:
    """A minimal registry: entries dict + resolve_model."""

    def __init__(self, entries=None, resolve=None):
        self.entries = entries or {}
        self._resolve = resolve or {}

    def resolve_model(self, label):
        return self._resolve.get(label, label)


def _registry_with_verdicts(spec):
    """spec: {seat: (refuted, total)} -> registry entries."""
    entries, i = {}, 0
    for seat, (ref, tot) in spec.items():
        for k in range(tot):
            entries[f"C{i:04d}"] = {
                "source_model": seat,
                "falsifier_verdict": "REFUTED" if k < ref else "CONFIRMED",
            }
            i += 1
    return _Reg(entries)


# ───────────────── rotation: cc2's half ─────────────────

def test_no_seed_is_byte_identical():
    assert exposure_rotated_order(DEFAULT_FALSIFIER_STRENGTH, None) == \
        tuple(DEFAULT_FALSIFIER_STRENGTH)
    assert exposure_rotated_order(DEFAULT_FALSIFIER_STRENGTH, "") == \
        tuple(DEFAULT_FALSIFIER_STRENGTH)


def test_rotation_preserves_the_set_and_the_cycle():
    base = tuple(DEFAULT_FALSIFIER_STRENGTH)
    rot = exposure_rotated_order(base, "exp_whatever")
    assert sorted(rot) == sorted(base)
    assert rot in {base[k:] + base[:k] for k in range(len(base))}


def test_rotation_is_deterministic_per_seed_and_covers_starts():
    base = tuple(DEFAULT_FALSIFIER_STRENGTH)
    a = exposure_rotated_order(base, "exp_a")
    assert a == exposure_rotated_order(base, "exp_a")
    # Over many seeds every member leads at least once (exposure, the point).
    firsts = {exposure_rotated_order(base, f"exp_{i}")[0] for i in range(64)}
    assert firsts == set(base)


def test_the_vendor_tuple_is_not_removed_narrowed_or_reordered():
    # ADDITIVE: the 2026-10-07 membership ruling is implemented AS this tuple.
    assert DEFAULT_FALSIFIER_STRENGTH == (
        "Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable")


def test_unestablished_fallback_rotates_and_says_so():
    reg = _registry_with_verdicts({"A": (0, 3), "B": (0, 3)})
    order, est, why = season_strength_order(reg, ["A", "B"], seed="exp_joint")
    assert est is False
    assert sorted(order) == sorted(DEFAULT_FALSIFIER_STRENGTH)
    if order != tuple(DEFAULT_FALSIFIER_STRENGTH):
        assert "ROTATED" in why or "rotation" in why.lower()
    # And the no-seed call is unchanged for every archived replay.
    order0, est0, why0 = season_strength_order(reg, ["A", "B"])
    assert order0 == tuple(DEFAULT_FALSIFIER_STRENGTH)
    assert "ROTATED" not in why0


def test_a_measured_order_is_never_rotated():
    # 4/4 vs 0/4 separates (Fisher p = 0.028571 single pair).
    reg = _registry_with_verdicts({"A": (4, 4), "B": (0, 4)})
    order, est, why = season_strength_order(reg, ["A", "B"], seed="exp_joint")
    assert est is True
    assert tuple(order) == ("A", "B")
    assert "ROTATED" not in why


def test_a_frozen_season_order_is_never_rotated():
    reg = _registry_with_verdicts({"A": (0, 2)})
    frozen = ("B", "A")
    order, est, why = season_strength_order(reg, ["A", "B"], frozen=frozen,
                                            seed="exp_joint")
    assert order == frozen and est is True
    assert "frozen" in why


def test_the_unestablished_stamp_survives_the_rotation():
    """THE COMPOSITION DEFECT NEITHER BLIND HALF CAUGHT: `route` stamped
    `strength_order_was_unestablished` by EQUALITY with the vendor tuple, so a
    rotated (still defaulted) fallback would have been recorded as measured —
    corrupting the 2026-10-17 field. The stamp now tests the rotation class."""
    base = tuple(DEFAULT_FALSIFIER_STRENGTH)
    rotated = exposure_rotated_order(base, "exp_joint")
    assert is_unmeasured_fallback_order(base) is True
    assert is_unmeasured_fallback_order(rotated) is True
    # A genuinely different (e.g. measured) order is NOT in the class.
    assert is_unmeasured_fallback_order(("CC2", "Codex")) is False

    finding = {"id": "F1", "source_model": None}
    out = route(finding, ["Codex-SIM"], [],
                resolve_fn=lambda m, f: "",
                reverify_fn=lambda c: "ERROR",
                similarity_fn=lambda a, b: 0.0,
                strength_order=rotated)
    assert out.strength_order_was_unestablished is True, (
        "a rotated fallback is still a DEFAULTED order and must be stamped so")


# ───────────────── recorder: fable's half ─────────────────

def test_rung_attempts_record_every_dispatched_rung():
    verdicts = {"M1": "REFUTED", "M2": "CONFIRMED"}
    out = resolve_via_routing(
        {"id": "F1"}, ["M1", "M2", "M3"],
        resolve_fn=lambda m, f: f"code-{m}",
        reverify_fn=lambda c: verdicts.get(c.split("-")[1], "ERROR"),
    )
    assert out.resolved is True and out.model_used == "M2"
    assert out.rung_attempts == [
        {"model": "M1", "verdict": "REFUTED"},
        {"model": "M2", "verdict": "CONFIRMED"},
    ]


def test_rung_attempts_record_error_rungs_and_the_self_rung():
    # M1 produces nothing (ERROR, the roster-gap shape); M2 fails; the
    # self-rung is then dispatched and recorded too.
    out = resolve_via_routing(
        {"id": "F1", "source_model": "SRC"}, ["M1", "M2"],
        resolve_fn=lambda m, f: "" if m == "M1" else f"code-{m}",
        reverify_fn=lambda c: "REFUTED",
        self_rung="SRC",
    )
    assert out.resolved is False
    assert out.rung_attempts == [
        {"model": "M1", "verdict": "ERROR"},
        {"model": "M2", "verdict": "REFUTED"},
        {"model": "SRC", "verdict": "REFUTED"},
    ]


def test_ladder_evidence_pools_per_identity_and_skips_error():
    entries = {
        "C0001": {"routing_history": [
            {"rung_attempts": [{"model": "A", "verdict": "CONFIRMED"},
                               {"model": "B", "verdict": "ERROR"}]},
            {"rung_attempts": [{"model": "A", "verdict": "REFUTED"}]},
        ]},
        "C0002": {"routing_history": [
            {"rung_attempts": [{"model": "A2", "verdict": "CONFIRMED"}]},
        ]},
    }
    # A and A2 are two seats of ONE model -> one identity; B's only attempt is
    # ERROR (no falsifier produced) and must not enter the denominator.
    reg = _Reg(entries, resolve={"A": "modelA@api", "A2": "modelA@api",
                                 "B": "modelB@api"})
    pooled = ladder_evidence_from_registry(reg)
    ids = RT.seat_identities(reg, ["A", "A2", "B"])
    assert pooled[ids["A"]] == (2, 3)          # pooled across both seats
    assert ids["A"] == ids["A2"]
    assert ids["B"] not in pooled              # ERROR-only -> no denominator


def test_ladder_evidence_is_empty_on_a_pre_field_archive():
    reg = _Reg({"C0001": {"routing_history": [
        {"round": 0, "verdict": "ERROR", "rungs_tried": 2,
         "model_used": "CC2-SIM"}]}})
    assert ladder_evidence_from_registry(reg) == {}


def test_the_evidence_shape_feeds_the_existing_estimator():
    # 4/4 vs 0/4 at perfect discrimination establishes from the pooled shape —
    # the 4-outcomes-per-seat distance measured in the blind round.
    ev = {"id_a": (4, 4), "id_b": (0, 4)}
    order, est, why = RT.strength_order_from_evidence(ev)
    assert est is True and order[0] == "id_a"


# ───────────── the composition, exercised together ─────────────

def test_rotated_ladder_passes_carry_their_own_denominator():
    """Both halves in one pass: a rotated rung order dispatches a seat the
    fixed order never reached, and the recorder keeps that seat's per-rung
    verdict — stratum and denominator together, which is the measured
    advantage of the composition over either half alone."""
    base = tuple(DEFAULT_FALSIFIER_STRENGTH)
    rotated = exposure_rotated_order(base, "exp_joint_2026-10-20")
    newly_first = rotated[0]
    roster = [f"{m}-SIM" for m in base]
    out = route({"id": "F1", "source_model": None}, roster, [],
                resolve_fn=lambda m, f: f"code::{m}",
                reverify_fn=lambda c: "CONFIRMED",
                similarity_fn=lambda a, b: 0.0,
                strength_order=rotated)
    assert out.resolved is True
    assert out.model_used == f"{newly_first}-SIM"
    assert out.rung_attempts == [
        {"model": f"{newly_first}-SIM", "verdict": "CONFIRMED"}]
    assert out.strength_order_was_unestablished is True


def test_the_runner_wires_both_halves():
    """Every addition is reached: the runner passes the experiment seed to the
    season call and persists rung_attempts at the single routing_history write
    site. Source-level, because executing the 22k-line runner end to end is a
    suite-scale job; the behaviour halves are executed above."""
    src = open("bench/reference_runner_v3.py", encoding="utf-8").read()
    assert 'seed=getattr(cfg, "experiment_name", "") or None' in src
    assert '"rung_attempts": list(getattr(result, "rung_attempts", []) or [])' \
        in src


def test_routing_result_defaults_keep_archived_replays_intact():
    r = RoutingResult("F1", "ERROR", False, None, "")
    assert r.rung_attempts == []
    # And the JSON shape the runner persists is serialisable.
    json.dumps({"rung_attempts": r.rung_attempts})


# ───────────── B13: the layer-4 miss, loud and non-fatal ─────────────

def test_unregistered_model_gets_the_strictest_layer_four_choice():
    import warnings
    from bench.cdsfl_registry.registry import load_effective_policy, _deep_merge
    from bench.routing import lookup_misses, reset_lookup_misses

    reset_lookup_misses()
    base = load_effective_policy("mathematics")
    assert _deep_merge(base, {}) == base       # the empty-overlay lemma
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pol = load_effective_policy("mathematics", model="kimi_k2")
    assert pol == base                          # exactly the layers-1..3 policy
    assert any("CAPABILITY LOOKUP MISS" in str(w.message) for w in caught)
    assert any(m["key"] == "kimi_k2" for m in lookup_misses())
    # Announced once per identity; recorded every time.
    with warnings.catch_warnings(record=True) as again:
        warnings.simplefilter("always")
        load_effective_policy("mathematics", model="kimi_k2")
    assert not any("CAPABILITY LOOKUP MISS" in str(w.message) for w in again)
    assert sum(m["key"] == "kimi_k2" for m in lookup_misses()) == 2


def test_the_admitted_policy_is_the_strictest_layer_four_choice():
    """Fails loudly the day a models/*.toml tightens a HARD key — at which
    point omitting layer 4 stops being the strictest choice and the non-fatal
    admission must be re-justified (the named refuter of the B13 fix)."""
    import glob
    import tomllib
    from bench.cdsfl_registry.registry import (
        HARD_CONSTRAINTS, HARD_THRESHOLDS, HARD_STRINGS)

    hard = set(HARD_CONSTRAINTS) | set(HARD_THRESHOLDS) | set(HARD_STRINGS)

    def _flat(d, pre=""):
        for k, v in d.items():
            kk = f"{pre}.{k}" if pre else k
            if isinstance(v, dict):
                yield from _flat(v, kk)
            else:
                yield kk

    for f in glob.glob("bench/cdsfl_registry/models/*.toml"):
        with open(f, "rb") as fh:
            touched = [k for k in _flat(tomllib.load(fh)) if k in hard]
        assert not touched, (
            f"{f} touches HARD key(s) {touched}: the empty overlay is no "
            f"longer provably the strictest layer-4 choice; re-open B13")


def test_a_hard_violation_still_raises():
    """The one thing the old raise actually protected is UNCHANGED: a layer
    that weakens a HARD constraint is refused, loudly and fatally."""
    from bench.cdsfl_registry.registry import (
        PolicyViolationError, _check_monotonicity, load_effective_policy)

    hostile = load_effective_policy("mathematics")
    hostile = json.loads(json.dumps(hostile))   # deep copy
    hostile["constraints"]["anti_deference"] = False
    with pytest.raises(PolicyViolationError):
        _check_monotonicity(hostile, "model/_panel_hostile_probe")
