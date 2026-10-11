"""The Lean anchor pool is difficulty-INVARIANT, and its grader refuses 4 measured loopholes.

FOUNDER'S RULING, 2026-10-11: *"y, build the anchor set with Lean"*, under the condition
*"if it adds nothing of use, then there is no requirement for you to do it."*

WHY THE POOL EXISTS. Relegation on sustained degradation is NOT IDENTIFIED from the live task
stream: only the difference between capability and difficulty enters the model, so a roster-wide
capability drop and a stream-wide difficulty rise produce identical distributions. That was
established symbolically before anything was built -- SymPy returns exactly 0, z3 returns
`unsat`, mpmath returns 0.0 over 27 points. The anchor breaks it not by RATING difficulty, which
would be circular, but by holding difficulty INVARIANT: byte-stable statements, graded by a
deterministic kernel rather than by a model judging a model.

EVERY LOOPHOLE BELOW WAS MEASURED ON LEAN 4.34.1 BEFORE THE GRADER WAS WRITTEN. All 4 exit 0,
and 3 of them emit no output whatsoever, so a grader keying on the exit code accepts them:
`sorry` (warning only), `axiom` (silent), `native_decide` (silent), and a RESTATED theorem
(silent, and the worst -- changing `a + b = b + a` to `a + b = a + b` and proving it by `rfl`
is accepted under the same name). The literature calls the last one semantic hallucination and
reports formal-versus-informal discrepancies in more than half of miniF2F's problems.

AND THE 5TH TRAP WAS THE AUTHOR'S OWN. The first reading of those exit codes returned 0 for all
3 cheats, because `$?` captured a `head` in a pipeline instead of `lean`. A grader built on that
reading would have passed everything. The exit code is now captured directly.

THESE TESTS EXECUTE THE GRADER. A test that read its source could not tell a guard that fires
from one that is spelled correctly, and this module's entire value is in what it REFUSES.
`execute-do-not-grep`.

LEAN IS OPTIONAL, SO THE TESTS SKIP RATHER THAN FAIL WHEN IT IS ABSENT -- the founder's standing
Wolfram ruling, that nobody may be compelled to install a tool, applies unchanged. The tests
that need no toolchain (the digest, the token refusals, the Wilson arithmetic) always run.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "bench" / "lean_anchor_2026-10-11.py"


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location("lean_anchor", TARGET)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lean_anchor"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def has_lean(M):
    return M.lean_available() is not None


needs_lean = pytest.mark.skipif(
    importlib.util.find_spec("lean_anchor") is None and False, reason="")


class TestTheseNeedNoToolchain:
    """Everything here runs whether or not Lean is installed."""

    def test_the_pool_is_not_empty_and_spans_tiers(self, M):
        assert len(M.POOL) >= 4, len(M.POOL)
        tiers = {p.tier for p in M.POOL}
        assert len(tiers) >= 3, (
            f"a pool with {len(tiers)} tier(s) cannot span a capability range: {tiers}")

    def test_every_statement_is_a_theorem_ending_in_assignment(self, M):
        for p in M.POOL:
            assert p.statement.startswith("theorem "), p.pid
            assert p.statement.rstrip().endswith(":="), (
                f"{p.pid}: a statement must end at `:=` so the candidate supplies ONLY a proof")

    def test_the_digest_pins_the_pool(self, M):
        """Invariance is only meaningful if it is checkable."""
        d1 = M.pool_digest()
        assert len(d1) == 64
        altered = (M.Problem("L1", "theorem anchor_L1 (a : Nat) : a + 0 = a + 0 :=",
                             "trivial", "restated"),)
        assert M.pool_digest(altered) != d1, (
            "the digest does not change when a statement changes, so it cannot pin the pool")

    def test_a_refused_token_fails_without_running_lean(self, M):
        """These must fail on inspection, so they cost nothing and work with no toolchain."""
        for tok, proof in (("sorry", " by sorry"),
                           ("axiom", "\naxiom cheat : forall a : Nat, a = a + 1"),
                           ("native_decide", " by native_decide")):
            r = M.grade(M.POOL[0], proof)
            assert r["verdict"] in (M.FAIL, M.UNAVAILABLE), (tok, r)
            if r["verdict"] == M.FAIL:
                assert tok in r["reason"], (tok, r["reason"])

    def test_wilson_lower_is_zero_on_no_attempts_and_below_the_point(self, M):
        assert M.wilson_lower(0, 0) == 0.0
        assert M.wilson_lower(5, 5) < 1.0, "a perfect score must not certify a rate of 1"
        assert M.wilson_lower(5, 5) < 5 / 5
        assert M.wilson_lower(50, 50) > M.wilson_lower(5, 5), (
            "more evidence must raise the lower bound")

    def test_a_perfect_small_pool_does_not_support_a_high_rate(self, M):
        """The honest consequence of a 5-problem pool, asserted rather than buried."""
        assert M.wilson_lower(5, 5) < 0.60, (
            f"5 of 5 gives {M.wilson_lower(5,5):.4f}; if this ever exceeds 0.60 the arithmetic "
            f"changed and the pool-size caveat in the docstring is stale")

    def test_an_absent_toolchain_leaves_the_denominator(self, M, monkeypatch):
        """UNAVAILABLE must be neither PASS nor FAIL, or an absent tool moves a seat's rate."""
        monkeypatch.setattr(M, "lean_available", lambda: None)
        s = M.score_seat({p.pid: " whatever" for p in M.POOL})
        assert s["attempts"] == 0, s
        assert s["unavailable"] == len(M.POOL), s
        assert s["successes"] == 0 and s["point_estimate"] is None, s
        assert s["wilson_lower"] == 0.0, s


class TestTheTwoGuardsAMutationPassFoundUNTESTED:
    """★ BOTH OF THESE EXIST BECAUSE A MUTATION PASS SURVIVED.

    Deleting the output check (`"error" in out or "sorry" in out`) left all 14 tests green,
    because the refused-token scan catches `sorry` before Lean ever runs -- so the branch that
    catches a LEAN-REPORTED sorry had no test behind it. And deleting the statement-identity
    branch entirely also left 14 green, because that branch was a TAUTOLOGY:
    `source = problem.statement + submitted`, so `source.startswith(problem.statement)` could
    never be false. A guard that cannot fail, inside the check protecting the pool's
    invariance. The guard is now on declaration keywords, which is checkable, and both
    branches are exercised below."""

    def test_an_exit_zero_with_a_reported_error_still_fails(self, M, monkeypatch):
        """Drives the output branch directly: Lean exits 0 and reports an error anyway."""
        class _Proc:
            returncode = 0
            stdout = "Foo.lean:1:0: error: something the kernel disliked"
            stderr = ""
        monkeypatch.setattr(M, "lean_available", lambda: "/usr/bin/true")
        monkeypatch.setattr(M.subprocess, "run", lambda *a, **k: _Proc())
        r = M.grade(M.POOL[0], " Nat.add_zero a")
        assert r["verdict"] == M.FAIL, r
        assert "exited 0" in r["reason"], r["reason"]

    def test_an_exit_zero_with_a_reported_sorry_still_fails(self, M, monkeypatch):
        """The loophole the token scan cannot reach: Lean itself reporting a `sorry`."""
        class _Proc:
            returncode = 0
            stdout = "Foo.lean:1:8: warning: declaration uses `sorry`"
            stderr = ""
        monkeypatch.setattr(M, "lean_available", lambda: "/usr/bin/true")
        monkeypatch.setattr(M.subprocess, "run", lambda *a, **k: _Proc())
        r = M.grade(M.POOL[0], " Nat.add_zero a")
        assert r["verdict"] == M.FAIL, r

    def test_a_clean_exit_zero_passes_so_the_branch_is_not_trivially_failing(self, M, monkeypatch):
        """MUTATION-GRADE: without this, a grader that failed EVERYTHING would pass the 2 above."""
        class _Proc:
            returncode = 0
            stdout = ""
            stderr = ""
        monkeypatch.setattr(M, "lean_available", lambda: "/usr/bin/true")
        monkeypatch.setattr(M.subprocess, "run", lambda *a, **k: _Proc())
        assert M.grade(M.POOL[0], " Nat.add_zero a")["verdict"] == M.PASS

    def test_a_submission_opening_its_own_declaration_fails(self, M):
        """The real restatement attack, and it needs no toolchain to refuse."""
        for kw, proof in (
            ("theorem", " rfl\ntheorem anchor_L2 (a b : Nat) : a + b = a + b := rfl"),
            ("lemma", " rfl\nlemma sneaky : True := trivial"),
            ("example", " rfl\nexample : True := trivial"),
        ):
            r = M.grade(M.POOL[1], proof)
            assert r["verdict"] == M.FAIL, (kw, r)
            assert "declaration" in r["reason"], (kw, r["reason"])

    def test_a_declaration_keyword_inside_a_comment_is_not_an_attack(self, M, has_lean):
        """Over-refusing would make the pool unusable, which is its own failure."""
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        r = M.grade(M.POOL[1], " Nat.add_comm a b -- this theorem is commutativity")
        assert r["verdict"] == M.PASS, r

    def test_the_helper_strips_block_comments_too(self, M):
        assert M._declares_its_own(" foo /- theorem hidden -/ bar") is None
        assert M._declares_its_own(" foo\ntheorem real : True := trivial") == "theorem"
        assert M._declares_its_own(" Nat.add_comm a b") is None


class TestTheseNeedLean:
    def test_the_reference_proofs_all_pass(self, M, has_lean):
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        s = M.score_seat(M.REFERENCE_PROOFS)
        assert s["attempts"] == len(M.POOL), s
        assert s["successes"] == len(M.POOL), [r for r in s["rows"] if r["verdict"] != M.PASS]

    def test_every_measured_loophole_is_refused(self, M, has_lean):
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        d = M.claim_the_grader_rejects_every_measured_loophole()
        assert d["all_as_expected"], d["cases"]

    def test_a_wrong_but_well_formed_proof_fails(self, M, has_lean):
        """No refused token, correct shape, wrong lemma. Only the kernel catches this."""
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        r = M.grade(M.POOL[1], " Nat.mul_comm a b")
        assert r["verdict"] == M.FAIL, r
        assert "sorry" not in r["reason"] and "axiom" not in r["reason"], (
            "this must fail on the KERNEL's verdict, not on a token scan")

    def test_a_restated_statement_is_a_different_problem(self, M, has_lean):
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        d = M.claim_a_restated_statement_cannot_pass()
        assert d["lean_accepts_the_restatement_on_its_own"] == M.PASS, (
            "if Lean no longer accepts the weakened statement, the guard is testing nothing")
        assert d["the_pool_problem_rejects_rfl"] == M.FAIL, d
        assert d["digest_differs"] is True, d

    def test_the_hardest_problem_is_not_a_one_liner(self, M, has_lean):
        """A pool whose hard tier falls to a single lemma does not span anything."""
        if not has_lean:
            pytest.skip("lean absent; optional by the founder's Wolfram ruling")
        hard = [p for p in M.POOL if p.tier == "hard"]
        assert hard, "no hard problem in the pool"
        ref = M.REFERENCE_PROOFS[hard[0].pid]
        assert ref.count("\n") >= 5, (
            f"the hard problem's reference proof is {ref.count(chr(10))+1} line(s); a 1-line "
            f"hard tier means the pool does not span a capability range")
        assert M.grade(hard[0], " rfl")["verdict"] == M.FAIL
        assert M.grade(hard[0], " Nat.lt_irrefl n")["verdict"] == M.FAIL


class TestItIsWiredToSomethingRatherThanStandingAlone:
    """An addition nothing reaches is not additive. This checks the OUTPUT SHAPE matches what
    routing's ranking would consume, so the remaining gap is 1 reviewable change rather than
    an unknown amount of work."""

    def test_the_score_is_the_pair_routings_wilson_ranking_takes(self, M):
        s = M.score_seat({})
        for k in ("successes", "attempts", "wilson_lower", "pool_sha256"):
            assert k in s, (k, sorted(s))
        assert isinstance(s["successes"], int) and isinstance(s["attempts"], int)

    def test_the_live_ladder_still_ranks_by_name_so_the_gap_is_named(self):
        """Pins the fact that makes this file's last mile the founder's decision.

        If a later change makes routing rate-aware, this test SHOULD fail and be updated --
        that is the point. It exists so the gap cannot be silently forgotten or silently closed.
        """
        spec = importlib.util.spec_from_file_location("rt_anchor", REPO / "bench" / "routing.py")
        rt = importlib.util.module_from_spec(spec)
        sys.modules["rt_anchor"] = rt
        spec.loader.exec_module(rt)
        order = rt.DEFAULT_FALSIFIER_STRENGTH
        assert isinstance(order, tuple) and all(isinstance(x, str) for x in order), order
        assert all(not x.replace(".", "").isdigit() for x in order), (
            "DEFAULT_FALSIFIER_STRENGTH now contains numbers rather than names, so routing may "
            "have become rate-aware -- if so, wire lean_anchor.score_seat into it and rewrite "
            "this test to assert the wiring instead of the gap")
