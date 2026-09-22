#!/usr/bin/env python3
"""FALSIFIER: a fix that breaks a WORKING listing must not be ADMITTED.

Raises AssertionError / prints FALSIFIED iff the defect is present.
Exits cleanly iff the claim is false. Imports the REAL module.

THE CLAIM. `_gateable_source` concatenates every fenced listing into one blob,
so `_baseline_code_is_parseable` abstains for the WHOLE blob as soon as ANY
listing was already broken -- and a fix that then breaks a DIFFERENT, working
listing is admitted at A = 1.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import bench.reference_runner_v3 as R

PATH = "notes/design.md"
def doc(a, b):
    return f"# n\n\n```python\n{a}```\n\nprose\n\n```python\n{b}```\n"

GOOD1, BAD1 = "def good():\n    return 1\n", "def good(:\n    return 1\n"
GOOD2, BAD2 = "def two():\n    return 2\n", "def bad(:\n    return 2\n"

BASE   = doc(GOOD1, BAD2)   # listing 1 parses; listing 2 already broken
BROKEN = doc(BAD1,  BAD2)   # the fix ALSO breaks listing 1
CLEAN  = doc(GOOD1, GOOD2)  # both listings parse


def test_fix_that_breaks_a_working_listing_is_convicted():
    g1 = R._run_hard_gate_ast(BROKEN, PATH, original_source=BASE)
    g2 = R._run_hard_gate_compile(BROKEN, PATH, original_source=BASE)
    # STRENGTHENED 2026-09-22 (CC1), and the weakness was in BOTH seats' work:
    # this asserted the PRODUCT g1*g2, which is 0 whenever EITHER gate convicts.
    # Measured by mutation -- deleting the per-hunk call from `_run_hard_gate_ast`
    # alone, or from `_run_hard_gate_compile` alone, left this test and fable's
    # falsifier BOTH green. Half the fix was revertable in silence. Each gate
    # carries its own per-hunk call, so each gate needs its own assertion.
    for name, g in (("_run_hard_gate_ast", g1), ("_run_hard_gate_compile", g2)):
        if g[0] != 0:
            print("FALSIFIED")
            raise AssertionError(
                f"{name} returned {g[0]}: a fix that broke listing 1 (which "
                f"parsed before) was ADMITTED because listing 2 was already "
                f"broken.\n  {name}={g}")


def test_no_conviction_is_rescinded_strictly_additive():
    """The guard may only ever make the gate STRICTER."""
    # already-broken listing untouched by the fix -> still abstain (unchanged)
    g1 = R._run_hard_gate_ast(BASE, PATH, original_source=BASE)
    g2 = R._run_hard_gate_compile(BASE, PATH, original_source=BASE)
    assert g1[0] * g2[0] == 1, f"abstention regressed: {g1} {g2}"
    # clean baseline, fix breaks listing 2 -> convicted, as before
    g1 = R._run_hard_gate_ast(doc(GOOD1, BAD2), PATH, original_source=CLEAN)
    assert g1[0] == 0, f"pre-existing conviction lost: {g1}"
    # a fix that DELETES a fence cannot be paired -> blob logic, unchanged
    g1 = R._run_hard_gate_ast("# n\n\n```python\n" + BAD1 + "```\n", PATH,
                              original_source=BASE)
    assert g1[0] == 1, f"unpairable fix wrongly convicted: {g1}"
    # a Python target is unaffected
    assert R._run_hard_gate_ast("x = 1\n", "m.py", original_source="x = 1\n")[0] == 1


if __name__ == "__main__":
    test_fix_that_breaks_a_working_listing_is_convicted()
    test_no_conviction_is_rescinded_strictly_additive()
    print("clean: defect not demonstrated")
