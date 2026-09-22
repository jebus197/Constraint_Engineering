#!/usr/bin/env python3
"""The 2 producers written by the 2026-09-22 panel audit are REACHED and EXECUTE.

The project's unreached-script ratchet exists because a script nothing runs is an
addition nothing reaches, and the founder's additive standard counts that as a
defect in its own right: 11 confirmed defects since 2026-08-01 were additions
that did nothing. These 2 producers carry the audit's 2 quantitative refutations,
so this file executes both and asserts on the figures they must produce.

  * scripts/falsifier_coverage_2026-09-22.py -- 77 of 97 scored fixes had no
    falsifier for the efficacy probe to re-run, so efficacy was unmeasurable and
    default-scored as a cure.
  * scripts/panel_size_trend_confound_2026-09-22.py -- the morning report's
    per-seat-round slope reverses sign when the 4th completed arm is included,
    and its criticals trend is consistent with a constant per-finding rate at
    Fisher p = 1.0.

Run:  python3 -m pytest bench/tests/test_panel_audit_producers_2026-09-22.py -q
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
COVERAGE = REPO / "scripts" / "falsifier_coverage_2026-09-22.py"
CONFOUND = REPO / "scripts" / "panel_size_trend_confound_2026-09-22.py"
ARCHIVE = REPO / "bench" / "logs"


def _run(script: pathlib.Path) -> subprocess.CompletedProcess:
    assert script.is_file(), f"producer missing: {script}"
    return subprocess.run([sys.executable, str(script)], cwd=str(REPO),
                          capture_output=True, text=True, timeout=300)


def _have_arms() -> bool:
    return bool(list(ARCHIVE.glob("commissioning_*/runner_state.json")))


def test_both_producers_answer_help_without_doing_the_work():
    """The founder's ruling: a --help must never cost money."""
    for script in (COVERAGE, CONFOUND):
        r = subprocess.run([sys.executable, str(script), "--help"], cwd=str(REPO),
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, (script.name, r.returncode, r.stderr[:400])
        assert "Run:" in (r.stdout + r.stderr), script.name


def test_falsifier_coverage_producer_runs_and_reports_the_gap():
    if not _have_arms():
        pytest.skip("commissioning archive absent")
    r = _run(COVERAGE)
    assert r.returncode == 0, (r.returncode, r.stderr[:600])
    out = r.stdout
    assert "efficacy NOT measurable : 77/97 = 79.3814%" in out, out[-1500:]
    assert "Wilson 95%, statsmodels   : [70.2871%, 86.2373%]" in out
    # The 2 interval routes must actually agree, not merely both be printed.
    assert "the 2 routes agree to 1e-12 : True" in out
    assert "NOT_PROBED_NO_FALSIFIER" in out
    # Every unprobed entry was admitted anyway -- the load-bearing consequence.
    assert "recorded ADMISSIBLE anyway : 77" in out


def test_confound_producer_reproduces_the_report_then_refutes_it():
    if not _have_arms():
        pytest.skip("commissioning archive absent")
    r = _run(CONFOUND)
    assert r.returncode == 0, (r.returncode, r.stderr[:600])
    out = r.stdout
    # It must first REPRODUCE the figures it disputes, or it is arguing with a
    # straw man.
    assert "slope=-0.1221  r=-0.9680" in out, out[-2000:]
    assert "slope=+0.4615  r=+0.9608" in out
    # Then refute both halves.
    assert "psr ~ seats  : slope=+0.1103" in out, "the sign reversal is the finding"
    assert "psr ~ rounds : slope=-0.2020  r=-0.9339" in out
    assert "Fisher exact, arm1 vs arm2 criticals/findings : p = 1.0000" in out
    assert "P(0 criticals | 9 findings at that rate) : 0.7623" in out


def test_arm4_is_the_arm_whose_inclusion_reverses_the_sign():
    """Pin the datum the morning report's table leaves out."""
    if not _have_arms():
        pytest.skip("commissioning archive absent")
    import json
    f = ARCHIVE / "commissioning_arm4_prose_20260922T053349Z" / \
        "commissioning_arm4_prose_report.json"
    if not f.is_file():
        pytest.skip(f"arm 4 report absent: {f}")
    rep = json.loads(f.read_text(encoding="utf-8"))
    seats, rounds = len(rep["models"]), rep["total_rounds"]
    psr = rep["total_findings"] / (seats * rounds)
    assert (seats, rounds, rep["total_findings"]) == (5, 1, 17)
    # The HIGHEST per-seat-round rate of all 4 arms, at the LARGEST panel size.
    assert abs(psr - 3.4) < 1e-9, psr
