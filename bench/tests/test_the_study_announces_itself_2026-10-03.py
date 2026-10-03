#!/usr/bin/env python3
"""The programme of study cannot be forgotten, and the mechanism is EXECUTED.

WHY THIS EXISTS. The founder's instruction of 2026-10-03 was to mechanise the
programme of study "so it cannot be forgotten and expires when complete". Two
pieces do that: `experimental_notes/STUDY_IN_FLIGHT.json`, which carries the
reason the runs exist and one record per outstanding measurement, and the
`UserPromptSubmit` hook `~/.claude/hooks/study_pulse.py`, which puts that reason
in front of the assistant on every turn until the register says CLOSED.

Neither was guarded by anything. A register nothing validates can go malformed
and a hook nothing executes can silently stop firing -- and this project's own
record names 11 confirmed defects that were additions nothing reached. So these
tests CALL the hook rather than reading it (`execute-do-not-grep`, 2026-09-04):
they run it as a subprocess against a planted register and compare its output.

WHAT WOULD FAIL. A hook that crashes, a hook that keeps announcing after the
study closes, a hook that announces nothing while measurements are outstanding,
and a register missing the fields the hook formats.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
REGISTER = REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json"
HOOK = pathlib.Path.home() / ".claude" / "hooks" / "study_pulse.py"

REQUIRED = ("id", "what", "founder_ruling", "result", "headline")


def _register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def test_the_register_exists_and_is_well_formed():
    assert REGISTER.exists(), f"the study register is missing: {REGISTER}"
    d = _register()
    assert d.get("status") in ("OPEN", "CLOSED"), (
        f"status must be OPEN or CLOSED, not {d.get('status')!r}; the hook "
        "keys its silence on that exact value"
    )
    assert d.get("rationale"), "the register carries no reason for the runs"
    assert d.get("closes_when"), "nothing says when the study expires"
    ms = d.get("measurements") or []
    assert len(ms) >= 1, "a study with no measurements cannot be measured"
    for m in ms:
        missing = [k for k in REQUIRED if k not in m]
        assert not missing, f"measurement {m.get('id')!r} lacks {missing}"


def test_every_measurement_id_is_unique():
    ids = [m["id"] for m in _register()["measurements"]]
    assert len(ids) == len(set(ids)), f"duplicate measurement ids in {ids}"


def test_the_closing_condition_is_the_one_the_register_states():
    """`closes_when` is prose; this asserts the PREDICATE it describes.

    The register closes when every measurement has both a result and a
    headline. If that is true and the status still says OPEN, the study has
    finished and nothing noticed -- which is the failure this guards.
    """
    d = _register()
    done = all(m.get("result") is not None and m.get("headline") is not None
               for m in d["measurements"])
    if done:
        assert d["status"] == "CLOSED", (
            "every measurement has a result and a headline, so the study is "
            "complete, but status is still OPEN -- the expiry did not fire"
        )
    else:
        assert d["status"] == "OPEN", (
            "measurements are still outstanding but the study is marked "
            "CLOSED, so the hook has gone silent too early"
        )


def _run_hook(register: pathlib.Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["CDSFL_STUDY_REGISTER"] = str(register)
    return subprocess.run(
        [sys.executable, str(HOOK)], input="{}", capture_output=True,
        text=True, env=env, timeout=30)


@pytest.mark.skipif(not HOOK.exists(), reason="the hook is not installed here")
def test_the_hook_announces_an_open_study(tmp_path):
    """EXECUTED. An OPEN register must produce an announcement naming the ids."""
    reg = tmp_path / "study.json"
    reg.write_text(json.dumps({
        "status": "OPEN", "rationale": "WHY: to measure whether the fixes work",
        "closes_when": "all results present",
        "measurements": [
            {"id": "alpha", "what": "w", "founder_ruling": "r",
             "result": None, "headline": None},
            {"id": "beta", "what": "w", "founder_ruling": "r",
             "result": 1, "headline": "done"},
        ]}), encoding="utf-8")
    p = _run_hook(reg)
    assert p.returncode == 0, f"the hook failed: {p.stderr[:400]}"
    out = p.stdout
    assert "alpha" in out, (
        f"an outstanding measurement was not named in the announcement: {out!r}")
    assert "1 of 2" in out or "1 of 2 measurements" in out, (
        f"the announcement does not state how many remain: {out!r}")


@pytest.mark.skipif(not HOOK.exists(), reason="the hook is not installed here")
def test_the_hook_falls_silent_when_the_study_closes(tmp_path):
    """EXECUTED. This is the founder's 'expires when complete' half."""
    reg = tmp_path / "study.json"
    reg.write_text(json.dumps({
        "status": "CLOSED", "rationale": "r", "closes_when": "c",
        "measurements": [{"id": "alpha", "what": "w", "founder_ruling": "r",
                          "result": 1, "headline": "h"}]}), encoding="utf-8")
    p = _run_hook(reg)
    assert p.returncode == 0, f"the hook failed: {p.stderr[:400]}"
    assert p.stdout.strip() == "", (
        f"a CLOSED study is still announcing itself: {p.stdout!r}")


@pytest.mark.skipif(not HOOK.exists(), reason="the hook is not installed here")
def test_the_hook_cannot_break_a_turn(tmp_path):
    """A context hook that raises would cost every later turn its context.

    `UserPromptSubmit` hooks in this project always exit 0 by construction.
    Three hostile registers: absent, unparseable, and structurally wrong.
    """
    cases = {
        "absent": None,
        "unparseable": "{not json at all",
        "wrong shape": json.dumps({"status": "OPEN"}),
    }
    for why, body in cases.items():
        reg = tmp_path / f"{why.replace(' ', '_')}.json"
        if body is not None:
            reg.write_text(body, encoding="utf-8")
        p = _run_hook(reg)
        assert p.returncode == 0, (
            f"the hook exited {p.returncode} on a {why} register, which would "
            f"break the turn: {p.stderr[:300]}")
