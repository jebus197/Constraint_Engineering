#!/usr/bin/env python3
"""I31: the premise the drift detector was wired on is false, and the detector cannot fire.

Commit 90873cb wired `update_drift` because `pi_mem` "appears nowhere in
docs/MATHEMATICAL_APPENDIX.md". It appears as `π_mem`, defined in section 1.5
with the CUSUM statistics and the 2.0 threshold, so the founder's condition for
deferring, dependence on the current mathematical model, was met. Whether to
keep the report-only call or revert it is the founder's verdict. This test holds
the facts either way, by calling `scripts/i31_drift_detector_premise_2026-09-17.py`.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def probe():
    spec = importlib.util.spec_from_file_location("i31_probe", ROOT / "scripts" / "i31_drift_detector_premise_2026-09-17.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_appendix_defines_what_the_commit_said_it_never_mentions(probe, capsys):
    probe.premise()
    out = capsys.readouterr().out
    assert "'pi_mem' 0" in out, out
    greek = int(re.search(r"'π_mem' (\d+)", out).group(1))
    assert greek >= 1 and "pi_mem defined: line None" not in out and "S_pos defined: line None" not in out


def test_the_code_is_the_appendix_formula(probe, capsys):
    probe.same_mathematics()
    out = capsys.readouterr().out
    assert "minus appendix formula = 0;" in out, out
    diff = float(re.search(r"largest difference ([0-9.e+-]+)", out).group(1))
    assert diff < 1e-9, out


def test_fewer_than_3_updates_cannot_fire(probe, capsys):
    probe.can_it_fire()
    out = capsys.readouterr().out
    assert "1 same-direction update(s) from 0 can exceed |2.0|: False" in out
    assert "2 same-direction update(s) from 0 can exceed |2.0|: False" in out
    assert "3 same-direction update(s) from 0 can exceed |2.0|: True" in out


def test_production_makes_1_update_per_run_and_keeps_no_state(probe, capsys):
    probe.production()
    out = capsys.readouterr().out
    assert re.search(r"production sequence: \d+ cases, 0 fired", out), out
    assert "drift state after reload: {}" in out, out
