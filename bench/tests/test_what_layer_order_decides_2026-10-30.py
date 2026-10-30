#!/usr/bin/env python3
"""Layer precedence is order-independent for the protected keys, and currently
decides nothing at all -- which corrects entry B21's own prose.

WHAT WENT WRONG IN THE PROSE. B21 put 3 questions to the free panel about adding
a ROLE layer to the 4-layer policy merge. Question 2 -- where the role layer
sits in the precedence -- was introduced with the claim that *"monotonicity
protects the HARD keys either way but the SOFT keys go to whichever layer merges
last"*. The first half is right. The second half asserts that such SOFT keys
EXIST, and measured by execution on 2026-10-30 there are **0** of them: across
60 (domain, model) pairs merged in both orders, not one leaf dotpath differs,
because the domain files write `constraints.*`, `convergence.*` and
`verification.*` while the model files write `model.*` and `protocol.*`. The
namespaces are disjoint, so precedence has nothing to decide.

Question 3 was introduced as a choice between 2 precedents, LOUD like the model
layer or SILENT like the task layer. There are 3: a missing model file RAISES
`FileNotFoundError`, a missing task file is skipped in SILENCE, and an unknown
domain WARNS and continues.

WHAT THIS FILE PINS, AND WHAT IT DELIBERATELY DOES NOT.

It does NOT pin "0 colliding pairs". The disjointness is a CONVENTION that
nothing in the merge engine enforces, so a future layer may legitimately write
into another's namespace, and a guard forbidding that would accuse correct code
-- the 9-of-36 failure class measured on 2026-10-28. It pins the RELATIONSHIP
instead: if no pair collides then no key is order-decided, and if any pair
collides then at least 1 key must be. That holds however the configuration
grows.

It DOES pin, unconditionally: that no HARD dotpath ever moves when the order is
reversed, which is the safety property a role layer would need; that the
detector is not blind, by a positive control over 2 synthetic colliding layers;
and that each layer's absence behaviour is what the panel question says it is.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PRODUCER = REPO / "scripts" / "what_does_layer_order_actually_decide_2026-10-30.py"

from bench.cdsfl_registry import registry as R  # noqa: E402


def _producer():
    assert PRODUCER.is_file(), f"producer absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("layer_order_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _producer()


@pytest.fixture(scope="module")
def order(mod):
    return mod.order_sensitivity()


class TestTheDetectorIsNotBlind:
    """A 0 from a blind instrument is indistinguishable from a real 0."""

    def test_two_colliding_layers_produce_a_reported_difference(self, mod):
        with tempfile.TemporaryDirectory() as td:
            a = pathlib.Path(td) / "a.toml"
            b = pathlib.Path(td) / "b.toml"
            a.write_text("[soft]\nbudget = 1\n")
            b.write_text("[soft]\nbudget = 2\n")
            fwd = mod._leaves(mod._merge_in_order([a, b]))
            rev = mod._leaves(mod._merge_in_order([b, a]))
            differing = sorted(k for k in set(fwd) | set(rev)
                               if fwd.get(k) != rev.get(k))
        assert differing == ["soft.budget"], (
            "the order detector did not see a deliberate collision, so every 0 "
            "it reports is uninformative")

    def test_it_reads_real_content_rather_than_empty_dicts(self, order):
        leaves = [p["leaves"] for p in order["pairs"]]
        assert leaves, "no pairs were merged at all"
        assert min(leaves) > 20, (
            f"the smallest merged policy has {min(leaves)} leaves; a near-empty "
            f"merge would make every comparison trivially equal")


class TestTheProtectedSetIsOrderIndependent:
    def test_no_hard_dotpath_moves_when_the_order_is_reversed(self, order):
        assert order["hard_order_differences"] == [], (
            f"{len(order['hard_order_differences'])} HARD key(s) differ under "
            f"order reversal: {order['hard_order_differences'][:5]}. That would "
            f"make question 2 a SAFETY question rather than a preference.")

    def test_the_protected_set_is_not_empty(self, mod):
        """An empty HARD set would make the test above vacuous."""
        hard = mod.hard_dotpaths()
        assert len(hard) >= 10, (
            f"only {len(hard)} HARD dotpath(s) are protected; the "
            f"order-independence result above would be near-vacuous")
        assert "convergence.hard_veto" in hard
        assert "constraints.falsification_required" in hard

    def test_monotonicity_is_checked_against_constants_not_the_prior_layer(self):
        """THE REASON order-independence holds, exercised rather than read.

        `_check_monotonicity` takes the merged policy and a layer NAME -- not the
        previous policy -- so it cannot compare one layer against another. A
        merged policy missing a HARD key must therefore fail whatever came
        before it.
        """
        with pytest.raises(R.PolicyViolationError):
            R._check_monotonicity({}, "a-layer-with-no-hard-keys")


class TestWhatOrderActuallyDecides:
    def test_collision_and_order_decision_agree(self, mod, order):
        """THE RELATIONSHIP, not the count -- so growth cannot falsely fail it."""
        disjoint = mod.namespace_disjointness()
        colliding = disjoint["colliding_pairs"]
        decided = order["order_decided_keys"]
        if colliding == 0:
            assert decided == {}, (
                f"no (domain, model) pair shares a leaf key, yet "
                f"{len(decided)} key(s) are reported as order-decided: "
                f"{sorted(decided)[:5]}. Those two measurements contradict "
                f"each other and one of them is wrong.")
        else:
            assert decided, (
                f"{colliding} pair(s) share a leaf key, yet 0 keys are "
                f"reported as order-decided. A collision that does not move a "
                f"value means the detector stopped working.")

    def test_the_disjointness_is_reported_with_its_denominator(self, mod):
        d = mod.namespace_disjointness()
        assert d["total_pairs"] > 0
        assert d["total_pairs"] == len(
            list((R.REGISTRY_DIR / "domains").glob("*.toml"))) * len(
            list((R.REGISTRY_DIR / "models").glob("*.toml")))


class TestTheAbsenceBehaviourQuestionThreeRestsOn:
    def test_a_missing_model_file_raises(self, mod):
        assert mod.absence_behaviour()["model_absent"].startswith("RAISE"), (
            "the model layer no longer fails loudly, so question 3's LOUD "
            "precedent has gone")

    def test_a_missing_task_file_is_silent(self, mod):
        assert mod.absence_behaviour()["task_absent"] == "SILENT"

    def test_an_unknown_domain_warns(self, mod):
        """THE THIRD PRECEDENT, which the panel question omitted."""
        assert mod.absence_behaviour()["domain_unknown"] == "WARN", (
            "the unknown-domain path no longer warns; question 3 was corrected "
            "to offer 3 precedents on the strength of this one")

    def test_the_three_precedents_are_distinct(self, mod):
        a = mod.absence_behaviour()
        kinds = {a["model_absent"].split(":")[0], a["task_absent"],
                 a["domain_unknown"]}
        assert len(kinds) == 3, (
            f"the 3 absence behaviours collapsed to {kinds}; question 3's "
            f"framing as a 3-way choice no longer matches the code")


def test_the_role_layer_still_does_not_exist():
    """The premise of the whole question. If a `roles/` directory appears, this
    entry has been acted on and the questions need re-reading, not re-asking."""
    assert not (R.REGISTRY_DIR / "roles").is_dir(), (
        "a roles/ directory now exists, so the role layer has been built; "
        "re-read entry B21 rather than treating its questions as open")
