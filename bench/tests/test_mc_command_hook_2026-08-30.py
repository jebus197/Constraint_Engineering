"""The MC-command hook: obligations arrive in context, mechanically, every time.

WHY A HOOK AND NOT ANOTHER MEMORY NOTE. `mc_commands_nonoptional.md` has said
since 20 April 2026 that MC commands are directives to be executed in full, and
instructed that the rule be marked in every memory and recovery resource. It was
marked, in six places, and recalled correctly whenever asked.

It still failed. Measured from the session transcript on 2026-08-30: `sy` issued
5 times; ONE genuine STEM-tool invocation across 223 tool calls on the night of
2026-08-29/30 (0.45%); the 21 April two-tool cross-verification rule satisfied
ZERO times. A headline given to the founder was falsified the next morning by one
statsmodels call that should have been made at the time.

The failure is not recall. An MC reads as a MODE ("be rigorous") rather than a
required ARTEFACT ("emit a tool call"), and under load the mode is satisfied in
prose while the artefact never appears. This project's own rule covers the case:
falsification must be STRUCTURALLY ENFORCED, not hoped for
(`feedback_falsification_gate.md`). The hook is the structural version.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "mc_commands.py"


def _load():
    spec = importlib.util.spec_from_file_location("_mc_hook", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fires(msg: str):
    r = subprocess.run([sys.executable, str(HOOK)],
                       input=json.dumps({"prompt": msg}), capture_output=True, text=True)
    return r.stdout.strip(), r.returncode


def test_the_hook_is_versioned_in_the_repo():
    assert HOOK.is_file(), "the hook exists only as a dotfile and is not recoverable"


@pytest.mark.parametrize("msg", [
    "why?\n\nrg, a, f. sy, d, t",                 # the founder's actual message, typo included
    "did it go well?\n\na, d",
    "check\n\nrg, sq, a, sy, sth, p, d, t, e",    # 9 -- the documented example is 8
    "rg, a, sy\n\nthen tell me\nabout x\nand y\nand z",
    "ok\n\nrg a d please",
    "check\n\nRG, A, D",
    "fine\n\ny",
])
def test_it_fires_on_real_command_forms(msg):
    out, rc = _fires(msg)
    assert out, f"missed a real MC directive: {msg!r}"
    assert rc == 0


@pytest.mark.parametrize("msg", [
    "Good morning. Is the work complete?",
    "I saw a dentist and a doctor",
    "Explain option a",
    "run:\n```\nls -la\n```",
    "Please do a full review of the divergence code",
    "So the answer is that we need to test it and then decide",
])
def test_it_does_not_fire_on_ordinary_prose(msg):
    out, rc = _fires(msg)
    assert not out, f"false positive on ordinary prose: {msg!r}"
    assert rc == 0


def test_sy_demands_an_actual_tool_call_not_a_mood():
    out, _ = _fires("check\n\nsy")
    assert "REQUIRES an actual STEM-tool invocation" in out
    assert "Prose reasoning does NOT satisfy it" in out
    assert "TWO tools" in out, "the 21 Apr cross-verification rule is not surfaced"
    assert "confidence interval" in out, "the interval requirement is not surfaced"


def test_f_surfaces_all_five_ffafp_steps():
    out, _ = _fires("check\n\nf")
    for step in ("FIND", "FOLLOW", "ANALYSE", "FIX", "P-PASS"):
        assert step in out, f"FFAFP step {step} missing from the obligation"


def test_every_issued_command_gets_an_obligation_line():
    out, _ = _fires("check\n\nrg, a, f, sy, d, t")
    assert out.count("  • ") == 6, f"not every command produced an obligation:\n{out}"


def test_the_hook_never_blocks_a_prompt():
    """A hook that blocks is far worse than a missed directive."""
    for msg in ("", "rg, a, d", "\x00\x01 garbage", "x" * 20000):
        _, rc = _fires(msg)
        assert rc == 0
    r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                       capture_output=True, text=True)
    assert r.returncode == 0


def test_t_is_defined_as_the_artefact_pair():
    """CC1 did not know what `t` meant until 2026-08-30, having been issued it 5
    times. It is the TTS + markdown notes pair."""
    out, _ = _fires("check\n\nt")
    assert "TTS" in out and "experimental_notes" in out
