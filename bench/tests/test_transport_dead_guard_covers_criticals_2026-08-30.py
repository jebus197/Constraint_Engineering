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
import reference_runner_v3 as R

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
    def test_the_two_blocker_readers_cannot_disagree(self):
        """Pins WHY the guard matters, and does it where the sibling below cannot.

        ★ REPLACED A SOURCE-TEXT ASSERTION, 2026-10-28. It read
        `assert "irreducible_escalation" in ast.unparse(_fn(
        "unverified_critical_count"))`. That method was refactored on 2026-10-17
        into a thin wrapper over `blocking_entry_ids`, so the literal moved and
        this went red ON A REFACTOR THAT MADE THE CODE BETTER -- the failure mode
        `execute-do-not-grep` names: a text assertion cannot follow a door that
        moves, and it punishes the fix.

        A STRAIGHT CONVERSION WOULD HAVE DUPLICATED THE SIBLING. The test below
        already measures the discrimination (1 -> 0 when the flag is set), so
        re-asserting it here would add a second copy of one check rather than
        cover what was lost. What the text assertion uniquely pinned was WHERE
        the door lives, and the refactor's own claim is that it now lives in ONE
        place that BOTH callers read: "blocking_entry_ids now holds the doors
        ONCE and both callers read it, so the claim in the reader's docstring
        that the 2 cannot drift is finally true of the blocker half as well."

        THAT CLAIM IS WHAT THIS MEASURES, and it is the one with a measured
        failure behind it: before the refactor the 2 readers disagreed, with
        `commissioning_arm3_contrast_20260922T025824Z` returning 4 blockers from
        the counter and 11 from the reader -- a numerator larger than its own
        denominator. So both are asked about the same registry, with and without
        the marking, and required to agree.
        """
        reg = R.FindingRegistry()
        f = R.Finding(finding_id="Z_F1", model_id="Z", round_idx=0,
                      flaw_class="code_behavioral", severity=0.9,
                      abstraction_index=0.5, description="critical thing")
        cid = reg.register(f, "Z")
        reg.entries[cid]["status"] = "UNCONFIRMED"
        reg.entries[cid]["severity"] = 0.9

        def _both():
            count = reg.unverified_critical_count()
            ids = set(reg.blocking_entry_ids())
            return count, ids

        count_before, ids_before = _both()
        assert count_before == len(ids_before) == 1, (
            f"the 2 readers disagree before the marking: counter "
            f"{count_before}, id set {sorted(ids_before)}. A numerator larger "
            f"than its own denominator is what motivated the 2026-10-17 repair")

        reg.entries[cid]["irreducible_escalation"] = True
        count_after, ids_after = _both()
        assert count_after == len(ids_after) == 0, (
            f"the 2 readers disagree after the marking: counter {count_after}, "
            f"id set {sorted(ids_after)}. The door must be held in one place")

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
