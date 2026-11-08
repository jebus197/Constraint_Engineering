"""Both convergence gates must agree before a run terminates. B76.

HIS RULING, 2026-11-08: *"Require both gates to agree. stm"*

THE DEFECT IS OBSERVED, NOT HYPOTHESISED, and the run's own log is the
evidence. On the 2026-11-02 rerun
(`bench/logs/study_run1b_rerun_20261102T033919Z_20261102T033920Z/console.log`)
the 2 enabled criteria disagreed and the MORE PERMISSIVE one stopped the run:

    γ-alt: hardened not met: γ_crit=0.808 (≥0.41? True; sustained=True;
           loo_ok=True) AND zero_crit_ok
    STATE_CONVERGED at round 5 (3 consecutive passes): All conditions met:
           open_ch=0 (stable), novel=0, contested=0, gamma=0.487

The hardened gate said NOT MET and the state gate terminated the run anyway,
because the composition was an OR.

WHY AN OR IS WRONG RATHER THAN MERELY DIFFERENT. An OR makes a pair of criteria
strictly WEAKER than either member alone, so adding a second criterion made
termination easier instead of harder. The project's standing directive states
the agreed design as a two-sided gate in which convergence requires BOTH sides
of the same diminishing-returns coin, neither alone.

WHY THIS FILE EXECUTES A PURE FUNCTION. The live decision sits inside a 20,000
line loop that needs a full experiment to exercise. A guard pointed at it could
only assert on source text, and a text assertion cannot detect a producer and a
consumer that disagree -- the shape that has produced 4 confirmed defects in
this project. So the composition is extracted as `both_gates_agree` and all 4
combinations are CALLED here.

WHAT IS DELIBERATELY NOT CLAIMED: that convergence is still reachable under this
rule. It is strictly harder, and the 2026-11-02 run would not have converged at
round 5. The directive's own position is that where convergence seems out of
reach the cause is MECHANICAL and is to be hunted in the mechanics -- never by
loosening the gate, which is the instinct it names as vindicated-wrong every
time.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench/reference_runner_v3.py"


@pytest.fixture(scope="module")
def agree():
    """`both_gates_agree`, lifted WITHOUT importing the 20,000-line runner.

    Importing the module costs seconds and pulls in the whole harness; the
    function is pure and self-contained, so its own source is compiled alone.
    That is still EXECUTION -- the function runs -- rather than a text match.
    """
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "both_gates_agree":
            seg = ast.get_source_segment(src, node)
            ns: dict = {}
            exec(compile(seg, "<both_gates_agree>", "exec"), ns)   # noqa: S102
            return ns["both_gates_agree"]
    pytest.fail("bench/reference_runner_v3.py defines no both_gates_agree, so "
                "his ruling produced nothing")


def test_both_true_converges(agree):
    ok, why = agree(True, "state ok", True, "gamma ok")
    assert ok is True, why
    assert "BOTH GATES AGREE" in why
    assert "state ok" in why and "gamma ok" in why, (
        "the reason must carry both sides, or a researcher cannot retrace it")


def test_the_state_gate_alone_no_longer_terminates(agree):
    """THE OBSERVED CASE. This is the exact 2026-11-02 shape."""
    ok, why = agree(True, "STATE_CONVERGED at round 5", False,
                    "hardened not met: zero_crit_ok False")
    assert ok is False, (
        "the state gate alone still terminates the run, which is the defect "
        "his ruling was given against")
    assert "DISSENTS" in why and "gamma gate DISSENTS" in why, (
        "the reason does not name which side dissented")


def test_the_gamma_gate_alone_no_longer_terminates(agree):
    """THE SYMMETRIC CASE. `agree` means agree, in both directions.

    The old OR promoted this one too, so leaving it would have kept half the
    defect while reporting the fix as done.
    """
    ok, why = agree(False, "gate passed but not 3 consecutive", True,
                    "gamma_critical 0.61 >= 0.30 and zero-crit streak 3")
    assert ok is False
    assert "state gate DISSENTS" in why


def test_neither_does_not_converge(agree):
    ok, why = agree(False, "open_ch=4", False, "zero_crit_ok False")
    assert ok is False
    assert "NEITHER" in why


def test_it_is_an_and_and_not_an_or(agree):
    """ANTI-VACUITY over the whole truth table.

    A function that returned False for everything would pass 3 of the 4 cases
    above. Exactly 1 of the 4 inputs may converge, and it must be the
    both-true one -- which is what distinguishes an AND from an OR and from a
    constant.
    """
    table = {(s, g): agree(s, "s", g, "g")[0]
             for s in (True, False) for g in (True, False)}
    assert table == {(True, True): True, (True, False): False,
                     (False, True): False, (False, False): False}, table


def test_the_live_site_calls_it(agree):
    """AN ADDITION NOTHING REACHES IS NOT ADDITIVE.

    The function could be correct and unused, which is the half of the additive
    standard this project has confirmed 11 times.
    """
    src = RUNNER.read_text(encoding="utf-8")
    calls = [l for l in src.splitlines()
             if "both_gates_agree(" in l and "def " not in l]
    assert calls, "both_gates_agree is defined and never called"
    assert any("converged, conv_reason = both_gates_agree(" in l
               for l in src.splitlines()), (
        "the live loop does not assign its own convergence verdict from "
        "both_gates_agree, so the composition is still whatever it was")


def test_the_old_or_is_gone(agree):
    """The promotion that made the pair weaker than either member.

    ★ COMMENTS ARE EXCLUDED, AND THAT IS NOT A CONVENIENCE. The first version
    of this test searched the WHOLE file and failed on its own fix: the comment
    block inside `both_gates_agree` QUOTES the OR it removed, so a detector
    looking for the pattern found the explanation of the pattern. A scar reads
    as a wound -- the 7th instance of that exact shape in this project on
    2026-11-08 alone.

    The pattern is also ASSEMBLED FROM PARTS below, so this test file cannot
    match itself either, which is the same trap one level up.
    """
    needle = "if gamma_alt_" + "converged and not " + "converged:"
    live = [l for l in RUNNER.read_text(encoding="utf-8").splitlines()
            if needle in l and not l.lstrip().startswith("#")]
    assert not live, (
        f"the OR that let either gate terminate the run on its own is still "
        f"live code: {live[:2]}")


def test_that_exclusion_cannot_hide_a_real_or(agree):
    """ANTI-VACUITY for the comment exclusion.

    Excluding comments is exactly how a text check goes blind, so the filter is
    put a synthetic line that IS code and must be caught, and a synthetic line
    that is a comment and must not be.
    """
    needle = "if gamma_alt_" + "converged and not " + "converged:"
    code = f"        {needle}"
    comment = f"        # {needle}"
    kept = [l for l in (code, comment) if needle in l
            and not l.lstrip().startswith("#")]
    assert kept == [code], (
        f"the comment filter is wrong: it kept {kept} where it should keep "
        f"only the code line")
