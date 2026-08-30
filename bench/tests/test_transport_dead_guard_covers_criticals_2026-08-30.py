"""A dead transport must never look like an exhausted ladder — at any severity.

THE DEFECT, found by CC2 in panel review 2026-08-30 and confirmed by AST.
--------------------------------------------------------------------------
`_apply_routing` sets `e["_error_route_pending"] = True`, and after `route()`
returns it checks that flag to decide whether any rung actually REACHED a model.
Its own comment: a transport-dead round "must not burn the attempt nor mint a
false 'ladder exhausted' record".

The assignment sat INSIDE `if (severity or 0.0) < CRITICAL_SEVERITY_THRESHOLD:`.
So for a CRITICAL the flag was never set, `e.pop(...)` was always falsy, and the
guard never ran. A critical whose every rung died on transport was recorded as
genuinely irreducible: `irreducible_escalation = True`.

`FindingRegistry.unverified_critical_count` then does
`if e.get("irreducible_escalation"): continue` — so that critical STOPS BLOCKING
CONVERGENCE. The chain is: network fails -> critical looks exhausted -> the
convergence gate stops counting it -> the run can converge on a transport
failure rather than on evidence.

Convergence caused by infrastructure is the most expensive failure class this
project has, so the guard is pinned structurally: the flag must not be reachable
only through a severity test.
"""
import ast, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v2 as R

SRC = pathlib.Path(R.__file__).read_text(encoding="utf-8")
TREE = ast.parse(SRC)


def _fn(name):
    return next(n for n in ast.walk(TREE)
                if isinstance(n, ast.FunctionDef) and n.name == name)


class TestTheGuardIsNotSeverityGated:
    def test_the_pending_flag_is_set_outside_any_severity_branch(self):
        fn = _fn("_apply_routing")
        sets = [n for n in ast.walk(fn)
                if isinstance(n, ast.Assign)
                and "_error_route_pending" in ast.unparse(n.targets[0])
                and ast.unparse(n.value) == "True"]
        assert sets, "_error_route_pending is never set — the guard is dead"
        for node in sets:
            enclosing = [n for n in ast.walk(fn) if isinstance(n, ast.If)
                         and n.lineno <= node.lineno <= (n.end_lineno or 0)
                         and "CRITICAL_SEVERITY_THRESHOLD" in ast.unparse(n.test)]
            assert not enclosing, (
                f"_error_route_pending is set at line {node.lineno}, inside a "
                f"severity branch. Criticals will not get the transport-dead "
                f"guard, and a dead transport can stop a critical blocking "
                f"convergence."
            )

    def test_the_flag_is_still_consumed_after_routing(self):
        body = ast.unparse(_fn("_apply_routing"))
        assert 'e.pop(\'_error_route_pending\'' in body or \
               'e.pop("_error_route_pending"' in body, \
               "the guard is set but never read"


class TestTheConsequenceIsStillReal:
    def test_irreducible_escalation_still_excuses_a_critical_from_the_count(self):
        """Pins WHY the guard matters. If this ever stops being true the guard is
        less critical — but while it holds, a false exhaustion is a false
        convergence."""
        body = ast.unparse(_fn("unverified_critical_count"))
        assert "irreducible_escalation" in body

    def test_a_critical_marked_irreducible_is_not_counted(self):
        reg = R.FindingRegistry()
        f = R.Finding(finding_id="X_F1", model_id="X", round_idx=0,
                      flaw_class="code_behavioral", severity=0.9,
                      abstraction_index=0.5, description="critical thing")
        cid = reg.register(f, "X")
        reg.entries[cid]["status"] = "UNCONFIRMED"
        reg.entries[cid]["severity"] = 0.9
        before = reg.unverified_critical_count()
        reg.entries[cid]["irreducible_escalation"] = True
        after = reg.unverified_critical_count()
        assert before == 1 and after == 0, (
            f"expected the irreducible flag to remove it from the blocking "
            f"count (1 -> 0), got {before} -> {after}"
        )
