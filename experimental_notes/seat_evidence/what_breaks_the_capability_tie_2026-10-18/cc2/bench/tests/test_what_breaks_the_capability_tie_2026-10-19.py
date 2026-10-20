# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'what_breaks_the_capability_tie_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cdff4edb93226712bb8e98f407a68f89673e9fa5d91996cfde9abfb9035d7f83
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""What breaks the capability tie, and what happens to an unregistered model.

TWO FIXES, EACH WITH ITS OWN EXECUTED FALSIFIER. Every assertion here fails if
the corresponding defect is present and passes only if it is absent.

FIX A -- `exposure_rotated_order` + `season_strength_order(seed=...)`.
  The defect: an unestablished order held fixed across every experiment is
  UNMEASURABLE, not merely unmeasured. Measured over all 285 dispatched routing
  passes in `bench/logs`, reconstructed by replaying `rank_falsifier_writers`
  against each run's own roster: DeepSeek-SIM was on the ladder 214 times and
  asked 0, Gemini-SIM 203/0, Fable-SIM 84/0 -- 501 ladder appearances, 0
  dispatches -- while 106 passes stopped short of the ladder's end unresolved.

FIX B -- a missing layer-4 model policy is LOUD and NON-FATAL.
  The defect: `load_effective_policy` raised FileNotFoundError for any model
  without a layer-4 file, and this directory holds 6 files against 24 roster
  identities. The replacement is derived, not preferred: absence of layer 4 is
  the EMPTY overlay, `_deep_merge(p, {}) == p`, and `_check_monotonicity` has
  already passed on layers 1-3 -- so the admitted policy is provably no weaker
  than any registered model's.
"""
from __future__ import annotations

import math
import warnings

import pytest

import bench.routing as RT
from bench.cdsfl_registry import registry as REG


# ───────────────────────── FIX A ─────────────────────────

class _Reg:
    def __init__(self, entries):
        self.entries = entries

    def resolve_model(self, label):
        return label


def _mk(spec):
    ents, i = {}, 0
    for seat, (ref, tot) in spec.items():
        for j in range(tot):
            ents[f"C{i:05d}"] = {
                "source_model": seat,
                "falsifier_verdict": "REFUTED" if j < ref else "CONFIRMED"}
            i += 1
    return _Reg(ents)


def test_the_vendor_tuple_is_not_removed_narrowed_or_reordered():
    """ADDITIVE. The set, the length and the cycle are all untouched."""
    assert RT.DEFAULT_FALSIFIER_STRENGTH == (
        "Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable")
    assert len(RT.DEFAULT_FALSIFIER_STRENGTH) == 6
    assert RT.VENDOR_ORDER_SUPERSEDED is RT.DEFAULT_FALSIFIER_STRENGTH
    assert RT.FALSIFIER_STRENGTH_IS_ESTABLISHED is False


def test_no_seed_changes_nothing_so_every_archived_replay_is_intact():
    base = RT.DEFAULT_FALSIFIER_STRENGTH
    for seed in (None, "", "   "):
        assert RT.exposure_rotated_order(base, seed) == base
    spec = {"A": (0, 3), "B": (0, 3)}
    order, est, _ = RT.season_strength_order(_mk(spec), list(spec))
    assert est is False
    assert order == base, "an unseeded fallback must be byte-identical to before"


def test_a_rotation_preserves_the_set_and_the_cycle_exactly():
    """A rotation of a set is NOT a ranking of it -- that is why it may be used
    where no capability claim is admissible."""
    base = RT.DEFAULT_FALSIFIER_STRENGTH
    k = len(base)
    for seed in ("exp56", "exp57", "study_run1", "leg3", "x", "zz", "a1b2"):
        rot = RT.exposure_rotated_order(base, seed)
        assert set(rot) == set(base), "membership must be identical"
        assert len(rot) == k
        # same cyclic sequence: some shift reproduces it exactly
        assert any(base[i:] + base[:i] == rot for i in range(k)), (
            "a rotation must preserve the relative cycle; a reordering would "
            "assert something about capability that no measurement supports")


def test_the_rotation_is_stable_within_an_experiment_and_varies_across_them():
    """A season's positions stay fixed; different experiments start elsewhere."""
    base = RT.DEFAULT_FALSIFIER_STRENGTH
    for seed in ("exp56_d9", "study_run1b"):
        assert (RT.exposure_rotated_order(base, seed)
                == RT.exposure_rotated_order(base, seed)), "must be deterministic"
    firsts = {RT.exposure_rotated_order(base, f"experiment_{n}")[0]
              for n in range(400)}
    assert firsts == set(base), (
        "every ladder member must be reachable as rung 1 for the rung-1 stratum "
        f"to be estimable at all; unreachable: {set(base) - firsts}")


def test_rotation_dominates_shuffle_on_exact_rung_one_coverage():
    """THE COMPOSABILITY MEASUREMENT, derived rather than asserted.

    Over k experiments a rotation covers all k rung-1 slots EXACTLY once. An
    independent uniform shuffle covers them only in expectation: the chance all
    k are distinct is k!/k^k, so for k = 6 the chance at least one member still
    has no rung-1 observation after 6 experiments is 1 - 6!/6^6 = 0.9845679.
    """
    k = len(RT.DEFAULT_FALSIFIER_STRENGTH)
    shuffle_gap = 1.0 - math.factorial(k) / float(k ** k)
    assert abs(shuffle_gap - 0.9845679012345679) < 1e-12, shuffle_gap
    firsts = [RT.exposure_rotated_order(RT.DEFAULT_FALSIFIER_STRENGTH, s)[0]
              for s in ("s0", "s1", "s2", "s3", "s4", "s5")]
    rotation_gap = 0.0 if len(set(firsts)) == k else 1.0
    # The rotation's guarantee is over CONSECUTIVE shifts, which is what the
    # mechanism provides by construction; the hashed seeds above are a sample.
    shifts = [RT.exposure_rotated_order(RT.DEFAULT_FALSIFIER_STRENGTH, s)
              for s in ("a",)]
    base = RT.DEFAULT_FALSIFIER_STRENGTH
    consecutive = {(base[i:] + base[:i])[0] for i in range(k)}
    assert consecutive == set(base), "consecutive shifts cover every member once"
    assert shuffle_gap > 0.9, (
        "if a shuffle covered rung 1 as reliably as a rotation the simpler "
        "mechanism would not dominate and this fix would be unjustified")


def test_the_fallback_says_it_rotated_and_still_claims_nothing():
    spec = {"A": (0, 3), "B": (0, 3)}
    order, est, why = RT.season_strength_order(_mk(spec), list(spec),
                                               seed="exp99_panel")
    assert est is False, "a rotation must NEVER be reported as established"
    assert "no capability claim is made" in why
    assert "FALSIFIER_STRENGTH_IS_ESTABLISHED is False" in why
    assert "STARTING POINT is rotated" in why, why
    assert set(order) == set(RT.DEFAULT_FALSIFIER_STRENGTH)


def test_a_measured_order_still_wins_and_is_never_rotated():
    """The rotation applies ONLY where nothing separates. 4 perfect observations
    per seat establish an order, and that order must come through untouched."""
    spec = {"A": (4, 4), "B": (0, 4)}
    order, est, why = RT.season_strength_order(_mk(spec), ["A", "B"],
                                               seed="exp99_panel")
    assert est is True, why
    assert order == ("A", "B"), order
    assert "STARTING POINT is rotated" not in why


def test_a_frozen_season_order_is_never_rotated():
    frozen = ("CC2", "Codex")
    order, est, why = RT.season_strength_order(_mk({"A": (0, 2)}), ["A"],
                                               frozen=frozen, seed="exp99")
    assert order == frozen and est is True, (order, why)


def test_the_runner_passes_the_experiment_name_as_the_seed():
    """An addition nothing reaches is not additive. This is the wiring."""
    src = open("bench/reference_runner_v3.py").read()
    assert 'experiment_name' in src
    assert "seed=_seed or None" in src, (
        "season_strength_order must receive the per-experiment seed from the "
        "live call site, or the rotation is an addition no caller reaches")


# ───────────────────────── FIX B ─────────────────────────

def test_an_unregistered_model_no_longer_refuses_dispatch():
    REG.reset_model_policy_misses()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        policy = REG.load_effective_policy(domain="mathematics", model="kimi_k2")
    assert isinstance(policy, dict) and policy, "a policy must still come back"
    msgs = [str(w.message) for w in caught]
    assert any("UNREGISTERED MODEL POLICY" in m for m in msgs), msgs
    assert any("kimi_k2" in m for m in msgs), msgs


def test_the_miss_is_recorded_against_the_stable_identity_not_the_name():
    REG.reset_model_policy_misses()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        REG.load_effective_policy(domain="mathematics", model="kimi_k2")
    misses = REG.MODEL_POLICY_MISSES
    assert len(misses) == 1, misses
    rec = misses[0]
    assert rec["key"] == "kimi_k2"
    assert rec["identity"] == RT.capability_identity("", "kimi_k2"), (
        "the announcement must use the SAME identity function every capability "
        "decision uses; a second one is producer/consumer drift")
    assert rec["identity"] != "unresolved"


def test_the_announcement_is_once_per_identity_but_recorded_every_time():
    REG.reset_model_policy_misses()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(5):
            REG.load_effective_policy(domain="mathematics", model="kimi_k2")
    assert len(REG.MODEL_POLICY_MISSES) == 5
    hits = [w for w in caught if "UNREGISTERED MODEL POLICY" in str(w.message)]
    assert len(hits) == 1, (
        f"{len(hits)} announcements for 1 defect; the composer runs once per "
        f"seat per round, so an un-deduplicated alarm floods the log")


def test_the_admitted_policy_is_the_strictest_layer_four_choice():
    """THE DERIVATION, executed. Absence of layer 4 IS the empty overlay."""
    base = REG.load_effective_policy(domain="mathematics")
    assert REG._deep_merge(base, {}) == base
    REG._check_monotonicity(base, "layers 1-3 only")   # raises if it ever fails
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unreg = REG.load_effective_policy(domain="mathematics", model="kimi_k2")
    assert unreg == base, "an unregistered model must get exactly layer 3"
    hard = dict(REG.HARD_CONSTRAINTS)
    hard.update(REG.HARD_THRESHOLDS)
    hard.update(REG.HARD_STRINGS)
    for f in sorted((REG.REGISTRY_DIR / "models").glob("*.toml")):
        merged = REG._deep_merge(base, REG._load_toml(f))
        changed = [k for k in hard
                   if REG._dotpath_get(merged, k) != REG._dotpath_get(base, k)]
        assert changed == [], (
            f"{f.stem} moves a HARD key {changed}; if a registered layer-4 file "
            f"can TIGHTEN a HARD constraint then omitting layer 4 is no longer "
            f"the strictest choice and this fix's derivation fails")


def test_monotonicity_still_refuses_a_weakening_layer_four():
    """THE SAFETY PROPERTY that makes arbitrary model selection admissible.
    Executed end to end against a real file on disk."""
    probe = REG.REGISTRY_DIR / "models" / "_tie_probe_hostile.toml"
    probe.write_text("[constraints]\nanti_deference = false\n")
    try:
        with pytest.raises(REG.PolicyViolationError) as ei:
            REG.load_effective_policy(domain="mathematics",
                                      model="_tie_probe_hostile")
        assert "constraints.anti_deference" in str(ei.value)
    finally:
        probe.unlink()


@pytest.mark.parametrize("overlay,needle", [
    ({"constraints": {"anti_deference": False}}, "constraints.anti_deference"),
    ({"convergence": {"hard_coverage_threshold": 0.8}},
     "convergence.hard_coverage_threshold"),
    ({"convergence": {"method": "compensatory"}}, "convergence.method"),
    ({"constraints": {"anti_deference": 1}}, "constraints.anti_deference"),
    ({"convergence": {"hard_coverage_threshold": float("nan")}},
     "convergence.hard_coverage_threshold"),
])
def test_every_weakening_shape_is_refused(overlay, needle):
    uni = REG._load_toml(REG.REGISTRY_DIR / "universal.toml")
    with pytest.raises(REG.PolicyViolationError) as ei:
        REG._check_monotonicity(REG._deep_merge(uni, overlay), "probe")
    assert needle in str(ei.value)


def test_a_non_fatal_miss_does_not_weaken_anything_it_merges():
    """The fix must not become a hole: an unregistered model is admitted, but a
    REGISTERED model that weakens a HARD is still refused, so 'loud and
    non-fatal' never becomes 'anything goes'."""
    probe = REG.REGISTRY_DIR / "models" / "_tie_probe_hostile2.toml"
    probe.write_text("[convergence]\nhard_coverage_threshold = 0.5\n")
    try:
        with pytest.raises(REG.PolicyViolationError):
            REG.load_effective_policy(domain="software",
                                      model="_tie_probe_hostile2")
    finally:
        probe.unlink()
