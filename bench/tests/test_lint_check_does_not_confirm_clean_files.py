"""ruff's success message was being counted as a violation.

THE DEFECT (B3, found 2026-08-01, live across the whole Exp 40-53 arc)
---------------------------------------------------------------------
``_verify_lint_check`` (bench/immune_agents.py) runs::

    python3 -m ruff check --no-fix --output-format=concise <file>

On a CLEAN file ruff exits 0 and prints ``All checks passed!`` on stdout. The
verifier then did::

    violations = [l for l in lines if l.strip()]

so ruff's own SUCCESS message counted as a violation. A clean file reported
``LINT_VIOLATION: All checks passed!`` and the B-Cell CONFIRMED the finding.

Every lint-class finding against a Python target has been getting a spurious
confirmation for the length of the arc. Severity is bounded by CONFIRM-only
discipline — a finding still needs a runnable falsifier to close — but a B-Cell
confirmation feeds severity and routing, and severity above 0.70 is the number
that decides whether the post-convergence sweep may ever clear a finding.

Raised by a background agent on 2026-08-01 and deferred that day for a stated
reason: it lives in the same file the prose-acceptance stage was exercising, and
changing verification machinery underneath the stage that verifies it is how that
day's errors happened. The reason expired when the stage landed.

rc==0 IS ruff's statement that the file is clean. stdout is commentary.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

IMMUNE = Path(__file__).resolve().parents[1] / "immune_agents.py"

_SUCCESS = ("All checks passed!", "All checks passed")


def _new_filter(stdout: str) -> list:
    """The repaired filter, mirrored from the generated subprocess code."""
    return [
        l for l in (stdout.strip().splitlines() if stdout else [])
        if l.strip() and l.strip() not in _SUCCESS
        and not l.strip().startswith("Found 0 errors")
    ]


def _old_filter(stdout: str) -> list:
    """The filter as it stood. Kept so the trap stays visible."""
    return [l for l in (stdout.strip().splitlines() if stdout else []) if l.strip()]


@pytest.fixture(scope="module")
def ruff_on_clean_file(tmp_path_factory):
    f = tmp_path_factory.mktemp("lint") / "clean.py"
    f.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    try:
        return subprocess.run(
            ["python3", "-m", "ruff", "check", "--no-fix",
             "--output-format=concise", str(f)],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover
        pytest.skip(f"ruff not runnable here: {exc}")


class TestTheTrapIsReal:
    """Characterisation. If ruff ever stops doing this, these tests say so."""

    def test_ruff_exits_zero_and_still_prints_to_stdout(self, ruff_on_clean_file):
        assert ruff_on_clean_file.returncode == 0
        assert ruff_on_clean_file.stdout.strip(), (
            "the whole defect depends on ruff printing on success; if this is "
            "empty the trap has changed shape and the fix should be re-read")

    def test_the_old_filter_reads_success_as_a_violation(self, ruff_on_clean_file):
        assert _old_filter(ruff_on_clean_file.stdout), (
            "this is the defect, reproduced: a clean file yields a non-empty "
            "violation list, which the verifier reports as LINT_VIOLATION and "
            "the B-Cell turns into a CONFIRMED finding")


class TestTheRepair:
    def test_the_new_filter_finds_nothing_on_a_clean_file(self, ruff_on_clean_file):
        assert _new_filter(ruff_on_clean_file.stdout) == []

    def test_a_real_violation_still_survives_the_filter(self, tmp_path):
        f = tmp_path / "dirty.py"
        f.write_text("import os\nimport sys\n\n\ndef f():\n    return 1\n",
                     encoding="utf-8")
        r = subprocess.run(
            ["python3", "-m", "ruff", "check", "--no-fix", "--select", "F401",
             "--output-format=concise", str(f)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode != 0, "two unused imports must fail ruff"
        kept = _new_filter(r.stdout)
        assert kept, "the repair must not silence genuine violations"
        assert any("F401" in k for k in kept)

    def test_rc_zero_is_treated_as_clean_regardless_of_stdout(self):
        src = IMMUNE.read_text()
        assert 'if result.returncode == 0:' in src
        assert 'print("LINT_CLEAN: no violations found (ruff exited 0)")' in src

    def test_the_old_expression_is_gone(self):
        src = IMMUNE.read_text()
        assert "violations = [l for l in lines if l.strip()]" not in src, (
            "the un-filtered comprehension is the defect itself")


class TestTheVerdictDirection:
    """A clean file must REJECT the finding, never confirm it."""

    def test_lint_clean_maps_to_rejected(self):
        src = IMMUNE.read_text()
        i = src.index('if stripped.startswith("LINT_CLEAN")')
        window = src[i:i + 400]
        assert 'verdict="REJECTED"' in window, (
            "a clean lint result is evidence AGAINST a code-quality finding")
