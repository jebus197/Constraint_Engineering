# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_fixes_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4138ec52dc5b11f2223c0c2a4572af89c40f707e8ed69652404e2ec1f20b207f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The vacuity predicate's direction is measured, and the raise probes cannot decide it.

WHY IT EXISTS. In the blind round of 2026-11-10 a panel seat reported that
HEAD's `bench/proof_verify.asserts_something` returns True on a strict superset
of the discarded copy's, naming 3 HEAD-only cases: an availability-only
`assert`, `raise SystemExit(0)`, and a dead `raise ValueError`. The joint brief
then recorded that 1 of the 3 did not reproduce and asked whether the direction
claim survives on the other 2.

IT DOES NOT SURVIVE ON THOSE 2, AND THE 3RD WAS NOT AN ISOLATED SLIP. All 3
named cases are `ast.Assert` or `ast.Raise` nodes, and BOTH predicates open
their walk with the SAME clause -- `isinstance(node, (_a.Assert, _a.Raise))`
-- which is `ast.dump`-identical between the 2 files, as is every statement
before the walk. A probe that parses to an Assert or a Raise therefore returns
True under both BY CONSTRUCTION, and no assert-shaped or raise-shaped probe can
separate them. The 2 predicates differ in exactly 1 clause:

    HEAD       any `ast.Constant` string containing "FALSIFIED" anywhere
    discarded  only strings emitted by an `ast.Call` that satisfy
               `_declares_falsified`

So HEAD is indeed the broader predicate -- the brief's CONCLUSION is right --
but it is broader on the FALSIFIED-string route, not on raises, and the cases
that witness it are non-emitted FALSIFIED strings such as a docstring or a bare
assignment. The reported figures (6 of 7 against 4 of 7) cannot have come from
the dispatched tree, because the discarded clause calls `_declares_falsified`,
which is defined NOWHERE in it: its module-level import of that name from
`bench.falsifier_verify` raises ImportError, so the discarded file is not even
loadable here. Any run of it supplied a substitute, and the differential is a
measurement of that substitute.

WHAT THIS FILE PINS, so the refuted reading cannot be re-asserted:
  1. HEAD accepts all 3 of the cases reported as HEAD-only -- which is the
     SAFE direction and is not a defect; a predicate deciding whether a clean
     exit means anything should err towards UNTOOLABLE, not towards admissible.
  2. HEAD's first walk clause is still exactly `(Assert, Raise)`. If that is
     ever narrowed, this test fails loudly -- at which point raise probes DO
     become discriminating and the direction must be re-measured.
  3. `_declares_falsified` is still absent from `bench.falsifier_verify`. The
     day it is folded back, this test fails, which is the day the discarded
     predicate becomes loadable and the differential becomes reproducible.
  4. `assert True` defeats HEAD's predicate. This is the residual the brief
     asks about, and it is NOT what makes the distinction immaterial: `assert
     True` is a DELIBERATE vacuous proof, while an availability-only assert or
     a dead raise is an ACCIDENTAL one. The 2 predicates are equally unsound
     against the first and identical against the second, so the distinction is
     immaterial for a different and stronger reason than the brief offers --
     on the whole accidental class they do not differ at all.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

HEAD = REPO / "bench" / "proof_verify.py"

#: The 3 cases reported as HEAD-only in the blind round, each paired with the
#: AST node class that decides it. All 3 are matched by clause 1.
REPORTED_HEAD_ONLY = [
    ("availability-only assert", "import sympy\nassert sympy is not None",
     ast.Assert),
    ("raise SystemExit(0)", "print('x')\nraise SystemExit(0)", ast.Raise),
    ("dead raise ValueError", "if False:\n    raise ValueError('x')",
     ast.Raise),
]


def _pred():
    from bench.proof_verify import asserts_something
    return asserts_something


def _head_clause_one():
    """HEAD's first walk clause, read out of its syntax tree."""
    tree = ast.parse(HEAD.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "asserts_something")
    loop = next(n for n in ast.walk(fn) if isinstance(n, ast.For))
    return loop.body[0]


class TestTheReportedHeadOnlyCasesAreNotHeadOnly:
    @pytest.mark.parametrize("label,code,node", REPORTED_HEAD_ONLY,
                             ids=[r[0] for r in REPORTED_HEAD_ONLY])
    def test_the_case_parses_to_the_node_clause_one_matches(self, label, code,
                                                            node):
        """Each reported case really is an Assert/Raise, so clause 1 decides it."""
        assert any(isinstance(n, node) for n in ast.walk(ast.parse(code))), (
            f"{label} does not contain an {node.__name__}; the refutation in "
            f"this file's docstring rests on it and must be re-derived")

    @pytest.mark.parametrize("label,code,node", REPORTED_HEAD_ONLY,
                             ids=[r[0] for r in REPORTED_HEAD_ONLY])
    def test_head_accepts_it(self, label, code, node):
        """HEAD returns True -- the safe direction, and the reported value."""
        assert _pred()(code) is True, label

    def test_clause_one_is_still_assert_or_raise(self):
        """If clause 1 is narrowed, raise probes become discriminating."""
        src = ast.unparse(_head_clause_one())
        assert "_a.Assert" in src and "_a.Raise" in src, (
            f"clause 1 is now {src!r}; a raise no longer necessarily returns "
            f"True, so the direction claim must be RE-MEASURED rather than "
            f"read off this file")


class TestTheDiscardedPredicateIsNotLoadableHere:
    def test_declares_falsified_is_absent(self):
        """The symbol the discarded clause 2 calls is defined nowhere in-tree."""
        import bench.falsifier_verify as fv
        assert not hasattr(fv, "declares_falsified"), (
            "`declares_falsified` has been folded back, so the discarded "
            "predicate is now loadable and its differential against HEAD is "
            "reproducible -- re-measure it and update this file")

    def test_the_absent_symbol_is_what_the_discarded_clause_calls(self):
        """Pin WHY absence matters: clause 2 of the discarded copy calls it."""
        harvest = (REPO / "bench" / "logs" / "check_my_fixes_2026-11-10"
                   / "sandbox_harvest" / "cc2" / "attempt-1" / "files"
                   / "bench" / "proof_verify.py")
        if not harvest.is_file():
            pytest.fail(
                "the discarded copy is no longer in the tree, so this file's "
                "docstring cites evidence a reader cannot reach; either "
                "restore the harvest or rewrite the docstring to stop "
                "claiming a reproducible comparison")
        src = harvest.read_text(encoding="utf-8")
        assert "_declares_falsified" in src
        assert "from bench.falsifier_verify import declares_falsified" in src

    def test_clause_one_is_identical_between_the_two_copies(self):
        """The core refutation: no assert/raise probe can separate them."""
        harvest = (REPO / "bench" / "logs" / "check_my_fixes_2026-11-10"
                   / "sandbox_harvest" / "cc2" / "attempt-1" / "files"
                   / "bench" / "proof_verify.py")
        if not harvest.is_file():
            pytest.fail("the discarded copy is no longer in the tree; see the "
                        "sibling test for why that breaks this file's claim")
        tree = ast.parse(harvest.read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "asserts_something")
        loop = next(n for n in ast.walk(fn) if isinstance(n, ast.For))
        assert ast.dump(loop.body[0]) == ast.dump(_head_clause_one()), (
            "clause 1 now DIFFERS between the 2 copies, so a raise probe can "
            "separate them after all and the docstring's refutation is void")


class TestTheResidualIsStatedNotHidden:
    def test_assert_true_defeats_the_predicate(self):
        """The declared residual. Neither predicate is sound against it."""
        assert _pred()("assert True") is True, (
            "`assert True` is now refused -- the residual this file records "
            "has been repaired and the docstring must be corrected")

    def test_an_import_only_proof_is_still_refused(self):
        """The property the predicate does discharge, kept under test."""
        assert _pred()("import sympy") is False
        assert _pred()("") is False
