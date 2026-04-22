"""Tests for bench/launch_exp40.py — Exp 40 launcher.

Gate C is the launch-time live-path preflight for the §17 admissibility
parser, folded into the Exp 40 launcher per the 21 April 2026 Round 2
plan review (RQ1 Codex-preflight resolution). The parser itself has full
offline coverage in test_feedback_channel.py; these tests pin Gate C's
*launcher-level* contract:

* ``gate_c_preflight()`` returns ``(True, [])`` on a healthy parser.
* ``gate_c_preflight()`` reports schema drift when ``ADMISSIBILITY_GATES``
  no longer matches the expected five-gate tuple.
* The ``--preflight`` CLI path exits 0 on a healthy parser and prints the
  Gate C PASS line.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_launch_exp40.py -v
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. gate_c_preflight() — unit-level
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateCPreflightUnit:
    """Unit tests for the launcher's gate_c_preflight() function."""

    def test_passes_on_healthy_parser(self):
        from bench.launch_exp40 import gate_c_preflight

        ok, failures = gate_c_preflight()
        assert ok is True, (
            f"Gate C preflight failed on a healthy parser. "
            f"Failures: {failures}"
        )
        assert failures == []

    def test_detects_schema_drift_on_gates_tuple(self, monkeypatch):
        """If ADMISSIBILITY_GATES drifts, preflight must fail and name the
        drift explicitly."""
        import bench.dm._feedback as feedback_mod
        from bench.launch_exp40 import gate_c_preflight

        # Simulate drift: drop q_retest from the tuple.
        drifted = tuple(g for g in feedback_mod.ADMISSIBILITY_GATES
                        if g != "q_retest")
        monkeypatch.setattr(feedback_mod, "ADMISSIBILITY_GATES", drifted)

        ok, failures = gate_c_preflight()
        assert ok is False
        assert any("ADMISSIBILITY_GATES drift" in f for f in failures), (
            f"Expected drift failure description; got: {failures}"
        )

    def test_failure_message_names_expected_and_got(self, monkeypatch):
        """Drift failure message must include both the got and expected
        gate sets so an operator can diagnose without opening the code."""
        import bench.dm._feedback as feedback_mod
        from bench.launch_exp40 import gate_c_preflight

        drifted = feedback_mod.ADMISSIBILITY_GATES + ("invented_gate",)
        monkeypatch.setattr(feedback_mod, "ADMISSIBILITY_GATES", drifted)

        ok, failures = gate_c_preflight()
        assert ok is False
        drift_msg = next((f for f in failures if "drift" in f), "")
        assert "invented_gate" in drift_msg
        assert "expected" in drift_msg.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 2. --preflight CLI path — subprocess-level smoke
# ═══════════════════════════════════════════════════════════════════════════════


class TestPreflightCLI:
    """Exercise the --preflight CLI path end-to-end."""

    def test_preflight_flag_exits_zero_on_healthy_parser(self):
        result = subprocess.run(
            [sys.executable, "bench/launch_exp40.py", "--preflight"],
            cwd=_project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"--preflight exited {result.returncode}. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        assert "Gate C preflight: PASS" in result.stdout

    def test_dry_run_does_not_trigger_gate_c(self):
        """--dry-run is a config-only path; Gate C should NOT fire there.
        If it did, a corrupted parser would block plan inspection, which
        defeats the purpose of --dry-run as a safe config check."""
        result = subprocess.run(
            [sys.executable, "bench/launch_exp40.py", "--dry-run"],
            cwd=_project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Gate C preflight" not in result.stdout


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Case matrix coverage
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateCCoverage:
    """Cases pinned by Gate C's internal matrix must match parser truth."""

    def test_canonical_cases_align_with_parser(self):
        """The canonical cases embedded in gate_c_preflight must match the
        parser's actual behaviour — if they drift apart, the preflight is
        either over-strict (blocks healthy launches) or over-lax (misses
        real breakage). This test pins alignment."""
        from bench.dm._feedback import parse_admissibility_block
        from bench.launch_exp40 import _GATE_C_EXPECTED_GATES

        # These mirror the cases in gate_c_preflight's internal matrix.
        # If a case is added or changed there, this test must move in lockstep.
        canonical_cases = [
            ("no admissibility block present", set(_GATE_C_EXPECTED_GATES)),
            ("", set(_GATE_C_EXPECTED_GATES)),
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: PASS\n"
                "  σ_measured: PASS\n"
                "  q_retest: PASS\n",
                set(),
            ),
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: FAIL (pytest not run)\n"
                "  σ_measured: PASS\n"
                "  q_retest: PASS\n",
                {"d_tool"},
            ),
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: PASS\n"
                "  sigma_measured: PASS\n"
                "  q_retest: PASS\n",
                set(),
            ),
        ]

        for text, expected in canonical_cases:
            got = set(parse_admissibility_block(text))
            assert got == expected, (
                f"Canonical case drift: input={text!r} expected={expected} "
                f"got={got}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
