"""The fix-efficacy probe is wired, contributory, and cannot gate anything.

CC2 measured on the repair-loop panel that `bench/fix_efficacy.py` was built,
tested, consumed by two scripts and called by NOTHING that runs:
`grep -c fix_efficacy bench/reference_runner_v2.py` returned 0.

These tests pin the wiring AND the two properties that make it safe to wire.
"""
import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

SRC = (REPO / "bench" / "reference_runner_v2.py").read_text(encoding="utf-8")


def _fn(name):
    return next(n for n in ast.walk(ast.parse(SRC))
                if isinstance(n, ast.FunctionDef) and n.name == name)


def test_the_probe_is_actually_called():
    body = ast.unparse(_fn("_update_finding_statuses"))
    assert "fix_efficacy" in body, "the probe is not called from the status pass"
    # The cap MOVED into `fix_efficacy_decision()` on 2026-08-30 when the guard
    # was extracted so it could be tested at all. The property is unchanged and
    # is asserted behaviourally below and in
    # test_fix_efficacy_records_why_it_did_not_run_2026-08-30.py; asserting the
    # constant's TEXT here only ever pinned where the code happened to live.
    assert "fix_efficacy_decision" in body, "the decision helper is not consulted"


def test_the_probe_is_contributory_and_cannot_gate_anything():
    """The rho ruling of 2026-08-29 in test form: an instrument that measures the
    exhaustion of a search must not be able to refuse the convergence it measures."""
    for gate in ("_evaluate_gate_conditions", "_check_gamma_alt_convergence"):
        body = ast.unparse(_fn(gate))
        assert "fix_efficacy" not in body, (
            f"{gate} mentions the fix-efficacy probe; it must not be able to gate")


def _probe_block():
    """The `if ...fix_efficacy_attempted...` statement, isolated by AST.

    An earlier version of this test sliced the function's source by string
    offsets and swept in the neighbouring bugzilla block, which legitimately
    writes `verified`. It failed against correct code. Boundaries guessed from
    text are not boundaries.
    """
    fn = _fn("_update_finding_statuses")
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and "fix_efficacy_attempted" in ast.unparse(node.test):
            return ast.unparse(node)
    # 2026-08-30: the admission test moved into `fix_efficacy_decision()`, so the
    # guard's condition no longer names `fix_efficacy_attempted` inline. The
    # block is now the `if` on the decision's result -- same statement, same
    # purpose, different (and testable) condition.
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and "_fe_decision" in ast.unparse(node.test):
            return ast.unparse(node)
    raise AssertionError("the fix-efficacy probe block was not found")


def test_the_probe_writes_no_status():
    seg = _probe_block()
    for forbidden in ("registry.resolve", "'verified'", '"verified"', "escalated",
                      "UNCONFIRMED", "mechanical_fault"):
        assert forbidden not in seg, (
            f"the probe block touches {forbidden}; it must write one key and no status")


def test_the_probe_writes_exactly_one_key_on_the_entry():
    seg = _probe_block()
    keys = set(re.findall(r"entry\[[\'\"]([a-z_]+)[\'\"]\]\s*=", seg))
    assert keys <= {"fix_efficacy", "fix_efficacy_attempted"}, (
        f"the probe block assigns unexpected entry keys: {sorted(keys)}")


def test_only_the_ineffective_outcome_reaches_a_model():
    """The four INDETERMINATE outcomes must stay silent. 'The instrument could
    not look' is about the apparatus, and telling a model that invites it to
    rewrite a fix nothing found fault with."""
    body = ast.unparse(_fn("_rejection_lines"))
    assert "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER" in body
    for silent in ("INDETERMINATE_NOT_INTERCEPTED", "INDETERMINATE_NO_BASELINE",
                   "INDETERMINATE_NO_APPLICABLE_FIX", "INDETERMINATE_OTHER"):
        assert silent not in body, f"{silent} is shown to the model; it must not be"


def test_the_cap_exists_and_is_small():
    import reference_runner_v2 as rr
    assert 1 <= rr.FIX_EFFICACY_PER_ROUND_LIMIT <= 10
