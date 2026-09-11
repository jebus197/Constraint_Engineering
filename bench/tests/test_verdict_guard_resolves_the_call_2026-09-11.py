"""Task A17: the verdict-tuple guard matched NAMES where it needed to resolve calls.

WHAT HAPPENED, 2026-09-10 16:55 BST. `TestVerdictTuplesAreNeverTestedForTruth`
collects the names of every function anywhere in the repository that returns a
`(bool, message)` tuple, then flags any binding of one of those NAMES that is
later tested for truth. It never resolved which function was actually called.

A new script defined `scan()` returning a 3-tuple. `scripts/supersession_check.py`
was then flagged at line 149 for `if not findings:` -- a truth test that is
entirely CORRECT, because that file's own `scan()` returns a LIST. A green suite
went red for a file nobody had touched, and the repair applied at the time was to
RENAME the new function, which removes the collision without addressing the
cause.

THE GUARD IS RIGHT ABOUT THE DEFECT CLASS AND WAS WRONG ABOUT THAT INSTANCE, and
the two must be kept apart: a false positive here is not a harmless annoyance,
because "the suite went red for a file nobody touched" is how a guard's output
starts being ignored -- this project's own sentence about 3 different alarms.

THE FIX IS PYTHON'S OWN SCOPING RULE, not a heuristic. A file that DEFINES a name
shadows every other definition of it, so the local definition decides. A name the
file defines for itself, whose local definition demonstrably does not return a
tuple of 2 or more elements, is removed from the flagged set FOR THAT FILE ONLY.

WHAT IT DELIBERATELY DOES NOT DO. It does not resolve IMPORTS. A name imported
from a module that returns a tuple is still flagged -- that is the guard doing
its job, and the defect it was built for (`scripts/cdsfl_seal_logs.py` binding a
verdict whole and testing it) is an imported call.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = ROOT / "bench" / "tests" / "test_operational_scripts.py"


@pytest.fixture(scope="module")
def g():
    spec = importlib.util.spec_from_file_location("guardmod", GUARD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["guardmod"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:                      # the module may guard its own import
        pass
    return m


TUPLE_SRC = ("def scan(x):\n    return True, 'msg'\n\n"
             "def use():\n    findings = scan(1)\n    if not findings:\n        pass\n")
LIST_SRC = ("def scan(x):\n    return [1, 2]\n\n"
            "def use():\n    findings = scan(1)\n    if not findings:\n        pass\n")


class TestTheLocalDefinitionDecides:
    def test_a_file_whose_own_function_returns_a_tuple_is_still_flagged(self, g):
        """THE GUARD MUST NOT BE WEAKENED. If this stops firing, A17's fix has
        turned a false positive into a false negative, which is worse."""
        hits = g._truthiness_violations(TUPLE_SRC, "tuple.py", {"scan"})
        assert len(hits) == 1, hits
        assert "findings" in hits[0] and "scan()" in hits[0]

    def test_a_file_whose_own_function_returns_a_list_is_not(self, g):
        assert g._truthiness_violations(LIST_SRC, "list.py", {"scan"}) == []

    def test_the_reported_instance_is_no_longer_flagged(self, g):
        """The exact file and the exact collision, reproduced."""
        src = (ROOT / "scripts" / "supersession_check.py").read_text(encoding="utf-8")
        assert g._truthiness_violations(
            src, "scripts/supersession_check.py", {"scan"}) == []

    def test_the_reported_instance_really_does_define_scan_returning_a_list(self):
        """ANTI-VACUITY. If supersession_check stopped defining `scan`, the test
        above would pass because the name never appears, not because the fix
        works."""
        import ast
        src = (ROOT / "scripts" / "supersession_check.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        names = {n.name for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert "scan" in names, (
            "supersession_check.py no longer defines scan(); re-derive A17's "
            "instance before trusting this file")


class TestImportsAreStillFlagged:
    def test_a_name_that_is_imported_not_defined_stays_in_the_set(self, g):
        """The boundary, stated and tested. Shadowing applies to LOCAL
        definitions only; an imported verdict function is still the defect the
        guard was built for."""
        src = ("from bench.verification_chain import verify_chain\n\n"
               "def use():\n    ok = verify_chain()\n    if ok:\n        pass\n")
        hits = g._truthiness_violations(src, "importer.py", {"verify_chain"})
        assert len(hits) == 1, hits

    def test_the_shadow_set_is_empty_for_a_file_defining_nothing(self, g):
        assert g._locally_shadowed("x = 1\n", {"scan", "verify_chain"}) == set()


class TestTheLiveSuiteIsUnaffected:
    def test_the_whole_guard_still_passes(self, g):
        """The guard's own production run, over the real scripts. A fix that
        silenced it everywhere would pass every unit case above."""
        names = g._tuple_returning_function_names(
            [p.read_text(encoding="utf-8") for p in g.SCRIPT_PATHS])
        assert "verify_chain" in names or len(names) > 5, (
            f"the collector has stopped seeing tuple-returning functions: "
            f"{sorted(names)[:10]}")
