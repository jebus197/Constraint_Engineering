"""The three gaps the instrument confirmation panel found, closed.

Both reviewers ran mutation tests over all 34 inventory rows and independently
refuted the inventory's "32 of 34 commissioned" figure. These are the components
whose defining behaviour could be hardwired to a constant with the whole suite
still green -- i.e. the inventory said "tested" where the truth was "called".

Measured 2026-08-28, before these tests existed:
  * check_sk_threshold  -> `return True` : 321 tests passed
  * _update_finding_statuses, CHALLENGE silenced : all tests naming it passed
  * the self-disabling skip guard : 45 passed -> 33 passed + 12 SKIPPED, rc 0
"""
import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import check_sk_threshold   # noqa: E402


# --------------------------------------------------------------------------- #
# I11 -- the Valley of Bad Fixes gate must be able to say NO                   #
# --------------------------------------------------------------------------- #
def test_a_fix_below_the_threshold_is_refused():
    """`return True` passed 321 tests. This is the assertion that was missing.

    Nothing anywhere required check_sk_threshold to reject anything, so the gate
    that exists to keep harmful fixes out could admit every fix silently, in all
    19 configurations that run it.
    """
    passes, s_star = check_sk_threshold(sk=0.01, nu_b=0.5, nu_f=0.5, q=0.1, R=0.1)
    assert s_star > 0.01, f"threshold {s_star} does not sit above the fix, so this proves nothing"
    assert passes is False, "a fix scoring below S* was admitted"


def test_a_fix_above_the_threshold_is_admitted():
    """The known-GOOD half: without it, `return False` would also pass."""
    passes, s_star = check_sk_threshold(sk=1.0, nu_b=0.01, nu_f=0.99, q=0.9, R=0.9)
    assert passes is True, f"a fix scoring 1.0 against S*={s_star} was refused"


def test_the_floor_can_refuse_a_fix_the_threshold_would_admit():
    below, _ = check_sk_threshold(sk=0.30, nu_b=0.5, nu_f=0.5, q=0.9, R=0.9, s_floor=0.9)
    above, _ = check_sk_threshold(sk=0.95, nu_b=0.5, nu_f=0.5, q=0.9, R=0.9, s_floor=0.9)
    assert below is False and above is True, "s_floor is not being applied"


# --------------------------------------------------------------------------- #
# I18 -- a CHALLENGE must still be able to contest a CONFIRMED finding         #
# --------------------------------------------------------------------------- #
def test_challenge_votes_are_read_from_the_verdict_list():
    """Pins the line that silencing broke: `challenges` must come from verdicts.

    Deleting the CHALLENGE collection left every test naming the function green.
    A model's disagreement with a CONFIRMED finding would simply vanish, the
    contested count would under-report, and gate condition (c) would open early
    on evidence that was never actually uncontested.
    """
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "_update_finding_statuses")

    # Find the assignment to `challenges` itself. Searching the function for the
    # word CHALLENGE is not enough -- it occurs elsewhere, so `challenges = []`
    # left an earlier version of this test green.
    assigns = [n for n in ast.walk(fn) if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "challenges" for t in n.targets)]
    assert assigns, "_update_finding_statuses no longer assigns `challenges` at all"
    for a in assigns:
        rhs = ast.unparse(a.value)
        assert "CHALLENGE" in rhs and "verdict" in rhs, (
            f"`challenges` is assigned {rhs!r}, which does not read CHALLENGE verdicts. "
            "A model's disagreement with a CONFIRMED finding would vanish silently.")

    unresolved = [n for n in ast.walk(fn) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "unresolved_challenges"
                          for t in n.targets)]
    assert unresolved, "the unresolved-challenge computation is gone"


# --------------------------------------------------------------------------- #
# A skip guard must never ask the component under test whether to run          #
# --------------------------------------------------------------------------- #
def _skipif_conditions(path: pathlib.Path):
    """Yield the source of every `skipif` condition expression in `path`."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr == "skipif" and node.args:
            yield ast.unparse(node.args[0])


def test_no_skip_guard_calls_the_code_it_guards():
    """The failure this catches exits 0, which is why it survived so long.

    `test_immune_memory_consumption.py` computed its guard by calling
    `compute_sk` -- the component under test -- so breaking the component turned
    12 tests into skips and the file passed. Both panel reviewers found it
    independently on 2026-08-28.
    """
    # Names DEFINED in the runner, not merely imported into it. `dir(rr)` also
    # returns re-exports such as `Path`, which made legitimate file-presence
    # guards look like calls into project logic.
    runner = ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8"))
    owned = {n.name for n in runner.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    offenders = []
    for f in sorted((REPO / "bench" / "tests").glob("test_*.py")):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        # A skipif condition is usually a NAME (`not _PIPELINE_LIVE`) and the
        # call hides in that name's module-level assignment. Resolving one hop
        # is required: an earlier version of this test looked only at the
        # condition text and passed against the very defect it targets.
        defined = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                rhs = ast.unparse(node.value)
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        defined[t.id] = rhs
        for cond in _skipif_conditions(f):
            sources = [cond] + [defined[n.id] for n in ast.walk(ast.parse(cond))
                                if isinstance(n, ast.Name) and n.id in defined]
            for src in sources:
                called = {m for m in owned if f"{m}(" in src}
                if called:
                    offenders.append(
                        f"{f.name}: skip guard `{cond}` resolves to a call of {sorted(called)}")
    assert not offenders, (
        "a skip guard decides whether to run by calling the code under test, so "
        "breaking that code silences the tests instead of failing them:\n  "
        + "\n  ".join(offenders))
