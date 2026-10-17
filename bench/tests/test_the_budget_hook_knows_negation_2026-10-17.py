"""The memory-budget hook must tell an instruction from a prohibition.

HIS RULING, 2026-10-17: "Make the guard aware of negation as you have suggested."

THE DEFECT, OBSERVED TWICE IN ONE TURN. The hook's predicate was a bare substring
search over the whole prompt, so a delegated brief whose text FORBADE the heavy
verification tooling matched on the very words expressing the prohibition. The
first refusal fired on an explicit "do NOT run pytest"; the second, after that
word was removed, fired on the phrase "cost more than a full board run" inside
the same prohibition.

WHY IT MATTERED MORE THAN THE INCONVENIENCE. An author who cannot state the limit
in a brief has 2 options: drop the limit, or rephrase around the matcher.
Dropping it is actively dangerous, because a delegated agent with no stated limit
is MORE likely to invoke the tooling. The false positive therefore selected for
exactly the behaviour the guard exists to prevent.

EVERY ASSERTION HERE RUNS THE HOOK OR CALLS ITS PREDICATE. None inspects source
text, per `execute-do-not-grep`: a source-text assertion would only prove the
module describes itself consistently, and this hook's defect was that its
description and its behaviour agreed perfectly while both were wrong.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"


@pytest.fixture(scope="module")
def mod():
    if not HOOK.is_file():
        pytest.skip(f"hook not present at {HOOK}")
    spec = importlib.util.spec_from_file_location("lrb", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(brief: str, tool: str = "Workflow") -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": tool, "tool_input": {"script": brief}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, timeout=60)


#: (text, should_be_treated_as_an_instruction, why)
CASES = [
    ("run pytest across bench/tests in each agent", True,
     "an explicit instruction must still be caught"),
    ("python3 -m pytest bench/tests -q", True,
     "a bare command form is imperative by itself"),
    ("each agent should invoke the full board", True,
     "a different wording of the same instruction"),
    ("do NOT run pytest or any test runner", False,
     "HIS SHAPE: the first false positive of 2026-10-17"),
    ("never invoke pytest in delegated work", False,
     "a prohibition with a different negator"),
    ("delegated verification runs cost more than a full board run, so avoid them",
     False, "THE SECOND false positive, which fired on 'full board'"),
    ("Do not invoke the suite; read files only", False,
     "a prohibition terminated by a semicolon"),
    ("use file reading and text search only, rather than running the suite", False,
     "the rather-than form, where the negation FOLLOWS the mention"),
    ("the suite has 606 tests", False,
     "a factual mention commands nothing, and refusing on ambiguity is what "
     "produced the false positives"),
    ("await parallel(xs.map(x=>()=>agent('pytest')))", True,
     "A COMMAND NAME NEEDS NO VERB. `pytest` is an executable, so this "
     "instructs it exactly as typing it at a shell would. The contract test of "
     "2026-10-11 is right about this and a first version of the polarity fix "
     "let it through by demanding a verb of every mention."),
    ("do not put pytest in the agent prompt", False,
     "the same command name, negated, must still be allowed"),
    ("read the full board results from the cached file", False,
     "a noun phrase governed by `read`, not by a verb of execution"),
]


@pytest.mark.parametrize("text,want,why", CASES)
def test_the_predicate_reads_polarity(mod, text, want, why):
    got = mod._instructs_heavy_verification(text.lower())
    assert got is want, f"{why}: {text!r} -> {got}, wanted {want}"


def test_a_prohibiting_brief_is_not_refused_end_to_end():
    """The 2 briefs that were actually refused on 2026-10-17, replayed."""
    v1 = ("OPERATING LIMITS. Work read-only. Do NOT run pytest or any test runner "
          "under any circumstances. Use parallel() over 5 buckets.")
    v2 = ("Never launch any automated verification tooling; delegated verification "
          "runs were measured as costing more than a full board run on 2026-10-11. "
          "pipeline() over the buckets.")
    for name, brief in (("v1", v1), ("v2", v2)):
        r = _run(brief)
        assert r.returncode == 0, (
            f"brief {name} FORBIDS the tooling and must not be refused; "
            f"exit {r.returncode}, stderr {r.stderr[-300:]}")


def test_a_genuine_instruction_is_still_refused_end_to_end():
    """Anti-vacuity: teaching the guard about negation must not disarm it."""
    r = _run("Each agent should run pytest bench/tests -q and report failures. "
             "parallel() over 5 agents.")
    assert r.returncode == 2, (
        f"a genuine delegated pytest instruction must still be refused; "
        f"exit {r.returncode}")
    assert "cached" in r.stderr.lower(), "the refusal must still name the remedy"


def test_a_negation_far_away_does_not_license_an_instruction(mod):
    """The window is short ON PURPOSE. A negation 200 characters earlier does not
    govern the sentence in hand, and treating it as though it did would let any
    brief smuggle an instruction past the guard by opening with a disclaimer."""
    text = ("do not worry about cost. " + ("filler text. " * 20) +
            "each agent should run pytest over the whole suite")
    assert mod._instructs_heavy_verification(text.lower()) is True, (
        "a distant negation must not suppress a nearby imperative")


def test_a_broken_payload_still_never_jams_the_session():
    r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (
        "a guard that fells the session on malformed input is worse than no guard")
