"""B21's status producer must DERIVE its answer, not carry it.

WHY THIS GUARD EXISTS. B21's own entry records a correction headed "THE PREMISE
IS WRONG, ESTABLISHED BY EXECUTION": the headline said the canonical runner does
not call the policy engine, which the entry calls *"true of the SYMBOL and false
of the BEHAVIOUR"*. So a status figure for B21 that is typed into prose is worth
nothing -- it is the exact claim that was already wrong once. The producer walks
syntax trees, and this file proves it walks them rather than reporting a
constant.

★ THE PREDICATE IS DELIBERATELY DIFFERENT FROM THE ONE USED FOR `record_miss`,
AND THE REASON IS THE QUESTION, NOT CONVENIENCE. On 2026-11-09 a guard for the
composer fallback had to require a STATEMENT-level call, because its question
was "does this ALWAYS record" and `None and record_miss(...)` satisfies a
substring while recording nothing. B21's question is different: "is the policy
engine REACHED from the canonical runner at all". A call inside an `if`, a
comprehension or a ternary is a real wiring and must count. So this producer
counts ANY Call node, and that choice is asserted here so it cannot drift into
the stricter form by imitation.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "which_of_b21s_five_steps_are_built_2026-11-09.py"


@pytest.fixture(scope="module")
def prod():
    assert PRODUCER.is_file(), f"the producer is absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("_b21steps", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_b21steps"] = m
    spec.loader.exec_module(m)
    return m


class TestItDerivesRatherThanDeclares:
    def test_a_real_call_is_counted(self, prod, tmp_path):
        f = tmp_path / "a.py"
        f.write_text("def g():\n    x = load_effective_policy(1)\n", encoding="utf-8")
        assert prod.call_sites(f, "load_effective_policy") == [2]

    def test_a_call_inside_a_branch_IS_counted(self, prod, tmp_path):
        """The question is REACHABILITY, so a guarded call is still a wiring."""
        f = tmp_path / "b.py"
        f.write_text("def g(c):\n    if c:\n        return load_effective_policy(1)\n",
                     encoding="utf-8")
        assert prod.call_sites(f, "load_effective_policy") == [3], (
            "a call inside a branch was not counted. For THIS question that is "
            "wrong: an `if` around a call still wires the engine in. The "
            "statement-level predicate belongs to the composer-fallback guard, "
            "whose question is whether a record ALWAYS happens")

    def test_a_mere_mention_is_NOT_counted(self, prod, tmp_path):
        """A name in a string, a comment or an attribute is not a call."""
        f = tmp_path / "c.py"
        f.write_text(
            "# load_effective_policy would go here\n"
            "S = 'load_effective_policy'\n"
            "def g(o):\n    return o.load_effective_policy\n",
            encoding="utf-8")
        assert prod.call_sites(f, "load_effective_policy") == [], (
            "a mention was counted as a call, so the producer would report a "
            "step as DONE on the strength of a comment")

    def test_an_unparseable_file_yields_nothing_rather_than_raising(self, prod, tmp_path):
        f = tmp_path / "d.py"
        f.write_text("def (:\n", encoding="utf-8")
        assert prod.call_sites(f, "anything") == []

    def test_the_live_answer_is_recomputed_not_stored(self, prod):
        """EXECUTED against the real tree, and the shape is checked, not the value.

        The counts themselves WILL move -- that is the point of the entry -- so
        pinning them here would be the stale-figure defect. What is pinned is
        that each step's answer comes back as evidence a reader can follow.
        """
        r = prod.measure()
        for key in ("step1_v3_calls_load_effective_policy",
                    "step4_v3_calls_validate_all_policies"):
            assert isinstance(r[key], list), (key, r[key])
        assert r["step2_n"] == len(prod.LIVE_HARNESS) == 6, (
            "the live-harness denominator moved away from the 6 files B13 "
            "names; if that list changed, change it deliberately")
        assert 0 <= r["step2_k"] <= r["step2_n"]
        assert isinstance(r["step3_role_files"], list)
        assert isinstance(r["step3_signature_takes_role"], bool)


class TestTheIntervalsAreCrossVerified:
    """THE FIRST VERSION OF THIS CLASS COULD NOT CATCH THE DEFECT IT WAS FOR.

    The producer's `_iv` returned WILSON TWICE where every other helper in
    `scripts/` returns Wilson and then Clopper-Pearson. These 3 tests all
    PASSED on that version: the bounds were ordered, the 2 Wilson routes
    genuinely agreed to 1.11e-16, and `(0.0, 0.0)` was the value pinned. It was
    caught by a SIBLING guard,
    `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, which
    executes every `_iv` in `scripts/` and compares all 4 numbers across them.

    So what is added here is the discriminator this class lacked: Clopper-
    Pearson is STRICTLY wider than Wilson at every interior k, which a Wilson
    pair in the second slot cannot satisfy. Measured over the grid 2 <= n < 40:
    strictly wider at 741 of 741 interior points, and a helper returning Wilson
    twice is caught at 741 of 741, 1.000000, Wilson [0.994843, 1.000000],
    Clopper-Pearson [0.995034, 1.000000]. CONTAINMENT alone would NOT catch it,
    because a Wilson pair contains itself with equality.
    """

    def test_two_routes_agree(self, prod):
        """Every proportion it prints carries an interval from 2 routes.

        The `if sl == sl` nan guard the first version wrapped this in is gone:
        the canonical helper imports statsmodels unconditionally, so there is
        no nan path left and the guard was a dead disjunct that could only ever
        make the assertion skippable.
        """
        for k, n in ((0, 6), (1, 6), (6, 6), (1, 5), (3, 5)):
            (wl, wh), (cl, ch), diff = prod._iv(k, n)
            assert 0.0 <= wl <= wh <= 1.0, (k, n, wl, wh)
            assert 0.0 <= cl <= ch <= 1.0, (k, n, cl, ch)
            assert diff < 1e-9, (k, n, diff)

    #: The grid the strictness figure is measured over. Quoted in B21, so it
    #: is defined here where the test that reproduces it can be run.
    GRID = range(2, 40)

    def test_the_second_pair_is_clopper_pearson_not_wilson_again(self, prod):
        """THE DISCRIMINATING TEST. Strictly wider, not merely containing.

        IT IS ALSO THE PRODUCER FOR THE FIGURE B21 QUOTES, which is why it
        walks a grid rather than the 5 convenient points: a rate quoted to the
        founder must be reproducible by committed code, and this is that code.
        It costs 5.24 s against a board of about 4000 s.
        """
        interior = strict = 0
        for n in self.GRID:
            for k in range(0, n + 1):
                (wl, wh), (cl, ch), _ = prod._iv(k, n)
                # Containment must hold EVERYWHERE, k == 0 and k == n included.
                assert cl <= wl + 1e-12 and ch >= wh - 1e-12, (
                    f"Clopper-Pearson must contain Wilson at {k}/{n}: "
                    f"CP[{cl:.9f},{ch:.9f}] W[{wl:.9f},{wh:.9f}]")
                if not 0 < k < n:
                    continue      # both lowers are 0 at k == 0, uppers 1 at k == n
                interior += 1
                if cl < wl and ch > wh:
                    strict += 1
                    continue
                raise AssertionError(
                    f"at {k}/{n} the second interval [{cl:.9f},{ch:.9f}] is not "
                    f"STRICTLY wider than Wilson [{wl:.9f},{wh:.9f}]; "
                    f"Clopper-Pearson is strictly wider at every interior k, "
                    f"so this is Wilson returned a second time")
        assert interior == 741, (
            f"the grid holds {interior} interior points, not the 741 B21 "
            f"quotes -- the figure and the grid have drifted apart")
        assert strict == interior, (strict, interior)

    def test_that_discriminator_can_actually_catch_the_defect(self, prod):
        """ANTI-VACUITY, and the load-bearing half.

        A test reporting 0 violations because nothing is wrong is
        indistinguishable from one reporting 0 because it detects nothing. So
        the predicate is run against a DELIBERATELY BROKEN helper -- Wilson
        returned in both slots, the exact shape this producer shipped with on
        2026-11-09 -- and required to reject every interior point.

        This is also why CONTAINMENT is not the predicate: a Wilson pair
        contains itself with equality, so a containment test passes on the
        broken form at every one of the 741 points.
        """
        def broken(k, n):
            (wl, wh), _, _ = prod._iv(k, n)
            return (wl, wh), (wl, wh), 0.0

        caught = contained = interior = 0
        for n in self.GRID:
            for k in range(1, n):
                interior += 1
                (wl, wh), (cl, ch), _ = broken(k, n)
                if not (cl < wl and ch > wh):
                    caught += 1
                if cl <= wl + 1e-12 and ch >= wh - 1e-12:
                    contained += 1
        assert interior == 741, interior
        assert caught == interior, (
            f"the strict-width predicate catches the broken helper at only "
            f"{caught} of {interior} interior points, so it would have let "
            f"this very defect through")
        assert contained == interior, (
            f"containment holds on the broken helper at {contained} of "
            f"{interior} points -- if this ever fails, containment has become "
            f"a usable discriminator and this test's premise is stale")

    def test_it_is_the_canonical_helper_byte_for_byte(self):
        """1 DEFINITION, MANY USERS. A near-copy is how 18 variants arose.

        The canonical body is the modal one in `scripts/`. Comparing the hash
        rather than the behaviour is deliberate here: behaviour is already
        compared by the sibling guard across every helper, and what this test
        adds is that no local edit has forked this copy away from the others.
        """
        import hashlib
        canon = (REPO / "scripts"
                 / "what_the_commit_gate_actually_costs_over_time_2026-11-08.py")
        assert canon.is_file(), f"the canonical source is absent: {canon}"

        def body_hash(path):
            txt = path.read_text(encoding="utf-8")
            for node in ast.walk(ast.parse(txt)):
                if (isinstance(node, ast.FunctionDef)
                        and node.name == "_iv"):
                    seg = ast.get_source_segment(txt, node)
                    return hashlib.sha256(seg.encode()).hexdigest()[:16]
            return None

        mine = body_hash(PRODUCER)
        theirs = body_hash(canon)
        assert theirs == "5c0ff108ca6d5966", (
            f"the canonical body has itself changed to {theirs}; re-derive the "
            f"modal hash across scripts/ before updating this pin")
        assert mine == theirs, (
            f"this producer's `_iv` is {mine} and the canonical one is "
            f"{theirs} -- it has forked into a variant of its own")

    def test_an_empty_denominator_does_not_raise(self, prod):
        """AT n == 0 THE ANSWER IS [0, 1] AND THE FIRST VERSION PINNED [0, 0].

        With no observations the binomial likelihood is 1 for every p, so no p
        is excluded and the whole unit interval is the only honest answer.
        `(0.0, 0.0)` asserts certainty that the proportion is 0 on the strength
        of no data, which is the opposite of what an empty denominator means.
        statsmodels returns (nan, nan) here, so the canonical helper
        short-circuits rather than printing nan.
        """
        (wl, wh), (cl, ch), diff = prod._iv(0, 0)
        assert (wl, wh) == (0.0, 1.0), (
            f"got {(wl, wh)}; a 0 denominator excludes no proportion at all")
        assert (cl, ch) == (0.0, 1.0), (cl, ch)
        assert diff == 0.0, diff


class TestItRuns:
    def test_help_is_answered_for_free(self):
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "STEPS BUILT" not in r.stdout, "--help ran the measurement"

    def test_it_exits_zero_and_names_all_five_steps(self):
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=REPO, timeout=600)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        for n in range(1, 6):
            assert f"\n{n}." in r.stdout, (
                f"step {n} is not reported; a partial status reads as a "
                f"complete one")
        assert "STEPS BUILT:" in r.stdout
        assert "Wilson [" in r.stdout
        assert "Clopper-Pearson [" in r.stdout, (
            "the second interval is computed and not PRINTED, so the "
            "report carries 1 interval while the helper returns 2 -- an "
            "addition nothing reaches")
        assert "NOT A RECOMMENDATION" in r.stdout, (
            "the producer must say that adopting a step is his decision; it "
            "measures status and does not advise")

    def test_the_json_form_carries_the_same_fields(self):
        import json
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER), "--json"],
                           capture_output=True, text=True, cwd=REPO, timeout=600)
        assert r.returncode == 0, r.stderr[-800:]
        d = json.loads(r.stdout)
        assert {"step2_k", "step2_n", "step3_role_files"} <= set(d)
