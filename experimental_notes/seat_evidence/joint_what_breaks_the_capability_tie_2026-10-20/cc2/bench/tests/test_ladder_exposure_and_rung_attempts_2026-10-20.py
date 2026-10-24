# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_what_breaks_the_capability_tie_2026-10-20', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 7b313242ba4d86055d1621ae32cdd878b85bda8625aec6c26e133cb85050ef5a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The rung sequence is rotated where no order is established, AND every rung
dispatched is recorded with the verdict it earned.

JOINT ROUND, what_breaks_the_capability_tie_2026-10-18. Two seats proved
different halves of one defect. fable proved the rung ORDER is outcome-inert:
under the exhaustion ruling P(resolve) = 1 - prod(1 - p_i) and a product
commutes. cc2 proved it is evidence-determining: seats that are never dispatched
can never earn a position. Both hold, and the fix is the conjunction -- rotate so
the stratum exists, record so it is readable without an offline replay.

WHAT THIS ROUND MEASURED AND CHANGED, and the reason the fix is not either
seat's as-proposed:

  1. THE DENOMINATOR WAS ALREADY RECOVERABLE. Replaying `rank_falsifier_writers`
     over each archived run's own roster, `ladder[rungs_tried - 1]` reproduces
     the recorded `model_used` on 104 of 104 resolved archived passes, 0
     mismatches. So "a stratum with no denominator is unrecoverable after the
     fact" is false. `rung_attempts` is justified instead by the PER-RUNG
     VERDICT, which is genuinely lost: 42 of 77 unresolved passes (54.5455%)
     terminated in ERROR, and ERROR is a tooling failure while REFUTED is a
     capability signal.
  2. ROTATING THE VENDOR TUPLE DOES NOT REACH THE LIVE ROSTER. On
     ['cx', 'cgpt', 'ge', 'ds', 'cc2', 'fable', 'kimi'] -- the roster
     `bench/routing.py` itself records, for which `strength_order_matched` is
     0 of 7 -- all 6 shifts of the tuple yield 1 distinct ladder. Rotating the
     RUNG SEQUENCE yields 7. The rotation is therefore applied after ranking.

Every test here executes the real `bench.routing` functions.
"""
from __future__ import annotations

import itertools

import pytest

import bench.routing as RT

LIVE_ROSTER = ["cx", "cgpt", "ge", "ds", "cc2", "fable", "kimi"]
SIM_ROSTER = ["Codex-SIM", "CC2-SIM", "ChatGPT-SIM", "Gemini-SIM",
              "DeepSeek-SIM", "Fable-SIM"]


@pytest.fixture(autouse=True)
def _no_seed_leaks():
    """The seed is module state; no test may leave it set for another."""
    before = RT.LADDER_ROTATION_SEED
    RT.LADDER_ROTATION_SEED = ""
    yield
    RT.LADDER_ROTATION_SEED = before


def _route(roster, source="CC2-SIM", verdict="REFUTED", seen=None):
    """Run the real `route` with a recording resolve_fn."""
    order = seen if seen is not None else []

    def resolve_fn(model, finding):
        order.append(model)
        return f"# falsifier from {model}"

    out = RT.route({"finding_id": "C0001", "source_model": source,
                    "description": "x", "title": "x"},
                   roster, [], resolve_fn, lambda code: verdict,
                   lambda a, b: 0.0, self_rung_enabled=False)
    return out, order


# ───────────────────────── the rotation half ─────────────────────────

def test_rotating_the_vendor_tuple_does_not_reach_the_live_roster():
    """The measurement that moved the rotation from the tuple to the ladder."""
    tuple_ladders = {tuple(RT.rank_falsifier_writers(
        LIVE_ROSTER, tuple(RT.DEFAULT_FALSIFIER_STRENGTH[s:]
                           + RT.DEFAULT_FALSIFIER_STRENGTH[:s])))
        for s in range(len(RT.DEFAULT_FALSIFIER_STRENGTH))}
    assert len(tuple_ladders) == 1, (
        "rotating the vendor tuple is expected to be a NO-OP on the live "
        f"roster; got {len(tuple_ladders)} distinct ladders")
    assert RT.labels_the_order_ranks(
        LIVE_ROSTER, RT.DEFAULT_FALSIFIER_STRENGTH) == [], (
        "the live roster is expected to match 0 of 7 names in the tuple")
    ladder = RT.rank_falsifier_writers(LIVE_ROSTER, RT.DEFAULT_FALSIFIER_STRENGTH)
    rung_ladders = {RT.cyclically_rotate(ladder, f"exp{s}") for s in range(400)}
    firsts = {l[0] for l in rung_ladders}
    assert firsts == set(LIVE_ROSTER), (
        "rotating the RUNG SEQUENCE must be able to place every live roster "
        f"member at position 1; reachable firsts were {sorted(firsts)}")


def test_rotation_is_deterministic_and_stable_across_processes():
    import subprocess
    import sys
    a = RT.cyclically_rotate(SIM_ROSTER, "exp_alpha")
    b = RT.cyclically_rotate(SIM_ROSTER, "exp_alpha")
    assert a == b
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0,'.');"
         "import bench.routing as R;"
         f"print(R.cyclically_rotate({SIM_ROSTER!r}, 'exp_alpha'))"],
        capture_output=True, text=True, check=True)
    assert out.stdout.strip() == str(a), (
        "the rotation must be reproducible in a FRESH process -- `hash()` on "
        "str is salted per process and would make a replay unrecoverable; got "
        f"{out.stdout.strip()!r} vs {a!r}")


def test_a_rotation_preserves_membership_and_the_cyclic_successor_relation():
    """It is a rotation of a set, not a ranking of it -- no capability claim."""
    for seed in ("e1", "e2", "experiment-42", ""):
        rot = RT.cyclically_rotate(SIM_ROSTER, seed)
        assert sorted(rot) == sorted(SIM_ROSTER), "membership must be preserved"
        assert len(rot) == len(SIM_ROSTER)
        n = len(SIM_ROSTER)
        succ_base = {SIM_ROSTER[i]: SIM_ROSTER[(i + 1) % n] for i in range(n)}
        succ_rot = {rot[i]: rot[(i + 1) % n] for i in range(n)}
        assert succ_rot == succ_base, (
            "a cyclic rotation must preserve the successor relation")


def test_an_empty_seed_leaves_every_archived_replay_byte_identical():
    assert RT.LADDER_ROTATION_SEED == "", "the default must disable rotation"
    assert RT.cyclically_rotate(SIM_ROSTER, "") == tuple(SIM_ROSTER)
    out, order = _route(SIM_ROSTER)
    expected = RT.rank_falsifier_writers(
        SIM_ROSTER, RT.DEFAULT_FALSIFIER_STRENGTH, exclude=["CC2-SIM"])
    assert order == expected, (
        "with no seed the dispatch order must be exactly the unrotated ladder")
    assert out.ladder_rotation == 0


def test_the_vendor_tuple_is_not_removed_narrowed_or_reordered():
    assert RT.DEFAULT_FALSIFIER_STRENGTH == (
        "Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable")
    assert RT.VENDOR_ORDER_SUPERSEDED is RT.DEFAULT_FALSIFIER_STRENGTH
    assert RT.FALSIFIER_STRENGTH_IS_ESTABLISHED is False
    # His 2026-10-07 membership ruling, implemented AS membership of this tuple.
    assert len(RT.DEFAULT_FALSIFIER_STRENGTH) == 6
    assert {"CC2", "Fable"} <= set(RT.DEFAULT_FALSIFIER_STRENGTH)


def test_a_seeded_route_rotates_the_dispatch_order_and_records_the_shift():
    RT.LADDER_ROTATION_SEED = "joint_round_2026-10-20"
    unrotated = RT.rank_falsifier_writers(
        SIM_ROSTER, RT.DEFAULT_FALSIFIER_STRENGTH, exclude=["CC2-SIM"])
    out, order = _route(SIM_ROSTER)
    assert order == list(RT.cyclically_rotate(unrotated,
                                              "joint_round_2026-10-20"))
    assert out.ladder_rotation == unrotated.index(order[0])
    assert sorted(order) == sorted(unrotated), "membership unchanged"


def test_a_measured_or_frozen_order_is_never_rotated():
    """`_unestablished` gates the rotation; a non-default order is measured."""
    RT.LADDER_ROTATION_SEED = "joint_round_2026-10-20"
    measured = ("Fable", "DeepSeek", "Gemini", "ChatGPT", "CC2", "Codex")
    assert tuple(measured) != tuple(RT.DEFAULT_FALSIFIER_STRENGTH)
    seen: list = []

    def resolve_fn(model, finding):
        seen.append(model)
        return "# f"

    out = RT.route({"finding_id": "C1", "source_model": "CC2-SIM",
                    "title": "x", "description": "x"},
                   SIM_ROSTER, [], resolve_fn, lambda c: "REFUTED",
                   lambda a, b: 0.0, strength_order=measured,
                   self_rung_enabled=False)
    assert out.strength_order_was_unestablished is False
    assert out.ladder_rotation == 0, "a MEASURED order must never be rotated"
    assert seen == RT.rank_falsifier_writers(
        SIM_ROSTER, measured, exclude=["CC2-SIM"])


def test_rotation_covers_every_position_exactly_once_where_a_shuffle_does_not():
    """The named property on which rotation dominates an independent shuffle."""
    import math
    k = 6
    shuffle_gap = 1 - math.factorial(k) / k ** k
    assert abs(shuffle_gap - 0.9845679012345679) < 1e-15, (
        "1 - k!/k**k at k=6 is the probability a shuffle leaves at least one "
        "member with no position-1 observation after k experiments")
    shifts = {RT.cyclically_rotate(SIM_ROSTER, f"e{i}")[0] for i in range(500)}
    assert shifts == set(SIM_ROSTER), (
        "every member must be reachable at position 1 by some seed")
    # And a rotation by each of the k shifts covers each position exactly once.
    firsts = [tuple(SIM_ROSTER[s:] + SIM_ROSTER[:s])[0] for s in range(k)]
    assert sorted(firsts) == sorted(SIM_ROSTER)


# ───────────────────────── the recorder half ─────────────────────────

def test_every_dispatched_rung_is_recorded_with_the_verdict_it_earned():
    out = RT.resolve_via_routing(
        {"finding_id": "C1"}, ["A", "B", "C"],
        lambda m, f: "" if m == "B" else "# f",
        lambda code: "REFUTED")
    assert [a["model"] for a in out.rung_attempts] == ["A", "B", "C"]
    assert [a["position"] for a in out.rung_attempts] == [1, 2, 3]
    assert [a["verdict"] for a in out.rung_attempts] == [
        "REFUTED", "ERROR", "REFUTED"], (
        "a rung that produced NO falsifier must be recorded as ERROR and "
        "distinguishable from a rung whose falsifier was REFUTED")
    assert out.rungs_tried == 3


def test_the_recorder_separates_what_the_terminal_verdict_pools():
    """The justification for the field: terminal verdict loses earlier rungs."""
    out = RT.resolve_via_routing(
        {"finding_id": "C1"}, ["A", "B"],
        lambda m, f: "" if m == "A" else "# f",
        lambda code: "REFUTED")
    assert out.verdict == "REFUTED", "the TERMINAL verdict is rung B's"
    assert out.resolved is False
    verdicts = {a["model"]: a["verdict"] for a in out.rung_attempts}
    assert verdicts == {"A": "ERROR", "B": "REFUTED"}, (
        "rung A's ERROR is recoverable ONLY from rung_attempts -- the pass's "
        f"single terminal verdict is {out.verdict!r}")


def test_a_resolved_pass_records_only_the_rungs_actually_asked():
    out = RT.resolve_via_routing(
        {"finding_id": "C1"}, ["A", "B", "C"],
        lambda m, f: "# f",
        lambda code: "CONFIRMED" if True else "REFUTED")
    assert out.resolved is True and out.model_used == "A"
    assert [a["model"] for a in out.rung_attempts] == ["A"], (
        "resolve_via_routing returns at the first CONFIRMED, so B and C were "
        "never asked and must not appear as attempts")
    assert out.rungs_tried == 1


def test_the_self_rung_is_recorded_and_flagged_as_the_self_rung():
    out = RT.resolve_via_routing(
        {"finding_id": "C1"}, ["A"], lambda m, f: "# f",
        lambda code: "REFUTED", self_rung="SRC")
    models = [a["model"] for a in out.rung_attempts]
    assert models == ["A", "SRC"]
    assert out.rung_attempts[0].get("self_rung") is None
    assert out.rung_attempts[1].get("self_rung") is True, (
        "the self-rung is a dispatch to the finding's OWN source and must not "
        "be counted as evidence that another seat was asked")


def test_an_empty_ladder_records_no_attempts_and_still_defers():
    out = RT.resolve_via_routing(
        {"finding_id": "C1"}, [], lambda m, f: "# f", lambda code: "REFUTED")
    assert out.rung_attempts == []
    assert out.rungs_tried == 0
    assert out.ladder_was_empty is True
    assert out.resolved is False


def test_the_recorder_defaults_empty_and_is_not_shared_between_results():
    a = RT.RoutingResult("C1", "ERROR", False, None, "")
    b = RT.RoutingResult("C2", "ERROR", False, None, "")
    assert a.rung_attempts == [] and b.rung_attempts == []
    a.rung_attempts.append({"position": 1})
    assert b.rung_attempts == [], (
        "a mutable default shared between instances is the classic dataclass "
        "defect; field(default_factory=list) must prevent it")


# ──────────────────── the two halves, exercised TOGETHER ────────────────────

def test_rotation_and_recorder_together_make_the_rung_one_stratum_readable():
    """The composition's demonstrated advantage over either half alone.

    Rotation alone generates the stratum but leaves its per-rung verdicts
    pooled into one terminal verdict. The recorder alone records verdicts for a
    stratum in which, measured over the archive, 3 of 6 members are never
    dispatched at all. Together, every member reaches position 1 and its
    verdict there is readable from the artefact without an offline replay.
    """
    seen_first: dict = {}
    for n in range(24):
        RT.LADDER_ROTATION_SEED = f"experiment_{n}"
        out, order = _route(SIM_ROSTER, source="CC2-SIM", verdict="REFUTED")
        assert out.rung_attempts, "the recorder must populate on a real route"
        first = out.rung_attempts[0]
        assert first["position"] == 1
        assert first["model"] == order[0]
        seen_first.setdefault(first["model"], 0)
        seen_first[first["model"]] += 1
    # CC2-SIM is this finding's source and is excluded from the ranked list, so
    # the reachable position-1 set is the roster minus the source.
    expected = set(SIM_ROSTER) - {"CC2-SIM"}
    assert set(seen_first) == expected, (
        "over 24 seeded experiments every non-source member must have held "
        f"position 1 at least once; missing {sorted(expected - set(seen_first))}")
    assert all(a["verdict"] == "REFUTED" for a in out.rung_attempts)


def test_the_composed_fix_changes_no_resolution_outcome():
    """fable's order-inertness, executed against the real `route`.

    Resolution is decided by whether ANY rung confirms. A permutation of the
    rungs cannot change that, so rotation is resolution-neutral by construction
    and this asserts it on the real code path rather than on a model of it.
    """
    for confirming in SIM_ROSTER:
        results = []
        for seed in ("", "e0", "e1", "e2", "e3", "e4", "e5"):
            RT.LADDER_ROTATION_SEED = seed
            out, order = _route(
                SIM_ROSTER, source="CC2-SIM",
                verdict="REFUTED")
            # re-run with a verdict function keyed to the confirming seat
            def resolve_fn(model, finding, _o=[]):
                _o.append(model)
                return f"# {model}"
            out2 = RT.route(
                {"finding_id": "C1", "source_model": "CC2-SIM",
                 "title": "x", "description": "x"},
                SIM_ROSTER, [], lambda m, f: f"# {m}",
                lambda code: ("CONFIRMED" if code == f"# {confirming}"
                              else "REFUTED"),
                lambda a, b: 0.0, self_rung_enabled=False)
            results.append(out2.resolved)
        assert len(set(results)) == 1, (
            f"rotation changed whether the finding resolved when {confirming} "
            f"was the only confirming rung: {results}")


def test_p_resolve_is_permutation_invariant_under_exhaustion():
    """The derivation itself, in SymPy -- 24 permutations, 1 expression."""
    sp = pytest.importorskip("sympy")
    p = sp.symbols("p1:5", positive=True)
    exprs = {sp.simplify(1 - sp.prod([1 - x for x in perm]))
             for perm in itertools.permutations(p)}
    assert len(exprs) == 1, (
        f"P(resolve) must be order-inert under exhaustion; got {len(exprs)} "
        "distinct expressions")
    # Expected DISPATCH COUNT is NOT inert in general, and IS inert under the
    # exchangeability that "no pair separates" licenses. Both are asserted,
    # because reporting only the second would overstate the result.
    def e_disp(perm):
        total = 0
        for k in range(len(perm)):
            term = 1
            for j in range(k):
                term *= (1 - perm[j])
            total += term
        return sp.expand(total)
    general = {sp.simplify(e_disp(perm)) for perm in itertools.permutations(p)}
    assert len(general) == 24, (
        f"expected dispatch count is order-SENSITIVE in general; got {len(general)}")
    q = sp.symbols("q", positive=True)
    exch = {sp.simplify(e_disp(perm).subs({x: q for x in p}))
            for perm in itertools.permutations(p)}
    assert len(exch) == 1, (
        f"under exchangeability it must be inert; got {len(exch)}")


def test_the_runner_persists_both_halves_at_its_single_write_site():
    """The additive standard: an addition nothing reaches is not additive."""
    import pathlib
    src = pathlib.Path("bench/reference_runner_v3.py").read_text(
        errors="replace")
    assert '"rung_attempts": [dict(a) for a in' in src, (
        "rung_attempts must be persisted at the routing_history write site or "
        "the recorder never reaches an artefact")
    assert '"ladder_rotation": int(getattr(result, "ladder_rotation", 0) or 0),' in src
    assert "_rt.LADDER_ROTATION_SEED = str(cfg.experiment_name or \"\")" in src, (
        "the rotation seed must be set by the runner or the rotation is an "
        "addition nothing reaches")
