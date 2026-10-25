"""A fan-out must name its hypothesis, its falsifier, and why 1 context will not do.

HIS QUESTION, 2026-10-25: *"But can't we somehow direct you to use some of that
reasoning depth prior to using these facilities also? What do you suggest?"*

THE ANSWER UNDER TEST. `hooks/local_resource_budget.py` already runs PreToolUse on
`Agent|Task|Workflow`. It now also refuses a brief that does not carry 3 literal
markers. These tests drive the hook as a SUBPROCESS and read its real exit code,
because that is the only thing the PreToolUse event consults -- a test that read
the hook's source would prove only that the hook describes itself consistently
(`execute-do-not-grep`).

WHY LITERAL MARKERS AND NOT A JUDGEMENT. A similarity-based version of this exact
check was written on 2026-10-24 for note asks and failed in BOTH directions: 5 of
5 false positives, then it cleared the single true case. It was replaced with an
exact id rule. Same discipline here.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "local_resource_budget.py"
DEPLOYED = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"

FULL = ("HYPOTHESIS: the sort mis-orders DEPRECATED rows. "
        "FALSIFIED BY: a blind reference sort over the same 433 rows agreeing. "
        "WHY NOT ONE CONTEXT: the reference needs an author blind to mine.")

#: WHY `FULL` CARRIES NO INCIDENTAL NEGATION. The first version of this brief said
#: the reference must be written "without seeing mine", and the word "without" is in
#: `_NEGATION`. It landed inside the guard's 140-character window and made a brief
#: that DID instruct pytest read as a prohibition of it.
#:
#: That looked like a regression and was measured before being reported. Across the
#: 115 real fan-out briefs recoverable from the session transcripts, 59 mention a
#: heavy verification run; of those, 14 are suppressed by a DELIBERATE prohibition
#: ("do not", "never"), which is the documented and correct behaviour, and **0 by an
#: incidental one**. The guard is sound; the synthetic brief was not. Recorded here
#: because the first figure computed was 15 of 59 (0.2542), which would have been an
#: alarming defect rate reported for a guard with no defect -- the failure mode
#: `feedback_control_proves_discrimination_2026-10-17` names.


def drive(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload), capture_output=True,
                          text=True, timeout=120)


@pytest.mark.parametrize("tool", ["Agent", "Task", "Workflow"])
def test_a_bare_brief_is_refused(tool):
    """No markers at all -> refused, for every gated tool."""
    r = drive({"tool_name": tool, "tool_input": {"prompt": "Go and check the store."}})
    assert r.returncode == 2, f"{tool} was ALLOWED without any markers: {r.stdout[:200]}"
    assert "DEPTH BEFORE BREADTH" in r.stderr
    assert "missing 3 of 3" in r.stderr


def test_a_complete_brief_is_allowed():
    """All 3 markers -> allowed, and the budget context is still printed."""
    r = drive({"tool_name": "Agent", "tool_input": {"prompt": FULL}})
    assert r.returncode == 0, f"a complete brief was REFUSED: {r.stderr[:400]}"
    assert "local-budget" in r.stdout, "the budget advice stopped being printed"


@pytest.mark.parametrize("drop,expect", [
    ("HYPOTHESIS:", "HYPOTHESIS:"),
    ("FALSIFIED BY:", "FALSIFIED BY:"),
    ("WHY NOT ONE CONTEXT:", "WHY NOT ONE CONTEXT:"),
])
def test_each_marker_is_individually_load_bearing(drop, expect):
    """Removing ANY one marker must refuse AND name the one removed.

    3 mutations. A gate that only notices a wholly empty brief would pass the
    bare-brief test above while being blind to a partial one.
    """
    brief = FULL.replace(drop, "NOTE:")
    r = drive({"tool_name": "Agent", "tool_input": {"prompt": brief}})
    assert r.returncode == 2, f"dropping {drop!r} was ALLOWED"
    assert "missing 1 of 3" in r.stderr, r.stderr[:300]
    assert expect in r.stderr, f"refusal did not name {expect!r}"


def test_markers_are_case_insensitive():
    """A lowercase brief is still a brief; the check must not police style."""
    r = drive({"tool_name": "Agent", "tool_input": {"prompt": FULL.lower()}})
    assert r.returncode == 0, f"lowercase markers REFUSED: {r.stderr[:300]}"


def test_an_ungated_tool_is_untouched():
    """`additive-standard`: the addition must not widen beyond its matcher."""
    for tool in ("Read", "Bash", "Edit", "Grep"):
        r = drive({"tool_name": tool, "tool_input": {"file_path": "/x"}})
        assert r.returncode == 0, f"{tool} was refused by a fan-out gate"


def test_the_pytest_refusal_still_fires_and_takes_precedence():
    """The pre-existing guard must survive the addition.

    A brief that carries all 3 markers AND instructs pytest is still refused, on
    the resource ground. 263 delegated pytest invocations cost 4557.8 s against
    3998.65 s for 1 full board.
    """
    r = drive({"tool_name": "Agent",
               "tool_input": {"prompt": FULL + " Now run the full pytest suite."}})
    # FULL deliberately carries no incidental negation; see its note above.
    assert r.returncode == 2
    assert "instructs pytest" in r.stderr, (
        "the depth gate masked the pytest refusal: " + r.stderr[:300])


def test_markers_found_anywhere_in_the_payload():
    """A Workflow states them in `script`, an Agent in `prompt`; both must count."""
    r = drive({"tool_name": "Workflow", "tool_input": {"script": f"// {FULL}\nagent('x')"}})
    assert r.returncode == 0, f"Workflow with markers in script REFUSED: {r.stderr[:300]}"


def test_malformed_input_does_not_block_work():
    """A broken payload must not refuse a legitimate call."""
    r = subprocess.run([sys.executable, str(HOOK)], input="not json",
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0


def test_the_deployed_hook_is_the_same_inode():
    """2 copies that drift are a gate that guards nothing."""
    if not DEPLOYED.exists():
        pytest.skip("not deployed on this machine")
    assert DEPLOYED.stat().st_ino == HOOK.stat().st_ino, (
        f"deployed hook has DRIFTED; re-link with ln -f {HOOK} {DEPLOYED}")


def test_it_is_still_registered_on_the_fanout_tools():
    settings = pathlib.Path.home() / ".claude" / "settings.json"
    if not settings.is_file():
        pytest.skip("no settings.json")
    cfg = json.loads(settings.read_text(encoding="utf-8"))
    pre = cfg.get("hooks", {}).get("PreToolUse", [])
    hit = [e for e in pre
           if any("local_resource_budget" in h.get("command", "")
                  for h in e.get("hooks", []))]
    assert hit, "the budget hook is not registered on PreToolUse"
    m = hit[0].get("matcher", "")
    for tool in ("Agent", "Task", "Workflow"):
        assert tool in m, f"matcher {m!r} does not cover {tool}"

def test_a_deliberate_prohibition_of_pytest_is_still_writable():
    """The guard must stay silent on a brief that FORBIDS the tooling.

    This is its documented contract and it is load-bearing: the standing rule is
    that delegated work never runs pytest, so 14 of the 59 real briefs that
    mention it do so to forbid it. A guard that refused those would make the
    correct brief unwritable.
    """
    brief = FULL + " Do not run pytest or the full suite; consult the cached board."
    r = drive({"tool_name": "Agent", "tool_input": {"prompt": brief}})
    assert r.returncode == 0, (
        "a brief FORBIDDING pytest was refused by the pytest guard: "
        + r.stderr[:300])


def test_an_incidental_negation_near_a_pytest_instruction_is_known_behaviour():
    """PINS the one synthetic case that fails, so a future change is visible.

    `without` inside the 140-character window suppresses the refusal. Measured as
    0 of 59 on the real corpus, so it is not fixed -- narrowing the window risks
    breaking the 14 correct prohibitions above, which is the larger harm. If this
    test ever starts FAILING, the window logic changed and the 14 need rechecking.
    """
    brief = ("HYPOTHESIS: a. FALSIFIED BY: b. WHY NOT ONE CONTEXT: the reference "
             "needs an author writing without sight of mine. Now run the full "
             "pytest suite.")
    r = drive({"tool_name": "Agent", "tool_input": {"prompt": brief}})
    assert r.returncode == 0, (
        "the incidental-negation window changed; recheck the 14 deliberate "
        "prohibitions measured on 2026-10-25 before accepting this")
