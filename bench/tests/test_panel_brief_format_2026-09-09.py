"""The panel brief format, and the refusal that makes it binding.

Written 2026-09-09 on the founder's ruling that panel review must be "full CDSFL
panel review format (so not just some simple open ended prompt)" and that the
format become the standard for the full 6-model paid panel.

Every test CALLS the validator or RUNS the dispatcher; none asserts on source
text. The dispatcher tests are what make this more than a document: a template
nothing enforces is an addition nothing reaches.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"
DISPATCHER = REPO / "bench" / "confer_maths_panel_2026-09-05.py"

_spec = importlib.util.spec_from_file_location("pbv_under_test",
                                               REPO / "scripts" / "panel_brief_validate.py")
pbv = importlib.util.module_from_spec(_spec)
sys.modules["pbv_under_test"] = pbv
_spec.loader.exec_module(pbv)

GOOD = """# Does the intake parser drop falsifier blocks?

The artefact under review is `bench/runner_core.py` and its companion
`bench/reference_runner_v3.py`.

## Use the harness
You must RUN the parser against the archived replies and report what you executed.
Use S_k and the severity model to say whether a recovered block would have changed
the gate's verdict; gamma should tell you whether the run was converging at all.

## Produce a fix and test it
A finding without a fix is half an answer. Write a runnable falsifier, EXECUTE it,
and report the command and its output.

## What would refute you
State what evidence would overturn your own conclusion before you conclude.

## Output
Return: verdict, reasoning, the falsifier and its executed result, and your
strongest disagreement with this brief's framing.

## Termination
Stop when a further pass produces no new above-threshold findings, and say how
many passes you ran. Diminishing returns is the criterion.
"""


def test_the_template_passes_its_own_validator():
    """The exemplar must satisfy the rule it defines, or the rule is unmeetable."""
    assert pbv.validate(TEMPLATE.read_text()) == []


def test_a_compliant_brief_passes():
    assert pbv.validate(GOOD) == [], pbv.validate(GOOD)


def test_a_simple_open_ended_prompt_is_refused():
    """The exact thing the founder's ruling names."""
    problems = pbv.validate("# A question\n\nWhat do you think about the runner?\n")
    assert len(problems) >= 6, problems


@pytest.mark.parametrize("drop,expect", [
    ("## Termination\nStop when a further pass produces no new above-threshold findings, and say how\nmany passes you ran. Diminishing returns is the criterion.\n", "termination"),
    ("Return: verdict, reasoning, the falsifier and its executed result, and your\nstrongest disagreement with this brief's framing.\n", "output"),
    ("Use S_k and the severity model to say whether a recovered block would have changed\nthe gate's verdict; gamma should tell you whether the run was converging at all.\n", "mathematical instrument"),
])
def test_removing_a_required_section_is_detected(drop, expect):
    """Each check must fail in the direction it exists to check, one at a time."""
    mutated = GOOD.replace(drop, "")
    assert mutated != GOOD, "the fixture text must actually change"
    problems = pbv.validate(mutated)
    assert any(expect in p for p in problems), (
        f"removing that section should be caught; got {problems}")


def test_the_validator_is_not_merely_hostile():
    """A rule that rejects everything tells you nothing. Measured across the
    archive: failures ranged 1 to 7 of 8 per brief, so it discriminates."""
    briefs = sorted((REPO / "bench" / "logs").rglob("BRIEF.md"))
    if not briefs:
        pytest.skip("no archived briefs on this machine")
    counts = [len(pbv.validate(b.read_text(errors="replace"))) for b in briefs]
    assert min(counts) < max(counts), "the validator must separate briefs, not reject uniformly"
    assert min(counts) <= 2, f"the best archived brief fails {min(counts)} checks; if that is high the rule is too strict"


# --- The refusal, executed. --------------------------------------------------

def _dispatch(tmp_path, brief_text, env_extra=None):
    import os
    name = "_pytest_brief_" + tmp_path.name[-8:]
    d = REPO / "bench" / "logs" / name
    d.mkdir(parents=True, exist_ok=True)
    try:
        (d / "BRIEF.md").write_text(brief_text)
        env = dict(os.environ)
        env["PANEL_ONLY"] = "__none__"          # never reach a real seat
        if env_extra:
            env.update(env_extra)
        return subprocess.run([sys.executable, str(DISPATCHER), name],
                              capture_output=True, text=True, timeout=180, env=env)
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def test_the_dispatcher_REFUSES_a_bad_brief_before_paying_a_seat(tmp_path):
    r = _dispatch(tmp_path, "# q\n\nWhat do you think?\n")
    assert r.returncode == 2, f"must refuse with exit 2; got {r.returncode}\n{r.stderr[:400]}"
    assert "REFUSED" in r.stderr
    assert "paid" in r.stderr, "the refusal should say why it matters"


def test_the_bypass_is_deliberate_and_announces_itself(tmp_path):
    r = _dispatch(tmp_path, "# q\n\nWhat do you think?\n",
                  env_extra={"PANEL_BRIEF_UNCHECKED": "1"})
    assert r.returncode != 2 or "dispatching anyway" in r.stderr, (
        "the documented bypass must work and must say it was used")
